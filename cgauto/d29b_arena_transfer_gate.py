#!/usr/bin/env python3
"""Evaluate the frozen D29b controlled Arena-transfer checkpoints."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any


BASELINE_SCORE = 23.05
EARLY_REJECT_SCORE = 21.55
REJECT_SCORE = 22.55
PROVISIONAL_SCORE = 23.85
PROMOTE_SCORE = 23.55
MAX_CATASTROPHIC_GAP = 0.02
MAX_NEGATIVE_MASS_RATE_RATIO = 1.10
CONFIRM_SECONDS = 15 * 60


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def observed_at(checkpoint: dict[str, Any]) -> datetime:
    stamp = checkpoint.get("observed_at")
    if not stamp:
        raise ValueError("checkpoint lacks observed_at")
    return datetime.fromisoformat(stamp.replace("Z", "+00:00"))


def games(checkpoint: dict[str, Any]) -> int:
    return int(checkpoint.get("matching_finished", 0))


def score(checkpoint: dict[str, Any]) -> float:
    value = (checkpoint.get("arena") or {}).get("score")
    if value is None:
        raise ValueError("checkpoint lacks Arena score")
    return float(value)


def clean(checkpoint: dict[str, Any]) -> tuple[bool, list[str]]:
    reasons = []
    if checkpoint.get("identity_clean") is not True:
        reasons.append("identity audit is not clean")
    if checkpoint.get("unexpected_rows"):
        reasons.append("battle stream contains unexpected rows")
    if checkpoint.get("fetch_failures"):
        reasons.append("one or more finished results could not be audited")
    if checkpoint.get("parsed_results") != checkpoint.get("matching_finished"):
        reasons.append("not every finished result was parsed")
    if (checkpoint.get("summary") or {}).get("validity_runtime_signals"):
        reasons.append("validity/runtime signal present")
    return not reasons, reasons


def control_prefix(control: dict[str, Any], count: int) -> dict[str, float]:
    rows = control.get("rows") or []
    if not rows:
        raise ValueError("control checkpoint lacks audited rows")
    prefix = rows[: min(count, len(rows))]
    margins = [float(row["margin"]) for row in prefix]
    negative_mass = sum(-margin for margin in margins if margin < 0)
    return {
        "games": len(prefix),
        "catastrophic_rate": sum(margin <= -100 for margin in margins) / len(prefix),
        "negative_mass_rate": negative_mass / len(prefix),
    }


def safety(control: dict[str, Any], candidate: dict[str, Any]) -> tuple[bool, dict, list[str]]:
    count = games(candidate)
    prefix = control_prefix(control, count)
    summary = candidate["summary"]
    candidate_catastrophic_rate = float(summary["catastrophic_rate"])
    candidate_negative_mass_rate = float(summary["negative_margin_mass"]) / count
    catastrophic_gap = candidate_catastrophic_rate - prefix["catastrophic_rate"]
    mass_ratio = (
        candidate_negative_mass_rate / prefix["negative_mass_rate"]
        if prefix["negative_mass_rate"]
        else (0.0 if candidate_negative_mass_rate == 0 else None)
    )
    reasons = []
    if catastrophic_gap > MAX_CATASTROPHIC_GAP:
        reasons.append("catastrophic rate exceeds matched resident by more than 2pp")
    if mass_ratio is None or mass_ratio > MAX_NEGATIVE_MASS_RATE_RATIO:
        reasons.append("negative-margin mass rate exceeds 110% of matched resident")
    metrics = {
        "matched_control_games": int(prefix["games"]),
        "control_catastrophic_rate": prefix["catastrophic_rate"],
        "candidate_catastrophic_rate": candidate_catastrophic_rate,
        "catastrophic_rate_gap": catastrophic_gap,
        "control_negative_mass_rate": prefix["negative_mass_rate"],
        "candidate_negative_mass_rate": candidate_negative_mass_rate,
        "negative_mass_rate_ratio": mass_ratio,
    }
    return not reasons, metrics, reasons


def health_gate(candidate: dict[str, Any]) -> dict[str, Any]:
    candidate_clean, reasons = clean(candidate)
    status = "wait"
    if games(candidate) >= 10:
        status = "pass" if candidate_clean else "reject"
    else:
        reasons.append("candidate read has fewer than 10 games")
    return {"gate": "candidate-health", "status": status, "reasons": reasons}


def early_gate(candidate: dict[str, Any]) -> dict[str, Any]:
    candidate_clean, reasons = clean(candidate)
    status = "wait"
    if games(candidate) < 60:
        reasons.append("candidate read has fewer than 60 games")
    elif not candidate_clean:
        status = "reject"
    elif score(candidate) <= EARLY_REJECT_SCORE:
        status = "reject"
        reasons.append("candidate score is at most 21.55")
    else:
        status = "continue"
    return {
        "gate": "candidate-060",
        "status": status,
        "score": score(candidate),
        "score_delta": score(candidate) - BASELINE_SCORE,
        "reasons": reasons,
    }


def checkpoint_120(control: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    candidate_clean, reasons = clean(candidate)
    report = {
        "gate": "candidate-120",
        "status": "wait",
        "score": score(candidate),
        "score_delta": score(candidate) - BASELINE_SCORE,
        "reasons": reasons,
    }
    if games(candidate) < 120:
        report["reasons"].append("candidate read has fewer than 120 games")
        return report
    safety_clean, metrics, safety_reasons = safety(control, candidate)
    report.update(metrics)
    report["reasons"].extend(safety_reasons)
    if not candidate_clean or not safety_clean or score(candidate) < REJECT_SCORE:
        report["status"] = "reject"
        if score(candidate) < REJECT_SCORE:
            report["reasons"].append("candidate score is below 22.55")
    elif score(candidate) >= PROVISIONAL_SCORE:
        report["status"] = "provisional-continue"
    else:
        report["status"] = "continue-terminal"
    return report


def terminal_gate(
    control: dict[str, Any],
    candidate: dict[str, Any],
    confirm: dict[str, Any] | None = None,
) -> dict[str, Any]:
    candidate_clean, reasons = clean(candidate)
    report = {
        "gate": "candidate-terminal",
        "status": "wait",
        "score": score(candidate),
        "score_delta": score(candidate) - BASELINE_SCORE,
        "reasons": reasons,
    }
    terminal_ready = games(candidate) >= 150 and candidate.get("matching_pending") == 0
    if not terminal_ready:
        report["reasons"].append("terminal read requires at least 150 games and zero pending")
        return report
    safety_clean, metrics, safety_reasons = safety(control, candidate)
    report.update(metrics)
    report["reasons"].extend(safety_reasons)
    if not candidate_clean or not safety_clean or score(candidate) < PROMOTE_SCORE:
        report["status"] = "reject"
        if score(candidate) < PROMOTE_SCORE:
            report["reasons"].append("candidate score is below 23.55")
        return report
    if confirm is None:
        report["reasons"].append("a second terminal read at least 15 minutes later is required")
        return report

    confirm_clean, confirm_reasons = clean(confirm)
    confirm_ready = games(confirm) >= 150 and confirm.get("matching_pending") == 0
    confirm_safety, confirm_metrics, confirm_safety_reasons = safety(control, confirm)
    elapsed = (observed_at(confirm) - observed_at(candidate)).total_seconds()
    report.update(
        {
            "confirm_score": score(confirm),
            "confirm_score_delta": score(confirm) - BASELINE_SCORE,
            "confirm_games": games(confirm),
            "elapsed_seconds": elapsed,
            "confirm_safety": confirm_metrics,
        }
    )
    report["reasons"].extend(confirm_reasons + confirm_safety_reasons)
    if elapsed < CONFIRM_SECONDS:
        report["reasons"].append("confirmation is less than 15 minutes later")
    elif (
        confirm_clean
        and confirm_ready
        and confirm_safety
        and score(confirm) >= PROMOTE_SCORE
    ):
        report["status"] = "promote"
    else:
        report["status"] = "reject"
        if not confirm_ready:
            report["reasons"].append(
                "confirmation requires at least 150 games and zero pending"
            )
        if score(confirm) < PROMOTE_SCORE:
            report["reasons"].append("confirmation score is below 23.55")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="gate", required=True)
    health = subparsers.add_parser("health")
    health.add_argument("--candidate", type=Path, required=True)
    early = subparsers.add_parser("candidate-060")
    early.add_argument("--candidate", type=Path, required=True)
    middle = subparsers.add_parser("candidate-120")
    middle.add_argument("--control", type=Path, required=True)
    middle.add_argument("--candidate", type=Path, required=True)
    terminal = subparsers.add_parser("terminal")
    terminal.add_argument("--control", type=Path, required=True)
    terminal.add_argument("--candidate", type=Path, required=True)
    terminal.add_argument("--confirm", type=Path)
    args = parser.parse_args()
    if args.gate == "health":
        result = health_gate(load(args.candidate))
    elif args.gate == "candidate-060":
        result = early_gate(load(args.candidate))
    elif args.gate == "candidate-120":
        result = checkpoint_120(load(args.control), load(args.candidate))
    else:
        result = terminal_gate(
            load(args.control),
            load(args.candidate),
            load(args.confirm) if args.confirm else None,
        )
    print(json.dumps(result, indent=1))


if __name__ == "__main__":
    main()
