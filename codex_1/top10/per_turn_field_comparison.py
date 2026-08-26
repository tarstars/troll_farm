#!/usr/bin/env python3
"""Streamed per-turn command comparison for Track T-1.

The turn corpus records issued commands, not referee state.  Provenance below therefore
means "the command was issued at a coordinate previously planted by that seat/opponent"
and is never presented as proof that the command succeeded.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path

TURN_SHA = "1e0ea236a3f0b813eae29d5ba4ec01564ab013984c0064be0ed8330fa5a66726"
COHORT = {
    6480541: "yaichi", 6491563: "Stounate", 6480520: "skotz",
    6483545: "Escdemon", 6559862: "therealbeef", 6479814: "yamo",
    6479779: "putibuzu", 6479420: "Risen", 6479657: "Konstant",
    6520935: "goq", 6480943: "Dridriun", 6479750: "mehdi_ayari",
    6481252: "DaNinja", 6541379: "GoodDevel", 6483491: "VINCE_MX",
    6480951: "0x6E0FF", 6479388: "Kheopsian", 6541416: "Ticasali",
    6479931: "abdelmathin", 6488436: "NOIIICE", 6505289: "tonigineer",
    6481094: "Shun_PI", 6488432: "anuragm", 6499915: "LeRenard",
    6535596: "FRHT",
}
FRUITS = ("PLUM", "LEMON", "APPLE", "BANANA")
BUCKETS = ("1-50", "51-100", "101-150", "151+")


def bucket(turn: int) -> str:
    return BUCKETS[min((turn - 1) // 50, 3)]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def label(row: dict) -> str | None:
    aid = row.get("agentId")
    if aid in COHORT:
        return COHORT[aid]
    if row.get("name") == "tass":
        return "ours"
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--turns", type=Path, default=Path("data/processed/turns.jsonl.gz"))
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    got = sha256(args.turns)
    if got != TURN_SHA:
        raise SystemExit(f"turn corpus hash mismatch: {got}")

    # First pass gives the last-30-turn boundary and one occurrence per game-seat.
    last_turn: dict[int, int] = {}
    games: dict[str, set[tuple[int, int]]] = defaultdict(set)
    corpus_rows = 0
    with gzip.open(args.turns, "rt") as f:
        for line in f:
            corpus_rows += 1
            r = json.loads(line)
            last_turn[r["gameId"]] = max(last_turn.get(r["gameId"], 0), r["turn"])
            lab = label(r)
            if lab:
                games[lab].add((r["gameId"], r["seat"]))

    counts: dict[str, Counter] = defaultdict(Counter)
    plant_bucket: dict[str, Counter] = defaultdict(Counter)
    endgame: dict[str, Counter] = defaultdict(Counter)
    examples: dict[str, dict[str, list[int]]] = defaultdict(lambda: defaultdict(list))
    positions: dict[tuple[int, int, int], tuple[int, int]] = {}
    planted: dict[int, dict[tuple[int, int], tuple[int, str, int]]] = defaultdict(dict)
    move_targets: dict[tuple[int, int, int], list[tuple[int, int]]] = defaultdict(list)

    with gzip.open(args.turns, "rt") as f:
        for line in f:
            r = json.loads(line)
            lab = label(r)
            gid, seat, turn = r["gameId"], r["seat"], r["turn"]
            if not lab:
                continue
            counts[lab]["seat_turns"] += 1
            useful = False
            for c in r["cmds"]:
                verb, unit, a = c["verb"], c.get("unit"), c.get("args") or []
                if verb == "MSG":
                    continue
                counts[lab][f"verb:{verb}"] += 1
                if verb in {"HARVEST", "CHOP", "DROP", "MINE", "PLANT", "PICK", "TRAIN"}:
                    useful = True
                if verb == "MOVE" and unit is not None and len(a) >= 2:
                    try:
                        pos = (int(a[0]), int(a[1]))
                    except ValueError:
                        continue
                    positions[(gid, seat, unit)] = pos
                    move_targets[(gid, seat, turn)].append(pos)
                pos = positions.get((gid, seat, unit)) if unit is not None else None
                if verb == "PLANT" and pos and a and a[0] in FRUITS:
                    fruit = a[0]
                    planted[gid][pos] = (seat, fruit, turn)
                    plant_bucket[lab][f"{fruit}:{bucket(turn)}"] += 1
                if verb in {"HARVEST", "CHOP"} and pos:
                    prior = planted[gid].get(pos)
                    prov = "starting_or_unknown"
                    if prior:
                        prov = "own_planted" if prior[0] == seat else "opponent_planted"
                        if verb == "CHOP" and prov == "own_planted":
                            counts[lab]["own_plant_chop_latency_sum"] += turn - prior[2]
                    counts[lab][f"{verb.lower()}:{prov}"] += 1
                    key = f"{verb.lower()}_{prov}"
                    if gid not in examples[lab][key] and len(examples[lab][key]) < 8:
                        examples[lab][key].append(gid)
                if turn > last_turn[gid] - 30:
                    endgame[lab][verb] += 1
            if not useful:
                counts[lab]["seat_turns_no_work_verb"] += 1
            targets = move_targets.get((gid, seat, turn), [])
            if len(targets) != len(set(targets)):
                counts[lab]["same_target_move_turns"] += 1

    result = {
        "task": "20260826-track-t-top10-field-comparison",
        "corpus": {"path": str(args.turns), "sha256": got,
                   "corpus_rows": corpus_rows,
                   "seat_turn_rows_measured": sum(c["seat_turns"] for c in counts.values())},
        "definitions": {
            "provenance": "issued command at last-known unit coordinate previously targeted by a PLANT command; success is unobserved",
            "no_work": "seat-turn with no issued HARVEST/CHOP/DROP/MINE/PLANT/PICK/TRAIN command",
            "contention_proxy": "two MOVE commands from one seat target the same coordinate in one turn; not the P3/P4 goal-contention detector",
        },
        "rows": {},
    }
    for lab in sorted(counts):
        n = len(games[lab])
        c = counts[lab]
        result["rows"][lab] = {
            "games": n,
            "seat_turns": c["seat_turns"],
            "verbs_per_game": {v: c[f"verb:{v}"] / n for v in
                               ("PLANT", "HARVEST", "CHOP", "DROP", "PICK", "MINE", "TRAIN")},
            "plant_by_fruit_bucket_per_game": {
                f: {b: plant_bucket[lab][f"{f}:{b}"] / n for b in BUCKETS} for f in FRUITS},
            "harvest_command_provenance_per_game": {
                p: c[f"harvest:{p}"] / n for p in
                ("own_planted", "opponent_planted", "starting_or_unknown")},
            "chop_command_provenance_per_game": {
                p: c[f"chop:{p}"] / n for p in
                ("own_planted", "opponent_planted", "starting_or_unknown")},
            "own_plant_chop_mean_latency": (
                c["own_plant_chop_latency_sum"] / c["chop:own_planted"]
                if c["chop:own_planted"] else None),
            "last30_verbs_per_game": {v: endgame[lab][v] / n for v in
                                      ("PLANT", "HARVEST", "CHOP", "DROP", "PICK", "MINE", "MOVE")},
            "no_work_verb_turn_pct": 100 * c["seat_turns_no_work_verb"] / c["seat_turns"],
            "same_target_move_turns_per_game": c["same_target_move_turns"] / n,
            "example_game_ids": examples[lab],
        }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
