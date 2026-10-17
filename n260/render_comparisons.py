#!/usr/bin/env python3
"""Render certified square packings and descriptive near-contact comparisons.

No geometric certificate is inferred from these floating-point illustrations.
See comparison-*.json for the exact-witness source and noncanonical matching.
"""
from __future__ import annotations
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
import argparse, hashlib, json, math
from dataclasses import dataclass
from fractions import Fraction
from html import escape
from pathlib import Path
import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.spatial import cKDTree
import shutil,subprocess
try:
    import cairosvg
except ImportError:
    cairosvg=None

ORANGE='#e87924'; INK='#172b40'; MUTED='#5b6e80'; EDGE='#4b6175'
FILL_AXIS='#e6ebf0'; FILL_TILT='#b9d0e2'; BG='#ffffff'
@dataclass
class Geometry:
    centers: np.ndarray
    basis: np.ndarray
    side: float
    @property
    def n(self):return len(self.centers)
    @property
    def angles(self):return np.arctan2(self.basis[:,1],self.basis[:,0])
    @property
    def corners(self):
        u=self.basis;v=np.c_[-u[:,1],u[:,0]]
        return self.centers[:,None,:]+.5*np.array([-1,1,1,-1])[None,:,None]*u[:,None,:]+.5*np.array([-1,-1,1,1])[None,:,None]*v[:,None,:]

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def baseline_geometry(row):
    p=np.asarray(row['poses'],float)
    return Geometry(p[:,:2],np.c_[np.cos(p[:,2]),np.sin(p[:,2])],float(row['reported_side']))
def exact_geometry(path):
    a=json.loads(Path(path).read_text());centers=[];basis=[]
    for square in a['squares']:
        xy=list(map(Fraction,square['center']));uv=list(map(Fraction,square['basis']))
        if uv[0]**2+uv[1]**2!=1:raise ValueError('Nonunit exact basis')
        centers.append(list(map(float,xy)));basis.append(list(map(float,uv)))
    if len(centers)!=a['n']:raise ValueError('Incorrect witness count')
    return Geometry(np.array(centers),np.array(basis),float(Fraction(a['side']))),a

def register(before,after,orientation_weight=.1):
    trials=[];best=None
    for reflected in[False,True]:
        for quarter in range(4):
            k=quarter%4;R=np.array([[[1,0],[0,1]],[[0,-1],[1,0]],[[-1,0],[0,-1]],[[0,1],[-1,0]]][k],float)
            M=R@np.diag([-1 if reflected else 1,1]);xy=(after.centers-after.side/2)@M.T+before.side/2;uv=after.basis@M.T;t=np.arctan2(uv[:,1],uv[:,0]);delta=before.angles[:,None]-t[None,:]
            dist2=np.sum((before.centers[:,None,:]-xy[None,:,:])**2,axis=2);angular=np.sin(2*delta)**2;cost=dist2+orientation_weight*angular;ii,jj=linear_sum_assignment(cost);score=float(cost[ii,jj].sum());item=dict(reflected=reflected,quarter_turns_ccw=quarter,total_cost=score)
            trials.append(item)
            if best is None or score<best[0]-1e-12:best=(score,M,jj,xy,uv,dist2,angular,item)
    score,M,assignment,xy,uv,d2,angular,item=best
    # Comparison coordinates are in the after box, with its D4 orientation
    # selected above. Container centers, rather than lower-left corners, align.
    local=(after.centers-after.side/2)@M.T+after.side/2
    aligned=Geometry(local[assignment],uv[assignment],after.side)
    mapping=[]
    for i,j in enumerate(assignment):
        diff=xy[j]-before.centers[i]
        angle=((math.atan2(uv[j,1],uv[j,0])-before.angles[i]+math.pi/4)%(math.pi/2))-math.pi/4
        mapping.append(dict(before_index=i,after_original_index=int(j),aligned_center_displacement=diff.tolist(),center_distance=float(np.linalg.norm(diff)),angle_difference_mod_quarter_turn=float(angle),assignment_cost=float(d2[i,j]+orientation_weight*angular[i,j])))
    return aligned,mapping,dict(**item,matrix=M.astype(int).tolist(),translation_for_before_centered_coordinates=(np.array([before.side/2,before.side/2])-M@np.array([after.side/2,after.side/2])).tolist(),orientation_weight=orientation_weight,d4_trials=trials,assignment_cost_formula='squared center distance + orientation_weight * sin(2 * angle_difference)^2',canonical=False)

