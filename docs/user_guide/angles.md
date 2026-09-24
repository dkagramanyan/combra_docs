# Vertex angles and the angle density

The {term}`angle density` is combra's primary descriptor of a microstructure. It
is the normalized histogram of the interior angles measured at every vertex of
every grain contour in a sample.

## Why angles

A WC-Co microstructure is a packing of faceted carbide grains in a cobalt
binder. The quantity that distinguishes one alloy grade from another — and a good
generative model from a bad one — is the *shape* of those grains, not their
greyscale statistics. Vertex angles capture shape while being invariant to
translation, to the number of grains in the field of view, and to overall
brightness.

The resulting distribution is characteristically **bimodal**. A convex vertex
contributes an angle below 180°; a reflex vertex, where a grain is concave
because a neighbour intrudes into it, contributes one above. Realistic WC-Co
densities carry roughly 23% of their mass in the reflex mode. That second mode is
what the bimodal-Gaussian fit in `combra.fitting` is for, and its presence or
absence is diagnostic — see {ref}`undefined-rather-than-wrong`. The whole
scheme is stated formally in {doc}`angle_fit`.

Note that the two halves are not two ends of a circle. `vertex_angles` reports
$\theta$ for a convex vertex and $360° - \theta$ for a reflex one, so 1° is a
needle-thin protrusion and 359° a needle-thin notch: opposite shapes that happen
to sit at opposite ends of the axis. The angle domain is an **interval**, which
is why the fitted model is truncated to $[0°, 360°]$ rather than wrapped around
it.

## From image to angle

{py:func}`combra.angles.vertex_angles` performs the measurement on one grey
image $I$ in five stages (the method called P6 in the extraction report). Each
stage is stated with its input, its output and its own parameters.

**Stage 1 — detection mask.** $I \mapsto M$, a boolean image, true on the
cobalt ({py:func}`~combra.angles.pool_mask`). With $\tilde I$ the image after a
$3 \times 3$ median filter (`median`),

$$
M_0 = \{\tilde I \le t_{\mathrm{Otsu}}\} \;\cup\;
      \{\tilde I \le G_b * \tilde I - c\},
$$

where $t_{\mathrm{Otsu}}$ is Otsu's global threshold, $G_b * \tilde I$ the
Gaussian-weighted local mean over an odd window $b \approx 0.1 W$ of the image
width $W$, and $c = 8$ grey levels. The global term finds the interiors of large
pools, the local one the faint pools under an illumination gradient. The
8-connected components of $M_0$ smaller than `min_area` (10 px) are removed and
the result is dilated once by the 4-connected cross, giving $M$.

**Stage 2 — sub-pixel boundary.** $M \mapsto \{C_r\}$, one closed curve per
region boundary, holes included. The pixel contours of $M$ are traced, a hole's
reversed so that every curve has the cobalt on the same side. With the blurred
mask $F = G_\sigma * M$ ($\sigma$ = `sigma`, 0.7 px), each contour point
$\mathbf{p}$ with unit normal $\mathbf{n}$ is moved to

$$
\mathbf{p}' = \mathbf{p} + t^\ast \mathbf{n},
\qquad
t^\ast = \arg\min_{|t| \le \rho} \{\, |t| : F(\mathbf{p} + t\mathbf{n}) = \tfrac12 \,\},
$$

the crossing of the $\tfrac12$ level nearest the point within the reach
$\rho$ (`reach`, 1.5 px), located by linear interpolation between samples
0.5 px apart. A point with no crossing stays where it is.

**Stage 3 — vertices.** $\{C_r\} \mapsto \{(V_1, \dots, V_m)_r\}$. A curve whose
bounding box comes within `border_eps` px of the frame is dropped: a pool
clipped by the frame has vertices that are artefacts of the crop.
Douglas–Peucker at tolerance `tol` (1.75 px) selects the vertices $V_k$ from the
points of $C_r$, and a region left with fewer than four is dropped. The vertices
lie on the curve, so each edge $V_k V_{k+1}$ owns the arc of $C_r$ between them.

**Stage 4 — angles.** $\{(V_k), C_r\} \mapsto \{\alpha_k\}$. Every edge $k$
gets a line fitted by total least squares to the points of its arc, leaving
out those within $\varepsilon$ (`fit_exclusion`, 0.5 px) of arclength from
either vertex, where the corner rounds the boundary (all points are used when
fewer than three remain). With $\mathbf{m}_k$ and $\Sigma_k$ the mean and
covariance of those points, the line is $\mathbf{m}_k + s\,\mathbf{d}_k$, where
$\mathbf{d}_k$ is the leading eigenvector of $\Sigma_k$, oriented along the chord
$V_{k+1} - V_k$. At vertex $k$, between edges $k-1$ and $k$,

