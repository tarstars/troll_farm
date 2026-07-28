#!/usr/bin/env python3
"""B4.4 -- two-worker peer-cohort analysis (read-only research scout).

Read-only diagnostic: no arena writes, no corpus mutation, no strategy changes. It
answers B4.3's residual question -- 25 Legend agents finish with the resident's exact
~2.00-worker final roster yet rank 7-104 (12 of them *above* the resident, at rank 43)
-- what do the strong two-worker agents do differently, with no scaling advantage at
all available to explain the gap?

Reuse, not a new parser (per the B4.4 brief):

- ``cgauto.roster_outcome_pricing`` -- corpus/leaderboard loading, ``is_clean``,
  ``roster_of``/``margin_of``/``won_of``, and every bootstrap/CI stats helper.  The
  cohort-selection band (Legend, final roster within 0.2 of the resident's own mean,
  >=10 games) is *the same rule* that B4.3's ``same_scale_peers`` used to find the "25
  agents" this task starts from -- recomputed fresh here (not read back from B4.3's
  report, which only persisted the first 15 of the 25 sorted by rank).
- ``cgauto.analyze_d101a_production_suppression.analyze_occurrence``/``summarize_rows``
  -- the exact generation-lineage reap-rate/suppression attribution D101 used to get
  "resident 0.94%, top-3 24.16%"; called here with this script's own cohort instead of
  D101's frozen top-20 selection, so the two numbers are directly comparable.
- ``cgauto.recent_resident_field_census.successful_events`` -- referee-confirmed
  per-turn event stream (TRAIN/PLANT/HARVEST/CHOP/DROP), reused for tempo (first
  plant/harvest/train/bank turn).
- ``cgauto.replay_conformance.action_commands`` -- turn-string -> command-list parsing,
  reused for the opening-window verb histogram and first-train-spec extraction.
- ``cgauto.top_player_macro_census.role_of`` -- the project's standing talent-vector ->
  role label (wood_specialist/hybrid_chopper/harvest_specialist/carrier/generalist).

Score composition, production counts (plants/game, harvested fruit units/game, wood/iron
collected/game), score-curve trajectory shape, and head-to-head roster-bucketed win rates
are all read directly out of ``data/processed/games.jsonl``'s existing per-player fields
(``final_inv``, ``planted_ok``, ``harvested``, ``effects``, ``score_curve``, ``trains``) --
no replay decode needed for those parts at all.

CLI usage::

    .venv/bin/python cgauto/peer_cohort_analysis.py --output <path/to/report.json> [--jobs 16]
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import statistics
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.roster_outcome_pricing import (  # noqa: E402
    RESIDENT_AGENT_ID,
    bootstrap_mean_ci,
    is_clean,
    latest_leaderboard_path,
    load_games,
    load_leaderboard,
    margin_of,
    mean_sd_n,
    roster_of,
    win_rate_ci,
    won_of,
)
from cgauto.analyze_d61p_field_snapshot import read_jsonl  # noqa: E402
from cgauto.analyze_d101a_production_suppression import (  # noqa: E402
    analyze_occurrence,
    summarize_rows,
)
from cgauto.recent_resident_field_census import successful_events  # noqa: E402
from cgauto.replay_conformance import action_commands  # noqa: E402
from cgauto.top_player_macro_census import role_of, spec_label  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
RAW_GAMES = REPO / "data/raw/games"
TRAJECTORIES = REPO / "data/processed/trajectories"
SCRATCH_DIR = Path(
    "/tmp/claude-1001/-home-tarstars-prj-troll-farm/b87b2a84-2e59-408b-9c9e-ecb58289a6d1/scratchpad"
)
DEFAULT_OUTPUT = SCRATCH_DIR / "b44-peer-cohort-data.json"

# ---------------------------------------------------------------------------
# Tunables -- module constants, not results.
# ---------------------------------------------------------------------------
MIN_GAMES_FOR_COHORT = 10  # matches B4.3's same_scale_peers floor
ROSTER_BAND_HALFWIDTH = 0.2  # matches B4.3's same_scale_peers band
OPENING_WINDOW_TURNS = 20  # brief: "first ~20 commands"
SCORE_CURVE_CUTS = (50, 100, 150, 200, 250, 300)  # fixed cuts baked into games.jsonl
FRUIT_ITEMS = ("PLUM", "LEMON", "APPLE", "BANANA")
DEFAULT_JOBS = 16


# ---------------------------------------------------------------------------
# Part 0: cohort selection
# ---------------------------------------------------------------------------


def per_agent_rosters(clean_games: list[dict]) -> dict[int, list[int]]:
    rosters: dict[int, list[int]] = defaultdict(list)
    for game in clean_games:
        for player in game["players"]:
            rosters[player["agentId"]].append(roster_of(game, player["index"]))
    return rosters


def build_cohort(clean_games: list[dict], leaderboard: dict[int, dict]) -> dict:
    rosters = per_agent_rosters(clean_games)
    resident_rosters = rosters[RESIDENT_AGENT_ID]
    resident_mean = statistics.mean(resident_rosters)
    resident_rank = leaderboard[RESIDENT_AGENT_ID]["rank"]

    def agent_row(agent_id: int, own_rosters: list[int]) -> dict:
        info = leaderboard[agent_id]
        return {
            "agent_id": agent_id,
            "pseudo": info["pseudo"],
            "rank": info["rank"],
            "score": info["score"],
            "n_games": len(own_rosters),
            "mean_roster": statistics.mean(own_rosters),
            "median_roster": statistics.median(own_rosters),
            "pct_games_at_roster_2": sum(r == 2 for r in own_rosters) / len(own_rosters),
            "roster_histogram": dict(sorted(Counter(own_rosters).items())),
        }

    primary_rows = []
    for agent_id, own_rosters in rosters.items():
        if agent_id == RESIDENT_AGENT_ID or agent_id not in leaderboard:
            continue
        info = leaderboard[agent_id]
        if info["division_index"] != 5:
            continue
        if len(own_rosters) < MIN_GAMES_FOR_COHORT:
            continue
        if abs(statistics.mean(own_rosters) - resident_mean) > ROSTER_BAND_HALFWIDTH:
            continue
        primary_rows.append(agent_row(agent_id, own_rosters))
    primary_rows.sort(key=lambda row: row["rank"])

    strong = [row for row in primary_rows if row["rank"] < resident_rank]
    peer_weak = [row for row in primary_rows if row["rank"] >= resident_rank]

    # Sensitivity check: the brief's alternative literal rule (median exactly 2,
    # min-games floor only, no mean-band restriction).  Reported, not used as primary,
    # because it admits agents whose mean roster is well above 2 (e.g. 2.9) -- median
    # 2 only because a bare majority of their games happen to stop there -- which is
    # not really "a two-worker architecture" in the sense B4.3's finding was about.
    median_rule_rows = []
    for agent_id, own_rosters in rosters.items():
        if agent_id == RESIDENT_AGENT_ID or agent_id not in leaderboard:
            continue
        info = leaderboard[agent_id]
        if info["division_index"] != 5 or len(own_rosters) < MIN_GAMES_FOR_COHORT:
            continue
        if statistics.median(own_rosters) != 2:
            continue
        median_rule_rows.append(agent_row(agent_id, own_rosters))
    median_rule_rows.sort(key=lambda row: row["rank"])

    return {
        "resident": {
            "agent_id": RESIDENT_AGENT_ID,
            "rank": resident_rank,
            "score": leaderboard[RESIDENT_AGENT_ID]["score"],
            "n_games": len(resident_rosters),
            "mean_roster": resident_mean,
            "median_roster": statistics.median(resident_rosters),
        },
        "inclusion_rule": {
            "division": "Legend (divisionIndex==5)",
            "min_games": MIN_GAMES_FOR_COHORT,
            "rule": f"mean final roster within {ROSTER_BAND_HALFWIDTH} of the resident's own mean ({resident_mean:.3f})",
        },
        "strong": strong,
        "peer_weak": peer_weak,
        "n_strong": len(strong),
        "n_peer_weak": len(peer_weak),
        "n_total": len(primary_rows),
        "sensitivity_median_rule": {
            "rule": "median final roster == 2, min games, no mean-band restriction",
            "n_total": len(median_rule_rows),
            "n_with_mean_roster_over_2_5": sum(1 for row in median_rule_rows if row["mean_roster"] > 2.5),
            "rows": median_rule_rows,
        },
    }


# ---------------------------------------------------------------------------
# Part 1+2+5: score composition, production, score-curve trajectory shape
# (all read directly out of games.jsonl -- no decode needed)
# ---------------------------------------------------------------------------


def index_agent_occurrences(clean_games: list[dict], agent_ids: set[int]) -> dict[int, list[tuple[dict, int]]]:
    index: dict[int, list[tuple[dict, int]]] = defaultdict(list)
    for game in clean_games:
        for player in game["players"]:
            if player["agentId"] in agent_ids:
                index[player["agentId"]].append((game, player["index"]))
    return index


def harvested_fruit_units(harvested: dict) -> int:
    """Sum a games.jsonl ``harvested`` dict across singular/plural keys.

    The referee's summary text is ``"harvested 1 PLUM"`` for a single fruit but
    ``"harvested 2 PLUMs"`` (plural) for a multi-fruit harvest -- confirmed against raw
    replay summary lines -- so ``data/scripts/parse.py``'s regex stores them as two
    distinct dict keys per fruit type; both must be added to get the true total.
    """

    total = 0
    for name in FRUIT_ITEMS:
        total += harvested.get(name, 0) + harvested.get(name + "s", 0)
    return total


def score_production_stats(pairs: list[tuple[dict, int]]) -> dict:
    fruit_pts, wood_pts, total_pts, wood_share = [], [], [], []
    plants_per_game, harvested_per_game, chops_landed_per_game = [], [], []
    wood_collected_per_game, iron_collected_per_game = [], []
    trains_issued_per_game, trains_succeeded_per_game = [], []
    n_turns_list = []
    for game, seat in pairs:
        per_player = game["per_player"][str(seat)]
        final_inv = per_player.get("final_inv")
        if final_inv:
            fruit = sum(final_inv[0:4])
            wood = 4 * final_inv[5]
            total = fruit + wood
            fruit_pts.append(fruit)
            wood_pts.append(wood)
            total_pts.append(total)
            if total > 0:
                wood_share.append(wood / total)
        planted_ok = per_player.get("planted_ok") or {}
        plants_per_game.append(sum(planted_ok.values()))
        harvested_per_game.append(harvested_fruit_units(per_player.get("harvested") or {}))
        effects = per_player.get("effects") or {}
        chops_landed_per_game.append(effects.get("chops_landed", 0))
        wood_collected_per_game.append(effects.get("collected_WOOD", 0))
        iron_collected_per_game.append(effects.get("collected_IRON", 0))
        trains_issued_per_game.append(len(per_player.get("trains") or []))
        trains_succeeded_per_game.append(effects.get("trained", 0))
        n_turns_list.append(game.get("n_turns"))
    return {
        "n_games": len(pairs),
        "score": mean_sd_n(total_pts),
        "fruit_points": mean_sd_n(fruit_pts),
        "wood_points": mean_sd_n(wood_pts),
        "wood_share_of_score": mean_sd_n(wood_share),
        "plants_per_game": mean_sd_n(plants_per_game),
        "harvested_fruit_units_per_game": mean_sd_n(harvested_per_game),
        "chops_landed_per_game": mean_sd_n(chops_landed_per_game),
        "wood_collected_per_game": mean_sd_n(wood_collected_per_game),
        "iron_collected_per_game": mean_sd_n(iron_collected_per_game),
        "trains_issued_per_game": mean_sd_n(trains_issued_per_game),
        "trains_succeeded_per_game": mean_sd_n(trains_succeeded_per_game),
        "mean_game_length_turns": mean_sd_n(n_turns_list),
    }


def score_trajectory_shape(pairs: list[tuple[dict, int]]) -> dict:
    own_by_cut: dict[int, list[float]] = {cut: [] for cut in SCORE_CURVE_CUTS}
    opp_by_cut: dict[int, list[float]] = {cut: [] for cut in SCORE_CURVE_CUTS}
    for game, seat in pairs:
        opp_seat = 1 - seat
        own_curve = game["per_player"][str(seat)].get("score_curve") or []
        opp_curve = game["per_player"][str(opp_seat)].get("score_curve") or []
        for cut, own_value, opp_value in zip(SCORE_CURVE_CUTS, own_curve, opp_curve):
            if own_value is not None and opp_value is not None:
                own_by_cut[cut].append(own_value)
                opp_by_cut[cut].append(opp_value)
    result = {}
    for cut in SCORE_CURVE_CUTS:
        own_values = own_by_cut[cut]
        opp_values = opp_by_cut[cut]
        result[str(cut)] = {
            "n": len(own_values),
            "mean_own_score": statistics.mean(own_values) if own_values else None,
            "mean_opponent_score": statistics.mean(opp_values) if opp_values else None,
            "mean_margin": (
                statistics.mean(o - p for o, p in zip(own_values, opp_values)) if own_values else None
            ),
        }
    return result


# ---------------------------------------------------------------------------
# Part 3+4: heavy pass -- D101 generation-lineage reap-rate/suppression reuse
# ---------------------------------------------------------------------------


def _heavy_worker(task: dict) -> dict:
    game_id = task["game_id"]
    try:
        full_task = {
            "game": {**task["game_row"], "split": "b44"},
            "raw_path": RAW_GAMES / f"{game_id}.json",
            "trajectory_path": TRAJECTORIES / f"{game_id}.jsonl",
        }
        row = analyze_occurrence(
            full_task,
            task["agent_id"],
            {"pseudo": task["pseudo"], "source_rank": task["rank"], "cohort": task["cohort"]},
        )
        return {"ok": True, "row": row}
    except Exception as exc:  # noqa: BLE001 -- keep a complete audit, one bad game shouldn't abort the sweep
        return {"ok": False, "game_id": game_id, "agent_id": task["agent_id"], "error": f"{type(exc).__name__}: {exc}"}


def run_heavy_pass(occurrence_tasks: list[dict], jobs: int) -> tuple[list[dict], list[dict]]:
    if jobs <= 1:
        results = [_heavy_worker(task) for task in occurrence_tasks]
    else:
        with ProcessPoolExecutor(max_workers=jobs) as executor:
            results = list(executor.map(_heavy_worker, occurrence_tasks, chunksize=4))
    ok_rows = [result["row"] for result in results if result["ok"]]
    failures = [result for result in results if not result["ok"]]
    return ok_rows, failures


def integrity_rollup(rows: list[dict]) -> dict:
    n = len(rows)
    if n == 0:
        return {"n": 0}
    return {
        "n": n,
        "zero_unknown_diff_updates_rate": sum(row["integrity"]["unknown_diff_updates"] == 0 for row in rows) / n,
        "spawn_train_exact_rate": sum(
            row["integrity"]["workers"] == 1 + row["integrity"]["successful_trains"] for row in rows
        )
        / n,
        "event_reference_compatible_rate": sum(row["integrity"]["event_reference_compatible"] for row in rows) / n,
        "lineage_reference_compatible_rate": sum(
            row["integrity"]["lineage_reference_compatible"] for row in rows
        )
        / n,
    }


# ---------------------------------------------------------------------------
# Part 4 continued: tempo + opening (medium pass -- successful_events + trajectory)
# ---------------------------------------------------------------------------


def first_event_turn(events: list[dict], kind: str) -> int | None:
    turns = [event["turn"] for event in events if event["kind"] == kind]
    return min(turns) if turns else None


def first_event_item(events: list[dict], kind: str) -> str | None:
    matching = sorted((event for event in events if event["kind"] == kind), key=lambda event: event["turn"])
    return matching[0].get("item") if matching else None


def opening_verb_histogram(trajectory: list[dict], seat: int, window: int) -> Counter:
    counts: Counter = Counter()
    for row in trajectory[:window]:
        for command in action_commands(row.get(f"commands{seat}")):
            counts[command.split()[0].upper()] += 1
    return counts


def train_spec_at_turn(trajectory: list[dict], seat: int, turn: int | None) -> list[int] | None:
    if turn is None or turn < 1 or turn > len(trajectory):
        return None
    for command in action_commands(trajectory[turn - 1].get(f"commands{seat}")):
        fields = command.split()
        if fields and fields[0].upper() == "TRAIN" and len(fields) == 5:
            try:
                return [int(value) for value in fields[1:5]]
            except ValueError:
                return None
    return None


def _tempo_worker(task: dict) -> dict:
    game_id = task["game_id"]
    seat = task["seat"]
    try:
        raw = json.loads((RAW_GAMES / f"{game_id}.json").read_text())
        events_by_seat = successful_events(raw["frames"])
        own_events = events_by_seat[seat]
        trajectory = read_jsonl(TRAJECTORIES / f"{game_id}.jsonl")
        verb_hist = opening_verb_histogram(trajectory, seat, OPENING_WINDOW_TURNS)
        first_train_turn = first_event_turn(own_events, "TRAIN")
        spec = train_spec_at_turn(trajectory, seat, first_train_turn)
        return {
            "ok": True,
            "game_id": game_id,
            "agent_id": task["agent_id"],
            "cohort": task["cohort"],
            "first_train_turn": first_train_turn,
            "first_train_spec": spec,
            "first_train_role": role_of(spec) if spec else None,
            "first_plant_turn": first_event_turn(own_events, "PLANT"),
            "first_plant_item": first_event_item(own_events, "PLANT"),
            "first_harvest_turn": first_event_turn(own_events, "HARVEST"),
            "first_bank_turn": first_event_turn(own_events, "DROP"),
            "opening_verb_histogram": dict(verb_hist),
            "opening_has_pick": verb_hist.get("PICK", 0) > 0,
            "opening_turn1_has_train": bool(
                any(
                    command.split()[0].upper() == "TRAIN"
                    for command in action_commands(trajectory[0].get(f"commands{seat}"))
                )
                if trajectory
                else False
            ),
        }
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "game_id": game_id, "agent_id": task["agent_id"], "error": f"{type(exc).__name__}: {exc}"}


def run_tempo_pass(occurrence_tasks: list[dict], jobs: int) -> tuple[list[dict], list[dict]]:
    if jobs <= 1:
        results = [_tempo_worker(task) for task in occurrence_tasks]
    else:
        with ProcessPoolExecutor(max_workers=jobs) as executor:
            results = list(executor.map(_tempo_worker, occurrence_tasks, chunksize=4))
    ok_rows = [result for result in results if result["ok"]]
    failures = [result for result in results if not result["ok"]]
    return ok_rows, failures


def summarize_tempo(rows: list[dict]) -> dict:
    def turn_stats(field: str) -> dict:
        values = [row[field] for row in rows if row[field] is not None]
        return {
            "n_reached": len(values),
            "coverage": len(values) / len(rows) if rows else None,
            **mean_sd_n(values),
        }

    verb_totals: Counter = Counter()
    for row in rows:
        verb_totals.update(row["opening_verb_histogram"])
    n = len(rows)
    role_counts = Counter(row["first_train_role"] for row in rows if row["first_train_role"])
    spec_counts = Counter(
        spec_label(row["first_train_spec"]) for row in rows if row["first_train_spec"]
    )
    return {
        "n_games": n,
        "first_train_turn": turn_stats("first_train_turn"),
        "first_plant_turn": turn_stats("first_plant_turn"),
        "first_harvest_turn": turn_stats("first_harvest_turn"),
        "first_bank_turn": turn_stats("first_bank_turn"),
        "turn1_has_train_rate": sum(row["opening_turn1_has_train"] for row in rows) / n if n else None,
        "opening_has_pick_rate": sum(row["opening_has_pick"] for row in rows) / n if n else None,
        "first_plant_item_distribution": dict(
            Counter(row["first_plant_item"] for row in rows if row["first_plant_item"]).most_common()
        ),
        "first_train_role_distribution": dict(role_counts.most_common()),
        "first_train_role_rate": {role: count / n for role, count in role_counts.items()} if n else {},
        "first_train_spec_distribution_top10": dict(spec_counts.most_common(10)),
        "mean_opening_verb_counts_per_game": {
            verb: count / n for verb, count in sorted(verb_totals.items())
        }
        if n
        else {},
    }


# ---------------------------------------------------------------------------
# Part 6: head-to-head
# ---------------------------------------------------------------------------


def resident_vs_group(clean_games: list[dict], group_ids: set[int]) -> dict:
    rows = []
    for game in clean_games:
        p0, p1 = game["players"]
        if p0["agentId"] == RESIDENT_AGENT_ID and p1["agentId"] in group_ids:
            seat = 0
        elif p1["agentId"] == RESIDENT_AGENT_ID and p0["agentId"] in group_ids:
            seat = 1
        else:
            continue
        rows.append(
            {
                "margin": margin_of(game, seat),
                "won": won_of(game, seat),
                "opponent": game["players"][1 - seat]["agentId"],
            }
        )
    wins = sum(row["won"] for row in rows)
    return {
        "n": len(rows),
        "distinct_opponents": len({row["opponent"] for row in rows}),
        "win_rate": win_rate_ci(wins, len(rows)),
        "margin": bootstrap_mean_ci([row["margin"] for row in rows]),
    }


def counterpart_vs_scale(pairs: list[tuple[dict, int]], top5_ids: set[int]) -> dict:
    def bucket(predicate) -> dict:
        subset = [(game, seat) for game, seat in pairs if predicate(roster_of(game, 1 - seat))]
        wins = sum(won_of(game, seat) for game, seat in subset)
        margins = [margin_of(game, seat) for game, seat in subset]
        return {"n": len(subset), "win_rate": win_rate_ci(wins, len(subset)), "margin": bootstrap_mean_ci(margins)}

    top5_subset = [(game, seat) for game, seat in pairs if game["players"][1 - seat]["agentId"] in top5_ids]
    top5_wins = sum(won_of(game, seat) for game, seat in top5_subset)
    return {
        "vs_1_worker": bucket(lambda r: r == 1),
        "vs_2_worker": bucket(lambda r: r == 2),
        "vs_3_worker": bucket(lambda r: r == 3),
        "vs_4plus_worker": bucket(lambda r: r >= 4),
        "vs_top5_ranked_opponent": {
            "n": len(top5_subset),
            "win_rate": win_rate_ci(top5_wins, len(top5_subset)),
            "margin": bootstrap_mean_ci([margin_of(game, seat) for game, seat in top5_subset]),
        },
        "opponent_roster_histogram": dict(
            sorted(Counter(roster_of(game, 1 - seat) for game, seat in pairs).items())
        ),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--leaderboard", type=Path, default=None)
    parser.add_argument("--jobs", type=int, default=DEFAULT_JOBS)
    args = parser.parse_args()

    leaderboard_path = args.leaderboard or latest_leaderboard_path()
    leaderboard = load_leaderboard(leaderboard_path)
    all_games = load_games()
    clean_games = [game for game in all_games if is_clean(game)]
    print(f"loaded {len(all_games)} games; clean = {len(clean_games)}; leaderboard = {leaderboard_path}")

    cohort = build_cohort(clean_games, leaderboard)
    strong_ids = {row["agent_id"] for row in cohort["strong"]}
    peer_ids = {row["agent_id"] for row in cohort["peer_weak"]}
    all_cohort_ids = strong_ids | peer_ids
    print(f"cohort: {cohort['n_total']} agents ({cohort['n_strong']} strong, {cohort['n_peer_weak']} peer/weak)")

    top5_ids = {agent_id for agent_id, info in leaderboard.items() if info["division_index"] == 5 and info["rank"] <= 5}

    tracked_ids = all_cohort_ids | {RESIDENT_AGENT_ID}
    occ_index = index_agent_occurrences(clean_games, tracked_ids)

    def cohort_tag(agent_id: int) -> str:
        if agent_id == RESIDENT_AGENT_ID:
            return "resident"
        return "strong" if agent_id in strong_ids else "peer_weak"

    def rank_of(agent_id: int) -> int:
        return leaderboard[agent_id]["rank"]

    def pseudo_of(agent_id: int) -> str:
        return leaderboard[agent_id]["pseudo"]

    # ---- Part 1+2+5: score composition / production / trajectory shape (cheap) ----
    def group_pairs(ids: set[int]) -> list[tuple[dict, int]]:
        pairs = []
        for agent_id in ids:
            pairs.extend(occ_index[agent_id])
        return pairs

    strong_pairs = group_pairs(strong_ids)
    peer_pairs = group_pairs(peer_ids)
    resident_pairs = occ_index[RESIDENT_AGENT_ID]

    score_production = {
        "strong": score_production_stats(strong_pairs),
        "peer_weak": score_production_stats(peer_pairs),
        "resident": score_production_stats(resident_pairs),
        "per_agent": {
            str(agent_id): {
                "pseudo": pseudo_of(agent_id),
                "rank": rank_of(agent_id),
                "cohort": cohort_tag(agent_id),
                **score_production_stats(occ_index[agent_id]),
            }
            for agent_id in sorted(tracked_ids, key=rank_of)
        },
    }
    print("part 1+2 done: score composition + production")

    trajectory_shape = {
        "strong": score_trajectory_shape(strong_pairs),
        "peer_weak": score_trajectory_shape(peer_pairs),
        "resident": score_trajectory_shape(resident_pairs),
    }
    print("part 5a done: score-curve trajectory shape")

    # ---- Part 6: head-to-head (cheap) ----
    head_to_head = {
        "resident_vs_strong": resident_vs_group(clean_games, strong_ids),
        "resident_vs_peer_weak": resident_vs_group(clean_games, peer_ids),
        "strong_vs_scale": counterpart_vs_scale(strong_pairs, top5_ids),
        "peer_weak_vs_scale": counterpart_vs_scale(peer_pairs, top5_ids),
        "resident_vs_scale": counterpart_vs_scale(resident_pairs, top5_ids),
        "per_agent_vs_scale_top_strong": {
            str(agent_id): {
                "pseudo": pseudo_of(agent_id),
                "rank": rank_of(agent_id),
                **counterpart_vs_scale(occ_index[agent_id], top5_ids),
            }
            for agent_id in sorted(strong_ids, key=rank_of)[:5]
        },
    }
    print("part 6 done: head-to-head")

    # ---- Part 3+4: heavy pass (D101 reuse) ----
    heavy_tasks = []
    for agent_id in tracked_ids:
        tag = cohort_tag(agent_id)
        rank = rank_of(agent_id) if agent_id != RESIDENT_AGENT_ID else leaderboard[RESIDENT_AGENT_ID]["rank"]
        pseudo = pseudo_of(agent_id) if agent_id != RESIDENT_AGENT_ID else leaderboard[RESIDENT_AGENT_ID]["pseudo"]
        for game, seat in occ_index[agent_id]:
            heavy_tasks.append(
                {
                    "game_id": game["gameId"],
                    "game_row": game,
                    "agent_id": agent_id,
                    "seat": seat,
                    "cohort": tag,
                    "rank": rank,
                    "pseudo": pseudo,
                }
            )
    print(f"heavy pass: {len(heavy_tasks)} occurrences queued")
    heavy_rows, heavy_failures = run_heavy_pass(heavy_tasks, jobs=args.jobs)
    print(f"heavy pass done: {len(heavy_rows)} ok, {len(heavy_failures)} failed")

    rows_by_group: dict[str, list[dict]] = defaultdict(list)
    rows_by_agent: dict[int, list[dict]] = defaultdict(list)
    for row in heavy_rows:
        rows_by_group[row["cohort"]].append(row)
        rows_by_agent[row["agent_id"]].append(row)

    production_suppression = {
        "strong": summarize_rows(rows_by_group.get("strong", [])),
        "peer_weak": summarize_rows(rows_by_group.get("peer_weak", [])),
        "resident": summarize_rows(rows_by_group.get("resident", [])),
        "per_agent": {
            str(agent_id): {
                "pseudo": pseudo_of(agent_id) if agent_id != RESIDENT_AGENT_ID else leaderboard[RESIDENT_AGENT_ID]["pseudo"],
                "rank": rank_of(agent_id) if agent_id != RESIDENT_AGENT_ID else leaderboard[RESIDENT_AGENT_ID]["rank"],
                "cohort": cohort_tag(agent_id),
                **summarize_rows(rows),
            }
            for agent_id, rows in rows_by_agent.items()
        },
        "integrity": {
            "strong": integrity_rollup(rows_by_group.get("strong", [])),
            "peer_weak": integrity_rollup(rows_by_group.get("peer_weak", [])),
            "resident": integrity_rollup(rows_by_group.get("resident", [])),
        },
    }
    print(
        "part 3+4 done: reap-rate/suppression -- "
        f"strong pooled_reaped_coverage={production_suppression['strong']['actor_generations']['pooled_reaped_coverage']}, "
        f"resident={production_suppression['resident']['actor_generations']['pooled_reaped_coverage']}"
    )

    # ---- Part 4 continued: tempo + opening (medium pass) ----
    print(f"tempo pass: {len(heavy_tasks)} occurrences queued")
    tempo_rows, tempo_failures = run_tempo_pass(heavy_tasks, jobs=args.jobs)
    print(f"tempo pass done: {len(tempo_rows)} ok, {len(tempo_failures)} failed")

    tempo_by_group: dict[str, list[dict]] = defaultdict(list)
    tempo_by_agent: dict[int, list[dict]] = defaultdict(list)
    for row in tempo_rows:
        tempo_by_group[row["cohort"]].append(row)
        tempo_by_agent[row["agent_id"]].append(row)

    tempo_opening = {
        "strong": summarize_tempo(tempo_by_group.get("strong", [])),
        "peer_weak": summarize_tempo(tempo_by_group.get("peer_weak", [])),
        "resident": summarize_tempo(tempo_by_group.get("resident", [])),
        "per_agent": {
            str(agent_id): {
                "pseudo": pseudo_of(agent_id) if agent_id != RESIDENT_AGENT_ID else leaderboard[RESIDENT_AGENT_ID]["pseudo"],
                "rank": rank_of(agent_id) if agent_id != RESIDENT_AGENT_ID else leaderboard[RESIDENT_AGENT_ID]["rank"],
                "cohort": cohort_tag(agent_id),
                **summarize_tempo(rows),
            }
            for agent_id, rows in tempo_by_agent.items()
        },
    }
    print("part 4 done: tempo + opening")

    report = {
        "schema": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "read-only field-data peer-cohort study (B4.4): no arena writes, no strategy changes, no corpus mutation",
        "resident_agent_id": RESIDENT_AGENT_ID,
        "leaderboard_snapshot": str(leaderboard_path.relative_to(REPO)),
        "corpus": {"n_games_total": len(all_games), "n_games_clean": len(clean_games)},
        "cohort": cohort,
        "score_production": score_production,
        "trajectory_shape": trajectory_shape,
        "production_suppression": production_suppression,
        "tempo_opening": tempo_opening,
        "head_to_head": head_to_head,
        "failures": {"heavy": heavy_failures[:50], "tempo": tempo_failures[:50]},
        "tunables": {
            "min_games_for_cohort": MIN_GAMES_FOR_COHORT,
            "roster_band_halfwidth": ROSTER_BAND_HALFWIDTH,
            "opening_window_turns": OPENING_WINDOW_TURNS,
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=1) + "\n")
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
