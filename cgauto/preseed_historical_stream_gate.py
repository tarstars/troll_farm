#!/usr/bin/env python3
"""Gate preseed on exact historical close-game state streams without replay mutation."""

from __future__ import annotations

import argparse
from concurrent.futures import as_completed, ThreadPoolExecutor
import json
from pathlib import Path
import statistics
import sys
import tempfile

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.historical_terminal_fixtures import (  # noqa: E402
    action_commands,
    preseed_opportunities,
    read_trajectory,
)
from cgauto.idle_harvest_study import (  # noqa: E402
    compile_source,
    grid_text,
    run_batch,
    turn_text,
)
from cgauto.replay_state import decode_replay, to_game_state  # noqa: E402

BASELINE = REPO / "cgauto/submissions/agent-6553250-yamo-orchard-live.min.rs"
CANDIDATE = REPO / "cgauto/submissions/candidate-agent6553250-preseed-low-supply.min.rs"
RAW_GAMES = REPO / "data/raw/games"
FIXTURES = REPO / "data/analysis/live-agent-6553250/terminal-fixtures/manifest.json"


def first_action_divergence(baseline: list[str], candidate: list[str]) -> int | None:
    common = min(len(baseline), len(candidate))
    for index in range(common):
        if action_commands(baseline[index]) != action_commands(candidate[index]):
            return index + 1
    return common + 1 if len(baseline) != len(candidate) else None


def run_game(row: dict, baseline_binary: Path, candidate_binary: Path) -> dict:
    game_id = row["game_id"]
    fixture = json.loads((FIXTURES.parent / row["file"]).read_text())
    seat = fixture["live_seat"]
    decoded = decode_replay(RAW_GAMES / f"{game_id}.json")
    games = [to_game_state(decoded["map"], state) for state in decoded["states"][:-1]]
    input_text = grid_text(games[0], seat) + "".join(turn_text(game, seat) for game in games)
    baseline_lines, baseline_stderr = run_batch(baseline_binary, input_text)
    candidate_lines, candidate_stderr = run_batch(candidate_binary, input_text)
    trajectory = read_trajectory(game_id)
    recorded = [turn.get(f"commands{seat}") or "" for turn in trajectory]

    baseline_mismatches = [
        turn
        for turn, (actual, reproduced) in enumerate(zip(recorded, baseline_lines), 1)
        if action_commands(actual) != action_commands(reproduced)
    ]
    if len(recorded) != len(baseline_lines):
        baseline_mismatches.append(min(len(recorded), len(baseline_lines)) + 1)

    first_mismatch = baseline_mismatches[0] if baseline_mismatches else None

    divergence = first_action_divergence(baseline_lines, candidate_lines)
    eligibility = []
    if divergence is not None and divergence <= len(games):
        eligibility = preseed_opportunities(
            games[divergence - 1],
            seat,
            action_commands(baseline_lines[divergence - 1]),
        )
    return {
        "game_id": game_id,
        "won": fixture["won"],
        "margin": fixture["margin"],
        "n_turns": fixture["n_turns"],
        "baseline_matches_recorded": not baseline_mismatches and not baseline_stderr,
        "baseline_first_mismatch": first_mismatch,
        "baseline_mismatch_recorded": (
            action_commands(recorded[first_mismatch - 1])
            if first_mismatch is not None and first_mismatch <= len(recorded)
            else None
        ),
        "baseline_mismatch_reproduced": (
            action_commands(baseline_lines[first_mismatch - 1])
            if first_mismatch is not None and first_mismatch <= len(baseline_lines)
            else None
        ),
        "baseline_stderr": baseline_stderr,
        "candidate_stderr": candidate_stderr,
        "first_divergence": divergence,
        "first_divergence_is_eligible": divergence is not None and bool(eligibility),
        "eligibility": eligibility,
        "baseline_commands": (
            action_commands(baseline_lines[divergence - 1]) if divergence else None
        ),
        "candidate_commands": (
            action_commands(candidate_lines[divergence - 1]) if divergence else None
        ),
    }


