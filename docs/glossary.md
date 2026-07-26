# Glossary

The domain terms that appear throughout the API. Read this once and the rest of
the reference reads faster.

```{glossary}

angle density
  The normalised histogram of {term}`vertex angle` values for one image or one
  batch, as `(x, y)` arrays where `sum(y) == 1`. Produced by
  {py:func}`combra.stats.density_histogram` and by
  {py:func}`combra.metrics.images_to_angle_density`. This is combra's primary
  descriptor of a microstructure: two microstructures are compared by comparing
  their angle densities, not their pixels.

vertex angle
  The interior angle at one vertex of a simplified grain contour, in degrees.
  {py:func}`combra.angles.vertex_angles` walks each closed polygon and emits one
  angle per vertex. WC-Co angle densities are characteristically **bimodal** —
  hence the bimodal-Gaussian fit everywhere in {doc}`combra.fitting <api/fitting>`.

step
  The bin width, in degrees, used to reduce raw angles to an
  {term}`angle density`. **Part of a metric's identity**: two runs are only
  comparable when reduced at the same `step`, which is why `step` is stored on
  every parquet row and checked by
  {py:func}`combra.metrics.parquet_has_step`. Defaults to
  {py:data}`combra.metrics.DEFAULT_ANGLE_STEP` (5.0°).

beam
  A WC grain approximated by its {term}`MVEE`. Its `a` and `b` semi-axis lengths
  are the *beam lengths*, and the ellipse rotation is the *beam orientation*.
  The beam-length distribution is the second descriptor combra scores, alongside
  the {term}`angle density`.

MVEE
  **M**inimum-**V**olume **E**nclosing **E**llipse: the smallest-area ellipse
  containing a contour, fitted by
  {py:func}`combra.ellipse.fit_mvee` via Khachiyan's iteration. It gives each
  grain a size (`a`, `b`) and an orientation without assuming the grain is
  convex or well-formed.

reference / generated
  The two sides of every comparison. **reference** is the ground-truth
  distribution — real SEM images, or the largest-N run in a sweep (see
  {py:func}`combra.metrics.find_reference`). **generated** is whatever is being
  scored against it, usually the output of a generative model.

N-sweep
  Computing a metric at increasing sample sizes `N` to see whether it converges.
  A metric that keeps shrinking as `N` grows was measuring sampling noise; one
  that flattens onto a non-zero floor has found a real bias. The floor is fitted
  by {py:func}`combra.fitting.fit_plateau` as $|m|(N) = a + b\,N^{-1/2}$, and
  the trend is tested by {py:func}`combra.stats.kendall_decreasing_p`.

kind
  A label distinguishing the generators being compared in one analysis (e.g.
  `'diffit'`, `'edm2'`, `'styleswin'`), used as the grouping key by
  {py:func}`combra.metrics.convergence_stats` and the metrics plots.

resolution
  The pixel side length of the images a run was produced at (256, 512, 1024 …).
  Paired with {term}`kind` it identifies a *panel* — one row/column cell of a
  comparison grid.

edge type
  The phase a crack-graph edge crosses: `0` = Co (binder), `1` = WC-Co
  (interface), `2` = WC (carbide), `3` = WC-WC (grain boundary). Each is
  weighted by the matching field of {py:class}`combra.graph.EnergyWeights`
  during the shortest-energy-path search.

fractal dimension
  The box-counting dimension of a binary image or a single contour: the slope of
  $\log N(\varepsilon)$ against $\log(1/\varepsilon)$, where $N(\varepsilon)$ is
  the number of occupied boxes of side $\varepsilon$. Computed by
  {py:func}`combra.image.image_fractal_dimension` and
  {py:func}`combra.image.contour_fractal_dimension`; the estimator is
  self-checked against shapes of known dimension by
  {py:func}`combra.validation.check_fractal_dimension`.

run_meta
  The provenance struct written on every parquet row — source file, requested
  N, extraction parameters, git commit, user, timestamp. Built by
  {py:func}`combra.io.build_run_meta`. It makes an artifact self-describing:
  you can always recover exactly how a distribution was produced.

prep
  The per-class computed payload of a parquet row (densities, fits, legends), as
  opposed to `meta`, which carries its identity (class name, step, image count).
  {py:func}`combra.io.load_rows` returns rows as `{'meta': ..., 'prep': ...}`.
```
