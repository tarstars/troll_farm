#!/usr/bin/env python3
"""Rerun the exact stopped G-d panel and audit it against Codex's package."""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


CLAUDE_COMMIT = "e6cb7523d87d4da02e6f81406d572e3e83e4cf10"
CANDIDATE_SHA256 = "457360589a65cb2662950761deba817852ea9eb0d2c53b05a3e6fd2ab9dfda8a"
BASE_SHA256 = "5e1f4df406480f678ff03677cdda0f69d510c5c94efe90d4f0a8231b70c3339e"
PANEL_SHA256 = "d8900abf31dd030d07096e9a063365aa0e1f58b85a1613d02b07d3935c523a6a"
ENGINE_SHA256 = "7c240abfcfdf678993960fe73440735a19f934596c9651bdf915e2902f78fb05"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require_digest(label, path, expected):
    actual = digest(path)
    if actual != expected:
        raise SystemExit(f"{label} hash mismatch: expected {expected}, got {actual}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--claude-checkout", required=True)
    parser.add_argument("--codex-artifact-checkout", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    claude = Path(args.claude_checkout).resolve()
    codex = Path(args.codex_artifact_checkout).resolve()
    output = Path(args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)

    head = subprocess.run(
        ["git", "-C", str(claude), "rev-parse", "HEAD"],
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()
    if head != CLAUDE_COMMIT:
        raise SystemExit(f"Claude checkout must be detached at {CLAUDE_COMMIT}, got {head}")

    panel = claude / "claude_1/pipeline/fuzz_panel.py"
    engine = claude / "rust/src/game/engine.rs"
    candidate = claude / "claude_1/picker3/candidate-door1-p3b.rs"
    base = claude / "claude_1/picker2/candidate-door1-p1p2.rs"
    require_digest("panel", panel, PANEL_SHA256)
    require_digest("engine", engine, ENGINE_SHA256)
    require_digest("candidate", candidate, CANDIDATE_SHA256)
    require_digest("base", base, BASE_SHA256)

    accepted_config = claude / "claude_1/pipeline/picker2-door1-cand-config.json"
    config = json.loads(accepted_config.read_text())
    config.update({
        "bin_cache_dir": str(output / "bin"),
        "games_dir": str(output / "games"),
        "task": "20260820-pair-selector-anti-benching Phase-3b G-d/G-e",
        "notes": ["Independent local_codex_1 reproduction of the stopped r2 G-d panel."],
    })
    config["candidate"] = {
        "crate": "local_codex_gdge_candidate",
        "sha256": CANDIDATE_SHA256,
        "source": str(candidate),
    }
    config["parent"] = {
        "crate": "local_codex_gdge_base",
        "sha256": BASE_SHA256,
        "source": str(base),
    }
    config_path = output / "config.json"
    config_path.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n")
    panel_json = output / "panel.json"
    panel_report = output / "panel.md"
    run = subprocess.run([
        sys.executable,
        str(panel),
        "--config", str(config_path),
        "--report", str(panel_report),
        "--json", str(panel_json),
    ])
    if run.returncode != 1:
        raise SystemExit(f"expected scientific BLOCK exit 1, got {run.returncode}")

    claimed_panel = codex / "codex_1/picker3/results/gd-door1-panel-2026-08-23.json"
    rerun_packet = json.loads(panel_json.read_text())
    claimed_packet = json.loads(claimed_panel.read_text())
    if rerun_packet["games"] != claimed_packet["games"]:
        raise SystemExit("rerun game rows differ from the committed candidate panel")
    rerun_packet["stats"].pop("wall_time_seconds")
    claimed_packet["stats"].pop("wall_time_seconds")
    if rerun_packet != claimed_packet:
        raise SystemExit("rerun packet differs beyond the permitted wall-time field")

    independent_json = output / "independent-decomposition.json"
    verifier = Path(__file__).with_name("reproduce_gd_blocker.py")
    subprocess.run([
        sys.executable,
        str(verifier),
        "--candidate", str(panel_json),
        "--base", str(codex / "codex_1/picker3/results/gd-door1-base-panel-2026-08-20.json"),
        "--claimed-decomposition", str(codex / "codex_1/picker3/results/gd-door1-decomposition-2026-08-23.json"),
        "--output", str(independent_json),
    ], check=True)
    summary = json.loads(independent_json.read_text())
    print(json.dumps({
        "panel_games_exact": True,
        "packet_exact_excluding_wall_time": True,
        "panel_output_sha256": digest(panel_json),
        "independent_output_sha256": digest(independent_json),
        "verdict": summary["verdict"],
        "candidate_blocking": summary["candidate_blocking"],
        "base_blocking": summary["base_blocking"],
        "de_novo_blocking": summary["de_novo_blocking"],
        "new_p3_games": summary["new_p3_games"],
        "new_p4_games": summary["new_p4_games"],
    }, indent=2))


if __name__ == "__main__":
    main()
