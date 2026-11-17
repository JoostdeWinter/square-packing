# Lowered upper bound for n = 268 (side 16.870013850405): registration request

This file follows the result registration template of the Squares Project (`.github/ISSUE_TEMPLATE/result-registration.md` in jlevy/squares).

**Credit name.** Joost de Winter, Delft University of Technology.

**Claim.** A packing of 268 unit squares in a square of side 16.870013850405 (rounded up at 12 places). The exact rational side is in `n268/n268_exact.json`. The case page https://squaremath.org/cases/268.html lists 16.87202984908445 (witness n-268 at jlevy/squares commit f9ddfeeef9070ede581142154ab992149b278ab0) on 17 November 2026. The gain is 0.0020.

**Certificate.** Exact rational coordinates of all 268 squares and the side, in the folder `n268` of https://github.com/JoostdeWinter/square-packing at commit a1ba5019e787e407646293d7bef81d63c9951b32. Later commits leave these files unchanged.

- `n268/n268_exact.json` (centre and unit edge direction of each square)
- `n268/n268_witness.yaml` (the same packing as a Witness/v2 file, corners, rational)

A figure of the packing is in `n268/n268_record.png`.

**Checking.**

1. `n268/verify_exact.py`. Arithmetic: Python `fractions.Fraction`. It checks that every edge direction is a unit vector, that every square lies in the container, and that every pair of squares with centres closer than sqrt(2) is separated along an edge direction of one of the two squares. It reports 268 squares and 620 close pairs. Command: `python3 -B verify_exact.py` in the folder `n268`. Cost: a few seconds on one core.
2. `n268/check_area.py`. Arithmetic: Python `fractions.Fraction`. It clips one square of each close pair against the other and requires an intersection of area exactly 0. It reports 268 squares and 620 close pairs. Command: `python3 -B check_area.py` in the folder `n268`. Cost: a few seconds on one core.

**What the checkers share.** The two scripts have one author, use Python's `Fraction` type and read the same input file. They share no code. The first uses a separating-axis test and the second uses the area of the clipped intersection. The witness file has not yet been run through the project's own checker.

**Not done.** No test of local optimality was run, and a proof of optimality is missing. Mykhailo Polkovskyi filed an exact certificate at 16.871868135 (issue #1009, 16 November 2026). This packing is 0.0019 below it. On the Kaggle per-puzzle leaderboard of "Squares in Squares" (notebook version 370726548), the team Thinking inside the box reported 16.870013850412470 for n = 268 (15 November 2026). This packing is 8.0e-12 below that value, so the two packings probably reach the same local optimum. Their coordinates were not found.

**Lineage and credit.** The search divided the container into nine diagonal slices and filled each slice from a transformed copy of a published packing: the first two and the last four slices from 302 squares, the third from 153 and the fourth and fifth from 129. In order along the diagonal the slices hold 8, 22, 40, 42, 60, 48, 30, 16 and 2 squares. A local optimization of all positions and angles and a rational enclosure followed. The inputs came from the public Kaggle compilations of Navneet Prabhat (129 and 153 squares) and Danil Malyshev (302 squares) and from Francisco Couzo's certificate (302 squares). The Squares Project credits Dmitry Ostashev at 129 and PingYou Ltd at 153 and 302. Please credit the new bound to Joost de Winter. The slices come from packings by Ostashev (129) and PingYou Ltd (153, 302), through the compilations of Prabhat, Malyshev and Couzo.

**AI assistance.** The search, optimization and rational certificate were produced with GPT-6.2 Sol (OpenAI). The repository files, checks and figure were produced with Claude (Anthropic). Both worked under my direction.
