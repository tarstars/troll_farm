#!/usr/bin/env python3
"""Processed-corpus-only first table for Track T-1.

This deliberately reads only data/processed/games.jsonl.  The fixed cohort is the
25-agent, anchor-matching N2 reconstruction; its historical ranks are provenance,
not a claim about the current ladder.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import statistics

FRUITS = ("PLUM", "LEMON", "APPLE", "BANANA")
CORPUS_SHA256 = "150a5507e90c2c00a5d22b34abf19b7a0ad933fc3b31e3abf3521d3bc4dc4d24"
COHORT = (
    (6480541, "yaichi", 7), (6491563, "Stounate", 8),
    (6480520, "skotz", 10), (6483545, "Escdemon", 11),
    (6559862, "therealbeef", 12), (6479814, "yamo", 15),
    (6479779, "putibuzu", 16), (6479420, "Risen", 17),
    (6479657, "Konstant", 24), (6520935, "goq", 29),
    (6480943, "Dridriun", 36), (6479750, "mehdi_ayari", 38),
    (6481252, "DaNinja", 46), (6541379, "GoodDevel", 50),
    (6483491, "VINCE_MX", 54), (6480951, "0x6E0FF", 57),
    (6479388, "Kheopsian", 58), (6541416, "Ticasali", 63),
    (6479931, "abdelmathin", 73), (6488436, "NOIIICE", 75),
    (6505289, "tonigineer", 94), (6481094, "Shun_PI", 95),
    (6488432, "anuragm", 97), (6499915, "LeRenard", 101),
    (6535596, "FRHT", 104),
)


def mean(values: list[float]) -> float:
    return statistics.mean(values) if values else 0.0


def load(path: Path) -> list[dict]:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != CORPUS_SHA256:
        raise SystemExit(f"corpus hash mismatch: {digest}")
    with path.open() as source:
        games = [json.loads(line) for line in source]
    if len(games) != 23613:
        raise SystemExit(f"corpus row-count mismatch: {len(games)}")
    return games


def side_row(game: dict, seat: int) -> dict:
    pp = game["per_player"][str(seat)]
    inv = pp.get("final_inv") or [0] * 6
    plants = pp.get("planted_ok") or {}
    curve = pp.get("score_curve") or []
    return {
        "score": game["scores"][seat],
        "fruit_points": sum(inv[:4]),
        "wood_points": 4 * inv[5],
        "plants": {fruit: plants.get(fruit, 0) for fruit in FRUITS},
        "second_train_turn": (pp.get("trains") or [[None]])[0][0],
        "third_trained": len(pp.get("trains") or []) >= 2,
        "score_curve": curve,
    }


def summarize(rows: list[dict]) -> dict:
    return {
        "games": len(rows),
        "score": mean([r["score"] for r in rows]),
        "fruit_points": mean([r["fruit_points"] for r in rows]),
        "wood_points": mean([r["wood_points"] for r in rows]),
        "plants": {f: mean([r["plants"][f] for r in rows]) for f in FRUITS},
        "second_train_turn": mean([r["second_train_turn"] for r in rows if r["second_train_turn"] is not None]),
        "third_train_pct": 100 * mean([float(r["third_trained"]) for r in rows]),
    }


def render_markdown(result: dict) -> str:
    lines = [
        "# Track T first table — who the two-troll peers are and what they plant",
        "",
        "- Date: 2026-08-26",
        f"- Corpus: `{result['corpus']['path']}` — **{result['corpus']['rows']:,} games**, "
        f"SHA-256 `{result['corpus']['sha256']}`",
        "- Method: `python3 codex_1/top10/field_comparison.py --output "
        "codex_1/top10/field-comparison-first-table-2026-08-26.md`",
        "- Cohort: the 25 identities from N2's anchor-matching reconstruction. The rank column "
        "is that reconstruction's historical rank, not a claim about today's ladder.",
        "- Our comparison row: every non-cohort occurrence whose recorded player name is `tass`; "
        "this is 10,274 occurrences across our submitted lineages in this corpus.",
        "",
        "## Result",
        "",
        "The 25 identities are all present. They contribute the game counts below. Plant counts "
        "are successful plants per game, computed identically for every peer and for us.",
        "",
        "| historical rank | agent | id | score at games | vs us | observed only | score/game | fruit pts | wood pts | PLUM | LEMON | APPLE | BANANA | second troll turn | third troll games |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in result["agents"]:
        p = row["plants"]
        lines.append(
            f"| {row['historical_rank']} | {row['name']} | {row['agent_id']} | "
            f"{row['arena_score_mean_at_games']:.2f} | {row['games_against_ours']} | "
            f"{row['games_observed_only']} | {row['score']:.1f} | {row['fruit_points']:.1f} | "
            f"{row['wood_points']:.1f} | {p['PLUM']:.2f} | {p['LEMON']:.2f} | "
            f"{p['APPLE']:.2f} | {p['BANANA']:.2f} | {row['second_train_turn']:.1f} | "
            f"{row['third_train_pct']:.1f}% |"
        )
    ours = result["ours"]
    p = ours["plants"]
    lines.extend([
        f"| — | **ours (`tass`)** | many | — | — | {ours['games']} | {ours['score']:.1f} | "
        f"{ours['fruit_points']:.1f} | {ours['wood_points']:.1f} | {p['PLUM']:.2f} | "
        f"{p['LEMON']:.2f} | {p['APPLE']:.2f} | {p['BANANA']:.2f} | "
        f"{ours['second_train_turn']:.1f} | {ours['third_train_pct']:.1f}% |",
        "",
        "## What this first table says",
        "",
        "Planting is common but not one trick. Several high-ranked peers plant roughly 27–37 "
        "bananas per game; others plant mostly non-banana fruit or plant little. Our pooled "
        "lineages plant much less banana than the heavy banana planters. This is descriptive "
        "field evidence, not an estimated causal point value.",
        "",
        "## Processed-corpus boundary",
        "",
        "This 82 MB processed file has final command counts, successful plant totals, training "
        "turns, six 50-turn score snapshots and final inventories. It does **not** have per-turn "
        "commands, plant-generation identity, harvest ownership, target cells, or idle episodes. "
        "Therefore this file alone cannot honestly fill planting turn buckets, who harvested a "
        "planted tree, near-shack suppression, teammate contention, or the last-30-turn verb mix. "
        "Those cells remain unreported rather than guessed. Track F's processed slice contains four "
        "of the b100 bot's 98 recorded ladder games, all from its first batch, "
        "but this same boundary prevents the theft-versus-own-crop attribution required by its dead "
        "condition.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", type=Path, default=Path("data/processed/games.jsonl"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    games = load(args.corpus)
    cohort_ids = {row[0] for row in COHORT}
    occurrences: dict[int, list[dict]] = defaultdict(list)
    versus_ours: Counter[int] = Counter()
    scores_seen: dict[int, list[float]] = defaultdict(list)
    ours: list[dict] = []
    for game in games:
        for seat, player in enumerate(game["players"]):
            aid = player["agentId"]
            if aid in cohort_ids:
                occurrences[aid].append(side_row(game, seat))
                scores_seen[aid].append(player.get("arenaScore", 0.0))
                if game["players"][1 - seat].get("name") == "tass":
                    versus_ours[aid] += 1
            if player.get("name") == "tass" and aid not in cohort_ids:
                ours.append(side_row(game, seat))
    result = {
        "corpus": {"path": str(args.corpus), "rows": len(games), "sha256": CORPUS_SHA256},
        "cohort_provenance": "N2 anchor-matching 25-agent reconstruction; historical ranks, not current ranks",
        "agents": [],
        "ours": summarize(ours),
    }
    for aid, name, rank in COHORT:
        summary = summarize(occurrences[aid])
        result["agents"].append({
            "agent_id": aid, "name": name, "historical_rank": rank,
            "games_against_ours": versus_ours[aid],
            "games_observed_only": len(occurrences[aid]) - versus_ours[aid],
            "arena_score_mean_at_games": mean(scores_seen[aid]),
            **summary,
        })
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.suffix == ".md":
        args.output.write_text(render_markdown(result))
    else:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
