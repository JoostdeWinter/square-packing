# Improved upper bounds for packing unit squares

17 November 2026

This search produced exactly certified packings improving the numerical comparison for **5,186 distinct counts**, from 1,036 through 9,946 unit squares. Smaller enclosing sides are better. Each retained gain exceeds 0.00001 side units after conservative rounding. These are improvements over the public bounds and construction consequences checked on the date above. Registration and priority are separate from the geometry checks.

**Start with `records.csv`.** It contains one row per count and the smallest certified side retained in this search. `upper_exact` is the exact fraction. `upper_up_12` rounds it upward for reporting. The best directly listed side and its source are followed by the more conservative comparison actually used. The comparison column is rounded down and is used only to measure the gain. It is not a lower bound on the packing problem.

| Unit squares | Comparison used | New side, rounded upward | Gain of at least |
|---:|---:|---:|---:|
| 1,036 | 32.66663819 | 32.656497332913 | 0.01014085 |
| 1,401 | 37.88853732 | 37.864242305929 | 0.02429501 |
| 1,627 | 40.82029285 | 40.802490991005 | 0.01780185 |
| 9,217 | 96.48768435 | 96.446390290823 | 0.04129405 |
| 9,410 | 97.48768435 | 97.445070007002 | 0.04261434 |
| 9,805 | 99.50004685 | 99.459458416804 | 0.04058843 |

At 9,410 the enclosing side is exactly 100006697018701875433196096 / 1026287907756810553643689. Adding one or two upright border layers to this construction gives 9,605 and 9,802 squares with the same improvement at the displayed precision. The illustration in `examples/two_packings.png` shows the actual coordinates for 1,401 and 9,410.

## What the count includes

The search retained 5,082 distinct counts in `constructions.csv` before the final border and deletion pass. These include 4,746 packings made from two tilted bands, 145 made by joining two rectangular pieces, 10 that use locally optimized rectangular pieces, 178 made from chains of pieces and 3 made by repeating a piece. These constructions share patterns and source pieces. A final pass added 104 further counts and tightened 568 of the original counts. All 672 consequences are in `derived.csv`.

The band search preserves the integer layout of a published packing in some cases. In others it pairs band patterns from different source counts or searches for new combinations of row angles and numbers of upright squares at each end. The final angle search always retained the previous certificate when it found no tighter exact packing. `bands/provenance.csv` identifies the method and the source rows when applicable. The two-band family builds on Sungjoon Ryu’s L-shaped frame, Evan Daniel’s filled ends, Kevin Fang’s formulation, and Mohsen Karimi’s independently parameterized bands and deposited packings. [Karimi’s preprint](https://www.preprints.org/manuscript/202611.0242) · [Karimi’s source deposit](https://doi.org/10.5281/zenodo.23819397)

The rectangular methods extract pieces from publicly available coordinates and the submitted handoff. They combine the pieces with upright grids in the remaining space, sometimes after changing individual square positions and angles within a piece. Rectangular recomposition has published precedents, including Dmitry Ostashev’s constructions. The component data retain coordinate-source identifiers, reflections, and crop offsets. A dataset identifier credits the immediate coordinate source. Several participants’ compilations contain earlier contributors’ designs. [Ostashev’s constructions](https://ostashev.ai/square-packing/)

## Replaying the geometry

Use standard Python 3.9 or newer with assertions enabled. From this directory run

```sh
python verify_all.py
python export.py 9410 n9410.cert
python export.py 9410 n9410.yaml --yaml
python bands/check_coordinates.py n9410.cert
```

The exporter works for every count in the index. The `.cert` format starts with the count and exact side, followed by each center and the tangent of half its rotation angle. The YAML option writes all four corners as exact rationals. Ready-to-use coordinate certificates are in `examples/`. Boundary contact between unit squares is allowed.

Two independently implemented exact checks cover every band row. One checks the available space and the supports required by the end layers. The other reconstructs the extreme tilted rectangles and projects the fill vertices onto their separating axes. Every two-piece and multi-piece construction was expanded and checked for pairwise separation and wall containment. The full replay also checks the index, the counts, the comparison margins, the border/deletion arithmetic, and selected expanded coordinates. The output is in `verification.txt`.

Adding j border layers to a packing of n squares in side S gives a packing in side S+j. On the right, j columns each hold floor(S) upright unit squares. Across the top, j rows each hold floor(S)+j. This adds 2j floor(S)+j² squares. Removing any surplus preserves feasibility. `derived.csv` records the exact parent and the number removed.

## Where the comparisons come from

The numerical baseline combines Francisco Couzo’s and Mykhailo Polkovskyi’s large-count indices, Karimi’s two-strip and filled-end tables, the Squares Project register and issues, and public Kaggle scores and coordinates in their applicable ranges. The comparison also allows smaller packings to be repeated, extended by upright borders, joined subject to conservative corner conditions, or reduced by deletion. A published Kaggle score can therefore tighten a comparison even when its coordinates are unavailable. `comparisons/sides.csv` records the source-by-source values, `closure.csv` the tiling, border and deletion screen, and `generic.csv` the further composition screen. The numeric benchmark is a dated snapshot. [Couzo](https://github.com/franciscouzo/square-packing) · [Polkovskyi](https://github.com/Mishapolk/square-packing-records) · [Karimi’s registration](https://github.com/jlevy/squares/issues/847) · [Squares Project frontier](https://squaremath.org/frontier.html) · [Kaggle per-puzzle leaderboard](https://www.kaggle.com/code/inversion/squares-in-squares-per-puzzle-leaderboard/output)

## Continuation below 325

The search found no new record in the handoff’s original range. The two supplied 263-square checkpoint arrays are identical and measure about 16.734372735. The new checkpoint in `continuation/n263-checkpoint.yaml` verifies at a side below 16.733166010911. Kaggle reported 16.724372709118 for the same count. The 263-square checkpoint and the handoff’s earlier results are excluded from the record count.
