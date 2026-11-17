import csv, math, sys
from fractions import Fraction as F
from pathlib import Path
from prepare import HERE, dimensions, terms, to_string
from verify_refined import verify
B = {int(x['n']): F(x['side_exact']) for x in csv.DictReader((HERE / 'comparison.csv').open())}
for x in csv.DictReader((HERE / 'recombined.csv').open()):
    n = int(x['n'])
    B[n] = min(B[n], F(x['side_exact']))
hdr = next(csv.reader((HERE / 'recombined.csv').open()))

def band(fields):
    b, p, den, R, near, far = map(int, fields)
    t = F(p, den)
    c, s, w = terms(b, t)
    if not 0 < t < 1:
        raise ValueError('angle')
    options = sorted(((max(0, F(i + 1) - b * s + m * s / c), i, m) for i in range(30) for m in range(1, int(w) + 1) if i + 1 - b * s + m * s / c <= F(32, 10)))

    def end(n):
        levels = {}
        for _, i, m in options[:n]:
            levels[i] = max(levels.get(i, 0), m)
        r = tuple((levels.get(i, 0) for i in range(len(levels))))
        assert sum(r) == n
        return r
    return (b, t, (R, end(near), end(far)))
from functools import lru_cache
band = lru_cache(None)(band)
rows = []
bad = 0
for line in open(HERE / 'endcaps.txt'):
    v = line.split()
    n, K = (int(v[0]), int(v[1]))
    sf = float(v[2])
    N = int(v[3])
    if sf > float(B[n]) - 1.001e-05:
        continue
    b, t, V = band(tuple(v[4:10]))
    bh, th, H = band(tuple(v[10:16]))
    w, L = dimensions(b, t, V)
    wh, lh = dimensions(bh, th, H)
    S = max(K - b + w, L, K - bh + wh)
    if lh > K - b or S > B[n] - F(1, 100000):
        bad += 1
        continue
    rec = dict(n=n, K=K, side_exact=str(S), side_up=f'{math.ceil(S * 10 ** 12) / 10 ** 12:.12f}', karimi_side=str(B[n]), bV=b, tV=str(t), V=to_string(V), bH=bh, tH=str(th), H=to_string(H), capacity=N)
    verify(rec)
    rows.append(rec)
with open(HERE / 'endcap_records.csv', 'w') as f:
    wri = csv.DictWriter(f, fieldnames=hdr)
    wri.writeheader()
    wri.writerows(rows)
print('count', len(rows), 'bad', bad, 'n min', [x['n'] for x in rows[:15]], 'top', sorted([(float(F(r['karimi_side']) - F(r['side_exact'])), r['n']) for r in rows], reverse=True)[:10])
