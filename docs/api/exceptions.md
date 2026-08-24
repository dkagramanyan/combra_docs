# combra.exceptions

```{eval-rst}
.. module:: combra.exceptions
.. currentmodule:: combra.exceptions
```

combra's typed error and warning hierarchy. Every error the library raises
derives from {py:class}`~combra.exceptions.CombraError`, so one `except` catches
all of them; each concrete error also derives from the built-in exception it
logically is — {py:class}`ValueError` for a malformed file — so an existing
`except ValueError` keeps working. The warnings sit under
{py:class}`~combra.exceptions.CombraWarning`, itself a `UserWarning`, so the
usual {py:mod}`warnings` filters apply.

```python
from combra import exceptions
```

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   CombraError
   SchemaError
   IncompleteShardError
   CombraWarning
   UnknownFormatWarning
```

## See also

- {doc}`combra.io <io>` — raises {py:class}`~combra.exceptions.SchemaError` on a
  parquet predating the current schema.
- {doc}`combra.data <data>` — raises
  {py:class}`~combra.exceptions.IncompleteShardError` on a crashed generation
  run and emits {py:class}`~combra.exceptions.UnknownFormatWarning` on an
  unrecognized HDF5 `format` attribute.
