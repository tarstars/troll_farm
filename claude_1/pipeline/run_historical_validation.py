#!/usr/bin/env python3
"""Historical acceptance validation for pre_review.py.

The tool must retroactively BLOCK the round-3 rejected state and CLEAR the
state that fixed it:

  (a) reconstruct the ROUND-3 state (commit 8b000bad, candidate bytes
      2f58edef...) with its then-committed t5_flip_convert trace declared
      candidate-driven -> trace-provenance MUST BLOCK (SCRIPTED_TRACE:
      the real candidate WAITs where the scripted trace converts);
  (b) reconstruct the round-3-era instrument files (trace_detectors.py,
      regression_tests.py, banana_blocks/block-i1.rs at 8b000bad) and run
      single-model with the CONVERSION_RACE_ORACLE config -> MUST BLOCK
      (MODEL_DIVERGENCE: old D-8 `exact_chops < eta_opp_now`, old candidate
      `< eta_opp.max(ripen)` with no oracle import/marker anywhere);
  (c) run the FULL pre_review with banana-r2-task-config.json against the
      current branch state -> expected CLEAR.

Usage: python3 run_historical_validation.py [--outdir DIR]

Writes per-run reports (a-report.md / b-report.md / c-report.md + .json)
into --outdir (default: ./validation next to this script) and prints a
PASS/FAIL summary. Exit 0 iff all three expectations hold.

Deterministic; read-only with respect to everything outside --outdir.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
R3_COMMIT = "8b000bad"
R3_FILES = {
    "candidate-banana-r2.min.rs":
        "claude_1/banana-restoration-r2/candidate-banana-r2.min.rs",
    "trace_detectors.py":
        "claude_1/banana-restoration-r2/trace_detectors.py",
    "regression_tests.py":
        "claude_1/banana-restoration-r2/regression_tests.py",
    "block-i1.rs":
        "claude_1/banana-restoration-r2/banana_blocks/block-i1.rs",
    "t5-transcript.txt":
        "claude_1/banana-restoration-r2/traces/t5_flip_convert-transcript.txt",
    "t5-commands.txt":
        "claude_1/banana-restoration-r2/traces/t5_flip_convert-commands.txt",
}


def git_root() -> Path:
    proc = subprocess.run(
        ["git", "-C", str(HERE), "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True)
    return Path(proc.stdout.strip())


def reconstruct(dest: Path) -> None:
    root = git_root()
    for local, repo_path in R3_FILES.items():
        proc = subprocess.run(
            ["git", "-C", str(root), "show", f"{R3_COMMIT}:{repo_path}"],
            capture_output=True, check=True)
        (dest / local).write_bytes(proc.stdout)


def run_pre_review(config: Path, report: Path, json_out: Path,
                   only: str | None) -> int:
    cmd = [sys.executable, str(HERE / "pre_review.py"),
           "--config", str(config), "--report", str(report),
           "--json", str(json_out)]
    if only:
        cmd += ["--only", only]
    proc = subprocess.run(cmd)
    return proc.returncode


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", default=str(HERE / "validation"))
    args = parser.parse_args(argv)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    results = {}
    old = Path(tempfile.gettempdir()) / "banana-r3-state"
    old.mkdir(parents=True, exist_ok=True)
    try:
        reconstruct(old)

        # ---- (a) round-3 t5 declared candidate-driven -------------------
        cfg_a = {
            "task": ("HISTORICAL round-3 rejected state (8b000bad / "
                     "2f58edef): t5 declared candidate-driven"),
            "ledger": str(HERE / "failure-ledger.json"),
            "traces": [{
                "name": "t5_flip_convert-as-handed-off",
                "transcript": str(old / "t5-transcript.txt"),
                "commands": str(old / "t5-commands.txt"),
                "binary_source": str(old / "candidate-banana-r2.min.rs"),
                "crate_name": "banana_r2",
                "scripted": False,
                "critical": True,
            }],
        }
        cfg_a_path = old / "config-a.json"
        cfg_a_path.write_text(json.dumps(cfg_a, indent=1))
        rc = run_pre_review(cfg_a_path, outdir / "a-report.md",
                            outdir / "a-report.json", "trace-provenance")
        results["a"] = ("PASS (BLOCK as required)" if rc == 1
                        else f"FAIL (exit {rc}, expected 1)")

        # ---- (b) round-3-era files vs the oracle config ------------------
        cfg_b = {
            "task": ("HISTORICAL round-3-era instruments (8b000bad): "
                     "single-model vs CONVERSION_RACE_ORACLE"),
            "ledger": str(HERE / "failure-ledger.json"),
            "oracles": [{
                "name": "CONVERSION_RACE_ORACLE",
                "module_path": str(
                    HERE.parent / "banana-restoration-r2"
                    / "conversion_race_oracle.py"),
                "quantity_patterns": [
                    "max\\(\\s*(?:t\\s*\\+\\s*)?eta_opp",
                    "eta_opp\\w*\\s*\\.\\s*max\\s*\\(",
                    "exact_chops\\w*\\s*<\\s*eta_opp",
                    "ceil\\w*\\(\\s*(?:current_)?health\\b[^)]*chop",
                ],
                "scan_files": [
                    str(old / "trace_detectors.py"),
                    str(old / "regression_tests.py"),
                    str(old / "block-i1.rs"),
                ],
                "allowed_importers": [
                    {"path": str(old / "trace_detectors.py")},
                    {"path": str(old / "regression_tests.py")},
                ],
                "allowed_mirrors": [
                    {"path": str(old / "block-i1.rs"),
                     "marker_regex": "CONVERSION_RACE_ORACLE"},
                ],
            }],
        }
        cfg_b_path = old / "config-b.json"
        cfg_b_path.write_text(json.dumps(cfg_b, indent=1))
        rc = run_pre_review(cfg_b_path, outdir / "b-report.md",
                            outdir / "b-report.json", "single-model")
        results["b"] = ("PASS (BLOCK as required)" if rc == 1
                        else f"FAIL (exit {rc}, expected 1)")
    finally:
        shutil.rmtree(old, ignore_errors=True)

    # ---- (c) full pre_review on the current branch state ----------------
    rc = run_pre_review(HERE / "banana-r2-task-config.json",
                        outdir / "c-report.md", outdir / "c-report.json",
                        None)
    results["c"] = ("PASS (CLEAR as expected)" if rc == 0
                    else f"FLAGGED (exit {rc}) - see c-report.md; report "
                         "honestly, do not tune checks")

    print()
    for key in ("a", "b", "c"):
        print(f"historical validation ({key}): {results[key]}")
    ok = (results["a"].startswith("PASS")
          and results["b"].startswith("PASS")
          and results["c"].startswith("PASS"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
