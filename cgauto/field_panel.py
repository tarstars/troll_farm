#!/usr/bin/env python3
"""Run a throttle-safe baseline/candidate panel against fixed Legend agents.

This uses CodinGame's read/write-neutral ``TestSession/play`` endpoint. It plays IDE code in
controlled games but never submits either source to the arena. A single invocation is capped at
12 games; on HTTP 422, an empty result, or any other request error it stops immediately and saves
the partial result.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
SESSION = REPO / "cgauto" / "cg_session.txt"
TSH = "77167730956ef53402472b3c52474908f5b73026"
PLAY_URL = "https://www.codingame.com/services/TestSession/play"
MAX_BURST = 12

TOP_FIVE = {
    "delineate": 6479768,
    "wala": 6481141,
    "escdemon": 6483545,
    "norxondor": 6480540,
    "laconic": 6482055,
}


class PanelStop(RuntimeError):
    """The panel must stop without issuing another external request."""


def cookie() -> str:
    values = []
    for line in SESSION.read_text().splitlines():
        line = line.strip()
        if line.startswith("rememberMe=") and "PASTE" not in line:
            values.append(line)
    if not values:
        raise RuntimeError(f"no usable rememberMe cookie in {SESSION}")
    return "; ".join(values)


def build_jobs(opponents: dict[str, int], games_per_cell: int) -> list[dict]:
    jobs = []
    for repetition in range(games_per_cell):
        for opponent, agent_id in opponents.items():
            for bot in ("baseline", "candidate"):
                jobs.append(
                    {
                        "repetition": repetition,
                        "opponent": opponent,
                        "opponent_agent": agent_id,
                        "bot": bot,
                    }
                )
    return jobs


def validate_seed_blocks(payload: dict) -> list[dict]:
    blocks = payload.get("blocks") if isinstance(payload, dict) else None
    if not isinstance(blocks, list) or not blocks:
        raise ValueError("seed bank must contain a non-empty 'blocks' list")
    validated = []
    identities = set()
    for index, block in enumerate(blocks):
        if not isinstance(block, dict):
            raise ValueError(f"seed block {index} is not an object")
        opponent = str(block.get("opponent") or "").lower()
        if opponent not in TOP_FIVE:
            raise ValueError(f"seed block {index} has unknown opponent {opponent!r}")
        agent_id = block.get("opponent_agent")
        if agent_id != TOP_FIVE[opponent]:
            raise ValueError(
                f"seed block {index} agent {agent_id!r} != frozen {TOP_FIVE[opponent]}"
            )
        seed = block.get("seed")
        if not isinstance(seed, int) or isinstance(seed, bool) or not -(2**63) <= seed < 2**63:
            raise ValueError(f"seed block {index} is not a signed int64")
        identity = (opponent, seed)
        if identity in identities:
            raise ValueError(f"duplicate seed block {identity}")
        identities.add(identity)
        validated.append(
            {"opponent": opponent, "opponent_agent": agent_id, "seed": seed}
        )
    return validated


def build_seeded_jobs(blocks: list[dict]) -> list[dict]:
    jobs = []
    for block_index, block in enumerate(blocks):
        for bot in ("baseline", "candidate"):
            jobs.append(
                {
                    "block": block_index,
                    "repetition": 0,
                    **block,
                    "bot": bot,
                }
            )
    return jobs


def final_inventory(frames: list[dict], player: int) -> list[int] | None:
    for frame in reversed(frames):
        match = re.search(r'"inputmodule":"([^"]+)"', frame.get("view") or "")
        if not match:
            continue
        lines = match.group(1).split("\\n")
        if len(lines) <= player:
            continue
        fields = lines[player].split()
        if len(fields) == 6:
            try:
                return [int(value) for value in fields]
            except ValueError:
                pass
    return None


def input_unit_counts(frame: dict) -> list[int] | None:
    """Decode per-player unit counts from a referee inputmodule frame when present."""

    match = re.search(r'"inputmodule":"([^"]+)"', frame.get("view") or "")
    if not match:
        return None
    lines = match.group(1).split("\\n")
    try:
        if len(lines) < 4:
            return None
        tree_count = int(lines[2])
        unit_count_index = 3 + tree_count
        unit_count = int(lines[unit_count_index])
        unit_lines = lines[unit_count_index + 1 : unit_count_index + 1 + unit_count]
        if len(unit_lines) != unit_count:
            return None
        counts = [0, 0]
        for line in unit_lines:
            fields = line.split()
            if len(fields) != 14:
                return None
            player = int(fields[1])
            if player not in (0, 1):
                return None
            counts[player] += 1
        return counts
    except (IndexError, ValueError):
        return None


def workforce_metrics(frames: list[dict]) -> dict:
    successful_turns = [[], []]
    turn = 1
    for frame in frames[1:]:
        for match in re.finditer(r"\$([01]): trained a troll", frame.get("summary") or ""):
            successful_turns[int(match.group(1))].append(turn)
        if frame.get("keyframe"):
            turn += 1
    snapshots = [counts for frame in frames if (counts := input_unit_counts(frame))]
    if snapshots:
        return {
            "source": "inputmodule",
            "snapshots": len(snapshots),
            "training_events": [len(turns) for turns in successful_turns],
            "training_turns": successful_turns,
            "max": [
                max((counts[player] for counts in snapshots), default=None)
                for player in (0, 1)
            ],
            "final": snapshots[-1],
        }

    # Production replays expose only the two inventories in their visualization inputmodule,
    # but the referee summary records each successful (not merely attempted) TRAIN action.
    trained = [len(turns) for turns in successful_turns]
    workforce = [1 + count for count in trained]
    return {
        "source": "referee_summary",
        "snapshots": 0,
        "training_events": trained,
        "training_turns": successful_turns,
        "max": workforce,
        "final": workforce,
    }


def runtime_diagnostics(frames: list[dict], player: int = 0) -> list[str]:
    diagnostics = []
    for frame in frames:
        if frame.get("agentId") != player:
            continue
        for key in ("stderr", "error"):
            value = frame.get(key)
            if value:
                diagnostics.append(f"{key}: {str(value)[:500]}")
    return diagnostics


def stdout_stream(frames: list[dict], player: int) -> list[str]:
    """Retain every stdout frame so controlled-game evidence survives replay expiry."""

    return [
        str(frame["stdout"])
        for frame in frames
        if frame.get("agentId") == player and frame.get("stdout") is not None
    ]


def stream_sha256(stream: list[str]) -> str:
    canonical = json.dumps(stream, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def trace_evidence(result: dict) -> dict:
    """Preserve compact causal evidence directly from a TestSession response."""

    frames = result.get("frames") or []
    streams = [stdout_stream(frames, player) for player in (0, 1)]
    turn_one = None
    turn_one_error = None
    try:
        # Import lazily so pure payload/unit tests do not need replay-state machinery.
        from cgauto.arena_rollout_forensics import render_turn_one

        turn_one = render_turn_one(result, 0)
    except Exception as error:  # noqa: BLE001 - preserve evidence for every decoder failure
        turn_one_error = f"{type(error).__name__}: {str(error)[:200]}"
    return {
        "agents": [
            {
                "index": agent.get("index"),
                "agent_id": agent.get("agentId"),
                "user_id": (agent.get("codingamer") or {}).get("userId"),
                "pseudo": (agent.get("codingamer") or {}).get("pseudo"),
            }
            for agent in (result.get("agents") or [])
        ],
        "turn_one": (
            {
                "text": turn_one,
                "bytes": len(turn_one.encode()),
                "sha256": hashlib.sha256(turn_one.encode()).hexdigest(),
            }
            if turn_one is not None
            else None
        ),
        "turn_one_error": turn_one_error,
        "stdout": [
            {
                "frames": len(stream),
                "sha256": stream_sha256(stream),
                "stream": stream,
            }
            for stream in streams
        ],
    }


def command_metrics(frames: list[dict], player: int = 0) -> dict:
    """Summarize commands and retain turn numbers for behavior-gate actions."""

    counts: Counter[str] = Counter()
    harvest_turns = []
    train_attempts = []
    announcements = []
    turn = 1
    for frame in frames[1:]:
        if frame.get("agentId") == player and frame.get("stdout"):
            for command in re.split(r"[;\n]", frame["stdout"]):
                fields = command.strip().split()
                if not fields:
                    continue
                verb = fields[0].upper()
                counts[verb] += 1
                if verb == "HARVEST":
                    harvest_turns.append(turn)
                elif verb == "TRAIN":
                    train_attempts.append({"turn": turn, "spec": fields[1:5]})
                elif verb == "MSG":
                    announcements.append(" ".join(fields[1:]))
        if frame.get("keyframe"):
            turn += 1
    return {
        "counts": dict(counts),
        "harvest_turns": harvest_turns,
        "train_attempts": train_attempts,
        "announcements": announcements,
    }


def build_play_body(code: str, opponent_agent: int, game_options: str = "") -> dict:
    """Build the exact TestSession payload, including an optional referee seed."""

    return {
        "code": code,
        "programmingLanguageId": "Rust",
        "multi": {"agentsIds": [-1, opponent_agent], "gameOptions": game_options},
    }


def validate_play_result(result: dict, requested_game_options: str = "") -> None:
    if not result.get("scores") or len(result["scores"]) != 2:
        raise PanelStop("degenerate game: response has no two-player scores")
    if requested_game_options and result.get("refereeInput") != requested_game_options:
        raise PanelStop(
            "game-options echo mismatch: "
            f"requested {requested_game_options!r}, got {result.get('refereeInput')!r}"
        )


def play(code: str, opponent_agent: int, game_options: str = "") -> dict:
    body = build_play_body(code, opponent_agent, game_options)
    request = urllib.request.Request(
        PLAY_URL,
        data=json.dumps([TSH, body]).encode(),
        headers={
            "Content-Type": "application/json",
            "Cookie": cookie(),
            "User-Agent": "Mozilla/5.0",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            result = json.loads(response.read().decode())
    except urllib.error.HTTPError as error:
        detail = error.read().decode(errors="replace")[:200]
        raise PanelStop(f"HTTP {error.code}: {detail}") from error
    except Exception as error:  # noqa: BLE001 - stop safely on every transport failure
        raise PanelStop(f"{type(error).__name__}: {str(error)[:200]}") from error
    validate_play_result(result, game_options)
    return result


def result_row(job: dict, result: dict) -> dict:
    frames = result.get("frames", [])
    inventories = [final_inventory(frames, player) for player in (0, 1)]
    scores = result["scores"]
    return {
        **job,
        "game_id": result.get("gameId"),
        "referee_input": result.get("refereeInput"),
        "scores": scores,
        "win": scores[0] > scores[1],
        "inventories": inventories,
        "wood": [inv[5] if inv else None for inv in inventories],
        "fruit": [sum(inv[:4]) if inv else None for inv in inventories],
        "turns": max(0, sum(1 for frame in frames if frame.get("keyframe")) - 1),
        "commands": command_metrics(frames),
        "workforce": workforce_metrics(frames),
        "diagnostics": runtime_diagnostics(frames),
        "trace": trace_evidence(result),
    }


def save(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=1) + "\n")
    temporary.replace(path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--games-per-cell", type=int, default=1)
    parser.add_argument(
        "--opponents",
        default=",".join(TOP_FIVE),
        help=f"comma-separated names from: {', '.join(TOP_FIVE)}",
    )
    parser.add_argument("--sleep", type=float, default=1.0)
    game_options = parser.add_mutually_exclusive_group()
    game_options.add_argument(
        "--seed",
        type=int,
        help="signed referee seed; sends gameOptions as 'seed=<value>\\n' for every game",
    )
    game_options.add_argument(
        "--seed-bank",
        type=Path,
        help="JSON bank of opponent/opponent_agent/seed blocks; runs baseline and candidate per block",
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    names = [name.strip().lower() for name in args.opponents.split(",") if name.strip()]
    unknown = [name for name in names if name not in TOP_FIVE]
    if unknown:
        raise SystemExit(f"unknown opponent(s): {', '.join(unknown)}")
    if args.games_per_cell < 1:
        raise SystemExit("--games-per-cell must be positive")
    game_options = f"seed={args.seed}\n" if args.seed is not None else ""
    seed_bank = None
    if args.seed_bank:
        bank_text = args.seed_bank.read_text()
        try:
            blocks = validate_seed_blocks(json.loads(bank_text))
        except (ValueError, json.JSONDecodeError) as error:
            raise SystemExit(f"invalid --seed-bank: {error}") from error
        jobs = build_seeded_jobs(blocks)
        seed_bank = {
            "path": str(args.seed_bank),
            "sha256": hashlib.sha256(bank_text.encode()).hexdigest(),
            "blocks": blocks,
        }
    else:
        opponents = {name: TOP_FIVE[name] for name in names}
        jobs = build_jobs(opponents, args.games_per_cell)
    if len(jobs) > MAX_BURST:
        raise SystemExit(
            f"refusing {len(jobs)} games in one burst (maximum {MAX_BURST}); "
            "split the opponent list or use separate runs"
        )

    paths = {"baseline": args.baseline, "candidate": args.candidate}
    codes = {name: path.read_text() for name, path in paths.items()}
    for name, code in codes.items():
        if len(code) > 100_000:
            raise SystemExit(f"{name} source is {len(code)} bytes (>100000)")
    now = datetime.now(timezone.utc)
    output = args.output or (
        REPO / "data" / "panels" / f"top5-ab-{now.strftime('%Y%m%dT%H%M%SZ')}.json"
    )
    payload = {
        "schema": 1,
        "started_at": now.isoformat(),
        "completed_at": None,
        "status": "dry-run" if args.dry_run else "running",
        "requested_game_options": game_options,
        "seed_bank": seed_bank,
        "sources": {
            name: {
                "path": str(path),
                "bytes": len(codes[name]),
                "sha256": hashlib.sha256(codes[name].encode()).hexdigest(),
            }
            for name, path in paths.items()
        },
        "jobs": jobs,
        "rows": [],
        "stop_reason": None,
    }
    save(output, payload)
    print(f"panel: {len(jobs)} controlled games -> {output}")
    if args.dry_run:
        for job in jobs:
            suffix = f" seed={job['seed']}" if "seed" in job else ""
            print(
                f"DRY {job['bot']:<9} vs {job['opponent']} "
                f"({job['opponent_agent']}){suffix}"
            )
        return 0

    for index, job in enumerate(jobs, 1):
        print(
            f"game {index}/{len(jobs)}: {job['bot']} vs {job['opponent']} "
            f"({job['opponent_agent']})",
            flush=True,
        )
        try:
            job_game_options = (
                f"seed={job['seed']}\n" if "seed" in job else game_options
            )
            result = play(
                codes[job["bot"]], job["opponent_agent"], job_game_options
            )
        except PanelStop as error:
            payload["status"] = "stopped"
            payload["stop_reason"] = str(error)
            payload["completed_at"] = datetime.now(timezone.utc).isoformat()
            save(output, payload)
            print(f"STOP: {error}", file=sys.stderr)
            return 75
        row = result_row(job, result)
        payload["rows"].append(row)
        if job_game_options and (row.get("trace") or {}).get("turn_one_error"):
            payload["status"] = "stopped"
            payload["stop_reason"] = "seeded capability game lacked turn-one trace evidence"
            payload["completed_at"] = datetime.now(timezone.utc).isoformat()
            save(output, payload)
            print(f"STOP: {payload['stop_reason']}", file=sys.stderr)
            return 75
        if job_game_options and row["diagnostics"]:
            payload["status"] = "stopped"
            payload["stop_reason"] = "seeded capability game produced player-0 diagnostics"
            payload["completed_at"] = datetime.now(timezone.utc).isoformat()
            save(output, payload)
            print(f"STOP: {payload['stop_reason']}", file=sys.stderr)
            return 75
        save(output, payload)
        print(
            f"  score {row['scores'][0]}-{row['scores'][1]} "
            f"wood {row['wood'][0]}-{row['wood'][1]} game={row['game_id']}",
            flush=True,
        )
        if index < len(jobs):
            time.sleep(args.sleep)

    payload["status"] = "complete"
    payload["completed_at"] = datetime.now(timezone.utc).isoformat()
    save(output, payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
