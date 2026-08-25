#!/usr/bin/env python3
"""Three arms from ONE source and ONE line.

`cure2-swap-v5.rs` carries exactly one flag line:

    const HOLD_RULE_ENABLED:bool=true;const NARRATE_V4_ENABLED:bool=true;

Each arm is that source with that single line rewritten -- nothing else. The script proves it:
after generating an arm it diffs the arm against the source and REFUSES unless exactly one line
differs, so "one source and a compile-time flag" is a checked property of the bytes rather than a
claim in a report.

    instrument  SWAP=true  NARRATE=true    the G-2 real-game read; can never be champion
    candidate   SWAP=true  NARRATE=false   the G-3 score block, and the ladder if kept
    ruleoff     SWAP=false NARRATE=true    the alpha parity reference

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
SOURCE = HERE / "cure2-swap-v5.rs"
MANIFEST = HERE / "arm-manifest.json"

FLAG_LINE = ("            const SWAP_RULE_ENABLED:bool={hold};"
             "const NARRATE_V5_ENABLED:bool={narrate};")

ARMS = {
    "instrument": (True, True),
    "candidate": (True, False),
    "ruleoff": (False, True),
}


class BuildError(Exception):
    pass


def rustc_env() -> dict:
    """Same PATH repair as claude_1/banana-restoration-r2/semantic_harness.py: rustup installs
    rustc under ~/.cargo/bin, which a non-login shell does not have."""
    env = dict(os.environ)
    cargo_bin = str(Path.home() / ".cargo" / "bin")
    if cargo_bin not in env.get("PATH", ""):
        env["PATH"] = cargo_bin + os.pathsep + env.get("PATH", "")
    return env


def flag_line(hold: bool, narrate: bool) -> str:
    return FLAG_LINE.format(hold="true" if hold else "false",
                            narrate="true" if narrate else "false")


def compile_check(text: str, crate: str) -> None:
    with tempfile.TemporaryDirectory(prefix="cure1-build-") as wd:
        completed = subprocess.run(
            ["rustc", "--edition=2021", "-O", "-Awarnings", "--crate-name", crate, "-",
             "-o", str(Path(wd) / crate)],
            input=text, text=True, capture_output=True, timeout=300, env=rustc_env())
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
        "task": "20260825-dance-cure-candidate-2-swap",
        "source": str(SOURCE.relative_to(REPO)),
        "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "base": "claude_1/cure1/cure1-hold-v4.rs",
        "base_sha256": "cc4b308705883f10192065dd205a36eb78baee3c1068a0697131b791f3d46e9b",
        "champion_sha256": "547fa706cc1c684a1f8c2a08174792d95e553b2382facfe15884d2ef544070b0",
        "arms": {},
    }
    for name, (hold, narrate) in ARMS.items():
        text = "\n".join(flag_line(hold, narrate) if l == marker else l for l in lines)
        diff = [i for i, (a, b) in enumerate(zip(source.split("\n"), text.split("\n"))) if a != b]
        expected = 0 if (hold, narrate) == (True, True) else 1
        if len(diff) != expected:
            raise BuildError(f"{name}: {len(diff)} lines differ from the source, expected "
                             f"{expected}")
        compile_check(text, f"cure2_{name}")
        out = HERE / f"arm-{name}.rs"
        out.write_text(text)
        sha = hashlib.sha256(text.encode()).hexdigest()
        (HERE / f"arm-{name}.rs.sha256").write_text(f"{sha}  arm-{name}.rs\n")
        manifest["arms"][name] = {
            "path": str(out.relative_to(REPO)), "sha256": sha,
            "swap_rule_enabled": hold, "narrate_v5_enabled": narrate,
            "lines_differing_from_source": len(diff),
        }
        print(f"  {name:<11} SWAP={str(hold):<5} NARRATE={str(narrate):<5} "
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
