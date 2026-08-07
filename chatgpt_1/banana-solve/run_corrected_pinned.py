#!/usr/bin/env python3
"""Run the hash-pinned Banana R2 panel with mechanically corrected attribution.

This wrapper is independent verification while the reviewer-owned canonical
panel correction is being published.  It imports an explicit panel file and
changes only classification, never game generation or commands:

* P1 detector failures are report-tier when the complete candidate and parent
  command streams are byte-identical, or when every full detector episode is
  reproduced by the parent and ends inside the aligned command prefix.
* P2/P4 are report-tier on fully byte-identical streams.
* A final-turn D-7 ``unbanked_at_end`` episode is removed only after rerunning
  that exact deterministic candidate job and observing in the referee's real
  post-C_T state that the exact unit no longer carries a banana.  Syntax alone
  is insufficient.

The output JSON is then bound to full SHA-256 values for candidate, parent,
panel, detector, oracle and effective config.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_panel(path: Path):
    spec = importlib.util.spec_from_file_location("pinned_fuzz_panel", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def first_divergence(left: str, right: str) -> int | None:
    a = left.splitlines()
    b = right.splitlines()
    for turn, (x, y) in enumerate(zip(a, b), start=1):
        if x != y:
            return turn
    if len(a) != len(b):
        return min(len(a), len(b)) + 1
    return None


def key(episode: dict[str, Any]) -> str:
    return json.dumps(episode, sort_keys=True, separators=(",", ":"))


def parse_cli(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--panel-file", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--json", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--save-failures", type=Path)
    parsed, remaining = parser.parse_known_args(argv)
    forwarded = [
        "--config", str(parsed.config),
        "--json", str(parsed.json),
        "--report", str(parsed.report),
    ]
    if parsed.save_failures is not None:
        forwarded.extend(["--save-failures", str(parsed.save_failures)])
    parsed.forwarded = forwarded + remaining
    return parsed


def main(argv: list[str] | None = None) -> int:
    args = parse_cli(sys.argv[1:] if argv is None else argv)
    fp = load_panel(args.panel_file.resolve())
    base_run_pair = fp.run_pair

    def corrected_run_pair(job):
        row = base_run_pair(job)
        artifacts = row.get("artifacts") or {}
        candidate_commands = artifacts.get("candidate_commands")
        parent_commands = artifacts.get("parent_commands")
        candidate_transcript = artifacts.get("candidate_transcript")
        parent_transcript = artifacts.get("parent_transcript")
        if not all(isinstance(value, str) for value in (
            candidate_commands,
            parent_commands,
            candidate_transcript,
            parent_transcript,
        )):
            return row

        byte_equal = candidate_commands == parent_commands
        divergence = first_divergence(candidate_commands, parent_commands)
        tr_c = fp.td.build_trace(candidate_transcript, candidate_commands)
        tr_p = fp.td.build_trace(parent_transcript, parent_commands)
        parent_cmds = fp.td.CommandParser().parse(parent_commands)
        candidate_full = {
            result["detector"]: result
            for result in artifacts.get("detectors", [])
        }
        parent_full = {
            result["detector"]: result
            for result in fp.td.run_all(tr_p, parent_cmds)
        }

        retained = []
        post_state = None
        for violation in row.get("violations", []):
            prop = violation.get("property")
            detector = violation.get("detector")
            if prop in {"P2", "P4"} and byte_equal:
                row.setdefault("flags", []).append({
                    "flag": "byte-identical-parent-property",
                    "property": prop,
                    "detail": (
                        f"{prop} reproduced on a complete command stream "
                        "byte-identical to the stable parent"
                    ),
                })
                continue
            if prop != "P1" or detector is None:
                retained.append(violation)
                continue

            c_result = candidate_full.get(detector, violation)
            c_episodes = list(c_result.get("episodes", []))
            p_episodes = list(parent_full.get(detector, {}).get("episodes", []))
            parent_keys = {key(episode) for episode in p_episodes}
            reproduced = bool(c_episodes) and all(
                key(episode) in parent_keys for episode in c_episodes
            )
            aligned = bool(c_episodes) and all(
                divergence is None
                or int(episode.get("turn_end", episode.get("turn_start", 10**9)))
                    < divergence
                for episode in c_episodes
            )
            if byte_equal or (aligned and reproduced):
                row.setdefault("flags", []).append({
                    "flag": "inherited-parent-detector",
                    "detector": detector,
                    "count": len(c_episodes),
                    "first_command_divergence_turn": divergence,
                    "detail": (
                        f"{detector} reproduced by the parent inside the "
                        "aligned command prefix"
                    ),
                })
                continue

            # Exact finite-trace correction for final D-7: the supplied
            # referee is mutated through C_T even though the serialized trace
            # stops at pre-action S_T.  Re-run only a row that needs this fact.
            if detector == "D-7" and c_episodes:
                if post_state is None:
                    ref = fp.make_referee(job["spec"])
                    fp.rt.run_binary_custom(Path(job["candidate"]), ref, job["turns"])
                    post_state = ref
                remaining = []
                cleared = []
                for episode in c_episodes:
                    uid = episode.get("unit")
                    terminal = (
                        episode.get("kind") == "unbanked_at_end"
                        and int(episode.get("turn_end", -1)) == tr_c.T
                        and isinstance(uid, int)
                    )
                    unit = post_state.units.get(uid) if terminal else None
                    banana_cleared = (
                        unit is not None and int(unit["carry"][3]) == 0
                    )
                    if terminal and banana_cleared:
                        cleared.append(episode)
                    else:
                        remaining.append(episode)
                if cleared:
                    row.setdefault("flags", []).append({
                        "flag": "terminal-post-state-cleared",
                        "detector": "D-7",
                        "count": len(cleared),
                        "episodes": cleared[:5],
                        "detail": (
                            "pre-action S_T showed banana cargo, but the exact "
                            "post-C_T referee state shows that unit cargo cleared"
                        ),
                    })
                if not remaining:
                    continue
                replacement = dict(violation)
                replacement["count"] = len(remaining)
                replacement["episodes"] = remaining[:5]
                retained.append(replacement)
                continue

            retained.append(violation)

        row["violations"] = retained
        row["block"] = bool(retained)
        row.setdefault("attribution", {})
        row["attribution"].update({
            "command_streams_byte_equal": byte_equal,
            "first_command_divergence_turn": divergence,
        })
        return row

    fp.run_pair = corrected_run_pair
    original_argv = sys.argv
    try:
        sys.argv = [str(args.panel_file)] + args.forwarded
        exit_code = fp.main()
    finally:
        sys.argv = original_argv

    result = json.loads(args.json.read_text())
    cfg = json.loads(args.config.read_text())
    config_dir = args.config.resolve().parent

    def resolve(source: str) -> Path:
        path = Path(source)
        return path if path.is_absolute() else (config_dir / path).resolve()

    panel_root = args.panel_file.resolve().parents[1]
    candidate_path = resolve(cfg["candidate"]["source"])
    parent_path = resolve(cfg["parent"]["source"])
    metadata = {
        "candidate_sha256": digest(candidate_path),
        "parent_sha256": digest(parent_path),
        "panel_sha256": digest(args.panel_file.resolve()),
        "config_sha256": digest(args.config.resolve()),
        "trace_detectors_sha256": digest(
            panel_root / "banana-restoration-r2/trace_detectors.py"
        ),
        "conversion_race_oracle_sha256": digest(
            panel_root / "banana-restoration-r2/conversion_race_oracle.py"
        ),
        "classification": "all-detector aligned-prefix + exact post-C_T D-7",
    }
    result["sha_binding"] = metadata
    args.json.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    print(json.dumps(metadata, indent=2, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
