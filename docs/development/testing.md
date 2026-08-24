# Testing and linting

After a development install, the suite, the linter and the formatter run from the
combra repository root:

```bash
pip install -e ".[dev]"

pytest                           # run the test suite
ruff check combra tests          # lint
ruff format combra tests         # format
```

Two suites are deselected from a bare `pytest`, and therefore from CI, because
they are not pass/fail checks worth paying for on every push:

```bash
pytest -m slow                   # ~11 s: ground-truth check of the angle metrics
                                 # against synthetic images whose vertex angles
                                 # are known exactly. Run after touching the angle
                                 # pipeline, the bimodal fit, or the gauss metrics.

pytest -m visual -s              # writes interactive plotly HTML for inspection:
                                 # the bimodal-Gaussian fit on synthetic angle
                                 # data, and whether each fit was judged usable.
                                 # Paths are printed; COMBRA_VISUAL_DIR overrides
                                 # where they are written.
```

CI (GitHub Actions) runs the ruff lint and format checks, mypy on the
strict-typed core, and `pytest` on Python 3.12 and 3.13.

## Documentation

The documentation lives in a separate repository,
[combra_docs](https://github.com/dkagramanyan/combra_docs). Its build is the
test:

```bash
pip install -r docs/requirements.txt -c docs/constraints.txt
python -m sphinx -b html -W --keep-going -j auto docs public
```

`-W` turns every warning into an error, so a broken cross-reference, an unknown
role, or a page missing from a toctree fails the build. CI additionally runs the
runnable examples:

```bash
python -m sphinx -b doctest -W --keep-going docs _doctest
```

Before writing documentation, read {doc}`docs_style` — it fixes the register,
the docstring section order, and the rules for math and examples.

### The build needs combra installed

The API reference is generated from combra's docstrings, so the package must be
importable or there is no reference to render. Locally, `conf.py` finds a
checkout sitting next to the docs repository, and `COMBRA_SRC` overrides the
path:

```bash
export COMBRA_SRC=/path/to/combra
```

In CI this means the workflow installs combra from git before building. Because
combra is a **private** repository, that install needs a token: a fine-grained
personal access token with read access to `dkagramanyan/combra`, stored on the
`combra_docs` repository as the `COMBRA_TOKEN` secret
(*Settings → Secrets and variables → Actions → New repository secret*).

Without it the build fails immediately, by design. The alternative — carrying on
and publishing a site whose entire API reference is missing — is worse than a red
build, because it looks like a successful deploy.
