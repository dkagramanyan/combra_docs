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

The semi-axes of every ellipse in an image come in two versions, like the vertex
angles, that differ only in image processing; their distributions are not
comparable. **v1** runs on the map {py:func}`combra.angles.preprocess_image`
returns, as the beam datasets do, and the metrics use it unless told
`method='v2'`; **v2** takes the image itself and fits the ellipses to the
detection mask of {py:func}`combra.angles.vertex_angles.v2`.
`combra.ellipse.semiaxes` itself is not callable.

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   semiaxes.v1
   semiaxes.v2
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
