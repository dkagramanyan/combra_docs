# Comparing microstructures

Every comparison in combra has two sides, named consistently throughout the API:
**reference** is the ground truth — real SEM images, or the largest-$N$ run in a
sweep — and **generated** is whatever is being scored against it. Every two-input
metric takes the reference first.

## The three families

**Distribution distances** compare the bimodal fits (below) of two
{term}`angle density` curves. {py:func}`~combra.metrics.compute_wasserstein_metrics`
returns four numbers: the
1- and 2-Wasserstein distances, and their circular variants. For one-dimensional
distributions the $p$-Wasserstein distance has the closed form

$$W_p(u, v) = \left( \int_0^1 \left| F_u^{-1}(q) - F_v^{-1}(q) \right|^p \, \mathrm{d}q \right)^{1/p}$$

where $F^{-1}$ is the quantile function. The circular variants apply the same
formula on the circle, which is the correct geometry for angles: on the line,
mass at 1° and mass at 359° appear maximally far apart instead of 2° apart.
Since 0.28.0 the distances are taken between the fitted curves, not the
histograms: like the semi-axis $W_2$ between the fitted exponential tails, they
compare the two models, and they are undefined where a fit fails outright.

**Parametric errors** fit a bimodal Gaussian to each density and compare the
fitted parameters, giving the per-mode relative error

$$\varepsilon_i = \frac{\theta_i^{\text{gen}} - \theta_i^{\text{ref}}}{\theta_i^{\text{ref}}}$$

for each of $\mu$, $\sigma$ and $\mathrm{amp}$. Where the Wasserstein distances
score the whole distribution with one number, these localize *where* a generator
is wrong: a shifted mode ($\mu$), a mode of the wrong width ($\sigma$), or one
carrying the wrong share of the mass ($\mathrm{amp}$). They are undefined when a
density is not genuinely bimodal — see below.

**Image-feature distances** ignore the geometry pipeline and compare deep
features: InceptionV3 FID, CLIP-MMD, and the Fréchet distance on DINOv2 features.
FID and FD-DINOv2 are the Fréchet distance between two Gaussians fitted to the
feature sets,

$$d^2 = \lVert \mu_1 - \mu_2 \rVert^2 + \operatorname{tr}\!\left( \Sigma_1 + \Sigma_2 - 2 (\Sigma_1 \Sigma_2)^{1/2} \right)$$

as introduced by Heusel et al. [^fid]. CLIP-MMD (CMMD) is instead the squared
maximum mean discrepancy between L2-normalized CLIP embeddings under a Gaussian
RBF kernel ($\sigma = 10$, scaled by 1000), as in Google's CMMD. The angle
families are stated formally, end to end, in {doc}`angle_fit`. The two Fréchet
distances need at least two images per side,
since each estimates a per-side covariance; the angle-based families are defined
on a single image.

**Semi-axis tail errors** compare the grains' minimum-volume enclosing ellipses
({doc}`beams`). Past its mode, the distribution of a semi-axis $x$ decays
exponentially, so its tail is fitted as

$$p(x) = a \, e^{k (x - x_0)}, \qquad x \ge x_0,$$

for the big semi-axis $A$ and the small semi-axis $B$ of each side, with $x_0$ the
mode of the histogram, $k < 0$ the decay rate and $a = p(x_0)$ the density where the
tail starts. Written as $a \, e^{kx + b}$, the shift is $b = -k x_0$, fixed by $x_0$:
$a$ and $b$ are not separately determined by the data.
{py:func}`~combra.metrics.semiaxis_metrics` reports, per semi-axis, the
2-Wasserstein distance between the two fitted tails and the relative errors of $k$
and $a$.

{py:func}`~combra.metrics.compute_all_metrics` runs the first two families and the
semi-axis errors always, and the image-feature family when `image_metrics=True`.
The semi-axes come from {py:func}`combra.ellipse.semiaxes.v1` unless
`semiaxis_kw={'method': 'v2'}`.

(undefined-rather-than-wrong)=

## Undefined rather than wrong

{py:func}`~combra.fitting.fit_bimodal_gaussian` always returns two modes, because
the model has two. When an angle density has only one, the solver must still put
the second somewhere, and it parks a **phantom** — either a flat pedestal or a
narrow spike at a position with no data under it.

A phantom can also appear on genuinely *bimodal* densities when the reflex mode
is weak over a heavy baseline: a wide pedestal is a competing least-squares
minimum, and the fit, which starts from a fixed point and leaves the means and
the widths free, can reach it — fitted $\sigma$ of $3.3 \times 10^4$ degrees has
been observed. On the 1083 stored real angle densities the screening below
accepts 1035 fits; the 48 it rejects all have a reflex mode just under the 5%
floors. The relative errors above divide by the
reference fit, so a phantom denominator produces numbers that look like
measurements and are not: two densities differing by 2° once scored
$\varepsilon_{\sigma_1} = 1357$ and $\varepsilon_{\mathrm{amp}_2} = 3050$.

