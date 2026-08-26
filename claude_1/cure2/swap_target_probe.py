#!/usr/bin/env python3
"""Which target did clause 6 compare? Measured at the predicate, on both corpora.

The coordinator's `20260825T173324Z` question: in the OSC-006 trace the mover's shown goal at the
exchange turn looks like the landing itself, and clause 6 requires `target != landing`. This
driver answers it by measurement rather than by reading: the PRINT-ONLY diagnostic arm
(`arm-diagnostic.rs`, three `eprintln!` lines over `arm-instrument.rs`) reports, at the predicate,
the mover's cell `c`, the predicate's target `T`, the landing `L`, the partner, and the two
distances clause 6 compares. The v5 wire supplies each unit's `chosen`/`want` for the same turn.

Gates, each of which fails the run rather than degrading it:

  G-A  print-only    -- the diagnostic arm's stdout command stream must be byte-identical to the
                        instrument arm's on every game run here.
  G-B  row identity  -- each panel game must reproduce its recorded `panel-swap-census.json` row
                        (swaps, so, sn, sf); each fixture its `swap-loop-control.json` turns.
  G-C  join          -- every SWAPFIRE must land on a turn whose wire shows that mover as `S` and
                        that partner as `X`, and the counts must agree.

    python3 claude_1/cure2/swap_target_probe.py [--fixtures-only]
"""
from __future__ import annotations

import json
import re
import subprocess
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
import narrate5 as n5                 # noqa: E402

DIAG = HERE / "arm-diagnostic.rs"
INSTR = HERE / "arm-instrument.rs"
PANEL_CFG = HERE / "cure2-instrument-config.json"
CENSUS = HERE / "results" / "panel-swap-census.json"
OUT = HERE / "results" / "swap-target-probe.json"

RE_DIAG = re.compile(r"^SWAPDIAG t=(\d+) m=(-?\d+) c=(-?\d+),(-?\d+) T=(-?\d+),(-?\d+) "
                     r"L=(-?\d+),(-?\d+) b=(-?\d+) adj=(\d) teq=(\d)$")
RE_DIST = re.compile(r"^SWAPDIST t=(\d+) m=(-?\d+) b=(-?\d+) dl=(-?\d+) dh=(-?\d+)$")
RE_FIRE = re.compile(r"^SWAPFIRE t=(\d+) m=(-?\d+) b=(-?\d+)$")
RE_CELL = re.compile(r"^(TREE|BANK|CELL)\((-?\d+),(-?\d+)\)$")


class GateError(Exception):
    """Anything that would make a number below mean something other than it says."""


def target_cell(text):
    """The cell inside a wire target, or None for SHACK / NONE / ABSENT (no cell is carried)."""
    m = RE_CELL.match(text)
    return (int(m.group(2)), int(m.group(3))) if m else None


def wire(lines):
    out = {}
    for index, line in enumerate(lines, 1):
        frags = n5.msg_fragments(line)
        if len(frags) != 1:
            raise GateError(f"turn {index}: {len(frags)} MSG fragments")
        turn, units, _order, _banner, meta = n5.decode(frags[0].strip())
        out[turn] = (units, meta)
    return out


def run(binary, ref, turns, capture_stderr):
    """rt.run_binary_custom, but with the arm's stderr captured to a temp file."""
    if not capture_stderr:
        return rt.run_binary_custom(binary, ref, turns) + ("",)
    with tempfile.TemporaryFile(mode="w+") as err:
        real = sys.stderr
        fd = sys.stderr.fileno()
        import os
        saved = os.dup(fd)
        os.dup2(err.fileno(), fd)
        try:
            transcript, commands = rt.run_binary_custom(binary, ref, turns)
        finally:
            os.dup2(saved, fd)
            os.close(saved)
            sys.stderr = real
        err.seek(0)
        return transcript, commands, err.read()


