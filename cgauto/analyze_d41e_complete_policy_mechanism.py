#!/usr/bin/env python3
"""Diagnose why the clean D41e complete policy missed its +5 promotion floor."""

from __future__ import annotations

import collections
import json
from pathlib import Path

from cgauto.analyze_d41a_macro_bc import sha256
from cgauto.evaluate_d41e_branch_gate import distribution


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
RESULT = ANALYSIS / "d41e-branch-gap-complete-policy-result.json"
OUTPUT = ANALYSIS / "d41e-complete-policy-mechanism-2026-07-21.json"
EXPECTED_RESULT_SHA256 = "3619d394ce42d5d257ca59894b5e2b482eef70dbc117f03bb070d6c9d166a17e"


def bucket_summary(indexes: list[int], candidate: list[dict], baseline: list[dict]) -> dict:
    deltas = [candidate[index]["margin"] - baseline[index]["margin"] for index in indexes]
    report = distribution(deltas)
    report["global_mean_contribution"] = sum(deltas) / len(candidate)
    return report


def analyze(candidate: list[dict], baseline: list[dict]) -> dict:
    if len(candidate) != len(baseline) or not candidate:
        raise ValueError("D41e mechanism rows must be nonempty and aligned")
    groups: dict[tuple[str, str], list[int]] = collections.defaultdict(list)
    for index, row in enumerate(candidate):
        overrides = int(row["overrides"])
        count_label = str(overrides) if overrides < 4 else "4+"
        groups[("override_count", count_label)].append(index)
        if not overrides:
            continue
        branch = row["branch_overrides"]
        branch_label = (
            "both"
            if branch["evacuation"] and branch["rate"]
            else ("evacuation" if branch["evacuation"] else "rate")
        )
        phase = row["phase_overrides"]
        phase_label = (
            "both"
            if phase["early"] and phase["late"]
            else ("early" if phase["early"] else "late")
        )
        groups[("branch_pattern", branch_label)].append(index)
        groups[("phase_pattern", phase_label)].append(index)
        if overrides == 1:
            groups[("single_override", f"{branch_label}_{phase_label}")].append(index)

    summaries = {
        f"{dimension}|{label}": bucket_summary(indexes, candidate, baseline)
        for (dimension, label), indexes in sorted(groups.items())
    }
    changed = [index for index, row in enumerate(candidate) if row["overrides"] > 0]
    changed_stats = bucket_summary(changed, candidate, baseline)
    required_changed_share = 5.0 / changed_stats["mean"]
    observed_changed_share = len(changed) / len(candidate)
    additional_equivalent_episodes = max(
        0, int(round((required_changed_share - observed_changed_share) * len(candidate)))
    )
    count_means = [
        summaries[f"override_count|{label}"]["mean"]
        for label in ("1", "2", "3", "4+")
        if f"override_count|{label}" in summaries
    ]
    return {
        "episodes": len(candidate),
        "changed_episodes": len(changed),
        "changed_episode_share": observed_changed_share,
        "changed_episode_margin": changed_stats,
        "required_changed_share_at_observed_value_for_plus_5": required_changed_share,
        "additional_equivalent_changed_episodes_for_plus_5": additional_equivalent_episodes,
        "groups": summaries,
        "diagnosis": {
            "multi_override_means_nondecreasing": all(
                left <= right for left, right in zip(count_means, count_means[1:])
            ),
            "rate_accounts_for_positive_global_gain": summaries[
                "branch_pattern|rate"
            ]["global_mean_contribution"]
            > 4.0,
            "evacuation_is_not_prospectively_positive": summaries[
                "branch_pattern|evacuation"
            ]["mean"]
            <= 0,
            "single_early_rate_mean": summaries["single_override|rate_early"]["mean"],
            "single_late_rate_mean": summaries["single_override|rate_late"]["mean"],
            "limiting_factor": "coverage, not repeated-override dilution",
            "next_hypothesis": (
                "expand fresh one-deviation labels below the early/late rate gap boundary; "
                "keep train/deficit exact and close the evacuation override"
            ),
        },
    }


def main() -> None:
    if not RESULT.exists():
        raise SystemExit(f"missing D41e result: {RESULT}")
    if sha256(RESULT) != EXPECTED_RESULT_SHA256:
        raise SystemExit("D41e result changed before mechanism analysis")
    if OUTPUT.exists():
        raise SystemExit("refusing to overwrite D41e mechanism artifact")
    result = json.loads(RESULT.read_text())
    if result["pass"] is not False or result["stage_a"]["pass"] is not False:
        raise SystemExit("D41e mechanism analysis expects a rejected Stage A")
    candidate = result["stage_a"]["candidate_a"]["episodes_detail"]
    baseline = result["stage_a"]["d40"]["episodes_detail"]
    report = {
        "result": str(RESULT),
        "result_sha256": sha256(RESULT),
        "analysis": analyze(candidate, baseline),
        "scope": "consumed D41e Stage-A diagnosis only; no policy qualification or platform action",
    }
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
