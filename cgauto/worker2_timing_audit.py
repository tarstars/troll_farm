#!/usr/bin/env python3
"""H8 -- worker-2 timing audit (read-only field study, backlog task
``coordination/tasks/20260729-h8-worker2-timing.md``).

The top cohort is claimed to train its second worker at median turn 2 while the resident
trains at median turn 8 (``docs/rank-hypotheses-2026-07-29.md``, hypothesis H3/H8). D160
and D174a both audited worker **3**'s affordability window (``WORKER3_N = 2`` in
``cgauto/training_currency_audit.py``); nobody has audited worker **2** (``n_before = 1``).
This script does exactly that, and separately re-verifies the "2 vs 8" cross-cohort claim
itself, independently of the older 2026-07-16 top-player census it traces to.

Reuses (does NOT re-derive replay parsing or any counterfactual-window machinery):

- ``cgauto.waste_sweep``: ``decode_game``/``resident_game_ids``/``DecodedGame`` for exact
  official per-turn state (``train_events`` already parses each successful TRAIN's own
  talent vector straight from the issued command text -- the only ground-truth "what did
  the live policy actually request" source, exactly the discipline D174a's own correction
  demanded after B3.8/B3.9 priced a synthetic assumed spec instead of the real one); and
  its ``training_cost``/``training_pay_indices``/``training_affordable``/
  ``training_blocked`` -- the exact, already cross-validated port of
  ``sim.engine.apply_train``'s cost formula and shack-occupancy guard.
- ``cgauto.roster_outcome_pricing``: ``load_games``/``is_clean``/``latest_leaderboard_path``/
  ``load_leaderboard``/``extract_all_train_turns``/``timing_analysis`` for the field-wide
  and B4.3-style early/late worker-2 margin pricing (reused verbatim, not reimplemented).
- ``cgauto.peer_cohort_analysis``: ``build_cohort`` (B4.4's exact STRONG/PEER_WEAK
  same-roster-band cohort definition) and ``run_tempo_pass``/``summarize_tempo``/
  ``first_event_turn`` for per-occurrence first-TRAIN-turn extraction, run fresh here
  against the current corpus rather than read back from B4.4's persisted JSON, so the
  "2 vs 8" framing is independently re-verified as the task requires, not inherited.

Source grounding (read via ``git show HEAD:rust/src/bin/yamo_orchard_live.rs``, SHA
prefix fff6669b -- the working tree is never touched):

- The live deployed path is ``SecureOrchardBot::new()`` -> ``YamoBot::
  tuned_carry_regeneration_transit_idle_harvest()`` -> opening policy
  ``YamoOpeningPolicy::TUNED_CARRY`` (``hard_train_turn: 35``, line ~589).
  ``banana_factory_enabled: false`` by default (``with_policy``, ~line 4077) -- no
  competing "opening economy" subsystem is active pre-worker-2 on the deployed binary.
- ``desired_second`` (the worker-2 bill) is computed **once**, at opening initialization
  (``ensure_opening``, guarded by ``!self.opening_initialized``), via ``choose_second_troll``
  -- an ETA-optimizing search over (movement_speed, carry_capacity, chop_power) in 1..=3
  (harvest_power always 0) -- and is re-decided only if, by ``hard_train_turn`` (turn 35),
  it is still unaffordable (``enforce_training_deadline``, ~line 1993). This is why the
  real bill must be read from each game's own revealed TRAIN command, not assumed.
- TRAIN itself fires the instant ``MoisanBot::can_train(view, desired)`` is true (~line
  3468/3474) -- bank-affordable AND no own unit standing exactly on the shack cell
  (``training_blocked``'s Python port of the engine's own guard) AND own-unit count < 2
  AND more than 20 turns remain. It is a **position-independent global command**: no unit
  needs to walk anywhere or stand on the shack to train (confirmed: ``can_train`` takes no
  unit argument). So, for worker 2, "geometry" reduces to one binary fact per turn: was an
  own unit occupying the shack cell at the moment ``apply_train``'s guard actually
  evaluates -- which is AFTER that turn's own MOVE resolves (referee order, cross-checked
  directly against ``sim/engine.py:step`` -- MOVE, HARVEST, PLANT, CHOP, PICK, TRAIN, DROP,
  MINE), not before it. A same-turn "TRAIN ...;MOVE ..." pair that vacates the shack this
  turn already succeeds (confirmed empirically: games where the starter spawns on the shack
  cell and trains on turn 1 via exactly this pattern). This script's own affordability walk
  therefore checks each candidate unit's POST-move (same-turn, pre-spawn) position, not its
  pre-turn one -- the naive "before" check every other established audit in this repo uses
  (D160/B3.8/B3.9's own ``training_blocked`` call sites) was never load-bearing for THEM
  because their bottleneck was stock affordability (near-never true), so the blocked check
  was moot there; for worker 2, affordability is often already true from the starting
  endowment, so this correction is load-bearing here and is applied throughout.
  The ``n >= 2`` cap in ``can_train`` (~line 836) is confirmed structurally irrelevant to
  worker 2: during the entire pre-worker-2 window the resident's own unit count is
  invariant at 1 (workers never die), so ``n >= 2`` never evaluates true until *after*
  worker 2 is already trained -- this script asserts that invariant empirically per game
  (``n_mismatch_turn_count``, expected 0 in every game) rather than merely assuming it.

CLI usage::

    .venv/bin/python cgauto/worker2_timing_audit.py --output <path/to/report.json> \
        [--jobs 8] [--limit N] [--skip-cohorts]
"""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import statistics
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.peer_cohort_analysis import build_cohort, run_tempo_pass, summarize_tempo  # noqa: E402
from cgauto.roster_outcome_pricing import (  # noqa: E402
    RESIDENT_AGENT_ID,
    extract_all_train_turns,
    is_clean,
    latest_leaderboard_path,
    load_games,
    load_leaderboard,
    timing_analysis as field_timing_analysis,
)
from cgauto.waste_sweep import (  # noqa: E402
    DecodedGame,
    IRON_INDEX,
    ITEMS,
    decode_game,
    resident_game_ids,
    training_affordable,
    training_blocked,
    training_cost,
    training_pay_indices,
)

