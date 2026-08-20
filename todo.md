# combra_docs — todo

Problems found while building the `run-combra-docs` skill (2026-07-21).

- [x] **`sphinx_design` is declared but unused.** Resolved 2026-08-18: it *is* used
  now — `docs/index.md` builds the module overview from a `{grid}` of
  `{grid-item-card}`s, so the dependency earns its place.

- [ ] **Docs build is fragile without network.** Building requires installing
  the Sphinx toolchain from PyPI; there is no vendored/offline path. On a machine
  without network access, deps must be recovered from pip's wheel cache (see the
  offline recovery in `.claude/skills/run-combra-docs/SKILL.md` Troubleshooting).
  Consider committing a `docs/constraints.txt` (pinned versions) and/or a small
  wheelhouse so offline/CI builds are reproducible.

- [x] **The API-drift check never gated the build.** Resolved 2026-08-18:
  `docs/check_api_drift.py` skipped itself whenever combra was not importable, and CI
  ran on Python 3.11 without installing combra, so it *always* skipped. CI now runs on
  3.12 and installs combra when a `COMBRA_TOKEN` secret is present, flipping
  `COMBRA_DRIFT_STRICT=1` in that case. Without the secret it still skips, so a fork's
  PR builds. **Set `COMBRA_TOKEN` in the repository secrets to arm it** — this is the
  check whose absence let combra 0.5.0 remove three functions the four model repos
  import with nothing noticing.

- [ ] **`sphinx.ext.doctest` cannot see the examples — the extension is dead weight.**
  Found 2026-08-20. `conf.py` loads `sphinx.ext.doctest` and 118 blocks are correctly
  fenced as ```` ```pycon ````, but a MyST fenced block becomes a plain `literal_block`,
  never a `doctest_block`, so the doctest builder collects **nothing**:

  ```
  $ python -m sphinx -b doctest docs _out
  Doctest summary: 0 tests, 0 failures
  ```

  Adding `-b doctest` to CI would therefore pass vacuously — armed-looking and testing
  nothing, the same failure mode as the drift check that always skipped. A collector
  that *does* see them is `pytest --doctest-glob='*.md' docs`, and it currently reports
  **20 of 20 example-bearing files failing** (including `index.md`, whose first block
  claims `combra.__version__ == '0.6.0'` against the installed 0.7.1). Fixing those is
  its own task — either repair each example, mark the illustrative ones
  `# doctest: +SKIP`, or convert them to `{doctest}` directives. Do that first, then
  gate CI on it. Do **not** add the sphinx `-b doctest` step on its own.
