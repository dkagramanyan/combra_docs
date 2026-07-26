# combra.stats

The `combra.stats` module exposes the parametric distribution functions used as targets by {doc}`combra.fitting <fitting>`, plus the histogram preprocessor every distribution fit calls first, plus the inference helpers (Kendall, Fisher) used by the convergence-analysis pipeline.

```python
from combra import stats
```

## Histogram preprocessing

````{py:function} combra.stats.density_histogram(array, step) -> tuple[ndarray, ndarray]

Quantize `array` to multiples of `step`, count occurrences via `np.bincount`, and normalise to a probability distribution. This is the first thing every distribution-fit in combra calls.

:param array: 1-D input (angles, beam lengths, etc.).
:type array: array_like
:param step: Bin width in input units.
:type step: float
:returns: **x_bins** (*ndarray[float32]*) – Bin centres (only non-empty bins); and **y_density** (*ndarray[float32]*) – Normalised counts; `sum(y) == 1`.
:rtype: tuple(ndarray, ndarray)

**Example**

```pycon
>>> import numpy as np
>>> from combra import stats, approx
>>> angles_array = np.array([12, 13, 87, 90, 92, 178, 180])
>>> x, y = stats.density_histogram(angles_array, step=5)
>>> (x_g, y_g), mus, sigmas, amps = fitting.fit_bimodal_gaussian(x, y)
```
````

## Distributions

These are `x`-first model callables, fitted by {doc}`combra.fitting <fitting>` with `scipy.optimize.curve_fit`. They return ndarrays — feed them an x grid and parameters, get back y values.

````{py:function} combra.stats.gaussian(x, mu, sigma, amp=1) -> ndarray

Single Gaussian, $amp \cdot \mathcal{N}(x \mid \mu, \sigma)$.

:param x: Evaluation points.
:type x: array_like
:param mu: Mean.
:type mu: float
:param sigma: Standard deviation.
:type sigma: float
:param amp: Multiplicative amplitude. Default: `1`.
:type amp: float, optional
:returns: **y** (*ndarray*) – Function values at `x`.
:rtype: ndarray

**Example**

```pycon
>>> import numpy as np
>>> from combra import stats
>>> x = np.linspace(0, 360, 200)
>>> y = stats.gaussian(x, mu=180, sigma=30, amp=1.0)
```
````

````{py:function} combra.stats.bimodal_gaussian(x, mu1, mu2, sigma1, sigma2, amp1=1, amp2=1) -> ndarray

Sum of two Gaussians. Use {py:func}`combra.fitting.fit_bimodal_gaussian` to fit it to a histogram.

:param x: Evaluation points.
:type x: array_like
:param mu1: First mean.
:type mu1: float
:param mu2: Second mean.
:type mu2: float
:param sigma1: First standard deviation.
:type sigma1: float
:param sigma2: Second standard deviation.
:type sigma2: float
:param amp1: First amplitude. Default: `1`.
:type amp1: float, optional
:param amp2: Second amplitude. Default: `1`.
:type amp2: float, optional
:returns: **y** (*ndarray*) – Function values at `x`.
:rtype: ndarray

**Example**

```pycon
>>> import numpy as np
>>> from combra import stats
>>> x = np.linspace(0, 360, 200)
>>> y = stats.bimodal_gaussian(x, mu1=90, mu2=270, sigma1=20, sigma2=25, amp1=1.0, amp2=0.8)
```
````

````{py:function} combra.stats.binomial(x, n, p, amp=1) -> ndarray

Binomial PMF scaled by `amp`. `x` is rounded and clipped to `[0, n]`, and `p`
is clipped to `[0, 1]`, so the callable stays well-defined for every trial
value an optimiser proposes. Signature kept `curve_fit`-compatible.

:param x: Evaluation points.
:type x: array_like
:param n: Number of trials; rounded to at least 1.
:type n: float
:param p: Success probability.
:type p: float
:param amp: Multiplicative amplitude. Default: `1`.
:type amp: float, optional
:returns: **y** (*ndarray*) – Scaled PMF values at `x`.
:rtype: ndarray

**Example**

```pycon
>>> import numpy as np
>>> from combra import stats
>>> y = stats.binomial(np.arange(0, 26), n=25, p=0.2, amp=1.0)
```
````

