# combra.graph

The `combra.graph` module turns a binarised crack image into a directed graph (`networkx.DiGraph`) whose nodes are contour vertices and whose edges are short straight segments classified as Co, WC-Co, WC, or WC-WC. From there you can run shortest-path / minimum-energy-path searches.

```python
from combra import graph
```

Edge type encoding:

| value | meaning |
| --- | --- |
| `0` | Co |
| `1` | WC-Co |
| `2` | WC |
| `3` | WC-WC |

## Build

````{py:function} combra.graph.extract_graph_nodes(image, r=2, border=30, border_node_eps=10, tol=5, disk=5, labeled_cnts=False, labels=False, entry_ellps_w=1, exit_ellps_w=1) -> tuple[list[int], list[int], ndarray, ndarray, list[ndarray], dict]

Median-filter, Otsu, and contour-extract the input. Pass ``labeled_cnts=True`` (and ``labels``) when you have hand-annotated contours and want to skip binarisation.

:param image: Source image (any channels).
:type image: ndarray
:param r: Marker radius for node visualisation. Default: ``2``.
:type r: int, optional
:param border: Padding added before extraction. Default: ``30``.
:type border: int, optional
:param border_node_eps: Max distance from border for a node to count as an entry/exit candidate. Default: ``10``.
:type border_node_eps: int, optional
:param tol: Douglas–Peucker tolerance. Default: ``5``.
:type tol: float, optional
:param disk: Median-filter footprint radius. Default: ``5``.
:type disk: int, optional
:param labeled_cnts: Skip binarisation; use ``labels`` directly. Default: ``False``.
:type labeled_cnts: bool, optional
:param labels: Hand-labelled contour data. Default: ``False``.
:type labels: ndarray or bool, optional
:param entry_ellps_w: Width of the entry ellipse region overlay. Default: ``1``.
:type entry_ellps_w: int, optional
:param exit_ellps_w: Width of the exit ellipse region overlay. Default: ``1``.
:type exit_ellps_w: int, optional
:returns: **entry_nodes** (*list[int]*) – Node indices on the entry side; and **exit_nodes** (*list[int]*) – Node indices on the exit side; and **img_preprocessed** (*ndarray*) – Binary preprocessed image (a copy used as the edge-drawing canvas). Returned third; and **img_contours_o** (*ndarray*) – RGB visualisation with contours and entry/exit nodes drawn. Returned fourth; and **cnts** (*list[ndarray]*) – Simplified contours; and **nodes_metadata** (*dict*) – Per-node lookup tables (global node coords, global/local contour indices, coord→index maps, and ``labels``/``contour_index2label`` when labelled).
:rtype: tuple(list[int], list[int], ndarray, ndarray, list[ndarray], dict)

**Example**

From ``wc_cv/graph_unlabeled.ipynb``:

```pycon
>>> from combra import graph, data
>>> image = data.load_microstructure().images[0]
>>> (entry_nodes, exit_nodes,
...  img_preprocessed, img_contours_o,
...  cnts, nodes_metadata) = graph.extract_graph_nodes(
...     image, border=30, disk=5, entry_ellps_w=5, exit_ellps_w=5, r=4,
... )
>>> print(f'{len(entry_nodes)} entry / {len(exit_nodes)} exit candidates')
```
````

````{py:function} combra.graph.build_crack_graph(img_shape, cnts, nodes_metadata, eps=100, line_eps=3, border=30, border_eps=0, border_number_min=2, border_pixel=255, same_node_eps=5, labels=False, labeled_line_eps=10, workers=10) -> tuple[networkx.DiGraph, ndarray]

Build the directed graph. ``eps`` is the maximum edge length in pixels; ``line_eps`` is the perpendicular tolerance used when classifying edges. Each edge carries ``edge_type`` and ``path_len``; ``weight`` and ``path_len_pixels`` are seeded from ``path_len`` so shortest-path searches work without a manual seeding loop.

