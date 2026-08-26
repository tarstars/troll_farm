#!/usr/bin/env python3
"""The P3 read on the candidate arm -- the item the control set has left open since C-16.

C-16 answered the RED half of R-B: with `SWAP_P3_SCOPING_ENABLED=false`, 9 of 60 orchard-eligible
seat views produce a P3 violation. That says the scoping is doing work. It says **nothing** about
what P3 reads on the arm that will actually be submitted, because on the eligible class the scoped
arm is byte-identical to the parent by construction. G-0 §8 carries the bar

    P3 games on orchard-eligible views (whole-game) | 0

and until this run, the candidate arm's number against that bar was UNMEASURED -- not passed.

This reads it, over the whole 240-view panel population, with `fuzz_panel.eval_p3` IMPORTED, not
restated. It also does the thing a bare "0" cannot do: it says **why** each 0 is a 0.

`fuzz_panel.eval_p3` (`claude_1/pipeline/fuzz_panel.py:1817`) has exactly three exits:

  A  `not orchard_eligible`      -> []   the guard. The two streams are never compared at all.
  B  `commands_c == commands_p`  -> []   the streams were compared and are equal.
  C  otherwise                   -> [{first_divergence_turn, ...}]   a violation.

A "0 P3 violations" headline is compatible with 240 A-exits, in which case the property has been
satisfied without a single stream comparison. So this run classifies every view by its exit, and
reports the decomposition beside the bar. That decomposition is the read; the bar is one line of it.

Then the counterfactual, which is the only number here that is not fixed in advance:

  P3*  -- `eval_p3(True, candidate, parent)` on the NON-eligible views, i.e. the same whole-stream
          predicate applied off-class, where P3 by definition does not reach. This is not a
          property violation and is never reported as one. It is the size of what the bar cannot
          see: how many views the candidate arm changes, and where each change starts.

GATES -- each aborts rather than degrading the number:

  G-S  subject identity. `arm-candidate.rs` hashes to the sha256 declared in
       `cure2-candidate-config.json` and in `arm-candidate.rs.sha256`, and declares
       `NARRATE_V5_ENABLED = false` -- it differs from `arm-instrument.rs` in exactly that one
       line. The instrument arm cannot answer P3 (its MSG diverges the stream on turn 1) and must
       not become the subject by accident. Checking for the *token* `MSG` would not do: the
       narration code is present in both arms and dead in this one, so the flag is the subject.
  G-Q  and the flag is not trusted either: on every graded view the candidate stream's `MSG`
       fragments must be identical to the PARENT's. Both bots emit the champion's one-time
       `MSG yamo-...` banner on their first turn -- that is the base's own stream, not telemetry --
       so "no MSG at all" is the wrong check and rejects the correct subject. What must be absent
       is any fragment the parent does not also emit. G-S is the declaration, G-Q is the
       observation.
  G-P  population identity. The regenerated 240 views agree with `results/panel-candidate.json`
       row for row on map, seat, class and `orchard_eligible`.
  G-M  reproduction. Every regenerated view reproduces that run's recorded candidate and parent
       margins. A read on a population that no longer reproduces the recorded panel is a read on a
       different corpus.
  G-B  eligible-class inertness. On every orchard-eligible view the candidate stream must be
       byte-identical to the parent's. A difference here is a REAL P3 violation and fails the read.
  G-V  the vacuity gate, and the reason this run is worth doing. At least one NON-eligible view
       must satisfy all three of: the streams differ, `eval_p3(False, ...)` is empty, and
       `eval_p3(True, ...)` is non-empty. That triple is the demonstration that exit A is a guard
       that returns [] without looking, rather than a comparison that happened to find equality.
       If no such view exists the read is INCONCLUSIVE and says so -- it does not claim a pass.
  G-C  correspondence. The set of non-eligible views the candidate changes must be exactly the set
       of games the C-4/C-15 census recorded an exchange on (`results/panel-swap-census.json`,
       decoded off the INSTRUMENT arm's `sw=` wire, a different arm and a different route). Two
       independent routes to the same 28 games, or the divergences are not the exchange's.

VERDICT.  The read is COMPLETE iff every gate passes and the graded P3 count is 0. COMPLETE is not
"P3 is neutral": it is "on this corpus the candidate arm violates P3 zero times, and here is
exactly how much of that zero is a measurement".

    python3 claude_1/cure2/p3_read.py [--only m004:0,...]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
for _p in ("claude_1/pipeline", "claude_1/banana-restoration-r2", "claude_1/narrate5"):
    sys.path.insert(0, str(REPO / _p))

import fuzz_panel as fp               # noqa: E402
import narrate5 as n5                 # noqa: E402
import regression_tests as rt         # noqa: E402
import semantic_harness as sh         # noqa: E402


def msg_fragments(commands):
    """Every MSG fragment of a command stream, in order, decoded by the narrator's own splitter."""
    return [(t, f.strip()) for t, line in enumerate(commands.rstrip("\n").split("\n"), 1)
            for f in n5.msg_fragments(line)]

