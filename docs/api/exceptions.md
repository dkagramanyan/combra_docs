# Errors (combra.exceptions)

```{eval-rst}
.. module:: combra.exceptions
.. currentmodule:: combra.exceptions
```

Every error combra raises derives from `CombraError`, and each also derives from
the built-in exception it logically is, so an existing `except ValueError` keeps
working.

```python
from combra import exceptions
```

## Errors

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   CombraError
   SchemaError
```
