# API reference

The functions a user calls to get from an image, a folder or a parquet to a
number or a figure, grouped by task. The stages these run internally, the
helpers and the result containers are not listed; their fields are described
in the Returns section of the function that produces them.

```python
from combra import data, angles, metrics
```

(api-data)=
## Data

Bundled sample images, the dataset that runs the extraction over a class
folder tree and writes parquet
({py:meth}`~combra.data.MicrostructureDataset.generate_angles`,
{py:meth}`~combra.data.MicrostructureDataset.generate_beams`), and the
readers for what it writes.

```{eval-rst}
.. module:: combra.data
.. module:: combra.io
.. currentmodule:: combra

.. autosummary::
   :toctree: generated/
   :nosignatures:

   data.MicrostructureDataset
   data.load_microstructure
   data.load_crack
   data.sweep_angles
   io.convert_folder_to_hdf5
   io.load_rows
```

(api-measure)=
## Measure an image

Vertex angles of the cobalt pools and the bimodal fit of their density,
minimum-volume enclosing ellipses (beams), and the box-counting fractal
dimension.

```{eval-rst}
.. module:: combra.angles
.. module:: combra.ellipse
.. module:: combra.image
.. currentmodule:: combra

.. autosummary::
   :toctree: generated/
   :nosignatures:

   angles.vertex_angles
   angles.angle_summary
   ellipse.fit_mvee
   image.image_fractal_dimension
```

(api-compare)=
## Compare real and generated

Score generated microstructures against a real reference: angle-Wasserstein
and bimodal-Gaussian errors from parquets, FID / CMMD / FD-DINOv2 from images,
sampler sweeps, and how the metrics converge with sample size.

```{eval-rst}
.. module:: combra.metrics
.. currentmodule:: combra

.. autosummary::
   :toctree: generated/
   :nosignatures:

   metrics.compare_folders
   metrics.compute_all_metrics
   metrics.compare_samplers
   metrics.convergence_stats
   metrics.print_convergence_report
```

(api-plotting)=
## Plotting

Every `plot_*` returns its figure and takes `save_path=None` (write a PNG) and
`show=True` (render it).

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   angles.plot_density
   angles.plot_overlay_grid
   ellipse.plot_beam_lengths
   ellipse.plot_beam_compare
   metrics.plot_wdist_convergence_grid
   metrics.plot_metrics_overlay
   metrics.plot_sampler_comparison
   graph.plot_graph
   graph.plot_paths
   synth.plot_benchmark
```

(api-crack-graph)=
## Crack graph

Crack image → directed graph → lowest-energy crack paths, for one set of
phase energies or a grid of them.

```{eval-rst}
.. module:: combra.graph
.. currentmodule:: combra

.. autosummary::
   :toctree: generated/
   :nosignatures:

   graph.extract_graph_nodes
   graph.build_crack_graph
   graph.EnergyWeights
   graph.find_shortest_energy_paths
   graph.build_energy_grid
   graph.optimize_path_energies
```

(api-benchmark)=
## Method benchmark

Generated pools with an exact truth, and the score of an angle method against
them.

```{eval-rst}
.. module:: combra.synth
.. currentmodule:: combra

.. autosummary::
   :toctree: generated/
   :nosignatures:

   synth.make_canvas
   synth.benchmark
```

(api-training)=
## Training-loop integration

What the model repositories call during training: a startup check, the
sharded evaluation harness, and the TensorBoard hyperparameter record. Every
rank calls `gather_generated`; rank 0 gates `distributed_metrics` on its
result:

```python
features, angles = gather_generated(shard_u8, device, rank, world_size)
if rank == 0 and angles is not None:
    scores = distributed_metrics(reference, angles, features, device=device)
```

```{eval-rst}
.. module:: combra.metrics.distributed
.. currentmodule:: combra

.. autosummary::
   :toctree: generated/
   :nosignatures:

   metrics.self_test
   metrics.distributed.precompute_reference
   metrics.distributed.gather_generated
   metrics.distributed.distributed_metrics
   io.write_hparams
```

(api-alternative)=
## Alternative angle methods

The method combra used before 0.15 and the candidate that may replace the
current one. Both take the same image and return the same
`(angles, polygons)` pair as {py:func}`combra.angles.vertex_angles`.

```{eval-rst}
.. module:: combra.legacy
.. module:: combra.experimental
.. currentmodule:: combra

.. autosummary::
   :toctree: generated/
   :nosignatures:

   legacy.vertex_angles
   experimental.vertex_angles
```

(api-errors)=
## Errors

Every error combra raises derives from `CombraError`, and each also derives
from the built-in exception it logically is, so an existing
`except ValueError` keeps working.

```{eval-rst}
.. module:: combra.exceptions
.. currentmodule:: combra

.. autosummary::
   :toctree: generated/
   :nosignatures:

   exceptions.CombraError
   exceptions.SchemaError
```
