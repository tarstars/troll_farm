#!/usr/bin/env python3
"""C-11 — the A-2 memory check: is the `prev_cells` map read on turn `t` the cells of turn `t-1`?

G-0 §4.0 names A-2 as an ASSUMPTION -- "`prev_cells` read on turn `t` equals the cells own units
occupied on turn `t-1`, and is absent for a unit not alive at `t-1`" -- and G-0 §9 requires C-11
to produce 100 %. Clause 4's standing test, and with it Theorem 1's proof, reads nothing else.

The measurement, per turn `t` of every game:

    read_t == { u.id: u.cell  for u in own units of the referee state at t-1 }     (t > 1)
    read_1 == {}                                                                   (first turn)

The READ comes from the arm itself, printed at the point of use by the PRINT-ONLY C-11 arm
(`arm-c11.rs`, +1 `eprintln!` over `arm-instrument.rs`) because the v5 wire does not carry it.
The EXPECTED cells come from the REFEREE's own transcript (`trace_detectors.build_trace`). The
two sources are independent by construction: the bot's memory against the referee's history.

Gates, each of which fails the run rather than degrading it:

  G-A  print-only     -- the C-11 arm's stdout command stream must be byte-identical to the
                         instrument arm's on every game run here. A read that changed a command
                         would be measuring a different bot.
  G-B  row identity   -- each panel game reproduces its `panel-swap-census.json` `swaps` count and
                         each fixture its `swap-loop-control.json` exchange turns, counted off the
                         wire of this run. Without it the population is not the G-1 population.
  G-C  coverage       -- every turn `1..T` of every game must carry exactly one PREVREAD line. A
                         turn on which the map was never read is an unmeasured turn, not a pass.

Two witnesses against inertness, reported and required to be positive over the corpus:

  W-1  discriminating -- turns where the read differs from the CURRENT turn's own cells. On a
                         corpus where nothing ever moved, `prev == current` and the check would
                         pass without distinguishing `t-1` from `t`.
  W-2  roster change  -- turns where the own-unit id set at `t-1` differs from the set at `t`
                         (a birth or a death). The "absent for a unit not alive at t-1" half of
                         A-2 is only exercised on these; if there are none, the report says so
                         instead of claiming that half was verified.

    python3 claude_1/cure2/c11_prev_cells_check.py [--fixtures-only] [--swap-games-only]

The default panel population is EVERY game in `panel-swap-census.json`, not only the 28
that carry an exchange: A-2 is a claim about every turn of every game, and restricting to
exchange games would measure it on the subset where it happens to matter most.
"""
from __future__ import annotations

import json
import os
import re
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

ARM = HERE / "arm-c11.rs"
INSTR = HERE / "arm-instrument.rs"
PANEL_CFG = HERE / "cure2-instrument-config.json"
CENSUS = HERE / "results" / "panel-swap-census.json"
FIXTURE_CONTROL = HERE / "results" / "swap-loop-control.json"
OUT = HERE / "results" / "c11-a2-check.json"

RE_READ = re.compile(r"^PREVREAD t=(\d+) n=(\d+) p=(.*)$")


class GateError(Exception):
    """Anything that would make the number below mean something other than it says."""


def run_capturing(binary, ref, turns):
    """rt.run_binary_custom with the arm's stderr captured (same shape as swap_target_probe.run)."""
    with tempfile.TemporaryFile(mode="w+") as err:
        fd = sys.stderr.fileno()
        saved = os.dup(fd)
        os.dup2(err.fileno(), fd)
        try:
            transcript, commands = rt.run_binary_custom(binary, ref, turns)
        finally:
            os.dup2(saved, fd)
            os.close(saved)
        err.seek(0)
        return transcript, commands, err.read()


def parse_reads(key, text):
    """turn -> {id: (x, y)}, refusing a duplicate or malformed line rather than keeping the last."""
    reads = {}
    for line in text.splitlines():
        m = RE_READ.match(line)
        if not m:
            continue
        turn, count, payload = int(m.group(1)), int(m.group(2)), m.group(3)
        entries = {}
        if payload:
            for frag in payload.split(";"):
                uid, cell = frag.split(":", 1)
                x, y = cell.split(",")
                entries[int(uid)] = (int(x), int(y))
        if len(entries) != count:
            raise GateError(f"{key} t{turn}: PREVREAD says n={count} but carries {len(entries)}")
        if turn in reads:
            raise GateError(f"{key} t{turn}: two PREVREAD lines on one turn (G-C)")
        reads[turn] = entries
    return reads


