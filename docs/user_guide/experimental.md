# The facet method (P7)

{py:mod}`combra.experimental` holds P7, a candidate angle method. It is more
accurate than P6 on synthetic images, but on real images it gives a different
angle histogram, and it is not yet known whether that difference is the
material's or the method's. Until that is settled P6 stays the method in use.
The API and output of this module may change without a deprecation period.

For a worked run, see {doc}`/examples/experimental`.

## Pipeline

{py:func}`~combra.experimental.vertex_angles` shares its first stage with P6 and
replaces the rest:

1. **Regions.** The mask of {py:func}`combra.angles.pool_mask` finds the pools
   and orders their boundaries; components smaller than `min_area` px are
   dropped.
2. **Edge location.** {py:func}`~combra.experimental.gradient_snap` moves every
   boundary point along its normal to the sub-pixel maximum of the image
   gradient, found by fitting a parabola through three samples (Devernay's
   sub-pixel edge detector). The polygon therefore sits on the edge of the
   image, not on a mask boundary that has to be inset.
3. **Facets.** {py:func}`~combra.experimental.facets` splits the ordered edge
   points finely (Douglas–Peucker at `split` px) and merges neighbouring facets
   again, smallest fit residual first, while one line fits both within
   `merge_residual` px or their directions differ by less than `merge_angle`
   degrees (the split-and-merge scheme of Pavlidis and Horowitz). The decision is
   a line fit rather than Douglas–Peucker's single distance.
4. **Corners.** Each corner is the intersection of two consecutive facet lines,
   kept within 3 px of the split vertex, and the angles are the interior angles
   of that polygon.

{py:func}`~combra.experimental.pool_regions` returns the mask and every region
with its snapped contour, polygon and angles, for inspection.

## How it compares

On the synthetic set of {doc}`synth`, P7 recovers about 54% of the true corners,
against 37% for P6, at the same RMS edge error (0.67 px). It puts more vertices
on each polygon and produces about four times as many polygons that match no
true pool. On real images its angles carry a larger reflex share and fit the
two-Gaussian model of {doc}`angle_fit` worse.

The facet stage is written in Python and is about 50 times slower than P6:
around 2 s for one 768 px image.
