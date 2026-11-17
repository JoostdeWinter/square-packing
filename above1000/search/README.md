# Search programs

The certificates can be used offline with Python’s standard library. These optional search programs use NumPy, SciPy, pandas, Numba, and a C++17 compiler. Run the following commands from this directory, preferably in an extracted working copy. The optimization outputs use the historical field name `karimi_side` for the comparison side used during that search. The final certificate table uses `comparison_side`.

## Tilted bands

```sh
python karimi_refine.py karimi_original.csv first_pass.csv
python recombine.py first_pass.csv
c++ -O3 -std=c++17 endcap.cpp -o endcap
./endcap 100 32 2400 2 > endcaps.txt
python evaluate_endcaps.py
python polish_angles.py recombined.csv tightened_recombinations.csv
python polish_angles.py endcap_records.csv tightened_end_fills.csv
```

The included `refined.csv` holds the first pass over all 5,134 original Karimi rows. The intermediate comparison in `comparison.csv` guided the search. The final filtering uses the stronger benchmark in `../comparisons/generic.csv`.

## Rectangular pieces

The C++ crop program accepts centered square poses with angles in radians. For a public source portfolio in the standard Kaggle CSV format, the following example extracts corner pieces, retains nondominated rectangles, and lists candidate two-piece constructions. Numerical candidates require rational certification. Several source portfolios and archived handoff pieces may be supplied together.

```sh
python encode_sources.py submission.csv
c++ -O3 -std=c++17 crop.cpp -o crop
./crop 0 > blocks.txt
./crop 2 > interior.txt
python thin.py
c++ -O3 -std=c++17 pair.cpp -o pair
./pair < thin.txt > pair_results.csv
```

The output columns are the integer base side, excess square count, total square count, approximate side, and the two orientation-coded component identifiers in the filtered pool. The packaged rational components and recipes are sufficient to reconstruct the delivered results without downloading the search portfolios. Separate starting coordinates and local search code for the refined rectangular pieces are in `../rectopt/search`.

## Scalar comparisons

`spacers.py` starts with the archived tiling/border/deletion envelope and applies the composition test described in `../comparisons/generic-proof.txt`. The result is `generic.csv` in the current working directory. `fraction_pair.py` applies a second fractional-corner screen. These programs compare numerical upper bounds. The geometry checks use exact arithmetic.
