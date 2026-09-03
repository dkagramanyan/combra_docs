# The angle fit, formally

The complete scheme behind combra's primary descriptor: how a contour becomes an
angle, angles become a density, the density becomes a bimodal-Gaussian fit, and
two fits become metrics. {doc}`angles` and {doc}`metrics` cover the same ground
in prose and are the better first read; this page fixes the notation and states
every formula the implementation actually uses.

## 1. From vertex to angle

Let a simplified contour be the closed polygon $P_1, \dots, P_M$. At vertex
$P_j$ with neighbours $P_{j-1}, P_{j+1}$, write the two edge vectors

$$\mathbf{v}_1 = P_{j-1} - P_j, \qquad \mathbf{v}_2 = P_{j+1} - P_j .$$

{py:func}`combra.angles.vertex_angles` reports

$$
\alpha_j =
\begin{cases}
\theta_j, & \det(\mathbf{v}_1, \mathbf{v}_2) < 0 \quad \text{(convex)} \\[4pt]
360^\circ - \theta_j, & \det(\mathbf{v}_1, \mathbf{v}_2) \ge 0 \quad \text{(reflex)}
\end{cases}
\qquad
\theta_j = \arccos \frac{\langle \mathbf{v}_1, \mathbf{v}_2 \rangle}
                       {\lVert \mathbf{v}_1 \rVert \, \lVert \mathbf{v}_2 \rVert}
\in [0^\circ, 180^\circ]
$$

with $\det(\mathbf{v}_1, \mathbf{v}_2) = v_1^x v_2^y - v_1^y v_2^x$, the signed
area of the pair. So $\alpha_j \in [0^\circ, 360^\circ)$, convex vertices occupy
the lower half and reflex vertices the upper half.

:::{important}
**The angle domain is an interval, not a circle.** $\alpha = 1^\circ$ is a
needle-thin protrusion and $\alpha = 359^\circ$ a needle-thin notch: opposite
shapes that happen to sit at opposite ends of the axis, not neighbours on a
circle. Everything downstream that *models a density* on this axis therefore
truncates rather than wraps. The Wasserstein distances of §6 are the one
exception, and deliberately so — there the circular variant is reported
alongside the linear one, because transport cost is a different question from
shape.
:::

:::{note}
**The angles are defined at the simplification scale.** A vertex exists only
after Douglas–Peucker simplification at tolerance `tol` (`angles_tol` in
{py:meth}`~combra.data.MicrostructureDataset.generate_angles`) and the pruning
of segments shorter than `min_segment_len`, so the angle density is a property
of the contour *at that scale*, not of the grain alone. On the 1024 px reference
set, raising `tol` from 2 to 5 px at `min_segment_len = 5` moves the fitted
convex mode from $117$–$119^\circ$ to $94$–$97^\circ$ and the reflex mode up by
$15$–$17^\circ$ across the three classes, while the model-free reflex share
$\sum_{x_k > 180} y_k$ moves by less than $0.04$; at `min_segment_len = 15` and
`tol` $\le 3$ the reflex mode dissolves into a $65$–$95^\circ$-wide shoulder and
the two-mode description of §3 no longer applies. Report both parameters with
every fitted mode, and compare fits only at equal parameters.
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
$\sum_k y_k h = h$ is the "area" the fitted curve of §3 matches. This convention
is what the Wasserstein distances of §6 consume directly, as transport masses.
:::

Bin occupancy sets the noise floor. With $n_k \approx n h / 360$ counts in a bin,
the relative sampling error is

$$
\frac{\operatorname{sd}(y_k)}{y_k} \approx \frac{1}{\sqrt{n_k}}
= \sqrt{\frac{360}{n h}},
$$

so halving $h$ costs a factor $\sqrt{2}$ in per-bin noise. At $h = 0.1^\circ$ a
class holds about $50\times$ fewer counts per bin than at $h = 5^\circ$, hence
about $7\times$ the relative noise — which is why the finest bin width is where
the estimator of §4 is most fragile.

## 3. The model

Write $\varphi(x; \mu, \sigma)$ and $\Phi(z)$ for the normal density and the
standard normal CDF, and let the angle domain be $D = [0^\circ, 360^\circ]$.
{py:func}`combra.stats.truncated_bimodal_gaussian` is

