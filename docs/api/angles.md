# Vertex angles (combra.angles)

```{eval-rst}
.. module:: combra.angles
.. currentmodule:: combra.angles
```

The vertex angles of the cobalt pools of an SEM image, the bimodal fit of the
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

## Legacy and experimental methods

Both take the same image and return the same `(angles, polygons)` pair as
{py:func}`vertex_angles`.

Legacy
: `combra.legacy` is the method used before 0.15, kept to reproduce results
  extracted with it.

Experimental
: `combra.experimental` is a candidate method; its API and output may change
  without a deprecation period.

```{eval-rst}
.. module:: combra.legacy
.. module:: combra.experimental
```

```{eval-rst}
.. currentmodule:: combra

.. autosummary::
   :toctree: generated/
   :nosignatures:

   legacy.vertex_angles
   experimental.vertex_angles
```
