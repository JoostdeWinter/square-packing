"""Expand all listed chains and check every square with exact integer arithmetic.

Run python verify_multi.py. To export one set of poses, run
python verify_multi.py --poses 2036 packing-2036.json.
"""
import argparse
import csv
import gzip
import hashlib
import json
from collections import defaultdict, deque
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

HERE=Path(__file__).resolve().parent
F=10**10
L=10000000020
D=F*F
T=10**12
CELL=F*L

@lru_cache(maxsize=20000)
def orientation(p):
    c, s, q = T*T-p*p, 2*T*p, T*T+p*p
    # Vertex offsets in units of 1/(2q). h is rounded outward in center units.
    h = ((abs(c)+abs(s))*D+2*q-1)//(2*q)
    return c,s,q,h,((c-s,s+c),(c+s,s-c),(-c+s,-s-c),(-c-s,-s+c))


def face_separates(dx,dy,u,v,qa,qb,vertices):
    center_dot = u*dx+v*dy
    if center_dot < 0:
        center_dot,u,v = -center_dot,-u,-v
    center_margin = (2*center_dot-D*qa)*qb
    if center_margin < 0:
        return False
    return all(center_margin+D*(u*cx+v*cy) >= 0 for cx,cy in vertices)


def intersects(dx,dy,a,b):
    ca,sa,qa,ha,va = a
    cb,sb,qb,hb,vb = b
    if abs(dx)>=ha+hb or abs(dy)>=ha+hb:
        return False
    if sa==0 and sb==0:
        return True
    return not (face_separates(dx,dy,ca,sa,qa,qb,vb)
                or face_separates(dx,dy,-sa,ca,qa,qb,vb)
                or face_separates(-dx,-dy,cb,sb,qb,qa,va)
                or face_separates(-dx,-dy,-sb,cb,qb,qa,va))


def verify(poses,side):
    # Two center x or y coordinates separated by 1.415 exceed sqrt(2),
    # so their closed squares cannot intersect. Sweep in increasing x and
    # maintain a queue of recent centers for each horizontal unit strip.
    band = (1415*D+999)//1000
    queues = defaultdict(deque)
    comparisons = 0
    for x,y,p in sorted(poses,key=lambda s:s[0]):
        geom = orientation(p)
        if min(x,y,side-x,side-y)<geom[3]:
            raise ValueError("square crosses a wall")
        for row in range((y-band)//D,(y+band)//D+1):
            queue = queues[row]
            while queue and x-queue[0][0]>band:
                queue.popleft()
            for xx,yy,g in queue:
                comparisons += 1
                if intersects(x-xx,y-yy,g,geom):
                    raise ValueError(f"interior intersection at centers {(xx,yy)} and {(x,y)}")
        queues[y//D].append((x,y,geom))
    return comparisons


def controls():
    # Rational orientation (3/5,4/5), an exact edge contact, and an
    # inward displacement of one unit in the encoded center coordinates.
    a = orientation(T//2)
    u = orientation(0)
    checks=(not intersects(3*D//5,4*D//5,a,a),
            intersects(3*D//5-1,4*D//5-1,a,a),
            intersects(0,0,a,u), not intersects(D,0,u,u))
    if not all(checks):
        raise ValueError("intersection controls failed")
    verify([(7*D//10,7*D//10,T//2)],2*D)
    try:
        verify([(7*D//10-1,7*D//10,T//2)],2*D)
    except ValueError:
        return
    raise ValueError("wall control failed")


def grid(w,h,x0,y0):
    return [(x0+i*CELL+CELL//2,y0+j*CELL+CELL//2,0)
            for j in range(h) for i in range(w)]


def pad(pts,a,b,w,h,f):
    if w<a or h<b:
        raise ValueError("invalid extension")
    return (list(pts)+grid(w-a,b,a*CELL+f,0)
            +grid(w,h-b,0,b*CELL+f))


def materialize(row,lib):
    n,k=int(row["n"]),int(row["k"])
    recipe=[tuple(map(int,entry.split(","))) for entry in row["chain"].split("|")]
    f=max(lib[str(key//2)]["f"] for key,_,_ in recipe)*L
    A,B,surplus,clear=0,0,0,True
    pts=[]
    for key,w,h in recipe:
        block=lib[str(key//2)]
        a,b,s=block["a"],block["b"],block["e"]
        local=block["poses"]
        if len(local)!=a*b+s or not clear:
            raise ValueError("bad component count or occupied assembly corner")
        if key%2:
            a,b=b,a
            local=[(y,x,-p) for x,y,p in local]
        local=pad(local,a,b,w,h,f)
        pts.extend((x+A*CELL,y+B*CELL,p) for x,y,p in local)
        pts.extend(grid(A,h,0,B*CELL+f))
        pts.extend(grid(w,B,A*CELL+f,0))
        A,B,surplus=A+w,B+h,surplus+s
        clear=bool(block["notch"]) or w>a or h>b
    pts=pad(pts,A,B,k,k,f)
    if len(pts)!=k*k+surplus or len(pts)<n:
        raise ValueError("wrong capacity")
    side=k*CELL+f
    if Fraction(side,D)!=Fraction(row["upper"]) or Fraction(side,D)>=Fraction(row["comparison_floor"]):
        raise ValueError("side or record mismatch")
    return side,pts[:n]


def main():
    args=argparse.ArgumentParser(description=__doc__)
    args.add_argument("--poses",nargs=2,metavar=("N","JSON"))
    options=args.parse_args()
    controls()
    with gzip.open(HERE/"blocks.json.gz","rt") as handle:
        lib=json.load(handle)
    with (HERE/"bounds.csv").open(newline="") as handle:
        rows=list(csv.DictReader(handle))
    if len({r["n"] for r in rows})!=len(rows):
        raise ValueError("duplicate counts")
    if options.poses:
        rows=[r for r in rows if int(r["n"])==int(options.poses[0])]
        if not rows:
            raise ValueError("count absent")
    count=pairs=0
    for row in rows:
        side,pts=materialize(row,lib)
        try:
            pairs+=verify(pts,side)
        except ValueError as exc:
            raise ValueError(f'n={row["n"]}: {exc}') from exc
        count+=len(pts)
        if options.poses:
            Path(options.poses[1]).write_text(json.dumps(
                dict(n=len(pts),side=row["upper"],center_denominator=D,
                     tangent_half_angle_denominator=T,poses=pts)))
    print(f"PASS. {len(rows)} expanded chain packings, {count} unit squares, "
          f"{pairs} sweep-line comparisons. Six geometry controls passed.")
    for name in ("blocks.json.gz","bounds.csv"):
        print(name,"SHA-256",hashlib.sha256((HERE/name).read_bytes()).hexdigest())


if __name__=="__main__":
    main()
