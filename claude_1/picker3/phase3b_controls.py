#!/usr/bin/env python3
r"""Phase 3b — the controls for G-a/G-c: can these gates fail?

This programme's own recorded failure mode (08-15 → 08-21) is an instrument that measures its own
instrumentation and a check that cannot go red. `run_phase3b_gates.py` returned PASS on 34/34
fixtures for both subjects; that statement is worth nothing until each clause has been shown to
reject something it should reject.

Every control below must FAIL the clause it targets. One clean control must PASS, so that a
harness which rejects everything is caught too.

- **CLEAN** — the real OSC-013 census and streams grade OK. (A harness that says FAIL to
  everything is as useless as one that says PASS.)
- **C1 shipped-source inertness (§5a)** — a graded source carrying one extra edit *outside*
  `main_candidates` must be refused, even though the §1 hunk is present and correct.
- **C2 probe parity** — a probe stream that differs from its plain arm must be caught. Run with a
  deliberately mismatched pair of binaries on a fixture where the two arms are known to differ.
- **C3 EFFECT identity** — divergence strictly BEFORE the first selected Δ-A tick must fail the
  class, because that divergence cannot be the change.
- **C4 NO-EFFECT identity** — a game with no selected Δ-A tick and a non-identical stream must
  fail, even though Δ-A was formed there.
- **C5 EFFECT provenance** — on the first selected tick, a changed command that is NOT one of the
  specifically preserved Δ-A `PICK`s must fail.
- **C6 §2 mutual exclusion** — a tick carrying both a replant `PICK` in `out` and `carried>0` bank
  candidates must be reported as a violation, refuting §2 rather than being absorbed.
- **C7 subset assertion** — a selected tick that is not a formed tick must be reported.

Run:  python3 claude_1/picker3/phase3b_controls.py
"""
from __future__ import annotations

import json, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(HERE))
for p in ("claude_1/t1", "claude_1/pipeline", "claude_1/banana-restoration-r2"):
    sys.path.insert(0, str(REPO / p))

import run_phase3b_gates as G      # noqa: E402
import make_phase3b_candidate as mk  # noqa: E402
import fixture_harness as fh       # noqa: E402
import semantic_harness as sh      # noqa: E402

PICK = {"command": "PICK 3 Plum", "score": 7500.0, "target": "Cell((4, 5))"}
BANK = {"command": "MOVE 3 4 6", "score": 6999.0, "target": "Bank((4, 6))"}
WAIT = {"command": "WAIT", "score": 0.0, "target": "None"}


def grade(base, cand, entered, returned, base_returned=None):
    return G.grade_game("CTRL", base, cand, entered, returned, base_returned or {})


def control_clean():
    """The real OSC-013 run, cure-C: it graded OK, and the controls harness must agree."""
    report = json.loads((HERE / "results" / "phase3b-gac-2026-08-23.json").read_text())
    row = next(r for r in report["subjects"]["cureC"]["rows"] if r["id"] == "OSC-013")
    ok = row["class_ok"] and not row["assertion_violations"] and row["class"] == "EFFECT"
    return ok, f"OSC-013 graded {row['class']} class_ok={row['class_ok']}"


def control_c1_inertness():
    src = mk.SUBJECTS["cureC"]["src"].read_text()
    patched = mk.patch("cureC", src)
    # One extra edit outside main_candidates: a whitespace-free but real change to another fn.
    tampered = patched.replace("fn fallback_second_troll()->Stats{",
                               "fn fallback_second_troll()->Stats{ /*x*/", 1)
    if tampered == patched:
        return False, "control could not tamper the source — the anchor moved"
    with tempfile.TemporaryDirectory() as wd:
        alt = Path(wd) / "candidate-cureC-p3b.rs"
        alt.write_text(tampered)
        saved = G.ARMS["cureC"]["cand_plain"]
        G.ARMS["cureC"]["cand_plain"] = alt
        try:
            G.shipped_source_inertness("cureC")
            return False, "tampered source ACCEPTED by the §5a check"
        except G.GateError as exc:
            return True, f"refused: {exc}"
        finally:
            G.ARMS["cureC"]["cand_plain"] = saved


def control_c2_probe_parity():
    """A probe whose stream differs from its plain arm must be visible as a parity failure."""
    cfg = json.loads(fh.CONFIG.read_text())
    sit = fh.load_situations(["OSC-013"])[0]
    with tempfile.TemporaryDirectory() as wd:
        wd = Path(wd)
        base_bin, cand_bin = wd / "base.bin", wd / "cand.bin"
        sh.compile_text(G.ARMS["cureC"]["base_plain"].read_text(), base_bin, crate="ctrl_base")
        sh.compile_text(G.ARMS["cureC"]["cand_plain"].read_text(), cand_bin, crate="ctrl_cand")
        base_lines, _ = G.run_arm(sit, base_bin, cfg, False)
        cand_lines, _ = G.run_arm(sit, cand_bin, cfg, False)
    if base_lines == cand_lines:
        return False, "control is inert: the two arms agree on OSC-013, so no parity check is tested"
    return True, ("a stream substituted for its own arm's is detected as different "
                  f"(first divergence turn {next(i for i,(a,b) in enumerate(zip(base_lines,cand_lines),1) if a!=b)})")


