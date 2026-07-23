#!/usr/bin/env python3
"""Analyze the frozen D32 deterministic closed-loop field option A/B."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import statistics
import subprocess
import sys
import tempfile

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.field_panel import validate_seed_blocks  # noqa: E402
from cgauto.make_d32_forced_turn75_farm import generate  # noqa: E402
from cgauto.replay_conformance import action_commands  # noqa: E402


REPO = Path(__file__).resolve().parent.parent
ROOT = REPO / "data/analysis/live-agent-6553250"
DEFAULT_BANK = ROOT / "d32-deterministic-field-option-bank.json"
DEFAULT_PANEL = REPO / "data/panels/d32-deterministic-field-option-ab-20260720.json"
DEFAULT_DRY_RUN = REPO / "data/panels/d32-deterministic-field-option-ab-dry-run-20260720.json"
DEFAULT_PRIOR_PANEL = REPO / "data/panels/legend-top5-common-seed-bank-v1-aa-20260719.json"
DEFAULT_PRIOR_RESULT = ROOT / "legend-top5-common-seed-bank-aa-result-2026-07-19.json"
DEFAULT_BASELINE = REPO / "cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs"
DEFAULT_CANDIDATE = REPO / "cgauto/submissions/diagnostic-agent6553250-d32-forced-turn75-farm.min.rs"
DEFAULT_OUTPUT = ROOT / "d32-deterministic-field-option-ab-development-2026-07-20.json"

EXPECTED_BASELINE_SHA = "a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55"
EXPECTED_CANDIDATE_SHA = "5138066175177a9b198c2c3f51deeef30d13d6207bee316227fae607662a6f82"
EXPECTED_BANK_SHA = "58260acf1327c3b57c2de36fd3a7efc57480dda47bda1fda67be086f5e7eab2d"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def normalized_action_stream(stream: list[str]) -> list[list[str]]:
    return [action_commands(line) for line in stream]


def first_difference_turn(left: list[list[str]], right: list[list[str]]) -> int | None:
    for turn, (left_actions, right_actions) in enumerate(zip(left, right), 1):
        if left_actions != right_actions:
            return turn
    if len(left) != len(right):
        return min(len(left), len(right)) + 1
    return None


def agent_id_at(trace: dict, index: int) -> int | None:
    matches = [row.get("agent_id") for row in trace.get("agents") or [] if row.get("index") == index]
    return matches[0] if len(matches) == 1 else None


def compile_strict(path: Path, crate_name: str) -> dict:
    with tempfile.TemporaryDirectory(prefix="d32-compile-") as directory:
        completed = subprocess.run(
            [
                "rustc",
                "--crate-name",
                crate_name,
                "--edition=2021",
                "-O",
                "-D",
                "warnings",
                str(path),
                "-o",
                str(Path(directory) / crate_name),
            ],
            text=True,
            capture_output=True,
            timeout=90,
            check=False,
        )
    return {
        "pass": completed.returncode == 0,
        "returncode": completed.returncode,
        "stderr": completed.stderr[:2000],
    }


def expected_jobs(blocks: list[dict]) -> list[dict]:
    rows = []
    for index, block in enumerate(blocks):
        for bot in ("baseline", "candidate"):
            rows.append({"block": index, "repetition": 0, **block, "bot": bot})
    return rows


def trace_stdout(row: dict, player: int) -> dict:
    streams = (row.get("trace") or {}).get("stdout") or []
    return streams[player] if len(streams) == 2 else {}


def prior_block(result: dict, block: dict) -> dict | None:
    matches = [
        row
        for row in result.get("per_block") or []
        if row.get("opponent") == block["opponent"]
        and row.get("opponent_agent") == block["opponent_agent"]
        and row.get("seed") == block["seed"]
    ]
    return matches[0] if len(matches) == 1 else None


def prior_rows(panel: dict, block: dict) -> list[dict]:
    return [
        row
        for row in panel.get("rows") or []
        if row.get("opponent") == block["opponent"]
        and row.get("opponent_agent") == block["opponent_agent"]
        and row.get("seed") == block["seed"]
    ]


def reference_match(current: dict, old: dict, old_result: dict, index: int) -> dict:
    stdout = (old_result.get("stdout_sha256") or [])[index]
    frames = (old_result.get("stdout_frames") or [])[index]
    current_stdout = [trace_stdout(current, player) for player in (0, 1)]
    fields = {
        "scores": current.get("scores") == old.get("scores"),
        "inventories": current.get("inventories") == old.get("inventories"),
        "turns": current.get("turns") == old.get("turns"),
        "workforce": current.get("workforce") == old.get("workforce"),
        "player_0_stdout": (
            current_stdout[0].get("sha256") == stdout[0]
            and current_stdout[0].get("frames") == frames[0]
        ),
        "player_1_stdout": (
            current_stdout[1].get("sha256") == stdout[1]
            and current_stdout[1].get("frames") == frames[1]
        ),
    }
    return {"game_id": old.get("game_id"), "fields": fields, "pass": all(fields.values())}


def value_summary(per_block: list[dict]) -> dict:
    margin_deltas = [row["delta"]["margin"] for row in per_block]
    own_deltas = [row["delta"]["own_score"] for row in per_block]
    metrics = {
        "mean_margin_delta": statistics.mean(margin_deltas),
        "mean_own_score_delta": statistics.mean(own_deltas),
        "positive_margin_blocks": sum(value > 0 for value in margin_deltas),
        "minimum_margin_delta": min(margin_deltas),
    }
    gates = {
        "mean_margin_delta_at_least_10": metrics["mean_margin_delta"] >= 10,
        "mean_own_score_delta_nonnegative": metrics["mean_own_score_delta"] >= 0,
        "at_least_two_positive_margin_blocks": metrics["positive_margin_blocks"] >= 2,
        "no_margin_delta_below_minus_20": metrics["minimum_margin_delta"] >= -20,
    }
    return {"metrics": metrics, "gates": gates, "pass": all(gates.values())}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bank", type=Path, default=DEFAULT_BANK)
    parser.add_argument("--panel", type=Path, default=DEFAULT_PANEL)
    parser.add_argument("--dry-run", type=Path, default=DEFAULT_DRY_RUN)
    parser.add_argument("--prior-panel", type=Path, default=DEFAULT_PRIOR_PANEL)
    parser.add_argument("--prior-result", type=Path, default=DEFAULT_PRIOR_RESULT)
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    parser.add_argument("--candidate", type=Path, default=DEFAULT_CANDIDATE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--protocol",
        default="d32-deterministic-field-option-ab-protocol-2026-07-20.md",
    )
    args = parser.parse_args()

    bank_text = args.bank.read_text()
    blocks = validate_seed_blocks(json.loads(bank_text))
    jobs = expected_jobs(blocks)
    panel = read_json(args.panel)
    dry_run = read_json(args.dry_run)
    old_panel = read_json(args.prior_panel)
    old_result = read_json(args.prior_result)
    rows = panel.get("rows") or []
    sources = panel.get("sources") or {}

    baseline_bytes = args.baseline.read_bytes()
    candidate_bytes = args.candidate.read_bytes()
    compile_results = {
        "baseline": compile_strict(args.baseline, "d32_resident"),
        "candidate": compile_strict(args.candidate, "d32_option"),
    }
    preflight = {
        "bank_sha256": digest(args.bank),
        "baseline_sha256": hashlib.sha256(baseline_bytes).hexdigest(),
        "candidate_sha256": hashlib.sha256(candidate_bytes).hexdigest(),
        "candidate_regeneration_exact": generate(
            REPO / "cgauto/submissions/candidate-agent6553250-d29b-spatial-option-critic.min.rs"
        )
        == candidate_bytes,
        "source_sizes_below_100000": len(baseline_bytes) < 100_000 and len(candidate_bytes) < 100_000,
        "fixed_turn75_decision_unique": (
            candidate_bytes.count(b"v.turn==75") == 1
            and candidate_bytes.count(b"self.s=true") == 1
            and b"self.s=d29k::p(&b)" not in candidate_bytes
        ),
        "strict_compile": compile_results,
        "dry_run_exact": (
            dry_run.get("status") == "dry-run"
            and dry_run.get("jobs") == jobs
            and dry_run.get("seed_bank") == panel.get("seed_bank")
            and dry_run.get("sources") == sources
        ),
    }
    preflight["pass"] = (
        preflight["bank_sha256"] == EXPECTED_BANK_SHA
        and preflight["baseline_sha256"] == EXPECTED_BASELINE_SHA
        and preflight["candidate_sha256"] == EXPECTED_CANDIDATE_SHA
        and preflight["candidate_regeneration_exact"]
        and preflight["source_sizes_below_100000"]
        and preflight["fixed_turn75_decision_unique"]
        and all(value["pass"] for value in compile_results.values())
        and preflight["dry_run_exact"]
    )

    selected_prior = [prior_block(old_result, block) for block in blocks]
    integrity = {
        "preflight_pass": preflight["pass"],
        "panel_complete": panel.get("status") == "complete",
        "six_rows": len(rows) == 6,
        "six_exact_jobs": panel.get("jobs") == jobs,
        "bank_hash_exact": (
            digest(args.bank) == EXPECTED_BANK_SHA
            and (panel.get("seed_bank") or {}).get("sha256") == EXPECTED_BANK_SHA
            and (panel.get("seed_bank") or {}).get("blocks") == blocks
        ),
        "source_hashes_exact": (
            set(sources) == {"baseline", "candidate"}
            and sources.get("baseline", {}).get("sha256") == EXPECTED_BASELINE_SHA
            and sources.get("candidate", {}).get("sha256") == EXPECTED_CANDIDATE_SHA
        ),
        "unique_game_ids": (
            len(rows) == 6
            and None not in {row.get("game_id") for row in rows}
            and len({row.get("game_id") for row in rows}) == 6
        ),
        "zero_diagnostics": len(rows) == 6 and all(not row.get("diagnostics") for row in rows),
        "trace_evidence_complete": (
            len(rows) == 6
            and all(
                (row.get("trace") or {}).get("turn_one")
                and not (row.get("trace") or {}).get("turn_one_error")
                and len((row.get("trace") or {}).get("stdout") or []) == 2
                for row in rows
            )
        ),
        "prior_global_integrity": all((old_result.get("integrity") or {}).values()),
        "selected_prior_blocks_exact": (
            all(row is not None and row.get("pass") for row in selected_prior)
            and len(selected_prior) == 3
        ),
    }

    per_block = []
    for index, block in enumerate(blocks):
        pair = rows[index * 2 : index * 2 + 2]
        baseline = pair[0] if len(pair) == 2 else {}
        candidate = pair[1] if len(pair) == 2 else {}
        reference = selected_prior[index] or {}
        old_rows = prior_rows(old_panel, block)
        reference_matches = [
            reference_match(baseline, old, reference, old_index)
            for old_index, old in enumerate(old_rows)
        ] if len(old_rows) == 2 else []
        baseline_stream = normalized_action_stream(trace_stdout(baseline, 0).get("stream") or [])
        candidate_stream = normalized_action_stream(trace_stdout(candidate, 0).get("stream") or [])
        opponent_a_stream = normalized_action_stream(trace_stdout(baseline, 1).get("stream") or [])
        opponent_b_stream = normalized_action_stream(trace_stdout(candidate, 1).get("stream") or [])
        first_difference = first_difference_turn(baseline_stream, candidate_stream)
        first_opponent_difference = first_difference_turn(opponent_a_stream, opponent_b_stream)
        expected_options = f"seed={block['seed']}\n"
        row_identity = (
            len(pair) == 2
            and [row.get("bot") for row in pair] == ["baseline", "candidate"]
            and all(row.get("block") == index for row in pair)
            and all(row.get("opponent") == block["opponent"] for row in pair)
            and all(row.get("opponent_agent") == block["opponent_agent"] for row in pair)
            and all(row.get("seed") == block["seed"] for row in pair)
        )
        turn_one_hashes = [
            ((row.get("trace") or {}).get("turn_one") or {}).get("sha256") for row in pair
        ]
        block_gates = {
            "row_identity_and_seed_echo_exact": (
                row_identity and all(row.get("referee_input") == expected_options for row in pair)
            ),
            "opponent_agent_identity_exact": (
                len(pair) == 2
                and all(agent_id_at(row.get("trace") or {}, 1) == block["opponent_agent"] for row in pair)
            ),
            "turn_one_a_b_and_prior_exact": (
                len(turn_one_hashes) == 2
                and len(set(turn_one_hashes)) == 1
                and turn_one_hashes[0] in (reference.get("turn_one_sha256") or [])
            ),
            "fresh_baseline_reproduces_prior": any(row["pass"] for row in reference_matches),
            "complete_stdout_lengths": (
                len(pair) == 2
                and all(
                    all(trace_stdout(row, player).get("frames") == row.get("turns") for player in (0, 1))
                    for row in pair
                )
            ),
            "player_0_actions_exact_through_turn_74": (
                len(baseline_stream) >= 85
                and len(candidate_stream) >= 85
                and baseline_stream[:74] == candidate_stream[:74]
            ),
            "player_0_first_divergence_turn_75_to_85": (
                first_difference is not None and 75 <= first_difference <= 85
            ),
        }
        score_a = baseline.get("scores") or [0, 0]
        score_b = candidate.get("scores") or [0, 0]
        margin_a = score_a[0] - score_a[1]
        margin_b = score_b[0] - score_b[1]
        per_block.append(
            {
                **block,
                "game_ids": [row.get("game_id") for row in pair],
                "scores": {"baseline": score_a, "candidate": score_b},
                "margins": {"baseline": margin_a, "candidate": margin_b},
                "delta": {
                    "own_score": score_b[0] - score_a[0],
                    "opponent_score": score_b[1] - score_a[1],
                    "margin": margin_b - margin_a,
                },
                "turn_one_sha256": turn_one_hashes,
                "stdout_sha256": {
                    "baseline": [trace_stdout(baseline, player).get("sha256") for player in (0, 1)],
                    "candidate": [trace_stdout(candidate, player).get("sha256") for player in (0, 1)],
                },
                "first_player_0_action_difference_turn": first_difference,
                "first_player_1_action_difference_turn": first_opponent_difference,
                "prior_reference_matches": reference_matches,
                "gates": block_gates,
                "integrity_pass": all(block_gates.values()),
            }
        )

    integrity["all_block_integrity"] = len(per_block) == 3 and all(
        row["integrity_pass"] for row in per_block
    )
    integrity_pass = all(integrity.values())
    value = value_summary(per_block) if len(per_block) == 3 else None
    value_evaluated = integrity_pass
    decision = (
        "invalid_panel"
        if not integrity_pass
        else "pass_field_option_development"
        if value and value["pass"]
        else "reject_permanent_turn75_farm"
    )
    payload = {
        "schema": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "scope": "D32 consumed deterministic TestSession A/B; no Arena submission",
        "protocol": args.protocol,
        "inputs": {
            "bank": str(args.bank),
            "bank_sha256": digest(args.bank),
            "panel": str(args.panel),
            "panel_sha256": digest(args.panel),
            "dry_run": str(args.dry_run),
            "dry_run_sha256": digest(args.dry_run),
            "prior_panel": str(args.prior_panel),
            "prior_panel_sha256": digest(args.prior_panel),
            "prior_result": str(args.prior_result),
            "prior_result_sha256": digest(args.prior_result),
        },
        "preflight": preflight,
        "integrity": integrity,
        "integrity_pass": integrity_pass,
        "per_block": per_block,
        "value_evaluated": value_evaluated,
        "value": value if value_evaluated else None,
        "decision": decision,
        "complete": integrity_pass and bool(value and value["pass"]),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=1) + "\n")
    print(json.dumps(payload, indent=1))
    return 0 if decision == "pass_field_option_development" else 1


if __name__ == "__main__":
    raise SystemExit(main())
