#!/usr/bin/env python3
"""B4.3 -- price the scaling direction from field data (read-only research scout).

Read-only diagnostic: it never touches the arena, never edits corpus data, and never
proposes strategy changes. It answers one question -- what is a larger final roster
(workforce size) actually worth on the real Legend ladder, in ladder-margin terms, and
with what uncertainty -- by mining the local replay corpus (``data/processed/games.jsonl``
plus ``data/raw/games/*.json`` for the small subset of fields not already indexed).

Roster size is exact and cheap: workers never die (project-standing fact, reconfirmed by
the 2026-07-28 comparative-baseline study), so an agent's final roster in a game is
``1 + (successful TRAINs that game)``. ``data/processed/games.jsonl``'s
``per_player.<seat>.effects.trained`` already counts successful trains (referee-confirmed
"trained a troll" summary lines, via ``data/scripts/parse.py``) -- this is NOT the same as
counting issued ``TRAIN`` commands (``per_player.<seat>.trains``), which includes commands
that failed their affordability/occupied-shack precondition; spot-checking 1,000 (game,
seat) pairs found issued-vs-succeeded mismatches in 5% of them, so this script always uses
``effects.trained``, never ``len(trains)``.

Five analyses, each a function below, matching the B4.3 brief:

1. ``field_roster_distribution`` -- histogram of final roster across the corpus; roster by
   leaderboard rank band; correlation of an agent's mean roster with its rank/score.
2. ``head_to_head_asymmetry`` -- the core natural experiment: games where the two sides'
   final rosters differ, margin as a function of the roster difference, PLUS three
   confound treatments: (a) raw/naive, (b) restricted to leaderboard-score-matched
   opponent pairs, (c) a within-agent fixed-effect estimate (does an agent's own margin
   still track its own roster edge, across its own games, holding its own policy/skill
   fixed?).
3. ``timing_analysis`` -- does an early 2nd/3rd/4th worker predict a better margin,
   conditional on eventually reaching (or exactly stopping at) that roster level?
4. ``resident_counterpart`` -- the resident's own 205 games, split by opponent roster
   (2 / 3 / 4+), its most decision-relevant number: how much of its deficit owes to
   facing bigger armies.
5. ``diminishing_returns`` -- per-transition marginal price (2->3, 3->4, 4->5, ...) from
   games whose two final rosters are adjacent integers.

Plus a rating-points bridge: an OLS fit of margin ~ leaderboard-arenaScore-difference
across the corpus, used to translate a margin price into ladder rating points.

CLI usage::

    .venv/bin/python cgauto/roster_outcome_pricing.py --output <path/to/report.json>

All thresholds (crash-score sentinel, min games for fixed effects, similar-skill bands,
bootstrap size) are module constants, listed in the "tunables" section below.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import statistics
import sys

import numpy as np

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.recent_resident_field_census import successful_events

REPO = Path(__file__).resolve().parent.parent
GAMES_INDEX = REPO / "data/processed/games.jsonl"
RAW_GAMES = REPO / "data/raw/games"
SNAPSHOTS_DIR = REPO / "data/raw/snapshots"
SCRATCH_DIR = Path(
    "/tmp/claude-1001/-home-tarstars-prj-troll-farm/b87b2a84-2e59-408b-9c9e-ecb58289a6d1/scratchpad"
)
DEFAULT_OUTPUT = SCRATCH_DIR / "b43-roster-outcome-pricing-data.json"

RESIDENT_AGENT_ID = 6561795

# ---------------------------------------------------------------------------
# Tunables -- module constants, not results.  Changing these changes what the
# analysis measures; they are not fit to the data.
# ---------------------------------------------------------------------------
CRASH_SCORE_THRESHOLD = 0.0  # any score < 0 is the CG crash/timeout sentinel (-2.0 observed)
MIN_AGENT_GAMES_FOR_FE = 10  # within-agent fixed-effect: minimum own clean games to include
MIN_BUCKET_GAMES_FOR_CONTRAST = 5  # min games in EACH of out-rostered/under-rostered
SIMILAR_SKILL_THRESHOLDS = (2.0, 4.0)  # arenaScore-point bands counted as "similar skill"
N_BOOT = 4000
BOOT_SEED = 20260728
ROSTER_DIFFS_REPORTED = (1, 2, 3)  # the brief's requested +1/+2/+3; 4+ reported as footnote
ADJACENT_TRANSITIONS = ((2, 3), (3, 4), (4, 5), (5, 6))  # marginal-value ladder rungs
TIMING_LEVELS = (2, 3, 4)


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


def load_games() -> list[dict]:
    with GAMES_INDEX.open() as handle:
        return [json.loads(line) for line in handle if line.strip()]


def latest_leaderboard_path() -> Path:
    """Newest dated snapshot directory under data/raw/snapshots (lexicographic ==
    chronological, since directory names are ISO-timestamp-prefixed)."""

    candidates = sorted(
        path for path in SNAPSHOTS_DIR.iterdir() if path.is_dir() and (path / "leaderboard.json").exists()
    )
    if not candidates:
        raise FileNotFoundError(f"no leaderboard snapshot found under {SNAPSHOTS_DIR}")
    return candidates[-1] / "leaderboard.json"


def load_leaderboard(path: Path) -> dict[int, dict]:
    """agentId -> {pseudo, score, division_index, rank}.  ``rank`` is confirmed (by direct
    lookup of the resident and the STATE.md-cited top-3) to be a single GLOBAL rank across
    the whole ladder, with Legend (division_index 5) occupying ranks 1..len(Legend) and
    Gold (division_index 4) continuing immediately after -- so "rank <= 5" and "6 <= rank
    <= 20" are exactly the project's established "top-5" / "ranks 6-20" cohorts without
    any extra division filter."""

    data = json.loads(path.read_text())
    out: dict[int, dict] = {}
    for user in data["users"]:
        league = user.get("league") or {}
        out[user["agentId"]] = {
            "pseudo": user.get("pseudo"),
            "score": user.get("score"),
            "division_index": league.get("divisionIndex"),
            "rank": user.get("rank"),
        }
    return out


def is_clean(game: dict) -> bool:
    """Exclude built-in-boss games and crash/timeout games (score < 0 -- the scoring
    formula sum(fruit)+4*wood can never be negative under normal play; -2.0 is the only
    negative value observed in the corpus, in 26/8,131 games, CG's crash/timeout
    sentinel).  Both are technical-failure classes, not genuine economic outcomes, and
    would spuriously correlate small-roster-because-crashed with large-negative-margin-
    because-crashed if left in."""

    if any(player.get("isBoss") for player in game["players"]):
        return False
    scores = game.get("scores") or [0, 0]
    if min(scores) < CRASH_SCORE_THRESHOLD:
        return False
    return True


def roster_of(game: dict, seat: int) -> int:
    effects = game["per_player"][str(seat)].get("effects", {})
    return 1 + int(effects.get("trained", 0))


def margin_of(game: dict, seat: int) -> float:
    scores = game["scores"]
    return float(scores[seat]) - float(scores[1 - seat])


def won_of(game: dict, seat: int) -> bool:
    """Matches cgauto/waste_sweep.py's DecodedGame.won convention exactly (rank==0 AND
    margin>0 -- the AND matters only for the rare tied-score game, where CG still
    resolves a rank-0 winner via a hidden tiebreak; under this convention neither side
    counts as "won" a margin=0 game, which is the conservative/consistent reading)."""

    ranks = game.get("ranks") or []
    if len(ranks) != 2:
        return False
    return ranks[seat] == 0 and margin_of(game, seat) > 0


# ---------------------------------------------------------------------------
# Stats helpers
# ---------------------------------------------------------------------------


def mean_sd_n(values) -> dict:
    arr = np.asarray(list(values), dtype=float)
    if arr.size == 0:
        return {"mean": None, "median": None, "sd": None, "n": 0}
    return {
        "mean": float(arr.mean()),
        "median": float(np.median(arr)),
        "sd": float(arr.std(ddof=1)) if arr.size > 1 else 0.0,
        "n": int(arr.size),
    }


def bootstrap_mean_ci(values, n_boot: int = N_BOOT, seed: int = BOOT_SEED) -> dict:
    arr = np.asarray(list(values), dtype=float)
    if arr.size == 0:
        return {"mean": None, "ci_lo": None, "ci_hi": None, "n": 0}
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, arr.size, size=(n_boot, arr.size))
    boots = arr[idx].mean(axis=1)
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return {"mean": float(arr.mean()), "ci_lo": float(lo), "ci_hi": float(hi), "n": int(arr.size)}


def bootstrap_diff_ci(a, b, n_boot: int = N_BOOT, seed: int = BOOT_SEED) -> dict:
    """Bootstrap CI for mean(a) - mean(b), independent resampling of each group."""

    arr_a = np.asarray(list(a), dtype=float)
    arr_b = np.asarray(list(b), dtype=float)
    if arr_a.size == 0 or arr_b.size == 0:
        return {"diff": None, "ci_lo": None, "ci_hi": None, "n_a": int(arr_a.size), "n_b": int(arr_b.size)}
    rng = np.random.default_rng(seed)
    idx_a = rng.integers(0, arr_a.size, size=(n_boot, arr_a.size))
    idx_b = rng.integers(0, arr_b.size, size=(n_boot, arr_b.size))
    boots = arr_a[idx_a].mean(axis=1) - arr_b[idx_b].mean(axis=1)
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return {
        "diff": float(arr_a.mean() - arr_b.mean()),
        "ci_lo": float(lo),
        "ci_hi": float(hi),
        "n_a": int(arr_a.size),
        "n_b": int(arr_b.size),
    }


def win_rate_ci(wins: int, n: int) -> dict:
    if n == 0:
        return {"rate": None, "ci_lo": None, "ci_hi": None, "n": 0}
    p = wins / n
    se = math.sqrt(p * (1 - p) / n) if 0 < p < 1 else 0.0
    return {"rate": p, "ci_lo": max(0.0, p - 1.96 * se), "ci_hi": min(1.0, p + 1.96 * se), "n": n}


def pearson(x, y) -> float | None:
    arr_x = np.asarray(list(x), dtype=float)
    arr_y = np.asarray(list(y), dtype=float)
    if arr_x.size < 3 or arr_x.std() == 0 or arr_y.std() == 0:
        return None
    return float(np.corrcoef(arr_x, arr_y)[0, 1])


def ols_with_intercept(x, y) -> dict:
    arr_x = np.asarray(list(x), dtype=float)
    arr_y = np.asarray(list(y), dtype=float)
    n = arr_x.size
    if n < 3:
        return {"alpha": None, "beta": None, "r2": None, "se_beta": None, "n": n}
    xbar, ybar = arr_x.mean(), arr_y.mean()
    sxx = float(np.sum((arr_x - xbar) ** 2))
    sxy = float(np.sum((arr_x - xbar) * (arr_y - ybar)))
    beta = sxy / sxx if sxx > 0 else None
    alpha = (ybar - beta * xbar) if beta is not None else None
    if beta is None:
        return {"alpha": None, "beta": None, "r2": None, "se_beta": None, "n": n}
    yhat = alpha + beta * arr_x
    ss_res = float(np.sum((arr_y - yhat) ** 2))
    ss_tot = float(np.sum((arr_y - ybar) ** 2))
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else None
    se_beta = math.sqrt((ss_res / (n - 2)) / sxx) if n > 2 and sxx > 0 else None
    return {"alpha": alpha, "beta": beta, "r2": r2, "se_beta": se_beta, "n": n}


# ---------------------------------------------------------------------------
# Part 1: field roster distribution
# ---------------------------------------------------------------------------


def field_roster_distribution(clean_games: list[dict], leaderboard: dict[int, dict]) -> dict:
    all_rosters = []
    per_agent_rosters: dict[int, list[int]] = defaultdict(list)
    for game in clean_games:
        for player in game["players"]:
            seat = player["index"]
            roster = roster_of(game, seat)
            all_rosters.append(roster)
            per_agent_rosters[player["agentId"]].append(roster)

    histogram = dict(sorted(Counter(all_rosters).items()))

    # Rank bands, pooled across games (matches the established resident/top-5/ranks6-20
    # methodology exactly -- validated byte-for-byte against docs/CONSTRAINTS.md's
    # "resident 2.00, top-5 3.55, ranks 6-20 2.50" during development).
    def band_stats(agent_ids: set[int]) -> dict:
        pooled = [roster for agent_id in agent_ids for roster in per_agent_rosters.get(agent_id, [])]
        return {**mean_sd_n(pooled), "n_agents": len(agent_ids)}

    legend_agents = sorted(
        (agent_id for agent_id, info in leaderboard.items() if info["division_index"] == 5),
        key=lambda agent_id: leaderboard[agent_id]["rank"],
    )
    corpus_agent_ids = set(per_agent_rosters)
    legend_in_corpus = [agent_id for agent_id in legend_agents if agent_id in corpus_agent_ids]

    bands = {
        "resident": band_stats({RESIDENT_AGENT_ID}),
        "top-5 (rank 1-5)": band_stats({a for a in legend_in_corpus if leaderboard[a]["rank"] <= 5}),
        "ranks 6-20": band_stats({a for a in legend_in_corpus if 6 <= leaderboard[a]["rank"] <= 20}),
        "ranks 21-50": band_stats({a for a in legend_in_corpus if 21 <= leaderboard[a]["rank"] <= 50}),
        "ranks 51+ (rest of Legend)": band_stats({a for a in legend_in_corpus if leaderboard[a]["rank"] > 50}),
        "Gold division (below Legend)": band_stats(
            {a for a in corpus_agent_ids if leaderboard.get(a, {}).get("division_index") == 4}
        ),
        "not in newest top-1000 snapshot": band_stats(
            {a for a in corpus_agent_ids if a not in leaderboard}
        ),
    }

    # Agent-level correlation: does a covered agent's mean roster track its rank/score?
    covered = [agent_id for agent_id in corpus_agent_ids if agent_id in leaderboard]
    agent_mean_roster = [statistics.mean(per_agent_rosters[agent_id]) for agent_id in covered]
    agent_rank = [leaderboard[agent_id]["rank"] for agent_id in covered]
    agent_score = [leaderboard[agent_id]["score"] for agent_id in covered]

    # Same-scale peers: agents whose mean final roster is ~2.0 (the resident's own
    # figure), regardless of rank -- directly tests whether a small roster is a hard
    # ceiling on rank, or whether higher-ranked agents also run small rosters (in which
    # case roster size is not the sole or even primary determinant of ladder position).
    resident_roster_mean = statistics.mean(per_agent_rosters[RESIDENT_AGENT_ID])
    same_scale_peers = [
        {
            "agent_id": agent_id,
            "pseudo": leaderboard[agent_id]["pseudo"],
            "rank": leaderboard[agent_id]["rank"],
            "score": leaderboard[agent_id]["score"],
            "mean_roster": statistics.mean(per_agent_rosters[agent_id]),
            "n_games": len(per_agent_rosters[agent_id]),
        }
        for agent_id in covered
        if agent_id != RESIDENT_AGENT_ID
        and leaderboard[agent_id]["division_index"] == 5
        and abs(statistics.mean(per_agent_rosters[agent_id]) - resident_roster_mean) <= 0.2
        and len(per_agent_rosters[agent_id]) >= 10
    ]
    same_scale_peers.sort(key=lambda row: row["rank"])

    return {
        "n_games": len(clean_games),
        "n_agent_seats": len(all_rosters),
        "n_unique_agents": len(per_agent_rosters),
        "histogram": histogram,
        "rank_bands": bands,
        "agent_level_correlation": {
            "n_agents_covered": len(covered),
            "pearson_rank_vs_mean_roster": pearson(agent_rank, agent_mean_roster),
            "pearson_arenaScore_vs_mean_roster": pearson(agent_score, agent_mean_roster),
        },
        "same_scale_peers": {
            "resident_mean_roster": resident_roster_mean,
            "band_halfwidth": 0.2,
            "min_games": 10,
            "n_peers_in_legend": len(same_scale_peers),
            "peers": same_scale_peers[:15],
        },
    }


# ---------------------------------------------------------------------------
# Part 2: head-to-head roster asymmetry (the core natural experiment)
# ---------------------------------------------------------------------------


def head_to_head_asymmetry(clean_games: list[dict], leaderboard: dict[int, dict]) -> dict:
    # One row per asymmetric game: (diff, margin_of_bigger_side, won_of_bigger_side,
    # arena_score_diff_if_both_covered).
    rows = []
    for game in clean_games:
        p0, p1 = game["players"]
        ros0, ros1 = roster_of(game, 0), roster_of(game, 1)
        if ros0 == ros1:
            continue
        bigger_seat = 0 if ros0 > ros1 else 1
        smaller_seat = 1 - bigger_seat
        diff = roster_of(game, bigger_seat) - roster_of(game, smaller_seat)
        margin = margin_of(game, bigger_seat)
        won = won_of(game, bigger_seat)
        bigger_agent = game["players"][bigger_seat]["agentId"]
        smaller_agent = game["players"][smaller_seat]["agentId"]
        score_diff = None
        if bigger_agent in leaderboard and smaller_agent in leaderboard:
            score_diff = leaderboard[bigger_agent]["score"] - leaderboard[smaller_agent]["score"]
        rows.append(
            {
                "diff": diff,
                "margin": margin,
                "won": won,
                "score_diff": score_diff,
                "bigger_agent": bigger_agent,
                "smaller_agent": smaller_agent,
            }
        )

    def bucket_table(row_subset) -> dict:
        table = {}
        for diff in sorted({row["diff"] for row in row_subset}):
            bucket = [row for row in row_subset if row["diff"] == diff]
            margins = [row["margin"] for row in bucket]
            wins = sum(row["won"] for row in bucket)
            table[str(diff)] = {
                "margin": bootstrap_mean_ci(margins),
                "win_rate": win_rate_ci(wins, len(bucket)),
                "n": len(bucket),
            }
        return table

    naive_table = bucket_table(rows)

    # Confound quantification: does the bigger-roster side also tend to be the
    # higher-rated side, and by how much?
    covered_rows = [row for row in rows if row["score_diff"] is not None]
    confound = {
        "n_both_covered": len(covered_rows),
        "n_total_asymmetric": len(rows),
        "mean_score_diff_of_bigger_side": mean_sd_n([row["score_diff"] for row in covered_rows]),
        "pearson_diff_vs_score_diff": pearson(
            [row["diff"] for row in covered_rows], [row["score_diff"] for row in covered_rows]
        ),
        "by_diff_bucket": {
            str(diff): mean_sd_n([row["score_diff"] for row in covered_rows if row["diff"] == diff])
            for diff in sorted({row["diff"] for row in covered_rows})
        },
    }

    similar_skill_tables = {}
    for threshold in SIMILAR_SKILL_THRESHOLDS:
        subset = [row for row in covered_rows if abs(row["score_diff"]) <= threshold]
        similar_skill_tables[str(threshold)] = {"n_total": len(subset), "table": bucket_table(subset)}

    # Within-agent fixed effect: for every agent with enough of its OWN games, does its
    # own margin track its own roster edge across its own games, holding its identity
    # (hence its own policy quality) fixed?  Two views: (a) a simple out-rostered vs
    # under-rostered per-agent contrast; (b) a pooled within-agent (demeaned) regression
    # slope, agent-clustered bootstrap CI.
    agent_games: dict[int, list[dict]] = defaultdict(list)
    for game in clean_games:
        for player in game["players"]:
            seat = player["index"]
            opp_seat = 1 - seat
            agent_games[player["agentId"]].append(
                {
                    "roster_diff": roster_of(game, seat) - roster_of(game, opp_seat),
                    "margin": margin_of(game, seat),
                }
            )

    contrasts = []
    dr_by_agent: dict[int, np.ndarray] = {}
    dm_by_agent: dict[int, np.ndarray] = {}
    for agent_id, own_rows in agent_games.items():
        if len(own_rows) < MIN_AGENT_GAMES_FOR_FE:
            continue
        diffs = np.array([row["roster_diff"] for row in own_rows], dtype=float)
        margins = np.array([row["margin"] for row in own_rows], dtype=float)
        dr_by_agent[agent_id] = diffs - diffs.mean()
        dm_by_agent[agent_id] = margins - margins.mean()

        out_margins = margins[diffs > 0]
        under_margins = margins[diffs < 0]
        if len(out_margins) >= MIN_BUCKET_GAMES_FOR_CONTRAST and len(under_margins) >= MIN_BUCKET_GAMES_FOR_CONTRAST:
            contrasts.append(
                {
                    "agent_id": agent_id,
                    "n_out": int(len(out_margins)),
                    "n_under": int(len(under_margins)),
                    "mean_margin_out_rostered": float(out_margins.mean()),
                    "mean_margin_under_rostered": float(under_margins.mean()),
                    "contrast": float(out_margins.mean() - under_margins.mean()),
                }
            )

    contrast_values = [row["contrast"] for row in contrasts]
    simple_contrast_summary = {
        "n_qualifying_agents": len(contrasts),
        "min_games_threshold": MIN_AGENT_GAMES_FOR_FE,
        "min_bucket_threshold": MIN_BUCKET_GAMES_FOR_CONTRAST,
        "contrast_stats": bootstrap_mean_ci(contrast_values) if contrast_values else None,
        "n_agents_positive_contrast": sum(1 for v in contrast_values if v > 0),
        "n_agents_negative_contrast": sum(1 for v in contrast_values if v < 0),
    }

    fe_agent_ids = sorted(dr_by_agent)
    all_dr = np.concatenate([dr_by_agent[a] for a in fe_agent_ids]) if fe_agent_ids else np.array([])
    all_dm = np.concatenate([dm_by_agent[a] for a in fe_agent_ids]) if fe_agent_ids else np.array([])
    denom = float(np.sum(all_dr * all_dr)) if all_dr.size else 0.0
    pooled_slope = float(np.sum(all_dr * all_dm) / denom) if denom > 0 else None

    slope_ci = {"ci_lo": None, "ci_hi": None}
    if fe_agent_ids and pooled_slope is not None:
        rng = np.random.default_rng(BOOT_SEED)
        agent_array = np.array(fe_agent_ids)
        boot_slopes = []
        for _ in range(N_BOOT):
            chosen = rng.choice(agent_array, size=len(agent_array), replace=True)
            dr_all = np.concatenate([dr_by_agent[a] for a in chosen])
            dm_all = np.concatenate([dm_by_agent[a] for a in chosen])
            d = float(np.sum(dr_all * dr_all))
            if d > 0:
                boot_slopes.append(float(np.sum(dr_all * dm_all) / d))
        if boot_slopes:
            lo, hi = np.percentile(boot_slopes, [2.5, 97.5])
            slope_ci = {"ci_lo": float(lo), "ci_hi": float(hi)}

    within_agent_regression = {
        "n_qualifying_agents": len(fe_agent_ids),
        "n_games_pooled": int(all_dr.size),
        "slope_margin_per_roster_unit": pooled_slope,
        **slope_ci,
    }

    return {
        "n_asymmetric_games": len(rows),
        "n_symmetric_games_excluded": len(clean_games) - len(rows),
        "naive_pooled_table": naive_table,
        "confound": confound,
        "similar_skill_restricted_tables": similar_skill_tables,
        "within_agent_simple_contrast": simple_contrast_summary,
        "within_agent_pooled_regression": within_agent_regression,
    }


# ---------------------------------------------------------------------------
# Part 3: timing -- early vs late Nth worker
# ---------------------------------------------------------------------------


def _extract_train_turns(game_id: int) -> tuple[int, list[int] | None, list[int] | None, str | None]:
    try:
        game = json.loads((RAW_GAMES / f"{game_id}.json").read_text())
        events = successful_events(game["frames"])
        turns0 = sorted(event["turn"] for event in events[0] if event["kind"] == "TRAIN")
        turns1 = sorted(event["turn"] for event in events[1] if event["kind"] == "TRAIN")
        return game_id, turns0, turns1, None
    except Exception as exc:  # noqa: BLE001 -- keep a complete audit, one bad game shouldn't abort the sweep
        return game_id, None, None, f"{type(exc).__name__}: {exc}"


def extract_all_train_turns(game_ids: list[int], jobs: int) -> tuple[dict[int, tuple[list[int], list[int]]], list[dict]]:
    turns_by_game: dict[int, tuple[list[int], list[int]]] = {}
    failures = []
    if jobs <= 1:
        results = [_extract_train_turns(game_id) for game_id in game_ids]
    else:
        with ProcessPoolExecutor(max_workers=jobs) as executor:
            results = list(executor.map(_extract_train_turns, game_ids, chunksize=8))
    for game_id, turns0, turns1, error in results:
        if error is not None:
            failures.append({"game_id": game_id, "error": error})
            continue
        turns_by_game[game_id] = (turns0, turns1)
    return turns_by_game, failures


def timing_analysis(clean_games: list[dict], turns_by_game: dict[int, tuple[list[int], list[int]]]) -> dict:
    integrity_mismatches = 0
    seat_rows = []
    for game in clean_games:
        turns = turns_by_game.get(game["gameId"])
        if turns is None:
            continue
        for seat in (0, 1):
            train_turns = turns[seat]
            roster = roster_of(game, seat)
            if len(train_turns) != roster - 1:
                integrity_mismatches += 1
                continue
            seat_rows.append(
                {
                    "final_roster": roster,
                    "margin": margin_of(game, seat),
                    "train_turns": train_turns,
                }
            )

    def level_analysis(level: int) -> dict:
        def turn_reaches(row) -> int:
            return row["train_turns"][level - 2]  # (level-1)-th successful TRAIN, 1-indexed -> [level-2]

        at_least = [row for row in seat_rows if row["final_roster"] >= level]
        exactly = [row for row in seat_rows if row["final_roster"] == level]

        def summarize(subset) -> dict:
            if len(subset) < 10:
                return {"n": len(subset), "note": "too few games for a stable readout"}
            turn_values = [turn_reaches(row) for row in subset]
            margins = [row["margin"] for row in subset]
            median_turn = statistics.median(turn_values)
            early = [row["margin"] for row in subset if turn_reaches(row) <= median_turn]
            late = [row["margin"] for row in subset if turn_reaches(row) > median_turn]
            return {
                "n": len(subset),
                "median_turn_reached": median_turn,
                "pearson_turn_vs_margin": pearson(turn_values, margins),
                "early_half_mean_margin": mean_sd_n(early),
                "late_half_mean_margin": mean_sd_n(late),
                "early_minus_late": bootstrap_diff_ci(early, late),
            }

        return {"at_least_this_roster": summarize(at_least), "exactly_this_roster": summarize(exactly)}

    return {
        "n_games_with_train_turns": len(turns_by_game),
        "n_seat_rows_used": len(seat_rows),
        "integrity_mismatches_excluded": integrity_mismatches,
        "by_level": {str(level): level_analysis(level) for level in TIMING_LEVELS},
    }


# ---------------------------------------------------------------------------
# Part 4: the resident's counterpart
# ---------------------------------------------------------------------------


def resident_counterpart(clean_games: list[dict]) -> dict:
    resident_rows = []
    for game in clean_games:
        agent_ids = [player["agentId"] for player in game["players"]]
        if RESIDENT_AGENT_ID not in agent_ids:
            continue
        seat = next(player["index"] for player in game["players"] if player["agentId"] == RESIDENT_AGENT_ID)
        opp_seat = 1 - seat
        resident_rows.append(
            {
                "opp_roster": roster_of(game, opp_seat),
                "margin": margin_of(game, seat),
                "won": won_of(game, seat),
            }
        )

    def bucket(predicate) -> dict:
        subset = [row for row in resident_rows if predicate(row["opp_roster"])]
        wins = sum(row["won"] for row in subset)
        return {
            "n": len(subset),
            "margin": bootstrap_mean_ci([row["margin"] for row in subset]),
            "win_rate": win_rate_ci(wins, len(subset)),
        }

    all_wins = sum(row["won"] for row in resident_rows)
    return {
        "n_resident_games": len(resident_rows),
        "overall": {
            "n": len(resident_rows),
            "margin": bootstrap_mean_ci([row["margin"] for row in resident_rows]),
            "win_rate": win_rate_ci(all_wins, len(resident_rows)),
        },
        "vs_1_worker": bucket(lambda r: r == 1),
        "vs_2_worker": bucket(lambda r: r == 2),
        "vs_3_worker": bucket(lambda r: r == 3),
        "vs_4plus_worker": bucket(lambda r: r >= 4),
        "opponent_roster_histogram": dict(sorted(Counter(row["opp_roster"] for row in resident_rows).items())),
    }


# ---------------------------------------------------------------------------
# Part 5: diminishing returns -- per-transition marginal price
# ---------------------------------------------------------------------------


def diminishing_returns(clean_games: list[dict]) -> dict:
    by_transition: dict[tuple[int, int], list[dict]] = defaultdict(list)
    for game in clean_games:
        ros0, ros1 = roster_of(game, 0), roster_of(game, 1)
        lo, hi = min(ros0, ros1), max(ros0, ros1)
        if hi - lo != 1:
            continue
        if (lo, hi) not in ADJACENT_TRANSITIONS:
            continue
        bigger_seat = 0 if ros0 > ros1 else 1
        by_transition[(lo, hi)].append(
            {"margin": margin_of(game, bigger_seat), "won": won_of(game, bigger_seat)}
        )

    table = {}
    for lo, hi in ADJACENT_TRANSITIONS:
        rows = by_transition.get((lo, hi), [])
        wins = sum(row["won"] for row in rows)
        table[f"{lo}->{hi}"] = {
            "n": len(rows),
            "margin": bootstrap_mean_ci([row["margin"] for row in rows]) if rows else None,
            "win_rate": win_rate_ci(wins, len(rows)),
        }

    # Increment-over-increment: is the 3->4 price smaller than the 2->3 price, etc.?
    prices = {key: value["margin"]["mean"] if value["margin"] else None for key, value in table.items()}
    return {"transition_table": table, "marginal_prices": prices}


# ---------------------------------------------------------------------------
# Rating-points bridge
# ---------------------------------------------------------------------------


def rating_points_bridge(clean_games: list[dict], leaderboard: dict[int, dict]) -> dict:
    margins = []
    score_diffs = []
    for game in clean_games:
        p0, p1 = game["players"]
        if p0["agentId"] not in leaderboard or p1["agentId"] not in leaderboard:
            continue
        score_diff = leaderboard[p0["agentId"]]["score"] - leaderboard[p1["agentId"]]["score"]
        margins.append(margin_of(game, 0))
        score_diffs.append(score_diff)

    fit = ols_with_intercept(score_diffs, margins)

    # Win-rate-by-margin-bucket, as an intuitive independent cross-check of what a given
    # margin "buys" in outcome terms.
    win_by_margin_bucket = {}
    all_rows = []
    for game in clean_games:
        all_rows.append({"margin": margin_of(game, 0), "won": won_of(game, 0)})
        all_rows.append({"margin": margin_of(game, 1), "won": won_of(game, 1)})
    edges = [-400, -100, -50, -20, -5, 0, 5, 20, 50, 100, 400]
    for lo, hi in zip(edges[:-1], edges[1:]):
        subset = [row for row in all_rows if lo <= row["margin"] < hi]
        wins = sum(row["won"] for row in subset)
        win_by_margin_bucket[f"[{lo},{hi})"] = win_rate_ci(wins, len(subset))

    return {
        "n_games_both_covered": len(margins),
        "margin_on_arenaScore_diff_ols": fit,
        "win_rate_by_margin_bucket": win_by_margin_bucket,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--leaderboard", type=Path, default=None, help="override the auto-discovered newest snapshot")
    parser.add_argument("--jobs", type=int, default=12, help="workers for the raw-JSON TRAIN-turn extraction pass")
    args = parser.parse_args()

    leaderboard_path = args.leaderboard or latest_leaderboard_path()
    leaderboard = load_leaderboard(leaderboard_path)

    all_games = load_games()
    clean_games = [game for game in all_games if is_clean(game)]
    excluded_boss = sum(1 for game in all_games if any(p.get("isBoss") for p in game["players"]))
    excluded_crash = sum(
        1 for game in all_games if not any(p.get("isBoss") for p in game["players"]) and min(game["scores"]) < 0
    )

    print(f"loaded {len(all_games)} games; clean = {len(clean_games)} "
          f"(excluded {excluded_boss} boss, {excluded_crash} crash/timeout)")

    part1 = field_roster_distribution(clean_games, leaderboard)
    print(f"part 1 done: {part1['n_unique_agents']} agents, roster histogram {part1['histogram']}")

    part2 = head_to_head_asymmetry(clean_games, leaderboard)
    print(f"part 2 done: {part2['n_asymmetric_games']} asymmetric games; "
          f"within-agent slope = {part2['within_agent_pooled_regression']['slope_margin_per_roster_unit']}")

    game_ids = [game["gameId"] for game in clean_games]
    turns_by_game, train_turn_failures = extract_all_train_turns(game_ids, jobs=args.jobs)
    print(f"train-turn extraction: {len(turns_by_game)}/{len(game_ids)} ok, "
          f"{len(train_turn_failures)} failures")

    part3 = timing_analysis(clean_games, turns_by_game)
    print(f"part 3 done: {part3['n_seat_rows_used']} seat-rows usable")

    part4 = resident_counterpart(clean_games)
    print(f"part 4 done: resident {part4['n_resident_games']} games")

    part5 = diminishing_returns(clean_games)
    print(f"part 5 done: transitions {list(part5['transition_table'].keys())}")

    bridge = rating_points_bridge(clean_games, leaderboard)
    print(f"rating bridge done: beta = {bridge['margin_on_arenaScore_diff_ols']['beta']}")

    report = {
        "schema": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": (
            "read-only field-data pricing study (B4.3): no arena writes, no strategy "
            "changes, no corpus mutation"
        ),
        "resident_agent_id": RESIDENT_AGENT_ID,
        "leaderboard_snapshot": str(leaderboard_path.relative_to(REPO)),
        "corpus": {
            "n_games_total": len(all_games),
            "n_games_clean": len(clean_games),
            "n_excluded_boss": excluded_boss,
            "n_excluded_crash_timeout": excluded_crash,
        },
        "train_turn_extraction_failures": train_turn_failures[:50],
        "part1_field_roster_distribution": part1,
        "part2_head_to_head_asymmetry": part2,
        "part3_timing_analysis": part3,
        "part4_resident_counterpart": part4,
        "part5_diminishing_returns": part5,
        "rating_points_bridge": bridge,
        "tunables": {
            "crash_score_threshold": CRASH_SCORE_THRESHOLD,
            "min_agent_games_for_fe": MIN_AGENT_GAMES_FOR_FE,
            "min_bucket_games_for_contrast": MIN_BUCKET_GAMES_FOR_CONTRAST,
            "similar_skill_thresholds": SIMILAR_SKILL_THRESHOLDS,
            "n_boot": N_BOOT,
            "boot_seed": BOOT_SEED,
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=1) + "\n")
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
