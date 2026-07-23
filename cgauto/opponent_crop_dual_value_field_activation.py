#!/usr/bin/env python3
"""Audit dual-value opponent-crop activation on fixed official resident prefixes."""

from __future__ import annotations

import argparse
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import re
import statistics
import sys
import tempfile


REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto import battle_taxonomy as arena  # noqa: E402
from cgauto.idle_harvest_study import compile_source, run_batch  # noqa: E402
from cgauto.opponent_crop_field_activation import (  # noqa: E402
    active_opponent_crops,
    first_action_divergence,
    game_stream,
)
from cgauto.recent_resident_field_census import terrain, unit_eta  # noqa: E402
from cgauto.replay_conformance import action_commands  # noqa: E402
from cgauto.top_player_opening_analysis import bfs  # noqa: E402


CENSUS = (
    REPO
    / "data/analysis/live-agent-6553250/phase21-control-field-census-2026-07-18.json"
)
RESIDENT = (
    REPO
    / "cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs"
)
CANDIDATE = (
    REPO
    / "cgauto/submissions/"
    "candidate-agent6553250-opponent-crop-dual-value-e6-slim.min.rs"
)
DEFAULT_OUTPUT = (
    REPO
    / "data/analysis/live-agent-6553250/"
    "opponent-crop-dual-value-field-activation-2026-07-19.json"
)
EXPECTED_AGENT = 6560240
PROBE_RE = re.compile(
    r"^@DUAL_SELECT t=(\d+) cell=(-?\d+),(-?\d+) "
    r"score=(-?[0-9.eE+]+) base=(-?[0-9.eE+]+) command=(.*)$"
)


def instrument_dual_value_probe(source: str) -> str:
    before = (
        "let mut selected=MoisanBot::select(by_id,&view.inventories[0]);"
        "MoisanBot::resolve_move_conflicts(view,&mut selected);"
    )
    after = (
        "let dual_probe:BTreeMap<String,(Cell,f64)>=by_id.values().flatten().filter_map("
        "|candidate|match candidate.target{Target::Tree(cell)if self.opponent_crops."
        "contains(&cell)=>Some((candidate.command.clone(),(cell,candidate.score))),_=>None,})"
        ".collect();let mut selected=MoisanBot::select(by_id,&view.inventories[0]);"
        "for command in &selected{if let Some((cell,score))=dual_probe.get(command){"
        'eprintln!("@DUAL_SELECT t={} cell={},{} score={:.9} base={:.9} command={}",'
        "view.turn,cell.0,cell.1,score,score/2.0,command);}}"
        "MoisanBot::resolve_move_conflicts(view,&mut selected);"
    )
    count = source.count(before)
    if count != 1:
        raise ValueError(f"expected one dual-probe selection anchor, found {count}")
    return source.replace(before, after, 1)


def parse_probe_events(stderr: str) -> list[dict]:
    events = []
    for line in stderr.splitlines():
        match = PROBE_RE.match(line.strip())
        if not match:
            continue
        fields = match[6].split()
        unit_id = None
        if len(fields) >= 2 and fields[0].upper() != "WAIT":
            try:
                unit_id = int(fields[1])
            except ValueError:
                pass
        score = float(match[4])
        base = float(match[5])
        events.append(
            {
                "turn": int(match[1]),
                "cell": [int(match[2]), int(match[3])],
                "doubled_score": score,
                "inferred_resident_score": base,
                "score_is_exactly_doubled": abs(score - 2.0 * base) <= 1e-6,
                "command": match[6],
                "unit_id": unit_id,
            }
        )
    return events


def explain_events(
    events: list[dict], census_row: dict, map_data: dict, state: dict, turn: int
) -> dict:
    active = active_opponent_crops(census_row, turn)
    board = terrain(map_data)
    units = {unit["id"]: unit for unit in state["units"]}
    reports = []
    for event in events:
        cell = tuple(event["cell"])
        unit = units.get(event["unit_id"])
        eta = None
        if unit is not None:
            eta = unit_eta(bfs(board["walkable"], [cell]), unit, board["walkable"])
        reports.append(
            {
                **event,
                "active_attributed_opponent_crop": cell in active,
                "current_eta": eta,
                "within_fixed_eta": eta is not None and eta <= 6,
            }
        )
    explained = [
        report
        for report in reports
        if report["active_attributed_opponent_crop"]
        and report["within_fixed_eta"]
        and report["score_is_exactly_doubled"]
    ]
    return {
        "events": reports,
        "active_opponent_crops": len(active),
        "explained": bool(explained),
        "explained_events": len(explained),
    }


