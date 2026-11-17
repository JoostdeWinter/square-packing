"""Expand the repeated-rectangle construction and verify every unit square with integers.
Run python verify_chains.py from any directory. With --export N, write all poses for N.
"""
from fractions import Fraction
from pathlib import Path
import argparse, csv, gzip, json
HERE=Path(__file__).resolve().parent
F=10**10
L=10000000020
D=F*F
T=10**12
CELL=F*L

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


def grid(w,h,x=0,y=0):
    return [(x+i*CELL+CELL//2,y+j*CELL+CELL//2,0)
            for i in range(w) for j in range(h)]

def expand(block,row):
    k=int(row['k'])
    m=int(row['copies'])
    swapped=int(row['transposed'])
    hseps=int(row['vertical_steps'])
    f=block['f']*L
    poses=[]
    w=h=0
    for i in range(m):
        transposed=i<swapped
        a,b=block['a'],block['b']
        sample=block['poses']
        if transposed:
            a,b=b,a
            sample=[(y,x,-p) for x,y,p in sample]
        # A one-cell spacer in either the row or column direction clears a join.
        sy=int(i>0 and i<=hseps)
        sx=int(i>0 and not sy)
        poses.extend([(x+(w+sx)*CELL,y+(h+sy)*CELL,p) for x,y,p in sample])
        if i:
            poses.extend(grid(a+sx,h+sy,w*CELL+f,0))
            poses.extend(grid(w+sx,b+sy,0,h*CELL+f))
        w+=a+sx
        h+=b+sy
    assert w<=k and h<=k
    poses.extend(grid(k-w,h,w*CELL+f,0))
    poses.extend(grid(k,k-h,0,h*CELL+f))
    assert len(poses)==k*k+m*block['e']
    n=int(row['n'])
    assert len(poses)==n
    side=k*CELL+f
    assert Fraction(side,D)==Fraction(row['upper'])
    return side,poses

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--export',type=int)
    args=parser.parse_args()
    with gzip.open(HERE/'rectangle.json.gz','rt') as f:
        block=json.load(f)
    assert len(block['poses'])==block['a']*block['b']+block['e']
    verify_geometry(block['poses'],(block['a']*F+block['f'])*L,(block['b']*F+block['f'])*L)
    data=list(csv.DictReader((HERE/'bounds.csv').open()))
    for row in data:
        side,poses=expand(block,row)
        verify_geometry(poses,side,side)
        assert Fraction(row['upper'])<Fraction(row['comparison_floor'])
        print(f"PASS {len(poses)} unit squares, exact side {Fraction(side,D)}")
        if args.export==len(poses):
            path=Path.cwd()/f"poses-{len(poses)}.json"
            path.write_text(json.dumps(dict(center_denominator=D,tan_half_denominator=T,
                side_numerator=side,poses=poses))+'\n')
if __name__=='__main__':
    main()