Every parametric entry point therefore screens both fits with
{py:func}`~combra.metrics.degenerate_fit_reason` and returns `nan`, logging the
reason at warning level, when a fit is:

- carrying under 5% of its mass in one mode, meaning there is only one real mode;
- with a mean within 5° of either end of $[0, 360]$ or outside it (the means are
  free), which is a fit artefact, and where $0$ would also be the denominator of
  the $\mu$ relative error;
- wider than 120° in one mode, which is a pedestal rather than a peak (the widths
  are not bounded above);
- unresolved, with the two means closer together than one $\sigma$;
- placed where the density carries under 5% of its mass. This is checked only
  when the density is supplied, and it is the criterion that catches a spike,
  whose amplitude is an integral and therefore not small.

In practice the metrics are reliable on realistic WC-Co angle densities: of the
1083 stored real densities, the 48 rejected are those whose reflex mode carries
just under 5%. They go undefined as the second mode thins, which is exactly the regime
in which they previously returned nonsense. Two consequences are worth knowing.

Small samples say so
: A single 128×128 image yields about 20 vertex angles, far too few to determine
  two modes, and returns `nan`. Pool on the order of 1000 angles — roughly 48
  such images — for a fit worth reporting.

`nan` is a signal about the generator
: Early in training, samples whose grains are near-convex have no reflex mode.
  Use the Wasserstein keys until the parametric keys come back: they compare the
  fitted curves, which exist even when a fit is screened as degenerate, and are
  `nan` only when a fit fails outright (fewer bins than parameters).

## Reading an N-sweep

A metric computed on a finite sample contains both the generator's real bias and
sampling noise. The two are separated by computing the metric at increasing
sample sizes $N$ and watching what it does: a curve that keeps falling as $N$
grows was measuring noise, while one that flattens onto a non-zero floor has
found a real difference. {py:func}`~combra.fitting.fit_plateau` fits that floor,

$$|m|(N) = a + b \, N^{-1/2},$$

where $a$ is the bias floor and the $N^{-1/2}$ term is the Monte-Carlo decay of
the sampling component. {py:func}`~combra.metrics.convergence_stats` fits this
per curve and adds a one-sided Kendall $\tau$ test of the hypothesis that
$|m|$ decreases with $N$, plus a power-law exponent $\alpha$ in
$|m| \sim N^{-\alpha}$. An $\alpha$ near $0.5$ is ideal Monte-Carlo decay, near
$0$ means no improvement, and negative means the metric grew with $N$.

Curves are grouped by {term}`kind` — the generator being compared — and
{term}`resolution`. See {py:func}`~combra.metrics.convergence_stats` for the full column list.

For a report, {py:func}`~combra.metrics.convergence_table` condenses a sweep to one
row per kind, resolution and metric: the plateau fit of the class-mean $|m|$ at
$N = n_\text{lo}$ and at a larger $N$ (or $N \to \infty$), the relative change
$\Delta$ between them, and a two-sided Kendall $\tau_N$ test of a trend with $N$.
{py:func}`~combra.metrics.plot_convergence_table` draws it, shading the rows with a
significant trend by $\Delta$:

```python
from combra.metrics import convergence_table, plot_convergence_table

df[['mu1', 'semi_major_k']] *= 100          # relative errors in %
table = convergence_table(df, ['w2', 'mu1', 'semi_major_w2', 'semi_major_k'], n_lo=1000)
plot_convergence_table(table, decimal=',', save_path='table.png')
```

{py:func}`~combra.metrics.plot_consistency_table` draws, in the same layout, the
Kendall $\tau_b$ between the angle statistics and the image metrics over a training
run ({py:func}`~combra.metrics.training_metric_consistency`): one column per image
metric, a cell shaded when its $\tau_b$ is significant and $|\tau_b| \ge 0.5$ (blue:
the statistic improves with the image metric, red: they move apart):

```python
import pandas as pd
from combra.io import read_tb_scalars
from combra.metrics import plot_consistency_table, training_metric_consistency

table = pd.concat([
    training_metric_consistency(read_tb_scalars(path), kimg_tag).assign(kind=kind, resolution=res)
    for kind, res, path, kimg_tag in runs])
plot_consistency_table(table, decimal=',', save_path='kendall.png')
```

## Sample size and step must match

Two results are comparable only when produced the same way. Both the
{term}`step` used to bin the angles and the `min_segment_len` used to extract
them change the measured distribution, so both are recorded on every parquet row;
{py:func}`~combra.metrics.parquet_has_step` checks the first before a comparison,
and `combra.angles.output_directory.v1` encodes the second in the folder
name. The angle version is part of the identity too: the training-time metrics
report v1 and v2 in separate sections, each against its own reference. See {doc}`angles` for what each does.

[^fid]: M. Heusel, H. Ramsauer, T. Unterthiner, B. Nessler, S. Hochreiter,
    *GANs Trained by a Two Time-Scale Update Rule Converge to a Local Nash
    Equilibrium*, NeurIPS 2017.
