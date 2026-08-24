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
absence is diagnostic — see {ref}`undefined-rather-than-wrong`.

## From contour to angle

{py:func}`combra.angles.vertex_angles` performs the measurement on one
preprocessed binary image:

1. Extract closed contours.
2. Simplify each with Douglas–Peucker at tolerance `tol`.
3. Iteratively remove vertices whose neighbouring segments are shorter than
   `min_segment_len`.
4. Emit the signed angle at each surviving vertex, traversing counter-clockwise,
   in degrees on $[0, 360)$.

Contours whose bounding box lies within `border_eps` pixels of the image edge are
dropped: a grain clipped by the frame has vertices that are artefacts of the crop.

```pycon
>>> import cv2
>>> from combra import data, angles
>>> img = data.load_microstructure().images[0]
>>> _, processed = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
>>> arr, contours = angles.vertex_angles(processed, border_eps=5, tol=3, min_segment_len=10.0)
>>> arr.min(), arr.max()
```

### Choosing `min_segment_len`

This is the parameter that matters. Contour tracing on a real SEM image produces
many one- and two-pixel segments that are digitization noise; each contributes a
near-arbitrary vertex angle, and together they smear the distribution. Pruning
short segments removes them, at the cost of also removing genuine fine detail.

Values of 5–20 px are the usable range. Higher values give smoother densities
from fewer angles. Because the choice changes the measured distribution, it is
**part of a result's identity**: {py:func}`combra.angles.output_directory` encodes
it in the output folder name (`..._msl5`) so runs made at different settings
cannot be silently compared.

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

Like `min_segment_len`, {term}`step` is part of a metric's identity: two runs are
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
