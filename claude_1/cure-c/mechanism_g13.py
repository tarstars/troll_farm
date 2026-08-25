#!/usr/bin/env python3
"""G1.3 MECHANISM PROBE — why OSC-009 and OSC-031 over-delivered.

Owner ruling 1 (`local_claude_1 20260818T041052Z`) makes G1.3 **explain-then-pass**: the clause
passes iff codex_1 can VERIFY the mechanism of each surprise. "Better than predicted" is
explicitly not the precedent. So this script does not argue that the misses were benign; it
measures WHICH of two rival mechanisms produced each one, and it is built so that a wrong
mechanism FAILS here rather than reading as a confirmation.

The two rival mechanisms, stated before measuring:

  M-BRANCH  The registry's branch attribution was WRONG. The turns it called ENDGAME-branch were
            really MAIN-branch, so C's door does run on them and cures them directly. Signature:
            the resident's no-goal turns carry branch != ENDGAME in the instrument, and the
            candidate supplies a non-WAIT generator list on those same turn/unit pairs.

  M-TRAJ    The branch attribution was RIGHT, but the candidate diverges EARLIER in the game, so
            the state that produced those no-goal turns is never reached. Signature: first
            divergent turn < the first no-goal turn, and the resident's turns are genuinely
            ENDGAME-branch.

THE CONTROL THAT MAKES THIS EVIDENCE. Two of my three earlier mechanisms died because they
applied equally to cases that did NOT show the effect. So the same quantities are measured on
OSC-001 and OSC-005 — the two predicted-uncured fixtures that MATCHED prediction. A mechanism
that is also true of the matching fixtures explains nothing, and this script says so out loud.
"""
from __future__ import annotations
import collections, json, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "hstarve1"))
sys.path.insert(0, str(HERE.parent / "pipeline"))
sys.path.insert(0, str(HERE))

import cause_table as CT
import coverage as C
import fixture_harness as H
import fuzz_panel as fp
import trace_detectors as td
import g1 as G1

REGISTRY = json.loads((HERE / "prediction-registry-2026-08-17.json").read_text())


class ProbeError(RuntimeError):
    pass


def per_turn_rows(binary, sit, cfg, plain_bin):
    """Full per-turn records (branch, gen kinds, token) for one situation."""
    err = C.check_parity(sit, cfg, plain_bin, binary)
    C.check_final_stage(sit, err)
    C.check_coverage(sit, err)
    spec = H.spec_for(sit, cfg)
    transcript, commands, _ = C.run_diagnostic(binary, fp.make_referee(spec), int(cfg["turns"]))
    tr = td.build_trace(transcript, commands)
    rows = CT.classify(sit, *CT.parse(err), tr)
    out = []
    for r in rows:
        for p in r.get("per_turn", []):
            out.append(dict(p, unit=r["unit"]))
    return out