def exchange_turns(key, lines):
    """Exchange turns off this run's own wire, for the G-B row-identity comparison."""
    out = []
    for index, line in enumerate(lines, 1):
        frags = n5.msg_fragments(line)
        if len(frags) != 1:
            raise GateError(f"{key} turn {index}: {len(frags)} MSG fragments")
        turn, _units, _order, _banner, meta = n5.decode(frags[0].strip())
        if meta["sw"]:
            out.append(turn)
    return out


def check_game(key, transcript, commands, stderr_text):
    """One row per turn whose read disagrees, plus the per-game counters and witnesses."""
    reads = parse_reads(key, stderr_text)
    trace = td.build_trace(transcript, commands)
    turns = list(range(1, trace.T + 1))
    missing = [t for t in turns if t not in reads]
    extra = sorted(t for t in reads if t not in turns)
    if missing or extra:
        raise GateError(f"{key}: PREVREAD missing on turns {missing[:8]} and present on "
                        f"non-turns {extra[:8]} (G-C coverage)")
    cells = {t: {u.id: u.cell for u in trace.state(t).own_units()} for t in turns}
    mismatches, discriminating, roster_change = [], 0, 0
    for t in turns:
        expected = {} if t == 1 else cells[t - 1]
        got = reads[t]
        if got != expected:
            mismatches.append({
                "game": key, "turn": t,
                "read": {str(k): list(v) for k, v in sorted(got.items())},
                "expected_cells_of_previous_turn": {str(k): list(v)
                                                    for k, v in sorted(expected.items())},
                "ids_read_not_alive_previous_turn": sorted(set(got) - set(expected)),
                "ids_alive_previous_turn_not_read": sorted(set(expected) - set(got)),
                "ids_with_wrong_cell": sorted(k for k in set(got) & set(expected)
                                              if got[k] != expected[k])})
        if t > 1:
            if got != cells[t]:
                discriminating += 1
            if set(cells[t - 1]) != set(cells[t]):
                roster_change += 1
    return {"game": key, "turns": trace.T, "reads": len(reads), "mismatches": mismatches,
            "discriminating_turns": discriminating, "roster_change_turns": roster_change}


def totals(rows):
    return {
        "games": len(rows),
        "turns_checked": sum(r["turns"] for r in rows),
        "turns_matching": sum(r["turns"] - len(r["mismatches"]) for r in rows),
        "mismatches": sum(len(r["mismatches"]) for r in rows),
        "mismatch_rows": [m for r in rows for m in r["mismatches"]][:50],
        "rate": (round(100.0 * sum(r["turns"] - len(r["mismatches"]) for r in rows)
                       / sum(r["turns"] for r in rows), 2) if rows else None),
        "W1_discriminating_turns": sum(r["discriminating_turns"] for r in rows),
        "W2_roster_change_turns": sum(r["roster_change_turns"] for r in rows),
    }


