# Packing comparison renderer

Run from this repository root:

```bash
python3 render_comparisons.py --catalogue baseline_packings.json --records render_records.json --output figures --contact-tolerance 0.001
```

The input registry points to the **exact rational witnesses**, which are used for the after geometry. Each rational basis is checked to have squared norm exactly one. The renderer does not re-prove pairwise separation; the registry's independently checked witnesses supply that evidence. All SVG and PNG coordinates are floating-point illustrations, not replacement certificates.

Dependencies: Python 3, NumPy, SciPy, and either CairoSVG or the Inkscape command-line program for PNG export. `--no-png` creates SVG and metadata only. `--only 227,229` selects cases. `--orientation-weight` adjusts the matching heuristic.

## Outputs

- `n227_before_after.png` / `.svg`, with corresponding files for each registry case.
- `square-227.svg` / `.png`: clean after-only, standalone, 960 × 680 website-style asset, without orange comparison overlays.
- `n227_topology_comparison.json`: correspondence, near-contact graph, changed edges, feature locations, tolerance sensitivity and source hashes.
- `before_after_orange.png` / `.svg`: combined comparison sheet.
- `manifest.json`: the current generated cases and their filenames.

Both comparison panels use the same unit scale. The after packing is shown in the registered D4 orientation, which may rotate or reflect its original witness. This is a container-preserving isometry; the rational witness itself is unchanged. The exact transform is recorded in the metadata. The clean after-only asset uses the same orientation as the comparison.

## What orange means

A pair is a **near-contact adjacency** when the minimum Euclidean distance between its square boundaries is at most `0.001` unit-square sides. This is a deliberately stated numerical threshold, not a statement that the pair has an exact algebraic contact. Boundary-to-container contacts are excluded from this pairwise comparison.

Orange on the before panel marks adjacencies absent from the matched after graph; orange on the after panel marks newly present adjacencies. Shared near-contacts remain blue/gray. Parallel edge contacts are drawn as orange segments; other contacts use small orange markers. The comparison metadata also includes counts at thresholds `0.0001`, `0.001` and `0.005`, so sensitivity can be inspected.

The square identities are **not canonical**. For each of the eight D4 transforms of the after packing, the script aligns container centers and solves a Hungarian assignment minimizing

```text
squared center distance + 0.1 × sin(2 × orientation difference)^2
```

The lowest-cost transform/assignment is retained, with a fixed transform-order tie break. All eight costs, the chosen transform, and the complete zero-based before-to-original-after mapping are exported. This is a useful geometric correspondence between unlabeled unit squares, not a claim about a unique matching or a continuous motion from one packing to the other. Therefore the orange overlay is a descriptive graph difference under that correspondence, not a canonical topological invariant.

Square fill is gray near axis alignment and blue for larger tilts (display threshold `0.001` radian). Orange is reserved for the selected changed near-contacts. Printed side lengths use `≈` because they are rounded; the exact certified side remains in the witness and metadata.