$$
\mathbf{u}_1 = -\mathbf{d}_{k-1}, \quad \mathbf{u}_2 = \mathbf{d}_k,
\qquad
\theta_k = \arccos \langle \mathbf{u}_1, \mathbf{u}_2 \rangle,
\qquad
\alpha_k =
\begin{cases}
\theta_k, & \det(\mathbf{u}_1, \mathbf{u}_2) > 0 \;\text{(convex)}, \\
360^\circ - \theta_k, & \text{otherwise (reflex)},
\end{cases}
$$

so $\alpha_k \in [0^\circ, 360^\circ)$. The vertex is then moved to the
intersection of the two lines, when they are not near-parallel
($|\mathbf{d}_{k-1} \times \mathbf{d}_k| > 0.05$) and the intersection lies
within 3 px of $V_k$. The angle does not depend on where along the curve
Douglas–Peucker placed the vertex, only on which edges it separates.

**Stage 5 — stored polygon.** $(V_k) \mapsto (V_k')$. The polygon is inset by

$$
\delta = \min\!\left(\delta_0 + \frac{\kappa}{d},\; \delta_{\max}\right),
\qquad
d = \sqrt{4A/\pi},
$$

with $A$ the polygon's area, $\delta_0$ = `inset` (1 px), $\kappa$ =
`inset_per_diameter` (10 px²) and $\delta_{\max}$ = `inset_cap` (3.5 px). Each
vertex moves along its corner bisector by the offset that shifts both adjacent
edges inward by exactly $\delta$ (along the outgoing edge's normal at a very
sharp corner). This undoes the dilation of stage 1 and the mask's outward
offset, which is larger for small pools. The angles are those of stage 4 and do
not depend on the inset.

The output is the concatenation of the $\alpha_k$ over all kept regions and
the list of the stored polygons, one row per angle.
{py:func}`~combra.angles.pool_regions` returns the same result with the mask of
stage 1 and the curve of stage 2 attached to every region.

```pycon
>>> from combra import data, angles
>>> img = data.load_microstructure().images[0]
>>> arr, polygons = angles.vertex_angles(img, border_eps=5, tol=1.75)
>>> arr.min(), arr.max()
```

{py:func}`~combra.angles.angle_summary` then fits the density of `arr` and
reports the two modes, the mass share, the fit residual and the model-free
reflex share in one named tuple.

### Choosing `tol`

The tolerance decides which bends of the boundary become vertices, so it is
**part of a result's identity**: {py:func}`combra.angles.output_directory`
encodes it in the output folder name (`..._tol1.75`) so runs made at different
settings cannot be silently compared. The default was chosen on the synthetic
set of {py:mod}`combra.synth`, where the truth is exact: at 1.75 px
the method recovers about 37% of the true corners with an RMS edge error of
0.67 px and the polygon overlaps the true region with an IoU of 0.81 averaged
over pools of 4–40 px. Below 8 px every corner reads too close to 180°, because
the blur rounds it over the whole edge of the pool; no setting of the stage
removes that, so small pools carry a known bias toward 180° rather than a
tunable one.

### The previous method

Until combra 0.15 the angles came from P0, now {py:func}`combra.legacy.vertex_angles`:
Otsu's threshold, Canny contours, Douglas–Peucker at 3 px and the pruning of
segments shorter than `min_segment_len`, with the angle between the chords at
each vertex. On the same synthetic set it recovers 12% of the true corners at an
RMS edge error of 1.26 px and misses the faint pools Otsu alone does not see. Its
parquets live in `..._msl5` folders and remain readable; a comparison across the
two methods is not meaningful, so every reference set is re-extracted with P6.

## From angles to a density

Raw angles are reduced to a density by
{py:func}`combra.stats.density_histogram`, which quantizes to multiples of
`step`, counts, and normalizes:

```{doctest}
>>> import numpy as np
>>> from combra import stats
>>> angles_array = np.array([12, 13, 87, 90, 92, 178, 180])
>>> x, y = stats.density_histogram(angles_array, step=5)
>>> float(y.sum())
1.0
```

Note that `y` sums to 1 over *bins*: these are bin probabilities, not a density
per degree, so their scale depends on `step`. The Wasserstein distances take them
as transport masses in exactly this form.

Each bin width is then fitted independently by
{py:func}`~combra.fitting.fit_bimodal_gaussian`, which seeds itself from the
density it is given. Earlier versions warm-started each width from the previous
one's solution; that made a bad fit at the finest, noisiest width propagate to
every coarser one, so it was removed.

Like `tol`, {term}`step` is part of a metric's identity: two runs are
comparable only when reduced at the same bin width. It is stored on every parquet
row and checked by {py:func}`combra.metrics.parquet_has_step`. The default is
{py:data}`~combra.metrics.training.DEFAULT_ANGLE_STEP` (5.0°).

## The bimodal model

The density is described by a mixture of two normal modes, each truncated to
the angle domain $D = [0^\circ, 360^\circ]$
({py:func}`combra.stats.truncated_bimodal_gaussian`):

$$
p(x; \boldsymbol{\theta}) =
T \left[ \frac{\pi}{Z_1}\, \varphi(x; \mu_1, \sigma_1)
      + \frac{1 - \pi}{Z_2}\, \varphi(x; \mu_2, \sigma_2) \right]
\mathbf{1}_{D}(x),
\qquad
Z_i = \Phi\!\left(\frac{360 - \mu_i}{\sigma_i}\right)
    - \Phi\!\left(\frac{-\mu_i}{\sigma_i}\right),
$$

where $\varphi(x; \mu, \sigma)$ is the normal density, $\Phi$ the standard
normal CDF, $\mu_i$ and $\sigma_i$ the position and width of mode $i$, and
$\boldsymbol{\theta} = (\mu_1, \mu_2, \sigma_1, \sigma_2, \pi)$. $Z_i$ is the
mass the $i$-th normal places inside $D$, so $\int_D p \,\mathrm{d}x = T$ and
$\pi$ is exactly the share of the mass in mode 1, $1 - \pi$ that in mode 2. Mode
1 is normally the convex mode and mode 2 the reflex one.

Given the histogram $(x_k, y_k)$ of bin width $h$,
{py:func}`~combra.fitting.fit_bimodal_gaussian` fixes the total mass to that of
the data, $T = h \sum_k y_k$, and solves

$$
\hat{\boldsymbol{\theta}}
= \arg\min_{\boldsymbol{\theta} \in \Theta}
\sum_k \bigl( y_k - p(x_k; \boldsymbol{\theta}) \bigr)^2,
\qquad
\Theta = [0, 360]^2 \times [10^{-6},\, 180]^2 \times [0, 1],
$$

by trust-region reflective least squares. The starting point is read off the
data, one mode per side of $180^\circ$: $\mu_i^{(0)}$ at the tallest bin of
that side, $\sigma_i^{(0)} = m_i / (\sqrt{2\pi}\, \max y_k)$ from the side's
mass $m_i$ and peak, and $\pi^{(0)} = m_1 / (m_1 + m_2)$. The result is ordered
so that $\mu_1 \le \mu_2$.

The fit always returns two modes, whether or not the data has two, so
$\hat{\boldsymbol{\theta}}$ is screened by
{py:func}`combra.metrics.degenerate_fit_reason` before it is read as a
measurement. {py:func}`~combra.angles.angle_summary` reports it together with
the relative residual
$\sum_k (p(x_k; \hat{\boldsymbol{\theta}}) - y_k)^2 / \sum_k y_k^2$ and the
model-free reflex share $\#\{\alpha_j > 180^\circ\} / n$, which is the one to
quote for the physical fraction of reflex vertices: on the reference sets
$1 - \hat\pi$ runs about 6% (relative) below it. Why least squares and not
maximum likelihood, why the modes are truncated rather than wrapped, and the
screening criteria are derived in {doc}`angle_fit`, §3–§5.

## Sample size

A single 128×128 image yields on the order of 20 vertex angles — enough to plot,
far too few to fit two modes to. Pool on the order of 1000 angles, roughly 48 such
images, before reporting a bimodal fit or any metric derived from one. The
Wasserstein distances in {doc}`metrics` are defined at any sample size, but they
too are noisy on small samples; the N-sweep described there is how that noise is
distinguished from real bias.

## Batch extraction

{py:meth}`combra.data.MicrostructureDataset.generate_angles` runs the extraction
over a whole dataset in parallel and writes the densities, fits and provenance to
parquet. See {doc}`../examples/angles` for a worked run, and
{py:mod}`combra.angles` for the plotting functions.
