# The angle fit, formally

The complete scheme behind combra's primary descriptor: how a contour becomes an
angle, angles become a density, the density becomes a bimodal-Gaussian fit, and
two fits become metrics. {doc}`angles` and {doc}`metrics` cover the same ground
in prose and are the better first read; this page fixes the notation and states
every formula the implementation actually uses.

## 1. From vertex to angle

Let a simplified contour be the closed polygon $V_1, \dots, V_M$, the vertices
left by the simplification and the pruning of {doc}`angles`. At vertex $V_k$
write the two chords leaving the vertex

$$\mathbf{v}_1 = V_{k-1} - V_k, \qquad \mathbf{v}_2 = V_{k+1} - V_k .$$

{py:func}`combra.angles.vertex_angles` reports

$$
\alpha_k =
\begin{cases}
\theta_k, & \det(\mathbf{v}_1, \mathbf{v}_2) < 0 \quad \text{(convex)} \\[4pt]
360^\circ - \theta_k, & \det(\mathbf{v}_1, \mathbf{v}_2) \ge 0 \quad \text{(reflex)}
\end{cases}
\qquad
\theta_k = \arccos
\frac{\langle \mathbf{v}_1, \mathbf{v}_2 \rangle}{\|\mathbf{v}_1\|\,\|\mathbf{v}_2\|}
\in [0^\circ, 180^\circ]
$$

with $\det(\mathbf{v}_1, \mathbf{v}_2) = v_1^x v_2^y - v_1^y v_2^x$, the signed
area of the pair, for the orientation the contours are traced in. So
$\alpha_k \in [0^\circ, 360^\circ)$, convex vertices occupy the lower half and
reflex vertices the upper half.

:::{important}
**The angle domain is an interval, not a circle.** $\alpha = 1^\circ$ is a
needle-thin protrusion and $\alpha = 359^\circ$ a needle-thin notch: opposite
shapes that happen to sit at opposite ends of the axis, not neighbours on a
circle. The fitted model of §3 is therefore not wrapped around the circle (it
is a sum of two normals on the real line, see §3). The Wasserstein distances of
§6 are the one place that treats the axis as a circle, and deliberately so —
there the circular variant is reported alongside the linear one, because
transport cost is a different question from shape.
:::

:::{note}
**The angles are defined at the simplification scale.** A vertex exists only
after Douglas–Peucker simplification at tolerance `tol` (`angles_tol` in
{py:meth}`~combra.data.MicrostructureDataset.generate_angles`), so the angle
density is a property of the contour *at that scale*, not of the grain alone.
On the 1024 px reference set, raising `tol` from 2 to 5 px at
`min_segment_len = 5` moved the fitted convex mode from $117$–$119^\circ$ to $94$–$97^\circ$ and the
reflex mode up by $15$–$17^\circ$ across the three classes, while the model-free
reflex share $\sum_{x_k > 180} y_k$ moved by less than $0.04$. Report the
tolerance (and the method) with every fitted mode, and compare fits only at
equal parameters; {py:func}`combra.angles.angle_summary` reports the model-free
share beside the fit.
:::

## 2. From angles to the empirical density

Pool the angles of every vertex of every contour of every image in a class into
$\{\alpha_1, \dots, \alpha_n\}$. For a bin width $h$ (the {term}`step`),
{py:func}`combra.stats.density_histogram` quantizes and normalizes:

$$
q_j = h \left\lfloor \frac{\alpha_j}{h} \right\rceil,
\qquad
n_k = \#\{ j : q_j = x_k \},
\qquad
y_k = \frac{n_k}{n},
\qquad
\sum_k y_k = 1
$$

where $\lfloor \cdot \rceil$ is rounding to nearest and $x_k$ ranges over the
*occupied* bin centres — empty bins are dropped, so $x$ need not be uniformly
spaced.

:::{note}
$y_k$ is a **bin probability, not a density per degree**. Its scale therefore
depends on $h$: the density per degree is $y_k / h$, and
$\sum_k y_k h = h$ is the area under it. The fit of §4 has its own 2° histogram:
this one is for drawing (a fitted density times $h$ lies over it) and for the
screen of §5.
:::

Bin occupancy sets the noise floor. With $n_k \approx n h / 360$ counts in a bin,
the relative sampling error is

