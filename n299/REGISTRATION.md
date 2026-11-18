# Lowered upper bound for n = 299 (side 17.793636991744): registration request

This file follows the result registration template of the Squares Project (`.github/ISSUE_TEMPLATE/result-registration.md` in jlevy/squares).

**Credit name.** Joost de Winter, Delft University of Technology.

**Claim.** A packing of 299 unit squares in a square of side 17.793636991744 (rounded up at 12 places). The exact rational side is in `n299/n299_exact.json`. The case page https://squaremath.org/cases/299.html lists 17.801004434255294 (T-277, Doğa Özden after Evan Daniel) on 18 November 2026. The gain is 0.0074.

**Certificate.** Exact rational coordinates of all 299 squares and the side, in the folder `n299` of https://github.com/JoostdeWinter/square-packing at commit 497eb478b790175ea8690671b66785b70c97f9f2. Later commits leave these files unchanged.

- `n299/n299_exact.json` (centre and unit edge direction of each square)
- `n299/n299_witness.yaml` (the same packing as a Witness/v2 file, corners, rational)

A figure of the packing is in `n299/n299_record.png`.

**Checking.**

1. `n299/verify_exact.py`. Arithmetic: Python `fractions.Fraction`. It checks that every edge direction is a unit vector, that every square lies in the container, and that every pair of squares with centres closer than sqrt(2) is separated along an edge direction of one of the two squares. It reports 299 squares and 714 close pairs. Command: `python3 -B verify_exact.py` in the folder `n299`. Cost: a few seconds on one core.
2. `n299/check_area.py`. Arithmetic: Python `fractions.Fraction`. It clips one square of each close pair against the other and requires an intersection of area exactly 0. It reports 299 squares and 714 close pairs. Command: `python3 -B check_area.py` in the folder `n299`. Cost: a few seconds on one core.

**What the checkers share.** The two scripts have one author, use Python's `Fraction` type and read the same input file. They share no code. The first uses a separating-axis test and the second uses the area of the clipped intersection. The witness file has not yet been run through the project's own checker.

**Not done.** No test of local optimality was run, and a proof of optimality is missing. On the Kaggle per-puzzle leaderboard of "Squares in Squares" (notebook completed 18 November 2026, 01:07:56 UTC), Nick Sarris reported 17.793636991746555 for n = 299. This packing is 3.5e-12 below that value, so the two packings are probably the same local optimum. His coordinates were not found.

**Lineage and credit.** The search divided the container into diagonal slices and filled each slice from a reflected or translated copy of a public packing: the outer slices from 372 squares and the seven middle slices from 335 squares. Both donors came from Asterios Panoras's public Kaggle compilation (version 17). Kaggle's community explorer (nevska) links the 372-square packing to prvsiyan's notebook "A Square Deal" and the 335-square packing to four notebooks with the same score, by areebbb, jazivxt, alexchilton and prvsiyan. A local optimization followed, in which the separating edges of touching pairs were exchanged. Reflecting part of one tilted group across the diagonal x + y = S and releasing the neighbouring squares gave the final gain. In the final layout 55 squares tilt at least 15 degrees one way and 54 at least 15 degrees the other way. Please credit the new bound to Joost de Winter, after the 335- and 372-square packings in Panoras's compilation (prvsiyan, areebbb, jazivxt, alexchilton).

**AI assistance.** The search, optimization and rational certificate were produced with GPT-6.2 Sol (OpenAI). The repository files, checks and figure were produced with Claude (Anthropic). Both worked under my direction.
