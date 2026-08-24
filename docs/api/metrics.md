# combra.metrics

```{eval-rst}
.. module:: combra.metrics
.. currentmodule:: combra.metrics
```

Metrics that score a generated sample against a reference one. Three families are
provided: transport distances between two {term}`angle density` curves, relative
errors between the bimodal-Gaussian fits of those curves, and Fréchet or MMD
distances between deep image features. Every two-input metric takes the reference
first and the generated second. The concepts — what each family measures, when
the parametric one goes undefined, and how an N-sweep is read — are in
{doc}`Comparing microstructures </user_guide/metrics>`.

```python
from combra import metrics
```

## Training-loop metrics

These score in-memory images — a numpy array or a torch tensor — and return a
scalar, so generated samples can be evaluated during training without a disk
round-trip. Each side may be a single image or a batch: the angle-density metrics
and CMMD are defined on one image, while the Fréchet-distance metrics estimate a
per-side covariance and need at least two.

Every two-input metric takes an optional `reference_cache` dict. The same dict
passed across calls that share one fixed reference batch makes the reference-side
work — the CLIP embedding, the Inception or DINOv2 moments, the angle density —
run only once. The cache is keyed by metric and parameters, not by content, so one
cache belongs to one reference batch.

### Image-feature metrics

Compare the deep-feature distributions of a reference and a generated image set.
All three ship with a default install; the DINOv2 backbone is fetched from
`torch.hub` and the InceptionV3 weights by `pytorch-fid`, both on first use.

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   compute_fid
   compute_cmmd
   compute_fd_dinov2
```

### Sharded feature extraction

Each image-feature metric is also exposed as two halves — a feature extractor and
a distance — so the expensive half can be sharded across devices or processes.
Extraction is per-image, so pooling the feature rows of disjoint shards before the
distance is exact rather than an approximation. The `compute_*` functions above
are thin wrappers over these, and the numbers are identical.

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   fid_features
   cmmd_features
   fd_dinov2_features
   frechet_from_features
   cmmd_from_features
```

### Angle-density metrics

Reduce both sides to their angle densities with the same image → angles →
histogram pipeline that builds the angle parquets, then score the two curves.
`compute_wasserstein_metrics` and `compute_gauss_metrics` additionally accept a
precomputed `(x, y)` density in place of images on either side.

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   compute_wasserstein_metrics
   compute_gauss_metrics
   images_to_angle_density
   images_to_pooled_angles
   angle_density_metrics_from_pooled
```

The bin width they fall back to when `step` is `None`:

```{eval-rst}
.. currentmodule:: combra.metrics.training

.. autodata:: DEFAULT_ANGLE_STEP

.. currentmodule:: combra.metrics
```

### Unified entry point

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   compute_all_metrics
```

## Distributed evaluation

`combra.metrics.distributed` is the sharded evaluation harness the model training
repos share. Every rank extracts features and pooled angles from its own shard;
only the feature rows and the 1-D angle arrays cross the wire, and rank 0 takes
the distances. The result is exact — verified against a single-process pass, the
ten angle-density metrics come back bit-identical and the Fréchet distances agree
to about 1e-8. The module needs `torch` and imports nothing until called. A caller
supplies only what is model-specific: how to produce a shard of generated images
as `uint8`.

```{eval-rst}
.. module:: combra.metrics.distributed
.. currentmodule:: combra.metrics.distributed

.. autosummary::
   :toctree: generated/
   :nosignatures:

   precompute_reference
   gather_generated
   distributed_metrics
   all_ranks_ok
   angle_workers

.. currentmodule:: combra.metrics
```

## Startup check & normalization

`self_test` is the check a training loop runs before its first tick, so a
misconfigured install aborts the run rather than logging `nan` for every metric.
Normalization is a separate contract every image-taking function here shares: a
non-`uint8` batch is accepted only with its float range declared as `data_range`,
because guessing per image lets two images in one batch be rescaled under
different assumptions. See {py:func}`combra.image.to_uint8`.

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   self_test
```

## Distribution comparison

Compare angle-distribution parquets, as produced by
{py:meth}`combra.data.MicrostructureDataset.generate_angles`, against a reference
parquet. `all_metrics_by_sample_size` is the image-based analogue of
`angle_metrics_by_sample_size` and adds the image-feature metrics.

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   compare_folders
   compare_pairs
   angle_metrics_by_sample_size
   all_metrics_by_sample_size
   find_kimg_parquets
   load_fid_by_kimg
```

## Reference lookup & record indexing

The small pure helpers the comparison wrappers are built from, public so a
notebook can drive a sweep itself rather than going through the printing
wrappers.

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   find_reference
   parquet_has_step
   index_by_name_step
   compute_angle_metrics
```

## Distance primitives

The metric kernels underneath the batch helpers. Each takes densities already
reduced to `(x, y)` by {py:func}`combra.stats.density_histogram`, or fits already
made against them, so they can be called directly on ad-hoc curves.

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   wasserstein_density_metrics
   gauss_density_metrics
   gauss_relative_errors
   degenerate_fit_reason
   frechet_distance
```

### Undefined rather than wrong

The bimodal-Gaussian metrics return `nan` rather than a number when either fit is
degenerate. The criteria, and what a `nan` says about the generator that produced
the density, are in {ref}`undefined-rather-than-wrong`.

## Sampler comparison

Answer how many reverse-diffusion steps a sampler needs for good quality: for each
sampler and each step count, generate a batch, score it against a fixed reference
with `compute_all_metrics`, and plot the metric against the step count.
`compare_samplers` is sampler- and codebase-agnostic — the caller supplies the
generators — so the same pair drives any diffusion model.

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   compare_samplers
   plot_sampler_comparison
```

## Convergence analysis

Aggregate an N-sweep into per-curve statistics — a Kendall trend test, endpoint
relative errors, a power-law exponent and a plateau fit — and render them as
tables and figures.

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   convergence_stats
   print_convergence_report
   summarize_metric_distribution
   plot_wdist_convergence_grid
   plot_metrics_grid
   plot_metrics_overlay
   plot_metric_distribution
   plot_distribution_grid
```

## TensorBoard training curves

Rebuild a run's training-progress plots straight from its `tfevents` scalars.
{py:func}`combra.io.read_tb_scalars` pulls every scalar series out of one event
file, {py:func}`combra.io.progress_fraction` maps event steps onto a common
`kimg / max kimg` axis so runs on different scales line up, and the grid builder
tiles them into a models × metric-family layout, each curve EMA-smoothed then
min-max normalized so the panels show convergence *shape*.

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   plot_training_curve_grid
```

## See also

- {doc}`Comparing microstructures </user_guide/metrics>` — the three families, the
  degenerate-fit rules, and how to read an N-sweep.
- {py:meth}`combra.data.MicrostructureDataset.generate_angles` — produces the
  angle parquets these comparators consume.
- {py:func}`combra.angles.plot_density_grid` — visualizes the same comparisons as
  overlaid density grids.
- {py:func}`combra.fitting.fit_plateau` — the plateau fitter used inside
  {py:func}`convergence_stats`.
- {doc}`combra.stats <stats>` — the histogram preprocessor and the distributions
  fitted here.
