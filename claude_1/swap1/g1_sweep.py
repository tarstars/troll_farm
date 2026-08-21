#!/usr/bin/env python3
r"""G-1 — inertness parity and the trigger measurements, over all 34 frozen fixtures.

Task `20260821-swap-r1-cure`, gate **G-1**. Three binaries per fixture, one game each:

- the **base** (`candidate-door1-pure-deletion.rs`, champion of record `547fa706…`),
- the **candidate** (`cgauto/submissions/candidate-swap-r1.rs`),
- the **probe** (the candidate plus instrumentation plus a verbatim SHADOW copy of the base's own
  seam function).

## The four things this measures, and why each needs its own check

1. **Probe parity.** The probe's command stream must equal the plain candidate's, byte for byte.
   Without that the instrumented run is a different bot and every row below is about something
   else. This is the same licence `coverage.check_parity` demands, and it is checked FIRST.

2. **Shadow inertness — every tick, including after a divergence.** Whole-game byte-identity only
   means something on a fixture where alpha never fires; after the first fire the two runs are
   different worlds, and a later difference is not evidence of anything. So on every tick the
   probe also runs the BASE's own function on a clone of the pre-resolve command vector and the
   same view, and reports whether the two agree. The G-1 claim — *a tick on which the trigger did
   not fire is byte-identical to the base's* — is then measured on **every tick of every
   fixture**, on the SAME input state. The gate is exact in both directions: `identical == False`
   iff a fire was recorded on that tick. A fire that left the stream identical would mean alpha
   emitted nothing; a difference without a fire would mean alpha is not inert.

3. **Pre-divergence whole-stream identity**, and on zero-fire fixtures whole-GAME identity: the
   coarse check, kept because it is the one a reviewer can reproduce without the probe at all.

4. **The trigger report.** Per fixture: fires, the T4(a)-before-detour split (the breadth of the
   one declared behaviour change, required by ruling 1), the T4(b) fires, the displaced verb and
   the turn `U` resumed it (required by the card: measured, not assumed), the re-swap detector
   (ruling 4: a repeated unordered pair within 4 ticks BLOCKS G-1), and the firing rate as a
   fraction of unit-turns.

**A zero total across the corpus FAILS the run.** An alpha that never fires would pass every
parity check above perfectly, which is the inert-check failure this programme has shipped before.

Run:  python3 claude_1/swap1/g1_sweep.py [--only OSC-005,OSC-012]
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
for p in ("claude_1/t1", "claude_1/hstarve1", "claude_1/banana-restoration-r2", "claude_1/pipeline"):
    sys.path.insert(0, str(REPO / p))
import coverage as C          # noqa: E402
import fixture_harness as H   # noqa: E402
import fuzz_panel as fp       # noqa: E402
import regression_tests as rt  # noqa: E402
import semantic_harness as sh  # noqa: E402

BASE = REPO / "cgauto/submissions/candidate-door1-pure-deletion.rs"
CANDIDATE = REPO / "cgauto/submissions/candidate-swap-r1.rs"
PROBE = HERE / "probe-swap-r1.rs"
OUT = HERE / "g1-sweep-2026-08-21.json"

RE_TURN = re.compile(r"^SW1TURN turn=(\d+) enabled=(\w+) own_units=(\d+)$")
RE_FIRE = re.compile(r"^SW1FIRE turn=(\d+) m=(-?\d+) u=(-?\d+) path=(\w+) detour_existed=(\w+) "
                     r"m_from=(-?\d+),(-?\d+) m_to=(-?\d+),(-?\d+) u_displaced=(.*)$")
RE_SEAM = re.compile(
    r"^SW1SEAM turn=(\d+) m=(-?\d+) u=(-?\d+) m_target=(-?\d+),(-?\d+) "
    r"next_from_landing=(-?\d+),(-?\d+) vacates=(\w+) d_from=(-?\d+) d_landing=(-?\d+) "
    r"target_is_landing=(\w+) u_cmd=(.*)$")
RE_SHADOW = re.compile(r"^SW1SHADOW turn=(\d+) identical=(\w+)$")
RE_CMD = re.compile(r"^SW1CMD turn=(\d+) id=(-?\d+) idx=(\d+) cmd=(.*)$")

RESWAP_WINDOW = 4


class GateError(Exception):
    """Anything that would make a number mean something other than it says."""


def parse(err: str):
    turns, fires, shadow, cmds = {}, [], {}, collections.defaultdict(dict)
    for line in err.splitlines():
        if not line.startswith("SW1"):
            continue
        m = RE_TURN.match(line)
        if m:
            turns[int(m.group(1))] = {"enabled": m.group(2) == "true",
                                      "own_units": int(m.group(3))}
            continue
        m = RE_FIRE.match(line)
        if m:
            fires.append({"turn": int(m.group(1)), "m": int(m.group(2)), "u": int(m.group(3)),
                          "path": m.group(4), "detour_existed": m.group(5) == "true",
                          "m_from": [int(m.group(6)), int(m.group(7))],
                          "m_to": [int(m.group(8)), int(m.group(9))],
                          "u_displaced": m.group(10)})
            continue
        m = RE_SEAM.match(line)
        if m:
            # the remedy-ruling diagnostic row; it rides beside the fire row it belongs to and
            # never changes a gate. Order is guaranteed: both are emitted from the same branch.
            if not fires:
                raise GateError(f"SW1SEAM row with no preceding fire: {line}")
            seam = {"m_target": [int(m.group(4)), int(m.group(5))],
                    "next_from_landing": [int(m.group(6)), int(m.group(7))],
                    "vacates_partner_cell": m.group(8) == "true",
                    "bfs_from_mover_cell": int(m.group(9)),
                    "bfs_from_landing": int(m.group(10)),
                    "target_is_landing": m.group(11) == "true",
                    "u_cmd": m.group(12)}
            last = fires[-1]
            if (last["turn"], last["m"], last["u"]) != (int(m.group(1)), int(m.group(2)),
                                                        int(m.group(3))):
                raise GateError(f"SW1SEAM row does not match its fire row: {line}")
            last["seam"] = seam
            continue
        m = RE_SHADOW.match(line)
        if m:
            shadow[int(m.group(1))] = m.group(2) == "true"
            continue
        m = RE_CMD.match(line)
        if m:
            cmds[int(m.group(1))][int(m.group(2))] = m.group(4)
            continue
        raise GateError(f"unparsed instrumentation row: {line}")
    return turns, fires, shadow, cmds


def verb(command: str) -> str:
    return command.split()[0].upper() if command.split() else ""


def resume_turns(fires, cmds):
    """For every fire that displaced real work, the turn U next issued that verb again.

    The card expects `U` back on its tree within 2 ticks on 005/027. This reports the number;
    it does not assert it. `None` means the verb never returned within the game.
    """
    out = []
    for fire in fires:
        displaced = verb(fire["u_displaced"])
        if displaced in ("WAIT", ""):
            out.append({**fire, "displaced_work": False, "resumed_turn": None, "resumed_after": None})
            continue
        resumed = None
        for turn in sorted(t for t in cmds if t > fire["turn"]):
            if verb(cmds[turn].get(fire["u"], "")) == displaced:
                resumed = turn
                break
        out.append({**fire, "displaced_work": True, "resumed_turn": resumed,
                    "resumed_after": None if resumed is None else resumed - fire["turn"]})
    return out


def reswaps(fires):
    """Ruling 4: the same unordered pair swapping again within four ticks is a design failure."""
    seen, hits = collections.defaultdict(list), []
    for fire in fires:
        key = tuple(sorted((fire["m"], fire["u"])))
        for earlier in seen[key]:
            if 0 < fire["turn"] - earlier <= RESWAP_WINDOW:
                hits.append({"pair": list(key), "first_turn": earlier, "again_turn": fire["turn"]})
        seen[key].append(fire["turn"])
    return hits


def stream_lines(text: str) -> list[str]:
    return [line for line in text.strip().splitlines()]


def run_fixture(sit, cfg, base_bin, cand_bin, probe_bin):
    spec = H.spec_for(sit, cfg)
    turns = int(cfg["turns"])
    _, base_cmds = rt.run_binary_custom(base_bin, fp.make_referee(spec), turns)
    _, cand_cmds = rt.run_binary_custom(cand_bin, fp.make_referee(spec), turns)
    _, probe_cmds, err = C.run_diagnostic(probe_bin, fp.make_referee(spec), turns)

    # 1. probe parity — checked before a single row is read
    if probe_cmds.strip() != cand_cmds.strip():
        raise GateError(f"{sit['id']}: the PROBE diverges from the plain candidate. The "
                        f"instrumented run is a different bot; no row from it means anything.")

    t_rows, fires, shadow, cmds = parse(err)
    fire_turns = {f["turn"] for f in fires}

    # 2. shadow inertness, exact in both directions, on every tick
    mismatched = sorted(t for t, same in shadow.items() if same == (t in fire_turns))
    #   same=True  and t in fire_turns  -> a fire that changed nothing
    #   same=False and t not in fire    -> a difference with no fire: alpha is not inert
    if mismatched:
        raise GateError(
            f"{sit['id']}: shadow gate FAILED on turns {mismatched[:10]} — a tick either fired "
            f"without changing the stream or changed the stream without firing.")

    base_lines, cand_lines = stream_lines(base_cmds), stream_lines(cand_cmds)
    first_fire = min(fire_turns) if fire_turns else None
    if first_fire is None:
        whole_game_identical = base_lines == cand_lines
        pre_divergence_identical = whole_game_identical
    else:
        # turn t is line index t-1
        pre = first_fire - 1
        whole_game_identical = base_lines == cand_lines
        pre_divergence_identical = base_lines[:pre] == cand_lines[:pre]

    unit_turns = sum(row["own_units"] for row in t_rows.values())
    detailed = resume_turns(fires, cmds)
    return {
        "id": sit["id"], "kind": sit["kind"],
        "turns_observed": len(t_rows),
        "alpha_disabled_ticks": sorted(t for t, row in t_rows.items() if not row["enabled"]),
        "unit_turns": unit_turns,
        "fires": len(fires),
        "fire_rate_of_unit_turns": (len(fires) / unit_turns) if unit_turns else 0.0,
        "yield_path": sum(1 for f in fires if f["path"] == "YIELD"),
        "yield_path_with_detour_available": sum(
            1 for f in fires if f["path"] == "YIELD" and f["detour_existed"]),
        "no_detour_path": sum(1 for f in fires if f["path"] == "NODETOUR"),
        "displaced_work_fires": sum(1 for f in detailed if f["displaced_work"]),
        "resume_deltas": [f["resumed_after"] for f in detailed if f["displaced_work"]],
        "reswaps": reswaps(fires),
        "shadow_ticks_checked": len(shadow),
        "whole_game_identical_to_base": whole_game_identical,
        "pre_first_fire_identical_to_base": pre_divergence_identical,
        "first_fire_turn": first_fire,
        "fire_detail": detailed,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--only")
    ap.add_argument("--json", default=str(OUT))
    args = ap.parse_args()

    cfg = json.loads(H.CONFIG.read_text())
    sits = H.load_situations(args.only.split(",") if args.only else None)
    rows, failures = [], []
    with tempfile.TemporaryDirectory(prefix="swap-g1-") as wd:
        wd = Path(wd)
        bins = {}
        for name, src in (("base", BASE), ("cand", CANDIDATE), ("probe", PROBE)):
            bins[name] = wd / f"{name}.bin"
            sh.compile_text(src.read_text(), bins[name], crate=f"swap_g1_{name}")
        for sit in sits:
            try:
                row = run_fixture(sit, cfg, bins["base"], bins["cand"], bins["probe"])
            except GateError as exc:
                failures.append(str(exc))
                print(f"  FAILED  {sit['id']}: {exc}")
                continue
            rows.append(row)
            print(f"  {row['id']}  fires={row['fires']:<4} "
                  f"yield={row['yield_path']}({row['yield_path_with_detour_available']} with detour) "
                  f"nodetour={row['no_detour_path']}  "
                  f"shadow_ticks={row['shadow_ticks_checked']}  "
                  f"whole_game_identical={row['whole_game_identical_to_base']}  "
                  f"reswaps={len(row['reswaps'])}")

    total_fires = sum(r["fires"] for r in rows)
    total_reswaps = sum(len(r["reswaps"]) for r in rows)
    zero_fire_rows = [r for r in rows if r["fires"] == 0]
    zero_fire_bad = [r["id"] for r in zero_fire_rows if not r["whole_game_identical_to_base"]]
    pre_bad = [r["id"] for r in rows if not r["pre_first_fire_identical_to_base"]]
    unit_turns = sum(r["unit_turns"] for r in rows)

    verdict = {
        "task": "20260821-swap-r1-cure", "gate": "G-1",
        "fixtures": len(rows), "harness_failures": failures,
        "total_fires": total_fires,
        "total_unit_turns": unit_turns,
        "corpus_fire_rate_of_unit_turns": (total_fires / unit_turns) if unit_turns else 0.0,
        "fixtures_that_fired": sorted(r["id"] for r in rows if r["fires"]),
        "zero_fire_fixtures": len(zero_fire_rows),
        "zero_fire_fixtures_not_byte_identical": zero_fire_bad,
        "pre_first_fire_divergences": pre_bad,
        "total_reswaps_within_4_ticks": total_reswaps,
        "alpha_disabled_ticks_total": sum(len(r["alpha_disabled_ticks"]) for r in rows),
        "rows": rows,
    }
    gates = {
        "probe parity and shadow inertness on every tick": not failures,
        "zero-fire fixtures byte-identical to the base for the whole game": not zero_fire_bad,
        "every fixture identical to the base before its first fire": not pre_bad,
        "the trigger fires somewhere in the corpus (an inert alpha fails)": total_fires > 0,
        "no repeated unordered swap pair within 4 ticks (ruling 4)": total_reswaps == 0,
    }
    verdict["gates"] = gates
    verdict["all_ok"] = all(gates.values())
    Path(args.json).write_text(json.dumps(verdict, indent=2) + "\n")

    print()
    for label, good in gates.items():
        print(f"  {'PASS' if good else 'FAIL'}  {label}")
    print(f"\n  total fires {total_fires} over {unit_turns} unit-turns "
          f"({100 * verdict['corpus_fire_rate_of_unit_turns']:.3f} % of unit-turns)")
    print(f"  G-1: {'ALL GATES PASS' if verdict['all_ok'] else 'A GATE FAILED'} -> {args.json}")
    return 0 if verdict["all_ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
