# combra.image

The `combra.image` module bundles every pixel-level helper used elsewhere in combra: file format conversion, geometric helpers, fractal dimension, and a few low-level numba kernels.

```python
from combra import image
```

The standard preprocessing pipeline produces an image with three pixel value classes:

$$
\text{preproc} = 1 - \mathrm{Otsu}(\mathrm{median}(\text{image})) + \mathrm{grad}(\mathrm{Otsu}(\mathrm{median}(\text{image})))
$$

| value | meaning |
| --- | --- |
| `0` | WC grain |
| `127` | Co region |
| `254` | boundary of Co region adjacent to a WC grain (1 px thick) |

## Preprocessing

````{py:function} combra.image.render_filled_contours(orig_img_padded, tol, labeled_cnts=False, labels=False) -> tuple[ndarray, list[ndarray]]

Run contour extraction with Douglas–Peucker tolerance `tol` on a padded binary image. Returns `(visualisation, contours)`. Use `labeled_cnts=True` (with `labels`) when working with hand-annotated contours and want to skip binarisation.

:param orig_img_padded: Padded binary input image.
:type orig_img_padded: ndarray
:param tol: Douglas–Peucker simplification tolerance.
:type tol: float
:param labeled_cnts: When `True`, use the supplied `labels` instead of running binarisation. Default: `False`.
:type labeled_cnts: bool, optional
:param labels: Pre-existing contour labels (only used when `labeled_cnts=True`). Default: `False`.
:type labels: ndarray or bool, optional
:returns: **visualisation** (*ndarray*) – Drawn-on copy of the input; and **contours** (*list[ndarray]*) – Extracted (simplified) contours.
:rtype: tuple(ndarray, list[ndarray])

**Example**

```pycon
>>> import cv2
>>> import numpy as np
>>> from combra import image, data
>>> img = data.load_microstructure().images[0]
>>> _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
>>> padded = np.pad(binary, 30)
>>> vis, cnts = image.render_filled_contours(padded, tol=3)
>>> print(f'{len(cnts)} contours')
```
````

````{py:function} combra.image.fill_polygon(grid, corners, fill_value=1) -> ndarray

Rasterize a polygon defined by `corners` into `grid` using a numba point-in-polygon test.

:param grid: Output grid; mutated in place.
:type grid: ndarray
:param corners: Polygon vertices.
:type corners: ndarray[N, 2]
:param fill_value: Value written to grid cells inside the polygon. Default: `1`.
:type fill_value: scalar, optional
:returns: **grid** (*ndarray*) – The mutated grid (same array passed in).
:rtype: ndarray

**Example**

```pycon
>>> import numpy as np
>>> from combra import image
>>> grid = np.zeros((100, 100), dtype=np.uint8)
>>> corners = np.array([[20, 20], [80, 20], [80, 80], [20, 80]])  # square
>>> image.fill_polygon(grid, corners, fill_value=255)
>>> print(grid.sum())   # ≈ 60*60*255 (interior pixels)
```
````

````{py:function} combra.image.resize_folder(input_root, output_root, target_size) -> None

Recursively walk an image tree, resize_folder each image to `target_size`, and convert to RGB if needed. Mirrors the source tree structure under `output_root`.

:param input_root: Source root.
:type input_root: str or Path
:param output_root: Destination root.
:type output_root: str or Path
:param target_size: `(width, height)` in pixels.
:type target_size: tuple[int, int]
:returns: Nothing. Writes resized images under `output_root`.
:rtype: None

**Example**

```pycon
>>> from combra import image
>>> # Downsample a folder-of-classes from 1024x1024 to 256x256, preserving subdir layout.
>>> image.resize('./data/orig_1024', './data/orig_256', target_size=(256, 256))
```
````

````{py:function} combra.image.tile_images(input_folder, output_folder, split=3, rotate=False) -> None

```{warning}
Legacy method — no working guarantee (emits a `DeprecationWarning`).
```

Walk a folder-of-classes tree and tile every image into quarters (`split=3`) or ninths (`split=9`), writing the tiles to `output_folder` with a `_part_N` suffix while preserving the per-class subdirectory layout.

:param input_folder: Source root (one subfolder per class).
:type input_folder: str or Path
:param output_folder: Destination root; created if missing.
:type output_folder: str or Path
:param split: `3` → 2×2 tiles, `9` → 3×3 tiles. Default: `3`.
:type split: int, optional
:param rotate: Reserved flag for rotation augmentation. Default: `False`.
:type rotate: bool, optional
:returns: Nothing. Writes tiled images under `output_folder`.
:rtype: None

**Example**

