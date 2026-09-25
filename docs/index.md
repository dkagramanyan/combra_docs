# combra documentation

**Version**: {{ release }}

**Useful links**:
{doc}`Installation <getting_started/installation>` |
[Source repository](https://github.com/dkagramanyan/combra) |
[Issue tracker](https://github.com/dkagramanyan/combra/issues) |
{doc}`Citing combra <getting_started/citing>`

combra measures the geometry of **WC-Co composite-alloy microstructures** in
SEM images — vertex angles of the cobalt pools, grain beams, fractal dimension,
crack paths — and scores generated microstructures against real ones.

```{doctest}
:hide:

>>> import combra
>>> combra.__version__
'0.18.0'
```

::::{grid} 1 2 2 2
:gutter: 4

:::{grid-item-card} Getting started
:link: getting_started/quickstart
:link-type: doc
:class-card: combra-module-card

New to combra? The quickstart extracts the angles of one bundled image and
writes a parquet for a whole dataset.
:::

:::{grid-item-card} User guide
:link: user_guide/index
:link-type: doc
:class-card: combra-module-card

What combra measures and why: the angle density, its bimodal fit, beams, and
how a generated microstructure is compared with a real one.
:::

:::{grid-item-card} API reference
:link: api/index
:link-type: doc
:class-card: combra-module-card

The public functions, module by module, with their parameters, returns and
examples.
:::

:::{grid-item-card} Developer guide
:link: development/index
:link-type: doc
:class-card: combra-module-card

How combra and these docs are tested, and the conventions a docstring
follows.
:::

::::

```{toctree}
:maxdepth: 1
:hidden:

user_guide/index
api/index
examples/index
models/index
development/index
release_notes
```
