#!/usr/bin/env python3
"""A2 Phase 0a -- renewable resource base feasibility audit (kill rule K1).

Read-only corpus audit. Answers one question: does a genuinely self-sustaining fruit-tree
economy exist on these maps, or does the top cohort merely consume a larger/faster windfall
from the same finite starting population that H1 already showed cannot fund a 4th worker?
See ``coordination/tasks/20260730-a2-phase0a-renewable-base.md`` and
``docs/A2-programme-charter-2026-07-30.md`` (Phase 0a). Never touches the arena, never
edits corpus data, never proposes a strategy change.

Mechanics ground truth (read directly from ``rust/src/game/engine.rs``/``state.rs``,
cross-checked against ``docs/mechanics.md``, 2026-07-30):

- PLANT consumes exactly ONE fruit unit (PLUM/LEMON/APPLE/BANANA) from the planting
  unit's CARRY (``apply_plant``: ``u.carry[idx] -= 1``). There is no separate "seed" game
  object -- a fruit unit *is* a seed once carried. The carried unit got there either by
  harvesting it directly (still in carry) or by PICKing it back out of the player's own
  banked inventory (``apply_pick``). Either way, the ONLY source of PLUM/LEMON/APPLE/BANANA
  units in this game is HARVEST -- there is no other tap.
- TRAIN's bill (``training_cost(n, talents)``) charges PLUM/LEMON/APPLE unconditionally
  (``cost[i] = n + talent_i^2``) and IRON only when the map has iron terrain; BANANA and
  WOOD are never priced. ``n`` = the player's own unit count immediately before training,
  so worker 3 <=> ``n_before == 2`` and worker 4 <=> ``n_before == 3``. Units never die in
  this game (no removal path in the engine) -- the roster is monotonic non-decreasing, so
  "n_before" values are exact and unambiguous.
- A tree needs 4 growth ticks (no fruit produced) to reach size 4, and from then on
  produces one fruit every ``cooldown`` ticks (species base PLUM/LEMON 8, APPLE 9,
  BANANA 6 ticks; near-water discount PLUM/LEMON -5, APPLE -7, BANANA -2) FOREVER, capped
  at 3 concurrent fruits, until CHOPPED. Chopping is the only removal mechanic -- trees
  never die of age. So a mature, unchopped, harvested-when-full tree is a perpetual fruit
  generator, not a one-shot windfall. This reframes the whole feasibility question from
  "does the initial census run out" (H1's framing, which is correct for a *fixed* pool)
  to "does the population of self-planted mature trees net-grow against chop losses" --
  exactly what this script measures.

Reuse discipline (per the task brief -- does not re-derive replay parsing or crop-lineage
attribution):

- ``cgauto.recent_resident_field_census.decoded_states`` -- exact official per-turn state
  reconstruction (units/plants/``inventories[player] = [PLUM,LEMON,APPLE,BANANA,IRON,WOOD]``).
- ``cgauto.top_player_opening_analysis.{terrain,analyze_players}`` -- map geometry and
  worker-ordinal/training-event bookkeeping (exact realized bill per TRAIN, read from the
  revealed command -- the same method H1/H8 use, not a synthetic spec).
- ``cgauto.analyze_d101a_production_suppression.reconstruct_generation_actions`` -- the
  crop-lineage/ownership reconstruction (D101's 24.16%/0.94% reap-rate machinery): per-turn
  live-cell -> generation-id map, and a ``generations`` dict tagging each generation's
  ``origin`` (natural / actor / opponent / ambiguous / unknown), ``birth_turn``, ``kind``.
- ``cgauto.crop_fate_census.{load_games_index,top_agents,load_game}`` -- corpus/cohort
  access, same population conventions as B3.7's crop-fate census (its own headline numbers,
  29.81% top-5 owner-harvested vs the resident's ~0%, are cited directly rather than
  recomputed).

Mechanics correction found while building this script and load-bearing for the accounting
below: contrary to ``docs/statement.md`` (which documents the WOOD/tutorial league only,
where "the last two values are always 0"), real Legend-league games do NOT start at zero
bank. Verified directly against ``rust/src/game/official_mapgen.rs::generate_official``:
``for item in inventory.iter_mut().take(5) { *item = random.next_int(9) + 2 }`` draws each
of PLUM/LEMON/APPLE/BANANA/IRON independently and uniformly from ``[2, 10]`` per game (WOOD
stays 0), and gives the SAME vector to both players (``inventories: [inventory, inventory]``
-- symmetric, so it never favours one side). Confirmed empirically across sampled resident
AND top-5 games (both players' turn-0 inventories always identical, values varying game to
game, e.g. one resident game starts ``[7,10,4,3,4,0]``, a top-5 game ``[6,7,4,9,9,0]``).
This is a genuine SECOND one-time windfall, independent of the tree population H1 already
analysed -- so the fruit accounting below explicitly separates "S0" (starting bank, present
before turn 1, unrelated to any harvest) from "H" (fruit actually harvested from a tree),
and the reproduction ratio is computed from H alone (the tree-renewability-relevant flow);
S0 is reported alongside it so a reader can see when a game's PLANT activity was funded by
inherited capital rather than any harvest.

What this script adds beyond the above (the reason it exists as a new file): the
generational REPRODUCTION RATIO. Because fruit is a fungible integer count (not a
FIFO-tagged individual item), a literal single-fruit lineage trace is impossible once fruit
can be banked and PICKed back out later -- this is stated as an explicit limitation, not
glossed over. Instead this script computes a defensible POOLED aggregate: for a game,
``H`` = total fruit the tracked player ever harvested (any source); ``P`` = total fruit
units it ever spent on successful PLANT commands; ``B`` = total fruit spent on TRAIN bills;
``S`` = fruit still banked at game end; these close under ``H ~= B + P + S + carry_remainder``
(checked per game as an integrity residual). ``rho = P / H`` is the population-level
reinvestment rate; ``Y`` = mean fruit yield of one actor-planted tree over its life
(including zero-yield trees chopped before fruiting); ``R = rho * Y`` is the expected number
of NEW trees one tree's total lifetime fruit funds, i.e. the reproduction ratio: R >= 1 is a
renewable base (a producing tree replaces itself and then some before the game ends); R < 1
is depletion with extra steps. A 50-turn-epoch-binned ``rho`` and the raw population
time series (by origin) corroborate whether this holds up over multiple generations rather
than being a whole-game average that hides an early-only effect.

Usage::

    .venv/bin/python3 cgauto/renewable_base_feasibility.py rows --output <rows.jsonl> \\
        [--jobs 20] [--resident-limit 0] [--top5-per-agent 50] \\
        [--rank6-20-per-agent 20] [--rank6-20-count 15]
    .venv/bin/python3 cgauto/renewable_base_feasibility.py aggregate --rows <rows.jsonl> \\
        --output <report.json>
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
import json
import os
from pathlib import Path
import statistics
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np  # noqa: E402

from cgauto.analyze_d101a_production_suppression import reconstruct_generation_actions  # noqa: E402
from cgauto.crop_fate_census import load_game, load_games_index, top_agents  # noqa: E402
from cgauto.recent_resident_field_census import decoded_states  # noqa: E402
from cgauto.top_player_opening_analysis import analyze_players, terrain  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
RESIDENT_AGENT_ID = 6561795

ITEMS = ("PLUM", "LEMON", "APPLE", "BANANA", "IRON", "WOOD")
FRUIT_ITEMS = ITEMS[:4]
BILL_FRUIT_ITEMS = ITEMS[:3]  # PLUM/LEMON/APPLE -- the only bill-chargeable fruit legs
CHECKPOINTS = tuple(range(0, 301, 25))
EPOCH_WIDTH = 50
N_BOOT = 4000
BOOT_SEED = 20260730

# Source-verified (rust/src/game/engine.rs) -- see module docstring.
SPECIES_COOLDOWN = {"PLUM": 8, "LEMON": 8, "APPLE": 9, "BANANA": 6}
SPECIES_WATER_BONUS = {"PLUM": 5, "LEMON": 5, "APPLE": 7, "BANANA": 2}
GROWTH_STAGES = 4  # size 0 -> 4 (MAX_SIZE) before the first fruit; each stage = 1 cooldown


def fruit_units(values: dict) -> int:
    return sum(int(values.get(name, 0)) for name in FRUIT_ITEMS)


def bill_units(values: dict) -> int:
    return sum(int(values.get(name, 0)) for name in BILL_FRUIT_ITEMS)


def ratio(numerator, denominator):
    return numerator / denominator if denominator else None


def mean(values):
    selected = [v for v in values if v is not None]
    return statistics.mean(selected) if selected else None


def median(values):
    selected = [v for v in values if v is not None]
    return statistics.median(selected) if selected else None


def bootstrap_mean_ci(values, n_boot: int = N_BOOT, seed: int = BOOT_SEED) -> dict:
    arr = np.asarray([v for v in values if v is not None], dtype=float)
    if arr.size == 0:
        return {"mean": None, "ci_lo": None, "ci_hi": None, "n": 0}
    if arr.size == 1:
        return {"mean": float(arr[0]), "ci_lo": float(arr[0]), "ci_hi": float(arr[0]), "n": 1}
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, arr.size, size=(n_boot, arr.size))
    boots = arr[idx].mean(axis=1)
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return {"mean": float(arr.mean()), "ci_lo": float(lo), "ci_hi": float(hi), "n": int(arr.size)}


# ---------------------------------------------------------------------------
# Cohort / occurrence selection (extends crop_fate_census.select_occurrences with a
# rank-6-20 reference cohort for the matched "loop vs capable labour" comparison)
# ---------------------------------------------------------------------------


def select_occurrences(
    games_index: dict,
    resident_limit: int,
    top5_per_agent: int,
    rank6_20_per_agent: int,
    rank6_20_count: int,
) -> tuple[list[tuple], list[dict], list[dict]]:
    rows = []
    resident_game_ids = sorted(
        gid
        for gid, row in games_index.items()
        if any(int(p["agentId"]) == RESIDENT_AGENT_ID for p in row["players"])
    )
    if resident_limit:
        resident_game_ids = resident_game_ids[:resident_limit]
    for gid in resident_game_ids:
        player_row = next(
            p for p in games_index[gid]["players"] if int(p["agentId"]) == RESIDENT_AGENT_ID
        )
        rows.append((gid, RESIDENT_AGENT_ID, int(player_row["index"]), "resident", "resident"))

    ranked = top_agents(5 + rank6_20_count)
    top5 = ranked[:5]
    rest = ranked[5 : 5 + rank6_20_count]

    def add_cohort(agents: list[dict], per_agent: int, label: str) -> None:
        ids = {int(row["agentId"]): row["pseudo"] for row in agents}
        per_agent_ids: dict[int, list[int]] = defaultdict(list)
        for gid, row in games_index.items():
            for player in row["players"]:
                aid = int(player["agentId"])
                if aid in ids:
                    per_agent_ids[aid].append(gid)
        for aid, gids in per_agent_ids.items():
            gids.sort()
            selected = gids[:per_agent] if per_agent else gids
            for gid in selected:
                player_row = next(
                    p for p in games_index[gid]["players"] if int(p["agentId"]) == aid
                )
                rows.append((gid, aid, int(player_row["index"]), label, ids[aid]))

    add_cohort(top5, top5_per_agent, "top5")
    add_cohort(rest, rank6_20_per_agent, "rank6_20")

    rows.sort(key=lambda item: (item[3], item[4], item[0]))
    return rows, top5, rest


# ---------------------------------------------------------------------------
# Per-occurrence analysis
# ---------------------------------------------------------------------------


def analyze_occurrence(game_id: int, actor_id: int, seat: int, cohort: str, pseudo: str) -> dict:
    try:
        raw, trajectory = load_game(game_id)
        map_data, states, unknown = decoded_states(raw, trajectory)
        usable = min(len(states) - 1, len(trajectory))
        if unknown or usable != len(trajectory) or usable != len(states) - 1:
            return {
                "ok": False,
                "game_id": game_id,
                "agent_id": actor_id,
                "cohort": cohort,
                "error": (
                    f"decode mismatch: unknown={unknown} usable={usable} "
                    f"states={len(states)} trajectory={len(trajectory)}"
                ),
            }
        actor = seat
        opponent = 1 - actor
        scores = [float(v) for v in raw["scores"]]
        ranks = raw.get("ranks") or []
        margin = scores[actor] - scores[opponent]
        won = bool(ranks and len(ranks) == 2 and ranks[actor] == 0 and margin > 0)

        analyses = analyze_players(states, trajectory)
        own_ordinals = {
            int(w["unit_id"]): int(w["ordinal"]) for w in analyses[actor]["workers"]
        }
        events, generations, lineage_by_state, quality = reconstruct_generation_actions(
            states, trajectory, actor, own_ordinals
        )
        board = terrain(map_data)

        # --- census (turn 0) ---
        natural_plants = states[0]["plants"]
        initial_by_species = Counter(p["type"] for p in natural_plants)
        initial_inventory = states[0]["inventories"][actor]
        S0 = fruit_units({name: initial_inventory[i] for i, name in enumerate(ITEMS[:4])})
        iron0 = int(initial_inventory[4])

        # --- population time series (global: both players' plantings + surviving natural) ---
        population_series = []
        checkpoints = sorted(set(CHECKPOINTS) | {usable})
        for t in checkpoints:
            if t > usable:
                continue
            live = lineage_by_state[t]
            origin_counts = Counter(generations[gid]["origin"] for gid in live.values())
            species_counts = Counter(generations[gid]["kind"] for gid in live.values())
            plants_now = {(p["x"], p["y"]): p for p in states[t]["plants"]}
            fruiting = sum(1 for cell in live if plants_now.get(cell, {}).get("fruits", 0) > 0)
            population_series.append(
                {
                    "turn": t,
                    "total_live": len(live),
                    "by_origin": dict(origin_counts),
                    "by_species": dict(species_counts),
                    "fruiting_now": fruiting,
                }
            )

        # --- fruit flow accounting ---
        harvest_by_gen: dict[str, int] = defaultdict(int)
        H = 0
        H_by_species = Counter()
        iron_mined = 0
        for event in events:
            if not event["success"]:
                continue
            if event["verb"] == "HARVEST":
                units = fruit_units(event["gained"])
                H += units
                for name in FRUIT_ITEMS:
                    H_by_species[name] += event["gained"].get(name, 0)
                gid = event["target_generation"]
                if gid is not None:
                    harvest_by_gen[gid] += units
            elif event["verb"] == "MINE":
                iron_mined += event["gained"].get("IRON", 0)

        actor_gens = [gid for gid, g in generations.items() if g["origin"] == "actor"]
        trees_planted = len(actor_gens)
        yields = [harvest_by_gen.get(gid, 0) for gid in actor_gens]
        Y = statistics.mean(yields) if yields else None
        harvested_parent_trees = sum(1 for y in yields if y > 0)
        reap_rate = ratio(harvested_parent_trees, trees_planted)

        P_seeds = sum(
            fruit_units(event["spent"])
            for event in events
            if event["success"] and event["verb"] == "PLANT"
        )

        training_events = analyses[actor]["training_events"]
        B = sum(bill_units(ev["cost"]) for ev in training_events)

        final_inventory = states[usable]["inventories"][actor]
        S = fruit_units({name: final_inventory[i] for i, name in enumerate(ITEMS[:4])})
        final_units = [u for u in states[usable]["units"] if int(u["player"]) == actor]
        carry_remainder = sum(
            fruit_units({name: u["carry"][i] for i, name in enumerate(ITEMS[:4])})
            for u in final_units
        )
        # Closed-form identity: everything the player ever had (starting bank + harvested)
        # must equal everything it ever did with it (bills + planting + still banked/carried).
        accounting_residual = (S0 + H) - B - P_seeds - S - carry_remainder

        rho = ratio(P_seeds, H)
        R = rho * Y if (rho is not None and Y is not None) else None

        # --- epoch-binned reinvestment (does rho hold up over multiple generations?) ---
        epochs = []
        start = 1
        while start <= usable:
            end = min(start + EPOCH_WIDTH - 1, usable)
            harvested_epoch = sum(
                fruit_units(event["gained"])
                for event in events
                if event["success"]
                and event["verb"] == "HARVEST"
                and start <= event["turn"] <= end
            )
            planted_epoch = sum(
                fruit_units(event["spent"])
                for event in events
                if event["success"]
                and event["verb"] == "PLANT"
                and start <= event["turn"] <= end
            )
            epochs.append(
                {
                    "epoch_start": start,
                    "epoch_end": end,
                    "harvested_fruit": harvested_epoch,
                    "planted_seeds": planted_epoch,
                    "rho_epoch": ratio(planted_epoch, harvested_epoch),
                }
            )
            start += EPOCH_WIDTH

        # --- worker-3 / worker-4 currency trace ---
        def currency_trace(train_event):
            if train_event is None:
                return None
            turn = train_event["turn"]
            origin_fruit = Counter()
            origin_fruit["initial_endowment"] = S0  # available from before turn 1 (see module docstring)
            for event in events:
                if event["success"] and event["verb"] == "HARVEST" and event["turn"] < turn:
                    gid = event["target_generation"]
                    origin = generations[gid]["origin"] if gid is not None else "unattached"
                    origin_fruit[origin] += fruit_units(event["gained"])
            mined_before = sum(
                event["gained"].get("IRON", 0)
                for event in events
                if event["success"] and event["verb"] == "MINE" and event["turn"] < turn
            )
            total = sum(origin_fruit.values())
            return {
                "turn": turn,
                "talents": train_event["spec"],
                "cost": train_event["cost"],
                "n_before": train_event["n_before"],
                "cumulative_fruit_by_origin": dict(origin_fruit),
                "cumulative_fruit_total": total,
                "natural_share": ratio(origin_fruit.get("natural", 0), total),
                "self_planted_share": ratio(origin_fruit.get("actor", 0), total),
                "opponent_planted_share": ratio(origin_fruit.get("opponent", 0), total),
                "initial_endowment_share": ratio(origin_fruit.get("initial_endowment", 0), total),
                "cumulative_iron_mined": mined_before,
                "initial_iron_endowment": iron0,
            }

        worker3_event = next((e for e in training_events if e["n_before"] == 2), None)
        worker4_event = next((e for e in training_events if e["n_before"] == 3), None)
        worker3_trace = currency_trace(worker3_event)
        worker4_trace = currency_trace(worker4_event)
        final_workers = 1 + len(training_events)

        return {
            "ok": True,
            "game_id": game_id,
            "agent_id": actor_id,
            "cohort": cohort,
            "pseudo": pseudo,
            "seat": actor,
            "turns": usable,
            "margin": margin,
            "won": won,
            "final_workers": final_workers,
            "census": {
                "initial_tree_count": len(natural_plants),
                "initial_by_species": dict(initial_by_species),
                "walkable_count": len(board["walkable"]),
                "iron_source_count": len(board["iron"]),
                "water_count": len(board["water"]),
                "initial_bank_fruit": S0,
                "initial_bank_iron": iron0,
            },
            "population_series": population_series,
            "economy": {
                "H_total_fruit_harvested": H,
                "H_by_species": dict(H_by_species),
                "B_fruit_spent_on_bills": B,
                "P_seeds_spent_on_planting": P_seeds,
                "trees_planted": trees_planted,
                "S_final_bank_fruit": S,
                "carry_remainder_fruit": carry_remainder,
                "accounting_residual": accounting_residual,
                "iron_mined_total": iron_mined,
            },
            "reproduction": {
                "Y_mean_fruit_yield_per_planted_tree": Y,
                "rho_reinvestment_rate": rho,
                "R_reproduction_ratio": R,
                "harvested_parent_trees": harvested_parent_trees,
                "reap_rate_of_own_plantings": reap_rate,
                "yields": yields,
            },
            "epoch_reinvestment": epochs,
            "worker3_trace": worker3_trace,
            "worker4_trace": worker4_trace,
            "training_events_summary": [
                {
                    "ordinal": e["ordinal"],
                    "turn": e["turn"],
                    "n_before": e["n_before"],
                    "talents": e["spec"],
                    "cost": e["cost"],
                }
                for e in training_events
            ],
            "integrity": {
                "unknown_diff_updates": unknown,
                "unknown_births": quality.get("unknown_births", 0),
                "ambiguous_births": quality.get("ambiguous_births", 0),
                "missing_live_generations": quality.get("missing_live_generations", 0),
                "missing_worker_ordinals": quality.get("missing_worker_ordinals", 0),
            },
        }
    except Exception as exc:  # noqa: BLE001 -- one bad game shouldn't abort the sweep
        return {
            "ok": False,
            "game_id": game_id,
            "agent_id": actor_id,
            "cohort": cohort,
            "error": f"{type(exc).__name__}: {exc}",
        }


# ---------------------------------------------------------------------------
# CLI: rows (decode+compute, streamed to disk) / aggregate (cohort summaries)
# ---------------------------------------------------------------------------


def cmd_rows(args: argparse.Namespace) -> int:
    games_index = load_games_index()
    occurrences, top5, rest = select_occurrences(
        games_index,
        args.resident_limit,
        args.top5_per_agent,
        args.rank6_20_per_agent,
        args.rank6_20_count,
    )
    print(f"occurrences selected: {len(occurrences)}", file=sys.stderr)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    meta_path = args.output.with_suffix(".meta.json")
    meta_path.write_text(
        json.dumps(
            {
                "resident_agent_id": RESIDENT_AGENT_ID,
                "top5_agents": [
                    {"agent_id": int(r["agentId"]), "pseudo": r["pseudo"], "rank": r.get("rank")}
                    for r in top5
                ],
                "rank6_20_agents": [
                    {"agent_id": int(r["agentId"]), "pseudo": r["pseudo"], "rank": r.get("rank")}
                    for r in rest
                ],
                "resident_limit": args.resident_limit,
                "top5_per_agent": args.top5_per_agent,
                "rank6_20_per_agent": args.rank6_20_per_agent,
                "occurrences_requested": len(occurrences),
            },
            indent=1,
        )
        + "\n"
    )
    n_ok = 0
    n_fail = 0
    with args.output.open("w") as handle:
        if args.jobs <= 1:
            for row in occurrences:
                result = analyze_occurrence(*row)
                handle.write(json.dumps(result) + "\n")
                handle.flush()
                n_ok += result["ok"]
                n_fail += not result["ok"]
        else:
            with ProcessPoolExecutor(max_workers=args.jobs) as executor:
                for result in executor.map(
                    analyze_occurrence,
                    [r[0] for r in occurrences],
                    [r[1] for r in occurrences],
                    [r[2] for r in occurrences],
                    [r[3] for r in occurrences],
                    [r[4] for r in occurrences],
                    chunksize=4,
                ):
                    handle.write(json.dumps(result) + "\n")
                    handle.flush()
                    n_ok += result["ok"]
                    n_fail += not result["ok"]
    print(f"rows written: ok={n_ok} failed={n_fail} -> {args.output}", file=sys.stderr)
    return 0


def load_rows(path: Path) -> list[dict]:
    rows = []
    with path.open() as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def species_ceiling(rows: list[dict]) -> dict:
    """Analytical throughput ceiling grounded in the corpus's own actor-planted species
    mix (top5 cohort). Effective cooldown assumes near-water discount applies to the
    same fraction of planted trees the corpus shows sitting adjacent to water at census
    time (approximated conservatively as 0% water bonus -- a lower bound on throughput
    per tree, i.e. an upper bound on turns-per-fruit) unless a richer per-tree water
    join is added later. Reported as an explicit, labelled estimate, not a measurement.
    """

    # Use H_by_species (realized harvesting) as the revealed-preference proxy for which
    # species dominate this cohort's actual fruit stream (population_series' by_species
    # is not separable by origin without an added kind x origin cross-tab).
    species_counts = Counter()
    for row in rows:
        if not row["ok"]:
            continue
        for name, count in row["economy"].get("H_by_species", {}).items():
            species_counts[name] += count
    total = sum(species_counts.values())
    if not total:
        return {"note": "no fruit harvested in sample", "mean_cooldown_no_water": None}
    weighted_cooldown = sum(
        SPECIES_COOLDOWN[name] * count for name, count in species_counts.items()
    ) / total
    weighted_cooldown_water = sum(
        (SPECIES_COOLDOWN[name] - SPECIES_WATER_BONUS[name]) * count
        for name, count in species_counts.items()
    ) / total
    return {
        "species_mix_by_realized_harvest": dict(species_counts),
        "harvest_weighted_mean_cooldown_no_water": weighted_cooldown,
        "harvest_weighted_mean_cooldown_with_water": weighted_cooldown_water,
        "per_tree_fruit_per_turn_no_water": ratio(1, weighted_cooldown),
        "per_tree_fruit_per_turn_with_water": ratio(1, weighted_cooldown_water),
        "maturation_turns_no_water": weighted_cooldown * GROWTH_STAGES,
        "maturation_turns_with_water": weighted_cooldown_water * GROWTH_STAGES,
    }


def population_growth_summary(rows: list[dict]) -> dict:
    by_turn: dict[int, list[dict]] = defaultdict(list)
    for row in rows:
        if not row["ok"]:
            continue
        for sample in row["population_series"]:
            by_turn[sample["turn"]].append(sample)
    per_turn = {}
    for turn in sorted(by_turn):
        samples = by_turn[turn]
        totals = [s["total_live"] for s in samples]
        natural = [s["by_origin"].get("natural", 0) for s in samples]
        actor = [s["by_origin"].get("actor", 0) for s in samples]
        opponent = [s["by_origin"].get("opponent", 0) for s in samples]
        fruiting = [s["fruiting_now"] for s in samples]
        per_turn[str(turn)] = {
            "games_sampled": len(samples),
            "mean_total_live": mean(totals),
            "mean_natural_alive": mean(natural),
            "mean_actor_planted_alive": mean(actor),
            "mean_opponent_planted_alive": mean(opponent),
            "mean_fruiting_now": mean(fruiting),
        }
    initial = [row["census"]["initial_tree_count"] for row in rows if row["ok"]]
    # "at end" = each game's own last sampled checkpoint (usable turn), not a fixed turn
    end_totals = []
    end_actor = []
    for row in rows:
        if not row["ok"] or not row["population_series"]:
            continue
        last = row["population_series"][-1]
        end_totals.append(last["total_live"])
        end_actor.append(last["by_origin"].get("actor", 0))
    growth = [
        end - row["census"]["initial_tree_count"]
        for row, end in zip([r for r in rows if r["ok"] and r["population_series"]], end_totals)
    ]
    return {
        "mean_initial_tree_count": mean(initial),
        "mean_final_total_live": mean(end_totals),
        "mean_final_actor_planted_alive": mean(end_actor),
        "mean_net_population_change_end_minus_start": mean(growth),
        "frac_games_final_population_exceeds_initial": ratio(
            sum(1 for g in growth if g > 0), len(growth)
        ),
        "per_turn": per_turn,
    }


def pooled_bootstrap_reproduction(rows: list[dict], n_boot: int = N_BOOT, seed: int = BOOT_SEED) -> dict:
    """Game-level-clustered bootstrap of the POOLED (sum/sum) reproduction statistics.

    Per-game ratios (rho = P/H etc.) are dominated by outlier games with a tiny or zero
    harvested-fruit denominator (e.g. resident games that harvest nothing but still plant
    a few endowment-funded trees give rho in the hundreds) -- their arithmetic MEAN across
    games is not a meaningful population statistic (same reason you don't average batting
    averages). The pooled sum/sum ratio, resampled at the GAME level (the true independent
    sampling unit, preserving each game's internal (H, P, yields) structure together), is
    the correct aggregate. Reported alongside the per-game distribution, not instead of it.
    """

    H = np.array([row["economy"]["H_total_fruit_harvested"] for row in rows], dtype=float)
    P = np.array([row["economy"]["P_seeds_spent_on_planting"] for row in rows], dtype=float)
    trees = np.array([row["economy"]["trees_planted"] for row in rows], dtype=float)
    yield_sum = np.array([sum(row["reproduction"]["yields"]) for row in rows], dtype=float)
    harvested_parents = np.array(
        [row["reproduction"]["harvested_parent_trees"] for row in rows], dtype=float
    )
    n = len(rows)
    if n == 0:
        empty = {"point": None, "ci_lo": None, "ci_hi": None, "n": 0}
        return {"rho_pooled": empty, "Y_pooled": empty, "R_pooled": empty, "reap_pooled": empty}

    def point(H_, P_, trees_, yield_sum_, harvested_parents_):
        rho_p = P_.sum() / H_.sum() if H_.sum() > 0 else None
        Y_p = yield_sum_.sum() / trees_.sum() if trees_.sum() > 0 else None
        R_p = rho_p * Y_p if (rho_p is not None and Y_p is not None) else None
        reap_p = harvested_parents_.sum() / trees_.sum() if trees_.sum() > 0 else None
        return rho_p, Y_p, R_p, reap_p

    rho0, Y0, R0, reap0 = point(H, P, trees, yield_sum, harvested_parents)

    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(n_boot, n))
    rho_boot, Y_boot, R_boot, reap_boot = [], [], [], []
    for row_idx in idx:
        Hs, Ps, ts, ys, hp = H[row_idx], P[row_idx], trees[row_idx], yield_sum[row_idx], harvested_parents[row_idx]
        rho_p, Y_p, R_p, reap_p = point(Hs, Ps, ts, ys, hp)
        if rho_p is not None:
            rho_boot.append(rho_p)
        if Y_p is not None:
            Y_boot.append(Y_p)
        if R_p is not None:
            R_boot.append(R_p)
        if reap_p is not None:
            reap_boot.append(reap_p)

    def summarize(point_value, boot_values):
        if point_value is None or not boot_values:
            return {"point": point_value, "ci_lo": None, "ci_hi": None, "n": n}
        lo, hi = np.percentile(boot_values, [2.5, 97.5])
        return {"point": float(point_value), "ci_lo": float(lo), "ci_hi": float(hi), "n": n}

    return {
        "rho_pooled": summarize(rho0, rho_boot),
        "Y_pooled": summarize(Y0, Y_boot),
        "R_pooled": summarize(R0, R_boot),
        "reap_pooled": summarize(reap0, reap_boot),
    }


def reproduction_summary(rows: list[dict]) -> dict:
    ok_rows = [row for row in rows if row["ok"]]
    R_values = [row["reproduction"]["R_reproduction_ratio"] for row in ok_rows]
    rho_values = [row["reproduction"]["rho_reinvestment_rate"] for row in ok_rows]
    Y_values = [row["reproduction"]["Y_mean_fruit_yield_per_planted_tree"] for row in ok_rows]
    reap_values = [row["reproduction"]["reap_rate_of_own_plantings"] for row in ok_rows]
    trees_planted = [row["economy"]["trees_planted"] for row in ok_rows]
    H_values = [row["economy"]["H_total_fruit_harvested"] for row in ok_rows]
    B_values = [row["economy"]["B_fruit_spent_on_bills"] for row in ok_rows]
    S_values = [row["economy"]["S_final_bank_fruit"] for row in ok_rows]
    residuals = [row["economy"]["accounting_residual"] for row in ok_rows]

    epoch_index: dict[int, list[float]] = defaultdict(list)
    for row in ok_rows:
        for e in row["epoch_reinvestment"]:
            if e["rho_epoch"] is not None:
                epoch_index[e["epoch_start"]].append(e["rho_epoch"])
    epoch_trend = {
        str(start): {"mean_rho": mean(values), "n": len(values)}
        for start, values in sorted(epoch_index.items())
    }

    return {
        "games": len(ok_rows),
        "pooled": pooled_bootstrap_reproduction(ok_rows),
        "frac_games_zero_harvest": ratio(sum(1 for h in H_values if h == 0), len(H_values)),
        "R_reproduction_ratio_per_game_mean": bootstrap_mean_ci(R_values),
        "R_median": median(R_values),
        "R_frac_ge_1": ratio(sum(1 for r in R_values if r is not None and r >= 1), len(R_values)),
        "R_frac_defined": ratio(sum(1 for r in R_values if r is not None), len(R_values)),
        "rho_reinvestment_rate_per_game_mean": bootstrap_mean_ci(rho_values),
        "rho_median": median(rho_values),
        "Y_mean_fruit_yield_per_tree_per_game_mean": bootstrap_mean_ci(Y_values),
        "Y_median": median(Y_values),
        "reap_rate_of_own_plantings_per_game_mean": bootstrap_mean_ci(reap_values),
        "reap_median": median(reap_values),
        "mean_trees_planted_per_game": mean(trees_planted),
        "mean_H_fruit_harvested_per_game": mean(H_values),
        "median_H_fruit_harvested_per_game": median(H_values),
        "mean_B_spent_on_bills_per_game": mean(B_values),
        "mean_S_banked_at_end_per_game": mean(S_values),
        "mean_accounting_residual_per_game": mean(residuals),
        "max_abs_accounting_residual": max((abs(r) for r in residuals), default=None),
        "epoch_rho_trend": epoch_trend,
    }


def worker_funding_summary(rows: list[dict]) -> dict:
    ok_rows = [row for row in rows if row["ok"]]

    def summarize(trace_key: str) -> dict:
        traces = [row[trace_key] for row in ok_rows if row.get(trace_key) is not None]
        turns = [t["turn"] for t in traces]
        natural_share = [t["natural_share"] for t in traces if t["natural_share"] is not None]
        self_share = [t["self_planted_share"] for t in traces if t["self_planted_share"] is not None]
        opp_share = [
            t["opponent_planted_share"] for t in traces if t["opponent_planted_share"] is not None
        ]
        endowment_share = [
            t["initial_endowment_share"] for t in traces if t["initial_endowment_share"] is not None
        ]
        return {
            "games_reaching": len(traces),
            "games_total": len(ok_rows),
            "reach_rate": ratio(len(traces), len(ok_rows)),
            "earliest_turn": min(turns) if turns else None,
            "median_turn": median(turns),
            "mean_turn": mean(turns),
            "mean_natural_share_of_currency": mean(natural_share),
            "mean_self_planted_share_of_currency": mean(self_share),
            "mean_opponent_planted_share_of_currency": mean(opp_share),
            "mean_initial_endowment_share_of_currency": mean(endowment_share),
            "mean_cumulative_iron_mined": mean([t["cumulative_iron_mined"] for t in traces]),
        }

    return {"worker3": summarize("worker3_trace"), "worker4": summarize("worker4_trace")}


def census_summary(rows: list[dict]) -> dict:
    ok_rows = [row for row in rows if row["ok"]]
    initial_counts = [row["census"]["initial_tree_count"] for row in ok_rows]
    walkable = [row["census"]["walkable_count"] for row in ok_rows]
    iron_sources = [row["census"]["iron_source_count"] for row in ok_rows]
    initial_bank_fruit = [row["census"]["initial_bank_fruit"] for row in ok_rows]
    initial_bank_iron = [row["census"]["initial_bank_iron"] for row in ok_rows]
    species_totals = Counter()
    for row in ok_rows:
        for name, count in row["census"]["initial_by_species"].items():
            species_totals[name] += count
    distinct_maps = {
        (row["census"]["walkable_count"], row["census"]["iron_source_count"], row["census"]["water_count"])
        for row in ok_rows
    }
    return {
        "games": len(ok_rows),
        "mean_initial_tree_count": mean(initial_counts),
        "median_initial_tree_count": median(initial_counts),
        "mean_walkable_cells": mean(walkable),
        "mean_iron_sources": mean(iron_sources),
        "mean_initial_bank_fruit": mean(initial_bank_fruit),
        "mean_initial_bank_iron": mean(initial_bank_iron),
        "initial_species_totals": dict(species_totals),
        "distinct_walkable_iron_water_signatures": len(distinct_maps),
    }


def cohort_report(rows: list[dict]) -> dict:
    return {
        "games_requested": len(rows),
        "games_ok": sum(1 for r in rows if r["ok"]),
        "games_failed": sum(1 for r in rows if not r["ok"]),
        "failures": [r for r in rows if not r["ok"]][:20],
        "census": census_summary(rows),
        "population_growth": population_growth_summary(rows),
        "reproduction": reproduction_summary(rows),
        "worker_funding": worker_funding_summary(rows),
        "throughput_ceiling": species_ceiling(rows),
        "mean_final_workers": mean([r["final_workers"] for r in rows if r["ok"]]),
        "mean_margin": mean([r["margin"] for r in rows if r["ok"]]),
        "win_rate": ratio(sum(1 for r in rows if r["ok"] and r["won"]), sum(1 for r in rows if r["ok"])),
    }


def cmd_aggregate(args: argparse.Namespace) -> int:
    rows = load_rows(args.rows)
    by_cohort: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_cohort[row["cohort"]].append(row)

    report = {
        "schema": 1,
        "scope": "read-only A2 Phase 0a renewable-base feasibility audit; no arena writes",
        "rows_path": str(args.rows),
        "cohorts": {name: cohort_report(cohort_rows) for name, cohort_rows in by_cohort.items()},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=1) + "\n")
    print(f"saved {args.output}")
    for name, cohort in report["cohorts"].items():
        rep = cohort["reproduction"]
        pooled = rep["pooled"]
        print(
            f"{name}: games_ok={cohort['games_ok']} "
            f"R_pooled={pooled['R_pooled']['point']} "
            f"rho_pooled={pooled['rho_pooled']['point']} "
            f"Y_pooled={pooled['Y_pooled']['point']} "
            f"reap_pooled={pooled['reap_pooled']['point']} "
            f"frac_zero_H={rep['frac_games_zero_harvest']}"
        )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(dest="stage", required=True)

    rows_parser = subparsers.add_parser("rows", help="decode occurrences and stream per-game rows to disk")
    rows_parser.add_argument("--output", type=Path, required=True)
    rows_parser.add_argument("--resident-limit", type=int, default=0, help="0 = every resident game")
    rows_parser.add_argument("--top5-per-agent", type=int, default=50)
    rows_parser.add_argument("--rank6-20-per-agent", type=int, default=20)
    rows_parser.add_argument("--rank6-20-count", type=int, default=15)
    rows_parser.add_argument("--jobs", type=int, default=min(20, os.cpu_count() or 1))
    rows_parser.set_defaults(func=cmd_rows)

    agg_parser = subparsers.add_parser("aggregate", help="aggregate rows into a cohort report")
    agg_parser.add_argument("--rows", type=Path, required=True)
    agg_parser.add_argument("--output", type=Path, required=True)
    agg_parser.set_defaults(func=cmd_aggregate)

    args = parser.parse_args()
    if args.stage == "rows" and args.jobs < 1:
        parser.error("--jobs must be positive")
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
