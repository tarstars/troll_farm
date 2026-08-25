#!/usr/bin/env python3
"""Cure C — GATE G1. Fail-first fixtures, the cure property, and full-34 no-regression.

Task `20260817-cure-c-implementation` §3.1. Every claim here is measured against the frozen
prediction registry (`prediction-registry-2026-08-17.json`, `593c660c`), which was written before
the candidate existed.

G1 has three parts and all three must pass:

1. **FAIL-FIRST.** The four cure fixtures are observed FAILING on the *unmodified* resident —
   311 `NO_GOAL_ASSIGNED` turns. A test that has never been seen red proves nothing; every guard
   in this track that was never observed failing turned out to be inert.
2. **CURED.** Under the candidate those same four report **zero** `NO_GOAL_ASSIGNED` turns, and
   the predicted-uncured four behave exactly as the registry predicted — including *not* being
   cured. A cure that over-delivers against its own pre-registration is as much a finding as one
   that under-delivers.
3. **NO REGRESSION.** All 34 situations under both builds: **zero de-novo D-1 and zero de-novo
   P4** — no episode or violation that the resident did not already have.

The cure property is measured with the ACCEPTED pool-#5 machinery: the candidate is instrumented
with the same `make_instrumented2` taps, so `cause_table.classify` reads it exactly as it read the
resident. Nothing about the attribution logic is re-implemented here; if it were, the two numbers
would not be comparable.
"""
from __future__ import annotations

import collections
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "claude_1/hstarve1"))
sys.path.insert(0, str(REPO / "claude_1/t1"))
sys.path.insert(0, str(REPO / "claude_1/banana-restoration-r2"))
import cause_table as CT        # noqa: E402
import coverage as C            # noqa: E402
import fixture_harness as H     # noqa: E402
import fuzz_panel as fp         # noqa: E402
import make_instrumented2 as MI  # noqa: E402
import trace_detectors as td    # noqa: E402

REGISTRY = json.loads((HERE / "prediction-registry-2026-08-17.json").read_text())
CANDIDATE = HERE / "candidate-cure-c-quiet.rs"
INSTR_CANDIDATE = HERE / "candidate-cure-c-instrumented.rs"
RESIDENT_INSTR = REPO / "claude_1/hstarve1/instrumented-hstarve2.rs"


class G1Error(Exception):
    """Fail-closed. A red G1 stops the task; it does not get argued around."""


def build_instrumented_candidate():
    """Apply the ACCEPTED instrument patches to the cured source.

    Reuses `make_instrumented2.PATCHES` rather than restating them. A second copy of the tap
    definitions would let the candidate and the resident be measured by subtly different
    instruments, which is precisely the confound that makes two numbers incomparable.
    """
    text = CANDIDATE.read_text()
    for name, old, new in MI.PATCHES:
        if text.count(old) != 1:
            raise G1Error(f"instrument anchor {name!r} matched {text.count(old)} times in the "
                          f"candidate — the cure moved a site the instrument depends on")
        text = text.replace(old, new)
    INSTR_CANDIDATE.write_text(text)
    order = [text.index('eprintln!("HS2PRE turn='),
             text.index("self.force_unique_door_clear(view,&mut by_id);"),
             text.index('eprintln!("HS2 turn='),
             text.index("MoisanBot::select(by_id,"),
             text.index('eprintln!("HS2CHOSENPRE turn='),
             text.index("MoisanBot::resolve_move_conflicts(view,&mut selected);"),
             text.index('eprintln!("HS2CHOSEN turn=')]
    if order != sorted(order):
        raise G1Error(f"tap order wrong in the instrumented candidate: {order}")
    print(f"  built {INSTR_CANDIDATE.name}; tap order verified")


