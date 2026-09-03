# Release notes

combra's changelog, and pointers to the four model repos' own.

## combra

The authoritative copy is `CHANGELOG.md` in the combra repository; the highlights
below track what changes for a *user* of the library.

### Unreleased

### 0.14.0

**Changed**

- **The mixing coefficient is reported once, under the key `pi` (breaking;
  `share1` and `share2` are gone).** The fit splits its mass between the two
  modes in the proportion $\pi$ to $1 - \pi$, and the two keys reported the
  relative error of each — but mode 2 carries $1 - \pi$, so its error is fixed
  by the first at $-\varepsilon\,\pi^{\text{ref}} / (1 - \pi^{\text{ref}})$.
  A fit whose coefficient moved from 0.70 to 0.62 reported `share1 = -0.114`
  beside `share2 = +0.267`: one number told twice.
  {py:func}`~combra.metrics.compute_all_metrics` and its siblings therefore
  return nine keys rather than ten, and
  {py:func}`~combra.metrics.gauss_relative_errors` and
  {py:func}`~combra.metrics.compute_angle_metrics` return a float where they
  returned a length-2 `share_m` array (records carry `pi_m`).

  Why `pi` and not `w`: the coefficient was written $w$ everywhere it was
  displayed, while `w1` and `w2` are the Wasserstein distances — the overlay
  plot's legend read `w₁ %` beside `W-dist`, and
  {py:func}`~combra.metrics.compare_folders` printed a `w1` column (a distance)
  next to `share1%` (a mass share). See {doc}`user_guide/angle_fit` §6.

  Stored fits are untouched: the parquet column `angles_gauss_shares`, the
  `weight` argument of {py:func}`~combra.stats.truncated_bimodal_gaussian` and
  the `shares` field of `BimodalGaussianFit` keep their names, so no parquet
  needs refitting. Code that reads the metric keys does need updating — the
  model training loops log `combra_pi` where they logged `combra_share1`.

### 0.13.0

**Changed**

- **The angle fit has five parameters: one mass share replaces the two
  amplitudes (breaking).** {py:func}`~combra.stats.truncated_bimodal_gaussian`
  takes `weight` (the share of mode 1) and `total` (the curve's integral over
  [0°, 360°]) instead of `amp1`, `amp2`;
  {py:func}`~combra.fitting.fit_bimodal_gaussian` fits
  `(mu1, mu2, sigma1, sigma2, weight)` with the total fixed to the histogram's
  bin width, and returns `BimodalGaussianFit(curve, mus, sigmas, shares, total)`.
  On the reference sets the fixed total moves the fitted modes by under 0.7°
  and the residual by under 2% against the six-parameter fit. Renamed with it:
  {py:func}`~combra.metrics.degenerate_fit_reason` and
  {py:func}`~combra.metrics.gauss_relative_errors` take shares, the metric keys
  `amp1`/`amp2` are `share1`/`share2` everywhere, comparison records carry
  `share_m`, and the parquet column `angles_gauss_amps` is
  `angles_gauss_shares`. See {doc}`user_guide/angle_fit` for the scheme, and
  its §4 for why the fit stays least squares on the histogram rather than
  maximum likelihood.

:::{warning}
Fits stored in angle parquets written before this release hold amplitudes
under a column that no longer exists and are not readable by the comparison
path. Refit any parquet you intend to keep — the stored densities are enough,
so no h5 access or angle re-extraction is needed.
:::

### 0.12.0

**Fixed**

- **The bimodal-Gaussian angle fit no longer loses its second mode to a
  pedestal.** {py:func}`~combra.fitting.fit_bimodal_gaussian` started from a
  fixed guess with no upper bound on `sigma`. Whenever the reflex mode was weak
  over a heavy baseline, one very wide Gaussian was a competing least-squares
  minimum and the solver took it — fitted widths of 355° and 1.0e5°, where the
  real second mode sits near 240°. It now seeds itself from the density and
  bounds `sigma` at 180°. Over 231 fits of real angle densities, degenerate
  results went from 83 to 0, 58 improved by more than 5% in residual, and none
  got worse.

- **{py:meth}`~combra.data.MicrostructureDataset.generate_angles` fits each bin
  width independently.** It used to warm-start each width from the previous
  one's solution, so one bad fit at the finest, noisiest width propagated to
  every coarser one — across the reference parquets, one bad fit became seven.

