# combra_docs — todo

Problems found while building the `run-combra-docs` skill (2026-07-21).

- [x] **`sphinx_design` is declared but unused.** Resolved 2026-08-18: it *is* used
  now — `docs/index.md` builds the module overview from a `{grid}` of
  `{grid-item-card}`s, so the dependency earns its place.

- [x] **Docs build is fragile without network.** Resolved 2026-08-20:
  `docs/constraints.txt` pins the exact transitive closure of the five direct docs
  deps (34 packages, markers evaluated for this platform), and CI installs with
  `-r docs/requirements.txt -c docs/constraints.txt` — `requirements.txt` declares
  only floors, so without the constraints CI silently drifted to whatever PyPI
  served that day. Both files are now pip-cache keys in the workflow. A wheelhouse
  was not committed; the pins make one reproducible on demand.

  Original report: Building requires installing
  the Sphinx toolchain from PyPI; there is no vendored/offline path. On a machine
  without network access, deps must be recovered from pip's wheel cache (see the
  offline recovery in `.claude/skills/run-combra-docs/SKILL.md` Troubleshooting).

- [x] **The API-drift check never gated the build.** Resolved 2026-08-18:
  `docs/check_api_drift.py` skipped itself whenever combra was not importable, and CI
  ran on Python 3.11 without installing combra, so it *always* skipped. CI now runs on
  3.12 and installs combra when a `COMBRA_TOKEN` secret is present, flipping
  `COMBRA_DRIFT_STRICT=1` in that case. Without the secret it still skips, so a fork's
  PR builds. **Set `COMBRA_TOKEN` in the repository secrets to arm it** — this is the
  check whose absence let combra 0.5.0 remove three functions the four model repos
  import with nothing noticing.

- [x] **`sphinx.ext.doctest` cannot see the examples — the extension is dead weight.**
  Resolved 2026-08-20. The collector was right, the *fence* was wrong: a MyST
  ```` ```pycon ```` block becomes a `literal_block`, and the doctest builder collects
  nodes carrying `testnodetype` (`sphinx/ext/doctest.py`), which only the
  ```` ```{doctest} ```` directive sets. Converting the runnable examples to that
  directive takes the builder from **0 tests** to **74 tests, 0 failures**, and CI now
  runs `-b doctest` (gated on `COMBRA_TOKEN`, like the drift check). Verified armed,
  not vacuous: breaking one example makes sphinx exit 1.

  **The "20 of 20 files failing" figure in the original report was not real.**
  `pytest --doctest-glob='*.md'` does not understand markdown fences — it reads the
  closing ` ``` ` as expected output. The honest measurement, running each file's blocks
  in one namespace in order: **113 blocks, 25 pass, 88 fail**. Of the failures, **41 are
  `NameError` on names that were never defined** (`real_batch`, `dpmpp_fn`,
  `reference_images`, …) — those blocks are illustrative prose with prompts and can
  never run, so they keep the plain `pycon` fence and are never collected. 21 blocks
  pass standalone; those carry the directive.

  Real bugs the measurement surfaced, now fixed: `api/ellipse.md` still imported
  `combra.mvee` (renamed `combra.ellipse` in **0.6**) and called `plot_angles`
  (renamed `plot_beam_orientations`) with `save_name` / `N` / `M` / `save` arguments
  that no longer exist; `api/image.md` called `image.resize` (it is `resize_folder`)
  and passed tuples to `segments_intersect`, which needs arrays.

  One example is deliberately **not** collected even though it runs: the
  `optimize_path_energies` example in `api/graph.md` sweeps a 20×20 energy grid
  × 9 entry/exit pairs of Yen's k-shortest-path and did not finish in 5 minutes.
  It is a research computation, not a CI step.

  Original report:
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
