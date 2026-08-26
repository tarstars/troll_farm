#!/usr/bin/env python3
"""The realised joint margin `rho` at every exchange of the six loop games.

Discharges review item 1 of codex_1's `20260826T071429Z` REVISION_REQUIRED: for each of the six
games in which the swap rule's C-5 loop was recorded, report the score inputs (`Delta`, `K`, `w`)
of BOTH units for BOTH trees at the first post-exchange turn, the realised `rho = S_B/S_A - 1`, and
whether the pre-registered `M = 0.25` is STRICTLY greater than it.

`S_A` is the KEEPING pair -- each unit re-scored at the post-exchange turn on the goal it held at
the exchange turn; `S_B` is the pair the selector actually chose there.  Both sums are over
PRE-BONUS chop scores `1000 * w / (Delta + K)`, which is the quantity the Candidate 3 rule would
compare; the post-bonus and post-penalty scores the selector compared are recorded alongside, so a
reader can see both and no claim rests on the difference being zero.

Gates, both fail-closed:
  G-A  print-only     -- the probe's command stream equals the plain instrument arm's, per game;
  G-B  same recording -- the exchange turns reproduce `claude_1/cure2/results/loop-anatomy.json`.

No Candidate 3 code is built or run.

    python3 claude_1/cure3/margin_probe.py
"""
from __future__ import annotations

import ast
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

CURE2 = REPO / "claude_1" / "cure2"
PANEL_CFG = CURE2 / "cure2-instrument-config.json"
RECORDED = CURE2 / "results" / "loop-anatomy.json"
PLAIN = CURE2 / "arm-instrument.rs"
PROBE = HERE / "arm-instrument-marginprobe.rs"
OUT = HERE / "results" / "margin-probe.json"

PANEL_GAMES = ["m078:0", "m090:0", "m090:1", "m118:1"]
FIXTURES = ["OSC-006", "OSC-007"]
M = 0.25

RE_CHOPIN = re.compile(
    r"^CHOPIN t=(\d+) u=(\d+) cell=(-?\d+),(-?\d+) tree=(-?\d+),(-?\d+) travel=(-?\d+) "
    r"chop=(-?\d+) ret=(-?\d+) turns=(-?\d+) wood=(-?\d+) score=(\S+) freecap=(-?\d+)$")
RE_CANDS = re.compile(r"^CANDS t=(\d+) u=(\d+) n=(\d+) list=(.*)$")
RE_TREE = re.compile(r"^TREE\((-?\d+),(-?\d+)\)$")


class GateError(Exception):
    pass


def run_capturing(binary, ref, turns):
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


def wire(commands):
    out = {}
    for line in commands.rstrip("\n").split("\n"):
        frags = n5.msg_fragments(line)
        if len(frags) != 1:
            raise GateError(f"{len(frags)} MSG fragments on a turn")
        turn, units, _order, _banner, meta = n5.decode(frags[0].strip())
        out[turn] = (units, meta)
    return out


def parse_stderr(text):
    """-> {turn: {"chopin": {(unit, tree): row}, "cands": {unit: [(command, score)]}}}"""
    by_turn = {}
    for line in text.splitlines():
        m = RE_CHOPIN.match(line)
        if m:
            t, u = int(m.group(1)), int(m.group(2))
            tree = (int(m.group(5)), int(m.group(6)))
            row = {"cell": (int(m.group(3)), int(m.group(4))), "tree": tree,
                   "travel": int(m.group(7)), "chop": int(m.group(8)),
                   "ret": int(m.group(9)), "turns": int(m.group(10)),
                   "wood": int(m.group(11)), "score_post": float(m.group(12)),
                   "freecap": int(m.group(13))}
            row["K"] = row["chop"] + row["ret"] + 1
            row["pre"] = 1000.0 * row["wood"] / row["turns"]
            by_turn.setdefault(t, {"chopin": {}, "cands": {}})["chopin"][(u, tree)] = row
            continue
        m = RE_CANDS.match(line)
        if m:
            t, u = int(m.group(1)), int(m.group(2))
            by_turn.setdefault(t, {"chopin": {}, "cands": {}})["cands"][u] = \
                ast.literal_eval(m.group(4))
    return by_turn


def tree_cell(goal):
    m = RE_TREE.match(goal or "")
    return (int(m.group(1)), int(m.group(2))) if m else None


