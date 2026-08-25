# Crack propagation as a graph

Turn a binarized crack image into a directed graph whose edges are classified by
the phase they cross, then search for the cheapest path a crack could take
through it.

This analysis is separate from the angle and beam descriptors: it asks where a
crack *would* go, rather than what the grain geometry looks like.

## Extracting nodes

{py:func}`combra.graph.extract_graph_nodes` skeletonizes the crack, finds the
contours of the surrounding grains, and identifies the nodes on the left and
right borders where a crack can enter and leave:

```{doctest}
>>> from combra import data, graph
>>> image = data.load_crack()[0][1][:400, :200]
>>> entry_nodes, exit_nodes, img_contours, preview, cnts, meta = (
...     graph.extract_graph_nodes(image, border=10, disk=3)
... )
>>> len(entry_nodes), len(exit_nodes), len(cnts)
(3, 2, 5)
```

`border` is how far from the image edge a node still counts as an entry or exit;
`disk` is the morphological radius used to close gaps in the traced crack.

## Building the graph

Nodes are contour vertices, and edges are short straight segments between them.
Each edge is classified by the phase it crosses:

| value | phase | meaning |
| --- | --- | --- |
| `0` | Co | the binder |
| `1` | WC-Co | a carbide/binder interface |
| `2` | WC | the interior of a carbide grain |
| `3` | WC-WC | a carbide grain boundary |

```{doctest}
>>> g, _ = graph.build_crack_graph(
...     img_contours.shape[:2], cnts, meta, eps=100, border=10, workers=1
... )
>>> g.number_of_nodes(), g.number_of_edges()
(27, 81)
>>> sorted(g[0][1])
['edge_type', 'path_len', 'path_len_pixels', 'weight']
```

`eps` bounds how far apart two nodes may be and still be joined by an edge.

## Weighting the phases

{py:class}`combra.graph.EnergyWeights` assigns an energy cost to each phase. The
values below make a crack prefer grain boundaries (`wc_wc=0`, free) over cutting
through a carbide (`wc=20`, expensive) — the transgranular-versus-intergranular
tradeoff:

```{doctest}
>>> weights = graph.EnergyWeights(co=15, wc_co=15, wc=20, wc_wc=0)
>>> weights.as_dict()
{0: 15, 1: 15, 2: 20, 3: 0}
```

## Finding the cheapest paths

{py:func}`~combra.graph.find_shortest_energy_paths` returns the `k` lowest-energy
routes between one entry and one exit node, with the per-phase breakdown of each:

```{doctest}
>>> paths = graph.find_shortest_energy_paths(
...     g, cnts, meta, entry_nodes[0], exit_nodes[0], k=2
... )
>>> paths['path_len_edges'].tolist()
[8, 9]
>>> paths['path_len_pixels'].tolist()
[453.11, 453.12]
```

Each row also carries `energy` and the per-phase edge counts and pixel lengths
(`co_edges`, `co_pixels`, and the equivalents for the other three phases), so a
path can be reported as how much of it ran through binder versus carbide.

To sweep a range of weightings instead of scoring one,
{py:func}`~combra.graph.build_energy_grid` builds the parameter grid and
{py:func}`~combra.graph.optimize_path_energies` searches it. See
{doc}`/api/graph` for the plotting helpers.