REPO = Path(__file__).resolve().parent.parent
SCRATCHPAD = Path(
    "/tmp/claude-1001/-home-tarstars-prj-troll-farm/"
    "b1ce51c4-4193-48d1-ae46-922ac20ad6db/scratchpad"
)
DEFAULT_OUTPUT = SCRATCHPAD / "h8-worker2-timing-audit-result.json"

# The four TRAIN-bill item slots (PLUM/LEMON/APPLE always charged; IRON only when the
# map has iron terrain -- training_pay_indices). NOT ITEMS[:4], which is
# (PLUM, LEMON, APPLE, BANANA) -- BANANA is never part of a TRAIN bill.
BILL_ITEMS = ("PLUM", "LEMON", "APPLE", "IRON")
BILL_INDEX = {"PLUM": 0, "LEMON": 1, "APPLE": 2, "IRON": IRON_INDEX}

# Own-unit count immediately before training the 2nd worker (D160/B3.8/B3.9's "WORKER3_N"
# convention generalized down one level: worker 2 = n_before 1, worker 3 = n_before 2).
WORKER2_N = 1
# YamoOpeningPolicy::TUNED_CARRY.hard_train_turn (source: rust/src/bin/yamo_orchard_live.rs,
# line ~589) -- the turn at which, if the original desired_second is still unaffordable,
# choose_second_troll's pick is downgraded to whatever is currently affordable. A game
# whose worker-2 TRAIN lands at or after this turn may be training a *different* (cheaper)
# bill than the one it was checking affordability against for turns 1..34.
HARD_TRAIN_TURN = 35


# ---------------------------------------------------------------------------
# Section A: per-resident-game affordability / legality / geometry audit
# ---------------------------------------------------------------------------


