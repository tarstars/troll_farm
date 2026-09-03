#!/usr/bin/env python3
"""Replay and decompose Track P's port-v2 loss before the one refinement loop.

The input is the replay file written by ``claude_1/h2h-panel/h2h.py --replays`` and the
exact panel file used for that run.  Every command pair is re-applied through the same
``FuzzReferee`` as the panel.  The recorded pre-turn scores are checked on every turn before
any derived count is accepted.

The output keeps the units explicit:

* banked fruit items and banked wood items per 50-turn phase (wood is also shown at four
  score points per item), plus the bank score after the phase;
* the shared board's tree count and size units after each phase;
* successful port-created trees, and how many were removed on a final chop turn involving
  the champion;
* emitted action counts per troll-turn in turns 100--200.  DROP is kept as its own category
  rather than being mislabeled idle, although the task's requested list omitted it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "local_claude_1" / "nn-bot"))

import bench  # noqa: E402


PHASES = ((1, 50), (51, 100), (101, 150), (151, 200), (201, 250), (251, 300))
ACTIVITY_WINDOWS = {"100-150": (100, 150), "151-200": (151, 200), "100-200": (100, 200)}
ACTIVITIES = ("harvest", "chop", "mine", "plant", "pick", "move", "drop", "idle")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def phase_index(turn: int) -> int:
    for index, (start, end) in enumerate(PHASES):
        if start <= turn <= end:
            return index
    raise ValueError(f"turn outside 1..300: {turn}")


def mean(values) -> float:
    return statistics.mean(values) if values else 0.0


def median_or_none(values):
    return statistics.median(values) if values else None


def rounded(value, digits: int = 3):
    return round(value, digits) if value is not None else None


def parsed_activity(parsed) -> dict[int, str]:
    """Return the effective parsed verb for each named unit id.

    The referee parser has already enforced the one-command-per-unit rule.  MSG, WAIT and
    TRAIN do not name a troll in the parsed representation; a pre-turn troll absent from this
    mapping is therefore idle for this per-troll accounting.
    """
    out: dict[int, str] = {}
    buckets = (
        ("move", parsed.moves.keys()),
        ("harvest", parsed.harvest),
        ("chop", parsed.chop),
        ("plant", (uid for uid, _ in parsed.plant)),
        ("pick", (uid for uid, _ in parsed.pick)),
        ("drop", parsed.drop),
        ("mine", parsed.mine),
    )
    for label, unit_ids in buckets:
        for unit_id in unit_ids:
            out[int(unit_id)] = label
    return out


def parse_panel(path: Path) -> tuple[str, dict[str, tuple[dict, list[int]]]]:
    raw = path.read_bytes()
    plan = {}
    for line in raw.splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        rec = item["rec"]
        plan[rec["map_hash"]] = (rec, item["draw"])
    return sha256_bytes(raw), plan


def parse_line(ref, line: str):
    parsed = ref.parse_commands(line, ref.turn)
    if parsed.errors:
        raise AssertionError(f"turn {ref.turn}: replay contains parse errors: {parsed.errors}")
    return parsed


def apply_instrumented(ref, parsed0, parsed1, origins, events, turn: int) -> None:
    """Apply one exact referee turn while retaining deposits and tree provenance."""
    moves = dict(parsed0.moves)
    moves.update(parsed1.moves)
    ref._apply_moves(moves)
    ref._apply_harvest(list(parsed0.harvest) + list(parsed1.harvest))

    choppable = set(ref.plants)
    plant_entries = list(parsed0.plant) + list(parsed1.plant)
    plant_intents = []
    for uid, kind in plant_entries:
        unit = ref.units.get(uid)
        if unit is not None:
            plant_intents.append((uid, unit["player"], unit["cell"], kind))
    plants_before = set(ref.plants)
    ref._apply_plant(plant_entries)
    for cell in set(ref.plants) - plants_before:
        kind = ref.plants[cell]["kind"]
        owners = {player for _, player, intent_cell, intent_kind in plant_intents
                  if intent_cell == cell and intent_kind == kind}
        origins[cell] = owners
        for owner in owners:
            events["trees_planted"][owner][phase_index(turn)] += 1

    chop_entries = list(parsed0.chop) + list(parsed1.chop)
    final_choppers: dict[tuple[int, int], set[int]] = {}
    for uid in chop_entries:
        unit = ref.units.get(uid)
        if unit is None or unit["chop"] <= 0 or unit["cell"] not in choppable:
            continue
        final_choppers.setdefault(unit["cell"], set()).add(unit["player"])
    trees_before = set(ref.plants)
    ref._apply_chop(chop_entries, choppable)
    for cell in trees_before - set(ref.plants):
        tree_owners = origins.pop(cell, set())
        if tree_owners:
            for owner in tree_owners:
                events["trees_felled_by_self"][owner][phase_index(turn)] += (
                    owner in final_choppers.get(cell, set())
                )
                events["trees_felled_by_opponent"][owner][phase_index(turn)] += (
                    (1 - owner) in final_choppers.get(cell, set())
                )
        events["tree_fall_turns"].append(turn)

    ref._apply_pick(list(parsed0.pick) + list(parsed1.pick))
    for talents in parsed0.train:
        ref._train_one(talents, 0)
    for talents in parsed1.train:
        ref._train_one(talents, 1)

    drop_entries = list(parsed0.drop) + list(parsed1.drop)
    deposits = []
    for uid in drop_entries:
        unit = ref.units.get(uid)
        if unit is not None and ref._near_shack(unit):
            deposits.append((unit["player"], list(unit["carry"])))
    ref._apply_drop(drop_entries)
    for player, carry in deposits:
        for item, amount in enumerate(carry):
            events["deposits"][player][phase_index(turn)][item] += amount

    ref._apply_mine(list(parsed0.mine) + list(parsed1.mine))
    ref.turn += 1


def empty_events():
    return {
        "deposits": {seat: [[0 for _ in range(6)] for _ in PHASES] for seat in (0, 1)},
        "trees_planted": {seat: [0 for _ in PHASES] for seat in (0, 1)},
        "trees_felled_by_self": {seat: [0 for _ in PHASES] for seat in (0, 1)},
        "trees_felled_by_opponent": {seat: [0 for _ in PHASES] for seat in (0, 1)},
        "tree_fall_turns": [],
    }


def replay_game(rec: dict, draw: list[int], replay: dict) -> dict:
    ref = bench.make_referee(rec, draw)
    policy_seat = replay["policy_seat"]
    events = empty_events()
    origins: dict[tuple[int, int], set[int]] = {}
    activity = {seat: {window: Counter() for window in ACTIVITY_WINDOWS} for seat in (0, 1)}
    activity_denominator = {seat: {window: 0 for window in ACTIVITY_WINDOWS} for seat in (0, 1)}
    chop_1_100 = {seat: 0 for seat in (0, 1)}
    chop_181_190 = {seat: 0 for seat in (0, 1)}
    phase_end = {}
    score_checks = 0
    tree_counts_after_turn = []

    for row in replay["turns"]:
        turn = row["turn"]
        if ref.turn != turn:
            raise AssertionError(f"{rec['map_hash']}: referee turn {ref.turn}, replay turn {turn}")
        expected = [bench.score_of(ref.inv), bench.score_of(ref.opp_inv)]
        if row["score"] != expected:
            raise AssertionError(
                f"{rec['map_hash']} seat {policy_seat} turn {turn}: score {row['score']} != {expected}"
            )
        score_checks += 1

        parsed = {0: parse_line(ref, row["seat0"]), 1: parse_line(ref, row["seat1"])}
        for seat in (0, 1):
            verbs = parsed_activity(parsed[seat])
            own_units = [uid for uid, unit in ref.units.items() if unit["player"] == seat]
            for window, (start, end) in ACTIVITY_WINDOWS.items():
                if start <= turn <= end:
                    activity_denominator[seat][window] += len(own_units)
                    for uid in own_units:
                        activity[seat][window][verbs.get(uid, "idle")] += 1
            if turn <= 100:
                chop_1_100[seat] += sum(label == "chop" for label in verbs.values())
            if 181 <= turn <= 190:
                chop_181_190[seat] += sum(label == "chop" for label in verbs.values())

        apply_instrumented(ref, parsed[0], parsed[1], origins, events, turn)
        ref.grow()
        tree_counts_after_turn.append(len(ref.plants))
        if turn in {end for _, end in PHASES}:
            phase_end[turn] = {
                "score": [bench.score_of(ref.inv), bench.score_of(ref.opp_inv)],
                "tree_count": len(ref.plants),
                "tree_size_units": sum(plant["size"] for plant in ref.plants.values()),
            }

    final = {
        "score": [bench.score_of(ref.inv), bench.score_of(ref.opp_inv)],
        "tree_count": len(ref.plants),
        "tree_size_units": sum(plant["size"] for plant in ref.plants.values()),
    }
    for _, end in PHASES:
        phase_end.setdefault(end, dict(final))

    last_tree_turn = None
    if tree_counts_after_turn and tree_counts_after_turn[-1] == 0:
        last_tree_turn = 1 + max((turn for turn, count in enumerate(tree_counts_after_turn, 1)
                                  if count > 0), default=0)

    def seat_payload(seat: int) -> dict:
        return {
            "deposits": events["deposits"][seat],
            "trees_planted": events["trees_planted"][seat],
            "trees_felled_by_self": events["trees_felled_by_self"][seat],
            "trees_felled_by_opponent": events["trees_felled_by_opponent"][seat],
            "activity": {window: dict(counts) for window, counts in activity[seat].items()},
            "troll_turns": activity_denominator[seat],
            "chop_commands_1_100": chop_1_100[seat],
            "chop_commands_181_190": chop_181_190[seat],
        }

    return {
        "map_hash": rec["map_hash"],
        "policy_seat": policy_seat,
        "turns": len(replay["turns"]),
        "score_checks": score_checks,
        "phase_end": phase_end,
        "last_tree_turn_when_empty_at_end": last_tree_turn,
        "policy": seat_payload(policy_seat),
        "champion": seat_payload(1 - policy_seat),
    }


def summarise(games: list[dict]) -> dict:
    score_rows = []
    tree_rows = []
    for index, (start, end) in enumerate(PHASES):
        score_row = {"turns": f"{start}-{end}"}
        for who in ("policy", "champion"):
            fruit = [sum(game[who]["deposits"][index][:4]) for game in games]
            wood = [game[who]["deposits"][index][bench.fp.WOOD] for game in games]
            seat_index = 0 if who == "policy" else 1
            scores = []
            for game in games:
                seat = game["policy_seat"] if seat_index == 0 else 1 - game["policy_seat"]
                scores.append(game["phase_end"][end]["score"][seat])
            score_row[who] = {
                "fruit_items_banked_mean": rounded(mean(fruit), 2),
                "wood_items_banked_mean": rounded(mean(wood), 2),
                "wood_score_banked_mean": rounded(4 * mean(wood), 2),
                "bank_score_after_phase_mean": rounded(mean(scores), 2),
            }
        score_row["policy_minus_champion_score"] = rounded(
            score_row["policy"]["bank_score_after_phase_mean"]
            - score_row["champion"]["bank_score_after_phase_mean"], 2
        )
        score_rows.append(score_row)

        tree_rows.append({
            "after_turn": end,
            "shared_tree_count_mean": rounded(mean([g["phase_end"][end]["tree_count"] for g in games]), 2),
            "shared_tree_size_units_mean": rounded(
                mean([g["phase_end"][end]["tree_size_units"] for g in games]), 2
            ),
            "policy_trees_planted_mean": rounded(mean([g["policy"]["trees_planted"][index] for g in games]), 2),
            "policy_trees_felled_by_champion_mean": rounded(
                mean([g["policy"]["trees_felled_by_opponent"][index] for g in games]), 2
            ),
            "policy_trees_felled_by_policy_mean": rounded(
                mean([g["policy"]["trees_felled_by_self"][index] for g in games]), 2
            ),
        })

    activity = {}
    for who in ("policy", "champion"):
        windows = {}
        for window in ACTIVITY_WINDOWS:
            counts = Counter()
            denominator = sum(game[who]["troll_turns"][window] for game in games)
            for game in games:
                counts.update(game[who]["activity"][window])
            windows[window] = {
                "troll_turns": denominator,
                "counts": {key: counts[key] for key in ACTIVITIES},
                "per_troll_turn": {
                    key: rounded(counts[key] / denominator, 4) for key in ACTIVITIES
                },
            }
        activity[who] = {
            "windows": windows,
            "chop_commands_per_game_turns_1_100": rounded(
                mean([game[who]["chop_commands_1_100"] for game in games]), 2
            ),
            "chop_commands_per_game_turns_181_190": rounded(
                mean([game[who]["chop_commands_181_190"] for game in games]), 2
            ),
        }

    last_tree_turns = [g["last_tree_turn_when_empty_at_end"] for g in games
                       if g["last_tree_turn_when_empty_at_end"] is not None]
    return {
        "games": len(games),
        "recorded_turn_score_checks": sum(game["score_checks"] for game in games),
        "score_by_50_turn_phase": score_rows,
        "board_and_policy_trees_by_50_turn_phase": tree_rows,
        "activity": activity,
        "games_empty_at_end": len(last_tree_turns),
        "last_tree_fall_turn_when_empty_at_end": {
            "n_games": len(last_tree_turns),
            "median": rounded(median_or_none(last_tree_turns), 1),
            "mean": rounded(mean(last_tree_turns), 1) if last_tree_turns else None,
        },
    }


def run(replays: Path, panel: Path) -> dict:
    panel_sha, plan = parse_panel(panel)
    replay_raw = replays.read_bytes()
    games = []
    for line in replay_raw.splitlines():
        if not line.strip():
            continue
        replay = json.loads(line)
        rec, draw = plan[replay["map_hash"]]
        games.append(replay_game(rec, draw, replay))
    return {
        "instrument": "codex_1/norxondor-port/loss_read.py",
        "replays": str(replays),
        "replays_sha256": sha256_bytes(replay_raw),
        "panel": str(panel),
        "panel_sha256": panel_sha,
        "summary": summarise(games),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replays", type=Path, required=True)
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.replays, args.panel)
    args.out.write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result["summary"], indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
