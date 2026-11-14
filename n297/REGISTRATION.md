# Lowered upper bound for n = 297 (side 17.739455558289): registration request

This file follows the result registration template of the Squares Project (`.github/ISSUE_TEMPLATE/result-registration.md` in jlevy/squares).

**Credit name.** Joost de Winter, Delft University of Technology.

**Claim.** A packing of 297 unit squares in a square of side 17.739455558289 (rounded up at 12 places). The exact rational side is in the certificate. The record holds 17.740417287543801851 for n = 297 (T-174) at commit 7629f5adede4c38f006e355281ea76340120fd94 of jlevy/squares. The gain is 0.00096.

**Certificate.** Exact rational coordinates of all 297 squares (centre and unit edge direction) and the side, in this folder of https://github.com/JoostdeWinter/square-packing at commit 7b4701f35e815301e4f467d214fab4205ded5eb1. Later commits leave these files unchanged.

- `n297/n297_exact.json`
- `n297/n297_witness.yaml` (the same packing as a Witness/v2 file, center-basis, rational)

A figure of T-174 and the new packing side by side is in `n297/n297_before_after.png`.

**Checking.**

1. `n297/verify_exact.py`. Arithmetic: Python `fractions.Fraction`. It checks that every edge direction is a unit vector, that every square lies in the container, and that every pair of squares with centres closer than sqrt(2) is separated along an edge direction of one of the two squares. It reports 297 squares and 632 close pairs. Command: `python3 -B verify_exact.py` in the folder `n297`. Cost: about 2 seconds on one core.
2. `n297/check_area.py`. Arithmetic: Python `fractions.Fraction`. It clips one square of each close pair against the other and requires an intersection of area exactly 0. It reports 297 squares and 632 close pairs. Command: `python3 -B check_area.py` in the folder `n297`. Cost: about 1 second on one core.
3. The witness file validates against `packing/witnesses/witness.schema.yaml` of jlevy/squares at the commit named above (jsonschema, 0 errors).

**What the checkers share.** One author, Python's `Fraction` type and the same input file. The two scripts share no code. The first uses a separating-axis test and the second uses the area of the clipped intersection.

**Not done.** The certificate has not been checked with the tools of the Squares Project. The statement that the packing is a local optimum of its arrangement rests on numerical work: two series of random restarts ended at the same side, a linear program over all 297 squares found no first-order improvement, and the rational side is 1.8e-59 above the 330-digit solution of the 4289 contact equations. A proof of local or global optimality is missing.

**Lineage and credit.** The layout is that of T-174 (found by Francisco Couzo, improved by Evan Daniel and PingYou Ltd): two blocks of axis-aligned squares with staircase edges, two corner blocks of 10 squares, and a diagonal band of 18 columns of tilted squares. Two things are new. First, each staircase has two steps of double size. Between them the band lies one staircase step closer to the upper left block, and a column of 7 squares sits at each double step. The upper left block has 6 squares fewer than in T-174, the lower right block has 4 more, and the band has 2 more. Second, the band columns change lean direction once, where T-174 changes three times. The double step was taken from the staircases of the pinwheel packings T-292 and T-293 (n = 132 and n = 157). Please credit the result to Joost de Winter as a packing that builds on T-174.

**AI assistance.** The construction, optimization, high-precision solution, rational certificate, checks and figures were produced with Claude Fable 5.2 (Anthropic) under my direction.
