# Datasets and sample data (combra.data)

```{eval-rst}
.. module:: combra.data
.. currentmodule:: combra.data
```

The dataset that runs combra's extraction over a folder tree of SEM images and
writes one parquet row per class, the sample images shipped with the package,
and the polyamide fracture dataset.

```python
from combra import data
```

## Datasets

{py:meth}`~combra.data.MicrostructureDataset.generate_angles` and
{py:meth}`~combra.data.MicrostructureDataset.generate_beams` are documented on
the class page.

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   MicrostructureDataset
   sweep_angles
```

## Sample data

Zero-argument loaders for the images under `combra/data/`, sized for examples
and smoke tests.

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   load_microstructure
   load_crack
```

## Polyamide fractures

A separate material: frames of a polyamide fracture surface, bucketed into
groups of consecutive frames. {py:meth}`~combra.data.PolyamideFractureDataset.generate`,
documented on the class page, writes one parquet row per group with the
fractal dimension and the size of every contour; the two plotters read that
parquet. See {doc}`/examples/polyamide`.

```{versionchanged} 0.17.1
{py:meth}`~combra.data.PolyamideFractureDataset.generate` no longer hangs when a
frame has a contour of at least `N` points.
```

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   PolyamideFractureDataset
   plot_polyamide_fractal
   plot_polyamide_contour
```