def audit_game(
    game: dict,
    census_row: dict,
    resident_binary: Path,
    candidate_binary: Path,
    probe_binary: Path,
) -> dict:
    me, trajectory, map_data, states, stream, unknown_updates = game_stream(game)
    resident, resident_stderr = run_batch(resident_binary, stream)
    candidate, candidate_stderr = run_batch(candidate_binary, stream)
    probe, probe_stderr = run_batch(probe_binary, stream)
    if resident_stderr or candidate_stderr:
        raise RuntimeError("production resident or candidate wrote stderr")
    if probe != candidate:
        raise RuntimeError("dual-value probe changed candidate stdout")
    recorded = [row.get(f"commands{me}") or "" for row in trajectory]
    baseline_mismatch = first_action_divergence(resident, recorded)
    divergence = first_action_divergence(candidate, resident)
    admissible = divergence is not None and (
        baseline_mismatch is None or divergence < baseline_mismatch
    )
    explanation = None
    displaced = None
    if admissible:
        events = [
            event for event in parse_probe_events(probe_stderr) if event["turn"] == divergence
        ]
        explanation = explain_events(
            events, census_row, map_data, states[divergence - 1], divergence
        )
        resident_actions = action_commands(resident[divergence - 1])
        candidate_actions = action_commands(candidate[divergence - 1])
        displaced = {
            "resident_actions": resident_actions,
            "candidate_actions": candidate_actions,
            "removed_resident_actions": sorted(set(resident_actions) - set(candidate_actions)),
            "added_candidate_actions": sorted(set(candidate_actions) - set(resident_actions)),
        }
    return {
        "game_id": int(census_row["game_id"]),
        "agent_id": int(census_row["agent_id"]),
        "seat": me,
        "opponent": census_row["opponent"],
        "margin": int(census_row["margin"]),
        "turns": len(trajectory),
        "unknown_diff_updates": unknown_updates,
        "resident_full_stream_exact": baseline_mismatch is None,
        "resident_first_mismatch_turn": baseline_mismatch,
        "candidate_first_divergence_turn": divergence,
        "admissible_first_divergence": admissible,
        "first_divergence_explanation": explanation,
        "displaced_actions": displaced,
        "opponent_crops": census_row["opponent_crop_summary"]["crops"],
        "opponent_crop_wood": census_row["opponent_crop_summary"][
            "opponent_wood_collected"
        ],
    }


def cohort_name(row: dict) -> str:
    if row["margin"] > 0:
        return "wins"
    if row["margin"] <= -100:
        return "catastrophic_losses"
    return "ordinary_losses"


def summarize(rows: list[dict]) -> dict:
    activated = [row for row in rows if row["admissible_first_divergence"]]
    turns = [row["candidate_first_divergence_turn"] for row in activated]
    return {
        "games": len(rows),
        "resident_full_stream_exact": sum(row["resident_full_stream_exact"] for row in rows),
        "raw_candidate_divergences": sum(
            row["candidate_first_divergence_turn"] is not None for row in rows
        ),
        "admissible_activated_games": len(activated),
        "activation_rate": len(activated) / len(rows) if rows else None,
        "median_first_divergence_turn": statistics.median(turns) if turns else None,
        "mean_opponent_crops": statistics.mean(row["opponent_crops"] for row in rows)
        if rows
        else None,
        "mean_opponent_crop_wood": statistics.mean(
            row["opponent_crop_wood"] for row in rows
        )
        if rows
        else None,
    }


