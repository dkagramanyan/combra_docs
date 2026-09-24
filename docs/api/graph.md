# Crack graph (combra.graph)

```{eval-rst}
.. module:: combra.graph
.. currentmodule:: combra.graph
```

Crack propagation modeled as a search on a graph: the contour vertices of a
cracked SEM image become nodes, short segments between them become edges typed
by the phase they cross, and a crack is a lowest-energy path from the top of
the image to the bottom.

```python
from combra import graph
```

## Building the graph

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   extract_graph_nodes
   build_crack_graph
```

## Energies and paths

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   EnergyWeights
   find_shortest_energy_paths
   build_energy_grid
   optimize_path_energies
```

## Plotting

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   plot_graph
   plot_paths
```
