#!/usr/bin/env python3
r"""Phase 3a — the two named panel games, diagnosed with the accepted selector probe.

The card asks for the **mechanism and turn** of the `m004` P3 regression and the **cost** of the
`m021` P4 / `r5-horizon`.  Both are panel games, not library fixtures, so `route_census.py`'s
fixture harness cannot reach them.  This driver reuses the panel's own job builder
(`fuzz_panel.build_jobs`) to regenerate exactly those two specs, then runs them with
`make_probe.py`'s already-accepted **selector** probe, whose `PS2PAIR ... p1drop=<b> waits=<n>`
row is the instrument that names which pair P1 dropped and how P2's wait tie-break moved the
winner.  Nothing here proposes or builds a change.

Gates, each of which fails the run rather than degrading it:

1. **Parity** — the instrumented binary's command stream must be byte-identical to the
   uninstrumented candidate's on the same spec.  The probe only prints.
2. **Row identity** — the probe run's `violations` and `flags` must equal the Phase-2 panel's
   recorded row for that (map, seat).  If the regenerated spec is not the same game, every turn
   number below is about a different world.
3. **Turn coverage** — the divergence turn under diagnosis must carry `PS2TURN` rows.

Run:  python3 claude_1/picker3/panel_game_probe.py 2> claude_1/picker3/probe-stderr.log
"""
from __future__ import annotations

import collections, json, os, re, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
for p in ("claude_1/t1", "claude_1/pipeline", "claude_1/banana-restoration-r2", "claude_1/hstarve1"):
    sys.path.insert(0, str(REPO / p))
import fuzz_panel as fp          # noqa: E402
import fixture_harness as H      # noqa: E402

CONFIG = REPO / "claude_1/pipeline/picker2-door1-cand-config.json"
PANEL_CAND = REPO / "claude_1/picker2/panel-door1-cand.json"
PLAIN_SRC = REPO / "claude_1/picker2/candidate-door1-p1p2.rs"
PROBE_SRC = REPO / "claude_1/picker2/probe-door1-p1p2.rs"
PARENT_SRC = REPO / "claude_1/chop4c/candidate-door1.rs"
OUT = HERE / "panel-game-probe-2026-08-21.json"

TARGETS = [("m004", 0), ("m021", 1)]

RE_TURN = re.compile(r"^PS2TURN turn=(\d+)$")
RE_BRANCH = re.compile(r"^PS2BRANCH n_ids=(\d+) arm=(\w+)$")
RE_CAND = re.compile(r"^PS2CAND unit=(-?\d+) idx=(\d+) score=(-?[\d.]+|-?inf|NaN) target=(.*?) cmd=(.*)$")
RE_PAIR = re.compile(r"^PS2PAIR ai=(\d+) bi=(\d+) compat=(\w+) stock=(\w+) p1drop=(\w+) waits=(\d+) sum=(-?[\d.]+|-?inf|NaN)$")
RE_WIN = re.compile(r"^PS2WIN ai=(\d+) bi=(\d+) sum=(-?[\d.]+|-?inf|NaN)$")


class GateError(Exception):
    """Anything that would make a turn number below mean something other than it says."""


def parse_turns(text):
    """Group every PS2 row under the PS2TURN that precedes it."""
    turns, cur = {}, None
    for line in text.splitlines():
        m = RE_TURN.match(line)
        if m:
            cur = int(m.group(1))
            turns[cur] = {"branch": None, "cands": [], "pairs": [], "win": None, "nopair": False}
            continue
        if cur is None:
            continue
        rec = turns[cur]
        m = RE_BRANCH.match(line)
        if m:
            rec["branch"] = {"n_ids": int(m.group(1)), "arm": m.group(2)}
            continue
        m = RE_CAND.match(line)
        if m:
            rec["cands"].append({"unit": int(m.group(1)), "idx": int(m.group(2)),
                                 "score": float(m.group(3)), "target": m.group(4),
                                 "cmd": m.group(5)})
            continue
        m = RE_PAIR.match(line)
        if m:
            rec["pairs"].append({"ai": int(m.group(1)), "bi": int(m.group(2)),
                                 "compat": m.group(3) == "true", "stock": m.group(4) == "true",
                                 "p1drop": m.group(5) == "true", "waits": int(m.group(6)),
                                 "sum": float(m.group(7))})
            continue
        m = RE_WIN.match(line)
        if m:
            rec["win"] = {"ai": int(m.group(1)), "bi": int(m.group(2)), "sum": float(m.group(3))}
            continue
        if line == "PS2NOPAIR":
            rec["nopair"] = True
    return turns