def analyse(sid, cfg, instr_res, instr_cand, plain_res, plain_cand):
    sit = H.load_situations([sid])[0]
    res = per_turn_rows(instr_res, sit, cfg, plain_res)
    cand = per_turn_rows(instr_cand, sit, cfg, plain_cand)

    res_ng = [r for r in res if r["token"] == "NO_GOAL_ASSIGNED"]
    cand_ng = [r for r in cand if r["token"] == "NO_GOAL_ASSIGNED"]
    if not res_ng:
        raise ProbeError(f"{sid}: no NO_GOAL_ASSIGNED turns on the RESIDENT — the probe is "
                         f"pointed at the wrong fixture or the classifier changed")

    first_div = G1.first_divergent_turn(sid, cfg, plain_res, plain_cand)
    first_ng = min(r["turn"] for r in res_ng)
    cand_by_key = {(r["turn"], r["unit"]): r for r in cand}

    branches = sorted({(r["branch"] or "?") for r in res_ng})
    endgame_only = branches == ["ENDGAME"]

    # Did the candidate's DOOR run on the very turn/unit pairs that were no-goal on the resident?
    cand_by_key = {(r["turn"], r["unit"]): r for r in cand}
    # NOTE ON WHAT "same state" CAN MEAN HERE. Matching on (turn, unit) alone does NOT prove the
    # world is the same: once the bots diverge, turn 80 in the candidate's game is a different
    # world from turn 80 in the resident's. So the pairs are split. Only the pre-divergence ones
    # are same-state in the strong sense (identical command streams up to that turn), and only
    # those can prove the DOOR ran rather than the trajectory moved.
    same_state_cured, postdiv_cured = [], []
    for r in res_ng:
        c = cand_by_key.get((r["turn"], r["unit"]))
        if c is not None and c["token"] != "NO_GOAL_ASSIGNED":
            rec = {"turn": r["turn"], "unit": r["unit"],
                   "res_branch": r["branch"], "cand_branch": c["branch"],
                   "cand_gen": c["gen"], "cand_final": c["final"]}
            # <= not <: first_div is the first turn whose OUTPUT differs, so the world at the
            # START of that turn is still identical in both games. The decision taken on it is
            # therefore same-state evidence — excluding it would discard the one turn where the
            # door demonstrably fires first.
            if first_div is None or r["turn"] <= first_div:
                same_state_cured.append(rec)
            else:
                postdiv_cured.append(rec)

    # M-BRANCH is only claimable on PRE-DIVERGENCE evidence: same world, no-goal on the resident,
    # cured on the candidate. Post-divergence cures are consistent with either mechanism and are
    # counted separately so they cannot be quietly used as proof.
    # WHERE THE DIVERGENCE IS SEEDED. A trajectory story with no identified seed is not a
    # mechanism, it is a shrug. At the first divergent turn the world is still identical, so any
    # generator-list difference there is C's door firing, and it is the CAUSE of everything after.
    # LIMITATION, STATED RATHER THAN DISCOVERED LATER. classify() only records turns inside the
    # fixture WINDOW. If the divergence starts before the window opens there are no rows there,
    # and an empty seed list means "this instrument cannot see it", NOT "no seed exists".
    win = sit["window"]
    lo, hi = win["turn_start"], win["turn_end"]
    seed_visible = first_div is not None and lo <= first_div <= hi
    seed = []
    if first_div is not None and seed_visible:
        res_at = {(r["turn"], r["unit"]): r for r in res if r["turn"] == first_div}
        for key, rr in sorted(res_at.items()):
            cc = cand_by_key.get(key)
            if cc is not None and list(cc["gen"]) != list(rr["gen"]):
                seed.append({"turn": key[0], "unit": key[1],
                             "res_branch": rr["branch"], "cand_branch": cc["branch"],
                             "res_gen": rr["gen"], "cand_gen": cc["gen"],
                             "res_final": rr["final"], "cand_final": cc["final"]})

    # WHAT ACTUALLY HAPPENED TO THE TURNS THAT STOPPED BEING NO-GOAL. Losing the
    # NO_GOAL_ASSIGNED attribution is NOT the same as the unit doing work: C can supply a
    # candidate that select() or the resolver then discards, which moves the token to a later
    # stage while the troll still stands still. Reporting only the count would hide that.
    became = collections.Counter()
    for r in res_ng:
        c = cand_by_key.get((r["turn"], r["unit"]))
        if c is None:
            became["no_matching_record"] += 1
        elif c["token"] is None:
            became["UNIT_ACTED"] += 1
        else:
            became[c["token"]] += 1

    verdict = "UNDETERMINED"
    if same_state_cured and seed:
        verdict = "M-SEEDED-TRAJ"
    elif endgame_only and first_div is not None and first_div < first_ng:
        verdict = "M-TRAJ"

    return {
        "situation": sid,
        "predicted_residual": (REGISTRY["predicted_uncured"][sid]["no_goal_turns"]
                               - REGISTRY["predicted_uncured"][sid]["c_supplies"]),
        "resident_no_goal_turns": len(res_ng),
        "candidate_no_goal_turns": len(cand_ng),
        "observed_residual": len(cand_ng),
        "matched_prediction": len(cand_ng) == (REGISTRY["predicted_uncured"][sid]["no_goal_turns"]
                                               - REGISTRY["predicted_uncured"][sid]["c_supplies"]),
        "resident_no_goal_branches": branches,
        "registry_said_endgame_only": REGISTRY["predicted_uncured"][sid]["reason"],
        "first_no_goal_turn": first_ng,
        "first_divergent_turn": first_div,
        "diverges_before_first_no_goal": (first_div is not None and first_div < first_ng),
        "predivergence_same_state_cured": len(same_state_cured),
        "predivergence_examples": same_state_cured[:4],
        "postdivergence_cured_pairs": len(postdiv_cured),
        "postdivergence_note": ("turn/unit pairs matched after divergence are NOT the same world; "
                                "they cannot distinguish the two mechanisms and are excluded from "
                                "the verdict"),
        "window": [lo, hi],
        "seed_search_visible": seed_visible,
        "seed_search_limit": (None if seed_visible else
                              f"divergence at turn {first_div} precedes the window [{lo}, {hi}]; "
                              f"the classifier records no rows there, so the seed is NOT "
                              f"OBSERVABLE with this instrument — absence of a seed here is a "
                              f"limit of the probe, not evidence that none exists"),
        "divergence_seed": seed,
        "resident_no_goal_turns_became": dict(became),
        "mechanism": verdict,
    }


