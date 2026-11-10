"""Append one row to artifacts/version_log.csv from a run JSON produced by run_eval.py.

    python scripts/log_version.py runs/<file>.json --changed system_prompt.md \
        --reason "..." --hypothesis "..." [--author team] [--metric case_accuracy]

metric_before = metric_after of the previous row in the CSV (empty for the first row).
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "artifacts" / "version_log.csv"
FIELDS = ["version", "author", "changed_artifact", "artifact_version", "prompt_hash", "tools_hash",
          "reason", "hypothesis", "metric_before", "metric_after", "run_file"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_file", type=Path)
    parser.add_argument("--changed", required=True, help="changed_artifact column, e.g. baseline / system_prompt.md")
    parser.add_argument("--reason", default="")
    parser.add_argument("--hypothesis", default="")
    parser.add_argument("--author", default="team")
    parser.add_argument("--metric", default="case_accuracy")
    args = parser.parse_args()

    run = json.loads(args.run_file.read_text(encoding="utf-8"))
    rows = list(csv.DictReader(LOG.open(encoding="utf-8"))) if LOG.exists() and LOG.stat().st_size else []
    before = rows[-1]["metric_after"] if rows else ""
    try:
        run_file = str(args.run_file.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        run_file = str(args.run_file)
    row = {
        "version": run["version"], "author": args.author, "changed_artifact": args.changed,
        "artifact_version": run["artifact_version"], "prompt_hash": run["prompt_hash"][:12],
        "tools_hash": run["tools_hash"][:12], "reason": args.reason, "hypothesis": args.hypothesis,
        "metric_before": before, "metric_after": run["summary"][args.metric], "run_file": run_file,
    }
    new_file = not LOG.exists() or LOG.stat().st_size == 0
    with LOG.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        if new_file:
            writer.writeheader()
        writer.writerow(row)
    print(f"logged {row['version']}: {args.metric} {before or '-'} -> {row['metric_after']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