$$
p(x; \boldsymbol{\theta}) =
T \left[ \frac{\pi}{Z_1}\, \varphi(x; \mu_1, \sigma_1)
      + \frac{1 - \pi}{Z_2}\, \varphi(x; \mu_2, \sigma_2) \right]
\mathbf{1}_{D}(x),
\qquad
Z_i = \Phi\!\left(\frac{360 - \mu_i}{\sigma_i}\right)
    - \Phi\!\left(\frac{0 - \mu_i}{\sigma_i}\right)
$$

with parameter vector
$\boldsymbol{\theta} = (\mu_1, \mu_2, \sigma_1, \sigma_2, \pi)$ and a total mass
$T$ that is set by the data rather than fitted (§4).

Three consequences are the reason for the truncation.

**Mass is conserved and interpretable.** Because $Z_i$ is exactly the mass the
$i$-th parent normal places inside $D$,

$$
\int_D p \,\mathrm{d}x = T,
\qquad
\int_D \frac{T\,\pi}{Z_1} \varphi(x; \mu_1, \sigma_1)\,\mathrm{d}x = T\,\pi ,
$$

so $\pi$ *is* the share of the mass in mode 1 and $1 - \pi$ the share in mode 2,
whatever the widths. An untruncated mixture with amplitudes $a_i$ has
$\int_{\mathbb{R}} = a_1 + a_2$ instead, and the fraction lost outside $D$,

$$
\text{leak} = 1 - \frac{1}{a_1 + a_2}\sum_{i=1}^{2} a_i Z_i ,
$$

reached 99.75% on real reference sets before truncation was adopted.

**Pedestals stay bounded.** A plain Gaussian of peak height $h_\ast$ satisfies
$a = h_\ast \sigma \sqrt{2\pi}$, so holding a wide pedestal at fixed height
forces $a \propto \sigma$ — fitted $\sigma = 10^5$ degrees with $a = 2\times10^3$
against an expected 5 were observed. Under truncation,

$$\lim_{\sigma \to \infty} p(x) \;=\; \frac{T}{360},$$

a uniform density of bounded amplitude. A pedestal remains *representable*, so
§5 still has to screen for it, but it no longer diverges.

**It matches the measurement.** No probability mass is placed on angles that
cannot occur.

## 4. The estimator

Given $(x_k, y_k)$, {py:func}`combra.fitting.fit_bimodal_gaussian` solves the
bound-constrained nonlinear least-squares problem

$$
\hat{\boldsymbol{\theta}}
= \arg\min_{\boldsymbol{\theta} \in \Theta}
\sum_k \bigl( y_k - p(x_k; \boldsymbol{\theta}) \bigr)^2 ,
\qquad
T = h \sum_k y_k ,
$$

$$
\Theta = [0, 360]^2 \times [10^{-6},\, 180]^2 \times [0, 1]
$$

by trust-region reflective least squares. The objective is fitted to $y_k$ on
the bin-probability scale of §2, where the curve that reproduces the data
integrates to $h$, so the total $T$ is fixed to that (and to the total count
when raw counts are passed) rather than fitted. A free pair of amplitudes,
which the fit had until 0.13.0, only ever carried this scale: replacing them
with $\pi$ moves the fitted modes by under $0.7^\circ$ and the residual by under
2% on the reference sets, and by $0.13^\circ$ in $\mu_1$, $1.5^\circ$ in
$\mu_2$ and $0.012$ in $\pi$ at the 95th percentile over all 231 stored real
densities.

### Why least squares on the histogram, and not maximum likelihood

