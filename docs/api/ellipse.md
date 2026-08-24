# combra.ellipse

```{eval-rst}
.. module:: combra.ellipse
.. currentmodule:: combra.ellipse
```

Minimum-volume enclosing ellipses for the contours of a microstructure image,
and the plotting helpers that read the resulting {term}`beam` distributions.
Each grain is reduced to two semi-axes and an orientation; see
{doc}`Beams and the MVEE </user_guide/beams>` for what those quantities mean and
how they are binned.

![Enclosed Ellipse](https://pobedit.s3.us-east-2.amazonaws.com/docs_images/enclosed-ellipse.png)

```python
from combra import ellipse
```

## Build

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   fit_mvee
```

## Plotting

Figures over per-sample beam records. Every one returns what it drew and writes
nothing to disk unless `save_path` is given.

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   plot_beam_lengths
   plot_beam_orientations
   plot_beam_compare
   plot_beam_heatmap
   plot_enclosing_ellipse
```

## Result types

SciPy-style named tuples (cf. `scipy.stats.linregress`): results carry attribute
names while staying unpacking-compatible with plain tuples.

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   MveeResult
   BeamComparison
```

## See also

- {doc}`Beams and the MVEE </user_guide/beams>` — why an enclosing ellipse, what
  `tol` does, and how beam lengths become physical units.
- {py:meth}`combra.data.MicrostructureDataset.generate_beams` — drives
  {py:func}`~combra.ellipse.fit_mvee` across whole class folders and writes
  parquet.
- {doc}`combra.fitting <fitting>` — supplies the straight-line fit the
  beam-length plots draw.
- {doc}`combra.contours <contours>` — extracts the contours the ellipses are
  fitted to.
