#!/usr/bin/env python3
"""Freeze the E7a live-parity inputs and baseline outputs for offline use.

This builder is the only component that contacts Codingame.  The resulting gzip packet
contains the 25 teacher-forced transcripts selected by the frozen audit and the exact live
baseline output for every turn.  Consumers can therefore test later candidates without
platform credentials or a replay cache.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile


REPO = Path(__file__).resolve().parents[2]
AUDIT_SHA256 = "8c29f433982fa9df05e16203bccdc15f290bae36ff5801084e862a882547af5a"
BASELINE = REPO / "cgauto/submissions/candidate-agent6553250-preseed-e7a-lemon-near-tie.min.rs"
BASELINE_SHA256 = "97bfe71e3f2f05e1b8fa3c697c5e5db3624ac9739e90954e9fa9be79a8e48595"
SACRED = REPO / "rust/src/bin/yamo_orchard_live.rs"
SACRED_SHA256 = "fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f"
SHARED_PATH = (
    REPO
    / "local_codex_1/e7a-half-size-logical-simplification/"
    "evaluate_live_period2_counterexamples.py"
)
SCHEMA = "troll-farm-e7a-live-command-parity-offline-packet-v1"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_sha256(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def load_shared():
    specification = importlib.util.spec_from_file_location(
        "e7a_offline_packet_shared", SHARED_PATH
    )
    if specification is None or specification.loader is None:
        raise RuntimeError("cannot load shared live-state decoder")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def run_baseline(binary: Path, payload: str, turns: int, game_id: int, shared) -> str:
    completed = subprocess.run(
        [str(binary)],
        cwd=REPO,
        input=payload,
        text=True,
        capture_output=True,
        timeout=30,
    )
    if completed.returncode:
        raise RuntimeError(
            f"baseline exited {completed.returncode} on {game_id}: "
            f"{completed.stderr[:1000]}"
        )
    if completed.stderr:
        raise RuntimeError(f"baseline stderr on {game_id}: {completed.stderr[:1000]}")
    lines = completed.stdout.splitlines()
    if len(lines) != turns:
        raise RuntimeError(f"command coverage mismatch on {game_id}: {len(lines)} != {turns}")
    for line in lines:
        shared.parse_commands(line)
    return "\n".join(lines) + "\n"


def freeze_game(binary: Path, selected: dict, shared) -> dict:
    game_id = int(selected["game_id"])
    seat = int(selected["seat"])
    game = shared.arena.call("gameResult/findByGameId", [game_id, None])
    if int(game.get("gameId", -1)) != game_id:
        raise RuntimeError(f"game identity mismatch for {game_id}")
    agents = game.get("agents") or []
    own = [agent for agent in agents if int(agent.get("agentId", -1)) == shared.AGENT_ID]
    if len(own) != 1 or int(own[0].get("index", -1)) != seat:
        raise RuntimeError(f"agent/seat identity mismatch for {game_id}")

    parser = shared.corpus_parser()
    _map0, _units0, inventory0, inventory1 = parser.parse_frame0(
        game["frames"][0]["view"]
    )
    trajectory, _final_inventory = parser.extract_turns(
        game["frames"], inventory0, inventory1
    )
    map_data, states, unknown_updates = shared.decoded_states(game, trajectory)
    usable = min(len(states) - 1, len(trajectory))
    payload = shared.transcript(map_data, states, seat, usable)
    expected_output = run_baseline(binary, payload, usable, game_id, shared)
    baseline_lines = expected_output.splitlines()
    return {
        "game_id": game_id,
        "seat": seat,
        "opponent": selected["opponent"],
        "turns": usable,
        "unknown_diff_updates": unknown_updates,
        "transcript": payload,
        "transcript_sha256": text_sha256(payload),
        "baseline_output": expected_output,
        "baseline_output_sha256": text_sha256(expected_output),
        "baseline_maximum_period2": shared.longest_period2(baseline_lines),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    audit = args.audit.resolve()
    output = args.output.resolve()

    if output.exists():
        parser.error("refusing to overwrite offline parity packet")
    if sha256(audit) != AUDIT_SHA256:
        raise RuntimeError("frozen audit hash mismatch")
    if sha256(BASELINE) != BASELINE_SHA256:
        raise RuntimeError("exact live baseline hash mismatch")
    if sha256(SACRED) != SACRED_SHA256:
        raise RuntimeError("sacred source hash mismatch")

    shared = load_shared()
    selected = shared.select_rows(json.loads(audit.read_text()))
    with tempfile.TemporaryDirectory(prefix="e7a-offline-packet-") as directory:
        binary = shared.compile_candidate(Path(directory), BASELINE, BASELINE_SHA256)
        rows = [freeze_game(binary, row, shared) for row in selected]

    if len(rows) != 25 or sum(row["turns"] for row in rows) != 7_234:
        raise RuntimeError("unexpected frozen packet coverage")
    if any(row["unknown_diff_updates"] != 0 for row in rows):
        raise RuntimeError("cannot freeze packet with unknown state updates")

    packet = {
        "schema": SCHEMA,
        "evidence_boundary": (
            "teacher-forced exact public live states and frozen exact-baseline commands; "
            "proves equality on this packet, not counterfactual value"
        ),
        "selection": {
            "audit_path": str(audit.relative_to(REPO)),
            "audit_sha256": AUDIT_SHA256,
            "agent_id": shared.AGENT_ID,
            "submission_id": shared.SUBMISSION_ID,
            "required_game": shared.REQUIRED_GAME,
            "games": len(rows),
        },
        "baseline": {
            "path": str(BASELINE.relative_to(REPO)),
            "bytes": BASELINE.stat().st_size,
            "sha256": BASELINE_SHA256,
        },
        "sacred_sha256": SACRED_SHA256,
        "metrics": {
            "games": len(rows),
            "turns": sum(row["turns"] for row in rows),
            "maximum_period2": max(row["baseline_maximum_period2"] for row in rows),
            "unknown_diff_updates": sum(row["unknown_diff_updates"] for row in rows),
        },
        "rows": rows,
    }
    payload = (json.dumps(packet, sort_keys=True, separators=(",", ":")) + "\n").encode()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(gzip.compress(payload, compresslevel=9, mtime=0))
    print(
        json.dumps(
            {
                "packet": str(output),
                "sha256": sha256(output),
                "compressed_bytes": output.stat().st_size,
                **packet["metrics"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