Maximum likelihood on the raw angles, or equivalently on the grouped counts at
any $h \le 5^\circ$ (the two agree to $0.1^\circ$), was tried on the nine
reference class-sets (three resolutions, three classes, $n$ from
$7 \times 10^4$ to $2 \times 10^6$) and rejected. Both estimators converge
from every start and neither degenerates, but with *this* model the likelihood
moves $\mu_2$ up by $7$–$16^\circ$, widens $\sigma_2$ by 30–80% and halves the
reflex peak, and its histogram residual is $1.2$–$2\times$ that of least
squares. The gain in log-likelihood comes almost entirely from the edge tails:
1–8% of the vertices lie below $60^\circ$ or above $300^\circ$, where two
Gaussians centred on the modes leave essentially no mass, and a likelihood cannot
leave data uncovered. The histogram objective is nearly indifferent to them:
a tail's residual is its tiny absolute mass, so the fit describes the peaks
(with free amplitudes it left 0.8–2.4% of the mass unclaimed on the reference
sets; with the total fixed it spreads that over the modes, which move by less
than a degree). Adding a uniform background component brings the
likelihood's $\mu_2$ back to within $1$–$3^\circ$ of the least-squares value at
512 and 1024 px but is not identifiable at 256 px, where the reflex mode is
itself $47^\circ$ wide. The fitted $\mu_i, \sigma_i$ are therefore peak
descriptors, not the parameters of a generative model of the whole density,
and should be read as such. The size of the model's tail deficit is visible
without any refit as the gap between the fit's mass above $180^\circ$ and the
density's own share: at most $0.027$ (median $0.010$) over the 231 stored fits
of real angle densities.

### Constraints

| bound | reason |
|---|---|
| $\mu_i \in [0, 360]$ | left free, the solver walks a mode out of the domain; $\mu = 648^\circ$ and $-167^\circ$ have both been observed |
| $\sigma_i \ge 10^{-6}$ | excludes the sign-flipped minimum $\sigma_2 < 0$ that weakly bimodal data invites |
| $\sigma_i \le 180$ | half the domain; wider is a pedestal, not a peak |
| $\pi \in [0, 1]$ | a share; mode 2 carries $1 - \pi$ |

The width bound is $180^\circ$ and **not** the $120^\circ$ at which §5 rejects.
That test is a strict $\sigma_{\max} > 120$, so bounding the solver at the
rejection threshold would park every pedestal at exactly $120.0$ and silently
switch the rejection off.

### Initialization

The objective is not convex, and on a density with a weak reflex mode over a
heavy baseline a broad pedestal is a genuine competing minimum. The starting
point is therefore read off the data rather than fixed. Splitting the domain at
$180^\circ$ into $S_1 = \{x_k < 180\}$ and $S_2 = \{x_k \ge 180\}$, and using
$a = h_\ast \sigma \sqrt{2\pi}$ in reverse:

$$
\mu_i^{(0)} = \arg\max_{x_k \in S_i} y_k,
\qquad
m_i = h \sum_{x_k \in S_i} y_k,
\qquad
\sigma_i^{(0)} = \frac{m_i}{\sqrt{2\pi} \, \max_{x_k \in S_i} y_k},
\qquad
w^{(0)} = \frac{m_1}{m_1 + m_2}
$$

with $\sigma_i^{(0)}$ clipped into $[1, 162]$ and $w^{(0)}$ into $[0.01, 0.99]$
so the solver never starts on a bound. Measured over 231 fits of real angle densities, this replaced 83
degenerate results with 0, improved 58 fits by more than 5% in residual, and made
none worse.

Each bin width is fitted independently. Warm-starting each $h$ from the previous
one's solution — as
{py:meth}`~combra.data.MicrostructureDataset.generate_angles` once did — makes
the whole sweep inherit the failure of its noisiest member (§2), turning one bad
fit into seven.

### Mode ordering

The model is invariant under exchanging its two modes, so the solver's slot
assignment is arbitrary. Results are canonicalized by

$$\mu_1 \le \mu_2 ,$$

with $\sigma$ permuted to match and $\pi \mapsto 1 - \pi$, so slot 1 is always the
lower-angle mode. §6 compares fits slot-wise and needs this.

## 5. When a fit is not a measurement

The model has two modes whether or not the data does, so a fit must be screened
before its parameters are read as measurements.
{py:func}`combra.metrics.degenerate_fit_reason` rejects
$\hat{\boldsymbol{\theta}}$ when any of the following holds, in this order:

$$
\begin{array}{llc}
\textbf{criterion} & \textbf{test} & \textbf{threshold} \\[3pt]
\text{no mass} & w_1 + w_2 \le 0 & — \\[3pt]
\text{one real mode} & \min(w_1, w_2) < \tau_{\text{mass}}
  & 0.05 \\[8pt]
