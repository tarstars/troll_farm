#!/usr/bin/env python3
"""Regenerate Candidate 2's v5 instrument/rule-off archives in isolated scratch."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def materialize_config(source: Path, output: Path, scratch: Path) -> Path:
    cfg = json.loads(source.read_text())
    source_root = source.parent
    for subject in ("candidate", "parent"):
        cfg[subject]["source"] = str((source_root / cfg[subject]["source"]).resolve())
    cfg["games_dir"] = str(scratch / output.stem / "games")
    cfg["bin_cache_dir"] = str(scratch / "bin")
    output.write_text(json.dumps(cfg, indent=2, sort_keys=True) + "\n")
    return output


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--claude-root", type=Path, required=True,
                    help="clean claude_1 worktree containing cure2 and pipeline")
    ap.add_argument("--scratch", type=Path, required=True)
    args = ap.parse_args()
    cure2 = args.claude_root / "claude_1/cure2"
    pipeline = args.claude_root / "claude_1/pipeline/fuzz_panel.py"
    args.scratch.mkdir(parents=True, exist_ok=True)
    for label in ("ruleoff", "instrument"):
        cfg = materialize_config(cure2 / f"cure2-{label}-config.json",
                                 args.scratch / f"cure2-{label}-config.json", args.scratch)
        report = args.scratch / f"panel-{label}.md"
        result = args.scratch / f"panel-{label}.json"
        proc = subprocess.run([sys.executable, str(pipeline), "--config", str(cfg),
                               "--report", str(report), "--json", str(result)])
        # fuzz_panel uses 1 for an ordinary BLOCK verdict; only transport/execution errors (>1)
        # abort reproduction.
        if proc.returncode not in (0, 1):
            raise SystemExit(f"{label} panel failed with exit {proc.returncode}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
