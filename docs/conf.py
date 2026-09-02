# Configuration file for the Sphinx documentation builder.
#
# combra documentation — built with Sphinx and the PyData Sphinx theme
# (the same theme family as the scikit-image docs).
# Full reference: https://www.sphinx-doc.org/en/master/usage/configuration.html

import inspect
import os
import subprocess
import sys

# The API reference is generated from combra's docstrings, so the package must be
# importable. A checkout sitting next to this repo is used when combra is not
# installed, which is the usual local-development layout; COMBRA_SRC overrides it.
_combra_src = os.environ.get("COMBRA_SRC") or os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "combra")
)
if os.path.isdir(os.path.join(_combra_src, "combra")):
    sys.path.insert(0, _combra_src)

import combra  # noqa: E402

# -- Project information -----------------------------------------------------

project = "combra"
copyright = "2026, D.G.Kagramanyan"
author = "D.G.Kagramanyan"
release = "0.13.0"
version = "0.13"

# -- General configuration ---------------------------------------------------

extensions = [
    "myst_parser",
    "sphinx_design",
    "sphinx_copybutton",
    "sphinx.ext.doctest",
    "sphinx.ext.linkcode",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "numpydoc",
]

# -- API reference generation ------------------------------------------------
#
# One page per object, listed from an ``autosummary`` table on each module page —
# the SciPy layout. The stub pages under ``api/generated/`` are written at build
# time and are not checked in.
#
# The tables are written inside ``{eval-rst}`` fences rather than MyST
# ``{autosummary}`` fences on purpose: autosummary's stub generator scans the raw
# source text for ``.. autosummary::`` and cannot see a MyST directive, so a MyST
# fence renders an empty table and silently generates no pages.
autosummary_generate = True
autosummary_imported_members = False

autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
}
autodoc_typehints = "none"  # numpydoc renders the documented types instead.
autodoc_member_order = "bysource"

# numpydoc would otherwise append an autosummary of every attribute and method to
# each class page, duplicating what the class docstring already documents.
numpydoc_show_class_members = False
numpydoc_class_members_toctree = False
# Parameter types are rendered as written rather than turned into
# cross-references: the build treats warnings as errors, and auto-linking every
# type token turns each unresolvable one (``ArrayLike``, ``array_like``) into a
# build failure.
numpydoc_xref_param_type = False

# An unresolvable ``:func:``/``:data:`` role renders as plain text and warns about
# nothing, so a broken cross-reference used to survive indefinitely -- that is how
# a reference to a `combra.metrics.load_rows` that never existed sat in the docs.
# Under nitpicky mode each one is a warning, and the build treats warnings as
# errors, so it cannot be committed.
nitpicky = True
nitpick_ignore = [
    # Internal base class: it is not part of the public API and has no page, but
    # ``:show-inheritance:`` names it in the "Bases:" line of its subclasses.
    ("py:class", "combra.data.pobedit_dataset.BaseImageDataset"),
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable", None),
    "scipy": ("https://docs.scipy.org/doc/scipy", None),
    "pandas": ("https://pandas.pydata.org/docs", None),
    "networkx": ("https://networkx.org/documentation/stable", None),
}

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

# Markdown (MyST) is the source format for every hand-written page; the
# autosummary stub pages under ``api/generated/`` are reStructuredText.
source_suffix = {".md": "markdown", ".rst": "restructuredtext"}
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
# ``sphinx.ext.linkcode`` renders a GitHub "[source]" link for every documented
# object — the same affordance the scikit-image API pages offer. Because the
# reference is generated by autodoc, the object itself is in hand and ``inspect``
# can locate it; no pre-built index is involved.

_COMBRA_REPO = "https://github.com/dkagramanyan/combra"
_COMBRA_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(combra.__file__)))


def _combra_ref():
    """Resolve the combra commit the documented package was built from."""
    for cmd in (["git", "rev-parse", "HEAD"],):
        try:
            out = subprocess.run(
                cmd, cwd=_COMBRA_ROOT, capture_output=True, text=True, timeout=10
            )
        except (OSError, subprocess.SubprocessError):
            break
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    return "main"


_COMBRA_REF = _combra_ref()


def linkcode_resolve(domain, info):
    if domain != "py" or not info.get("module"):
        return None

    obj = sys.modules.get(info["module"])
    if obj is None:
        return None
    for part in (info.get("fullname") or "").split("."):
        obj = getattr(obj, part, None)
        if obj is None:
            return None

    obj = inspect.unwrap(obj)
    obj = getattr(obj, "fget", obj)  # properties
    try:
        file = inspect.getsourcefile(obj)
        lines, start = inspect.getsourcelines(obj)
    except (TypeError, OSError):
        return None
    if not file:
        return None

    rel = os.path.relpath(file, _COMBRA_ROOT)
    if rel.startswith(".."):
        return None
    anchor = f"#L{start}-L{start + len(lines) - 1}"
    return f"{_COMBRA_REPO}/blob/{_COMBRA_REF}/{rel.replace(os.sep, '/')}{anchor}"