\text{mean on the boundary} & \min_i \mu_i < \delta \;\text{ or }\;
  \max_i \mu_i > 360 - \delta & \delta = 5^\circ \\[6pt]
\text{pedestal} & \max_i \sigma_i > \sigma_{\max} & 120^\circ \\[6pt]
\text{unresolved} & |\mu_1 - \mu_2| < \max_i \sigma_i & — \\[6pt]
\text{no support} & \displaystyle\sum_{|x_k - \mu_i| \le w_i} y_k
  < \tau_{\text{sup}} & 0.05
\end{array}
$$

The last test needs the density, not just the parameters, and uses the widened
window $w_i = \max(\sigma_i, h)$ so that a mode narrower than the bin spacing
cannot claim the mass of a bin it never covers. It is the only criterion that
catches a *spike* phantom — a very narrow mode parked where there is no data —
because a spike's amplitude is an integral and therefore not small.

A returned $\mu$ of exactly $0$ or $360$, or a $\sigma$ of exactly $180$, is the
solver sitting on a bound of §4 rather than a measured quantity.

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
\theta \in \{\mu, \sigma\},
\quad i \in \{1, 2\},
\qquad
\varepsilon^{\pi} =
\frac{\hat{\pi}^{\text{gen}} - \hat{\pi}^{\text{ref}}}
     {\hat{\pi}^{\text{ref}}},
$$

five numbers keyed `mu1`, `mu2`, `sigma1`, `sigma2`, `pi`. These are
errors, not distances: the sign says which way the generator is wrong, and the
reference fit is the denominator — which is precisely why §5 must screen both
sides first. Screening is applied to both fits and, if *either* is rejected, all
five are returned as $\text{nan}$ with the reason logged. Undefined rather than
wrong.

$\mu$ and $\sigma$ are reported per mode, $\pi$ once. The second mode's share
is $1 - \pi$, so its relative error is
$-\varepsilon^{\pi}\,\pi^{\text{ref}} / (1 - \pi^{\text{ref}})$ — a
restatement of $\varepsilon^{\pi}$, not a second measurement, and it was
reported as one (the key `share2`) until 0.14.0.

The shares are scale-free by construction, so the histogram's bin width cannot
enter the errors.

:::{warning}
$1 - \pi$ is **not** the reflex-vertex fraction, though it is close.
On the reference sets it runs about 6% low in relative terms — the two-Gaussian
model does not reproduce all of the reflex mass. Quote
$\sum_{x_k \ge 180} y_k$ from the data when the physical fraction is what is
wanted.
:::

### Transport distances

{py:func}`combra.metrics.wasserstein_density_metrics` compares the two densities
directly, with no fit and therefore no screening. For one-dimensional
distributions,

$$
W_p(u, v) = \left( \int_0^1
\bigl| F_u^{-1}(q) - F_v^{-1}(q) \bigr|^p \,\mathrm{d}q \right)^{1/p},
$$

evaluated on the union of the two supports. The circular variants apply the same
construction on $\mathbb{R} / 360\mathbb{Z}$, minimizing over the rotation
offset, and are reported in degrees. Four keys result: `w1`, `w2`,
`circular_w1`, `circular_w2`. Unlike the parametric errors above these are defined at
any sample size, which makes them the ones to watch while a generator is still
producing near-convex grains.

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
| $h$ | histogram bin width, the {term}`step` | §2 |
| $x_k, y_k$ | occupied bin centres and bin probabilities, $\sum_k y_k = 1$ | §2 |
| $n, n_k$ | pooled angle count; count in bin $k$ | §2 |
| $\mu_i, \sigma_i$ | mode mean, parent width | §3 |
| $\pi$, $T$ | share of the mass in mode 1; total mass of the curve, $h \sum_k y_k$ | §3, §4 |
| $Z_i$ | mass of parent normal $i$ inside $[0, 360]$ | §3 |
| $\Theta$ | the box the fit is constrained to | §4 |
| $\varepsilon^{\theta}_i$ | signed relative error of parameter $\theta$, mode $i$ | §6 |
| $A, B$ | convergence plateau and decay coefficients | §6 |
