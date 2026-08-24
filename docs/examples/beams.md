# Beam lengths from enclosing ellipses

Measure grain size by fitting each contour's {term}`MVEE`, then write the
per-class beam-length distributions to parquet.

For what a beam is and why an enclosing ellipse defines it, see
{doc}`/user_guide/beams`.

## One image

{py:func}`combra.ellipse.fit_mvee` fits every contour in a preprocessed image and
returns the semi-axes, orientations, centroids and source contours together:

```{doctest}
>>> import cv2
>>> import numpy as np
>>> from combra import data, ellipse
>>> img = data.load_microstructure().images[0]
>>> _, processed = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
>>> result = ellipse.fit_mvee(processed, tol=0.2)
>>> len(result.a)
392
>>> result.angle_rad.shape
(392,)
```

The solver returns the semi-axes **ascending**, so `a` is the minor one:

```{doctest}
>>> bool(np.all(result.a <= result.b))
True
>>> round(float(np.median(result.b)), 2)
3.0
```

```{warning}
This ordering is the opposite of the usual `(semi-major, semi-minor)` reading,
and the `cv2.fitEllipse` fallback used for contours the solver cannot handle
orders them the other way round. Check which you have before treating a beam
length as a grain diameter.
```

## A dataset

{py:meth}`~combra.data.MicrostructureDataset.generate_beams` runs the fit over
every class, converts the beam lengths to physical units, fits a straight line to
each log-density, and writes one parquet:

```{doctest}
>>> ds = data.MicrostructureDataset(
...     path=data.microstructure_data_dir(),
...     max_per_class=2,
... )
>>> out_path = ds.generate_beams(
...     save_path='./beams',
...     class_types={
...         'Ultra_Co11':  'medium grains',
...         'Ultra_Co25':  'fine grains',
...         'Ultra_Co8':   'medium-fine grains',
...         'Ultra_Co6_2': 'coarse grains',
...         'Ultra_Co15':  'medium-fine grains',
...     },
...     step=4,            # bin width for the beam-length histogram
...     pixel=50 / 1000,   # physical size of one pixel
... )
>>> out_path.name
'beams_n2.parquet'
```

`pixel` scales the beam lengths out of pixel units and is recorded on the row, so
runs taken at different magnifications stay comparable:

```{doctest}
>>> from combra import io
>>> rows = io.load_rows(out_path)
>>> len(rows)
5
>>> rows[0]['meta']['pixel2meter']
0.05
```

## Reading the fit

The beam-length density is approximately exponential, so each row carries the
slope of a straight line fitted to its log-density. A steeper (more negative)
slope means the distribution falls off faster — a finer-grained alloy:

```{doctest}
>>> round(float(rows[0]['prep']['a_k']), 4)
-1.6822
```

The `start` and `end` arguments of `generate_beams` trim that fit, because both
extremes of a binned beam distribution are poorly sampled: the smallest bins hold
tracing noise and the largest hold a handful of grains. The defaults drop the
first two and last three bins.

See {doc}`/api/ellipse` for the plotting helpers and
{doc}`/api/data` for the batch writer.
