#!/usr/bin/env python3
"""Build the C-16 RED-HALF arms: `SWAP_P3_SCOPING_ENABLED=false`, and nothing else.

G-0 §9, control C-16: *R-B red half -- `SWAP_P3_SCOPING_ENABLED=false` on an identical
orchard-eligible map. P3 fires => the scoping is doing work, not decoration.*

§3.6 adopts R-B verbatim: on a seat view satisfying the base's `orchard_eligible` predicate the
exchange is inert for the WHOLE game, because `fuzz_panel.eval_p3` compares the WHOLE command
stream on those maps. That is a scoping cost, not a neutrality claim, and a cost is only real if
the thing it buys can be seen. C-16 is the seeing: flip the one line, keep the map, the seat, the
seeds and the opponent identical, and grade P3 exactly as the panel does.

Two arms, because the graded stream and the attributing stream are not the same stream:

  arm-c16noscope.rs             from `arm-candidate.rs`  (NARRATE_V5_ENABLED=false)
      The GRADED arm. P3 compares the candidate's whole command stream against the parent's, so a
      telemetry `MSG` fragment would make every eligible game diverge for a reason that has
      nothing to do with the exchange. Only a narrate-off arm can be graded by `eval_p3`.

  arm-c16noscope-instrument.rs  from `arm-instrument.rs` (NARRATE_V5_ENABLED=true)
      The ATTRIBUTING arm. It carries the v5 wire, so `sw=` says on which turns an exchange was
      granted. It is only allowed to explain the graded arm's divergence after the driver has
      checked that the two streams are identical in play (MSG stripped) -- gate G-I.

Each arm must differ from its own source arm in EXACTLY ONE LINE, and that line must be the
scoping flag. The generator refuses otherwise, and compiles each arm before recording its hash.

    python3 claude_1/cure2/make_c16_noscope_arms.py
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
OLD = "            const SWAP_P3_SCOPING_ENABLED:bool=true;"
NEW = "            const SWAP_P3_SCOPING_ENABLED:bool=false;"
ARMS = {
    "arm-c16noscope.rs": ("arm-candidate.rs", "cure2_c16noscope", False),
    "arm-c16noscope-instrument.rs": ("arm-instrument.rs", "cure2_c16noscope_instrument", True),
}


class BuildError(Exception):
    pass


def rustc_env() -> dict:
    env = dict(os.environ)
    cargo_bin = str(Path.home() / ".cargo" / "bin")
    if cargo_bin not in env.get("PATH", ""):
        env["PATH"] = cargo_bin + os.pathsep + env.get("PATH", "")
    return env


def compile_check(text: str, crate: str) -> None:
    with tempfile.TemporaryDirectory(prefix="cure2-c16-build-") as wd:
        done = subprocess.run(
            ["rustc", "--edition=2021", "-O", "-Awarnings", "--crate-name", crate, "-",
             "-o", str(Path(wd) / crate)],
            input=text, text=True, capture_output=True, timeout=600, env=rustc_env())
    if done.returncode:
        raise BuildError(f"{crate}: rustc failed\n{done.stderr[:4000]}")


def main() -> int:
    manifest = {"task": "20260825-dance-cure-candidate-2-swap", "control": "C-16",
                "flag": "SWAP_P3_SCOPING_ENABLED", "from": "true", "to": "false", "arms": {}}
    for out_name, (src_name, crate, narrate) in ARMS.items():
        src = (HERE / src_name).read_text()
        lines = src.split("\n")
        if lines.count(OLD) != 1:
            raise BuildError(f"{src_name}: scoping flag line occurs {lines.count(OLD)} times, "
                             f"expected exactly 1")
        text = "\n".join(NEW if line == OLD else line for line in lines)
        diff = [i for i, (a, b) in enumerate(zip(lines, text.split("\n"))) if a != b]
        if len(diff) != 1 or lines[diff[0]] != OLD:
            raise BuildError(f"{out_name}: {len(diff)} lines differ from {src_name}, expected "
                             f"exactly the scoping flag line")
        compile_check(text, crate)
        (HERE / out_name).write_text(text)
        sha = hashlib.sha256(text.encode()).hexdigest()
        (HERE / f"{out_name}.sha256").write_text(f"{sha}  {out_name}\n")
        manifest["arms"][out_name] = {
            "path": str((HERE / out_name).relative_to(REPO)), "sha256": sha,
            "from_arm": src_name,
            "from_arm_sha256": hashlib.sha256(src.encode()).hexdigest(),
            "lines_differing_from_source_arm": len(diff),
            "narrate_v5_enabled": narrate,
            "swap_p3_scoping_enabled": False,
        }
        print(f"  {out_name:<30} from {src_name:<20} compiles, {len(diff)} line differs  "
              f"sha256 {sha[:16]}")
    (HERE / "c16-arm-manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True)
                                                + "\n")
    print(f"  manifest -> {(HERE / 'c16-arm-manifest.json').relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BuildError as exc:
        print(f"BUILD REFUSED: {exc}", file=sys.stderr)
        sys.exit(2)
