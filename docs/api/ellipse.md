# combra.ellipse

The `combra.ellipse` module fits the **Minimum Volume Enclosing Ellipse** to each polygon in an image and provides plotting / comparison helpers. The algorithm comes from [L.N. Khachiyan](https://en.wikipedia.org/wiki/Ellipsoid_method) (implementation borrowed from [radio-beam](https://radio-beam.readthedocs.io/en/latest/api/radio_beam.commonbeam.getMinVolEllipse.html)).

![Enclosed Ellipse](https://pobedit.s3.us-east-2.amazonaws.com/docs_images/enclosed-ellipse.png)

```python
from combra import ellipse
```

## Build

````{py:function} combra.ellipse.fit_mvee(image, tol=0.2) -> MveeResult

Fit MVEE to every contour in a preprocessed image. This is the per-image primitive that {py:meth}`combra.data.MicrostructureDataset.generate_beams` calls in parallel.

:param image: Preprocessed image.
:type image: ndarray
:param tol: Convergence tolerance. Lower → tighter ellipses, slower. Default: `0.2`.
:type tol: float, optional
:returns: **result** – an {py:class}`~combra.ellipse.MveeResult` ``(a, b, angle_rad, centroid, contour)``: per-contour semi-major axes, semi-minor axes, rotation angles (radians), centre coordinates, and the source contours in fit order.
:rtype: MveeResult

**Example**

```pycon
>>> import cv2
>>> from combra import ellipse, data
>>> img = data.load_microstructure().images[0]
>>> _, processed = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
>>> res = ellipse.fit_mvee(processed, tol=0.2)
>>> print(f'{len(res.a)} polygons   median a/b = {res.a.sum()/res.b.sum():.2f}')
```
````

````{py:class} combra.ellipse.MveeResult(a, b, angle_rad, centroid, contour)

SciPy-style named tuple returned by {py:func}`~combra.ellipse.fit_mvee` (cf.
``scipy.stats.linregress``). Unpacking-compatible with the historical 5-tuple.

:param a: Per-contour semi-major axis lengths (pixels).
:type a: ndarray
:param b: Per-contour semi-minor axis lengths (pixels).
:type b: ndarray
:param angle_rad: Per-contour ellipse orientation in radians.
:type angle_rad: ndarray
:param centroid: Per-contour ``(x, y)`` centre coordinates.
:type centroid: ndarray
:param contour: The accepted ``(N, 2)`` contours the ellipses were fit to.
:type contour: list[ndarray]
````

## Plotting

````{py:function} combra.ellipse.plot_beam_lengths(rows, step, width, height, indices=None, scatter_size=60, font_size=20, save_path=None, show=True) -> None

Plot the `a_beams` and `b_beams` distributions for each class in an $N \times M$ grid.

:param rows: Rows from a beams parquet (e.g. via `pq.read_table().to_pylist()`).
:type rows: list[dict]
:param save_name: Title and filename.
:type save_name: str
:param step: Filter to this histogram step.
:type step: float
:param N: Grid rows.
:type N: int
:param M: Grid columns.
:type M: int
:param indices: Class indices to draw. Default: `None`.
:type indices: list[int] or None, optional
:param save: Write to `<save_name>.png`. Default: `False`.
:type save: bool, optional
:param scatter_size: Marker size. Default: `60`.
:type scatter_size: int, optional
:param font_size: Plot font size. Default: `20`.
:type font_size: int, optional
:returns: Nothing. Renders the grid and, when `save=True`, writes `<save_name>.png`.
:rtype: None

**Example**

```pycon
>>> import pyarrow.parquet as pq
>>> from combra import data, mvee
>>> ds = data.MicrostructureDataset(path=data.microstructure_data_dir())
>>> ds.generate_beams(
...     save_path='./beams',
...     class_types={'Ultra_Co11': 'medium grain'},
...     step=4, pixel=50/1000,
... )
>>> rows = pq.read_table('./beams/beams_n100.parquet').to_pylist()
>>> ellipse.plot_beam_lengths(rows, save_name='beams.png', step=4, N=2, M=1, save=False)
```
````

````{py:function} combra.ellipse.plot_beam_orientations(data, step, width, height, indices=None, save_path=None, show=True) -> None

Plot the ellipse rotation-angle distributions across classes.

:param data: Rows from a beams parquet.
:type data: list[dict]
:param saved_image_name: Output filename.
:type saved_image_name: str
:param step: Histogram step to filter on.
:type step: float
:param N: Grid rows.
:type N: int
:param M: Grid columns.
:type M: int
:param indices: Class indices to draw. Default: `None`.
:type indices: list[int] or None, optional
:param save: Write the figure. Default: `False`.
:type save: bool, optional
:returns: Nothing. Renders the figure and, when `save=True`, writes it to disk.
:rtype: None

**Example**

```pycon
>>> import pyarrow.parquet as pq
>>> from combra import ellipse
>>> rows = pq.read_table('./beams/beams_n100.parquet').to_pylist()
>>> ellipse.plot_angles(rows, saved_image_name='angles.png',
...                  step=4, N=2, M=2, save=False)
```
````

````{py:function} combra.ellipse.plot_beam_compare(data_1, data_2, beam_types, width, height, indices_1, indices_2, title='', scatter_size=60, font_size=20, save_path=None, show=True) -> list[str]

Side-by-side comparison of two parquet datasets at the same step.

:param data_1: Rows from the first beams parquet.
:type data_1: list[dict]
:param data_2: Rows from the second beams parquet.
:type data_2: list[dict]
:param save_name: Output filename.
:type save_name: str
:param beam_types: Which fields to compare — e.g. `['a_beams', 'b_beams']`.
:type beam_types: list[str]
:param N: Grid rows.
:type N: int
:param M: Grid columns.
:type M: int
:param indices_1: Class indices from the first set to align.
:type indices_1: list[int]
:param indices_2: Class indices from the second set to align.
:type indices_2: list[int]
:param save: Write the figure. Default: `False`.
:type save: bool, optional
:param scatter_size: Marker size. Default: `60`.
:type scatter_size: int, optional
:param font_size: Plot font size. Default: `20`.
:type font_size: int, optional
:returns: **fit_metrics** (*list[str]*) – One formatted `"<Δk%> <Δb%>"` string per aligned class pair — the relative differences of the linear-fit slope `k` and intercept `b` between the two datasets, in percent.
:rtype: list[str]

**Example**

```pycon
>>> import pyarrow.parquet as pq
>>> from combra import ellipse
>>> rows_real = pq.read_table('./beams/real_n360.parquet').to_pylist()
>>> rows_gen  = pq.read_table('./beams/gen_n10000.parquet').to_pylist()
>>> metrics = ellipse.plot_beam_compare(
...     rows_real, rows_gen, save_name='compare.png',
...     beam_types=['a_beams', 'b_beams'], N=2, M=2,
...     indices_1=[0, 1], indices_2=[0, 1],
... )
```
````

````{py:function} combra.ellipse.plot_beam_heatmap(data, step, indices=None, bin_max=30, width=7, height=7, font_size=20, scatter_size=60, save_path=None, show=True) -> None

2-D heatmap of `(a_beam, b_beam)` pairs per class.

:param data: Rows from a beams parquet.
:type data: list[dict]
:param step: Histogram step to filter on.
:type step: float
:param saved_names: Per-class display names (overrides `meta.name`).
:type saved_names: list[str]
:param indices: Class indices to draw. Default: `None`.
:type indices: list[int] or None, optional
:param bin_max: Upper bound on histogram axes. Default: `30`.
:type bin_max: float, optional
:param N: Heatmap bin count along rows. Default: `7`.
:type N: int, optional
:param M: Heatmap bin count along columns. Default: `7`.
:type M: int, optional
:param font_size: Plot font size. Default: `20`.
:type font_size: int, optional
:param save: Write the figure. Default: `False`.
:type save: bool, optional
:param scatter_size: Marker size. Default: `60`.
:type scatter_size: int, optional
:returns: Nothing. Renders the heatmaps and, when `save=True`, writes them to disk.
:rtype: None

**Example**

```pycon
>>> import pyarrow.parquet as pq
>>> from combra import ellipse
>>> rows = pq.read_table('./beams/beams_n100.parquet').to_pylist()
>>> ellipse.plot_beam_heatmap(rows, step=4, saved_names=['small', 'medium', 'large'],
...                    indices=[0, 1, 2], bin_max=30, N=7, M=7)
```
````

````{py:function} combra.ellipse.plot_enclosing_ellipse(image, pos=0, tolerance=0.2, size=15, save_path=None, show=True) -> None

Plot a single polygon (index `pos`) and the ellipse fitted around it. Useful for sanity-checking `tolerance`.

:param image: Source image (raw or preprocessed).
:type image: ndarray
:param pos: Index of the contour to inspect. Default: `0`.
:type pos: int, optional
:param tolerance: MVEE tolerance. Default: `0.2`.
:type tolerance: float, optional
:param N: Number of points sampled on the rendered ellipse. Default: `15`.
:type N: int, optional
:returns: Nothing. Renders the polygon and its fitted ellipse.
:rtype: None

**Example**

```pycon
>>> from combra import ellipse, data
>>> img = data.load_microstructure().images[0]
>>> ellipse.plot_enclosing_ellipse(img, pos=0, tolerance=0.2)
```
````

## Result types

````{py:class} combra.ellipse.BeamComparison(figures, metrics)

Result of {py:func}`~combra.ellipse.plot_beam_compare`.

:param figures: One figure per entry of `beam_types`, in the order given.
:type figures: list[matplotlib.figure.Figure]
:param metrics: Per-pair relative-error strings for the linear `k` and `b` coefficients.
:type metrics: list[str]
````

## See also

- {py:meth}`combra.data.MicrostructureDataset.generate_beams` — drives `fit_mvee` across whole class folders and writes parquet.
