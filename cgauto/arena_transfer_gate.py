#!/usr/bin/env python3
"""Evaluate the frozen Phase 21 arena-transfer gates from checkpoint JSON.

This module contains no network or submission code.  It turns the thresholds in
the predeclared protocol into reproducible decisions while leaving source files
and arena state untouched.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any


CONTROL_SCORE_FLOOR = 21.3
CONTROL_CONFIRM_MIN_SECONDS = 15 * 60
CONTROL_CONFIRM_MIN_GAMES = 20
CANDIDATE_ABSOLUTE_FLOOR = 22.1
CANDIDATE_EARLY_REJECT_DELTA = -1.5
CANDIDATE_PROMOTE_DELTA_120 = 0.8
CANDIDATE_REJECT_DELTA = -0.5
CANDIDATE_MAX_CATASTROPHIC_GAP = 0.02
CANDIDATE_MAX_NEGATIVE_MASS_RATIO = 1.10
CANDIDATE_PROMOTE_DELTA_180 = 0.5


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def observed_at(checkpoint: dict[str, Any]) -> datetime:
    stamp = checkpoint.get("observed_at") or checkpoint.get("captured_at")
    if not stamp:
        raise ValueError("checkpoint lacks observed_at")
    return datetime.fromisoformat(stamp.replace("Z", "+00:00"))


def games(checkpoint: dict[str, Any]) -> int:
    return int(checkpoint.get("matching_finished", 0))


def score(checkpoint: dict[str, Any]) -> float:
    value = (checkpoint.get("arena") or {}).get("score")
    if value is None:
        raise ValueError("checkpoint lacks arena score")
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
    signals = (checkpoint.get("summary") or {}).get("validity_runtime_signals") or []
    if signals:
        reasons.append("validity/runtime signal present")
    return not reasons, reasons


def control_gate(
    initial: dict[str, Any], confirm: dict[str, Any] | None = None
) -> dict[str, Any]:
    initial_clean, reasons = clean(initial)
    report = {
        "gate": "control-capacity",
        "status": "wait",
        "initial_games": games(initial),
        "initial_score": score(initial),
        "reasons": list(reasons),
    }
    if games(initial) < 120:
        report["reasons"].append("initial control read has fewer than 120 games")
        return report
    if not initial_clean or score(initial) < CONTROL_SCORE_FLOOR:
        if score(initial) < CONTROL_SCORE_FLOOR:
            report["reasons"].append("initial control score is below 21.3")
        report["status"] = "fail"
        return report
    if confirm is None:
        report["reasons"].append("a second read at least 15 minutes later is required")
        return report

    confirm_clean, confirm_reasons = clean(confirm)
    elapsed = (observed_at(confirm) - observed_at(initial)).total_seconds()
    added_games = games(confirm) - games(initial)
    report.update(
        {
            "confirm_games": games(confirm),
            "confirm_score": score(confirm),
            "elapsed_seconds": elapsed,
            "additional_games": added_games,
        }
    )
    report["reasons"].extend(confirm_reasons)
    timing_ready = bool(
        elapsed >= CONTROL_CONFIRM_MIN_SECONDS
        and added_games >= CONTROL_CONFIRM_MIN_GAMES
    )
    if elapsed < CONTROL_CONFIRM_MIN_SECONDS:
        report["reasons"].append("confirmation is less than 15 minutes later")
    if added_games < CONTROL_CONFIRM_MIN_GAMES:
        report["reasons"].append("confirmation has fewer than 20 additional games")
    if score(confirm) < CONTROL_SCORE_FLOOR:
        report["reasons"].append("confirmation score is below 21.3")
    if not confirm_clean:
        report["status"] = "fail"
    elif timing_ready:
        report["status"] = "pass" if score(confirm) >= CONTROL_SCORE_FLOOR else "fail"
    return report


def comparison_metrics(
    control: dict[str, Any], candidate: dict[str, Any]
) -> dict[str, Any]:
    control_summary = control["summary"]
    candidate_summary = candidate["summary"]
    control_mass = float(control_summary["negative_margin_mass"])
    candidate_mass = float(candidate_summary["negative_margin_mass"])
    return {
        "control_score": score(control),
        "candidate_score": score(candidate),
        "score_delta": score(candidate) - score(control),
        "control_catastrophic_rate": control_summary["catastrophic_rate"],
        "candidate_catastrophic_rate": candidate_summary["catastrophic_rate"],
        "catastrophic_rate_gap": (
            float(candidate_summary["catastrophic_rate"])
            - float(control_summary["catastrophic_rate"])
        ),
        "control_negative_margin_mass": control_mass,
        "candidate_negative_margin_mass": candidate_mass,
        "negative_margin_mass_ratio": (
            candidate_mass / control_mass if control_mass else (0.0 if not candidate_mass else None)
        ),
    }


def candidate_early_gate(
    control: dict[str, Any], candidate: dict[str, Any]
) -> dict[str, Any]:
    candidate_clean, reasons = clean(candidate)
    metrics = comparison_metrics(control, candidate)
    status = "continue"
    if games(candidate) < 60:
        status = "wait"
        reasons.append("candidate read has fewer than 60 games")
    elif not candidate_clean:
        status = "reject"
    elif metrics["score_delta"] <= CANDIDATE_EARLY_REJECT_DELTA:
        status = "reject"
        reasons.append("candidate is at least 1.5 below matched control")
    return {"gate": "candidate-060", "status": status, "reasons": reasons, **metrics}


def safety_passes(metrics: dict[str, Any]) -> tuple[bool, list[str]]:
    reasons = []
    if metrics["catastrophic_rate_gap"] > CANDIDATE_MAX_CATASTROPHIC_GAP:
        reasons.append("catastrophic rate exceeds control by more than 2pp")
    ratio = metrics["negative_margin_mass_ratio"]
    if ratio is None or ratio > CANDIDATE_MAX_NEGATIVE_MASS_RATIO:
        reasons.append("negative-margin mass exceeds 110% of control")
    return not reasons, reasons


def candidate_120_gate(
    control: dict[str, Any],
    candidate: dict[str, Any],
    confirm: dict[str, Any] | None = None,
) -> dict[str, Any]:
    candidate_clean, reasons = clean(candidate)
    metrics = comparison_metrics(control, candidate)
    safety_clean, safety_reasons = safety_passes(metrics)
    reasons.extend(safety_reasons)
    report = {"gate": "candidate-120", "status": "wait", "reasons": reasons, **metrics}
    if games(candidate) < 120:
        report["reasons"].append("candidate read has fewer than 120 games")
        return report
    if not candidate_clean or not safety_clean or metrics["score_delta"] < CANDIDATE_REJECT_DELTA:
        report["status"] = "reject"
        if metrics["score_delta"] < CANDIDATE_REJECT_DELTA:
            report["reasons"].append("candidate is more than 0.5 below matched control")
        return report
    if metrics["score_delta"] < CANDIDATE_PROMOTE_DELTA_120:
        report["status"] = "extend-180"
        report["reasons"].append("score delta is in the predeclared ambiguous interval")
        return report
    if metrics["candidate_score"] < CANDIDATE_ABSOLUTE_FLOOR:
        report["status"] = "reject"
        report["reasons"].append("candidate score is below 22.1")
        return report
    if confirm is None:
        report["reasons"].append("a second candidate read at least 15 minutes later is required")
        return report

    confirm_clean, confirm_reasons = clean(confirm)
    confirm_metrics = comparison_metrics(control, confirm)
    elapsed = (observed_at(confirm) - observed_at(candidate)).total_seconds()
    report.update(
        {
            "confirm_games": games(confirm),
            "confirm_score": score(confirm),
            "confirm_score_delta": confirm_metrics["score_delta"],
            "elapsed_seconds": elapsed,
        }
    )
    report["reasons"].extend(confirm_reasons)
    if elapsed < CONTROL_CONFIRM_MIN_SECONDS:
        report["reasons"].append("confirmation is less than 15 minutes later")
    elif (
        confirm_clean
        and confirm_metrics["score_delta"] >= CANDIDATE_PROMOTE_DELTA_120
        and confirm_metrics["candidate_score"] >= CANDIDATE_ABSOLUTE_FLOOR
    ):
        report["status"] = "promote"
    else:
        report["status"] = "reject" if elapsed >= CONTROL_CONFIRM_MIN_SECONDS else "wait"
    return report


def candidate_180_gate(
    control: dict[str, Any],
    candidate: dict[str, Any],
    confirm: dict[str, Any] | None = None,
) -> dict[str, Any]:
    candidate_clean, reasons = clean(candidate)
    metrics = comparison_metrics(control, candidate)
    safety_clean, safety_reasons = safety_passes(metrics)
    reasons.extend(safety_reasons)
    report = {"gate": "candidate-180", "status": "wait", "reasons": reasons, **metrics}
    if games(candidate) < 180:
        report["reasons"].append("candidate read has fewer than 180 games")
        return report
    if (
        not candidate_clean
        or not safety_clean
        or metrics["score_delta"] < CANDIDATE_PROMOTE_DELTA_180
        or metrics["candidate_score"] < CANDIDATE_ABSOLUTE_FLOOR
    ):
        report["status"] = "reject"
        if metrics["score_delta"] < CANDIDATE_PROMOTE_DELTA_180:
            report["reasons"].append("candidate is less than 0.5 above matched control")
        if metrics["candidate_score"] < CANDIDATE_ABSOLUTE_FLOOR:
            report["reasons"].append("candidate score is below 22.1")
        return report
    if confirm is None:
        report["reasons"].append("a second final read at least 15 minutes later is required")
        return report

    confirm_clean, confirm_reasons = clean(confirm)
    confirm_metrics = comparison_metrics(control, confirm)
    elapsed = (observed_at(confirm) - observed_at(candidate)).total_seconds()
    report.update(
        {
            "confirm_games": games(confirm),
            "confirm_score": score(confirm),
            "confirm_score_delta": confirm_metrics["score_delta"],
            "elapsed_seconds": elapsed,
        }
    )
    report["reasons"].extend(confirm_reasons)
    if elapsed < CONTROL_CONFIRM_MIN_SECONDS:
        report["reasons"].append("confirmation is less than 15 minutes later")
    elif (
        confirm_clean
        and confirm_metrics["score_delta"] >= CANDIDATE_PROMOTE_DELTA_180
        and confirm_metrics["candidate_score"] >= CANDIDATE_ABSOLUTE_FLOOR
    ):
        report["status"] = "promote"
    else:
        report["status"] = "reject" if elapsed >= CONTROL_CONFIRM_MIN_SECONDS else "wait"
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="gate", required=True)
    control_parser = subparsers.add_parser("control")
    control_parser.add_argument("--initial", type=Path, required=True)
    control_parser.add_argument("--confirm", type=Path)
    early_parser = subparsers.add_parser("candidate-060")
    early_parser.add_argument("--control", type=Path, required=True)
    early_parser.add_argument("--candidate", type=Path, required=True)
    candidate_parser = subparsers.add_parser("candidate-120")
    candidate_parser.add_argument("--control", type=Path, required=True)
    candidate_parser.add_argument("--candidate", type=Path, required=True)
    candidate_parser.add_argument("--confirm", type=Path)
    final_parser = subparsers.add_parser("candidate-180")
    final_parser.add_argument("--control", type=Path, required=True)
    final_parser.add_argument("--candidate", type=Path, required=True)
    final_parser.add_argument("--confirm", type=Path)
    args = parser.parse_args()
    if args.gate == "control":
        report = control_gate(load(args.initial), load(args.confirm) if args.confirm else None)
    elif args.gate == "candidate-060":
        report = candidate_early_gate(load(args.control), load(args.candidate))
    elif args.gate == "candidate-120":
        report = candidate_120_gate(
            load(args.control),
            load(args.candidate),
            load(args.confirm) if args.confirm else None,
        )
    else:
        report = candidate_180_gate(
            load(args.control),
            load(args.candidate),
            load(args.confirm) if args.confirm else None,
        )
    print(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
