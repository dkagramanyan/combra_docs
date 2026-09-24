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

```{warning}
**Known bug in combra 0.15.2:** {py:meth}`~combra.data.PolyamideFractureDataset.generate` hangs when any frame has a contour
of at least `N` points. The constructor runs the fractal-dimension self-check
with PyTorch in the main process; `generate()` then forks its workers, and a
worker that computes a fractal dimension with PyTorch deadlocks. The run never
finishes and raises nothing.
```

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   PolyamideFractureDataset
   plot_polyamide_fractal
   plot_polyamide_contour
```
