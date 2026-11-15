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

Note that the two halves are not two ends of a circle. `vertex_angles` (either version) reports
$\theta$ for a convex vertex and $360° - \theta$ for a reflex one, so 1° is a
needle-thin protrusion and 359° a needle-thin notch: opposite shapes that happen
to sit at opposite ends of the axis. The angle domain is an **interval**, which
is why the fitted model is not wrapped around it.

## From image to angle

The angle pipeline is that of Straumal et al., *Materials* 16, 5560 (2023) —
median filter, Otsu, gradient, Canny, border following, Douglas–Peucker, chord
angles — plus the short-side pruning of step 3 below, with every setting a length on
the sample (see {ref}`pixel-size`). {py:func}`combra.angles.vertex_angles` measures
the angles of one image in two calls.

**Preprocessing.** {py:func}`~combra.angles.preprocess_image` reduces the image
to a three-level map:

1. an image coarser than 0.15 µm per pixel is enlarged twice (bicubic), so that the
   lengths below span enough pixels;
2. a median filter over a disk of radius 0.1 µm on the sample, its rank near the
   frame that of the full disk, counted over the pixels inside the image;
3. Otsu's threshold;
4. the morphological gradient of the thresholded mask.

The mask and its boundary are stored in one `uint8` array with the levels 0,
127 and 254. A colour image is converted as RGB, so an image read with OpenCV
must be converted from BGR first.

In the map, 254 is carbide, 127 the cobalt interior and 0 the cobalt pixels on the
phase boundary. The carbide pixels on the boundary come out 127 as well (the
`uint8` arithmetic wraps), so the grey region of the map is the cobalt grown by one
pixel. Count cobalt with {py:func}`combra.contours.cobalt_mask`, not on the map.

(pixel-size)=
### Pixel size

