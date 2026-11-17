"""Second exact checker for every row. Verifies tilted tip rectangles by projecting
their vertices and the vertices of each filled layer onto the row normal."""
import csv
import sys
from fractions import Fraction as F
from pathlib import Path

if not __debug__:
    raise RuntimeError('Run this verifier without -O.')

def band(row, which, length):
    b = int(row['b'+which])
    p = F(row['t'+which])
    d = p.denominator
    e = p.numerator
    hyp = d*d+e*e
    co = F(d*d-e*e,hyp)
    si = F(2*d*e,hyp)
    assert co>0 and si>0 and co*co+si*si==1
    W = b*co+si
    rs, near, far = row[which].split(':')
    R = int(rs)
    assert b>0 and R>0
    near = [int(v) for v in near.split(',') if v]
    far = [int(v) for v in far.split(',') if v]
    # Put the first tilted row as low as permitted by the near filled rectangles.
    # A near level's top-left vertex has largest row-normal projection.
    near_lift = max([F(0)]+[j+1+(si-(W-m))*si/co for j,m in enumerate(near)])
    def polygon(k):
        O = (si,near_lift+k/co)
        return [(O[0]+u*co-v*si,O[1]+u*si+v*co)
                for u,v in [(0,0),(b,0),(b,1),(0,1)]]
    first, last = polygon(0),polygon(R-1)
    assert all(0<=x<=W and 0<=y<=length for x,y in first+last)
    def project(P):
        return [-si*x+co*y for x,y in P]
    first_n, last_n = project(first),project(last)
    assert max(first_n)-min(first_n)==1
    assert min(last_n)-min(first_n)==R-1
    assert max(last_n)-min(last_n)==1
    # The other rows interpolate these extrema and have disjoint row-normal
    # projection interiors [start+j,start+j+1].
    for flip, levels in [(False,near),(True,far)]:
        for j,m in enumerate(levels):
            assert m>0
            P=[(x,y) for x in [W-m,W] for y in [j,j+1]]
            if flip:P=[(W-x,length-y) for x,y in P]
            assert all(0<=x<=W and 0<=y<=length for x,y in P)
            coord=project(P)
            if flip: assert min(coord)>=max(last_n)
            else: assert max(coord)<=min(first_n)
    return W,R*b+sum(near)+sum(far)

def verify(row):
    n,K = int(row['n']),int(row['K'])
    bv,bh = int(row['bV']),int(row['bH'])
    S = F(row['side_exact'])
    Gx,Gy=K-bv,K-bh
    assert Gx>0 and Gy>0
    Wv,nv=band(row,'V',S)
    Wh,nh=band(row,'H',F(Gx))
    # Horizontal strip has x <= Gx. Vertical strip has x >= Gx.
    # The grid has y <= Gy in x <= Gx, with horizontal strip above it.
    assert Gx+Wv<=S and Gy+Wh<=S
    assert 0<n<=Gx*Gy+nv+nh==int(row['capacity'])
    assert S<F(row['comparison_side'])

def main():
    path=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).with_name('bounds.csv')
    rows=list(csv.DictReader(path.open(newline='')))
    assert len({int(x['n']) for x in rows})==len(rows)
    for row in rows:verify(row)
    for mutation in ['count','side','levels']:
        bad=dict(rows[0])
        if mutation=='count':bad['n']=int(bad['capacity'])+1
        if mutation=='side':bad['side_exact']='1'
        if mutation=='levels':bad['V']='99:1000:'
        try:verify(bad)
        except AssertionError:pass
        else:raise RuntimeError('Accepted mutated '+mutation)
    print(f'PASS. Independent exact vertex and separating-axis check for {len(rows)} patterns, {sum(int(x["n"]) for x in rows):,} retained unit squares. Three mutations rejected.')
if __name__=='__main__':main()