:param img_shape: ``(H, W)`` of the source image.
:type img_shape: tuple[int, int]
:param cnts: Contours from ``extract_graph_nodes``.
:type cnts: list[ndarray]
:param nodes_metadata: Node lookup tables from ``extract_graph_nodes``.
:type nodes_metadata: dict
:param eps: Maximum edge length in pixels. Default: ``100``.
:type eps: int, optional
:param line_eps: Perpendicular tolerance used when classifying edges. Default: ``3``.
:type line_eps: int, optional
:param border: Image padding (must match ``extract_graph_nodes``). Default: ``30``.
:type border: int, optional
:param border_eps: Margin from image edge that excludes detections. Default: ``0``.
:type border_eps: int, optional
:param border_number_min: Minimum contour-border pixel count for an edge to count. Default: ``2``.
:type border_number_min: int, optional
:param border_pixel: Pixel value that marks a contour border. Default: ``255``.
:type border_pixel: int, optional
:param same_node_eps: Distance below which two candidate nodes are merged. Default: ``5``.
:type same_node_eps: int, optional
:param labels: Hand-labelled contour data. Default: ``False``.
:type labels: ndarray or bool, optional
:param labeled_line_eps: Perpendicular tolerance for the labelled-contour path. Default: ``10``.
:type labeled_line_eps: int, optional
:param workers: Worker count for edge enumeration. Default: ``10``.
:type workers: int, optional
:returns: **g** (*networkx.DiGraph*) – Built crack graph; and **img_contours** (*ndarray*) – Contour-overlay image with graph edges drawn.
:rtype: tuple(networkx.DiGraph, ndarray)

**Example**

```pycon
>>> from combra import graph, data
>>> img = data.load_crack()[0][1]
>>> (entry_nodes, exit_nodes,
...  img_preprocessed, img_contours_o,
...  cnts, nodes_metadata) = graph.extract_graph_nodes(
...     img, border=30, disk=5, entry_ellps_w=5, exit_ellps_w=5, r=4)
>>> g, img_contours = graph.build_crack_graph(
...     img_preprocessed.shape, cnts, nodes_metadata, eps=300)
>>> print(f'{g.number_of_nodes()} nodes, {g.number_of_edges()} edges')
```
````

````{py:function} combra.graph.find_edges(start_node_index, nodes_metadata, process_metadata) -> list[dict]

Compute outgoing edges from one node — used internally by ``build_crack_graph``. You normally don't need to call it directly.

:param start_node_index: Source node.
:type start_node_index: int
:param nodes_metadata: Node lookup tables.
:type nodes_metadata: dict
:param process_metadata: Internal builder state.
:type process_metadata: dict
:returns: **edges** (*list[dict]*) – Outgoing edges with classification metadata.
:rtype: list[dict]

**Example**

``find_edges`` is called inside ``build_crack_graph``; direct invocation is only useful when implementing a custom edge enumerator:

```pycon
>>> from combra import graph
>>> # process_metadata is the internal builder state — usually obtained by patching
>>> # build_crack_graph. For most use cases call build_crack_graph instead.
>>> edges = graph.find_edges(start_node_index=0,
...                         nodes_metadata=nodes_metadata,
...                         process_metadata=process_metadata)
```
````

````{py:function} combra.graph.classify_edge_geometric(node1, node2, cnts, nodes_metadata, wc_eps=30, border_pixel=0) -> int

Classify a single edge between two node indices into Co / WC-Co / WC / WC-WC.

:param node1: First node index.
:type node1: int
:param node2: Second node index.
:type node2: int
:param cnts: Contours.
:type cnts: list[ndarray]
:param nodes_metadata: Node lookup tables.
:type nodes_metadata: dict
:param wc_eps: Minimum contour-pixel count below which the edge is reclassified. Default: ``30``.
:type wc_eps: int, optional
:param border_pixel: Pixel value that marks a contour border. Default: ``0``.
:type border_pixel: int, optional
:returns: **edge_type** (*int*) – Edge-type code (0–3).
:rtype: int

**Example**

```pycon
>>> from combra import graph
>>> # 0=Co, 1=WC-Co, 2=WC, 3=WC-WC
>>> edge_type = graph.classify_edge_geometric(node1=0, node2=5,
...                                 cnts=cnts, nodes_metadata=nodes_metadata)
>>> print({0: 'Co', 1: 'WC-Co', 2: 'WC', 3: 'WC-WC'}[edge_type])
```
````

````{py:function} combra.graph.classify_edge_labeled(node1, node2, nodes_metadata, line_eps=10) -> int

Same as ``classify_edge_geometric`` but uses hand labels carried in ``nodes_metadata``. Use when you've labelled contours manually.