def point_segment(p,a,b):
    ab=b-a;t=float(np.dot(p-a,ab)/np.dot(ab,ab));q=a+np.clip(t,0,1)*ab
    return float(np.dot(p-q,p-q)),p,q

def nearest_feature(A,B,parallel_tolerance=1e-5):
    best=(float('inf'),None,None)
    for V,E in[(A,B),(B,A)]:
        for p in V:
            for k in range(4):
                item=point_segment(p,E[k],E[(k+1)%4])
                if item[0]<best[0]:best=item
    d=math.sqrt(max(0,best[0]));point=(best[1]+best[2])/2
    longest=None
    for k in range(4):
        a,b=A[k],A[(k+1)%4];u=b-a;L=np.linalg.norm(u);u=u/L;normal=np.array([-u[1],u[0]])
        for j in range(4):
            c,e=B[j],B[(j+1)%4];v=e-c;v=v/np.linalg.norm(v)
            if abs(float(u[0]*v[1]-u[1]*v[0]))>parallel_tolerance:continue
            offset=float((c-a)@normal)
            if abs(offset)>max(d+1e-9,1e-9):continue
            ends=np.array([(c-a)@u,(e-a)@u]);lo=max(0.,float(ends.min()));hi=min(float(L),float(ends.max()));length=hi-lo
            if length>.025 and(longest is None or length>longest[0]):longest=(length,a+lo*u+offset*normal/2,a+hi*u+offset*normal/2)
    feature=dict(distance=d,kind='point',point=point.tolist())
    if longest is not None:feature.update(kind='segment',segment=[longest[1].tolist(),longest[2].tolist()],length=float(longest[0]))
    return feature

def contacts(g,tolerance):
    corners=g.corners;result={};h=.5*np.abs(g.basis).sum(axis=1)
    for i,j in sorted(cKDTree(g.centers).query_pairs(math.sqrt(2)+tolerance)):
        if np.any(np.abs(g.centers[j]-g.centers[i])-h[i]-h[j]>tolerance):continue
        f=nearest_feature(corners[i],corners[j])
        if f['distance']<=tolerance+1e-12:result[(i,j)]=f
    return result

def text(x,y,value,size=18,fill=INK,weight='400',anchor='start'):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" text-anchor="{anchor}">{escape(str(value))}</text>'
def open_svg(width,height,title,description,metadata):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc"><title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc><metadata>{escape(json.dumps(metadata,separators=(",",":")))}</metadata><rect width="{width}" height="{height}" fill="{BG}"/><g font-family="DejaVu Sans,Arial,sans-serif">'
def packing_svg(g,x,y,scale,changed=None):
    parts=[]
    def coords(q):return np.c_[x+q[:,0]*scale,y+(g.side-q[:,1])*scale]
    for i,poly in enumerate(g.corners):
        q=coords(poly);angle=((g.angles[i]+math.pi/4)%(math.pi/2))-math.pi/4;fill=FILL_AXIS if abs(angle)<.001 else FILL_TILT
        points=' '.join(f'{a:.10f},{b:.10f}'for a,b in q)
        parts.append(f'<polygon points="{points}" fill="{fill}" stroke="{EDGE}" stroke-width=".8" stroke-linejoin="round"/>')
    parts.append(f'<rect x="{x:.10f}" y="{y:.10f}" width="{g.side*scale:.10f}" height="{g.side*scale:.10f}" fill="none" stroke="{INK}" stroke-width="1.7"/>')
    for pair,f in sorted((changed or {}).items()):
        if f['kind']=='segment':
            a,b=coords(np.asarray(f['segment']));parts.append(f'<path d="M{a[0]:.10f},{a[1]:.10f} L{b[0]:.10f},{b[1]:.10f}" fill="none" stroke="white" stroke-width="4.6" stroke-linecap="round"/><path d="M{a[0]:.10f},{a[1]:.10f} L{b[0]:.10f},{b[1]:.10f}" fill="none" stroke="{ORANGE}" stroke-width="2.8" stroke-linecap="round"><title>Changed near-contact: {pair[0]}–{pair[1]}</title></path>')
        else:
            a=coords(np.asarray([f['point']]))[0];parts.append(f'<circle cx="{a[0]:.10f}" cy="{a[1]:.10f}" r="3.3" fill="{ORANGE}" stroke="white" stroke-width="1.1"><title>Changed near-contact: {pair[0]}–{pair[1]}</title></circle>')
    return ''.join(parts)