```pycon
>>> from combra import image
>>> image.tile_images('./data/orig', './data/orig_tiles', split=3)
```
````

````{py:function} combra.image.augment_quadrants(image, size=1024) -> Iterator[tuple[str, PIL.Image.Image]]

Generate the deduplicated augmentations of a single image. The image is scaled to a `1.5 * size` square and cut into the four overlapping `size × size` quadrant crops (a 2×2 window slid over a 3×3 grid); each crop is expanded into its 8 dihedral orientations (rotations of 0/90/180/270° × {plain, mirrored}). Rotations are lossless `transpose` operations (no interpolation). Crops identical (pixel-for-pixel) to one already yielded for the same source image are skipped, so a plain image yields up to 32 crops.

:param image: Source image; converted to RGB internally.
:type image: PIL.Image.Image
:param size: Side length of each output crop in pixels. Default: `1024`.
:type size: int, optional
:returns: Iterator of **(suffix, crop)** pairs — **suffix** (*str*) a filename tag such as `"combo_2_rot90_mirror"`, and **crop** (*PIL.Image.Image*) the transformed `size × size` RGB crop.
:rtype: Iterator[tuple[str, PIL.Image.Image]]

**Example**

```pycon
>>> from PIL import Image
>>> from combra import image
>>> src = Image.open('./data/orig/Ultra_Co11/img001.jpeg')
>>> for suffix, crop in image.augment_quadrants(src, size=1024):
...     crop.save(f'img001_{suffix}.jpeg', 'JPEG', quality=95)
```
````

````{py:function} combra.image.build_quadrant_dataset(input_folder, output_folder, class_map, size=1024, quality=95) -> str

Augment a folder-of-classes tree and write a StyleGAN-style `dataset.json`. For every image in each `class_map` subfolder of `input_folder`, the deduplicated crops from `augment_quadrants` are written to the mirrored subfolder under `output_folder` and recorded as `[relative_path, class_index]` label pairs. Only the subfolders listed in `class_map` are processed.

:param input_folder: Root folder with one subfolder per class.
:type input_folder: str or Path
:param output_folder: Destination root; class subfolders and `dataset.json` are created here.
:type output_folder: str or Path
:param class_map: Mapping from class-subfolder name to integer class label.
:type class_map: dict[str, int]
:param size: Side length of each output crop in pixels. Default: `1024`.
:type size: int, optional
:param quality: JPEG quality for the saved crops. Default: `95`.
:type quality: int, optional
:returns: **json_path** (*str*) – Path to the written `dataset.json` (`{"labels": [[relative_path, class_index], ...]}`).
:rtype: str

**Example**

```pycon
>>> from combra import image
>>> class_map = {'Ultra_Co25': 0, 'Ultra_Co11': 1, 'Ultra_Co6_2': 2}
>>> json_path = image.build_quadrant_dataset(
...     './data/orig', './data/imagenet_9to4_1024x1024', class_map,
... )
>>> print(json_path)   # ./data/imagenet_9to4_1024x1024/dataset.json
```
````

## Fractal dimension

````{py:function} combra.image.image_fractal_dimension(binary, sizes, max_shift=0) -> float

Box-counting fractal dimension of a binary image.

:param binary: Binary image (any non-zero pixel counts as "filled").
:type binary: ndarray[uint8]
:param sizes: Box sizes to sweep, in pixels — dyadic sizes such as `2 ** np.arange(1, 8)`, kept below half the smaller image dimension.
:type sizes: ndarray[int]
:param max_shift: If `>0`, average box counts over `max_shift` grid offsets to reduce alignment bias. Default: `0`.
:type max_shift: int, optional
:returns: **fd** (*float*) – Fractal dimension estimate.
:rtype: float

**Example**

```pycon
>>> import cv2
>>> import numpy as np
>>> from combra import image, data
>>> img = data.load_microstructure().images[0]
>>> _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
>>> sizes = 2 ** np.arange(1, 8)      # [2, 4, ..., 128]
>>> fd = image.image_fractal_dimension(binary, sizes, max_shift=0)
>>> print(f'fractal dimension = {fd:.3f}')
```
````

````{py:function} combra.image.contour_fractal_dimension(contour, max_size_thr) -> float

Fractal dimension of a single contour.

:param contour: Contour vertices.
:type contour: ndarray[N, 2]
:param max_size_thr: Maximum box size considered.
:type max_size_thr: int
:returns: **fd** (*float*) – Fractal dimension, or `np.nan` for contours too short to span `max_size_thr` boxes.
:rtype: float

**Example**

