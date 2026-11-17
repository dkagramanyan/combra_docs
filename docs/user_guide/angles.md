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

The angle pipeline follows Straumal et al., *Materials* 16, 5560 (2023) — median
filter, Otsu, contours, Douglas–Peucker, chord angles — with the boundary traced
between the pixels and the spike removal of the steps below, and
every setting a length on the sample (see {ref}`pixel-size`).
{py:func}`combra.angles.vertex_angles` measures the angles of one image in two calls.

**Preprocessing.** {py:func}`~combra.angles.preprocess_image` filters the image:

1. an image coarser than 0.15 µm per pixel is enlarged twice (bicubic), so that the
   lengths below span enough pixels;
2. a median filter over a disk of radius 0.1 µm on the sample, its rank near the
   frame that of the full disk, counted over the pixels inside the image.

A colour image is converted as RGB, so an image read with OpenCV must be converted from
BGR first. The 0.1 µm median keeps small noise specks, so count cobalt with
{py:func}`combra.contours.cobalt_mask` (0.4 µm), not on this image.

```{versionchanged} 0.33.0
The contours are the boundaries of the cobalt regions instead of the outer borders of
the Canny edges of the three-level map (0/127/254). Two pools 1–3 px apart had touching
edge lines and were traced as one polygon, with chords across the carbide and angles
near 0° and 360° at the join. The three-level map (`combra.angles._core.binary_map`) is
still built for the crack graph and the MVEE fit.
```

```{versionchanged} 0.35.0
`preprocess_image` returns the filtered grey image, not its Otsu binary:
{py:func}`~combra.angles.vertex_angles` places the boundary between the pixels and needs
the grey levels for it. The polygons are built by the steps listed under **Angles**
below; before, the boundary was the chain of boundary pixels, the tolerance 0.4 µm,
sides under 0.7 µm were cut off with a chord, and triangles and regions at the frame
were dropped. Densities of 0.35 and of earlier versions are not comparable.
```

```{versionchanged} 0.36.0
No side is rebuilt: 0.35 replaced a side under 0.4 µm by the point where its two
neighbours meet, and removed the vertices within 12° of 180°. The rebuilt corners could
stick out past the region, and their angles put a kink near 50° on the first mode.
Densities of 0.36 and 0.35 are not comparable.
```

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
| Douglas–Peucker `tol` | 0.15 µm | 1.5 px | 1.5 px | 3.0 px |
| rebuilt side `min_segment_len` | none | 0 | 0 | 0 |
| spike width (4/3 `tol`) | 0.2 µm | 2.0 px | 2.0 px | 4.0 px |
| cobalt-mask median | 0.4 µm | 2 px | 4 px | 8 px |

At 256 px the angle settings are in pixels of the enlarged image. A setting of fixed
size in pixels acts on different features at different resolutions: the 3 px
tolerance of combra before 0.31 is 0.6 µm of the sample at 256 px but 0.15 µm at
1024 px. With all lengths fixed on the sample the same field gives close angle
distributions at different sizes: on the real crops the Wasserstein-1 distance between
the 256 and 512 px distributions of the same fields is 1.9–3.5° (0.2–0.4° with the
coarser polygons of 0.33–0.34, 37.5° between 256 and 1024 px with the settings of
0.30).

The angles and the cobalt fraction use different medians. A median rounds the
corners it filters: the 0.4 µm median keeps the cobalt fraction of the training crops
within 2.4 % of the alloys' cobalt volume fraction at all three sizes, but blunts the
sharp corners, which then read as 100–130°. The angles use 0.1 µm; the cobalt mask
({py:func}`combra.contours.cobalt_mask`, {py:func}`combra.contours.median_radius`), the
cobalt areas and the semi-axes keep 0.4 µm.

Every extraction therefore needs the pixel size: {py:func}`~combra.angles.preprocess_image`,
{py:func}`~combra.angles.vertex_angles`, {py:func}`combra.contours.areas` and every
metric take `pixel_size` and raise `ValueError` without it. An explicit `disk` gives
the image of that median without enlargement, with a tolerance of 3 px. The dataset class and the h5 comparisons read the pixel size from the file's
`pixel_size_um` attribute.

```pycon
>>> from combra import angles, data
>>> for w in (256, 512, 1024):
...     s = angles.angle_settings(data.SEM_PIXEL_SIZE * 1024 / w)
...     print(w, s.scale, s.disk, round(s.tol, 1), round(s.min_segment_len, 1))
256 2 1 1.5 0.0
512 1 1 1.5 0.0
1024 1 2 3.0 0.0
```

