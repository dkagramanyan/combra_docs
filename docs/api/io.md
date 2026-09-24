# Input and output (combra.io)

```{eval-rst}
.. module:: combra.io
.. currentmodule:: combra.io
```

Readers and writers for combra's files: the angle and beam parquets, the image
HDF5 containers, and the TensorBoard record of a training run.

```python
from combra import io
```

## Parquet and HDF5

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   load_rows
   convert_folder_to_hdf5
```

## TensorBoard

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   write_hparams
```
