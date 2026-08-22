#!/usr/bin/env python3
r"""The revised both-ways/coverage gate, OBSERVED FAILING on the probe it was written to catch.

Task `20260821-osc032-033-no-goal-instrument`, G-1 revision.

A mechanism that cannot fail is not a check. The first delivery of this task shipped a
both-ways control that passed because it had been reshaped around the case it should have
refused; codex_1 caught that at G-1. Asserting that the replacement is stricter is worth
nothing unless the replacement is watched refusing something, so this runs
`no_goal_census.py` against the PREVIOUS five-anchor probe — the exact artifact whose gap the
revision repairs — and requires a non-zero exit naming the coverage failure.

It restores every artifact it touched, and verifies the restoration by digest rather than
trusting the `finally`. Observed 2026-08-21: exit 1, with all three failure kinds firing
(no non-idle route named for OSC-033; 34 and 20 employed turns unnamed; 14 idle turns
unnamed; audited-unit coverage inexact in both fixtures).

Run:  python3 claude_1/nogoal/gate_negative_control.py
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
BUILDER = REPO / "claude_1/picker2/make_route_probe.py"
MANIFEST = HERE / "route-probe-manifest-2026-08-21.json"
LIVE = "EXTRA_EDITS = {\"door1-champion\": EARLY_EDITS}"
STUB = "EXTRA_EDITS = {}  # NEGATIVE CONTROL — the pre-revision five-anchor probe"

# Every failure line the five-anchor probe must produce. Checking the TEXT, not just the exit
# code, is what keeps this from passing on an unrelated crash.
MUST_REPORT = [
    "OSC-033: the tap named NO non-idle route anywhere in this fixture",
    "OSC-032: 34 employed turns produced no route row",
    "OSC-033: 20 employed turns produced no route row",
    "OSC-033: 14 idle turns produced no route row",
]


def digests():
    man = json.loads(MANIFEST.read_text())["door1-champion"]
    probe = REPO / man["probe"]
    return man["probe_sha256"], hashlib.sha256(probe.read_bytes()).hexdigest(), len(man["anchors"])


def main() -> int:
    want_probe, got_probe, n_anchors = digests()
    if want_probe != got_probe or n_anchors != 7:
        print(f"refusing to run: the live artifacts are not the 7-anchor build "
              f"({n_anchors} anchors, manifest {want_probe[:12]}, disk {got_probe[:12]}). "
              f"Rebuild before running the control.", file=sys.stderr)
        return 2
    builder_src = BUILDER.read_text()
    manifest_src = MANIFEST.read_text()
    probe_path = REPO / json.loads(manifest_src)["door1-champion"]["probe"]
    probe_src = probe_path.read_text()
    if builder_src.count(LIVE) != 1:
        print(f"refusing to run: {LIVE!r} not found exactly once in the builder; the control "
              f"cannot be sure what it is disabling.", file=sys.stderr)
        return 2
    try:
        BUILDER.write_text(builder_src.replace(LIVE, STUB))
        subprocess.run([sys.executable, str(BUILDER), "--subject", "door1-champion",
                        "--manifest", str(MANIFEST)], check=True, cwd=REPO)
        BUILDER.write_text(builder_src)
        n = len(json.loads(MANIFEST.read_text())["door1-champion"]["anchors"])
        if n != 5:
            print(f"the control built {n} anchors, expected the pre-revision 5", file=sys.stderr)
            return 2
        run = subprocess.run([sys.executable, str(HERE / "no_goal_census.py")],
                             capture_output=True, text=True, cwd=REPO)
        out = run.stdout + run.stderr
    finally:
        BUILDER.write_text(builder_src)
        MANIFEST.write_text(manifest_src)
        probe_path.write_text(probe_src)
        want, got, n_anchors = digests()
        if want != got or n_anchors != 7:
            print(f"RESTORATION FAILED: manifest {want[:12]} vs disk {got[:12]}, "
                  f"{n_anchors} anchors. Rebuild before trusting any artifact.", file=sys.stderr)
            return 2
        print(f"restored: {n_anchors} anchors, probe {got[:12]}")
    if run.returncode == 0:
        print("CONTROL FAILED: the five-anchor probe PASSED the gate. The gate does not "
              "discriminate and no result may be reported on its strength.", file=sys.stderr)
        return 1
    missing = [m for m in MUST_REPORT if m not in out]
    if missing:
        print("CONTROL FAILED: the gate refused, but not for the expected reasons. Missing:",
              file=sys.stderr)
        for m in missing:
            print(f"  {m}", file=sys.stderr)
        return 1
    print(f"\nCONTROL PASSED: the five-anchor probe is REFUSED (exit {run.returncode}), "
          f"and all {len(MUST_REPORT)} expected failure lines were reported.")
    for line in out.splitlines():
        if line.strip().startswith(("OSC-032:", "OSC-033:")):
            print(f"  {line.strip()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
