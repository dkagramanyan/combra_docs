# combra

Computer-vision tools for analysis of **WC-Co composite-alloy microstructure SEM images** —
contour/angle extraction, MVEE beam fitting, fractal dimension, crack graphs, and
distribution metrics.

```pycon
>>> import combra
>>> combra.__version__
'0.6.0'
```

```{toctree}
:maxdepth: 1
:caption: Getting started
:hidden:

get_started
glossary
```

```{toctree}
:maxdepth: 1
:caption: Python API
:hidden:

api/data
api/image
api/contours
api/angles
api/ellipse
api/stats
api/fitting
api/metrics
api/graph
api/io
api/viz
api/exceptions
api/utils
api/validation
```

```{toctree}
:maxdepth: 1
:caption: Examples
:hidden:

examples/angles
examples/models_api
examples/san_v2
examples/styleswin
examples/diffit
examples/edm2
examples/sampler_comparison
```

```{toctree}
:maxdepth: 1
:caption: Design notes
:hidden:

examples/models_api_proposal
```

## The pipeline

SEM image → contours → per-vertex angles → a fitted distribution → a metric that
scores a generated microstructure against a real one.

::::{grid} 1 2 2 3
:gutter: 3

:::{grid-item-card} combra.data
:link: api/data
:link-type: doc
:class-card: combra-module-card

Datasets, bundled sample images, and the parquet writers
(`generate_angles`, `generate_beams`).
:::

:::{grid-item-card} combra.image
:link: api/image
:link-type: doc
:class-card: combra-module-card

Pixel preprocessing, box-counting fractal dimension, and the numba
geometry kernels.
:::

:::{grid-item-card} combra.contours
:link: api/contours
:link-type: doc
:class-card: combra-module-card

Raw and Douglas–Peucker-simplified polygon extraction, plus drawing.
:::

:::{grid-item-card} combra.angles
:link: api/angles
:link-type: doc
:class-card: combra-module-card

Per-image vertex-angle extraction, density plots and overlay grids.
:::

:::{grid-item-card} combra.ellipse
:link: api/ellipse
:link-type: doc
:class-card: combra-module-card

Minimum-volume enclosing ellipses (MVEE) and beam-length distributions.
:::

:::{grid-item-card} combra.stats
:link: api/stats
:link-type: doc
:class-card: combra-module-card

Parametric distributions, the density histogram, and inference helpers.
:::

:::{grid-item-card} combra.fitting
:link: api/fitting
:link-type: doc
:class-card: combra-module-card

Gaussian, bimodal-Gaussian, binomial, Poisson, exponential, linear and
plateau fits — one `fit_*` family, one result protocol.
:::

:::{grid-item-card} combra.metrics
:link: api/metrics
:link-type: doc
:class-card: combra-module-card

Angle-Wasserstein and bimodal-Gaussian comparison, image-feature metrics
(FID / CMMD / FD-DINOv2), sampler sweeps, and convergence-vs-N analysis.
:::

:::{grid-item-card} combra.graph
:link: api/graph
:link-type: doc
:class-card: combra-module-card

Crack image → directed graph → shortest-energy-path search.
:::

:::{grid-item-card} combra.io
:link: api/io
:link-type: doc
:class-card: combra-module-card

One parquet loader, the angle/beam schemas, HDF5 conversion, and
TensorBoard scalar reading.
:::

:::{grid-item-card} combra.viz
:link: api/viz
:link-type: doc
:class-card: combra-module-card

The shared plotting theme: palettes, axis style, PNG export.
:::

:::{grid-item-card} combra.utils · validation · exceptions
:link: api/utils
:link-type: doc
:class-card: combra-module-card

`Bunch` container, the fractal self-check, and the typed error hierarchy.
:::

::::

## API conventions

combra follows the conventions of the wider scientific-Python stack, so most of
the API should already be familiar.

Functions
: `verb_noun`, never `get_*` — `find_edges`, `fit_distribution`, `load_crack`,
  `build_crack_graph`, `plot_density`.

Results
: Anything returning more than two values returns a SciPy-style named tuple —
  {py:class}`~combra.fitting.BimodalGaussianFit`, {py:class}`~combra.ellipse.MveeResult`,
  {py:class}`~combra.graph.EnergyWeights`. They unpack positionally, so
  `curve, mus, sigmas, amps = fit_bimodal_gaussian(x, y)` works alongside `fit.mus`.

Plotting
: Every `plot_*` returns its figure and takes the same tail arguments —
  `save_path=None` (write a PNG) and `show=True` (render it). There is no
  `save=True` boolean and no separate filename argument.

Reference vs. generated
: Every comparison names its two sides `reference` and `generated`. Sample
  counts are `n`; figure geometry is `width`/`height` or `n_rows`/`n_cols`.

:::{seealso}
{doc}`glossary` defines the domain terms — angle density, beam, MVEE, `step`,
`kind`, N-sweep.
:::
