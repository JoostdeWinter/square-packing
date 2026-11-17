# Packings for n between 1,036 and 9,928

This folder holds exactly certified packings that lower the best public side for 2,837 counts between 1,036 and 9,928 unit squares. `claimed.csv` lists them, one row per count, with the exact side, the side rounded up at 12 places, the best public value with its source, the comparison used, the gain and the construction method. The gains range from 0.000016 to 0.043.

Examples:

| n | Comparison used | New side, rounded up | Gain of at least |
|---:|---:|---:|---:|
| 1,036 | 32.66663819 | 32.656497332913 | 0.01014 |
| 1,401 | 37.88853732 | 37.864242305929 | 0.02430 |
| 1,627 | 40.82029285 | 40.802490991005 | 0.01780 |
| 9,410 | 97.48768435 | 97.445070007002 | 0.04261 |

## Construction

The packings come from four methods:

- 1,760 counts from a new search in the two-band family, over row angles and the numbers of upright squares at each end;
- 268 counts made by joining rectangular pieces cut from public packings, as pairs, chains, repeated pieces or individually optimized pieces, with upright grids in the remaining space;
- 217 counts that recombine band patterns from Mohsen Karimi's published packings of different counts;
- 592 counts that follow from the packings above by adding upright border layers and removing surplus squares (`derived.csv` gives the parent of each).

The two-band family builds on Sungjoon Ryu's L-shaped frame, Evan Daniel's filled ends, Kevin Fang's formulation and Mohsen Karimi's independently parameterized bands. Rectangular recomposition has published precedents, including Dmitry Ostashev's constructions.

The search also refined the angles of 2,269 of Karimi's own published layouts, and 80 further counts follow from those by border layers. Those counts are in `records.csv` and are not claimed here, because the layouts are Karimi's.

## Comparison

The comparison combines Francisco Couzo's and Mykhailo Polkovskyi's large-count indices, Karimi's tables, the Squares Project register and issues, and public Kaggle scores, all as of 17 November 2026. It also allows smaller packings to be repeated, extended by upright borders, joined or reduced by deletion. `comparisons/` holds the source-by-source values and these screens.

## Checking

Run from this folder (Python 3.9 or later, standard library only):

```sh
python verify_all.py
python export.py 9410 n9410.cert
python bands/check_coordinates.py n9410.cert
```

`verify_all.py` replays the full set with exact rational arithmetic. Two separate exact checks cover every two-band packing. Every packing made from rectangular pieces is expanded to coordinates and checked for pairwise separation and containment. The output is in `verification.txt`. `export.py` writes the coordinates of any count, and `examples/` holds ready coordinate files for five counts. `README_archive.md` describes the original archive in full.

## Method and AI assistance

The search, constructions and certificates were produced with GPT-6.2 Astra (OpenAI). The selection of the claimed set and the repository files were produced with Claude (Anthropic). Both worked under the direction of Joost de Winter.
