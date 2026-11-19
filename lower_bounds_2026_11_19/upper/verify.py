"""Replay exact containment, separation and strict historical comparisons."""
from pathlib import Path
from fractions import Fraction as Q
import json,gzip,itertools,sys
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H/'verification'))
import check_centers_and_edges as center_edges
from check_witness import parse_witness_v2_yaml,check_exact
def case(folder):
    path=folder/'packing.json.gz';z=json.load(gzip.open(path));n=z['n'];L=Q(z['side'])
    audit=center_edges.run(path);k,s,squares,sha=parse_witness_v2_yaml(str(folder/'witness.yaml'));assert k==n and s==L and len(squares)==n
    for tile,poly in zip(z['squares'],squares,strict=True):
        x,y,t=(Q(tile[k])for k in ('cx','cy','t'));c=(1-t*t)/(1+t*t);si=2*t/(1+t*t)
        assert set(poly)=={(x+(u*c-v*si)/2,y+(u*si+v*c)/2)for u,v in itertools.product((-1,1),repeat=2)}
    ok,why,count=check_exact(n,s,squares);assert ok and count==n*(n-1)//2,why
    dup=list(squares);dup[1]=dup[0];changed=[list(p) for p in squares];x,y=changed[0][0];changed[0][0]=x+Q(1,10**24),y
    for side,tiles in ((L-Q(1,10**12),squares),(L,dup),(L,changed)):assert not check_exact(n,side,tiles)[0]
    c=json.load(open(folder/'comparison.json'));assert c['n']==n and Q(c['new_side_exact'])==L
    for old in c['comparisons']:assert Q(old['safe_lower'])-L==Q(old['gain'])>0
    return dict(n=n,pairs_per_predicate=count,independent_geometric_predicates=3,negative_controls=7,geometry_audit=audit,witness_sha256=sha)
if __name__=='__main__':
    if not __debug__:raise SystemExit('Run with assertions enabled.')
    for comparison in sorted((H/'cases').glob('n*/comparison.json')):
        r=case(comparison.parent);assert r==json.load(open(comparison.parent/'audit.json'));print(f"{r['n']} squares, {r['pairs_per_predicate']:,} pairs per predicate, seven negative controls.",flush=True)