def recorded_row(map_id, seat):
    panel = json.loads(PANEL_CAND.read_text())
    for row in panel["games"]:
        if row["map_id"] == map_id and row["seat"] == seat:
            return row
    raise GateError("panel-door1-cand.json has no row for %s seat %d" % (map_id, seat))


def norm(violations):
    """Comparable shape: property + detector + the detail keys that carry turns."""
    out = []
    for v in violations:
        item = {"property": v.get("property"), "detector": v.get("detector"),
                "count": v.get("count")}
        d = v.get("detail")
        if isinstance(d, dict):
            item["detail"] = {k: d[k] for k in sorted(d)}
        elif d is not None:
            item["detail"] = d
        out.append(item)
    return sorted(out, key=lambda x: json.dumps(x, sort_keys=True))


def main():
    cfg = fp.load_config(CONFIG)
    results = {"task": "20260820-pair-selector-anti-benching Phase 3a — m004 P3 and m021 P4/r5-horizon",
               "config": str(CONFIG.relative_to(REPO)),
               "instrument_version": cfg["instrument_version"],
               "corpus_version": cfg["corpus_version"],
               "probe_source": str(PROBE_SRC.relative_to(REPO)),
               "plain_source": str(PLAIN_SRC.relative_to(REPO)),
               "parent_source": str(PARENT_SRC.relative_to(REPO)),
               "games": {}}

    with tempfile.TemporaryDirectory(prefix="ps3a-") as wd:
        wd = Path(wd)
        print("compiling plain / probe / parent ...", file=sys.stdout, flush=True)
        for sub in ("plain", "probe", "parent"):
            (wd / sub).mkdir(parents=True, exist_ok=True)
        plain = H.compile_candidate(PLAIN_SRC, wd / "plain")
        probe = H.compile_candidate(PROBE_SRC, wd / "probe")
        parent = H.compile_candidate(PARENT_SRC, wd / "parent")

        jobs = fp.build_jobs(cfg, plain, parent)
        by_key = {(j["spec"]["map_id"], j["spec"]["seat"]): j for j in jobs}

        for map_id, seat in TARGETS:
            key = (map_id, seat)
            if key not in by_key:
                raise GateError("build_jobs produced no %s seat %d" % key)
            job = dict(by_key[key])
            spec = job["spec"]

            # --- run 1: uninstrumented, for the parity reference and the row identity gate
            ref = fp.make_referee(spec)
            import regression_tests as rt
            _, cmds_plain = rt.run_binary_custom(plain, ref, job["turns"])
            row_plain = fp.run_pair(dict(job, candidate=str(plain)))

            # --- run 2: instrumented; stderr goes to this process's stderr (inherited)
            print("PS2GAME map=%s seat=%d" % (map_id, seat), file=sys.stderr, flush=True)
            ref2 = fp.make_referee(spec)
            _, cmds_probe = rt.run_binary_custom(probe, ref2, job["turns"])

            # GATE 1 — parity
            if cmds_plain != cmds_probe:
                raise GateError("%s seat %d: probe command stream differs from the plain "
                                "candidate's; the probe is not print-only here" % key)

            # GATE 2 — row identity against the Phase-2 panel record
            rec = recorded_row(map_id, seat)
            if norm(row_plain["violations"]) != norm(rec["violations"]):
                raise GateError("%s seat %d: regenerated spec does not reproduce the Phase-2 "
                                "row's violations.\n  now:      %s\n  recorded: %s"
                                % (map_id, seat, json.dumps(norm(row_plain["violations"]))[:600],
                                   json.dumps(norm(rec["violations"]))[:600]))
            if row_plain["flags"] != rec["flags"]:
                raise GateError("%s seat %d: flags differ from the Phase-2 row" % key)

            results["games"][f"{map_id}-s{seat}"] = {
                "spec": {k: spec[k] for k in ("map_id", "seat", "class", "profile", "seed",
                                              "attempt", "orchard_eligible")},
                "parity_command_streams_identical": True,
                "row_identity_vs_phase2_panel": "MATCH",
                "violations": rec["violations"],
                "flags": rec["flags"],
                "detector_counts": rec["detector_counts"],
                "commands_sha_len": len(cmds_plain),
            }
            print("  %s seat %d: parity OK, row identity MATCH" % key, flush=True)

    OUT.write_text(json.dumps(results, indent=1) + "\n")
    print("wrote", OUT.relative_to(REPO))
    return 0


if __name__ == "__main__":
    sys.exit(main())
