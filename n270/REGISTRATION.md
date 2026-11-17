# Lowered upper bound for n = 270 (side 16.927314216352): registration request

This file follows the result registration template of the Squares Project (`.github/ISSUE_TEMPLATE/result-registration.md` in jlevy/squares).

**Credit name.** Joost de Winter, Delft University of Technology.

**Claim.** A packing of 270 unit squares in a square of side 16.927314216352 (rounded up at 12 places). The exact rational side is in `n270/n270_exact.json`. The case page https://squaremath.org/cases/270.html lists 16.928148603342855 (witness n-270 at jlevy/squares commit f9ddfeeef9070ede581142154ab992149b278ab0) on 17 November 2026. The gain is 0.00083.

**Certificate.** Exact rational coordinates of all 270 squares and the side, in the folder `n270` of https://github.com/JoostdeWinter/square-packing at commit a1ba5019e787e407646293d7bef81d63c9951b32. Later commits leave these files unchanged.

- `n270/n270_exact.json` (centre and unit edge direction of each square)
- `n270/n270_witness.yaml` (the same packing as a Witness/v2 file, corners, rational)

A figure of the packing is in `n270/n270_record.png`.

**Checking.**

1. `n270/verify_exact.py`. Arithmetic: Python `fractions.Fraction`. It checks that every edge direction is a unit vector, that every square lies in the container, and that every pair of squares with centres closer than sqrt(2) is separated along an edge direction of one of the two squares. It reports 270 squares and 642 close pairs. Command: `python3 -B verify_exact.py` in the folder `n270`. Cost: a few seconds on one core.
2. `n270/check_area.py`. Arithmetic: Python `fractions.Fraction`. It clips one square of each close pair against the other and requires an intersection of area exactly 0. It reports 270 squares and 642 close pairs. Command: `python3 -B check_area.py` in the folder `n270`. Cost: a few seconds on one core.

**What the checkers share.** The two scripts have one author, use Python's `Fraction` type and read the same input file. They share no code. The first uses a separating-axis test and the second uses the area of the clipped intersection. The witness file has not yet been run through the project's own checker.

**Not done.** No test of local optimality was run, and a proof of optimality is missing. The best public coordinates are those of Panoras's compilation at 16.92746606488242. Danil Malyshev's coordinates in issue #1012 give 16.927469593519. This packing is 0.00015 below both. On the Kaggle per-puzzle leaderboard of "Squares in Squares" (notebook version 370726548), the team [NUP] Junie is all you need reported 16.927314216351814 for n = 270 (9 November 2026). This packing is 1.1e-13 below that value, so the two packings are probably the same local optimum. Their coordinates were not found.

**Lineage and credit.** The search started from the 270-square packing in Asterios Panoras's public Kaggle compilation (version 17, side 16.92746606488242), a merge of many contributors that does not name the finder of this arrangement. It removed and relaxed the two end regions in turn, compressed a 68-square region at the bottom inside a rectangle, reassembled the packing and optimized the position and angle of every square. Please credit the new bound to Joost de Winter, after the arrangement in Panoras's compilation.

**AI assistance.** The search, optimization and rational certificate were produced with GPT-6.2 Sol (OpenAI). The repository files, checks and figure were produced with Claude (Anthropic). Both worked under my direction.
