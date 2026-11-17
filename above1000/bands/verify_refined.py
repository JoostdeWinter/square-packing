"""Exact verification and optional coordinate expansion for the filled-band refinements.
Usage: python verify_refined.py refined.csv [--write 3891 n3891.cert]
All calculations concerning geometry and acceptance use fractions.Fraction.
"""
import argparse
import csv
from fractions import Fraction as Q

if not __debug__:
    raise RuntimeError("Run without Python optimization so assertions remain enabled.")

def shape(text):
    r, a, b = text.split(':')
    unpack = lambda x: [] if x == '' else list(map(int, x.split(',')))
    return int(r), unpack(a), unpack(b)

def inspect_band(width, t, length, pattern):
    row_count, near, far = pattern
    assert width >= 1 and row_count >= 1 and 0 < t < 1
    cos = (1 - t*t)/(1+t*t)
    sin = 2*t/(1+t*t)
    assert cos*cos + sin*sin == 1
    span_x = width*cos + sin
    row_height = width*sin + cos
    free = length - (row_count-1)/cos - row_height
    assert free >= 0
    # The upper left corner of an i-th fill level must lie below the
    # lower supporting edge passing through (sin, near_lift).
    # Reflection about the strip rectangle's centre handles the far end.
    def required(counts):
        y = Q(0)
        for i,m in enumerate(counts):
            assert 0 < m <= span_x
            y = max(y, i+1-(span_x-m-sin)*sin/cos)
        return y
    y0 = required(near)
    assert required(far) <= free-y0
    for levels, height in ((near, y0),(far, free-y0)):
        for i,m in enumerate(levels):
            assert i+1 <= height+(span_x-m-sin)*sin/cos
    return width*row_count+sum(near)+sum(far), span_x, y0

def band_points(width, t, length, pattern, y0):
    row_count, near, far = pattern
    cos = (1-t*t)/(1+t*t)
    sin = 2*t/(1+t*t)
    span_x = width*cos+sin
    h = Q(1,2)
    for j in range(row_count):
        for i in range(width):
            yield (sin+(i+h)*cos-h*sin, y0+j/cos+(i+h)*sin+h*cos, t)
    for reverse, counts in ((False, near), (True, far)):
        for i,m in enumerate(counts):
            for j in range(m):
                x, y = span_x-m+j+h, i+h
                yield (span_x-x,length-y,0) if reverse else (x,y,0)

def verify(row, expand=False):
    n, k, bv, bh = (int(row[key]) for key in ('n','K','bV','bH'))
    tv, th, s = (Q(row[key]) for key in ('tV','tH','side_exact'))
    v, h = shape(row['V']), shape(row['H'])
    assert k>max(bv,bh) and n>0
    nv, wv, yv = inspect_band(bv,tv,s,v)
    nh, wh, yh = inspect_band(bh,th,Q(k-bv),h)
    assert k-bv+wv <= s and k-bh+wh <= s
    capacity = (k-bv)*(k-bh)+nv+nh
    assert capacity == int(row['capacity']) and capacity>=n
    assert s < Q(row["comparison_side"])
    assert s<=Q(row['side_up']) < s+Q(1,10**12)
    if not expand: return
    grid=[(i+Q(1,2),j+Q(1,2),0) for i in range(k-bv) for j in range(k-bh)]
    sq=grid+[(k-bv+x,y,t) for x,y,t in band_points(bv,tv,s,v,yv)]
    sq.extend((y,k-bh+x,-t) for x,y,t in band_points(bh,th,Q(k-bv),h,yh))
    return s,sq[-n:]

def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('csv')
    cli.add_argument('--write',nargs=2,metavar=('N','FILE'))
    args=cli.parse_args()
    seen=set()
    with open(args.csv, newline='') as stream:
        for row in csv.DictReader(stream):
            n=int(row['n'])
            assert n not in seen
            seen.add(n)
            selected = bool(args.write) and n==int(args.write[0])
            outcome=verify(row,selected)
            if selected:
                side, points = outcome
                with open(args.write[1],'w') as f:
                    print('# Refinement of Karimi filled-end construction',file=f)
                    print(n,side,file=f)
                    for x,y,t in points: print(x,y,t,file=f)
    if args.write and int(args.write[0]) not in seen: raise ValueError('Count is absent')
    print(f'PASS: {len(seen)} distinct packings. Exact dimensions, band separation, end fills and count verified.')
if __name__=='__main__': main()
