# API reference

This reference describes the functions, classes and modules a user of combra
calls. Each module page groups its functions by task and links to one page per
function.

## Public API

Only the objects listed on these pages are public. combra exports more — the
stages its pipelines run internally, helpers, result containers and constants
— and those can change or disappear without notice, even though their names
carry no leading underscore.

Stable
: Every module below except `combra.experimental`. A breaking change is listed
  in the {doc}`/release_notes`.

Legacy
: `combra.legacy`, the angle method used before 0.15, kept to reproduce results
  extracted with it.

Experimental
: `combra.experimental`, a candidate angle method; its API and output may
  change without a deprecation period.

## Modules

| Module | |
| --- | --- |
| {doc}`combra.data <data>` | Datasets that write angle and beam parquets; sample images |
| {doc}`combra.io <io>` | Parquet, HDF5 and TensorBoard input and output |
| {doc}`combra.angles <angles>` | Vertex angles, their density fit and plots; legacy and experimental methods |
| {doc}`combra.ellipse <ellipse>` | Minimum-volume enclosing ellipses and beam-length plots |
| {doc}`combra.image <image>` | Measures computed on an image |
| {doc}`combra.metrics <metrics>` | Real-vs-generated metrics, convergence, training-loop evaluation |
| {doc}`combra.graph <graph>` | Crack graph and lowest-energy crack paths |
| {doc}`combra.synth <synth>` | Generated pools with an exact truth and the method benchmark |
| {doc}`combra.exceptions <exceptions>` | Error types |

```{toctree}
:hidden:

data
io
angles
ellipse
image
metrics
graph
synth
exceptions
```

## Conventions

combra follows the conventions of the wider scientific-Python stack.

Functions
: `verb_noun`, never `get_*` — `load_crack`, `build_crack_graph`,
  `plot_density`.

Results
: Anything returning more than two values returns a SciPy-style named tuple.
  It unpacks positionally, so
  `a, b, angle_rad, centroid, contour = fit_mvee(image)` works alongside
  `result.a`.

Plotting
: Every `plot_*` returns its figure and takes the same tail arguments —
  `save_path=None` (write a PNG) and `show=True` (render it).

Reference vs. generated
: Every comparison names its two sides `reference` and `generated`, reference
  first. Sample counts are `n`; figure geometry is `width`/`height` or
  `n_rows`/`n_cols`.

:::{seealso}
{doc}`/user_guide/glossary` defines the domain terms — angle density, beam,
MVEE, `step`, `kind`, N-sweep.
:::
