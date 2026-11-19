"""
Independent Standalone Witness/v2 Rational Checker (`check_witness.py`)
=======================================================================
Written completely apart from `verify_exact.py` and `sis_engine.py`:
  - Parses `Witness/v2` YAML directly using only Python standard library (`fractions.Fraction`, `re`).
  - Verifies with ZERO floating-point operations, ZERO tolerance, and ZERO distance filtering:
      1. Header `n` matches exact number of squares.
      2. Every square has 4 rational corners `(c0, c1, c2, c3)` forming an exact unit square (`|e0|^2 = 1`,
         `|e1|^2 = 1`, `e0 . e1 = 0`, `det(e0, e1) = +1`, `c2 = c0 + e0 + e1`).
      3. Every corner lies in `[0, side] x [0, side]` over `Q`.
      4. Every one of the `n*(n-1)/2` unordered square pairs has strictly disjoint closed squares
         (strict separating axis gap `> 0` over `Q`).
  - Also runs 3 negative-control tamper tests (side lowered, duplicate square, corner perturbed by 1e-30)
    to prove the checker rejects invalid certificates.
"""

from fractions import Fraction
import hashlib
import sys


def parse_witness_v2_yaml(path: str):
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()
    sha256 = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    n_val = None
    side_val = None
    squares = []
    cur_corners = None

    for line in raw.splitlines():
        s = line.strip()
        if s.startswith("n:"):
            n_val = int(s.split(":", 1)[1].strip())
        elif s.startswith("side:"):
            tok = s.split(":", 1)[1].strip().strip("'\"")
            side_val = Fraction(tok)
        elif s.startswith("- id:"):
            if cur_corners is not None:
                squares.append(cur_corners)
            cur_corners = []
        elif s.startswith("- [") and cur_corners is not None:
            inner = s[s.index("[") + 1 : s.rindex("]")]
            a_str, b_str = [p.strip().strip("'\"") for p in inner.split(",")]
            cur_corners.append((Fraction(a_str), Fraction(b_str)))
    if cur_corners is not None:
        squares.append(cur_corners)
    return n_val, side_val, squares, sha256


def check_exact(n_val: int, side: Fraction, squares: list):
    if len(squares) != n_val:
        return False, f"count mismatch {len(squares)} != {n_val}", 0
    axes = []
    for i, pts in enumerate(squares):
        if len(pts) != 4:
            return False, f"sq {i} corners != 4", 0
        c0, c1, c2, c3 = pts
        e0 = (c1[0] - c0[0], c1[1] - c0[1])
        e1 = (c3[0] - c0[0], c3[1] - c0[1])
        if e0[0] * e0[0] + e0[1] * e0[1] != 1:
            return False, f"sq {i} |e0|^2 != 1", 0
        if e1[0] * e1[0] + e1[1] * e1[1] != 1:
            return False, f"sq {i} |e1|^2 != 1", 0
        if e0[0] * e1[0] + e0[1] * e1[1] != 0:
            return False, f"sq {i} e0.e1 != 0", 0
        if e0[0] * e1[1] - e0[1] * e1[0] != 1:
            return False, f"sq {i} orientation det != 1", 0
        if (c0[0] + e0[0] + e1[0], c0[1] + e0[1] + e1[1]) != c2:
            return False, f"sq {i} c2 mismatch", 0
        for px, py in pts:
            if px < 0 or px > side or py < 0 or py > side:
                return False, f"sq {i} outside [0, side]^2", 0
        axes.append((e0, e1))

    pairs_tested = 0
    for i in range(n_val):
        pi = squares[i]
        ai0, ai1 = axes[i]
        i0_lo = min(ai0[0] * x + ai0[1] * y for x, y in pi)
        i0_hi = max(ai0[0] * x + ai0[1] * y for x, y in pi)
        i1_lo = min(ai1[0] * x + ai1[1] * y for x, y in pi)
        i1_hi = max(ai1[0] * x + ai1[1] * y for x, y in pi)
        for j in range(i + 1, n_val):
            pairs_tested += 1
            pj = squares[j]
            # Test 4 axes; strictly disjoint iff at least one axis has strict gap > 0!
            jp0 = [ai0[0] * x + ai0[1] * y for x, y in pj]
            if min(jp0) > i0_hi or max(jp0) < i0_lo:
                continue
            jp1 = [ai1[0] * x + ai1[1] * y for x, y in pj]
            if min(jp1) > i1_hi or max(jp1) < i1_lo:
                continue
            aj0, aj1 = axes[j]
            j0_lo = min(aj0[0] * x + aj0[1] * y for x, y in pj)
            j0_hi = max(aj0[0] * x + aj0[1] * y for x, y in pj)
            ip0 = [aj0[0] * x + aj0[1] * y for x, y in pi]
            if min(ip0) > j0_hi or max(ip0) < j0_lo:
                continue
            j1_lo = min(aj1[0] * x + aj1[1] * y for x, y in pj)
            j1_hi = max(aj1[0] * x + aj1[1] * y for x, y in pj)
            ip1 = [aj1[0] * x + aj1[1] * y for x, y in pi]
            if min(ip1) > j1_hi or max(ip1) < j1_lo:
                continue
            return False, f"pair ({i}, {j}) not disjoint", pairs_tested

    return True, "VALID", pairs_tested


if __name__ == "__main__":
    ypath = sys.argv[1]
    n_val, side, squares, sha = parse_witness_v2_yaml(ypath)
    RECORDS_Q = {
        232: Fraction(15759531627556573, 1000000000000000),
        262: Fraction("16.707106781186547"),
        270: Fraction("16.928148603340"),  # stricter of STATUS.md (16.928148603343) and open Issue #1009 (16.928148603340)
        292: Fraction(4397844536374424539902715795867, 250000000000000000000000000000),
        295: Fraction("17.704232790736"),
    }
    rec_frac = RECORDS_Q[n_val]
    ok, msg, n_pairs = check_exact(n_val, side, squares)
    diff_exact = side - rec_frac
    print(f"Independent check_witness.py on {ypath}:")
    print(f"  Result:            {msg} (ok={ok}, pairs_tested={n_pairs})")
    print(f"  Exact side < rec:  {diff_exact < 0} (side - record = {float(diff_exact):.10e})")
    print(f"  SHA-256:           {sha}")

    # Negative-control tamper tests (must all be REJECTED!)
    ok_t1, m1, _ = check_exact(n_val, side - Fraction(1, 10**10), squares)
    sq_dup = list(squares); sq_dup[1] = sq_dup[0]
    ok_t2, m2, _ = check_exact(n_val, side, sq_dup)
    sq_bad = [list(pts) for pts in squares]; sq_bad[0][0] = (sq_bad[0][0][0] + Fraction(1, 10**30), sq_bad[0][0][1])
    ok_t3, m3, _ = check_exact(n_val, side, sq_bad)
    print(f"  Tamper tests refused: side_lowered={not ok_t1} ({m1}), overlap={not ok_t2} ({m2}), bad_unit_sq={not ok_t3} ({m3})")
    assert ok and diff_exact < 0 and (not ok_t1) and (not ok_t2) and (not ok_t3)