def main():
    cfg = json.loads(H.CONFIG.read_text())
    print("building instrumented resident + candidate (shared tap definitions)")
    G1.build_instrumented_candidate()
    wd = Path(tempfile.mkdtemp(prefix="curec-mech-"))
    for name in ("res", "cand", "plain_res", "plain_cand"):
        (wd / name).mkdir(parents=True, exist_ok=True)
    instr_res = H.compile_candidate(G1.RESIDENT_INSTR, wd / "res")
    instr_cand = H.compile_candidate(G1.INSTR_CANDIDATE, wd / "cand")
    plain_res = H.compile_candidate(H.RESIDENT, wd / "plain_res")
    plain_cand = H.compile_candidate(G1.CANDIDATE, wd / "plain_cand")

    surprises = ["OSC-009", "OSC-031"]
    controls = ["OSC-001", "OSC-005"]
    out = {"surprises": [], "controls": []}

    for sid in surprises:
        r = analyse(sid, cfg, instr_res, instr_cand, plain_res, plain_cand)
        out["surprises"].append(r)
        print(f"\n{sid}: predicted residual {r['predicted_residual']}, observed "
              f"{r['observed_residual']} -> mechanism {r['mechanism']}")
        print(f"  resident no-goal branches: {r['resident_no_goal_branches']}")
        print(f"  first no-goal turn {r['first_no_goal_turn']}, first divergent turn "
              f"{r['first_divergent_turn']}")
        print(f"  PRE-divergence same-state pairs cured: {r['predivergence_same_state_cured']}"
              f"  (post-divergence, non-probative: {r['postdivergence_cured_pairs']})")
        print(f"  divergence seed: {r['divergence_seed'] if r['seed_search_visible'] else 'NOT OBSERVABLE — ' + r['seed_search_limit']}")
        print(f"  resident no-goal turns became: {r['resident_no_goal_turns_became']}")

    for sid in controls:
        r = analyse(sid, cfg, instr_res, instr_cand, plain_res, plain_cand)
        out["controls"].append(r)
        print(f"\nCONTROL {sid}: predicted {r['predicted_residual']}, observed "
              f"{r['observed_residual']}, matched={r['matched_prediction']}, "
              f"diverges_before_first_no_goal={r['diverges_before_first_no_goal']}")

    # THE DISCRIMINATION CHECK. If the controls show the same signature as the surprises, the
    # signature is not a mechanism and this probe must not be read as one.
    traj = [r for r in out["surprises"] if r["mechanism"] == "M-TRAJ"]
    if traj:
        ctrl_same = [r for r in out["controls"] if r["diverges_before_first_no_goal"]]
        out["control_verdict"] = {
            "surprises_claiming_M-TRAJ": [r["situation"] for r in traj],
            "controls_with_same_signature": [r["situation"] for r in ctrl_same],
            "discriminates": not ctrl_same,
        }
        if ctrl_same:
            print(f"\n!! CONTROL FAILS THE CLAIM: {[r['situation'] for r in ctrl_same]} also "
                  f"diverge before their first no-goal turn yet MATCHED prediction. "
                  f"'Divergence' alone is therefore NOT the mechanism.")
        else:
            print("\ncontrol discriminates: no matching fixture shows the signature")

    (HERE / "mechanism-g13-2026-08-18.json").write_text(json.dumps(out, indent=2) + "\n")
    print(f"\nwrote {(HERE / 'mechanism-g13-2026-08-18.json').name}")


if __name__ == "__main__":
    main()