- **{py:func}`~combra.data.plot_polyamide_fractal` no longer prints a phantom
  second mode in its subplot titles.** It fitted contour fractal dimensions —
  values in [1, 2] — with the *angle* fitter, whose means are bounded to
  [0, 360], leaving the second mode free to settle far from any data. It now
  bounds every parameter to the group's own data range. A group with too few
  occupied bins to determine the six parameters is titled
  `"(too few bins to fit)"` instead of being given invented numbers.

**Changed**

- **The angle density is fitted with a model truncated to [0°, 360°]**,
  {py:func}`~combra.stats.truncated_bimodal_gaussian`. All of the fitted
  probability mass now lies inside the interval the angles were measured on;
  the untruncated model leaked 46.8% and 99.75% on the worst real fits. `amps`
  is now each mode's integral over [0, 360], so `amps[i] / sum(amps)` is its
  share of the fitted mass. Truncated rather than wrapped, because a vertex
  angle is not a circular variable — see
  {doc}`user_guide/angle_fit` for the full scheme.

- {py:func}`~combra.fitting.fit_bimodal_gaussian`'s `mu1`…`amp2` arguments
  default to `None`, meaning "seed this from the data". Passing a value still
  overrides it per parameter, so existing callers are unaffected.

:::{warning}
Fits stored in angle parquets written before this release come from the
untruncated model with the old seeding and are **not** comparable with new ones.
Refit any parquet you intend to keep — the stored densities are enough, so no h5
access or angle re-extraction is needed.
:::

### 0.11.0

**Added**

- **The image-metric readers refuse incomplete generated h5s.**
  {py:func}`combra.metrics.compare_folders` and
  {py:func}`combra.metrics.all_metrics_by_sample_size` now validate every file
  they open the way the angle pipeline always has: a nonzero `missing_count` or
  an unwritten `written` slot raises {py:class}`combra.exceptions.IncompleteShardError`,
  a `class_*` group with no `images` dataset raises
  {py:class}`combra.exceptions.SchemaError`, and an unknown `format` warns. A
  crashed generation run can no longer feed zero-filled black images into
  FID / CMMD / FD-DINOv2.

- {py:func}`~combra.data.sweep_angles` accepts `force=True` to regenerate every
  parquet, overriding the skip of `N`s whose parquet already holds all requested
  steps. Without it, `force_rebuild_cache` on a complete sweep never takes
  effect — the up-to-date check returns before `generate_angles` runs.

**Changed**

- **The preprocessing median is now `cv2.medianBlur(5)`, and single-image HDF5
  reads no longer decompress a whole chunk each.** The two together make
  {py:meth}`~combra.data.MicrostructureDataset.generate_angles` about 2–4×
  faster end to end (23 s → 6 s for 3×360 images at 1024² on 18 workers), with
  the preprocessing-cache build — previously ~96% of the runtime — improved
  ~5×. The median change is visible in results: prep maps differ on ~0.4% of
  pixels and pooled angle densities shift slightly (L1 ≈ 0.085), so the prep
  cache version is bumped — caches rebuild automatically, but **parquets
  generated before this change should not be mixed with new ones** in
  fine-grained distribution comparisons. The exact disk-footprint median
  remains available via `preprocess_image(..., exact_median=True)` or any
  `disk` radius other than 3, and is itself ~32× faster than before. The read
  cache also adapts to the file's chunking: shards whose chunks exceed the
  128 MB default (e.g. 256-image shards at 512², 192 MB per chunk) previously
  re-decompressed a full chunk on every read (~307 ms per image) and now read
  from cache at ~0 ms.

- **The metric helpers pair classes by name, not by HDF5 group string.**
  {py:func}`~combra.metrics.compare_folders` used the group string both to read
  reference images and to key the image metrics it merges into parquet-derived
  records — but a parquet row names its class `Ultra_Co25` where the h5 group is
  `class_Ultra_Co25` or `class_0`. The two never matched, so `fid`, `cmmd` and
  `fd_dinov2` were computed and then dropped from every record without an error.
  Both helpers now resolve each file's classes the way the dataset loader does
  (`class_names` → per-group `class_name` → named group suffix) and match on the
  resolved name, so files that group their classes differently still pair up.

  `class_map=` remains available as a deliberate override, but it is now keyed by
  class name rather than group string — **update any mapping written as
  `{'class_0': 'class_Ultra_Co25'}`**. On
  {py:func}`~combra.metrics.all_metrics_by_sample_size` it is optional, and `ns`
  became keyword-only so an old positional call raises instead of binding a
  mapping to the sample-size sweep. An unpairable class is logged at warning
  level; nothing pairing at all raises
  {py:class}`combra.exceptions.SchemaError`.

