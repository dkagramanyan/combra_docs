# Generative models — API scheme

Four source-only repos generate WC-Co microstructure SEM images. They are
**separate forks that deliberately converge on one "san-v2-style" tooling
convention** — not a single package. This page is the cross-model map: what is
identical everywhere (the contract) and the few model-family details that stay
per-repo (samplers, EMA, float training space).

```{seealso}
This page documents the **current** state. The full specification — including the
per-repo migration deltas — is in {doc}`models_api_proposal`.
```

```{note}
**All four repos now implement the v2 convention** ({doc}`models_api_proposal`).
san-v2 (v0.3.0), StyleSwin-v2 (v0.3.0), DiffiT-v2 (v3.1.0) and EDM2-v2 (v3.1.0)
each expose the shared API:
console scripts, the unified training CLI (`--precision`/`--tf32`/`--bench`,
`True/False` booleans, kimg/tick progress), EMA-only `.pt` inference snapshots
(atomic, no resume/best/latest/final), the unified HDF5 generation signature
(`format="generated_images_shard"`, `schema_version=1`, merged `<desc>.h5`),
`class_names` on every artifact, combra metrics mirrored into `stats.jsonl`, and
no Hydra / `requirements.txt`. The cells below therefore read as the target API in
every column; only the genuinely model-specific rows (samplers, EMA algorithm,
float training space) still differ, and are documented as such.
```

