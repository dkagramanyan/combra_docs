# combra.contours

The `combra.contours` module extracts polygon contours from preprocessed binary images and renders them back onto images for visualisation. Used internally by {py:func}`combra.angles.vertex_angles`, {py:func}`combra.mvee.fit_mvee`, and the crack-graph builder.

```python
from combra import contours
```

## Extraction

````{py:function} combra.contours.get_row_contours(image) -> list[ndarray]

Extract raw contours via Canny edges + Suzuki contour finding. No simplification.

:param image: Preprocessed binary image.
:type image: ndarray
:returns: **contours** (*list[ndarray]*) – One `(N_points, 2)` array per region, every boundary pixel.
:rtype: list[ndarray]

**Example**

```python
>>> import cv2
>>> from combra import contours, data
>>> _, img = data.microstructure_images()[0]
>>> _, processed = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
>>> raw = contours.get_row_contours(processed)
>>> print(f'{len(raw)} contours; first has {len(raw[0])} vertices')
```
````

````{py:function} combra.contours.find_contours(image, tol=3) -> list[ndarray]

Same as `get_row_contours` but applies Douglas–Peucker simplification with tolerance `tol` to every contour. This is what most downstream code calls.

:param image: Preprocessed binary image.
:type image: ndarray
:param tol: Simplification tolerance in pixels — higher → fewer vertices. Default: `3`.
:type tol: float, optional
:returns: **contours** (*list[ndarray]*) – Simplified contours.
:rtype: list[ndarray]

**Example**

```python
>>> import cv2
>>> from combra import contours, data
>>> _, img = data.microstructure_images()[0]
>>> _, processed = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
>>> raw = contours.get_row_contours(processed)             # ~thousands of vertices per region
>>> simplified = contours.find_contours(processed, tol=3)  # ~tens of vertices per region
>>> print(f'raw[0]: {len(raw[0])} pts   simplified[0]: {len(simplified[0])} pts')
```
````

````{py:function} combra.contours.skeletons_coords(image) -> list[ndarray]

Morphological skeletonisation + per-component split via `scipy.ndimage.label`. One coordinate array per skeleton component.

:param image: Binary image.
:type image: ndarray
:returns: **coords** (*list[ndarray]*) – `(N_pixels, 2)` int arrays, one per connected component.
:rtype: list[ndarray]

**Example**

```python
>>> import cv2
>>> from combra import contours, data
>>> _, img = data.microstructure_images()[0]
>>> _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
>>> skels = contours.skeletons_coords(binary)
>>> print(f'{len(skels)} skeleton components')
```
````

````{py:function} combra.contours.contour_to_binary_mask(contour, eps=1, thickness=1, pad=2) -> ndarray

Render a single contour into a small binary mask.

:param contour: Polygon vertices in raw OpenCV layout (the shape returned by `cv2.findContours`). Reshape `(N, 2)` arrays to `(N, 1, 2)` first.
:type contour: ndarray[N, 1, 2]
:param eps: Mask quantisation factor (downsamples the bounding box by `eps`). Default: `1`.
:type eps: int, optional
:param thickness: Drawing line thickness. Default: `1`.
:type thickness: int, optional
:param pad: Margin added around the contour. Default: `2`.
:type pad: int, optional
:returns: **mask** (*ndarray[uint8]*) – Small `{0, 1}` mask sized to the contour's bounding box + padding.
:rtype: ndarray

**Example**

From `poliamid/fractals.ipynb`:

```python
>>> from combra.contours import contour_to_binary_mask
>>> mask = contour_to_binary_mask(cnt, eps=1, thickness=1, pad=2)
>>> print(mask.shape, mask.dtype)
```
````

## Drawing

````{py:function} combra.contours.draw_contours(image, cnts, color_corner=(0, 139, 139), color_line=(255, 140, 0), r=2, e_width=5, l_width=2, corners=False) -> PIL.Image

Draw simplified contours onto a `PIL.Image`. When `corners=True`, also draws filled circles of radius `r` at each vertex.

:param image: Background to draw on.
:type image: PIL.Image
:param cnts: Contours from `find_contours`.
:type cnts: list[ndarray]
:param color_corner: Vertex marker colour `(R, G, B)`. Default: `(0, 139, 139)`.
:type color_corner: tuple[int, int, int], optional
:param color_line: Edge colour `(R, G, B)`. Default: `(255, 140, 0)`.
:type color_line: tuple[int, int, int], optional
:param r: Vertex marker radius (if `corners=True`). Default: `2`.
:type r: int, optional
:param e_width: Vertex outline width. Default: `5`.
:type e_width: int, optional
:param l_width: Line width. Default: `2`.
:type l_width: int, optional
:param corners: Draw filled circles at vertices. Default: `False`.
:type corners: bool, optional
:returns: **image** (*PIL.Image*) – Modified in place and returned.
:rtype: PIL.Image

**Example**

```python
>>> import cv2
>>> from PIL import Image
>>> from skimage import color
>>> from combra import contours, data
>>> _, img = data.microstructure_images()[0]
>>> _, processed = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
>>> simplified = contours.find_contours(processed, tol=3)
>>> pil = Image.fromarray(color.gray2rgb(processed))
>>> overlay = contours.draw_contours(pil, simplified, corners=True, r=2)
```
````

## See also

- {py:func}`combra.angles.vertex_angles` — uses `find_contours` internally.
- {py:func}`combra.mvee.fit_mvee` — fits an MVEE to each `find_contours` output.
