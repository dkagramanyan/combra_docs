# Vertex angles (combra.angles)

```{eval-rst}
.. module:: combra.angles
.. currentmodule:: combra.angles
```

The vertex angles of the grain contours of an SEM image, the bimodal fit of the
density they form, and the plots of stored densities. What the angles measure
and how the fit is defined is in {doc}`/user_guide/angles`.

```python
from combra import angles
```

## Extraction

One pipeline: the map {py:func}`preprocess_image` returns (an optional enlargement,
a median filter, Otsu, the phase boundary), then {py:func}`vertex_angles`: contours,
Douglas-Peucker, short-side pruning, chord angles. Every setting is a length on the
sample, turned into pixels by {py:func}`angle_settings` from the image's
`pixel_size`, which the pipeline requires: a median of 0.1 µm, a tolerance of
0.4 µm and a shortest side of 0.8 µm, with the image enlarged twice when its pixel
is coarser than 0.15 µm. {py:func}`extract_polygons` returns the cobalt mask and the
polygons in pixels of the image, the form {py:func}`combra.synth.benchmark` scores.

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   angle_settings
   preprocess_image
   vertex_angles
   extract_polygons
   angle_summary
```

## Plotting

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   plot_density
   plot_overlay_grid
```