def aggregate(rows: list[dict]) -> dict:
    activated = [row for row in rows if row["first_divergence"] is not None]
    turns = [row["first_divergence"] for row in activated]
    admissible = [row for row in rows if row["baseline_matches_recorded"]]
    admissible_activated = [
        row for row in admissible if row["first_divergence"] is not None
    ]
    admissible_turns = [row["first_divergence"] for row in admissible_activated]
    return {
        "games": len(rows),
        "baseline_exact_reproductions": sum(row["baseline_matches_recorded"] for row in rows),
        "rejected_nonreproducing_streams": sum(
            not row["baseline_matches_recorded"] for row in rows
        ),
        "candidate_activated_games": len(activated),
        "activated_close_losses": sum(not row["won"] for row in activated),
        "activated_matched_close_wins": sum(row["won"] for row in activated),
        "inactive_command_identical_games": len(rows) - len(activated),
        "eligible_first_divergences": sum(
            row["first_divergence_is_eligible"] for row in activated
        ),
        "candidate_stderr_games": sum(bool(row["candidate_stderr"]) for row in rows),
        "median_first_divergence_turn": statistics.median(turns) if turns else None,
        "pre_turn_100_divergences": sum(
            row["first_divergence"] is not None and row["first_divergence"] < 100
            for row in rows
        ),
        "admissible_candidate_activated_games": len(admissible_activated),
        "admissible_activated_close_losses": sum(
            not row["won"] for row in admissible_activated
        ),
        "admissible_activated_matched_close_wins": sum(
            row["won"] for row in admissible_activated
        ),
        "admissible_inactive_command_identical_games": len(admissible)
        - len(admissible_activated),
        "admissible_eligible_first_divergences": sum(
            row["first_divergence_is_eligible"] for row in admissible_activated
        ),
        "admissible_median_first_divergence_turn": (
            statistics.median(admissible_turns) if admissible_turns else None
        ),
        "admissible_pre_turn_100_divergences": sum(
            row["first_divergence"] is not None and row["first_divergence"] < 100
            for row in admissible
        ),
    }


def save(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=1) + "\n")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO
        / "data/analysis/live-agent-6553250/preseed-historical-stream-gate.json",
    )
    args = parser.parse_args()
    if not 1 <= args.jobs <= 8:
        raise SystemExit("--jobs must be between 1 and 8")

    manifest = json.loads(FIXTURES.read_text())
    with tempfile.TemporaryDirectory(prefix="preseed-stream-gate-") as directory:
        temp = Path(directory)
        baseline = temp / "baseline"
        candidate = temp / "candidate"
        compile_source(BASELINE, baseline, "preseed_stream_baseline")
        compile_source(CANDIDATE, candidate, "preseed_stream_candidate")
        rows = []
        with ThreadPoolExecutor(max_workers=args.jobs) as executor:
            futures = {
                executor.submit(run_game, row, baseline, candidate): row["game_id"]
                for row in manifest["fixtures"]
            }
            for future in as_completed(futures):
                rows.append(future.result())
        rows.sort(key=lambda row: row["game_id"])

    payload = {
        "schema": 1,
        "scope": (
            "fixed reconstructed historical state streams; only streams whose exact baseline "
            "commands reproduce the recording are admissible; causal selection gate, not outcome replay"
        ),
        "sources": {
            "baseline": str(BASELINE.relative_to(REPO)),
            "candidate": str(CANDIDATE.relative_to(REPO)),
            "fixtures": str(FIXTURES.relative_to(REPO)),
        },
        "aggregate": aggregate(rows),
        "rows": rows,
    }
    save(args.output, payload)
    print(json.dumps(payload["aggregate"], indent=1))
    print(f"saved {args.output}")
    return 0 if (
        payload["aggregate"]["baseline_exact_reproductions"] > 0
        and payload["aggregate"]["admissible_eligible_first_divergences"]
        == payload["aggregate"]["admissible_candidate_activated_games"]
        and payload["aggregate"]["admissible_pre_turn_100_divergences"] == 0
        and payload["aggregate"]["candidate_stderr_games"] == 0
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
