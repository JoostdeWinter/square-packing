# Lower bound for n = 20

Twenty unit squares, each free to move and rotate, cannot fit in a closed square of side 99/20. By compactness, s(20) > 99/20 = 4.95. Four rows of five give s(20) <= 5.

`PROOF.md` gives the argument. Twenty-two marked points from Figure 3 of Wolfram Bentz (arXiv:1606.03746), scaled by 99/100, lie in the board so that every unit square contains a mark in its concentric square of side 1 - 1/100000. Each square is assigned the nearest mark, which leaves two marks unassigned. The 231 choices of the unassigned pair fall into 67 classes under the two reflections of the board. Every class is excluded with the exact pose-exclusion software of Mira Cult's 18-square proof (github.com/Mira-Cult/math at 78bec6aacebf304d942a9225e16c2f18165778ff), with 75 terminal regions in all.

## Files

- `n20.py`: the complete program. `python3 n20.py` checks the angle cover, rebuilds the case tree, replays every exclusion and writes the archive. `python3 n20.py --cases n20_certificate.json` replays the stored tree. It downloads the pinned Mira Cult sources and checks their Git blob hashes (Python 3.10+, g++ with C++17).
- `n20_certificate.json`: the case tree.
- `n20_verdicts.json`: the verdict of every terminal region.
- `n20_receipt.json`: summary (67 classes, 75 regions, verdict SHA-256 bd1877fc8a8348ed0f36a18f5827371f6ef0732828ac55dac4461aeb258f3048).
- `n20_orientation_intervals.json`: the 17 angle intervals of the independent cover check.
- `replay_log.txt`: output of a complete fresh run of `n20.py` on 20 November 2026 (2 cores, about 2 minutes).
- `PROOF.md`: the written proof and the original program text.

## Credit and AI assistance

Research direction: Joost de Winter. The application to twenty squares and the certificate search were produced with GPT-6.2 Astra (OpenAI). The fresh replay and repository files were produced with Claude (Anthropic). Marks: Wolfram Bentz. Exclusion software: Mira Cult.