CANDIDATE = HERE / "arm-candidate.rs"
INSTRUMENT = HERE / "arm-instrument.rs"
CAND_SHA = HERE / "arm-candidate.rs.sha256"
PANEL_CFG = HERE / "cure2-candidate-config.json"
RECORDED = HERE / "results" / "panel-candidate.json"
CENSUS = HERE / "results" / "panel-swap-census.json"
OUT = HERE / "results" / "p3-read-candidate-arm.json"


class GateError(Exception):
    """Anything that would make the number below mean something other than it says."""


NARRATE_OFF = "const NARRATE_V5_ENABLED:bool=false;"
NARRATE_ON = "const NARRATE_V5_ENABLED:bool=true;"


def subject_gate(cfg):
    """G-S: the arm under read is the candidate arm, by hash, with narration declared off.

    The `MSG` token appears in BOTH arms -- the narration code is compiled in and simply never
    reached when the flag is false -- so a substring check on `MSG` rejects the correct subject.
    What separates the two arms is one line, and this gate reads it: the candidate arm must
    declare the flag false, the instrument arm true, and they must differ nowhere else.
    """
    text = CANDIDATE.read_text()
    digest = hashlib.sha256(text.encode()).hexdigest()
    declared = cfg["candidate"]["sha256"]
    if digest != declared:
        raise GateError(f"arm-candidate.rs hashes {digest[:12]} but the panel config declares "
                        f"{declared[:12]} (G-S)")
    sidecar = CAND_SHA.read_text().split()[0]
    if sidecar != digest:
        raise GateError(f"arm-candidate.rs.sha256 says {sidecar[:12]}, bytes say {digest[:12]} "
                        f"(G-S)")
    if NARRATE_OFF not in text or NARRATE_ON in text:
        raise GateError("arm-candidate.rs does not declare NARRATE_V5_ENABLED=false -- the "
                        "subject may be an instrument arm, whose MSG diverges the stream on "
                        "turn 1 (G-S)")
    a, b = text.split("\n"), INSTRUMENT.read_text().split("\n")
    if len(a) != len(b):
        raise GateError(f"arm-candidate.rs has {len(a)} lines against arm-instrument.rs's "
                        f"{len(b)} (G-S)")
    diff = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
    if len(diff) != 1 or NARRATE_OFF not in a[diff[0]] or NARRATE_ON not in b[diff[0]]:
        raise GateError(f"arm-candidate.rs differs from arm-instrument.rs on {len(diff)} lines "
                        f"and not solely in the narration flag (G-S)")
    return {"file": "arm-candidate.rs", "sha256": digest,
            "narrate_v5_enabled": False,
            "sole_line_differing_from_arm_instrument.rs": diff[0],
            "source_of_truth": "cure2-candidate-config.json candidate.sha256"}


def run(binary, spec, turns):
    ref = fp.make_referee(spec)
    _transcript, commands = rt.run_binary_custom(Path(binary), ref, turns)
    return commands, fp.score(ref.inv) - fp.score(ref.opp_inv)


