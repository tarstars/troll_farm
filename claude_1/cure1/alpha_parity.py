#!/usr/bin/env python3
"""G-1 item 1 — the **alpha parity gate** on the 34 frozen situations.

The claim under test, from the charter: *the rule-off arm with `MSG` stripped is byte-identical in
play to the base*. Parity is codex_1's definition 4: exact ordered gameplay-token equality after
stripping the single `MSG` fragment, plus identical next referee state.

Both halves are checked here. The second half is the one a token comparison alone would miss: two
command streams can agree token for token and still leave different worlds if the harness feeds
them differently, so the referee state after the last turn is compared field by field.

The rule-off arm carries the SAME resolver as the candidate — `resolve_move_conflicts_hold` with
`HOLD_RULE_ENABLED=false`. That is the point of the gate: it proves the two-phase machinery, the
BFS memoization and the branch bookkeeping are behaviour-neutral, so any difference the candidate
arm later shows on the panel belongs to the hold rule and to nothing else.

Also checked on every rule-off turn, from the wire rather than from prose (construction ruling,
section 1): exactly one pass, K* empty (`sp=0`), no `H`, no nonzero `b`.

    python3 claude_1/cure1/alpha_parity.py [--only OSC-001,OSC-004] [--arm ruleoff]
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "claude_1" / "t1"))
sys.path.insert(0, str(REPO / "claude_1" / "pipeline"))
sys.path.insert(0, str(REPO / "claude_1" / "banana-restoration-r2"))
sys.path.insert(0, str(REPO / "claude_1" / "narrate4"))

import fixture_harness as fh        # noqa: E402
import fuzz_panel as fp             # noqa: E402
import regression_tests as rt       # noqa: E402
import semantic_harness as sh       # noqa: E402
import narrate4 as n4               # noqa: E402

BASE = REPO / "cgauto" / "submissions" / "candidate-door1-pure-deletion.rs"


def referee_state(ref):
    """A comparable snapshot of the referee world AFTER the last applied command set.

    Read off the referee's own state dicts (`units`, `plants`, `inv`, `opp_inv`, `turn`,
    `next_id`) rather than through a trace, because 'identical next referee state' is a claim
    about the world the two arms leave behind, not about how a trace renders it.
    """
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
    ap.add_argument("--arm", default="ruleoff", help="arm to compare against the base")
    ap.add_argument("--rule-on", action="store_true",
                    help="the arm has the hold rule ON: skip the rule-off-only wire checks and "
                         "report divergence instead of requiring parity")
    ap.add_argument("--out")
    args = ap.parse_args()

    arm = HERE / f"arm-{args.arm}.rs"
    out = Path(args.out) if args.out else HERE / "results" / f"alpha-parity-{args.arm}.json"
    cfg = json.loads(fh.CONFIG.read_text())
    sits = fh.load_situations(args.only.split(",") if args.only else None)
    rows, telemetry_errors = [], []
    census = n4.new_census()
    with tempfile.TemporaryDirectory(prefix="cure1-alpha-") as wd:
        wd = Path(wd)
        base_bin, arm_bin = wd / "base.bin", wd / "arm.bin"
        sh.compile_text(BASE.read_text(), base_bin, crate="cure1_alpha_base")
        sh.compile_text(arm.read_text(), arm_bin, crate="cure1_alpha_arm")
        for sit in sits:
            sid = sit["id"]
            base_lines, base_state, _ = run_arm(sit, base_bin, cfg)
            arm_lines, arm_state, arm_trace = run_arm(sit, arm_bin, cfg)
            stripped = [n4.strip_msg(line) for line in arm_lines]
            base_stripped = [n4.strip_msg(line) for line in base_lines]
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
            errs = n4.check_telemetry(sid, arm_trace, arm_lines, census,
                                      rule_off=not args.rule_on)
            telemetry_errors.extend(f"{sid}: {e}" for e in errs)
            rows.append({
                "id": sid, "turns": len(arm_lines),
                "byte_identical_without_msg": identical,
                "referee_state_identical": base_state == arm_state,
                "first_divergence": first_diff,
                "telemetry_errors": len(errs),
                "base_msg_tokens": sum(len(n4.msg_fragments(l)) for l in base_lines),
                "arm_msg_tokens": sum(len(n4.msg_fragments(l)) for l in arm_lines),
            })
            mark = ("PARITY" if identical and base_state == arm_state and not errs
                    else "DIVERGES" if args.rule_on else "FAILED")
            print(f"  {mark:<8} {sid:<10} turns {len(arm_lines):>3}  "
                  f"telemetry errors {len(errs)}")

    parity = sum(1 for r in rows if r["byte_identical_without_msg"])
    states = sum(1 for r in rows if r["referee_state_identical"])
    ok = (not telemetry_errors) and (args.rule_on or (parity == len(rows) == states))
    report = {
        "gate": f"alpha parity (NARRATE v4, arm {args.arm})",
        "task": "20260825-dance-cure-candidate-1-hold",
        "ruling": "charter local_claude_1 20260825T075500Z; construction ruling 20260825T085500Z; "
                  "parity definition codex_1 20260825T080228Z item 4",
        "base": str(BASE.relative_to(REPO)),
        "arm": str(arm.relative_to(REPO)),
        "rule_on": args.rule_on,
        "fixtures": len(rows),
        "byte_identical_without_msg": parity,
        "referee_state_identical": states,
        "telemetry_error_count": len(telemetry_errors),
        "telemetry_errors": telemetry_errors[:40],
        "verdict": "PASS" if ok else "FAIL",
        "census": census,
        "not_proven_here": "platform non-interference: this harness does not react to command "
                           "count, ordering or line length; a telemetry arm emits a MSG token on "
                           "every turn where the base emits one on turn 1 only",
        "rows": rows,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"\n  alpha parity ({args.arm}): {parity}/{len(rows)} byte-identical without MSG, "
          f"{states}/{len(rows)} identical referee state, "
          f"{len(telemetry_errors)} telemetry errors -> {report['verdict']}")
    print(f"  branches: {census['branches']}  max passes {census['max_passes']}  "
          f"stale protections {census['stale_protections']}  "
          f"W-collisions {census['w_collision_events']} on {census['w_collision_turns']} turns")
    print(f"  longest payload {census['payload_max_chars']} chars")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
