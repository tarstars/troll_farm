#!/usr/bin/env python3
"""r5 §9.1 — the **containment gate** on the 34 frozen situations, Candidate 3.

The claim under test: *the rule-off arm, with its `MSG` fragment stripped, is byte-identical in
play to its base*. One counterexample is a BLOCK on my own arm, and it is pre-committed as one.

Both halves are checked, because a token comparison alone would miss the second: two command
streams can agree token for token and still leave different worlds if the harness feeds them
differently, so the referee state after the last turn is compared field by field.

The rule-off arm carries the SAME instrumented resolver as the candidate
(`resolve_move_conflicts` with the branch map and the W-collision count threaded through) and the
same narrator. That is the point of the gate: it proves the instrumentation and the `KEEP` gate
are behaviour-neutral, so any difference the candidate arm later shows on the panel belongs to
the keep rule and to nothing else.

    python3 claude_1/cure3/containment.py [--only OSC-001,OSC-004] [--arm ruleoff] [--rule-on]
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
for _p in ("claude_1/t1", "claude_1/pipeline", "claude_1/banana-restoration-r2",
           "claude_1/narrate6"):
    sys.path.insert(0, str(REPO / _p))

import fixture_harness as fh        # noqa: E402
import fuzz_panel as fp             # noqa: E402
import regression_tests as rt       # noqa: E402
import semantic_harness as sh       # noqa: E402
import narrate6 as n6               # noqa: E402

BASE = REPO / "readable" / "door1-champion.rs"
BASE_SHA = "ad1ae4eff70a5569e03e2149882bb22510746f4f8592907a5dfb936943ef0bfb"


strip_msg = n6.strip_msg


def referee_state(ref) -> str:
    return json.dumps({
        "turn": ref.turn,
        "next_id": ref.next_id,
        "units": {str(uid): {k: (list(v) if isinstance(v, (tuple, list)) else v)
                             for k, v in unit.items()}
                  for uid, unit in sorted(ref.units.items())},
        "plants": {str(list(cell)): dict(sorted(plant.items()))
                   for cell, plant in sorted(ref.plants.items())},
        "inventory": list(ref.inv),
        "opponent_inventory": list(ref.opp_inv),
    }, sort_keys=True, default=str)


def run_arm(sit, binary, cfg):
    spec = fh.spec_for(sit, cfg)
    ref = fp.make_referee(spec)
    transcript, commands = rt.run_binary_custom(Path(binary), ref, int(cfg["turns"]))
    import trace_detectors as td
    tr = td.build_trace(transcript, commands)
    return commands.rstrip("\n").split("\n"), referee_state(ref), tr


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--only")
    ap.add_argument("--arm", default="ruleoff")
    ap.add_argument("--rule-on", action="store_true",
                    help="the arm has the keep rule ON: report divergence instead of demanding "
                         "parity")
    ap.add_argument("--out")
    args = ap.parse_args()

    import hashlib
    base_text = BASE.read_text()
    sha = hashlib.sha256(base_text.encode()).hexdigest()
    if sha != BASE_SHA:
        print(f"REFUSED: base is {sha}, expected {BASE_SHA}", file=sys.stderr)
        return 2

    arm = HERE / f"arm-{args.arm}.rs"
    out = Path(args.out) if args.out else HERE / "results" / f"containment-{args.arm}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    cfg = json.loads(fh.CONFIG.read_text())
    sits = fh.load_situations(args.only.split(",") if args.only else None)
    rows, telemetry_errors = [], []
    census = n6.new_census()
    with tempfile.TemporaryDirectory(prefix="cure3-containment-") as wd:
        wd = Path(wd)
        base_bin, arm_bin = wd / "base.bin", wd / "arm.bin"
        sh.compile_text(base_text, base_bin, crate="cure3_base")
        sh.compile_text(arm.read_text(), arm_bin, crate="cure3_arm")
        for sit in sits:
            sid = sit["id"]
            base_lines, base_state, _ = run_arm(sit, base_bin, cfg)
            arm_lines, arm_state, arm_trace = run_arm(sit, arm_bin, cfg)
            stripped = [strip_msg(line) for line in arm_lines]
            base_stripped = [strip_msg(line) for line in base_lines]
            identical = stripped == base_stripped
            first_diff = None
            if not identical:
                for i, (a, b) in enumerate(zip(base_stripped, stripped), 1):
                    if a != b:
                        first_diff = {"turn": i, "base": a, "arm": b}
                        break
                if first_diff is None:
                    first_diff = {"turn": None, "base_turns": len(base_stripped),
                                  "arm_turns": len(stripped)}
            errs = n6.check_telemetry(sid, arm_trace, arm_lines, census,
                                      rule_off=not args.rule_on)
            telemetry_errors.extend(f"{sid}: {e}" for e in errs)
            rows.append({
                "id": sid, "turns": len(arm_lines), "telemetry_errors": len(errs),
                "byte_identical_without_msg": identical,
                "referee_state_identical": base_state == arm_state,
                "first_divergence": first_diff,
            })
            mark = ("PARITY" if identical and base_state == arm_state and not errs
                    else "DIVERGES" if args.rule_on and not errs else "FAILED")
            print(f"  {mark:<8} {sid:<10} turns {len(arm_lines):>3}  "
                  f"telemetry errors {len(errs)}")

    parity = sum(1 for r in rows if r["byte_identical_without_msg"])
    states = sum(1 for r in rows if r["referee_state_identical"])
    ok = (not telemetry_errors) and (args.rule_on or (parity == len(rows) == states))
    report = {
        "gate": f"containment, r5 §9.1 (NARRATE v6, arm {args.arm})",
        "task": "20260826-candidate-3-keep-your-goal",
        "packet": "claude_1/cure3/g0-candidate-3-2026-08-26-r6.md",
        "base": str(BASE.relative_to(REPO)), "base_sha256": BASE_SHA,
        "arm": str(arm.relative_to(REPO)),
        "rule_on": args.rule_on,
        "fixtures": len(rows),
        "byte_identical": parity,
        "referee_state_identical": states,
        "status": "PASS" if ok else "FAIL",
        "telemetry_error_count": len(telemetry_errors),
        "telemetry_errors": telemetry_errors[:200],
        "census": census,
        "rows": rows,
    }
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"\n  {report['status']}  {parity}/{len(rows)} byte-identical, "
          f"{states}/{len(rows)} same referee state  -> {out}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
