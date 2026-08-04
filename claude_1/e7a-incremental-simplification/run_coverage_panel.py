#!/usr/bin/env python3
"""Region/function coverage of a candidate over the frozen open replay packet.

Builds the candidate with `-C instrument-coverage`, replays all 25 games of the
frozen packet (verifying each output still matches the packet baseline, so the
instrumented build is proven equivalent), merges the profiles and reports:

  * overall region and function coverage — how much of the bot the live-replay
    safety gate actually exercises;
  * per-function cold-region ranking — reachable code that never ran.

Coverage is evidence about the *test panel*, not about reachability: cold code
is not dead code, and deleting it is a behavior change that needs the ablation
protocol, not this programme's behavior-exact rounds.

Requires: rustup component llvm-tools-preview.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import re
import subprocess
from collections import defaultdict
from pathlib import Path

PACKET_SHA256 = "fb8e968ff65fc55c6f6f9d2f2b678434ab2dfda8eba84fdb6d0384d41856c7e2"


def llvm_bin() -> Path:
    root = Path.home() / ".rustup/toolchains"
    for toolchain in sorted(root.iterdir()):
        candidate = toolchain / "lib/rustlib/x86_64-unknown-linux-gnu/bin"
        if (candidate / "llvm-profdata").exists():
            return candidate
    raise RuntimeError("llvm-tools-preview not installed")


def segments(name: str) -> list[str]:
    out, i = [], 0
    while i < len(name):
        m = re.match(r"(\d+)", name[i:])
        if m:
            length = int(m.group(1))
            i += m.end()
            out.append(name[i:i + length])
            i += length
        else:
            i += 1
    return [s for s in out if re.fullmatch(r"[A-Za-z_]\w*", s or "")]


def owner(name: str, crate: str) -> str:
    parts = [s for s in segments(name) if not s.startswith(crate)]
    parts = [s for s in parts
             if s not in ("bot", "moisan", "game", "nav", "rules", "types", "protocol")]
    for part in reversed(parts):
        if len(part) > 2 and not part.startswith("_"):
            return part
    return parts[-1] if parts else "?"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--workdir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    packet_bytes = args.packet.read_bytes()
    if hashlib.sha256(packet_bytes).hexdigest() != PACKET_SHA256:
        raise RuntimeError("packet SHA-256 mismatch")
    packet = json.loads(gzip.decompress(packet_bytes))

    work = args.workdir
    work.mkdir(parents=True, exist_ok=True)
    for stale in work.glob("*.profraw"):
        stale.unlink()
    binary = work / "instrumented.bin"
    crate = args.candidate.stem.replace("-", "_")

    subprocess.run(
        ["rustc", "--edition=2021", "-O", "-Awarnings", "-C", "instrument-coverage",
         "--crate-name", crate, str(args.candidate), "-o", str(binary)],
        check=True, capture_output=True, text=True,
    )

    identical = 0
    for index, row in enumerate(packet["rows"]):
        env = dict(os.environ, LLVM_PROFILE_FILE=str(work / f"game-{index:02d}.profraw"))
        proc = subprocess.run([str(binary)], input=row["transcript"],
                              capture_output=True, text=True, timeout=300, env=env)
        identical += proc.stdout.strip() == row["baseline_output"].strip()
    if identical != len(packet["rows"]):
        raise RuntimeError(f"instrumented build diverged: {identical}/{len(packet['rows'])}")

    tools = llvm_bin()
    profdata = work / "merged.profdata"
    subprocess.run([str(tools / "llvm-profdata"), "merge", "-sparse",
                    *[str(p) for p in sorted(work.glob("*.profraw"))],
                    "-o", str(profdata)], check=True, capture_output=True)
    export = subprocess.run([str(tools / "llvm-cov"), "export", str(binary),
                             f"-instr-profile={profdata}", "-format=text"],
                            check=True, capture_output=True, text=True).stdout
    data = json.loads(export)["data"][0]

    agg = defaultdict(lambda: {"regions": 0, "cold": 0, "entries": 0})
    dead_units = 0
    for function in data["functions"]:
        key = owner(function["name"], crate)
        agg[key]["entries"] += function["count"]
        dead_units += function["count"] == 0
        for region in function["regions"]:
            agg[key]["regions"] += 1
            agg[key]["cold"] += region[4] == 0

    totals = data["totals"]
    result = {
        "schema": "troll-farm-e7a-coverage-panel-v1",
        "candidate": {
            "path": str(args.candidate),
            "sha256": hashlib.sha256(args.candidate.read_bytes()).hexdigest(),
        },
        "packet_sha256": PACKET_SHA256,
        "games": len(packet["rows"]),
        "instrumented_output_identical": identical,
        "region_coverage_percent": round(totals["regions"]["percent"], 3),
        "function_coverage_percent": round(totals["functions"]["percent"], 3),
        "never_executed_units": dead_units,
        "by_function": {
            name: {
                "regions": v["regions"],
                "cold_regions": v["cold"],
                "coverage_percent": round(100 * (v["regions"] - v["cold"]) / v["regions"], 2)
                if v["regions"] else None,
                "entries": v["entries"],
            }
            for name, v in sorted(agg.items(), key=lambda kv: -kv[1]["cold"])
        },
        "evidence_boundary": (
            "coverage of the 25-game frozen open packet only; those games were "
            "selected as liveness counterexamples, not sampled uniformly, so cold "
            "regions may be cold in this sample rather than on the ladder. Cold is "
            "not dead: removing cold code is a behavior change."
        ),
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in
                      ("region_coverage_percent", "function_coverage_percent",
                       "never_executed_units", "instrumented_output_identical")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