$$
\frac{\operatorname{sd}(y_k)}{y_k} \approx \frac{1}{\sqrt{n_k}}
= \sqrt{\frac{360}{n h}},
$$

so halving $h$ costs a factor $\sqrt{2}$ in per-bin noise. At $h = 0.1^\circ$ a
class holds about $50\times$ fewer counts per bin than at $h = 5^\circ$, hence
about $7\times$ the relative noise of the drawn histogram. The fit of §4 is
unaffected.

## 3. The model

Write $\varphi(x; \mu, \sigma)$ for the normal density and let the angle domain
be $D = [0^\circ, 360^\circ]$. {py:func}`combra.stats.bimodal_gaussian` is the
sum of two normals,

$$
p(x; \boldsymbol{\theta}) =
a_1\, \varphi(x; \mu_1, \sigma_1) + a_2\, \varphi(x; \mu_2, \sigma_2),
\qquad a_1 + a_2 = 1,
$$

with parameter vector
$\boldsymbol{\theta} = (\mu_1, \mu_2, \sigma_1, \sigma_2, a_1)$: the
amplitudes $a_i$ are the weights of the modes.

$a_i$ is the integral of mode $i$ over the whole real line,
$\int_{\mathbb{R}} p\,\mathrm{d}x = a_1 + a_2$. The model is **not truncated**
to $D$: a mode whose mean lies near $0^\circ$ or $360^\circ$, or whose width is
large, places part of its amplitude on angles that cannot occur, and the
fraction lost outside $D$,

$$
\text{leak} = 1 - \frac{1}{a_1 + a_2}\sum_{i=1}^{2} a_i Z_i ,
\qquad
Z_i = \Phi\!\left(\frac{360 - \mu_i}{\sigma_i}\right)
    - \Phi\!\left(\frac{0 - \mu_i}{\sigma_i}\right),
$$

with $\Phi$ the standard normal CDF, is small on the WC-Co sets: fitting the
truncated model by the same likelihood moves the means of the six real
resolution-class sets by less than $1^\circ$.

`combra.fitting.fit_bimodal_share` fits the truncated variant, each mode
divided by its $Z_i$ and the two amplitudes replaced by one mass share.

## 4. The estimator

{py:func}`combra.fitting.fit_angle_distribution` maximizes the likelihood of the
histogram of the angles in bins $[b_j, b_{j+1})$ of $2^\circ$, centred on even degrees
(since 0.39.0; before, least squares on the histogram of §2). With $c_j$ angles in bin
$j$,

$$
\hat{\boldsymbol{\theta}}
= \arg\max_{\boldsymbol{\theta}} \sum_j c_j \ln P_j,
\qquad
P_j = \int_{b_j}^{b_{j+1}} p(x; \boldsymbol{\theta})\,\mathrm{d}x,
\qquad
\sigma_i \ge 1^\circ,\quad a_i \ge 0,\quad a_1 + a_2 = 1 .
$$

The model is integrated over each bin rather than read at its centre, which would
widen each mode by $h^2 / 12$ in $\sigma^2$. The two edge bins are open, as the model
is not truncated, so the $P_j$ sum to 1. The maximum is found by
expectation-maximization. With $r_j = a_1 P_{1j} / P_j$ the share of bin $j$ that
belongs to mode 1, $P_{1j}$ the mass of $\varphi(x; \mu_1, \sigma_1)$ in it and
$E_j$, $E^{(2)}_j$ the means of $x$ and $(x - \mu_1)^2$ of that normal within it,
each iteration sets

$$
a_1 = \frac{\sum_j c_j r_j}{\sum_j c_j}, \qquad
\mu_1' = \frac{\sum_j c_j r_j E_j}{\sum_j c_j r_j}, \qquad
\sigma_1'^2 = \frac{\sum_j c_j r_j E^{(2)}_j}{\sum_j c_j r_j} - (\mu_1' - \mu_1)^2,
$$

and mode 2 likewise with $1 - r_j$, until the means and widths move by less than
$10^{-4}$ degrees (and $a_1$ by less than $10^{-6}$), at most 1000 times.

The start is fixed, $(\mu_1, \mu_2, \sigma_1, \sigma_2, a_1)^{(0)} =
(100, 240, 30, 30, 0.5)$. The width floor keeps a mode off a single repeated angle,
where the likelihood rises as the mode narrows. With fewer than six
occupied bins every parameter is returned as $\text{nan}$.

