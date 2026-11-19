# Rational refinements of known packings

The exact sides and placements are in cases. Each certificate contains all square centers and rational half-angle tangents, as well as a Squares Project Witness/v2 with exact corner coordinates. The decimal in improvements.csv is rounded upward. Each decrease is measured against the smallest conservative comparison value in the case file, including the author’s earlier private witness when available. Smaller decimal refinements at or below 10⁻²⁰ are listed separately in precision_only.csv when present. Their exact changes can be much finer than the displayed decimal. Each case includes the exact rational side, gain and source credit.

Run python3 verify.py in this directory. Three rational geometry tests check every pair. The checker also rejects duplicate squares, damaged corners and insufficient containers. Replaying the witnesses takes only the Python standard library.

The 260-square refinement starts from the author’s earlier certificate derived from prvsiyan’s Squares Verified Best of 1105, version 25. Evan Daniel and Mykhailo Polkovskyi appear in the SquareMath history of this layout. The new computation adjusts individual centers and angles. The geometry retains the source dataset’s CC BY-SA 4.0 license. The comparisons and file chain identify the earlier inputs.

- https://squaremath.org/cases/260.html
- https://www.kaggle.com/datasets/prvsiyan/squares-verified-best-of-1105/versions/25
- https://github.com/jlevy/squares/issues/1009