:param node1: First node index.
:type node1: int
:param node2: Second node index.
:type node2: int
:param nodes_metadata: Node lookup tables including ``labels``.
:type nodes_metadata: dict
:param line_eps: Perpendicular tolerance. Default: ``10``.
:type line_eps: int, optional
:returns: **edge_type** (*int*) – Edge-type code.
:rtype: int

**Example**

```pycon
>>> from combra import graph
>>> # Same code domain as classify_edge_geometric, but reads contour-class labels from
>>> # nodes_metadata instead of inferring from pixel values.
>>> edge_type = graph.classify_edge_labeled(node1=0, node2=5,
...                                         nodes_metadata=nodes_metadata,
...                                         line_eps=10)
```
````

````{py:function} combra.graph.remove_edges_of_type(g, edge_type) -> networkx.DiGraph

Drop every edge of a given ``edge_type`` (0=Co, 1=WC-Co, 2=WC, 3=WC-WC) from the graph, in place. Replaces the hand-written edge-filter + ``remove_edges_from`` in the crack notebooks; pass a ``copy.deepcopy`` to keep the original.

:param g: Crack graph from ``build_crack_graph``.
:type g: networkx.DiGraph
:param edge_type: Edge-type code to remove.
:type edge_type: int
:returns: **g** (*networkx.DiGraph*) – The same graph with matching edges removed.
:rtype: networkx.DiGraph

**Example**

```pycon
>>> import copy
>>> from combra import graph
>>> # remove WC (edge_type 2) edges from a working copy, keeping g intact
>>> g_cleaned = graph.remove_edges_of_type(copy.deepcopy(g), 2)
```
````

## Energies and paths

````{py:function} combra.graph.build_energy_grid(rows, cols, const, row_key=None, col_key=None) -> list[list[dict]]

Build the ``(rows, cols)`` edge-weight grid consumed by ``optimize_path_energies``. Every cell starts from ``const`` (a ``{edge_type: weight}`` dict); ``row_key`` / ``col_key`` override that edge type with the row / column index. Replaces the ``np.zeros((N, M)).tolist()`` + double-``for`` builders in the crack notebooks.

:param rows: Grid rows.
:type rows: int
:param cols: Grid columns.
:type cols: int
:param const: Fixed ``{edge_type: weight}`` entries applied to every cell (0=Co, 1=WC-Co, 2=WC, 3=WC-WC).
:type const: dict
:param row_key: Edge type swept along the rows (set to the row index). Default: ``None``.
:type row_key: int or None, optional
:param col_key: Edge type swept along the columns (set to the column index). Default: ``None``.
:type col_key: int or None, optional
:returns: **grid** (*list[list[dict]]*) – ``rows`` × ``cols`` grid of edge-weight dicts.
:rtype: list[list[dict]]

**Example**

```{doctest}
>>> from combra import graph
>>> # sweep WC-Co (rows) × WC-WC (cols), Co fixed at 10
>>> energy_conf = graph.build_energy_grid(20, 20, const={0: 10}, row_key=1, col_key=3)
>>> # a single fixed configuration
>>> base = graph.build_energy_grid(1, 1, const={0: 15, 1: 15, 2: 20, 3: 0})
```
````

````{py:function} combra.graph.optimize_path_energies(energy_conf, g, cnts, nodes_metadata, entry_nodes, exit_nodes, first_k_paths=2, parallel=False, workers=23, recalculate_paths=False) -> list[list[list[DataFrame]]]

Sweep an ``(N, M)`` grid of edge-type weights. For every grid cell, set the edge weights and run k-shortest-path between every (entry, exit) pair.

:param energy_conf: ``(N, M)`` grid where each cell is ``{0: co_e, 1: wc_co_e, 2: wc_e, 3: wc_wc_e}`` — edge-type weights at that grid point.
:type energy_conf: list[list[dict]]
:param g: Graph from ``build_crack_graph``.
:type g: networkx.DiGraph
:param cnts: Contours from ``build_crack_graph``.
:type cnts: list[ndarray]
:param nodes_metadata: Node lookup tables from ``build_crack_graph``.
:type nodes_metadata: dict
:param entry_nodes: Entry endpoint pool.
:type entry_nodes: list[int]
:param exit_nodes: Exit endpoint pool.
:type exit_nodes: list[int]
:param first_k_paths: ``k`` for Yen's k-shortest-path. Default: ``2``.
:type first_k_paths: int, optional
:param parallel: Use multiprocessing pool. Default: ``False``.
:type parallel: bool, optional
:param workers: Pool size when ``parallel=True``. Default: ``23``.
:type workers: int, optional
:param recalculate_paths: Force recompute even when a cached result exists. Default: ``False``.
:type recalculate_paths: bool, optional
:returns: **energies_paths** (*list[list[list[DataFrame]]]*) – Same shape as ``energy_conf``; each cell is a list of per-pair ``DataFrame``s.
:rtype: list[list[list[DataFrame]]]

