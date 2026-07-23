#!/usr/bin/env python3
"""Audit the fixed crop candidate on exact official resident replay states.

The audit is read-only and interprets only the first candidate divergence on a
resident-reproduced prefix.  Historical states after that divergence are not a
candidate rollout and are never treated as counterfactual outcome evidence.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import re
import statistics
import sys
import tempfile


REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.idle_harvest_study import (  # noqa: E402
    compile_source,
    grid_text,
    run_batch,
    turn_text,
)
from cgauto.recent_resident_field_census import (  # noqa: E402
    corpus_parser,
    current_player,
    decoded_states,
    terrain,
    unit_eta,
)
from cgauto.replay_conformance import action_commands  # noqa: E402
from cgauto.replay_state import to_game_state  # noqa: E402
from cgauto.top_player_opening_analysis import bfs  # noqa: E402


CENSUS = (
    REPO
    / "data/analysis/live-agent-6553250/recent-resident-field-census-2026-07-18.json"
)
RESIDENT = (
    REPO
    / "cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs"
)
CANDIDATE = (
    REPO
    / "cgauto/submissions/candidate-agent6553250-opponent-crop-b100-e6-slim.min.rs"
)
DEFAULT_OUTPUT = (
    REPO
    / "data/analysis/live-agent-6553250/"
    "opponent-crop-field-activation-2026-07-18.json"
)
PROBE_RE = re.compile(
    r"^@CROP_SELECT t=(\d+) cell=(-?\d+),(-?\d+) command=(.*)$"
)


def instrument_crop_probe(source: str) -> str:
    before = (
        "let mut selected=MoisanBot::select(by_id,&view.inventories[0]);"
        "MoisanBot::resolve_move_conflicts(view,&mut selected);"
    )
    after = (
        "let crop_probe:BTreeMap<String,Cell>=by_id.values().flatten().filter_map(|candidate|"
        "match candidate.target{Target::Tree(cell)if self.opponent_crops.contains(&cell)=>"
        "Some((candidate.command.clone(),cell)),_=>None,}).collect();"
        "let mut selected=MoisanBot::select(by_id,&view.inventories[0]);"
        "for command in &selected{if let Some(cell)=crop_probe.get(command){"
        'eprintln!("@CROP_SELECT t={} cell={},{} command={}",'
        "view.turn,cell.0,cell.1,command);}}"
        "MoisanBot::resolve_move_conflicts(view,&mut selected);"
    )
    count = source.count(before)
    if count != 1:
        raise ValueError(f"expected one crop-probe selection anchor, found {count}")
    return source.replace(before, after, 1)


def parse_probe_events(stderr: str) -> list[dict]:
    events = []
    for line in stderr.splitlines():
        match = PROBE_RE.match(line.strip())
        if match:
            fields = match[4].split()
            unit_id = None
            if len(fields) >= 2 and fields[0].upper() != "WAIT":
                try:
                    unit_id = int(fields[1])
                except ValueError:
                    pass
            events.append(
                {
                    "turn": int(match[1]),
                    "cell": [int(match[2]), int(match[3])],
                    "command": match[4],
                    "unit_id": unit_id,
                }
            )
    return events


def first_action_divergence(left: list[str], right: list[str]) -> int | None:
    common = min(len(left), len(right))
    for index in range(common):
        if action_commands(left[index]) != action_commands(right[index]):
            return index + 1
    return common + 1 if len(left) != len(right) else None


def active_opponent_crops(census_row: dict, turn: int) -> dict[tuple[int, int], dict]:
    active = {}
    for record in census_row["opponent_crop_records"]:
        death = record["death_turn"]
        if record["birth_turn"] < turn and (death is None or turn <= death):
            active[tuple(record["cell"])] = record
    return active


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
            eta = unit_eta(
                # unit_eta expects distances from the target to every cell.
                bfs(board["walkable"], [cell]),
                unit,
                board["walkable"],
            )
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
        if report["active_attributed_opponent_crop"] and report["within_fixed_eta"]
    ]
    return {
        "events": reports,
        "active_opponent_crops": len(active),
        "explained": bool(explained),
        "explained_events": len(explained),
    }


def game_stream(game: dict) -> tuple[int, list[dict], dict, list[dict], str, int]:
    me = current_player(game)
    if me is None:
        raise ValueError("fixed replay does not contain the resident user")
    parser = corpus_parser()
    _, _, inv0, inv1 = parser.parse_frame0(game["frames"][0]["view"])
    trajectory, _ = parser.extract_turns(game["frames"], inv0, inv1)
    map_data, states, unknown_updates = decoded_states(game, trajectory)
    usable = min(len(states) - 1, len(trajectory))
    views = [to_game_state(map_data, state) for state in states[:usable]]
    stream = grid_text(views[0], me) + "".join(turn_text(view, me) for view in views)
    return me, trajectory[:usable], map_data, states[:usable], stream, unknown_updates


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
        raise RuntimeError("crop probe changed candidate stdout")
    recorded = [row.get(f"commands{me}") or "" for row in trajectory]
    baseline_mismatch = first_action_divergence(resident, recorded)
    candidate_divergence = first_action_divergence(candidate, resident)
    admissible = candidate_divergence is not None and (
        baseline_mismatch is None or candidate_divergence < baseline_mismatch
    )
    explanation = None
    if admissible:
        turn_events = [
            event
            for event in parse_probe_events(probe_stderr)
            if event["turn"] == candidate_divergence
        ]
        explanation = explain_events(
            turn_events,
            census_row,
            map_data,
            states[candidate_divergence - 1],
            candidate_divergence,
        )
    return {
        "game_id": census_row["game_id"],
        "agent_id": census_row["agent_id"],
        "seat": me,
        "opponent": census_row["opponent"],
        "margin": census_row["margin"],
        "turns": len(trajectory),
        "unknown_diff_updates": unknown_updates,
        "resident_full_stream_exact": baseline_mismatch is None,
        "resident_first_mismatch_turn": baseline_mismatch,
        "candidate_first_divergence_turn": candidate_divergence,
        "admissible_first_divergence": admissible,
        "first_divergence_explanation": explanation,
        "opponent_crops": census_row["opponent_crop_summary"]["crops"],
        "opponent_crop_wood": census_row["opponent_crop_summary"][
            "opponent_wood_collected"
        ],
    }


def cohort_name(row: dict) -> str:
    if row["margin"] > 0:
        return "wins"
    if row["margin"] == 0:
        return "ties"
    if row["margin"] <= -100:
        return "catastrophic_losses"
    return "ordinary_losses"


def summarize(rows: list[dict]) -> dict:
    if not rows:
        return {"games": 0}
    activated = [row for row in rows if row["admissible_first_divergence"]]
    turns = [row["candidate_first_divergence_turn"] for row in activated]
    return {
        "games": len(rows),
        "resident_full_stream_exact": sum(
            row["resident_full_stream_exact"] for row in rows
        ),
        "raw_candidate_divergences": sum(
            row["candidate_first_divergence_turn"] is not None for row in rows
        ),
        "admissible_activated_games": len(activated),
        "activation_rate": len(activated) / len(rows),
        "median_first_divergence_turn": statistics.median(turns) if turns else None,
        "mean_opponent_crops": statistics.mean(row["opponent_crops"] for row in rows),
        "mean_opponent_crop_wood": statistics.mean(
            row["opponent_crop_wood"] for row in rows
        ),
        "activated_mean_opponent_crops": (
            statistics.mean(row["opponent_crops"] for row in activated)
            if activated
            else None
        ),
        "activated_mean_opponent_crop_wood": (
            statistics.mean(row["opponent_crop_wood"] for row in activated)
            if activated
            else None
        ),
    }


def analyze(rows: list[dict], fetch_failures: list[dict]) -> dict:
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
        "all_fixed_games_fetched_and_decoded": len(rows) == 80 and not fetch_failures,
        "no_unknown_diff_updates": all(row["unknown_diff_updates"] == 0 for row in rows),
        "minimum_full_resident_reproductions": sum(
            row["resident_full_stream_exact"] for row in rows
        )
        >= 60,
        "minimum_admissible_activations": len(activated) >= 30,
        "minimum_catastrophic_activations": len(catastrophic) >= 8,
        "minimum_catastrophic_opponents": len(
            {row["opponent"] for row in catastrophic}
        )
        >= 3,
        "all_first_divergences_explained_by_active_eta6_crop": len(explained)
        == len(activated),
        "no_production_stderr": True,
    }
    return {
        "schema": 1,
        "scope": (
            "read-only, open-loop first-divergence audit on the fixed 80-game official corpus; "
            "not a candidate outcome replay and not an arena result"
        ),
        "games": len(rows),
        "fetch_failures": fetch_failures,
        "cohorts": {
            name: summarize(groups.get(name, []))
            for name in ("wins", "ties", "ordinary_losses", "catastrophic_losses")
        },
        "aggregate": summarize(rows),
        "admissible_activated_games": len(activated),
        "explained_first_divergences": len(explained),
        "catastrophic_activated_games": len(catastrophic),
        "catastrophic_activated_opponents": sorted(
            {row["opponent"] for row in catastrophic}
        ),
        "prospective_gate_checks": checks,
        "prospective_gate_passed": all(checks.values()),
        "rows": rows,
        "decision": {
            "draft_controlled_transfer_protocol": all(checks.values()),
            "play_or_submit": False,
            "reason": (
                "the fixed candidate activates the attributed official-state mechanism"
                if all(checks.values())
                else "official-state reproduction, coverage, or attribution gate failed"
            ),
        },
    }


def save(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=1) + "\n")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    census = json.loads(CENSUS.read_text())
    fixed_rows = census["rows"]
    if len(fixed_rows) != 80 or {row["agent_id"] for row in fixed_rows} != {6559583}:
        raise SystemExit("field activation corpus is not the frozen 80-game resident set")

    from cgauto import battle_taxonomy as arena

    with tempfile.TemporaryDirectory(prefix="crop-field-activation-") as directory:
        temp = Path(directory)
        resident_binary = temp / "resident"
        candidate_binary = temp / "candidate"
        probe_source = temp / "probe.rs"
        probe_binary = temp / "probe"
        probe_source.write_text(instrument_crop_probe(CANDIDATE.read_text()))
        compile_source(RESIDENT, resident_binary, "crop_field_resident")
        compile_source(CANDIDATE, candidate_binary, "crop_field_candidate")
        compile_source(probe_source, probe_binary, "crop_field_probe")

        rows = []
        failures = []
        for index, census_row in enumerate(fixed_rows, 1):
            game_id = census_row["game_id"]
            try:
                game = arena.call("gameResult/findByGameId", [game_id, None])
                rows.append(
                    audit_game(
                        game,
                        census_row,
                        resident_binary,
                        candidate_binary,
                        probe_binary,
                    )
                )
            except Exception as error:  # noqa: BLE001 - preserve complete read audit
                failures.append(
                    {"game_id": game_id, "error": f"{type(error).__name__}: {error}"}
                )
            if index % 10 == 0 or index == len(fixed_rows):
                print(
                    f"audited {index}/{len(fixed_rows)} fixed official replays "
                    f"({len(failures)} failures)",
                    flush=True,
                )
    payload = analyze(rows, failures)
    save(args.output, payload)
    print(json.dumps({
        "gate": payload["prospective_gate_passed"],
        "aggregate": payload["aggregate"],
        "catastrophic_activated_games": payload["catastrophic_activated_games"],
        "catastrophic_activated_opponents": payload["catastrophic_activated_opponents"],
        "checks": payload["prospective_gate_checks"],
    }, indent=1))
    print(f"saved {args.output}")
    return 0 if payload["prospective_gate_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
