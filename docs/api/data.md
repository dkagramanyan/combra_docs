# Datasets and sample data (combra.data)

```{eval-rst}
.. module:: combra.data
.. currentmodule:: combra.data
```

The dataset that runs combra's extraction over a folder tree of SEM images and
writes one parquet row per class, and the sample images shipped with the
package.

```python
from combra import data
```

## Datasets

{py:meth}`~combra.data.MicrostructureDataset.generate_angles` and
{py:meth}`~combra.data.MicrostructureDataset.generate_beams` are documented on
the class page.

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   MicrostructureDataset
   sweep_angles
```

## Sample data

Zero-argument loaders for the images under `combra/data/`, sized for examples
and smoke tests.

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   load_microstructure
   load_crack
```
