# combra.viz

```{eval-rst}
.. module:: combra.viz
.. currentmodule:: combra.viz
```

The plotting theme shared by every `combra.*` plot module: one categorical
palette, one axis style, one PNG export, so that a figure looks the same
whichever module drew it. plotly ships with the core install, so this module is
always importable.

```python
from combra import viz
```

## Styling and export

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   axis_style
   export_png
```

## Palettes and marker cycles

Module constants. Each is indexed modulo its length, so a figure with more
series than the cycle has entries repeats them.

```{eval-rst}
.. currentmodule:: combra.viz.theme

.. autodata:: SERIES_PALETTE

.. autodata:: METRIC_PALETTE

.. autodata:: MARKERS

.. autodata:: MARKER_GLYPHS

.. currentmodule:: combra.viz
```

## See also

- {doc}`combra.angles <angles>` — angle plots, styled from `SERIES_PALETTE`,
  `MARKERS` and `MARKER_GLYPHS`.
- {doc}`combra.metrics <metrics>` — metric plots, styled from
  `METRIC_PALETTE`.
