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
  pip install -r docs/requirements.txt -c docs/constraints.txt
  ```
  That pulls `sphinx>=7`, `myst-parser>=2`, `pydata-sphinx-theme>=0.15`,
  `sphinx-design>=0.5`, `sphinx-copybutton>=0.5`, `numpydoc>=1.7`.
  **If PyPI is unreachable** see [Gotchas](#gotchas) for the offline install from
  pip's wheel cache.
- **Network at build time.** `intersphinx` fetches the numpy / scipy / pandas /
  networkx / python inventories on every cold build, and `nitpicky` mode is on,
  so without network every cross-reference into those projects fails the build.
  There is no offline fallback configured; if you need one, cache the
  `objects.inv` files and point `intersphinx_mapping` at the local copies.
- **The `combra` package must be importable.** The API reference is generated
  from its docstrings by `autodoc` + `autosummary`, so the build fails without
  it. `conf.py` looks for a `combra` checkout next to this repo
  (`../combra`) and falls back to whatever is installed; `COMBRA_SRC`
  overrides the path:
  ```bash
  export COMBRA_SRC=/path/to/combra
  ```

Point the driver at the interpreter that has the toolchain with `SPHINX_PY`
(defaults to `python3`):
```bash
export SPHINX_PY=/path/to/venv/bin/python
```

## Run (agent path) — the driver

Build + serve + screenshot in one shot. Screenshots land in `_shots/`:
```bash
./.claude/skills/run-combra-docs/driver.sh shot                         # index.html
./.claude/skills/run-combra-docs/driver.sh shot api/angles.html getting_started/installation.html
```
Output:
```
built -> public/index.html
shot -> .../_shots/index_html.png  (184850 bytes)
```
Then **look at the PNG** in `_shots/` — a correct landing page shows the
"🔧 combra" wordmark, a version dropdown, the left nav tree (Getting started /
User guide / API reference / Examples / Generative models / Development), and a
right-hand "On this page" TOC with "Edit on GitHub" / "Show Source" links.

A module page such as `api/angles.html` is a short intro plus `autosummary`
tables; the per-object pages it links to live under `api/generated/` (e.g.
`api/generated/combra.angles.vertex_angles.html`) and show the signature, a
teal `[source]` link, and Parameters / Returns / See Also / Notes / Examples
sections.

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

CI additionally runs every runnable example — the ```` ```{doctest} ```` blocks on
the hand-written pages and the `Examples` sections of combra's docstrings, which
autodoc pulls into the generated reference pages:
```bash
python -m sphinx -b doctest -W --keep-going docs _doctest
```
Examples that cannot run in CI carry an explicit `# doctest: +SKIP`. Run this
after touching any example or docstring.

## Gotchas

- **`sphinx_design` powers the module grid** on the landing page
  (`::::{grid}` / `:::{grid-item-card}`), so the build hard-fails if it isn't
  installed. Install the full `docs/requirements.txt`; don't drop it.
- **The API reference is generated, not written.** `docs/api/*.md` are short
  intro pages holding `autosummary` tables; the per-object pages under
  `docs/api/generated/` are written at build time and are **not** checked in
  (`rm -rf docs/api/generated` is safe and often the right first move when a
  stale stub lingers). To change what an API page says, edit the **docstring in
  the combra source**, not the docs repo.
- **`autosummary` tables must sit inside an ```` ```{eval-rst} ```` fence.** The
  stub generator scans raw source text for `.. autosummary::` and cannot see a
  MyST `{autosummary}` fence — one renders an empty table and silently generates
  no pages.
- **linkcode `[source]` links** are resolved by `inspect` against the imported
  package, and point at the combra commit that `conf.py` resolved via
  `git rev-parse` in the source tree (falling back to `main`).
- **`--headless` (old) vs `--headless=new`**: use `--headless=new` (the driver
  does). Old headless renders the pydata theme with broken fonts/layout.
- **`--no-sandbox` is required** for Chrome as root / in this container, else it
  exits immediately with no screenshot. The driver passes it.
- **`public/` and `_shots/` are build artifacts** — regenerated each run, safe
  to `rm -rf`. CI builds to `public/` too.

## Troubleshooting

- **`Could not import extension sphinx_design` (or myst_parser / pydata / numpydoc…)** →
  toolchain not installed into `SPHINX_PY`'s interpreter. Run
  `pip install -r docs/requirements.txt -c docs/constraints.txt` into that env.
- **`ModuleNotFoundError: No module named 'combra'`** in `conf.py` → the package
  is neither installed nor sitting at `../combra`. Point `COMBRA_SRC` at a
  checkout.
- **An API page renders an empty table and no per-object pages appear** → the
  `autosummary` block is in a MyST `{autosummary}` fence instead of an
  ```` ```{eval-rst} ```` one. See Gotchas.
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
