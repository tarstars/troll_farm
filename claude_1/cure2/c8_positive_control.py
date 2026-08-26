#!/usr/bin/env python3
"""C-8 -- the POSITIVE control: a dance that the exchange ends, with progress restored.

G-0 §9: *C-8 -- positive control: a fixture where the exchange must fire and the dance ends ->
fires, and `progress_restored`.*

C-7 showed the two stop-counters can count a BAD swap (17->350, 0->344 under a gutted predicate).
C-8 is the other direction: that a GOOD one is recognised as good -- the rule does the thing it
was designed to do, and the instrument can see it.

WHY THIS CANNOT BE RUN THROUGH `fixture_harness`'s FIXED VERDICT
---------------------------------------------------------------
The obvious route -- point `fixture_harness.py` at the candidate arm and read a `FIXED` off one of
the 34 recorded situations -- is CLOSED, and closed for a real reason rather than a plumbing one.
The harness's episode-identity gate (card `20260821-episode-identity-regrade`, lifted verbatim
from the accepted `real_end_regrade.py`) asks whether the run reproduces THE RECORDED EPISODE:
the frozen window's command lines, and the board at the window's first turn. The library's subject
bot is the RESIDENT; the candidate is a different lineage. Measured, not assumed, this wake:

    fixture_harness.py --candidate claude_1/cure2/arm-candidate.rs --only <the 12 fixtures
    that grant an exchange>   ->   12/12 NOT_REPRODUCIBLE_ON_BASE, 0 graded either way.

That verdict is CORRECT and must not be worked around: a window is a property of the bot that
produced it (my `20260821T094945Z`, coordinator-accepted). So C-8 does not point the candidate at
another bot's window. It uses a window the candidate's OWN lineage produces.

THE SHAPE, pre-committed here before any number existed
-------------------------------------------------------
Two arms, differing by exactly ONE line (`arm-manifest.json`, control C-3):

    ON   `arm-instrument.rs`  swap rule ENABLED,  NARRATE v5 on   (C-2: equivalent in play to
                              `arm-candidate.rs` on 240/240 games -- so reading the exchange off
                              the instrument's wire is a reading about the candidate)
    OFF  `arm-ruleoff.rs`     swap rule DISABLED, NARRATE v5 on

Same map, same seed, same opponent, same everything else. Then, per game:

  1. THE DANCE is a D-1 episode on the **OFF** arm: `(unit u, turns [lo,hi], cells, k)`, found by
     `trace_detectors.detect_d1` -- the panel's own detector, not a second definition written
     here. The window therefore belongs to the bot that produced it: the candidate's own lineage
     with the rule switched off. That is the counterfactual "what happens without the rule".

  2. THE EXCHANGE MUST FIRE: on the ON arm, a granted exchange (`sw >= 1` on the v5 wire) at a
     turn `t` inside `[lo, hi]` whose `S`/`X` units include `u`.

  3. THE DANCE ENDS, by the harness's OWN two clauses, never one alone:
       `detector_silent`     -- no D-1 episode for `u` on the ON arm overlapping `[lo, hi]`
       `progress_restored`   -- `fixture_harness.had_progress(tr_on, u, lo, hi)`, imported from
                                the harness rather than re-implemented, so "progress" cannot mean
                                one thing to the gate and another here.

  A case PASSES iff all three hold. C-8 PASSES iff at least one case passes, and the census of
  every case -- passing and failing -- is published.

THE GATE THAT MAKES THE COUNTERFACTUAL LEGITIMATE
-------------------------------------------------
The two arms diverge, so the OFF arm's turn numbers describe a run that is not the ON arm's. That
is the exact hazard I raised on 2026-08-21 and it is not waved away here, it is GATED:

  G-D  divergence identity -- for every case, the first turn on which the two arms' command lines
       differ (MSG stripped) must be EXACTLY the ON arm's first exchange turn, and the dance
       window must OPEN at or before it (`lo <= d`). Then turns `1..d-1` are literally shared
       history: the same board, the same commands, the same unit in the same cells entering the
       same alternation. The exchange is the only thing that could have changed what followed.
       A game where the arms diverge BEFORE any exchange fails the gate and is excluded from the
       primary population with its reason published (never silently dropped).

  G-E  the ON arm must actually grant the exchange the wire claims: the S/X units are read from
       the decoded v5 payload and must be non-empty on every counted turn.

CONTROLS -- so a PASS is a measurement and not a tautology
----------------------------------------------------------
  N-1  INERTNESS. The identical pipeline is re-run with the ON arm replaced by the OFF arm
       itself (`--inert`). Without the rule nothing can fire, so every case must fail and the
       pass count must be 0. A pipeline that reports passes with no rule at all is measuring
       something other than the exchange.
  N-2  CLAUSE LIVENESS. `progress_restored` is computed on the OFF arm over the SAME windows. If
       it were True everywhere it would be a clause that cannot say no, and a PASS would be
       worth nothing. The number is published either way.
  N-3  CORROBORATION, not a gate. For each case, whether the OFF arm's episode is EXACTLY a
       frozen library episode (same unit, bounds, cells and k) -- i.e. the dance the rule ends is
       one the corpus actually recorded, not one the counterfactual invented.
  G-R  DOUBLE COUNTING, refused. All 34 fixtures are re-runs of panel games: every fixture's
       provenance `map_id:seat` is one of the 240. On a `--panel` run each of them is therefore
       played TWICE, and reporting "274 games" would inflate the population by 14 %. Every row
       carries its canonical `map_id:seat`, the headline counts are the DEDUPLICATED ones, and
       G-R requires the two runs of a duplicated case to return the SAME verdict -- a free
       re-run identity check over the fixture set, which fails the run if it ever disagrees.

    python3 claude_1/cure2/c8_positive_control.py [--panel] [--only OSC-005,...] [--inert]
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
           "claude_1/narrate5"):
    sys.path.insert(0, str(REPO / _p))

import fixture_harness as fh          # noqa: E402
import fuzz_panel as fp               # noqa: E402
import regression_tests as rt         # noqa: E402
import semantic_harness as sh         # noqa: E402
import trace_detectors as td          # noqa: E402
import narrate5 as n5                 # noqa: E402

ON_ARM = HERE / "arm-instrument.rs"
OFF_ARM = HERE / "arm-ruleoff.rs"
PANEL_CFG = HERE / "cure2-instrument-config.json"
CENSUS = HERE / "results" / "panel-swap-census.json"
OUT = HERE / "results" / "c8-positive-control.json"


class GateError(Exception):
    """Anything that would make the number below mean something other than it says."""


def run(binary, spec, turns):
    """One game on one arm: the trace, the command lines, the D-1 episodes, the exchange turns."""
    transcript, commands = rt.run_binary_custom(binary, fp.make_referee(spec), int(turns))
    tr = td.build_trace(transcript, commands)
    lines = commands.rstrip("\n").split("\n")
    if len(lines) != tr.T:
        raise GateError(f"{len(lines)} command lines against {tr.T} traced turns")
    exchanges = []
    for t, line in enumerate(lines, 1):
        frags = n5.msg_fragments(line)
        if len(frags) != 1:
            raise GateError(f"turn {t}: {len(frags)} MSG fragments")
        _turn, units, _order, _banner, meta = n5.decode(frags[0].strip())
        if not meta["sw"]:
            continue
        involved = sorted(uid for uid, u in units.items() if u[2] in ("S", "X"))
        if not involved:                                              # G-E
            raise GateError(f"turn {t}: sw={meta['sw']} but no S/X unit on the wire (G-E)")
        exchanges.append({"turn": t, "sw": meta["sw"], "units": involved})
    return {"trace": tr, "lines": lines, "episodes": td.detect_d1(tr).get("episodes", []),
            "exchanges": exchanges}


def first_divergence(on_lines, off_lines):
    """The first turn whose commands differ with the MSG fragment stripped. The two arms both
    narrate, and their payloads differ by construction (`so`/`sn` counters), so comparing the raw
    lines would report divergence on turn 1 of every game and the gate would be meaningless."""
    for t, (a, b) in enumerate(zip(on_lines, off_lines), 1):
        if n5.strip_msg(a) != n5.strip_msg(b):
            return t
    if len(on_lines) != len(off_lines):
        return min(len(on_lines), len(off_lines)) + 1
    return None


def canonical_keys(sits):
    """`fixture id -> map_id:seat`, so a fixture and the panel game it was cut from are one game."""
    return {s["id"]: f"{s['provenance']['map_id']}:{s['provenance']['seat']}" for s in sits}


def frozen_episodes(sits):
    """The library's own frozen D-1 windows, for the N-3 corroboration column."""
    out = {}
    for sit in sits:
        w = sit["window"]
        if sit["kind"] != "D1_EPISODE":
            continue
        out[sit["id"]] = {"unit": w["unit"], "turn_start": w["turn_start"],
                          "turn_end": w["turn_end"], "k": w["k"],
                          "cells": [list(c) for c in w["cells"]]}
    return out


