#!/usr/bin/env python3
"""The fallback firing census on all 240 panel games, and the containment gate it feeds.

For each panel game the two print-only probes are run on the same spec the panel ran, and each
probe's command stream is compared against the stream the PANEL recorded for its own arm
(`games.jsonl.gz`, `parent_commands` for the champion and `candidate_commands` for arm-fix).  That
single comparison discharges two things at once:

  G-A  print-only  -- the probe plays exactly like its arm, so its stderr may be read at all;
  G-B  form parity -- the READABLE source probed here plays exactly like the COMPACTED source the
       panel ran, so a claim proved on one is a claim about the other.

Then, per game:

  fires_base / fires_fix   turns on which the fallback clause fired on each arm
  suppressed               turns on which arm-fix's new guard suppressed the second bank append
                           (carried > 0 && adjacent to the shack)
  diverged                 the panel's own two command streams differ (MSG stripped)

Pre-committed expectation (1) of the accepted G-0 packet is exactly: diverged => fires_base > 0.

    python3 claude_1/cure0/fallback_probe.py
"""
from __future__ import annotations

import gzip
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

import fuzz_panel as fp               # noqa: E402
import regression_tests as rt         # noqa: E402
import semantic_harness as sh         # noqa: E402
import narrate5 as n5                 # noqa: E402

CFG = HERE / "cure0-panel-config.json"
GAMES = Path("/tmp/claude-1000/cure0/games/games.jsonl.gz")
OUT = HERE / "results" / "fallback-probe.json"
PROBES = {"base": HERE / "arm-base-probe.rs", "fix": HERE / "arm-fix-probe.rs"}
RE_FIRE = re.compile(r"^FBFIRE t=(\d+) u=(\d+) carried=(\d+) plants=(\d+) adj=(\d) out=(\d+) "
                     r"ih=(\d+) bk=(\d+)$")


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


def main() -> int:
    cfg = fp.load_config(CFG)
    panel = {}
    for line in gzip.open(GAMES, "rt"):
        game = json.loads(line)
        panel[f"{game['map_id']}:{game.get('seat')}"] = game
    result = {"task": "20260826-candidate-0-regeneration-fallback", "gates": {}, "games": {}}
    with tempfile.TemporaryDirectory(prefix="cure0-probe-") as wd:
        wd = Path(wd)
        bins = {}
        for name, src in PROBES.items():
            bins[name] = wd / f"{name}-probe.bin"
            sh.compile_text(src.read_text(), bins[name], crate=f"cure0_probe_{name}")
        parent = wd / "parent.bin"
        parent_src = (CFG.parent / cfg["parent"]["source"]).resolve()
        sh.compile_text(parent_src.read_text(), parent, crate="cure0_probe_parent")
        cand = wd / "cand.bin"
        cand_src = (CFG.parent / cfg["candidate"]["source"]).resolve()
        sh.compile_text(cand_src.read_text(), cand, crate="cure0_probe_cand")
        jobs = fp.build_jobs(cfg, cand, parent)
        parity_fail, done = [], 0
        for job in jobs:
            spec, turns = job["spec"], job["turns"]
            key = f"{spec['map_id']}:{spec['seat']}"
            if key not in panel:
                raise GateError(f"{key}: panel has no row for this job")
            row = {"fires": {}, "suppressed": {}}
            for name in PROBES:
                _, probe_cmds, err = run_capturing(bins[name], fp.make_referee(spec), turns)
                field = "parent_commands" if name == "base" else "candidate_commands"
                ref_cmds = panel[key]["artifacts"][field]
                if probe_cmds.rstrip("\n") != ref_cmds.rstrip("\n"):
                    parity_fail.append({"game": key, "arm": name})
                    continue
                fires, supp = [], []
                for line in err.splitlines():
                    m = RE_FIRE.match(line)
                    if not m:
                        continue
                    turn, uid, carried, _plants, adj = (int(m.group(i)) for i in (1, 2, 3, 4, 5))
                    fires.append({"t": turn, "u": uid, "carried": carried, "adj": adj,
                                  "out": int(m.group(6)), "ih": int(m.group(7)),
                                  "bk": int(m.group(8))})
                    if carried > 0 and adj:
                        supp.append({"t": turn, "u": uid})
                row["fires"][name] = fires
                row["suppressed"][name] = supp
            a = [n5.strip_msg(l) for l in
                 panel[key]["artifacts"]["candidate_commands"].rstrip("\n").split("\n")]
            b = [n5.strip_msg(l) for l in
                 panel[key]["artifacts"]["parent_commands"].rstrip("\n").split("\n")]
            row["diverged"] = a != b
            row["first_divergence"] = None
            if row["diverged"]:
                for i, (x, y) in enumerate(zip(b, a), 1):
                    if x != y:
                        row["first_divergence"] = {"turn": i, "base": x, "fix": y}
                        break
            row["score_delta"] = (panel[key]["candidate"]["score"]
                                  - panel[key]["parent"]["score"])
            result["games"][key] = row
            done += 1
            if done % 40 == 0:
                print(f"  {done}/{len(jobs)} games", flush=True)
        if parity_fail:
            raise GateError(f"print-only/form parity FAILED on {len(parity_fail)}: "
                            f"{parity_fail[:5]}")
        result["gates"]["G-A print-only + G-B readable==compacted"] = (
            f"PASS on {done} games, both arms")

    games = result["games"]
    fired = [k for k, v in games.items() if v["fires"]["base"]]
    div = [k for k, v in games.items() if v["diverged"]]
    counterexamples = [k for k in div if not games[k]["fires"]["base"]]
    silent_changed = [k for k, v in games.items()
                      if not v["fires"]["base"] and v["score_delta"] != 0]
    result["summary"] = {
        "games": len(games),
        "games_where_champion_fallback_fires": len(fired),
        "diverging_games": len(div),
        "expectation_1_counterexamples": counterexamples,
        "changed_score_without_a_firing": silent_changed,
        "total_firings_base": sum(len(v["fires"]["base"]) for v in games.values()),
        "total_firings_fix": sum(len(v["fires"]["fix"]) for v in games.values()),
        "total_suppression_turns_fix": sum(len(v["suppressed"]["fix"]) for v in games.values()),
        "suppression_games_that_also_diverge": sorted(
            k for k, v in games.items() if v["suppressed"]["fix"] and v["diverged"]),
    }
    OUT.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    print(json.dumps(result["summary"], indent=1)[:1200])
    print("wrote", OUT.relative_to(REPO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
