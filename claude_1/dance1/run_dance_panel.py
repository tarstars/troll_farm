#!/usr/bin/env python3
"""The real-game dance attribution panel: fact table, classes, controls, both passes.

Task: `20260824-real-game-dance-attribution`, step 2.  Definitions of record
`claude_1/dance1/definitions-g1-r3-2026-08-24.md`, ruled DEFINITIONS_ACCEPTED by codex_1
(`20260824T172730Z`).  This runs the definitions; it changes none of them.

    python3 claude_1/dance1/run_dance_panel.py --inputs DIR [--out-dir DIR] [--skip-k3-negative]

`--inputs` holds the pinned corpora, extracted from the record (see the report's provenance
table):

    batch1/                 149 replays, agent 6652424, NARRATE v2   (local_claude_1@3256dafb)
    batch2.jsonl.gz         160 replays, agent 6652602, NARRATE v2   (local_claude_1@3256dafb)
    batch3.jsonl.gz         160 replays, agent 6652642, NARRATE v3   (local_claude_1@3256dafb)
    champion.jsonl.gz       306 replays, door-1 lineage, NO telemetry (local_claude_1@4b9bd563)
    champion-manifest.json  the per-game agent id for the champion pass
    episodes-door1.json     the episode list of record, 382 rows

Determinism: the results file is written with `sort_keys=True` and carries no clock, so a second
run is byte-identical.
"""

from __future__ import annotations

import argparse
import collections
import glob
import gzip
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
for _p in (HERE, REPO / "claude_1" / "adapter1", REPO / "claude_1" / "banana-restoration-r2",
           REPO / "claude_1" / "narrate1", REPO / "claude_1" / "narrate3", REPO):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import dance_controls as dc                                   # noqa: E402
import dance_facts as df                                      # noqa: E402
import narrate_decode as nd                                   # noqa: E402
import narrate3_decode as n3                                  # noqa: E402
import replay_to_trace as rt                                  # noqa: E402
import trace_detectors as td                                  # noqa: E402

BATCHES = [
    {"batch": "batch1", "agent": 6652424, "version": "v2", "kind": "dir",
     "source": "local_claude_1/narrate/games/ @3256dafb"},
    {"batch": "batch2", "agent": 6652602, "version": "v2", "kind": "jsonl",
     "source": "local_claude_1/narrate/read2/games-agent6652602-submission41182352.jsonl.gz "
               "@3256dafb"},
    {"batch": "batch3", "agent": 6652642, "version": "v3", "kind": "jsonl",
     "source": "local_claude_1/narrate/v3/games-agent6652642-submission41182608.jsonl.gz "
               "@3256dafb"},
]


