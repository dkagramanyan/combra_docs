# combra.angles

```{eval-rst}
.. module:: combra.angles
.. currentmodule:: combra.angles
```

Extraction of grain-boundary vertex angles from preprocessed binary images, and
the plotting helpers for the densities they produce.
{py:func}`~combra.angles.vertex_angles` is the per-image primitive
{py:meth}`combra.data.MicrostructureDataset.generate_angles` runs in parallel
across a class folder.

```python
from combra import angles
```

## Extraction

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   vertex_angles
```

## Output layout

The folder naming shared by the generation and the plotting sides, so neither
re-derives the `_msl` suffix.

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   output_directory
```

## Plotting

Two entry points and the assembly steps between them: `plot_density` draws one
parquet, and `plot_overlay_grid` goes from a generation manifest to a finished
reference-vs-generators grid.

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   plot_density
   plot_density_grid
   resolve_overlay_rows
   build_overlay_grid
   plot_overlay_grid
```

## Display

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   AngleDensityDisplay
```

## See also

- {py:meth}`combra.data.MicrostructureDataset.generate_angles` — drives
  `vertex_angles` across whole class folders and writes parquet.
- {doc}`combra.contours <contours>` — the contour extractor `vertex_angles`
  relies on internally.
- {py:func}`combra.io.load_rows` — loads angles parquets into the row shape
  these plotters expect.
- {py:func}`combra.stats.density_histogram` — reduces extracted angles to the
  density these plotters draw.
- {doc}`Vertex angles and the angle density </user_guide/angles>` — what a
  density means and how `min_segment_len` is chosen.
