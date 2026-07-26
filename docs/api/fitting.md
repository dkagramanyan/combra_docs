# combra.fitting

The `combra.fitting` module fits parametric distributions and lines to 1-D data.

One generic {py:func}`~combra.fitting.fit_distribution` covers the standard
distributions; the two domain-specific models keep named fitters. Every
result is a SciPy-style named tuple carrying the fitted parameters *and* a
`curve` sampled ready for plotting, plus an `evaluate(x)` method that
re-evaluates the model on any grid without refitting:

```pycon
>>> from combra import fitting, stats
>>> x, y = stats.density_histogram(angles, step=5)
>>> fit = fitting.fit_bimodal_gaussian(x, y)
>>> fit.mus, fit.sigmas, fit.amps          # named access
>>> x_curve, y_curve = fit.curve           # ready to plot
>>> fit.evaluate([0, 90, 180, 270])        # re-evaluate anywhere
```

Results also unpack positionally, so
`(x_g, y_g), mus, sigmas, amps = fitting.fit_bimodal_gaussian(x, y)` works too.

## Distribution fits

````{py:function} combra.fitting.fit_distribution(model, x, y, p0, bounds=None, x_lim=None, N=100, drop_invalid=True) -> DistributionFit

Least-squares fit of any `model(x, *params)` callable to `(x, y)`, plus the fitted curve sampled on a dense grid. One fitter for every distribution in {doc}`combra.stats <stats>` — the initial guesses and bounds that belong to a distribution stay with the caller rather than being baked into a per-distribution wrapper.

:param model: Model callable `model(x, *params) -> ndarray`, e.g. {py:func}`combra.stats.gaussian`.
:type model: callable
:param x: Input histogram bin centres.
:type x: array_like
:param y: Input histogram densities.
:type y: array_like
:param p0: Initial guesses, in the model's parameter order.
:type p0: sequence of float
:param bounds: `(lower, upper)` per parameter. Bounds put `curve_fit` on its trust-region solver; without them it runs Levenberg-Marquardt and parameters are free to take unphysical signs. Default: `None`.
:type bounds: tuple[sequence, sequence] or None, optional
:param x_lim: `(x_min, x_max)` for the fit and the sampled curve. Defaults to `(x.min(), x.max())`. Default: `None`.
:type x_lim: tuple[float, float] or None, optional
:param N: Number of sample points on the returned curve. Default: `100`.
:type N: int, optional
:param drop_invalid: Drop non-finite and negative-`y` samples before fitting. Pass `False` to keep samples a decay drives below zero. Default: `True`.
:type drop_invalid: bool, optional
:returns: **result** – a {py:class}`~combra.fitting.DistributionFit` `(curve, params, model)`.
:rtype: DistributionFit

**Example**

Per-group Gaussian and exponential fits on contour-length histograms:

```pycon
>>> from combra import fitting, stats
>>> x, y = stats.density_histogram(len_list, step=1)
>>> fit = fitting.fit_distribution(stats.gaussian, x, y, p0=[3, 3, 1], x_lim=(0, 25))
>>> mu, sigma, amp = fit.params
>>> x_fit, y_fit = fit.curve
>>> decay = fitting.fit_distribution(
...     stats.exponential, x, y, p0=[5, 1],
...     bounds=([1e-10, 0.0], [1e6, float("inf")]), x_lim=(0, 25),
... )
```
````

````{py:function} combra.fitting.fit_bimodal_gaussian(x, y, mu1=100, mu2=240, sigma1=30, sigma2=30, amp1=1, amp2=1) -> BimodalGaussianFit

Bimodal Gaussian fit + sampled curve. Used inside {py:meth}`combra.data.MicrostructureDataset.generate_angles` to populate `prep_per_step.angles_gauss_*`.

The model is symmetric under swapping its two modes, so the returned modes are **sorted by `mu`** — slot 1 is always the lower-angle mode. Without that convention which mode lands in slot 1 is arbitrary, and {py:func}`combra.metrics.gauss_relative_errors` compares modes slot-wise.