**Example**

```pycon
>>> import numpy as np
>>> from combra import graph
>>> energy_conf = np.zeros((20, 20)).tolist()
>>> for i, en1 in enumerate(range(20)):       # Co weight
...     for j, en2 in enumerate(range(20)):   # WC-Co weight
...         energy_conf[i][j] = {0: en1, 1: en2, 2: 20, 3: 0}
>>> energies_paths = graph.optimize_path_energies(
...     energy_conf, g, cnts, nodes_metadata,
...     entry_nodes=[0, 1, 3], exit_nodes=[63, 64, 67],
...     first_k_paths=1, parallel=True, workers=20,
... )
```
````

````{py:function} combra.graph.find_shortest_energy_paths(G, cnts, nodes_metadata, entry_node, exit_node, k, recalculate_paths=False) -> pandas.DataFrame

Find the ``k`` shortest paths between one entry/exit pair and return per-path lengths, energies, and edge-type breakdowns.

:param G: Crack graph.
:type G: networkx.DiGraph
:param cnts: Contours.
:type cnts: list[ndarray]
:param nodes_metadata: Node lookup tables.
:type nodes_metadata: dict
:param entry_node: Entry endpoint.
:type entry_node: int
:param exit_node: Exit endpoint.
:type exit_node: int
:param k: Number of shortest paths to return.
:type k: int
:param recalculate_paths: Force recompute. Default: ``False``.
:type recalculate_paths: bool, optional
:returns: **df** (*pandas.DataFrame*) – One row per path with columns for total length, energy, and per-edge-type pixel fractions.
:rtype: pandas.DataFrame

**Example**

```pycon
>>> from combra import graph
>>> # Set edge weights on g first (or it will use defaults), then ask for the top-3.
>>> df = graph.find_shortest_energy_paths(
...     g, cnts, nodes_metadata,
...     entry_node=entry_nodes[0], exit_node=exit_nodes[0], k=3,
... )
>>> print(df[['path_len_pixel', 'energy_total']].head())
```
````

````{py:function} combra.graph.shortest_energy_paths_all_pairs(g, cnts, nodes_metadata, entry_nodes, exit_nodes, k=1) -> pandas.DataFrame

Collect the ``k`` shortest-energy paths for every ``(entry, exit)`` pair by calling ``find_shortest_energy_paths`` on each pair, skipping unconnected pairs, and concatenating. Replaces the hand-written double loop in the crack notebooks.

:param g: Weighted crack graph from ``build_crack_graph``.
:type g: networkx.DiGraph
:param cnts: Contours.
:type cnts: list[ndarray]
:param nodes_metadata: Node lookup tables.
:type nodes_metadata: dict
:param entry_nodes: Entry endpoint pool.
:type entry_nodes: list[int]
:param exit_nodes: Exit endpoint pool.
:type exit_nodes: list[int]
:param k: Shortest paths to keep per pair. Default: ``1``.
:type k: int, optional
:returns: **df** (*pandas.DataFrame*) – Concatenated path tables (see ``find_shortest_energy_paths``).
:rtype: pandas.DataFrame

**Example**

```pycon
>>> from combra import graph
>>> paths = graph.shortest_energy_paths_all_pairs(
...     g, cnts, nodes_metadata, entry_nodes, exit_nodes, k=1)
>>> shortest_entry = graph.shortest_paths_per_endpoint(paths, by='entry', k=1)
```
````

````{py:function} combra.graph.shortest_paths_per_endpoint(df, by='entry', k=1) -> pandas.DataFrame

Select the ``k`` shortest paths (by ``path_len_pixels``) for every entry — or exit — node in a path table. Replaces the per-endpoint ``groupby``/``sort`` loop hand-written in the crack notebooks.