def exchange_rows(key, rows, probe_rows, recorded_turns):
    """One row per exchange, from the wire and the probe."""
    out = []
    turns_seen = []
    for turn in sorted(rows):
        units, meta = rows[turn]
        if not meta["sw"]:
            continue
        turns_seen.append(turn)
        s_ids = sorted(u for u, v in units.items() if v[2] == "S")
        x_ids = sorted(u for u, v in units.items() if v[2] == "X")
        row = {"game": key, "turn": turn}
        if len(s_ids) != 1 or len(x_ids) != 1:
            row["status"] = "AMBIGUOUS_PAIR"
            out.append(row)
            continue
        mover, partner = s_ids[0], x_ids[0]
        nxt = rows.get(turn + 1)
        if nxt is None:
            row["status"] = "NO_POST_EXCHANGE_TURN"
            out.append(row)
            continue
        kept = {mover: tree_cell(units[mover][0]), partner: tree_cell(units[partner][0])}
        chosen = {uid: tree_cell(nxt[0].get(uid, (None,))[0]) for uid in (mover, partner)}
        row.update({"mover": mover, "partner": partner,
                    "kept": {str(u): list(c) if c else None for u, c in kept.items()},
                    "chosen": {str(u): list(c) if c else None for u, c in chosen.items()}})
        probe = probe_rows.get(turn + 1, {"chopin": {}, "cands": {}})
        inputs, missing = {}, []
        for uid in (mover, partner):
            for label, cell in (("kept", kept[uid]), ("chosen", chosen[uid])):
                if cell is None:
                    missing.append(f"u{uid}:{label}=not a tree")
                    continue
                got = probe["chopin"].get((uid, cell))
                if got is None:
                    missing.append(f"u{uid}:{label}=TREE{cell} not scored at t+1")
                    continue
                inputs[f"u{uid}:{cell[0]},{cell[1]}"] = got
        row["inputs"] = {k: v for k, v in inputs.items()}
        row["missing"] = missing
        if missing:
            row["status"] = "NOT_SCOREABLE"
            out.append(row)
            continue

        def pre(uid, cell):
            return probe["chopin"][(uid, cell)]["pre"]

        def post(uid, cell):
            return probe["chopin"][(uid, cell)]["score_post"]

        s_a = pre(mover, kept[mover]) + pre(partner, kept[partner])
        s_b = pre(mover, chosen[mover]) + pre(partner, chosen[partner])
        row["S_A_keeping_pre"] = s_a
        row["S_B_chosen_pre"] = s_b
        row["S_A_keeping_post"] = post(mover, kept[mover]) + post(partner, kept[partner])
        row["S_B_chosen_post"] = post(mover, chosen[mover]) + post(partner, chosen[partner])
        row["rho"] = s_b / s_a - 1.0 if s_a > 0 else None
        row["rho_post"] = (row["S_B_chosen_post"] / row["S_A_keeping_post"] - 1.0
                           if row["S_A_keeping_post"] > 0 else None)
        row["goals_traded"] = (chosen[mover] == kept[partner]
                               and chosen[partner] == kept[mover])
        row["margin_holds"] = (row["rho"] is not None and M > row["rho"])
        row["status"] = "OK"
        out.append(row)
    if recorded_turns is not None and turns_seen != recorded_turns:
        raise GateError(f"{key}: exchanges now at {turns_seen}, recorded {recorded_turns}")
    return out


def main() -> int:
    recorded = json.loads(RECORDED.read_text())["games"]
    rec_turns = {k: [e["turn"] for e in v["instrument"]["exchanges"]]
                 for k, v in recorded.items()}
    result = {"task": "20260826-candidate-3-keep-your-goal", "M": M,
              "ruling": "coordination/messages/codex_1/20260826T071429Z-20260826-candidate-3-"
                        "g0-r2-ack.md item 1",
              "gates": {}, "rows": []}
    with tempfile.TemporaryDirectory(prefix="cure3-margin-") as wd:
        wd = Path(wd)
        plain, probe = wd / "plain.bin", wd / "probe.bin"
        sh.compile_text(PLAIN.read_text(), plain, crate="cure3_margin_plain")
        sh.compile_text(PROBE.read_text(), probe, crate="cure3_margin_probe")

        def one(key, spec_ref, turns):
            _, plain_cmds = rt.run_binary_custom(plain, spec_ref(), turns)
            _, probe_cmds, err = run_capturing(probe, spec_ref(), turns)
            if plain_cmds != probe_cmds:
                raise GateError(f"{key}: probe is NOT print-only")
            rows = wire(plain_cmds)
            out = exchange_rows(key, rows, parse_stderr(err), rec_turns.get(key))
            print(f"  {key}: parity OK, {len(out)} exchanges", flush=True)
            return out

        fcfg = json.loads(fh.CONFIG.read_text())
        for sit in fh.load_situations(FIXTURES):
            spec = fh.spec_for(sit, fcfg)
            result["rows"] += one(sit["id"], lambda spec=spec: fp.make_referee(spec),
                                  int(fcfg["turns"]))
        cfg = fp.load_config(PANEL_CFG)
        parent = wd / "parent.bin"
        parent_src = (PANEL_CFG.parent / cfg["parent"]["source"]).resolve()
        sh.compile_text(parent_src.read_text(), parent, crate="cure3_margin_parent")
        jobs = {f"{j['spec']['map_id']}:{j['spec']['seat']}": j
                for j in fp.build_jobs(cfg, plain, parent)}
        for key in PANEL_GAMES:
            job = jobs[key]
            result["rows"] += one(key, lambda spec=job["spec"]: fp.make_referee(spec),
                                  job["turns"])
    result["gates"]["G-A print-only"] = "PASS on all six games"
    result["gates"]["G-B recorded exchange turns reproduced"] = "PASS on all six games"
    ok = [r for r in result["rows"] if r["status"] == "OK"]
    bad = [r for r in result["rows"] if r["status"] != "OK"]
    result["summary"] = {
        "exchanges": len(result["rows"]),
        "scoreable": len(ok),
        "not_scoreable": [{"game": r["game"], "turn": r["turn"], "status": r["status"],
                           "missing": r.get("missing")} for r in bad],
        "max_rho": max((r["rho"] for r in ok), default=None),
        "max_rho_at": max(ok, key=lambda r: r["rho"])["game"] + ":"
                      + str(max(ok, key=lambda r: r["rho"])["turn"]) if ok else None,
        "min_K": min((v["K"] for r in ok for v in r["inputs"].values()), default=None),
        "min_Delta": min((v["travel"] for r in ok for v in r["inputs"].values()), default=None),
        "margin_holds_everywhere": all(r["margin_holds"] for r in ok),
        "violations": [f'{r["game"]}:{r["turn"]}' for r in ok if not r["margin_holds"]],
    }
    OUT.write_text(json.dumps(result, indent=1, sort_keys=True, default=str) + "\n")
    print(json.dumps(result["summary"], indent=1))
    print("wrote", OUT.relative_to(REPO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
