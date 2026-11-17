# Raised lower bound for n = 108 and n = 109 (side 10.630037940829): registration request

**Credit name.** Joost de Winter, Delft University of Technology, after Hiroaki Hosono.

**Claim.** s(108) >= 1700799526134255846599/159999384348528500000 = 10.630037940829... (rounded down at 12 places). The same bound holds for s(109), because a packing of 109 squares contains a packing of 108. The case page https://squaremath.org/cases/108.html lists the lower bound 10.62 (T-216, Hiroaki Hosono) on 17 November 2026. The gain is 0.0100 for both counts.

**Certificate.** Folder `lower_n108` of https://github.com/JoostdeWinter/square-packing at commit cc20a26845789c2502950041c26709eda8a71081. Later commits leave these files unchanged.

- `lower_n108/proof_n108.pdf`: the proof (one page).
- `lower_n108/evidence/n108_measure.json.gz`: Hosono's measure with every rectangle coordinate multiplied by 1063/1062 and every mass kept. Total mass 107.99999 in a square of side 10.63, 823 rectangle orbits under the eight symmetries of the square.
- `lower_n108/evidence/direction_runs/`: the unmodified outputs of `sqverify_fast` (jlevy/squares at commit f9ddfeeef9070ede581142154ab992149b278ab0, format M, per-bin centre domains) for 401 directions with half-angle tangents r·83/80000, r = 0, …, 400, and core side 0.99896. Every direction has verdict "verified". Together the runs visited 266,337,510 branch-and-bound nodes.

**Argument.** For each direction the verifier certifies that every closed square of side 0.99896 at that direction, with its centre in the certified range, captures mass at least one. Any unit square contains such a core at the nearest grid direction. A packing of 108 unit squares in the claimed side, scaled and translated into the square of side 10.63, therefore gives 108 cores with disjoint interiors that each capture mass at least one, for a total of at least 108. The total mass is 107.99999, so no such packing exists. The scaling step gives the small enlargement from 10.63 to the claimed side. Details are in `proof_n108.pdf`.

**Checking.**

1. `lower_n108/check_lower.py`. Arithmetic: Python `fractions.Fraction`. It rebuilds the rescaled measure from Hosono's file, checks the input and source hashes in every receipt, requires exactly one verified record for every direction 0–400, integrates all eight images of every rectangle at the axis direction independently (minimum capture 1.007478833692, and 0.997404045355 after reducing every mass by 1%), and checks the final rational enlargement. Command: `python3 check_lower.py` in the folder `lower_n108`. Cost: under a minute on one core.
2. `lower_n108/replay_lower.sh`. It builds `sqverify_fast` from the bundled source and recomputes all 401 directions, then runs the audit. Cost: several CPU hours.

**Not done.** The archived direction runs were produced by the project's verifier, but the full replay has not been repeated independently. The bound is not claimed to be close to optimal.

**Lineage and credit.** The measure is Hiroaki Hosono's (T-216). The new parts are the spatial rescaling by 1063/1062, the finer direction grid with 401 directions and core side 0.99896, the new verifier runs and the rational enlargement. Please credit the bound to Joost de Winter, after Hiroaki Hosono.

**AI assistance.** The rescaling, the computation and the proof were produced with GPT-6.2 Astra (OpenAI). The repository files and checks were produced with Claude (Anthropic). Both worked under my direction.