:param df: Path table with ``entry_node``, ``exit_node`` and ``path_len_pixels`` columns (e.g. from ``find_shortest_energy_paths``).
:type df: pandas.DataFrame
:param by: Group by the entry node (``'entry'``) or the exit node (``'exit'``). Default: ``'entry'``.
:type by: str, optional
:param k: Number of shortest paths to keep per node. Default: ``1``.
:type k: int, optional
:returns: **df** (*pandas.DataFrame*) – The selected rows, sorted within each node by ``path_len_pixels``.
:rtype: pandas.DataFrame

**Example**

```pycon
>>> from combra import graph
>>> shortest_entry = graph.shortest_paths_per_endpoint(df, by='entry', k=1)
>>> shortest_exit = graph.shortest_paths_per_endpoint(df, by='exit', k=1)
```
````

````{py:function} combra.graph.evaluate_path_energies(g, cnts, nodes_metadata, entry_nodes, exit_nodes, workers=23, base_weights=None, sweep_rows=20, sweep_cols=20, parallel=True, first_k_paths=1) -> list[list[list[DataFrame]]]

Compute energies along a fixed set of paths (no optimisation).

:returns: **energies_paths_recalculated** (*list[list[list[DataFrame]]]*) – Per-grid-cell lists of fixed-path ``DataFrame``s.
:rtype: list[list[list[DataFrame]]]

**Example**

```pycon
>>> from combra import graph
>>> # Use when you already have a fixed entry/exit-pair list and want their
>>> # energies without enumerating k-shortest paths from scratch.
>>> energies = graph.evaluate_path_energies(
...     g, cnts, nodes_metadata,
...     entry_nodes=[0, 1, 3], exit_nodes=[63, 64, 67], workers=8,
... )
```
````

````{py:function} combra.graph.all_simple_paths_within_radius(g, epsilon=100, cutoff=10, workers=23) -> pandas.DataFrame

Pair each node with every other node within ``epsilon`` pixels, then enumerate all simple paths (up to ``cutoff`` edges) for each pair across a worker pool. Replaces the ``find_paths`` closure and node-pairing block hand-written in the crack notebooks.

:param g: Weighted crack graph from ``build_crack_graph`` (edges carry ``weight``).
:type g: networkx.DiGraph
:param epsilon: Maximum pixel distance for two nodes to be paired. Default: ``100``.
:type epsilon: int, optional
:param cutoff: Maximum edges per enumerated path. Default: ``10``.
:type cutoff: int, optional
:param workers: Worker-process count. Default: ``23``.
:type workers: int, optional
:returns: **df** (*pandas.DataFrame*) – One row per path with ``path``, ``path_len_edges``, ``path_len_pixels``, ``entry_node`` and ``exit_node``.
:rtype: pandas.DataFrame

**Example**

```pycon
>>> from combra import graph
>>> df = graph.all_simple_paths_within_radius(g, epsilon=100, cutoff=10, workers=23)
>>> graph.plot_path_length_distribution(df['path_len_pixels'], 'all_pixels.jpg')
```
````

````{py:function} combra.graph.enumerate_simple_paths(g, entry_nodes, exit_nodes, workers=23) -> list

Internal queue-based path enumerator — enumerates all simple paths for every ``(entry, exit)`` pair across a worker pool.

:param g: Crack graph.
:type g: networkx.DiGraph
:param entry_nodes: Entry endpoint pool to pair up.
:type entry_nodes: list[int]
:param exit_nodes: Exit endpoint pool to pair up.
:type exit_nodes: list[int]
:param workers: Pool size. Default: ``23``.
:type workers: int, optional
:returns: **results** (*list*) – Flattened per-pair path enumeration results.
:rtype: list

**Example**

``enumerate_simple_paths`` is an internal helper used by ``optimize_path_energies`` to multiplex (entry, exit) pairs across workers. Call ``optimize_path_energies`` directly — it sets up the queue for you.
````

## Plotting

````{py:function} combra.graph.plot_graph(g, img_contours=None, node_size=12, edge_width=2, color_dict=None, edge_width_dict=None, save_path=None) -> plotly.graph_objects.Figure

Interactive Plotly plot of the graph overlaid on ``img_contours``.

:param g: Graph to plot.
:type g: networkx.DiGraph
:param img_contours: Background image. Default: ``None``.
:type img_contours: ndarray or None, optional
:param node_size: Plotly marker size. Default: ``12``.
:type node_size: int, optional
:param edge_width: Default edge line width. Default: ``2``.
:type edge_width: int, optional
:param color_dict: ``{edge_type: color}``. Default: ``None``.
:type color_dict: dict or None, optional
:param edge_width_dict: ``{edge_type: width}``. Default: ``None``.
:type edge_width_dict: dict or None, optional
:param save_path: Write the figure here. Default: `None` (nothing is written).
:type save_path: str or Path or None, optional
:returns: **fig** (*plotly.graph_objects.Figure*) – The assembled graph figure.
:rtype: plotly.graph_objects.Figure