One fit serves every stored bin width: the curve stored beside a histogram of bin width
$h$ is $h\,p(x; \hat{\boldsymbol{\theta}})$.

A caller that holds only a histogram gets the same likelihood on its own bins:
{py:func}`combra.metrics.gauss_density_metrics` and a precomputed `(x, y)` passed
to the metrics.

### Means are not peaks

Two normals do not describe all of the angle density: the reflex mode is
asymmetric and the tails are heavier than normal. On the six real
resolution-class sets $\mu_2$ lies about $12^\circ$ from the top of the smoothed
histogram, where least squares on the histogram put it about $7^\circ$ away.
Read $\mu_i$ as the mean of a component, not as the position of a peak. Against
least squares the likelihood fit of these sets has $\mu_1$ lower by $1$–$4^\circ$,
$\mu_2$ higher by $3$–$5^\circ$ and $\sigma_2$ of $22$–$24^\circ$ instead of
$17$–$22^\circ$, so fits of the two estimators must not be compared.

### Mode ordering

The model is invariant under exchanging its two modes, so the solver's slot
assignment is arbitrary. Results are canonicalized by

$$\mu_1 \le \mu_2 ,$$

with $\sigma$ and $a$ permuted to match, so slot 1 is always the lower-angle
mode. §6 compares fits slot-wise and needs this.

## 5. When a fit is not a measurement

The model has two modes whether or not the data does, so a fit must be screened
before its parameters are read as measurements.
{py:func}`combra.metrics.degenerate_fit_reason` rejects
$\hat{\boldsymbol{\theta}}$ when any of the following holds, in this order:

$$
\begin{array}{llc}
\textbf{criterion} & \textbf{test} & \textbf{threshold} \\[3pt]
\text{no mass} & a_1 + a_2 \le 0 & — \\[3pt]
\text{one real mode} & \dfrac{\min_i a_i}{a_1 + a_2} < \tau_{\text{mass}}
  & 0.05 \\[8pt]
\text{mean on the boundary} & \min_i \mu_i < \delta \;\text{ or }\;
  \max_i \mu_i > 360 - \delta & \delta = 5^\circ \\[6pt]
\text{pedestal} & \max_i \sigma_i > \sigma_{\max} & 120^\circ \\[6pt]
\text{unresolved} & |\mu_1 - \mu_2| < \max_i \sigma_i & — \\[6pt]
\text{no reflex mode} & \text{not } \min_i \mu_i < 180^\circ < \max_i \mu_i & — \\[6pt]
\text{one peak} & p(x; \hat{\boldsymbol{\theta}}) \text{ has one maximum on } D & — \\[6pt]
\text{no support} & \displaystyle\sum_{|x_k - \mu_i| \le w_i} y_k
  < \tau_{\text{sup}} & 0.05
\end{array}
$$

The last test (no support) needs the density, not just the parameters, and uses the widened
window $w_i = \max(\sigma_i, h)$ so that a mode narrower than the bin spacing
cannot claim the mass of a bin it never covers. It is the only criterion that
catches a *spike* phantom — a very narrow mode parked where there is no data —
because a spike's amplitude is an integral and therefore not small.

The no-reflex and one-peak tests exist for the likelihood fit, which describes
convex angles alone with two convex normals, and covers a single wide or
skewed mode with two overlapping normals instead of parking a phantom. It cannot
work on a handful of angles, so the parametric errors also need at least 100
angles per sample (`MIN_FIT_ANGLES`) where the angles themselves are given.

A returned $\mu$ outside $[0, 360]$ is the free mean walking out of the
domain, not a measured angle; the boundary test above rejects it.

## 6. The metrics

### Parametric errors

For a reference fit $\hat{\boldsymbol{\theta}}^{\text{ref}}$ and a generated fit
$\hat{\boldsymbol{\theta}}^{\text{gen}}$,
{py:func}`combra.metrics.gauss_relative_errors` reports the **signed relative
error** per parameter and per mode,

$$
\varepsilon^{\theta}_i =
\frac{\hat{\theta}_i^{\text{gen}} - \hat{\theta}_i^{\text{ref}}}
     {\hat{\theta}_i^{\text{ref}}},
