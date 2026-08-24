# combra.graph

```{eval-rst}
.. module:: combra.graph
.. currentmodule:: combra.graph
```

Crack propagation through a WC-Co microstructure, modeled as a search on a
graph. A binarized SEM image is reduced to its contours, every contour vertex
becomes a node, and short straight segments between nodes become directed edges
typed by the phase they cross. A crack is then a shortest path from the top of
the image to the bottom, under edge weights that price each phase.

```python
from combra import graph
```

Every edge carries an `edge_type` code, and each energy in an
{py:class}`~combra.graph.EnergyWeights` weights the matching one:

| value | phase | meaning |
| --- | --- | --- |
| `0` | Co | the binder |
| `1` | WC-Co | a carbide/binder interface |
| `2` | WC | the interior of a carbide grain |
| `3` | WC-WC | a carbide grain boundary |

## Build

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   extract_graph_nodes
   build_crack_graph
   find_edges
   classify_edge_geometric
   classify_edge_labeled
   remove_edges_of_type
```

## Energies and paths

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   build_energy_grid
   optimize_path_energies
   evaluate_path_energies
   find_shortest_energy_paths
   shortest_energy_paths_all_pairs
   shortest_paths_per_endpoint
   all_simple_paths_within_radius
   enumerate_simple_paths
```

## Plotting

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   plot_graph
   plot_paths
   plot_optimized_paths
   plot_optimized_energies
   plot_path_length_distribution
   draw_skeleton
```

## Energy weights

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   EnergyWeights
```

## See also

- {doc}`combra.contours <contours>` — the contour extractor
  {py:func}`~combra.graph.extract_graph_nodes` uses internally.
- {py:func}`combra.image.bresenham_line` and friends — the geometry kernels the
  edge classifiers call.
- {doc}`combra.data <data>` — {py:func}`~combra.data.load_crack` and
  {py:func}`~combra.data.load_crack_contours` supply the bundled crack image and
  its hand-labeled contours.
