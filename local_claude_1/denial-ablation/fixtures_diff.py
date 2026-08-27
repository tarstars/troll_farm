#!/usr/bin/env python3
"""The denial-ablation arm on the 34 frozen situations: does it play, does it differ, is it
the file the ladder receives.

Adapted from `claude_1/instrument6/fixtures.py` (bot A's parity run). Bot A's question was
"identical to the champion?"; this arm is MEANT to differ, so the questions here are:

  plays          every situation runs to its end (no crash, no empty command);
  differs        the arm's stream with `MSG` stripped differs from the champion's on at least
                 one situation -- an ablation that changes nothing on the bed would be a build
                 mistake, not a result (reported, and how many);
  compacted      the compacted file plays exactly as the arm does, `MSG` included (the ladder
                 receives the compacted file, so that is the file that has to behave);
  deterministic  the arm run twice on the same situation produces the same bytes;
  telemetry      the v6 line decodes on every turn (rule_off=True: the keep rule is off).

The 34 fixtures were retired as gates on 2026-08-26 (row 0-1); this is a differential bed and
its numbers are not a behaviour result. The ladder is the judge.

    python3 local_claude_1/denial-ablation/fixtures_diff.py
"""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "claude_1" / "cure3"))

import containment as ct        # noqa: E402  (its own sys.path inserts bring the harnesses in)
import fixture_harness as fh    # noqa: E402
import semantic_harness as sh   # noqa: E402
import narrate6 as n6           # noqa: E402

ARM = HERE / "champion-denial-off-v6-instrument.rs"
BASE = REPO / "readable" / "door1-champion.rs"
BASE_SHA = "ad1ae4eff70a5569e03e2149882bb22510746f4f8592907a5dfb936943ef0bfb"
SUBMISSION = REPO / "cgauto" / "submissions" / "candidate-champion-denial-off-v6-instrument.rs"


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def main() -> int:
    base_text, arm_text = BASE.read_text(), ARM.read_text()
    got = sha(base_text)
    if got != BASE_SHA:
        print(f"REFUSED: base is {got}, expected {BASE_SHA}", file=sys.stderr)
        return 2
    recorded = (HERE / "champion-denial-off-v6-instrument.rs.sha256").read_text().split()[0]
    if sha(arm_text) != recorded:
        print(f"REFUSED: arm is {sha(arm_text)}, its sidecar says {recorded}", file=sys.stderr)
        return 2
    sub_text = SUBMISSION.read_text()
    sub_recorded = (SUBMISSION.parent / (SUBMISSION.name + ".sha256")).read_text().split()[0]
    if sha(sub_text) != sub_recorded:
        print(f"REFUSED: submission is {sha(sub_text)}, its sidecar says {sub_recorded}",
              file=sys.stderr)
        return 2

    cfg = json.loads(fh.CONFIG.read_text())
    sits = fh.load_situations(None)
    rows, telemetry_errors = [], []
    census = n6.new_census()
    with tempfile.TemporaryDirectory(prefix="denial-off-") as wd:
        wd = Path(wd)
        base_bin, arm_bin, min_bin = wd / "base.bin", wd / "arm.bin", wd / "min.bin"
        sh.compile_text(base_text, base_bin, crate="champion_base")
        sh.compile_text(arm_text, arm_bin, crate="denial_off_arm")
        sh.compile_text(sub_text, min_bin, crate="denial_off_min")
        for sit in sits:
            sid = sit["id"]
            base_lines, base_state, _ = ct.run_arm(sit, base_bin, cfg)
            arm_lines, arm_state, arm_trace = ct.run_arm(sit, arm_bin, cfg)
            again_lines, again_state, _ = ct.run_arm(sit, arm_bin, cfg)
            min_lines, min_state, _ = ct.run_arm(sit, min_bin, cfg)
            stripped = [n6.strip_msg(l) for l in arm_lines]
            champion = [n6.strip_msg(l) for l in base_lines]
            differs = stripped != champion
            deterministic = arm_lines == again_lines and arm_state == again_state
            compacted_same = arm_lines == min_lines and arm_state == min_state
            first = None
            if differs:
                for i, (a, b) in enumerate(zip(champion, stripped), 1):
                    if a != b:
                        first = {"turn": i, "champion": a, "arm_stripped": b}
                        break
                if first is None:
                    first = {"turn": None, "champion_turns": len(champion),
                             "arm_turns": len(stripped)}
            errs = n6.check_telemetry(sid, arm_trace, arm_lines, census, rule_off=True)
            telemetry_errors.extend(f"{sid}: {e}" for e in errs)
            own = arm_state.get("scores", [None, None])[0] if isinstance(arm_state, dict) else None
            base_own = base_state.get("scores", [None, None])[0] if isinstance(base_state, dict) else None
            rows.append({
                "id": sid, "turns": len(arm_lines),
                "differs_from_champion_without_msg": differs,
                "referee_state_identical": base_state == arm_state,
                "deterministic_on_rerun": deterministic,
                "compacted_binary_identical": compacted_same,
                "telemetry_errors": len(errs),
                "first_divergence": first,
                "own_score_arm": own, "own_score_champion": base_own,
            })
            mark = ("DIFFERS" if differs else "SAME") if deterministic and compacted_same and not errs else "FAILED"
            print(f"  {mark:<7} {sid:<10} turns {len(arm_lines):>3}  first divergence turn "
                  f"{(first or {}).get('turn')}  telemetry errors {len(errs)}")

    n = len(rows)
    differs = sum(1 for r in rows if r["differs_from_champion_without_msg"])
    det = sum(1 for r in rows if r["deterministic_on_rerun"])
    minsame = sum(1 for r in rows if r["compacted_binary_identical"])
    plays = sum(1 for r in rows if r["turns"] > 0)
    ok = det == minsame == plays == n and not telemetry_errors
    report = {
        "bed": "34 frozen situations, differential only (retired as gates, row 0-1)",
        "experiment": "denial ablation: the diagnostics champion minus the plum/lemon denial bonus",
        "base": str(BASE.relative_to(REPO)), "base_sha256": BASE_SHA,
        "arm": str(ARM.relative_to(REPO)), "arm_sha256": sha(arm_text),
        "submission": str(SUBMISSION.relative_to(REPO)), "submission_sha256": sha(sub_text),
        "fixtures": n,
        "plays_to_the_end": plays,
        "differs_from_champion_without_msg": differs,
        "deterministic_on_rerun": det,
        "compacted_binary_identical": minsame,
        "telemetry_error_count": len(telemetry_errors),
        "telemetry_errors": telemetry_errors[:100],
        "census": census,
        "status": "PASS" if ok else "FAIL",
        "rows": rows,
    }
    out = HERE / "results" / "fixtures.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"\n  {report['status']}  plays {plays}/{n}, differs from the champion on {differs}/{n}, "
          f"deterministic {det}/{n}, compacted==arm {minsame}/{n}, telemetry errors "
          f"{len(telemetry_errors)}  -> {out}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
