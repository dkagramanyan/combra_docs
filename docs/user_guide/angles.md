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
is why the fitted model is not wrapped around it.

## From image to angle

{py:func}`combra.angles.vertex_angles` measures the angles of one image in two
calls (the method called P0 in the extraction report).

**Preprocessing.** {py:func}`~combra.angles.preprocess_image` reduces the image
to a three-level map:

1. a median filter over a disk of radius `disk` (3), its rank near the frame
   that of the full disk, counted over the pixels inside the image;
2. Otsu's threshold;
3. the morphological gradient of the thresholded mask.

The mask and its boundary are stored in one `uint8` array with the levels 0,
127 and 254. A colour image is converted as RGB, so an image read with OpenCV
must be converted from BGR first. The same map is the input of the beam fit,
{doc}`beams`.

**Angles.** {py:func}`~combra.angles.vertex_angles` then takes that map:

1. contours are found, and a contour whose bounding box comes within
   `border_eps` px of the frame is dropped: a grain clipped by the frame has
   vertices that are artefacts of the crop;
2. each contour is simplified with Douglas–Peucker at `tol` px (default 3), and
   one left with three or fewer vertices is dropped;
3. vertices are removed one at a time, shortest neighbouring segment first,
   until no segment is shorter than `min_segment_len` px (default 10) or only
   three vertices remain;
4. the angle at every remaining vertex $V_k$ is measured between the chords
   $\mathbf{a} = V_{k-1} - V_k$ and $\mathbf{b} = V_{k+1} - V_k$,

   $$
   \theta_k = \arccos
   \frac{\langle \mathbf{a}, \mathbf{b} \rangle}{\|\mathbf{a}\|\,\|\mathbf{b}\|},
   $$

   and the sign of $\det[\mathbf{a}\ \mathbf{b}]$ selects $\theta_k$ or
   $360^\circ - \theta_k$, so a reflex vertex is kept above 180° rather than
   folded into $[0^\circ, 180^\circ]$.

The output is the concatenation of the angles over all kept contours and the
list of the simplified contours that produced them.

```pycon
>>> from combra import data, angles
>>> img = data.load_microstructure().images[0]
>>> prep = angles.preprocess_image(img)
>>> arr, contours = angles.vertex_angles(prep, border_eps=5, tol=3, min_segment_len=10.0)
>>> arr.min(), arr.max()
```

{py:func}`~combra.angles.angle_summary` then fits the density of `arr` and
reports the two modes, their amplitudes, the fit residual and the model-free
reflex share in one named tuple.

### Choosing `tol` and `min_segment_len`

Both settings decide which bends of the boundary become vertices. `tol` is how
far the simplified contour may leave the pixel contour. `min_segment_len` then
suppresses the staircase vertices of the pixel boundary: raising it gives fewer
angles and a smoother density, and 5 to 20 px is the useful range. Densities
extracted at different values are different measurements, so the value is
**part of a result's identity**: {py:func}`combra.angles.output_directory`
writes it into the output folder name (`..._msl5`), so runs made at different
settings cannot be silently compared.

### The experimental method

{py:mod}`combra.experimental` holds P6, which detects the cobalt pools itself,
locates their boundary to sub-pixel precision and reads each angle from lines
fitted to the boundary; {doc}`experimental` describes it. From 0.15.0 to 0.20.2
P6 was the method of this module, and the parquets extracted with it live in
`..._tol1.75` and `..._scale0.25` folders and remain readable. A comparison
across the two methods is not meaningful, so both sides of a comparison are
always extracted with the same method.

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
{py:func}`~combra.fitting.fit_bimodal_gaussian`, from the same fixed start at
every width. Earlier versions warm-started each width from the previous
one's solution; that made a bad fit at the finest, noisiest width propagate to
every coarser one, so it was removed.

Like `min_segment_len`, {term}`step` is part of a metric's identity: two runs are
comparable only when reduced at the same bin width. It is stored on every parquet
row and checked by {py:func}`combra.metrics.parquet_has_step`. The default is
{py:data}`~combra.metrics.training.DEFAULT_ANGLE_STEP` (5.0°).

## The bimodal model

The density is described by the sum of two normal modes
({py:func}`combra.stats.bimodal_gaussian`):

$$
p(x; \boldsymbol{\theta}) =
a_1\, \varphi(x; \mu_1, \sigma_1) + a_2\, \varphi(x; \mu_2, \sigma_2),
$$

where $\varphi(x; \mu, \sigma)$ is the normal density, $\mu_i$, $\sigma_i$ and
$a_i$ the position, width and amplitude of mode $i$, and
$\boldsymbol{\theta} = (\mu_1, \mu_2, \sigma_1, \sigma_2, a_1, a_2)$. The modes
are not truncated to the angle domain $D = [0^\circ, 360^\circ]$: $a_i$ is the
integral of mode $i$ over the whole real line, part of which may lie outside
$D$. Mode 1 is normally the convex mode and mode 2 the reflex one. This is the
model combra fitted when the training-time metrics of June 2026 were logged.

Given the histogram $(x_k, y_k)$ of bin width $h$,
{py:func}`~combra.fitting.fit_bimodal_gaussian` solves

$$
\hat{\boldsymbol{\theta}}
= \arg\min_{\boldsymbol{\theta}}
\sum_k \bigl( y_k - p(x_k; \boldsymbol{\theta}) \bigr)^2,
\qquad
\sigma_i \ge 10^{-6},\; a_i \ge 0,
$$

by Levenberg–Marquardt from the fixed start
$(\mu_1, \mu_2, \sigma_1, \sigma_2, a_1, a_2)^{(0)} = (100, 240, 30, 30, 1, 1)$,
with the means free. The start assumes a histogram that sums to one, as
{py:func}`combra.stats.density_histogram` returns it, and then
$a_1 + a_2 \approx h$, so amplitudes compare only at one bin width. The result
is ordered so that $\mu_1 \le \mu_2$.

The fit always returns two modes, whether or not the data has two, so
$\hat{\boldsymbol{\theta}}$ is screened by
{py:func}`combra.metrics.degenerate_fit_reason` before it is read as a
measurement. {py:func}`~combra.angles.angle_summary` reports it together with
the relative residual
$\sum_k (p(x_k; \hat{\boldsymbol{\theta}}) - y_k)^2 / \sum_k y_k^2$ and the
model-free reflex share $\#\{\alpha_j > 180^\circ\} / n$, which is the one to
quote for the physical fraction of reflex vertices rather than the fitted
$\hat a_2 / (\hat a_1 + \hat a_2)$. Why least squares and not maximum
likelihood, and the screening criteria, are derived in {doc}`angle_fit`,
§3–§5.

{py:mod}`combra.experimental` holds a five-parameter variant of the model,
truncated to $D$, in which the two amplitudes are replaced by one mass share
and a total fixed by the data; see {doc}`experimental`.

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
