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

## Cobalt mask and areas

The cobalt is the dark side of the median-filtered Otsu binary of the image, with a
median of 0.4 µm ({py:func}`median_radius` of the image's `pixel_size`): the size that
keeps the cobalt fraction of the WC-Co crops at the alloys' cobalt volume fraction.
The angles use a smaller median ({py:func}`combra.angles.angle_settings`). A region is
an 8-connected component of the mask, its area its pixel count.

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   cobalt_mask
   areas
   median_radius
```

## Plotting

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   plot_area_grid
```
