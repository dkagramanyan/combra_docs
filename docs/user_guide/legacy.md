# The previous angle method (P0)

{py:mod}`combra.legacy` holds P0, the angle method combra used before 0.15.
It is kept so that results extracted with it can be read and reproduced; new
measurements use P6, {py:func}`combra.angles.vertex_angles`. The two methods'
densities are not comparable, so a comparison always re-extracts both sides with
the same method.

For a worked run, see {doc}`/examples/legacy`.

## Pipeline

P0 works in two calls.

{py:func}`~combra.legacy.preprocess_image` reduces the image to a three-level
map (a {term}`prep` map):

1. a median filter (at the default `disk=3`, OpenCV's fast 5×5 median, which
   differs from the exact disk median on about 0.4% of pixels);
2. Otsu's threshold;
3. the morphological gradient of the thresholded mask.

The mask and its boundary are stored in one `uint8` array with the levels 0,
127 and 254. A colour image is converted as RGB, so an image read with OpenCV
must be converted from BGR first.

{py:func}`~combra.legacy.vertex_angles` then takes that map:

1. contours are found and those near the image border (`border_eps`) are
   dropped, because a clipped pool has corners made by the crop;
2. each contour is simplified with Douglas–Peucker at `tol` px (default 3);
3. vertices are removed one at a time, shortest neighbouring segment first,
   until no segment is shorter than `min_segment_len` px (5 to 20 is the useful
   range);
4. the angle at every remaining vertex is measured between the two chords, and
   the sign of their cross product puts reflex corners above 180°.

The same prep map is still the input of the beam fit, {doc}`beams`.

## `min_segment_len` is part of the result

Raising `min_segment_len` suppresses the staircase vertices of the pixel
boundary: fewer angles and a smoother density. Densities extracted at different
values are therefore different measurements.
{py:func}`~combra.legacy.output_directory` writes the value into the folder name
(`{stem}_msl5`), the same way P6 folders carry `_tol` from
{py:func}`combra.angles.output_directory`.

## How it compares

On the synthetic set of {doc}`synth`, P0 recovers about 12% of the true corners
at an RMS edge error of 1.26 px, against 37% and 0.67 px for P6. It also misses
the faint pools that Otsu's threshold alone does not see, which P6's union with
an adaptive threshold finds. {py:func}`~combra.legacy.extract_polygons` wraps
P0 in the form the benchmark scores, with the settings the reference parquets
were extracted with.