:param x: Input histogram bin centres.
:type x: array_like
:param y: Input histogram densities.
:type y: array_like
:param mu1: Initial guess for the first mean. Default: `100`.
:type mu1: float, optional
:param mu2: Initial guess for the second mean. Default: `240`.
:type mu2: float, optional
:param sigma1: Initial guess for the first sigma. Default: `30`.
:type sigma1: float, optional
:param sigma2: Initial guess for the second sigma. Default: `30`.
:type sigma2: float, optional
:param amp1: Initial guess for the first amplitude. Default: `1`.
:type amp1: float, optional
:param amp2: Initial guess for the second amplitude. Default: `1`.
:type amp2: float, optional
:returns: **result** – a {py:class}`~combra.fitting.BimodalGaussianFit` ``(curve, mus, sigmas, amps)``: the `(x_gauss, y_gauss)` sampled curve, and the fitted per-mode means, sigmas and amplitudes.
:rtype: BimodalGaussianFit

**Example**

```pycon
>>> import numpy as np
>>> from combra import angles, fitting, stats
>>> # Suppose `arr` is the angles array from combra.angles.vertex_angles
>>> arr = np.concatenate([np.random.normal(90, 20, 1000),
...                       np.random.normal(270, 25, 1500)])
>>> x, y = stats.density_histogram(arr, step=2)
>>> (x_g, y_g), mus, sigmas, amps = fitting.fit_bimodal_gaussian(x, y)
>>> print(f'mu = {mus},  sigma = {sigmas},  amp = {amps}')
```
````

## Linear fits

````{py:function} combra.fitting.fit_line(x, y) -> tuple[tuple[ndarray, ndarray], float, float, float, float]

Least-squares line $y = kx + b$, solved by a numba-compiled kernel. Used in {py:meth}`combra.data.MicrostructureDataset.generate_beams` to populate `prep.a_*` and `prep.b_*` fit fields.

:param x: Input series.
:type x: array_like
:param y: Input series.
:type y: array_like
:returns: **result** – a {py:class}`~combra.fitting.LineFit` ``(curve, slope, intercept, angle_deg, r2)``: the `(x_pred, y_pred)` sampled line, the slope, the intercept, `arctan(slope)` in degrees, and the R².
:rtype: LineFit

**Example**

```pycon
>>> import numpy as np
>>> from combra import fitting
>>> x = np.linspace(0, 10, 50)
>>> y = 2.5 * x + 1.0 + np.random.normal(scale=0.5, size=50)
>>> fit = fitting.fit_line(x, y)
>>> print(f'k={fit.slope:.3f}  b={fit.intercept:.3f}  angle={fit.angle_deg:.2f}°  R²={fit.r2:.3f}')
>>> (x_pred, y_pred), k, b, angle_deg, score = fit  # positional unpacking still works
```
````


## Plateau / asymptote fits

````{py:function} combra.fitting.fit_plateau(ns, vals) -> PlateauFit

