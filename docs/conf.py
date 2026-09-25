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
release = "0.17.0"
version = "0.17"

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
    "sphinx_gallery.gen_gallery",
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
]

# The reference lists only the high-level entry points; every other export is
# named in ``undocumented.py`` and has no page. Docstrings and guide pages still
# cross-reference those objects, so a reference that resolves to one of them is
# rendered as plain code instead of failing the build. A reference to something
# that does not exist at all still fails, which keeps nitpicky mode's guard.
sys.path.insert(0, os.path.dirname(__file__))
from undocumented import UNDOCUMENTED, UNDOCUMENTED_MODULES  # noqa: E402

import importlib  # noqa: E402

from sphinx.util.nodes import make_refnode  # noqa: E402

_MISSING = object()


def _import_chain(path):
    """Return the objects along a dotted path, or ``None`` if it does not import."""
    parts = path.split(".")
    for i in range(len(parts), 0, -1):
        try:
            obj = importlib.import_module(".".join(parts[:i]))
        except ImportError:
            continue
        chain = [obj]
        for attr in parts[i:]:
            obj = getattr(obj, attr, _MISSING)
            if obj is _MISSING:
                return None
            chain.append(obj)
        return chain
    return None


def _undocumented_ids():
    ids = set()
    for name in UNDOCUMENTED | UNDOCUMENTED_MODULES:
        chain = _import_chain(name)
        if chain is None:
            raise RuntimeError(f"undocumented.py names {name}, which does not import")
        ids.add(id(chain[-1]))
    return ids


def _plain_undocumented_reference(app, env, node, contnode):
    if node.get("refdomain") != "py":
        return None
    target = node["reftarget"].lstrip(".~")
    module, cls = node.get("py:module"), node.get("py:class")
    candidates = [target]
    if module:
        candidates += [f"{module}.{target}"] + ([f"{module}.{cls}.{target}"] if cls else [])
    for candidate in candidates:
        chain = _import_chain(candidate)
        # A method of an undocumented class counts as undocumented too.
        if chain and any(id(obj) in app.config._undocumented_ids for obj in chain[1:]):
            return contnode
    # The API page's tables show each summary line outside its module, so a bare
    # name in one (``:func:`optimize_path_energies```) no longer resolves. Link
    # it when exactly one documented object carries that name.
    if "." not in target:
        py = env.get_domain("py")
        hits = [(name, entry) for name, entry in py.objects.items()
                if name.endswith("." + target) and not entry.aliased]
        if len(hits) == 1:
            name, entry = hits[0]
            return make_refnode(app.builder, node["refdoc"], entry.docname,
                                entry.node_id, contnode, name)
    return None


def setup(app):
    app.config._undocumented_ids = _undocumented_ids()
    app.connect("missing-reference", _plain_undocumented_reference)

# No ``scipy`` entry. Nothing here resolves against it -- the scipy names in
# combra's docstrings are all inside ``literals``, and with
# ``numpydoc_xref_param_type = False`` and ``autodoc_typehints = "none"`` no
# cross-reference is generated from a type either. Its only effect was a fetch
# of docs.scipy.org, and when that host went unreachable the resulting
# "failed to reach any of the inventories" warning turned into a build failure
# under ``-W``. That warning is logged without a type, so ``suppress_warnings``
# cannot silence it; leaving the mapping out is what removes it. Nitpicky mode
# makes this self-correcting: a scipy cross-reference written later fails the
# build as an unresolvable target, which is the signal to add the entry back.
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable", None),
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

# -- Example gallery ---------------------------------------------------------
#
# The worked examples are Python scripts under ``examples_src/``, in
# sphinx-gallery's ``# %%`` cell format. The html build executes every one and
# writes a page per script into ``examples/`` -- generated output, git-ignored,
# the same layout as the scikit-learn and scikit-image galleries. A failing
# script fails the build. The doctest builder does not collect these pages;
# the scripts are checked by running them here.
#
# Figures are plotly. The scripts end a cell with ``plotly.io.show(fig)``;
# importing plotly's scraper switches the default renderer to
# ``sphinx_gallery_png``, which writes each shown figure as an interactive HTML
# page plus a static PNG (through kaleido), and the scraper embeds the HTML
# in the example page and keeps the PNG for the gallery thumbnail. The scraper
# keeps one figure per cell, so a cell shows at most one.
#
# ``doc_module``/``backreferences_dir`` record which example uses which combra
# function; the function pages list them through the ``minigallery`` in
# ``_templates/autosummary/function.rst``. ``reference_url`` links the names in
# the example code to their API pages.
sphinx_gallery_conf = {
    "examples_dirs": "examples_src",
    "gallery_dirs": "examples",
    "filename_pattern": r"\.py$",  # execute every script, not only plot_*.py
    "within_subsection_order": "FileNameSortKey",
    "image_scrapers": ("plotly.io._sg_scraper.plotly_sg_scraper",),
    "download_all_examples": True,
    "remove_config_comments": True,
    "doc_module": ("combra",),
    "backreferences_dir": "api/generated/backreferences",
    "reference_url": {"combra": None},
}

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
# ``{{ release }}`` on the landing page, so the version is written only here.
myst_substitutions = {"release": release}

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
    # Gallery sources; sphinx-gallery writes the pages into examples/.
    "examples_src/**",
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
    # As in the NumPy and SciPy docs: the top-level sections are header links,
    # and the left sidebar shows only the pages of the section being read.
    "navbar_start": ["navbar-logo", "version-switcher"],
    "navbar_center": ["navbar-nav"],
    "header_links_before_dropdown": 6,
    "navbar_end": ["theme-switcher", "navbar-icon-links"],
    "navbar_persistent": ["search-button"],
    "show_prev_next": True,
    "use_edit_page_button": True,
    "navigation_with_keys": False,
    # Every sidebar branch keeps its expand arrow, collapsed by default.
    "collapse_navigation": False,
    "show_nav_level": 1,
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

html_sidebars = {
    # The landing page is the four cards alone.
    "index": [],
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
