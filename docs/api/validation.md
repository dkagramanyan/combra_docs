# combra.validation

```{eval-rst}
.. module:: combra.validation
.. currentmodule:: combra.validation
```

Self-validation helpers shipped with combra. Each builds shapes whose answer is
known analytically and checks a combra estimator against them, which makes them
useful as a post-install sanity check on a new machine or a new build of the
numba and torch dependencies.

```python
from combra import validation
```

```{eval-rst}
.. autosummary::
   :toctree: generated/
   :nosignatures:

   check_fractal_dimension
```

## See also

- {doc}`combra.image <image>` — the box-counting estimator under test.
- {doc}`Installation </getting_started/installation>` — where this check fits in
  a post-install run-through.