def analyze(rows: list[dict], failures: list[dict], source_rule_exact: bool) -> dict:
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        groups[cohort_name(row)].append(row)
    activated = [row for row in rows if row["admissible_first_divergence"]]
    catastrophic = [row for row in activated if row["margin"] <= -100]
    explained = [
        row
        for row in activated
        if row["first_divergence_explanation"]
        and row["first_divergence_explanation"]["explained"]
    ]
    checks = {
        "all_fixed_games_fetched_and_decoded": len(rows) == 131 and not failures,
        "exact_source_rule": source_rule_exact,
        "no_unknown_diff_updates": all(row["unknown_diff_updates"] == 0 for row in rows),
        "minimum_admissible_activations": len(activated) >= 50,
        "minimum_catastrophic_activations": len(catastrophic) >= 10,
        "minimum_catastrophic_opponents": len({row["opponent"] for row in catastrophic})
        >= 3,
        "all_first_divergences_explained_by_doubled_active_eta6_crop": len(explained)
        == len(activated),
        "no_production_stderr": True,
    }
    passed = all(checks.values())
    return {
        "schema": 1,
        "scope": (
            "read-only first-divergence audit on 131 fixed exact-resident official replays; "
            "historical suffixes are not candidate outcomes"
        ),
        "expected_agent": EXPECTED_AGENT,
        "games": len(rows),
        "fetch_or_audit_failures": failures,
        "source_rule_exact": source_rule_exact,
        "aggregate": summarize(rows),
        "cohorts": {
            name: summarize(groups.get(name, []))
            for name in ("wins", "ordinary_losses", "catastrophic_losses")
        },
        "admissible_activated_games": len(activated),
        "explained_first_divergences": len(explained),
        "catastrophic_activated_games": len(catastrophic),
        "catastrophic_activated_opponents": sorted(
            {row["opponent"] for row in catastrophic}
        ),
        "prospective_gate_checks": checks,
        "prospective_gate_passed": passed,
        "rows": sorted(rows, key=lambda row: row["game_id"]),
        "decision": (
            "freeze a controlled arena protocol"
            if passed
            else "close dual-value scoring without tuning"
        ),
    }


def save(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=1) + "\n")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--jobs", type=int, default=20)
    args = parser.parse_args()
    if not 1 <= args.jobs <= 32:
        raise SystemExit("--jobs must be between 1 and 32")
    census = json.loads(CENSUS.read_text())
    fixed = census.get("rows") or []
    if len(fixed) != 131 or {int(row["agent_id"]) for row in fixed} != {EXPECTED_AGENT}:
        raise SystemExit("census is not the frozen 131-game exact-resident control")
    source = CANDIDATE.read_text()
    rule = "if eta<=6{candidate.score+=candidate.score;}"
    source_rule_exact = source.count(rule) == 1 and "candidate.score+=100" not in source

    with tempfile.TemporaryDirectory(prefix="crop-dual-field-") as directory:
        temp = Path(directory)
        resident_binary = temp / "resident"
        candidate_binary = temp / "candidate"
        probe_source = temp / "probe.rs"
        probe_binary = temp / "probe"
        probe_source.write_text(instrument_dual_value_probe(source))
        compile_source(RESIDENT, resident_binary, "crop_dual_field_resident")
        compile_source(CANDIDATE, candidate_binary, "crop_dual_field_candidate")
        compile_source(probe_source, probe_binary, "crop_dual_field_probe")

        def work(census_row: dict) -> tuple[dict | None, dict | None]:
            game_id = int(census_row["game_id"])
            try:
                game = arena.call("gameResult/findByGameId", [game_id, None])
                return (
                    audit_game(
                        game,
                        census_row,
                        resident_binary,
                        candidate_binary,
                        probe_binary,
                    ),
                    None,
                )
            except Exception as error:  # pragma: no cover - external failure path
                return None, {
                    "game_id": game_id,
                    "error": f"{type(error).__name__}: {error}",
                }

        rows = []
        failures = []
        with ThreadPoolExecutor(max_workers=args.jobs) as executor:
            futures = [executor.submit(work, row) for row in fixed]
            for index, future in enumerate(as_completed(futures), 1):
                row, failure = future.result()
                if row is not None:
                    rows.append(row)
                if failure is not None:
                    failures.append(failure)
                if index % 10 == 0 or index == len(futures):
                    print(
                        f"audited {index}/{len(futures)} fixed official replays "
                        f"({len(failures)} failures)",
                        flush=True,
                    )
    payload = analyze(rows, failures, source_rule_exact)
    save(args.output, payload)
    print(
        json.dumps(
            {
                "gate": payload["prospective_gate_passed"],
                "aggregate": payload["aggregate"],
                "catastrophic_activated_games": payload[
                    "catastrophic_activated_games"
                ],
                "catastrophic_activated_opponents": payload[
                    "catastrophic_activated_opponents"
                ],
                "checks": payload["prospective_gate_checks"],
            },
            indent=1,
        )
    )
    print(f"saved {args.output}")
    return 0 if payload["prospective_gate_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
