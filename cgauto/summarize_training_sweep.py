#!/usr/bin/env python3
"""Consolidate the ten isolated live-agent training-policy screens."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import statistics

REPO = Path(__file__).resolve().parent.parent
ANALYSIS = REPO / "data/analysis/live-agent-6553250"
SUBMISSIONS = REPO / "cgauto/submissions"

IDEAS = [
    ("train-prefer-carry3", "raise preferred minimum carry from 2 to 3"),
    ("train-cap-carry2", "cap trained carry at 2"),
    ("train-prefer-chop2", "raise preferred minimum chop from 1 to 2"),
    ("train-cap-chop2", "cap trained chop at 2"),
    ("train-require-carry2", "require the preferred carry-2 floor"),
    ("train-extra-eta8", "reduce permitted extra training ETA from 15 to 8"),
    ("train-extra-eta25", "increase permitted extra training ETA from 15 to 25"),
    ("train-deadline25", "move the hard training deadline from turn 35 to 25"),
    ("train-deadline45", "move the hard training deadline from turn 35 to 45"),
    ("train-prefer-movement-ties", "prefer movement when opening objectives tie"),
]

DECISIONS = {
    "train-prefer-carry3": "reject_negative_mean",
    "train-cap-carry2": "reject_negative_wood",
    "train-prefer-chop2": "park_inert",
    "train-cap-chop2": "reject_outlier_driven",
    "train-require-carry2": "reject_negative_mean",
    "train-extra-eta8": "reject_confirmation_negative",
    "train-extra-eta25": "reject_negative_mean",
    "train-deadline25": "reject_negative_wood",
    "train-deadline45": "park_inert_negative_only",
    "train-prefer-movement-ties": "park_inert",
}


def row_stats(rows: list[dict]) -> dict:
    margins = [row["candidate_paired_margin"] for row in rows]
    wood = [row["candidate_wood_delta"] for row in rows]
    if not margins:
        raise ValueError("cannot summarize an empty study")
    mean = statistics.mean(margins)
    deviation = statistics.stdev(margins) if len(margins) > 1 else 0.0
    standard_error = deviation / math.sqrt(len(margins))
    ordered = sorted(margins)
    trim = math.floor(len(ordered) * 0.05)
    trimmed = ordered[trim : len(ordered) - trim] if trim else ordered
    return {
        "seeds": len(rows),
        "mean_margin": mean,
        "median_margin": statistics.median(margins),
        "margin_stdev": deviation,
        "approximate_95_ci": [mean - 1.96 * standard_error, mean + 1.96 * standard_error],
        "trimmed_5pct_mean_margin": statistics.mean(trimmed),
        "mean_wood_delta": statistics.mean(wood),
        "mean_nonwood_score_delta": statistics.mean(
            margin - 4 * wood_delta for margin, wood_delta in zip(margins, wood)
        ),
        "wins_ties_losses": {
            "wins": sum(margin > 0 for margin in margins),
            "ties": sum(margin == 0 for margin in margins),
            "losses": sum(margin < 0 for margin in margins),
        },
        "active_seeds": sum(margin != 0 for margin in margins),
        "minimum_margin": min(margins),
        "maximum_margin": max(margins),
    }


def artifact_metadata(path: Path) -> dict:
    content = path.read_bytes()
    return {
        "path": str(path.relative_to(REPO)),
        "bytes": len(content),
        "sha256": hashlib.sha256(content).hexdigest(),
    }


def load_rows(path: Path) -> list[dict]:
    payload = json.loads(path.read_text())
    return payload["rows"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis-dir", type=Path, default=ANALYSIS)
    parser.add_argument(
        "--output", type=Path, default=ANALYSIS / "training-policy-sweep-summary.json"
    )
    args = parser.parse_args()

    ideas = []
    for name, hypothesis in IDEAS:
        stage1_path = args.analysis_dir / f"{name}-local-study.json"
        confirmation_path = args.analysis_dir / f"{name}-local-study-200.json"
        stage1 = row_stats(load_rows(stage1_path))
        confirmation = row_stats(load_rows(confirmation_path)) if confirmation_path.exists() else None
        candidate = SUBMISSIONS / f"candidate-agent6553250-{name}.min.rs"
        ideas.append(
            {
                "name": name,
                "hypothesis": hypothesis,
                "artifact": artifact_metadata(candidate),
                "stage1": stage1,
                "confirmation": confirmation,
                "final_evidence": confirmation or stage1,
                "decision": DECISIONS[name],
                "field_escalated": False,
            }
        )

    payload = {
        "schema": 1,
        "scope": "paired local self-harm screen; not an arena predictor",
        "protocol": {
            "stage1_seeds": 60,
            "confirmation_seeds": 200,
            "workers": 8,
            "seat_swapped": True,
        },
        "baseline": artifact_metadata(
            SUBMISSIONS / "agent-6553250-yamo-orchard-live.min.rs"
        ),
        "ideas": ideas,
        "field_games": 0,
        "arena_submissions": 0,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=1) + "\n")
    print(f"summarized {len(ideas)} ideas -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