The pixel size is the length of the sample one pixel covers, in µm. The WC-Co
micrographs were taken at 5000×, where one pixel is 0.049687 µm
(`combra.data.SEM_PIXEL_SIZE`, from the microscope's TIFF metadata). The training
images are 1024 px crops of them resized to $w$ px, so their pixel size is
$0.049687 \cdot 1024 / w$. Every setting of the pipeline is a length on the sample,
turned into pixels by {py:func}`~combra.angles.angle_settings`:

| setting | on the sample | 256 × 256 (0.199 µm/px) | 512 × 512 (0.099 µm/px) | 1024 × 1024 (0.050 µm/px) |
|---|---|---|---|---|
| enlargement | above 0.15 µm/px | 2× | — | — |
| median radius | 0.1 µm | 1 px | 1 px | 2 px |
| Douglas–Peucker `tol` | 0.4 µm | 4.0 px | 4.0 px | 8.1 px |
| shortest side `min_segment_len` | 0.8 µm | 8.1 px | 8.1 px | 16.1 px |
| cobalt-mask median | 0.4 µm | 2 px | 4 px | 8 px |

At 256 px the angle settings are in pixels of the enlarged image. A setting of fixed
size in pixels acts on different features at different resolutions: the 3 px
tolerance of combra before 0.31 is 0.6 µm of the sample at 256 px but 0.15 µm at
1024 px. With all lengths fixed on the sample the same field gives the same angle
distribution at all three sizes: on the real crops the Wasserstein-1 distance between
the 256 and 1024 px distributions of the same fields is 5.5° (37.5° with the
settings of 0.30).

The angles and the cobalt fraction use different medians. A median rounds the
corners it filters: the 0.4 µm median keeps the cobalt fraction of the training crops
within 2.4 % of the alloys' cobalt volume fraction at all three sizes, but blunts the
sharp corners, which then read as 100–130°. The angles use 0.1 µm; the cobalt mask
({py:func}`combra.contours.cobalt_mask`, {py:func}`combra.contours.median_radius`), the
cobalt areas and the semi-axes keep 0.4 µm.

Every extraction therefore needs the pixel size: {py:func}`~combra.angles.preprocess_image`,
{py:func}`~combra.angles.vertex_angles`, {py:func}`combra.contours.areas` and every
metric take `pixel_size` and raise `ValueError` without it. An explicit `disk` gives
the map of that median without enlargement, with the 3 and 5 px tolerance and
shortest side of earlier versions (`disk=3` reproduces the angles of combra before
0.30). The dataset class and the h5 comparisons read the pixel size from the file's
`pixel_size_um` attribute.

```pycon
>>> from combra import angles, data
>>> for w in (256, 512, 1024):
...     s = angles.angle_settings(data.SEM_PIXEL_SIZE * 1024 / w)
...     print(w, s.scale, s.disk, round(s.tol, 1), round(s.min_segment_len, 1))
256 2 1 4.0 8.1
512 1 1 4.0 8.1
1024 1 2 8.1 16.1
```

**Angles.** {py:func}`~combra.angles.vertex_angles` then takes that map:

1. contours are found, and a contour whose bounding box comes within
   `border_eps` px of the frame is dropped: a grain clipped by the frame has
   vertices that are artefacts of the crop;
2. each contour is simplified with Douglas–Peucker at `tol` (0.4 µm), and one left
   with three or fewer vertices is dropped;
3. vertices are removed one at a time, shortest neighbouring side first, until no
   side is shorter than `min_segment_len` (0.8 µm) or only three vertices remain;
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
>>> px = data.SEM_PIXEL_SIZE
>>> prep = angles.preprocess_image(img, pixel_size=px)
>>> arr, contours = angles.vertex_angles(prep, pixel_size=px)
>>> arr.min(), arr.max()
```

{py:func}`~combra.angles.angle_summary` then fits the density of `arr` and
reports the two modes, their amplitudes, the fit residual and the model-free
reflex share in one named tuple.

### Choosing `tol` and `min_segment_len`

Both settings decide which bends of the boundary become vertices. `tol` is how
far the simplified contour may leave the pixel contour. `min_segment_len` then
suppresses the staircase vertices of the pixel boundary: raising it gives fewer
angles and a smoother density. Pruning stops at three vertices, so it cuts both
ways:

- **Too long** turns small pools into triangles. A pool whose perimeter is under
  about three times `min_segment_len` keeps three vertices, whose angles add up
  to 180° and are never reflex.
- **Too short** keeps the staircase of the pixel boundary and splits corners: the
  histogram fills with angles near the multiples of 45°.

The values 0.4 µm and 0.8 µm were chosen on synthetic micrographs with exact angles
and on the real crops at 256, 512 and 1024 px, for the distance to the true angle
distribution, the quality of the bimodal fit, the absence of pixel-grid spikes and
the agreement between resolutions. On the synthetic images the Wasserstein-1 distance
to the truth is 29°, 27° and 22° at 256, 512 and 1024 px, against 28°, 39° and 48°
with the settings of 0.30. Every method measured underestimates the share of reflex
vertices (0.17–0.21 against 0.37), because a pixel mask does not resolve the short
notches of the boundary.

Densities extracted at different values are different measurements, so the value is
**part of a result's identity**: `combra.angles.output_directory` writes
`min_segment_len` into the output folder name (`..._msl5`), and the parquets record
the pixel size, the enlargement and the pixel values of the settings.

### History

combra 0.15.0–0.20.2 measured the angles with a second method (P6: a detection mask,
a sub-pixel boundary and angles from lines fitted to it), from 0.25.0 to 0.30.0 kept
as `combra.angles.vertex_angles.v2` beside this one (`v1`). It was removed in 0.31.0;
the parquets extracted with it (`..._tol1.75` and `..._scale0.25` folders) remain
readable but are not comparable with the densities of this pipeline.

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
per degree, so their scale depends on `step`. The bimodal fit takes them in
exactly this form, and the Wasserstein distances compare the fitted curves.

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

`combra.fitting.fit_bimodal_share` fits a five-parameter variant of the model,
truncated to $D$, in which the two amplitudes are replaced by one mass share
and a total fixed by the data.

## Sample size

A single 128×128 image yields on the order of 20 vertex angles — enough to plot,
far too few to fit two modes to. Pool on the order of 1000 angles, roughly 48 such
images, before reporting a bimodal fit or any metric derived from one, including
the Wasserstein distances in {doc}`metrics`, which compare the fits. They are noisy
on small samples too; the N-sweep described there is how that noise is
distinguished from real bias.

## Batch extraction

{py:meth}`combra.data.MicrostructureDataset.generate_angles` runs the extraction
over a whole dataset in parallel and writes the densities, fits and provenance to
parquet. See {doc}`../examples/angles` for a worked run, and
{py:mod}`combra.angles` for the plotting functions.
