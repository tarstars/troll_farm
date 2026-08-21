#!/usr/bin/env python3
r"""G-1/G-2 controls for the episode-identity gate lifted into the shared harness.

Card `20260821-episode-identity-regrade`, deliverable 1. The gate itself lives in
`claude_1/t1/fixture_harness.py` (`check_window_commands`, `check_entry_state`,
`episode_identity`); this file is the evidence that it is the ACCEPTED gate, that the grader
consults it before it grades, and that it is capable of saying no.

## G-1 — the lift is the accepted bytes, not a paraphrase

The two functions were lifted out of `claude_1/regrade1/real_end_regrade.py`, whose gate codex_1
ACCEPTED at `20260821T100154Z`. A copy is only as good as the proof that it did not drift, so:

1. `inspect.getsource` of each function is compared **character for character** between the two
   modules. Not a digest of the file — the exact function bodies the reviewer read.
2. The source file's sha256 is pinned, so a later edit to the accepted script is caught here
   rather than silently making this comparison compare two changed things to each other.
3. Call order is shown by AST: inside `grade`, the first reference to the identity verdict comes
   before the first reference to any of the recorded-window inputs it gates.

## G-2 — the gate is capable of rejecting

A gate that has only ever agreed is not evidence of agreement. The controls:

- the champion is REJECTED on OSC-032 — the case that motivated the card, and the one where the
  window-command half alone would pass because every recorded line is `WAIT`;
- a constructed same-count/wrong-cell entry state is REJECTED on a run that otherwise passes;
- a fixture whose `world_state_at_entry` cannot be decoded FAILS CLOSED, not open;
- a `grade()` call with no identity verdict is REFUSED.

The 34/34 acceptance of the subject bot is the other half and lives in `regrade34.py`, because it
needs the full sweep.

Run:  python3 claude_1/regrade2/identity_gate_controls.py
"""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import inspect
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
for p in ("claude_1/t1", "claude_1/hstarve1", "claude_1/banana-restoration-r2",
          "claude_1/pipeline", "claude_1/cause1"):
    sys.path.insert(0, str(REPO / p))
sys.path.insert(0, str(REPO))
import fixture_harness as H     # noqa: E402

ACCEPTED = REPO / "claude_1/regrade1/real_end_regrade.py"
ACCEPTED_SHA256 = "370122fada39ac852290ead952afc61e0c8ff2c0e3898bdbe72ce146c1a56fc2"
CHAMPION = REPO / "claude_1/chop4c/candidate-door1.rs"
CHAMPION_SHA256 = "547fa706cc1c684a1f8c2a08174792d95e553b2382facfe15884d2ef544070b0"
LIFTED = ("check_window_commands", "check_entry_state")
OUT = HERE / "identity-gate-controls-2026-08-21.json"


def load_accepted():
    spec = importlib.util.spec_from_file_location("real_end_regrade_accepted", ACCEPTED)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def call_order_in_grade():
    """Inside `grade`, is the identity verdict consulted before the window inputs it gates?"""
    tree = ast.parse(Path(H.__file__).read_text())
    fn = next(n for n in ast.walk(tree)
              if isinstance(n, ast.FunctionDef) and n.name == "grade")
    first = {}
    for node in ast.walk(fn):
        if isinstance(node, ast.Name):
            first.setdefault(node.id, node.lineno)
            first[node.id] = min(first[node.id], node.lineno)
    gated = ("d1_episodes", "p4_violations", "had_progress", "left_the_cycle")
    present = {name: first[name] for name in gated if name in first}
    return {"identity_first_referenced_line": first.get("identity"),
            "gated_inputs_first_referenced": present,
            "identity_read_first": (first.get("identity") is not None and present
                                    and first["identity"] < min(present.values()))}


