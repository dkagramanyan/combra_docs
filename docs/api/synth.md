# combra.synth

```{eval-rst}
.. module:: combra.synth
.. currentmodule:: combra.synth
```

A synthetic set of cobalt pools with an exact truth, rendered like the
micrographs, and the benchmark that scores an angle method against it. Real
images have no labels, so the truth-based part of the method comparison uses
generated polygons: every pool is a polygon whose vertices are known, placed on
a canvas at the real spacing and rendered with the real texture, noise, edge
smearing and border uncertainty. The generator and the renderer are calibrated
to real images; the defaults are the fitted values for the 512 px grades.

```python
from combra import synth
```

## The generator

A pool is bounded by carbide grains: its junctions are its convex vertices,
the grain corners pressed into it its reflex ones. The draw is balanced so
that the truth's vertices are half reflex in every size bin.

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   pool_polygon
   make_canvas
   Canvas
   TruthRegion
   interior_angles
```

```{eval-rst}
.. autodata:: GENERATOR
.. autodata:: SIZE_BINS
.. autodata:: DIAMETER_RANGE
.. autodata:: SUPERSAMPLE
.. autodata:: MIN_GAP
```

## The renderer

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   render
   image_statistics
```

```{eval-rst}
.. autodata:: RENDERER
.. autodata:: STAT_KEYS
```

## Calibration

The renderer's amplitudes are fitted to fourteen statistics of the real
images; the generator's shape parameters by a grid search on the real pools'
solidity, aspect ratio and P6 chord-angle histogram per size class.

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   fit_renderer
   RendererFit
   real_reference
   fit_generator
   GeneratorFit
```

## The benchmark

Four metrics by region size — the overlap of the polygon with the truth region,
where its edge sits, the angle error at the corners it found, and the share of
its vertex angles above 180° against the truth's — with the boundary F-score,
the regions found and the false polygons beside them.

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   benchmark
   BenchmarkResult
   score_canvas
   CanvasScore
   summarize
   iou_per_region
   edge_offset
   corner_angle_error
   reflex_share
```

## Figures

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   plot_benchmark
   plot_canvas
   plot_pools
```

## Raster helpers

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   rasterize
   coverage_patch
   shoelace
```

## See also

- {py:func}`combra.angles.extract_polygons`,
  {py:func}`combra.experimental.extract_polygons`,
  {py:func}`combra.legacy.extract_polygons` — the three methods in the form
  `benchmark` scores.
- {doc}`Vertex angles and the angle density </user_guide/angles>` — what the
  benchmark says about the method in use.
