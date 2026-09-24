# Comparing microstructures (combra.metrics)

```{eval-rst}
.. module:: combra.metrics
.. currentmodule:: combra.metrics
```

Scores of a generated microstructure against a real reference: transport
distances and bimodal-Gaussian errors between angle densities, and FID / CMMD /
FD-DINOv2 between image features. Every metric takes the reference first. See
{doc}`/user_guide/metrics`.

```python
from combra import metrics
```

## Comparison

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   compare_folders
   compute_all_metrics
   compare_samplers
```

## Convergence with sample size

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   convergence_stats
   print_convergence_report
```

## Plotting

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   plot_wdist_convergence_grid
   plot_metrics_overlay
   plot_sampler_comparison
```

## Training-loop integration

What the model repositories call during training: a startup check and the
sharded evaluation harness, `combra.metrics.distributed`. Every rank calls
`gather_generated`; rank 0 gates `distributed_metrics` on its result:

```python
features, angles = gather_generated(shard_u8, device, rank, world_size)
if rank == 0 and angles is not None:
    scores = distributed_metrics(reference, angles, features, device=device)
```

{py:func}`combra.io.write_hparams` records the run's configuration in
TensorBoard.

```{eval-rst}
.. module:: combra.metrics.distributed
```

```{eval-rst}
.. currentmodule:: combra.metrics

.. autosummary::
   :toctree: generated/
   :nosignatures:

   self_test
   distributed.precompute_reference
   distributed.gather_generated
   distributed.distributed_metrics
```
