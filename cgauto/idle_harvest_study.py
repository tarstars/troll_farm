#!/usr/bin/env python3
"""Run causal local checks for the live Yamo idle-harvest fallback.

This is deliberately not an arena predictor. It provides two narrower guarantees:

1. a fixed 300-view input stream proves the stderr probe leaves stdout byte-identical and
   locates the first baseline/candidate action divergence on an identical state;
2. a seat-swapped local simulation measures what happens after activation under the repository's
   deterministic simulator.

The exact recovered baseline, exact one-site ablation, and exact-minified probe are compiled in a
temporary directory. No source is submitted or written to CodinGame.
"""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import as_completed, ThreadPoolExecutor
import copy
from dataclasses import dataclass
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from sim.engine import has_stalled, recompute_scores, step  # noqa: E402
from sim.mapgen import generate_bronze  # noqa: E402
from sim.state import GameState, SimPlant, SimUnit  # noqa: E402

BASELINE_SOURCE = REPO / "cgauto/submissions/agent-6553250-yamo-orchard-live.min.rs"
CANDIDATE_SOURCE = (
    REPO / "cgauto/submissions/candidate-agent6553250-idle-harvest-off.min.rs"
)
PROBE_SOURCE = (
    REPO / "cgauto/submissions/diagnostic-agent6553250-idle-harvest-probe.min.rs"
)

EVENT_RE = re.compile(
    r"^@IH_(CAND|SELECT|ORCHARD_FORCE) t=(\d+) unit=(\d+) "
    r"(?:commands|command)=(.*)$"
)


def parse_probe_events(stderr: str) -> list[dict]:
    events = []
    for line in stderr.splitlines():
        match = EVENT_RE.match(line.strip())
        if match:
            events.append(
                {
                    "kind": match[1].lower(),
                    "turn": int(match[2]),
                    "unit": int(match[3]),
                    "commands": match[4],
                }
            )
    return events


def action_commands(line: str) -> list[str]:
    """Return state-changing commands, excluding the announcement-only MSG verb."""

    return [
        command.strip()
        for command in re.split(r"[;\n]", line)
        if command.strip() and not command.strip().upper().startswith("MSG ")
    ]


def grid_text(game: GameState, seat: int) -> str:
    lines = [f"{game.width} {game.height}"]
    for y in range(game.height):
        row = []
        for x in range(game.width):
            cell = (x, y)
            if cell == game.shacks[seat]:
                row.append("0")
            elif cell == game.shacks[1 - seat]:
                row.append("1")
            elif cell in game.iron:
                row.append("+")
            elif cell in game.water:
                row.append("~")
            elif cell in game.walkable:
                row.append(".")
            else:
                row.append("#")
        lines.append("".join(row))
    return "\n".join(lines) + "\n"


def turn_text(game: GameState, seat: int) -> str:
    lines = []
    for player in (seat, 1 - seat):
        lines.append(" ".join(str(value) for value in game.inventories[player]))
    lines.append(str(len(game.plants)))
    for plant in game.plants:
        lines.append(
            f"{plant.type} {plant.x} {plant.y} {plant.size} {plant.health} "
            f"{plant.fruits} {plant.cooldown}"
        )
    lines.append(str(len(game.units)))
    for unit in game.units:
        relative_player = 0 if unit.player == seat else 1
        carry = " ".join(str(value) for value in unit.carry)
        lines.append(
            f"{unit.id} {relative_player} {unit.x} {unit.y} {unit.ms} {unit.cc} "
            f"{unit.hp} {unit.chop} {carry}"
        )
    return "\n".join(lines) + "\n"


def fixed_fixture() -> GameState:
    width, height = 7, 5
    shacks = [(1, 2), (5, 2)]
    walkable = {
        (x, y)
        for x in range(width)
        for y in range(height)
        if (x, y) not in shacks
    }
    game = GameState(
        width=width,
        height=height,
        walkable=walkable,
        shacks=shacks,
        inventories=[[0] * 6, [0] * 6],
        units=[
            SimUnit(0, 0, 3, 2, 1, 1, 1, 1, [0] * 6),
            SimUnit(1, 1, 5, 2, 1, 1, 1, 1, [0] * 6),
        ],
        plants=[SimPlant("APPLE", 3, 2, 4, 20, 1, 9)],
        scores=[0, 0],
        turn=1,
        next_id=2,
    )
    recompute_scores(game)
    return game


