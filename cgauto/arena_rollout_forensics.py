#!/usr/bin/env python3
"""Reconstruct the frozen rollout selector on archived arena replays.

The CodinGame battle list is submission-scoped and old lists disappear after a
replacement submission lands.  This tool therefore consumes an explicit game-id
manifest, downloads those immutable game results, rebuilds the exact turn-one
input, and runs an instrumented copy of the frozen candidate locally.  The probe
changes only stderr: stdout must still match the command recorded by the arena.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import statistics
import subprocess
import sys
import tempfile
import time


REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.battles import USERID, call  # noqa: E402
from cgauto.replay_state import DiffDecoder, view_payload  # noqa: E402


DEFAULT_MANIFEST = (
    REPO
    / "data/analysis/live-agent-6553250/compact-gold-rollout-arena-known-games-2026-07-18.json"
)
DEFAULT_CANDIDATE = (
    REPO
    / "cgauto/submissions/candidate-agent6553250-compact-gold-rollout30.min.rs"
)
SELECT_EXPRESSION = (
    "Some(if rollout::select(&view){SecureOrchardBot::max_bank_first_hp0()}"
    "else{SecureOrchardBot::new()});}"
)
PROBE_EXPRESSION = (
    'Some(if rollout::select(&view){eprintln!("ROLLOUT_OPTION");'
    "SecureOrchardBot::max_bank_first_hp0()}else{"
    'eprintln!("ROLLOUT_CONTROL");SecureOrchardBot::new()});}'
)


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text)
    temporary.replace(path)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def instrument_source(source: str) -> str:
    if source.count(SELECT_EXPRESSION) != 1:
        raise ValueError("candidate selector expression is not unique")
    return source.replace(SELECT_EXPRESSION, PROBE_EXPRESSION)


def initial_replay_state(result: dict) -> tuple[dict, dict]:
    initial = view_payload(result["frames"][0]["view"])
    if initial is None:
        raise ValueError(f"game {result['gameId']} has no initial replay payload")
    header, *rows = initial["global"]["inputmodule"].splitlines()
    width, height = (int(value) for value in header.split())
    if len(rows) != height:
        raise ValueError(f"game {result['gameId']} has an incomplete map")
    decoder = DiffDecoder()
    decoder.apply(initial["frame"].get("diff", ""), 0)
    inventories = [
        [int(value) for value in line.split()]
        for line in initial["frame"]["inputmodule"].splitlines()
    ]
    return (
        {"width": width, "height": height, "rows": rows},
        decoder.snapshot(0, inventories),
    )


def render_turn_one(result: dict, seat: int) -> str:
    map_data, state = initial_replay_state(result)
    rows = list(map_data["rows"])
    if seat == 1:
        rows = [
            row.translate(str.maketrans({"0": "1", "1": "0"})) for row in rows
        ]
    lines = [f"{map_data['width']} {map_data['height']}", *rows]
    lines.extend(
        " ".join(map(str, state["inventories"][player]))
        for player in (seat, 1 - seat)
    )
    lines.append(str(len(state["plants"])))
    lines.extend(
        f"{plant['type']} {plant['x']} {plant['y']} {plant['size']} "
        f"{plant['health']} {plant['fruits']} {plant['cooldown']}"
        for plant in state["plants"]
    )
    lines.append(str(len(state["units"])))
    for unit in state["units"]:
        relative_player = 0 if unit["player"] == seat else 1
        values = (
            unit["id"],
            relative_player,
            unit["x"],
            unit["y"],
            unit["ms"],
            unit["cc"],
            unit["hp"],
            unit["chop"],
            *unit["carry"],
        )
        lines.append(" ".join(map(str, values)))
    return "\n".join(lines) + "\n"


def observed_first_stdout(result: dict, seat: int) -> str:
    for frame in result["frames"]:
        if str(frame.get("agentId")) == str(seat) and frame.get("stdout"):
            return frame["stdout"]
    raise ValueError(f"game {result['gameId']} has no recorded first command for seat {seat}")


def compile_probe(source: Path, binary: Path) -> None:
    compiled = subprocess.run(
        [
            "rustc",
            "--edition=2021",
            "-O",
            "-Awarnings",
            "--crate-name",
            "arena_rollout_probe",
            "-",
            "-o",
            str(binary),
        ],
        input=instrument_source(source.read_text()),
        text=True,
        capture_output=True,
        timeout=60,
    )
    if compiled.returncode:
        raise RuntimeError(f"rollout probe compilation failed: {compiled.stderr[:2000]}")


def candidate_seat(result: dict, candidate_agent: int) -> int:
    matches = [
        agent["index"]
        for agent in result.get("agents") or []
        if agent.get("agentId") == candidate_agent
        and (agent.get("codingamer") or {}).get("userId") == USERID
    ]
    if len(matches) != 1:
        raise ValueError(
            f"game {result['gameId']} has {len(matches)} candidate-agent matches"
        )
    return matches[0]


def selection_marker(stderr: str) -> str:
    option = "ROLLOUT_OPTION" in stderr
    control = "ROLLOUT_CONTROL" in stderr
    if option == control:
        return "unknown"
    return "option" if option else "control"


def analyze_game(
    result: dict, *, candidate_agent: int, window: str, binary: Path
) -> tuple[dict, str]:
    seat = candidate_seat(result, candidate_agent)
    input_text = render_turn_one(result, seat)
    observed = observed_first_stdout(result, seat)
    started = time.perf_counter()
    probe = subprocess.run(
        [binary],
        input=input_text,
        text=True,
        capture_output=True,
        timeout=3,
    )
    elapsed_ms = (time.perf_counter() - started) * 1000
    if probe.returncode:
        raise RuntimeError(
            f"game {result['gameId']} probe exited {probe.returncode}: {probe.stderr[:500]}"
        )
    opponent = next(agent for agent in result["agents"] if agent["index"] != seat)
    row = {
        "game_id": result["gameId"],
        "window": window,
        "seat": seat,
        "selection": selection_marker(probe.stderr),
        "stdout_exact": probe.stdout == observed,
        "elapsed_ms": elapsed_ms,
        "won": result["ranks"][seat] == 0,
        "margin": result["scores"][seat] - result["scores"][1 - seat],
        "scores": result["scores"],
        "opponent": (opponent.get("codingamer") or {}).get("pseudo"),
        "opponent_agent": opponent.get("agentId"),
        "observed_first_command": observed.rstrip("\r\n"),
        "reproduced_first_command": probe.stdout.rstrip("\r\n"),
    }
    return row, f"SEED {result['gameId']}\n{input_text}"


def outcome_summary(rows: list[dict]) -> dict:
    if not rows:
        return {"games": 0, "wins": 0, "mean_margin": None, "median_margin": None}
    margins = [row["margin"] for row in rows]
    return {
        "games": len(rows),
        "wins": sum(row["won"] for row in rows),
        "mean_margin": statistics.mean(margins),
        "median_margin": statistics.median(margins),
        "minimum_margin": min(margins),
        "maximum_margin": max(margins),
    }


def manifest_records(manifest: dict) -> list[tuple[int, str]]:
    records = []
    seen = set()
    for window in manifest["windows"]:
        for game_id in window["game_ids"]:
            if game_id in seen:
                raise ValueError(f"duplicate game id {game_id}")
            seen.add(game_id)
            records.append((game_id, window["name"]))
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--candidate", type=Path, default=DEFAULT_CANDIDATE)
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dataset-output", type=Path)
    args = parser.parse_args()
    if not 1 <= args.jobs <= 32:
        raise SystemExit("--jobs must be between 1 and 32")

    manifest = json.loads(args.manifest.read_text())
    records = manifest_records(manifest)
    candidate_agent = int(manifest["candidate_agent_id"])

    def fetch(record: tuple[int, str]) -> tuple[int, str, dict]:
        game_id, window = record
        return game_id, window, call("gameResult/findByGameId", [game_id, None])

    with ThreadPoolExecutor(max_workers=args.jobs) as executor:
        fetched = list(executor.map(fetch, records))

    with tempfile.TemporaryDirectory(prefix="arena-rollout-forensics-") as directory:
        binary = Path(directory) / "rollout-probe"
        compile_probe(args.candidate, binary)

        def analyze(item: tuple[int, str, dict]) -> tuple[dict, str]:
            _game_id, window, result = item
            return analyze_game(
                result,
                candidate_agent=candidate_agent,
                window=window,
                binary=binary,
            )

        with ThreadPoolExecutor(max_workers=args.jobs) as executor:
            analyzed = list(executor.map(analyze, fetched))

    rows = sorted((row for row, _record in analyzed), key=lambda row: row["game_id"])
    dataset_records = {
        row["game_id"]: record
        for row, record in analyzed
    }
    exact = sum(row["stdout_exact"] for row in rows)
    if exact != len(rows):
        raise RuntimeError(f"only {exact}/{len(rows)} arena commands reproduced exactly")
    unknown = [row["game_id"] for row in rows if row["selection"] == "unknown"]
    if unknown:
        raise RuntimeError(f"missing selector marker for games {unknown}")

    by_selection = {
        selection: outcome_summary(
            [row for row in rows if row["selection"] == selection]
        )
        for selection in ("control", "option")
    }
    payload = {
        "schema": 1,
        "scope": (
            "observational arena replay forensics; two explicitly captured 30-game "
            "windows from the rejected candidate; not a paired counterfactual estimate"
        ),
        "manifest": str(args.manifest.relative_to(REPO)),
        "candidate": {
            "path": str(args.candidate.relative_to(REPO)),
            "sha256": digest(args.candidate),
            "agent_id": candidate_agent,
        },
        "sample_games": len(rows),
        "candidate_total_valid_games_at_audit": manifest.get(
            "candidate_total_valid_games_at_audit"
        ),
        "stdout_exact_games": exact,
        "selection_counts": {
            selection: sum(row["selection"] == selection for row in rows)
            for selection in ("control", "option")
        },
        "by_selection": by_selection,
        "option_games": [row for row in rows if row["selection"] == "option"],
        "rows": rows,
        "interpretation_limit": (
            "Selection is reconstructed exactly, but outcomes are observational.  Maps "
            "selected by the rollout may be intrinsically harder, and the unobserved "
            "control counterfactual against each arena opponent is unavailable."
        ),
    }
    atomic_write(args.output, json.dumps(payload, indent=1) + "\n")
    if args.dataset_output:
        atomic_write(
            args.dataset_output,
            "".join(dataset_records[row["game_id"]] for row in rows),
        )
    print(
        f"PASS: {exact}/{len(rows)} commands exact; "
        f"option={by_selection['option']}; control={by_selection['control']}"
    )
    print(f"saved {args.output}")
    if args.dataset_output:
        print(f"saved {args.dataset_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
