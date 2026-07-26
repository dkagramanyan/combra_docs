# combra.fitting

The `combra.fitting` module fits parametric distributions and lines to 1-D data.

There is **one `fit_*` function per model** and **one result type per fit**. Every
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

## Gaussian fits

````{py:function} combra.fitting.fit_gaussian(x, y, mu=1, sigma=1, amp=1, x_lim=None, N=100) -> GaussianFit

Single Gaussian fit + sampled curve.

:param x: Input histogram bin centres.
:type x: array_like
:param y: Input histogram densities.
:type y: array_like
:param mu: Initial guess for the mean. Default: `1`.
:type mu: float, optional
:param sigma: Initial guess for the standard deviation. Default: `1`.
:type sigma: float, optional
:param amp: Initial guess for the amplitude. Default: `1`.
:type amp: float, optional
:param x_lim: `(x_min, x_max)` for the sampled curve. Defaults to `(x.min(), x.max())`. Default: `None`.
:type x_lim: tuple[float, float] or None, optional
:param N: Number of sample points on the returned curve. Default: `100`.
:type N: int, optional
:returns: **curve** (*tuple[ndarray, ndarray]*) – `(x_gauss, y_gauss)` sampled curve; and **mu** (*float*) – Fitted mean; and **sigma** (*float*) – Fitted standard deviation; and **amp** (*float*) – Fitted amplitude.
:rtype: tuple(tuple(ndarray, ndarray), float, float, float)

**Example**

Adapted from `poliamid/data_viz.ipynb` (per-group Gaussian fit on contour-length histograms):

```pycon
>>> from combra import stats, approx
>>> x_orig, y_orig = stats.density_histogram(len_list, step=1)
>>> (x_fit, y_fit), mu, sigma, amp = fitting.fit_gaussian(
...     x_orig, y_orig, mu=3, sigma=3, amp=1, x_lim=[0, 25], N=100,
... )
```
````

````{py:function} combra.fitting.fit_bimodal_gaussian(x, y, mu1=100, mu2=240, sigma1=30, sigma2=30, amp1=1, amp2=1) -> BimodalGaussianFit

Bimodal Gaussian fit + sampled curve. Used inside {py:meth}`combra.data.MicrostructureDataset.generate_angles` to populate `prep_per_step.angles_gauss_*`.

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
>>> from combra import angles, approx, stats
>>> # Suppose `arr` is the angles array from combra.angles.vertex_angles
>>> arr = np.concatenate([np.random.normal(90, 20, 1000),
...                       np.random.normal(270, 25, 1500)])
>>> x, y = stats.density_histogram(arr, step=2)
>>> (x_g, y_g), mus, sigmas, amps = fitting.fit_bimodal_gaussian(x, y)
>>> print(f'mu = {mus},  sigma = {sigmas},  amp = {amps}')
```
````

## Other distributions

````{py:function} combra.fitting.fit_binomial(x, y, n=10, p=0.5, amp=1, x_lim=None, N=100) -> BinomialFit

Binomial fit + sampled curve.

:param x: Input histogram bin centres.
:type x: array_like
:param y: Input histogram densities.
:type y: array_like
:param n: Initial trial count. Default: `10`.
:type n: int, optional
:param p: Initial success probability. Default: `0.5`.
:type p: float, optional
:param amp: Initial amplitude. Default: `1`.
:type amp: float, optional
:param x_lim: Range for the sampled curve. Default: `None`.
:type x_lim: tuple[float, float] or None, optional
:param N: Number of sample points. Default: `100`.
:type N: int, optional
:returns: **curve** (*tuple[ndarray, ndarray]*) – `(x_pred, y_pred)`; and **n** (*float*) – Fitted trial count; and **p** (*float*) – Fitted success probability; and **amp** (*float*) – Fitted amplitude.
:rtype: tuple(tuple(ndarray, ndarray), float, float, float)

**Example**

From `poliamid/data_viz.ipynb`:

```pycon
>>> from combra import stats, approx
>>> x, y = stats.density_histogram(len_list, step=1)
>>> (x_fit, y_fit), n_fit, p_fit, amp = fitting.fit_binomial(
...     x, y, n=25, p=0.2, x_lim=[0, 25], N=100,
... )
```
````

````{py:function} combra.fitting.fit_poisson(x, y, lam=1, amp=1, x_lim=None, N=100) -> PoissonFit

Poisson fit + sampled curve.

:param x: Input histogram bin centres.
:type x: array_like
:param y: Input histogram densities.
:type y: array_like
:param lam: Initial rate. Default: `1`.
:type lam: float, optional
:param amp: Initial amplitude. Default: `1`.
:type amp: float, optional
:param x_lim: Range for the sampled curve. Default: `None`.
:type x_lim: tuple[float, float] or None, optional
:param N: Number of sample points. Default: `100`.
:type N: int, optional
:returns: **curve** (*tuple[ndarray, ndarray]*) – `(x_pred, y_pred)`; and **lam** (*float*) – Fitted rate; and **amp** (*float*) – Fitted amplitude.
:rtype: tuple(tuple(ndarray, ndarray), float, float)

**Example**

From `poliamid/data_viz.ipynb`:

```pycon
>>> from combra import stats, approx
>>> x, y = stats.density_histogram(len_list, step=1)
>>> (x_fit, y_fit), lam, amp = fitting.fit_poisson(x, y, x_lim=[-5, 25], N=100)
```
````

````{py:function} combra.fitting.fit_exponential(x, y, a=1, amp=1, x_lim=None, N=100) -> ExponentialFit

Exponential decay $amp \cdot e^{-x/a}$ fit + sampled curve.

:param x: Input histogram bin centres.
:type x: array_like
:param y: Input histogram densities.
:type y: array_like
:param a: Initial decay constant. Default: `1`.
:type a: float, optional
:param amp: Initial amplitude. Default: `1`.
:type amp: float, optional
:param x_lim: Range for the sampled curve. Default: `None`.
:type x_lim: tuple[float, float] or None, optional
:param N: Number of sample points. Default: `100`.
:type N: int, optional
:returns: **curve** (*tuple[ndarray, ndarray]*) – `(x_pred, y_pred)`; and **a** (*float*) – Fitted decay constant; and **amp** (*float*) – Fitted amplitude.
:rtype: tuple(tuple(ndarray, ndarray), float, float)

**Example**

From `poliamid/data_viz.ipynb`:

```pycon
>>> from combra import stats, approx
>>> x, y = stats.density_histogram(len_list, step=1)
>>> (x_fit, y_fit), a, amp = fitting.fit_exponential(
...     x, y, a=5, amp=1, x_lim=[0, 25], N=100,
... )
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

