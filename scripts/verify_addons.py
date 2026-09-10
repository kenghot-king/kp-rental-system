#!/usr/bin/env python3
"""Dependency-free static checks for the custom Odoo addons.

This check deliberately does not import Odoo or connect to a database. It catches
syntax errors, malformed XML, invalid manifests, and missing manifest data files so
it can run locally and in CI before an Odoo integration test is available.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]
ADDONS = ROOT / "addons"


def fail(errors: list[str], path: Path, message: str) -> None:
    errors.append(f"{path.relative_to(ROOT)}: {message}")


def verify_python(path: Path, errors: list[str]) -> None:
    try:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError) as exc:
        fail(errors, path, str(exc))


def verify_xml(path: Path, errors: list[str]) -> None:
    try:
        ElementTree.parse(path)
    except (OSError, ElementTree.ParseError) as exc:
        fail(errors, path, str(exc))


def verify_manifest(module: Path, errors: list[str]) -> None:
    manifest_path = module / "__manifest__.py"
    try:
        manifest = ast.literal_eval(manifest_path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError, ValueError) as exc:
        fail(errors, manifest_path, f"cannot read manifest dictionary: {exc}")
        return

    if not isinstance(manifest, dict):
        fail(errors, manifest_path, "manifest must evaluate to a dictionary")
        return

    for key in ("name", "version", "depends"):
        if key not in manifest:
            fail(errors, manifest_path, f"missing required key: {key}")

    for section in ("data", "demo"):
        for relative_path in manifest.get(section, []):
            if not isinstance(relative_path, str):
                fail(errors, manifest_path, f"{section} contains a non-string entry")
            elif not (module / relative_path).is_file():
                fail(errors, manifest_path, f"{section} file is missing: {relative_path}")


def main() -> int:
    errors: list[str] = []
    modules = sorted(path for path in ADDONS.iterdir() if (path / "__manifest__.py").is_file())

    if not modules:
        print("No custom Odoo modules found.", file=sys.stderr)
        return 1

    for module in modules:
        verify_manifest(module, errors)
        for path in module.rglob("*.py"):
            if "__pycache__" not in path.parts:
                verify_python(path, errors)
        for path in module.rglob("*.xml"):
            verify_xml(path, errors)

    if errors:
        print("Static addon verification failed:", file=sys.stderr)
        print("\n".join(f"- {error}" for error in errors), file=sys.stderr)
        return 1

    print(f"Static addon verification passed for {len(modules)} modules.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