def load_games(inputs: Path, spec):
    if spec["kind"] == "dir":
        for path in sorted(glob.glob(str(inputs / spec["batch"] / "*.json.gz"))):
            with gzip.open(path, "rt", encoding="utf-8") as fh:
                yield json.load(fh)
    else:
        with gzip.open(inputs / (spec["batch"] + ".jsonl.gz"), "rt", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    yield json.loads(line)


def sha256_file(path: Path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# --------------------------------------------------------------------------

def grade_instrument_batch(inputs, spec, keep_traces=False):
    rows, refusals = [], []
    traces = {}
    d1 = d2 = d3 = 0
    d1_games = set()
    games = 0
    for game in load_games(inputs, spec):
        games += 1
        gid = game.get("gameId")
        try:
            tr, meta = rt.adapt_to_trace(game, agent_id=spec["agent"])
        except rt.AdapterError as exc:
            refusals.append({"game": gid, "stage": "adapter", "reason": str(exc)})
            continue
        seat = meta["seat"]
        r1 = td.detect_d1(tr)
        d1 += r1["count"]
        d2 += td.detect_d2(tr)["count"]
        d3 += td.detect_d3(tr)["count"]
        if r1["count"]:
            d1_games.add(gid)
        if keep_traces:
            traces[(gid, seat)] = (tr, r1["episodes"])
        if not r1["episodes"]:
            continue
        telemetry, reason = None, None
        try:
            if spec["version"] == "v3":
                trows, _tmeta = n3.decode_game(game, spec["agent"])
            else:
                trows, _tmeta = nd.decode_game(game, spec["agent"])
            telemetry = {(r["turn"], r["unit"]): r for r in trows}
        except (nd.NarrateError, n3.Narrate3Error) as exc:
            reason = str(exc)
            refusals.append({"game": gid, "stage": "telemetry", "reason": reason})
        for ep in r1["episodes"]:
            rows.append(df.episode_row(tr, ep, gid, spec["agent"], seat, telemetry,
                                       spec["version"], "instrument", reason))
    return {
        "batch": spec["batch"], "agent": spec["agent"], "version": spec["version"],
        "source": spec["source"], "games": games,
        "d1": d1, "d1_games": len(d1_games), "d2": d2, "d3": d3,
        "detector_episodes": d1,
        "refusals": refusals,
        "telemetry_refused_games": sum(1 for r in refusals if r["stage"] == "telemetry"),
        "rows": rows,
        "traces": traces,
    }


def grade_champion(inputs):
    manifest = json.loads((inputs / "champion-manifest.json").read_text())
    agent_by_game = {g["game_id"]: g["agent_id"] for g in manifest["games"]}
    of_record = json.loads((inputs / "episodes-door1.json").read_text())
    rows, refusals = [], []
    games = 0
    d1 = 0
    d1_games = set()
    observed_keys = set()
    with gzip.open(inputs / "champion.jsonl.gz", "rt", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            game = json.loads(line)
            games += 1
            gid = game.get("gameId")
            agent = agent_by_game.get(gid)
            if agent is None:
                refusals.append({"game": gid, "stage": "manifest",
                                 "reason": "game absent from the champion manifest"})
                continue
            try:
                tr, meta = rt.adapt_to_trace(game, agent_id=agent)
            except rt.AdapterError as exc:
                refusals.append({"game": gid, "stage": "adapter", "reason": str(exc)})
                continue
            r1 = td.detect_d1(tr)
            d1 += r1["count"]
            if r1["count"]:
                d1_games.add(gid)
            for ep in r1["episodes"]:
                observed_keys.add((gid, ep["unit"], ep["turn_start"], ep["turn_end"]))
                rows.append(df.episode_row(tr, ep, gid, agent, meta["seat"], None,
                                           None, "champion"))
    record_keys = {(e["game"], e["unit"], e["turn_start"], e["turn_end"]) for e in of_record}
    return {
        "batch": "champion", "agent": "door-1 lineage (16 agent ids)", "version": None,
        "source": "local_claude_1/dance-lineage/door1-games/ @4b9bd563",
        "games": games, "d1": d1, "d1_games": len(d1_games),
        "detector_episodes": d1,
        "episodes_of_record": len(of_record),
        "episode_identity_against_record": {
            "matched": len(observed_keys & record_keys),
            "only_here": sorted(observed_keys - record_keys)[:20],
            "only_in_record": sorted(record_keys - observed_keys)[:20],
            "exact": observed_keys == record_keys,
        },
        "refusals": refusals,
        "rows": rows,
        "traces": {},
    }


# --------------------------------------------------------------------------
# tables
# --------------------------------------------------------------------------

def tables(rows, pass_kind):
    classes = collections.Counter(r["class"] for r in rows)
    mech_counts = collections.Counter(r["mech"] for r in rows)
    swap_by_mech = collections.Counter(
        ("swap" if r["f5_swap"]["dancer_swap_ticks"] else "no_swap", r["mech"]) for r in rows)
    class_by_k = collections.Counter((r["class"], r["k_bucket"]) for r in rows)
    no_blocker_classes = ([df.SWAP_CLASS, "NO_TELEMETRY"] if pass_kind == "champion"
                          else [df.SWAP_CLASS, "GOAL_FLIP", "FIXED_TARGET_NO_BLOCKER",
                                "NO_TARGET", "UNCLASSIFIED"])
    mech_split = collections.Counter(
        (r["class"], r["mech"]) for r in rows if r["class"] in no_blocker_classes)
    late_sensitivity = [
        {"game": r["game"], "unit": r["f1_dancer"]["unit"],
         "turn_start": r["f2_window"]["turn_start"], "class": r["class"]}
        for r in rows
        if any(x["late_stationary_adjacent"] for x in r["f3b_late_peers"])
        and r["class"] in no_blocker_classes]
    short_lived = [
        {"game": r["game"], "unit": r["f1_dancer"]["unit"],
         "turn_start": r["f2_window"]["turn_start"], "class": r["class"],
         "blocker": r["f3_blocker"]["unit"] if r["f3_blocker"] else None,
         "turns_alive": (r["f3_blocker"]["turns_alive_in_window"]
                         if r["f3_blocker"] else None),
         "window_length": r["f2_window"]["window_length_states"]}
        for r in rows if r["blocker_short_lived"]]
    blocked = [r for r in rows if r["class"] in ("BLOCKED_BY_IDLE_TEAMMATE",
                                                 "BLOCKED_BY_WORKING_TEAMMATE")]
    to_game_end = collections.Counter(
        (r["k_bucket"], r["f3_blocker"]["distinct_cells_to_game_end"]) for r in blocked)
    f7 = collections.Counter(r["f7_end"]["label"] for r in rows)
    f4 = collections.Counter(r["f4_telemetry"]["label"] for r in rows)

    universe = (df.champion_classes() if pass_kind == "champion" else df.instrument_classes())
    class_table = {c: classes.get(c, "EMPTY") for c in universe}
    if pass_kind == "champion":
        for c in df.TELEMETRY_ONLY_CLASSES:
            class_table[c] = "n/a (no telemetry)"
    return {
        "classes": dict(classes),
        "class_table": class_table,
        "mech": dict(mech_counts),
        "swap_by_mech": {"%s|%s" % k: v for k, v in sorted(swap_by_mech.items())},
        "class_by_window_length": {"%s|%s" % k: v for k, v in sorted(class_by_k.items())},
        "mech_split_of_no_blocker_classes": {"%s|%s" % k: v for k, v in sorted(mech_split.items())},
        "late_peer_sensitivity": {"count": len(late_sensitivity), "rows": late_sensitivity},
        "blocker_liveness": {"count": len(short_lived), "rows": short_lived},
        "blocker_distinct_cells_to_game_end_by_k":
            {"%s|%s" % (a, b): v for (a, b), v in sorted(to_game_end.items())},
        "f7_end": dict(f7),
        "f4_labels": dict(f4),
    }


# --------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--inputs", required=True)
    ap.add_argument("--out-dir", default=str(HERE / "results"))
    ap.add_argument("--skip-k3-negative", action="store_true",
                    help="diagnostic only; a run with this flag never prints PASS")
    args = ap.parse_args(argv)

    inputs = Path(args.inputs).expanduser()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # K3's negative side runs FIRST, before a single episode is graded: it decides whether class 3
    # may carry the causal name `SWAP_FLAP` or must carry the descriptive `POSITIONAL_EXCHANGE`,
    # and the definitions pre-commit that remedy.  Deciding it after the counts were visible would
    # be exactly the boundary-with-the-counts-in-view the card forbids.
    if args.skip_k3_negative:
        k3_negative = {"pairs_scanned": 0, "clean": False, "ticks_total": None,
                       "games_with_ticks": None, "adapter_refusals": [],
                       "ticks_with_move_command_pair": None, "detail": [],
                       "skipped": "--skip-k3-negative: diagnostic run, never a PASS"}
    else:
        k3_negative = dc.k3_negative()
    df.set_swap_class_name("SWAP_FLAP" if k3_negative["clean"] else "POSITIONAL_EXCHANGE")
    print("K3 negative side: %s; class 3 graded as %s"
          % ("silent" if k3_negative["clean"]
             else "%s tick(s) in %s game x seat pairs" % (k3_negative["ticks_total"],
                                                          k3_negative["games_with_ticks"]),
             df.SWAP_CLASS), file=sys.stderr)

    graded = []
    for spec in BATCHES:
        keep = spec["batch"] == "batch1"          # K0 and K3's positive side need batch-1 traces
        graded.append(grade_instrument_batch(inputs, spec, keep_traces=keep))
        print("graded %s: %d games, D-1 %d episodes in %d games"
              % (spec["batch"], graded[-1]["games"], graded[-1]["d1"], graded[-1]["d1_games"]),
              file=sys.stderr)
    champion = grade_champion(inputs)
    print("graded champion: %d games, D-1 %d episodes in %d games"
          % (champion["games"], champion["d1"], champion["d1_games"]), file=sys.stderr)

    batch1_traces = graded[0]["traces"]

    controls = []
    controls.append(dc.k0_progress_agreement(batch1_traces))
    controls.append(dc.k1_identity(graded[0]))
    controls.append(dc.k2_mechanism_reproduction())
    controls.append(dc.k3_swap_detector(batch1_traces, k3_negative))
    controls.append(dc.k4_telemetry_decode([
        {"batch": g["batch"], "version": g["version"], "games": g["games"],
         "refused": g["telemetry_refused_games"]} for g in graded]))

    instrument_rows = [r for g in graded for r in g["rows"]]
    per_batch = []
    for g in graded:
        per_batch.append({
            "batch": g["batch"],
            "detector_episodes": g["detector_episodes"],
            "classes": collections.Counter(r["class"] for r in g["rows"]),
            "telemetry_refused_episodes": sum(
                1 for r in g["rows"] if r["f4_telemetry"]["label"] == "REFUSED"),
        })
    per_batch.append({
        "batch": "champion",
        "detector_episodes": champion["detector_episodes"],
        "classes": collections.Counter(r["class"] for r in champion["rows"]),
        "telemetry_refused_episodes": 0,
    })
    controls.append(dc.k5_exhaustiveness(per_batch))

    result = {
        "task": "20260824-real-game-dance-attribution",
        "definitions": "claude_1/dance1/definitions-g1-r3-2026-08-24.md (DEFINITIONS_ACCEPTED, "
                       "codex_1 20260824T172730Z)",
        "class_3_name_in_force": df.SWAP_CLASS,
        "caution": "D-1 off replays is an UPPER BOUND: the adapter reconstructs plant clocks and "
                   "the reconstruction error direction invents dancing. No count here may be "
                   "quoted without this sentence.",
        "batches": [{k: v for k, v in g.items() if k not in ("rows", "traces")} for g in graded],
        "champion": {k: v for k, v in champion.items() if k not in ("rows", "traces")},
        "instrument_pass": tables(instrument_rows, "instrument"),
        "instrument_pass_by_batch": {
            g["batch"]: tables(g["rows"], "instrument") for g in graded},
        "champion_pass": tables(champion["rows"], "champion"),
        "controls": controls,
        "controls_all_fired": all(c.get("fired") for c in controls),
        "controls_all_passed": all(c.get("passed") for c in controls),
    }
    result["status"] = "PASS" if (result["controls_all_fired"]
                                  and result["controls_all_passed"]) else "FAIL"

    (out_dir / "dance-panel-2026-08-24.json").write_text(
        json.dumps(result, indent=2, sort_keys=True, default=str) + "\n")
    (out_dir / "dance-facts-instrument-2026-08-24.json").write_text(
        json.dumps(instrument_rows, indent=2, sort_keys=True, default=str) + "\n")
    (out_dir / "dance-facts-champion-2026-08-24.json").write_text(
        json.dumps(champion["rows"], indent=2, sort_keys=True, default=str) + "\n")

    print(json.dumps({k: v for k, v in result.items()
                      if k not in ("controls", "instrument_pass_by_batch")},
                     indent=2, sort_keys=True, default=str))
    for c in controls:
        print("%-60s fired=%s passed=%s" % (c["control"], c.get("fired"), c.get("passed")),
              file=sys.stderr)
    print("STATUS %s" % result["status"], file=sys.stderr)
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