| repo | family | upstream | docs |
|---|---|---|---|
| [san-v2](https://github.com/dkagramanyan/san-v2) | GAN — StyleGAN3 + Projected GAN + SAN | Sony StyleSAN-XL | {doc}`san_v2` |
| [StyleSwin-v2](https://github.com/dkagramanyan/StyleSwin-v2) | GAN — Swin transformer | Microsoft StyleSwin | {doc}`styleswin` |
| [DiffiT-v2](https://github.com/dkagramanyan/DiffiT-v2) | latent diffusion — transformer, DDPM 1000-step schedule | NVlabs DiffiT | {doc}`diffit` |
| [EDM2-v2](https://github.com/dkagramanyan/edm2-v2) | latent diffusion — EDM σ-space U-Net | NVlabs EDM2 | {doc}`edm2` |

## The shared contract

Every repo follows the same conventions:

- **click CLI as the single source of truth** for options and defaults; the Hydra
  wrappers have been removed everywhere.
- **Dataset format**: StyleGAN-style `.zip` of images + `dataset.json`, which now
  carries an index-aligned `class_names` list, built with the repo's
  `<model>-prepare-data convert` tool.
- **Run directories**: auto-numbered `<outdir>/<id:05d>-<cfg>-gpus<N>-batch<B>[-desc]`
  with `training_options.json`, the rank-0 `.log`, `stats.jsonl`, TensorBoard events
  and `fakes<kimg>.png` grids; training is accounted in **kimg/ticks** with `--snap`
  controlling the snapshot cadence.
- **Multi-GPU is self-spawning**: both training and generation launch one worker per
  GPU via `torch.multiprocessing` — no `torchrun`.
- **combra evaluation** (optional, guarded import, `--combra-metrics` default
  `true`): every snapshot tick, fakes are generated **sharded across all ranks**
  and scored against the training set (reference features precomputed once) using
  combra's split APIs — {py:func}`combra.metrics.fid_features` /
  {py:func}`combra.metrics.frechet_from_features` (one helper for both Fréchet
  metrics), {py:func}`combra.metrics.cmmd_features` /
  {py:func}`combra.metrics.cmmd_from_features`,
  {py:func}`combra.metrics.fd_dinov2_features`, and
  {py:func}`combra.metrics.images_to_pooled_angles` +
  {py:func}`combra.metrics.angle_density_metrics_from_pooled` — numerically
  equivalent to a single-GPU {py:func}`combra.metrics.compute_all_metrics` call.
  Results are mirrored into **both** TensorBoard (`Metrics/combra_fid`,
  `Metrics/combra_cmmd`, `Metrics/combra_fd_dinov2`, `Metrics/combra_fid_best`,
  `Metrics/combra_num_fid_samples` + the angle metrics) and `stats.jsonl` in all
  four repos, so post-hoc snapshot selection survives loss of the tfevents file.
  Each repo carries its own copy of the shard-generate → extract → gather harness;
  combra supplies the metric primitives, not the distribution plumbing.
- **combra install is `combra[metrics]`, and Python is 3.12+.** All four `[combra]`
  extras request `combra[metrics] @ git+https://…`, not bare `combra`: since combra
  0.5.0 the torch / `pytorch-fid` / `open-clip-torch` stack lives behind that extra,
  and without it `combra_fid` / `combra_cmmd` / `combra_fd_dinov2` come back `nan`.
  combra floors Python at 3.12, so every model repo does too.
- **Metric keys are bare.** `Metrics/combra_fid`, not `combra_fid10k`. The old `10k`
  suffix was a literal that never changed with `--num-fid-samples`, so any chart built
  from it was mislabelled; the sample count is now its own scalar,
  `Metrics/combra_num_fid_samples`. {py:func}`combra.metrics.load_fid_by_kimg` reads
  the bare key and still accepts the legacy one, so archived runs stay readable.
- **One checkpoint kind**: the EMA-only `.pt` inference snapshot, written
  atomically every snapshot tick **and always at the last tick**, pruned to
  `--snapshot-keep-last` (default 3, `0` = keep all). No resume, no rolling
  `latest`, no `best_model.*`, no separate final artifact — the best snapshot is
  chosen post-hoc from `stats.jsonl`.

## Training

| | san-v2 | StyleSwin-v2 | DiffiT-v2 | EDM2-v2 |
|---|---|---|---|---|
| entry point | `san-train` | `styleswin-train` | `diffit-train` | `edm2-train` |
| Hydra wrapper | **none** | **none** | **none** | **none** |
| presets | `--cfg` = architecture (`stylegan3-r`, …) | `--cfg styleswin-{256,512,1024}` | `--cfg diffit-{256,512,1024}` | `--cfg edm2-img{256,512,1024}-s` (+ more sizes) |
| required flags | `--outdir --cfg --data --gpus --batch-gpu` | `--outdir --data --gpus` | `--outdir --cfg --data --gpus --batch-gpu` | `--outdir --data` (`--cfg`/`--gpus`/`--batch-gpu` default) |
| precision | `--precision {fp32,fp16,bf16}` + `--tf32`/`--bench` (unified across all four; per-repo default) | | | |
| gradient accumulation | `--grad-accum` (all four; total batch = `batch-gpu × gpus × grad-accum`) | | | |
| conditioning | `--cond` | `--cond` | **always conditional** (CFG against a null class — no flag) | `--cond` (default `true`) |
| resolution strategy | **progressive**: 16² stem, then superres stages (`--superres --up-factor 2 --path-stem`, a weights-only warm start) | independent run per resolution | finetune upward via `--init-weights` (RoPE-2D) | independent preset per resolution (shared VAE latent space); no resume |

## Evaluation

| | san-v2 | StyleSwin-v2 | DiffiT-v2 | EDM2-v2 |
|---|---|---|---|---|
| in-training combra | ✔ (`--num-fid-samples`, default 10 000; `--combra-ref-count 0` = whole reference set) | ✔ (same) | ✔ (same) | ✔ (same) |
| native metric suite | `--metrics` registry (legacy) | none (`--metrics` is a reserved stub) | Inception IS/FID/sFID/P/R via `--combra-metrics=false` | offline FID + FD-DINOv2 |
| standalone evaluator | `san-eval` | `styleswin-eval` | `diffit-eval` (click) | `edm2-eval calc/gen/ref` |
| sampler-vs-steps sweep | n/a (GAN) | n/a (GAN) | `diffit-compare-samplers` | `edm2-compare-samplers` (see {doc}`sampler_comparison`) |

## Checkpoints

The checkpoint contract is now identical across all four (EMA-only `.pt` state
dicts, atomic, pruned, no resume/best/latest/final); only the snapshot filename
prefix and the EMA algorithm differ.

| | san-v2 | StyleSwin-v2 | DiffiT-v2 | EDM2-v2 |
|---|---|---|---|---|
| format | **`.pt` state dicts** — EMA-only + `{n_classes, resolution, class_names, cur_nimg}` metadata, atomic writes, no pickled modules | same | same | same |
| rolling full checkpoint | **none** (no resume) | **none** | **none** | **none** |
| inference snapshot (pruned) | `san-snapshot-<kimg>-inference.pt` — every tick **+ last tick**, `--snapshot-keep-last` | `network-snapshot-<kimg>-inference.pt` | `diffit-snapshot-<kimg>-inference.pt` | `edm2-snapshot-<kimg>[-<ema_std>]-inference.pt` |
| best model | **none** (post-hoc from `stats.jsonl`) | **none** | **none** | **none** |
| final artifact | **none** (newest snapshot is final) | **none** | **none** | **none** |
| EMA | classic `G_ema` (rampup) | classic `g_ema` | classic EMA (`--ema-rate`) | **PowerFunctionEMA** (one snapshot per EMA std) |

## Samplers (diffusion models only)

| | DiffiT-v2 | EDM2-v2 |
|---|---|---|
| available | `dpm++`, `unipc`, `ddim`, `ddpm` | `dpm++`, `edm` (Heun), `euler`, `ddim` (≡ `euler`) |
| space | DDPM 1000-step discrete schedule | EDM σ-space (Karras schedule) |
| eval default | `ddim` @ 100 steps | `dpm++` @ 25 steps |
| flags | `--eval-sampler` / `--eval-sampling-steps` (training), `--sampler` / `--steps` (generation) | `--eval-sampler` / `--eval-sampling-steps` (training), `--sampler` / `--steps` (generation) |

```{note}
The overlapping names are **not interchangeable**: `ddim` and `dpm++` integrate
different parameterisations of the reverse process in the two repos, so step
counts and quality do not transfer. Calibrate per repo with its own
compare-samplers tool ({doc}`sampler_comparison`).
```

## Generation

| | san-v2 | StyleSwin-v2 | DiffiT-v2 | EDM2-v2 |
|---|---|---|---|---|
| script | `san-gen-images` | `styleswin-gen-images` | `diffit-gen-images` | `edm2-gen-images` |
| checkpoint flag | `--network` (`.pt`) | `--network` (`.pt`) | `--network` (alias `--model-path`) (`.pt`) | `--net`/`--network` (`.pt`) |
| class selection | `--classes` (indices/ranges **or names**, validated) + `--samples-per-class` | same | same | `--classes 0,1,4-6` **or names** + `--samples-per-class` (`--seeds` legacy) |
| output | **HDF5** (unified sig, merged `<desc>.h5`, merge hard-fails on gaps) or PNG dirs + `classes.json` (`--save-mode`); self-spawning `--gpus` | same | same | same |
| quality knobs | `--trunc`, `--centroids-path` | `--trunc` | `--cfg-scale`, `--sampler`, `--steps` | `--sampler`, `--steps`, `--guidance --gnet` |

```{note}
**The generation artifacts are now equivalent.** All four repos emit the per-class
`RankH5Writer` HDF5 layout (`class_<c>/images|seeds`, uint8 NHWC) with the unified
`format="generated_images_shard"` / `schema_version=1` signature and `class_names`,
merged to `<desc>.h5` — directly consumable by the downstream angle pipeline
(`co_angles/generate_class_samples.py`,
{py:meth}`combra.data.MicrostructureDataset.generate_angles`) with no conversion step, and
the merge hard-fails on incomplete shards.
```

## Class index → grain class

All four dataset tools now derive the integer label from the **alphabetical** class
folder sort (`0 → Ultra_Co11`, `1 → Ultra_Co25`, `2 → Ultra_Co6_2`) and stamp an
index-aligned `class_names` list into `dataset.json`, every checkpoint and every
generated artifact — so new runs are self-describing by name and combra matches by
name rather than a fragile integer convention.

```{warning}
**Existing pre-migration checkpoints still use the old swapped order.** The on-disk
`imagenet_9to4_*` archives the existing runs of all four models trained on carry the
non-alphabetical order `0 → Ultra_Co25`, `1 → Ultra_Co11`, `2 → Ultra_Co6_2` (the
`Co11`↔`Co25` swap) and record no `class_names`. Those checkpoints and everything
generated from them stay under combra's legacy `CLASS_MAP` until retrained on rebuilt
zips — classify each run by the dataset path in its `training_options.json` before
remapping. See the {doc}`models_api_proposal` label contract (§5).
```

## Other known divergences

Now that all four repos share the contract, the remaining differences are
model-family details, not tooling drift:

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
6. **The sharded eval harness is per-repo.** Each repo owns its shard-generate →
   extract → all-gather → distance code. combra supplies the metric primitives
   (feature extractors, distances, `angle_density_metrics_from_pooled`) and stays out
   of the distribution plumbing, so it carries no `torch.distributed` dependency.
