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

The vertex angles come in two versions that are not interchangeable: their
densities differ and must not be compared with each other. Call a version
explicitly; `combra.angles.vertex_angles` itself is not callable.

- **v1** (P0) runs on the map {py:func}`preprocess_image` returns: median filter,
  Otsu, Canny contours, Douglas-Peucker, short-segment pruning
  (`min_segment_len`, 5 px by default), chord angles. The datasets use it, and
  the metrics use it unless told `method='v2'`.
- **v2** (P6) takes the image itself: a detection mask, a sub-pixel boundary,
  Douglas-Peucker, and angles from lines fitted to the boundary on either side
  of each vertex. {py:func}`settings_for_scale` gives its settings for an
  image of another resolution.

The training-time metrics report both versions; see
{doc}`/user_guide/metrics`.

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   preprocess_image
   vertex_angles.v1
   vertex_angles.v2
   settings_for_scale
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
