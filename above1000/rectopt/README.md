# Rectangular pieces after local optimization

Ten square-container packings use rectangular pieces cropped from five donor datasets. The source field, reflection index and integer crop offset in each piece identify its input. Six pieces in the delivered packings underwent local optimization. The other pieces retain their verified donor geometry. Different input datasets may contain the same earlier packing.

The optimization moves centers and angles and minimizes the excess above the integer side lengths of a rectangle. Every accepted piece has exact rational centers and exact rational half-angle tangents. The two-piece construction puts these pieces in opposite corners and fills the remaining strips with aligned unit squares.

The following command regenerates all ten complete coordinate lists internally and checks every wall and potential pair of overlapping squares with integer arithmetic. It also verifies the component counts and the quoted benchmark comparisons.

```
python verify.py --full 1060 --full 1170 --full 1187 --full 1188 --full 1239 --full 1248 --full 1320 --full 1393 --full 1411 --full 1479
```

To write the complete coordinates for one packing, run `python verify.py --full 1188 --poses n1188.json`. The included search directory contains the starting poses for the six optimized components and the numerical optimization method. The rational packing witnesses can be checked with Python's standard library.