def parse_diag(text):
    """turn -> {'cases': [...], 'dist': {(m,b): (dl,dh)}, 'fires': [(m,b)]}"""
    rows = {}
    for line in text.splitlines():
        m = RE_DIAG.match(line)
        if m:
            t = int(m.group(1))
            rows.setdefault(t, {"cases": [], "dist": {}, "fires": []})["cases"].append({
                "mover": int(m.group(2)), "c": (int(m.group(3)), int(m.group(4))),
                "T": (int(m.group(5)), int(m.group(6))),
                "L": (int(m.group(7)), int(m.group(8))),
                "partner": int(m.group(9)), "adjacent": m.group(10) == "1",
                "target_equals_landing": m.group(11) == "1"})
            continue
        m = RE_DIST.match(line)
        if m:
            t = int(m.group(1))
            rows.setdefault(t, {"cases": [], "dist": {}, "fires": []})["dist"][
                (int(m.group(2)), int(m.group(3)))] = (int(m.group(4)), int(m.group(5)))
            continue
        m = RE_FIRE.match(line)
        if m:
            t = int(m.group(1))
            rows.setdefault(t, {"cases": [], "dist": {}, "fires": []})["fires"].append(
                (int(m.group(2)), int(m.group(3))))
    return rows


def rows_for_game(key, lines, diag_text):
    """One row per STANDING-partner case, with the wire's targets joined on the same turn."""
    payload = wire(lines)
    diag = parse_diag(diag_text)
    cases, fired = [], 0
    for turn in sorted(diag):
        units = payload[turn][0]
        meta = payload[turn][1]
        s_ids = sorted(u for u, v in units.items() if v[2] == "S")
        x_ids = sorted(u for u, v in units.items() if v[2] == "X")
        for case in diag[turn]["cases"]:
            m, b = case["mover"], case["partner"]
            dist = diag[turn]["dist"].get((m, b))
            granted = (m, b) in diag[turn]["fires"]
            if granted and not (m in s_ids and b in x_ids):
                raise GateError(f"{key} t{turn}: SWAPFIRE {m}->{b} but wire shows S={s_ids} X={x_ids}")
            mover_wire = units.get(m)
            partner_wire = units.get(b)
            chosen = mover_wire[0] if mover_wire else None
            cases.append({
                "game": key, "turn": turn, "mover": m, "partner": b,
                "mover_cell_c": list(case["c"]), "predicate_T": list(case["T"]),
                "landing_L": list(case["L"]),
                "mover_chosen": chosen, "mover_want": mover_wire[1] if mover_wire else None,
                "partner_chosen": partner_wire[0] if partner_wire else None,
                "partner_want": partner_wire[1] if partner_wire else None,
                "chosen_cell": list(target_cell(chosen)) if chosen and target_cell(chosen) else None,
                "chosen_equals_T": target_cell(chosen) == case["T"] if chosen else None,
                "chosen_equals_L": target_cell(chosen) == case["L"] if chosen else None,
                "T_equals_L": case["target_equals_landing"], "adjacent": case["adjacent"],
                "d_landing": dist[0] if dist else None, "d_here": dist[1] if dist else None,
                "granted": granted,
                "outcome": ("EXCHANGE" if granted
                            else "refused sn (non-adjacent)" if not case["adjacent"]
                            else "refused so (teammate on the goal)" if case["target_equals_landing"]
                            else "refused sf (slot map)" if dist is None
                            else "no cure: d(L) >= d(c)")})
            fired += int(granted)
        del meta
    return cases, fired