def render_case(n,before,after,record,metadata,lost,gained,tol):
    W,H=1800,1050;S=max(before.side,after.side);scale=760/S
    parts=[open_svg(W,H,f'n = {n}: certified packing improvement',f'Before and after packing of {n} unit squares. Orange marks removed near-contacts on the left and added near-contacts on the right under one geometric matching.',metadata)]
    parts+=[text(70,49,f'{n} unit squares',32,weight='700'),text(70,85,'A smaller enclosing square',20,fill=MUTED),text(1730,49,f'−{record["improvement"]:.9f} units',25,fill=INK,weight='700',anchor='end'),text(1730,84,f'{100*record["improvement"]/before.side:.4f}% reduction in side length',17,fill=MUTED,anchor='end')]
    for x,label,value,g,changed in[(70,'BEFORE · website-listed upper bound',before.side,before,lost),(970,'AFTER · certified upper bound',after.side,after,gained)]:
        parts+=[text(x,127,label,16,fill=MUTED,weight='700'),text(x,159,f'S ≈ {value:.12f}',24,weight='600')]
        offset=(S-g.side)*scale/2;parts.append(packing_svg(g,x+offset,183+offset,scale,changed))
    parts+=[f'<path d="M70,980 L105,980" stroke="{ORANGE}" stroke-width="3" stroke-linecap="round"/>',text(119,986,f'{len(lost)} removed near-contacts',17),f'<path d="M970,980 L1005,980" stroke="{ORANGE}" stroke-width="3" stroke-linecap="round"/>',text(1019,986,f'{len(gained)} added near-contacts',17),text(70,1025,f'Pairwise near-contact threshold: {tol:g} unit. Same geometric scale in both panels.',14,fill=MUTED),text(970,1025,'One D4 + assignment matching; orange does not show motion.',14,fill=MUTED)]
    return ''.join(parts)+'</g></svg>'

def render_single(n,g,record,metadata):
    parts=[open_svg(960,680,f'Packing of {n} unit squares',f'Certified upper-bound packing with enclosing side {g.side:.12f}. Geometry is a floating-point illustration of the exact rational witness.',metadata),text(36,42,f'{n} unit squares',28,weight='700'),text(36,77,f'S ≈ {g.side:.12f}',20,fill=MUTED),packing_svg(g,220,105,520/g.side),text(220,655,'Unit squares · certified upper bound',15,fill=MUTED)]
    return ''.join(parts)+'</g></svg>'

