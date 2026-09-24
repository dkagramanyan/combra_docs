#!/usr/bin/env python3
"""Fail if a public ``combra`` name is neither on the API page nor named undocumented.

The reference lists only the high-level entry points, on ``docs/api/*.md``;
every other export is named in ``docs/undocumented.py``. An object no
``autosummary`` table names simply never gets a page, and nothing else forces a
*newly added* public name to be triaged into one list or the other. This script
is that guard.

For each module it compares ``__all__`` against both lists and reports

* public names on neither list;
* names on both;
* names on either list that the module no longer exports.

Run it from the repo root (``python docs/check_api_coverage.py``); exits non-zero
on any finding so CI can gate on it.
"""

from __future__ import annotations

import importlib
import os
import pathlib
import re
import sys

DOCS = pathlib.Path(__file__).parent
API_PAGES = sorted((DOCS / "api").glob("*.md"))

sys.path.insert(0, str(DOCS))
from undocumented import UNDOCUMENTED, UNDOCUMENTED_MODULES  # noqa: E402

# Modules whose public surface must be triaged.
SUBMODULES = [
    "angles",
    "contours",
    "data",
    "ellipse",
    "experimental",
    "fitting",
    "graph",
    "image",
    "io",
    "legacy",
    "metrics",
    "metrics.distributed",
    "stats",
    "synth",
    "utils",
    "validation",
    "viz",
]

# Names inside an ``autosummary`` block: indented, dotted-or-plain identifiers.
_AUTOSUMMARY = re.compile(r"^\.\.\s+autosummary::\s*$")
_DIRECTIVE_OPTION = re.compile(r"^\s*:\w[\w-]*:")
_NAME = re.compile(r"^\s+([A-Za-z_][\w.]*)\s*$")
_CURRENTMODULE = re.compile(r"^\s*\.\.\s+(?:currentmodule|module)::\s+([\w.]+)")


def names_on_page(path: pathlib.Path) -> set[str]:
    """Collect the fully qualified name of every object the page lists."""
    found: set[str] = set()
    current = "combra"
    in_table = False
    for line in path.read_text(encoding="utf-8").splitlines():
        switch = _CURRENTMODULE.match(line)
        if switch:
            current = switch.group(1)
            in_table = False
            continue
        if _AUTOSUMMARY.match(line.strip()) and line.lstrip().startswith(".."):
            in_table = True
            continue
        if not in_table:
            continue
        if not line.strip() or _DIRECTIVE_OPTION.match(line):
            continue
        entry = _NAME.match(line)
        if entry:
            found.add(f"{current}.{entry.group(1)}")
        else:
            in_table = False
    return found


def main() -> int:
    try:
        importlib.import_module("combra")
    except ImportError as exc:
        print(f"cannot import combra: {exc}", file=sys.stderr)
        print("The API reference is generated from it; install it first.", file=sys.stderr)
        return 1

    exported: set[str] = set()
    for sub in SUBMODULES:
        module = importlib.import_module(f"combra.{sub}")
        exported |= {f"combra.{sub}.{n}" for n in getattr(module, "__all__", ()) or ()}

    documented = set().union(*(names_on_page(p) for p in API_PAGES))
    problems = []
    problems += [f"{n}: exported, but neither on an API page nor in undocumented.py"
                 for n in sorted(exported - documented - UNDOCUMENTED)]
    problems += [f"{n}: on an API page and in undocumented.py"
                 for n in sorted(documented & UNDOCUMENTED)]
    for name in sorted(documented | UNDOCUMENTED):
        if name in exported:
            continue
        module, _, attr = name.rpartition(".")
        try:
            ok = hasattr(importlib.import_module(module), attr)
        except ImportError:
            ok = False
        # combra.exceptions exports nothing through __all__; its classes are
        # checked for existence only.
        if not ok or module != "combra.exceptions":
            problems.append(f"{name}: listed, but not exported")
    for name in sorted(UNDOCUMENTED_MODULES):
        try:
            importlib.import_module(name)
        except ImportError:
            problems.append(f"{name}: in UNDOCUMENTED_MODULES, but not importable")

    for p in problems:
        print(p)
    if problems:
        print(f"\n{len(problems)} coverage problem(s).", file=sys.stderr)
        return 1
    print(f"API coverage OK: {len(documented)} documented, "
          f"{len(UNDOCUMENTED)} undocumented, across {len(SUBMODULES)} modules.")
    return 0


if __name__ == "__main__":
    if os.environ.get("COMBRA_COVERAGE_STRICT", "1") == "0":
        print("COMBRA_COVERAGE_STRICT=0 -- skipping.")
        raise SystemExit(0)
    raise SystemExit(main())
