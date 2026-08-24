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
coordinate-descent iteration [^khachiyan], following the implementation in
[radio-beam](https://radio-beam.readthedocs.io/en/latest/api/radio_beam.commonbeam.getMinVolEllipse.html).
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
>>> ds = data.MicrostructureDataset(path=data.microstructure_data_dir(), max_per_class=50)
>>> ds.generate_beams(
...     save_path='./beams',
...     class_types={'Ultra_Co11': 'medium grain', 'Ultra_Co25': 'fine grain'},
...     step=4, pixel=50 / 1000,
...     run_meta={'family': 'real', 'resolution': 256},
... )
```

See {doc}`../api/ellipse` for the plotting helpers and
{doc}`../api/data` for the batch writer.

[^khachiyan]: L. G. Khachiyan, *Rounding of polytopes in the real number model of
    computation*, Mathematics of Operations Research 21(2), 1996, 307–320.