**Example**

```pycon
>>> graph.plot_graph(g, img_contours=img_contours, name='crack.html', save=True)
```
````

````{py:function} combra.graph.plot_optimized_energies(energies, path_index=0, n_rows=6, n_cols=6, y_label='co_co_e', x_label='wc_co_e', fixed_paths=False, fontsize_h=10, fontsize_axes=30, save_path=None, show=True) -> matplotlib.figure.Figure

Heatmap of optimal path energies over the ``(Co, WC-Co)`` weight grid for path index ``path_index``.

:param energies: Output of ``optimize_path_energies``.
:type energies: list[list[list[DataFrame]]]
:param path_index: Path rank to plot. Default: ``0``.
:type path_index: int, optional
:param n_rows: Subplot grid dimensions. Default: `6`.
:type n_rows: int, optional
:param n_cols: Subplot grid dimensions. Default: `6`.
:type n_cols: int, optional
:param y_label: Y-axis label. Default: ``'co_co_e'``.
:type y_label: str, optional
:param x_label: X-axis label. Default: ``'wc_co_e'``.
:type x_label: str, optional
:param fixed_paths: Read cells as fixed-path results (output of ``evaluate_path_energies``) instead of optimised k-shortest paths. Default: ``False``.
:type fixed_paths: bool, optional
:param fontsize_h: Heatmap annotation font size. Default: ``10``.
:type fontsize_h: int, optional
:param fontsize_axes: Axis label font size. Default: ``30``.
:type fontsize_axes: int, optional
:param save_path: Write the figure here. Default: `None` (nothing is written).
:type save_path: str or Path or None, optional
:param show: Display the figure. Default: `True`.
:type show: bool, optional
:returns: The figure is displayed (and optionally saved).
:rtype: matplotlib.figure.Figure

**Example**

```pycon
>>> from combra import graph
>>> # energies_paths from a 20x20 (Co × WC-Co) weight grid
>>> graph.plot_optimized_energies(
...     energies_paths, path_index=0, N=20, M=20,
...     y_label='co_co_e', x_label='wc_co_e',
... )
```
````

````{py:function} combra.graph.plot_paths(g, df, img_aligned, border=30, save_path=None, show=True) -> matplotlib.figure.Figure

Overlay the paths in ``df`` (output of ``find_shortest_energy_paths``) on the background image.

:param g: Graph.
:type g: networkx.DiGraph
:param df: Path table.
:type df: pandas.DataFrame
:param img_aligned: Background image.
:type img_aligned: ndarray
:param border: Padding to compensate for. Default: ``30``.
:type border: int, optional
:param save_path: Write the figure here. Default: `None` (nothing is written).
:type save_path: str or Path or None, optional
:param show: Display the figure. Default: `True`.
:type show: bool, optional
:returns: The figure is displayed.
:rtype: matplotlib.figure.Figure

**Example**

```pycon
>>> from combra import graph
>>> df = graph.find_shortest_energy_paths(
...     g, cnts, nodes_metadata,
...     entry_node=entry_nodes[0], exit_node=exit_nodes[0], k=3,
... )
>>> graph.plot_paths(g, df, img_aligned=img_contours_o, border=30)
```
````

````{py:function} combra.graph.plot_optimized_paths(g, energies_paths, img_contours_o, param_1=10, param_2=10, save_path=None, show=True) -> matplotlib.figure.Figure

Overlay the energy-optimised paths from ``optimize_path_energies`` on the contour image at grid position ``(param_1, param_2)``.

:param g: Graph.
:type g: networkx.DiGraph
:param energies_paths: Output of ``optimize_path_energies``.
:type energies_paths: list[list[list[DataFrame]]]
:param img_contours_o: Background image.
:type img_contours_o: ndarray
:param param_1: Grid row coordinate to draw. Default: ``10``.
:type param_1: int, optional
:param param_2: Grid column coordinate to draw. Default: ``10``.
:type param_2: int, optional
:param save_path: Write the figure here. Default: `None` (nothing is written).
:type save_path: str or Path or None, optional
:param show: Display the figure. Default: `True`.
:type show: bool, optional
:returns: The figure is displayed.
:rtype: matplotlib.figure.Figure

