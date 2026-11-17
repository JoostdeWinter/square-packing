import sys, csv, math, json
from fractions import Fraction as F
from pathlib import Path
from collections import defaultdict
import numpy as np
from prepare import HERE, dimensions, terms, to_string
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('refined', type=Path, help='refined.csv with original-layout Karimi improvements')
args = parser.parse_args()
from verify_refined import shape, verify
r = list(csv.DictReader(args.refined.open()))
templates = {}
for x in r:
    for v in 'VH':
        R, a, z = shape(x[v])
        b = int(x['b' + v])
        t = F(x['t' + v])
        a, z = sorted([tuple(a), tuple(z)])
        templates.setdefault((b, t, a, z), (int(x['n']), v))
ts = []
allT = []
for (b, t, a, z), prov in templates.items():
    w, l = dimensions(b, float(t), (1, a, z))
    c = terms(b, float(t))[0]
    allT.append((b, t, a, z, prov))
    ts.append((b, float(t), c, w, l, sum(a) + sum(z)))
T = np.array(ts)
bv, Tt, c, w, l, e = T.T
bv = bv.astype(int)
e = e.astype(int)
cost = bv - w

def best_options(num, score):
    if not len(num):
        return np.empty(0, dtype=int)
    idx = np.lexsort((-score, num))
    sortedn = num[idx]
    return idx[np.r_[True, np.diff(sortedn) != 0]]
res = {}
traces = {}
maxk = 100
hopt = {}
for k in range(2, maxk):
    rv = np.floor((k - l) * c + 2e-12).astype(int) + 1
    delt = bv - w
    ev = rv * bv + e - bv * k
    good = (rv >= 1) & (np.floor(w + 1e-10) >= 1) & (delt > 0)
    hv = np.flatnonzero(good)
    idx = hv[best_options(ev[good], delt[good])]
    hopt[k] = [(int(ev[j]), cost[j], j, rv[j]) for j in idx]
for k in range(6, maxk + 1):
    rv = np.floor((k - l) * c + 2e-12).astype(int) + 1
    for b in sorted(set(bv[bv < k - 1])):
        hor = hopt[k - b]
        ids = np.flatnonzero(bv == b)
        rr = np.r_[rv[ids], rv[ids] - 1]
        jj = np.tile(ids, 2)
        ds = np.minimum(cost[jj], k - (rr - 1) / c[jj] - l[jj])
        es = rr * b + e[jj] - b * k
        ok = (rr >= 1) & (ds > 1e-07)
        g = np.flatnonzero(ok)
        if not len(g):
            continue
        opt = g[best_options(es[g], ds[g])]
        for j in opt:
            for eh, dh, hi, rh in hor:
                n = k * k + int(es[j]) + eh
                dv = min(ds[j], dh)
                if n <= 0 or n > 10000 or dv <= 0:
                    continue
                old = res.get(n, (100000.0,))
                if k - dv < old[0]:
                    res[n] = (k - dv, k, jj[j], rr[j], hi, rh, n)
for n in range(9999, 0, -1):
    if n + 1 in res and res.get(n, (1000000.0,))[0] > res[n + 1][0]:
        res[n] = res[n + 1]
baseline = {int(x['n']): float(F(x['side_exact'])) for x in csv.DictReader((HERE / 'comparison.csv').open())}
ans = []
provenance = []
for n, (sf, k, iv, rv, ih, rh, capacity) in sorted(res.items()):
    if sf > baseline[n] - 1e-05:
        continue
    b, t, a, z, pv = allT[iv]
    bh, th, ah, zh, ph = allT[ih]
    V = (int(rv), a, z)
    H = (int(rh), ah, zh)
    wv, lv = dimensions(b, t, V)
    wh, lh = dimensions(bh, th, H)
    if lh > k - b:
        continue
    s = max(k - b + wv, k - bh + wh, lv)
    old = F(str(baseline[n]))
    if s > old - F(1, 100000):
        continue
    rec = dict(n=n, K=k, side_exact=str(s), side_up=f'{math.ceil(s * 10 ** 12) / 10 ** 12:.12f}', karimi_side=str(old), bV=b, tV=str(t), V=to_string(V), bH=bh, tH=str(th), H=to_string(H), capacity=int(capacity))
    verify(rec)
    ans.append(rec)
    provenance.append([n, pv[0], pv[1], ph[0], ph[1]])
with open(HERE / 'recombined.csv', 'w') as f:
    wri = csv.DictWriter(f, fieldnames=r[0].keys())
    wri.writeheader()
    wri.writerows(ans)
with open(HERE / 'recombined_sources.csv', 'w') as f:
    wr = csv.writer(f)
    wr.writerow(['n', 'original_n_vertical', 'original_role_vertical', 'original_n_horizontal', 'original_role_horizontal'])
    wr.writerows(provenance)
print('count', len(ans), 'min n', [x['n'] for x in ans[:10]], 'wins under 1000', sum((x['n'] <= 1000 for x in ans)), 'top', sorted([(float(F(x['karimi_side'])) - float(F(x['side_exact'])), x['n']) for x in ans], reverse=True)[:6])
