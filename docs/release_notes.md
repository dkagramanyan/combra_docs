# Release notes

combra's changelog, and pointers to the four model repos' own.

## combra

The authoritative copy is `CHANGELOG.md` in the combra repository; the highlights
below track what changes for a *user* of the library.

### Unreleased

**Added**

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
| san-v2 | 0.3.0 | `CHANGELOG.md` in [san-v2](https://github.com/dkagramanyan/san-v2) |
| StyleSwin-v2 | 0.3.0 | `CHANGELOG.md` in [StyleSwin-v2](https://github.com/dkagramanyan/StyleSwin-v2) |
| DiffiT-v2 | 3.1.0 | `CHANGELOG.md` in [DiffiT-v2](https://github.com/dkagramanyan/DiffiT-v2) |
| EDM2-v2 | 3.1.0 | `CHANGELOG.md` in [edm2-v2](https://github.com/dkagramanyan/edm2-v2) |

The current cycle in all four: the conda environments moved to Python 3.12 (they were
still 3.11, so `pip install -e .` could not succeed and combra was absent everywhere);
the sharded eval harness moved into combra; hyperparameters now reach TensorBoard; and
thirteen divergent scalar keys were settled against the §7 contract and pinned by a
test in each repo.
