#!/usr/bin/env python3
"""Prove exact live-state command parity for the single-deletion candidate."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile


REPO = Path(__file__).resolve().parents[2]
BASELINE = REPO / "cgauto/submissions/candidate-agent6553250-preseed-e7a-lemon-near-tie.min.rs"
BASELINE_SHA256 = "97bfe71e3f2f05e1b8fa3c697c5e5db3624ac9739e90954e9fa9be79a8e48595"
SACRED = REPO / "rust/src/bin/yamo_orchard_live.rs"
SACRED_SHA256 = "fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f"
SHARED_PATH = (
    REPO
    / "local_codex_1/e7a-half-size-logical-simplification/"
    "evaluate_live_period2_counterexamples.py"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_shared():
    specification = importlib.util.spec_from_file_location(
        "e7a_single_delete_live_shared", SHARED_PATH
    )
    if specification is None or specification.loader is None:
        raise RuntimeError("cannot load shared live-state decoder")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def run(binary: Path, payload: str, turns: int, game_id: int, shared) -> list[str]:
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
            f"source exited {completed.returncode} on {game_id}: "
            f"{completed.stderr[:1000]}"
        )
    if completed.stderr:
        raise RuntimeError(f"source stderr on {game_id}: {completed.stderr[:1000]}")
    lines = completed.stdout.splitlines()
    if len(lines) != turns:
        raise RuntimeError(f"command coverage mismatch on {game_id}: {len(lines)} != {turns}")
    for line in lines:
        shared.parse_commands(line)
    return lines


def compare_game(baseline: Path, candidate: Path, selected: dict, shared) -> dict:
    game_id = int(selected["game_id"])
    seat = int(selected["seat"])
    game = shared.arena.call("gameResult/findByGameId", [game_id, None])
    if int(game.get("gameId", -1)) != game_id:
        raise RuntimeError(f"game identity mismatch for {game_id}")
    agents = game.get("agents") or []
    own = [
        agent
        for agent in agents
        if int(agent.get("agentId", -1)) == shared.AGENT_ID
    ]
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
    baseline_lines = run(baseline, payload, usable, game_id, shared)
    candidate_lines = run(candidate, payload, usable, game_id, shared)
    exact = baseline_lines == candidate_lines
    first_difference = next(
        (
            turn
            for turn, (left, right) in enumerate(
                zip(baseline_lines, candidate_lines), 1
            )
            if left != right
        ),
        None,
    )
    return {
        "game_id": game_id,
        "seat": seat,
        "opponent": selected["opponent"],
        "turns": usable,
        "unknown_diff_updates": unknown_updates,
        "exact_command_lines": exact,
        "first_different_turn": first_difference,
        "baseline_output_sha256": hashlib.sha256(
            ("\n".join(baseline_lines) + "\n").encode()
        ).hexdigest(),
        "candidate_output_sha256": hashlib.sha256(
            ("\n".join(candidate_lines) + "\n").encode()
        ).hexdigest(),
        "baseline_maximum_period2": shared.longest_period2(baseline_lines),
        "candidate_maximum_period2": shared.longest_period2(candidate_lines),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--candidate-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    audit = args.audit.resolve()
    candidate = args.candidate.resolve()
    output = args.output.resolve()

    if output.exists():
        parser.error("refusing to overwrite live parity evidence")
    if sha256(BASELINE) != BASELINE_SHA256:
        raise RuntimeError("exact live baseline hash mismatch")
    if sha256(SACRED) != SACRED_SHA256:
        raise RuntimeError("sacred source hash mismatch")
    if sha256(candidate) != args.candidate_sha256:
        raise RuntimeError("candidate hash mismatch")

    shared = load_shared()
    selected = shared.select_rows(json.loads(audit.read_text()))
    with tempfile.TemporaryDirectory(prefix="e7a-single-delete-live-") as directory:
        temp = Path(directory)
        baseline_dir = temp / "baseline"
        candidate_dir = temp / "candidate"
        baseline_dir.mkdir()
        candidate_dir.mkdir()
        baseline_binary = shared.compile_candidate(
            baseline_dir, BASELINE, BASELINE_SHA256
        )
        candidate_binary = shared.compile_candidate(
            candidate_dir, candidate, args.candidate_sha256
        )
        rows = [
            compare_game(baseline_binary, candidate_binary, row, shared)
            for row in selected
        ]

    gates = {
        "all_25_counterexamples": len(rows) == 25,
        "required_game_present": any(
            row["game_id"] == shared.REQUIRED_GAME for row in rows
        ),
        "zero_unknown_diff_updates": all(
            row["unknown_diff_updates"] == 0 for row in rows
        ),
        "exact_command_parity": all(row["exact_command_lines"] for row in rows),
        "exact_liveness_parity": all(
            row["baseline_maximum_period2"] == row["candidate_maximum_period2"]
            for row in rows
        ),
    }
    result = {
        "schema": "troll-farm-e7a-single-logical-deletion-live-command-parity-v1",
        "evidence_boundary": (
            "teacher-forced exact public live states; proves command equality on this "
            "packet, not counterfactual value"
        ),
        "selection": {
            "audit_path": str(audit.relative_to(REPO)),
            "audit_sha256": sha256(audit),
            "agent_id": shared.AGENT_ID,
            "submission_id": shared.SUBMISSION_ID,
            "games": len(rows),
        },
        "baseline": {
            "path": str(BASELINE.relative_to(REPO)),
            "bytes": BASELINE.stat().st_size,
            "sha256": BASELINE_SHA256,
        },
        "candidate": {
            "path": str(candidate.relative_to(REPO)),
            "bytes": candidate.stat().st_size,
            "sha256": args.candidate_sha256,
        },
        "sacred_sha256": SACRED_SHA256,
        "metrics": {
            "games": len(rows),
            "turns": sum(row["turns"] for row in rows),
            "different_games": sum(not row["exact_command_lines"] for row in rows),
            "maximum_period2": max(row["candidate_maximum_period2"] for row in rows),
        },
        "gates": gates,
        "rows": rows,
    }
    result["verdict"] = (
        "LIVE_COMMAND_PARITY_PASS" if all(gates.values()) else "LIVE_COMMAND_PARITY_FAIL"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                **result["metrics"],
            },
            sort_keys=True,
        )
    )
    return 0 if all(gates.values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
