# combra.contours

The `combra.contours` module extracts polygon contours from preprocessed binary images and renders them back onto images for visualisation. Used internally by {py:func}`combra.angles.vertex_angles`, {py:func}`combra.ellipse.fit_mvee`, and the crack-graph builder.

```python
from combra import contours
```

## Extraction

````{py:function} combra.contours.find_contours(image, tol=None) -> list[ndarray]

Extract external contours via Canny edges + Suzuki contour finding. With `tol` set, each contour is additionally simplified with Douglas–Peucker, which is what most downstream code wants.

:param image: Preprocessed binary image.
:type image: ndarray
:param tol: Douglas–Peucker simplification tolerance in pixels — higher → fewer vertices. `None` keeps every boundary pixel; a value also drops degenerate contours of fewer than 3 points, which cannot be simplified into a polygon. Default: `None`.
:type tol: float or None, optional
:returns: **contours** (*list[ndarray]*) – One `(N_points, 2)` array per region, in both modes.
:rtype: list[ndarray]

**Example**

```pycon
>>> import cv2
>>> from combra import contours, data
>>> img = data.load_microstructure().images[0]
>>> _, processed = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
>>> raw = contours.find_contours(processed)                  # ~thousands of vertices per region
>>> simplified = contours.find_contours(processed, tol=3)    # ~tens of vertices per region
>>> print(f'raw[0]: {len(raw[0])} pts   simplified[0]: {len(simplified[0])} pts')
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

```pycon
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

```pycon
>>> import cv2
>>> from PIL import Image
>>> from skimage import color
>>> from combra import contours, data
>>> img = data.load_microstructure().images[0]
>>> _, processed = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
>>> simplified = contours.find_contours(processed, tol=3)
>>> pil = Image.fromarray(color.gray2rgb(processed))
>>> overlay = contours.draw_contours(pil, simplified, corners=True, r=2)
```
````

## See also

- {py:func}`combra.angles.vertex_angles` — uses `find_contours` internally.
- {py:func}`combra.ellipse.fit_mvee` — fits an MVEE to each `find_contours` output.
