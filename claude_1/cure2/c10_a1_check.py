#!/usr/bin/env python3
"""C-10 — the A-1 referee check: for every exchange, are the realised next-turn cells the exchange?

G-0 §4.0 names A-1 (the referee executes a circular two-unit swap when both own units are ordered
onto each other's cell) as an ASSUMPTION, and G-0 §10 says C-10 below 100 % withdraws the design:
"A-1 is wrong about the referee and the whole exchange premise fails." Nothing else in Candidate 2
is worth reading until this number is 100 %, which is why the coordinator's `20260825T184429Z`
puts C-10 first.

The measurement, per exchange at turn `t` with mover `M` and displaced partner `B`:

    c_{t+1}(M) == c_t(B)   and   c_{t+1}(B) == c_t(M)

Both cells come from the REFEREE's own transcript (`trace_detectors.build_trace`), never from the
arm's payload; the pair `(M, B)` comes from the `S`/`X` branch codes on the v5 wire. So the wire
says who was ordered to exchange and the referee says where they actually stood.

Gates, each of which fails the run rather than degrading it:

  G-B  row identity   -- each panel game reproduces its `panel-swap-census.json` `swaps` count and
                         each fixture its `swap-loop-control.json` exchange turns. Without this the
                         population being checked is not the population the G-1 report describes.
  G-D  unambiguous    -- an exchange turn carries exactly one `S` and one `X`; anything else is
                         refused rather than paired by guesswork.
  G-E  observability  -- an exchange on the final turn has no turn `t+1` in the trace and is
                         counted NOT OBSERVABLE, never as a pass. Same for a unit that is not in
                         the `t+1` state at all (death), which is reported separately with its ids.

    python3 claude_1/cure2/c10_a1_check.py [--fixtures-only]
"""
from __future__ import annotations

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

INSTR = HERE / "arm-instrument.rs"
PANEL_CFG = HERE / "cure2-instrument-config.json"
CENSUS = HERE / "results" / "panel-swap-census.json"
FIXTURE_CONTROL = HERE / "results" / "swap-loop-control.json"
OUT = HERE / "results" / "c10-a1-check.json"


class GateError(Exception):
    """Anything that would make the number below mean something other than it says."""


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def exchange_turns(key, lines):
    """[(turn, mover, partner)] off the wire, refusing any ambiguous turn (G-D)."""
    out = []
    for index, line in enumerate(lines, 1):
        frags = n5.msg_fragments(line)
        if len(frags) != 1:
            raise GateError(f"{key} turn {index}: {len(frags)} MSG fragments")
        turn, units, _order, _banner, meta = n5.decode(frags[0].strip())
        if not meta["sw"]:
            continue
        s_ids = sorted(u for u, v in units.items() if v[2] == "S")
        x_ids = sorted(u for u, v in units.items() if v[2] == "X")
        if len(s_ids) != 1 or len(x_ids) != 1:
            raise GateError(f"{key} t{turn}: ambiguous exchange turn, S={s_ids} X={x_ids} "
                            f"(G-D refuses to pair by guesswork)")
        out.append((turn, s_ids[0], x_ids[0]))
    return out


def check_game(key, transcript, commands):
    """One row per exchange: the two cells before, the two cells after, and the verdict."""
    lines = commands.rstrip("\n").split("\n")
    trace = td.build_trace(transcript, commands)
    rows = []
    for turn, mover, partner in exchange_turns(key, lines):
        row = {"game": key, "turn": turn, "mover": mover, "partner": partner}
        if turn + 1 > trace.T:
            row["verdict"] = "NOT_OBSERVABLE_final_turn"
            rows.append(row)
            continue
        here, nxt = trace.state(turn), trace.state(turn + 1)
        c_m, c_b = here.unit(mover), here.unit(partner)
        n_m, n_b = nxt.unit(mover), nxt.unit(partner)
        if c_m is None or c_b is None:
            raise GateError(f"{key} t{turn}: wire named u{mover}/u{partner} but the referee "
                            f"state has {sorted(u.id for u in here.own_units())}")
        row["mover_cell_before"] = list(c_m.cell)
        row["partner_cell_before"] = list(c_b.cell)
        row["manhattan_before"] = manhattan(c_m.cell, c_b.cell)
        if n_m is None or n_b is None:
            row["verdict"] = "NOT_OBSERVABLE_unit_absent_next_turn"
            row["absent"] = [u for u, v in ((mover, n_m), (partner, n_b)) if v is None]
            rows.append(row)
            continue
        row["mover_cell_after"] = list(n_m.cell)
        row["partner_cell_after"] = list(n_b.cell)
        exchanged = (n_m.cell == c_b.cell and n_b.cell == c_m.cell)
        row["verdict"] = "EXCHANGED" if exchanged else "MISS"
        # observations, not gates: what else stood on the two cells afterwards
        others = sorted(u.id for u in nxt.own_units()
                        if u.id not in (mover, partner) and u.cell in (c_m.cell, c_b.cell))
        row["third_own_unit_on_either_cell_after"] = others
        rows.append(row)
    return rows


