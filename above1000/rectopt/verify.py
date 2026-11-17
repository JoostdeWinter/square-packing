"""Replay exact rational packing components and the two-block construction.
Run python verify.py, or python verify.py --full 2538 to expand and check one case.
All geometry uses integers. Distinct interiors may meet at their boundaries.
"""
import argparse
import csv
import gzip
import json
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
F = 10**10
L = 10000000020                     # Grid spacing is L / F.
D = F*F                          # Centers are stored in units of 1/D.
T = 10**12                        # p/T is the tangent of half of the angle.
CELL = F*L

def oriented(pose):
    x,y,p = pose
    c, s, q = T*T-p*p, 2*T*p, T*T+p*p
    return x,y,c,s,q

def overlaps(u,v):
    x,y,c,s,q = u
    X,Y,C,S,Q = v
    dx,dy = X-x,Y-y
    h = D*(q*Q + abs(c*C+s*S) + abs(c*S-s*C))
    return (2*Q*max(abs(c*dx+s*dy),abs(-s*dx+c*dy)) < h
            and 2*q*max(abs(C*dx+S*dy),abs(-S*dx+C*dy)) < h)

def verify_geometry(poses,width,height,notch=None):
    bins = {}
    for pos in poses:
        v = oriented(pos)
        x,y,c,s,q = v
        rad = (abs(c)+abs(s))*D
        assert 2*q*min(x,width-x,y,height-y) >= rad, 'wall violation'
        if notch is not None:
            bx,by=notch
            if 2*q*(bx-x)<rad and 2*q*(by-y)<rad:
                dx,dy = bx+width-2*x, by+height-2*y
                w,h = width-bx,height-by
                assert (abs(c*dx+s*dy)>=q*D+abs(c)*w+abs(s)*h
                        or abs(-s*dx+c*dy)>=q*D+abs(s)*w+abs(c)*h), 'occupied notch'
        # A unit square lies within sqrt(2)/2 of its center.
        # Centers separated by at least 2 along x or y cannot overlap.
        i,j=x//(2*D), y//(2*D)
        for a in range(i-1,i+2):
            for b in range(j-1,j+2):
                for other in bins.get((a,b),()):
                    assert not overlaps(v,other), 'overlapping squares'
        bins.setdefault((i,j),[]).append(v)

def blocks():
    with gzip.open(HERE/'blocks.json.gz','rt') as f:
        return json.load(f)

def check_block(block):
    a,b,e,f=map(block.__getitem__,['a','b','e','f'])
    assert a>0 and b>0 and e>0 and 0<f<F
    assert len(block['poses']) == a*b+e
    notch=(a*CELL,b*CELL) if block['notch'] else None
    verify_geometry(block['poses'],(a*F+f)*L,(b*F+f)*L,notch)

def component(key,library):
    key=int(key)
    if key==-1: return 0,0,0,0,True,[]
    block=library[str(key//2)]
    a,b=block['a'],block['b']
    poses=block['poses']
    if key%2:
        a,b=b,a
        # Reflection across y=x changes the square angle to -theta modulo pi/2.
        poses=[(y,x,-p) for x,y,p in poses]
    return a,b,block['e'],block['f'],block['notch'],poses

def construction(row,library,expand=False):
    k,n = int(row['k']),int(row['n'])
    a,b,e,f1,clear1,v1 = component(row['block_A'],library)
    c,d,h,f2,clear2,v2 = component(row['block_B'],library)
    C,H=k-a,k-b
    assert c<=C and d<=H and min(C,H)>=0
    assert c<C or d<H or clear1 or clear2
    assert n==k*k+e+h
    f=max(f1,f2)*L
    bound=k*CELL+f
    assert Fraction(row['upper'])==Fraction(bound,D)
    if not expand: return
    def grid(nx,ny,x0,y0):
        return [(x0+i*CELL+CELL//2,y0+j*CELL+CELL//2,0)
                for i in range(nx) for j in range(ny)]
    top=list(v2)
    top.extend(grid(C-c,d,c*CELL+f,0))
    top.extend(grid(C,H-d,0,d*CELL+f))
    poses=list(v1)+[(bound-x,bound-y,p) for x,y,p in top]
    poses+=grid(a,H,0,b*CELL+f)+grid(C,b,a*CELL+f,0)
    assert len(poses)==n
    return bound,poses

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--full',type=int,action='append',default=[])
    ap.add_argument('--poses',type=Path,help='write expanded integer pose triples for a single --full')
    args=ap.parse_args()
    library=blocks()
    with open(HERE/'bounds.csv') as f: rows=list(csv.DictReader(f))
    assert len({r['n'] for r in rows})==len(rows)
    for block in library.values(): check_block(block)
    print(f'PASS: {len(library)} rational packing components, including containment, notches, and separation.')
    for row in rows:
        construction(row,library)
        assert Fraction(row['upper']) < Fraction(row['comparison_floor'])
    print(f'PASS: {len(rows)} constructions, square counts, and strict comparisons to benchmark floors.')
    for n in args.full:
        row=next(r for r in rows if int(r['n'])==n)
        side,poses=construction(row,library,True)
        verify_geometry(poses,side,side)
        print(f'PASS: independent expanded geometry for n={n}, side {row["upper"]}.')
        if args.poses:
            assert len(args.full)==1
            args.poses.write_text(json.dumps(dict(center_denominator=D,tan_half_denominator=T,side_numerator=side,poses=poses))+'\n')
if __name__=='__main__':main()
