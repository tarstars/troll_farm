#!/usr/bin/env python3
r"""Derive the 167-turn manifest EXACTLY as pinned by the task owner.

Pin: `local_claude_1/chop4c/167-manifest-derivation-pin-2026-08-18.md` (2026-08-18T08:01:52Z).
Every degree of freedom — population, predicate, expected count — was closed by that document
BEFORE any manifest existed, and it was written because both the reviewer and I said the same
thing: the implementer must not select this subset after seeing the chop4c result.

**This script exercises no selection.** It executes the pinned predicate and reports what comes
out. The chop4c instrument plays NO role here; the derivation runs on the accepted pool-1/-3
stack, byte-pinned by sha256 and verified at startup.

Predicate — a turn t is in the manifest iff ALL of:
  1. t is in OSC-031's window [11, 200];
  2. the accepted pool-3 per-turn token for unit 0 at t is `NO_GOAL_ASSIGNED`;
  3. the accepted oracle's `eligible_actions(tr, 0, t)` is EXACTLY {"CHOP"}.

STOP RULE: |manifest| must be 167. Any other number is a discrepancy BETWEEN THE ACCEPTED
ARTIFACTS, to be reported and reconciled on the record — never adjusted to fit. This script
fails loudly rather than emitting a manifest of the wrong size.
"""
import hashlib, json, sys, tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "claude_1/t1"))
sys.path.insert(0, str(REPO / "claude_1/hstarve1"))
sys.path.insert(0, str(REPO / "claude_1/pipeline"))
import cause_table as CT   # noqa: E402
import coverage as C       # noqa: E402
import fixture_harness as H  # noqa: E402
import fuzz_panel as fp    # noqa: E402
import oracle as O         # noqa: E402
import trace_detectors as td  # noqa: E402

PINNED = {
    "claude_1/hstarve1/instrumented-hstarve2.rs":
        "42128838d014b96b2c6ae6868f30c8ca068c6ac0c7b6759a145f72c491c7b101",
    "claude_1/hstarve1/oracle.py":
        "542202f9b0705d4351853912d4bb16fca8bd2dc5256fcc19a4763c511d0e99a5",
    "claude_1/hstarve1/audit.py":
        "cf690aa57dacafd8ee12608da9414e349460e22545f4dcd2fdf41acea3045d15",
    "claude_1/hstarve1/cause-table-pool3-2026-08-17.json":
        "79cc5b9d3d2198d5033c62bf7d2f2e3259fc4bd6f54a88cb7ae3600123cb9466",
    "claude_1/hstarve1/mechanism-pool5-2026-08-17.json":
        "fc248786126d5b96d3f3d4efbe8c62a8b1b463ea6fdd55412e2f581318eb095f",
}
EXPECTED = 167
UNIT = 0


class StopAndReport(RuntimeError):
    """The pin's STOP rule. Never resolved by adjusting the predicate or the count."""


def main():
    for rel, want in PINNED.items():
        got = hashlib.sha256((REPO / rel).read_bytes()).hexdigest()
        if got != want:
            raise StopAndReport(f"pinned tooling changed: {rel}\n  want {want}\n  got  {got}")
    print(f"tooling: all {len(PINNED)} pinned shas verified")

    cfg = json.loads(H.CONFIG.read_text())
    sit = H.load_situations(["OSC-031"])[0]
    lo, hi = sit["window"]["turn_start"], sit["window"]["turn_end"]

    wd = Path(tempfile.mkdtemp(prefix="c4c-man-"))
    (wd / "i").mkdir(); (wd / "p").mkdir()
    instr = H.compile_candidate(REPO / "claude_1/hstarve1/instrumented-hstarve2.rs", wd / "i")
    plain = H.compile_candidate(H.RESIDENT, wd / "p")

    err = C.check_parity(sit, cfg, plain, instr)     # shared accepted path
    C.check_final_stage(sit, err)
    C.check_coverage(sit, err)
    spec = H.spec_for(sit, cfg)
    transcript, commands, _ = C.run_diagnostic(instr, fp.make_referee(spec), int(cfg["turns"]))
    tr = td.build_trace(transcript, commands)
    rows = CT.classify(sit, *CT.parse(err), tr, force_units=[UNIT])

    per_turn = [p for r in rows for p in r.get("per_turn", [])]
    manifest, rejected = [], {"token": 0, "eligible": 0}
    for p in per_turn:
        t = p["turn"]
        if not (lo <= t <= hi):
            continue
        if p["token"] != "NO_GOAL_ASSIGNED":
            rejected["token"] += 1
            continue
        elig = set(O.eligible_actions(tr, UNIT, t))
        if elig != {"CHOP"}:
            rejected["eligible"] += 1
            continue
        manifest.append({"turn": t, "token": p["token"], "eligible_actions": sorted(elig)})

    turns = sorted(m["turn"] for m in manifest)
    print(f"window [{lo},{hi}] · pool-3 NO_GOAL turns for unit {UNIT}: "
          f"{sum(1 for p in per_turn if p['token'] == 'NO_GOAL_ASSIGNED')}")
    print(f"excluded by token: {rejected['token']} · by eligibility != {{CHOP}}: "
          f"{rejected['eligible']}")
    print(f"|manifest| = {len(turns)}  (pre-registered {EXPECTED})")

    if len(turns) != EXPECTED:
        raise StopAndReport(
            f"|manifest| = {len(turns)}, pre-registered {EXPECTED}. This is a discrepancy "
            f"BETWEEN ACCEPTED ARTIFACTS (pool-3 table / pool-5 aggregate / oracle), not a "
            f"licence to adjust the predicate. Reporting; G-4c.3 blocks until reconciled.")

    out = {"task": "20260818-osc031-chop-clause-instrument",
           "derivation_pin": "local_claude_1/chop4c/167-manifest-derivation-pin-2026-08-18.md",
           "situation": "OSC-031", "unit": UNIT, "window": [lo, hi],
           "predicate": ["turn in window", "pool-3 token == NO_GOAL_ASSIGNED",
                         "oracle eligible_actions == exactly {CHOP}"],
           "expected_count": EXPECTED, "count": len(turns),
           "tooling_sha256": PINNED, "turns": turns, "per_turn": manifest}
    p = REPO / "claude_1/chop4c/osc031-167-manifest.json"
    p.write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {p.relative_to(REPO)}  sha256={hashlib.sha256(p.read_bytes()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
