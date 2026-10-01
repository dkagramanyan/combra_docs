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

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   preprocess_image
   vertex_angles
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

## Experimental methods

`combra.experimental` holds two candidates. P6 is an extraction method: it
takes the image itself and returns the angles with one sub-pixel polygon per
cobalt pool. The mass-share fit is a five-parameter variant of the angle fit.
Their API and output may change without a deprecation period; see
{doc}`/user_guide/experimental`.

```{eval-rst}
.. module:: combra.experimental
```

```{eval-rst}
.. currentmodule:: combra

.. autosummary::
   :toctree: generated/
   :nosignatures:

   experimental.vertex_angles
   experimental.settings_for_scale
   experimental.fit_bimodal_gaussian
```