def main() -> int:
    cases = []

    def case(label, ok, detail):
        cases.append({"control": label, "pass": bool(ok), "detail": str(detail)[:300]})
        print(f"  {'OK  ' if ok else 'FAIL'}  {label}\n         {str(detail)[:150]}")

    accepted_sha = hashlib.sha256(ACCEPTED.read_bytes()).hexdigest()
    module = load_accepted()
    for name in LIFTED:
        theirs = inspect.getsource(getattr(module, name))
        mine = inspect.getsource(getattr(H, name))
        case(f"{name} in the harness is byte-identical to the accepted source",
             theirs == mine,
             f"{len(mine)} chars; accepted file sha256 {accepted_sha[:16]}…")

    case("the accepted source file is unchanged since the lift",
         accepted_sha == ACCEPTED_SHA256,
         f"sha256 {accepted_sha}, pin {ACCEPTED_SHA256}")

    order = call_order_in_grade()
    case("grade() reads the identity verdict BEFORE any recorded-window input",
         order["identity_read_first"], order)

    cfg = json.loads(H.CONFIG.read_text())
    sit = H.load_situations(["OSC-032"])[0]
    if hashlib.sha256(CHAMPION.read_bytes()).hexdigest() != CHAMPION_SHA256:
        raise SystemExit("the champion file is not the champion of record; refusing to run.")
    with tempfile.TemporaryDirectory(prefix="ident-controls-") as wd:
        binary = H.compile_candidate(CHAMPION, Path(wd))
        tr, eps, p4, _, lines = H.run_situation_ex(sit, binary, cfg)
        ident = H.episode_identity(sit["id"], sit, tr, lines)
        case("the champion is REJECTED on OSC-032 (all-WAIT window, different board)",
             not ident["reproduces_the_recorded_episode"], ident["reasons"])
        case("and the window-command half ALONE would have accepted it "
             "(which is why both halves exist)",
             ident["window_commands"] is not None
             and ident["window_commands"]["mismatches"] == 0,
             ident["window_commands"])

        verdict = H.grade(sit, tr, eps, p4, ident)
        case("the grader returns NOT_REPRODUCIBLE_ON_BASE, never FIXED or NOT_FIXED",
             verdict["verdict"] == "NOT_REPRODUCIBLE_ON_BASE", verdict["why"])

        # a run that DOES pass, so the constructed controls below are perturbations of a pass
        subject = H.load_situations(["OSC-006"])[0]
        subject_dir = Path(wd) / "subject"
        subject_dir.mkdir()
        sbin = H.compile_candidate(H.RESIDENT, subject_dir)
        str_, _, _, _, slines = H.run_situation_ex(subject, sbin, cfg)
        good = H.episode_identity(subject["id"], subject, str_, slines)
        case("the subject bot is ACCEPTED on its own recorded episode (the gate can say yes)",
             good["reproduces_the_recorded_episode"], good["reasons"])

        ws = subject["world_state_at_entry"]
        moved = [list(u) for u in ws["units"]]
        moved[0][2] += 5
        bent = {**subject, "world_state_at_entry": {**ws, "units": moved}}
        bad = H.episode_identity(subject["id"], bent, str_, slines)
        case("a same-count/wrong-cell entry board is REJECTED",
             not bad["reproduces_the_recorded_episode"], bad["reasons"])

        broken = {**subject, "world_state_at_entry": {**ws, "units": "not a board"}}
        closed = H.episode_identity(subject["id"], broken, str_, slines)
        case("an undecodable entry state FAILS CLOSED",
             not closed["reproduces_the_recorded_episode"], closed["reasons"])

        try:
            H.grade(subject, str_, [], [])
            case("grade() without an identity verdict is REFUSED", False, "no error raised")
        except H.HarnessError as exc:
            case("grade() without an identity verdict is REFUSED", True, exc)

    ok = all(c["pass"] for c in cases)
    OUT.write_text(json.dumps({
        "task": "20260821-episode-identity-regrade", "gate": "G-1/G-2",
        "accepted_source": str(ACCEPTED.relative_to(REPO)), "accepted_sha256": accepted_sha,
        "lifted_functions": list(LIFTED), "call_order": order,
        "controls": cases, "all_ok": ok}, indent=2) + "\n")
    print(f"\n  {sum(c['pass'] for c in cases)}/{len(cases)} controls pass -> "
          f"{OUT.relative_to(REPO)}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
