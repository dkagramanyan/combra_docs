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
what the bimodal-Gaussian fit in {doc}`../api/fitting` is for, and its presence or
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
image, in five stages (the method called P6 in the extraction report):

1. **Detect the pools.** A 3×3 median filter, then the union of Otsu's
   threshold and a Gaussian adaptive threshold; components under 10 px are
   removed and the mask is dilated by one pixel
   ({py:func}`~combra.angles.pool_mask`).
2. **Locate the boundary.** Every pixel contour of the mask, holes included,
   is moved along its normal to the 0.5 level of the blurred mask (σ 0.7 px),
   which places the boundary to sub-pixel precision.
3. **Choose the vertices** with Douglas–Peucker at tolerance `tol`, 1.75 px
   by default. Regions with fewer than four vertices or within `border_eps`
   of the frame are dropped: a pool clipped by the frame has vertices that are
   artefacts of the crop.
4. **Read the angles.** A line is fitted by total least squares to the
   boundary points of every edge, half a pixel away from both vertices where
   the corner rounds the boundary; the angle at a vertex is the angle between
   its two lines, reflex above 180°, and the vertex moves to their
   intersection.
5. **Store the polygon** inset by `1 + 10/d` px (`d` its equivalent
   diameter), which undoes the dilation and the mask's outward offset. The
   angles do not depend on the inset.

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
set of {doc}`combra.synth </api/synth>`, where the truth is exact: at 1.75 px
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
{doc}`../api/angles` for the plotting helpers.
