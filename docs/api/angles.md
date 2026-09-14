# combra.angles

```{eval-rst}
.. module:: combra.angles
.. currentmodule:: combra.angles
```

Extraction of the vertex angles of the cobalt pools from SEM images, the fit
of the density they form, and the plotting helpers for stored densities.
{py:func}`~combra.angles.vertex_angles` is the per-image primitive
{py:meth}`combra.data.MicrostructureDataset.generate_angles` runs in parallel
across a class folder. The method is the one called P6 in the extraction
report: a detection mask, a sub-pixel boundary, Douglas–Peucker vertices and
angles read from lines fitted to the boundary. The previous method, P0, is
{doc}`combra.legacy <legacy>`; the facet-based alternative, P7, is
{doc}`combra.experimental <experimental>`.

```python
from combra import angles
```

## Extraction

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   vertex_angles
   pool_mask
   pool_regions
   extract_polygons
   Region
```

## The density fit

The bimodal fit of an angle set with the model-free shares beside it: what a
method's angle set looks like, in eight numbers.

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   angle_summary
   AngleSummary
```

## Output layout

The folder naming shared by the generation and the plotting sides, so neither
re-derives the `_tol` suffix.

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
- {doc}`combra.synth <synth>` — the synthetic set with an exact truth the
  method was chosen on, and the benchmark that scores it.
- {doc}`combra.legacy <legacy>` and {doc}`combra.experimental <experimental>`
  — the previous and the candidate method, same call signature.
- {py:func}`combra.io.load_rows` — loads angles parquets into the row shape
  these plotters expect.
- {py:func}`combra.stats.density_histogram` — reduces extracted angles to the
  density these plotters draw.
- {doc}`Vertex angles and the angle density </user_guide/angles>` — what a
  density means and how the tolerance is chosen.
