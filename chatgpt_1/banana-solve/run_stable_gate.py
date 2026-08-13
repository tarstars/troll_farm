#!/usr/bin/env python3
"""Run the shared Banana R2 gate with unconditional oscillation blocking.

Game generation and detector execution come from an explicitly pinned panel.
This wrapper changes only the final hard verdict:

* every raw candidate D-1 episode blocks, even if the parent reproduces it;
* every raw candidate D-4 episode blocks, even if the parent reproduces it;
* all other panel verdicts remain exactly as the pinned panel classified them.

The JSON is bound to the exact candidate, parent, gate contract, panel,
effective config, detector, oracle and runner SHA-256 values.  Raw counts and
raw detector episodes are retained; attribution flags are diagnostic only.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("stable_gate_panel", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--panel-file", type=Path, required=True)
    parser.add_argument("--gate-contract", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--json", type=Path, required=True)
    parser.add_argument("--save-failures", type=Path)
    parsed, remaining = parser.parse_known_args(argv)
    forwarded = [
        "--config", str(parsed.config),
        "--report", str(parsed.report),
        "--json", str(parsed.json),
    ]
    if parsed.save_failures is not None:
        forwarded.extend(["--save-failures", str(parsed.save_failures)])
    parsed.forwarded = forwarded + remaining
    return parsed


def detector_rows(row: dict[str, Any]) -> dict[str, dict[str, Any]]:
    artifacts = row.get("artifacts") or {}
    return {
        result.get("detector"): result
        for result in artifacts.get("detectors", [])
        if isinstance(result, dict) and result.get("detector")
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    panel_path = args.panel_file.resolve()
    fp = load_module(panel_path)
    base_run_pair = fp.run_pair

    def stable_run_pair(job):
        row = base_run_pair(job)
        raw_counts = dict(row.get("detector_counts") or {})
        rows = detector_rows(row)
        hard = []
        for detector in ("D-1", "D-4"):
            count = int(raw_counts.get(detector, 0) or 0)
            if count <= 0:
                continue
            result = rows.get(detector, {})
            hard.append({
                "property": "STABILITY",
                "detector": detector,
                "count": count,
                "episodes": list(result.get("episodes", [])),
                "rule": (
                    "unconditional hard gate; inherited/byte-identical "
                    "attribution cannot demote this detector"
                ),
            })
        if hard:
            row.setdefault("violations", []).extend(hard)
            row["block"] = True
        row["hard_stability"] = {
            "D-1": int(raw_counts.get("D-1", 0) or 0),
            "D-4": int(raw_counts.get("D-4", 0) or 0),
            "block": bool(hard),
        }
        return row

    fp.run_pair = stable_run_pair
    old_argv = sys.argv
    try:
        sys.argv = [str(panel_path)] + args.forwarded
        panel_exit = fp.main()
    finally:
        sys.argv = old_argv

    result = json.loads(args.json.read_text())
    games = list(result.get("games", []))
    d1_games = [game for game in games if int(game.get("detector_counts", {}).get("D-1", 0) or 0) > 0]
    d4_games = [game for game in games if int(game.get("detector_counts", {}).get("D-4", 0) or 0) > 0]
    blocking = [game for game in games if game.get("block")]

    cfg = json.loads(args.config.read_text())
    cfg_dir = args.config.resolve().parent

    def resolve(source: str) -> Path:
        path = Path(source)
        return path if path.is_absolute() else (cfg_dir / path).resolve()

    panel_root = panel_path.parents[1]
    candidate = resolve(cfg["candidate"]["source"])
    parent = resolve(cfg["parent"]["source"])
    detector = panel_root / "banana-restoration-r2/trace_detectors.py"
    oracle = panel_root / "banana-restoration-r2/conversion_race_oracle.py"
    gate_contract = args.gate_contract.resolve()
    runner = Path(__file__).resolve()

    try:
        rustc = subprocess.check_output(
            ["rustc", "--version"], text=True
        ).strip()
    except Exception as exc:  # pragma: no cover - evidence only
        rustc = f"ERROR: {exc}"

    binding = {
        "candidate_sha256": sha256(candidate),
        "parent_sha256": sha256(parent),
        "gate_contract_sha256": sha256(gate_contract),
        "panel_sha256": sha256(panel_path),
        "effective_config_sha256": sha256(args.config.resolve()),
        "trace_detectors_sha256": sha256(detector),
        "conversion_race_oracle_sha256": sha256(oracle),
        "gate_runner_sha256": sha256(runner),
    }
    hard_summary = {
        "games": len(games),
        "D-1_games": len(d1_games),
        "D-1_episodes": sum(int(game.get("detector_counts", {}).get("D-1", 0) or 0) for game in games),
        "D-4_games": len(d4_games),
        "D-4_episodes": sum(int(game.get("detector_counts", {}).get("D-4", 0) or 0) for game in games),
        "blocking_games": len(blocking),
        "verdict": "CLEAR" if not blocking and not d1_games and not d4_games else "BLOCK",
    }
    result["gate_contract"] = json.loads(gate_contract.read_text())
    result["sha_binding"] = binding
    result["hard_stability_summary"] = hard_summary
    result["environment"] = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "rustc": rustc,
    }
    result["verdict"] = hard_summary["verdict"]
    if isinstance(result.get("stats"), dict):
        result["stats"]["blocking_games"] = len(blocking)
    args.json.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")

    print(json.dumps({
        "panel_exit": panel_exit,
        "sha_binding": binding,
        "hard_stability_summary": hard_summary,
    }, indent=2, sort_keys=True))
    return 0 if hard_summary["verdict"] == "CLEAR" else 1


if __name__ == "__main__":
    raise SystemExit(main())
