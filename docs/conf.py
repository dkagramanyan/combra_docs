# Configuration file for the Sphinx documentation builder.
#
# combra documentation — built with Sphinx and the PyData Sphinx theme
# (the same theme family as the scikit-image docs).
# Full reference: https://www.sphinx-doc.org/en/master/usage/configuration.html

import json
import os

# -- Project information -----------------------------------------------------

project = "combra"
copyright = "2026, D.G.Kagramanyan"
author = "D.G.Kagramanyan"
release = "0.10.0"
version = "0.10"

# -- General configuration ---------------------------------------------------

extensions = [
    "myst_parser",
    "sphinx_design",
    "sphinx_copybutton",
    "sphinx.ext.doctest",
    "sphinx.ext.linkcode",
]

# -- Doctests ----------------------------------------------------------------
#
# `python -m sphinx -b doctest docs _doctest` runs the examples written as
# ```{doctest}``` blocks. Plain ```pycon``` fences are NOT collected -- a MyST
# fence becomes a literal_block, never a doctest_block, so the builder cannot see
# it. That is deliberate: most examples on these pages are illustrative sessions
# over names that do not exist (`real_batch`, `dpmpp_fn`), and can never run. Only
# blocks that pass standalone carry the directive.
#
# Some of those write files (parquets, PNGs), so run them in a scratch directory
# instead of the source tree.
doctest_global_setup = """
import os as _os, tempfile as _tempfile
_os.chdir(_tempfile.mkdtemp(prefix='combra-doctest-'))
"""

# -- Copy button -------------------------------------------------------------
#
# Examples are written as `pycon` sessions (`>>> ` / `... ` prompts). Pygments
# only emits the `.gp` prompt token that sphinx-copybutton strips by default
# when the block is lexed as `pycon`; any block still tagged `python` would copy
# its prompts verbatim and paste as a syntax error. Stripping by regex covers
# both, plus shell prompts in the install snippets.
copybutton_prompt_text = r">>> |\.\.\. |\$ "
copybutton_prompt_is_regexp = True
copybutton_only_copy_prompt_lines = True
copybutton_remove_prompts = True

# Markdown (MyST) is the source format for every page.
source_suffix = {".md": "markdown"}
master_doc = "index"

# MyST extensions: dollar/AMS math (rendered by MathJax), colon-fence
# admonitions, definition lists, and reST-style field lists inside directives.
myst_enable_extensions = [
    "dollarmath",
    "amsmath",
    "colon_fence",
    "deflist",
    "fieldlist",
    "attrs_inline",
    "substitution",
]
myst_heading_anchors = 3

templates_path = ["_templates"]
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "QUICKSTART.md",
    "README.md",
    "content/**",
    "layouts/**",
    "archetypes/**",
    "public/**",
]

# -- Options for HTML output -------------------------------------------------

html_theme = "pydata_sphinx_theme"
html_title = "combra"
html_static_path = ["_static"]
html_css_files = ["custom.css"]

# Link the "Edit this page" button and the GitHub icon back to the docs repo.
html_context = {
    "github_user": "dkagramanyan",
    "github_repo": "combra_docs",
    "github_version": "main",
    "doc_path": "docs",
    # Follow the reader's OS preference instead of forcing light. The theme
    # toggle in `navbar_end` still overrides it per-visitor.
    "default_mode": "auto",
}

html_theme_options = {
    # Wrench-emoji wordmark stands in for any project logo, in the header…
    "logo": {"text": "🔧 combra"},
    # Header keeps only the wordmark + version dropdown (left) and the
    # search / theme-toggle / GitHub controls (right). The section
    # navigation lives in the left sidebar as a structured tree, not in
    # the header.
    "navbar_start": ["navbar-logo", "version-switcher"],
    "navbar_center": [],
    "navbar_end": ["theme-switcher", "navbar-icon-links"],
    "navbar_persistent": ["search-button"],
    "show_prev_next": True,
    "use_edit_page_button": True,
    "navigation_with_keys": False,
    "collapse_navigation": False,
    # Expand the left-sidebar tree down to the per-module API pages.
    "show_nav_level": 2,
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/dkagramanyan/combra",
            "icon": "fa-brands fa-github",
        },
    ],
    # Version dropdown in the upper-left corner.
    "switcher": {
        "json_url": "_static/switcher.json",
        "version_match": release,
    },
    "show_version_warning_banner": True,
    "search_bar_text": "Search the combra docs…",
    # Footer: combra wordmark on the left, copyright on the right.
    "footer_start": ["footer-brand"],
    "footer_end": ["copyright"],
}

# Show the structured navigation tree in the left sidebar on every page —
# including the landing page, where PyData hides it by default.
html_sidebars = {
    "**": ["sidebar-tree"],
}

# Sphinx domain settings.
add_module_names = False
python_use_unqualified_type_names = True


# -- Source links ("[source]" next to every object) --------------------------
#
# The API pages are hand-authored ``py:`` directives rather than autodoc, so we
# resolve each object back to its definition in the combra source tree through a
# pre-built index (``_static/source_index.json``, generated from the package
# AST). ``sphinx.ext.linkcode`` then renders a GitHub "[source]" link for every
# function, class, and method — the same affordance the scikit-image API pages
# offer.

_COMBRA_REPO = "https://github.com/dkagramanyan/combra"
_COMBRA_REF = "main"
_SOURCE_INDEX = None


def _load_source_index():
    global _SOURCE_INDEX
    if _SOURCE_INDEX is None:
        path = os.path.join(os.path.dirname(__file__), "_static", "source_index.json")
        try:
            with open(path, encoding="utf-8") as fh:
                _SOURCE_INDEX = json.load(fh)
        except OSError:
            _SOURCE_INDEX = []
    return _SOURCE_INDEX


def linkcode_resolve(domain, info):
    if domain != "py":
        return None
    fullname = info.get("fullname") or ""
    if not fullname:
        return None
    leaf = fullname.split(".")[-1]
    tokens = set((info.get("module") or "").split(".")) | set(fullname.split("."))

    candidates = [rec for rec in _load_source_index() if rec["leaf"] == leaf]
    if not candidates:
        return None
    if len(candidates) > 1:
        by_subpkg = [rec for rec in candidates if rec["subpkg"] in tokens]
        candidates = by_subpkg or candidates
    if len(candidates) > 1:
        by_class = [rec for rec in candidates if rec["qual"].split(".")[0] in tokens]
        candidates = by_class or candidates

    rec = candidates[0]
    return f"{_COMBRA_REPO}/blob/{_COMBRA_REF}/{rec['file']}#L{rec['start']}-L{rec['end']}"
