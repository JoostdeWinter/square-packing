# Lowered upper bound for n = 305 (side 17.945755838742): registration request

**Credit name.** Joost de Winter, Delft University of Technology, improving the Kodaj–JoeGun arrangement.

**Claim.** A packing of 305 unit squares in a square of side 17.945755838742 (rounded up at 12 places). The exact rational side is in `n305/n305_exact.json`. The case page https://squaremath.org/cases/305.html lists 17.9457623596589697 (T-309, Tomáš Kodaj, improved by JoeGun). The gain is 6.5e-6.

**Certificate.** Exact rational coordinates of all 305 squares and the side, in the folder `n305` of https://github.com/JoostdeWinter/square-packing at commit db8efcb6bf05906e977bc62f1f6d8ccfcaa296ef. Later commits leave these files unchanged.

- `n305/n305_exact.json` (centre and unit edge direction of each square)
- `n305/n305_witness.yaml` (the same packing as a Witness/v2 file, corners, rational)

A figure is in `n305/n305_record.png`.

**Checking.**

1. `n305/verify_exact.py`. Arithmetic: Python `fractions.Fraction`. It checks unit edge directions, containment, and separation of every pair of squares with centres closer than sqrt(2) along an edge direction of one of the two squares. It reports 305 squares and 715 close pairs. Command: `python3 -B verify_exact.py` in the folder `n305`.
2. `n305/check_area.py`. Arithmetic: Python `fractions.Fraction`. It clips one square of each close pair against the other and requires an intersection of area exactly 0. It reports 305 squares and 715 close pairs. Command: `python3 -B check_area.py` in the folder `n305`.

**What the checkers share.** The two scripts read the same input file and share no code. A third check on the witness file, written separately, also found no overlaps. The witness file has not yet been run through the project's own checker.

**Not done.** No test of local optimality was run, and a proof of optimality is missing. On the Kaggle per-puzzle leaderboard of "Squares in Squares" (version 38, run 371230297), Shadoks reported 17.94575583874176 for n = 305 on 15 November 2026. This packing is 1.7e-13 below that value, so the two probably reach the same local optimum. Their coordinates were not found. The certificate is also below the project's own local re-solve of T-309 (17.945762359467513).

**Lineage and credit.** The arrangement is Tomáš Kodaj's public Kaggle packing as improved by JoeGun (T-309, two quench runs with Evan Daniel's code and a fault-line step). The search started from that arrangement in Alex Chilton's public compilation and re-optimized the positions and angles of all squares, followed by a rational enclosure. Compared with the project's regularized drawing of T-309, all 305 squares correspond under the identity symmetry: 302 move by less than 0.1, the largest move is 0.178, the RMS move is 0.018, and no tilt is reversed. Please credit the new bound to Joost de Winter as improver of the Kodaj–JoeGun arrangement.

**AI assistance.** The search, optimization and rational certificate were produced with OpenAI Codex. The repository files, checks and figure were produced with Claude (Anthropic). Both worked under my direction.
