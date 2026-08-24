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

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   gaussian
   bimodal_gaussian
   binomial
   poisson
   exponential
```

## See also

- {doc}`combra.fitting <fitting>` — fits these distributions to data.
- {doc}`combra.angles <angles>` — uses `density_histogram` and
  `bimodal_gaussian` for angle histograms.
- {doc}`Vertex angles and the angle density </user_guide/angles>` — what a
  density means and how `step` is chosen.