def compile_source(source: Path, output: Path, crate_name: str) -> None:
    result = subprocess.run(
        [
            "rustc",
            "--edition",
            "2021",
            "-O",
            "--crate-name",
            crate_name,
            str(source),
            "-o",
            str(output),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode:
        raise RuntimeError(f"rustc failed for {source}:\n{result.stderr}")


def run_batch(binary: Path, input_text: str) -> tuple[list[str], str]:
    result = subprocess.run(
        [binary], input=input_text, capture_output=True, text=True, timeout=90
    )
    if result.returncode:
        raise RuntimeError(f"{binary.name} exited {result.returncode}: {result.stderr[:500]}")
    return result.stdout.splitlines(), result.stderr


@dataclass
class BotSession:
    binary: Path
    game: GameState
    seat: int

    def __post_init__(self) -> None:
        self.process = subprocess.Popen(
            [self.binary],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        assert self.process.stdin is not None
        self.process.stdin.write(grid_text(self.game, self.seat))
        self.process.stdin.flush()

    def command(self, game: GameState) -> str:
        assert self.process.stdin is not None and self.process.stdout is not None
        self.process.stdin.write(turn_text(game, self.seat))
        self.process.stdin.flush()
        line = self.process.stdout.readline()
        if not line:
            stderr = self.process.stderr.read() if self.process.stderr else ""
            raise RuntimeError(
                f"{self.binary.name} produced no turn output (exit={self.process.poll()}): "
                f"{stderr[:500]}"
            )
        return line.rstrip("\r\n")

    def close(self) -> str:
        assert self.process.stdin is not None
        self.process.stdin.close()
        returncode = self.process.wait(timeout=30)
        stderr = self.process.stderr.read() if self.process.stderr else ""
        if returncode:
            raise RuntimeError(f"{self.binary.name} exited {returncode}: {stderr[:500]}")
        return stderr


def fixed_stream_result(baseline: Path, candidate: Path, probe: Path) -> dict:
    game = fixed_fixture()
    fixed_input = grid_text(game, 0) + turn_text(game, 0) * 300
    baseline_lines, baseline_stderr = run_batch(baseline, fixed_input)
    candidate_lines, _ = run_batch(candidate, fixed_input)
    probe_lines, probe_stderr = run_batch(probe, fixed_input)
    if baseline_lines != probe_lines:
        raise RuntimeError("probe changed stdout on the fixed 300-view stream")
    if baseline_stderr:
        raise RuntimeError("the exact baseline unexpectedly wrote to stderr")

    divergence = None
    for turn, (base, cand) in enumerate(zip(baseline_lines, candidate_lines), 1):
        if action_commands(base) != action_commands(cand):
            divergence = {
                "turn": turn,
                "baseline": action_commands(base),
                "candidate": action_commands(cand),
            }
            break
    if divergence is None:
        raise RuntimeError("fixed fixture never distinguished baseline and candidate")
    events = parse_probe_events(probe_stderr)
    selected_turns = [event["turn"] for event in events if event["kind"] == "select"]
    if divergence["turn"] not in selected_turns:
        raise RuntimeError("first action divergence is not explained by @IH_SELECT telemetry")
    return {
        "stdout_neutral": True,
        "turns": len(baseline_lines),
        "first_action_divergence": divergence,
        "probe_events": events,
    }


def rollout_one(binary: Path, start_turn: int) -> dict:
    fixed = fixed_fixture()
    session = BotSession(binary, fixed, 0)
    for _ in range(1, start_turn):
        session.command(fixed)

    game = copy.deepcopy(fixed)
    game.turn = start_turn
    records = []
    turns_until_end = 0
    ended_by_stall = False
    while game.turn <= 300:
        turn = game.turn
        line = session.command(game)
        commands = action_commands(line)
        records.append({"turn": turn, "commands": commands})
        step(game, commands, ["WAIT"])
        ended_by_stall, turns_until_end = has_stalled(game, turns_until_end)
        if ended_by_stall:
            break
    stderr = session.close()
    return {
        "score": game.scores[0],
        "inventory": game.inventories[0],
        "commands": records,
        "probe_events": parse_probe_events(stderr),
        "terminal_turn": game.turn - 1,
        "ended_by_stall": ended_by_stall,
    }


def run_match(game: GameState, binary0: Path, binary1: Path) -> dict:
    sessions = [BotSession(binary0, game, 0), BotSession(binary1, game, 1)]
    command_counts = [Counter(), Counter()]
    turns_until_end = 0
    ended_by_stall = False
    try:
        while game.turn <= 300:
            lines = [session.command(game) for session in sessions]
            commands = [action_commands(line) for line in lines]
            for seat in (0, 1):
                command_counts[seat].update(
                    command.split()[0].upper() for command in commands[seat] if command.split()
                )
            step(game, commands[0], commands[1])
            ended_by_stall, turns_until_end = has_stalled(game, turns_until_end)
            if ended_by_stall:
                break
    finally:
        stderrs = [session.close() for session in sessions]
    return {
        "scores": list(game.scores),
        "inventories": copy.deepcopy(game.inventories),
        "command_counts": [dict(counts) for counts in command_counts],
        "events": [parse_probe_events(stderr) for stderr in stderrs],
        "terminal_turn": game.turn - 1,
        "ended_by_stall": ended_by_stall,
    }


def event_counts(events: list[dict]) -> dict:
    counts = Counter(event["kind"] for event in events)
    return {kind: counts.get(kind, 0) for kind in ("cand", "select", "orchard_force")}


def paired_row(seed: int, probe: Path, candidate: Path) -> dict:
    initial = generate_bronze(seed)
    first = run_match(copy.deepcopy(initial), probe, candidate)
    second = run_match(copy.deepcopy(initial), candidate, probe)
    probe_events = first["events"][0] + second["events"][1]
    margins = [
        first["scores"][0] - first["scores"][1],
        second["scores"][1] - second["scores"][0],
    ]
    return {
        "seed": seed,
        "baseline_seat0": first,
        "baseline_seat1": second,
        "baseline_margins": margins,
        "paired_margin": sum(margins) / 2,
        "probe_event_counts": event_counts(probe_events),
        "probe_select_turns": sorted(
            event["turn"] for event in probe_events if event["kind"] == "select"
        ),
    }


def save(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=1) + "\n")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=int, default=20)
    parser.add_argument("--seed-start", type=int, default=0)
    parser.add_argument("--jobs", type=int, default=1)
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO / "data/analysis/live-agent-6553250/idle-harvest-local-study.json",
    )
    args = parser.parse_args()
    if args.seeds < 0:
        raise SystemExit("--seeds cannot be negative")
    if not 1 <= args.jobs <= 8:
        raise SystemExit("--jobs must be between 1 and 8")

    with tempfile.TemporaryDirectory(prefix="idle-harvest-study-") as directory:
        temp = Path(directory)
        baseline = temp / "baseline"
        candidate = temp / "candidate"
        probe = temp / "probe"
        compile_source(BASELINE_SOURCE, baseline, "idle_harvest_baseline")
        compile_source(CANDIDATE_SOURCE, candidate, "idle_harvest_candidate")
        compile_source(PROBE_SOURCE, probe, "idle_harvest_probe")

        fixed = fixed_stream_result(baseline, candidate, probe)
        start_turn = fixed["first_action_divergence"]["turn"]
        rollout_baseline = rollout_one(probe, start_turn)
        rollout_candidate = rollout_one(candidate, start_turn)
        fixed["rollout"] = {
            "start_turn": start_turn,
            "baseline": rollout_baseline,
            "candidate": rollout_candidate,
            "score_delta": rollout_baseline["score"] - rollout_candidate["score"],
        }
        print(
            f"fixture: first divergence t{start_turn}, "
            f"score delta {fixed['rollout']['score_delta']:+d}",
            flush=True,
        )

        seeds = list(range(args.seed_start, args.seed_start + args.seeds))
        rows = []
        with ThreadPoolExecutor(max_workers=args.jobs) as executor:
            futures = {
                executor.submit(paired_row, seed, probe, candidate): seed for seed in seeds
            }
            for future in as_completed(futures):
                row = future.result()
                rows.append(row)
                counts = row["probe_event_counts"]
                print(
                    f"seed {row['seed']}: paired margin {row['paired_margin']:+.1f}, "
                    f"select={counts['select']} orchard={counts['orchard_force']}",
                    flush=True,
                )
        rows.sort(key=lambda row: row["seed"])

    activated = [row for row in rows if row["probe_event_counts"]["select"]]
    payload = {
        "schema": 1,
        "scope": "causal fixture plus local deterministic simulator; not an arena predictor",
        "sources": {
            "baseline": str(BASELINE_SOURCE.relative_to(REPO)),
            "candidate": str(CANDIDATE_SOURCE.relative_to(REPO)),
            "probe": str(PROBE_SOURCE.relative_to(REPO)),
        },
        "fixed_fixture": fixed,
        "paired": {
            "seed_start": args.seed_start,
            "seeds": args.seeds,
            "activated_seeds": len(activated),
            "mean_paired_margin_all": (
                sum(row["paired_margin"] for row in rows) / len(rows) if rows else None
            ),
            "mean_paired_margin_activated": (
                sum(row["paired_margin"] for row in activated) / len(activated)
                if activated
                else None
            ),
            "rows": rows,
        },
    }
    save(args.output, payload)
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
