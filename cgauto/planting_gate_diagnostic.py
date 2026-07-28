#!/usr/bin/env python3
"""B4.5 -- planting-gate diagnostic (read-only research scout).

Follow-up to B4.4 (``cgauto/peer_cohort_analysis.py``): B4.4 found the resident's median
first successful PLANT is turn 191.5 vs turn 21-29 for 25 two-worker Legend peers, and
traced this to a tested ``banana_factory_*`` self-planting/reaping subsystem in the live
planner's dev source (``rust/src/bin/yamo_orchard_live.rs``) that defaults to
``enabled: false`` behind a one-shot board-richness selector evaluated once at 2-worker
roster. This script:

1. measures how often that selector's predicate would fire against the resident's own
   205 (in practice: however many are in the corpus today) field games, replayed exactly;
2. sweeps its thresholds to produce an activation-vs-threshold curve;
3. characterizes the field's early-planting peers (STRONG+PEER/WEAK cohort from B4.4:
   the same 25 Legend two-worker agents) -- volume, timing, concurrency, seed provenance,
   own-crop disposition -- against D89's ledger record and against the resident; and
4. tests D89's safety-rejection mechanism (private production feeding the opponent's own
   economy) against the field: does peer planting volume correlate with opponent score.

STRICTLY READ-ONLY. All Rust-source facts used below (the enable flag, the selector
predicate/thresholds, the code paths, line numbers) were pinned by reading
``git show HEAD:rust/src/bin/yamo_orchard_live.rs`` in a separate research pass (a
concurrent agent, D174a, is compiling/editing that file's working-tree copy) and are
hardcoded as constants here with citations in comments -- this script never opens the
working-tree copy of that file. No arena writes, no corpus mutation, no tracked-file
edits.

Reuse, not a new parser:

- ``cgauto.roster_outcome_pricing`` -- corpus/leaderboard loading, ``is_clean``,
  ``RESIDENT_AGENT_ID``, ``roster_of``/``margin_of``, and the stats helpers
  (``mean_sd_n``, ``bootstrap_mean_ci``, ``bootstrap_diff_ci``, ``win_rate_ci``, ``pearson``).
- ``cgauto.peer_cohort_analysis.build_cohort``/``index_agent_occurrences`` -- the exact
  same 25-agent STRONG/PEER_WEAK cohort B4.4 used (Legend, >=10 games, mean final roster
  within 0.2 of the resident's own mean), recomputed fresh against the current corpus
  rather than hand-copied, so growth in the daily-cron corpus is picked up automatically.
- ``cgauto.replay_state.decode_replay``/``to_game_state`` -- exact official per-turn state
  reconstruction from CodinGame replay diffs (units, plants with kind/health/fruits).
- ``cgauto.replay_conformance.action_commands``/``effective_chop_unit_ids`` -- turn-string
  parsing and the chop-vs-growth disambiguation the project's own heavy-pass decode
  fidelity checks (D101a) rely on.
- ``cgauto.recent_resident_field_census.successful_events`` -- referee-confirmed
  TRAIN/PLANT/HARVEST/CHOP/DROP event stream with resolved turn, reused for tempo
  cross-checks without a full diff decode.

CLI usage::

    .venv/bin/python cgauto/planting_gate_diagnostic.py --output <path/to/report.json>
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass, field
import json
from pathlib import Path
import statistics
import sys
import time

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.roster_outcome_pricing import (  # noqa: E402
    RESIDENT_AGENT_ID,
    bootstrap_diff_ci,
    bootstrap_mean_ci,
    is_clean,
    latest_leaderboard_path,
    load_games,
    load_leaderboard,
    mean_sd_n,
    pearson,
    roster_of,
    win_rate_ci,
)
from cgauto.peer_cohort_analysis import build_cohort, index_agent_occurrences  # noqa: E402
from cgauto.recent_resident_field_census import successful_events  # noqa: E402
from cgauto.replay_conformance import action_commands, effective_chop_unit_ids  # noqa: E402
from cgauto.replay_state import decode_replay  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
RAW_GAMES = REPO / "data/raw/games"
TRAJECTORIES = REPO / "data/processed/trajectories"
GAMES_INDEX = REPO / "data/processed/games.jsonl"
DEPLOYED_SOURCE = (
    REPO
    / "cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs"
)
SCRATCH_DIR = Path(
    "/tmp/claude-1001/-home-tarstars-prj-troll-farm/b87b2a84-2e59-408b-9c9e-ecb58289a6d1/scratchpad"
)
DEFAULT_OUTPUT = SCRATCH_DIR / "b45-planting-gate-diagnostic-data.json"

# ---------------------------------------------------------------------------
# Gate constants -- pinned by reading `git show HEAD:rust/src/bin/yamo_orchard_live.rs`
# (a separate, read-only pass; this script never opens the working-tree copy, which a
# concurrent agent, D174a, is compiling/editing). Line numbers as of the commit this
# script's companion report cites. NOT re-derived at runtime -- changing these constants
# changes what the sweep measures, they are not fit to data.
# ---------------------------------------------------------------------------
SELECTOR_MAX_PLANTS = 20  # yamo_orchard_live.rs:5233 `live_plants.len() <= 20`
SELECTOR_MIN_FRUITS = 27  # yamo_orchard_live.rs:5233 `fruits >= 27`
SELECTOR_MIN_BANANA = 6  # yamo_orchard_live.rs:5233 `banana_plants >= 6`
GATE_CODE_REFS = {
    "banana_factory_enabled_field": "yamo_orchard_live.rs:3773 (struct field)",
    "banana_factory_enabled_default_false": "yamo_orchard_live.rs:4077 (with_policy() struct literal)",
    "production_constructor_chain": (
        "yamo_orchard_live.rs:3824-3832 SecureOrchardBot::new() -> "
        "with_policy(YamoBot::tuned_carry_regeneration_transit_idle_harvest(), 8, false, 11, 1); "
        "fn main() at 6008-6024 calls SecureOrchardBot::new() unconditionally (6016), no cfg/env branch"
    ),
    "banana_seed_factory_constructor": "yamo_orchard_live.rs:3843-3846 (test/offline-only; not reached from main())",
    "selector_enable_flag": "yamo_orchard_live.rs:3853-3857 banana_seed_factory_activation_selector() sets banana_factory_selector_enabled=true (test/offline-only)",
    "one_shot_selector_evaluation": "yamo_orchard_live.rs:5210-5234 (fn commands: own_count computed 5215; selector guarded !banana_factory_selector_decided && own_count>=2 at 5216-5219; decided=true 5221; predicate computed+assigned 5222-5233)",
    "dispatch_to_factory": "yamo_orchard_live.rs:5235-5241 (banana_factory_enabled && (!selector_enabled || selector_selected) && (active || own_count>=2) -> banana_factory_commands)",
    "banana_factory_commands_entry": "yamo_orchard_live.rs:5081-5086",
    "bootstrap_plant_emission": "yamo_orchard_live.rs:4747-4792 banana_factory_starter_command (PLANT ... BANANA at 4792)",
    "disabled_by_default_test": "yamo_orchard_live.rs:5635-5641 banana_factory_is_disabled_by_default_and_preactivation_is_exact",
    "scarce_intent_enum": "yamo_orchard_live.rs:618 ScarceIntent; scarce_farming field default false at 1629; only true via tuned_carry_regeneration_scarce() at 1752-1756, not in production chain",
    "mother_orchard_geometry_setup": "yamo_orchard_live.rs:4132-4202 SecureOrchardBot::initialize() (geometry: Option<OrchardGeometry> field at 3759; OrchardPhase enum at 3677; OrchardGeometry struct at 3684)",
    "mother_can_activate": "yamo_orchard_live.rs:4394-4416",
    "mother_can_continue_seed": "yamo_orchard_live.rs:4417-4443",
    "mother_state_machine_and_plant_emission": "yamo_orchard_live.rs:5242-5429 (fallback path when banana_factory inactive; PLANT APPLE at 5383)",
    "idle_regeneration_conversion_path": "yamo_orchard_live.rs:3084-3145 YamoBot::main_candidates (idle_regeneration && chops.is_empty() branch at 3129-3138 falls into endgame_candidates)",
    "endgame_candidates_plant_emission": "yamo_orchard_live.rs:3200-3253 (carried-fruit conversion-to-wood PLANT at 3242)",
    "bank_seeded_endgame_pick": "yamo_orchard_live.rs:3102-3117 (turn>=100 && plants.len()<=2 && own_count>=2 gate on PICK from bank inventory)",
}

# ---------------------------------------------------------------------------
# Threshold-sweep grids -- module constants, not fit to data.
# ---------------------------------------------------------------------------
PLANTS_MAX_GRID = [5, 10, 15, 20, 25, 30, 40, 50, 60, 80, 100, 10_000]
FRUITS_MIN_GRID = [0, 5, 10, 15, 20, 25, 27, 30, 35, 40, 50, 60, 80]
BANANA_MIN_GRID = [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 15]
NAMED_SCENARIOS = [
    ("current_D91_selector", 20, 27, 6),
    ("plants_relaxed_40", 40, 27, 6),
    ("plants_unbounded", 10_000, 27, 6),
    ("fruits_relaxed_15", 20, 15, 6),
    ("fruits_off", 20, 0, 6),
    ("banana_relaxed_3", 20, 27, 3),
    ("banana_off", 20, 27, 0),
    ("moderate_joint_relaxation", 40, 15, 3),
    ("loose_joint_relaxation", 60, 10, 2),
    ("fully_open_no_selector", 10_000, 0, 0),
]

# Sample cap for the expensive per-turn peer decode (concurrent crops, seed provenance,
# own-crop disposition) -- bounded per agent so the 25-agent cohort is covered broadly
# rather than dominated by whichever agent has the most games.
PEER_SAMPLE_GAMES_PER_AGENT = 6

SCHEMA = 1


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


def load_corpus() -> tuple[list[dict], dict[int, dict]]:
    games = load_games()
    clean = [g for g in games if is_clean(g)]
    leaderboard = load_leaderboard(latest_leaderboard_path())
    return clean, leaderboard


def deployed_source_check() -> dict:
    """Cross-check: does the ACTUALLY DEPLOYED resident binary (not the dev-tree HEAD
    copy of yamo_orchard_live.rs) even contain the banana_factory subsystem? Read-only
    inspection of an already-committed, static submission artifact (not the file the
    concurrent agent is editing)."""

    if not DEPLOYED_SOURCE.exists():
        return {"found": False, "path": str(DEPLOYED_SOURCE)}
    src = DEPLOYED_SOURCE.read_text()
    markers = [
        "banana_factory",
        "ScarceIntent",
        "scarce_farming",
        "task_market_enabled",
        "opponent_crop_dual_value",
        "worker_three_bridge",
        "idle_regeneration",
        "OrchardPhase::Dormant",
        "can_activate",
        "endgame_candidates",
        "main_candidates",
        "carried_fruit",
        "regeneration_commitments",
    ]
    counts = {marker: src.count(marker) for marker in markers}
    return {
        "found": True,
        "path": str(DEPLOYED_SOURCE.relative_to(REPO)),
        "bytes": len(src),
        "marker_counts": counts,
        "contains_banana_factory_subsystem": counts["banana_factory"] > 0,
        "contains_mother_and_idle_regeneration_paths": (
            counts["idle_regeneration"] > 0 and counts["OrchardPhase::Dormant"] > 0
        ),
    }


# ---------------------------------------------------------------------------
# Part 2+3: selector predicate evaluated against resident field replays, threshold sweep
# ---------------------------------------------------------------------------


def own_seat_of(raw_game: dict, agent_id: int) -> int | None:
    for agent in raw_game.get("agents") or []:
        if agent.get("agentId") == agent_id:
            return agent.get("index")
    return None


def build_chop_ids_by_turn(trajectory: list[dict]) -> list[list[int]]:
    trajectory_sorted = sorted(trajectory, key=lambda row: row["t"])
    out = []
    for row in trajectory_sorted:
        ids: list[int] = []
        for player in (0, 1):
            commands = action_commands(row.get(f"commands{player}"))
            ids.extend(effective_chop_unit_ids(commands))
        out.append(ids)
    return out


def decode_game(game_id: int) -> tuple[dict, list[dict]] | None:
    raw_path = RAW_GAMES / f"{game_id}.json"
    traj_path = TRAJECTORIES / f"{game_id}.jsonl"
    if not raw_path.exists() or not traj_path.exists():
        return None
    raw = json.loads(raw_path.read_text())
    trajectory = [
        json.loads(line) for line in traj_path.read_text().splitlines() if line.strip()
    ]
    chop_ids = build_chop_ids_by_turn(trajectory)
    decoded = decode_replay(raw_path, chop_unit_ids_by_turn=chop_ids)
    return raw, decoded, trajectory  # type: ignore[return-value]


def first_own_roster_2_state(states: list[dict], own_seat: int) -> tuple[int, dict] | None:
    """First decoded state (resolved_turn index k, i.e. the view fed to the bot at the
    START of view.turn = k+1, before that turn's action is decided) where the resident's
    own unit count is >= 2 -- exactly the instant `SecureOrchardBot::commands()` computes
    `own_count` and (if the selector were live) would evaluate it, per
    yamo_orchard_live.rs:5215-5219."""

    for index, state in enumerate(states):
        own_units = sum(1 for unit in state["units"] if unit["player"] == own_seat)
        if own_units >= 2:
            return index, state
    return None


def selector_components(state: dict) -> dict:
    live_plants = state["plants"]  # decode_replay already filters to health>0 (active)
    fruits = sum(plant["fruits"] for plant in live_plants)
    banana_plants = sum(1 for plant in live_plants if plant["type"] == "BANANA")
    return {
        "n_plants": len(live_plants),
        "fruits": fruits,
        "banana_plants": banana_plants,
    }


def predicate(components: dict, max_plants: int, min_fruits: int, min_banana: int) -> bool:
    return (
        components["n_plants"] <= max_plants
        and components["fruits"] >= min_fruits
        and components["banana_plants"] >= min_banana
    )


def process_resident_game(game: dict) -> dict:
    game_id = game["gameId"]
    own_index = None
    for player in game["players"]:
        if player["agentId"] == RESIDENT_AGENT_ID:
            own_index = player["index"]
    result: dict = {
        "game_id": game_id,
        "map_hash": game.get("map_hash"),
        "own_index": own_index,
        "roster": roster_of(game, own_index) if own_index is not None else None,
        "decode_ok": False,
    }
    decoded_tuple = decode_game(game_id)
    if decoded_tuple is None:
        result["error"] = "raw_or_trajectory_missing"
        return result
    raw, decoded, _trajectory = decoded_tuple
    own_seat = own_seat_of(raw, RESIDENT_AGENT_ID)
    if own_seat is None:
        result["error"] = "agent_not_in_raw_agents"
        return result
    result["unknown_updates"] = len(decoded["unknown_updates"])
    hit = first_own_roster_2_state(decoded["states"], own_seat)
    if hit is None:
        result["own_roster_never_reaches_2"] = True
        return result
    index, state = hit
    components = selector_components(state)
    result.update(
        {
            "decode_ok": True,
            "own_roster_never_reaches_2": False,
            "view_turn_at_roster_2": index + 1,  # resolved_turn=index -> view.turn=index+1
            **components,
            "predicate_current": predicate(
                components, SELECTOR_MAX_PLANTS, SELECTOR_MIN_FRUITS, SELECTOR_MIN_BANANA
            ),
            "fails_plants_clause": components["n_plants"] > SELECTOR_MAX_PLANTS,
            "fails_fruits_clause": components["fruits"] < SELECTOR_MIN_FRUITS,
            "fails_banana_clause": components["banana_plants"] < SELECTOR_MIN_BANANA,
        }
    )
    events = successful_events(raw["frames"])[own_seat]
    plant_turns = sorted(event["turn"] for event in events if event["kind"] == "PLANT")
    result["first_plant_turn"] = plant_turns[0] if plant_turns else None
    result["own_score"] = float(game["scores"][own_seat])
    result["opponent_score"] = float(game["scores"][1 - own_seat])
    return result


def summarize_fire_rate(rows: list[dict]) -> dict:
    decoded = [row for row in rows if row.get("decode_ok")]
    n = len(decoded)
    fired = [row for row in decoded if row["predicate_current"]]
    not_fired = [row for row in decoded if not row["predicate_current"]]
    turn2_turns = [row["view_turn_at_roster_2"] for row in decoded]

    by_map: dict[str, list[dict]] = defaultdict(list)
    for row in decoded:
        by_map[row["map_hash"]].append(row)
    map_breakdown = []
    for map_hash, group in sorted(by_map.items(), key=lambda kv: -len(kv[1])):
        fired_here = sum(1 for row in group if row["predicate_current"])
        map_breakdown.append(
            {
                "map_hash": map_hash,
                "n_games": len(group),
                "n_fired": fired_here,
                "fire_rate": fired_here / len(group),
                "mean_plants": statistics.mean(row["n_plants"] for row in group),
                "mean_fruits": statistics.mean(row["fruits"] for row in group),
                "mean_banana_plants": statistics.mean(row["banana_plants"] for row in group),
            }
        )

    def plant_turn_stats(subset: list[dict]) -> dict:
        turns = [row["first_plant_turn"] for row in subset if row["first_plant_turn"] is not None]
        return {
            "n_games": len(subset),
            "n_ever_planted": len(turns),
            "pct_ever_planted": len(turns) / len(subset) if subset else None,
            "median_first_plant_turn": statistics.median(turns) if turns else None,
            "mean_first_plant_turn": statistics.mean(turns) if turns else None,
        }

    return {
        "n_resident_games_total": len(rows),
        "n_decode_ok": n,
        "n_decode_failures": len(rows) - n,
        "n_own_roster_never_reaches_2": sum(
            1 for row in rows if row.get("own_roster_never_reaches_2")
        ),
        "n_nonzero_unknown_updates": sum(
            1 for row in decoded if row.get("unknown_updates", 0) > 0
        ),
        "view_turn_at_roster_2": mean_sd_n(turn2_turns),
        "fire_rate_current_selector": len(fired) / n if n else None,
        "n_fired": len(fired),
        "n_not_fired": len(not_fired),
        "component_distributions": {
            "n_plants": mean_sd_n(row["n_plants"] for row in decoded),
            "fruits": mean_sd_n(row["fruits"] for row in decoded),
            "banana_plants": mean_sd_n(row["banana_plants"] for row in decoded),
        },
        "clause_failure_counts_among_all_games": {
            "fails_plants_clause_(n_plants>20)": sum(
                1 for row in decoded if row["fails_plants_clause"]
            ),
            "fails_fruits_clause_(fruits<27)": sum(
                1 for row in decoded if row["fails_fruits_clause"]
            ),
            "fails_banana_clause_(banana<6)": sum(
                1 for row in decoded if row["fails_banana_clause"]
            ),
        },
        "map_breakdown": map_breakdown,
        "n_distinct_maps": len(by_map),
        "crosscheck_first_plant_turn_predicate_true": plant_turn_stats(fired),
        "crosscheck_first_plant_turn_predicate_false": plant_turn_stats(not_fired),
    }


def threshold_sweep(rows: list[dict]) -> dict:
    decoded = [row for row in rows if row.get("decode_ok")]
    n = len(decoded)

    def rate(max_plants: int, min_fruits: int, min_banana: int) -> dict:
        fired = sum(
            1
            for row in decoded
            if predicate(row, max_plants, min_fruits, min_banana)
        )
        return {
            "max_plants": max_plants,
            "min_fruits": min_fruits,
            "min_banana": min_banana,
            "n_fired": fired,
            "fire_rate": fired / n if n else None,
        }

    marginal_plants = [
        rate(value, SELECTOR_MIN_FRUITS, SELECTOR_MIN_BANANA) for value in PLANTS_MAX_GRID
    ]
    marginal_fruits = [
        rate(SELECTOR_MAX_PLANTS, value, SELECTOR_MIN_BANANA) for value in FRUITS_MIN_GRID
    ]
    marginal_banana = [
        rate(SELECTOR_MAX_PLANTS, SELECTOR_MIN_FRUITS, value) for value in BANANA_MIN_GRID
    ]
    named = [
        {"name": name, **rate(max_plants, min_fruits, min_banana)}
        for name, max_plants, min_fruits, min_banana in NAMED_SCENARIOS
    ]
    return {
        "n_games": n,
        "marginal_sweep_plants_max": marginal_plants,
        "marginal_sweep_fruits_min": marginal_fruits,
        "marginal_sweep_banana_min": marginal_banana,
        "named_scenarios": named,
    }


# ---------------------------------------------------------------------------
# Part 4: peer design comparison (cheap games.jsonl stats over the full cohort, plus a
# bounded per-agent sample for the expensive per-turn decode).
# ---------------------------------------------------------------------------


def cheap_plant_and_score_stats(occurrences: list[tuple[dict, int]]) -> dict:
    plants_per_game = []
    opponent_scores = []
    own_scores = []
    for game, seat in occurrences:
        per_player = game["per_player"][str(seat)]
        planted = sum(per_player.get("planted_ok", {}).values())
        plants_per_game.append(planted)
        own_scores.append(float(game["scores"][seat]))
        opponent_scores.append(float(game["scores"][1 - seat]))
    return {
        "n_games": len(occurrences),
        "plants_per_game": mean_sd_n(plants_per_game),
        "own_score": mean_sd_n(own_scores),
        "opponent_score": mean_sd_n(opponent_scores),
    }


def first_plant_timing(occurrences: list[tuple[dict, int]]) -> dict:
    turns = []
    n_ever = 0
    for game, seat in occurrences:
        raw_path = RAW_GAMES / f"{game['gameId']}.json"
        if not raw_path.exists():
            continue
        raw = json.loads(raw_path.read_text())
        events = successful_events(raw["frames"])[seat]
        plant_turns = sorted(e["turn"] for e in events if e["kind"] == "PLANT")
        if plant_turns:
            n_ever += 1
            turns.append(plant_turns[0])
    return {
        "n_games_scanned": len(occurrences),
        "n_ever_planted": n_ever,
        "pct_ever_planted": n_ever / len(occurrences) if occurrences else None,
        "first_plant_turn": mean_sd_n(turns),
    }


def partial_pearson(x, y, control) -> float | None:
    """Pearson r between x and y after linearly residualizing out `control` from both --
    a cheap check for the obvious game-length confound (longer games mechanically give
    both sides more time to plant/score, independent of any causal link between them)."""

    import numpy as np

    x_arr, y_arr, c_arr = (np.asarray(list(v), dtype=float) for v in (x, y, control))
    if x_arr.size < 5 or c_arr.std() == 0:
        return None

    def residualize(values: "np.ndarray") -> "np.ndarray":
        slope, intercept = np.polyfit(c_arr, values, 1)
        return values - (slope * c_arr + intercept)

    return pearson(residualize(x_arr), residualize(y_arr))


def opponent_score_correlation(occurrences: list[tuple[dict, int]]) -> dict:
    """Item 5: does peer planting volume correlate with the peer's OWN opponent scoring
    more, mirroring D89's safety-rejection mechanism (private production relaxes pressure
    on the rival's own loop)? Pooled (confounded by cross-agent skill) plus a within-agent
    high/low split (agent identity, hence skill, held fixed) -- the more credible test.
    Also checks and partials out the obvious game-length confound: a game that simply runs
    longer gives both sides more time to plant AND score, with no causal link required."""

    plants = []
    opp_scores = []
    n_turns_list = []
    by_agent: dict[int, list[tuple[int, float, float]]] = defaultdict(list)
    for game, seat in occurrences:
        per_player = game["per_player"][str(seat)]
        planted = sum(per_player.get("planted_ok", {}).values())
        own_score = float(game["scores"][seat])
        opp_score = float(game["scores"][1 - seat])
        plants.append(planted)
        opp_scores.append(opp_score)
        n_turns_list.append(float(game.get("n_turns", 300)))
        agent_id = game["players"][seat]["agentId"]
        by_agent[agent_id].append((planted, opp_score, own_score))

    pooled_r = pearson(plants, opp_scores)
    confound_r_plants_vs_turns = pearson(plants, n_turns_list)
    confound_r_oppscore_vs_turns = pearson(opp_scores, n_turns_list)
    pooled_partial_r_controlling_game_length = partial_pearson(plants, opp_scores, n_turns_list)

    within_agent_splits = []
    for agent_id, triples in by_agent.items():
        if len(triples) < 15:
            continue
        triples_sorted = sorted(triples, key=lambda triple: triple[0])
        half = len(triples_sorted) // 2
        low = triples_sorted[:half]
        high = triples_sorted[-half:]
        low_median_plants = statistics.median(p for p, _, _ in low)
        high_median_plants = statistics.median(p for p, _, _ in high)
        low_mean_opp = statistics.mean(s for _, s, _ in low)
        high_mean_opp = statistics.mean(s for _, s, _ in high)
        low_mean_own = statistics.mean(s for _, _, s in low)
        high_mean_own = statistics.mean(s for _, _, s in high)
        delta_opp = high_mean_opp - low_mean_opp
        delta_own = high_mean_own - low_mean_own
        agent_r = pearson([p for p, _, _ in triples], [s for _, s, _ in triples])
        within_agent_splits.append(
            {
                "agent_id": agent_id,
                "n_games": len(triples),
                "low_half_median_plants": low_median_plants,
                "high_half_median_plants": high_median_plants,
                "low_half_mean_opponent_score": low_mean_opp,
                "high_half_mean_opponent_score": high_mean_opp,
                "high_minus_low_opponent_score": delta_opp,
                "low_half_mean_own_score": low_mean_own,
                "high_half_mean_own_score": high_mean_own,
                "high_minus_low_own_score": delta_own,
                "opponent_over_own_delta_ratio": (
                    delta_opp / delta_own if delta_own > 0 else None
                ),
                "within_agent_pearson_r": agent_r,
            }
        )

    diffs = [row["high_minus_low_opponent_score"] for row in within_agent_splits]
    positive_rs = [
        row["within_agent_pearson_r"]
        for row in within_agent_splits
        if row["within_agent_pearson_r"] is not None
    ]
    valid_ratios = [
        row["opponent_over_own_delta_ratio"]
        for row in within_agent_splits
        if row["opponent_over_own_delta_ratio"] is not None
    ]
    return {
        "pooled_n": len(occurrences),
        "pooled_pearson_r_plants_vs_opponent_score": pooled_r,
        "pooled_note": (
            "Confounded both ways: better agents plant more (raises r) but also suppress "
            "opponents harder (lowers opponent score, lowers r) -- direction is not "
            "pre-signed by skill alone."
        ),
        "game_length_confound_check": {
            "r_plants_vs_n_turns": confound_r_plants_vs_turns,
            "r_opponent_score_vs_n_turns": confound_r_oppscore_vs_turns,
            "pooled_partial_r_plants_vs_opponent_score_controlling_n_turns": pooled_partial_r_controlling_game_length,
            "note": (
                "A game that simply runs longer gives both sides more time to plant AND "
                "score, with no causal link required -- this is the single biggest threat "
                "to reading the raw correlation/ratio as evidence of D89's mechanism. The "
                "partial correlation above removes the linear part of that confound; the "
                "within-agent high/low-half split below inherits the same confound (longer "
                "games plant more AND let the opponent score more) and is NOT a substitute "
                "for a controlled paired-map A/B like D89/D91 ran."
            ),
        },
        "n_agents_with_within_agent_split": len(within_agent_splits),
        "within_agent_splits": within_agent_splits,
        "within_agent_high_minus_low_opponent_score": mean_sd_n(diffs),
        "within_agent_high_minus_low_diff_ci": bootstrap_diff_ci(
            [row["high_half_mean_opponent_score"] for row in within_agent_splits],
            [row["low_half_mean_opponent_score"] for row in within_agent_splits],
        )
        if within_agent_splits
        else None,
        "within_agent_mean_pearson_r": statistics.mean(positive_rs) if positive_rs else None,
        "within_agent_n_positive_r": sum(1 for r in positive_rs if r > 0),
        "within_agent_n_negative_r": sum(1 for r in positive_rs if r < 0),
        "competitive_efficiency_ratio_note": (
            "opponent_over_own_delta_ratio mirrors D89/D91's frozen competitive-efficiency "
            "gate (selected opponent-score increase <= 40% of selected own-score increase; "
            "D89 unconditional factory = 0.511 FAIL, D91's exact selector rule = 0.337 PASS) "
            "-- computed here per agent from real field high-vs-low-planting-half games, "
            "not from a controlled panel."
        ),
        "pooled_opponent_over_own_delta_ratio": mean_sd_n(valid_ratios),
        "n_agents_ratio_at_most_0.40": sum(1 for ratio in valid_ratios if ratio <= 0.40),
        "n_agents_ratio_over_0.40": sum(1 for ratio in valid_ratios if ratio > 0.40),
    }


@dataclass
class Generation:
    cell: tuple
    kind: str
    plant_turn: int
    provenance: str  # "bank_seeded" | "harvest_seeded" | "unknown"
    end_turn: int | None = None
    ever_harvested_by_owner: bool = False
    self_chopped: bool = False
    opponent_chopped: bool = False


def classify_peer_game(game_id: int, own_seat: int) -> list[Generation] | None:
    decoded_tuple = decode_game(game_id)
    if decoded_tuple is None:
        return None
    _raw, decoded, trajectory = decoded_tuple
    states = decoded["states"]
    trajectory_by_turn = {row["t"]: row for row in trajectory}

    last_acquisition: dict[int, tuple[str, str]] = {}  # unit_id -> (kind, "PICK"|"HARVEST")
    open_generations: dict[tuple, Generation] = {}  # cell -> Generation (still alive)
    all_generations: list[Generation] = []

    for turn in range(1, len(states)):
        before = states[turn - 1]
        row = trajectory_by_turn.get(turn)
        if row is None:
            continue
        before_units_by_id = {u["id"]: u for u in before["units"]}
        before_plants_by_cell = {(p["x"], p["y"]): p for p in before["plants"]}
        for player in (0, 1):
            for command in action_commands(row.get(f"commands{player}")):
                fields = command.split()
                if len(fields) < 2:
                    continue
                verb = fields[0].upper()
                try:
                    unit_id = int(fields[1])
                except ValueError:
                    continue
                unit = before_units_by_id.get(unit_id)
                if unit is None or unit["player"] != player:
                    continue
                cell = (unit["x"], unit["y"])
                if verb == "PICK" and len(fields) >= 3:
                    last_acquisition[unit_id] = (fields[2].upper(), "PICK")
                elif verb == "HARVEST":
                    plant = before_plants_by_cell.get(cell)
                    if plant is not None:
                        last_acquisition[unit_id] = (plant["type"], "HARVEST")
                    if player == own_seat and plant is not None:
                        gen = open_generations.get(cell)
                        if gen is not None:
                            gen.ever_harvested_by_owner = True
                elif verb == "PLANT" and len(fields) >= 3 and player == own_seat:
                    item = fields[2].upper()
                    source = last_acquisition.get(unit_id)
                    if source is not None and source[0] == item:
                        prov = "bank_seeded" if source[1] == "PICK" else "harvest_seeded"
                    else:
                        prov = "unknown"
                    gen = Generation(cell=cell, kind=item, plant_turn=turn, provenance=prov)
                    open_generations[cell] = gen
                    all_generations.append(gen)
                elif verb == "CHOP":
                    plant = before_plants_by_cell.get(cell)
                    if plant is None:
                        continue
                    gen = open_generations.get(cell)
                    if gen is None:
                        continue
                    if player == own_seat:
                        gen.self_chopped = True
                    else:
                        gen.opponent_chopped = True

        after = states[turn]
        after_plants_by_cell = {(p["x"], p["y"]): p for p in after["plants"]}
        for cell, gen in list(open_generations.items()):
            still_alive = cell in after_plants_by_cell and after_plants_by_cell[cell]["type"] == gen.kind
            if not still_alive:
                gen.end_turn = turn
                del open_generations[cell]
    for cell, gen in open_generations.items():
        gen.end_turn = len(states) - 1
    return all_generations


def peak_concurrency(generations: list[Generation], total_turns: int) -> int:
    if not generations:
        return 0
    delta = [0] * (total_turns + 2)
    for gen in generations:
        start = gen.plant_turn
        end = gen.end_turn if gen.end_turn is not None else total_turns
        end = max(end, start)
        delta[start] += 1
        delta[min(end + 1, total_turns + 1)] -= 1
    running = 0
    peak = 0
    for value in delta:
        running += value
        peak = max(peak, running)
    return peak


def sample_peer_generation_stats(
    cohort_agent_ids: list[int], occurrences_by_agent: dict[int, list[tuple[dict, int]]]
) -> dict:
    provenance_counter: Counter = Counter()
    disposition_counter: Counter = Counter()
    peaks = []
    means = []
    n_games_sampled = 0
    n_games_failed = 0
    per_agent_rows = []
    for agent_id in cohort_agent_ids:
        occs = sorted(
            occurrences_by_agent.get(agent_id, []), key=lambda pair: pair[0]["gameId"]
        )[:PEER_SAMPLE_GAMES_PER_AGENT]
        agent_gens = 0
        agent_games = 0
        for game, seat in occs:
            gens = classify_peer_game(game["gameId"], seat)
            if gens is None:
                n_games_failed += 1
                continue
            n_games_sampled += 1
            agent_games += 1
            total_turns = game.get("n_turns", 300)
            peaks.append(peak_concurrency(gens, total_turns))
            means.append(len(gens))
            agent_gens += len(gens)
            for gen in gens:
                provenance_counter[gen.provenance] += 1
                if gen.ever_harvested_by_owner:
                    disposition_counter["ever_harvested"] += 1
                if gen.self_chopped:
                    disposition_counter["self_chopped"] += 1
                if gen.opponent_chopped:
                    disposition_counter["opponent_chopped"] += 1
                if not gen.ever_harvested_by_owner and not gen.self_chopped and not gen.opponent_chopped:
                    disposition_counter["untouched_or_expired"] += 1
        per_agent_rows.append(
            {"agent_id": agent_id, "n_games_sampled": agent_games, "n_generations": agent_gens}
        )
    n_generations = sum(provenance_counter.values())
    return {
        "n_games_sampled": n_games_sampled,
        "n_games_failed_decode": n_games_failed,
        "n_generations_observed": n_generations,
        "provenance_counts": dict(provenance_counter),
        "provenance_rates": {
            key: value / n_generations for key, value in provenance_counter.items()
        }
        if n_generations
        else {},
        "disposition_counts": dict(disposition_counter),
        "disposition_rates": {
            key: value / n_generations for key, value in disposition_counter.items()
        }
        if n_generations
        else {},
        "concurrent_live_crops_peak": mean_sd_n(peaks),
        "generations_per_game": mean_sd_n(means),
        "per_agent": per_agent_rows,
    }


# ---------------------------------------------------------------------------
# D89/D91/D92 ledger citations -- hardcoded from the frozen result docs (read-only
# citation, not recomputed): data/analysis/live-agent-6553250/d89a-banana-seed-factory-
# result-2026-07-21.md, d91c-factory-activation-selector-protocol-2026-07-21.md,
# d92-factory-dual-value-result-2026-07-21.md.
# ---------------------------------------------------------------------------
LEDGER_CITATIONS = {
    "D89_full_factory_discovery_256_tasks": {
        "source": "data/analysis/live-agent-6553250/d89a-banana-seed-factory-result-2026-07-21.md",
        "activates": "256/256 tasks, both seats, all 8 opponent families",
        "seeding": "plants ALL 1,344 initial bank BANANAs immediately (5.25/task) -- unconditional bank-seeded bootstrap, no selector",
        "sustained_loop": "252/256 tasks (98.4%) reach a sustained own-harvest/replant loop",
        "harvests_per_task": 10729 / 256,
        "renewable_plants_per_task": 10611 / 256,
        "own_score_delta": 162.305,
        "wood_delta": 40.590,
        "successful_plants_delta": 35.688,
        "own_crop_harvested_fruits_delta": 36.176,
        "margin_delta": 79.441,
        "margin_ci95": [40.991, 117.892],
        "catastrophes": "26 -> 11",
        "negative_margin_mass_ratio": 0.584,
        "safety_gate_failures": {
            "worst_opponent_family_mean": {"required": ">= -5", "observed": "gold_adaptive -6.938"},
            "active_p10_margin_delta": {"required": ">= -20", "observed": -72},
            "active_worst_margin_delta": {"required": ">= -60", "observed": -235},
            "mean_opponent_score_delta": {"required": "<= +1", "observed": 82.863},
        },
        "causal_decomposition": {
            "direct_theft_of_our_crops_score_equiv": 12.453,
            "opponent_own_created_crops_score_equiv": 76.508,
            "opponent_own_created_crops_breakdown_raw_units": {"wood": 16.461, "fruit": 10.680},
            "our_owned_crop_acquisition_score_equiv": 316.254,
            "our_natural_plus_opponent_source_acquisition_delta": -117.508,
            "interpretation": (
                "Direct theft of OUR crops is a minor term (+12.5). The dominant leak "
                "(+76.5 of +82.9 total) is the OPPONENT'S OWN economy accelerating -- "
                "private production relaxes the pressure our suppression/contest normally "
                "applies to their loop, not a direct resource gift."
            ),
        },
        "efficiency_ratio_opponent_over_own_gain": 82.863 / 162.305,
    },
    "D88_yaichi_factory_lineage_boundary": {
        "source": "d89a result doc, 'Next eligible experiment' section, citing D88",
        "bank_seeded_crops_harvested": "350/363 (96.4%)",
        "harvest_seeded_descendants_harvested": "4/358 (1.1%)",
        "harvest_seeded_descendants_chopped": "317/358 (88.5%)",
        "interpretation": (
            "Even inside the tested factory design, bank-seeded plantings are the ones "
            "that get harvested; harvest-seeded 'renewable' descendants are overwhelmingly "
            "chopped for wood, not re-harvested -- 'renewable descendants remain conversion "
            "stock for the wood worker and are never ordinary harvest targets' (D89a doc)."
        ),
    },
    "D91_activation_selector_discovery_256_tasks": {
        "source": (
            "data/analysis/live-agent-6553250/d91c-factory-activation-selector-protocol-2026-07-21.md "
            "(pre-registered protocol) and d91-factory-activation-selector-result-2026-07-21.md (result -- authoritative for pass/fail)"
        ),
        "predicate": "live_plants<=20 AND fruits>=27 AND banana_plants>=6, evaluated once at first observed 2-worker state",
        "selects": "50/256 consumed development tasks (19.5%)",
        "development_value": "+31.012 overall / +158.780 selected mean margin; selected own/opponent score +239.520/+80.740; 47 improve, 3 regress, 0 tie; p10 +20, worst -25; every opponent family positive (development figures -- select the rule, not validation)",
        "competitive_efficiency_gate_result": (
            "PASSED: opponent/own growth ratio 0.337, below the frozen 0.40 ceiling "
            "(D89's own unconditional-factory ratio is 0.511, which fails it). This is NOT "
            "why D91 was rejected."
        ),
        "actual_rejection_reason_map_transfer_failure": (
            "Selection concentrated on only 5 of 16 discovery maps; most maps stayed exact-resident "
            "(abstained). The 16 map-level means have a normal 95% CI of [-1.738, +63.761] -- the "
            "lower bound is negative, failing the preregistered map-cluster-nonnegative gate. "
            "Reciprocal eight-map fits (fit on one half, evaluate the other) stay positive on mean "
            "but blow the -60 tail floor (held worst -96 to -112). Verdict: 'a sparse map cluster, "
            "not yet a transferable first-move policy' -- rejected on GENERALIZATION/robustness, "
            "not on the safety/efficiency ratio, which this exact rule already satisfied."
        ),
    },
    "D92_dual_value_denial_composition": {
        "source": "data/analysis/live-agent-6553250/d92-factory-dual-value-result-2026-07-21.md",
        "broad_dual_value_vs_D89": {"mean_margin_delta": -6.371, "own_score_delta": -20.254, "opponent_score_delta": -13.883},
        "trained_only_dual_value_vs_D89": {
            "mean_margin_delta": -5.609,
            "opponent_score_delta": 0.188,
            "opponent_crop_target_selections": 898,
        },
        "verdict": (
            "Rejected. Targeting a known opponent crop with the TRAINED worker doesn't move "
            "opponent score (too late/low-leverage; the worker's existing productive order "
            "dominates); taxing the STARTER (broad variant) suppresses opponent score but "
            "destroys more own score than it denies. The leak is in the STARTER's attention "
            "budget, not fixable by retargeting a different unit."
        ),
    },
    "D87_fresh_harvest_regeneration": {
        "source": "docs/CONSTRAINTS.md (e) Renewal & farm grammars",
        "result": "-51.161 active margin; adds 3.866 plants/active-task but exactly zero own-crop harvests",
        "interpretation": "the resident's own regeneration grammar converts plants toward wood, not toward a renewable orchard -- same mechanism this diagnostic finds live in production (idle_regeneration/endgame_candidates conversion-to-wood path)",
    },
}


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def main() -> int:
    global PEER_SAMPLE_GAMES_PER_AGENT
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--peer-sample-per-agent",
        type=int,
        default=PEER_SAMPLE_GAMES_PER_AGENT,
        help="cap on peer games decoded per agent for the concurrency/provenance sample",
    )
    args = parser.parse_args()
    PEER_SAMPLE_GAMES_PER_AGENT = args.peer_sample_per_agent

    t0 = time.time()
    clean_games, leaderboard = load_corpus()
    resident_games = [
        game
        for game in clean_games
        if any(p["agentId"] == RESIDENT_AGENT_ID for p in game["players"])
    ]
    print(f"[{time.time()-t0:6.1f}s] corpus loaded: {len(clean_games)} clean, "
          f"{len(resident_games)} resident games", file=sys.stderr)

    deploy_check = deployed_source_check()
    print(f"[{time.time()-t0:6.1f}s] deployed-source check: "
          f"contains_banana_factory={deploy_check.get('contains_banana_factory_subsystem')}",
          file=sys.stderr)

    # --- Items 2+3: resident games, selector predicate + threshold sweep ---
    resident_rows = []
    for i, game in enumerate(resident_games):
        resident_rows.append(process_resident_game(game))
        if (i + 1) % 50 == 0:
            print(f"[{time.time()-t0:6.1f}s] decoded {i+1}/{len(resident_games)} resident games",
                  file=sys.stderr)
    fire_rate_summary = summarize_fire_rate(resident_rows)
    sweep = threshold_sweep(resident_rows)
    print(f"[{time.time()-t0:6.1f}s] resident decode+sweep done: "
          f"fire_rate={fire_rate_summary['fire_rate_current_selector']}", file=sys.stderr)

    # --- Item 4: peer cohort ---
    cohort = build_cohort(clean_games, leaderboard)
    strong_ids = {row["agent_id"] for row in cohort["strong"]}
    peer_weak_ids = {row["agent_id"] for row in cohort["peer_weak"]}
    all_peer_ids = strong_ids | peer_weak_ids
    occurrences_by_agent = index_agent_occurrences(clean_games, all_peer_ids)
    strong_occurrences = [
        pair for agent_id in strong_ids for pair in occurrences_by_agent.get(agent_id, [])
    ]
    peer_weak_occurrences = [
        pair for agent_id in peer_weak_ids for pair in occurrences_by_agent.get(agent_id, [])
    ]
    resident_occurrences = [(game, own_index) for game in resident_games
                             for own_index in [next(p["index"] for p in game["players"]
                                                      if p["agentId"] == RESIDENT_AGENT_ID)]]

    print(f"[{time.time()-t0:6.1f}s] peer cohort: {len(strong_ids)} STRONG "
          f"({len(strong_occurrences)} occ), {len(peer_weak_ids)} PEER_WEAK "
          f"({len(peer_weak_occurrences)} occ)", file=sys.stderr)

    design_comparison = {
        "resident": {
            **cheap_plant_and_score_stats(resident_occurrences),
            "first_plant_timing": fire_rate_summary["view_turn_at_roster_2"],
            "note": "own-reap rate / strict-role-separated cited from B4.4 (D101a reuse), not recomputed here",
        },
        "strong": {
            **cheap_plant_and_score_stats(strong_occurrences),
        },
        "peer_weak": {
            **cheap_plant_and_score_stats(peer_weak_occurrences),
        },
    }

    print(f"[{time.time()-t0:6.1f}s] computing first-plant timing over full peer cohort "
          f"({len(strong_occurrences)+len(peer_weak_occurrences)} occurrences, events-only, "
          f"no full diff decode)...", file=sys.stderr)
    design_comparison["strong"]["first_plant_timing"] = first_plant_timing(strong_occurrences)
    design_comparison["peer_weak"]["first_plant_timing"] = first_plant_timing(peer_weak_occurrences)
    print(f"[{time.time()-t0:6.1f}s] first-plant timing done", file=sys.stderr)

    # --- Item 5: opponent-score correlation (cheap, full population) ---
    risk_strong = opponent_score_correlation(strong_occurrences)
    risk_peer_weak = opponent_score_correlation(peer_weak_occurrences)
    risk_all = opponent_score_correlation(strong_occurrences + peer_weak_occurrences)
    print(f"[{time.time()-t0:6.1f}s] opponent-score correlation done", file=sys.stderr)

    # --- Item 4 (expensive part): bounded per-agent sample, full decode ---
    print(f"[{time.time()-t0:6.1f}s] sampling up to {PEER_SAMPLE_GAMES_PER_AGENT} games/agent "
          f"for concurrency+provenance decode ({len(all_peer_ids)} agents)...", file=sys.stderr)
    sample_stats = sample_peer_generation_stats(sorted(all_peer_ids), occurrences_by_agent)
    print(f"[{time.time()-t0:6.1f}s] sample decode done: "
          f"{sample_stats['n_games_sampled']} games, "
          f"{sample_stats['n_generations_observed']} generations", file=sys.stderr)

    output = {
        "schema": SCHEMA,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "elapsed_seconds": time.time() - t0,
        "provenance": {
            "resident_agent_id": RESIDENT_AGENT_ID,
            "corpus_clean_games": len(clean_games),
            "resident_clean_games": len(resident_games),
            "leaderboard_snapshot": str(latest_leaderboard_path()),
            "deployed_source_check": deploy_check,
        },
        "gate_pin": {
            "selector_thresholds": {
                "max_plants": SELECTOR_MAX_PLANTS,
                "min_fruits": SELECTOR_MIN_FRUITS,
                "min_banana": SELECTOR_MIN_BANANA,
            },
            "code_refs": GATE_CODE_REFS,
        },
        "item2_fire_rate": fire_rate_summary,
        "item3_threshold_sweep": sweep,
        "item4_design_comparison": design_comparison,
        "item4_sample_based_generation_stats": sample_stats,
        "item4_ledger_citations": LEDGER_CITATIONS,
        "item5_risk_opponent_score_correlation": {
            "strong": risk_strong,
            "peer_weak": risk_peer_weak,
            "pooled_strong_plus_peer_weak": risk_all,
        },
        "cohort": {
            "n_strong": len(strong_ids),
            "n_peer_weak": len(peer_weak_ids),
            "strong_agent_ids": sorted(strong_ids),
            "peer_weak_agent_ids": sorted(peer_weak_ids),
        },
        "resident_rows": resident_rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=1, default=str) + "\n")
    print(f"[{time.time()-t0:6.1f}s] wrote {args.output}", file=sys.stderr)

    print(json.dumps(
        {
            "n_resident_games": fire_rate_summary["n_decode_ok"],
            "fire_rate_current_selector": fire_rate_summary["fire_rate_current_selector"],
            "n_distinct_maps": fire_rate_summary["n_distinct_maps"],
            "view_turn_at_roster_2_median": fire_rate_summary["view_turn_at_roster_2"]["median"],
            "deployed_source_contains_banana_factory": deploy_check.get(
                "contains_banana_factory_subsystem"
            ),
            "fully_open_scenario_fire_rate": next(
                s["fire_rate"] for s in sweep["named_scenarios"] if s["name"] == "fully_open_no_selector"
            ),
        },
        indent=2,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
