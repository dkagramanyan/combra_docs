# combra

Computer-vision tools for analysis of **WC-Co composite-alloy microstructure SEM images** —
contour/angle extraction, MVEE beam fitting, fractal dimension, crack graphs, and
distribution metrics.

```{doctest}
>>> import combra
>>> combra.__version__
'0.15.2'
```

```{toctree}
:maxdepth: 1
:caption: Getting started
:hidden:

getting_started/installation
getting_started/quickstart
```

```{toctree}
:maxdepth: 2
:caption: User guide
:hidden:

user_guide/index
```

```{toctree}
:maxdepth: 1
:caption: API reference
:hidden:

api/index
```

```{toctree}
:maxdepth: 1
:caption: Examples
:hidden:

examples/angles
examples/beams
examples/crack_graph
examples/metrics
examples/sampler_comparison
```

```{toctree}
:maxdepth: 1
:caption: Generative models
:hidden:

models/spec
models/san_v2
models/styleswin
models/diffit
models/edm2
```

```{toctree}
:maxdepth: 1
:caption: Development
:hidden:

development/testing
development/docs_style
release_notes
```

## The pipeline

SEM image → cobalt pools → sub-pixel polygons → per-vertex angles → a fitted
distribution → a metric that scores a generated microstructure against a real
one. The
{doc}`user guide <user_guide/index>` walks through each stage.

::::{grid} 1 2 2 3
:gutter: 3

:::{grid-item-card} Data
:link: api-data
:link-type: ref
:class-card: combra-module-card

Bundled sample images, the dataset that writes angle and beam parquets, and the readers for them.
:::

:::{grid-item-card} Measure an image
:link: api-measure
:link-type: ref
:class-card: combra-module-card

Vertex angles and their bimodal fit, enclosing ellipses (beams), fractal dimension.
:::

:::{grid-item-card} Compare real and generated
:link: api-compare
:link-type: ref
:class-card: combra-module-card

Angle and image-feature metrics, sampler sweeps, convergence with sample size.
:::

:::{grid-item-card} Plotting
:link: api-plotting
:link-type: ref
:class-card: combra-module-card

Angle densities, overlay grids, beam lengths, metric curves, crack paths.
:::

:::{grid-item-card} Crack graph
:link: api-crack-graph
:link-type: ref
:class-card: combra-module-card

Crack image → directed graph → lowest-energy crack paths.
:::

:::{grid-item-card} Method benchmark
:link: api-benchmark
:link-type: ref
:class-card: combra-module-card

Generated pools with an exact truth, and the score of an angle method against them.
:::

:::{grid-item-card} Training-loop integration
:link: api-training
:link-type: ref
:class-card: combra-module-card

The startup check and the sharded evaluation the model repositories call.
:::

:::{grid-item-card} Alternative angle methods
:link: api-alternative
:link-type: ref
:class-card: combra-module-card

The method used before 0.15, and the candidate that may replace the current one.
:::

:::{grid-item-card} Errors
:link: api-errors
:link-type: ref
:class-card: combra-module-card

The typed error hierarchy.
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
  `curve, mus, sigmas, shares, total = fit_bimodal_gaussian(x, y)` works alongside `fit.mus`.

Plotting
: Every `plot_*` returns its figure and takes the same tail arguments —
  `save_path=None` (write a PNG) and `show=True` (render it). There is no
  `save=True` boolean and no separate filename argument.

Reference vs. generated
: Every comparison names its two sides `reference` and `generated`. Sample
  counts are `n`; figure geometry is `width`/`height` or `n_rows`/`n_cols`.

:::{seealso}
{doc}`user_guide/glossary` defines the domain terms — angle density, beam, MVEE,
`step`, `kind`, N-sweep.
:::
