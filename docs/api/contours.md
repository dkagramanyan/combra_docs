# combra.contours

```{eval-rst}
.. module:: combra.contours
.. currentmodule:: combra.contours
```

Extraction of polygon contours from preprocessed binary images, and their
rasterization back to masks and overlays. This is the layer
{py:func}`combra.ellipse.fit_mvee`, {py:func}`combra.legacy.vertex_angles` and
the crack-graph builder share; {py:func}`combra.angles.vertex_angles` locates
its own sub-pixel boundaries from the pool mask instead.

```python
from combra import contours
```

## Extraction

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   find_contours
   contour_to_binary_mask
```

## Drawing

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   draw_contours
```

## See also

- {py:func}`combra.legacy.vertex_angles` — uses `find_contours` internally.
- {py:func}`combra.ellipse.fit_mvee` — fits an MVEE to each `find_contours`
  output.
- {py:func}`combra.image.contour_fractal_dimension` — box-counts the mask
  `contour_to_binary_mask` returns.