```pycon
>>> import cv2
>>> from combra import image, contours, data
>>> img = data.load_microstructure().images[0]
>>> _, processed = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
>>> cnts = contours.find_contours(processed, tol=3)
>>> fd = image.contour_fractal_dimension(cnts[0], max_size_thr=64)
>>> print(f'contour fd = {fd:.3f}')
```
````

## Geometry & line kernels

These functions are numba-accelerated and (where possible) zero-allocating — intended for hot-loop use inside the graph builder and angle extractor.

````{py:function} combra.image.bresenham_line(x0, y0, x1, y1) -> tuple[ndarray, ndarray]

Bresenham line rasterisation.

:param x0: Start x-coordinate.
:type x0: int
:param y0: Start y-coordinate.
:type y0: int
:param x1: End x-coordinate.
:type x1: int
:param y1: End y-coordinate.
:type y1: int
:returns: **xs** (*ndarray[int]*) – Pixel x-coordinates along the line; and **ys** (*ndarray[int]*) – Pixel y-coordinates along the line.
:rtype: tuple(ndarray, ndarray)

**Example**

```pycon
>>> from combra import image
>>> xs, ys = image.bresenham_line(0, 0, 10, 5)
>>> print(list(zip(xs, ys)))   # all pixel coordinates on the line
```
````

````{py:function} combra.image.count_border_pixels_on_line(img_contours_np, start_node_x, start_node_y, end_node_x, end_node_y, border_pixel=255) -> int

Count contour pixels (value `== border_pixel`) that fall on the Bresenham line between two points. Used in the crack-graph builder to score the "thickness" of an edge.

:param img_contours_np: Image of drawn contours.
:type img_contours_np: ndarray
:param start_node_x: Start x-coordinate.
:type start_node_x: int
:param start_node_y: Start y-coordinate.
:type start_node_y: int
:param end_node_x: End x-coordinate.
:type end_node_x: int
:param end_node_y: End y-coordinate.
:type end_node_y: int
:param border_pixel: Pixel value that counts as a contour hit. Default: `255`.
:type border_pixel: int, optional
:returns: **count** (*int*) – Pixel count.
:rtype: int

**Example**

```pycon
>>> from combra import image
>>> # img_contours: binary contour mask with contour pixels == 255
>>> n = image.count_border_pixels_on_line(
...     img_contours, start_node_x=10, start_node_y=20, end_node_x=80, end_node_y=60,
...     border_pixel=255,
... )
>>> print(f'{n} contour pixels lie on the line')
```
````

````{py:function} combra.image.count_border_pixels_in_band(img_contours_np, start_x, start_y, end_x, end_y, perp_v_x, perp_v_y, line_eps, border_pixel, border_eps) -> int

Count contour pixels intersected by a band of width `2*line_eps` perpendicular to a line. Pair with `perpendicular_vector`.

:param img_contours_np: Image of drawn contours.
:type img_contours_np: ndarray
:param start_x: Start x-coordinate.
:type start_x: int
:param start_y: Start y-coordinate.
:type start_y: int
:param end_x: End x-coordinate.
:type end_x: int
:param end_y: End y-coordinate.
:type end_y: int
:param perp_v_x: Perpendicular vector x-component (from `perpendicular_vector`).
:type perp_v_x: float
:param perp_v_y: Perpendicular vector y-component (from `perpendicular_vector`).
:type perp_v_y: float
:param line_eps: Half-width of the perpendicular band.
:type line_eps: int
:param border_pixel: Contour-pixel value.
:type border_pixel: int
:param border_eps: Margin from image edge that excludes detections.
:type border_eps: int
:returns: **count** (*int*) – Pixel count.
:rtype: int

**Example**

```pycon
>>> from combra import image
>>> perp_x, perp_y = image.perpendicular_vector(10, 20, 80, 60, line_eps=10)
>>> n = image.count_border_pixels_in_band(
...     img_contours, 10, 20, 80, 60, perp_x, perp_y,
...     line_eps=10, border_pixel=255, border_eps=2,
... )
>>> print(n)
```
````

````{py:function} combra.image.perpendicular_vector(start_x, start_y, end_x, end_y, line_eps=10) -> tuple[float, float]

Unit perpendicular vector to the line `(start → end)`, scaled by `line_eps`. Use with `count_border_pixels_in_band` to define the perpendicular band.

:param start_x: Start x-coordinate.
:type start_x: int
:param start_y: Start y-coordinate.
:type start_y: int
:param end_x: End x-coordinate.
:type end_x: int
:param end_y: End y-coordinate.
:type end_y: int
:param line_eps: Scale of the resulting vector. Default: `10`.
:type line_eps: int, optional
:returns: **perp_v_x** (*float*) – X-component of the scaled perpendicular vector; and **perp_v_y** (*float*) – Y-component of the scaled perpendicular vector.
:rtype: tuple(float, float)

