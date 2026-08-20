# Release notes

combra's changelog, and pointers to the four model repos' own.

```{note}
Until now no changelog reached a reader of this site. Someone reading the published
documentation could not discover that san-v2 dropped `--resume`, or that the
bimodal-Gaussian metrics changed to return `nan` for a degenerate fit — every
changelog lived only in a private code repository.
```

## combra

The authoritative copy is `CHANGELOG.md` in the combra repository; the highlights
below track what changes for a *user* of the library.

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

## Model repositories

Each fork keeps its own `CHANGELOG.md`; {doc}`examples/models_api_spec` is the
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
