#!/usr/bin/env python3
"""H3 -- the no-loop quartet audit (read-only research scout).

Task record: ``coordination/tasks/20260729-h3-no-loop-quartet.md``. Read-only field
study: no arena writes, no corpus mutation, no strategy changes, and no edits to any
tracked file other than this one.

Question (from the task brief): the resident (agent 6561795, roster 2.00, no sustained
plant-reap loop) collapses when outnumbered (margin -37.1 vs 3-worker opponents n=60,
5.0% win rate vs 4+-worker opponents n=20).  Four Legend agents -- Escdemon, therealbeef,
yamo, mehdi_ayari -- share the resident's macro profile (roster ~=2.00, no loop, per
B4.4's heterogeneity check, section 9 of ``b44-peer-cohort-report.md``) yet rank above it
and, pooled as part of B4.4's STRONG cohort, hold -1.8 at 2v3 (n=700) and 13.7% wins vs
4+ (n=190).  This script narrows that STRONG-cohort-wide number down to the exact
four-agent quartet, under matched (not pooled) comparisons, and revalidates the
"no-loop" label from primitives rather than from the aggregate D101 reap-rate number
alone.

Mandatory controls (from the integrated review that spawned this task):

1. Match, do not pool: opponent workforce, opponent identity/strength, seat, map,
   duration.  See ``matched_comparison`` -- layers ``raw_pooled`` (B4.4-style, for
   continuity), ``shared_opponent_matched`` (identical opponent identity),
   ``arena_score_band_matched`` (opponent strength bands + explicit confound
   quantification), ``seat_split``, ``map_overlap_matched`` (exact ``map_hash``),
   ``duration_tercile_split``, and ``ols_adjusted`` (multi-covariate OLS on
   margin ~ is_quartet + opponent arenaScore + game length, agent-clustered bootstrap
   CI on the is_quartet coefficient -- 5 clusters: resident + 4 quartet agents).
2. Revalidate "no-loop" from primitives (commands issued, crop fates), not from the
   aggregate D101 reap-rate number alone: see ``no_loop_revalidation`` -- combines (a)
   ``analyze_d101a_production_suppression``'s generation-lineage reap rate (same code
   path B4.4 used, recomputed fresh, split by opponent-roster bucket this time), (b)
   an *independent* code path, ``crop_fate_census``'s per-crop fate partition
   (harvested_by_owner / by_opponent / chopped_by_owner / by_opponent / alive_at_end),
   (c) a cadence/burst-vs-spread statistic computed directly from crop birth turns
   (single early burst vs a sustained, spread-out planting pattern), and (d) a fourth,
   fully independent, raw-command-level cross-check via
   ``recent_resident_field_census.successful_events`` (turn-decile histogram of
   successful PLANT/HARVEST commands).  Two+ independent measurement paths agreeing is
   the project's own standing bar for a trusted finding.
3. Separate policy value from maturity/matchmaking effects: see
   ``maturity_discussion`` -- rank/score deltas between the two most recent leaderboard
   snapshots (quantifies live non-stationarity), the opponent-arenaScore-faced
   comparison already produced by control #1's ``arena_score_band_matched`` layer
   (matchmaking affects *who* you play, which is exactly what that layer tests), and an
   explicit, honest statement of what cannot be recovered (no per-game historical
   timestamp exists in this corpus; local file mtime is a collection-time proxy only).
4. Concrete comparisons: unit specs/carry capacity, tree-size mix at felling, banking
   latency, target provenance, suppression rate/efficiency, score trajectory shape --
   see ``concrete_comparisons``, computed both overall and restricted to the outnumbered
   (opp_roster>=3) subset specifically, since that is where a mechanism must live if one
   exists.

Reuse, not a new parser (per the brief):

- ``cgauto.roster_outcome_pricing`` -- ``RESIDENT_AGENT_ID``, ``is_clean``, ``load_games``,
  ``load_leaderboard``, ``latest_leaderboard_path``, ``SNAPSHOTS_DIR``, ``roster_of``,
  ``margin_of``, ``won_of``, ``bootstrap_mean_ci``, ``win_rate_ci``, ``mean_sd_n``.
- ``cgauto.peer_cohort_analysis`` -- ``build_cohort`` (STRONG/PEER split, recomputed
  fresh against the newest snapshot as a sanity cross-check that the quartet still
  qualifies), ``index_agent_occurrences``, ``first_event_turn``, ``train_spec_at_turn``,
  ``score_trajectory_shape``.
- ``cgauto.analyze_d101a_production_suppression`` -- ``analyze_occurrence``,
  ``summarize_rows``, ``reconstruct_generation_actions`` (the exact generation-lineage
  reap-rate/suppression/target-provenance attribution D101 and B4.4 used).
- ``cgauto.crop_fate_census`` -- ``analyze_occurrence``, ``fate_summary``,
  ``interaction_totals``, ``expiry_summary``, ``harvest_power_summary`` (independent
  per-crop fate partition, a different code path from D101's).
- ``cgauto.recent_resident_field_census`` -- ``decoded_states``, ``successful_events``.
- ``cgauto.replay_conformance`` -- ``action_commands`` (via imports inside reused
  helpers).
- ``cgauto.top_player_macro_census`` -- ``role_of``, ``spec_label``.
- ``cgauto.top_player_opening_analysis`` -- ``analyze_players``.
- ``cgauto.waste_sweep`` -- ``agent_game_ids``, ``sweep`` (the six-detector execution-
  waste suite, comparative-baseline path, restricted here to the outnumbered subset for
  a banking-latency / execution-quality comparison).

The one genuinely new piece of code is ``_chop_size_worker`` (tree-size mix at felling):
it composes ``decoded_states`` + ``analyze_players`` + ``reconstruct_generation_actions``
(all reused, unmodified) and adds a ~20-line size lookup keyed by the already-decoded
per-turn plant state -- not a new parser.

CLI usage::

    .venv/bin/python cgauto/no_loop_quartet_audit.py --output <path/to/data.json>
        [--jobs 16] [--limit-per-agent N]
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

import numpy as np

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.roster_outcome_pricing import (  # noqa: E402
    RESIDENT_AGENT_ID,
    SNAPSHOTS_DIR,
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
from cgauto.peer_cohort_analysis import (  # noqa: E402
    build_cohort,
    first_event_turn,
    index_agent_occurrences,
    score_trajectory_shape,
    train_spec_at_turn,
)
from cgauto.analyze_d61p_field_snapshot import read_jsonl  # noqa: E402
from cgauto.analyze_d101a_production_suppression import (  # noqa: E402
    analyze_occurrence as d101_analyze_occurrence,
    reconstruct_generation_actions,
    summarize_rows as d101_summarize_rows,
)
from cgauto.crop_fate_census import (  # noqa: E402
    analyze_occurrence as fate_analyze_occurrence,
    fate_summary,
)
from cgauto.recent_resident_field_census import decoded_states, successful_events  # noqa: E402
from cgauto.top_player_macro_census import role_of  # noqa: E402
from cgauto.top_player_opening_analysis import analyze_players  # noqa: E402
from cgauto.waste_sweep import agent_game_ids, sweep as waste_sweep_run  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
RAW_GAMES = REPO / "data/raw/games"
TRAJECTORIES = REPO / "data/processed/trajectories"
SCRATCH_DIR = Path(
    "/tmp/claude-1001/-home-tarstars-prj-troll-farm/b1ce51c4-4193-48d1-ae46-922ac20ad6db/scratchpad"
)
DEFAULT_OUTPUT = SCRATCH_DIR / "h3-no-loop-quartet-data.json"

QUARTET_PSEUDOS = ("Escdemon", "therealbeef", "yamo", "mehdi_ayari")
MIN_CELL_N = 5  # below this a bucket is flagged "sparse" -- project-standard floor
DEFAULT_JOBS = 16
N_BOOT_OLS = 2000
BOOT_SEED = 20260729


# ---------------------------------------------------------------------------
# Small stats helpers not already in roster_outcome_pricing
# ---------------------------------------------------------------------------


def ratio_or_none(numerator, denominator):
    return numerator / denominator if denominator else None


def tertile_edges(values: list[float]) -> list[float]:
    ordered = sorted(values)
    cuts = statistics.quantiles(ordered, n=3)
    return [ordered[0], cuts[0], cuts[1], ordered[-1] + 1e-6]


def make_bands(edges: list[float]) -> dict[str, tuple[float, float]]:
    labels = ["low", "mid", "high"]
    return {labels[i]: (edges[i], edges[i + 1]) for i in range(3)}


def bucket_stats(rows: list[dict]) -> dict:
    wins = sum(row["won"] for row in rows)
    return {
        "n": len(rows),
        "win_rate": win_rate_ci(wins, len(rows)),
        "margin": bootstrap_mean_ci([row["margin"] for row in rows]),
        "sparse": len(rows) < MIN_CELL_N,
    }


# ---------------------------------------------------------------------------
# Part 0: cohort resolution
# ---------------------------------------------------------------------------


def resolve_quartet(leaderboard: dict[int, dict]) -> dict[str, int]:
    by_pseudo: dict[str, int] = {}
    for agent_id, info in leaderboard.items():
        if info.get("pseudo") in QUARTET_PSEUDOS:
            by_pseudo[info["pseudo"]] = agent_id
    missing = set(QUARTET_PSEUDOS) - set(by_pseudo)
    if missing:
        raise SystemExit(f"quartet pseudos not found in newest leaderboard snapshot: {sorted(missing)}")
    return by_pseudo


def cohort_table(clean_games: list[dict], leaderboard: dict[int, dict], quartet_ids: dict[str, int]) -> dict:
    rosters: dict[int, list[int]] = defaultdict(list)
    for game in clean_games:
        for player in game["players"]:
            rosters[player["agentId"]].append(roster_of(game, player["index"]))

    def row_for(agent_id: int, pseudo_override: str | None = None) -> dict:
        own = rosters.get(agent_id, [])
        info = leaderboard.get(agent_id, {})
        return {
            "agent_id": agent_id,
            "pseudo": pseudo_override or info.get("pseudo"),
            "rank": info.get("rank"),
            "score": info.get("score"),
            "division_index": info.get("division_index"),
            "n_games": len(own),
            "mean_roster": statistics.mean(own) if own else None,
            "median_roster": statistics.median(own) if own else None,
            "pct_games_at_roster_2": ratio_or_none(sum(r == 2 for r in own), len(own)),
        }

    resident_row = row_for(RESIDENT_AGENT_ID)
    quartet_rows = {pseudo: row_for(agent_id, pseudo) for pseudo, agent_id in quartet_ids.items()}

    strong_cohort = build_cohort(clean_games, leaderboard)
    strong_pseudos = {row["pseudo"] for row in strong_cohort["strong"]}
    still_strong = {pseudo: pseudo in strong_pseudos for pseudo in quartet_ids}

    return {
        "resident": resident_row,
        "quartet": quartet_rows,
        "b44_strong_cohort_recomputed_fresh": {
            "n_strong": strong_cohort["n_strong"],
            "quartet_still_in_strong_cohort": still_strong,
            "resident_rank_used_for_split": strong_cohort["resident"]["rank"],
        },
    }


# ---------------------------------------------------------------------------
# Part 1: occurrence indexing / matched-row construction
# ---------------------------------------------------------------------------


def build_rows(pairs: list[tuple[dict, int]], agent_id: int, leaderboard: dict[int, dict]) -> list[dict]:
    rows = []
    for game, seat in pairs:
        opp_seat = 1 - seat
        opp_player = game["players"][opp_seat]
        opp_id = opp_player["agentId"]
        opp_lb = leaderboard.get(opp_id)
        effects = game["per_player"][str(seat)].get("effects", {})
        rows.append(
            {
                "game_id": game["gameId"],
                "_agent_id": agent_id,
                "seat": seat,
                "own_roster": roster_of(game, seat),
                "opp_agent_id": opp_id,
                "opp_roster": roster_of(game, opp_seat),
                "opp_arena_score_leaderboard": opp_lb["score"] if opp_lb else None,
                "opp_arena_score_embedded": opp_player.get("arenaScore"),
                "opp_rank_leaderboard": opp_lb["rank"] if opp_lb else None,
                "map_hash": game.get("map_hash"),
                "n_turns": game.get("n_turns"),
                "margin": margin_of(game, seat),
                "won": won_of(game, seat),
                "wood_collected": effects.get("collected_WOOD", 0),
                "chops_landed": effects.get("chops_landed", 0),
            }
        )
    return [row for row in rows if row["own_roster"] == 2]


# ---------------------------------------------------------------------------
# Part 2: matched comparison layers (mandatory control #1)
# ---------------------------------------------------------------------------


def build_design_matrix(rows: list[dict], covariate_fields: list[str]) -> tuple[np.ndarray, np.ndarray]:
    X, y = [], []
    for row in rows:
        vec = [1.0]
        ok = True
        for field in covariate_fields:
            value = row.get(field)
            if value is None:
                ok = False
                break
            vec.append(float(value))
        if not ok:
            continue
        X.append(vec)
        y.append(row["margin"])
    return np.array(X, dtype=float), np.array(y, dtype=float)


def ols_fit(X: np.ndarray, y: np.ndarray) -> dict | None:
    n, k = X.shape
    if n <= k:
        return None
    coef, _, _, _ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ coef
    dof = n - k
    sigma2 = float(resid @ resid / dof) if dof > 0 else None
    se = None
    if sigma2 is not None:
        try:
            xtx_inv = np.linalg.inv(X.T @ X)
            se = np.sqrt(np.diag(xtx_inv) * sigma2)
        except np.linalg.LinAlgError:
            se = None
    return {"coef": coef, "se": se, "n": n, "dof": dof}


def ols_adjusted_gap(rows: list[dict], covariate_fields: list[str]) -> dict:
    names = ["intercept"] + covariate_fields
    X, y = build_design_matrix(rows, covariate_fields)
    if X.size == 0:
        return {"n": 0, "note": "no rows with complete covariates"}
    fit = ols_fit(X, y)
    if fit is None:
        return {"n": X.shape[0], "note": "not enough rows relative to covariates"}
    point = {name: float(value) for name, value in zip(names, fit["coef"])}
    se = {name: float(value) for name, value in zip(names, fit["se"])} if fit["se"] is not None else None

    complete_rows = [row for row in rows if all(row.get(f) is not None for f in covariate_fields)]
    by_agent: dict[int, list[dict]] = defaultdict(list)
    for row in complete_rows:
        by_agent[row["_agent_id"]].append(row)
    agent_keys = sorted(by_agent)

    boot_vals = []
    idx_quartet = names.index("is_quartet") if "is_quartet" in names else None
    if idx_quartet is not None and len(agent_keys) >= 2:
        rng = np.random.default_rng(BOOT_SEED)
        for _ in range(N_BOOT_OLS):
            chosen = rng.choice(agent_keys, size=len(agent_keys), replace=True)
            boot_rows = [row for key in chosen for row in by_agent[key]]
            Xb, yb = build_design_matrix(boot_rows, covariate_fields)
            fit_b = ols_fit(Xb, yb)
            if fit_b is not None:
                boot_vals.append(float(fit_b["coef"][idx_quartet]))
    ci = {}
    if boot_vals:
        lo, hi = np.percentile(boot_vals, [2.5, 97.5])
        ci = {"ci_lo": float(lo), "ci_hi": float(hi), "n_boot_ok": len(boot_vals)}

    return {
        "n": fit["n"],
        "dof": fit["dof"],
        "covariates": names,
        "coef": point,
        "se_classic_iid": se,
        "is_quartet_coef": point.get("is_quartet"),
        "is_quartet_agent_clustered_bootstrap_ci": ci,
        "n_agent_clusters": len(agent_keys),
        "note": "SE is classic OLS (i.i.d. residuals); the CI is the trustworthy one -- agent-clustered bootstrap (5 clusters: resident + 4 quartet agents), matching roster_outcome_pricing's within_agent_pooled_regression convention",
    }


def matched_comparison(
    resident_rows_all: list[dict],
    quartet_rows_all_by_pseudo: dict[str, list[dict]],
    roster_predicate,
) -> dict:
    resident_subset = [row for row in resident_rows_all if roster_predicate(row["opp_roster"])]
    quartet_subset_by_pseudo = {
        pseudo: [row for row in rows if roster_predicate(row["opp_roster"])]
        for pseudo, rows in quartet_rows_all_by_pseudo.items()
    }
    quartet_pooled = [row for rows in quartet_subset_by_pseudo.values() for row in rows]

    raw_pooled = {
        "resident": bucket_stats(resident_subset),
        "quartet_pooled": bucket_stats(quartet_pooled),
        "quartet_per_agent": {pseudo: bucket_stats(rows) for pseudo, rows in quartet_subset_by_pseudo.items()},
    }

    # Layer 1 -- shared opponent identity (tightest possible control)
    resident_opp_ids = {row["opp_agent_id"] for row in resident_subset}
    quartet_opp_ids = {row["opp_agent_id"] for row in quartet_pooled}
    shared_ids = resident_opp_ids & quartet_opp_ids
    shared_opponent = {
        "n_shared_opponent_identities": len(shared_ids),
        "n_resident_distinct_opponents": len(resident_opp_ids),
        "n_quartet_distinct_opponents": len(quartet_opp_ids),
        "resident_on_shared": bucket_stats([row for row in resident_subset if row["opp_agent_id"] in shared_ids]),
        "quartet_on_shared": bucket_stats([row for row in quartet_pooled if row["opp_agent_id"] in shared_ids]),
    }

    # Layer 2 -- opponent arenaScore band (confound quantification + matched bands)
    covered_resident = [row for row in resident_subset if row["opp_arena_score_leaderboard"] is not None]
    covered_quartet = [row for row in quartet_pooled if row["opp_arena_score_leaderboard"] is not None]
    pooled_scores = [row["opp_arena_score_leaderboard"] for row in covered_resident + covered_quartet]
    arena_band = {
        "coverage_resident": ratio_or_none(len(covered_resident), len(resident_subset)),
        "coverage_quartet": ratio_or_none(len(covered_quartet), len(quartet_pooled)),
        "mean_opp_arena_score_resident": mean_sd_n([row["opp_arena_score_leaderboard"] for row in covered_resident]),
        "mean_opp_arena_score_quartet": mean_sd_n([row["opp_arena_score_leaderboard"] for row in covered_quartet]),
    }
    if len(pooled_scores) >= 6:
        bands = make_bands(tertile_edges(pooled_scores))
        arena_band["bands"] = {
            label: {
                "score_range": [lo, hi],
                "resident": bucket_stats(
                    [row for row in covered_resident if lo <= row["opp_arena_score_leaderboard"] < hi]
                ),
                "quartet_pooled": bucket_stats(
                    [row for row in covered_quartet if lo <= row["opp_arena_score_leaderboard"] < hi]
                ),
            }
            for label, (lo, hi) in bands.items()
        }

    # Layer 3 -- seat split
    seat_split = {
        "resident_seat0": bucket_stats([row for row in resident_subset if row["seat"] == 0]),
        "resident_seat1": bucket_stats([row for row in resident_subset if row["seat"] == 1]),
        "quartet_seat0": bucket_stats([row for row in quartet_pooled if row["seat"] == 0]),
        "quartet_seat1": bucket_stats([row for row in quartet_pooled if row["seat"] == 1]),
    }

    # Layer 4 -- map overlap (exact map_hash)
    resident_maps = {row["map_hash"] for row in resident_subset}
    quartet_maps = {row["map_hash"] for row in quartet_pooled}
    shared_maps = resident_maps & quartet_maps
    map_overlap = {
        "n_resident_distinct_maps": len(resident_maps),
        "n_quartet_distinct_maps": len(quartet_maps),
        "n_shared_maps": len(shared_maps),
        "jaccard": ratio_or_none(len(shared_maps), len(resident_maps | quartet_maps)),
        "resident_on_shared_maps": bucket_stats([row for row in resident_subset if row["map_hash"] in shared_maps]),
        "quartet_on_shared_maps": bucket_stats([row for row in quartet_pooled if row["map_hash"] in shared_maps]),
    }

    # Layer 5 -- duration tercile
    pooled_turns = [row["n_turns"] for row in resident_subset + quartet_pooled if row["n_turns"] is not None]
    duration = {}
    if len(pooled_turns) >= 6:
        bands = make_bands(tertile_edges(pooled_turns))
        duration["bands"] = {
            label: {
                "turn_range": [lo, hi],
                "resident": bucket_stats(
                    [row for row in resident_subset if row["n_turns"] is not None and lo <= row["n_turns"] < hi]
                ),
                "quartet_pooled": bucket_stats(
                    [row for row in quartet_pooled if row["n_turns"] is not None and lo <= row["n_turns"] < hi]
                ),
            }
            for label, (lo, hi) in bands.items()
        }

    # Layer 6 -- multi-covariate OLS, agent-clustered bootstrap CI on is_quartet
    pooled_for_ols = []
    for row in resident_subset:
        pooled_for_ols.append({**row, "is_quartet": 0.0})
    for row in quartet_pooled:
        pooled_for_ols.append({**row, "is_quartet": 1.0})
    ols = ols_adjusted_gap(pooled_for_ols, ["is_quartet", "opp_arena_score_leaderboard", "n_turns"])

    return {
        "n_resident": len(resident_subset),
        "n_quartet_pooled": len(quartet_pooled),
        "raw_pooled": raw_pooled,
        "shared_opponent_matched": shared_opponent,
        "arena_score_band_matched": arena_band,
        "seat_split": seat_split,
        "map_overlap_matched": map_overlap,
        "duration_tercile_split": duration,
        "ols_adjusted": ols,
    }


# ---------------------------------------------------------------------------
# Part 3: no-loop revalidation from primitives (mandatory control #2)
# ---------------------------------------------------------------------------


def _d101_worker(task: dict) -> dict:
    game_id = task["game_id"]
    try:
        full_task = {
            "game": {**task["game_row"], "split": "h3"},
            "raw_path": RAW_GAMES / f"{game_id}.json",
            "trajectory_path": TRAJECTORIES / f"{game_id}.jsonl",
        }
        row = d101_analyze_occurrence(
            full_task,
            task["agent_id"],
            {"pseudo": task["pseudo"], "source_rank": task["rank"], "cohort": task["cohort"]},
        )
        return {"ok": True, "row": row}
    except Exception as exc:  # noqa: BLE001 -- keep a complete audit, one bad game shouldn't abort the sweep
        return {"ok": False, "game_id": game_id, "agent_id": task["agent_id"], "error": f"{type(exc).__name__}: {exc}"}


def run_d101_pass(tasks: list[dict], jobs: int) -> tuple[list[dict], list[dict]]:
    if jobs <= 1:
        results = [_d101_worker(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=jobs) as executor:
            results = list(executor.map(_d101_worker, tasks, chunksize=4))
    ok_rows = [result["row"] for result in results if result["ok"]]
    failures = [result for result in results if not result["ok"]]
    return ok_rows, failures


def run_fate_pass(tasks: list[dict], jobs: int) -> tuple[list[dict], list[dict]]:
    if jobs <= 1:
        results = [
            fate_analyze_occurrence(task["game_id"], task["agent_id"], task["seat"], task["cohort"], task["pseudo"])
            for task in tasks
        ]
    else:
        with ProcessPoolExecutor(max_workers=jobs) as executor:
            results = list(
                executor.map(
                    fate_analyze_occurrence,
                    [task["game_id"] for task in tasks],
                    [task["agent_id"] for task in tasks],
                    [task["seat"] for task in tasks],
                    [task["cohort"] for task in tasks],
                    [task["pseudo"] for task in tasks],
                    chunksize=4,
                )
            )
    ok_rows = [result for result in results if result["ok"]]
    failures = [result for result in results if not result["ok"]]
    return ok_rows, failures


def cadence_stats(occurrences: list[dict]) -> dict:
    """Burst-vs-spread signal computed directly from crop_fate_census's own per-crop
    ``birth_turn``/``fate`` primitives (an agent's own-created generations only, per
    ``crop_fate_census.analyze_occurrence``): a "sustained loop" should show repeated
    plantings spread across the game with a healthy owner-harvest closure rate; a
    single early burst (e.g. one starter/mother tree, or a wood-farming cell chopped
    once and abandoned) should show almost all creations in the first fifth of the game
    and few games with 2+ own creations."""

    per_game_counts = []
    early_num = early_den = 0
    norm_positions = []
    gaps = []
    for occ in occurrences:
        crops = occ["crops"]
        turns = occ["turns"] or 1
        per_game_counts.append(len(crops))
        births = sorted(crop["birth_turn"] for crop in crops)
        for birth in births:
            norm = birth / turns
            norm_positions.append(norm)
            early_den += 1
            if norm <= 0.2:
                early_num += 1
        if len(births) >= 2:
            gaps.extend(b2 - b1 for b1, b2 in zip(births, births[1:]))
    return {
        "occurrences": len(occurrences),
        "own_crops_per_game": mean_sd_n(per_game_counts),
        "games_with_zero_own_crops_rate": ratio_or_none(sum(1 for c in per_game_counts if c == 0), len(per_game_counts)),
        "games_with_2plus_own_creations_rate": ratio_or_none(sum(1 for c in per_game_counts if c >= 2), len(per_game_counts)),
        "own_creation_fraction_in_first_20pct_of_game": ratio_or_none(early_num, early_den),
        "mean_normalized_birth_position": statistics.mean(norm_positions) if norm_positions else None,
        "mean_gap_between_successive_own_plantings_turns": statistics.mean(gaps) if gaps else None,
    }


def _events_worker(task: dict) -> dict:
    game_id = task["game_id"]
    seat = task["seat"]
    try:
        raw = json.loads((RAW_GAMES / f"{game_id}.json").read_text())
        own_events = successful_events(raw["frames"])[seat]
        n_turns = task["n_turns"] or max((event["turn"] for event in own_events), default=1)
        plant_deciles: Counter = Counter()
        harvest_deciles: Counter = Counter()
        for event in own_events:
            decile = min(9, int(10 * event["turn"] / max(n_turns, 1)))
            if event["kind"] == "PLANT":
                plant_deciles[decile] += 1
            elif event["kind"] == "HARVEST":
                harvest_deciles[decile] += 1
        first_bank_turn = first_event_turn(own_events, "DROP")
        return {
            "ok": True,
            "game_id": game_id,
            "agent_id": task["agent_id"],
            "plant_count": sum(plant_deciles.values()),
            "harvest_count": sum(harvest_deciles.values()),
            "plant_deciles": dict(plant_deciles),
            "harvest_deciles": dict(harvest_deciles),
            "first_bank_turn": first_bank_turn,
        }
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "game_id": game_id, "agent_id": task["agent_id"], "error": f"{type(exc).__name__}: {exc}"}


def run_events_pass(tasks: list[dict], jobs: int) -> tuple[list[dict], list[dict]]:
    if jobs <= 1:
        results = [_events_worker(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=jobs) as executor:
            results = list(executor.map(_events_worker, tasks, chunksize=8))
    ok_rows = [result for result in results if result["ok"]]
    failures = [result for result in results if not result["ok"]]
    return ok_rows, failures


def events_histogram(rows: list[dict]) -> dict:
    plant: Counter = Counter()
    harvest: Counter = Counter()
    for row in rows:
        for decile, count in row["plant_deciles"].items():
            plant[int(decile)] += count
        for decile, count in row["harvest_deciles"].items():
            harvest[int(decile)] += count
    return {"plant_by_decile": dict(sorted(plant.items())), "harvest_by_decile": dict(sorted(harvest.items()))}


def no_loop_revalidation(
    d101_rows: list[dict],
    fate_rows: list[dict],
    events_rows: list[dict],
    opp_roster_lookup: dict[tuple[int, int], int | None],
    agent_ids: dict[str, int],
) -> dict:
    buckets = {
        "all": lambda roster: True,
        "vs2": lambda roster: roster == 2,
        "vs3": lambda roster: roster == 3,
        "vs4plus": lambda roster: roster is not None and roster >= 4,
    }

    def per_agent(agent_id: int) -> dict:
        d_all = [row for row in d101_rows if row["agent_id"] == agent_id]
        f_all = [row for row in fate_rows if row["agent_id"] == agent_id]
        e_all = [row for row in events_rows if row["agent_id"] == agent_id]
        out = {}
        for label, predicate in buckets.items():
            d_sub = [row for row in d_all if predicate(opp_roster_lookup.get((row["game_id"], agent_id)))]
            f_sub = [row for row in f_all if predicate(opp_roster_lookup.get((row["game_id"], agent_id)))]
            e_sub = [row for row in e_all if predicate(opp_roster_lookup.get((row["game_id"], agent_id)))]
            out[label] = {
                "n": len(d_sub),
                "d101": d101_summarize_rows(d_sub) if d_sub else None,
                "fate": fate_summary(f_sub) if f_sub else None,
                "cadence": cadence_stats(f_sub) if f_sub else None,
                "events_decile_histogram": events_histogram(e_sub) if e_sub else None,
            }
        return out

    per_agent_out = {label: per_agent(agent_id) for label, agent_id in agent_ids.items()}

    verdicts = {}
    for label, data in per_agent_out.items():
        all_bucket = data["all"]
        d101_reap = all_bucket["d101"]["actor_generations"]["pooled_reaped_coverage"] if all_bucket["d101"] else None
        fate_reap = None
        if all_bucket["fate"]:
            fate_reap = all_bucket["fate"]["by_fate"].get("harvested_by_owner", {}).get("rate")
        classification = "unknown"
        if fate_reap is not None:
            if fate_reap < 0.05:
                classification = "no-loop (own-reap rate < 5%, matches resident's near-zero profile)"
            elif fate_reap < 0.15:
                classification = "borderline / partial (own-reap rate 5-15%, between resident and cohort norm)"
            else:
                classification = "loop-present (own-reap rate >= 15%, matches STRONG/PEER cohort norm)"
        verdicts[label] = {
            "d101_pooled_reaped_coverage": d101_reap,
            "crop_fate_harvested_by_owner_rate": fate_reap,
            "classification": classification,
        }

    return {"per_agent": per_agent_out, "verdicts": verdicts}


# ---------------------------------------------------------------------------
# Part 4: concrete comparisons (mandatory control #4)
# ---------------------------------------------------------------------------


def _spec_worker(task: dict) -> dict:
    game_id = task["game_id"]
    seat = task["seat"]
    try:
        raw = json.loads((RAW_GAMES / f"{game_id}.json").read_text())
        trajectory = read_jsonl(TRAJECTORIES / f"{game_id}.jsonl")
        own_events = successful_events(raw["frames"])[seat]
        first_train_turn = first_event_turn(own_events, "TRAIN")
        spec = train_spec_at_turn(trajectory, seat, first_train_turn)
        return {
            "ok": True,
            "game_id": game_id,
            "agent_id": task["agent_id"],
            "first_train_turn": first_train_turn,
            "spec": spec,
            "role": role_of(spec) if spec else None,
        }
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "game_id": game_id, "agent_id": task["agent_id"], "error": f"{type(exc).__name__}: {exc}"}


def run_spec_pass(tasks: list[dict], jobs: int) -> tuple[list[dict], list[dict]]:
    if jobs <= 1:
        results = [_spec_worker(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=jobs) as executor:
            results = list(executor.map(_spec_worker, tasks, chunksize=8))
    ok_rows = [result for result in results if result["ok"]]
    failures = [result for result in results if not result["ok"]]
    return ok_rows, failures


def summarize_specs(rows: list[dict]) -> dict:
    specced = [row for row in rows if row["spec"]]
    if not specced:
        return {"n": len(rows), "n_specced": 0}
    ms = [row["spec"][0] for row in specced]
    cc = [row["spec"][1] for row in specced]
    hp = [row["spec"][2] for row in specced]
    chop = [row["spec"][3] for row in specced]
    return {
        "n": len(rows),
        "n_specced": len(specced),
        "mean_movement_speed": statistics.mean(ms),
        "mean_carry_capacity": statistics.mean(cc),
        "mean_harvest_power": statistics.mean(hp),
        "mean_chop_power": statistics.mean(chop),
        "role_distribution": dict(Counter(row["role"] for row in specced).most_common()),
        "spec_distribution_top5": dict(
            Counter("/".join(str(v) for v in row["spec"]) for row in specced).most_common(5)
        ),
    }


def _chop_size_worker(task: dict) -> dict:
    """Tree-size mix at felling: composes decoded_states + analyze_players +
    reconstruct_generation_actions (all reused, unmodified) and adds a size lookup
    against the already-decoded per-turn plant state -- not a new parser."""

    game_id = task["game_id"]
    seat = task["seat"]
    try:
        raw = json.loads((RAW_GAMES / f"{game_id}.json").read_text())
        trajectory = read_jsonl(TRAJECTORIES / f"{game_id}.jsonl")
        _map_data, states, unknown = decoded_states(raw, trajectory)
        usable = min(len(states) - 1, len(trajectory))
        if unknown or usable != len(trajectory):
            return {"ok": False, "game_id": game_id, "agent_id": task["agent_id"], "error": "decode mismatch"}
        analyses = analyze_players(states, trajectory)
        worker_ordinals = {int(worker["unit_id"]): int(worker["ordinal"]) for worker in analyses[seat]["workers"]}
        events, _generations, _lineage, _quality = reconstruct_generation_actions(states, trajectory, seat, worker_ordinals)
        chops = []
        for event in events:
            if event["verb"] != "CHOP" or not event["success"]:
                continue
            turn = event["turn"]
            unit = next((u for u in states[turn - 1]["units"] if u["id"] == event["unit_id"]), None)
            if unit is None:
                continue
            cell = (int(unit["x"]), int(unit["y"]))
            plant = next(
                (p for p in states[turn - 1]["plants"] if (int(p["x"]), int(p["y"])) == cell),
                None,
            )
            if plant is None:
                continue
            chops.append(
                {
                    "size": int(plant["size"]),
                    "kind": plant["type"],
                    "target_origin": event["target_origin"],
                    "wood_gained": int(event["gained"].get("WOOD", 0)),
                }
            )
        return {"ok": True, "game_id": game_id, "agent_id": task["agent_id"], "chops": chops}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "game_id": game_id, "agent_id": task["agent_id"], "error": f"{type(exc).__name__}: {exc}"}


def run_chop_size_pass(tasks: list[dict], jobs: int) -> tuple[list[dict], list[dict]]:
    if jobs <= 1:
        results = [_chop_size_worker(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=jobs) as executor:
            results = list(executor.map(_chop_size_worker, tasks, chunksize=4))
    ok_rows = [result for result in results if result["ok"]]
    failures = [result for result in results if not result["ok"]]
    return ok_rows, failures


def summarize_chop_sizes(rows: list[dict]) -> dict:
    chops = [chop for row in rows for chop in row["chops"]]
    if not chops:
        return {"games": len(rows), "chops": 0}
    sizes = [chop["size"] for chop in chops]
    by_origin: Counter = Counter(chop["target_origin"] or "none" for chop in chops)
    wood_by_size: dict[int, list[int]] = defaultdict(list)
    for chop in chops:
        wood_by_size[chop["size"]].append(chop["wood_gained"])
    return {
        "games": len(rows),
        "chops": len(chops),
        "chops_per_game": ratio_or_none(len(chops), len(rows)),
        "size_distribution": dict(sorted(Counter(sizes).items())),
        "mean_size": statistics.mean(sizes),
        "target_origin_distribution": dict(by_origin.most_common()),
        "mean_wood_gained_by_size": {
            str(size): statistics.mean(values) for size, values in sorted(wood_by_size.items())
        },
        "total_wood_gained": sum(chop["wood_gained"] for chop in chops),
    }


def suppression_efficiency(rows: list[dict]) -> dict:
    total_wood = sum(row["wood_collected"] for row in rows)
    total_chops = sum(row["chops_landed"] for row in rows)
    return {
        "n_games": len(rows),
        "mean_wood_collected_per_game": ratio_or_none(total_wood, len(rows)),
        "mean_chops_landed_per_game": ratio_or_none(total_chops, len(rows)),
        "wood_per_chop": ratio_or_none(total_wood, total_chops),
    }


def concrete_comparisons(
    agent_ids: dict[str, int],
    rows_by_label: dict[str, list[dict]],
    outnumbered_rows_by_label: dict[str, list[dict]],
    occ_index: dict[int, list[tuple[dict, int]]],
    spec_rows: list[dict],
    d101_rows: list[dict],
    opp_roster_lookup: dict[tuple[int, int], int | None],
    waste_sweep_by_label: dict[str, dict],
    chop_size_rows: list[dict],
) -> dict:
    out = {}
    for label, agent_id in agent_ids.items():
        rows_all = rows_by_label[label]
        rows_outnumbered = outnumbered_rows_by_label[label]
        pairs_outnumbered = [(game, seat) for game, seat in occ_index[agent_id] if roster_of(game, 1 - seat) >= 3]
        own_spec_rows = [row for row in spec_rows if row["agent_id"] == agent_id]
        own_d101_all = [row for row in d101_rows if row["agent_id"] == agent_id]
        own_d101_outnumbered = [
            row for row in own_d101_all if (opp_roster_lookup.get((row["game_id"], agent_id)) or 0) >= 3
        ]
        own_chop_rows = [row for row in chop_size_rows if row["agent_id"] == agent_id]
        out[label] = {
            "unit_specs_first_trained_worker": {
                "overall": summarize_specs(own_spec_rows),
            },
            "target_provenance_successful_actions": {
                "overall": d101_summarize_rows(own_d101_all)["successful_material_actions"] if own_d101_all else None,
                "outnumbered_vs3plus": (
                    d101_summarize_rows(own_d101_outnumbered)["successful_material_actions"]
                    if own_d101_outnumbered
                    else None
                ),
            },
            "suppression_efficiency": {
                "overall": suppression_efficiency(rows_all),
                "outnumbered_vs3plus": suppression_efficiency(rows_outnumbered),
                "opponent_contact_coverage_overall": (
                    d101_summarize_rows(own_d101_all)["opponent_generations"]["pooled_contact_coverage"]
                    if own_d101_all
                    else None
                ),
                "opponent_contact_coverage_outnumbered_vs3plus": (
                    d101_summarize_rows(own_d101_outnumbered)["opponent_generations"]["pooled_contact_coverage"]
                    if own_d101_outnumbered
                    else None
                ),
            },
            "score_trajectory_shape_outnumbered_vs3plus": score_trajectory_shape(pairs_outnumbered),
            "banking_latency_and_execution_waste_outnumbered_vs3plus": waste_sweep_by_label.get(label),
            "tree_size_mix_at_felling_outnumbered_vs3plus": summarize_chop_sizes(own_chop_rows),
        }
    return out


# ---------------------------------------------------------------------------
# Part 5: maturity / pool discussion (mandatory control #3)
# ---------------------------------------------------------------------------


def previous_leaderboard_path() -> Path | None:
    candidates = sorted(path for path in SNAPSHOTS_DIR.iterdir() if path.is_dir() and (path / "leaderboard.json").exists())
    if len(candidates) < 2:
        return None
    return candidates[-2] / "leaderboard.json"


def maturity_discussion(
    leaderboard_current: dict[int, dict],
    leaderboard_current_path: Path,
    agent_ids: dict[str, int],
) -> dict:
    prev_path = previous_leaderboard_path()
    leaderboard_prev = load_leaderboard(prev_path) if prev_path else {}

    def snap(lb: dict[int, dict], agent_id: int) -> dict | None:
        info = lb.get(agent_id)
        return {"rank": info["rank"], "score": info["score"]} if info else None

    deltas = {}
    for label, agent_id in {"resident": RESIDENT_AGENT_ID, **agent_ids}.items():
        prev = snap(leaderboard_prev, agent_id)
        curr = snap(leaderboard_current, agent_id)
        deltas[label] = {
            "prev_snapshot": prev,
            "current_snapshot": curr,
            "rank_delta": (curr["rank"] - prev["rank"]) if prev and curr else None,
            "score_delta": (curr["score"] - prev["score"]) if prev and curr else None,
        }

    mtime_stats = {}
    for label, agent_id in {"resident": RESIDENT_AGENT_ID, **agent_ids}.items():
        game_ids = agent_game_ids(agent_id)
        times = []
        for game_id in game_ids:
            path = RAW_GAMES / f"{game_id}.json"
            if path.exists():
                times.append(path.stat().st_mtime)
        if times:
            mtime_stats[label] = {
                "n_games_with_file": len(times),
                "min": datetime.fromtimestamp(min(times), tz=timezone.utc).isoformat(),
                "median": datetime.fromtimestamp(statistics.median(times), tz=timezone.utc).isoformat(),
                "max": datetime.fromtimestamp(max(times), tz=timezone.utc).isoformat(),
            }

    return {
        "prev_snapshot_path": str(prev_path.relative_to(REPO)) if prev_path else None,
        "current_snapshot_path": str(leaderboard_current_path.relative_to(REPO)),
        "rank_score_deltas_between_two_most_recent_snapshots": deltas,
        "collection_mtime_proxy": {
            "caveat": (
                "local file mtime records when THIS repo collected/downloaded the replay, not "
                "when the game was actually played on CodinGame's servers, and no per-game "
                "historical timestamp or historical arenaScore-at-play-time exists anywhere in "
                "this corpus (confirmed: the embedded per-game players[].arenaScore field is "
                "constant across all 220 resident occurrences at 22.18 -- a value merged in at "
                "corpus-parse time, itself different from both the 07-28 (21.97) and 07-29 "
                "(21.76) leaderboard snapshots used elsewhere in this report -- so it is a third, "
                "frozen-at-parse-time reference point, not a time machine)."
            ),
            "by_agent": mtime_stats,
        },
    }


# ---------------------------------------------------------------------------
# CLI / orchestration
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--jobs", type=int, default=DEFAULT_JOBS)
    parser.add_argument("--limit-per-agent", type=int, default=0, help="0 = every game (smoke-test aid only)")
    args = parser.parse_args()

    leaderboard_path = latest_leaderboard_path()
    leaderboard = load_leaderboard(leaderboard_path)
    all_games = load_games()
    clean_games = [game for game in all_games if is_clean(game)]
    print(f"loaded {len(all_games)} games; clean = {len(clean_games)}; leaderboard = {leaderboard_path}")

    quartet_ids = resolve_quartet(leaderboard)
    print(f"quartet resolved: {quartet_ids}")

    cohort = cohort_table(clean_games, leaderboard, quartet_ids)
    print(
        f"cohort table built; still-STRONG under newest snapshot: "
        f"{cohort['b44_strong_cohort_recomputed_fresh']['quartet_still_in_strong_cohort']}"
    )

    tracked_ids = {RESIDENT_AGENT_ID} | set(quartet_ids.values())
    occ_index = index_agent_occurrences(clean_games, tracked_ids)
    if args.limit_per_agent:
        occ_index = {agent_id: pairs[: args.limit_per_agent] for agent_id, pairs in occ_index.items()}

    resident_rows = build_rows(occ_index[RESIDENT_AGENT_ID], RESIDENT_AGENT_ID, leaderboard)
    quartet_rows_by_pseudo = {
        pseudo: build_rows(occ_index[agent_id], agent_id, leaderboard) for pseudo, agent_id in quartet_ids.items()
    }
    print(
        f"rows built: resident={len(resident_rows)} "
        + " ".join(f"{pseudo}={len(rows)}" for pseudo, rows in quartet_rows_by_pseudo.items())
    )

    opp_roster_lookup: dict[tuple[int, int], int | None] = {}
    for row in resident_rows:
        opp_roster_lookup[(row["game_id"], RESIDENT_AGENT_ID)] = row["opp_roster"]
    for pseudo, rows in quartet_rows_by_pseudo.items():
        agent_id = quartet_ids[pseudo]
        for row in rows:
            opp_roster_lookup[(row["game_id"], agent_id)] = row["opp_roster"]

    matched = {
        "vs3": matched_comparison(resident_rows, quartet_rows_by_pseudo, lambda roster: roster == 3),
        "vs4plus": matched_comparison(resident_rows, quartet_rows_by_pseudo, lambda roster: roster >= 4),
        "vs2_reference_only": {
            "resident": bucket_stats([row for row in resident_rows if row["opp_roster"] == 2]),
            "quartet_pooled": bucket_stats(
                [row for rows in quartet_rows_by_pseudo.values() for row in rows if row["opp_roster"] == 2]
            ),
        },
    }
    print(
        f"matched comparisons done: vs3 resident n={matched['vs3']['n_resident']} "
        f"quartet n={matched['vs3']['n_quartet_pooled']}; "
        f"vs4plus resident n={matched['vs4plus']['n_resident']} quartet n={matched['vs4plus']['n_quartet_pooled']}"
    )

    # ---- heavy passes: D101 + crop_fate_census + raw-event cadence, ALL games (own_roster==2) ----
    def build_tasks(rows: list[dict], pseudo_or_resident: str, agent_id: int, rank) -> list[dict]:
        game_by_id = {game["gameId"]: game for game, _seat in occ_index[agent_id]}
        return [
            {
                "game_id": row["game_id"],
                "game_row": game_by_id[row["game_id"]],
                "agent_id": agent_id,
                "seat": row["seat"],
                "cohort": pseudo_or_resident,
                "rank": rank,
                "pseudo": pseudo_or_resident,
                "n_turns": row["n_turns"],
            }
            for row in rows
        ]

    all_tasks = build_tasks(resident_rows, "resident", RESIDENT_AGENT_ID, leaderboard[RESIDENT_AGENT_ID]["rank"])
    for pseudo, agent_id in quartet_ids.items():
        all_tasks.extend(build_tasks(quartet_rows_by_pseudo[pseudo], pseudo, agent_id, leaderboard[agent_id]["rank"]))
    print(f"total tracked occurrences (own_roster==2): {len(all_tasks)}")

    d101_rows, d101_failures = run_d101_pass(all_tasks, args.jobs)
    print(f"D101 pass done: {len(d101_rows)} ok, {len(d101_failures)} failed")

    fate_rows, fate_failures = run_fate_pass(all_tasks, args.jobs)
    print(f"crop_fate_census pass done: {len(fate_rows)} ok, {len(fate_failures)} failed")

    events_rows, events_failures = run_events_pass(all_tasks, args.jobs)
    print(f"events (cadence) pass done: {len(events_rows)} ok, {len(events_failures)} failed")

    agent_ids_by_label = {"resident": RESIDENT_AGENT_ID, **quartet_ids}
    no_loop = no_loop_revalidation(d101_rows, fate_rows, events_rows, opp_roster_lookup, agent_ids_by_label)
    print(f"no-loop revalidation: {json.dumps(no_loop['verdicts'], indent=1)}")

    spec_rows, spec_failures = run_spec_pass(all_tasks, args.jobs)
    print(f"unit-spec pass done: {len(spec_rows)} ok, {len(spec_failures)} failed")

    # ---- outnumbered-subset-only passes: waste_sweep + tree-size mix ----
    rows_by_label = {"resident": resident_rows, **quartet_rows_by_pseudo}
    outnumbered_rows_by_label = {
        label: [row for row in rows if row["opp_roster"] >= 3] for label, rows in rows_by_label.items()
    }

    waste_sweep_by_label = {}
    for label, agent_id in agent_ids_by_label.items():
        game_ids = sorted({row["game_id"] for row in outnumbered_rows_by_label[label]})
        if not game_ids:
            waste_sweep_by_label[label] = None
            continue
        report = waste_sweep_run(game_ids, jobs=min(args.jobs, 16), agent_id=agent_id)
        waste_sweep_by_label[label] = {
            "games_swept": report["games_decoded_ok"],
            "detectors": {
                name: {
                    "total_episodes": summary["total_episodes"],
                    "games_with_episode": summary["games_with_episode"],
                    "episodes_per_game_mean": summary["episodes_per_game"]["mean"],
                    "total_flagged_turns": summary["total_flagged_turns"],
                }
                for name, summary in report["detectors"].items()
            },
        }
        print(f"waste_sweep done for {label}: {len(game_ids)} outnumbered games")

    chop_size_tasks = [task for task in all_tasks if (opp_roster_lookup.get((task["game_id"], task["agent_id"])) or 0) >= 3]
    chop_size_rows, chop_size_failures = run_chop_size_pass(chop_size_tasks, args.jobs)
    print(f"tree-size-at-felling pass done: {len(chop_size_rows)} ok, {len(chop_size_failures)} failed (outnumbered subset only)")

    concrete = concrete_comparisons(
        agent_ids_by_label,
        rows_by_label,
        outnumbered_rows_by_label,
        occ_index,
        spec_rows,
        d101_rows,
        opp_roster_lookup,
        waste_sweep_by_label,
        chop_size_rows,
    )

    maturity = maturity_discussion(leaderboard, leaderboard_path, quartet_ids)

    report = {
        "schema": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "H3 -- read-only no-loop-quartet field study; no arena writes, no strategy changes, no corpus mutation",
        "resident_agent_id": RESIDENT_AGENT_ID,
        "quartet_agent_ids": quartet_ids,
        "leaderboard_snapshot": str(leaderboard_path.relative_to(REPO)),
        "corpus": {"n_games_total": len(all_games), "n_games_clean": len(clean_games)},
        "cohort": cohort,
        "matched_comparison_2v3_and_2v4plus": matched,
        "no_loop_revalidation": no_loop,
        "concrete_comparisons": concrete,
        "maturity_and_pool_discussion": maturity,
        "failures": {
            "d101": d101_failures[:50],
            "fate": fate_failures[:50],
            "events": events_failures[:50],
            "spec": spec_failures[:50],
            "chop_size": chop_size_failures[:50],
        },
        "tunables": {"min_cell_n": MIN_CELL_N, "jobs": args.jobs, "limit_per_agent": args.limit_per_agent},
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=1) + "\n")
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
