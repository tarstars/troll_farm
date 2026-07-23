#!/usr/bin/env python3
"""Evaluate the frozen dual-value mature-resident arena transfer protocol."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import sys


REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.arena_transfer_checkpoint import summarize


BASELINE_AGENT = 6560289
BASELINE_SUBMISSION = 41012593
CANDIDATE_AGENT = 6560350
CANDIDATE_SUBMISSION = 41012867
BASELINE_SCORE = 24.28
EARLY_FLOOR = 22.78
REJECT_FLOOR = 23.78
PROVISIONAL_120 = 25.08
FINAL_FLOOR = 24.78
MAX_CATASTROPHIC_GAP = 0.02
MAX_NEGATIVE_MASS_RATIO = 1.10
CONFIRM_SECONDS = 15 * 60


def observed_at(checkpoint: dict) -> datetime:
    return datetime.fromisoformat(checkpoint["observed_at"].replace("Z", "+00:00"))


def score(checkpoint: dict) -> float:
    return float(checkpoint["arena"]["score"])


def games(checkpoint: dict) -> int:
    return int(checkpoint["matching_finished"])


def clean(checkpoint: dict, agent: int, submission: int) -> tuple[bool, list[str]]:
    reasons = []
    if checkpoint.get("agent_id") != agent or checkpoint.get("submission_id") != submission:
        reasons.append("checkpoint has the wrong agent or submission")
    if checkpoint.get("identity_clean") is not True:
        reasons.append("checkpoint identity audit is not clean")
    if checkpoint.get("parsed_results") != checkpoint.get("matching_finished"):
        reasons.append("not every finished replay parsed")
    if checkpoint.get("fetch_failures"):
        reasons.append("one or more replay fetches failed")
    if checkpoint.get("unexpected_rows"):
        reasons.append("battle stream contains unexpected rows")
    if (checkpoint.get("summary") or {}).get("validity_runtime_signals"):
        reasons.append("candidate runtime or validity signal present")
    return not reasons, reasons


def baseline_integrity(baseline: dict) -> tuple[bool, list[str]]:
    valid, reasons = clean(baseline, BASELINE_AGENT, BASELINE_SUBMISSION)
    if games(baseline) != 160:
        reasons.append("baseline is not the frozen 160-game mature read")
    if score(baseline) != BASELINE_SCORE:
        reasons.append("baseline score differs from the frozen 24.28 bracket")
    return valid and not reasons, reasons


def count_matched_safety(baseline: dict, candidate: dict) -> dict:
    count = min(games(candidate), len(baseline["rows"]))
    control = summarize(baseline["rows"][:count])
    trial = candidate["summary"]
    catastrophic_gap = float(trial["catastrophic_rate"]) - float(
        control["catastrophic_rate"]
    )
    control_mass = float(control["negative_margin_mass"])
    candidate_mass = float(trial["negative_margin_mass"])
    ratio = candidate_mass / control_mass if control_mass else None
    checks = {
        "catastrophic_rate": catastrophic_gap <= MAX_CATASTROPHIC_GAP,
        "negative_margin_mass": ratio is not None and ratio <= MAX_NEGATIVE_MASS_RATIO,
    }
    return {
        "count": count,
        "control_catastrophic_rate": control["catastrophic_rate"],
        "candidate_catastrophic_rate": trial["catastrophic_rate"],
        "catastrophic_rate_gap": catastrophic_gap,
        "control_negative_margin_mass": control_mass,
        "candidate_negative_margin_mass": candidate_mass,
        "negative_margin_mass_ratio": ratio,
        "checks": checks,
        "passed": all(checks.values()),
    }


def evaluate(
    baseline: dict, candidate: dict, phase: str, confirm: dict | None = None
) -> dict:
    baseline_ok, reasons = baseline_integrity(baseline)
    candidate_ok, candidate_reasons = clean(
        candidate, CANDIDATE_AGENT, CANDIDATE_SUBMISSION
    )
    reasons.extend(candidate_reasons)
    report = {
        "schema": 1,
        "phase": phase,
        "status": "wait",
        "candidate_games": games(candidate),
        "candidate_pending": int(candidate["matching_pending"]),
        "baseline_score": BASELINE_SCORE,
        "candidate_score": score(candidate),
        "score_delta": score(candidate) - BASELINE_SCORE,
        "reasons": reasons,
    }
    if not baseline_ok or not candidate_ok:
        report["status"] = "reject"
        return report

    if phase == "early-60":
        if games(candidate) < 60:
            report["reasons"].append("fewer than 60 candidate games")
        elif score(candidate) <= EARLY_FLOOR:
            report["status"] = "reject"
            report["reasons"].append("candidate is at least 1.50 below baseline")
        else:
            report["status"] = "continue"
        return report

    safety = count_matched_safety(baseline, candidate)
    report["count_matched_safety"] = safety
    if phase == "checkpoint-120":
        if games(candidate) < 120:
            report["reasons"].append("fewer than 120 candidate games")
        elif not safety["passed"]:
            report["status"] = "reject"
            report["reasons"].append("count-matched tail safety failed")
        elif score(candidate) < REJECT_FLOOR:
            report["status"] = "reject"
            report["reasons"].append("candidate delta is below -0.50")
        elif score(candidate) >= PROVISIONAL_120:
            report["status"] = "provisional-pass"
        else:
            report["status"] = "continue-terminal"
        return report

    if phase != "terminal":
        raise ValueError(f"unknown phase {phase}")
    ready = games(candidate) >= 150 and int(candidate["matching_pending"]) == 0
    if not ready:
        report["reasons"].append("terminal read requires >=150 games and zero pending")
        return report
    if not safety["passed"]:
        report["status"] = "reject"
        report["reasons"].append("terminal count-matched tail safety failed")
        return report
    if score(candidate) < FINAL_FLOOR:
        report["status"] = "reject"
        report["reasons"].append("terminal score is below baseline +0.50")
        return report
    if confirm is None:
        report["reasons"].append("a second terminal read after 15 minutes is required")
        return report
    confirm_ok, confirm_reasons = clean(
        confirm, CANDIDATE_AGENT, CANDIDATE_SUBMISSION
    )
    report["reasons"].extend(confirm_reasons)
    elapsed = (observed_at(confirm) - observed_at(candidate)).total_seconds()
    confirm_safety = count_matched_safety(baseline, confirm)
    report["confirmation"] = {
        "elapsed_seconds": elapsed,
        "games": games(confirm),
        "pending": int(confirm["matching_pending"]),
        "score": score(confirm),
        "score_delta": score(confirm) - BASELINE_SCORE,
        "count_matched_safety": confirm_safety,
    }
    if elapsed < CONFIRM_SECONDS:
        report["reasons"].append("confirmation is less than 15 minutes later")
    if games(confirm) < 150 or int(confirm["matching_pending"]) != 0:
        report["reasons"].append("confirmation is not terminal")
    if score(confirm) < FINAL_FLOOR:
        report["reasons"].append("confirmation score is below baseline +0.50")
    if not confirm_safety["passed"]:
        report["reasons"].append("confirmation tail safety failed")
    report["status"] = (
        "promote"
        if confirm_ok
        and elapsed >= CONFIRM_SECONDS
        and games(confirm) >= 150
        and int(confirm["matching_pending"]) == 0
        and score(confirm) >= FINAL_FLOOR
        and confirm_safety["passed"]
        else "wait"
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument(
        "--phase", choices=("early-60", "checkpoint-120", "terminal"), required=True
    )
    parser.add_argument("--confirm", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = evaluate(
        json.loads(args.baseline.read_text()),
        json.loads(args.candidate.read_text()),
        args.phase,
        json.loads(args.confirm.read_text()) if args.confirm else None,
    )
    rendered = json.dumps(payload, indent=1) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)
    print(rendered, end="")
    return 1 if payload["status"] == "reject" else 0


if __name__ == "__main__":
    raise SystemExit(main())