````{py:function} combra.stats.poisson(x, lam, amp=1) -> ndarray

Poisson PMF scaled by `amp`, $amp \cdot e^{-\lambda} \lambda^{k} / k!$ with
$k$ the rounded, non-negative `x`. Signature kept `curve_fit`-compatible.

:param x: Evaluation points.
:type x: array_like
:param lam: Rate parameter $\lambda$; clamped to be non-negative.
:type lam: float
:param amp: Multiplicative amplitude. Default: `1`.
:type amp: float, optional
:returns: **y** (*ndarray*) – Scaled PMF values at `x`.
:rtype: ndarray

**Example**

```pycon
>>> import numpy as np
>>> from combra import stats
>>> y = stats.poisson(np.arange(0, 30), lam=6.0, amp=1.0)
```
````

````{py:function} combra.stats.exponential(x, a, amp=1) -> ndarray

Exponential decay $amp \cdot e^{-x/a}$. `a` is floored at `1e-10` so the
callable never divides by zero mid-fit.

:param x: Evaluation points.
:type x: array_like
:param a: Decay scale.
:type a: float
:param amp: Multiplicative amplitude. Default: `1`.
:type amp: float, optional
:returns: **y** (*ndarray*) – Decay values at `x`.
:rtype: ndarray

**Example**

```pycon
>>> import numpy as np
>>> from combra import stats
>>> y = stats.exponential(np.linspace(0, 50, 200), a=8.0, amp=1.0)
```
````

## Inference

Hypothesis-testing primitives used by {py:func}`combra.metrics.convergence_stats` / {py:func}`combra.metrics.print_convergence_report`. Both are pure and tiny — exposed so notebooks can call them directly on ad-hoc curves.

````{py:function} combra.stats.kendall_decreasing_p(ns, vals) -> float

One-sided Kendall τ p-value for the null "`|vals|` does not decrease as `ns` grows" against the alternative "decreases" (`scipy.stats.kendalltau(..., alternative='less')`). Rank-based, handles ties cleanly.

:param ns: Sample-size axis (typically integer Ns).
:type ns: array_like
:param vals: Metric values at each `N`. Sign is ignored — the test runs on `|vals|`.
:type vals: array_like
:returns: **p** (*float*) – One-sided p-value. NaN when the input has fewer than 3 points or is perfectly flat.
:rtype: float

**Example**

```pycon
>>> import numpy as np
>>> from combra import stats
>>> ns   = np.array([100, 250, 500, 1000, 2500, 5000])
>>> vals = np.array([0.40, 0.28, 0.21, 0.15, 0.11, 0.09])   # monotonically shrinking
>>> p = stats.kendall_decreasing_p(ns, vals)
>>> print(f'p={p:.4f}  (small p ⇒ |vals| really does decrease with N)')
```
````

````{py:function} combra.stats.fisher_combine(ps) -> tuple[float, int]

Combine independent one-sided p-values via Fisher's method ($\chi^2 = -2 \sum \log p$ with `2k` degrees of freedom). Entries that are NaN, ≤ 0, or > 1 are silently filtered out (only `0 < p ≤ 1` is meaningful for `log p`).

:param ps: Individual p-values.
:type ps: array_like
:returns: **combined_p** (*float*) – Fisher's combined p-value. NaN if no valid input remained after filtering; and **k** (*int*) – Count of p-values that survived filtering and contributed to `combined_p`.
:rtype: tuple(float, int)

**Example**

```pycon
>>> from combra import stats
>>> per_class_ps = [0.012, 0.041, 0.087, float('nan')]   # nan is silently dropped
>>> combined_p, k = stats.fisher_combine(per_class_ps)
>>> print(f'combined p={combined_p:.4f}   (k={k} of {len(per_class_ps)} curves contributed)')
```
````

## See also

- {doc}`combra.fitting <fitting>` — fits these distributions to data.
- {doc}`combra.angles <angles>` — uses `density_histogram` + `bimodal_gaussian` for angle histograms.
- {py:func}`combra.metrics.convergence_stats` — drives `kendall_decreasing_p` + `fisher_combine` across whole convergence tables.
