#!/usr/bin/env python3
"""Remove source-identifying fields and long excerpts from public research data."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path


CASE_FIELDS = ("case_id", "author_group", "characters", "authorship_status")
SENSITIVE_METRIC_FIELDS = {
    "titles",
    "opening_first_two_sentences",
    "ending_last_two_sentences",
}


def atomic_write_json(path: Path, value: object) -> None:
    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(file_descriptor, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temporary_name, path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def sanitize_case_index(path: Path) -> tuple[int, set[str]]:
    records = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise ValueError("case-index.json must contain a list")

    removed: set[str] = set()
    public_records = []
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("case-index.json contains a non-object record")
        removed.update(set(record) - set(CASE_FIELDS))
        public_records.append({field: record[field] for field in CASE_FIELDS if field in record})

    atomic_write_json(path, public_records)
    return len(public_records), removed


def sanitize_metrics(path: Path) -> tuple[int, set[str]]:
    metrics = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(metrics, dict):
        raise ValueError("style-pattern-metrics.json must contain an object")

    removed: set[str] = set()
    for profile in metrics.values():
        if not isinstance(profile, dict):
            raise ValueError("style metrics profile must be an object")
        for field in SENSITIVE_METRIC_FIELDS:
            if field in profile:
                removed.add(field)
                profile.pop(field)

    atomic_write_json(path, metrics)
    return len(metrics), removed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data_dir", type=Path)
    args = parser.parse_args()

    case_path = args.data_dir / "case-index.json"
    metrics_path = args.data_dir / "style-pattern-metrics.json"
    if not case_path.is_file() or not metrics_path.is_file():
        parser.error("data_dir must contain case-index.json and style-pattern-metrics.json")

    case_count, case_removed = sanitize_case_index(case_path)
    profile_count, metric_removed = sanitize_metrics(metrics_path)
    print(f"sanitized case records: {case_count}")
    print("removed case fields: " + (", ".join(sorted(case_removed)) or "none"))
    print(f"sanitized metric profiles: {profile_count}")
    print("removed metric fields: " + (", ".join(sorted(metric_removed)) or "none"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
