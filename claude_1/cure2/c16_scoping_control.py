#!/usr/bin/env python3
"""C-16 -- the R-B red half: is the orchard scoping doing work, or is it decoration?

G-0 §9 (`claude_1/cure2/definitions-g0-2026-08-25.md`): *C-16 -- R-B red half:
`SWAP_P3_SCOPING_ENABLED=false` on an identical orchard-eligible map. P3 fires => the scoping is
doing work, not decoration.*

§3.6 adopts R-B verbatim and states the cost in plain words: on a seat view satisfying the base's
`orchard_eligible` predicate the exchange is inert for the WHOLE game, so dances on
orchard-eligible maps are untouched by Candidate 2. A cost paid to avoid a property violation is
only a real cost if the violation is real. C-16 pays nothing and checks: flip that ONE line, keep
the map, the seat, the seeds, the opponent and the referee identical, and grade P3 with
`fuzz_panel.eval_p3` -- the panel's own function, imported, not restated.

Two halves on the same 12 games:

  GREEN  `arm-candidate.rs`  (scoping ON)   -- P3 must be 0 on every orchard-eligible game.
  RED    `arm-c16noscope.rs` (scoping OFF)  -- P3 must fire on at least one of them.

A green half alone proves nothing (a rule that never fires anywhere is also green); a red half
alone proves nothing (P3 could be firing for a reason that is not the exchange). The pair is the
control, and the gates below are what tie the red half's divergence to an exchange rather than to
the flip in general.

GATES -- each aborts the run rather than degrading the number:

  G-1L  one-line arms. Both scoping-off arms differ from their source arm in exactly one line,
        and that line is the scoping flag (checked by `make_c16_noscope_arms.py`, re-checked here
        against the recorded manifest and the on-disk bytes).
  G-E   population identity. The graded games are exactly the rows of
        `results/panel-swap-census.json` with `orchard_eligible` true, and the panel's own
        regenerated specs agree game for game.
  G-B   green-half identity. On the scoping-ON arm every graded game reproduces its recorded
        census exchange count (0 by construction of the scoping) -- so the two arms are being
        compared on the recorded population, not a re-drawn one.
  G-I   in-play identity of the two red arms. The narrate-ON attributing arm and the narrate-OFF
        graded arm must be identical in play (MSG stripped) on every graded game. Only then may
        the `sw=` wire of the first explain the divergence of the second.
  G-A   attribution. On every game where the red half's P3 fires, the first P3 divergence turn
        must equal the first turn on which the wire granted an exchange (`sw>0`). If a divergence
        starts before any exchange, the flip changed something other than the exchange and the
        run aborts instead of claiming a fire.
  G-N   off-class inertness. On the non-eligible games that DO carry exchanges, the scoping-off
        arm must be byte-identical to the scoping-ON arm: the flag is allowed to change behaviour
        only on maps the predicate selects. Without this, "P3 fires with the flag off" could be a
        statement about the flag rather than about the scoping.

VERDICT.  C-16 PASSES iff the green half is 0 on every graded game AND the red half fires on at
least one of them with the exchange attribution above. C-16 FAILS -- and the honest report is
"the scoping is decoration ON THIS CORPUS" -- if the red half never fires.

PRE-COMMITTED EXTENSION.  The primary population is 12 games; it may simply be too small to
contain a fire. `cure2-c16-extension-config.json` was written BEFORE this run and declares the
enlargement: 48 maps of class `orchard_eligible` only, same referee, same seeds, same turn budget,
same opponent mix. It is used only if the primary population produces no exchange on the red half,
and either outcome is published.

    python3 claude_1/cure2/c16_scoping_control.py [--extend] [--only m004:0,...]
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

import fuzz_panel as fp               # noqa: E402
import regression_tests as rt         # noqa: E402
import semantic_harness as sh         # noqa: E402
import narrate5 as n5                 # noqa: E402

CANDIDATE = HERE / "arm-candidate.rs"
NOSCOPE = HERE / "arm-c16noscope.rs"
NOSCOPE_INSTR = HERE / "arm-c16noscope-instrument.rs"
INSTR = HERE / "arm-instrument.rs"
ARM_MANIFEST = HERE / "c16-arm-manifest.json"
PANEL_CFG = HERE / "cure2-instrument-config.json"
EXT_CFG = HERE / "cure2-c16-extension-config.json"
CENSUS = HERE / "results" / "panel-swap-census.json"
OUT = HERE / "results" / "c16-scoping-control.json"
SCOPING_LINE = "            const SWAP_P3_SCOPING_ENABLED:bool="


class GateError(Exception):
    """Anything that would make the number below mean something other than it says."""


def one_line_gate():
    """G-1L, re-checked here from the bytes rather than trusted from the manifest."""
    manifest = json.loads(ARM_MANIFEST.read_text())
    rows = {}
    for arm, source in ((NOSCOPE, CANDIDATE), (NOSCOPE_INSTR, INSTR)):
        a, b = arm.read_text().split("\n"), source.read_text().split("\n")
        if len(a) != len(b):
            raise GateError(f"{arm.name}: {len(a)} lines against {source.name}'s {len(b)} (G-1L)")
        diff = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
        if len(diff) != 1:
            raise GateError(f"{arm.name}: {len(diff)} lines differ from {source.name}, "
                            f"expected 1 (G-1L)")
        i = diff[0]
        if not (b[i] == SCOPING_LINE + "true;" and a[i] == SCOPING_LINE + "false;"):
            raise GateError(f"{arm.name}: the differing line is not the scoping flag: "
                            f"{b[i]!r} -> {a[i]!r} (G-1L)")
        entry = manifest["arms"].get(arm.name, {})
        rows[arm.name] = {"from_arm": source.name, "differing_line_index": i,
                          "was": b[i].strip(), "now": a[i].strip(),
                          "sha256": entry.get("sha256")}
    return rows


def wire_rows(commands):
    """Per-turn `sw` off the v5 wire of the attributing arm."""
    rows = []
    for t, line in enumerate(commands.rstrip("\n").split("\n"), 1):
        frags = n5.msg_fragments(line)
        if len(frags) != 1:
            raise GateError(f"turn {t}: {len(frags)} MSG fragments on the attributing arm")
        _turn, _units, _order, _banner, meta = n5.decode(frags[0].strip())
        rows.append({"turn": t, "sw": meta["sw"], "so": meta["so"], "sn": meta["sn"],
                     "sf": meta["sf"]})
    return rows


def in_play(commands):
    return [n5.strip_msg(l) for l in commands.rstrip("\n").split("\n")]


def run(binary, spec, turns):
    ref = fp.make_referee(spec)
    _transcript, commands = rt.run_binary_custom(Path(binary), ref, turns)
    return commands, fp.score(ref.inv) - fp.score(ref.opp_inv)


def grade(key, spec, turns, bins):
    """One graded game: both halves, the attribution wire, and every per-game gate."""
    parent_cmds, parent_margin = run(bins["parent"], spec, turns)
    scoped_cmds, scoped_margin = run(bins["scoped"], spec, turns)
    red_cmds, red_margin = run(bins["red"], spec, turns)
    wire_cmds, _wire_margin = run(bins["red_instr"], spec, turns)

    # G-I: the attributing arm and the graded arm are the same game in play.
    if in_play(wire_cmds) != in_play(red_cmds):
        first = next((t for t, (a, b) in enumerate(zip(in_play(wire_cmds), in_play(red_cmds)), 1)
                      if a != b), None)
        raise GateError(f"{key}: the narrate-on and narrate-off scoping-off arms differ in play, "
                        f"first at turn {first} (G-I)")

    green = fp.eval_p3(True, scoped_cmds, parent_cmds)
    red = fp.eval_p3(True, red_cmds, parent_cmds)
    wire = wire_rows(wire_cmds)
    exchange_turns = [r["turn"] for r in wire if r["sw"] > 0]
    exchanges = sum(r["sw"] for r in wire)

    # G-A: a red fire must start exactly where the first exchange was granted.
    if red:
        first_div = red[0]["first_divergence_turn"]
        if not exchange_turns:
            raise GateError(f"{key}: P3 fires with the scoping off but the wire granted no "
                            f"exchange -- the divergence is not the exchange's (G-A)")
        if first_div != exchange_turns[0]:
            raise GateError(f"{key}: first P3 divergence at turn {first_div} but the first "
                            f"exchange was granted on turn {exchange_turns[0]} (G-A)")
    return {
        "game": key, "class": spec["class"], "seat": spec["seat"], "turns": turns,
        "green_p3_violations": len(green), "green_p3": green,
        "red_p3_violations": len(red), "red_p3": red,
        "red_exchanges": exchanges, "red_exchange_turns": exchange_turns[:20],
        "red_refusals": {"so": sum(r["so"] for r in wire), "sn": sum(r["sn"] for r in wire),
                         "sf": sum(r["sf"] for r in wire)},
        "parent_margin": parent_margin, "scoped_margin": scoped_margin,
        "red_margin": red_margin,
        "red_minus_scoped_margin": red_margin - scoped_margin,
        "scoped_identical_to_parent": scoped_cmds == parent_cmds,
    }


def off_class_gate(jobs, census_rows, bins):
    """G-N: on the non-eligible games that carry exchanges, the flag must change nothing."""
    keys = [r["game"] for r in census_rows
            if r["swaps"] > 0 and not r["orchard_eligible"]]
    checked, differing = [], []
    for key in keys:
        job = jobs[key]
        scoped, _m = run(bins["scoped"], job["spec"], job["turns"])
        red, _m2 = run(bins["red"], job["spec"], job["turns"])
        same = scoped == red
        checked.append({"game": key, "identical": same, "census_swaps":
                        next(r["swaps"] for r in census_rows if r["game"] == key)})
        if not same:
            differing.append(key)
    if differing:
        raise GateError(f"the scoping flag changed {len(differing)} non-eligible games "
                        f"{differing[:5]} -- it is not confined to the predicate's class (G-N)")
    return {"games": len(checked), "identical": sum(1 for c in checked if c["identical"]),
            "rows": checked}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--only")
    ap.add_argument("--extend", action="store_true",
                    help="run the pre-declared 48-map orchard-eligible-only extension population "
                         "as well (used when the primary 12 produce no exchange)")
    ap.add_argument("--no-off-class", action="store_true",
                    help="skip G-N (a subset debug run; the gate is reported NOT RUN)")
    args = ap.parse_args()

    arms = one_line_gate()
    census = json.loads(CENSUS.read_text())
    census_rows = census["rows"]
    cfg = fp.load_config(PANEL_CFG)

    with tempfile.TemporaryDirectory(prefix="cure2-c16-") as wd:
        wd = Path(wd)
        bins = {}
        for name, src, crate in (("parent", (PANEL_CFG.parent /
                                             cfg["parent"]["source"]).resolve(),
                                  "cure2_parent_c16"),
                                 ("scoped", CANDIDATE, "cure2_scoped_c16"),
                                 ("red", NOSCOPE, "cure2_red_c16"),
                                 ("red_instr", NOSCOPE_INSTR, "cure2_red_instr_c16")):
            bins[name] = wd / f"{name}.bin"
            sh.compile_text(Path(src).read_text(), bins[name], crate=crate)
        print("  four arms compiled (parent, scoped, red, red-attributing)", flush=True)

        jobs = {f"{j['spec']['map_id']}:{j['spec']['seat']}": j
                for j in fp.build_jobs(cfg, bins["scoped"], bins["parent"])}

        # G-E: the graded population is the census's own orchard-eligible set, and the
        # regenerated specs agree with it game for game.
        census_eligible = [r["game"] for r in census_rows if r["orchard_eligible"]]
        spec_eligible = [k for k, j in jobs.items() if j["spec"]["orchard_eligible"]]
        if sorted(census_eligible) != sorted(spec_eligible):
            raise GateError(f"census names {len(census_eligible)} orchard-eligible games, the "
                            f"regenerated specs name {len(spec_eligible)} (G-E)")
        graded = census_eligible
        if args.only:
            wanted = set(args.only.split(","))
            graded = [g for g in graded if g in wanted]
        print(f"  {len(graded)} orchard-eligible games", flush=True)

        rows = []
        for i, key in enumerate(graded, 1):
            job = jobs[key]
            rows.append(grade(key, job["spec"], job["turns"], bins))
            print(f"    {key}  green P3 {rows[-1]['green_p3_violations']}  "
                  f"red P3 {rows[-1]['red_p3_violations']}  "
                  f"red exchanges {rows[-1]['red_exchanges']}", flush=True)

        # G-B: the green half reproduces the recorded exchange counts of the census.
        by_game = {r["game"]: r for r in census_rows}
        bad = [r["game"] for r in rows
               if by_game[r["game"]]["swaps"] != 0 or not r["scoped_identical_to_parent"]]
        if bad and not args.only:
            raise GateError(f"green half does not reproduce the census on {bad[:5]} (G-B)")

        off_class = None
        if not args.no_off_class and not args.only:
            print("  G-N: off-class inertness on the exchange-bearing non-eligible games",
                  flush=True)
            off_class = off_class_gate(jobs, census_rows, bins)
            print(f"    {off_class['identical']}/{off_class['games']} byte-identical", flush=True)

        ext_rows = []
        red_fires = [r for r in rows if r["red_p3_violations"] > 0]
        if args.extend or (not red_fires and not args.only):
            print("  extension population (pre-declared, "
                  f"{EXT_CFG.name})", flush=True)
            ecfg = fp.load_config(EXT_CFG)
            ejobs = fp.build_jobs(ecfg, bins["red"], bins["parent"])
            elig = [j for j in ejobs if j["spec"]["orchard_eligible"]]
            print(f"    {len(elig)} eligible seat views of {len(ejobs)} generated", flush=True)
            for i, job in enumerate(elig, 1):
                key = f"x{job['spec']['map_id']}:{job['spec']['seat']}"
                ext_rows.append(grade(key, job["spec"], job["turns"], bins))
                if i % 8 == 0:
                    print(f"    extension {i}/{len(elig)}", flush=True)

    all_rows = rows + ext_rows
    red_fires = [r for r in all_rows if r["red_p3_violations"] > 0]
    green_fires = [r for r in all_rows if r["green_p3_violations"] > 0]
    verdict = "PASS" if (red_fires and not green_fires) else "FAIL"

    report = {
        "control": "C-16 -- R-B red half: is the orchard scoping doing work or decoration?",
        "task": "20260825-dance-cure-candidate-2-swap",
        "arms": arms,
        "graded_primary": graded,
        "extension_used": bool(ext_rows),
        "extension_config": str(EXT_CFG.relative_to(REPO)),
        "gates": {
            "G-1L one-line arms": "PASS -- both scoping-off arms differ from their source arm in "
                                  "exactly the scoping flag line",
            "G-E population identity": f"PASS -- {len(census_eligible)} orchard-eligible games, "
                                       f"census and regenerated specs agree game for game"
                                       + (f" (subset run: --only {args.only})" if args.only
                                          else ""),
            "G-B green-half identity": ("PASS -- every graded game reproduces its census "
                                        "exchange count of 0 and is byte-identical to the parent"
                                        if not args.only else
                                        f"NOT RUN -- subset run (--only {args.only})"),
            "G-I red-arm in-play identity": f"PASS -- the narrate-on attributing arm and the "
                                            f"narrate-off graded arm are identical in play on all "
                                            f"{len(all_rows)} graded games",
            "G-A attribution": (f"PASS -- on all {len(red_fires)} firing games the first P3 "
                                f"divergence turn is the first turn the wire granted an exchange"
                                if red_fires else "VACUOUS -- the red half never fired"),
            "G-N off-class inertness": (f"PASS -- {off_class['identical']}/{off_class['games']} "
                                        f"exchange-bearing non-eligible games byte-identical "
                                        f"between the scoping-on and scoping-off arms"
                                        if off_class else "NOT RUN"),
        },
        "green_half": {
            "arm": "arm-candidate.rs (SWAP_P3_SCOPING_ENABLED=true)",
            "games": len(all_rows), "p3_firing_games": len(green_fires),
            "p3_violations": sum(r["green_p3_violations"] for r in all_rows),
        },
        "red_half": {
            "arm": "arm-c16noscope.rs (SWAP_P3_SCOPING_ENABLED=false)",
            "games": len(all_rows), "p3_firing_games": len(red_fires),
            "p3_violations": sum(r["red_p3_violations"] for r in all_rows),
            "exchanges": sum(r["red_exchanges"] for r in all_rows),
            "games_with_an_exchange": sum(1 for r in all_rows if r["red_exchanges"] > 0),
            "net_margin_delta_against_the_scoped_arm":
                sum(r["red_minus_scoped_margin"] for r in all_rows),
        },
        "off_class_inertness": off_class,
        "rows": all_rows,
        "verdict": verdict,
        "meaning": (
            "the scoping is doing work: with the one line flipped, the same maps, seats, seeds "
            "and opponent produce P3 violations that the scoped arm does not produce, and each "
            "one begins on the turn an exchange was granted. The whole-game inertness on "
            "orchard-eligible maps is a paid cost, not decoration."
            if verdict == "PASS" else
            "on this corpus the scoping is DECORATION: with it off, the exchange never changed a "
            "command stream on an orchard-eligible map, so no P3 violation was avoided by "
            "switching the rule off there. The cost stated in §3.6 is still paid -- dances on "
            "those maps are untouched -- but nothing measured here is bought with it."),
        "not_proven_here": (
            "that P3 would fire on every orchard-eligible map, or that the scoped arm is "
            "P3-neutral by any argument other than whole-game inertness. C-16 measures the "
            "scoping's effect on the corpus it was run on and nothing wider."),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"  green half: {len(green_fires)} of {len(all_rows)} games with a P3 violation")
    print(f"  red half:   {len(red_fires)} of {len(all_rows)} games with a P3 violation, "
          f"{report['red_half']['exchanges']} exchanges")
    print(f"  C-16 -> {verdict}")
    print(f"  -> {OUT.relative_to(REPO)}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except GateError as exc:
        print(f"GATE FAILURE: {exc}", file=sys.stderr)
        sys.exit(2)
