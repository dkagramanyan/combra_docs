# Beams (combra.ellipse)

```{eval-rst}
.. module:: combra.ellipse
.. currentmodule:: combra.ellipse
```

Minimum-volume enclosing ellipses of the grains of a microstructure image, and
the plots of the beam-length distributions they give. See
{doc}`/user_guide/beams`.

```python
from combra import ellipse
```

## Fitting

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   fit_mvee
```

## Semi-axes

The big and small semi-axes of the minimum-area ellipses around the vertices of the
angle polygons ({py:func}`combra.angles.vertex_angles`) of the cobalt regions that do
not touch the image frame. {py:func}`fit_mvee` and the beam datasets are a separate
pipeline, on the contours of the three-level map.

```{versionchanged} 0.39.0
The ellipses were fitted to the Canny contours of the 0.4 µm cobalt mask.
```

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   semiaxes
```

## Plotting

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   plot_beam_lengths
   plot_beam_compare
   plot_semiaxis_grid
```
