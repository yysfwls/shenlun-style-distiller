#!/usr/bin/env python3
"""Perform deterministic checks on a plain-text or Markdown Shenlun essay."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


PLACEHOLDER_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bTODO\b",
        r"\bTBD\b",
        r"待补(?:充)?",
        r"占位符?",
        r"\{\{[^}\n]+\}\}",
        r"\[\s*待(?:补|填)[^\]]*\]",
        r"\bX{2,}\b",
    )
]


def split_title_and_body(text: str, require_title: bool) -> tuple[str, str]:
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    first_index = next((index for index, line in enumerate(lines) if line.strip()), None)
    if first_index is None:
        return "", ""

    first = lines[first_index].strip()
    markdown_title = first.startswith("#")
    plain_title = (
        len(first) <= 60
        and first_index + 1 < len(lines)
        and not lines[first_index + 1].strip()
    )

    if markdown_title or plain_title:
        title = first.lstrip("#").strip()
        body = "\n".join(lines[first_index + 1 :]).strip()
        return title, body

    if require_title:
        return "", "\n".join(lines[first_index:]).strip()
    return "", "\n".join(lines[first_index:]).strip()


def count_non_whitespace(text: str) -> int:
    return sum(not character.isspace() for character in text)


def find_placeholders(text: str) -> list[str]:
    matches: list[str] = []
    for pattern in PLACEHOLDER_PATTERNS:
        matches.extend(match.group(0) for match in pattern.finditer(text))
    return sorted(set(matches))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("essay", type=Path)
    parser.add_argument("--min-chars", type=int, default=1000)
    parser.add_argument("--max-chars", type=int, default=1200)
    parser.add_argument("--min-paragraphs", type=int, default=4)
    parser.add_argument("--required", action="append", default=[])
    parser.add_argument("--no-title", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.min_chars < 0 or args.max_chars < args.min_chars:
        parser.error("invalid character range")
    if not args.essay.is_file():
        parser.error(f"essay not found: {args.essay}")

    text = args.essay.read_text(encoding="utf-8")
    title, body = split_title_and_body(text, require_title=not args.no_title)
    character_count = count_non_whitespace(body)
    paragraphs = [block.strip() for block in re.split(r"\n\s*\n", body) if block.strip()]
    placeholders = find_placeholders(text)
    missing_required = [item for item in args.required if item not in text]

    checks = {
        "title_present": bool(title) or args.no_title,
        "character_range": args.min_chars <= character_count <= args.max_chars,
        "paragraph_count": len(paragraphs) >= args.min_paragraphs,
        "no_placeholders": not placeholders,
        "required_terms_present": not missing_required,
    }
    passed = all(checks.values())
    result = {
        "essay": str(args.essay),
        "title": title,
        "body_non_whitespace_characters": character_count,
        "expected_character_range": [args.min_chars, args.max_chars],
        "paragraph_count": len(paragraphs),
        "placeholders": placeholders,
        "missing_required_terms": missing_required,
        "checks": checks,
        "status": "pass" if passed else "fail",
        "note": "Mechanical validation only; it does not verify prompt fit, material facts, argument quality, or style fidelity.",
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"status: {result['status']}")
        print(f"title: {title or '[missing]'}")
        print(f"body characters (non-whitespace): {character_count}")
        print(f"paragraphs: {len(paragraphs)}")
        if placeholders:
            print("placeholders: " + ", ".join(placeholders))
        if missing_required:
            print("missing required terms: " + ", ".join(missing_required))
        print(result["note"])

    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
