#!/usr/bin/env python3
"""Measure the value ceiling of selecting resident or the three-worker policy.

The opponent-name selector is intentionally an information upper bound: arena code does not
receive an opponent label.  Its purpose is to decide whether learning an observable opening
signature is worth another iteration, then to freeze a mapping on discovery seeds and apply it
unchanged to later seeds.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import statistics

from cgauto.norxondor_research_rollout_study import atomic_write, read_rows, summary


RESIDENT = "resident"
THREE_WORKER = "norx_three_worker_resident_challenge"


def policy_rows(rows: list[dict], policy: str) -> dict[tuple[str, int, int], dict]:
    selected = {
        (row["opponent"], row["seed"], row["seat"]): row
        for row in rows
        if row["candidate"] == policy
    }
    if not selected:
        raise ValueError(f"policy {policy!r} is absent")
    return selected


def paired(rows: list[dict]) -> tuple[dict, dict]:
    resident = policy_rows(rows, RESIDENT)
    three_worker = policy_rows(rows, THREE_WORKER)
    if resident.keys() != three_worker.keys():
        missing_resident = sorted(three_worker.keys() - resident.keys())[:3]
        missing_three = sorted(resident.keys() - three_worker.keys())[:3]
        raise ValueError(
            "policy grids differ: "
            f"missing resident={missing_resident}, missing three-worker={missing_three}"
        )
    return resident, three_worker


def fit_opponent_selector(rows: list[dict], minimum_gain: float = 0.0) -> dict[str, str]:
    resident, three_worker = paired(rows)
    deltas: dict[str, list[int]] = defaultdict(list)
    for key, baseline in resident.items():
        deltas[key[0]].append(three_worker[key]["margin"] - baseline["margin"])
    return {
        opponent: THREE_WORKER if statistics.mean(values) > minimum_gain else RESIDENT
        for opponent, values in sorted(deltas.items())
    }


def fit_confident_opponent_selector(rows: list[dict]) -> tuple[dict[str, str], dict]:
    """Select the alternative only when its seed-balanced normal 95% CI clears zero."""
    resident, three_worker = paired(rows)
    by_opponent_seed: dict[tuple[str, int], list[int]] = defaultdict(list)
    for key, baseline in resident.items():
        by_opponent_seed[(key[0], key[1])].append(
            three_worker[key]["margin"] - baseline["margin"]
        )
    by_opponent: dict[str, list[float]] = defaultdict(list)
    for (opponent, _seed), values in by_opponent_seed.items():
        by_opponent[opponent].append(statistics.mean(values))

    evidence = {}
    selector = {}
    for opponent, values in sorted(by_opponent.items()):
        mean = statistics.mean(values)
        standard_error = statistics.stdev(values) / len(values) ** 0.5
        lower95 = mean - 1.96 * standard_error
        evidence[opponent] = {
            "seeds": len(values),
            "mean_delta": mean,
            "standard_error": standard_error,
            "normal_95_lower": lower95,
        }
        selector[opponent] = THREE_WORKER if lower95 > 0 else RESIDENT
    return selector, evidence


def evaluate(rows: list[dict], selector: dict[str, str] | None = None) -> dict:
    resident, three_worker = paired(rows)
    keys = sorted(resident)
    resident_margins = [resident[key]["margin"] for key in keys]
    three_margins = [three_worker[key]["margin"] for key in keys]
    deltas = [three_worker[key]["margin"] - resident[key]["margin"] for key in keys]

    opponent_deltas: dict[str, list[int]] = defaultdict(list)
    for key, delta in zip(keys, deltas, strict=True):
        opponent_deltas[key[0]].append(delta)
    mean_opponent_deltas = {
        opponent: statistics.mean(values)
        for opponent, values in sorted(opponent_deltas.items())
    }

    oracle_margins = []
    oracle_alternative = 0
    oracle_resident = 0
    oracle_ties = 0
    for key in keys:
        left = resident[key]["margin"]
        right = three_worker[key]["margin"]
        oracle_margins.append(max(left, right))
        if right > left:
            oracle_alternative += 1
        elif left > right:
            oracle_resident += 1
        else:
            oracle_ties += 1

    result = {
        "cells": len(keys),
        "seeds": len({key[1] for key in keys}),
        "resident_margin": summary(resident_margins),
        "three_worker_margin": summary(three_margins),
        "three_worker_delta_vs_resident": summary(deltas),
        "three_worker_opponent_mean_deltas": mean_opponent_deltas,
        "cell_oracle": {
            "margin": summary(oracle_margins),
            "mean_gain_vs_resident": statistics.mean(oracle_margins)
            - statistics.mean(resident_margins),
            "selected_three_worker": oracle_alternative,
            "selected_resident": oracle_resident,
            "ties": oracle_ties,
        },
    }

    if selector is not None:
        expected = set(mean_opponent_deltas)
        if set(selector) != expected:
            raise ValueError(
                f"selector opponents differ: expected={sorted(expected)}, got={sorted(selector)}"
            )
        selected_margins = []
        selected_deltas = []
        selected_by_opponent: dict[str, list[int]] = defaultdict(list)
        for key in keys:
            chosen = resident if selector[key[0]] == RESIDENT else three_worker
            margin = chosen[key]["margin"]
            delta = margin - resident[key]["margin"]
            selected_margins.append(margin)
            selected_deltas.append(delta)
            selected_by_opponent[key[0]].append(delta)
        selected_opponent_deltas = {
            opponent: statistics.mean(values)
            for opponent, values in sorted(selected_by_opponent.items())
        }
        result["frozen_opponent_selector"] = {
            "mapping": selector,
            "margin": summary(selected_margins),
            "delta_vs_resident": summary(selected_deltas),
            "opponent_mean_deltas": selected_opponent_deltas,
            "worst_opponent_mean_delta": min(selected_opponent_deltas.values()),
            "nonnegative_opponents": sum(
                value >= 0 for value in selected_opponent_deltas.values()
            ),
        }
    return result


def analyze(
    rows: list[dict], discovery_seed_count: int, selector_method: str = "sign"
) -> dict:
    seeds = sorted({row["seed"] for row in rows})
    if not (0 < discovery_seed_count < len(seeds)):
        raise ValueError("discovery seed count must leave a nonempty validation block")
    discovery_seeds = set(seeds[:discovery_seed_count])
    validation_seeds = set(seeds[discovery_seed_count:])
    discovery = [row for row in rows if row["seed"] in discovery_seeds]
    validation = [row for row in rows if row["seed"] in validation_seeds]

    if selector_method == "sign":
        selector = fit_opponent_selector(discovery)
        selector_fit = {
            "method": "positive opponent mean delta",
            "evidence": None,
        }
    elif selector_method == "lower95":
        selector, evidence = fit_confident_opponent_selector(discovery)
        selector_fit = {
            "method": "positive seed-balanced normal 95% lower bound",
            "evidence": evidence,
        }
    else:
        raise ValueError(f"unknown selector method {selector_method!r}")
    discovery_report = evaluate(discovery, selector)
    validation_report = evaluate(validation, selector)
    validation_selector = validation_report["frozen_opponent_selector"]
    if selector_method == "sign":
        validation_mapping = fit_opponent_selector(validation)
        stability_requirement = "the sign-derived opponent mapping is unchanged on validation"
        stable_mapping = validation_mapping == selector
    else:
        validation_mapping, _ = fit_confident_opponent_selector(validation)
        validation_deltas = validation_report["three_worker_opponent_mean_deltas"]
        stability_requirement = (
            "every alternative branch selected by the discovery lower bound remains positive "
            "on validation"
        )
        stable_mapping = all(
            policy == RESIDENT or validation_deltas[opponent] > 0
            for opponent, policy in selector.items()
        )
    continue_gate = (
        validation_selector["delta_vs_resident"]["mean"] > 0
        and validation_selector["nonnegative_opponents"] == len(selector)
        and validation_selector["worst_opponent_mean_delta"] >= -5
        and stable_mapping
    )
    return {
        "schema": 1,
        "scope": (
            "exact-engine generated-map information-value study; the opponent identity used by "
            "the upper-bound selector is not supplied to an arena bot and must be replaced by "
            "state-observable opening evidence before implementation"
        ),
        "policies": {"resident": RESIDENT, "alternative": THREE_WORKER},
        "split": {
            "discovery_seeds": [min(discovery_seeds), max(discovery_seeds)],
            "validation_seeds": [min(validation_seeds), max(validation_seeds)],
        },
        "frozen_selector": selector,
        "selector_fit": selector_fit,
        "validation_refit_selector": validation_mapping,
        "discovery": discovery_report,
        "validation": validation_report,
        "opening_signature_gate": {
            "requirements": [
                "positive frozen-selector mean margin delta on later seeds",
                "nonnegative mean delta for every opponent under the frozen mapping",
                "worst opponent mean delta at least -5",
                stability_requirement,
            ],
            "passed": continue_gate,
        },
        "decision": {
            "build_observable_opening_signature_study": continue_gate,
            "build_online_selector": False,
            "build_submission_candidate": False,
            "reason": (
                "The label-aware selector is an information ceiling, not deployable evidence. "
                "Continue only by proving that the needed archetypes can be classified from "
                "commands and state observed before the workforce commitment becomes irreversible."
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, nargs="+")
    parser.add_argument("--discovery-seeds", type=int, required=True)
    parser.add_argument(
        "--selector-method", choices=("sign", "lower95"), default="sign"
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = [row for path in args.input for row in read_rows(path)]
    payload = analyze(rows, args.discovery_seeds, args.selector_method)
    atomic_write(args.output, json.dumps(payload, indent=1) + "\n")
    compact = {
        "split": payload["split"],
        "mapping": payload["frozen_selector"],
        "discovery_gain": payload["discovery"]["frozen_opponent_selector"]
        ["delta_vs_resident"]["mean"],
        "validation_gain": payload["validation"]["frozen_opponent_selector"]
        ["delta_vs_resident"]["mean"],
        "validation_cell_oracle_gain": payload["validation"]["cell_oracle"]
        ["mean_gain_vs_resident"],
        "gate": payload["opening_signature_gate"],
        "decision": payload["decision"],
    }
    print(json.dumps(compact, indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
