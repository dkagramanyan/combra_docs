# combra.experimental

```{eval-rst}
.. module:: combra.experimental
.. currentmodule:: combra.experimental
```

P7, a candidate angle method with a different polygon architecture. The mask
of {py:func}`combra.angles.pool_mask` only finds the regions and orders their
boundaries; every boundary point is moved to the sub-pixel maximum of the image
gradient, and the polygon's facets come from a split-and-merge stage with a
model criterion instead of a distance tolerance. On the synthetic set of
{doc}`combra.synth <synth>` it is the best of the three methods on every
geometric count (corners recovered 54% against 37% for P6, the same edge
error); on real images its angle set carries more reflex vertices and fits the
two-Gaussian model of {doc}`combra.fitting <fitting>` worse, and its facet
stage is Python, about fifty times slower than P6. It stays experimental until
the reference distributions are re-extracted with it and the model revised.

```python
from combra import experimental
```

## Extraction

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   vertex_angles
   pool_regions
   extract_polygons
```

## Stages

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   gradient_snap
   facets
```

## See also

- {py:func}`combra.angles.vertex_angles` — P6, the method in use.
- {py:func}`combra.synth.benchmark` — scores both against the exact truth.
