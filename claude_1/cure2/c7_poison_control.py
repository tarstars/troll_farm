#!/usr/bin/env python3
"""C-7 -- the inertness control for C-5 and C-6, run against a poison arm that DOES loop.

G-0 §9: C-5 (the same unordered pair exchanging twice within 6 turns) and C-6 (the same pair on
CONSECUTIVE turns) are the two counters that can stop Candidate 2. On the candidate arm C-6 is 0.
A zero from a counter that cannot count is not a measurement, so C-7 requires a bot whose
predicate is gutted to "swap on every block" (`arm-c7poison.rs`, built by
`make_c7_poison_arm.py`) and demands that BOTH counters fire loudly on it.

THE COUNTING SHAPE, settled before the run (coordinator 20260825T201608Z, replacement card
20260825T201101Z).  `swap_loop_control.py` pairs movers with displaced partners off the v5 wire,
which carries per-unit branch codes `S`/`X` and the count `sw` but NOT which `S` went with which
`X`.  On a turn that granted one exchange the pairing is forced; on a turn that granted two or
more it is not, and the published control reports the turn as AMBIGUOUS and counts it against the
gate rather than guessing.  That is the right conservative choice for the candidate -- where the
count is 0 -- and the wrong one here: the gutted predicate grants several exchanges per turn, so a
poison that fires would be reported as "ambiguous", which reads as "the control could not tell"
when what happened is "the control fired".

So this control pairs from the COMMAND STREAM instead, where the pairing is a fact and not an
inference.  An exchange writes exactly two commands: the mover `S` at cell A moves to the
partner's cell B, and the partner `X` moves to A.  Given the referee's own pre-turn cells, a pair
{a,b} is an exchange iff

    dest(a) == cell(b)  and  dest(b) == cell(a)   with  branch(a),branch(b) == S,X

and this is unambiguous no matter how many exchanges a turn granted, because a cell holds one
unit.  Nothing is guessed and nothing is dropped: a multi-exchange turn contributes every one of
its pairs.  Both pairings are computed and reported side by side.

Gates -- each fails the run rather than degrading it:

  G-P  pairing completeness -- on EVERY turn of EVERY game of BOTH arms the number of
       command-derived pairs must equal the wire's `sw`, and the units in those pairs must be
       exactly the units carrying `S`/`X`.  This is what earns the word "unambiguous": if the two
       sources disagreed anywhere the pairing would be an interpretation, not a reading.
  G-B  baseline identity -- the unpoisoned instrument arm re-run here must reproduce the
       published `swap-loop-control.json`: the same 20 exchanges on the same 12 pairs and turns.
       Without it the poison and the baseline are not the same population.
  G-C  wire-pairing agreement -- on turns that granted exactly one exchange the two pairings must
       name the same pair.  The command pairing is then a strict extension of the published one,
       not a different measurement.

Verdicts:

  C-7 PASSES iff on the poison arm C-6 > 0 AND C-5 > 0 under the command pairing, and the
  unpoisoned baseline reproduces its published C-6 = 0.  A poison that only moved C-5 would leave
  C-6 -- the counter that carries Theorem 1's falsifier -- still unproven.

    python3 claude_1/cure2/c7_poison_control.py [--only OSC-001,...]
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

POISON = HERE / "arm-c7poison.rs"
INSTR = HERE / "arm-instrument.rs"
PUBLISHED = HERE / "results" / "swap-loop-control.json"
PANEL_CFG = HERE / "cure2-instrument-config.json"
CENSUS = HERE / "results" / "panel-swap-census.json"
OUT = HERE / "results" / "c7-poison-control.json"
WINDOW = 6


class GateError(Exception):
    """Anything that would make the number below mean something other than it says."""


def exchange_pairs(cells, dest, branch):
    """The exchange pairs of one turn, read off the commands. Pure, so it is unit-testable
    against a fabricated multi-exchange turn -- which the corpus never produced.

    `cells` id -> pre-turn cell, `dest` id -> MOVE destination (movers only), `branch` id -> v5
    branch code. Returns (rule_pairs, incidental), where a rule pair carries `S`/`X` and an
    incidental one is a mutual position exchange two planners arranged on their own.
    """
    pairs, incidental = [], []
    ids = sorted(dest)
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            if dest[a] == cells.get(b) and dest[b] == cells.get(a):
                if sorted((branch.get(a), branch.get(b))) == ["S", "X"]:
                    pairs.append((a, b))
                else:
                    incidental.append({"pair": [a, b],
                                       "branches": [branch.get(a), branch.get(b)]})
    return pairs, incidental


def turn_rows(key, transcript, commands):
    """One row per turn: the wire's S/X ids and `sw`, and the command-derived exchange pairs."""
    trace = td.build_trace(transcript, commands)
    lines = commands.rstrip("\n").split("\n")
    if len(lines) != trace.T:
        raise GateError(f"{key}: {len(lines)} command lines against {trace.T} traced turns")
    rows = []
    for t in range(1, trace.T + 1):
        frags = n5.msg_fragments(lines[t - 1])
        if len(frags) != 1:
            raise GateError(f"{key} turn {t}: {len(frags)} MSG fragments")
        _turn, units, _order, _banner, meta = n5.decode(frags[0].strip())
        s_ids = sorted(uid for uid, u in units.items() if u[2] == "S")
        x_ids = sorted(uid for uid, u in units.items() if u[2] == "X")
        cells = {u.id: u.cell for u in trace.state(t).own_units()}
        dest = {uid: tuple(c.args[0]) for uid, c in trace.cmds(t).by_unit.items()
                if c.verb == "MOVE"}
        branch = {uid: u[2] for uid, u in units.items()}
        pairs, incidental = exchange_pairs(cells, dest, branch)
        incidental = [dict(row, turn=t) for row in incidental]
        # G-P: the two sources must agree on how many exchanges happened and on who was in them.
        if len(pairs) != meta["sw"]:
            raise GateError(f"{key} turn {t}: {len(pairs)} command-derived pairs against "
                            f"sw={meta['sw']} on the wire (G-P)")
        flat = sorted(uid for pair in pairs for uid in pair)
        if flat != sorted(s_ids + x_ids):
            raise GateError(f"{key} turn {t}: paired units {flat} against S/X "
                            f"{sorted(s_ids + x_ids)} (G-P)")
        rows.append({"turn": t, "sw": meta["sw"], "own_units": len(cells),
                     "movers": s_ids, "displaced": x_ids,
                     "incidental_exchanges": incidental,
                     "pairs": [list(p) for p in pairs],
                     "directed": [[s, x] for s in s_ids for x in x_ids
                                  if tuple(sorted((s, x))) in pairs]})
    return rows