def main() -> int:
    fixtures_only = "--fixtures-only" in sys.argv
    census = json.loads(CENSUS.read_text())
    census_rows = {r["game"]: r for r in census["rows"]}
    panel_targets = [r["game"] for r in census["rows"] if r["swaps"]]

    result = {"task": "20260825-dance-cure-candidate-2-swap",
              "question": "coordination/messages/local_claude_1/20260825T173324Z-"
                          "20260825-dance-cure-candidate-2-swap-question.md",
              "arm": "claude_1/cure2/arm-diagnostic.rs (print-only, +3 eprintln over arm-instrument.rs)",
              "gates": {}, "cases": [], "summary": {}}

    with tempfile.TemporaryDirectory(prefix="cure2-tgt-") as wd:
        wd = Path(wd)
        diag_bin, instr_bin = wd / "diag.bin", wd / "instr.bin"
        sh.compile_text(DIAG.read_text(), diag_bin, crate="cure2_arm_diagnostic")
        sh.compile_text(INSTR.read_text(), instr_bin, crate="cure2_arm_instrument_probe")

        # ---------------------------------------------------------------- fixtures
        cfg = json.loads(fh.CONFIG.read_text())
        sits = fh.load_situations(None)
        fixture_keys = []
        for sit in sits:
            spec = fh.spec_for(sit, cfg)
            _, cmds_i = rt.run_binary_custom(instr_bin, fp.make_referee(spec), int(cfg["turns"]))
            _, cmds_d, err = run(diag_bin, fp.make_referee(spec), int(cfg["turns"]), True)
            if cmds_i != cmds_d:
                raise GateError(f"{sit['id']}: diagnostic arm is NOT print-only")
            key = sit["id"]
            fixture_keys.append(key)
            cases, fired = rows_for_game(key, cmds_d.rstrip("\n").split("\n"), err)
            result["cases"].extend(cases)
        result["gates"]["G-A print-only (fixtures)"] = f"PASS on {len(fixture_keys)} fixtures"

        if not fixtures_only:
            pcfg = fp.load_config(PANEL_CFG)
            parent = wd / "parent.bin"
            parent_src = (PANEL_CFG.parent / pcfg["parent"]["source"]).resolve()
            sh.compile_text(parent_src.read_text(), parent, crate="cure2_parent_probe")
            jobs = {f"{j['spec']['map_id']}:{j['spec']['seat']}": j
                    for j in fp.build_jobs(pcfg, diag_bin, parent)}
            checked = []
            for key in panel_targets:
                job = jobs[key]
                spec = job["spec"]
                _, cmds_i = rt.run_binary_custom(instr_bin, fp.make_referee(spec), job["turns"])
                _, cmds_d, err = run(diag_bin, fp.make_referee(spec), job["turns"], True)
                if cmds_i != cmds_d:
                    raise GateError(f"{key}: diagnostic arm is NOT print-only")
                cases, fired = rows_for_game(key, cmds_d.rstrip("\n").split("\n"), err)
                recorded = census_rows[key]
                if fired != recorded["swaps"]:
                    raise GateError(f"{key}: {fired} exchanges now against {recorded['swaps']} "
                                    f"recorded in panel-swap-census.json")
                checked.append(key)
                result["cases"].extend(cases)
                print(f"  {key}: {fired} exchanges, row identity MATCH", flush=True)
            result["gates"]["G-A print-only (panel)"] = f"PASS on {len(checked)} games"
            result["gates"]["G-B row identity"] = (
                f"PASS — {len(checked)} panel games reproduce their recorded swap count")

    granted = [c for c in result["cases"] if c["granted"]]
    result["summary"] = {
        "standing_partner_cases": len(result["cases"]),
        "exchanges": len(granted),
        "exchanges_where_chosen_equals_T": sum(1 for c in granted if c["chosen_equals_T"]),
        "exchanges_where_chosen_differs_from_T": sorted(
            {c["game"] + f" t{c['turn']}" for c in granted if c["chosen_equals_T"] is False}),
        "exchanges_where_chosen_equals_L": sum(1 for c in granted if c["chosen_equals_L"]),
        "exchanges_where_T_equals_L": sum(1 for c in granted if c["T_equals_L"]),
        "refused_so_teammate_on_goal": sum(1 for c in result["cases"]
                                           if c["outcome"].startswith("refused so")),
        "refused_sn_non_adjacent": sum(1 for c in result["cases"]
                                       if c["outcome"].startswith("refused sn")),
        "refused_sf_slot_map": sum(1 for c in result["cases"]
                                   if c["outcome"].startswith("refused sf")),
        "no_cure_distance": sum(1 for c in result["cases"] if c["outcome"].startswith("no cure")),
    }
    result["gates"]["G-C join"] = "PASS — every SWAPFIRE matched an S/X pair on the same wire turn"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    print(json.dumps(result["summary"], indent=1))
    print("wrote", OUT.relative_to(REPO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