def audit_one_game(game_id: int) -> dict:
    try:
        game: DecodedGame = decode_game(game_id)
    except Exception as exc:  # noqa: BLE001 -- keep a complete read audit
        return {"ok": False, "game_id": game_id, "error": f"{type(exc).__name__}: {exc}"}

    starting_positions = [(unit["x"], unit["y"]) for unit in game.states[0]["units"] if unit["player"] == game.me]
    spawn_on_shack = game.own_shack in starting_positions

    event = next((e for e in game.train_events if e["n_before"] == WORKER2_N), None)
    if event is None:
        return {
            "ok": True,
            "game_id": game_id,
            "trained_worker2": False,
            "margin": game.margin,
            "won": game.won,
            "turns": game.turns,
            "opponent": game.opponent_name,
            "spawn_on_shack": spawn_on_shack,
        }

    talents = tuple(int(v) for v in event["talents"])
    t_actual = event["turn"]
    cost = training_cost(WORKER2_N, talents)
    pay = training_pay_indices(game.iron_present)
    starting_bank = [int(v) for v in game.states[0]["inventories"][game.me]]

    first_afford_turn = None
    first_legal_turn = None
    blocked_while_affordable_turns: list[int] = []
    n_mismatch_turns: list[int] = []
    for t in range(1, t_actual + 1):
        own_units_before = [unit for unit in game.states[t - 1]["units"] if unit["player"] == game.me]
        if len(own_units_before) != WORKER2_N:
            n_mismatch_turns.append(t)
            continue
        bank_before = [int(v) for v in game.states[t - 1]["inventories"][game.me]]
        afford = training_affordable(WORKER2_N, talents, bank_before, game.iron_present)
        # apply_train's occupancy guard (sim/engine.py:274) runs AFTER this turn's own
        # MOVE resolves -- the referee's fixed per-turn order is MOVE, HARVEST, PLANT,
        # CHOP, PICK, TRAIN, DROP, MINE (sim/engine.py:step, cross-checked directly
        # against source). A unit that moves off the shack this same turn has already
        # vacated by the time TRAIN's guard runs -- empirically confirmed: 4/8 smoke-
        # test games train successfully at turn 1 with the starter spawning exactly on
        # the shack cell, via a same-turn "TRAIN ...;MOVE ..." pair. Nothing between
        # MOVE and TRAIN in the resolution order changes a unit's cell, so this same
        # unit id's position in the POST-turn state (states[t]) is an exact read of
        # its position at the moment the guard evaluated, not an approximation --
        # unlike the pre-turn state (states[t-1]) that a naive "before" check would use.
        post_turn_by_id = {unit["id"]: unit for unit in game.states[t]["units"] if unit["player"] == game.me}
        post_move_units = [
            post_turn_by_id[unit["id"]] for unit in own_units_before if unit["id"] in post_turn_by_id
        ]
        blocked = training_blocked(post_move_units, game.own_shack)
        if afford and first_afford_turn is None:
            first_afford_turn = t
        if afford and blocked:
            blocked_while_affordable_turns.append(t)
        if afford and not blocked and first_legal_turn is None:
            first_legal_turn = t

    gap_legal_turns = (t_actual - first_legal_turn) if first_legal_turn is not None else None
    gap_afford_only_turns = (t_actual - first_afford_turn) if first_afford_turn is not None else None

    return {
        "ok": True,
        "game_id": game_id,
        "trained_worker2": True,
        "margin": game.margin,
        "won": game.won,
        "turns": game.turns,
        "iron_present": game.iron_present,
        "opponent": game.opponent_name,
        "spawn_on_shack": spawn_on_shack,
        "talents": list(talents),
        "cost_nominal": {name: int(cost[BILL_INDEX[name]]) for name in BILL_ITEMS},
        "cost_paid_items": [ITEMS[i] for i in pay],
        "starting_bank": starting_bank,
        "t_actual": t_actual,
        "first_afford_turn": first_afford_turn,
        "first_legal_turn": first_legal_turn,
        "gap_legal_turns": gap_legal_turns,
        "gap_afford_only_turns": gap_afford_only_turns,
        "shack_blocked_while_affordable_turn_count": len(blocked_while_affordable_turns),
        "shack_blocked_while_affordable_turns": blocked_while_affordable_turns,
        "n_mismatch_turn_count": len(n_mismatch_turns),
        "past_hard_train_turn": t_actual >= HARD_TRAIN_TURN,
    }