def counters(events):
    """C-5 and C-6 off a list of {game, turn, pair} exchanges. Same algebra as the published
    control; only the source of `pair` differs."""
    by_pair = {}
    for e in events:
        by_pair.setdefault((e["game"], tuple(e["pair"])), []).append(e)
    c5, c6 = [], []
    for (game, pair), rows in sorted(by_pair.items()):
        rows.sort(key=lambda r: r["turn"])
        for previous, current in zip(rows, rows[1:]):
            gap = current["turn"] - previous["turn"]
            record = {"game": game, "pair": list(pair), "first_turn": previous["turn"],
                      "second_turn": current["turn"], "gap": gap}
            if gap <= WINDOW:
                c5.append(record)
            if gap == 1:
                c6.append(record)
    return c5, c6, {f"{g}:{p[0]}-{p[1]}": [r["turn"] for r in rows]
                    for (g, p), rows in sorted(by_pair.items())}


def measure(arm_rows):
    """Both pairings over every game of one arm."""
    command_events, wire_events, ambiguous, agree, disagree = [], [], [], 0, []
    for key, rows in arm_rows:
        for row in rows:
            for pair in row["pairs"]:
                command_events.append({"game": key, "turn": row["turn"],
                                       "pair": tuple(sorted(pair))})
            if row["sw"] == 0:
                continue
            if len(row["movers"]) == 1 and len(row["displaced"]) == 1:
                wire_pair = tuple(sorted((row["movers"][0], row["displaced"][0])))
                wire_events.append({"game": key, "turn": row["turn"], "pair": wire_pair})
                if [list(wire_pair)] == row["pairs"]:
                    agree += 1
                else:
                    disagree.append({"game": key, "turn": row["turn"],
                                     "wire": list(wire_pair), "commands": row["pairs"]})
            else:
                ambiguous.append({"game": key, "turn": row["turn"], "movers": row["movers"],
                                  "displaced": row["displaced"], "pairs": row["pairs"]})
    c5, c6, pairs = counters(command_events)
    w5, w6, wpairs = counters(wire_events)
    return {
        "games": len(arm_rows),
        "turns": sum(len(r) for _k, r in arm_rows),
        "exchange_turns": sum(1 for _k, rows in arm_rows for r in rows if r["sw"]),
        "exchanges": len(command_events),
        "max_exchanges_on_one_turn": max((r["sw"] for _k, rows in arm_rows for r in rows),
                                         default=0),
        "multi_exchange_turns": sum(1 for _k, rows in arm_rows for r in rows if r["sw"] > 1),
        "max_own_units_on_one_turn": max((r["own_units"] for _k, rows in arm_rows for r in rows),
                                         default=0),
        "incidental_position_exchanges": sum(len(r["incidental_exchanges"])
                                             for _k, rows in arm_rows for r in rows),
        "incidental_rows": [dict(row_i, game=k) for k, rows in arm_rows for r in rows
                            for row_i in r["incidental_exchanges"]][:40],
        "command_pairing": {
            "exchanges_paired": len(command_events), "ambiguous": 0,
            "c5_repeats_within_window": len(c5), "c6_consecutive_turn_repeats": len(c6),
            "c5_rows": c5[:60], "c6_rows": c6[:60], "pairs": pairs},
        "wire_pairing": {
            "exchanges_paired": len(wire_events), "ambiguous_turns": len(ambiguous),
            "exchanges_lost_to_ambiguity": len(command_events) - len(wire_events),
            "c5_repeats_within_window": len(w5), "c6_consecutive_turn_repeats": len(w6),
            "verdict_as_published": ("PASS" if not w6 and not ambiguous else "FAIL"),
            "ambiguous_rows": ambiguous[:40], "pairs": wpairs},
        "agreement": {"single_exchange_turns": agree + len(disagree), "agree": agree,
                      "disagree": disagree},
    }