def classify(eligible, cand, parent, graded):
    """Which of eval_p3's three exits produced this view's result."""
    if not eligible:
        return "A-guard"
    if cand == parent:
        return "B-compared-equal"
    if graded:
        return "C-violation"
    raise GateError("eval_p3 returned no violation on an eligible view with differing streams -- "
                    "the imported grader does not have the three exits this read assumes")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--only")
    args = ap.parse_args()

    cfg = fp.load_config(PANEL_CFG)
    subject = subject_gate(cfg)
    recorded = json.loads(RECORDED.read_text())
    rec = {f"{g['map_id']}:{g['seat']}": g for g in recorded["games"]}
    if recorded["candidate_sha256"] != subject["sha256"]:
        raise GateError(f"results/panel-candidate.json was produced by "
                        f"{recorded['candidate_sha256'][:12]}, not the subject "
                        f"{subject['sha256'][:12]} (G-M)")

    with tempfile.TemporaryDirectory(prefix="cure2-p3read-") as wd:
        wd = Path(wd)
        bins = {}
        for name, src, crate in (
                ("parent", (PANEL_CFG.parent / cfg["parent"]["source"]).resolve(),
                 "cure2_parent_p3read"),
                ("candidate", CANDIDATE, "cure2_candidate_p3read")):
            bins[name] = wd / f"{name}.bin"
            sh.compile_text(Path(src).read_text(), bins[name], crate=crate)
        print("  two arms compiled (parent, candidate)", flush=True)

        jobs = {f"{j['spec']['map_id']}:{j['spec']['seat']}": j
                for j in fp.build_jobs(cfg, bins["candidate"], bins["parent"])}

        # G-P: the regenerated population is the recorded panel's population.
        if sorted(jobs) != sorted(rec):
            raise GateError(f"regenerated {len(jobs)} views, recorded panel has {len(rec)} "
                            f"(G-P)")
        for key, job in jobs.items():
            spec, row = job["spec"], rec[key]
            if (spec["class"] != row["class"]
                    or bool(spec["orchard_eligible"]) != bool(row["orchard_eligible"])):
                raise GateError(f"{key}: regenerated class/eligibility "
                                f"{spec['class']}/{spec['orchard_eligible']} against recorded "
                                f"{row['class']}/{row['orchard_eligible']} (G-P)")

        graded_keys = sorted(jobs)
        if args.only:
            wanted = set(args.only.split(","))
            graded_keys = [k for k in graded_keys if k in wanted]
        print(f"  {len(graded_keys)} seat views "
              f"({sum(1 for k in graded_keys if jobs[k]['spec']['orchard_eligible'])} "
              f"orchard-eligible)", flush=True)

        rows, margin_mismatch = [], []
        for i, key in enumerate(graded_keys, 1):
            job = jobs[key]
            spec, turns = job["spec"], job["turns"]
            eligible = bool(spec["orchard_eligible"])
            p_cmds, p_margin = run(bins["parent"], spec, turns)
            c_cmds, c_margin = run(bins["candidate"], spec, turns)

            c_msg, p_msg = msg_fragments(c_cmds), msg_fragments(p_cmds)
            if c_msg != p_msg:                                     # G-Q, per view
                raise GateError(f"{key}: the candidate emits MSG fragments the parent does not "
                                f"({c_msg[:2]} against {p_msg[:2]}) -- the narration flag is "
                                f"declared off but the arm narrates (G-Q)")

            graded = fp.eval_p3(eligible, c_cmds, p_cmds)          # the bar, as the panel grades it
            offclass = fp.eval_p3(True, c_cmds, p_cmds)            # P3*, the counterfactual
            exit_taken = classify(eligible, c_cmds, p_cmds, graded)

            row = rec[key]
            if (c_margin != row["candidate"]["margin"]
                    or p_margin != row["parent"]["margin"]):
                margin_mismatch.append(
                    {"game": key, "candidate": [c_margin, row["candidate"]["margin"]],
                     "parent": [p_margin, row["parent"]["margin"]]})

            rows.append({
                "game": key, "class": spec["class"], "seat": spec["seat"],
                "orchard_eligible": eligible, "turns": turns,
                "eval_p3_exit": exit_taken,
                "p3_violations": len(graded), "p3": graded,
                "streams_differ": c_cmds != p_cmds,
                "p3star_first_divergence_turn":
                    (offclass[0]["first_divergence_turn"] if offclass else None),
                "candidate_margin": c_margin, "parent_margin": p_margin,
                "margin_delta": c_margin - p_margin,
                "score_delta": row["candidate"]["score"] - row["parent"]["score"],
                "opp_score_delta": row["candidate"]["opp_score"] - row["parent"]["opp_score"],
            })
            if i % 40 == 0:
                print(f"    {i}/{len(graded_keys)}", flush=True)

    if margin_mismatch and not args.only:
        raise GateError(f"{len(margin_mismatch)} views do not reproduce the recorded panel's "
                        f"margins, first {margin_mismatch[:3]} (G-M)")

    eligible_rows = [r for r in rows if r["orchard_eligible"]]
    noneligible = [r for r in rows if not r["orchard_eligible"]]
    violations = [r for r in rows if r["p3_violations"] > 0]

    # G-B: eligible-class whole-game inertness.
    not_inert = [r["game"] for r in eligible_rows if r["streams_differ"]]
    if not_inert:
        raise GateError(f"{len(not_inert)} orchard-eligible views are NOT byte-identical to the "
                        f"parent {not_inert[:5]} -- these are real P3 violations (G-B)")

    # G-C: the changed off-class views are exactly the census's exchange-bearing games.
    census_swap = sorted(r["game"] for r in json.loads(CENSUS.read_text())["rows"]
                         if r["swaps"] > 0)
    changed_off = sorted(r["game"] for r in noneligible if r["streams_differ"])
    if not args.only and changed_off != census_swap:
        raise GateError(
            f"the candidate changes {len(changed_off)} non-eligible views but the census recorded "
            f"an exchange on {len(census_swap)}; symmetric difference "
            f"{sorted(set(changed_off) ^ set(census_swap))[:6]} (G-C)")

    # G-V: the vacuity demonstration.
    witnesses = [r["game"] for r in noneligible
                 if r["streams_differ"] and r["p3_violations"] == 0
                 and r["p3star_first_divergence_turn"] is not None]
    exits = {}
    for r in rows:
        exits[r["eval_p3_exit"]] = exits.get(r["eval_p3_exit"], 0) + 1

    p3star_firing = [r for r in noneligible if r["p3star_first_divergence_turn"] is not None]
    complete = bool(witnesses) and not violations and not args.only
    verdict = "COMPLETE" if complete else ("INCONCLUSIVE" if not witnesses else "SUBSET")
    if violations:
        verdict = "FAIL"

    report = {
        "read": "P3 on the candidate arm -- the bar, and how much of it is a measurement",
        "task": "20260825-dance-cure-candidate-2-swap",
        "subject": subject,
        "grader": "fuzz_panel.eval_p3, imported (claude_1/pipeline/fuzz_panel.py:1817) -- not "
                  "restated here",
        "population": {
            "config": str(PANEL_CFG.relative_to(REPO)),
            "views": len(rows), "orchard_eligible": len(eligible_rows),
            "non_eligible": len(noneligible),
            "recorded_panel": str(RECORDED.relative_to(REPO)),
        },
        "gates": {
            "G-S subject identity": f"PASS -- arm-candidate.rs {subject['sha256'][:12]} matches "
                                    f"the panel config and its sidecar, declares "
                                    f"NARRATE_V5_ENABLED=false, and differs from "
                                    f"arm-instrument.rs in exactly that one line",
            "G-Q narration observed off": f"PASS -- on all {len(rows)} graded views the "
                                          f"candidate's MSG fragments are identical to the "
                                          f"parent's (the champion's one-time banner and nothing "
                                          f"else); the arm emits no telemetry",
            "G-P population identity": f"PASS -- {len(rows)} regenerated views agree with the "
                                       f"recorded panel on map, seat, class and eligibility"
                                       + (f" (subset run: --only {args.only})" if args.only
                                          else ""),
            "G-M reproduction": ("PASS -- every view reproduces the recorded panel's candidate "
                                 "and parent margins"
                                 if not args.only else
                                 f"NOT RUN -- subset run (--only {args.only})"),
            "G-B eligible-class inertness": f"PASS -- {len(eligible_rows)}/{len(eligible_rows)} "
                                            f"orchard-eligible views byte-identical to the parent",
            "G-C correspondence with the census": (
                f"PASS -- the {len(changed_off)} non-eligible views the candidate changes are "
                f"exactly the {len(census_swap)} games the census recorded an exchange on, "
                f"decoded off the instrument arm's sw= wire by a different route"
                if not args.only else
                f"NOT RUN -- subset run (--only {args.only})"),
            "G-V vacuity demonstration": (
                f"PASS -- {len(witnesses)} non-eligible views have differing streams on which "
                f"eval_p3(False, ...) returns [] while eval_p3(True, ...) returns a divergence; "
                f"exit A is a guard, not a comparison"
                if witnesses else
                "FAIL -- no non-eligible view changes the stream, so nothing here demonstrates "
                "that the 0 is vacuous rather than earned; the read is INCONCLUSIVE"),
        },
        "the_bar": {
            "G-0 §8": "P3 games on orchard-eligible views (whole-game) = 0",
            "measured": len(violations),
            "met": not violations,
        },
        "decomposition_of_the_zero": {
            "eval_p3 exit A (guard: not orchard_eligible, streams never compared)":
                exits.get("A-guard", 0),
            "eval_p3 exit B (eligible, streams compared and equal)":
                exits.get("B-compared-equal", 0),
            "eval_p3 exit C (violation)": exits.get("C-violation", 0),
        },
        "counterfactual_p3star": {
            "what": "eval_p3(True, candidate, parent) on the NON-eligible views -- the same "
                    "whole-stream predicate applied where P3 does not reach. NOT a property "
                    "violation and never reported as one.",
            "non_eligible_views": len(noneligible),
            "views_whose_stream_the_candidate_changes": len(p3star_firing),
            "first_divergence_turns": sorted(
                r["p3star_first_divergence_turn"] for r in p3star_firing)[:40],
            "net_margin_delta_on_changed_views":
                sum(r["margin_delta"] for r in p3star_firing),
            "net_score_delta_on_changed_views":
                sum(r["score_delta"] for r in p3star_firing),
            "two_aggregates_are_not_the_same_number": (
                "C-15's published net cost is a delta of OWN SCORES; the C-16 and P3* figures are "
                "deltas of MARGIN (own score minus opponent score). Over this panel they differ "
                "in sign: own score %+d, opponent score %+d, margin %+d. Neither is wrong and "
                "neither may be quoted as the other."
                % (sum(r["score_delta"] for r in rows),
                   sum(r["opp_score_delta"] for r in rows),
                   sum(r["margin_delta"] for r in rows))),
            "changed_views": [{"game": r["game"], "class": r["class"],
                               "first_divergence_turn": r["p3star_first_divergence_turn"],
                               "margin_delta": r["margin_delta"],
                               "score_delta": r["score_delta"]}
                              for r in p3star_firing],
        },
        "rows": rows,
        "verdict": verdict,
        "meaning": (
            f"the candidate arm violates P3 {len(violations)} times over {len(rows)} seat views. "
            f"{exits.get('A-guard', 0)} of those views never reached a stream comparison at all "
            f"-- eval_p3's orchard guard returned [] before looking -- and the remaining "
            f"{exits.get('B-compared-equal', 0)} are the eligible class, where the scoping makes "
            f"the candidate byte-identical to the parent for the whole game by construction. So "
            f"the bar is met and NO part of the zero comes from the candidate changing a stream "
            f"and P3 finding it acceptable. Off-class, where P3 does not reach, the candidate "
            f"changes {len(p3star_firing)} views."
            if complete else
            "the read did not complete under its own gates; see gates above."),
        "not_proven_here": (
            "that the candidate is P3-neutral in any sense stronger than the scoping's whole-game "
            "inertness, or that the off-class changes are harmless -- P3* is a size, not a "
            "verdict, and the properties that do reach off-class (P1, P4, D-3) are graded by the "
            "panel and reported there, not here."),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"  P3 violations: {len(violations)} of {len(rows)} views")
    print(f"  exits: A-guard {exits.get('A-guard', 0)}  "
          f"B-compared-equal {exits.get('B-compared-equal', 0)}  "
          f"C-violation {exits.get('C-violation', 0)}")
    print(f"  P3* (off-class counterfactual): {len(p3star_firing)} of {len(noneligible)} "
          f"non-eligible views changed")
    print(f"  P3 read -> {verdict}")
    print(f"  -> {OUT.relative_to(REPO)}")
    return 0 if verdict in ("COMPLETE", "SUBSET") else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except GateError as exc:
        print(f"GATE FAILURE: {exc}", file=sys.stderr)
        sys.exit(2)
