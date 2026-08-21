#!/usr/bin/env python3
r"""The whole Phase-2 battery, in order, fail-closed — one command for the reviewer.

Every step below is a separate, independently runnable script; this only sequences them and
reports which failed, so that "the package passed" is a statement someone else can reproduce with
one command rather than a claim about eleven separate runs I did.

Order matters and is not cosmetic: nothing may be measured before the candidates are built from
their allowlisted subjects, and no verdict may be read off a panel before its floor is shown to
be matched.

Run:  python3 claude_1/picker2/run_gates.py [--skip-panels]
"""
import argparse, json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
PY = sys.executable

STEPS = [
    ("build (one generator, two subjects, identical patch)",
     [PY, "claude_1/picker2/make_pair_selector_candidate.py", "--check"], False),
    ("probes (both arms, both bases)", [PY, "claude_1/picker2/make_probe.py"], False),
    ("gate 1a BENCHED — fail-first, parity + coverage + P1 liveness",
     [PY, "claude_1/picker2/gate_bench.py"], False),
    ("gate 1b employment cross-check (uninstrumented command stream)",
     [PY, "claude_1/picker2/gate_employment.py"], False),
    ("all-34 sweep, cure-C base", [PY, "claude_1/t1/fixture_harness.py", "--candidate",
     "cgauto/submissions/submitted-sub41153619-cure-c-quiet.rs", "--json",
     "claude_1/picker2/sweep34-cureC-base.json"], False),
    ("all-34 sweep, cure-C P1+P2", [PY, "claude_1/t1/fixture_harness.py", "--candidate",
     "claude_1/picker2/candidate-cureC-p1p2.rs", "--json",
     "claude_1/picker2/sweep34-cureC-p1p2.json"], False),
    ("all-34 sweep, door-1 base", [PY, "claude_1/t1/fixture_harness.py", "--candidate",
     "claude_1/chop4c/candidate-door1.rs", "--json",
     "claude_1/picker2/sweep34-door1-base.json"], False),
    ("all-34 sweep, door-1 P1+P2", [PY, "claude_1/t1/fixture_harness.py", "--candidate",
     "claude_1/picker2/candidate-door1-p1p2.rs", "--json",
     "claude_1/picker2/sweep34-door1-p1p2.json"], False),
    ("panel: cure-C candidate (240)", [PY, "claude_1/pipeline/fuzz_panel.py", "--config",
     "claude_1/pipeline/picker2-cureC-cand-config.json", "--report",
     "claude_1/picker2/panel-cureC-cand.md", "--json",
     "claude_1/picker2/panel-cureC-cand.json"], True),
    ("panel: door-1 matched floor (240)", [PY, "claude_1/pipeline/fuzz_panel.py", "--config",
     "claude_1/pipeline/picker2-door1-floor-config.json", "--report",
     "claude_1/picker2/panel-door1-floor.md", "--json",
     "claude_1/picker2/panel-door1-floor.json"], True),
    ("panel: door-1 candidate (240)", [PY, "claude_1/pipeline/fuzz_panel.py", "--config",
     "claude_1/pipeline/picker2-door1-cand-config.json", "--report",
     "claude_1/picker2/panel-door1-cand.md", "--json",
     "claude_1/picker2/panel-door1-cand.json"], True),
    ("panel: cure-C candidate at 1 process (parity arm)",
     [PY, "claude_1/pipeline/fuzz_panel.py", "--config",
      "claude_1/pipeline/picker2-cureC-cand-1proc-config.json", "--report",
      "claude_1/picker2/panel-cureC-cand-1proc.md", "--json",
      "claude_1/picker2/panel-cureC-cand-1proc.json"], True),
    ("matched-floor check (the reused cure-C floor is THIS candidate's floor)",
     [PY, "claude_1/picker2/check_floor_match.py"], False),
    ("decomposition (map_id, seat), cure-C", [PY, "claude_1/chop4c/phase2_decompose.py",
     "claude_1/picker2/panel-cureC-cand.json", "claude_1/chop4c/osc031-phase2-floor.json",
     "claude_1/picker2/decomposition-cureC-2026-08-20.json"], False),
    ("decomposition (map_id, seat), door-1", [PY, "claude_1/chop4c/phase2_decompose.py",
     "claude_1/picker2/panel-door1-cand.json", "claude_1/picker2/panel-door1-floor.json",
     "claude_1/picker2/decomposition-door1-2026-08-20.json"], False),
    ("de-novo DIRECTION control (swap the arms; healed must reappear as de-novo)",
     [PY, "claude_1/picker2/denovo_direction_control.py"], False),
    ("every behaviour change named", [PY, "claude_1/picker2/named_changes.py"], False),
    ("process-count parity (8-proc vs 1-proc, 240 rows)",
     [PY, "claude_1/chop4c/phase2_parity.py", "claude_1/picker2/panel-cureC-cand.json",
      "claude_1/picker2/panel-cureC-cand-1proc.json",
      "claude_1/picker2/parity-cureC-2026-08-20.json"], False),
    ("latency p95, all four arms", [PY, "claude_1/picker2/latency.py"], False),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-panels", action="store_true",
                    help="reuse the committed panel JSONs instead of re-running the four panels")
    args = ap.parse_args()
    results, ok = [], True
    for label, cmd, is_panel in STEPS:
        if is_panel and args.skip_panels:
            print(f"  SKIPPED  {label}")
            results.append({"step": label, "status": "SKIPPED"})
            continue
        print(f"  RUN      {label}")
        rc = subprocess.run(cmd, cwd=REPO).returncode
        # fuzz_panel exits 1 on a BLOCK verdict, which is a RESULT (the gate is the floor
        # comparison downstream), not a harness failure. Named here rather than swallowed.
        good = rc == 0 or (is_panel and rc == 1)
        ok &= good
        print(f"  {'OK      ' if good else 'FAILED  '} {label} (exit {rc})")
        results.append({"step": label, "exit": rc,
                        "status": "OK" if good else "FAILED",
                        "note": ("fuzz_panel exit 1 = BLOCK verdict, a result not a failure"
                                 if is_panel and rc == 1 else None)})
    (HERE / "gate-battery-run-2026-08-20.json").write_text(
        json.dumps({"task": "20260820-pair-selector-anti-benching", "phase": 2,
                    "steps": results, "all_ok": ok}, indent=2) + "\n")
    print(f"\n  BATTERY: {'ALL STEPS OK' if ok else 'A STEP FAILED — no verdict may be read'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