def run_section_a(game_ids: list[int], jobs: int) -> list[dict]:
    if jobs <= 1:
        return [audit_one_game(game_id) for game_id in game_ids]
    with ProcessPoolExecutor(max_workers=jobs) as executor:
        return list(executor.map(audit_one_game, game_ids, chunksize=4))


def summarize_section_a(rows: list[dict]) -> dict:
    ok = [row for row in rows if row["ok"]]
    failed = [row for row in rows if not row["ok"]]
    trained = [row for row in ok if row["trained_worker2"]]
    never_trained = [row for row in ok if not row["trained_worker2"]]

    def stats(values: list[float]) -> dict:
        values = list(values)
        if not values:
            return {"n": 0, "median": None, "mean": None, "min": None, "max": None}
        return {
            "n": len(values),
            "median": statistics.median(values),
            "mean": statistics.fmean(values),
            "min": min(values),
            "max": max(values),
        }

    t_actual_values = [row["t_actual"] for row in trained]
    first_afford_values = [row["first_afford_turn"] for row in trained if row["first_afford_turn"] is not None]
    first_legal_values = [row["first_legal_turn"] for row in trained if row["first_legal_turn"] is not None]
    gap_legal_values = [row["gap_legal_turns"] for row in trained if row["gap_legal_turns"] is not None]
    gap_afford_values = [row["gap_afford_only_turns"] for row in trained if row["gap_afford_only_turns"] is not None]

    gap_histogram = dict(sorted(Counter(gap_legal_values).items()))
    games_gap_zero = sum(1 for g in gap_legal_values if g == 0)
    games_gap_positive = sum(1 for g in gap_legal_values if g and g > 0)
    games_gap_negative = sum(1 for g in gap_legal_values if g and g < 0)

    talents_counter = Counter(tuple(row["talents"]) for row in trained)
    cost_by_item: dict[str, list[int]] = {name: [] for name in BILL_ITEMS}
    for row in trained:
        for name in BILL_ITEMS:
            # PLUM/LEMON/APPLE always paid; IRON only when it is in cost_paid_items
            # (i.e. the map has iron) -- see training_pay_indices' own docstring.
            if name == "IRON" and name not in row["cost_paid_items"]:
                continue
            cost_by_item[name].append(row["cost_nominal"][name])

    n_never_never_afford = sum(1 for row in trained if row["first_afford_turn"] is None)
    n_mismatch_total = sum(row["n_mismatch_turn_count"] for row in trained)
    n_spawn_on_shack = sum(1 for row in ok if row["spawn_on_shack"])
    n_blocked_any = sum(1 for row in trained if row["shack_blocked_while_affordable_turn_count"] > 0)
    n_past_hard_deadline = sum(1 for row in trained if row["past_hard_train_turn"])

    return {
        "games_ok": len(ok),
        "games_failed": len(failed),
        "failures": failed[:50],
        "games_trained_worker2": len(trained),
        "games_never_trained_worker2": len(never_trained),
        "never_trained_worker2_game_ids": [row["game_id"] for row in never_trained],
        "sanity_checks": {
            "n_mismatch_turn_count_total_expected_0": n_mismatch_total,
            "spawn_on_shack_at_turn0_count": n_spawn_on_shack,
            "spawn_on_shack_at_turn0_rate": n_spawn_on_shack / len(ok) if ok else None,
            "games_where_bill_was_never_bank_affordable_before_t_actual_expected_0": n_never_never_afford,
        },
        "real_bill": {
            "talents_distribution_ms_cc_hp_chop": {str(k): v for k, v in talents_counter.most_common()},
            "n_distinct_talent_vectors": len(talents_counter),
            "cost_paid_by_item": {
                name: stats(values) for name, values in cost_by_item.items() if values
            },
            "note": (
                "cost is training_cost(n=1, talents) evaluated per game against that "
                "game's own revealed TRAIN command talents; IRON is only ever paid on "
                "iron-present maps (training_pay_indices), so its stats pool over the "
                "iron-present subset only, same convention as D160/B3.8/B3.9."
            ),
        },
        "t_actual_turn": stats(t_actual_values),
        "first_afford_turn": stats(first_afford_values),
        "first_legal_turn": stats(first_legal_values),
        "gap_legal_turns": {**stats(gap_legal_values), "histogram": gap_histogram},
        "gap_afford_only_turns": stats(gap_afford_values),
        "games_gap_legal_zero": games_gap_zero,
        "games_gap_legal_positive": games_gap_positive,
        "games_gap_legal_negative_unexpected": games_gap_negative,
        "games_with_any_shack_blocked_while_affordable_turn": n_blocked_any,
        "games_past_hard_train_turn_35_possible_downgrade": n_past_hard_deadline,
    }


