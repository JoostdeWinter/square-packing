"""Export the exact packing for a listed n. Only Python's standard library is required."""
import argparse
import csv
import gzip
import importlib.util
import json
from fractions import Fraction as Q
from pathlib import Path

HERE=Path(__file__).resolve().parent
def module(path):
    spec=importlib.util.spec_from_file_location(path.stem,path)
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def load_row(path,n):
    with path.open(newline='') as f:
        for row in csv.DictReader(f):
            if int(row['n'])==n: return row
    raise ValueError(f'{n} is absent from {path.name}')

def direct_packing(n):
    entry=load_row(HERE/'constructions.csv',n)
    folder=HERE/entry['witness_folder']
    row=load_row(folder/'bounds.csv',n)
    if folder.name=='bands':
        s,poses=module(folder/'verify_refined.py').verify(row,True)
    else:
        single=folder.name=='chains'
        with gzip.open(folder/('rectangle.json.gz' if single else 'blocks.json.gz'),'rt') as f:blocks=json.load(f)
        if folder.name in ('rectangles','rectopt'):
            m=module(folder/'verify.py')
            s,poses=m.construction(row,blocks,True)
        elif folder.name=='multi':
            m=module(folder/'verify_multi.py')
            s,poses=m.materialize(row,blocks)
        else:
            m=module(folder/'verify_chains.py')
            s,poses=m.expand(blocks,row)
        s=Q(s,m.D)
        poses=[(Q(x,m.D),Q(y,m.D),Q(t,m.T)) for x,y,t in poses]
    assert len(poses)==n and s==Q(entry['upper_exact'])
    return s,poses

def packing(n):
    entry=load_row(HERE/'records.csv',n)
    if entry['witness_folder']!='derived.csv':
        return direct_packing(n)
    r=load_row(HERE/'derived.csv',n)
    s,base=direct_packing(int(r['source_n']))
    t=int(r['copies_per_axis']);j=int(r['border_layers'])
    poses=[(x+i*s,y+k*s,a) for i in range(t) for k in range(t) for x,y,a in base]
    s=t*s;h=int(s);half=Q(1,2)
    poses.extend((s+i+half,k+half,0) for i in range(j) for k in range(h))
    poses.extend((i+half,s+k+half,0) for i in range(h+j) for k in range(j))
    assert len(poses)-int(r['squares_removed'])==n and s+j==Q(entry['upper_exact'])
    return s+j,poses[:n]

def export(n,dest,as_yaml=False):
    s,poses=packing(n)
    with dest.open('w') as f:
        if not as_yaml:
            print('# center x, center y, tangent of half-angle; all lengths exact',file=f)
            print(n,s,file=f)
            for x,y,t in poses:print(x,y,t,file=f)
        else:
            print('softschema:\n  contract: packing.squares:Witness/v2',file=f)
            print(f"n: {n}\nscalar:\n  kind: rational\nside: '{s}'\nsquares:",file=f)
            for i,(x,y,t) in enumerate(poses):
                t=Q(t)
                c=(1-t*t)/(1+t*t);d=2*t/(1+t*t)
                print(f'  - id: {i}\n    corners:',file=f)
                for u,v in [(-1,-1),(1,-1),(1,1),(-1,1)]:
                    print(f"      - ['{x+(u*c-v*d)/2}', '{y+(u*d+v*c)/2}']",file=f)
if __name__=='__main__':
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('n',type=int);cli.add_argument('output',type=Path)
    cli.add_argument('--yaml',action='store_true',help='write four rational corners for every square')
    args=cli.parse_args();export(args.n,args.output,args.yaml)
