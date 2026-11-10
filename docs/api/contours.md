# Cobalt regions (combra.contours)

```{eval-rst}
.. module:: combra.contours
.. currentmodule:: combra.contours
```

The areas of the cobalt regions of a microstructure image and its cobalt fraction,
and the plot of the area distributions. See {doc}`/user_guide/metrics`.

```python
from combra import contours
```

## Areas

The areas of an image come in two versions, like the vertex angles and the
semi-axes, that differ only in image processing; their distributions are not
comparable. **v1** takes the cobalt side of the median-filtered Otsu binary
{py:func}`combra.angles.preprocess_image` starts from, and the metrics use it unless
told `method='v2'`; **v2** takes the detection mask of
{py:func}`combra.angles.vertex_angles.v2`. Both take the image itself. A region is an
8-connected component of the mask, its area its pixel count.
`combra.contours.areas` itself is not callable.

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   areas.v1
   areas.v2
```

## Plotting

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   plot_area_grid
```
