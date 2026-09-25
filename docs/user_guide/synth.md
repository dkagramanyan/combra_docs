# Synthetic ground truth

A real micrograph cannot tell you how accurate an angle method is: nobody knows
where the true corners of its pools are. {py:mod}`combra.synth` makes images
where that is known. It draws cobalt {term}`pools <pool>` as polygons, renders
them like an SEM image, runs a method on the rendering and scores the method's
polygons against the polygons that were drawn. This is how P6
({py:func}`combra.angles.vertex_angles`) was chosen over P0
({doc}`legacy`), and how P7 ({doc}`experimental`) is measured.

For a worked run, see {doc}`/examples/synth`.

## The generator

{py:func}`~combra.synth.pool_polygon` draws one pool of a given equivalent
diameter. `k` junctions are placed on an ellipse, at jittered radii and at least
`120° / k` apart: these are the convex corners. Between two junctions the
neighbouring carbide grain presses one or two corners into the pool, which gives
the reflex corners. The shape is then scaled to the diameter, and nearly
collinear vertices, very short edges and self-intersections are removed. The
parameters live in {py:data}`~combra.synth.GENERATOR`.

{py:func}`~combra.synth.make_canvas` fills a 512 px canvas with such pools:

- The diameters are stratified over {py:data}`~combra.synth.DIAMETER_RANGE`
  (4–40 px), so every size gets the same number of pools.
- Pools are placed largest first, at least {py:data}`~combra.synth.MIN_GAP` px
  apart plus an exponential gap fitted to the real spacing.
- By default the draw keeps half of the true vertices reflex in every size bin
  (`balance=0.5`), so the reflex share a method reports can be read directly
  against 0.5.
- Each pool is rasterised on a grid four times finer than the image
  ({py:data}`~combra.synth.SUPERSAMPLE`) before anything is rendered, so the
  truth is exact to a quarter pixel.

The result is a {py:class}`~combra.synth.Canvas`: the pixel coverage the
renderer takes, the fine label map, and one
{py:class}`~combra.synth.TruthRegion` (label, diameter, polygon) per pool.

## The renderer

{py:func}`~combra.synth.render` turns the coverage map into a grey `uint8`
image with the properties that make real images hard to read: two grey levels
per phase, a faint grain mosaic in the carbide, noise with the real amplitude
and pixel-to-pixel correlation, an illumination gradient, and a boundary that is
blurred and slightly displaced from the true one. The last point matters: the
image itself does not say exactly where the truth is, so no method can score
perfectly.

The renderer's parameters ({py:data}`~combra.synth.RENDERER`) and the
generator's were fitted to real images: {py:func}`~combra.synth.fit_renderer`
matches the image statistics of {py:func}`~combra.synth.image_statistics`
(edge width, noise, texture, illumination, cobalt fraction, pool shape and
spacing), and {py:func}`~combra.synth.fit_generator` matches the real pools'
solidity, aspect ratio and P6 angle histograms per size class. You do not need
to rerun either to use the benchmark.

## Scoring

A method is any function `method(image) -> (mask, polygons)`: a boolean
detection mask and one `(N, 2)` polygon in `(x, y)` pixel coordinates per pool.
{py:func}`combra.angles.extract_polygons`,
{py:func}`combra.legacy.extract_polygons` and
{py:func}`combra.experimental.extract_polygons` have this form.

{py:func}`~combra.synth.score_canvas` matches every polygon to the true pool it
overlaps most and records raw rows; {py:func}`~combra.synth.summarize` pools
them into four metrics, overall and per size bin
({py:data}`~combra.synth.SIZE_BINS`):

| Metric | What it measures |
|---|---|
| IoU (`iou_truth`) | Overlap of each true pool with its polygon; 0 for a pool no polygon found. |
| Edge offset (`bias`, `spread`, `rms`) | Signed distance from the polygon's edge to the true edge, px; positive outside. |
| Corners (`corner_recovery`, `angle_err_median`) | Share of resolvable true corners with a vertex within 1.5 px, and the angle error at them. |
| Reflex share (`reflex_share` vs `reflex_share_truth`) | Share of vertex angles above 180°, the method's against the truth's. |

Two counts come with them: `found`, the share of true pools at least half
covered by the mask, and `false_polygons`, polygons that overlap no true pool.

{py:func}`~combra.synth.benchmark` runs all of this over a set of canvases.
Every canvas is rendered with the seed `seed + 300`, so every method sees the
same images. The default, `seeds=range(20)`, holds about 1960 true pools and
gives the reference numbers quoted in {doc}`angles`; it takes a few minutes for
P6. {py:func}`~combra.synth.plot_benchmark` draws the four metrics by pool size
for several methods at once.

```{note}
Below about 8 px every method reads corners too close to 180°: the blur rounds
a small pool over its whole edge. The benchmark reports this per size bin; it is
a property of the images, not a setting to tune.
```
