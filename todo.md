# combra_docs — todo

Problems found while building the `run-combra-docs` skill (2026-07-21).

- [ ] **`sphinx_design` is declared but unused.** It's listed in
  `docs/conf.py` `extensions` and required by `docs/requirements.txt`, but no
  page uses any of its directives (no `grid` / `card` / `dropdown` / `tab-set`).
  The build hard-fails if it isn't installed, for zero benefit. Decide: drop it
  from `conf.py` + `requirements.txt`, or actually start using its components.

- [ ] **Docs build is fragile without network.** Building requires installing
  the Sphinx toolchain from PyPI; there is no vendored/offline path. On a machine
  without network access, deps must be recovered from pip's wheel cache (see the
  offline recovery in `.claude/skills/run-combra-docs/SKILL.md` Troubleshooting).
  Consider committing a `docs/constraints.txt` (pinned versions) and/or a small
  wheelhouse so offline/CI builds are reproducible.
