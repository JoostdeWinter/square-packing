"""Check rational unit-square packings with two independent geometric predicates."""
import argparse,gzip,itertools,json,sys
from pathlib import Path
from fractions import Fraction as Q
def read(path):
    z=json.loads(gzip.decompress(path.read_bytes()))if path.suffix=='.gz'else json.loads(path.read_text())
    assert isinstance(z['n'],int) and z['n']==len(z['squares']) and Q(z['side'])>0
    return Q(z['side']),[tuple(Q(x[k]) for k in ('cx','cy','t'))for x in z['squares']]
def center(S,tiles):
    poses=[]
    for x,y,t in tiles:
        e=1+t*t;c=(1-t*t)/e;s=2*t/e;assert c*c+s*s==1
        h=(abs(c)+abs(s))/2;assert h<=x<=S-h and h<=y<=S-h
        poses.append((x,y,c,s,h))
    pairs=0
    for (x,y,c,s,h),(X,Y,C,T,H) in itertools.combinations(poses,2):
        dx=X-x;dy=Y-y
        if abs(dx)<h+H and abs(dy)<h+H:
            rhs=(1+abs(c*C+s*T)+abs(c*T-s*C))/2
            assert max(abs(dx*c+dy*s),abs(-dx*s+dy*c),abs(dx*C+dy*T),abs(-dx*T+dy*C))>=rhs
        pairs+=1
    return pairs
def polygon(S,tiles):
    polygons=[];boxes=[]
    for x,y,t in tiles:
        # Two corners arise from adding and subtracting the rational images of (1/2,1/2).
        a=(1-2*t-t*t)/(2*(1+t*t));b=(1+2*t-t*t)/(2*(1+t*t))
        p=[(x+a,y+b),(x-b,y+a),(x-a,y-b),(x+b,y-a)];polygons.append(p)
        es=[(p[(j+1)%4][0]-p[j][0],p[(j+1)%4][1]-p[j][1])for j in range(4)]
        assert all(u*u+v*v==1 for u,v in es) and all(es[j][0]*es[(j+1)%4][0]+es[j][1]*es[(j+1)%4][1]==0 for j in range(4))
        assert es[0][0]*es[1][1]-es[0][1]*es[1][0]==1 and all(0<=a<=S and 0<=b<=S for a,b in p)
        xp,yp=zip(*p);boxes.append((min(xp),max(xp),min(yp),max(yp)))
    def separating(p,q):
        for j,(x,y)in enumerate(p):
            X,Y=p[(j+1)%4];dx=X-x;dy=Y-y
            if all(dx*(b-y)-dy*(a-x)<=0 for a,b in q):return True
        return False
    checked=0
    for i,j in itertools.combinations(range(len(tiles)),2):
        a,A,b,B=boxes[i];c,C,d,D=boxes[j]
        if a<C and c<A and b<D and d<B:
            assert separating(polygons[i],polygons[j])or separating(polygons[j],polygons[i])
        checked+=1
    return checked
def run(path):
    S,sq=read(path);p=center(S,sq);q=polygon(S,sq);assert p==q==len(sq)*(len(sq)-1)//2
    for f in (center,polygon):
        try:f(S,[sq[0],sq[0]])
        except AssertionError:pass
        else:raise ValueError('duplicate-square control accepted')
        try:f(Q(1,4),[sq[0]])
        except AssertionError:pass
        else:raise ValueError('small-board control accepted')
    return dict(n=len(sq),center_pairs=p,polygon_pairs=q,negative_controls_passed=4)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('witness',type=Path,nargs='*');a=ap.parse_args()
    for p in a.witness or sorted(Path(__file__).parent.glob('*/packing.json.gz')):print(json.dumps(run(p)),flush=True)
