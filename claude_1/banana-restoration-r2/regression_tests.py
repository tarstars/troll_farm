#!/usr/bin/env python3
"""RED-phase regression checks R-1 / R-2 for the banana-restoration-r2 task.

Two named regression checks, implemented as pure trace analyses over the
(transcript, commands) pair produced by the mini-referee of
``make_banana_traces.py`` (or any byte-compatible trace):

  R-1 "one-seed-reservation"      -> invariant I-9  (surplus rule)
  R-2 "unripe-contested-response" -> invariant I-10a (ownership-loss response)

Both are runnable from the CLI against any candidate binary (or source, which
is then compiled) and R-1 additionally in trace-file mode against an existing
committed trace. The checks were built to FAIL on the rejected candidate
``candidate-banana-r2.min.rs`` (SHA-256 f29efd0e...) for the reasons given in
the host review, and to PASS on compliant synthetic control traces (see the
``controls`` subcommand), so they are falsifiable in both directions.

Usage:
  regression_tests.py r1-trace --transcript F --commands F
  regression_tests.py r1-bin  (--binary F | --source F)   # runs t1 lifecycle
  regression_tests.py r2-bin  (--binary F | --source F)   # runs t3/t4 dynamic
  regression_tests.py controls                            # compliant traces
  regression_tests.py all     (--binary F | --source F)   # everything above

Exit code 0 iff every requested check reports PASS (for ``controls``: iff the
compliant synthetic traces PASS, i.e. the checks are not vacuous-always-FAIL).

Deterministic, stdlib only. This module never modifies the candidate, the
harness fixtures, the detectors, or the committed traces.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import semantic_harness as sh            # noqa: E402  (compiler)
import trace_detectors as td             # noqa: E402  (trace parser / BFS)
import make_banana_traces as mbt         # noqa: E402  (referees + scenarios)

BANANA = 3          # carry/inventory slot of BANANA
BIG = 10 ** 6


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def resident_id(tr: td.Trace) -> int:
    """The resident = the starter = min-id own unit at turn 1 (spec B3:
    'the starter (min-id unit at turn 1) ... is the resident and performs
    all banana work')."""
    return min(u.id for u in tr.state(1).own_units())


def dist_map_to(tr: td.Trace, cell):
    """BFS distance map toward ``cell`` over the walkable set (plus the cell
    itself, which on the trace maps is walkable anyway)."""
    walk = set(tr.smap.walkable) | {cell}
    return td.bfs_distances(walk, [cell])


def travel_eta(dist_map, cell, speed) -> int:
    d = dist_map.get(cell)
    if d is None:
        return BIG
    return td.ceil_div(d, max(speed, 1))


def ownership_flip_turn(tr: td.Trace, mother, opp_id):
    """First turn t at which I-7 ownership of the mother cell is false:
    NOT (eta_res(c,t) < eta_opp_h(c,t)) with strict inequality, ties treated
    as not owned ('ties are treated as not owned', I-7). Returns
    (t, eta_res, eta_opp) or None if ownership never flips in the trace."""
    rid = resident_id(tr)
    dmap = dist_map_to(tr, mother)
    for t in range(1, tr.T + 1):
        res = tr.unit(rid, t)
        opp = tr.unit(opp_id, t)
        if res is None or opp is None:
            continue
        eta_res = travel_eta(dmap, res.cell, res.speed)
        eta_opp = travel_eta(dmap, opp.cell, opp.speed)
        if not (eta_res < eta_opp):
            return t, eta_res, eta_opp
    return None


# ---------------------------------------------------------------------------
# R-1 "one-seed-reservation" (targets I-9)
# ---------------------------------------------------------------------------

def r1_one_seed_reservation(tr: td.Trace) -> dict:
    """R-1 "one-seed-reservation" — regression check for invariant I-9.

    Spec language (invariant-spec-2026-08-04.md, B3):

      "I-9 (surplus rule). Replant demand (an empty eligible Ring cell
      within horizon I-5) has priority for at most one carried seed; every
      additional carried banana is surplus and must be on a bank path
      (monotone door approach as in I-19, then DROP)."

    and its ambiguity resolution: "bank vs replant priority? -> Resolve: I-9
    (one seed for replant, rest banked)."

    Derived trace predicate: replant may reserve AT MOST ONE carried banana.
    The moment the resident's banana carry exceeds 1, everything beyond one
    seed is surplus and must reach the bank (a DROP issued at a door) before
    it may be spent on planting. Therefore a *surplus window* opens at the
    first turn t with carry(t) > 1 and closes only when the resident banks
    (issues DROP while standing on a door cell) or the carried bananas are
    gone. Every ``PLANT <resident> BANANA`` issued while the window is open
    is a violation: it means harvested seeds are being replanted beyond the
    one-seed reservation with no intervening bank of the surplus. This is
    exactly the rejected candidate's committed t55-t61 lifecycle pattern
    (harvest x2 at t55/56, carry 2 at t57, PLANT at t58 and t61, first DROP
    only at t79).

    FAIL iff at least one such PLANT exists. Reported per violation: the
    turn, the resident's banana carry before the command, and the turn the
    unbanked-surplus window opened.
    """
    rid = resident_id(tr)
    violations = []
    banks = []
    window_open = False
    window_since = None
    for t in range(1, tr.T + 1):
        unit = tr.unit(rid, t)
        if unit is None:
            continue
        carry = unit.carry[BANANA]
        if carry > 1:
            if not window_open:
                window_open = True
                window_since = t
        elif carry == 0:
            window_open = False
            window_since = None
        cmd = tr.cmd_of(rid, t)
        if cmd is None:
            continue
        if (cmd.verb == "PLANT" and cmd.args and cmd.args[0] == "BANANA"
                and window_open):
            violations.append({
                "turn": t,
                "carry_before": carry,
                "surplus_since_turn": window_since,
            })
        if cmd.verb == "DROP" and unit.cell in tr.doors:
            banks.append(t)
            window_open = False
            window_since = None
    return {
        "check": "R-1 one-seed-reservation",
        "invariant": "I-9",
        "resident": rid,
        "verdict": "FAIL" if violations else "PASS",
        "violations": violations,
        "bank_turns": banks[:20],
    }


# ---------------------------------------------------------------------------
# R-2 "unripe-contested-response" (targets I-10a)
# ---------------------------------------------------------------------------

R2_DOC = """Spec language (invariant-spec-2026-08-04.md, B4):

  "I-10a (dynamic ownership-loss response ...). If ownership of a live own
  banana asset is lost after plant time (I-7 flips false at some t through
  opponent movement), the resident responds deterministically at the first
  such t: if a ripe fruit is harvestable immediately, harvest now; otherwise
  convert (chop at current size, orthogonal arithmetic of B2) iff the
  conversion completes strictly before eta_opp, else abandon (no further
  commands invested in the asset)."
"""


def r2_abandon(tr: td.Trace, mother=None, opp_id=5) -> dict:
    """R-2 variant A "unripe-contested-abandon" — regression check for I-10a.

    Scenario contract (t3_abandon): the mother is UNRIPE at the ownership
    flip and conversion is impossible (travel + ceil(health/chop_power)
    chop turns cannot complete strictly before the opponent's earliest
    harvest), so I-10a requires the Abandoned transition: "no further
    commands invested in the asset". FAIL if after the flip turn the
    resident keeps investing: any MOVE targeted at the mother cell, any
    PLANT, or any HARVEST/CHOP while standing on the mother cell.
    """ + R2_DOC
    mother = mother or mbt.MOTHER_CELL
    rid = resident_id(tr)
    flip = ownership_flip_turn(tr, mother, opp_id)
    if flip is None:
        return {"check": "R-2a unripe-contested-abandon", "invariant": "I-10a",
                "verdict": "ERROR",
                "reason": "scenario invalid: ownership never flips"}
    flip_t, eta_res, eta_opp = flip
    st = tr.state(flip_t)
    plant = st.plant_at(mother)
    unripe_at_flip = plant is not None and plant.fruits == 0
    violations = []
    for t in range(flip_t, tr.T + 1):
        unit = tr.unit(rid, t)
        cmd = tr.cmd_of(rid, t)
        if unit is None or cmd is None:
            continue
        if cmd.verb == "MOVE" and cmd.args and cmd.args[0] == mother:
            violations.append({"turn": t, "command": cmd.raw,
                               "why": "MOVE toward the lost mother"})
        elif cmd.verb == "PLANT":
            violations.append({"turn": t, "command": cmd.raw,
                               "why": "PLANT after ownership flip"})
        elif cmd.verb in ("HARVEST", "CHOP") and unit.cell == mother:
            violations.append({"turn": t, "command": cmd.raw,
                               "why": cmd.verb + " on the lost mother"})
    return {
        "check": "R-2a unripe-contested-abandon",
        "invariant": "I-10a",
        "resident": rid,
        "mother": list(mother),
        "flip_turn": flip_t,
        "eta_res_at_flip": eta_res,
        "eta_opp_at_flip": eta_opp,
        "unripe_at_flip": unripe_at_flip,
        "verdict": "FAIL" if violations else "PASS",
        "violations": violations,
    }


def r2_convert(tr: td.Trace, mother=None, opp_id=5) -> dict:
    """R-2 variant B "unripe-contested-convert" — regression check for I-10a.

    Scenario contract (t4_convert): the mother is UNRIPE at the ownership
    flip and conversion IS possible — the chop (travel eta_res plus
    ceil(health/chop_power) chop turns) completes strictly before eta_opp,
    the opponent's earliest possible harvest of the asset, which for an
    unripe mother is bounded below by its ripening time max(travel, ripen).
    I-10a then requires "convert (chop at current size)". FAIL if the
    resident never begins the conversion: no CHOP issued while standing on
    the mother cell at any turn of the trace.
    """ + R2_DOC
    mother = mother or mbt.MOTHER_CELL
    rid = resident_id(tr)
    flip = ownership_flip_turn(tr, mother, opp_id)
    if flip is None:
        return {"check": "R-2b unripe-contested-convert", "invariant": "I-10a",
                "verdict": "ERROR",
                "reason": "scenario invalid: ownership never flips"}
    flip_t, eta_res, eta_opp = flip
    # Conversion-feasibility report at the first not-owned turn.
    feas = None
    for t in range(1, tr.T + 1):
        st = tr.state(t)
        plant = st.plant_at(mother)
        res = tr.unit(rid, t)
        opp = tr.unit(opp_id, t)
        if plant is None or res is None or opp is None:
            continue
        dmap = dist_map_to(tr, mother)
        e_res = travel_eta(dmap, res.cell, res.speed)
        e_opp = travel_eta(dmap, opp.cell, opp.speed)
        if e_res < e_opp:
            continue
        chop_turns = td.ceil_div(plant.health, max(res.chop_power, 1))
        ripen = 0 if plant.fruits > 0 else plant.cooldown
        opp_earliest_harvest = max(e_opp, ripen)
        feas = {
            "turn": t,
            "chop_completes_by": e_res + chop_turns,
            "opp_earliest_harvest": opp_earliest_harvest,
            "conversion_possible":
                e_res + chop_turns < opp_earliest_harvest,
        }
        break
    chops = []
    for t in range(1, tr.T + 1):
        unit = tr.unit(rid, t)
        cmd = tr.cmd_of(rid, t)
        if (unit is not None and cmd is not None and cmd.verb == "CHOP"
                and unit.cell == mother and tr.state(t).plant_at(mother)):
            chops.append(t)
    return {
        "check": "R-2b unripe-contested-convert",
        "invariant": "I-10a",
        "resident": rid,
        "mother": list(mother),
        "flip_turn": flip_t,
        "eta_res_at_flip": eta_res,
        "eta_opp_at_flip": eta_opp,
        "feasibility_at_flip": feas,
        "chop_turns_on_mother": chops[:20],
        "verdict": "PASS" if chops else "FAIL",
        "violations": [] if chops else [
            {"why": "conversion was possible but no CHOP on the mother "
                    "cell was ever issued (candidate falls through to "
                    "normal investment / waiting instead of converting)"}],
    }


# ---------------------------------------------------------------------------
# Trace production (no writes into traces/)
# ---------------------------------------------------------------------------

def run_binary(binary: Path, referee, turns: int):
    """Closed-loop run of a compiled candidate against a referee instance.
    Same protocol as make_banana_traces.run_scenario but writes no files;
    returns (transcript_text, commands_text)."""
    header = f"{len(mbt.MAP[0])} {len(mbt.MAP)}\n" + "\n".join(mbt.MAP) + "\n"
    transcript_parts = [header]
    command_lines = []
    with subprocess.Popen(
        [str(binary)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        text=True,
    ) as proc:
        proc.stdin.write(header)
        proc.stdin.flush()
        for _ in range(turns):
            block = referee.turn_text()
            transcript_parts.append(block)
            proc.stdin.write(block)
            proc.stdin.flush()
            line = proc.stdout.readline()
            if not line:
                raise RuntimeError("candidate closed stdout early")
            line = line.rstrip("\n")
            command_lines.append(line)
            referee.apply(line)
            referee.grow()
        proc.stdin.close()
    return "".join(transcript_parts), "\n".join(command_lines) + "\n"


def run_scripted(referee, policy, turns: int):
    """Closed-loop run of a Python turn policy (turn, referee) -> command
    line. Used for the compliant synthetic control traces."""
    header = f"{len(mbt.MAP[0])} {len(mbt.MAP)}\n" + "\n".join(mbt.MAP) + "\n"
    transcript_parts = [header]
    command_lines = []
    for turn in range(1, turns + 1):
        transcript_parts.append(referee.turn_text())
        line = policy(turn, referee)
        command_lines.append(line)
        referee.apply(line)
        referee.grow()
    return "".join(transcript_parts), "\n".join(command_lines) + "\n"


def build(transcript, commands) -> td.Trace:
    return td.build_trace(transcript, commands)


# ---------------------------------------------------------------------------
# Compliant synthetic control traces (near-miss controls)
# ---------------------------------------------------------------------------

def control_r1():
    """Near-miss control for R-1: the resident harvests TWO bananas (carry
    exceeds 1, the surplus window opens), then banks at a door (DROP)
    BEFORE any replant, then harvests one seed and plants it with carry
    exactly 1. Compliant with I-9, so R-1 must PASS."""
    referee = mbt.Referee(
        inventory=[0, 0, 0, 0, 0, 0],
        plants={(2, 2): {"kind": "BANANA", "size": 4, "health": 6,
                         "fruits": 3, "cd": 6}},
        units={
            0: mbt.unit_row(0, 0, (2, 2), cap=2, harvest=1, chop=1),
            1: mbt.unit_row(1, 0, (11, 3), cap=1, harvest=0, chop=0),
            5: mbt.unit_row(5, 1, (13, 0), cap=2, harvest=1, chop=1),
        },
    )
    script = {
        1: "HARVEST 0;WAIT",       # carry 1
        2: "HARVEST 0;WAIT",       # carry 2 -> surplus window opens
        3: "MOVE 0 2 1;WAIT",      # monotone door approach
        4: "DROP 0;WAIT",          # bank at the (2,1) door -> window closes
        5: "MOVE 0 2 2;WAIT",
        6: "HARVEST 0;WAIT",       # carry 1 (the one-seed reservation)
        7: "MOVE 0 1 2;WAIT",
        8: "PLANT 0 BANANA;WAIT",  # replant with carry == 1: compliant
        9: "WAIT",
        10: "WAIT",
    }
    return run_scripted(referee, lambda t, _r: script.get(t, "WAIT"), 10)


def control_r2_abandon():
    """Near-miss control for R-2a: same t3_abandon dynamic scenario, but the
    resident abandons at (indeed before) the flip: it retreats to the bank
    door and idles — no MOVE targeted at the mother, no PLANT, no
    HARVEST/CHOP on the mother. Compliant with I-10a, so R-2a must PASS."""
    referee = mbt.scenario_t3_abandon()
    script = {1: "MOVE 0 1 2;WAIT", 2: "MOVE 0 1 2;WAIT",
              3: "MOVE 0 1 2;WAIT", 4: "MOVE 0 1 2;WAIT"}
    return run_scripted(referee, lambda t, _r: script.get(t, "WAIT"), 20)


def control_r2_convert():
    """Near-miss control for R-2b: same t4_convert dynamic scenario; the
    resident steps onto the mother and chops it down (health 2, chop 1:
    done by turn 3, strictly before the opponent's earliest harvest, which
    the 30-turn ripening bounds below). Compliant with I-10a convert, so
    R-2b must PASS."""
    referee = mbt.scenario_t4_convert()
    script = {1: "MOVE 0 2 2;WAIT", 2: "CHOP 0;WAIT", 3: "CHOP 0;WAIT",
              4: "MOVE 0 2 1;WAIT", 5: "DROP 0;WAIT"}
    return run_scripted(referee, lambda t, _r: script.get(t, "WAIT"), 20)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def compile_source(source_path: Path, workdir: Path) -> Path:
    binary = workdir / "rt_candidate"
    sh.compile_text(source_path.read_text(), binary, "rt_candidate")
    return binary


def emit(report: dict) -> bool:
    print(json.dumps(report, indent=1, sort_keys=True))
    return report.get("verdict") == "PASS"


def cmd_r1_trace(args) -> bool:
    tr = build(Path(args.transcript).read_text(),
               Path(args.commands).read_text())
    return emit(r1_one_seed_reservation(tr))


def cmd_r1_bin(binary: Path, outdir) -> bool:
    transcript, commands = run_binary(binary, mbt.scenario_t1(), 300)
    if outdir:
        Path(outdir, "r1-t1_lifecycle-transcript.txt").write_text(transcript)
        Path(outdir, "r1-t1_lifecycle-commands.txt").write_text(commands)
    return emit(r1_one_seed_reservation(build(transcript, commands)))


def cmd_r2_bin(binary: Path, outdir) -> bool:
    ok = True
    for name, factory, turns, checker in (
        ("t3_abandon", mbt.scenario_t3_abandon, 20, r2_abandon),
        ("t4_convert", mbt.scenario_t4_convert, 20, r2_convert),
    ):
        transcript, commands = run_binary(binary, factory(), turns)
        if outdir:
            Path(outdir, f"r2-{name}-transcript.txt").write_text(transcript)
            Path(outdir, f"r2-{name}-commands.txt").write_text(commands)
        ok = emit(checker(build(transcript, commands))) and ok
    return ok


def cmd_controls() -> bool:
    ok = True
    for label, (transcript, commands), checker in (
        ("control-r1-compliant", control_r1(), r1_one_seed_reservation),
        ("control-r2a-compliant", control_r2_abandon(), r2_abandon),
        ("control-r2b-compliant", control_r2_convert(), r2_convert),
    ):
        report = checker(build(transcript, commands))
        report["control"] = label
        ok = emit(report) and ok
    return ok


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["r1-trace", "r1-bin", "r2-bin",
                                         "controls", "all"])
    parser.add_argument("--transcript")
    parser.add_argument("--commands")
    parser.add_argument("--binary")
    parser.add_argument("--source")
    parser.add_argument("--outdir", help="optional directory for the raw "
                        "trace files produced by the binary modes")
    args = parser.parse_args(argv)
    if args.outdir:
        Path(args.outdir).mkdir(parents=True, exist_ok=True)

    if args.mode == "controls":
        return 0 if cmd_controls() else 1
    if args.mode == "r1-trace":
        if not (args.transcript and args.commands):
            parser.error("r1-trace requires --transcript and --commands")
        return 0 if cmd_r1_trace(args) else 1

    with tempfile.TemporaryDirectory(prefix="banana-rt-") as workdir:
        if args.binary:
            binary = Path(args.binary)
        elif args.source:
            binary = compile_source(Path(args.source), Path(workdir))
        else:
            parser.error(f"{args.mode} requires --binary or --source")
        ok = True
        if args.mode in ("r1-bin", "all"):
            ok = cmd_r1_bin(binary, args.outdir) and ok
        if args.mode in ("r2-bin", "all"):
            ok = cmd_r2_bin(binary, args.outdir) and ok
        if args.mode == "all":
            ok = cmd_controls() and ok
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