# ---------------------------------------------------------------------------
# Section B: cross-cohort re-verification of the "median turn 2 vs 8" claim
# ---------------------------------------------------------------------------


def worker2_turn_stats_from_extraction(
    clean_games: list[dict], turns_by_game: dict[int, tuple[list[int], list[int]]], agent_ids: set[int]
) -> dict:
    values = []
    n_never = 0
    for game in clean_games:
        turns = turns_by_game.get(game["gameId"])
        if turns is None:
            continue
        for player in game["players"]:
            if player["agentId"] not in agent_ids:
                continue
            seat_turns = turns[player["index"]]
            if seat_turns:
                values.append(seat_turns[0])
            else:
                n_never += 1
    values.sort()
    return {
        "n_occurrences_with_worker2": len(values),
        "n_occurrences_never_trained": n_never,
        "median_turn": statistics.median(values) if values else None,
        "mean_turn": statistics.fmean(values) if values else None,
        "min_turn": values[0] if values else None,
        "max_turn": values[-1] if values else None,
    }


def run_section_b(jobs: int) -> dict:
    leaderboard_path = latest_leaderboard_path()
    leaderboard = load_leaderboard(leaderboard_path)
    all_games = load_games()
    clean_games = [game for game in all_games if is_clean(game)]

    cohort = build_cohort(clean_games, leaderboard)
    strong_ids = {row["agent_id"] for row in cohort["strong"]}
    peer_weak_ids = {row["agent_id"] for row in cohort["peer_weak"]}
    top5_ids = {
        agent_id
        for agent_id, info in leaderboard.items()
        if info.get("division_index") == 5 and info.get("rank") is not None and info["rank"] <= 5
    }
    resident_ids = {RESIDENT_AGENT_ID}

    # Field-wide (light pass: successful_events on raw JSON only, no trajectory read) --
    # reuses roster_outcome_pricing.extract_all_train_turns/timing_analysis verbatim; this
    # is the exact machinery and definition behind B4.3's published "2nd worker: median
    # turn 8" field figure, recomputed fresh here rather than read back from that report.
    game_ids = [game["gameId"] for game in clean_games]
    turns_by_game, extraction_failures = extract_all_train_turns(game_ids, jobs=jobs)
    field_timing = field_timing_analysis(clean_games, turns_by_game)

    groups = {
        "resident": resident_ids,
        "strong_b44_cohort": strong_ids,
        "peer_weak_b44_cohort": peer_weak_ids,
        "top5_literal_rank": top5_ids,
    }
    light_pass = {name: worker2_turn_stats_from_extraction(clean_games, turns_by_game, ids) for name, ids in groups.items()}

    # Heavier tempo pass (peer_cohort_analysis._tempo_worker: raw JSON + trajectory read,
    # gives median/mean/sd via summarize_tempo AND the first-train spec/role) for the same
    # four bounded groups -- an independent second measurement of the same "first TRAIN
    # turn" fact via a different code path (successful_events + explicit min-turn walk vs
    # this script's own extract_all_train_turns-based walk above), plus bill-spec context.
    occurrence_tasks = []
    for name, ids in groups.items():
        for game in clean_games:
            for player in game["players"]:
                if player["agentId"] in ids:
                    occurrence_tasks.append(
                        {"game_id": game["gameId"], "seat": player["index"], "agent_id": player["agentId"], "cohort": name}
                    )
    tempo_rows, tempo_failures = run_tempo_pass(occurrence_tasks, jobs=jobs)
    tempo_by_cohort: dict[str, list[dict]] = {name: [] for name in groups}
    for row in tempo_rows:
        tempo_by_cohort[row["cohort"]].append(row)
    tempo_summary = {name: summarize_tempo(rows) for name, rows in tempo_by_cohort.items()}

    return {
        "leaderboard_snapshot": str(leaderboard_path.relative_to(REPO)) if leaderboard_path.is_relative_to(REPO) else str(leaderboard_path),
        "corpus_n_games_total": len(all_games),
        "corpus_n_games_clean": len(clean_games),
        "cohort_definition": cohort["inclusion_rule"],
        "cohort_sizes": {
            "strong_b44_cohort_agents": len(strong_ids),
            "peer_weak_b44_cohort_agents": len(peer_weak_ids),
            "top5_literal_rank_agents": len(top5_ids),
        },
        "field_wide_light_pass_extraction_failures": len(extraction_failures),
        "field_wide_timing_analysis_level_2": field_timing["by_level"]["2"],
        "light_pass_first_worker2_train_turn_by_group": light_pass,
        "tempo_pass_first_worker2_train_turn_by_group": {
            name: summary["first_train_turn"] for name, summary in tempo_summary.items()
        },
        "tempo_pass_first_train_spec_role_by_group": {
            name: {
                "role_distribution": summary["first_train_role_distribution"],
                "spec_distribution_top10": summary["first_train_spec_distribution_top10"],
            }
            for name, summary in tempo_summary.items()
        },
        "tempo_pass_failures": len(tempo_failures),
    }


