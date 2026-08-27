# combra.stats

```{eval-rst}
.. module:: combra.stats
.. currentmodule:: combra.stats
```

Parametric distribution functions used as fitting targets by
{doc}`combra.fitting <fitting>`, and the histogram preprocessor that every
distribution fit calls first.

```python
from combra import stats
```

## Histogram preprocessing

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   density_histogram
   require_density
```

## Distributions

Model callables taking `x` first and the parameters after, in the form
`scipy.optimize.curve_fit` expects. Each returns an array of values on the given
grid; {doc}`combra.fitting <fitting>` fits them to data.

The angle density is fitted with
{py:func}`~combra.stats.truncated_bimodal_gaussian`, whose two modes are each
renormalized over $[0°, 360°]$ so that all of the fitted probability mass lies
inside the interval the angles were measured on. Truncated rather than wrapped:
a vertex angle is not a circular variable, so 1° (a needle-thin protrusion) and
359° (a needle-thin notch) are opposite shapes rather than neighbours.
{py:func}`~combra.stats.bimodal_gaussian` is the plain untruncated sum, kept for
callers who want it.

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   gaussian
   bimodal_gaussian
   truncated_bimodal_gaussian
   binomial
   poisson
   exponential
```

## See also

- {doc}`combra.fitting <fitting>` — fits these distributions to data.
- {doc}`combra.angles <angles>` — uses `density_histogram` and
  `truncated_bimodal_gaussian` for angle histograms.
- {doc}`Vertex angles and the angle density </user_guide/angles>` — what a
  density means and how `step` is chosen.
