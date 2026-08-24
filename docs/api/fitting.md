# combra.fitting

```{eval-rst}
.. module:: combra.fitting
.. currentmodule:: combra.fitting
```

Least-squares fits of the {doc}`combra.stats <stats>` distributions, of a
straight line, and of the Monte-Carlo convergence law, to one-dimensional data.
Every fitter returns a SciPy-style named tuple carrying the fitted parameters,
a `curve` sampled ready for plotting, and an `evaluate(x)` method that
re-applies the model on any grid without refitting.

```python
from combra import fitting
```

## Distribution fits

One generic {py:func}`~combra.fitting.fit_distribution` covers the standard
distributions; the angle density keeps a named fitter because its bounds and
mode ordering are part of the model.

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   fit_distribution
   fit_bimodal_gaussian
```

```{warning}
{py:func}`~combra.fitting.fit_bimodal_gaussian` returns two modes whether or not
the data has two, so a single-moded density acquires a phantom second mode whose
parameters are solver artifacts. Screen a fit with
{py:func}`combra.metrics.degenerate_fit_reason` before reading its parameters;
the gauss metrics do this themselves and return `nan`. See
{ref}`undefined-rather-than-wrong`.
```

## Linear fits

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   fit_line
```

## Plateau / asymptote fits

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   fit_plateau
```

## Result types

SciPy-style named tuples (cf. `scipy.stats.linregress`): results carry attribute
names while staying unpacking-compatible with plain tuples, so
`(x_g, y_g), mus, sigmas, amps = fitting.fit_bimodal_gaussian(x, y)` works as
well as attribute access.

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   DistributionFit
   BimodalGaussianFit
   LineFit
   PlateauFit
```

## See also

- {doc}`combra.stats <stats>` — the distribution functions these fits target.
- {doc}`combra.angles <angles>` — uses `fit_bimodal_gaussian` for angle
  histograms.
- {doc}`combra.ellipse <ellipse>` — uses `fit_line` for beam-length log-density
  fits.
- {py:func}`combra.metrics.convergence_stats` — uses `fit_plateau` to estimate
  per-curve bias floors.
- {doc}`Comparing microstructures </user_guide/metrics>` — why a parametric
  metric goes undefined, and how an N-sweep is read.