def summarise(rows):
    exchanged = [r for r in rows if r["verdict"] == "EXCHANGED"]
    misses = [r for r in rows if r["verdict"] == "MISS"]
    unobservable = [r for r in rows if r["verdict"].startswith("NOT_OBSERVABLE")]
    observable = len(exchanged) + len(misses)
    return {
        "exchanges_seen": len(rows),
        "observable": observable,
        "exchanged": len(exchanged),
        "misses": len(misses),
        "miss_rows": misses,
        "not_observable": len(unobservable),
        "not_observable_rows": unobservable,
        "rate_over_observable": (round(100.0 * len(exchanged) / observable, 2)
                                 if observable else None),
        "non_adjacent_before": [r for r in rows if r.get("manhattan_before") not in (None, 1)],
        "third_unit_cases": [r for r in rows if r.get("third_own_unit_on_either_cell_after")],
    }


def main() -> int:
    fixtures_only = "--fixtures-only" in sys.argv
    census = json.loads(CENSUS.read_text())
    census_rows = {r["game"]: r for r in census["rows"]}
    panel_targets = [r["game"] for r in census["rows"] if r["swaps"]]
    fixture_pairs = json.loads(FIXTURE_CONTROL.read_text())["pairs"]
    fixture_turns = {}
    for pair_key, turns in fixture_pairs.items():
        game = pair_key.rsplit(":", 1)[0]
        fixture_turns.setdefault(game, []).extend(turns)
    fixture_turns = {g: sorted(t) for g, t in fixture_turns.items()}

    result = {"control": "C-10 — A-1 realised-cells check",
              "task": "20260825-dance-cure-candidate-2-swap",
              "arm": str(INSTR.relative_to(REPO)),
              "cells_from": "the referee transcript via trace_detectors.build_trace",
              "pairs_from": "the S/X branch codes on the v5 wire",
              "gates": {}, "rows": []}

    with tempfile.TemporaryDirectory(prefix="cure2-c10-") as wd:
        wd = Path(wd)
        instr = wd / "instr.bin"
        sh.compile_text(INSTR.read_text(), instr, crate="cure2_arm_instrument_c10")

        cfg = json.loads(fh.CONFIG.read_text())
        fixture_rows = []
        for sit in fh.load_situations(None):
            spec = fh.spec_for(sit, cfg)
            transcript, commands = rt.run_binary_custom(instr, fp.make_referee(spec),
                                                        int(cfg["turns"]))
            rows = check_game(sit["id"], transcript, commands)
            seen = sorted(r["turn"] for r in rows)
            expected = fixture_turns.get(sit["id"], [])
            if seen != expected:
                raise GateError(f"{sit['id']}: exchange turns {seen} against the recorded "
                                f"{expected} in swap-loop-control.json (G-B)")
            fixture_rows.extend(rows)
            if rows:
                print(f"  {sit['id']}: {len(rows)} exchanges, row identity MATCH", flush=True)
        result["gates"]["G-B row identity (fixtures)"] = (
            f"PASS — {len(fixture_turns)} fixtures reproduce their recorded exchange turns "
            f"({len(fixture_rows)} exchanges)")
        result["rows"].extend(fixture_rows)
        result["fixture_summary"] = summarise(fixture_rows)

        panel_rows = []
        if not fixtures_only:
            pcfg = fp.load_config(PANEL_CFG)
            parent = wd / "parent.bin"
            parent_src = (PANEL_CFG.parent / pcfg["parent"]["source"]).resolve()
            sh.compile_text(parent_src.read_text(), parent, crate="cure2_parent_c10")
            jobs = {f"{j['spec']['map_id']}:{j['spec']['seat']}": j
                    for j in fp.build_jobs(pcfg, instr, parent)}
            for key in panel_targets:
                job = jobs[key]
                transcript, commands = rt.run_binary_custom(
                    instr, fp.make_referee(job["spec"]), job["turns"])
                rows = check_game(key, transcript, commands)
                if len(rows) != census_rows[key]["swaps"]:
                    raise GateError(f"{key}: {len(rows)} exchanges now against "
                                    f"{census_rows[key]['swaps']} in panel-swap-census.json (G-B)")
                panel_rows.extend(rows)
                bad = [r for r in rows if r["verdict"] != "EXCHANGED"]
                print(f"  {key}: {len(rows)} exchanges, row identity MATCH"
                      + (f", {len(bad)} NOT EXCHANGED" if bad else ""), flush=True)
            result["gates"]["G-B row identity (panel)"] = (
                f"PASS — {len(panel_targets)} panel games reproduce their recorded swap count "
                f"({len(panel_rows)} exchanges)")
            result["rows"].extend(panel_rows)
            result["panel_summary"] = summarise(panel_rows)

    result["gates"]["G-D unambiguous pairing"] = (
        "PASS — every exchange turn carried exactly one S and one X")
    total = summarise(result["rows"])
    result["total_summary"] = total
    result["gates"]["G-E observability"] = (
        f"{total['not_observable']} exchange(s) had no observable next-turn state; "
        f"they are excluded from the rate and listed, never counted as passes")
    result["verdict"] = ("PASS" if total["misses"] == 0 and total["observable"] == total[
        "exchanges_seen"] else
        "PASS_WITH_UNOBSERVED" if total["misses"] == 0 else "WITHDRAW — A-1 IS FALSE")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    printable = {k: v for k, v in total.items() if not isinstance(v, list)}
    print(json.dumps(printable, indent=1))
    print("miss rows:", json.dumps(total["miss_rows"]))
    print("not observable:", json.dumps(total["not_observable_rows"]))
    print("verdict:", result["verdict"])
    print("wrote", OUT.relative_to(REPO))
    return 0 if not total["misses"] else 1


if __name__ == "__main__":
    sys.exit(main())