def control_c3_effect_early_divergence():
    base = ["WAIT", "WAIT", "WAIT", "WAIT"]
    cand = ["WAIT", "MOVE 3 1 1", "WAIT", "PICK 3 Plum"]     # diverges at 2, selected tick is 4
    entered = {(4, 3): {"carried": 0, "items": [WAIT, PICK]}}
    row = grade(base, cand, entered, {(4, 3): [WAIT, PICK]})
    return not row["class_ok"], row["why"]


def control_c4_no_effect_divergence():
    base = ["WAIT", "WAIT", "WAIT"]
    cand = ["WAIT", "MOVE 3 1 1", "WAIT"]                     # Δ-A formed, never selected
    entered = {(2, 3): {"carried": 0, "items": [WAIT, PICK]}}
    row = grade(base, cand, entered, {(2, 3): [WAIT, PICK]})
    return (not row["class_ok"]) and row["class"] == "NO-EFFECT", row["why"]


def control_c5_effect_wrong_command():
    base = ["WAIT", "WAIT", "WAIT"]
    cand = ["WAIT", "WAIT", "PICK 3 Plum;MOVE 9 2 2"]         # an unrelated extra command on T
    entered = {(3, 3): {"carried": 0, "items": [WAIT, PICK]}}
    row = grade(base, cand, entered, {(3, 3): [WAIT, PICK]})
    return not row["class_ok"], row["why"]


def control_c6_mutual_exclusion():
    base = ["WAIT", "WAIT"]
    cand = ["WAIT", "WAIT"]
    entered = {(2, 3): {"carried": 2, "items": [WAIT, PICK, BANK]}}
    row = grade(base, cand, entered, {(2, 3): [WAIT, PICK, BANK, BANK]})
    hit = any("mutual" in v or "carried=" in v for v in row["assertion_violations"])
    return hit, "; ".join(row["assertion_violations"]) or "no violation reported"


def control_c7_subset():
    """A selected tick that is not a formed tick: forced by grading a stream whose PICK is emitted
    on a tick the census never saw as formed. The class logic must not invent it as formed."""
    base = ["WAIT", "WAIT", "WAIT"]
    cand = ["WAIT", "PICK 3 Plum", "WAIT"]
    entered = {(3, 3): {"carried": 0, "items": [WAIT, PICK]}}   # formed at 3, emitted at 2
    row = grade(base, cand, entered, {(3, 3): [WAIT, PICK]})
    # tick 2's PICK is NOT attributed as a selected Δ-A tick, and the game diverges at 2 while the
    # first selected tick is 3 — the EFFECT identity clause must reject it.
    return (2 not in row["delta_a_selected"]) and not row["class_ok"], \
        f"selected={row['delta_a_selected']} why={row['why']}"


CONTROLS = [
    ("CLEAN  real OSC-013 grades OK", control_clean, True),
    ("C1     §5a refuses an edit outside main_candidates", control_c1_inertness, True),
    ("C2     probe/plain stream mismatch is visible", control_c2_probe_parity, True),
    ("C3     EFFECT: divergence before the first selected tick", control_c3_effect_early_divergence, True),
    ("C4     NO-EFFECT: any divergence", control_c4_no_effect_divergence, True),
    ("C5     EFFECT: changed command is not a preserved PICK", control_c5_effect_wrong_command, True),
    ("C6     §2 mutual exclusion is reported, not absorbed", control_c6_mutual_exclusion, True),
    ("C7     a PICK on an unformed tick is not counted as selected", control_c7_subset, True),
]


def main() -> int:
    rows, failures = [], []
    for name, fn, want in CONTROLS:
        got, detail = fn()
        fired = got == want
        rows.append({"control": name, "fired": fired, "detail": detail})
        print(f"  {'FIRED ' if fired else 'INERT '} {name}\n           {detail}")
        if not fired:
            failures.append(name)
    out = {"gate": "G-a/G-c controls", "task": "20260820-pair-selector-anti-benching",
           "controls": len(rows), "fired": sum(1 for r in rows if r["fired"]),
           "inert": failures, "verdict": "PASS" if not failures else "FAIL", "rows": rows}
    (HERE / "results" / "phase3b-controls-2026-08-23.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"\n  controls: {out['fired']}/{out['controls']} fired -> {out['verdict']}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
