# combra.io

```{eval-rst}
.. module:: combra.io
.. currentmodule:: combra.io
```

The single home for combra's on-disk artifacts: the angle and beam **parquet**
files, the image **HDF5** containers, the parquet schemas and the `run_meta`
provenance block, and the readers for TensorBoard event logs. It follows the
`skimage.io` convention — one loader, one place.

```python
from combra import io
```

## Parquet loading

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   load_rows
```

## Schemas & provenance

The pyarrow schemas live here rather than inside the dataset class that writes
them, so writers and readers share one definition. Both hold one row per class,
with the per-step results nested under `prep_per_step` and the run provenance
duplicated on every row.

```{eval-rst}
.. currentmodule:: combra.io.schema

.. autodata:: ANGLES_SCHEMA
   :no-value:

.. autodata:: BEAMS_SCHEMA
   :no-value:

.. currentmodule:: combra.io
```

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   build_run_meta
```

## HDF5 conversion

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   convert_folder_to_hdf5
```

## TensorBoard logs

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   read_tb_scalars
   progress_fraction
```

## Hyperparameters

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   flatten_hparams
   write_hparams
```

## See also

- {py:class}`combra.data.MicrostructureDataset` — writes these parquets via
  `generate_angles` / `generate_beams`, and calls
  {py:func}`combra.io.convert_folder_to_hdf5` when handed a folder.
- {doc}`combra.metrics <metrics>` — consumes the rows this module loads.
- {doc}`combra.image <image>` — prepares the folder trees this packs into HDF5.
