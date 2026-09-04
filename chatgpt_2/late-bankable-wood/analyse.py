#!/usr/bin/env python3
"""Adjudicate late-bankable-wood on two independent champion replay packages.

This is a read, not a bot build.  For every own troll-turn from 251 onward whose
recorded command is NONE, PICK, or PLANT, test whether that troll could begin a
CHOP job on the pre-turn board and still fell, carry, and DROP the resulting wood
by turn 300.  The calculation mirrors claude_1/live-observations/observe.py.

Two outputs are intentionally separated:

* event feasibility: "was some bankable chop available at this exact decision?"
* unused standing-tree ceiling: final-standing trees that were bankable at one
  of those exact decisions, counted once each.  This is an optimistic ceiling
  on extra banked points, not a counterfactual replay.

The original E-1 co-chop-duplication estimate is reported separately, never
added to the idle/PICK/PLANT mechanism.
"""
from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
import json
import random
import statistics
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

from local_claude_1.reconstructions.fits.reconstruct import (
    Reconstructor,
    build_game,
    parse_frame0,
)

TOTAL_TURNS = 300
LATE_FROM = 251
ELIGIBLE_VERBS = {"NONE", "PICK", "PLANT"}
UNIT_VERBS = {"MOVE", "HARVEST", "CHOP", "PLANT", "PICK", "DROP", "MINE"}
ORTH = ((1, 0), (-1, 0), (0, 1), (0, -1))
PLANT_COOLDOWN = {"PLUM": 8, "LEMON": 8, "APPLE": 9, "BANANA": 6}
WATER_BOOST = {"PLUM": 5, "LEMON": 5, "APPLE": 7, "BANANA": 2}
HEALTH_SLOPE = {"PLUM": 2, "LEMON": 2, "APPLE": 3, "BANANA": 1}


class ReplayReconstructor(Reconstructor):
    """Existing exact reconstructor initialized from one in-memory package row."""

    def __init__(self, replay: dict[str, Any]) -> None:
        self.game_id = int(replay["gameId"])
        self.replay = replay
        self.frames = replay["frames"]
        width, height, rows, units, plants, inventories = parse_frame0(self.frames[0])
        self.map = {"w": width, "h": height, "rows": rows}
        self.game = build_game(width, height, rows, units, plants, inventories)
        self.unit_by_eid = {}
        self.plant_by_eid = {}
        by_id = {unit.id: unit for unit in self.game.units}
        for entity_id, unit in units.items():
            self.unit_by_eid[entity_id] = by_id[unit["id"]]
        by_pos = {plant.pos: plant for plant in self.game.plants}
        for entity_id, plant in plants.items():
            self.plant_by_eid[entity_id] = by_pos[(plant["x"], plant["y"])]
        self.mismatch = collections.Counter()
        self.examples = {}
        self.agents = {agent["index"]: agent for agent in replay["agents"]}
        self.n_turns = (len(self.frames) - 1) // 2


