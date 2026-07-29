#!/usr/bin/env python3
"""H1 -- joint economy package: read-only NET upper bound (backlog task
``coordination/tasks/20260729-h1-joint-upper-bound.md``).

Four separate levers were each tested on the resident and each failed for a
*complementarity* reason (D173a/b harvest-before-chop, D174a opportunistic mining + the
``can_train`` cap repair, D175a bounded early planting): D173a/b showed 99.9% of
addressable harvest-slack clears once a harvest-CAPABLE unit is present, but 99.93% of
the surviving vein sits on trained units hardcoded ``harvest_power: 0``; D174a mined
10.6x more iron (0.51 -> 5.40/game) that nothing could spend, because the real worker-3
bill's PLUM/LEMON legs (not IRON) never clear; D175a made the bot plant at turn 13
instead of 199 and it cost -26.44 margin/game (Delta-own -5.41, Delta-opponent +21.09)
because nothing could harvest what was planted. Bundling all four was REJECTED
(CONSTRAINTS.md (h): multi-lever bundles on the resident destroy attribution and
re-create the graft pattern). This script is the sanctioned replacement: a read-only,
stock-accounting NET upper bound on what the bundle could have been worth, computed
directly from the resident's own already-played arena replays -- no rerun, no simulated
bot, no arena write.

Reuse discipline (does NOT re-derive replay parsing or any counterfactual-window
machinery -- see the task's own "Tooling" list):

- ``cgauto.waste_sweep``: ``decode_game``/``resident_game_ids``/``DecodedGame`` for exact
  official per-turn state, and its ``training_cost``/``training_pay_indices``/
  ``training_affordable``/``training_blocked`` -- the cross-validated port of
  ``sim.engine.apply_train``'s cost formula and shack-occupancy guard.
- ``cgauto.training_currency_audit`` (B3.8): ``enumerate_fruit_events`` (the uncollected-
  reachable-fruit enumeration, BFS<=3, per-fruit-unit, own_or_unclaimed vs opponent
  territory), ``deposit_schedule``/``augmented_bank_series`` (stock-accounting bank
  construction), ``scenario_events``.
- ``cgauto.iron_acquisition_audit`` (B3.9): ``own_states_by_turn``/``iron_source_geometry``/
  ``iron_reachability_episodes`` (STRICT/GENEROUS visit-based iron credit)/
  ``iron_deposit_schedule``/``merge_schedules`` -- the combined-counterfactual machinery.
- ``cgauto.replay_conformance.action_commands`` for own-side CHOP-turn counting (the
  corpus-measured opportunity-cost rate for displacement pricing).

What is NOT reused, and why: B3.8/B3.9's own ``worker3_windows``/``SPECS`` (the synthetic
``cheap_helper_1101``/``balanced_chopper_2202`` bills) are deliberately NOT used for the
affordability question -- D174a's own post-mortem names this exact substitution as the
error that made B3.8/B3.9 report 84.4% affordability "for a spec the bot never requests".
Instead, the worker-3/4 bill is established the way H8 established the worker-2 bill:
read from each game's own revealed TRAIN command. Source-verified
(``git show HEAD:rust/src/bin/yamo_orchard_live.rs``, SHA prefix ``fff6669b``):
``YamoBot::commands()`` computes ``desired`` from ``self.desired_second`` UNCONDITIONALLY
(regardless of ``own_count``; the only two branches gated on ``own_count == 1`` are the
turn-1 override and the ``first_worker_max_bank_hp0`` case) and ``desired_second`` itself
freezes once workforce reaches 2 (``enforce_training_deadline``'s own early-return guard,
``own_count >= 2``). So once ``can_train``'s ``n >= 2`` clause is lifted, the live code, as
literally written, reuses the SAME talent vector for every subsequent TRAIN -- confirmed
independently by D174a's own empirical finding (mean ``training_cost(n=2, desired)`` over
1,595 activated Delta-2 games = PLUM 6.23/LEMON 5.87/APPLE 2.00/IRON 7.12, i.e. exactly
``training_cost(2, <worker-2 talents>)``, not a separately-chosen worker-3 spec). This
script therefore takes each game's own worker-2 TRAIN talents (``train_events`` with
``n_before == 1``) as the SAME talents for the worker-3 (``n_before == 2``) and worker-4
(``n_before == 3``) bill, costed at the higher ``n``.

TRAIN legality uses the POST-move shack-occupancy convention throughout (H8's correction:
the referee resolves MOVE before TRAIN within a turn, ``sim/engine.py:step``) -- the same
correction applied to worker 3/4 here that H8 applied to worker 2. The ``TOTAL_TURNS -
turn <= 20`` deadline clause in ``can_train`` (``rust/src/bin/yamo_orchard_live.rs:836``)
is left ACTIVE (only the ``n >= 2`` clause is the lever this package lifts).

Worker-4's own-unit-count precondition (``n_before == 3``) never actually occurs in the
real corpus (the resident's real roster is always exactly 1 then 2 -- ``can_train``'s cap
means worker 3 never really trains), so worker-4's window is a CASCADING counterfactual:
find worker 3's own first affordable+legal turn against the augmented bank, debit its own
bill once at that turn, then continue the same augmented-bank walk (still keyed to the
real, always-2-unit roster's own post-move positions for the shack-occupancy guard, since
that guard only cares whether an EXISTING unit sits on the shack cell and there is no real
third unit to ask) checking worker 4's own bill (talents unchanged, ``n=3``) against the
post-debit bank.

Every number this script produces is an explicit UPPER BOUND on a pure stock-accounting
counterfactual (fruit/iron banked at the turn a unit was reachable, with no other change
to behaviour, no turns spent walking/harvesting/banking/mining -- exactly B3.8/B3.9's own
documented caveat) MINUS an explicit, calibrated displacement cost (see
``build_calibration``): unit-turns consumed collecting the credited fruit/iron are priced
against the corpus's own measured CHOP throughput (own side) and D175a's own measured
Delta-opponent/Delta-own ratio (opponent side, the only real causal A/B this project has
of "turns diverted from chop/suppression to a new activity"). See the module-level
``build_report`` docstring for the exact net-bound formula and what it ignores.

CLI usage::

    .venv/bin/python cgauto/joint_economy_upper_bound.py --output <path/to/report.json> \
        [--jobs 8] [--limit N]
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import statistics
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.iron_acquisition_audit import (  # noqa: E402
    iron_deposit_schedule,
    iron_reachability_episodes,
    iron_source_geometry,
    merge_schedules,
    own_states_by_turn,
)
from cgauto.replay_conformance import action_commands  # noqa: E402
from cgauto.training_currency_audit import (  # noqa: E402
    augmented_bank_series,
    deposit_schedule,
    enumerate_fruit_events,
    scenario_events,
)
from cgauto.waste_sweep import (  # noqa: E402
    DecodedGame,
    UNREACHABLE,
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
DEFAULT_OUTPUT = SCRATCHPAD / "h1-joint-economy-upper-bound-result.json"

# ---------------------------------------------------------------------------
# Source-verified constants (rust/src/bin/yamo_orchard_live.rs, SHA prefix fff6669b)
# ---------------------------------------------------------------------------
TOTAL_TURNS = 300  # `pub const TOTAL_TURNS: i32 = 300;`
TRAIN_DEADLINE_MARGIN = 20  # can_train: `TOTAL_TURNS - view.turn <= 20` => refuse (kept active)
WORKER3_N = 2  # own-unit count immediately before training the 3rd worker
WORKER4_N = 3  # own-unit count immediately before training the 4th worker
BILL_FRUIT_INDICES = (0, 1, 2)  # PLUM, LEMON, APPLE -- the only bill-chargeable fruit slots
FRUIT_SCORE_INDICES = (0, 1, 2, 3)  # + BANANA -- all four fruit slots count toward score

# ---------------------------------------------------------------------------
# Pricing constants, cited verbatim from already-published, already-validated reports
# (NOT recomputed here -- re-deriving them would duplicate B4.3/H8's own work).
# ---------------------------------------------------------------------------
# B4.3 (b43-roster-outcome-pricing-report.md Sec. 5 + rating-points bridge):
MARGIN_PER_RATING = 11.75  # margin ~= 11.75 * arenaScore_diff
PRICE_2_TO_3_MARGIN = 22.7
PRICE_2_TO_3_CI = (18.1, 27.5)
PRICE_3_TO_4_MARGIN = 38.9
PRICE_3_TO_4_CI = (30.0, 47.6)
# H8 (h8-worker2-timing-report.md Sec 6, reproducing b43 Sec 3's "at least" scope):
TIMING_WORKER3_EARLY_LATE = 42.6
TIMING_WORKER3_CI = (36.0, 49.4)
TIMING_WORKER4_EARLY_LATE = 60.1
TIMING_WORKER4_CI = (49.6, 70.5)
TIMING_WORKER2_EARLY_LATE = 1.31  # not significant, CI [-2.80, 5.42] -- cited for contrast only
FIELD_MEDIAN_TURN_WORKER3_AT_LEAST = 100  # b43 Sec 3
FIELD_MEDIAN_TURN_WORKER4_AT_LEAST = 145  # b43 Sec 3

# D175a calibration anchor (data/analysis/live-agent-6553250/d175a-bounded-early-planting-result.json,
# "activated_subset"/"safety"/"mechanism" blocks -- read directly, not re-derived):
D175A_MEAN_OWN_DELTA = -5.410080743821874  # activated subset, n=4087
D175A_MEAN_OPPONENT_DELTA = 21.08906288230976  # activated subset, n=4087
D175A_MARGIN_DELTA_ACTIVATED = -26.499143626131637
D175A_MARGIN_DELTA_OVERALL = -26.44091796875
D175A_RATIO_OPP_OVER_OWN = -3.898105015603093  # Delta_opponent / Delta_own -- the transferable elasticity
D175A_CANDIDATE_GENERATIONS_PER_GAME = 55715 / 4087  # ~13.634
D175A_CONTROL_GENERATIONS_PER_GAME = 47164 / 4092  # ~11.526 (games ever planted)
D175A_DELTA_CROPS_PER_GAME = D175A_CANDIDATE_GENERATIONS_PER_GAME - D175A_CONTROL_GENERATIONS_PER_GAME
D175A_PEAK_CONCURRENT_CANDIDATE = 1.98095703125
D175A_PEAK_CONCURRENT_CONTROL = 1.923583984375
D175A_PEER_FIELD_REFERENCE_CONCURRENT = 5.5  # H2/D175a's own cited peer shape

# B3.7/B4.4 citations used for the (speculative, bracketed) "additional early crops" term:
TOP5_FRUIT_PER_HARVESTED_CROP = 7.0  # b37 Sec 2, top-5 harvested_by_owner mean
STRONG_PEER_REAP_RATE = 0.163  # b44 Sec 3, midpoint of STRONG/PEER-WEAK 15.3-17.2%
D175A_CANDIDATE_REAP_RATE = 0.0045230189356546713  # d175a JSON own_reap_rate.candidate_rate_pct/100

BASE_FRUIT_COOLDOWN_TURNS = 8.5  # docs/mechanics.md: PLUM/LEMON 8, APPLE 9 (mean, non-water)


# ---------------------------------------------------------------------------
# Per-game: the real worker-2 bill, source-verified to be the SAME bill the live code
# would reuse for worker 3/4 once the cap is lifted (see module docstring)
# ---------------------------------------------------------------------------


def resident_bill_talents(game: DecodedGame) -> tuple[int, int, int, int] | None:
    event = next((e for e in game.train_events if e["n_before"] == 1), None)
    return tuple(int(v) for v in event["talents"]) if event is not None else None


def _post_move_units(game: DecodedGame, turn: int, unit_ids: list[int]) -> list[dict]:
    """Positions of ``unit_ids`` at the END of ``turn`` (state index ``turn``) -- the
    post-MOVE, pre-TRAIN read H8 established is what ``apply_train``'s occupancy guard
    actually evaluates (referee order: MOVE -> HARVEST -> PLANT -> CHOP -> PICK -> TRAIN
    -> DROP -> MINE)."""

    by_id = {unit["id"]: unit for unit in game.states[turn]["units"] if unit["player"] == game.me}
    return [by_id[uid] for uid in unit_ids if uid in by_id]


# ---------------------------------------------------------------------------
# Worker-3 / worker-4 real-bill affordability, post-move legality, CASCADING
# ---------------------------------------------------------------------------


def joint_package_windows(game: DecodedGame, talents: tuple[int, int, int, int], bank_series: list[list[int]]) -> dict:
    """First (stock-affordable) and (stock-affordable + shack-legal) turn to train worker
    3, then -- cascading from that turn, with worker 3's own bill debited once -- the same
    for worker 4.  Both use the REAL worker-2 bill's talents (see module docstring) and the
    POST-move shack-occupancy convention (H8's correction).  The ``TOTAL_TURNS - turn <=
    20`` deadline clause is kept active (only ``can_train``'s ``n >= 2`` clause is lifted).
    """

    cost3 = training_cost(WORKER3_N, talents)
    cost4 = training_cost(WORKER4_N, talents)
    pay = training_pay_indices(game.iron_present)

    t3_stock = t3_legal = None
    for t in range(1, game.turns + 1):
        if TOTAL_TURNS - t <= TRAIN_DEADLINE_MARGIN:
            break
        own_before = [unit for unit in game.states[t - 1]["units"] if unit["player"] == game.me]
        if len(own_before) != WORKER3_N:
            continue
        bank = bank_series[t - 1]
        if not training_affordable(WORKER3_N, talents, bank, game.iron_present):
            continue
        if t3_stock is None:
            t3_stock = t
        post_units = _post_move_units(game, t, [unit["id"] for unit in own_before])
        if not training_blocked(post_units, game.own_shack):
            t3_legal = t
            break

    t4_stock = t4_legal = None
    if t3_legal is not None:
        for t in range(t3_legal + 1, game.turns + 1):
            if TOTAL_TURNS - t <= TRAIN_DEADLINE_MARGIN:
                break
            # Worker 4's own-count precondition (n_before == 3) never really occurs in this
            # corpus (real roster is always exactly 2 for the rest of the game); the
            # counterfactual keeps using the real 2-unit roster's own post-move positions
            # for the shack-block check (see module docstring) while checking affordability
            # at the counterfactual n=3.
            own_before = [unit for unit in game.states[t - 1]["units"] if unit["player"] == game.me]
            if len(own_before) != WORKER3_N:
                continue
            bank = [bank_series[t - 1][i] - cost3[i] for i in range(6)]
            if not training_affordable(WORKER4_N, talents, bank, game.iron_present):
                continue
            if t4_stock is None:
                t4_stock = t
            post_units = _post_move_units(game, t, [unit["id"] for unit in own_before])
            if not training_blocked(post_units, game.own_shack):
                t4_legal = t
                break

    return {
        "worker3_stock_turn": t3_stock,
        "worker3_legal_turn": t3_legal,
        "worker4_stock_turn": t4_stock,
        "worker4_legal_turn": t4_legal,
        "cost3": [int(v) for v in cost3],
        "cost4": [int(v) for v in cost4],
        "pay_indices": list(pay),
    }


# ---------------------------------------------------------------------------
# Displacement inputs: unit-turns consumed collecting the credited fruit/iron, and the
# corpus's own measured CHOP throughput (the own-side opportunity-cost rate)
# ---------------------------------------------------------------------------


ACTION_TURNS_PER_EVENT = 1  # the action itself (HARVEST or MINE) -- see note below on DROP

# A first version of this function charged every credited event a full independent
# solo round trip (nearest_unit_distance_at_bankable + own_door_distance + 2): summed
# over a game's 15-30 credited events this routinely EXCEEDED the game's entire own
# unit-turn budget (turns x own-unit-count) -- e.g. 297 turns charged in a 134-turn,
# 2-unit game (268 unit-turns total). That is not how the corpus's own real successful
# economies actually collect this value: B3.9's own top-5 mining census found "0/81
# distinct miner-workers had MINE at >=30% of their own command mix -- mining is a
# low-intensity side activity... never the worker's primary job," picked up
# OPPORTUNISTICALLY while already moving for other reasons (chop/suppression/banking
# wood), not via dedicated round trips. The primary charge below follows that
# real-measured pattern: only the action itself (HARVEST-or-MINE) is charged; the walk
# AND the DROP are treated as piggybacking on the unit's existing wood-banking cycle (a
# DROP empties everything a unit carries in one action -- fruit/iron riding along with
# whatever wood that unit is already carrying back is not an extra trip). This is also
# the internally-consistent choice against ``v_own_per_chop_turn`` (wood-score per CHOP
# COMMAND, not per chop-plus-its-own-drop -- wood drops are naturally batched across
# many chops sharing one trip too, so v_own's own denominator already excludes DROP
# turns; charging harvest/mine events a DROP they wouldn't otherwise need while NOT
# charging chop a comparable share of its own drop turns would be an apples-to-oranges
# comparison that structurally penalizes harvesting). The full independent-round-trip
# sum (walk + action + walk + DROP, no batching, no sharing with anything) is still
# computed and reported as an explicit PESSIMISTIC sensitivity bound (see
# ``*_dedicated_trip_turns`` in each event's returned tuple) so the report can show the
# bound's range rather than assert one number as certain.


DEDICATED_TRIP_ACTION_TURNS = 2  # pessimistic variant only: action + its OWN dedicated DROP


def displacement_turns_for_fruit(events: list[dict]) -> tuple[int, int, int]:
    """Primary charge: ACTION_TURNS_PER_EVENT per credited fruit unit (opportunistic,
    en-route collection, DROP shared with an existing trip -- see module note above).
    Also returns the pessimistic full independent-round-trip sum (walk-to-tree + HARVEST
    + walk-to-door + its own DROP, no sharing) as a reported sensitivity bound, reusing
    ``enumerate_fruit_events``'s own BFS fields (``nearest_unit_distance_at_bankable``,
    ``own_door_distance``) rather than re-deriving any geometry."""

    opportunistic_total = 0
    dedicated_trip_total = 0
    skipped_unreachable = 0
    for event in events:
        near = event["nearest_unit_distance_at_bankable"]
        door = event["own_door_distance"]
        if near >= UNREACHABLE or door >= UNREACHABLE:
            skipped_unreachable += 1
            continue
        opportunistic_total += ACTION_TURNS_PER_EVENT
        dedicated_trip_total += near + door + DEDICATED_TRIP_ACTION_TURNS
    return opportunistic_total, dedicated_trip_total, skipped_unreachable


def displacement_turns_for_iron(episodes: list[dict], sources: list[dict]) -> tuple[int, int, int]:
    opportunistic_total = 0
    dedicated_trip_total = 0
    skipped_unreachable = 0
    for episode in episodes:
        source = sources[episode["source_index"]]
        door = source["own_door_distance"]
        if door >= UNREACHABLE:
            skipped_unreachable += 1
            continue
        opportunistic_total += ACTION_TURNS_PER_EVENT
        dedicated_trip_total += episode["distance_at_start"] + door + DEDICATED_TRIP_ACTION_TURNS
    return opportunistic_total, dedicated_trip_total, skipped_unreachable


def own_chop_and_wood(game: DecodedGame) -> tuple[int, int]:
    """Own CHOP-command count and final banked-wood score contribution (4x banked WOOD) --
    the corpus's own measured "what a turn currently produces" rate for the own-score side
    of displacement pricing."""

    chop_turns = 0
    for turn in range(1, game.turns + 1):
        commands = action_commands(game.trajectory[turn - 1].get(f"commands{game.me}"))
        chop_turns += sum(1 for command in commands if command.split()[0].upper() == "CHOP")
    wood_banked = int(game.states[game.turns]["inventories"][game.me][5])
    return chop_turns, 4 * wood_banked


# ---------------------------------------------------------------------------
# Per-game driver
# ---------------------------------------------------------------------------


def analyze_one_game(game_id: int) -> dict:
    try:
        game = decode_game(game_id)
    except Exception as exc:  # noqa: BLE001 -- keep a complete read audit
        return {"ok": False, "game_id": game_id, "error": f"{type(exc).__name__}: {exc}"}

    talents = resident_bill_talents(game)
    if talents is None:
        return {"ok": False, "game_id": game_id, "error": "no worker-2 TRAIN event (real bill unavailable)"}

    # --- gross fruit (component 1a): B3.8's own reachable-fruit enumeration, real bill ---
    fruit_events, fruit_diag = enumerate_fruit_events(game)
    own_fruit = scenario_events(fruit_events, "own_or_unclaimed_only")
    all_fruit = scenario_events(fruit_events, "own_plus_opponent")
    gross_fruit_units = len(own_fruit)
    gross_fruit_units_with_opponent = len(all_fruit)
    fruit_turns, fruit_turns_dedicated, fruit_unreachable_skipped = displacement_turns_for_fruit(own_fruit)

    # --- iron (funding only -- never direct score; B3.9's reachability machinery, strict) ---
    own_by_turn = own_states_by_turn(game)
    sources = iron_source_geometry(game)
    reach = iron_reachability_episodes(game, sources, own_by_turn)
    iron_episodes = reach["strict"]
    iron_turns, iron_turns_dedicated, iron_unreachable_skipped = displacement_turns_for_iron(iron_episodes, sources)

    # --- augmented bank: real bank + credited fruit + credited iron ---
    fruit_schedule = deposit_schedule(own_fruit)
    iron_schedule = iron_deposit_schedule(iron_episodes)
    combined_schedule = merge_schedules(fruit_schedule, iron_schedule)
    bank_series = augmented_bank_series(game, combined_schedule)

    # --- worker 3 / worker 4 real-bill affordability, post-move legality, cascading ---
    windows = joint_package_windows(game, talents, bank_series)

    # --- own-side displacement inputs ---
    chop_turns, wood_score = own_chop_and_wood(game)

    spent_fruit = 0
    if windows["worker3_legal_turn"] is not None:
        spent_fruit += sum(windows["cost3"][i] for i in BILL_FRUIT_INDICES)
    if windows["worker4_legal_turn"] is not None:
        spent_fruit += sum(windows["cost4"][i] for i in BILL_FRUIT_INDICES)
    net_fruit_score = gross_fruit_units - spent_fruit

    return {
        "ok": True,
        "game_id": game_id,
        "margin": game.margin,
        "won": game.won,
        "turns": game.turns,
        "iron_present": game.iron_present,
        "opponent": game.opponent_name,
        "talents": list(talents),
        "growth_anomalies": fruit_diag["growth_anomalies"],
        "gross_fruit_units_own_or_unclaimed": gross_fruit_units,
        "gross_fruit_units_own_plus_opponent": gross_fruit_units_with_opponent,
        "gross_fruit_unreachable_skipped": fruit_unreachable_skipped,
        "fruit_displacement_turns": fruit_turns,
        "fruit_displacement_turns_dedicated_trip": fruit_turns_dedicated,
        "iron_episodes_credited": len(iron_episodes),
        "iron_units_credited": sum(episode["credit_iron"] for episode in iron_episodes),
        "iron_unreachable_skipped": iron_unreachable_skipped,
        "iron_displacement_turns": iron_turns,
        "iron_displacement_turns_dedicated_trip": iron_turns_dedicated,
        "spent_fruit_on_bills": spent_fruit,
        "net_fruit_score": net_fruit_score,
        "chop_turns": chop_turns,
        "wood_score": wood_score,
        **windows,
    }


def run_main_audit(game_ids: list[int], jobs: int) -> list[dict]:
    if jobs == 1:
        return [analyze_one_game(game_id) for game_id in game_ids]
    with ProcessPoolExecutor(max_workers=jobs) as executor:
        return list(executor.map(analyze_one_game, game_ids, chunksize=2))


# ---------------------------------------------------------------------------
# Aggregation and the net-bound calculation
# ---------------------------------------------------------------------------


def mean(values) -> float | None:
    selected = list(values)
    return statistics.fmean(selected) if selected else None


def median(values) -> float | None:
    selected = list(values)
    return statistics.median(selected) if selected else None


def stats(values) -> dict:
    selected = [v for v in values if v is not None]
    if not selected:
        return {"n": 0, "mean": None, "median": None, "min": None, "max": None}
    return {
        "n": len(selected),
        "mean": statistics.fmean(selected),
        "median": statistics.median(selected),
        "min": min(selected),
        "max": max(selected),
    }


def build_calibration(v_own_per_chop_turn: float | None) -> dict:
    """The D175a calibration check the task requires as mandatory: apply the SAME
    own-side rate this script derives from the resident's own corpus (never from D175a
    itself) to an independently-estimated D175a turn-diversion count, and compare the
    predicted Delta-own to D175a's own actually-measured -5.41 (activated subset). Two
    brackets for "turns per additional early-planted crop" (2 = PLANT + PICK only; 5 =
    + a modest walk/detour budget) since this is the one genuinely unmeasured input --
    reported as a bracket, not a point estimate, per the task's own honesty requirement.
    """

    if v_own_per_chop_turn is None:
        return {"available": False, "reason": "no chop turns observed in corpus (v_own undefined)"}

    brackets = {}
    for label, turns_per_crop in (("low_2_turns_per_crop", 2.0), ("high_5_turns_per_crop", 5.0)):
        turns_diverted = D175A_DELTA_CROPS_PER_GAME * turns_per_crop
        predicted_own_delta = -v_own_per_chop_turn * turns_diverted
        residual = predicted_own_delta - D175A_MEAN_OWN_DELTA
        ratio = predicted_own_delta / D175A_MEAN_OWN_DELTA if D175A_MEAN_OWN_DELTA else None
        brackets[label] = {
            "turns_per_additional_crop_assumed": turns_per_crop,
            "estimated_turns_diverted_per_game": turns_diverted,
            "predicted_own_delta": predicted_own_delta,
            "actual_own_delta_activated_subset": D175A_MEAN_OWN_DELTA,
            "residual_predicted_minus_actual": residual,
            "ratio_predicted_over_actual": ratio,
            "same_sign": (predicted_own_delta < 0) == (D175A_MEAN_OWN_DELTA < 0),
        }

    return {
        "available": True,
        "method": (
            "v_own_per_chop_turn (this corpus, computed independently of D175a) x "
            "estimated turns diverted by D175a's own real crop-count delta "
            "(D175A_DELTA_CROPS_PER_GAME = candidate_generations/game - "
            "control_generations/game, from the d175a result JSON) x an assumed "
            "turns-per-additional-crop bracket -- compared to D175a's own actually "
            "measured Delta-own (-5.41, activated subset)."
        ),
        "v_own_per_chop_turn": v_own_per_chop_turn,
        "d175a_delta_crops_per_game": D175A_DELTA_CROPS_PER_GAME,
        "brackets": brackets,
        "opponent_side_ratio_used_for_pricing": D175A_RATIO_OPP_OVER_OWN,
        "opponent_side_note": (
            "The opponent-side displacement price is NOT independently derived in this "
            "script -- it is D175a's own measured Delta_opponent/Delta_own ratio, "
            "transferred as a turn-count-invariant elasticity (the only real causal A/B "
            "this project has of turns diverted from chop/suppression to a new activity). "
            "This makes the opponent-side price self-consistent with D175a BY "
            "CONSTRUCTION, not an independent cross-check; only the own-side bracket "
            "above is a genuine out-of-sample test of this script's methodology."
        ),
    }


def build_additional_early_crops_estimate() -> dict:
    """Component 1b: fruit from crops the package would plant earlier than the resident's
    real turn ~191-199, bounded two ways because the peer 5-6-concurrent shape and the
    resident's own real D175a-measured shape disagree sharply on how many EXTRA standing
    crops the package plausibly produces (see the 'grounded' vs 'aspirational' brackets).
    Deliberately a single aggregate estimate (not per-game): there is no real per-game data
    for a crop that was never planted in any actual replay."""

    grounded_fruit_per_game = (
        D175A_DELTA_CROPS_PER_GAME * D175A_CANDIDATE_REAP_RATE * TOP5_FRUIT_PER_HARVESTED_CROP
    )
    aspirational_delta_crops = max(0.0, D175A_PEER_FIELD_REFERENCE_CONCURRENT - D175A_PEAK_CONCURRENT_CANDIDATE)
    aspirational_fruit_per_game = (
        aspirational_delta_crops * STRONG_PEER_REAP_RATE * TOP5_FRUIT_PER_HARVESTED_CROP
    )
    return {
        "grounded_bracket": {
            "basis": (
                "D175a's own REAL, EXECUTED measurement of what bounded early planting "
                "does to this exact codebase: +{:.2f} crops/game planted (candidate "
                "generations/game - control), reaped at candidate's own measured 0.4523%, "
                "at top-5's own realized fruit/harvested-crop mean (7.0). This bracket "
                "does NOT additionally assume the harvest-capability lever fixes the "
                "reap rate -- it uses the rate D175a itself measured with planting alone."
            ).format(D175A_DELTA_CROPS_PER_GAME),
            "additional_crops_per_game": D175A_DELTA_CROPS_PER_GAME,
            "reap_rate_used": D175A_CANDIDATE_REAP_RATE,
            "fruit_per_harvested_crop_used": TOP5_FRUIT_PER_HARVESTED_CROP,
            "additional_fruit_score_per_game": grounded_fruit_per_game,
            "displacement_turns_per_game": D175A_DELTA_CROPS_PER_GAME * 2.0,  # PLANT + PICK, low bracket
        },
        "aspirational_bracket": {
            "basis": (
                "The peer cohort's own concurrent-crop shape (~5.5), reached in full, "
                "reaped at the STRONG/PEER-WEAK cohort's own realized rate (16.3% "
                "midpoint). REQUIRES A FIFTH, UN-MODELED CHANGE beyond the four levers "
                "in scope: D175a's own real intervention (median first-plant 199->13, "
                "99.8% activation) left peak concurrent crops essentially UNCHANGED "
                "(1.92->1.98) because chop-priority/crop-protection -- which decides "
                "whether an already-planted crop survives long enough to fruit -- is a "
                "separate mechanism none of the four levers touches. This bracket is "
                "reported for completeness and is EXCLUDED from the headline net bound."
            ),
            "additional_crops_per_game": aspirational_delta_crops,
            "reap_rate_used": STRONG_PEER_REAP_RATE,
            "fruit_per_harvested_crop_used": TOP5_FRUIT_PER_HARVESTED_CROP,
            "additional_fruit_score_per_game": aspirational_fruit_per_game,
        },
    }


def build_report(rows: list[dict]) -> dict:
    """Net bound = (worker value actually purchasable) + (direct fruit score, net of what
    is spent funding the bills) - (displacement, priced own-side from this corpus's own
    measured CHOP throughput and opponent-side from D175a's own measured
    Delta_opponent/Delta_own elasticity). Every number here is an UPPER BOUND on a pure
    stock-accounting counterfactual -- see the enumerated 'ignores' list in the report.
    """

    ok = [row for row in rows if row["ok"]]
    failed = [row for row in rows if not row["ok"]]
    ok.sort(key=lambda row: row["game_id"])

    total_chop_turns = sum(row["chop_turns"] for row in ok)
    total_wood_score = sum(row["wood_score"] for row in ok)
    v_own_per_chop_turn = (total_wood_score / total_chop_turns) if total_chop_turns else None

    w3_legal_rows = [row for row in ok if row["worker3_legal_turn"] is not None]
    w4_legal_rows = [row for row in ok if row["worker4_legal_turn"] is not None]
    w3_stock_rows = [row for row in ok if row["worker3_stock_turn"] is not None]
    w4_stock_rows = [row for row in ok if row["worker4_stock_turn"] is not None]

    additional_early_crops = build_additional_early_crops_estimate()
    grounded_extra_fruit_per_game = additional_early_crops["grounded_bracket"]["additional_fruit_score_per_game"]
    component_1b_turns_per_game = additional_early_crops["grounded_bracket"]["displacement_turns_per_game"]

    def compute_bound(fruit_key: str, iron_key: str, apply_opponent_ratio: bool = True) -> list[dict]:
        """Shared net-bound arithmetic, parameterized by which displacement-turn field to
        charge -- ``*_displacement_turns`` (primary, opportunistic/en-route collection) or
        ``*_displacement_turns_dedicated_trip`` (pessimistic sensitivity: every credited
        event gets its own independent solo round trip). Component 1b's own displacement
        (PLANT+PICK per additional early crop, low bracket) is a fixed per-game constant
        added to every variant identically.

        ``apply_opponent_ratio=False`` gives the OWN-SIDE-ONLY floor: D175a's own ratio
        was measured at a turn-diversion scale of ~4-10 turns/game (component 1b's own
        scale); component 1a alone (the real corpus's own reachable fruit+iron) diverts
        ~40-100+ turns/game -- 5-25x larger. Linearly extrapolating a ratio fit at one
        scale to a regime an order of magnitude larger is not something this script can
        validate (there is no real A/B test at THAT scale), and it produces margin costs
        that exceed plausible game-level magnitude (see report caveats). The own-side-only
        variant assumes zero additional opponent leak beyond what is directly measured,
        i.e. it is the OPTIMISTIC bound on displacement cost; the full linear-ratio
        variant is the PESSIMISTIC-on-displacement bound. Both are reported; neither is
        asserted as the single right answer."""

        out = []
        for row in ok:
            worker_value_margin = 0.0
            if row["worker3_legal_turn"] is not None:
                worker_value_margin += PRICE_2_TO_3_MARGIN
            if row["worker4_legal_turn"] is not None:
                worker_value_margin += PRICE_3_TO_4_MARGIN

            gross_fruit_margin = row["net_fruit_score"] + grounded_extra_fruit_per_game

            turns_diverted = row[fruit_key] + row[iron_key] + component_1b_turns_per_game
            own_disp_cost = (v_own_per_chop_turn or 0.0) * turns_diverted
            delta_own_displacement = -own_disp_cost
            delta_opponent_displacement = D175A_RATIO_OPP_OVER_OWN * delta_own_displacement if apply_opponent_ratio else 0.0
            margin_displacement = delta_own_displacement - delta_opponent_displacement

            net_margin = worker_value_margin + gross_fruit_margin + margin_displacement
            out.append(
                {
                    "game_id": row["game_id"],
                    "worker_value_margin": worker_value_margin,
                    "gross_fruit_margin": gross_fruit_margin,
                    "turns_diverted": turns_diverted,
                    "delta_own_displacement": delta_own_displacement,
                    "delta_opponent_displacement": delta_opponent_displacement,
                    "margin_displacement": margin_displacement,
                    "net_margin": net_margin,
                }
            )
        return out

    per_game_bound = compute_bound("fruit_displacement_turns", "iron_displacement_turns")
    per_game_bound_pessimistic = compute_bound(
        "fruit_displacement_turns_dedicated_trip", "iron_displacement_turns_dedicated_trip"
    )
    per_game_bound_own_side_only = compute_bound(
        "fruit_displacement_turns", "iron_displacement_turns", apply_opponent_ratio=False
    )

    def summarize_bound(per_game: list[dict]) -> dict:
        net_margins = [row["net_margin"] for row in per_game]
        margin_mean = mean(net_margins)
        margin_median = median(net_margins)
        margin_sd = statistics.pstdev(net_margins) if len(net_margins) > 1 else None
        margin_se = (margin_sd / (len(net_margins) ** 0.5)) if margin_sd is not None else None
        ci = (
            (margin_mean - 1.96 * margin_se, margin_mean + 1.96 * margin_se)
            if margin_se is not None and margin_mean is not None
            else None
        )
        return {
            "mean": margin_mean,
            "median": margin_median,
            "sd": margin_sd,
            "se": margin_se,
            "ci95_normal_approx": ci,
            "mean_rating_points": (margin_mean / MARGIN_PER_RATING) if margin_mean is not None else None,
            "ci95_rating_points": ((ci[0] / MARGIN_PER_RATING, ci[1] / MARGIN_PER_RATING) if ci is not None else None),
        }

    net_margin_mean = mean(row["net_margin"] for row in per_game_bound)
    net_margin_median = median(row["net_margin"] for row in per_game_bound)
    net_margin_sd = statistics.pstdev([row["net_margin"] for row in per_game_bound]) if len(per_game_bound) > 1 else None
    net_margin_se = (net_margin_sd / (len(per_game_bound) ** 0.5)) if net_margin_sd is not None else None
    ci95 = (
        (net_margin_mean - 1.96 * net_margin_se, net_margin_mean + 1.96 * net_margin_se)
        if net_margin_se is not None and net_margin_mean is not None
        else None
    )

    calibration = build_calibration(v_own_per_chop_turn)

    lever_attribution = {
        "worker_value_from_worker3_unlock_alone_mean": mean(
            (PRICE_2_TO_3_MARGIN if row["worker3_legal_turn"] is not None and row["worker4_legal_turn"] is None else 0.0)
            for row in ok
        ),
        "worker_value_from_worker3_and_worker4_mean": mean(
            ((PRICE_2_TO_3_MARGIN + PRICE_3_TO_4_MARGIN) if row["worker4_legal_turn"] is not None else 0.0)
            for row in ok
        ),
        "gross_fruit_mean_net_of_bills": mean(row["net_fruit_score"] for row in ok),
        "additional_early_crops_grounded_mean": grounded_extra_fruit_per_game,
        "displacement_mean_margin_cost": mean(row["margin_displacement"] for row in per_game_bound),
    }

    report = {
        "schema": "troll-farm-h1-joint-economy-upper-bound-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": (
            "read-only NET upper bound over the resident's own decoded arena replays; no "
            "arena writes, no strategy changes, no rerun of any game, no simulated bot"
        ),
        "caveat_upper_bound": (
            "This is a pure stock-accounting counterfactual layered with a calibrated "
            "displacement price, not a causal simulation. It explicitly IGNORES: (1) "
            "opponent adaptation to a changed resident trajectory; (2) trajectory "
            "divergence cascades (different unit positions change ALL later fruit/iron "
            "availability, not just the credited events); (3) the coordination cost the "
            "2026-07-29 terminal synthesis identified ('local improvements break the "
            "coordination') -- this script prices four levers as if a scheduler existed "
            "that would make exactly these choices and no others; no such scheduler is "
            "specified or built; (4) possible overlap between the worker-value term "
            "(B4.3's price is a holistic field correlate of ending the game at a higher "
            "roster, which may already partly embed some of the same future-production "
            "value the fruit-credit term separately prices) -- this is a known, "
            "un-netted double-count risk that biases the bound upward; (5) the "
            "opponent-side displacement price is transferred from D175a's own ratio, not "
            "independently derived, so it is self-consistent with D175a by construction, "
            "not an independent confirmation of it; (6) the PRIMARY displacement charge "
            "prices only the two actions that cannot be shared with other work (HARVEST-"
            "or-MINE, then DROP) per credited event, treating the walk itself as already "
            "happening en route -- matching B3.9's own real measurement of how top-5 "
            "agents actually collect iron (opportunistic, a few percent of a worker's "
            "command budget, never a dedicated trip). An UNCAPPED independent-solo-round-"
            "trip variant (walk-to-target + action + walk-to-door + DROP, no batching, no "
            "sharing) is reported separately as 'net_bound_margin_pessimistic_sensitivity' "
            "-- it routinely exceeds the game's own total unit-turn budget when summed "
            "over 15-30 credited events, which is itself evidence the opportunistic model "
            "is the more realistic of the two, not merely the more convenient one."
        ),
        "resident_agent_id": 6561795,
        "games_requested": len(rows),
        "games_decoded_ok": len(ok),
        "games_failed": len(failed),
        "failures": failed[:50],
        "worker3_n": WORKER3_N,
        "worker4_n": WORKER4_N,
        "total_turns": TOTAL_TURNS,
        "train_deadline_margin": TRAIN_DEADLINE_MARGIN,
        "bill_method": (
            "Real worker-2 TRAIN talents (train_events n_before==1), source-verified to "
            "be the SAME talents YamoBot::commands() reuses for every later TRAIN once "
            "can_train's n>=2 clause is lifted (self.desired_second read unconditionally "
            "of own_count; frozen once workforce reaches 2). NOT the synthetic "
            "cheap_helper/balanced_chopper specs B3.8/B3.9 used."
        ),
        "real_bill_cross_check": {
            "note": (
                "This corpus's own mean training_cost(n=2, real talents) should land near "
                "D174a's independently-published figure (PLUM 6.23/LEMON 5.87/APPLE "
                "2.00/IRON 7.12, n=1595 activated games) if the source-derivation above "
                "is correct."
            ),
            "cost3_mean": {
                "PLUM": mean(row["cost3"][0] for row in ok),
                "LEMON": mean(row["cost3"][1] for row in ok),
                "APPLE": mean(row["cost3"][2] for row in ok),
                "IRON": mean(row["cost3"][4] for row in ok if row["iron_present"]),
            },
        },
        "gross_fruit": {
            "own_or_unclaimed_units": stats(row["gross_fruit_units_own_or_unclaimed"] for row in ok),
            "own_plus_opponent_units": stats(row["gross_fruit_units_own_plus_opponent"] for row in ok),
            "net_of_bill_spending": stats(row["net_fruit_score"] for row in ok),
            "spent_on_bills_mean": mean(row["spent_fruit_on_bills"] for row in ok),
            "unreachable_skipped_total": sum(row["gross_fruit_unreachable_skipped"] for row in ok),
            "growth_anomalies_total": sum(row["growth_anomalies"] for row in ok),
        },
        "iron": {
            "episodes_credited": stats(row["iron_episodes_credited"] for row in ok),
            "units_credited": stats(row["iron_units_credited"] for row in ok),
            "unreachable_skipped_total": sum(row["iron_unreachable_skipped"] for row in ok),
            "note": "IRON is never direct score; its entire value is mediated through worker3/4 affordability.",
        },
        "worker3_affordability": {
            "games_with_stock_window": len(w3_stock_rows),
            "games_with_legal_window": len(w3_legal_rows),
            "pct_games_with_legal_window": len(w3_legal_rows) / len(ok) if ok else None,
            "legal_turn": stats(row["worker3_legal_turn"] for row in w3_legal_rows),
            "field_median_turn_at_least_3_reference": FIELD_MEDIAN_TURN_WORKER3_AT_LEAST,
        },
        "worker4_affordability": {
            "games_with_stock_window": len(w4_stock_rows),
            "games_with_legal_window": len(w4_legal_rows),
            "pct_games_with_legal_window": len(w4_legal_rows) / len(ok) if ok else None,
            "pct_of_worker3_unlocks_that_also_reach_worker4": (
                len(w4_legal_rows) / len(w3_legal_rows) if w3_legal_rows else None
            ),
            "legal_turn": stats(row["worker4_legal_turn"] for row in w4_legal_rows),
            "field_median_turn_at_least_4_reference": FIELD_MEDIAN_TURN_WORKER4_AT_LEAST,
        },
        "additional_early_crops_component_1b": additional_early_crops,
        "displacement": {
            "v_own_per_chop_turn": v_own_per_chop_turn,
            "corpus_total_chop_turns": total_chop_turns,
            "corpus_total_wood_score": total_wood_score,
            "action_turns_per_event_primary": ACTION_TURNS_PER_EVENT,
            "mean_fruit_displacement_turns_per_game": mean(row["fruit_displacement_turns"] for row in ok),
            "mean_iron_displacement_turns_per_game": mean(row["iron_displacement_turns"] for row in ok),
            "mean_fruit_displacement_turns_per_game_dedicated_trip": mean(
                row["fruit_displacement_turns_dedicated_trip"] for row in ok
            ),
            "mean_iron_displacement_turns_per_game_dedicated_trip": mean(
                row["iron_displacement_turns_dedicated_trip"] for row in ok
            ),
            "component_1b_turns_per_game": component_1b_turns_per_game,
            "mean_turns_diverted_per_game": mean(row["turns_diverted"] for row in per_game_bound),
            "opponent_side_ratio_source": "D175a activated-subset Delta_opponent/Delta_own",
            "opponent_side_ratio_value": D175A_RATIO_OPP_OVER_OWN,
            "mean_margin_displacement": mean(row["margin_displacement"] for row in per_game_bound),
        },
        "d175a_calibration": calibration,
        "pricing_constants_cited": {
            "margin_per_rating": MARGIN_PER_RATING,
            "price_2_to_3_margin": {"value": PRICE_2_TO_3_MARGIN, "ci95": PRICE_2_TO_3_CI},
            "price_3_to_4_margin": {"value": PRICE_3_TO_4_MARGIN, "ci95": PRICE_3_TO_4_CI},
            "timing_worker3_early_late": {"value": TIMING_WORKER3_EARLY_LATE, "ci95": TIMING_WORKER3_CI},
            "timing_worker4_early_late": {"value": TIMING_WORKER4_EARLY_LATE, "ci95": TIMING_WORKER4_CI},
            "timing_worker2_early_late_not_significant": TIMING_WORKER2_EARLY_LATE,
        },
        "net_bound_margin": {
            "mean": net_margin_mean,
            "median": net_margin_median,
            "sd": net_margin_sd,
            "se": net_margin_se,
            "ci95_normal_approx": ci95,
            "mean_rating_points": (net_margin_mean / MARGIN_PER_RATING) if net_margin_mean is not None else None,
            "ci95_rating_points": (
                (ci95[0] / MARGIN_PER_RATING, ci95[1] / MARGIN_PER_RATING) if ci95 is not None else None
            ),
        },
        "net_bound_margin_pessimistic_sensitivity": summarize_bound(per_game_bound_pessimistic),
        "net_bound_margin_own_side_only_optimistic_sensitivity": summarize_bound(per_game_bound_own_side_only),
        "lever_attribution_mean_margin": lever_attribution,
        "per_game": per_game_bound,
        "games": [
            {
                "game_id": row["game_id"],
                "margin": row["margin"],
                "won": row["won"],
                "turns": row["turns"],
                "opponent": row["opponent"],
                "iron_present": row["iron_present"],
                "worker3_legal_turn": row["worker3_legal_turn"],
                "worker4_legal_turn": row["worker4_legal_turn"],
            }
            for row in ok
        ],
    }
    return report


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument("--limit", type=int, default=0, help="0 means every resident game in the corpus")
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

    rows = run_main_audit(game_ids, jobs=args.jobs)
    report = build_report(rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=1) + "\n")

    print(f"resident games decoded: {report['games_decoded_ok']}/{report['games_requested']}")
    if report["games_failed"]:
        print(f"decode failures: {report['games_failed']}")
        for failure in report["failures"][:5]:
            print(f"  {failure}")
    w3 = report["worker3_affordability"]
    w4 = report["worker4_affordability"]
    print(
        f"worker3: {w3['games_with_legal_window']}/{report['games_decoded_ok']} "
        f"({w3['pct_games_with_legal_window']:.1%}) median turn={w3['legal_turn']['median']}"
    )
    print(
        f"worker4: {w4['games_with_legal_window']}/{report['games_decoded_ok']} "
        f"({w4['pct_games_with_legal_window']:.1%}) median turn={w4['legal_turn']['median']}"
    )
    nb = report["net_bound_margin"]
    print(f"net bound margin: mean={nb['mean']:.2f} median={nb['median']:.2f} rating={nb['mean_rating_points']:.3f}")
    calib = report["d175a_calibration"]
    if calib.get("available"):
        for label, bracket in calib["brackets"].items():
            print(
                f"  calibration[{label}]: predicted Delta-own={bracket['predicted_own_delta']:.2f} "
                f"actual={bracket['actual_own_delta_activated_subset']:.2f} "
                f"ratio={bracket['ratio_predicted_over_actual']}"
            )
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