- **The image-feature metrics ship by default.** `torch`, `torchvision`,
  `pytorch-fid` and `open-clip-torch` moved from the `metrics` extra into the core
  dependencies, so {py:func}`~combra.metrics.compute_fid`,
  {py:func}`~combra.metrics.compute_cmmd` and
  {py:func}`~combra.metrics.compute_fd_dinov2` work after a plain
  `pip install combra` rather than raising `ImportError` at the point of use. A
  default install is correspondingly larger, most of it PyTorch. The `metrics`
  extra is kept as an empty alias, so `pip install 'combra[metrics]'` — which the
  model repositories and the docs workflow ask for — continues to work unchanged.

  Environments that install a CUDA-specific PyTorch first, as the
  {doc}`model repositories <models/spec>` do, keep that build as long as it
  satisfies `torch>=2.13`.

**Fixed**

- **One rank failing during a sharded eval no longer hangs the job.**
  {py:func}`~combra.metrics.distributed.gather_generated` interleaved local
  extraction with the gathers, so a rank hitting a CUDA OOM or a cv2 error
  dropped out of the collectives while the others blocked in `gather` until the
  NCCL watchdog killed the run — a timeout, with the real error printed only on
  the rank that raised. It now extracts everything locally first, agrees through
  `all_ranks_ok`, and returns `(None, None)` on every rank when any rank failed.
  **Gate the {py:func}`~combra.metrics.distributed.distributed_metrics` call on
  `angles is not None`**: on rank 0 that is now the failure signal, and passing
  the sentinel through raises `ValueError` naming the cause.

- **An empty generated angle density no longer discards that tick's image
  metrics.** Early in training the generator produces nothing the contour
  pipeline finds vertices in, and the resulting exception took `fid`, `cmmd` and
  `fd_dinov2` down with the angle metrics — after their features had already
  been extracted at full GPU cost. The ten angle keys now come back `nan` with
  one logged warning, and the image metrics are returned as usual.

- **Corner pixels of the disk-median filter were uninitialized memory.** The
  median rank was computed from the full 29-pixel footprint, which a corner
  window never reaches, so those output pixels kept unwritten buffer contents
  and prep caches were non-deterministic at image corners. Shrunk border
  windows now take the median of the pixels they actually contain.

- **A preprocessing cache no longer outlives the HDF5 it was built from.** The
  reuse check accepted any cache whose shape and dtype read back — exactly what a
  regenerated container preserves — so rebuilding an `.h5` from new images left
  every later sweep silently measuring the previous run's pixels. A cache older
  than its source file is now rebuilt.

### 0.10.0

**Removed (breaking)**

- **`combra.data.CLASS_MAP` and the legacy index→name fallback.** A generated `.h5`
  with bare `class_0` / `class_1` groups and no `class_names` used to be resolved
  through a hard-coded table whose order was itself a guess about which training zip
  the checkpoint had seen. When the guess was wrong, every metric was silently
  attributed to the wrong grain class — a plausible number, not an error. Such a file
  now raises {py:class}`combra.exceptions.SchemaError`, naming the attributes that fix
  it. Artifacts from the standardized writers carry `class_names` and are unaffected;
  the per-call `class_map=` argument stays.

**Fixed**

- The synthetic gauss-metric suite was flaky on seeds it does not use. Tolerances are
  now set from measurement over unused seeds, and the mode assertions check the
  *direction* of the rasterisation bias rather than a symmetric window.

### 0.9.1

- `contour_fractal_dimension` could not accept the contours
  {py:func}`combra.contours.find_contours` returns. `cv2.findContours` yields
  `(N, 1, 2)`; combra flattens that to `(N, 2)`, which is also the shape the function
  documents -- but the mask builder underneath it accepted only the first, so the
  chain the API reference shows raised a `TypeError`. Found by running the docs.

### 0.9.0

**Added**

- Extraction parquets now record **which combra wrote them**. `run_meta` gained a
  `combra_version` field, alongside the `code_commit` that has always been there but
  resolves to `unknown` for a non-git install — which is how the model repos install
  combra, so cluster-produced rows previously carried no usable provenance.
- Every public callable now documents its parameters. The last 19 without numpydoc
  sections were closed, and the ratchet that tracked them is empty.

```{note}
A parquet written by 0.9.0 has a `run_meta` field that earlier files do not.
{py:func}`combra.io.load_rows` is unaffected — it reads only `meta` and
`prep_per_step` — but code reading the `run_meta` column directly with pyarrow will
find no `combra_version` key on a file written before 0.9.0.
```

