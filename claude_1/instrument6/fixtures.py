#!/usr/bin/env python3
"""0-3a on the 34 frozen situations: parity against the champion, and determinism.

Task `20260826-champion-instrument-v6`. Two questions, one compile of each binary:

  parity       the arm's stream with `MSG` stripped == the champion's stream, byte for byte,
               and the referee's state after the last turn is field-for-field the same;
  determinism  the arm run TWICE on the same situation produces the same bytes, `MSG` payloads
               included -- an instrument whose telemetry wobbles between runs cannot be read.

The 34 fixtures were RETIRED as gates on 2026-08-26 (row 0-1, `local_claude_1/fixtures/
fixture-drift-2026-08-26.md`): they are the very-old bot's episodes, so "the champion fails 23
of them" is a statement about a different bot and not about this arm. They are still a fine
**differential** bed -- the question here is only whether two binaries agree with each other on
the same 34 starts -- which is why the run is kept and reported, and why its number is not
offered as a behaviour result.

    python3 claude_1/instrument6/fixtures.py
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

ARM = HERE / "champion-v6-instrument.rs"
BASE = REPO / "readable" / "door1-champion.rs"
BASE_SHA = "ad1ae4eff70a5569e03e2149882bb22510746f4f8592907a5dfb936943ef0bfb"
SUBMISSION = REPO / "cgauto" / "submissions" / "candidate-champion-v6-instrument.rs"
ARM_SHA = "0f75e7d61c71d4881502aac2204faf6fb5035331857a9f400ea2647bccd94141"


def main() -> int:
    base_text, arm_text = BASE.read_text(), ARM.read_text()
    for text, want, what in ((base_text, BASE_SHA, "base"), (arm_text, ARM_SHA, "arm")):
        got = hashlib.sha256(text.encode()).hexdigest()
        if got != want:
            print(f"REFUSED: {what} is {got}, expected {want}", file=sys.stderr)
            return 2

    cfg = json.loads(fh.CONFIG.read_text())
    sits = fh.load_situations(None)
    rows, telemetry_errors = [], []
    census = n6.new_census()
    with tempfile.TemporaryDirectory(prefix="instrument6-") as wd:
        wd = Path(wd)
        base_bin, arm_bin = wd / "base.bin", wd / "arm.bin"
        min_bin = wd / "min.bin"
        sh.compile_text(base_text, base_bin, crate="champion_base")
        sh.compile_text(arm_text, arm_bin, crate="champion_v6_arm")
        # The ladder receives the COMPACTED file, so the compacted file is what has to behave.
        # A round-trip report proves the token streams match; this proves the two binaries play
        # the same game, `MSG` payloads included.
        sh.compile_text(SUBMISSION.read_text(), min_bin, crate="champion_v6_min")
        for sit in sits:
            sid = sit["id"]
            base_lines, base_state, _ = ct.run_arm(sit, base_bin, cfg)
            arm_lines, arm_state, arm_trace = ct.run_arm(sit, arm_bin, cfg)
            again_lines, again_state, _ = ct.run_arm(sit, arm_bin, cfg)
            min_lines, min_state, _ = ct.run_arm(sit, min_bin, cfg)
            stripped = [n6.strip_msg(l) for l in arm_lines]
            champion = [n6.strip_msg(l) for l in base_lines]
            identical = stripped == champion
            deterministic = arm_lines == again_lines and arm_state == again_state
            compacted_same = arm_lines == min_lines and arm_state == min_state
            first = None
            if not identical:
                for i, (a, b) in enumerate(zip(champion, stripped), 1):
                    if a != b:
                        first = {"turn": i, "champion": a, "arm_stripped": b}
                        break
                if first is None:
                    first = {"turn": None, "champion_turns": len(champion),
                             "arm_turns": len(stripped)}
            errs = n6.check_telemetry(sid, arm_trace, arm_lines, census, rule_off=True)
            telemetry_errors.extend(f"{sid}: {e}" for e in errs)
            rows.append({
                "id": sid, "turns": len(arm_lines),
                "byte_identical_without_msg": identical,
                "referee_state_identical": base_state == arm_state,
                "deterministic_on_rerun": deterministic,
                "compacted_binary_identical": compacted_same,
                "telemetry_errors": len(errs),
                "first_divergence": first,
            })
            mark = ("PARITY" if identical and base_state == arm_state
                    and deterministic and compacted_same and not errs else "FAILED")
            print(f"  {mark:<7} {sid:<10} turns {len(arm_lines):>3}  "
                  f"deterministic {deterministic}  telemetry errors {len(errs)}")

    parity = sum(1 for r in rows if r["byte_identical_without_msg"])
    states = sum(1 for r in rows if r["referee_state_identical"])
    det = sum(1 for r in rows if r["deterministic_on_rerun"])
    minsame = sum(1 for r in rows if r["compacted_binary_identical"])
    ok = parity == states == det == minsame == len(rows) and not telemetry_errors
    report = {
        "gate": "0-3a fixtures: champion parity + determinism (34 frozen situations)",
        "task": "20260826-champion-instrument-v6",
        "fixtures_retired_as_gates": "row 0-1, local_claude_1/fixtures/fixture-drift-2026-08-26.md"
                                     " -- read here as a differential bed only",
        "base": str(BASE.relative_to(REPO)), "base_sha256": BASE_SHA,
        "arm": str(ARM.relative_to(REPO)), "arm_sha256": ARM_SHA,
        "fixtures": len(rows),
        "byte_identical_without_msg": parity,
        "referee_state_identical": states,
        "deterministic_on_rerun": det,
        "compacted_binary_identical": minsame,
        "submission": str(SUBMISSION.relative_to(REPO)),
        "telemetry_error_count": len(telemetry_errors),
        "telemetry_errors": telemetry_errors[:100],
        "census": census,
        "status": "PASS" if ok else "FAIL",
        "rows": rows,
    }
    out = HERE / "results" / "fixtures.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"\n  {report['status']}  {parity}/{len(rows)} byte-identical without MSG, "
          f"{states}/{len(rows)} same referee state, {det}/{len(rows)} deterministic, "
          f"{minsame}/{len(rows)} compacted==readable  -> {out}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