def no_goal_turns(binary, sits, cfg, plain_bin):
    """-> {situation: [turns]} of NO_GOAL_ASSIGNED, via the accepted classifier."""
    out = {}
    for sit in sits:
        err = C.check_parity(sit, cfg, plain_bin, binary)
        C.check_final_stage(sit, err)
        C.check_coverage(sit, err)
        spec = H.spec_for(sit, cfg)
        transcript, commands, _ = C.run_diagnostic(binary, fp.make_referee(spec),
                                                   int(cfg["turns"]))
        tr = td.build_trace(transcript, commands)
        rows = CT.classify(sit, *CT.parse(err), tr)
        turns = []
        for r in rows:
            turns += [p["turn"] for p in r.get("per_turn", []) if p["token"] == "NO_GOAL_ASSIGNED"]
        out[sit["id"]] = sorted(turns)
    return out


def detectors(binary, cfg):
    """-> {situation: (d1_episode_count, p4_violation_count)} over the WHOLE game.

    `grade()` reports `*_in_window` counts, which is the right measure for T-1's question but the
    wrong one here: a cure could introduce an episode OUTSIDE a fixture's window and the window
    counts would never see it. `run_situation` returns the full lists, so the comparison is
    whole-game and strictly stronger.
    """
    out = {}
    for sit in H.load_situations(None):
        _, eps, p4, _ = H.run_situation(sit, binary, cfg)
        out[sit["id"]] = (len(eps), len(p4))
    return out


def sit_window(sid):
    w = H.load_situations([sid])[0]["window"]
    return [w["turn_start"], w["turn_end"]]


def first_divergent_turn(sid, cfg, res_bin, cand_bin):
    """First turn whose emitted command line differs. Names the CAUSE of a divergence.

    A prediction miss with no stated mechanism is just a surprise; with the first divergent turn
    attached it is a finding. This is what separates "the cure over-delivered" from "the cure
    changed the trajectory at turn 1 and the later stall never occurred".
    """
    import regression_tests as rt
    sit = H.load_situations([sid])[0]
    spec = H.spec_for(sit, cfg)
    _, a = rt.run_binary_custom(Path(res_bin), fp.make_referee(spec), int(cfg["turns"]))
    _, b = rt.run_binary_custom(Path(cand_bin), fp.make_referee(spec), int(cfg["turns"]))
    la, lb = a.strip().split("\n"), b.strip().split("\n")
    return next((i + 1 for i, (x, y) in enumerate(zip(la, lb)) if x != y), None)


