# Lowered upper bounds for n = 262 (side 16.699693441904) and n = 295 (side 17.699693441716): registration request

This file follows the result registration template of the Squares Project (`.github/ISSUE_TEMPLATE/result-registration.md` in jlevy/squares).

**Credit name.** Joost de Winter, Delft University of Technology.

**Claim.** Two packings, each rounded up at 12 places. The record values are those at commit f9ddfeeef9070ede581142154ab992149b278ab0 of jlevy/squares.

| n | side | exact rational side | record | gain |
| ---: | ---: | :--- | ---: | ---: |
| 262 | 16.699693441904 | 166996934419035177/10000000000000000 | 16.70710678118655 (16 + sqrt(2)/2) | 0.00741 |
| 295 | 17.699693441716 | 35399386883430443/2000000000000000 | 17.70423279073603036 ((22 + 22 sqrt(2))/3) | 0.00454 |

**Certificate.** Exact rational coordinates of all squares and the side, in the folders `n262` and `n295` of https://github.com/JoostdeWinter/square-packing at commit 853b92ee2236f418160782dd2871d38ea75271a4. Later commits leave these files unchanged.

- `n262/n262_exact.json`, `n295/n295_exact.json` (centre and unit edge direction of each square)
- `n262/n262_witness.yaml`, `n295/n295_witness.yaml` (the same packings as Witness/v2 files, corners, rational)

Figures are in `n262/n262_record.png` and `n295/n295_record.png`.

**Checking.**

1. `verify_exact.py` in each folder. Arithmetic: Python `fractions.Fraction`. It checks that every edge direction is a unit vector, that every square lies in the container, and that every pair of squares with centres closer than sqrt(2) is separated along an edge direction of one of the two squares. It reports 558 close pairs for n = 262 and 626 for n = 295.
2. `check_area.py` in each folder. Arithmetic: Python `fractions.Fraction`. It clips one square of each close pair against the other and requires an intersection of area exactly 0. Same pair counts.
3. `packing/devtools/check_rational_witness_independent.py` of jlevy/squares at the commit named under Claim. It reports "VERIFIED: 262 squares, 34191 pairs" and "VERIFIED: 295 squares, 43365 pairs".
4. Both witness files validate against `packing/witnesses/witness.schema.yaml` of jlevy/squares at the same commit (jsonschema, 0 errors).
5. A further exact checker, written separately, compared each side with the irrational record side in exact arithmetic (2(s - 16)^2 < 1 for n = 262, (3s - 22)^2 < 968 for n = 295).

Each check takes a few seconds on one core.

**Construction.** A band of 72 squares, tilted by 25 to 30 degrees and arranged 4 squares wide and 18 long, runs along the diagonal. The other squares are axis-aligned (190 for n = 262, 223 for n = 295). An integer program placed the axis-aligned squares, a numerical optimization followed, and the result was rounded to exact rational coordinates. No coordinates of other packings were used. The packing for n = 295 is the packing for n = 262 with an L-shaped border of 33 axis-aligned squares, so its side is larger by exactly 1.

**Not done.** No local optimality test. The packings show small gaps, so a further small reduction of the sides is likely possible. A proof of local or global optimality is missing.

**AI assistance.** The construction, the search and the rational certificates were produced with Gemini Carbon (Google). The conversion to the witness format and the checks were run with Claude (Anthropic). Both worked under my direction.
