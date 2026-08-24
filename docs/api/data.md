# combra.data

```{eval-rst}
.. module:: combra.data
.. currentmodule:: combra.data
```

Example assets shipped with the package, and the dataset classes that drive
combra's extraction pipelines. A dataset reads an image container, builds a
preprocessed-image cache, and writes per-class metrics to parquet;
{doc}`combra.metrics <metrics>` compares those parquets across runs.

```python
from combra import data
```

## Bundled fetchers

Zero-argument loaders for the assets shipped under `combra/data/`, sized for
smoke tests and minimal reproducible examples rather than for measurement.

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   load_microstructure
   microstructure_data_dir
   load_crack
   load_crack_annotations
   load_crack_contours
```

## Datasets

Each class ingests an image source, exposes it as a map dataset, and writes one
parquet row per class or per group. Their methods are documented on the class
pages.

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   MicrostructureDataset
   PolyamideFractureDataset
```

## Polyamide plots

Subplot grids over a
{py:meth}`~combra.data.PolyamideFractureDataset.generate` parquet, one panel per
frame group, with fitted distributions overlaid.

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   plot_polyamide_fractal
   plot_polyamide_contour
```

## Sweeps

Batch driver for convergence studies: one parquet per per-class image count, in
the folder layout {doc}`combra.metrics <metrics>` reads.

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   sweep_angles
```

## See also

- {doc}`combra.angles <angles>` — the angle extractor
  {py:meth}`~combra.data.MicrostructureDataset.generate_angles` calls per image.
- {doc}`combra.ellipse <ellipse>` — the MVEE primitive
  {py:meth}`~combra.data.MicrostructureDataset.generate_beams` calls per image.
- {doc}`combra.metrics <metrics>` — comparing parquet outputs across runs.
- {doc}`combra.io <io>` — the HDF5 conversion and the parquet schemas.
- {doc}`Vertex angles and the angle density </user_guide/angles>` — what a
  density means and how `step` is chosen.
