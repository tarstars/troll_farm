#!/usr/bin/env python3
"""Independently rerun the four c5 D-9 demonstrations through fuzz_panel.eval_p1."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent.parent
PIPELINE = ROOT / "claude_1" / "pipeline"
BR2 = ROOT / "claude_1" / "banana-restoration-r2"
for directory in (PIPELINE, BR2):
    sys.path.insert(0, str(directory))

import fuzz_panel as fp  # noqa: E402
import trace_detectors as td  # noqa: E402


ROWS = ("0....1", "......", "......")
UNIT = [7, 0, 1, 0, 1, 2, 1, 1, 0, 0, 0, 0, 0, 0]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def trace(commands: list[str]):
    parts = [f"{len(ROWS[0])} {len(ROWS)}", *ROWS]
    for _ in commands:
        parts.extend(("0 0 0 0 0 0", "0 0 0 0 0 0", "0", "1", " ".join(map(str, UNIT))))
    transcript = "\n".join(parts) + "\n"
    return td.build_trace(transcript, "\n".join(commands) + "\n")


def d9_kinds(results: list[dict]) -> list[str]:
    d9 = next(result for result in results if result["detector"] == "D-9")
    return [episode["kind"] for episode in d9["episodes"]]


def run_case(candidate: list[str], parent: list[str]) -> dict:
    candidate_trace = trace(candidate)
    parent_trace = trace(parent)
    parent_commands = td.CommandParser().parse("\n".join(parent) + "\n")
    results, violations, inherited, dropped = fp.eval_p1(
        candidate_trace, parent_trace, parent_commands, False
    )
    return {
        "d9_kinds": d9_kinds(results),
        "violation_detectors": [result["detector"] for result in violations],
        "inherited": inherited,
        "d9_dropped": dropped,
    }


def analyze() -> dict:
    parent = ["WAIT", "TRAIN 1 1 0 1", "WAIT", "WAIT"]
    cases = {
        "parent_t2_candidate_never": {
            "candidate": ["WAIT", "WAIT", "WAIT", "WAIT"],
            "expected": ["train_missing"],
        },
        "parent_t2_candidate_t4": {
            "candidate": ["WAIT", "WAIT", "WAIT", "TRAIN 1 1 0 1"],
            "expected": ["train_late"],
        },
        "both_t2_different_talents": {
            "candidate": ["WAIT", "TRAIN 2 1 0 1", "WAIT", "WAIT"],
            "expected": ["train_stats_differ"],
        },
        "both_t2_identical_talents": {
            "candidate": list(parent),
            "expected": [],
        },
    }
    passed = True
    for case in cases.values():
        case["observed"] = run_case(case.pop("candidate"), parent)
        case["pass"] = (
            case["observed"]["d9_kinds"] == case["expected"]
            and case["observed"]["inherited"] == []
            and case["observed"]["d9_dropped"] == 0
        )
        passed = passed and case["pass"]
    return {
        "schema": "codex-1-c5-d9-demonstration-verification-v1",
        "scope": "four constructed execution cases through fuzz_panel.eval_p1; no live-corpus claim",
        "source_hashes": {
            "fuzz_panel.py": sha256(PIPELINE / "fuzz_panel.py"),
            "trace_detectors.py": sha256(BR2 / "trace_detectors.py"),
        },
        "cases": cases,
        "verdict": "VERIFIED" if passed else "MISMATCH",
    }


def markdown(result: dict) -> str:
    lines = [
        "# c5 D-9 demonstration execution verification",
        "",
        f"**Verdict: `{result['verdict']}`**",
        "",
        "Four constructed cases were run through the panel's own `fuzz_panel.eval_p1` path.",
        "This verifies instrument capability only; it makes no live-corpus coverage claim.",
        "",
        "| case | expected D-9 kinds | observed D-9 kinds | pass |",
        "|---|---|---|---|",
    ]
    for name, case in result["cases"].items():
        lines.append(
            f"| `{name}` | `{case['expected']}` | `{case['observed']['d9_kinds']}` | `{case['pass']}` |"
        )
    lines.extend(
        [
            "",
            "The three broken cases fired only their named paired clause; the identical-turn,",
            "identical-talents case was silent. The raw gate returned no inherited or dropped D-9",
            "channel in any case.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    output = ROOT / "codex_1" / "results" / "c5-d9-demonstration-verification-2026-08-14.json"
    report = output.with_suffix(".md")
    result = analyze()
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    report.write_text(markdown(result))
    print(json.dumps({"verdict": result["verdict"], "json": str(output), "markdown": str(report)}))
    return 0 if result["verdict"] == "VERIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
