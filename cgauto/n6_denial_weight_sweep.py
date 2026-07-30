#!/usr/bin/env python3
"""N6 denial-distance weight source materializer and paired-panel analyzer.

The only source mutation this tool permits is the exact live focus-denial scalar:
450 (LOW), unchanged 900 (CONTROL), or 1800 (HIGH). Development selects at most one
non-control arm on fresh maps; confirmation uses a separate fresh range.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path
import random
import statistics
import sys


REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.waste_sweep import DETECTORS, build_decoded_game  # noqa: E402

RESIDENT = REPO / "rust/src/d171a_control_resident_snapshot.rs"
RESIDENT_SHA256 = "fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f"
TARGET_LINE = "score += 900.0 / (1 + opponent_distance) as f64;"
CRATE_ALLOW_LINE = "#![allow(dead_code, unused_imports)]\n"
WEIGHTS = {"low": 450, "control": 900, "high": 1800}
DEVELOPMENT_START = 9_858_000
DEVELOPMENT_MAPS = 32
CONFIRMATION_START = 9_859_000
CONFIRMATION_MAPS = 128
FAMILIES = 8
SEATS = 2
BOOTSTRAP_REPS = 20_000
BOOTSTRAP_SEED = 20_260_730


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def materialize_source(source: str, weight: int) -> str:
    if weight not in WEIGHTS.values():
        raise ValueError(f"unsupported weight: {weight}")
    if source.count(TARGET_LINE) != 1:
        raise ValueError(
            f"expected one denial-weight target, found {source.count(TARGET_LINE)}"
        )
    if weight == 900:
        transformed = source
    else:
        replacement = (
            f"score += {weight}.0 / (1 + opponent_distance) as f64;"
        )
        transformed = source.replace(
            TARGET_LINE,
            replacement,
        )
    expected = (
        source
        if weight == 900
        else source.replace(TARGET_LINE, replacement, 1)
    )
    if transformed != expected:
        raise AssertionError("materializer changed bytes outside the exact scalar")
    return transformed


def module_compatible_source(source: str) -> str:
    """Remove the crate-only allow attribute; the runner puts it on each module."""

    if not source.startswith(CRATE_ALLOW_LINE):
        raise ValueError("resident is missing the expected leading crate allow attribute")
    return source[len(CRATE_ALLOW_LINE) :]


def materialize(args: argparse.Namespace) -> int:
    actual = sha256_file(args.resident)
    if actual != RESIDENT_SHA256:
        raise SystemExit(f"resident hash mismatch: {actual}")
    source = module_compatible_source(args.resident.read_text())
    outputs = {
        "low": args.low_output,
        "control": args.control_output,
        "high": args.high_output,
    }
    result = {"resident_sha256": actual, "outputs": {}}
    for arm, path in outputs.items():
        text = materialize_source(source, WEIGHTS[arm])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        result["outputs"][arm] = {
            "weight": WEIGHTS[arm],
            "sha256": hashlib.sha256(text.encode()).hexdigest(),
            "bytes": len(text.encode()),
        }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def truth(value: str | int | bool | None) -> bool:
    return str(value).lower() in {"1", "true", "yes"}


def reason_counts(value: str | None) -> dict[str, int]:
    counts = {}
    for field in (value or "").split(","):
        if not field:
            continue
        reason, count = field.rsplit("=", 1)
        counts[reason] = int(count)
    return counts


def read_rows(path: Path) -> list[dict]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def task_key(row: dict) -> tuple[int, int, int]:
    return (int(row["map_seed"]), int(row["seat"]), int(row["opponent_index"]))


def expected_task_set(start: int, maps: int) -> set[tuple[int, int, int]]:
    return {
        (seed, seat, family)
        for seed in range(start, start + maps)
        for seat in range(SEATS)
        for family in range(FAMILIES)
    }


def arm_index(rows: list[dict]) -> tuple[dict, list[str]]:
    indexed = {}
    duplicates = []
    for row in rows:
        key = (*task_key(row), row["arm"])
        if key in indexed:
            duplicates.append(":".join(map(str, key)))
        indexed[key] = row
    return indexed, duplicates


def mean(values) -> float | None:
    values = list(values)
    return statistics.mean(values) if values else None


def paired_rows(rows: list[dict], arm: str) -> list[dict]:
    indexed, _duplicates = arm_index(rows)
    tasks = sorted({task_key(row) for row in rows})
    out = []
    for task in tasks:
        control = indexed.get((*task, "control"))
        candidate = indexed.get((*task, arm))
        if not control or not candidate:
            continue
        candidate_reasons = reason_counts(candidate.get("legality_reason_counts"))
        control_reasons = reason_counts(control.get("legality_reason_counts"))
        out.append(
            {
                "task": task,
                "map_seed": task[0],
                "seat": task[1],
                "opponent_index": task[2],
                "margin_delta": int(candidate["margin"]) - int(control["margin"]),
                "own_score_delta": int(candidate["own_score"])
                - int(control["own_score"]),
                "opponent_score_delta": int(candidate["opponent_score"])
                - int(control["opponent_score"]),
                "diverged": truth(candidate.get("command_diverged")),
                "common_state": truth(candidate.get("first_divergence_common_state")),
                "both_focus": truth(candidate.get("first_both_focus")),
                "directional_comparable": truth(
                    candidate.get("first_directional_comparable")
                ),
                "directional": truth(candidate.get("first_directional")),
                "opponent_command_mismatch": truth(
                    candidate.get("opponent_command_mismatch")
                ),
                "candidate_done": truth(candidate.get("done")),
                "control_done": truth(control.get("done")),
                "candidate_critical": int(candidate.get("critical_issues") or 0),
                "control_critical": int(control.get("critical_issues") or 0),
                "candidate_unclassified": int(
                    candidate.get("unclassified_issues") or 0
                ),
                "control_unclassified": int(control.get("unclassified_issues") or 0),
                "candidate_issues": int(candidate.get("legality_issues") or 0),
                "control_issues": int(control.get("legality_issues") or 0),
                "candidate_ownership_issues": candidate_reasons.get(
                    "unit_not_owned", 0
                ),
                "control_ownership_issues": control_reasons.get("unit_not_owned", 0),
            }
        )
    return out


def summarize_development_arm(pairs: list[dict], arm: str) -> dict:
    directional = [
        row
        for row in pairs
        if row["directional_comparable"] and row["common_state"]
    ]
    by_seat = {
        str(seat): mean(row["margin_delta"] for row in pairs if row["seat"] == seat)
        for seat in (0, 1)
    }
    by_family = {
        str(family): mean(
            row["margin_delta"] for row in pairs if row["opponent_index"] == family
        )
        for family in range(FAMILIES)
    }
    issue_integrity = all(
        row["candidate_done"]
        and row["control_done"]
        and row["candidate_critical"] == 0
        and row["control_critical"] == 0
        and row["candidate_unclassified"] == 0
        and row["control_unclassified"] == 0
        and row["candidate_ownership_issues"] == 0
        and row["control_ownership_issues"] == 0
        and not row["opponent_command_mismatch"]
        and (not row["diverged"] or row["common_state"])
        for row in pairs
    )
    task_count = len(pairs)
    gates = {
        "paired_tasks_complete": task_count
        == DEVELOPMENT_MAPS * SEATS * FAMILIES,
        "command_divergence_ge_5pct": (
            sum(row["diverged"] for row in pairs) / task_count >= 0.05
            if task_count
            else False
        ),
        "directional_first_divergence_ge_60pct": (
            sum(row["directional"] for row in directional) / len(directional) >= 0.60
            if directional
            else False
        ),
        "paired_mean_positive": (
            mean(row["margin_delta"] for row in pairs) or 0.0
        )
        > 0,
        "both_seats_positive": all(
            value is not None and value > 0 for value in by_seat.values()
        ),
        "six_families_positive": sum(
            value is not None and value > 0 for value in by_family.values()
        )
        >= 6,
        "issue_and_terminal_integrity": issue_integrity,
    }
    return {
        "arm": arm,
        "weight": WEIGHTS[arm],
        "paired_tasks": task_count,
        "command_divergence_tasks": sum(row["diverged"] for row in pairs),
        "common_state_directionally_comparable_divergences": len(directional),
        "directional_focus_divergences": sum(
            row["directional"] for row in directional
        ),
        "paired_mean_margin_delta": mean(row["margin_delta"] for row in pairs),
        "paired_mean_own_score_delta": mean(
            row["own_score_delta"] for row in pairs
        ),
        "paired_mean_opponent_score_delta": mean(
            row["opponent_score_delta"] for row in pairs
        ),
        "margin_delta_by_seat": by_seat,
        "margin_delta_by_family": by_family,
        "gates": gates,
        "eligible": all(gates.values()),
    }


def choose_development_arm(summaries: list[dict]) -> str | None:
    eligible = [row for row in summaries if row["eligible"]]
    if not eligible:
        return None
    eligible.sort(
        key=lambda row: (
            -row["paired_mean_margin_delta"],
            abs(row["weight"] - 900),
            row["weight"],
        )
    )
    return eligible[0]["arm"]


def analyze_development_rows(rows: list[dict]) -> dict:
    indexed, duplicates = arm_index(rows)
    expected_tasks = DEVELOPMENT_MAPS * SEATS * FAMILIES
    observed_tasks = {task_key(row) for row in rows}
    expected_tasks_set = expected_task_set(DEVELOPMENT_START, DEVELOPMENT_MAPS)
    arm_counts = {
        arm: sum(row["arm"] == arm for row in rows)
        for arm in ("low", "control", "high")
    }
    summaries = [
        summarize_development_arm(paired_rows(rows, arm), arm)
        for arm in ("low", "high")
    ]
    selected = choose_development_arm(summaries)
    source_integrity = (
        not duplicates
        and observed_tasks == expected_tasks_set
        and all(arm_counts[arm] == expected_tasks for arm in arm_counts)
        and len(indexed) == expected_tasks * 3
    )
    if not source_integrity:
        verdict = "UNIDENTIFIABLE"
        selected = None
    elif selected is None:
        verdict = "CLOSED_AT_DEVELOPMENT"
    else:
        verdict = "SELECTED_FOR_CONFIRMATION"
    return {
        "schema": "troll-farm-n6-development-v1",
        "verdict": verdict,
        "selected_arm": selected,
        "source_integrity": source_integrity,
        "duplicates": duplicates,
        "observed_tasks": len(observed_tasks),
        "arm_counts": arm_counts,
        "arms": {row["arm"]: row for row in summaries},
    }


def percentile(values: list[float], probability: float) -> float:
    values = sorted(values)
    if not values:
        raise ValueError("percentile requires values")
    position = (len(values) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return values[lower]
    weight = position - lower
    return values[lower] * (1 - weight) + values[upper] * weight


def map_cluster_interval(
    pairs: list[dict], reps: int = BOOTSTRAP_REPS, seed: int = BOOTSTRAP_SEED
) -> dict:
    by_map = defaultdict(list)
    for row in pairs:
        by_map[row["map_seed"]].append(row["margin_delta"])
    maps = sorted(by_map)
    rng = random.Random(seed)
    draws = []
    for _ in range(reps):
        values = [
            value
            for _ in maps
            for value in by_map[maps[rng.randrange(len(maps))]]
        ]
        draws.append(statistics.mean(values))
    return {
        "mean": statistics.mean(row["margin_delta"] for row in pairs),
        "ci_lo": percentile(draws, 0.025),
        "ci_hi": percentile(draws, 0.975),
        "reps": reps,
        "seed": seed,
    }


def _expand_unit(values: list) -> dict:
    return {
        "id": values[0],
        "player": values[1],
        "x": values[2],
        "y": values[3],
        "ms": values[4],
        "cc": values[5],
        "hp": values[6],
        "chop": values[7],
        "carry": values[8:14],
    }


def _expand_plant(values: list) -> dict:
    return {
        "x": values[0],
        "y": values[1],
        "type": values[2],
        "size": values[3],
        "health": values[4],
        "fruits": values[5],
        "cooldown": values[6],
    }


def _expand_state(raw: dict) -> dict:
    return {
        "units": [_expand_unit(unit) for unit in raw["u"]],
        "plants": [_expand_plant(plant) for plant in raw["p"]],
        "inventories": raw["b"],
    }


def decode_trajectory_record(record: dict):
    states = [_expand_state(state) for state in record["states"]]
    trajectory = [
        {
            "commands0": ";".join(record["c0"][index]),
            "commands1": ";".join(record["c1"][index]),
        }
        for index in range(len(record["c0"]))
    ]
    me = int(record["seat"])
    opponent = 1 - me
    scores = [int(value) for value in record["scores"]]
    margin = scores[me] - scores[opponent]
    ranks = [0, 0]
    if margin > 0:
        ranks[me], ranks[opponent] = 0, 1
    elif margin < 0:
        ranks[me], ranks[opponent] = 1, 0
    arm_offset = {"control": 0, "low": 10_000_000, "high": 20_000_000}[
        record["arm"]
    ]
    game_id = (
        (int(record["seed"]) - CONFIRMATION_START) * SEATS * FAMILIES
        + me * FAMILIES
        + int(record["opp"])
        + arm_offset
    )
    return build_decoded_game(
        game_id=game_id,
        me=me,
        map_rows=record["map_rows"],
        states=states,
        trajectory=trajectory,
        scores=scores,
        ranks=ranks,
        opponent_name=record["opp_name"],
    )


def trajectory_detector_summary(
    path: Path,
    rows: list[dict],
    selected_arm: str,
    *,
    start: int = CONFIRMATION_START,
    maps: int = CONFIRMATION_MAPS,
) -> dict:
    indexed, _duplicates = arm_index(rows)
    expected_tasks = expected_task_set(start, maps)
    expected = {
        (*task, arm)
        for task in expected_tasks
        for arm in ("control", selected_arm)
    }
    seen = set()
    duplicates = []
    errors = []
    episodes: dict[str, Counter[str]] = {
        arm: Counter() for arm in ("control", selected_arm)
    }
    flagged_turns: dict[str, Counter[str]] = {
        arm: Counter() for arm in ("control", selected_arm)
    }
    record_counts = Counter()
    with path.open() as source:
        for line_number, line in enumerate(source, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
                key = (
                    int(record["seed"]),
                    int(record["seat"]),
                    int(record["opp"]),
                    record["arm"],
                )
                if key in seen:
                    duplicates.append(list(key))
                seen.add(key)
                if key not in expected:
                    raise ValueError(f"unexpected trajectory key {key!r}")
                row = indexed[key]
                if record["opp_name"] != row["opponent"]:
                    raise ValueError("opponent label mismatch")
                if int(record["turns"]) != int(row["turn"]) - 1:
                    raise ValueError("turn count mismatch")
                if len(record["states"]) != int(record["turns"]) + 1:
                    raise ValueError("state count mismatch")
                if len(record["c0"]) != int(record["turns"]):
                    raise ValueError("player-zero command count mismatch")
                if len(record["c1"]) != int(record["turns"]):
                    raise ValueError("player-one command count mismatch")
                expected_scores = (
                    [int(row["own_score"]), int(row["opponent_score"])]
                    if int(row["seat"]) == 0
                    else [int(row["opponent_score"]), int(row["own_score"])]
                )
                if record["scores"] != expected_scores:
                    raise ValueError("score mismatch")
                decoded = decode_trajectory_record(record)
                arm = record["arm"]
                record_counts[arm] += 1
                for detector_name, detector in DETECTORS.items():
                    found = detector(decoded)
                    episodes[arm][detector_name] += len(found)
                    flagged_turns[arm][detector_name] += sum(
                        episode["duration"] for episode in found
                    )
            except Exception as error:
                if len(errors) < 20:
                    errors.append(
                        {
                            "line": line_number,
                            "error": f"{type(error).__name__}: {error}",
                        }
                    )
    missing = expected - seen
    unexpected = seen - expected
    coverage_pass = (
        seen == expected
        and not duplicates
        and not errors
        and all(
            record_counts[arm] == len(expected_tasks)
            for arm in ("control", selected_arm)
        )
    )
    detector_gates = {}
    for detector_name in sorted(DETECTORS):
        control_rate = (
            episodes["control"][detector_name] / record_counts["control"]
            if record_counts["control"]
            else math.inf
        )
        candidate_rate = (
            episodes[selected_arm][detector_name] / record_counts[selected_arm]
            if record_counts[selected_arm]
            else math.inf
        )
        detector_gates[detector_name] = {
            "control_episode_rate": control_rate,
            "candidate_episode_rate": candidate_rate,
            "candidate_le_1_10x_control": candidate_rate <= 1.10 * control_rate,
        }
    detector_pass = len(DETECTORS) == 6 and all(
        gate["candidate_le_1_10x_control"] for gate in detector_gates.values()
    )
    return {
        "path": str(path),
        "sha256": sha256_file(path),
        "records": sum(record_counts.values()),
        "records_by_arm": dict(record_counts),
        "missing_records": [list(key) for key in sorted(missing)[:20]],
        "unexpected_records": [list(key) for key in sorted(unexpected)[:20]],
        "duplicate_records": duplicates[:20],
        "decode_or_detector_errors": errors,
        "episodes": {
            arm: dict(episodes[arm]) for arm in ("control", selected_arm)
        },
        "flagged_turns": {
            arm: dict(flagged_turns[arm]) for arm in ("control", selected_arm)
        },
        "detector_gates": detector_gates,
        "coverage_pass": coverage_pass,
        "detector_rate_pass": detector_pass,
        "pass": coverage_pass and detector_pass,
    }


def analyze_confirmation_rows(
    rows: list[dict],
    selected_arm: str,
    *,
    bootstrap_reps: int = BOOTSTRAP_REPS,
    thread_byte_identity: bool = False,
    detector_summary: dict | None = None,
) -> dict:
    if selected_arm not in {"low", "high"}:
        raise ValueError("confirmation arm must be low or high")
    indexed, duplicates = arm_index(rows)
    pairs = paired_rows(rows, selected_arm)
    expected_tasks = CONFIRMATION_MAPS * SEATS * FAMILIES
    observed_tasks = {task_key(row) for row in rows}
    expected_tasks_set = expected_task_set(CONFIRMATION_START, CONFIRMATION_MAPS)
    interval = (
        map_cluster_interval(pairs, reps=bootstrap_reps)
        if pairs
        else {"mean": None, "ci_lo": None, "ci_hi": None}
    )
    mean_own_score_delta = mean(row["own_score_delta"] for row in pairs)
    mean_opponent_score_delta = mean(row["opponent_score_delta"] for row in pairs)
    by_seat = {
        str(seat): mean(row["margin_delta"] for row in pairs if row["seat"] == seat)
        for seat in (0, 1)
    }
    by_family_margin = {
        str(family): mean(
            row["margin_delta"] for row in pairs if row["opponent_index"] == family
        )
        for family in range(FAMILIES)
    }
    by_family_opponent = {
        str(family): mean(
            row["opponent_score_delta"]
            for row in pairs
            if row["opponent_index"] == family
        )
        for family in range(FAMILIES)
    }
    directional = [
        row
        for row in pairs
        if row["directional_comparable"] and row["common_state"]
    ]
    source_integrity = (
        not duplicates
        and len(pairs) == expected_tasks
        and observed_tasks == expected_tasks_set
        and len(indexed) == expected_tasks * 2
    )
    control_negative = sum(
        max(0, -int(indexed[(*row["task"], "control")]["margin"])) for row in pairs
    )
    candidate_negative = sum(
        max(0, -int(indexed[(*row["task"], selected_arm)]["margin"]))
        for row in pairs
    )
    control_catastrophes = sum(
        int(indexed[(*row["task"], "control")]["margin"]) <= -100 for row in pairs
    )
    candidate_catastrophes = sum(
        int(indexed[(*row["task"], selected_arm)]["margin"]) <= -100 for row in pairs
    )
    candidate_issues = sum(row["candidate_issues"] for row in pairs)
    control_issues = sum(row["control_issues"] for row in pairs)
    gates = {
        "source_and_task_integrity": source_integrity,
        "critical_unclassified_terminal_integrity": all(
            row["candidate_done"]
            and row["control_done"]
            and row["candidate_critical"] == 0
            and row["control_critical"] == 0
            and row["candidate_unclassified"] == 0
            and row["control_unclassified"] == 0
            and row["candidate_ownership_issues"] == 0
            and row["control_ownership_issues"] == 0
            for row in pairs
        ),
        "noncritical_issues_le_1_10x": candidate_issues
        <= 1.10 * control_issues,
        "first_divergence_attributable": all(
            not row["opponent_command_mismatch"]
            and (not row["diverged"] or row["common_state"])
            for row in pairs
        ),
        "command_divergence_ge_5pct": (
            sum(row["diverged"] for row in pairs) / len(pairs) >= 0.05
            if pairs
            else False
        ),
        "directional_first_divergence_ge_60pct": (
            sum(row["directional"] for row in directional) / len(directional) >= 0.60
            if directional
            else False
        ),
        "opponent_score_delta_le_minus_1": (
            mean_opponent_score_delta or 0
        )
        <= -1,
        "six_family_opponent_deltas_nonpositive": sum(
            value is not None and value <= 0 for value in by_family_opponent.values()
        )
        >= 6,
        "margin_delta_ge_20": interval["mean"] is not None
        and interval["mean"] >= 20,
        "bootstrap_ci_lower_gt_0": interval["ci_lo"] is not None
        and interval["ci_lo"] > 0,
        "both_seats_positive": all(
            value is not None and value > 0 for value in by_seat.values()
        ),
        "worst_family_margin_ge_minus_5": all(
            value is not None and value >= -5 for value in by_family_margin.values()
        ),
        "own_score_delta_ge_minus_5": (
            mean_own_score_delta is not None and mean_own_score_delta >= -5
        ),
        "catastrophes_not_worse": candidate_catastrophes <= control_catastrophes,
        "negative_mass_le_1_05x": candidate_negative <= 1.05 * control_negative,
    }
    gates["thread_byte_identity"] = thread_byte_identity
    gates["six_waste_detectors_pass"] = bool(
        detector_summary and detector_summary.get("pass")
    )
    integrity_keys = (
        "source_and_task_integrity",
        "critical_unclassified_terminal_integrity",
        "noncritical_issues_le_1_10x",
        "first_divergence_attributable",
        "thread_byte_identity",
        "six_waste_detectors_pass",
    )
    mechanism_keys = (
        "command_divergence_ge_5pct",
        "directional_first_divergence_ge_60pct",
        "opponent_score_delta_le_minus_1",
        "six_family_opponent_deltas_nonpositive",
    )
    if not all(gates[key] for key in integrity_keys + mechanism_keys):
        verdict = "CLOSED_AT_MECHANISM"
    elif all(gates.values()):
        verdict = "QUALIFIED"
    else:
        verdict = "CLOSED_AT_VALUE"
    return {
        "schema": "troll-farm-n6-confirmation-v1",
        "selected_arm": selected_arm,
        "verdict": verdict,
        "paired_tasks": len(pairs),
        "interval": interval,
        "mean_own_score_delta": mean_own_score_delta,
        "mean_opponent_score_delta": mean_opponent_score_delta,
        "margin_delta_by_seat": by_seat,
        "margin_delta_by_family": by_family_margin,
        "opponent_score_delta_by_family": by_family_opponent,
        "control_catastrophes": control_catastrophes,
        "candidate_catastrophes": candidate_catastrophes,
        "control_negative_mass": control_negative,
        "candidate_negative_mass": candidate_negative,
        "thread_byte_identity": thread_byte_identity,
        "trajectory_detectors": detector_summary,
        "gates": gates,
    }


def self_test() -> None:
    source = f"prefix\n{TARGET_LINE}\nsuffix\n"
    assert materialize_source(source, 900) == source
    assert "450.0" in materialize_source(source, 450)
    try:
        materialize_source(source + TARGET_LINE, 1800)
    except ValueError:
        pass
    else:
        raise AssertionError("duplicate anchor did not fail")

    rows = []
    for seed in range(DEVELOPMENT_START, DEVELOPMENT_START + DEVELOPMENT_MAPS):
        for seat in range(SEATS):
            for family in range(FAMILIES):
                for arm, margin in (("control", 0), ("low", 2), ("high", -1)):
                    rows.append(
                        {
                            "map_seed": str(seed),
                            "seat": str(seat),
                            "opponent_index": str(family),
                            "arm": arm,
                            "margin": str(margin),
                            "own_score": str(100 + margin),
                            "opponent_score": "100",
                            "done": "1",
                            "critical_issues": "0",
                            "unclassified_issues": "0",
                            "legality_issues": "0",
                            "command_diverged": "1",
                            "first_divergence_common_state": "1",
                            "first_both_focus": "1",
                            "first_directional_comparable": "1",
                            "first_directional": "1" if arm == "low" else "0",
                            "opponent_command_mismatch": "0",
                            "legality_reason_counts": "",
                        }
                    )
    result = analyze_development_rows(rows)
    assert result["verdict"] == "SELECTED_FOR_CONFIRMATION"
    assert result["selected_arm"] == "low"
    print("self-test: ok")


def write_result(path: Path, result: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"verdict": result["verdict"], "output": str(path)}, sort_keys=True))


def analyze_confirmation(args: argparse.Namespace) -> int:
    rows = read_rows(args.panel)
    thread_byte_identity = args.jobs1.read_bytes() == args.panel.read_bytes()
    detectors = trajectory_detector_summary(
        args.trajectories,
        rows,
        args.selected_arm,
    )
    result = analyze_confirmation_rows(
        rows,
        args.selected_arm,
        bootstrap_reps=args.bootstrap_reps,
        thread_byte_identity=thread_byte_identity,
        detector_summary=detectors,
    )
    result["inputs"] = {
        "jobs1": {
            "path": str(args.jobs1),
            "sha256": sha256_file(args.jobs1),
        },
        "jobs20": {
            "path": str(args.panel),
            "sha256": sha256_file(args.panel),
        },
        "trajectories": {
            "path": str(args.trajectories),
            "sha256": sha256_file(args.trajectories),
        },
    }
    write_result(args.output, result)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    materializer = sub.add_parser("materialize")
    materializer.add_argument("--resident", type=Path, default=RESIDENT)
    materializer.add_argument("--low-output", type=Path, required=True)
    materializer.add_argument("--control-output", type=Path, required=True)
    materializer.add_argument("--high-output", type=Path, required=True)
    materializer.set_defaults(func=materialize)

    development = sub.add_parser("analyze-development")
    development.add_argument("--panel", type=Path, required=True)
    development.add_argument("--output", type=Path, required=True)
    development.set_defaults(
        func=lambda args: (
            write_result(args.output, analyze_development_rows(read_rows(args.panel)))
            or 0
        )
    )

    confirmation = sub.add_parser("analyze-confirmation")
    confirmation.add_argument("--panel", type=Path, required=True)
    confirmation.add_argument("--jobs1", type=Path, required=True)
    confirmation.add_argument("--trajectories", type=Path, required=True)
    confirmation.add_argument("--selected-arm", choices=("low", "high"), required=True)
    confirmation.add_argument("--output", type=Path, required=True)
    confirmation.add_argument("--bootstrap-reps", type=int, default=BOOTSTRAP_REPS)
    confirmation.set_defaults(func=analyze_confirmation)

    test = sub.add_parser("self-test")
    test.set_defaults(func=lambda _args: (self_test() or 0))
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