\qquad
\theta \in \{\mu, \sigma, a\},
\quad i \in \{1, 2\},
$$

six numbers keyed `mu1`, `mu2`, `sigma1`, `sigma2`, `amp1`, `amp2`. These are
errors, not distances: the sign says which way the generator is wrong, and the
reference fit is the denominator — which is precisely why §5 must screen both
sides first. Screening is applied to both fits and, if *either* is rejected, all
six are returned as $\text{nan}$ with the reason logged. Undefined rather than
wrong.

Because both sides are divided by the same reference, $\varepsilon$ is invariant
to any common rescaling of the amplitudes. As $a_1 + a_2 = 1$, the two amplitude
errors are one measurement:
$\hat a_1^{\text{ref}} \varepsilon^a_1 = -\hat a_2^{\text{ref}} \varepsilon^a_2$.

:::{warning}
$a_2 / (a_1 + a_2)$ is **not** the reflex-vertex fraction. The amplitudes include
whatever mass the normals place outside $D$, and the two-Gaussian model does not
reproduce all of the reflex mass. Quote $\sum_{x_k \ge 180} y_k$ from the data
when the physical fraction is what is wanted.
:::

### Transport distances

{py:func}`combra.metrics.wasserstein_density_metrics` compares two densities. The
angle metrics pass it the two fitted curves of §3, so the distances compare the
models (since 0.28.0; before, the histograms, which gave values 15 – 30 % larger
on the WC-Co sets). For one-dimensional distributions,

$$
W_p(u, v) = \left( \int_0^1
\bigl| F_u^{-1}(q) - F_v^{-1}(q) \bigr|^p \,\mathrm{d}q \right)^{1/p},
$$

evaluated after both densities are linearly interpolated onto one 1024-point
grid spanning their supports and renormalized, as in June 2026.
The circular variants apply the same construction on $\mathbb{R} / 360\mathbb{Z}$,
minimizing over the rotation offset, and are reported in degrees.

:::{warning}
POT's circular routine, `ot.wasserstein_circle` (0.9.7), returns about
$360^\circ$ minus the true distance for some inputs on grids of 256 – 1024
points. On the 1024-point grid a smooth two-mode pair $8.35^\circ$ apart reads
`circular_w1` $= 355.4^\circ$. None of 528 pairs of stored real angle densities
is affected; a circular value above $180^\circ$ is this fault, not a distance.
::: Four keys result: `w1`, `w2`,
`circular_w1`, `circular_w2`. They need both fitted curves, so they are `nan` when
a fit fails outright (fewer than six occupied bins), but not when a fit is only
screened as degenerate: while a generator still produces near-convex grains they
stay defined where the parametric errors do not.

### Convergence

A metric on a finite sample carries both the generator's systematic bias and
Monte-Carlo noise. Evaluating it over increasing $N$ and fitting

$$|m|(N) = A + B N^{-1/2}, \qquad A \ge 0$$

with {py:func}`combra.fitting.fit_plateau` separates them: $A$ is the bias floor
as $N \to \infty$ and $B$ scales the sampling term. Only $A$ is constrained —
forcing $B \ge 0$ would collapse a curve that approaches its floor from below to
$B = 0$, $A = \operatorname{mean}|m|$.

## Summary of symbols

| symbol | meaning | where |
|---|---|---|
| $\alpha_j$ | vertex angle, degrees on $[0, 360)$ | §1 |
| $\mathbf{d}_k$ | unit direction of the line fitted to edge $k$ | §1 |
| $h$ | histogram bin width, the {term}`step` | §2 |
| $x_k, y_k$ | occupied bin centres and bin probabilities, $\sum_k y_k = 1$ | §2 |
| $n, n_k$ | pooled angle count; count in bin $k$ | §2 |
| $\mu_i, \sigma_i, a_i$ | mode mean, width, weight ($a_1 + a_2 = 1$) | §3 |
| $Z_i$ | mass of normal $i$ inside $[0, 360]$, used for the leak | §3 |
| $c_j, P_j$ | count and model mass of bin $j$ of the fit | §4 |
| $r_j$ | share of bin $j$ that belongs to mode 1 | §4 |
| $\varepsilon^{\theta}_i$ | signed relative error of parameter $\theta$, mode $i$ | §6 |
| $A, B$ | convergence plateau and decay coefficients | §6 |
