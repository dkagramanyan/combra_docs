# Beams and the MVEE

The second descriptor combra computes from a set of contours is the *beam-length
distribution*: the sizes of the carbide grains, obtained by enclosing each grain
in its smallest ellipse.

## Why an enclosing ellipse

Grain size needs a definition that survives irregular, partially merged and
non-convex contours, which is what contour tracing on a real SEM image produces.
Fitting an ellipse by moments is sensitive to how the boundary was traced; a
bounding box is orientation-dependent. The {term}`MVEE` — the
**minimum-volume enclosing ellipse** — is the unique smallest-area ellipse
containing the contour, so it is defined for any point set, invariant to
rotation, and insensitive to boundary noise that does not change the extent.

Each grain therefore acquires three quantities: two semi-axis lengths $a$ and
$b$, and an orientation. In combra's vocabulary the grain approximated this way
is a {term}`beam`, $a$ and $b$ are its *beam lengths*, and the ellipse rotation
is its *beam orientation*.

```{warning}
The solver returns the semi-axes **ascending**, so $a \le b$: `a` is the
*minor* semi-axis and `b` the *major* one. This is the opposite of the usual
`(semi-major, semi-minor)` reading, and the `cv2.fitEllipse` fallback used for
contours the solver cannot handle orders them the other way round. Check which
you have before interpreting a beam length as a grain diameter.
```

## The algorithm

{py:func}`combra.ellipse.fit_mvee` solves the MVEE with Khachiyan's barycentric
coordinate-descent iteration [^khachiyan], with the implementation of
[radio-beam](https://radio-beam.readthedocs.io/en/latest/api/radio_beam.commonbeam.getMinVolEllipse.html)
0.3.9 vendored into combra, so radio-beam is not a dependency.
The `tol` argument is the convergence tolerance: lower values give tighter
ellipses and run slower. The default of `0.2` is loose enough to be fast on
thousands of contours per image and tight enough that the resulting distribution
is stable.

```pycon
>>> import cv2
>>> from combra import data, ellipse
>>> img = data.load_microstructure().images[0]
>>> _, processed = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
>>> res = ellipse.fit_mvee(processed, tol=0.2)
>>> len(res.a), res.a.mean()
```

The result is a named tuple `(a, b, angle_rad, centroid, contour)`; see
{py:class}`~combra.ellipse.MveeResult`.

## Physical units

Beam lengths are measured in pixels. To report them as lengths, supply the
physical pixel size: {py:meth}`combra.data.MicrostructureDataset.generate_beams`
takes a `pixel` argument, scales the beam lengths by it, and records it in the
row's `meta` as `pixel2meter`. Reported beam distributions from different
magnifications are comparable only once this scaling has been applied.

## The distribution and its fit

Pooled beam lengths are binned like any other combra distribution, then fitted on
a log scale with a straight line: the beam-length density of a WC-Co
microstructure is approximately exponential, so $\log(\mathrm{density})$ against
length is approximately linear and its slope is a single-number summary of grain
coarseness.

The `start` and `end` arguments of `generate_beams` trim that fit. Both extremes
of a binned beam distribution are poorly sampled — the smallest bins contain
tracing noise, the largest contain a handful of grains — and including them lets
a few counts set the slope. The defaults drop the first two and last three bins.

```pycon
>>> from combra import data
>>> ds = data.MicrostructureDataset(path=data.microstructure_data_dir(), max_per_class=50,
...                                 pixel_size=data.SEM_PIXEL_SIZE)
>>> ds.generate_beams(
...     save_path='./beams',
...     class_types={'Ultra_Co11': 'medium grain', 'Ultra_Co25': 'fine grain'},
...     step=4, pixel=data.SEM_PIXEL_SIZE,
...     run_meta={'family': 'real', 'resolution': 256},
... )
```

See {py:mod}`combra.ellipse` for the plotting functions and
{py:meth}`~combra.data.MicrostructureDataset.generate_beams` for the batch writer.

## Semi-axes as a metric

{py:func}`combra.ellipse.semiaxes` returns the big ($A$) and small ($B$) semi-axis of
every ellipse in an image. It takes the polygons of the angle pipeline
({py:func}`combra.angles.vertex_angles`: a 0.1 µm median, the boundary at the Otsu
level, simplified within 0.15 µm), leaves out those with a vertex on the image frame,
whose size the field of view limits, and finds the ellipse of least area around the
vertices of each. There is no edge detector. The semi-axes are then rounded to whole
pixels. This is not the pipeline of `generate_beams`, which fits the Canny contours of
the three-level map.

```{versionchanged} 0.39.0
The ellipses were fitted by {py:func}`~combra.ellipse.fit_mvee` to the contours of
the 0.4 µm cobalt mask, and regions on the frame were kept.
```

At the resolution of training images the regions are a few pixels wide, and the
histogram of a semi-axis has a peak at a few pixels, which can be 1 px for the small
semi-axis at 256 px; the exponential decay follows it.
{py:func}`~combra.metrics.fit_exponential_tail` therefore starts the line at
the mode rather than at a fixed bin, and fits it by maximum likelihood to the 1 px
histogram from there on. These are whole pixels, so the likelihood is that of a geometric
distribution, and $k = -\ln(1 + 1/m)$ with $m$ the mean of $x - x_0$. {py:func}`~combra.metrics.semiaxis_metrics` compares two such fits (see
{doc}`metrics`).

The semi-axes are lengths in pixels, so two sets compare only at the same physical
size of a pixel. A set of full frames resized to 256 px and a set of crops of
two thirds of the frame resized to 256 px show the same grain 1.5 times smaller in
the first: the fitted slopes then differ by about a third, with nothing wrong in
either set. Compare a generator with the images it was trained on, at their scale.

{py:func}`~combra.ellipse.plot_semiaxis_grid` draws the distributions the way
{py:func}`~combra.angles.plot_density_grid` draws the angles: a grid of cells (e.g.
resolution by grain class), each overlaying the sources as histogram points and
their fitted tails on a log density axis, with a legend in the upper right corner.
The trace key `scale` (the length of one pixel) puts the axis in physical units, and
`tag` writes a short text at the end of a group of lines, e.g. `A` and `B` when the
big and the small semi-axis of each source share a cell:

```python
from combra import data, ellipse

um_per_px = data.SEM_PIXEL_SIZE * 1024 / 256  # 1024 native px across a 256 px image
cell = [dict(values=values[source][axis], scale=um_per_px, label=source,
             color=color, marker=marker + ('' if axis == 'A' else '-open'),
             dash='solid' if axis == 'A' else 'dash', tag=axis)
        for axis in ('A', 'B')
        for source, color, marker in (('real', 'blue', 'circle'),
                                      ('SAN', 'orange', 'square'))]
fig = ellipse.plot_semiaxis_grid([[cell]], ['256×256'], ['small grains'],
                                 x_title='semi-axis length, µm', start=3, min_count=10)
```

[^khachiyan]: L. G. Khachiyan, *Rounding of polytopes in the real number model of
    computation*, Mathematics of Operations Research 21(2), 1996, 307–320.