def main() -> int:
    fixtures_only = "--fixtures-only" in sys.argv
    census = json.loads(CENSUS.read_text())
    census_rows = {r["game"]: r for r in census["rows"]}
    swap_only = "--swap-games-only" in sys.argv
    panel_targets = [r["game"] for r in census["rows"]
                     if r["swaps"] or not swap_only]
    fixture_pairs = json.loads(FIXTURE_CONTROL.read_text())["pairs"]
    fixture_turns = {}
    for pair_key, turns in fixture_pairs.items():
        fixture_turns.setdefault(pair_key.rsplit(":", 1)[0], []).extend(turns)
    fixture_turns = {g: sorted(t) for g, t in fixture_turns.items()}

    result = {"control": "C-11 — A-2 prev_cells memory check",
              "task": "20260825-dance-cure-candidate-2-swap",
              "arm": str(ARM.relative_to(REPO)) + " (print-only, +1 eprintln over arm-instrument.rs)",
              "read_from": "the arm itself, printed at the point of use",
              "expected_from": "the referee transcript via trace_detectors.build_trace",
              "gates": {}, "games": []}

    with tempfile.TemporaryDirectory(prefix="cure2-c11-") as wd:
        wd = Path(wd)
        arm_bin, instr_bin = wd / "c11.bin", wd / "instr.bin"
        sh.compile_text(ARM.read_text(), arm_bin, crate="cure2_arm_c11")
        sh.compile_text(INSTR.read_text(), instr_bin, crate="cure2_arm_instrument_c11")

        cfg = json.loads(fh.CONFIG.read_text())
        fixture_rows = []
        for sit in fh.load_situations(None):
            spec = fh.spec_for(sit, cfg)
            _, cmds_i = rt.run_binary_custom(instr_bin, fp.make_referee(spec), int(cfg["turns"]))
            transcript, cmds, err = run_capturing(arm_bin, fp.make_referee(spec),
                                                  int(cfg["turns"]))
            if cmds_i != cmds:
                raise GateError(f"{sit['id']}: the C-11 arm is NOT print-only (G-A)")
            seen = exchange_turns(sit["id"], cmds.rstrip("\n").split("\n"))
            if seen != fixture_turns.get(sit["id"], []):
                raise GateError(f"{sit['id']}: exchange turns {seen} against the recorded "
                                f"{fixture_turns.get(sit['id'], [])} (G-B)")
            row = check_game(sit["id"], transcript, cmds, err)
            fixture_rows.append(row)
            if seen:
                print(f"  {sit['id']}: {row['turns']} turns read, {len(row['mismatches'])} "
                      f"mismatches, row identity MATCH", flush=True)
        result["gates"]["G-A print-only (fixtures)"] = f"PASS on {len(fixture_rows)} fixtures"
        result["gates"]["G-B row identity (fixtures)"] = (
            f"PASS — {len(fixture_turns)} fixtures with exchanges reproduce their recorded turns")
        result["games"].extend(fixture_rows)
        result["fixture_summary"] = totals(fixture_rows)

        panel_rows = []
        if not fixtures_only:
            pcfg = fp.load_config(PANEL_CFG)
            parent = wd / "parent.bin"
            parent_src = (PANEL_CFG.parent / pcfg["parent"]["source"]).resolve()
            sh.compile_text(parent_src.read_text(), parent, crate="cure2_parent_c11")
            jobs = {f"{j['spec']['map_id']}:{j['spec']['seat']}": j
                    for j in fp.build_jobs(pcfg, arm_bin, parent)}
            for key in panel_targets:
                job = jobs[key]
                _, cmds_i = rt.run_binary_custom(instr_bin, fp.make_referee(job["spec"]),
                                                 job["turns"])
                transcript, cmds, err = run_capturing(arm_bin, fp.make_referee(job["spec"]),
                                                      job["turns"])
                if cmds_i != cmds:
                    raise GateError(f"{key}: the C-11 arm is NOT print-only (G-A)")
                seen = exchange_turns(key, cmds.rstrip("\n").split("\n"))
                if len(seen) != census_rows[key]["swaps"]:
                    raise GateError(f"{key}: {len(seen)} exchanges now against "
                                    f"{census_rows[key]['swaps']} in panel-swap-census.json (G-B)")
                row = check_game(key, transcript, cmds, err)
                panel_rows.append(row)
                print(f"  {key}: {row['turns']} turns read, {len(row['mismatches'])} mismatches, "
                      f"row identity MATCH", flush=True)
            result["gates"]["G-A print-only (panel)"] = f"PASS on {len(panel_rows)} games"
            result["gates"]["G-B row identity (panel)"] = (
                f"PASS — {len(panel_rows)} panel games reproduce their recorded swap count")
            result["games"].extend(panel_rows)
            result["panel_summary"] = totals(panel_rows)

    total = totals(result["games"])
    result["total_summary"] = total
    result["gates"]["G-C coverage"] = (
        f"PASS — exactly one PREVREAD on every turn of every game "
        f"({total['turns_checked']} turns)")
    result["witnesses"] = {
        "W-1 discriminating turns (read != current turn's cells)": total["W1_discriminating_turns"],
        "W-2 roster-change turns (birth or death between t-1 and t)":
            total["W2_roster_change_turns"],
        "note": ("W-2 = 0 would mean the 'absent for a unit not alive at t-1' half of A-2 was "
                 "never exercised by this corpus and is NOT verified by this run."),
    }
    result["verdict"] = ("PASS" if total["mismatches"] == 0 and total["W1_discriminating_turns"]
                         else "INERT — no turn distinguished t-1 from t" if not total[
                             "mismatches"] else "FAIL — A-2 IS FALSE")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    printable = {k: v for k, v in total.items() if not isinstance(v, list)}
    print(json.dumps(printable, indent=1))
    print("mismatch rows:", json.dumps(total["mismatch_rows"])[:2000])
    print("verdict:", result["verdict"])
    print("wrote", OUT.relative_to(REPO))
    return 0 if total["mismatches"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