def write_svg_png(path,svg,png=True):
    path.write_text('<?xml version="1.0" encoding="UTF-8"?>\n'+svg,encoding='utf-8')
    if png:
        if cairosvg is not None:cairosvg.svg2png(bytestring=svg.encode(),write_to=str(path.with_suffix('.png')))
        elif shutil.which('inkscape'):subprocess.run(['inkscape',str(path),'--export-type=png','--export-filename='+str(path.with_suffix('.png'))],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        else:raise RuntimeError('PNG export requires CairoSVG or Inkscape; SVG outputs are already written.')

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--catalogue',type=Path,default=Path('shared/catalogue.json'));ap.add_argument('--records',type=Path,default=Path('verification/verified_records.json'));ap.add_argument('--output',type=Path,default=Path('campaign_visuals/output'));ap.add_argument('--contact-tolerance',type=float,default=.001);ap.add_argument('--orientation-weight',type=float,default=.1);ap.add_argument('--only',type=str);ap.add_argument('--no-png',action='store_true');args=ap.parse_args()
    if args.contact_tolerance<=0:raise ValueError('contact-tolerance must be positive')
    if args.orientation_weight<0:raise ValueError('orientation-weight must be nonnegative')
    C=json.loads(args.catalogue.read_text());records=json.loads(args.records.read_text());args.output.mkdir(parents=True,exist_ok=True);only=set(map(int,args.only.split(',')))if args.only else None;cases=[];manifest=[]
    for ns,record in sorted(records.items(),key=lambda a:int(a[0])):
        n=int(ns)
        if only and n not in only:continue
        witness=Path(record['witness'])
        if not witness.exists() and(args.records.parent/witness).exists():witness=args.records.parent/witness
        before=baseline_geometry(C[ns]);raw,exact=exact_geometry(witness)
        if Fraction(exact['side'])!=Fraction(record['certified_side_exact']):raise ValueError(f'Certified side mismatch for {n}')
        if before.n!=raw.n or raw.n!=n:raise ValueError('Comparison count mismatch')
        if abs(before.side-record['previous_bound'])>1e-8:raise ValueError('Registry and catalogue baseline differ')
        after,mapping,registration=register(before,raw,args.orientation_weight);maximum=max(.005,args.contact_tolerance);bc=contacts(before,maximum);ac=contacts(after,maximum);tol=args.contact_tolerance;bnear={k:v for k,v in bc.items()if v['distance']<=tol};anear={k:v for k,v in ac.items()if v['distance']<=tol};lost={k:bnear[k]for k in bnear.keys()-anear.keys()};gained={k:anear[k]for k in anear.keys()-bnear.keys()}
        sensitivities=[]
        for t in sorted(set([.0001,tol,.005])):
            B={k for k,v in bc.items()if v['distance']<=t};A={k for k,v in ac.items()if v['distance']<=t};sensitivities.append(dict(tolerance=t,before_edges=len(B),after_edges=len(A),removed_edges=len(B-A),added_edges=len(A-B)))
        metadata=dict(n=n,kind='descriptive near-contact comparison',indexing='Zero-based array indices; after contacts are relabeled by matched before indices.',near_contact_definition='Minimum Euclidean distance between the two square boundaries is at most contact_tolerance; this is a floating-point descriptive threshold, not a claim of exact contact.',contact_tolerance=tol,parallel_feature_tolerance=1e-5,display_axis_angle_threshold_radians=.001,correspondence_caveat='Unit squares are unlabeled. This deterministic D4/Hungarian correspondence is useful for visualization, not canonical, and does not establish a continuous motion between packings.',registration=registration,mapping=mapping,before_source=str(args.catalogue),before_source_sha256=digest(args.catalogue),before_side=before.side,after_exact_witness=str(witness),after_exact_witness_sha256=digest(witness),after_certified_side_exact=exact['side'],after_side=after.side,record=record,before_near_contacts=[dict(pair=list(k),**v)for k,v in sorted(bnear.items())],after_near_contacts=[dict(pair=list(k),**v)for k,v in sorted(anear.items())],removed_near_contacts=[dict(pair=list(k),after_original_pair=[mapping[k[0]]['after_original_index'],mapping[k[1]]['after_original_index']],**v)for k,v in sorted(lost.items())],added_near_contacts=[dict(pair=list(k),after_original_pair=[mapping[k[0]]['after_original_index'],mapping[k[1]]['after_original_index']],**v)for k,v in sorted(gained.items())],tolerance_sensitivity=sensitivities,visual_geometry='Float projections of input centers and unit bases. Comparison and clean website-style asset use the registered D4 orientation of the exact witness.')
        (args.output/f'n{n}_topology_comparison.json').write_text(json.dumps(metadata,indent=2)+'\n');public={k:metadata[k]for k in['n','kind','contact_tolerance','correspondence_caveat','registration','before_source','before_source_sha256','before_side','after_exact_witness','after_exact_witness_sha256','after_certified_side_exact','after_side','visual_geometry']};public['correspondence_metadata_file']=f'n{n}_topology_comparison.json';svg=render_case(n,before,after,record,public,lost,gained,tol);write_svg_png(args.output/f'n{n}_before_after.svg',svg,not args.no_png);write_svg_png(args.output/f'square-{n}.svg',render_single(n,after,record,public),not args.no_png);cases.append(svg);manifest.append(dict(n=n,comparison=f'n{n}_before_after.svg',comparison_png=f'n{n}_before_after.png',after_only=f'square-{n}.svg',metadata=f'n{n}_topology_comparison.json',removed=len(lost),added=len(gained),side_before=before.side,side_after=after.side));print(json.dumps(manifest[-1]),flush=True)
    import xml.etree.ElementTree as ET
    outer=ET.Element('{http://www.w3.org/2000/svg}svg',{'width':'1800','height':str(1050*len(cases)),'viewBox':f'0 0 1800 {1050*len(cases)}','role':'img'});ET.SubElement(outer,'{http://www.w3.org/2000/svg}title').text='Certified packing improvements: before and after'
    for i,svg in enumerate(cases):
        child=ET.fromstring(svg);child.set('y',str(i*1050))
        for element in child.iter():
            if 'id'in element.attrib:element.set('id',f'case-{i}-'+element.attrib['id'])
            if 'aria-labelledby'in element.attrib:element.set('aria-labelledby',' '.join(f'case-{i}-'+v for v in element.attrib['aria-labelledby'].split()))
        outer.append(child)
    combined=ET.tostring(outer,encoding='unicode');write_svg_png(args.output/'before_after_orange.svg',combined,not args.no_png);(args.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
if __name__=='__main__':main()