### 0.8.1

- `from combra import __version__` did not type-check: `__init__.pyi` listed it in
  `__all__` without declaring it.

### 0.8.0

**Added**

- **Every run records which combra computed its metrics.**
  {py:func}`combra.io.write_hparams` stamps `combra/version` into the TensorBoard
  HPARAMS payload. Two runs weeks apart could otherwise be compared on numbers from
  different metric code while their logged provenance looked identical.
- {py:mod}`combra.metrics.distributed` — the sharded evaluation harness, moved into
  combra from the four model repos that each carried a copy. One implementation now,
  behind the `[metrics]` extra.
- {py:func}`combra.io.flatten_hparams` / {py:func}`combra.io.write_hparams` — record a
  run's configuration in TensorBoard's HPARAMS tab.
- `amp=False` on {py:func}`combra.metrics.fid_features`,
  {py:func}`combra.metrics.cmmd_features` and
  {py:func}`combra.metrics.fd_dinov2_features` — opt-in fp16 autocast, roughly 2.9×
  on the CLIP forward for a metric shift well under 0.1%.
- `strict=True` and `images=` on {py:func}`combra.metrics.self_test`, so a training
  loop can require the image-feature backends to be finite and can validate against
  its own reference batch.

**Fixed**

- The angle worker pool ran serial on most real batches (a fixed `chunksize=64`).
  7.2× at 64 images, 10.0× at 256, both measured at 512 px.
- `self_test`'s synthetic sample was too small to constrain a bimodal fit — degenerate
  on 6 of 12 seeds, passing only because its seed is hardcoded.

### 0.7.1

- {py:func}`combra.fitting.fit_bimodal_gaussian` could fit a mode outside the angle
  domain, and the gauss metrics blew up when it did.

### 0.7.0

- {py:func}`combra.metrics.angle_density_metrics_from_pooled` restored — its removal
  in 0.5.0 had silently disabled the model repos' combra metrics.
- The metrics path no longer guesses image ranges; `data_range` is explicit.

```{seealso}
The bimodal-Gaussian metrics return **signed relative errors**, not distances. They
can be negative, and they are `nan` when either fit is not two real modes — see
{py:func}`combra.metrics.gauss_density_metrics`.
```

## Migrating from 0.5 or earlier

0.6 was an API-convention release. Functions were renamed to `verb_noun` form, two
modules moved (`combra.approx` → {doc}`combra.fitting <api/fitting>`,
`combra.mvee` → {doc}`combra.ellipse <api/ellipse>`), and every plotter now returns
its figure and takes `save_path=` and `show=`. There are no compatibility aliases;
the repository `CHANGELOG.md` carries the full rename table.

## Model repositories

Each fork keeps its own `CHANGELOG.md`; {doc}`models/spec` is the
convention all four implement.

| repo | current | changelog |
| --- | --- | --- |
| san-v2 | 0.4.0 | `CHANGELOG.md` in [san-v2](https://github.com/dkagramanyan/san-v2) |
| StyleSwin-v2 | 0.4.0 | `CHANGELOG.md` in [StyleSwin-v2](https://github.com/dkagramanyan/StyleSwin-v2) |
| DiffiT-v2 | 0.4.0 | `CHANGELOG.md` in [DiffiT-v2](https://github.com/dkagramanyan/DiffiT-v2) |
| EDM2-v2 | 0.4.0 | `CHANGELOG.md` in [edm2-v2](https://github.com/dkagramanyan/edm2-v2) |

The current cycle in all four: the conda environments moved to Python 3.12 (they were
still 3.11, so `pip install -e .` could not succeed and combra was absent everywhere);
the sharded eval harness moved into combra; hyperparameters now reach TensorBoard; and
thirteen divergent scalar keys were settled against the §7 contract and pinned by a
test in each repo.

Most recently, every repo's eval path was audited for what happens when one rank
fails. The pattern found in all four — local work that can raise on a single rank,
sitting before a collective the others are already blocked in — turned single-rank
errors into NCCL watchdog timeouts that hid the real cause. combra's half is fixed in
{py:func}`~combra.metrics.distributed.gather_generated` (above); the repos' halves
were the reference-slice load in san-v2 and StyleSwin-v2, and the rank-0-only startup
raises in DiffiT-v2 and edm2. san-v2 and StyleSwin-v2 additionally reported
`Timing/eval_sec` from rank 0 alone, which desynchronized the training-stats
`all_reduce` on any multi-GPU run, and edm2 refused pre-encoded latent zips the angle
pipeline cannot read. See each repo's changelog.
