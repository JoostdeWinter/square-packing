"""Direct exact check of expanded rational square coordinates.
Use 'python check_coordinates.py n3891.cert' or omit files to test five sample
counts from refined.csv. Requires Python 3.9+ and only the standard library.
"""
import csv
import math
import sys
from fractions import Fraction as F
from pathlib import Path
from verify_refined import verify as expand

def direct(n,side,pts):
    if len(pts)!=n: raise ValueError('incorrect count')
    D=math.lcm(side.denominator,*(v.denominator for x,y,t in pts for v in (x,y)))
    S=int(side*D)
    cell={}
    orientations={}
    threshold={}
    compared=0
    for x,y,t in pts:
        t=F(t)
        if t not in orientations:
            a,b=t.denominator,t.numerator
            c,s,q=a*a-b*b,2*a*b,a*a+b*b
            if c*c+s*s!=q*q:raise ValueError('invalid orientation')
            orientations[t]=(c,s,q)
        c,s,q=orientations[t]
        X,Y=int(D*x),int(D*y)
        if 2*q*min(X,Y,S-X,S-Y)<D*(abs(c)+abs(s)):raise ValueError('outside')
        i,j=X//D,Y//D
        # Squares have circumradius sqrt(2)/2, so cell indices farther than
        # two apart cannot interact. Exact Cartesian bounding boxes discard
        # even more pairs, including boundary-only contacts.
        for a in range(i-2,i+3):
            for b in range(j-2,j+3):
                for U,V,h in cell.get((a,b),()):
                    C,T,Q=orientations[h]
                    dx,dy=X-U,Y-V
                    key=(t,h)
                    if key not in threshold:
                        threshold[key]=(D*((abs(c)+abs(s))*Q+(abs(C)+abs(T))*q),
                            D*(q*Q+abs(c*C+s*T)+abs(c*T-s*C)))
                    box,axis=threshold[key]
                    if 2*q*Q*max(abs(dx),abs(dy))>=box:continue
                    compared+=1
                    asep=max(abs(c*dx+s*dy),abs(c*dy-s*dx))*2*Q
                    bsep=max(abs(C*dx+T*dy),abs(C*dy-T*dx))*2*q
                    if max(asep,bsep)<axis:raise ValueError('overlapping interiors')
        cell.setdefault((i,j),[]).append((X,Y,t))
    return compared

def read(path):
    lines=[s for s in open(path) if s.strip() and not s.startswith('#')]
    n,s=lines[0].split()
    return int(n), F(s), [tuple(map(F,r.split())) for r in lines[1:]]

def main():
    if len(sys.argv)>1:
        for filename in sys.argv[1:]:
            n,s,pts=read(filename)
            print(f'PASS n={n}, {direct(n,s,pts)} pairs required rotated-axis comparisons')
        return
    tests={3891,6565,7575,9410,9805}
    path=Path(__file__).with_name('bounds.csv')
    cs=[]
    for row in csv.DictReader(path.open(newline='')):
        n=int(row['n'])
        if n not in tests:continue
        s,pts=expand(row,True)
        print(f'PASS n={n}, {direct(n,s,pts)} pairs required rotated-axis comparisons',flush=True)
        cs.append(n)
    if set(cs)!=tests:raise ValueError('missing requested samples')
    for label,p in [('count',pts[:-1]),('wall',[(F(0),F(0),0)]+pts[1:]),
                    ('duplicate',[pts[-1]]+pts[1:])]:
        try:direct(n,s,p)
        except ValueError:pass
        else:raise AssertionError('control '+label)
    print('Three controls rejected, for count, containment and overlap.')
if __name__=='__main__':main()