def cases_for_game(key, on, off, frozen=None):
    """Every (dance, exchange) case of one game, each carrying its own verdict and reasons."""
    d = first_divergence(on["lines"], off["lines"])
    first_exchange = on["exchanges"][0]["turn"] if on["exchanges"] else None
    rows = []
    for ep in off["episodes"]:
        u, lo, hi = ep["unit"], ep["turn_start"], ep["turn_end"]
        fires = [e for e in on["exchanges"] if lo <= e["turn"] <= hi and u in e["units"]]
        # G-D: shared history up to the first exchange, and the dance already open there.
        gate_d = (d is not None and first_exchange is not None and d == first_exchange
                  and lo <= d)
        reasons = []
        if not fires:
            reasons.append("no exchange involving this unit inside the dance window")
        if not gate_d:
            if first_exchange is None:
                reasons.append("the ON arm granted no exchange in this game")
            elif d != first_exchange:
                reasons.append(f"the arms diverge at turn {d} but the first exchange is at "
                               f"{first_exchange}: something other than the rule moved them "
                               f"apart (G-D)")
            else:
                reasons.append(f"the dance opens at {lo}, after the arms diverge at {d}, so its "
                               f"turn numbers are not shared history (G-D)")
        on_over = [e for e in on["episodes"]
                   if e["unit"] == u and not (e["turn_end"] < lo or e["turn_start"] > hi)]
        silent = not on_over
        restored = fh.had_progress(on["trace"], u, lo, hi)
        off_restored = fh.had_progress(off["trace"], u, lo, hi)
        # Diagnostics, REPORTED and never part of the verdict: does the unit progress at all
        # after the window closes? It separates "parked for the rest of the game" from
        # "progressed a turn after the window the counterfactual drew".
        tail_on = fh.had_progress(on["trace"], u, hi, on["trace"].T)
        tail_off = fh.had_progress(off["trace"], u, hi, off["trace"].T)
        if not silent:
            reasons.append(f"the ON arm still dances: {len(on_over)} D-1 episode(s) overlap "
                           f"the window")
        if not restored:
            reasons.append("progress not restored on the ON arm over the window")
        corroborated = None
        if frozen is not None:
            f = frozen.get(key)
            corroborated = bool(f and f["unit"] == u and f["turn_start"] == lo
                                and f["turn_end"] == hi and f["k"] == ep["k"]
                                and f["cells"] == [list(c) for c in ep["cells"]])
        rows.append({
            "game": key, "unit": u, "window": [lo, hi], "k": ep["k"],
            "cells": [list(c) for c in ep["cells"]],
            "first_divergence_turn": d, "first_exchange_turn": first_exchange,
            "shared_history_gate": gate_d,
            "exchange_fires_in_window": bool(fires),
            "exchange_turns": [e["turn"] for e in fires],
            "detector_silent_on_arm": silent,
            "progress_restored_on_arm": restored,
            "progress_on_ruleoff_arm": off_restored,
            "progress_after_window_on_arm": tail_on,
            "progress_after_window_on_ruleoff_arm": tail_off,
            "matches_frozen_episode": corroborated,
            "verdict": ("PASS" if (fires and gate_d and silent and restored) else "FAIL"),
            "reasons": reasons,
        })
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--only")
    ap.add_argument("--panel", action="store_true", help="add the 240-game panel")
    ap.add_argument("--inert", action="store_true",
                    help="N-1: replace the ON arm with the OFF arm. Every case must FAIL.")
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()

    cfg = json.loads(fh.CONFIG.read_text())
    sits = fh.load_situations(args.only.split(",") if args.only else None)
    frozen = frozen_episodes(sits)
    canon = canonical_keys(fh.load_situations())
    all_rows, per_game = [], []

    with tempfile.TemporaryDirectory(prefix="cure2-c8-") as wd:
        wd = Path(wd)
        on_bin, off_bin = wd / "on.bin", wd / "off.bin"
        sh.compile_text(OFF_ARM.read_text(), off_bin, crate="cure2_arm_ruleoff_c8")
        if args.inert:
            on_bin = off_bin
        else:
            sh.compile_text(ON_ARM.read_text(), on_bin, crate="cure2_arm_instrument_c8")
        print(f"  {len(sits)} fixtures, two arms"
              f"{' (N-1 INERT: both arms are the rule-off arm)' if args.inert else ''}",
              flush=True)
        for sit in sits:
            spec = fh.spec_for(sit, cfg)
            on = run(on_bin, spec, cfg["turns"])
            off = run(off_bin, spec, cfg["turns"])
            rows = cases_for_game(sit["id"], on, off, frozen)
            all_rows += rows
            per_game.append({"game": sit["id"], "dances_without_the_rule": len(off["episodes"]),
                             "dances_with_the_rule": len(on["episodes"]),
                             "exchanges": len(on["exchanges"])})
        if args.panel:
            pcfg = fp.load_config(PANEL_CFG)
            parent = wd / "parent.bin"
            parent_src = (PANEL_CFG.parent / pcfg["parent"]["source"]).resolve()
            sh.compile_text(parent_src.read_text(), parent, crate="cure2_parent_c8")
            jobs = {f"{j['spec']['map_id']}:{j['spec']['seat']}": j
                    for j in fp.build_jobs(pcfg, on_bin, parent)}
            census = {r["game"]: r for r in json.loads(CENSUS.read_text())["rows"]}
            keys = list(census)
            for i, key in enumerate(keys, 1):
                job = jobs[key]
                on = run(on_bin, job["spec"], job["turns"])
                off = run(off_bin, job["spec"], job["turns"])
                # G-B: the ON arm re-run here must reproduce the published exchange count of
                # this game, or it is not the population the census describes.
                if not args.inert and len(on["exchanges"]) != census[key]["swaps"]:
                    raise GateError(f"{key}: {len(on['exchanges'])} exchanges against the "
                                    f"published {census[key]['swaps']} in "
                                    f"panel-swap-census.json (G-B)")
                rows = cases_for_game(key, on, off, None)
                all_rows += rows
                per_game.append({"game": key, "dances_without_the_rule": len(off["episodes"]),
                                 "dances_with_the_rule": len(on["episodes"]),
                                 "exchanges": len(on["exchanges"])})
                if i % 40 == 0:
                    print(f"  panel {i}/{len(keys)}", flush=True)

    for r in all_rows:
        r["canonical_game"] = canon.get(r["game"], r["game"])
    for g in per_game:
        g["canonical_game"] = canon.get(g["game"], g["game"])

    # G-R: a duplicated case (fixture run and panel run of the same map:seat) must agree.
    by_case = {}
    for r in all_rows:
        by_case.setdefault((r["canonical_game"], r["unit"], tuple(r["window"])), []).append(r)
    disagree = {"|".join(map(str, k)): sorted({x["verdict"] for x in v})
                for k, v in by_case.items() if len({x["verdict"] for x in v}) > 1}
    if disagree:
        raise GateError(f"the same case returned different verdicts on its fixture run and its "
                        f"panel run: {disagree} (G-R)")
    duplicated = sum(1 for v in by_case.values() if len(v) > 1)

    passes = [r for r in all_rows if r["verdict"] == "PASS"]
    fired = [r for r in all_rows if r["exchange_fires_in_window"]]
    distinct_cases = len(by_case)
    distinct_fired = len({k for k, v in by_case.items() if v[0]["exchange_fires_in_window"]})
    distinct_passes = len({k for k, v in by_case.items() if v[0]["verdict"] == "PASS"})
    distinct_quiet_but_stalled = len(
        {k for k, v in by_case.items()
         if v[0]["exchange_fires_in_window"] and v[0]["shared_history_gate"]
         and v[0]["detector_silent_on_arm"] and not v[0]["progress_restored_on_arm"]})
    verdict = "FAIL" if args.inert else ("PASS" if passes else "FAIL")
    if args.inert:
        verdict = "PASS (N-1 inert control: 0 cases, as required)" if not passes else \
                  "FAIL -- the inert arm produced a passing case; the pipeline is not measuring " \
                  "the exchange"

    report = {
        "control": "C-8 -- positive control: the exchange fires and the dance ends",
        "task": "20260825-dance-cure-candidate-2-swap",
        "mode": "N-1 inert (both arms rule-off)" if args.inert else "ON=arm-instrument.rs, "
                                                                   "OFF=arm-ruleoff.rs",
        "dance_definition": "a D-1 episode on the rule-off arm, from trace_detectors.detect_d1",
        "clauses": "detector_silent AND progress_restored, both from the fixture harness; "
                   "progress via fixture_harness.had_progress, imported not re-implemented",
        "games_played": len(per_game),
        "games": len({g["canonical_game"] for g in per_game}),
        "dance_cases": distinct_cases,
        "cases_where_the_exchange_fires": distinct_fired,
        "cases_passing": distinct_passes,
        "cases_quiet_but_stalled": distinct_quiet_but_stalled,
        "rows_before_deduplication": {
            "rows": len(all_rows), "firing": len(fired), "passing": len(passes),
            "duplicated_cases": duplicated,
            "meaning": "all 34 fixtures are re-runs of panel games, so a --panel run plays each "
                       "of them twice; the headline counts above are deduplicated by "
                       "(map_id:seat, unit, window)"},
        "gates": {
            "G-D divergence identity": "the arms' first differing command turn must be the ON "
                                       "arm's first exchange turn, and the dance must open at or "
                                       "before it; cases that fail it are published with the "
                                       "reason, never dropped",
            "G-B panel identity": ("PASS -- every panel game reproduces its "
                                   "panel-swap-census.json exchange count on the ON arm"
                                   if args.panel and not args.inert else
                                   "NOT RUN -- fixtures only" if not args.panel else
                                   "NOT APPLICABLE -- inert run grants no exchange"),
            "G-E wire honesty": "every counted exchange turn carries at least one S/X unit",
            "G-R duplicate agreement": f"PASS -- {duplicated} cases played twice (fixture run and "
                                       f"panel run of the same map:seat), 0 disagreements"},
        "controls": {
            "N-1 inertness": "run with --inert; every case must FAIL",
            "N-2 clause liveness": {
                "windows_where_the_ruleoff_arm_also_progresses":
                    sum(1 for v in by_case.values() if v[0]["progress_on_ruleoff_arm"]),
                "windows_where_it_does_not":
                    sum(1 for v in by_case.values() if not v[0]["progress_on_ruleoff_arm"]),
                "meaning": "if the second number is 0 the progress clause cannot say no and a "
                           "PASS is worth nothing"},
            "N-3 corroboration": {
                "passing_cases_matching_a_frozen_library_episode":
                    sum(1 for v in by_case.values()
                        if v[0]["verdict"] == "PASS" and any(x["matches_frozen_episode"]
                                                             for x in v))},
        },
        "verdict": verdict,
        "passing_cases": passes,
        "cases": all_rows,
        "per_game": per_game,
    }
    Path(args.out).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"\n  distinct dance cases {distinct_cases}; exchange fires in {distinct_fired}; "
          f"PASS {distinct_passes}; quiet-but-stalled {distinct_quiet_but_stalled} "
          f"({len(all_rows)} rows before deduplication)")
    for r in passes[:10]:
        print(f"    PASS {r['game']} unit {r['unit']} turns {r['window'][0]}-{r['window'][1]} "
              f"k={r['k']} exchange@{r['exchange_turns']} frozen={r['matches_frozen_episode']}")
    print(f"  verdict: {verdict}")
    print(f"  -> {args.out}")
    return 0 if verdict.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
