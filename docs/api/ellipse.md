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

The big and small semi-axes of the ellipses {py:func}`fit_mvee` fits to the cobalt
regions of an image: the regions of {py:func}`combra.contours.cobalt_mask`, the
0.4 µm-median mask whose area is the cobalt fraction, as the beam datasets use.

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