**Example**

```pycon
>>> from combra import graph
>>> # Cell (10, 10) in a 20x20 (Co × WC-Co) weight grid → draw the best path there.
>>> graph.plot_optimized_paths(g, energies_paths, img_contours_o, param_1=10, param_2=10)
```
````

````{py:function} combra.graph.plot_path_length_distribution(data, title=False, bins=60, xlim=None, save_path=None, show=True) -> matplotlib.figure.Figure

Histogram of crack-path lengths with vertical markers at the mean and ±1σ / ±2σ, plus a legend reporting count, mean and std. Replaces the ``plot_path_length_distribution`` helper hand-written in the crack notebooks.

:param data: Path-length values to histogram.
:type data: array-like
:param title: Plot title; falsy for none. Default: ``False``.
:type title: str or bool, optional
:param bins: Histogram bins. Default: ``60``.
:type bins: int, optional
:param xlim: ``(low, high)`` x-axis limits. Default: ``None``.
:type xlim: tuple or None, optional
:param save_path: Write the figure here. Default: `None` (nothing is written).
:type save_path: str or Path or None, optional
:param show: Display the figure. Default: `True`.
:type show: bool, optional
:returns: The figure that was drawn; written to disk when `save_path` is given.
:rtype: matplotlib.figure.Figure

**Example**

```pycon
>>> from combra import graph
>>> df = graph.all_simple_paths_within_radius(g, epsilon=100)
>>> graph.plot_path_length_distribution(df['path_len_pixels'], title='all paths')
```
````

````{py:function} combra.graph.draw_skeleton(img, centres=False, leafs=False, nodes=False, bones=False) -> ndarray

Render skeleton landmarks (centres / leaves / nodes / skeleton pixels) onto a binary image.

:param img: Binary input.
:type img: ndarray
:param centres: Draw centre landmarks. Default: ``False``.
:type centres: bool, optional
:param leafs: Draw leaf landmarks. Default: ``False``.
:type leafs: bool, optional
:param nodes: Draw node landmarks. Default: ``False``.
:type nodes: bool, optional
:param bones: Draw skeleton pixels. Default: ``False``.
:type bones: bool, optional
:returns: **rendered** (*ndarray*) – Annotated image.
:rtype: ndarray

**Example**

```pycon
>>> import cv2
>>> from combra import graph, data
>>> img = data.load_microstructure().images[0]
>>> _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
>>> annotated = graph.draw_skeleton(binary, centres=True, nodes=True, bones=True)
```
````

## Energy weights

````{py:class} combra.graph.EnergyWeights(co, wc_co, wc, wc_wc)

Per-phase edge energies for the crack-path search.

combra labels every graph edge with the phase it crosses, and the
shortest-energy search weights an edge by the energy of its phase. This named
tuple replaces the historical `param_1 … param_4` positional arguments; field
order is unchanged, so `EnergyWeights(15, 15, 20, 0)` is the old
`param_1=15, param_2=15, param_3=20, param_4=0`.

:param co: Energy of a Co (binder) edge — historical `param_1`.
:type co: float
:param wc_co: Energy of a WC-Co (interface) edge — historical `param_2`.
:type wc_co: float
:param wc: Energy of a WC (carbide) edge — historical `param_3`.
:type wc: float
:param wc_wc: Energy of a WC-WC (grain-boundary) edge — historical `param_4`.
:type wc_wc: float

````{py:method} as_dict() -> dict[int, float]
The `{edge_type: weight}` mapping the solver consumes, i.e.
`{0: co, 1: wc_co, 2: wc, 3: wc_wc}`.
````

**Example**

```{doctest}
>>> from combra.graph import EnergyWeights, evaluate_path_energies
>>> base = EnergyWeights(co=15, wc_co=15, wc=20, wc_wc=0)
>>> sweep = EnergyWeights(co=20, wc_co=20, wc=20, wc_wc=0)   # 20x20 Co x WC-Co grid
>>> base.as_dict()
{0: 15, 1: 15, 2: 20, 3: 0}
```
````

## See also

- {doc}`combra.contours <contours>` — the contour extractor `extract_graph_nodes` uses internally.
- {py:func}`combra.image.bresenham_line` and friends — the geometry kernels the edge-classifier calls.