def ceil_div(a: int, b: int) -> int:
    return -(-a // b) if b > 0 else 10**6


def bfs(
    walkable: set[tuple[int, int]],
    starts: Iterable[tuple[int, int]],
) -> dict[tuple[int, int], int]:
    dist: dict[tuple[int, int], int] = {}
    queue: collections.deque[tuple[int, int]] = collections.deque()
    for start in starts:
        if start in walkable and start not in dist:
            dist[start] = 0
            queue.append(start)
    while queue:
        x, y = queue.popleft()
        d = dist[(x, y)]
        for dx, dy in ORTH:
            cell = (x + dx, y + dy)
            if cell in walkable and cell not in dist:
                dist[cell] = d + 1
                queue.append(cell)
    return dist


def near_water(water: set[tuple[int, int]], cell: tuple[int, int]) -> bool:
    return any((cell[0] + dx, cell[1] + dy) in water for dx, dy in ORTH)


def effective_cd(kind: str, wet: bool) -> int:
    return PLANT_COOLDOWN[kind] - (WATER_BOOST[kind] if wet else 0)


def predict_tree(
    plant: dict[str, Any],
    turns: int,
    opponent_chop: int,
    wet: bool,
) -> tuple[int, int, int] | None:
    size = int(plant["size"])
    health = int(plant["health"])
    cooldown = int(plant["cooldown"])
    for _ in range(turns):
        if opponent_chop > 0:
            health -= opponent_chop
            if health <= 0:
                return None
        if cooldown > 0:
            cooldown -= 1
        if cooldown == 0 and health > 0:
            if size < 4:
                size += 1
                health += HEALTH_SLOPE[plant["type"]]
                cooldown = effective_cd(plant["type"], wet)
    return size, health, cooldown


def chop_outcome(
    kind: str,
    size: int,
    health: int,
    cooldown: int,
    chop_power: int,
    wet: bool,
) -> tuple[int, int] | None:
    if chop_power <= 0:
        return None
    reset = effective_cd(kind, wet)
    for turns in range(1, 101):
        health -= chop_power
        if health <= 0:
            return turns, size
        if cooldown > 0:
            cooldown -= 1
        if cooldown == 0 and size < 4:
            size += 1
            health += HEALTH_SLOPE[kind]
            cooldown = reset
    return None


def command_by_unit(commands: list[str]) -> dict[int, str]:
    result: dict[int, str] = {}
    for command in commands:
        fields = command.split()
        if len(fields) < 2:
            continue
        verb = fields[0].upper()
        if verb not in UNIT_VERBS or not fields[1].lstrip("-").isdigit():
            continue
        result[int(fields[1])] = verb
    return result


@dataclass(frozen=True)
class Candidate:
    cell: tuple[int, int]
    kind: str
    total_turns: int
    finish_turn: int
    wood_units: int
    points: int
    final_size: int
    travel_turns: int
    chop_turns: int
    return_and_drop_turns: int


def bankable_candidates(
    *,
    state: dict[str, Any],
    unit: dict[str, Any],
    turn: int,
    walkable: set[tuple[int, int]],
    water: set[tuple[int, int]],
    shack: tuple[int, int],
    to_shack: dict[tuple[int, int], int],
    opponent_units: list[dict[str, Any]],
) -> list[Candidate]:
    free = int(unit["cc"]) - sum(int(x) for x in unit["carry"])
    chop_power = int(unit["chop"])
    if free <= 0 or chop_power <= 0:
        return []
    from_unit = bfs(walkable, [(int(unit["x"]), int(unit["y"]))])
    movement = max(int(unit["ms"]), 1)
    left = TOTAL_TURNS - turn + 1
    out: list[Candidate] = []
    for plant in state["plants"]:
        if int(plant["health"]) <= 0:
            continue
        cell = (int(plant["x"]), int(plant["y"]))
        if cell not in from_unit:
            continue
        travel = ceil_div(from_unit[cell], movement)
        opponent_chop = sum(
            int(other["chop"])
            for other in opponent_units
            if (int(other["x"]), int(other["y"])) == cell
        )
        wet = near_water(water, cell)
        predicted = predict_tree(plant, travel, opponent_chop, wet)
        if predicted is None or predicted[0] <= 0 or predicted[1] <= 0:
            continue
        outcome = chop_outcome(
            plant["type"],
            predicted[0],
            predicted[1],
            predicted[2],
            chop_power,
            wet,
        )
        if outcome is None:
            continue
        chop_turns, final_size = outcome
        return_distance = to_shack.get(cell)
        if return_distance is None:
            return_distance = abs(cell[0] - shack[0]) + abs(cell[1] - shack[1])
        return_turns = ceil_div(return_distance, movement)
        return_and_drop = return_turns + 1
        total = max(travel + chop_turns + return_and_drop, 1)
        wood_units = min(final_size, free)
        if total > left or wood_units <= 0:
            continue
        out.append(
            Candidate(
                cell=cell,
                kind=str(plant["type"]),
                total_turns=total,
                finish_turn=turn + total - 1,
                wood_units=wood_units,
                points=4 * wood_units,
                final_size=final_size,
                travel_turns=travel,
                chop_turns=chop_turns,
                return_and_drop_turns=return_and_drop,
            )
        )
    out.sort(key=lambda candidate: (-candidate.points, candidate.total_turns, candidate.cell, candidate.kind))
    return out


def quantiles(values: list[float]) -> dict[str, float]:
    if not values:
        return {"min": 0.0, "p25": 0.0, "median": 0.0, "p75": 0.0, "p90": 0.0, "max": 0.0}
    ordered = sorted(values)

    def nearest(p: float) -> float:
        return float(ordered[round((len(ordered) - 1) * p)])

    return {
        "min": float(ordered[0]),
        "p25": nearest(0.25),
        "median": nearest(0.50),
        "p75": nearest(0.75),
        "p90": nearest(0.90),
        "max": float(ordered[-1]),
    }


def bootstrap_mean_interval(
    values: list[float],
    seed: int = 1,
    draws: int = 20_000,
) -> list[float]:
    if not values:
        return [0.0, 0.0]
    rng = random.Random(seed)
    n = len(values)
    means = []
    for _ in range(draws):
        means.append(sum(values[rng.randrange(n)] for _ in range(n)) / n)
    means.sort()
    return [means[int(0.025 * draws)], means[int(0.975 * draws) - 1]]


def final_tree_births(
    states: list[dict[str, Any]],
    n_turns: int,
) -> dict[tuple[int, int], tuple[str, int]]:
    """Birth turn of each tree standing in the final state, by continuity on its cell."""
    final = states[n_turns]
    result: dict[tuple[int, int], tuple[str, int]] = {}
    for plant in final["plants"]:
        if int(plant["health"]) <= 0:
            continue
        cell = (int(plant["x"]), int(plant["y"]))
        kind = str(plant["type"])
        birth = 1
        for turn in range(n_turns, 0, -1):
            present = next(
                (
                    candidate
                    for candidate in states[turn - 1]["plants"]
                    if (int(candidate["x"]), int(candidate["y"])) == cell
                    and str(candidate["type"]) == kind
                    and int(candidate["health"]) > 0
                ),
                None,
            )
            if present is None:
                birth = turn + 1
                break
            birth = turn
        result[cell] = (kind, birth)
    return result


def load_package(path: Path) -> list[dict[str, Any]]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def analyse_game(replay: dict[str, Any], agent_id: int) -> dict[str, Any] | None:
    reconstructor = ReplayReconstructor(replay)
    states = reconstructor.run(keep_states=True)
    seat_matches = [
        int(agent["index"])
        for agent in replay["agents"]
        if int(agent["agentId"]) == agent_id
    ]
    if len(seat_matches) != 1:
        raise ValueError(
            f"game {replay['gameId']}: agent {agent_id} seat count {len(seat_matches)}"
        )
    ours = seat_matches[0]
    if reconstructor.n_turns < LATE_FROM:
        return None

    walkable = set(reconstructor.game.walkable)
    water = set(reconstructor.game.water)
    shack = tuple(reconstructor.game.shacks[ours])
    doors = [
        (shack[0] + dx, shack[1] + dy)
        for dx, dy in ORTH
        if (shack[0] + dx, shack[1] + dy) in walkable
    ]
    to_shack = bfs(walkable, doors)
    births = final_tree_births(states, reconstructor.n_turns)

    counts = collections.Counter()
    feasible = collections.Counter()
    bucket_counts = collections.Counter()
    bucket_feasible = collections.Counter()
    best_event_points: list[int] = []
    final_tree_options: dict[tuple[int, int], Candidate] = {}
    examples: list[dict[str, Any]] = []
    greedy_used: set[tuple[int, int]] = set()
    greedy_free_at: dict[int, int] = {}
    greedy_points = 0
    greedy_trees = 0

    for turn in range(LATE_FROM, reconstructor.n_turns + 1):
        state = states[turn - 1]
        commands = reconstructor.commands(turn)[ours]
        by_unit = command_by_unit(commands)
        own_units = [unit for unit in state["units"] if int(unit["player"]) == ours]
        opponent_units = [unit for unit in state["units"] if int(unit["player"]) != ours]
        bucket = min((turn - LATE_FROM) // 10, 4)
        for unit in own_units:
            uid = int(unit["id"])
            verb = by_unit.get(uid, "NONE")
            if verb not in ELIGIBLE_VERBS:
                continue
            counts[verb] += 1
            bucket_counts[bucket] += 1
            candidates = bankable_candidates(
                state=state,
                unit=unit,
                turn=turn,
                walkable=walkable,
                water=water,
                shack=shack,
                to_shack=to_shack,
                opponent_units=opponent_units,
            )
            if not candidates:
                continue
            feasible[verb] += 1
            bucket_feasible[bucket] += 1
            best_event_points.append(candidates[0].points)

            for candidate in candidates:
                birth_info = births.get(candidate.cell)
                if birth_info is None:
                    continue
                final_kind, birth_turn = birth_info
                if turn < birth_turn or candidate.kind != final_kind:
                    continue
                old = final_tree_options.get(candidate.cell)
                if old is None or (
                    candidate.points,
                    -candidate.total_turns,
                ) > (
                    old.points,
                    -old.total_turns,
                ):
                    final_tree_options[candidate.cell] = candidate

            # A scheduling sanity bound: no reused tree and no overlapping job for one
            # troll. Later locations remain the recorded ones, so this is still optimistic.
            if turn >= greedy_free_at.get(uid, LATE_FROM):
                choice = next(
                    (candidate for candidate in candidates if candidate.cell not in greedy_used),
                    None,
                )
                if choice is not None:
                    greedy_used.add(choice.cell)
                    greedy_free_at[uid] = choice.finish_turn + 1
                    greedy_points += choice.points
                    greedy_trees += 1

            if len(examples) < 12:
                examples.append(
                    {
                        "turn": turn,
                        "unit": uid,
                        "verb": verb,
                        "cell": [int(unit["x"]), int(unit["y"])],
                        "best": {
                            **asdict(candidates[0]),
                            "cell": list(candidates[0].cell),
                        },
                    }
                )

    unique_ceiling_points = sum(candidate.points for candidate in final_tree_options.values())
    return {
        "game_id": int(replay["gameId"]),
        "turns": reconstructor.n_turns,
        "eligible": dict(counts),
        "feasible": dict(feasible),
        "eligible_total": sum(counts.values()),
        "feasible_total": sum(feasible.values()),
        "buckets_eligible": [bucket_counts[index] for index in range(5)],
        "buckets_feasible": [bucket_feasible[index] for index in range(5)],
        "event_best_points_sum_repeated": sum(best_event_points),
        "event_best_points": best_event_points,
        "unused_final_standing_trees": len(final_tree_options),
        "unused_final_standing_points_ceiling": unique_ceiling_points,
        "scheduled_distinct_tree_points_ceiling": greedy_points,
        "scheduled_distinct_trees": greedy_trees,
        "final_standing_trees": len(births),
        "examples": examples,
        "reconstruction_mismatches": dict(reconstructor.mismatch),
    }


def summarise_package(
    *,
    label: str,
    path: Path,
    agent_id: int,
) -> dict[str, Any]:
    replay_rows = sorted(load_package(path), key=lambda row: int(row["gameId"]))
    games_all = [analyse_game(replay, agent_id) for replay in replay_rows]
    games = [game for game in games_all if game is not None]
    eligible = collections.Counter()
    feasible = collections.Counter()
    buckets_eligible = [0] * 5
    buckets_feasible = [0] * 5
    mismatch = collections.Counter()
    for game in games:
        eligible.update(game["eligible"])
        feasible.update(game["feasible"])
        for index in range(5):
            buckets_eligible[index] += game["buckets_eligible"][index]
            buckets_feasible[index] += game["buckets_feasible"][index]
        mismatch.update(game["reconstruction_mismatches"])

    unique_points = [
        float(game["unused_final_standing_points_ceiling"])
        for game in games
    ]
    scheduled_points = [
        float(game["scheduled_distinct_tree_points_ceiling"])
        for game in games
    ]
    event_points = [
        float(point)
        for game in games
        for point in game["event_best_points"]
    ]
    total_eligible = sum(eligible.values())
    total_feasible = sum(feasible.values())
    return {
        "label": label,
        "package": str(path),
        "package_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "agent_id": agent_id,
        "games_total": len(replay_rows),
        "long_games": len(games),
        "eligible": dict(eligible),
        "feasible": dict(feasible),
        "feasible_share_by_verb": {
            verb: (feasible[verb] / eligible[verb] if eligible[verb] else 0.0)
            for verb in sorted(ELIGIBLE_VERBS)
        },
        "eligible_total": total_eligible,
        "feasible_total": total_feasible,
        "feasible_share": total_feasible / total_eligible if total_eligible else 0.0,
        "buckets_eligible": buckets_eligible,
        "buckets_feasible": buckets_feasible,
        "best_bankable_points_per_feasible_event": {
            "mean": statistics.mean(event_points) if event_points else 0.0,
            **quantiles(event_points),
        },
        "unused_final_standing_points_ceiling_per_long_game": {
            "mean": statistics.mean(unique_points) if unique_points else 0.0,
            "interval_95_bootstrap": bootstrap_mean_interval(unique_points),
            **quantiles(unique_points),
            "positive_games": sum(value > 0 for value in unique_points),
            "games": len(unique_points),
        },
        "scheduled_distinct_tree_points_ceiling_per_long_game": {
            "mean": statistics.mean(scheduled_points) if scheduled_points else 0.0,
            "interval_95_bootstrap": bootstrap_mean_interval(scheduled_points),
            **quantiles(scheduled_points),
            "positive_games": sum(value > 0 for value in scheduled_points),
            "games": len(scheduled_points),
        },
        "reconstruction_mismatches": dict(mismatch),
        "games": games,
    }


def markdown(results: list[dict[str, Any]]) -> str:
    lines = [
        "# Late bankable wood — adjudication read",
        "",
        "This is a read only. No candidate was built.",
        "",
        "## Verdict",
        "",
    ]
    primary = results[0]
    ceiling = primary["unused_final_standing_points_ceiling_per_long_game"]
    if ceiling["mean"] < 4.0:
        verdict = (
            "**DEAD ON PAPER.** Even the optimistic, unique-final-tree ceiling is "
            f"{ceiling['mean']:.2f} banked points per long game "
            f"(95% bootstrap interval {ceiling['interval_95_bootstrap'][0]:.2f} to "
            f"{ceiling['interval_95_bootstrap'][1]:.2f}), below the four-point bar."
        )
    else:
        verdict = (
            "**PREMISE SURVIVES THE CHEAP READ.** The optimistic, unique-final-tree ceiling is "
            f"{ceiling['mean']:.2f} banked points per long game "
            f"(95% bootstrap interval {ceiling['interval_95_bootstrap'][0]:.2f} to "
            f"{ceiling['interval_95_bootstrap'][1]:.2f}). A build would still be needed to "
            "measure actual incremental points because this ceiling does not replay the changed policy."
        )
    lines += [verdict, ""]

    lines += [
        "## Exact decision-time feasibility",
        "",
        "| package | long games | eligible troll-turns | feasible | share | NONE | PICK | PLANT | unused final-standing ceiling, mean / median |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for result in results:
        ceiling = result["unused_final_standing_points_ceiling_per_long_game"]
        by_verb = []
        for verb in ("NONE", "PICK", "PLANT"):
            by_verb.append(
                f"{result['feasible'].get(verb, 0)}/{result['eligible'].get(verb, 0)} "
                f"({result['feasible_share_by_verb'].get(verb, 0.0):.1%})"
            )
        lines.append(
            f"| {result['label']} | {result['long_games']} | {result['eligible_total']} | "
            f"{result['feasible_total']} | {result['feasible_share']:.1%} | "
            f"{by_verb[0]} | {by_verb[1]} | {by_verb[2]} | "
            f"{ceiling['mean']:.2f} / {ceiling['median']:.0f} |"
        )
    lines += [
        "",
        "A chop is counted only when, on that pre-turn board, the troll has chop power and free carry, "
        "can reach a living tree, the tree is predicted to survive until arrival, can fell it, can "
        "carry at least one wood, can reach a shack door, and can issue DROP by turn 300.",
        "",
        "The `unused final-standing ceiling` counts each tree still standing at game end at most once, "
        "and only if that same continuously existing tree was bankable at an eligible decision. It is "
        "an optimistic upper bound: it does not charge the lost PICK/PLANT continuation and it does not "
        "replay changed later positions.",
        "",
        "## Reconciliation",
        "",
        "The two headline numbers do not contradict each other. They use different populations and different "
        "units of observation. `705/734` is a **tree-level ever-event** statistic from champion package "
        "`41234663`: a final-standing tree qualified if any troll could bank it on any turn from 200 to 300. "
        "The `83.7% terminal waits` result is a **troll-turn statistic** from the older champion package "
        "`41202036`, restricted to no-command turns from 251 onward. Moreover, the old E-1 `chop-feasible` "
        "script tested travel plus felling but omitted the return trip and DROP for chops; this read applies "
        "the full bankable test. A tree can therefore be feasible at turn 220, then generate many infeasible "
        "idle turns near turn 300. Neither statistic alone justified Experiment B.",
        "",
        "## Co-chop duplication — separate mechanism",
        "",
        "E-1 found 61 late odd-size fellings in the 96 long games where an idle partner could have joined the "
        "death turn. The referee can award one duplicated last wood in that case: 61 × 4 / 96 = **2.54 points "
        "per long game** as an optimistic ceiling. This is not added to the NONE/PICK/PLANT result: it is a "
        "same-cell co-chop rule, not a choice between replanting and starting a new bankable tree job.",
        "",
        "## Distribution",
        "",
    ]
    for result in results:
        ceiling = result["unused_final_standing_points_ceiling_per_long_game"]
        scheduled = result["scheduled_distinct_tree_points_ceiling_per_long_game"]
        lines += [
            f"### {result['label']}",
            "",
            f"- unique final-standing ceiling: mean {ceiling['mean']:.2f}, 95% bootstrap "
            f"[{ceiling['interval_95_bootstrap'][0]:.2f}, {ceiling['interval_95_bootstrap'][1]:.2f}], "
            f"p25/median/p75/p90/max {ceiling['p25']:.0f}/{ceiling['median']:.0f}/{ceiling['p75']:.0f}/"
            f"{ceiling['p90']:.0f}/{ceiling['max']:.0f}, positive in "
            f"{ceiling['positive_games']}/{ceiling['games']} games;",
            f"- non-overlapping recorded-location scheduling ceiling: mean {scheduled['mean']:.2f}, "
            f"95% bootstrap [{scheduled['interval_95_bootstrap'][0]:.2f}, "
            f"{scheduled['interval_95_bootstrap'][1]:.2f}], median {scheduled['median']:.0f}. "
            "This remains optimistic because later locations are borrowed from the original replay.",
            "",
        ]
    lines += [
        "## Measurement boundary",
        "",
        "This read determines whether opportunities existed on recorded boards. It does not prove the score "
        "of a modified policy. If the premise survives, only a byte-identical-through-turn-250 paired build "
        "can measure incremental value. A sub-2.2 rating expectation cannot be settled by one ladder reading.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("chatgpt_2/late-bankable-wood/results"),
    )
    args = parser.parse_args()
    specs = [
        (
            "E-1 package 41202036",
            Path(
                "local_claude_1/denial-ablation/games-41202036/"
                "games-agent6667789-submission41202036.jsonl.gz"
            ),
            6667789,
        ),
        (
            "independent champion package 41234663",
            Path(
                "local_claude_1/ladder-queue/games-41234663/"
                "games-agent6693889-submission41234663.jsonl.gz"
            ),
            6693889,
        ),
    ]
    results = [
        summarise_package(label=label, path=path, agent_id=agent_id)
        for label, path, agent_id in specs
    ]
    args.out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "task": "20260904-late-bankable-wood",
        "late_from": LATE_FROM,
        "total_turns": TOTAL_TURNS,
        "eligible_verbs": sorted(ELIGIBLE_VERBS),
        "cochop_duplication_given_by_e1": {
            "opportunities": 61,
            "long_games": 96,
            "points_per_opportunity": 4,
            "points_per_long_game_ceiling": 61 * 4 / 96,
            "kept_separate": True,
        },
        "packages": results,
    }
    (args.out_dir / "results.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    report = markdown(results)
    (args.out_dir / "RESULTS.md").write_text(report, encoding="utf-8")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
