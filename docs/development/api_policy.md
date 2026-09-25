# API stability and deprecation

What combra promises about its public API between releases, how a function is
retired, and where a breaking change is announced. The policy follows the
scientific-Python stack: the stability labels of NumPy and SciPy, and the
deprecation cycle of scikit-learn and scikit-image.

## What is public

The public API is the set of objects listed on the {doc}`/api/index` pages.
combra exports more — the stages its pipelines run internally, helpers, result
containers and constants — and those can change or disappear without notice,
even though their names carry no leading underscore. Anything with a leading
underscore is private.

Each module carries one of three stability labels:

Stable
: Every module except `combra.experimental`. A breaking change goes through the
  deprecation cycle below where that is possible, and is always listed in the
  {doc}`/release_notes`.

Legacy
: `combra.legacy`, the angle method used before 0.15, kept to reproduce results
  extracted with it. It is stable in the same sense.

Experimental
: `combra.experimental`, a candidate angle method; its API and output may
  change without a deprecation period. A change is still listed in the release
  notes.

The output formats written by {py:mod}`combra.io` — the angle and beam parquet
schemas and the HDF5 image containers — are part of the stable API. A release
that changes them says whether existing files need regenerating.

## Version numbers

combra is in its `0.x` series, and version numbers read
`0.MINOR.PATCH`:

- A **patch** release (`0.16.0` → `0.16.1`) fixes bugs and does not break
  code or change output formats.
- A **minor** release (`0.16` → `0.17`) may break the stable API. Every break
  is listed under *Changed (breaking)* or *Removed* in the release notes.

Code that depends on combra should therefore pin a minor version,
`combra>=0.16,<0.17`, or an exact release.

## Deprecation

A stable function that is to be removed or replaced is first deprecated:

1. It is wrapped in the `combra.utils.deprecated` decorator, which takes the
   release it was deprecated in, the release it will be removed in and,
   optionally, the replacement:

   ```python
   from combra.utils import deprecated

   @deprecated("0.4.0", "0.18.0", alternative="combra.image.build_quadrant_dataset")
   def tile_images(input_folder, output_folder, split=3, rotate=False):
       ...
   ```

2. Every call then emits a {py:exc}`DeprecationWarning` that names the
   function, both releases and the replacement, and points at the calling
   line. The function's docstring gains a `.. deprecated::` note after its
   summary line, so its reference page shows it.

3. The deprecation is listed in the {doc}`/release_notes` of the release that
   introduces it.

4. The function is removed **two minor releases later** — deprecated in
   `0.16`, removed in `0.18` — and the removal is listed under *Removed*.

Python hides {py:exc}`DeprecationWarning` outside `__main__` by default;
pytest shows it in the warnings summary. To make every deprecated call in a
test suite fail instead:

```bash
pytest -W error::DeprecationWarning
```

A renamed argument or a changed default cannot always be deprecated without an
alias that outlives its purpose. Such a change is made in a minor release
without a deprecation period, as a *clean break*, and the release notes say so
at the top of that release; 0.16.0 is one (`show` defaults to `False`, `seed`
became `rng`).

```{note}
`combra.image.tile_images`, the example above, was superseded by
`build_quadrant_dataset` in 0.4.0, long before the decorator existed. It
started warning in 0.16.0 and is removed in 0.18.0, two minor releases after
the first warning.
```

## Announcing a change

A breaking change is announced in two places:

- the {doc}`/release_notes`, under *Changed (breaking)* or *Removed*, with the
  replacement or the new call;
- the docstring of every affected function, with a `versionchanged` marker
  naming the release, so the note is on the reference page itself:

  ```
  .. versionchanged:: 0.16.0
      ``show`` defaults to ``False``.
  ```

New functions and arguments carry `versionadded` in the same way. The markers
take a release number, never a date; see {doc}`docs_style`.
