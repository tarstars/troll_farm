#!/usr/bin/env python3
"""Three arms from ONE source and ONE line — task `20260826-candidate-3-keep-your-goal`.

`cure3-keep-v6.rs` carries exactly one flag line:

    const KEEP_RULE_ENABLED: bool = true; const NARRATE_V6_ENABLED: bool = true;

Each arm is that source with that single line rewritten -- nothing else. The script proves it:
after generating an arm it diffs the arm against the source and REFUSES unless exactly one line
differs, so "one source and a compile-time flag" is a checked property of the bytes rather than a
claim in a report.

    instrument  KEEP=true  NARRATE=true    the G-1 read; can never be champion
    candidate   KEEP=true  NARRATE=false   the score block, and the ladder if the panel passes
    ruleoff     KEEP=false NARRATE=true    the containment reference (r5 §9.1)

Each arm is compiled (rustc --edition=2021 -O) before its hash is recorded: an arm that does not
build has no hash worth publishing.
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
SOURCE = HERE / "cure3-keep-v6.rs"
MANIFEST = HERE / "arm-manifest.json"
CHAMPION_SHA = "ad1ae4eff70a5569e03e2149882bb22510746f4f8592907a5dfb936943ef0bfb"

FLAG_LINE = ("            const KEEP_RULE_ENABLED: bool = {keep};"
             " const NARRATE_V6_ENABLED: bool = {narrate};")

ARMS = {
    "instrument": (True, True),
    "candidate": (True, False),
    "ruleoff": (False, True),
}


class BuildError(Exception):
    pass


def rustc_env() -> dict:
    """rustup installs rustc under ~/.cargo/bin, which a non-login shell does not have."""
    env = dict(os.environ)
    cargo_bin = str(Path.home() / ".cargo" / "bin")
    if cargo_bin not in env.get("PATH", ""):
        env["PATH"] = cargo_bin + os.pathsep + env.get("PATH", "")
    return env


def flag_line(keep: bool, narrate: bool) -> str:
    return FLAG_LINE.format(keep="true" if keep else "false",
                            narrate="true" if narrate else "false")


def compile_check(text: str, crate: str) -> None:
    with tempfile.TemporaryDirectory(prefix="cure3-build-") as wd:
        completed = subprocess.run(
            ["rustc", "--edition=2021", "-O", "-Awarnings", "--crate-name", crate, "-",
             "-o", str(Path(wd) / crate)],
            input=text, text=True, capture_output=True, timeout=600, env=rustc_env())
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
        "task": "20260826-candidate-3-keep-your-goal",
        "packet": "claude_1/cure3/g0-candidate-3-2026-08-26-r6.md",
        "source": str(SOURCE.relative_to(REPO)),
        "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "base": "readable/door1-champion.rs",
        "base_sha256": CHAMPION_SHA,
        "arms": {},
    }
    for name, (keep, narrate) in ARMS.items():
        text = "\n".join(flag_line(keep, narrate) if l == marker else l for l in lines)
        diff = [i for i, (a, b) in enumerate(zip(lines, text.split("\n"))) if a != b]
        expected = 0 if (keep, narrate) == (True, True) else 1
        if len(diff) != expected:
            raise BuildError(f"{name}: {len(diff)} lines differ from the source, expected "
                             f"{expected}")
        compile_check(text, f"cure3_{name}")
        out = HERE / f"arm-{name}.rs"
        out.write_text(text)
        sha = hashlib.sha256(text.encode()).hexdigest()
        (HERE / f"arm-{name}.rs.sha256").write_text(f"{sha}  arm-{name}.rs\n")
        manifest["arms"][name] = {
            "path": str(out.relative_to(REPO)), "sha256": sha,
            "keep_rule_enabled": keep, "narrate_v6_enabled": narrate,
            "lines_differing_from_source": len(diff),
        }
        print(f"  {name:<11} KEEP={str(keep):<5} NARRATE={str(narrate):<5} "
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
