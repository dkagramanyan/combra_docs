# Scoring a generated microstructure

Compare a generated {term}`angle density` against a reference one, and read what
each family of numbers says. For the concepts behind them, see
{doc}`/user_guide/metrics`.

Every two-input metric takes the **reference first**, then the generated sample.

## Two densities

A real comparison reduces images to densities with
{py:func}`~combra.metrics.images_to_angle_density`. Here the densities are built
analytically instead, so the answers are known in advance: two bimodal curves
whose first mode differs by 5°.

```{doctest}
>>> import numpy as np
>>> from combra import metrics, stats
>>> x = np.arange(0., 360., 5.)
>>> reference = (x, stats.bimodal_gaussian(x, 100., 250., 20., 20., 3., 1.))
>>> generated = (x, stats.bimodal_gaussian(x, 105., 250., 20., 20., 3., 1.))
```

## Transport distances

{py:func}`~combra.metrics.compute_wasserstein_metrics` scores the whole
distribution with one number per variant. The circular forms treat angles on the
circle, which is the correct geometry — on the line, mass at 1° and mass at 359°
look maximally far apart instead of 2°.

```{doctest}
>>> distances = metrics.compute_wasserstein_metrics(reference, generated)
>>> sorted(distances)
['circular_w1', 'circular_w2', 'w1', 'w2']
>>> round(distances['w1'], 3)
3.75
```

The value is below the 5° mode shift because only the first mode moved, and it
carries three quarters of the mass.

## Parametric errors

{py:func}`~combra.metrics.compute_gauss_metrics` fits a bimodal Gaussian to each
density and reports the relative error of each fitted parameter. Where the
transport distances say *how far apart*, these say *which part is wrong*:

```{doctest}
>>> errors = metrics.compute_gauss_metrics(reference, generated)
>>> sorted(errors)
['amp1', 'amp2', 'mu1', 'mu2', 'sigma1', 'sigma2']
>>> round(errors['mu1'], 3)
0.05
>>> round(errors['mu2'], 3)
0.0
```

`mu1` is 0.05 — the first mode is 5% off its reference position of 100° — while
the untouched second mode reads 0.

## When the parametric metrics go undefined

A generator whose grains are near-convex produces a density with only one mode.
The bimodal model still returns two, so the second is a solver artefact and every
relative error computed from it would be meaningless. combra returns `nan`
instead:

```{doctest}
>>> unimodal = (x, stats.gaussian(x, 100., 20., 3.))
>>> errors = metrics.compute_gauss_metrics(reference, unimodal)
>>> bool(np.all(np.isnan(list(errors.values()))))
True
```

The transport distances remain defined, which is why they are the ones to watch
early in training:

```{doctest}
>>> distances = metrics.compute_wasserstein_metrics(reference, unimodal)
>>> round(distances['w1'], 3)
37.5
```

{py:func}`~combra.metrics.degenerate_fit_reason` reports why a fit was rejected:

```{doctest}
>>> from combra import fitting
>>> _, mus, sigmas, amps = fitting.fit_bimodal_gaussian(*unimodal)
>>> metrics.degenerate_fit_reason(mus, sigmas, amps, density=unimodal)
'a mode carries 0.33% of the mass, under the 5% floor -- there is only one real mode'
```

The full set of rejection criteria is in {ref}`undefined-rather-than-wrong`.

## In a training loop

{py:func}`~combra.metrics.compute_all_metrics` runs both angle families on
in-memory image batches, and adds the image-feature metrics (FID, CMMD,
FD-DINOv2) when asked. Those need the optional `metrics` extra and at least two
images per side:

```pycon
>>> scores = metrics.compute_all_metrics(
...     real_batch, generated_batch, image_metrics=True,
... )
>>> scores['w1'], scores['mu1'], scores['fid']
```

Pass a shared `reference_cache` dict across calls to compute the reference side
once. See {doc}`/api/metrics` for the sharded evaluation harness and the
convergence tools.
