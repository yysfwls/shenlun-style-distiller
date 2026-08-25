#!/usr/bin/env python3
"""Audit a shenlun-style-distiller directory before public packaging."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


FORBIDDEN_NAMES = {".DS_Store", "teach", "raw"}
FORBIDDEN_SUFFIXES = {".pdf", ".doc", ".docx", ".ppt", ".pptx"}
SENSITIVE_JSON_KEYS = {
    "source_file",
    "title",
    "titles",
    "opening_first_two_sentences",
    "ending_last_two_sentences",
}
LOCAL_PATH_PATTERNS = (
    re.compile("/" + r"Users/[^/\s]+/"),
    re.compile(r"[A-Za-z]:\\" + r"Users\\[^\\\s]+\\"),
)
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def collect_json_keys(value: object) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        keys.update(str(key) for key in value)
        for child in value.values():
            keys.update(collect_json_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(collect_json_keys(child))
    return keys


def audit(root: Path) -> list[str]:
    issues: list[str] = []
    files = [path for path in root.rglob("*") if path.is_file()]

    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if any(part in FORBIDDEN_NAMES for part in relative.parts):
            issues.append(f"forbidden path: {relative}")
        if any(ord(character) > 127 for character in relative.as_posix()):
            issues.append(f"non-ASCII public path: {relative}")
        if path.is_symlink():
            issues.append(f"symlink not allowed in release: {relative}")

    for path in files:
        relative = path.relative_to(root)
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            issues.append(f"source document in release: {relative}")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            issues.append(f"unexpected binary file: {relative}")
            continue

        for pattern in LOCAL_PATH_PATTERNS:
            if pattern.search(text):
                issues.append(f"local absolute path in: {relative}")

        if path.suffix.lower() == ".json":
            try:
                value = json.loads(text)
            except json.JSONDecodeError as error:
                issues.append(f"invalid JSON {relative}: {error}")
            else:
                present = collect_json_keys(value) & SENSITIVE_JSON_KEYS
                if present:
                    issues.append(
                        f"sensitive JSON keys in {relative}: {', '.join(sorted(present))}"
                    )

        if path.suffix.lower() == ".md":
            for target in MARKDOWN_LINK.findall(text):
                clean_target = target.split("#", 1)[0].strip()
                if not clean_target or "://" in clean_target or clean_target.startswith("mailto:"):
                    continue
                linked = (path.parent / clean_target).resolve()
                if not linked.exists():
                    issues.append(f"broken link in {relative}: {target}")

    return sorted(set(issues))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, nargs="?", default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    if not root.is_dir():
        parser.error(f"not a directory: {root}")

    issues = audit(root)
    if issues:
        print("release audit: fail")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print(f"release audit: pass ({root})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
