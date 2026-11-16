# Lowered upper bound for n = 292 (side 17.590016442847): registration request

This file follows the result registration template of the Squares Project (`.github/ISSUE_TEMPLATE/result-registration.md` in jlevy/squares).

**Credit name.** Joost de Winter, Delft University of Technology.

**Claim.** A packing of 292 unit squares in a square of side 17.590016442847 (rounded up at 12 places). The exact rational side is 33872522175917279266554668306659248043633029180856810473/1925667453806884053962316529711800854170000000000000000. The record holds 17.5913781454976982 for n = 292 (T-146) at commit f9ddfeeef9070ede581142154ab992149b278ab0 of jlevy/squares. The gain is 0.00136.

**Certificate.** Exact rational coordinates of all 292 squares and the side, in the folder `n292` of https://github.com/JoostdeWinter/square-packing at commit 796ff3b76e7816f9df24bf4f6ef0bb3b9cacef24. Later commits leave these files unchanged.

- `n292/n292_exact.json` (centre and unit edge direction of each square)
- `n292/n292_witness.yaml` (the same packing as a Witness/v2 file, corners, rational)

A figure is in `n292/n292_record.png`.

**Checking.**

1. `n292/verify_exact.py`. Arithmetic: Python `fractions.Fraction`. It checks that every edge direction is a unit vector, that every square lies in the container, and that every pair of squares with centres closer than sqrt(2) is separated along an edge direction of one of the two squares. It reports 292 squares and 668 close pairs. Command: `python3 -B verify_exact.py` in the folder `n292`. Cost: a few seconds on one core.
2. `n292/check_area.py`. Arithmetic: Python `fractions.Fraction`. It clips one square of each close pair against the other and requires an intersection of area exactly 0. It reports 292 squares and 668 close pairs. Command: `python3 -B check_area.py` in the folder `n292`. Cost: a few seconds on one core.
3. `packing/devtools/check_rational_witness_independent.py` of jlevy/squares, run on `n292/n292_witness.yaml`. It reports "VERIFIED: 292 squares, 42486 pairs".
4. The witness file validates against `packing/witnesses/witness.schema.yaml` of jlevy/squares at the commit named under Claim (jsonschema, 0 errors).

**What the checkers share.** The first two scripts have one author, use Python's `Fraction` type and read the same input file. They share no code. The first uses a separating-axis test and the second uses the area of the clipped intersection. The third checker is the project's own and reads the corners in the witness file.

**Not done.** A linear program over all 292 squares, with every contact linearized, found no first-order improvement. That test covers one set of contacts. The certificate keeps a smallest gap of 3e-12 between squares, so an exact solution of the contact equations would be smaller by an amount of that order. A proof of local or global optimality is missing. Smaller sides are known to exist without a public packing: a table of the best sides per team in the Kaggle competition "Squares in Squares" of 8 November 2026 (Samanyu-dev/squares_in_squares) lists 17.589053943368 for n = 292, for the team "Cats and boxes". A public merged submission (bestbryant/claude_code_squaresinsquares, 16 November 2026) lists 17.591378147172.

**Lineage and credit.** The packing has one continuous ribbon of 59 tilted squares along the diagonal and 233 axis-aligned squares. The ribbon extends the ribbon of 37 tilted squares in the packing of 146 squares with side 12.583782190152, which your record credits to David W. Cantrell (2025). That ribbon repeats after a shift of (5, 5). Two copies, at (0, 0) and (5, 5), share 15 squares and form the ribbon of 59. The coordinates of the 146 packing were taken from a public Kaggle notebook (sigmaborov, "Squares in Squares: certified contact polish", Apache License 2.0, as included in areebbb's "merge 28" notebook). An integer program placed the axis-aligned squares, a numerical optimization of all 292 squares followed, and the result was rounded to exact rational coordinates. The house packing for n = 292 has two separate tilted blocks of 16 and 33 squares. Please credit the new bound to Joost de Winter, as an extension of Cantrell's ribbon.

**AI assistance.** The construction and the search were run with Gemini Carbon (Google). The checking, the witness file, the figure and the comparison with other known values were produced with Claude Fable 5.2 (Anthropic). Both worked under my direction.