# ---------------------------------------------------------------------------
# Report assembly
# ---------------------------------------------------------------------------


def build_report(section_a_rows: list[dict], section_a_summary: dict, section_b: dict | None) -> dict:
    report = {
        "schema": "troll-farm-h8-worker2-timing-audit-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": (
            "read-only field study (backlog H8): no arena writes, no strategy changes, no "
            "corpus mutation, no rerun of any game"
        ),
        "worker2_n": WORKER2_N,
        "hard_train_turn": HARD_TRAIN_TURN,
        "resident_agent_id": RESIDENT_AGENT_ID,
        "section_a_resident_affordability_audit": section_a_summary,
        "section_a_games": section_a_rows,
    }
    if section_b is not None:
        report["section_b_cross_cohort_reverification"] = section_b
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument("--limit", type=int, default=0, help="0 means every resident game in the corpus")
    parser.add_argument("--skip-cohorts", action="store_true", help="skip section B (cross-cohort re-verification)")
    args = parser.parse_args()
    if not 1 <= args.jobs <= 16:
        parser.error("--jobs must be between 1 and 16")
    if args.limit < 0:
        parser.error("--limit cannot be negative")

    game_ids = resident_game_ids()
    if args.limit:
        game_ids = game_ids[: args.limit]
    if not game_ids:
        raise SystemExit("no resident games found in the corpus")

    section_a_rows = run_section_a(game_ids, jobs=args.jobs)
    section_a_summary = summarize_section_a(section_a_rows)
    print(
        f"section A: {section_a_summary['games_trained_worker2']}/{section_a_summary['games_ok']} games trained "
        f"worker2; t_actual median={section_a_summary['t_actual_turn']['median']}, "
        f"first_legal median={section_a_summary['first_legal_turn']['median']}, "
        f"gap(legal) median={section_a_summary['gap_legal_turns']['median']}, "
        f"games gap=0: {section_a_summary['games_gap_legal_zero']}, "
        f"games gap>0: {section_a_summary['games_gap_legal_positive']}"
    )

    section_b = None
    if not args.skip_cohorts:
        section_b = run_section_b(jobs=args.jobs)
        print(
            "section B: field-wide level-2 median turn = "
            f"{section_b['field_wide_timing_analysis_level_2']['at_least_this_roster'].get('median_turn_reached')}; "
            + ", ".join(
                f"{name}={stats['median_turn']}"
                for name, stats in section_b["light_pass_first_worker2_train_turn_by_group"].items()
            )
        )

    report = build_report(section_a_rows, section_a_summary, section_b)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=1) + "\n")
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