````{py:class} combra.fitting.GaussianFit(curve, mu, sigma, amp)

Result of {py:func}`~combra.fitting.fit_gaussian`.

:param curve: `(x, y)` of the fitted density sampled on the evaluation grid.
:type curve: tuple[ndarray, ndarray]
:param mu: Fitted mean.
:type mu: float
:param sigma: Fitted standard deviation.
:type sigma: float
:param amp: Fitted amplitude — the integral of the curve.
:type amp: float

````{py:method} evaluate(x) -> ndarray
Re-evaluate the fitted Gaussian on an arbitrary grid, without refitting.
````
````

````{py:class} combra.fitting.BinomialFit(curve, n, p, amp)

Result of {py:func}`~combra.fitting.fit_binomial`.

:param curve: `(x, y)` of the fitted PMF sampled on the evaluation grid.
:type curve: tuple[ndarray, ndarray]
:param n: Fitted number of trials.
:type n: float
:param p: Fitted success probability.
:type p: float
:param amp: Fitted amplitude.
:type amp: float

````{py:method} evaluate(x) -> ndarray
Re-evaluate the fitted PMF on an arbitrary grid.
````
````

````{py:class} combra.fitting.PoissonFit(curve, lam, amp)

Result of {py:func}`~combra.fitting.fit_poisson`.

:param curve: `(x, y)` of the fitted PMF sampled on the evaluation grid.
:type curve: tuple[ndarray, ndarray]
:param lam: Fitted rate parameter $\lambda$.
:type lam: float
:param amp: Fitted amplitude.
:type amp: float

````{py:method} evaluate(x) -> ndarray
Re-evaluate the fitted PMF on an arbitrary grid.
````
````

````{py:class} combra.fitting.ExponentialFit(curve, a, amp)

Result of {py:func}`~combra.fitting.fit_exponential`.

:param curve: `(x, y)` of the fitted decay sampled on the evaluation grid.
:type curve: tuple[ndarray, ndarray]
:param a: Fitted decay scale.
:type a: float
:param amp: Fitted amplitude.
:type amp: float

````{py:method} evaluate(x) -> ndarray
Re-evaluate the fitted decay on an arbitrary grid.
````
````

````{py:class} combra.fitting.PlateauFit(asymptote, asymptote_stderr, decay)

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
````

## See also

- {doc}`combra.stats <stats>` — the distribution functions these fits target.
- {doc}`combra.angles <angles>` — uses `fit_bimodal_gaussian` for angle histograms.
- {doc}`combra.ellipse <ellipse>` — uses `fit_line` for beam-length log-density fits.
- {py:func}`combra.metrics.convergence_stats` — uses `fit_plateau` to estimate per-curve bias floors.
