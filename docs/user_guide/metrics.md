# Comparing microstructures

Every comparison in combra has two sides, named consistently throughout the API:
**reference** is the ground truth — real SEM images, or the largest-$N$ run in a
sweep — and **generated** is whatever is being scored against it. Every two-input
metric takes the reference first.

## The three families

**Distribution distances** compare two {term}`angle density` curves directly.
{py:func}`~combra.metrics.compute_wasserstein_metrics` returns four numbers: the
1- and 2-Wasserstein distances, and their circular variants. For one-dimensional
distributions the $p$-Wasserstein distance has the closed form

$$W_p(u, v) = \left( \int_0^1 \left| F_u^{-1}(q) - F_v^{-1}(q) \right|^p \, \mathrm{d}q \right)^{1/p}$$

where $F^{-1}$ is the quantile function. The circular variants apply the same
formula on the circle, which is the correct geometry for angles: on the line,
mass at 1° and mass at 359° appear maximally far apart instead of 2° apart.
These metrics are defined for any pair of densities, at any sample size.

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
All three reduce to the Fréchet distance between two Gaussians fitted to the
feature sets,

$$d^2 = \lVert \mu_1 - \mu_2 \rVert^2 + \operatorname{tr}\!\left( \Sigma_1 + \Sigma_2 - 2 (\Sigma_1 \Sigma_2)^{1/2} \right)$$

as introduced by Heusel et al. [^fid]. The angle families are stated formally,
end to end, in {doc}`angle_fit`. They need at least two images per side,
since each estimates a per-side covariance; the angle-based families are defined
on a single image.

{py:func}`~combra.metrics.compute_all_metrics` runs the first two families
always, and the third when `image_metrics=True`.

(undefined-rather-than-wrong)=

## Undefined rather than wrong

{py:func}`~combra.fitting.fit_bimodal_gaussian` always returns two modes, because
the model has two. When an angle density has only one, the solver must still put
the second somewhere, and it parks a **phantom** — either a flat pedestal or a
narrow spike at a position with no data under it.

A phantom used to appear even on genuinely *bimodal* densities, whenever the
reflex mode was weak over a heavy baseline: a wide pedestal is a competing
least-squares minimum, and unbounded widths made it a cheap one — fitted
$\sigma$ of $3.3 \times 10^4$ degrees has been observed. Seeding each mode from
its own side of the density and bounding $\sigma$ at 180° removed that failure
(83 degenerate fits out of 231 real angle densities became 0), so a rejection now
much more reliably means the data really has one mode rather than that the solver
missed the second. The relative errors above divide by the
reference fit, so a phantom denominator produces numbers that look like
measurements and are not: two densities differing by 2° once scored
$\varepsilon_{\sigma_1} = 1357$ and $\varepsilon_{\mathrm{amp}_2} = 3050$.

Every parametric entry point therefore screens both fits with
{py:func}`~combra.metrics.degenerate_fit_reason` and returns `nan`, logging the
reason at warning level, when a fit is:

- carrying under 5% of its mass in one mode, meaning there is only one real mode;
- sitting on the $[0, 360]$ boundary the means are clamped to, which is a fit
  artefact, and where $0$ would also be the denominator of the $\mu$ relative
  error;
- wider than 120° in one mode, which is a pedestal rather than a peak. The
  solver is itself bounded at 180°, deliberately above this threshold: bounding
  it at 120° would park every pedestal at exactly 120.0 and, since the test is a
  strict `>`, switch the rejection off;
- unresolved, with the two means closer together than one $\sigma$;
- placed where the density carries under 5% of its mass. This is checked only
  when the density is supplied, and it is the criterion that catches a spike,
  whose amplitude is an integral and therefore not small.

In practice the metrics are reliable on realistic WC-Co angle densities, those
with roughly 23% reflex vertices: across more than 900 such fits none was
rejected. They go undefined as the second mode thins, which is exactly the regime
in which they previously returned nonsense. Two consequences are worth knowing.

Small samples say so
: A single 128×128 image yields about 20 vertex angles, far too few to determine
  two modes, and returns `nan`. Pool on the order of 1000 angles — roughly 48
  such images — for a fit worth reporting.

`nan` is a signal about the generator
: Early in training, samples whose grains are near-convex have no reflex mode.
  Use the Wasserstein keys, which are defined unconditionally, until the
  parametric keys come back.

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
{term}`resolution`. See {doc}`../api/metrics` for the full column list.

## Sample size and step must match

Two results are comparable only when produced the same way. Both the
{term}`step` used to bin the angles and the `min_segment_len` used to extract
them change the measured distribution, so both are recorded on every parquet row;
{py:func}`~combra.metrics.parquet_has_step` checks the first before a comparison,
and {py:func}`~combra.angles.output_directory` encodes the second in the folder
name. See {doc}`angles` for what each does.

[^fid]: M. Heusel, H. Ramsauer, T. Unterthiner, B. Nessler, S. Hochreiter,
    *GANs Trained by a Two Time-Scale Update Rule Converge to a Local Nash
    Equilibrium*, NeurIPS 2017.