def run_arm(binary, sits, cfg):
    rows = []
    for sit in sits:
        spec = fh.spec_for(sit, cfg)
        transcript, commands = rt.run_binary_custom(binary, fp.make_referee(spec),
                                                    int(cfg["turns"]))
        rows.append((sit["id"], turn_rows(sit["id"], transcript, commands)))
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--only")
    ap.add_argument("--panel", action="store_true",
                    help="add the 240-game panel to the 34 fixtures. The fixtures carry two or "
                         "three own units and the poison never granted two exchanges on one turn "
                         "there; the panel is where a multi-exchange turn -- the ambiguity the "
                         "wire pairing cannot resolve -- actually occurs.")
    args = ap.parse_args()
    cfg = json.loads(fh.CONFIG.read_text())
    sits = fh.load_situations(args.only.split(",") if args.only else None)

    with tempfile.TemporaryDirectory(prefix="cure2-c7-") as wd:
        wd = Path(wd)
        instr_bin, poison_bin = wd / "instr.bin", wd / "poison.bin"
        sh.compile_text(INSTR.read_text(), instr_bin, crate="cure2_arm_instrument_c7")
        sh.compile_text(POISON.read_text(), poison_bin, crate="cure2_arm_c7poison")
        print(f"  {len(sits)} fixtures, two arms", flush=True)
        base_rows = run_arm(instr_bin, sits, cfg)
        print("  baseline (arm-instrument.rs) done", flush=True)
        poison_rows = run_arm(poison_bin, sits, cfg)
        print("  poison   (arm-c7poison.rs)  done", flush=True)
        panel_keys, census_rows = [], {}
        base_panel, poison_panel = [], []
        if args.panel:
            census_rows = {r["game"]: r for r in json.loads(CENSUS.read_text())["rows"]}
            pcfg = fp.load_config(PANEL_CFG)
            parent = wd / "parent.bin"
            parent_src = (PANEL_CFG.parent / pcfg["parent"]["source"]).resolve()
            sh.compile_text(parent_src.read_text(), parent, crate="cure2_parent_c7")
            jobs = {f"{j['spec']['map_id']}:{j['spec']['seat']}": j
                    for j in fp.build_jobs(pcfg, instr_bin, parent)}
            panel_keys = [r["game"] for r in json.loads(CENSUS.read_text())["rows"]]
            for i, key in enumerate(panel_keys, 1):
                job = jobs[key]
                for binary, rows in ((instr_bin, base_panel), (poison_bin, poison_panel)):
                    transcript, cmds = rt.run_binary_custom(binary, fp.make_referee(job["spec"]),
                                                            job["turns"])
                    rows.append((key, turn_rows(key, transcript, cmds)))
                if i % 40 == 0:
                    print(f"  panel {i}/{len(panel_keys)}", flush=True)
            # G-B on the panel: every game reproduces its recorded exchange count on the
            # unpoisoned arm, so the two arms are being compared on the recorded population.
            seen = {}
            for key, rows in base_panel:
                if key in census_rows:
                    seen[key] = sum(r["sw"] for r in rows)
            bad = {k: (v, census_rows[k]["swaps"]) for k, v in seen.items()
                   if v != census_rows[k]["swaps"]}
            if bad:
                raise GateError(f"panel exchange counts differ from panel-swap-census.json: "
                                f"{list(bad.items())[:5]} (G-B)")

    base_fixtures = measure(base_rows)
    base = measure(base_rows + base_panel)
    poison = measure(poison_rows + poison_panel)

    # G-B: the baseline is the published population, exchange for exchange. Only meaningful on
    # the whole fixture set; a --only subset reports the gate as NOT RUN rather than as passed.
    published = json.loads(PUBLISHED.read_text())
    full_run = args.only is None
    if full_run:
        if base_fixtures["exchanges"] != published["exchanges"]:
            raise GateError(f"baseline {base_fixtures['exchanges']} exchanges against the "
                            f"published {published['exchanges']} (G-B)")
        if base_fixtures["command_pairing"]["pairs"] != published["pairs"]:
            raise GateError("baseline pair/turn map differs from the published control (G-B)")
    # G-C: on forced turns the two pairings must name the same pair, on both arms.
    for name, m in (("baseline", base), ("poison", poison)):
        if m["agreement"]["disagree"]:
            raise GateError(f"{name}: wire and command pairings disagree on "
                            f"{len(m['agreement']['disagree'])} single-exchange turns (G-C)")

    fired = (poison["command_pairing"]["c6_consecutive_turn_repeats"] > 0
             and poison["command_pairing"]["c5_repeats_within_window"] > 0)
    baseline_clean = base["command_pairing"]["c6_consecutive_turn_repeats"] == 0
    verdict = "PASS" if fired and baseline_clean else "FAIL"

    report = {
        "control": "C-7 -- C-5/C-6 inertness against a gutted-predicate poison arm",
        "task": "20260825-dance-cure-candidate-2-swap",
        "window_turns": WINDOW,
        "poison_arm": str(POISON.relative_to(REPO)),
        "poison_deletions": [
            "P1 clause 4's prev_cells standing memory -- the only cross-turn memory in the "
            "predicate, and the only thing that can refuse an immediate back-swap",
            "P2 clause 5's adjacency test",
            "P3 clause 6, both halves: teammate-on-goal and the strictly-beyond BFS test"],
        "poison_retentions": [
            "R1 !moving_ids / !displaced -- per-pass locals with no memory across turns, so "
            "neither can suppress the next turn's back-swap; kept so one pass cannot rewrite a "
            "unit's command twice and make the stream malformed instead of looping",
            "R2 the positional slot map -- the mechanism that writes the partner's command"],
        "counting_shape": (
            "paired from the COMMAND STREAM against the referee's pre-turn cells: {a,b} is an "
            "exchange iff dest(a)==cell(b) and dest(b)==cell(a). Unambiguous at any sw, so a "
            "multi-exchange poison turn is counted as FIRED, never reported as AMBIGUOUS."),
        "gates": {
            "G-P pairing completeness": f"PASS -- command pairs == sw and == the S/X units on "
                                        f"all {base['turns'] + poison['turns']} turns of both arms",
            "G-B panel identity": (f"PASS -- {len(panel_keys)} panel games reproduce their "
                                   f"panel-swap-census.json exchange counts on the unpoisoned "
                                   f"arm") if args.panel else "NOT RUN -- fixtures only",
            "G-B baseline identity": (f"PASS -- {base_fixtures['exchanges']} exchanges on "
                                      f"{len(published['pairs'])} pairs, identical to "
                                      f"{PUBLISHED.relative_to(REPO)}") if full_run else
                                     f"NOT RUN -- subset run (--only {args.only})",
            "G-C wire/command agreement": f"PASS -- {base['agreement']['agree']} baseline and "
                                          f"{poison['agreement']['agree']} poison single-exchange "
                                          f"turns, 0 disagreements"},
        "baseline_fixtures_only": {k: v for k, v in base_fixtures.items()
                                   if k not in ("incidental_rows",)},
        "baseline": base,
        "poison": poison,
        "subset": args.only,
        "population": (f"{len(sits)} fixtures" + (f" + {len(panel_keys)} panel games"
                                                  if args.panel else "")),
        "verdict": verdict,
        "meaning": (
            "C-5 and C-6 are not inert: a predicate that exchanges on every block makes both "
            "counters positive on the same fixtures where the candidate leaves C-6 at 0."
            if verdict == "PASS" else
            "the poison did not move both counters -- the zero on the candidate arm remains "
            "unproven as a measurement"),
        "not_proven_here": (
            "that the candidate's C-5 = 5 is benign. C-7 measures only that the counters can "
            "count; the pre-committed STOP AND ASK on those five repeats stands and is the "
            "owner's ruling to make."),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")

    for name, m in (("baseline", base), ("poison  ", poison)):
        cp, wp = m["command_pairing"], m["wire_pairing"]
        print(f"  {name}: {m['exchanges']} exchanges on {m['exchange_turns']} turns  "
              f"| commands: C-6 {cp['c6_consecutive_turn_repeats']}  "
              f"C-5 {cp['c5_repeats_within_window']}  "
              f"| wire: paired {wp['exchanges_paired']}, ambiguous turns "
              f"{wp['ambiguous_turns']} (lost {wp['exchanges_lost_to_ambiguity']}), "
              f"as-published verdict {wp['verdict_as_published']}")
    print(f"  C-7 -> {verdict}")
    print(f"  -> {OUT.relative_to(REPO)}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except GateError as exc:
        print(f"GATE FAILURE: {exc}", file=sys.stderr)
        sys.exit(2)
