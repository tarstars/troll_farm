#!/usr/bin/env python3
"""Audit secure-orchard forced harvesting on a frozen exact-resident arena corpus.

This is a read-only, teacher-forced mechanism audit. It reconstructs official states, runs the
exact resident and a stderr-only probe on those states, and admits probe events only while the
resident still reproduces the recorded command prefix. It never treats historical states after a
candidate change as a counterfactual rollout.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from concurrent.futures import as_completed, ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import statistics
import sys
import tempfile

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.idle_harvest_study import (  # noqa: E402
    compile_source,
    grid_text,
    parse_probe_events,
    run_batch,
    turn_text,
)
from cgauto.make_idle_harvest_probe import instrument_minified  # noqa: E402
from cgauto.opponent_crop_field_activation import first_action_divergence  # noqa: E402
from cgauto.recent_resident_field_census import (  # noqa: E402
    corpus_parser,
    current_player,
    decoded_states,
)
from cgauto.replay_conformance import action_commands  # noqa: E402
from cgauto.replay_state import to_game_state  # noqa: E402


REPO = Path(__file__).resolve().parent.parent
CENSUS = (
    REPO
    / "data/analysis/live-agent-6553250/"
    "recent-resident-restore-field-census-2026-07-19.json"
)
RESIDENT = (
    REPO
    / "cgauto/submissions/"
    "candidate-agent6553250-preseed-orchard-coverage-slim.min.rs"
)
CONTROLLED = REPO / "data/panels/top5-idle-harvest-telemetry.json"
LOCAL = REPO / "data/analysis/live-agent-6553250/idle-harvest-local-study.json"
DEFAULT_OUTPUT = (
    REPO
    / "data/analysis/live-agent-6553250/"
    "secure-orchard-conversion-audit-2026-07-19.json"
)
RESIDENT_AGENT_ID = 6560353
FRUIT_HOARD_GAME_IDS = (896294348, 896294247)
APPLE = 2


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def official_stream(game: dict) -> dict:
    """Return exact pre-action state views and the recorded resident command stream."""

    me = current_player(game)
    if me is None:
        raise ValueError("replay does not contain the resident user")
    parser = corpus_parser()
    _, _, inv0, inv1 = parser.parse_frame0(game["frames"][0]["view"])
    trajectory, _ = parser.extract_turns(game["frames"], inv0, inv1)
    map_data, states, unknown_updates = decoded_states(game, trajectory)
    usable = min(len(states) - 1, len(trajectory))
    views = [to_game_state(map_data, state) for state in states[:usable]]
    stream = grid_text(views[0], me) + "".join(turn_text(view, me) for view in views)
    recorded = [row.get(f"commands{me}") or "" for row in trajectory[:usable]]
    return {
        "seat": me,
        "states": states[: usable + 1],
        "turns": usable,
        "stream": stream,
        "recorded": recorded,
        "unknown_diff_updates": unknown_updates,
    }


def event_is_admissible(turn: int, first_mismatch: int | None) -> bool:
    """The action at the first mismatching turn is not an exact historical attribution."""

    return first_mismatch is None or turn < first_mismatch


def command_for_unit(line: str, unit_id: int, verb: str) -> bool:
    expected = verb.upper()
    for command in action_commands(line):
        fields = command.split()
        if len(fields) >= 2 and fields[0].upper() == expected:
            try:
                if int(fields[1]) == unit_id:
                    return True
            except ValueError:
                pass
    return False


def by_id(state: dict, unit_id: int) -> dict | None:
    return next((unit for unit in state["units"] if unit["id"] == unit_id), None)


def event_detail(event: dict, stream: dict) -> dict:
    """Join one forced action to its official before/after state and next-turn bank."""

    turn = int(event["turn"])
    unit_id = int(event["unit"])
    states = stream["states"]
    if not 1 <= turn < len(states):
        raise ValueError(f"probe event turn {turn} is outside decoded state range")
    before = states[turn - 1]
    after = states[turn]
    unit_before = by_id(before, unit_id)
    unit_after = by_id(after, unit_id)
    if unit_before is None or unit_after is None:
        raise ValueError(f"forced-harvest unit {unit_id} is absent at turn {turn}")
    cell = [unit_before["x"], unit_before["y"]]
    plant = next(
        (
            plant
            for plant in before["plants"]
            if [plant["x"], plant["y"]] == cell
        ),
        None,
    )
    carried_delta = unit_after["carry"][APPLE] - unit_before["carry"][APPLE]
    banked_next_turn = False
    inventory_after_next = None
    if turn < stream["turns"]:
        next_line = stream["recorded"][turn]
        after_next = states[turn + 1]
        inventory_after_next = after_next["inventories"][stream["seat"]][APPLE]
        banked_next_turn = command_for_unit(next_line, unit_id, "DROP") and (
            inventory_after_next > after["inventories"][stream["seat"]][APPLE]
        )
    return {
        **event,
        "cell": cell,
        "mother_is_ripe_apple": bool(
            plant
            and plant["type"] == "APPLE"
            and plant["fruits"] > 0
            and plant["health"] > 0
        ),
        "mother_fruits_before": plant["fruits"] if plant else None,
        "inventory_apple_before": before["inventories"][stream["seat"]][APPLE],
        "inventory_apple_after_harvest": after["inventories"][stream["seat"]][APPLE],
        "inventory_apple_after_next": inventory_after_next,
        "carried_apple_before": unit_before["carry"][APPLE],
        "carried_apple_after": unit_after["carry"][APPLE],
        "successful_apple_amount": max(0, carried_delta),
        "banked_next_turn": banked_next_turn,
    }


def outcome_cohort(row: dict) -> str:
    if row["margin"] > 0:
        return "wins"
    if row["margin"] == 0:
        return "ties"
    if row["margin"] <= -100:
        return "catastrophic_losses"
    return "ordinary_losses"


def audit_game(
    game: dict, census_row: dict, resident_binary: Path, probe_binary: Path
) -> dict:
    stream = official_stream(game)
    resident, resident_stderr = run_batch(resident_binary, stream["stream"])
    probe, probe_stderr = run_batch(probe_binary, stream["stream"])
    if resident_stderr:
        raise RuntimeError("production resident unexpectedly wrote to stderr")
    if resident != probe:
        raise RuntimeError("stderr probe changed resident stdout")
    mismatch = first_action_divergence(resident, stream["recorded"])
    raw_forces = [
        event
        for event in parse_probe_events(probe_stderr)
        if event["kind"] == "orchard_force"
    ]
    admissible = [
        event_detail(event, stream)
        for event in raw_forces
        if event_is_admissible(event["turn"], mismatch)
    ]
    banked = [event for event in admissible if event["banked_next_turn"]]
    replacement_bank_turn = banked[0]["turn"] + 1 if banked else None
    post_replacement = [
        event
        for event in admissible
        if replacement_bank_turn is not None and event["turn"] > replacement_bank_turn
    ]
    first_inventory = admissible[0]["inventory_apple_before"] if admissible else None
    final_apple = census_row["final"]["my"]["inventory"][APPLE]
    forced_success = sum(event["successful_apple_amount"] for event in admissible)
    net_bank_growth = (
        max(0, final_apple - first_inventory) if first_inventory is not None else 0
    )
    return {
        "game_id": census_row["game_id"],
        "agent_id": census_row["agent_id"],
        "seat": stream["seat"],
        "opponent": census_row["opponent"],
        "cohort": outcome_cohort(census_row),
        "margin": census_row["margin"],
        "scores": census_row["scores"],
        "turns": stream["turns"],
        "unknown_diff_updates": stream["unknown_diff_updates"],
        "probe_resident_stdout_equal": True,
        "resident_full_stream_exact": mismatch is None,
        "resident_first_mismatch_turn": mismatch,
        "raw_forced_harvests": len(raw_forces),
        "admissible_forced_harvests": len(admissible),
        "first_force_turn": admissible[0]["turn"] if admissible else None,
        "last_force_turn": admissible[-1]["turn"] if admissible else None,
        "mother_cell": admissible[0]["cell"] if admissible else None,
        "all_forces_on_ripe_apple": all(
            event["mother_is_ripe_apple"] for event in admissible
        ),
        "successful_forced_apple": forced_success,
        "banked_forced_cycles": len(banked),
        "seed_replacement_bank_turn": replacement_bank_turn,
        "post_seed_replacement_forces": len(post_replacement),
        "forced_harvest_explains_net_apple_growth": bool(admissible)
        and forced_success >= net_bank_growth,
        "final": {
            "apple": final_apple,
            "fruit": census_row["final"]["my"]["fruit"],
            "wood": census_row["final"]["my"]["wood"],
            "successful_plants": census_row["final"]["my"]["successful_plants"],
            "opponent_crops": census_row["opponent_crop_summary"]["crops"],
            "opponent_crop_wood": census_row["opponent_crop_summary"][
                "opponent_wood_collected"
            ],
        },
        "events": admissible,
    }


def mean(rows: list[dict], getter) -> float | None:
    values = [getter(row) for row in rows]
    return statistics.mean(values) if values else None


def summarize(rows: list[dict]) -> dict:
    activated = [row for row in rows if row["admissible_forced_harvests"] > 0]
    sustained = [row for row in activated if row["post_seed_replacement_forces"] > 0]
    return {
        "games": len(rows),
        "activated_games": len(activated),
        "sustained_after_seed_replacement_games": len(sustained),
        "activation_rate": len(activated) / len(rows) if rows else None,
        "total_admissible_forced_harvests": sum(
            row["admissible_forced_harvests"] for row in rows
        ),
        "forced_harvest_count_distribution": sorted(
            row["admissible_forced_harvests"] for row in activated
        ),
        "mean_margin": mean(rows, lambda row: row["margin"]),
        "activated_mean_margin": mean(activated, lambda row: row["margin"]),
        "inactive_mean_margin": mean(
            [row for row in rows if row not in activated], lambda row: row["margin"]
        ),
        "activated_mean_final_apple": mean(
            activated, lambda row: row["final"]["apple"]
        ),
        "activated_mean_final_wood": mean(
            activated, lambda row: row["final"]["wood"]
        ),
        "activated_mean_successful_plants": mean(
            activated, lambda row: row["final"]["successful_plants"]
        ),
        "activated_mean_opponent_crops": mean(
            activated, lambda row: row["final"]["opponent_crops"]
        ),
        "activated_mean_opponent_crop_wood": mean(
            activated, lambda row: row["final"]["opponent_crop_wood"]
        ),
    }


def prior_evidence() -> dict:
    controlled = json.loads(CONTROLLED.read_text())
    controlled_active = []
    for row in controlled.get("rows", []):
        count = row.get("telemetry", {}).get("counts", {}).get("orchard_force", 0)
        if count:
            controlled_active.append(
                {
                    "game_id": row["game_id"],
                    "opponent": row["opponent"],
                    "scores": row["scores"],
                    "inventories": row["inventories"],
                    "forced_harvests": count,
                }
            )
    local = json.loads(LOCAL.read_text())
    local_active = []
    for row in local.get("paired", {}).get("rows", []):
        count = row.get("probe_event_counts", {}).get("orchard_force", 0)
        if count:
            local_active.append(
                {
                    "seed": row["seed"],
                    "forced_harvests": count,
                    "paired_margin": row["paired_margin"],
                    "baseline_margins": row["baseline_margins"],
                }
            )
    return {
        "controlled_top_five": controlled_active,
        "deterministic_local": local_active,
    }


def analyze(rows: list[dict], failures: list[dict]) -> dict:
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        groups[row["cohort"]].append(row)
    by_game = {row["game_id"]: row for row in rows}
    fruit_hoard = [by_game.get(game_id) for game_id in FRUIT_HOARD_GAME_IDS]
    fruit_hoard_supported = all(
        row is not None
        and row["post_seed_replacement_forces"] > 0
        and row["forced_harvest_explains_net_apple_growth"]
        for row in fruit_hoard
    )
    checks = {
        "all_frozen_games_fetched_and_decoded": len(rows) == 80 and not failures,
        "all_probe_streams_stdout_neutral": all(
            row["probe_resident_stdout_equal"] for row in rows
        ),
        "zero_unknown_diff_updates": all(
            row["unknown_diff_updates"] == 0 for row in rows
        ),
        "minimum_full_resident_reproductions": sum(
            row["resident_full_stream_exact"] for row in rows
        )
        >= 60,
        "all_admissible_forces_are_ripe_apple": all(
            row["all_forces_on_ripe_apple"] for row in rows
        ),
    }
    integrity = all(checks.values())
    return {
        "schema": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": (
            "read-only exact-resident official-state forced-orchard audit; observational "
            "mechanism attribution, not a counterfactual candidate replay"
        ),
        "corpus": {
            "path": str(CENSUS.relative_to(REPO)),
            "games": 80,
            "resident_agent_id": RESIDENT_AGENT_ID,
            "fruit_hoard_game_ids": list(FRUIT_HOARD_GAME_IDS),
        },
        "source": {
            "path": str(RESIDENT.relative_to(REPO)),
            "bytes": RESIDENT.stat().st_size,
            "sha256": digest(RESIDENT),
        },
        "fetch_failures": failures,
        "integrity_checks": checks,
        "integrity_passed": integrity,
        "aggregate": summarize(rows),
        "cohorts": {
            name: summarize(groups.get(name, []))
            for name in ("wins", "ties", "ordinary_losses", "catastrophic_losses")
        },
        "fruit_hoard_games": [row for row in fruit_hoard if row is not None],
        "fruit_hoard_mechanism_supported": fruit_hoard_supported,
        "prior_mechanism_evidence": prior_evidence(),
        "rows": rows,
        "decision": {
            "freeze_seed_replacement_release_experiment": integrity
            and fruit_hoard_supported,
            "construct_or_submit_candidate": False,
            "reason": (
                "both fresh fruit-hoard catastrophes are exact sustained orchard locks"
                if integrity and fruit_hoard_supported
                else "integrity or direct fruit-hoard attribution failed"
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
    parser.add_argument("--fetch-workers", type=int, default=8)
    parser.add_argument("--audit-workers", type=int, default=16)
    args = parser.parse_args()
    if not 1 <= args.fetch_workers <= 20 or not 1 <= args.audit_workers <= 20:
        parser.error("worker counts must be between 1 and 20")
    census = json.loads(CENSUS.read_text())
    fixed_rows = census.get("rows") or []
    if len(fixed_rows) != 80 or {row["agent_id"] for row in fixed_rows} != {
        RESIDENT_AGENT_ID
    }:
        raise SystemExit("field corpus is not the frozen 80-game exact-resident set")
    if RESIDENT.stat().st_size != 62_725 or digest(RESIDENT) != (
        "a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55"
    ):
        raise SystemExit("exact resident source identity changed")

    from cgauto import battle_taxonomy as arena

    games: dict[int, dict] = {}
    failures = []

    def fetch(row: dict) -> tuple[int, dict]:
        game_id = row["game_id"]
        return game_id, arena.call("gameResult/findByGameId", [game_id, None])

    with ThreadPoolExecutor(max_workers=args.fetch_workers) as executor:
        futures = {executor.submit(fetch, row): row for row in fixed_rows}
        for index, future in enumerate(as_completed(futures), 1):
            row = futures[future]
            try:
                game_id, game = future.result()
                games[game_id] = game
            except Exception as error:  # noqa: BLE001 - retain the read audit
                failures.append(
                    {
                        "game_id": row["game_id"],
                        "stage": "fetch",
                        "error": f"{type(error).__name__}: {error}",
                    }
                )
            if index % 20 == 0 or index == len(futures):
                print(f"fetched {index}/80 ({len(failures)} failures)", flush=True)

    with tempfile.TemporaryDirectory(prefix="orchard-conversion-audit-") as directory:
        temp = Path(directory)
        resident_binary = temp / "resident"
        probe_source = temp / "probe.rs"
        probe_binary = temp / "probe"
        probe_source.write_text(instrument_minified(RESIDENT.read_text()))
        compile_source(RESIDENT, resident_binary, "orchard_audit_resident")
        compile_source(probe_source, probe_binary, "orchard_audit_probe")

        def run(row: dict) -> dict:
            return audit_game(
                games[row["game_id"]], row, resident_binary, probe_binary
            )

        rows = []
        eligible = [row for row in fixed_rows if row["game_id"] in games]
        with ThreadPoolExecutor(max_workers=args.audit_workers) as executor:
            futures = {executor.submit(run, row): row for row in eligible}
            for index, future in enumerate(as_completed(futures), 1):
                row = futures[future]
                try:
                    rows.append(future.result())
                except Exception as error:  # noqa: BLE001 - retain the audit failure
                    failures.append(
                        {
                            "game_id": row["game_id"],
                            "stage": "audit",
                            "error": f"{type(error).__name__}: {error}",
                        }
                    )
                if index % 20 == 0 or index == len(futures):
                    print(
                        f"audited {index}/{len(futures)} ({len(failures)} failures)",
                        flush=True,
                    )
    rows.sort(key=lambda row: row["game_id"], reverse=True)
    payload = analyze(rows, failures)
    save(args.output, payload)
    print(
        json.dumps(
            {
                "integrity": payload["integrity_passed"],
                "aggregate": payload["aggregate"],
                "catastrophic": payload["cohorts"]["catastrophic_losses"],
                "fruit_hoard_supported": payload[
                    "fruit_hoard_mechanism_supported"
                ],
                "decision": payload["decision"],
            },
            indent=1,
        )
    )
    print(f"saved {args.output}")
    return 0 if payload["integrity_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
