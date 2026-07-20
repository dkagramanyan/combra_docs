---
name: run-combra-docs
description: Build, serve, preview, and screenshot the combra documentation site (Sphinx + pydata-sphinx-theme). Use when asked to run, build, serve, preview, or screenshot combra_docs / the combra docs, or to verify a docs change renders.
---

# Run combra_docs

`combra_docs` is the **Sphinx documentation site** for the `combra` package —
MyST-Markdown sources under `docs/`, built with the `pydata-sphinx-theme`. It is
a **static site**: there is no app server. "Running" it means *build the HTML →
serve it over http → screenshot pages with headless Chrome*.

The driver that does all three is
[`.claude/skills/run-combra-docs/driver.sh`](driver.sh). **All paths below are
relative to the `combra_docs/` unit root** (the directory containing `docs/`).

## Prerequisites

- Python 3.11+ and headless Chrome/Chromium. This container has
  `google-chrome` (150.x) at `/usr/bin/google-chrome`; the driver auto-detects
  `google-chrome`/`chromium`.
- The Sphinx toolchain (exactly what CI installs):
  ```bash
  pip install -r docs/requirements.txt
  ```
  That pulls `sphinx>=7`, `myst-parser>=2`, `pydata-sphinx-theme>=0.15`,
  `sphinx-design>=0.5`, `sphinx-copybutton>=0.5`.
  **If PyPI is unreachable** (this container has no network) see
  [Gotchas](#gotchas) for the offline install from pip's wheel cache.

Point the driver at the interpreter that has the toolchain with `SPHINX_PY`
(defaults to `python3`):
```bash
export SPHINX_PY=/path/to/venv/bin/python
```

## Run (agent path) — the driver

Build + serve + screenshot in one shot. Screenshots land in `_shots/`:
```bash
./.claude/skills/run-combra-docs/driver.sh shot                         # index.html
./.claude/skills/run-combra-docs/driver.sh shot api/angles.html get_started.html
```
Output:
```
built -> public/index.html
shot -> .../_shots/index_html.png  (184850 bytes)
```
Then **look at the PNG** in `_shots/` — a correct landing page shows the
"🔧 combra" wordmark, a "0.5 (stable)" version dropdown, the left nav tree
(Getting started / Python API / Examples), and a right-hand "On this page" TOC
with "Edit on GitHub" / "Show Source" links. API pages (e.g. `api/angles.html`)
show `py:` function signatures with teal `[source]` links, param/return tables,
and copy-button code blocks.

Other subcommands:
```bash
./.claude/skills/run-combra-docs/driver.sh build     # build docs -> public/ only (the CI command)
./.claude/skills/run-combra-docs/driver.sh serve     # build + serve http://127.0.0.1:8347 (Ctrl-C to stop)
```
Env: `PORT` (default 8347), `SHOT_DIR` (default `./_shots`), `CHROME`, `OUT`
(default `public`).

## Build (what CI runs)

The driver's `build` is exactly the GitHub Pages command in
`.github/workflows/pages.yaml` — **warnings are errors**:
```bash
python -m sphinx -b html -W --keep-going -j auto docs public
```
A clean build ends with `build succeeded.` and exit 0. Any broken cross-ref,
missing toctree entry, or bad directive fails the build (that is the point of
`-W` — the same gate blocks a PR).

## Human path

`python -m sphinx -b html docs public` then open `public/index.html` in a
browser. Useless headless — use the driver's `shot`/`serve` instead.

## Test

There is no test suite; the **warnings-as-errors build is the test**. If
`driver.sh build` exits 0, the docs are valid.

## Gotchas

- **No sphinx-design directives are actually used** in the content, but
  `sphinx_design` is still listed in `conf.py`'s `extensions`, so the build
  hard-fails if it isn't installed. Install the full `docs/requirements.txt`;
  don't drop it.
- **linkcode `[source]` links** are resolved from a pre-built AST index
  (`docs/_static/source_index.json`), **not** autodoc — the combra source tree
  does not need to be importable to build the docs. If `[source]` links 404,
  that JSON is stale, not the build.
- **`--headless` (old) vs `--headless=new`**: use `--headless=new` (the driver
  does). Old headless renders the pydata theme with broken fonts/layout.
- **`--no-sandbox` is required** for Chrome as root / in this container, else it
  exits immediately with no screenshot. The driver passes it.
- **`public/` and `_shots/` are build artifacts** — regenerated each run, safe
  to `rm -rf`. CI builds to `public/` too.

## Troubleshooting

- **`Could not import extension sphinx_design` (or myst_parser / pydata…)** →
  toolchain not installed into `SPHINX_PY`'s interpreter. Run
  `pip install -r docs/requirements.txt` into that env.
- **`pip install` fails with `Connection reset` / `No matching distribution`**
  (no network) → install offline from pip's HTTP cache. All five deps and their
  transitive wheels were present under `~/.cache/pip/http-v2` in this container.
  Extract them into a wheelhouse and install with `--no-index`:
  ```bash
  python - <<'PY'
  import os, zipfile, re, shutil
  cache=os.path.expanduser("~/.cache/pip/http-v2"); wh="/tmp/wheelhouse"; os.makedirs(wh, exist_ok=True)
  want={"myst-parser","pydata-sphinx-theme","sphinx-copybutton","sphinx-design",
        "markdown-it-py","mdit-py-plugins","accessible-pygments","docutils","sphinx",
        "babel","pygments","jinja2","markupsafe","beautifulsoup4","soupsieve","mdurl",
        "typing-extensions","snowballstemmer","imagesize","alabaster","packaging","pyyaml"}
  best={}
  for root,_,files in os.walk(cache):
    for f in files:
      if not f.endswith(".body"): continue
      p=os.path.join(root,f)
      with open(p,"rb") as fh:
        if fh.read(2)!=b"PK": continue
      try:
        z=zipfile.ZipFile(p)
        md=[n for n in z.namelist() if n.endswith(".dist-info/METADATA")]
        wf=[n for n in z.namelist() if n.endswith(".dist-info/WHEEL")]
        if not md or not wf: continue
        m=z.read(md[0]).decode("utf-8","replace")
        nm=re.search(r"^Name:\s*(.+)$",m,re.M).group(1).strip().lower().replace("_","-")
        if nm not in want: continue
        vr=re.search(r"^Version:\s*(.+)$",m,re.M).group(1).strip()
        tag=re.search(r"^Tag:\s*(.+)$",z.read(wf[0]).decode(),re.M).group(1).strip()
        if nm not in best or best[nm][0]<vr:
          best[nm]=(vr,p,f"{nm.replace('-','_')}-{vr}-{tag}.whl")
      except Exception: pass
  for nm,(vr,p,fn) in best.items(): shutil.copy(p,os.path.join(wh,fn))
  print("wheels:",len(best))
  PY
  python -m venv --system-site-packages /tmp/docsvenv
  /tmp/docsvenv/bin/pip install --no-index --find-links /tmp/wheelhouse \
    "sphinx>=7" "myst-parser>=2" "pydata-sphinx-theme>=0.15" "sphinx-design>=0.5" "sphinx-copybutton>=0.5"
  export SPHINX_PY=/tmp/docsvenv/bin/python
  ```
  (`--system-site-packages` lets the venv reuse deps already in the base
  interpreter, so only the missing/newer wheels come from the cache.)
- **Blank / tiny screenshot** → server never came up (wrong `SPHINX_PY`, port in
  use) or old `--headless`. Check `/tmp/combra_docs_http.log`; try another `PORT`.
