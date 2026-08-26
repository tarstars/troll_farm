#!/usr/bin/env python3
"""Three arms of the banana farm from ONE source and ONE line — task
`20260826-banana-farm-candidate` (board row F-2).

Identical in method to `claude_1/cure3b/build_arms3b.py`, deliberately: the shape that makes "one
source and a compile-time flag" a checked property of the bytes has to keep checking it here.
`farm-v8.rs` carries exactly one flag line:

    const KEEP_RULE_ENABLED: bool = false; const NARRATE_V6_ENABLED: bool = true; const FARM_ENABLED: bool = true;

Each arm is that source with that single line rewritten — nothing else. After generating an arm
the script diffs it against the source and REFUSES unless exactly one line differs.

    instrument  FARM=true  NARRATE=true   the panel read, v8 on the wire
    candidate   FARM=true  NARRATE=false  the score block, and ladder slot 3 on a validity pass
    farmoff     FARM=false NARRATE=true   the containment reference (gate C1)

`KEEP_RULE_ENABLED` is false on all three (packet §7 row W3): Candidate 3 is closed and the farm
carries its own stickiness, so the flag is present in the line but never true. The farm-off arm
still narrates, because gate C1 reads `fs=0` and `fp=0` on every turn of it.

Each arm is compiled (rustc --edition=2021 -O) before its hash is recorded.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
SOURCE = HERE / "farm-v8.rs"
MANIFEST = HERE / "arm-manifest.json"
CHAMPION_SHA = "ad1ae4eff70a5569e03e2149882bb22510746f4f8592907a5dfb936943ef0bfb"

FLAG_LINE = ("            const KEEP_RULE_ENABLED: bool = false;"
             " const NARRATE_V6_ENABLED: bool = {narrate};"
             " const FARM_ENABLED: bool = {farm};")

ARMS = {
    "instrument": (True, True),
    "candidate": (True, False),
    "farmoff": (False, True),
}


class BuildError(Exception):
    pass


def rustc_env() -> dict:
    env = dict(os.environ)
    cargo_bin = str(Path.home() / ".cargo" / "bin")
    if cargo_bin not in env.get("PATH", ""):
        env["PATH"] = cargo_bin + os.pathsep + env.get("PATH", "")
    return env


def flag_line(farm: bool, narrate: bool) -> str:
    return FLAG_LINE.format(farm="true" if farm else "false",
                            narrate="true" if narrate else "false")


def compile_check(text: str, crate: str) -> None:
    with tempfile.TemporaryDirectory(prefix="farm-build-") as wd:
        completed = subprocess.run(
            ["rustc", "--edition=2021", "-O", "-Awarnings", "--crate-name", crate, "-",
             "-o", str(Path(wd) / crate)],
            input=text, text=True, capture_output=True, timeout=900, env=rustc_env())
    if completed.returncode:
        raise BuildError(f"{crate}: rustc failed\n{completed.stderr[:4000]}")


def main() -> int:
    source = SOURCE.read_text()
    lines = source.split("\n")
    marker = flag_line(True, True)
    if lines.count(marker) != 1:
        raise BuildError(f"the flag line occurs {lines.count(marker)} times in the source, "
                         f"expected exactly 1")
    manifest = {
        "task": "20260826-banana-farm-candidate",
        "card": "coordination/tasks/20260826-banana-farm-candidate.md",
        "packet": "claude_1/farm/g0-farm-2026-08-26.md",
        "parent_source": "claude_1/cure3/cure3-keep-v6.rs",
        "source": str(SOURCE.relative_to(REPO)),
        "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "base": "readable/door1-champion.rs",
        "base_sha256": CHAMPION_SHA,
        "dialect": "v8",
        "decoder": "claude_1/narrate8/narrate8.py",
        "arms": {},
    }
    for name, (farm, narrate) in ARMS.items():
        text = "\n".join(flag_line(farm, narrate) if line == marker else line for line in lines)
        diff = [i for i, (a, b) in enumerate(zip(lines, text.split("\n"))) if a != b]
        expected = 0 if (farm, narrate) == (True, True) else 1
        if len(diff) != expected:
            raise BuildError(f"{name}: {len(diff)} lines differ from the source, expected "
                             f"{expected}")
        compile_check(text, f"farm_{name}")
        out = HERE / f"arm-{name}.rs"
        out.write_text(text)
        sha = hashlib.sha256(text.encode()).hexdigest()
        (HERE / f"arm-{name}.rs.sha256").write_text(f"{sha}  arm-{name}.rs\n")
        manifest["arms"][name] = {
            "path": str(out.relative_to(REPO)), "sha256": sha,
            "farm_enabled": farm, "narrate_enabled": narrate,
            "keep_rule_enabled": False,
            "lines_differing_from_source": len(diff),
        }
        print(f"  {name:<11} FARM={str(farm):<5} NARRATE={str(narrate):<5} "
              f"compiles, {len(diff)} line differs  sha256 {sha[:16]}")
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(f"  manifest -> {MANIFEST.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BuildError as exc:
        print(f"BUILD REFUSED: {exc}", file=sys.stderr)
        sys.exit(2)
