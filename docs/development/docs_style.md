# Documentation style

combra's documentation follows the conventions of the scientific-Python stack —
NumPy, SciPy, scikit-image — in an **academic short** register: a reference entry
states what a function computes, names its parameters, gives the mathematics in a
*Notes* section, cites the literature, and ends with an example that runs. It does
not narrate.

This page is the contract. Everything under {doc}`../api/data` is expected to
follow it; the user guide and the model pages follow the looser rules in
[Registers](#registers).

## Registers

Three registers, and the distinction matters more than any individual rule.

Reference
: `api/**` — generated from docstrings in the combra source. Terse, impersonal,
  complete. One entry per object. No narrative, no history, no "this is the first
  thing every fit calls". If a fact is about *how the library fits together*
  rather than *what this object does*, it belongs in the user guide.

User guide
: `user_guide/**` — explains concepts across objects: what an angle density is,
  why the Gaussian metrics go undefined, how an N-sweep is read. Prose is allowed
  to connect things and to motivate, but stays economical. Cross-links into the
  reference for signatures rather than repeating them.

Project pages
: `models/**`, `release_notes.md` — describe an evolving system rather than a
  fixed API. History, rationale, and dated notes are legitimate here.

## The reference entry

Docstrings are [numpydoc](https://numpydoc.readthedocs.io/en/latest/format.html)
format. Sections appear in this order, and only those that carry content:

```
Summary line.

Extended summary.

Parameters
Returns
Yields
Raises
See Also
Notes
References
Examples
```

Rules:

1. **Summary** — one sentence, imperative mood ("Compute…", "Fit…", "Extract…"),
   on the line after the opening quotes, ending in a period. Not "Computes", not
   "This function computes".
2. **Extended summary** — at most two sentences, and only when the summary leaves
   a real question. Most entries do not need one.
3. **Parameters** — every parameter, in signature order, `name : type` with the
   description indented beneath. Optional parameters read
   `name : type, optional` and state the default in the description as
   `Default is ``5.0``.` Do not restate defaults already visible in the
   signature unless the behaviour of the default is non-obvious.
4. **Returns** — name and type for each return value. A tuple return documents
   each element separately.
5. **Raises** — only exceptions the caller is expected to handle.
6. **See Also** — sibling functions, the inverse operation, the higher-level
   entry point. One line each.
7. **Notes** — the mathematics, the algorithm, the numerical caveats. This is
   where formulas live; never in the summary or a parameter description.
8. **References** — numbered `[1]_` entries for published algorithms. Any
   function implementing something from the literature cites it.
9. **Examples** — see [Examples](#examples) below.

Docstrings containing LaTeX must be raw strings (`r"""`), or every backslash is a
bug.

## Prose

- Third person, present tense, no "we" and no "you" in reference text. The user
  guide may address the reader directly.
- No narrative connectives in the reference: not "note that", "as mentioned
  above", "it turns out that".
- No history. What a function used to do belongs in {doc}`../release_notes`.
- Prefer the precise term to the friendly one — *quantize*, *normalize*,
  *degenerate* — and define it once in the {doc}`../user_guide/glossary`.
- British/American spelling: **American** (`normalize`, `centre` → `center`),
  matching NumPy.

## Math

- Inline math with `$…$`, display math with `$$…$$`. Both are rendered by
  MathJax through MyST's `dollarmath` extension.
- **Multi-letter names are not variables.** Write `\mathrm{amp}`,
  `\operatorname{tr}`, `\mathrm{MVEE}` — never `$amp$`, which renders as the
  product $a \cdot m \cdot p$.
- Define every symbol used, at first use, in the same Notes section.
- A formula that is only a restatement of the prose adds nothing. Include math
  when it is the precise statement, not as decoration.

## Examples

Every public function has at least one example, and **an example either runs or
is not written as a session**.

- Runnable examples are written as doctests and executed in CI
  (`sphinx -b doctest`). In MyST that means a ```` ```{doctest} ```` fence — a
  plain ```` ```pycon ```` fence is a literal block the doctest builder cannot
  see.
- Examples that cannot run standalone — because they need a trained checkpoint,
  a GPU, or a multi-gigabyte dataset — are written as ```` ```pycon ```` and must
  be recognisable as illustrations: name the missing inputs (`real_batch`,
  `checkpoint_path`) rather than implying they exist.
- Show output. An example whose last line produces a value should display it.
- Keep an example under fifteen lines. Longer belongs in {doc}`../examples/angles`.
- Import explicitly (`from combra import stats`) — no implicit names.

## Admonitions and emphasis

- `{warning}` is for a hazard that silently produces a wrong answer, or a
  removal. Not for emphasis, and not for history.
- `{note}` is for a fact a careful reader would want and would not guess.
- `{seealso}` for literature and cross-references.
- **Bold is rare.** If a paragraph has more than one bold span it has none.
- Nothing is written in capitals for emphasis.

## Cross-references and the glossary

- Link objects with `{py:func}`, `{py:class}`, `{py:meth}` — never bare code
  spans for names that exist.
- Link the first occurrence of a domain term on each page with `{term}` so it
  resolves to the {doc}`../user_guide/glossary`: `{term}`angle density``.
- Link pages with `{doc}`, using a path from the docs root for anything outside
  the current directory.

The build runs in **nitpicky** mode, so an unresolvable reference is an error
rather than silently-rendered plain text. Two consequences are worth knowing
before you write one.

### Constants live under their defining module

`combra`'s subpackages are `lazy_loader` stubs, so a module-level constant has no
usable `__module__`. `.. autodata:: SERIES_PALETTE` under
`.. currentmodule:: combra.viz` does not fail — it renders the *type's* docstring
("Built-in mutable sequence…"), which looks documented and is not. Point
`currentmodule` at the defining submodule for the constants block, then switch
back:

````
```{eval-rst}
.. currentmodule:: combra.viz.theme

.. autodata:: SERIES_PALETTE
   :no-value:

.. currentmodule:: combra.viz
```
````

`:no-value:` keeps a large repr (a pyarrow schema, say) out of the signature
line. Cross-references must then use the same defining path —
`` :data:`~combra.viz.theme.SERIES_PALETTE` `` — with `~` so the short name still
displays. Every constant also needs a PEP 258 attribute docstring: a string
literal on the line *after* the assignment.

### Module targets are declared, not implied

`.. currentmodule::` sets the context but creates no target, so `` :mod:`combra.fitting` ``
will not resolve. Each API page therefore declares its module once:

````
```{eval-rst}
.. module:: combra.fitting
.. currentmodule:: combra.fitting
```
````

## Version markers

`{versionadded}`, `{versionchanged}` and `{deprecated}` take a **release number**,
not a date:

````
```{versionchanged} 0.10.0
`class_names` is now required in generated HDF5 files.
```
````

The release number ties the marker to an entry in {doc}`../release_notes`; a date
does not.

## Checks

Three gates, all run by CI, all runnable locally:

```bash
python -m sphinx -b html -W --keep-going docs public   # 1. the build
python docs/check_api_coverage.py                      # 2. nothing undocumented
python -m sphinx -b doctest -W --keep-going docs _doctest   # 3. examples still run
```

1. **The build.** Warnings are errors, and nitpicky mode is on, so a broken
   cross-reference, an unknown role, a page missing from a toctree, or a
   reference to a name that no longer exists all fail it.
2. **Coverage.** autodoc makes a documented signature incapable of drifting from
   the code, but nothing forces a *newly added* public name to be listed on a
   page. `docs/check_api_coverage.py` compares each module's `__all__`
   against the names its page lists.
3. **Examples.** `sphinx -b doctest` runs the ```` ```{doctest} ```` blocks on
   these pages *and* the `Examples` sections of combra's docstrings, which
   autodoc pulls into the generated reference. Note that combra's own `pytest`
   does **not** collect docstring examples — this build is the only thing that
   does.
