# combra.legacy

```{eval-rst}
.. module:: combra.legacy
.. currentmodule:: combra.legacy
```

The previous angle method, P0, kept for reading and reproducing results
extracted before combra 0.15: a 5×5 median filter, Otsu's threshold folded with
its morphological gradient into one map, Canny contours, Douglas–Peucker at
tolerance 3 px, pruning of segments shorter than `min_segment_len`, and the
angle between the chords at every remaining vertex. New extractions use
{py:func}`combra.angles.vertex_angles`; against the exact truth of
{doc}`combra.synth <synth>` P0 recovers 12% of the true corners with an RMS
edge error of 1.26 px, P6 37% at 0.67 px.

```python
from combra import legacy
```

## Extraction

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   preprocess_image
   vertex_angles
   extract_polygons
```

## Output layout

The `_msl` folder naming of the P0 parquets.

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   output_directory
```

## See also

- {py:func}`combra.angles.vertex_angles` — the method that replaced this one.
- {py:meth}`combra.data.MicrostructureDataset.generate_beams` — the beam
  extraction still consumes the map `preprocess_image` builds.
