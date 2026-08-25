#!/usr/bin/env python3
"""Generate surface statistics that serve only as L1 analysis candidates."""

from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re
import statistics
import sys


SENTENCE_END = re.compile(r"[。！？!?；;]+")
HAN = re.compile(r"[\u4e00-\u9fff]")
LATIN_WORD = re.compile(r"[A-Za-z][A-Za-z0-9_-]*")
PUNCTUATION = "，。；：！？、,.!?;:“”‘’（）()—…《》"
CONNECTORS = (
    "因此", "所以", "然而", "但是", "同时", "首先", "其次", "再次", "最后",
    "一方面", "另一方面", "不仅", "而且", "只有", "才能", "既要", "也要",
    "归根结底", "由此可见", "换言之", "尤其是", "更重要的是",
)


def percentile(values: list[int], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = (len(ordered) - 1) * fraction
    lower = int(index)
    upper = min(lower + 1, len(ordered) - 1)
    weight = index - lower
    return round(ordered[lower] * (1 - weight) + ordered[upper] * weight, 2)


def describe(values: list[int]) -> dict[str, float | int]:
    if not values:
        return {"count": 0, "mean": 0.0, "median": 0.0, "p25": 0.0, "p75": 0.0}
    return {
        "count": len(values),
        "mean": round(statistics.fmean(values), 2),
        "median": round(statistics.median(values), 2),
        "p25": percentile(values, 0.25),
        "p75": percentile(values, 0.75),
    }


def visible_length(text: str) -> int:
    return sum(1 for char in text if not char.isspace())


def analyze_text(text: str) -> dict[str, object]:
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    sentences = [part.strip() for part in SENTENCE_END.split(text) if part.strip()]
    punctuation = {mark: text.count(mark) for mark in PUNCTUATION if text.count(mark)}
    connectors = {word: text.count(word) for word in CONNECTORS if text.count(word)}
    latin_words = collections.Counter(word.lower() for word in LATIN_WORD.findall(text))
    return {
        "characters_non_whitespace": visible_length(text),
        "han_characters": len(HAN.findall(text)),
        "paragraph_lengths": describe([visible_length(part) for part in paragraphs]),
        "sentence_lengths": describe([visible_length(part) for part in sentences]),
        "punctuation": punctuation,
        "connectors": connectors,
        "latin_words_top20": latin_words.most_common(20),
    }


def collect_files(inputs: list[str]) -> list[pathlib.Path]:
    found: set[pathlib.Path] = set()
    for raw in inputs:
        path = pathlib.Path(raw)
        if path.is_file() and path.suffix.lower() in {".md", ".txt"}:
            found.add(path.resolve())
        elif path.is_dir():
            found.update(
                candidate.resolve()
                for candidate in path.rglob("*")
                if candidate.is_file() and candidate.suffix.lower() in {".md", ".txt"}
            )
        else:
            raise FileNotFoundError(f"No readable .md/.txt input at: {path}")
    return sorted(found)


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize surface statistics for essay corpora.")
    parser.add_argument("inputs", nargs="+", help="Files or directories containing .md/.txt essays")
    parser.add_argument("--output", help="Write JSON to this path; otherwise print to stdout")
    parser.add_argument(
        "--case-prefix",
        default="CASE",
        help="Anonymous prefix for per-file case IDs (default: CASE)",
    )
    args = parser.parse_args()

    try:
        files = collect_files(args.inputs)
    except FileNotFoundError as error:
        parser.error(str(error))
    if not files:
        parser.error("No .md or .txt files found")

    per_case: dict[str, object] = {}
    combined_parts: list[str] = []
    for index, path in enumerate(files, start=1):
        text = path.read_text(encoding="utf-8-sig")
        case_id = f"{args.case_prefix}-{index:03d}"
        per_case[case_id] = analyze_text(text)
        combined_parts.append(text)

    report = {
        "notice": "Statistics are L1 candidates, not author-style conclusions.",
        "file_count": len(files),
        "combined": analyze_text("\n\n".join(combined_parts)),
        "cases": per_case,
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        pathlib.Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
