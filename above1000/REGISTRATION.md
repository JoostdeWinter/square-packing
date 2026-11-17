# Lowered upper bounds for 2,837 counts between n = 1,036 and n = 9,928: registration request

**Credit name.** Joost de Winter, Delft University of Technology. For the 218 counts marked "after Karimi" in `claimed.csv`: Joost de Winter, after Mohsen Karimi.

**Claim.** Exactly certified packings that lower the best public side for 2,837 counts between 1,036 and 9,928 unit squares. `above1000/claimed.csv` lists each count with its exact rational side, the side rounded up at 12 places, the best public value and its source, and the gain. The gains range from 0.000016 to 0.043. Examples: n = 1,036 at 32.656497332913 (gain 0.0101), n = 1,401 at 37.864242305929 (gain 0.0243), n = 9,410 at 97.445070007002 (gain 0.0426).

**Certificate.** Folder `above1000` of https://github.com/JoostdeWinter/square-packing at commit cc20a26845789c2502950041c26709eda8a71081. Later commits leave these files unchanged. `python export.py N file.cert` writes exact rational coordinates (centre and tangent of the half-angle of each square) for any count N, and `python export.py N file.yaml --yaml` writes all four corners as exact rationals. Ready coordinate files for n = 1,036, 1,401, 1,627, 2,934 and 9,410 are in `above1000/examples/`.

**Construction.** 1,760 counts come from a new search in the two-band family (row angles and numbers of upright squares at each end), building on the work of Sungjoon Ryu, Evan Daniel, Kevin Fang and Mohsen Karimi. 268 counts join rectangular pieces cut from public packings, with upright grids in the remaining space. 217 counts recombine band patterns from Karimi's packings of different counts. 592 counts follow from these by adding upright border layers and removing surplus squares. The angle refinements of Karimi's own layouts (2,269 counts, plus 80 by border layers) are in `records.csv` but are not part of this request.

**Checking.** `python verify_all.py` in the folder `above1000` (Python 3.9 or later, standard library only, exact rational arithmetic). Two separately written exact checks cover every two-band packing (29,895,955 unit squares in total). Every packing made from rectangular pieces is expanded and checked for pairwise separation and wall containment. The script also checks the counts, the border and deletion arithmetic and the comparisons. Output in `above1000/verification.txt`.

**Comparison.** Francisco Couzo's and Mykhailo Polkovskyi's large-count indices, Karimi's tables (https://github.com/jlevy/squares/issues/847), the Squares Project register and issues, and public Kaggle scores, as of 17 November 2026. The comparison also allows smaller packings to be repeated, extended by upright borders, joined, or reduced by deletion. Sources and screens are in `above1000/comparisons/`.

**Not done.** No optimality claim. The comparison is a dated snapshot, and newer public results may beat some counts.

**AI assistance.** The search, constructions and certificates were produced with GPT-6.2 Astra (OpenAI). The selection of the claimed set and the repository files were produced with Claude (Anthropic). Both worked under my direction.