**Example**

```pycon
>>> from combra import image
>>> # Perpendicular to a horizontal line; line_eps=10 ⇒ vector points up by 10.
>>> px, py = image.perpendicular_vector(0, 0, 100, 0, line_eps=10)
>>> print(px, py)   # ≈ (0, 10) or (0, -10)
```
````

````{py:function} combra.image.segments_intersect(p1, p2, p3, p4) -> bool

Test if two line segments intersect.

:param p1: First endpoint of the first segment.
:type p1: tuple[float, float]
:param p2: Second endpoint of the first segment.
:type p2: tuple[float, float]
:param p3: First endpoint of the second segment.
:type p3: tuple[float, float]
:param p4: Second endpoint of the second segment.
:type p4: tuple[float, float]
:returns: **intersect** (*bool*) – `True` if segments `(p1, p2)` and `(p3, p4)` intersect.
:rtype: bool

**Example**

```pycon
>>> from combra import image
>>> # Crossing 'X' shape — segments (0,0)→(10,10) and (0,10)→(10,0) cross at (5,5).
>>> print(image.segments_intersect((0, 0), (10, 10), (0, 10), (10, 0)))   # True
>>> print(image.segments_intersect((0, 0), (1, 1), (5, 5), (6, 6)))       # False
```
````

````{py:function} combra.image.is_point_in_polygon(x, y, corners) -> bool

Numba point-in-polygon test.

:param x: Query point x-coordinate.
:type x: float
:param y: Query point y-coordinate.
:type y: float
:param corners: Polygon vertices.
:type corners: ndarray[N, 2]
:returns: **inside** (*bool*) – Whether the point is inside the polygon.
:rtype: bool

**Example**

```pycon
>>> import numpy as np
>>> from combra import image
>>> square = np.array([[0, 0], [10, 0], [10, 10], [0, 10]])
>>> print(image.is_point_in_polygon(5, 5, square))    # True
>>> print(image.is_point_in_polygon(15, 5, square))   # False
```
````

## Notes

:::{note}
`tile_images` is in `__all__` but relies on hardcoded paths. Treat it as legacy.
:::

## Array conversion

````{py:function} combra.image.to_uint8(a, data_range=None) -> ndarray

Rescale an image array to `uint8 [0, 255]` under an **explicit** range contract —
the strict, caller-facing counterpart of combra's internal per-image guessing, so
two images in one scored batch can never be rescaled under different assumptions
(the normalization hazard behind content-dependent FID/CMMD bias).

:param a: Image array.
:type a: array_like
:param data_range: `None` — `a` must already be `uint8`, else `ValueError`; `(lo, hi)` — linearly map `[lo, hi]` onto `[0, 255]`. Default: `None`.
:type data_range: None or tuple[float, float] or str, optional
:returns: **out** (*ndarray[uint8]*) – The rescaled image.
:rtype: ndarray

**Example**

```pycon
>>> import numpy as np
>>> from combra.image import to_uint8
>>> to_uint8(np.array([-1.0, 0.0, 1.0]), data_range=(-1.0, 1.0))
array([  0, 127, 255], dtype=uint8)
```
````

## Ellipse geometry

````{py:function} combra.image.ellipse(a, b, angle, xc=0, yc=0, num=50) -> tuple[ndarray, ndarray]

Sample `num` points on the ellipse with semi-axes `(a, b)`, rotation `angle` (radians, decreasing → clockwise), and centre `(xc, yc)`. Handy for overlaying MVEE results.

:param a: Semi-major axis.
:type a: float
:param b: Semi-minor axis.
:type b: float
:param angle: Rotation in radians.
:type angle: float
:param xc: Centre x-coordinate. Default: `0`.
:type xc: float, optional
:param yc: Centre y-coordinate. Default: `0`.
:type yc: float, optional
:param num: Number of sample points. Default: `50`.
:type num: int, optional
:returns: **x** (*ndarray*) – Length-`num` 1-D array of the `x` coordinates along the ellipse; and **y** (*ndarray*) – Length-`num` 1-D array of the `y` coordinates along the ellipse.
:rtype: tuple(ndarray, ndarray)

**Example**

```pycon
>>> import matplotlib.pyplot as plt
>>> from combra import image
>>> x, y = image.ellipse(a=20, b=8, angle=0.4, xc=0, yc=0, num=200)
>>> plt.plot(x, y)
>>> plt.gca().set_aspect('equal'); plt.show()
```
````

## See also

- {doc}`combra.contours <contours>` — polygon extraction from a binarised image.
- {doc}`combra.graph <graph>` — heavy user of the geometry kernels here.