def main():
    cfg = json.loads(H.CONFIG.read_text())
    eight = (list(REGISTRY["cured_completely"]) + list(REGISTRY["predicted_uncured"]))
    sits8 = H.load_situations(sorted(eight))
    four = sorted(REGISTRY["cured_completely"])

    print("building the instrumented candidate from the cured source")
    build_instrumented_candidate()

    with tempfile.TemporaryDirectory(prefix="curec-g1-") as wd:
        wd = Path(wd)
        for name in ("res", "cand", "plain_res", "plain_cand"):
            (wd / name).mkdir()
        instr_res = H.compile_candidate(RESIDENT_INSTR, wd / "res")
        instr_cand = H.compile_candidate(INSTR_CANDIDATE, wd / "cand")
        plain_res = H.compile_candidate(H.RESIDENT, wd / "plain_res")
        plain_cand = H.compile_candidate(CANDIDATE, wd / "plain_cand")

        print("\n=== G1.1 FAIL-FIRST — the four fixtures must be RED on the resident ===")
        before = no_goal_turns(instr_res, sits8, cfg, plain_res)
        red = sum(len(before[s]) for s in four)
        for s in four:
            exp = REGISTRY["cured_completely"][s]["no_goal_turns"]
            if len(before[s]) != exp:
                raise G1Error(f"{s}: resident shows {len(before[s])} no-goal turns, registry "
                              f"pre-registered {exp}. The baseline moved under the registry.")
            print(f"  RED  {s}: {len(before[s])} NO_GOAL_ASSIGNED turns on the resident")
        if red != REGISTRY["cured_turn_total"]:
            raise G1Error(f"fail-first total {red} != pre-registered {REGISTRY['cured_turn_total']}")
        print(f"  fail-first CONFIRMED: {red}/{red} turns red before the cure exists")

        print("\n=== G1.2 CURED — the same four must be GREEN under the candidate ===")
        after = no_goal_turns(instr_cand, sits8, cfg, plain_cand)
        for s in four:
            if after[s]:
                raise G1Error(f"{s}: still {len(after[s])} NO_GOAL_ASSIGNED turns under the "
                              f"candidate, first at turn {after[s][0]}")
            print(f"  GREEN {s}: 0 NO_GOAL_ASSIGNED turns ({len(before[s])} -> 0)")

        print("\n=== G1.3 PREDICTED-UNCURED — must behave exactly as pre-registered ===")
        # A divergence here is RECORDED WITH ITS CAUSE and blocks the gate. It is NOT smoothed by
        # amending the frozen registry: a pre-registration edited after seeing the result is
        # worthless, and relaxing an acceptance gate to fit an outcome is how this programme got a
        # fabricated acceptance into its quarantine list.
        divergences = []
        for s in sorted(REGISTRY["predicted_uncured"]):
            pred = REGISTRY["predicted_uncured"][s]
            expect = pred["no_goal_turns"] - pred["c_supplies"]
            got = len(after[s])
            ok = got == expect
            first = first_divergent_turn(s, cfg, plain_res, plain_cand)
            print(f"  {s}: {len(before[s])} -> {got} (predicted {expect}) — "
                  f"{'as predicted' if ok else 'DIVERGES'}; first differing command turn: {first}")
            if not ok:
                divergences.append({"situation": s, "predicted_remaining": expect,
                                    "observed_remaining": got,
                                    "first_divergent_command_turn": first,
                                    "window": sit_window(s)})

        print("\n=== G1.4 NO REGRESSION — all 34, zero de-novo D-1 and zero de-novo P4 ===")
        res_det = detectors(plain_res, cfg)
        cand_det = detectors(plain_cand, cfg)
        denovo_d1, denovo_p4 = [], []
        for sid, (d1c, p4c) in sorted(cand_det.items()):
            d1b, p4b = res_det[sid]
            if d1c > d1b:
                denovo_d1.append((sid, d1b, d1c))
            if p4c > p4b:
                denovo_p4.append((sid, p4b, p4c))
        print(f"  situations compared: {len(cand_det)}")
        print(f"  de-novo D-1: {len(denovo_d1)}  {denovo_d1[:5]}")
        print(f"  de-novo P4:  {len(denovo_p4)}  {denovo_p4[:5]}")
        if denovo_d1 or denovo_p4:
            raise G1Error("de-novo detector firings — the cure introduced oscillation or stalls")

    out = HERE / "g1-results-2026-08-17.json"
    out.write_text(json.dumps({
        "gate": "G1",
        "task": "20260817-cure-c-implementation",
        "registry": "claude_1/cure-c/prediction-registry-2026-08-17.json",
        "fail_first_turns_red_on_resident": red,
        "no_goal_before": {k: len(v) for k, v in sorted(before.items())},
        "no_goal_after": {k: len(v) for k, v in sorted(after.items())},
        "situations_compared_for_regression": len(cand_det),
        "detector_counts_whole_game": {k: {"resident": list(res_det[k]), "candidate": list(v)}
                                       for k, v in sorted(cand_det.items())},
        "denovo_d1": denovo_d1,
        "denovo_p4": denovo_p4,
        "prediction_divergences": divergences,
        "verdict": "PASS" if not divergences else "BLOCKED_ON_PREDICTION_DIVERGENCE",
    }, indent=1, sort_keys=True) + "\n")
    if divergences:
        print(f"\nG1: BLOCKED — {len(divergences)} situation(s) diverged from the FROZEN "
              f"pre-registration. Recorded with cause; the registry is NOT amended.")
        for d in divergences:
            print(f"  {d['situation']}: predicted {d['predicted_remaining']} remaining, observed "
                  f"{d['observed_remaining']}; commands first differ at turn "
                  f"{d['first_divergent_command_turn']}, window {d['window']}")
        print(f"wrote {out.relative_to(REPO)}")
        return 1
    print(f"\nG1: PASS — wrote {out.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except G1Error as e:
        print(f"\nG1: FAIL — {e}")
        sys.exit(1)
