# combra.image

```{eval-rst}
.. module:: combra.image
.. currentmodule:: combra.image
```

Pixel-level helpers: the preprocessing and augmentation routines that turn an SEM
image tree into a training set, the box-counting fractal-dimension estimators, and
the numba line and polygon kernels the graph builder and angle extractor run in
their inner loops.

```python
from combra import image
```

The standard preprocessing pipeline reduces a grayscale image to three pixel
classes (see {doc}`the pipeline overview </user_guide/index>`):

$$
\mathrm{preproc} = 1 - \mathrm{Otsu}(\mathrm{median}(I))
                 + \mathrm{grad}(\mathrm{Otsu}(\mathrm{median}(I)))
$$

| value | meaning |
| --- | --- |
| `0` | WC grain |
| `127` | Co region |
| `254` | boundary of a Co region adjacent to a WC grain, 1 px thick |

## Preprocessing

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   render_filled_contours
   fill_polygon
   resize_folder
   augment_quadrants
   build_quadrant_dataset
   tile_images
```

## Fractal dimension

Box-counting estimators of the Minkowski-Bouligand dimension. Both take the
dimension as the slope of $\log N(\varepsilon)$ against $\log(1/\varepsilon)$ over
the range of box sizes $\varepsilon$ where that relation is linear;
{py:func}`combra.validation.check_fractal_dimension` checks them against shapes of
analytically known dimension.

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   image_fractal_dimension
   contour_fractal_dimension
```

## Geometry & line kernels

numba-compiled and, where possible, zero-allocating — written for hot-loop use
inside the crack-graph builder and the angle extractor.

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   bresenham_line
   count_border_pixels_on_line
   count_border_pixels_in_band
   perpendicular_vector
   segments_intersect
   is_point_in_polygon
```

## Array conversion

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   to_uint8
```

## Ellipse geometry

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   ellipse
```

## See also

- {doc}`combra.contours <contours>` — polygon extraction from a binarized image.
- {doc}`combra.ellipse <ellipse>` — fits the MVEE that {py:func}`ellipse` draws.
- {doc}`combra.graph <graph>` — heavy user of the geometry kernels here.
- {doc}`combra.io <io>` — packs a preprocessed folder tree into HDF5.
- {doc}`The pipeline overview </user_guide/index>` — where preprocessing sits.
