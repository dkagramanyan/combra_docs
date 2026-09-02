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

{py:func}`~combra.fitting.fit_bimodal_gaussian` fits
{py:func}`combra.stats.truncated_bimodal_gaussian`: the two modes share one
total mass, fixed to the histogram's bin width rather than fitted, and the fit
returns their `shares` (summing to 1) with that `total`. Its starting guess is
read off the density rather than fixed —
one mode seeded per side of 180°, from that side's tallest bin and its mass — and
mode widths are bounded to 180°.

```{warning}
{py:func}`~combra.fitting.fit_bimodal_gaussian` returns two modes whether or not
the data has two, so a single-moded density acquires a phantom second mode whose
parameters are solver artifacts. Screen a fit with
{py:func}`combra.metrics.degenerate_fit_reason` before reading its parameters;
the gauss metrics do this themselves and return `nan`. See
{ref}`undefined-rather-than-wrong`.
```

```{note}
Fits stored in angle parquets written before 0.13.0 hold two amplitudes under
`angles_gauss_amps`, a column that no longer exists, and those written before
the truncated model was adopted placed most of their mass outside
$[0°, 360°]$. Refit any parquet you intend to keep; the stored densities are
enough, so no h5 access or angle re-extraction is needed.
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
`(x_g, y_g), mus, sigmas, shares, total = fitting.fit_bimodal_gaussian(x, y)` works as
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
