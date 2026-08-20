# Generative models — the v2 API convention

The four model repos are **separate forks that deliberately converge on one
tooling convention**. This page is that convention: the specification every one of
them implements, section by section. All four ship it — san-v2 (v0.3.0),
StyleSwin-v2 (v0.3.0), DiffiT-v2 (v3.1.0) and EDM2-v2 (v3.1.0).

| repo | family | upstream | docs |
|---|---|---|---|
| [san-v2](https://github.com/dkagramanyan/san-v2) | GAN — StyleGAN3 + Projected GAN + SAN | Sony StyleSAN-XL | {doc}`san_v2` |
| [StyleSwin-v2](https://github.com/dkagramanyan/StyleSwin-v2) | GAN — Swin transformer | Microsoft StyleSwin | {doc}`styleswin` |
| [DiffiT-v2](https://github.com/dkagramanyan/DiffiT-v2) | latent diffusion — transformer, DDPM 1000-step schedule | NVlabs DiffiT | {doc}`diffit` |
| [EDM2-v2](https://github.com/dkagramanyan/edm2-v2) | latent diffusion — EDM σ-space U-Net | NVlabs EDM2 | {doc}`edm2` |

```{warning}
**The "today …" asides in sections 6 and 7 are history.** They name specific
defects in the present tense — EDM2-v2 taking the first N reference images,
EDM2-v2 scoring against VAE round-tripped reals, StyleSwin-v2 flip-doubling its
reference, DiffiT-v2 interleaving text records into `stats.jsonl`, san-v2 and
StyleSwin-v2 writing metrics to TensorBoard only. **All of them were fixed.** They
are kept because the rationale for each requirement is the defect that motivated
it.
```

The goal: any command, flag, checkpoint name, or generated artifact learned on
one repo transfers to the other three unchanged, and every model's generated
output feeds the wc_cv angle pipeline
(`co_angles/generate_class_samples.py`,
{py:meth}`combra.data.MicrostructureDataset.generate_angles`) with zero conversion.

The four repos: [san-v2](https://github.com/dkagramanyan/san-v2) (GAN —
StyleGAN3 + Projected GAN + SAN),
[StyleSwin-v2](https://github.com/dkagramanyan/StyleSwin-v2) (GAN — Swin
transformer), [DiffiT-v2](https://github.com/dkagramanyan/DiffiT-v2) (latent
diffusion — transformer, DDPM schedule) and
[EDM2-v2](https://github.com/dkagramanyan/edm2-v2) (latent diffusion — EDM
σ-space U-Net).

---

# The convention

## 1. Packaging & entry points

Every repo is pip-installable (`pip install -e .`) and exposes the same
console-script family:

| command | purpose | applies to |
|---|---|---|
| `<model>-train` | training | all |
| `<model>-gen-images` | per-class generation | all |
| `<model>-eval` | standalone metrics | all |
| `<model>-prepare-data` | dataset zip builder | all |
| `<model>-download-models` | backbone / weight prefetch | all |
| `<model>-compare-samplers` | sampler-vs-steps sweep | diffusion only |

- **`pyproject.toml` is the only dependency declaration** — there is no
  `requirements.txt`, and `pip install -e .` is the one install path.
  torch / ninja stay out of `pyproject.toml` (installed from the CUDA wheel
  index / conda, as now).
- combra from **one** source everywhere: optional extra `[combra]` →
  `git+https` private repo.
- CUDA story per repo class: JIT-op repos (san-v2, StyleSwin-v2) need `nvcc`
  + `ninja`; pure-torch repos (DiffiT-v2, EDM2-v2) do not.
- **`<model>-prepare-data` is a click group** with a `convert` subcommand
  (EDM2-v2's shape), sharing one transform set everywhere: `center-crop`,
  `center-crop-wide`, `center-crop-dhariwal`. EDM2-v2 additionally keeps its
  `encode` / `decode` subcommands for VAE latents.
- Bulk generation is `<model>-gen-images --save-mode hdf5`; scoring is the
  combra eval and `<model>-eval`.

## 2. Training CLI

```bash
<model>-train --outdir <dir> --cfg <preset> --data <zip> --gpus N --batch-gpu B
```

- **The click CLI is the only interface** — there is no Hydra entry point and
  no `configs/` directory.
- **`--cfg` is the preset flag name everywhere.**
- **Progress is counted in kimg and ticks** (`--kimg`, `--tick`, `--snap`) —
  never raw image counts or `Ki/Mi` suffixes.
- **One batch formula**: `total = batch_gpu × gpus × grad_accum`, with
  `--grad-accum` explicit (default 1). There is no total-batch flag.
- **One precision scheme**: `--precision {fp32,fp16,bf16}` (each repo's
  default documented in its presets; GradScaler used only for fp16), plus
  `--tf32 True/False` (default `True`) and `--bench True/False` (default
  `True`, cuDNN autotune).
- **Boolean flags are `--flag True/False`** (click `type=bool`) — no
  `--x/--no-x` pairs.
- **`--mirror True/False`** (default `False`) means one thing everywhere: a
  stochastic per-item horizontal flip in the **training** loader. Eval and
  combra-reference loaders never flip, and datasets are never flip-doubled.
- Shared optional flags — identical names *and semantics* in all four:

  | group | flags |
  |---|---|
  | run control | `--kimg --tick --snap --seed --desc -n/--dry-run --workers` (workers default 3) |
  | data | `--cond --mirror` |
  | batch / precision | `--grad-accum --precision --tf32 --bench` |
  | checkpointing | `--snapshot-keep-last` |
  | combra eval | `--combra-metrics --num-fid-samples --combra-ref-count` |
  | diffusion eval | `--eval-sampler --eval-sampling-steps` |

- **Progressive-training flags** (model-specific, but following the same
  conventions — kebab-case names, `--flag True/False` booleans):
  - **san-v2** keeps its StyleGAN-XL progressive stack, renamed to
    kebab-case: `--stem`, `--superres`, `--up-factor`, `--head-layers`,
    `--syn-layers`, `--cls-weight`, and `--path-stem <snapshot>` (weights-only
    warm start of the frozen lower-resolution stem).
  - **DiffiT-v2** gets `--init-weights <snapshot>` — a weights-only warm
    start for higher-resolution finetuning (loads EMA weights from a previous
    stage's snapshot, fresh optimizer; replaces the removed `--resume`-based
    flow).
  - **StyleSwin-v2** and **EDM2-v2** train each resolution independently and
    have no progressive flags.
- **Self-spawning multi-GPU**: `--gpus N` spawns one worker per GPU via
  `torch.multiprocessing`; `torchrun` is never required for training.
- **`--seed` means the same thing everywhere**: it seeds weight
  initialisation, data shuffling and the eval-latent draws in all four repos,
  so two runs with the same command and seed produce the same snapshots (up
  to hardware nondeterminism from cuDNN / `torch.compile`). The eval-latent
  and grid-latent draws derive from `--seed` alone — never scaled by the GPU
  count (today the GAN loops seed them with `seed × gpus`), so the same seed
  draws the same latents at any `--gpus`. "Data shuffling" includes the
  distributed sampler: its epoch seed derives from `--seed` (today DiffiT-v2
  never seeds its `DistributedSampler`, so `--seed` does not change
  multi-GPU data order at all). Paired draws come from **one** seeded
  generator: today san-v2 draws eval latents from torch's RNG but the
  paired class labels from numpy's global RNG, so a specific fake batch is
  not reproducible even at a fixed GPU count. Generation-side determinism
  is the §4 seed rule.
- Run directory: `<outdir>/<id:05d>-<cfg>-gpus<G>-batch<B>[-desc]`, where
  `B` is the **total** batch and the name after the id is exactly
  `<cfg>-gpus<G>-batch<B>` — no dataset name spliced in (today san-v2 and
  StyleSwin-v2 embed the dataset basename). A **fresh id is always
  allocated**: existing directories are never reused (today EDM2-v2 and
  san-v2 re-enter a matching directory to resume — san-v2's reuse branch is
  permanently active because `--restart_every` defaults to 999999999, and
  each re-entry truncates `stats.jsonl` **and overwrites
  `training_options.json`**, losing config provenance; DiffiT-v2 re-enters
  a matching directory only when `--resume` is passed — all of that goes
  away with §3). The directory contents are fixed by the §7 log contract.

## 3. Checkpoint contract

Exactly one artifact kind — no resume, no best-model tracking, no separate
final checkpoint:

| artifact | rule |
|---|---|
| `<model>-snapshot-<kimg:06d>-inference.pt` | EMA-only weights; written every snapshot tick **and always at the last tick**, so the newest snapshot *is* the final model; history pruned to `--snapshot-keep-last` (default 3, `0` = keep all) |

- **No resume.** There is no `--resume` flag, no rolling `latest` checkpoint
  and no auto-restart: training runs start-to-finish.
- **Writes are atomic — MUST.** Every snapshot is written to a temp file in
  the run directory and moved into place with `os.replace`, so a snapshot
  that exists under its final name is always complete (today **no repo does
  this fully**: EDM2-v2 is atomic for its `.pt` checkpoints only — the
  per-tick inference `.pkl` is a plain in-place `pickle.dump`; DiffiT-v2
  writes its `-inference.pt` files — exactly what generation loads — in
  place, and its pruning can then delete the last good snapshot while
  keeping a corrupt newest; san-v2 and StyleSwin-v2 stream every checkpoint
  in place, so a walltime kill mid-dump corrupts the very file resume
  depends on).
- **The last tick always snapshots — MUST**, even when `--kimg` is not a
  multiple of the snapshot cadence (today EDM2-v2 never snapshots the final
  partial interval), so the newest snapshot is always the final model.
- **Only EMA weights ever touch disk** — raw (non-EMA) model weights,
  discriminators and optimizer state are never saved.
- **No `best_model.*`.** Pick the best checkpoint post-hoc from `stats.jsonl`
  against the snapshot history (set `--snapshot-keep-last 0` on runs where
  you want the full history to choose from). This depends on the §6 rule
  that combra metrics are mirrored into `stats.jsonl` — today san-v2 and
  StyleSwin-v2 write them to TensorBoard only, so post-hoc selection is
  impossible for their existing runs.
- **EMA stays per-family** (like samplers): classic half-life EMA in the
  GANs, `--ema-rate` in DiffiT-v2, PowerFunctionEMA in EDM2-v2 — the
  algorithms are genuinely different and are documented, not unified.
- **Progressive stages still work**: san-v2's `--path-stem` and DiffiT-v2's
  `--init-weights` are **weights-only warm starts** from a previous stage's
  snapshot (§2) — initialization, not resume.
- **Format: `.pt` state dicts only** — a state dict stores only weight
  tensors keyed by parameter name, so loading rebuilds the model from current
  code instead of unpickling stored classes. No pickled-module saving.
- **No `timm` in artifacts.** Both artifact kinds hold **generator-side
  weights only** — no discriminator and therefore no `timm` feature-network
  modules or weights ever enter a checkpoint. Loading a checkpoint never
  requires `timm` (or any particular `timm` version); `timm` remains a
  train-time-only dependency of the GAN discriminators.
- **Self-describing metadata** in every checkpoint:
  `{n_classes, resolution, class_names, cur_nimg}` — downstream code reads
  grain-class *names* from the checkpoint instead of guessing integer
  conventions (the full label contract is §5).

```{warning}
Runs are unrecoverable by design: a crash or SLURM walltime kill cannot be
resumed. Size `--kimg` (or split stages) so a run fits its job's time limit —
the training sbatch scripts allow 3–4 days. Because there is no resume, the
two MUSTs above are load-bearing — atomic writes guarantee a kill never
corrupts an already-written snapshot, and the last-tick snapshot guarantees a
completed run always ends in a usable model — and both are verified by the
conformance suite below.
```

## 4. Generation contract

```bash
<model>-gen-images \
    --network <checkpoint> --outdir <dir> \
    --classes 0,1,4-6 --samples-per-class N \
    --seed 42 --gpus 2 --batch-gpu 32 \
    --save-mode {hdf5,dir} \
    [GAN: --trunc 0.7] \
    [diffusion: --sampler <name> --steps K --cfg-scale S | --guidance G]
```

- One checkpoint flag: **`--network`**.
- **`--batch-gpu` is the only generation batching flag**, and `--gpus N`
  self-spawns per-GPU worker processes — the same launch model as training
  (no `torchrun`, no thread pools).
- `--classes` accepts indices **or class names**
  (`--classes Ultra_Co11,Ultra_Co6_2`) — see the label contract in §5 — and
  every entry is validated against the checkpoint's `n_classes` /
  `class_names` metadata (today san-v2 does no validation: an out-of-range
  index dies with a bare `IndexError` deep in `w_avg` indexing, and an
  in-range but untrained or swapped row generates silently).
- **Determinism rule** in all four: `seed = base + class·samples_per_class + idx`
  — any subset of the output is reproducible in isolation.
- **Identical outputs across repos**:
  - `hdf5` (default): per-rank shards `shards/rank_NNN.h5` in the
    **`RankH5Writer` layout** (`class_<c>/images|seeds`, images stored as
    **uint8 NHWC** — see the §5 normalization contract), merged by rank 0
    into **`<desc>.h5`** — exactly what the wc_cv angle pipeline consumes.
  - `dir`: `class_<c>/idx_<i:06d>_seed_<s>.png`.
- **One h5 signature**: every shard and merged file carries the attributes
  `format = "generated_images_shard"` (one value for all four repos) and
  `schema_version = 1`, so downstream code sniffs any model's output
  identically.
- **The merge hard-fails on incomplete shards.** Every shard records a
  per-sample `written` mask and a `missing_count` attribute; rank 0 refuses
  to produce the merged `<desc>.h5` while any `missing_count` is nonzero
  (today the san-v2 and DiffiT-v2 mergers record `missing_count` but merge
  anyway — and the combra consumer never reads it, so a crashed generation
  run's zero-filled slots are consumed downstream as black images).

## 5. Class-label & dataset contract

The integer label is an implementation detail; the grain-class *name* is the
identity. Two rules:

**Rule 1 — canonical ordering.** The integer label is the index of the class
folder in `sorted()` (alphabetical) order. Every `dataset_tool*.py` derives
labels this way.

```{warning}
**Artifacts predating Rule 1 do not follow it, and combra will not guess.** The
on-disk `imagenet_9to4_*` archives the earlier runs consumed carry a swapped
`1, 0, 2` label order and record no class names, so class identity is simply not
recoverable from those files. combra no longer ships a legacy index→name table:
a generated `.h5` whose groups are bare `class_0` / `class_1` with no
`class_names` is **rejected**, because the alternative was silently attributing
every metric to the wrong grain class whenever the guess was wrong. Rebuild the
dataset (Rule 2) and retrain rather than remapping.
```

**Rule 2 — names travel with every artifact.**

| stage | requirement |
|---|---|
| dataset zip | `dataset.json` carries `"class_names": ["Ultra_Co11", "Ultra_Co25", "Ultra_Co6_2"]`, index-aligned, written automatically from the folder names |
| checkpoint | `class_names` copied into every checkpoint (part of the §3 metadata) |
| generated h5 | `class_names` stamped as a root attribute + per-`class_<c>` group attribute |
| generated dir | a `classes.json` manifest next to the `class_<c>/` folders |
| CLI | `--classes` accepts **names as well as indices** |
| downstream | combra matches by **name**. There is no index→name fallback: a file with bare `class_<n>` groups and no names raises rather than being guessed at |

### Dataset item contract

What a dataset yields is part of the API, identical in all four repos:

- **Item = uint8 CHW at the zip's resolution; label = one-hot float32.**
  Any normalization (`[-1,1]`, ImageNet mean/std) happens in the training
  loop, never inside the dataset class.
- **RGB everywhere.** The pipelines are explicitly 3-channel end-to-end:
  grayscale sources are converted **once, at dataset build time**
  (`<model>-prepare-data`); dataset classes and generation writers *assert*
  3 channels instead of silently converting at runtime.
- Horizontal flip is the loader-level `--mirror` augmentation defined in §2 —
  datasets are never flip-doubled.

### Normalization contract

**uint8 `[0, 255]` RGB at every boundary; float only inside the process.**

- On disk and at every artifact boundary the image format is uint8 RGB:
  dataset zips, generated PNGs, the h5 `images` datasets, and every batch
  handed to combra for scoring. Never pass float batches to combra and rely
  on its range inference — an unusual batch (e.g. an all-positive `[-1,1]`
  batch) can be misread; the training loops denormalize to uint8 first.
- The **float training space is per-family** (like EMA and samplers) because
  it is baked into the trained weights, and it stays *inside* the
  training/generation process: `[-1, 1]` for san-v2 and DiffiT-v2, the
  Stable-Diffusion VAE latent space for EDM2-v2, ImageNet mean/std for
  StyleSwin-v2. Each repo normalizes immediately after loading and
  denormalizes with the **exact inverse** immediately before writing or
  scoring — one normalize/denormalize pair per repo, defined in one place,
  asserted to round-trip.

## 6. Evaluation contract

- **In-training combra eval** (all four): every snapshot tick, fakes generated
  **sharded across all ranks**; reference = whole training set — **raw,
  unflipped uint8 dataset pixels, never VAE round-trips** — with features
  precomputed once before the loop; `self_test` at startup (one
  shared implementation in `combra.metrics` — today only DiffiT-v2 and
  EDM2-v2 carry private copies, the GANs have none).
- **Uniform knobs**: `--num-fid-samples` (default 10000, `0` disables eval)
  and `--combra-ref-count` (cap the reference side). A capped reference is a
  **seeded random subset** — never the first N: dataset zips are
  class-sorted, so a first-N slice is class-biased (today EDM2-v2 takes the
  first N while its fakes draw classes uniformly — the two sides of the FID
  that drives `best_model.pt` don't even share a class distribution).
- **Uniform keys**: `Metrics/combra_fid`, `Metrics/combra_cmmd`,
  `Metrics/combra_fd_dinov2`, the angle-density metrics, and
  `Metrics/combra_fid_best` — all mirrored to `stats.jsonl` (san-v2 and
  StyleSwin-v2 originally wrote `Metrics/combra_*` to TensorBoard **only**: lose the
  tfevents file and the run's entire metric history was gone).

  ```{versionchanged} 2026-08-18
  **The `10k` suffix is gone.** This section originally specified a *literal* `10k`
  in the key names, so that keys stayed stable across runs whatever
  `--num-fid-samples` said. That backfired: every run evaluated at a non-default
  count emitted a key claiming 10 000 samples, and every chart built from it was
  mislabelled. Keys are now bare and the count is its own scalar,
  `Metrics/combra_num_fid_samples` — stable *and* honest.
  {py:func}`combra.metrics.load_fid_by_kimg` reads the bare key and still accepts
  the legacy one, so archived runs remain readable.
  ```
- `<model>-eval` standalone evaluator in all four.

### How the combra metrics are computed

One eval pass per snapshot tick, identical in all four repos:

1. **Reference (once, before the loop).** Every rank extracts features from
   its deterministic slice of the real training set — **raw dataset pixels
   as uint8, never flip-augmented and never VAE round-trips** (today EDM2-v2
   scores against encoder-decoded reals, which hides the VAE quality gap and
   breaks cross-repo comparability, and StyleSwin-v2's `--mirror`
   flip-doubles the reference) — InceptionV3 features
   (FID), CLIP embeddings (CMMD), DINOv2 features (FD-DINOv2) and pooled
   vertex angles — via combra's split APIs
   ({py:func}`combra.metrics.fid_features`, `cmmd_features`,
   `fd_dinov2_features`, {py:func}`combra.metrics.images_to_pooled_angles`).
   The gathered reference features are cached on rank 0 for the whole run.
2. **Fakes (each tick).** Every rank generates its shard of the
   `--num-fid-samples` fakes from the EMA generator — GANs by a direct
   `G_ema` forward, diffusion models by running `--eval-sampler` for
   `--eval-sampling-steps` in VAE latent space and decoding to pixels — and
   extracts the same features from its own shard.
3. **Distances (rank 0).** Only the small feature rows and pooled-angle
   arrays are gathered; rank 0 computes the Fréchet distances (`fid`,
   `fd_dinov2`), the CLIP MMD (`cmmd`) and the angle-density metrics
   (Wasserstein `w1`/`w2`/`circular_*` + bimodal-Gaussian fit errors) against
   the cached reference
   ({py:func}`combra.metrics.frechet_from_features` for both Fréchet metrics,
   {py:func}`combra.metrics.cmmd_from_features` for CMMD, and
   {py:func}`combra.metrics.angle_density_metrics_from_pooled` over the gathered
   {py:func}`combra.metrics.images_to_pooled_angles` arrays).
4. **Logging.** Results land in TensorBoard as `Metrics/combra_*` and in
   `stats.jsonl`. A metric whose backend is unavailable (e.g. no network for
   DINOv2 weights) records `nan`; a missing combra package prints a startup
   warning and training continues without eval.

Because feature extraction is per-image and angle pooling is concatenation,
the sharded result is **exact** — numerically identical to a single-GPU
{py:func}`combra.metrics.compute_all_metrics` call over the full batches.

## 7. Logging & TensorBoard contract

Every run directory contains the same five artifacts — no more, no fewer.
One console log, one scalar stream, one TensorBoard event file:

| file | contents |
|---|---|
| `training_options.json` | the resolved launch config |
| `<id:05d>-<cfg>-gpus<G>-batch<B>[-desc].log` | rank-0 console transcript, named after the run directory; every line prefixed `[YYYY-MM-DD HH:MM:SS]` |
| `stats.jsonl` | **the machine-readable source of truth**: one JSON line per tick holding every scalar (same keys as the TensorBoard tags) plus `wall_time` / `datetime` columns — **scalar rows only**, no text/log records (today DiffiT-v2's vendored logger interleaves `{"kind": "text", ...}` console records among the scalar rows: archived run 00018 holds 2 607 text lines among 2 395 scalar rows, so any reader must shape-filter first) |
| `events.out.tfevents.*.<id:05d>-<cfg>-gpus<G>-batch<B>[-desc]` | TensorBoard scalars, image grids and text — written by rank 0 only; the run name is appended via `SummaryWriter(filename_suffix=...)` |
| `reals.png`, `fakes_init.png`, `fakes<kimg>.png` | sample grids (see below) |

The event file is written **directly in the run directory** — never in a
`tb/` or `logs/` subfolder — so the TensorBoard run name is exactly the run
directory name (`<id:05d>-<cfg>-gpus<G>-batch<B>[-desc]`). Point TensorBoard
at the parent: `tensorboard --logdir <outdir>` and every run appears under
its training-folder name. The event file also carries the run name as a
**`filename_suffix`**: TensorBoard's writer generates the
`events.out.tfevents.<time>.<host>.<pid>.<n>` prefix and the file cannot be
renamed outright, but the suffix makes a copied event file self-identifying
— the `wc_cv/ml/` analysis folders hold bare tfevents files copied out of
their run dirs, identifiable today only by the folder they were copied
into. The `.log` file carries the same name, so a run's log, its folder,
its event file and its TensorBoard curve are all found by one string.

**What the run log does and does not capture.** The `.log` file starts when
the training process installs its logger — which the trainer must do **first
thing in `main()`**, and immediately write a startup header (torch / CUDA
versions, GPU names, the relevant env vars) so the log is self-sufficient.
Anything printed *before* that is not in it: the `sh/` launch script's own
output (conda activation, env setup) and early failures (import errors, CUDA
init crashes). Under SLURM that output lands in `slurm-<jobid>.out` — keep it
as the debugging fallback for launches that die before the run directory
exists.

**Sample grids follow one scheme** (san-v2's implementation is the
reference): fixed latents seeded once at startup, class-sorted rows for
labeled data, resolution-adaptive grid size; `reals.png` built once from raw
dataset samples, `fakes_init.png` at start, `fakes<kimg>.png` every snapshot
tick, and the same grid logged to TensorBoard under the `Fakes` tag.

TensorBoard tag schema — identical namespaces in all four, with the global
step = `cur_nimg` everywhere, so curves are directly comparable across batch
sizes, GPU counts and repos:

| namespace | contents | cadence |
|---|---|---|
| `Loss/*` | model-family losses (G / D / R1 for the GANs, denoiser loss for diffusion) | every tick |
| `LearningRate/*` | effective learning rates (`G`/`D`, or `lr`) | every tick |
| `Timing/*` | sec/tick, sec/kimg, eval time | every tick |
| `Resources/*` | GPU / CPU memory | every tick |
| `Metrics/combra_*` | the §6 combra metrics | every snapshot tick; **not** step-held |
| `Fakes` | EMA sample grid (image) | every snapshot tick |

```{versionchanged} 2026-08-20
**`Metrics/combra_*` are not step-held.** This table originally said the metric row was
held between snapshot ticks. All four repos deliberately do the opposite: a tick with no
eval writes no combra columns. Repeating the previous tick's values at a new step turns
the metric curves into step functions and lets post-hoc snapshot selection resolve to a
kimg that was never evaluated.

**One shared `self_test` and one shared harness.** §6's "one shared implementation"
and §7's "global step = `cur_nimg` everywhere" are now true of all four repos; they were
not when written. DiffiT-v2 and EDM2-v2 carried private `combra_smoke_test` copies, and
san-v2 and EDM2-v2 logged the step in kimg.
```

`stats.jsonl` keys are part of the contract, not an implementation detail:
the wc_cv analysis layer reads them directly (e.g.
`combra.metrics.load_fid_by_kimg`, which reads the contract keys
`Metrics/combra_fid` + `Progress/kimg` from the same JSON line and falls back to
the legacy `Metrics/combra_fid10k`), so renaming a key is a breaking change for
the analysis notebooks.

## 8. Samplers (diffusion models)

Sampler **algorithms stay per-family** — DiffiT-v2's `dpm++/unipc/ddim/ddpm`
(DDPM 1000-step schedule) and EDM2-v2's `dpm++/edm/euler/ddim` (σ-space) are
genuinely different integrators and are *not* unified. Only the **flag names**
are standardized:

| context | flags |
|---|---|
| training-time eval | `--eval-sampler` / `--eval-sampling-steps` |
| generation | `--sampler` / `--steps` |

```{note}
The overlapping names are **not interchangeable**: `ddim` and `dpm++`
integrate different parameterisations of the reverse process in the two
repos, so step counts and quality do not transfer. Calibrate per repo with
its own `<model>-compare-samplers` ({doc}`sampler_comparison`).
```

## 9. Launch scripts

Cluster launches are plain shell scripts — **no `.sbatch` files in the
repos**. Each repo ships the same set under `sh/`:

```
sh/train_256.sh     sh/train_512.sh     sh/train_1024.sh
sh/generate_256.sh  sh/generate_512.sh  sh/generate_1024.sh
```

Each script contains exactly two things:

1. **The environment** — everything a compute node needs, in one place:
   conda activation (env name = repo name), `CUDA_HOME` /
   `TORCH_CUDA_ARCH_LIST`, and the **offline-cluster contract**:
   `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1` set in every script, with
   backbones prefetched once on a login node via `<model>-download-models`.
2. **One console-command call** — `<model>-train …` or
   `<model>-gen-images …` with the §2 / §4 flags.

Rules:

- **No hardcoded user homes, `--nodelist`, or account IDs** inside the
  scripts. The repo root is self-located (walk up to `pyproject.toml`);
  SLURM specifics are supplied at submission time:
  `sbatch --account=<proj> --partition=rocky --gpus=2 sh/train_256.sh`.
- The same script runs unmodified on a workstation:
  `bash sh/train_256.sh`.

## 10. Repository infrastructure

- **Tests**: every repo ships `tests/test_smoke.py` (CPU: forward contracts,
  CLI parsing) plus CUDA-op tests where custom kernels exist (san-v2,
  StyleSwin-v2); pytest config lives in `pyproject.toml`
  (`testpaths=["tests"]`).
- **CI**: one identical `ci.yml` in all four — a ruff lint job + the CPU
  smoke tests, one Python version (3.11), modern action pins, all-branch
  push triggers, concurrency cancel, pip cache, deps via
  `pip install -e ".[dev]"`.
- **Lint**: the same ruff block in every `pyproject.toml` — `select=["F","I"]`,
  line-length 120, `combine-as-imports`.
- **Python floor**: `requires-python = ">=3.10"` everywhere; no upper caps.
- **Versioning**: semver in `pyproject.toml` + Keep-a-Changelog with real
  versioned releases (EDM2-v2's current style) — no more dated
  "Unreleased"-only changelogs.
- **`.gitignore`**: one template — `runs/`, `training-runs/`, `datasets/`,
  `generated/`, `logs/`, `*.log`, `__pycache__/`, `*.py[cod]`,
  `.pytest_cache/`, `*.egg-info/`, `build/`, `dist/`.
- **Vendored code**: one `dnnlib/` lineage (the 2024 copy + the timestamp
  patch) shared by the three repos that vendor it. `torch_utils/` is
  intentionally **not** unified — san-v2 genuinely needs its CUDA `ops/`
  tree and EDM2-v2 its distributed helpers.
- **No fork leftovers**: upstream demo images, Microsoft template meta files
  and other inherited clutter are removed (kept: the actual licenses).

---

# Model-family differences

Everything above is identical across the four repos. What follows is deliberately
not — these are model-family details, not tooling drift:

1. **combra install** is uniform: all four pull the private repo over `git+https`
   via the `[combra]` extra — which requests `combra[metrics]`, so the FID / CMMD /
   FD-DINOv2 backends come with it — and none ship a `requirements.txt`
   (`pip install -e .`). All four require Python 3.12+, matching combra.
2. **CUDA toolchain**: san-v2 and StyleSwin-v2 build custom CUDA ops (san-v2 against
   conda's `nvcc` with `CUDA_HOME=$CONDA_PREFIX`; StyleSwin-v2 via the system CUDA
   module); DiffiT-v2 and EDM2-v2 are pure-torch and need no custom ops.
3. **Model-family internals stay per-repo** (documented, not unified): the samplers
   (above), the EMA algorithm (classic half-life vs `--ema-rate` vs PowerFunctionEMA),
   and the float training space (`[-1, 1]` for san-v2/DiffiT-v2, ImageNet mean/std for
   StyleSwin-v2, the VAE latent space for EDM2-v2). Every artifact still crosses the
   boundary as uint8, so cross-repo comparisons remain valid.
4. **DiffiT-v2 has no `--cond`.** It is class-conditional by construction —
   classifier-free guidance trains against a null class — so an unconditional switch
   would be a flag that cannot do anything, not CLI alignment. The other three take
   `--cond`.
5. **Tick and snapshot cadence differ.** `--snap` counts ticks and a tick is a
   different amount of training per repo: san-v2 and StyleSwin-v2 default to
   4 kimg/tick × 50 ticks = 200 kimg between snapshots, EDM2-v2 to 128 × 64 = 8 192
   kimg, DiffiT-v2 to its per-`--cfg` values. Set `--tick`/`--snap` explicitly when
   comparing runs across repos.
6. **The sharded eval harness is shared, not per-repo.** It lives in
   {py:mod}`combra.metrics.distributed`, behind the `[metrics]` extra that every repo
   already installs, so combra's dependency-light core still carries no torch. The four
   private copies had drifted apart — two used `all_gather` and two `gather`, two
   reported a failure flag and two could not — which is why they were merged. A 2-rank
   check pins the result: the ten angle-density metrics are bit-identical to a
   single-process pass and the Fréchet distances agree to ~1e-8.

# Conformance

Each repo proves the convention with its own CPU-only test suite — no GPU, no
dataset, no model execution — so drift is caught by `pytest`, not by a failed
cluster run. The convention had already rotted silently once (`--use-ddim`,
`network-snapshot-final.pkl`, inverted flags), which is why the checks exist.

| check | what it asserts | where |
|---|---|---|
| **Entry points** | Every `[project.scripts]` console script answers `--help` **from a foreign cwd**. Catches a script declared but not importable once installed — pytest puts the repo root on `sys.path` and masks exactly this. | `test_entry_points.py` (all four) |
| **CLI + artifact contract** | The §2/§4 flags and defaults; the HDF5 shard schema (`class_<c>/images|seeds`, `format`/`schema_version`) and the merge hard-fail on gaps; §3 checkpoint metadata; the normalize/denormalize round-trip; the §5 class-label rules. | `test_conformance.py` (edm2) |
| **Logging namespaces** | The §7 TensorBoard / `stats.jsonl` key names, asserted against the training loop. Thirteen keys had drifted across the four repos — two logged the step in kimg and two in images, one filed learning rate under `Loss/`. | `test_logging_contract.py` (all four) |
| **`stats.jsonl` readability** | The row this repo writes is readable by `combra.metrics.load_fid_by_kimg`, which shape-filters non-scalar values away **silently**. That is how san-v2 and StyleSwin runs produced an unreadable metric history while every dashboard looked fine. | `test_stats_contract.py` (all four) |
| **combra symbols** | Every combra symbol the repo imports exists. The eval path is deliberately fault-tolerant, and that tolerance is how combra 0.5.0 removing three functions hid for a whole release. | `test_combra_contract.py` (all four) |

Repo-specific suites cover the rest: dataset conversion and the `--max-images`
class balance (`test_dataset_tool.py`, edm2 + StyleSwin), the rank-shard writer
(`test_rank_h5.py`, StyleSwin), the CUDA-op build and its `PATH` requirement
(`test_cuda_ops.py` / `test_custom_ops_path.py`, san-v2), and the generation-mode
CLI (`test_gen_images_cli.py`, DiffiT-v2).
