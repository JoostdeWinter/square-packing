"""Check every expanded packing using exact corner projections and a sweep line.

Run python check_expanded.py. The geometry verifier is independent of the
component verifier. It uses the catalogue's expansion function and reads the
input format's two denominator constants. Requires only Python 3.8 or newer.
"""
import csv
import hashlib
from collections import defaultdict, deque
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from verify import blocks, construction, D, T

HERE = Path(__file__).resolve().parent


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


def main():
    controls()
    path=HERE/"bounds.csv"
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    with path.open(newline="") as f:
        rows=list(csv.DictReader(f))
    if len({int(row["n"]) for row in rows})!=len(rows):
        raise ValueError("repeated count")
    library=blocks()
    count=comparisons=0
    for row in rows:
        n=int(row["n"])
        side,poses=construction(row,library,expand=True)
        if len(poses)!=n or Fraction(side,D)!=Fraction(row["upper"]):
            raise ValueError(f"wrong number or side at n={n}")
        try:
            comparisons+=verify(poses,side)
        except ValueError as exc:
            raise ValueError(f"n={n}: {exc}") from exc
        count+=n
    if hashlib.sha256(path.read_bytes()).hexdigest()!=digest:
        raise RuntimeError("catalogue changed during verification")
    print(f"PASS. {len(rows)} expanded packings, {count} unit squares, "
          f"{comparisons} sweep-line comparisons. Six geometry controls passed.")
    print(f"bounds.csv SHA-256 {digest}")


if __name__=="__main__":
    main()