Fit $|m|(N) = a + b \cdot N^{-1/2}$ with `a, b ≥ 0`. The asymptote `a` is the irreducible `|m|` as `N → ∞` (e.g. a generator's bias floor); `b` captures the Monte-Carlo sampling-noise term (theoretical `N^(-1/2)` decay for Wasserstein / Gaussian-fit moment errors).

Used by {py:func}`combra.metrics.convergence_stats` to estimate per-curve plateaus and the standard error around them.

:param ns: Sample sizes (N values along the convergence curve).
:type ns: array_like[int]
:param vals: Metric values at each `N`. Sign is ignored; the fit is on `|vals|`.
:type vals: array_like[float]
:returns: **a_hat** (*float*) – Plateau (irreducible `|m|` at infinite N); and **a_se** (*float*) – Standard error on `a_hat` from the covariance matrix. NaN if the fit fails or is degenerate; and **b_hat** (*float*) – Sampling-noise coefficient. NaN for all three when the fit fails, when fewer than 3 points are supplied, or when all `vals` are identical.
:rtype: tuple(float, float, float)

**Example**

Driven inside {py:func}`combra.metrics.convergence_stats` over a W-dist curve. Standalone:

```pycon
>>> import numpy as np
>>> from combra import fitting
>>> ns = np.array([100, 250, 500, 1000, 2500, 5000, 10000])
>>> # True asymptote a=0.05; sampling-noise b=0.30; small additive jitter
>>> vals = 0.05 + 0.30 / np.sqrt(ns) + np.random.normal(scale=0.005, size=len(ns))
>>> a, a_se, b = fitting.fit_plateau(ns, vals)
>>> print(f'plateau a={a:.4f} ± {a_se:.4f}    b={b:.4f}')
```
````

## Result types

The fit functions return SciPy-style named tuples (cf. `scipy.stats.linregress`),
so results carry attribute names while staying unpacking-compatible with the
historical plain tuples.

````{py:class} combra.fitting.LineFit(curve, slope, intercept, angle_deg, r2)

Result of {py:func}`~combra.fitting.fit_line`.

Deliberately its own type rather than a {py:class}`~combra.fitting.DistributionFit`: `angle_deg` and `r2` are derived diagnostics rather than parameters the solver searched for, so they do not belong in that class's `params` — and a line is not one of the {doc}`combra.stats <stats>` densities. `scipy.stats.linregress` draws the same distinction.

:param curve: `(x_pred, y_pred)` of the fitted line sampled across the data span.
:type curve: tuple[ndarray, ndarray]
:param slope: Line slope `k`.
:type slope: float
:param intercept: Line intercept `b` (value at `x = 0`).
:type intercept: float
:param angle_deg: Slope as an angle in degrees, `atan(k)`.
:type angle_deg: float
:param r2: Coefficient of determination on the input points.
:type r2: float
````

````{py:class} combra.fitting.BimodalGaussianFit(curve, mus, sigmas, amps)

Result of {py:func}`~combra.fitting.fit_bimodal_gaussian`.

:param curve: `(x, y)` of the fitted bimodal-Gaussian density.
:type curve: tuple[ndarray, ndarray]
:param mus: The two per-mode means.
:type mus: list[float]
:param sigmas: The two per-mode standard deviations.
:type sigmas: list[float]
:param amps: The two per-mode amplitudes.
:type amps: list[float]
````

`````{py:class} combra.fitting.DistributionFit(curve, params, model)

Result of {py:func}`~combra.fitting.fit_distribution`.

:param curve: `(x, y)` of the fitted density sampled on the evaluation grid.
:type curve: tuple[ndarray, ndarray]
:param params: Fitted parameters, in the model's own signature order (after `x`).
:type params: tuple[float, ...]
:param model: The model that was fitted, so `evaluate` can re-apply it.
:type model: callable

````{py:method} evaluate(x) -> ndarray
Re-evaluate the fitted model on an arbitrary grid, without refitting.
````
`````
`````{py:class} combra.fitting.PlateauFit(asymptote, asymptote_stderr, decay)

Result of {py:func}`~combra.fitting.fit_plateau`, which fits the
Monte-Carlo convergence law

$$|m|(N) = a + b \, N^{-1/2}$$

:param asymptote: The irreducible $|m|$ as $N \to \infty$ — coefficient $a$, constrained non-negative. For a generator this is its bias floor.
:type asymptote: float
:param asymptote_stderr: Standard error of `asymptote`, from the covariance of the fit. NaN when the covariance is not finite.
:type asymptote_stderr: float
:param decay: Coefficient $b$ of the $N^{-1/2}$ term, unconstrained in sign. $b > 0$ is the canonical decay (the curve approaches the asymptote from above); $b < 0$ means small-$N$ fits landed lucky-close to the reference and the systematic bias only emerges as $N$ grows.
:type decay: float

All three fields are NaN when the input has fewer than 3 points, is perfectly
flat, or the fit fails.

````{py:method} evaluate(ns) -> ndarray
Evaluate $a + b N^{-1/2}$ at the sample sizes `ns`.
````

**Example**

```pycon
>>> import numpy as np
>>> from combra import fitting
>>> ns = np.array([100, 250, 500, 1000, 2500, 5000])
>>> vals = 0.08 + 1.2 * ns ** -0.5
>>> fit = fitting.fit_plateau(ns, vals)
>>> print(f'floor={fit.asymptote:.3f} +- {fit.asymptote_stderr:.3f}, b={fit.decay:.2f}')
```
`````

## See also

- {doc}`combra.stats <stats>` — the distribution functions these fits target.
- {doc}`combra.angles <angles>` — uses `fit_bimodal_gaussian` for angle histograms.
- {doc}`combra.ellipse <ellipse>` — uses `fit_line` for beam-length log-density fits.
- {py:func}`combra.metrics.convergence_stats` — uses `fit_plateau` to estimate per-curve bias floors.