**Angles.** {py:func}`~combra.angles.vertex_angles` then takes that image:

1. the image is split at its Otsu level, and the boundary of every cobalt region is
   traced between the pixels, where the image crosses that level (marching squares).
   A chain of whole boundary pixels would put the angles of small regions on the pixel
   grid, at 45°, 63°, 72° and 90°. A region clipped by the frame is closed along it;
2. each boundary is simplified with Douglas–Peucker at `tol` (0.15 µm), so no boundary
   point is further than that from the polygon. A vertex that is nearly straight lies
   within the tolerance of the line through its neighbours, so almost no angle between
   168° and 192° is left;
3. spikes narrower than 4/3 `tol` (0.2 µm) are removed: a vertex whose neighbour lies
   closer than that to the side on its other hand is dropped and the polygon closed
   across it, narrowest first, and a polygon that is all spike is dropped. A cobalt
   film that thin has its two sides on one line: its tip would read as an angle near
   0° and its folds near 360°;
4. polygons of three or more vertices are kept;
5. the angle at every remaining vertex $V_k$ is measured between the chords
   $\mathbf{a} = V_{k-1} - V_k$ and $\mathbf{b} = V_{k+1} - V_k$,

   $$
   \theta_k = \arccos
   \frac{\langle \mathbf{a}, \mathbf{b} \rangle}{\|\mathbf{a}\|\,\|\mathbf{b}\|},
   $$

   and the sign of $\det[\mathbf{a}\ \mathbf{b}]$ selects $\theta_k$ or
   $360^\circ - \theta_k$, so a reflex vertex is kept above 180° rather than
   folded into $[0^\circ, 180^\circ]$. The vertices within a pixel of the frame are
   created by the crop and are not measured.

The output is the concatenation of the angles over all polygons and the list of the
polygons that produced them.

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

`tol` is how far the polygon may leave the boundary.

- **A coarse tolerance** (0.4 µm in 0.31–0.34) lets the sides leave the outline, turns
  small regions into needle triangles and loses the short sides of large ones.
- **A fine tolerance** follows the outline. Douglas–Peucker keeps a vertex only if it
  stands out of the line through its neighbours by more than the tolerance, so the
  noise of a straight side adds almost no vertices.

`min_segment_len` is the length under which a side is read as a corner the median has
rounded and is rebuilt: its two neighbours are extended past it, and the point where
they meet replaces the side if it lies within 1.5 `min_segment_len` of the side's
middle. It is 0 by default, so no side is rebuilt. Rebuilding at 0.4 µm (the default of
0.35) brings the angles of synthetic micrographs closer to the true ones, because a
rounded sharp corner then reads as one corner and not as two blunt ones. On real crops
the rebuilt corners can stick out past the region, and their angles put a kink near 50°
on the first mode.

The settings were compared on the real WC-Co crops at 256 and 512 px and on synthetic
micrographs with exact angles. On the 360 crops per class at 512 px (small, medium and
large grains):

| | 0.33–0.34 | 0.35 | 0.36 |
|---|---|---|---|
| polygons | 33k / 14k / 9k | 126k / 47k / 26k | 126k / 47k / 26k |
| angles | 194k / 85k / 62k | 751k / 279k / 165k | 805k / 299k / 176k |
| first mode $\mu_1$ | 77 / 82 / 80° | 90 / 89 / 83° | 100 / 99 / 93° |
| second mode $\mu_2$ | 256 / 242 / 245° | 241 / 223 / 228° | 239 / 224 / 227° |
| residual of the bimodal fit, all bins | 0.074 / 0.058 / 0.048 | 0.077 / 0.080 / 0.085 | 0.074 / 0.067 / 0.080 |
| density at 50° over 100° | | 0.76 / 0.83 / 0.98 | 0.53 / 0.56 / 0.71 |
| 256 against 512 px, W1 | 0.2–0.4° | 1.3–1.7° | 1.9–3.5° |
| synthetic, W1 to the true angles | 33.6° | 29.5° | 33.9° |

With 0.35 and 0.36, 0.2–1.1 % of the cobalt area is left without a polygon.

The fine polygons cost the bimodal model some of its fit. The valley around 180° is
empty and the second mode starts abruptly near 192°, where two Gaussians overlap; the
fitted widths and amplitudes are therefore less stable than the positions. Every
method measured underestimates the share of reflex vertices, because a pixel image
does not resolve the short notches of the boundary.

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
