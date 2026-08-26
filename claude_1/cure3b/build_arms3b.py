#!/usr/bin/env python3
"""Three arms of Candidate 3b from ONE source and ONE line — task
`20260826-candidate-3b-stuck-holder-release`.

Identical in method to `claude_1/cure3/build_arms3.py`, which is deliberate: the shape that made
"one source and a compile-time flag" a checked property of the bytes for Candidate 3 has to keep
checking it now that the line carries a third flag. `cure3b-keep-v7.rs` carries exactly one flag
line:

    const KEEP_RULE_ENABLED: bool = true; const NARRATE_V6_ENABLED: bool = true; const STUCK_RELEASE_ENABLED: bool = true;

Each arm is that source with that single line rewritten -- nothing else. After generating an arm
the script diffs it against the source and REFUSES unless exactly one line differs.

    instrument  KEEP=true  NARRATE=true  STUCK=true    the panel read
    candidate   KEEP=true  NARRATE=false STUCK=true    the score block, and the ladder on a pass
    ruleoff     KEEP=false NARRATE=true  STUCK=false   the containment reference

The rule-off arm turns the stuck release off with the keep rule: rule iii only ever releases a
kept goal, so with no kept goals it could not fire anyway, and leaving it `true` there would put a
flag in the containment reference that means nothing. Containment is the gate that says a cure
with its rule off is byte-identical to the champion; it must be read against a genuinely ruleless
arm.

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
SOURCE = HERE / "cure3b-keep-v7.rs"
MANIFEST = HERE / "arm-manifest.json"
CHAMPION_SHA = "ad1ae4eff70a5569e03e2149882bb22510746f4f8592907a5dfb936943ef0bfb"

FLAG_LINE = ("            const KEEP_RULE_ENABLED: bool = {keep};"
             " const NARRATE_V6_ENABLED: bool = {narrate};"
             " const STUCK_RELEASE_ENABLED: bool = {stuck};")

ARMS = {
    "instrument": (True, True, True),
    "candidate": (True, False, True),
    "ruleoff": (False, True, False),
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


def flag_line(keep: bool, narrate: bool, stuck: bool) -> str:
    return FLAG_LINE.format(keep="true" if keep else "false",
                            narrate="true" if narrate else "false",
                            stuck="true" if stuck else "false")


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
    marker = flag_line(True, True, True)
    if lines.count(marker) != 1:
        raise BuildError(f"the flag line occurs {lines.count(marker)} times in the source, "
                         f"expected exactly 1")
    manifest = {
        "task": "20260826-candidate-3b-stuck-holder-release",
        "card": "coordination/tasks/20260826-candidate-3b-stuck-holder-release.md",
        "parent_source": "claude_1/cure3/cure3-keep-v6.rs",
        "source": str(SOURCE.relative_to(REPO)),
        "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "base": "readable/door1-champion.rs",
        "base_sha256": CHAMPION_SHA,
        "arms": {},
    }
    for name, (keep, narrate, stuck) in ARMS.items():
        text = "\n".join(flag_line(keep, narrate, stuck) if l == marker else l
                         for l in lines)
        diff = [i for i, (a, b) in enumerate(zip(lines, text.split("\n"))) if a != b]
        expected = 0 if (keep, narrate, stuck) == (True, True, True) else 1
        if len(diff) != expected:
            raise BuildError(f"{name}: {len(diff)} lines differ from the source, expected "
                             f"{expected}")
        compile_check(text, f"cure3b_{name}")
        out = HERE / f"arm-{name}.rs"
        out.write_text(text)
        sha = hashlib.sha256(text.encode()).hexdigest()
        (HERE / f"arm-{name}.rs.sha256").write_text(f"{sha}  arm-{name}.rs\n")
        manifest["arms"][name] = {
            "path": str(out.relative_to(REPO)), "sha256": sha,
            "keep_rule_enabled": keep, "narrate_v6_enabled": narrate,
            "stuck_release_enabled": stuck,
            "lines_differing_from_source": len(diff),
        }
        print(f"  {name:<11} KEEP={str(keep):<5} NARRATE={str(narrate):<5} "
              f"STUCK={str(stuck):<5} compiles, {len(diff)} line differs  sha256 {sha[:16]}")
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(f"  manifest -> {MANIFEST.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BuildError as exc:
        print(f"BUILD REFUSED: {exc}", file=sys.stderr)
        sys.exit(2)
