#!/usr/bin/env python3
"""Grade D-1 / D-2 / D-3 across our bot lineage on real ladder replays.

The question this answers: the 2026-08-23 grading found dancing (D-1) in 11 % of
the NARRATE instrument's real games.  Is that rate *old or new*?  The champion of
record ("door 1", `547fa706...`, which has no swap cure) and the two bots before it
played thousands of real ladder games and have never been graded.  This program
grades every one of them with the same instrument, on the same corpus, and reports
one row per (lineage x own-unit count).

INSTRUMENT.  Nothing here detects anything.  Detection is
`claude_1/adapter1/replay_to_trace.py` (the G-1 ACCEPTED replay->Trace adapter)
plus `claude_1/banana-restoration-r2/trace_detectors.detect_d1/d2/d3`, both taken
UNMODIFIED from an export of `agent/claude_1`, and the export is identity-checked
against the accepted panel's sha256 before a single game is read.  This program
supplies only: which games, which seat, which cohort, and the arithmetic.

SEAT.  Resolved from the replay's own `agents` array by `agentId`
(`resolve_seat(..., agent_id=...)` inside the adapter), never from a battle
listing's position -- `docs/METHODS-LEDGER.md`, `seat-from-the-replay`.  Our
account is `codingamer.userId == 1302251`, pseudonym `tass`
(`data/raw/players.json`).

PINNING.  Every agent id below is tied to a source sha256 by a written record,
cited per id in `PINS`.  An id that cannot be pinned goes to `unpinned` and is
excluded from every aggregate -- it is never guessed.

`units`.  Reproduces the 2026-08-23 grading's field exactly: the number of
DISTINCT own unit ids seen anywhere in the traced game (`len(trace.own_ids)`).
Verified against `g1-first-grading-2026-08-23.json` rows before use.

CAVEAT that travels with every D-1 number here: off replays D-1 is an UPPER
BOUND.  The adapter's own §6 -- plant clocks are reconstructed by the diff
decoder, a missed create/remove is a missed progress event, and a missed progress
event fails to break a window that should have been broken, so the error
direction INVENTS dancing.  It is applied identically to every cohort.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import multiprocessing
import os
import re
import sys

OUR_USER_ID = 1302251

PANEL_RELPATH = "claude_1/adapter1/results/adapter-panel-2026-08-23.json"
PANEL_SHA256 = "ce72ec22a4cf45fdd39e0909691057c559c781b6f6a993ed5d1094a7f85c1eea"


# --- the pinning table: agent id -> source sha256, with the record that pins it -

LINEAGE_ORDER = ["pre-cure-july", "very-old", "cure-C", "door-1", "instrument"]

SHA_JULY = "1a55319e8db6a19c26fdb1baaee5915aae43da254e1fdccc6c4afd8591c08ce0"
SHA_OLD = "98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29"
SHA_CURE_C = "ad3bfefe4b2326f4f6b4a270dc862ea19a0e319a1cddfde44b96cc6f6d35a5d1"
SHA_DOOR1 = "547fa706cc1c684a1f8c2a08174792d95e553b2382facfe15884d2ef544070b0"
SHA_INSTR_V2 = "aaebc503cc2660e920d45858767c6932575324085c93ef9345906f683b5a9271"
SHA_INSTR_V3 = "9a3e875823f3fc26bb7be04f67d872d5c5590f4479f771cae4402ed1e3281239"

# record paths are relative to the coordinator worktree
# /home/tarstars/prj/troll_farm-local_claude_1 unless they name a git object.
_D1N = "local_claude_1/door1-night-state.json"
_B1 = ("git show fe0ed7f8:local_claude_1/door1-vs-old-2026-08-20-state.json"
       " (session 3 block 1; the live ledger was rewritten when block 3 opened)")
_B2 = ("git show 0cd83d12:local_claude_1/door1-vs-old-2026-08-20-state.json"
       " (session 3 block 2; same rewrite)")
_CCN = "local_claude_1/cure-c-night-2026-08-18.md"
_AAA = "local_claude_1/narrate/aaaaa-block-2026-08-23.md"

PINS = [
    # --- pre-cure July lineage ------------------------------------------------
    dict(agent=6536563, lineage="pre-cure-july", sha256=SHA_JULY,
         source="cgauto/submissions/v1.2.2-farmcap.rs",
         record="data/README.md:46-47 (agentId 6536563, live code `v1.2.2-farmcap`"
                " per in-game MSG) + claude_1/block-index/block-index.json"
                " (`cgauto/submissions/v1.2.2-farmcap.rs` sha256 1a55319e...)",
         pin_strength="indirect: agent -> build name by in-game MSG, build name"
                      " -> file sha by the block index"),
    # --- very-old resident 98628e98 ------------------------------------------
    dict(agent=6593838, lineage="very-old", sha256=SHA_OLD,
         source="cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs",
         record=_CCN + ":15 (arm B source file names agent 6593838; sha 98628e98...)",
         pin_strength="direct"),
    dict(agent=6632048, lineage="very-old", sha256=SHA_OLD, source="idem",
         record=_CCN + ":15,52 (arm B = 98628e98...; read B1 agent 6632048)",
         pin_strength="direct"),
    dict(agent=6633209, lineage="very-old", sha256=SHA_OLD, source="idem",
         record=_CCN + ":15,54 (read B2)", pin_strength="direct"),
    dict(agent=6633935, lineage="very-old", sha256=SHA_OLD, source="idem",
         record=_CCN + ":15,56 (read B3)", pin_strength="direct"),
    dict(agent=6634792, lineage="very-old", sha256=SHA_OLD, source="idem",
         record=_CCN + ":15,58 (read B4)", pin_strength="direct"),
    dict(agent=6635217, lineage="very-old", sha256=SHA_OLD, source="idem",
         record=_CCN + ":15,60 (read B5)", pin_strength="direct"),
    dict(agent=6644257, lineage="very-old", sha256=SHA_OLD, source="idem",
         record=_B1 + " arms.B.sha256 = 98628e98...; reads[].label B1",
         pin_strength="direct"),
    dict(agent=6645217, lineage="very-old", sha256=SHA_OLD, source="idem",
         record=_B1 + " read B2", pin_strength="direct"),
    dict(agent=6646271, lineage="very-old", sha256=SHA_OLD, source="idem",
         record=_B1 + " read B3", pin_strength="direct"),
    dict(agent=6647102, lineage="very-old", sha256=SHA_OLD, source="idem",
         record=_B1 + " read B4", pin_strength="direct"),
    dict(agent=6647689, lineage="very-old", sha256=SHA_OLD, source="idem",
         record=_B1 + " read B5", pin_strength="direct"),
    dict(agent=6648091, lineage="very-old", sha256=SHA_OLD, source="idem",
         record=_B2 + " arms.B.sha256 = 98628e98...; read B1",
         pin_strength="direct"),
    dict(agent=6648682, lineage="very-old", sha256=SHA_OLD, source="idem",
         record=_B2 + " read B2", pin_strength="direct"),
    dict(agent=6649241, lineage="very-old", sha256=SHA_OLD, source="idem",
         record=_B2 + " read B3", pin_strength="direct"),
    dict(agent=6649868, lineage="very-old", sha256=SHA_OLD, source="idem",
         record=_B2 + " read B4", pin_strength="direct"),
    dict(agent=6650168, lineage="very-old", sha256=SHA_OLD, source="idem",
         record=_B2 + " read B5", pin_strength="direct"),
    # --- cure C ad3bfefe ------------------------------------------------------
    dict(agent=6631618, lineage="cure-C", sha256=SHA_CURE_C,
         source="cgauto/submissions/submitted-sub41153619-cure-c-quiet.rs",
         record=_CCN + ":14,50 (arm A = ad3bfefe...; read A1)",
         pin_strength="direct"),
    dict(agent=6632611, lineage="cure-C", sha256=SHA_CURE_C, source="idem",
         record=_CCN + ":14,53 (read A2)", pin_strength="direct"),
    dict(agent=6633433, lineage="cure-C", sha256=SHA_CURE_C, source="idem",
         record=_CCN + ":14,55 (read A3)", pin_strength="direct"),
    dict(agent=6634457, lineage="cure-C", sha256=SHA_CURE_C, source="idem",
         record=_CCN + ":14,57 (read A4)", pin_strength="direct"),
    dict(agent=6634986, lineage="cure-C", sha256=SHA_CURE_C, source="idem",
         record=_CCN + ":14,59 (read A5)", pin_strength="direct"),
    dict(agent=6640802, lineage="cure-C", sha256=SHA_CURE_C, source="idem",
         record=_D1N + " arms.B.sha256 = ad3bfefe...; reads[] label B1",
         pin_strength="direct"),
    dict(agent=6641617, lineage="cure-C", sha256=SHA_CURE_C, source="idem",
         record=_D1N + " read B2", pin_strength="direct"),
    dict(agent=6642442, lineage="cure-C", sha256=SHA_CURE_C, source="idem",
         record=_D1N + " read B3", pin_strength="direct"),
    dict(agent=6643172, lineage="cure-C", sha256=SHA_CURE_C, source="idem",
         record=_D1N + " read B4", pin_strength="direct"),
    dict(agent=6643465, lineage="cure-C", sha256=SHA_CURE_C, source="idem",
         record=_D1N + " read B5", pin_strength="direct"),
    # --- door 1 547fa706 (the champion of record; NO swap cure) ---------------
    dict(agent=6640462, lineage="door-1", sha256=SHA_DOOR1,
         source="cgauto/submissions/candidate-door1-pure-deletion.rs",
         record=_D1N + " arms.A.sha256 = 547fa706...; reads[] label A1",
         pin_strength="direct"),
    dict(agent=6641056, lineage="door-1", sha256=SHA_DOOR1, source="idem",
         record=_D1N + " read A2", pin_strength="direct"),
    dict(agent=6642046, lineage="door-1", sha256=SHA_DOOR1, source="idem",
         record=_D1N + " read A3", pin_strength="direct"),
    dict(agent=6642773, lineage="door-1", sha256=SHA_DOOR1, source="idem",
         record=_D1N + " read A4", pin_strength="direct"),
    dict(agent=6643278, lineage="door-1", sha256=SHA_DOOR1, source="idem",
         record=_D1N + " read A5", pin_strength="direct"),
    dict(agent=6643835, lineage="door-1", sha256=SHA_DOOR1, source="idem",
         record=_B1 + " arms.A.sha256 = 547fa706...; read A1",
         pin_strength="direct"),
    dict(agent=6644785, lineage="door-1", sha256=SHA_DOOR1, source="idem",
         record=_B1 + " read A2", pin_strength="direct"),
    dict(agent=6645883, lineage="door-1", sha256=SHA_DOOR1, source="idem",
         record=_B1 + " read A3", pin_strength="direct"),
    dict(agent=6646733, lineage="door-1", sha256=SHA_DOOR1, source="idem",
         record=_B1 + " read A4", pin_strength="direct"),
    dict(agent=6647370, lineage="door-1", sha256=SHA_DOOR1, source="idem",
         record=_B1 + " read A5", pin_strength="direct"),
    dict(agent=6647954, lineage="door-1", sha256=SHA_DOOR1, source="idem",
         record=_B2 + " arms.A.sha256 = 547fa706...; read A1",
         pin_strength="direct"),
    dict(agent=6648254, lineage="door-1", sha256=SHA_DOOR1, source="idem",
         record=_B2 + " read A2", pin_strength="direct"),
    dict(agent=6648976, lineage="door-1", sha256=SHA_DOOR1, source="idem",
         record=_B2 + " read A3", pin_strength="direct"),
    dict(agent=6649705, lineage="door-1", sha256=SHA_DOOR1, source="idem",
         record=_B2 + " read A4", pin_strength="direct"),
    dict(agent=6650034, lineage="door-1", sha256=SHA_DOOR1, source="idem",
         record=_B2 + " read A5", pin_strength="direct"),
    dict(agent=6650438, lineage="door-1", sha256=SHA_DOOR1, source="idem",
         record="docs/STATE.md:15-17 (champion of record: submission 41178858 /"
                " agent 6650438, source candidate-door1-pure-deletion.rs, SHA-256"
                " 547fa706...) + local_claude_1/door1-vs-old-pooled-verdict-"
                "2026-08-22.md ('opened block 3 and submitted arm A"
                " (submission 41178858)')",
         pin_strength="direct"),
    # --- instrument: swap R-1 + NARRATE telemetry -----------------------------
    dict(agent=6652424, lineage="instrument", sha256=SHA_INSTR_V2,
         source="local_claude_1/narrate/instrument-swap-r1-narrate-v2-"
                "SUBMITTED-2026-08-23.rs",
         record=_AAA + ":7-8,16 (arm sha aaebc503...; read 1 submission 41182039"
                       " / agent 6652424)", pin_strength="direct"),
    dict(agent=6652602, lineage="instrument", sha256=SHA_INSTR_V2, source="idem",
         record=_AAA + ":7-8,17 (read 2 submission 41182352 / agent 6652602)",
         pin_strength="direct"),
    dict(agent=6652642, lineage="instrument", sha256=SHA_INSTR_V3,
         source="local_claude_1/narrate/instrument-swap-r1-narrate-v3-"
                "SUBMITTED-2026-08-23.rs",
         record=_AAA + ":76-78 (NARRATE v3, submission 41182608, sha 9a3e8758...)"
                       " + docs/STATE.md:15-17 (live: 41182608 / 6652642)",
         pin_strength="direct"),
]

# Ids the brief names but which no written record pins to a source sha.
UNPINNED = [
    dict(agent=6536359, claimed_lineage="pre-cure-july",
         reason="data/README.md:50 counts it only as '(+1 where tass appears in a"
                " top player's list)' -- an earlier agent of ours whose source is"
                " named nowhere. The 2026-08-23 grading folded it into OLD-ours;"
                " here it is EXCLUDED from every aggregate rather than guessed.",
         corpus_games=None),
]

LINEAGE_OF = {p["agent"]: p["lineage"] for p in PINS}
UNPINNED_IDS = {u["agent"] for u in UNPINNED}


# --- corpus indexing --------------------------------------------------------

AGENTS_RE = re.compile(r'"agents"\s*:\s*\[')
TAIL_BYTES = 16384


def agents_of_file(path):
    """The replay's own `agents` array.

    It sits at the end of the file, so read the tail; fall back to a full parse
    when the tail does not carry it.  Fail-closed: a file whose agents array
    cannot be read raises, and the caller lists it as refused.
    """
    size = os.path.getsize(path)
    with open(path, "rb") as fh:
        if size > TAIL_BYTES:
            fh.seek(size - TAIL_BYTES)
        blob = fh.read()
    text = blob.decode("utf-8", errors="ignore")
    last = None
    for last in AGENTS_RE.finditer(text):
        pass
    if last is None:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh).get("agents")
    return json.JSONDecoder().raw_decode(text[last.end() - 1:])[0]


def index_corpus(corpus_dir):
    """{game_id: [[seat, agent_id, user_id, pseudo], ...]} plus refusals."""
    index, refused = {}, []
    for name in sorted(os.listdir(corpus_dir)):
        if not name.endswith(".json"):
            continue
        gid = name[: -len(".json")]
        try:
            agents = agents_of_file(os.path.join(corpus_dir, name))
            if not agents:
                raise ValueError("no agents array")
            rows = sorted([int(a["index"]), int(a["agentId"]),
                           (a.get("codingamer") or {}).get("userId"),
                           (a.get("codingamer") or {}).get("pseudo")]
                          for a in agents)
            index[gid] = rows
        except Exception as exc:                                  # noqa: BLE001
            refused.append({"corpus": "raw", "game": int(gid), "seat": None,
                            "agent": None, "cohort": None, "stage": "index",
                            "reason": "%s: %s" % (type(exc).__name__, exc)})
    return index, refused


# --- grading (worker side) --------------------------------------------------

_MOD = {}


def _worker_init(export_dir):
    sys.path.insert(0, os.path.join(export_dir, "claude_1", "adapter1"))
    sys.path.insert(0, export_dir)
    import replay_to_trace                                        # noqa: E402
    import trace_detectors                                        # noqa: E402
    _MOD["rt"] = replay_to_trace
    _MOD["td"] = trace_detectors


def _load(path):
    if path.endswith(".gz"):
        with gzip.open(path, "rb") as fh:
            return json.loads(fh.read().decode("utf-8"))
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def grade_one(task):
    """(corpus, path, game, seat, agent, cohort) -> row | refusal."""
    corpus, path, game, seat, agent, cohort = task
    rt, td = _MOD["rt"], _MOD["td"]
    try:
        replay = _load(path)
        trace, meta = rt.adapt_to_trace(replay, agent_id=agent)
        if seat is not None and meta["seat"] != seat:
            raise rt.AdapterError(
                "seat from the replay's agents array is %d, the index said %d"
                % (meta["seat"], seat))
        d1 = td.detect_d1(trace)
        d2 = td.detect_d2(trace)
        d3 = td.detect_d3(trace)
        for res in (d1, d2, d3):
            if res["count"] != len(res["episodes"]):
                raise ValueError("%s count %r != len(episodes) %d"
                                 % (res["detector"], res["count"],
                                    len(res["episodes"])))
        row = {"corpus": corpus, "game": int(game), "seat": meta["seat"],
               "agent": agent, "cohort": cohort,
               "units": len(trace.own_ids), "turns": meta["traced_turns"],
               "d1": d1["count"], "d2": d2["count"], "d3": d3["count"]}
        episodes = [dict(ep, corpus=corpus, game=int(game), seat=meta["seat"],
                         agent=agent, cohort=cohort) for ep in d1["episodes"]]
        return ("ok", row, episodes)
    except Exception as exc:                                      # noqa: BLE001
        return ("refused", {"corpus": corpus, "game": int(game), "seat": seat,
                            "agent": agent, "cohort": cohort, "stage": "grade",
                            "reason": "%s: %s" % (type(exc).__name__, exc)}, [])


def run_tasks(tasks, export_dir, workers):
    rows, episodes, refused = [], [], []
    if workers <= 1:
        _worker_init(export_dir)
        results = (grade_one(t) for t in tasks)
    else:
        pool = multiprocessing.Pool(workers, initializer=_worker_init,
                                    initargs=(export_dir,))
        results = pool.imap_unordered(grade_one, tasks, chunksize=16)
    for kind, payload, eps in results:
        if kind == "ok":
            rows.append(payload)
            episodes.extend(eps)
        else:
            refused.append(payload)
    if workers > 1:
        pool.close()
        pool.join()
    key = lambda r: (r["corpus"], r["game"], r["seat"])            # noqa: E731
    rows.sort(key=key)
    refused.sort(key=key)
    episodes.sort(key=lambda e: (e["corpus"], e["game"], e["seat"],
                                 e["unit"], e["turn_start"]))
    return rows, episodes, refused


# --- aggregation ------------------------------------------------------------

def aggregate(rows, key_of):
    agg = {}
    for r in rows:
        k = key_of(r)
        if k is None:
            continue
        a = agg.setdefault(k, {"games": 0, "turns": 0, "d1": 0, "d1_games": 0,
                               "d2": 0, "d2_games": 0, "d3": 0, "d3_games": 0})
        a["games"] += 1
        a["turns"] += r["turns"]
        for d in ("d1", "d2", "d3"):
            a[d] += r[d]
            if r[d]:
                a[d + "_games"] += 1
    for a in agg.values():
        a["d1_games_pct"] = round(100.0 * a["d1_games"] / a["games"], 2)
        a["d2_games_pct"] = round(100.0 * a["d2_games"] / a["games"], 2)
        a["d3_games_pct"] = round(100.0 * a["d3_games"] / a["games"], 2)
        a["d1_per_1000_turns"] = round(1000.0 * a["d1"] / a["turns"], 3) \
            if a["turns"] else None
        a["d2_per_1000_turns"] = round(1000.0 * a["d2"] / a["turns"], 3) \
            if a["turns"] else None
        a["d3_per_1000_turns"] = round(1000.0 * a["d3"] / a["turns"], 3) \
            if a["turns"] else None
    return {k: agg[k] for k in sorted(agg)}


# --- main -------------------------------------------------------------------

def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--corpus-dir", required=True,
                    help="data/raw/games/ (READ-ONLY)")
    ap.add_argument("--export-dir", required=True,
                    help="git-archive export of agent/claude_1 holding "
                         "claude_1/adapter1 + claude_1/banana-restoration-r2")
    ap.add_argument("--narrate-dir", required=True,
                    help="local_claude_1/narrate/games/ (149 *.json.gz), "
                         "control 1")
    ap.add_argument("--tracked-list", required=True,
                    help="file holding `git ls-files data/raw/games` output, "
                         "control 2")
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args(argv)

    # -- identity of the instrument, before anything is read -----------------
    panel = os.path.join(args.export_dir, PANEL_RELPATH)
    got = sha256_of(panel)
    if got != PANEL_SHA256:
        print("FATAL: adapter export identity check FAILED\n  %s\n  got      %s"
              "\n  expected %s" % (panel, got, PANEL_SHA256), file=sys.stderr)
        return 2
    print("instrument identity OK: %s = %s" % (PANEL_RELPATH, got))

    # -- index -----------------------------------------------------------------
    index, refused = index_corpus(args.corpus_dir)
    print("indexed %d replays in %s (%d refused at index)"
          % (len(index), args.corpus_dir, len(refused)))

    by_agent = {}
    our_agents_seen = set()
    for gid, agents in index.items():
        for seat, aid, uid, _pseudo in agents:
            if uid == OUR_USER_ID:
                our_agents_seen.add(aid)
            by_agent.setdefault(aid, []).append((gid, seat))

    # -- tasks -----------------------------------------------------------------
    tasks = []
    for pin in PINS:
        aid = pin["agent"]
        for gid, seat in sorted(by_agent.get(aid, [])):
            tasks.append(("raw", os.path.join(args.corpus_dir, gid + ".json"),
                          gid, seat, aid, pin["lineage"]))
            other = [row for row in index[gid] if row[0] != seat]
            if len(other) != 1:
                continue
            oseat, oaid = other[0][0], other[0][1]
            tasks.append(("raw", os.path.join(args.corpus_dir, gid + ".json"),
                          gid, oseat, oaid, pin["lineage"] + "-opponents"))

    # control 1: reproduce the 2026-08-23 grading over its own 149 replays
    narrate_files = sorted(f for f in os.listdir(args.narrate_dir)
                           if f.endswith(".json.gz"))
    for name in narrate_files:
        gid = name[: -len(".json.gz")]
        tasks.append(("narrate149", os.path.join(args.narrate_dir, name),
                      gid, None, 6652424, "control1-reproduction"))

    # control 2: detector-alive over the git-tracked in-repo games, both seats
    tracked = []
    with open(args.tracked_list, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                tracked.append(os.path.basename(line)[: -len(".json")])
    for gid in sorted(tracked):
        if gid not in index:
            refused.append({"corpus": "in-repo", "game": int(gid), "seat": None,
                            "agent": None, "cohort": "control2-detector-alive",
                            "stage": "index",
                            "reason": "git-tracked but absent from the corpus "
                                      "directory"})
            continue
        for seat, aid, _uid, _p in index[gid]:
            tasks.append(("in-repo",
                          os.path.join(args.corpus_dir, gid + ".json"),
                          gid, seat, aid, "control2-detector-alive"))

    print("grading %d (game, seat) traces on %d workers ..."
          % (len(tasks), args.workers))
    rows, episodes, grade_refused = run_tasks(tasks, args.export_dir,
                                              args.workers)
    refused.extend(grade_refused)
    refused.sort(key=lambda r: (r["corpus"], str(r["game"]),
                                r.get("seat") if r.get("seat") is not None
                                else -1))

    # -- controls --------------------------------------------------------------
    rep = [r for r in rows if r["cohort"] == "control1-reproduction"]
    rep2 = [r for r in rep if r["units"] == 2]
    rep_obs = {"games": len(rep2), "turns": sum(r["turns"] for r in rep2),
               "d1": sum(r["d1"] for r in rep2),
               "d1_games": sum(1 for r in rep2 if r["d1"]),
               "d2": sum(r["d2"] for r in rep2),
               "d3": sum(r["d3"] for r in rep2)}
    rep_want = {"games": 149, "turns": 38869, "d1": 22, "d1_games": 17,
                "d2": 0, "d3": 0}

    ctl2 = [r for r in rows if r["cohort"] == "control2-detector-alive"]
    ctl2_sorted = sorted(ctl2, key=lambda r: (r["game"], r["seat"]))
    prefix = ctl2_sorted[:240]
    control2 = {
        "scope": "all git-tracked in-repo games, both seats",
        "pairs": len(ctl2), "games": len(set(r["game"] for r in ctl2)),
        "turns": sum(r["turns"] for r in ctl2),
        "d1": sum(r["d1"] for r in ctl2), "d2": sum(r["d2"] for r in ctl2),
        "d3": sum(r["d3"] for r in ctl2),
        "prefix_240_pairs": {
            "note": "the 2026-08-23 handoff's control figure ('240 pairs / "
                    "70,562 turns, D-1 24 D-2 27 D-3 206') is the FIRST 240 "
                    "rows of that sweep in (game, seat) order -- the first 120 "
                    "games -- not the whole 290-game corpus. Reproduced here "
                    "for identity.",
            "pairs": len(prefix), "turns": sum(r["turns"] for r in prefix),
            "d1": sum(r["d1"] for r in prefix), "d2": sum(r["d2"] for r in prefix),
            "d3": sum(r["d3"] for r in prefix),
            "expected": {"pairs": 240, "turns": 70562, "d1": 24, "d2": 27,
                         "d3": 206}},
    }
    control2["prefix_240_pairs"]["identical"] = (
        {k: control2["prefix_240_pairs"][k] for k in
         ("pairs", "turns", "d1", "d2", "d3")}
        == control2["prefix_240_pairs"]["expected"])
    control2["detectors_alive"] = (control2["d1"] > 0 and control2["d2"] > 0
                                   and control2["d3"] > 0)

    # -- aggregates ------------------------------------------------------------
    lineage_rows = [r for r in rows if not r["cohort"].startswith("control")]
    agg = aggregate(lineage_rows, lambda r: "%s|units=%d" % (r["cohort"],
                                                             r["units"]))
    agg.update(aggregate([r for r in rows if r["cohort"].startswith("control")],
                         lambda r: "%s|units=%d" % (r["cohort"], r["units"])))
    per_agent = aggregate(
        [r for r in lineage_rows if not r["cohort"].endswith("-opponents")],
        lambda r: "agent:%d|%s|units=%d" % (r["agent"], r["cohort"], r["units"]))

    for u in UNPINNED:
        u["corpus_games"] = len(by_agent.get(u["agent"], []))

    ungraded_ours = sorted(a for a in our_agents_seen
                           if a not in LINEAGE_OF and a not in UNPINNED_IDS)

    out = {
        "title": "Dance lineage: D-1 / D-2 / D-3 on real ladder games, by pinned "
                 "bot generation and own-unit count",
        "generated_by": "local_claude_1/dance-lineage/grade_lineage.py",
        "instrument": "claude_1 replay->Trace adapter (G-1 ACCEPTED) + "
                      "trace_detectors detect_d1/d2/d3, both unmodified; export "
                      "identity sha256(%s) = %s" % (PANEL_RELPATH, PANEL_SHA256),
        "corpus": {"raw": os.path.abspath(args.corpus_dir),
                   "raw_replays_indexed": len(index),
                   "narrate149": os.path.abspath(args.narrate_dir),
                   "tracked_list": os.path.abspath(args.tracked_list)},
        "detectors": {
            "d1": "A->B->A movement with zero progress in window",
            "d2": "repeated PICK/DROP",
            "d3": "same-target / occupied-cell contention between OWN units"},
        "definitions": {
            "seat": "resolved from the replay's own `agents` array by agentId "
                    "(adapter resolve_seat), never a battle-listing position",
            "ours": "codingamer.userId == %d, pseudonym `tass`" % OUR_USER_ID,
            "units": "len(trace.own_ids) -- distinct own unit ids seen anywhere "
                     "in the traced game; reproduces the 2026-08-23 grading's "
                     "`units` field exactly (verified row-for-row)",
            "turns": "adapter meta.traced_turns",
            "d1_upper_bound": "off replays D-1 is an UPPER BOUND: plant clocks "
                              "are reconstructed, a missed create/remove is a "
                              "missed progress event, and the error direction "
                              "INVENTS dancing. Applied identically to every "
                              "cohort."},
        "cohorts": {
            "pre-cure-july": "agent 6536563, v1.2.2-farmcap, July Gold-era play",
            "very-old": "the very-old resident 98628e98... -- the bot that "
                        "produced the fixture library; never generates swaps",
            "cure-C": "cure C ad3bfefe...",
            "door-1": "the champion of record 547fa706..., cure C minus the "
                      "fictional-decay hunk; has NO swap cure",
            "instrument": "swap R-1 + NARRATE telemetry (v2 aaebc503..., "
                          "v3 9a3e8758...); can never be champion -- it changes "
                          "the command stream",
            "<lineage>-opponents": "the opponent seat of exactly the games in "
                                   "that lineage's row",
            "control1-reproduction": "the 149 replays of the 2026-08-23 grading",
            "control2-detector-alive": "the git-tracked in-repo games, both "
                                       "seats"},
        "lineage_order": LINEAGE_ORDER,
        "pins": PINS,
        "unpinned": UNPINNED,
        "ungraded_own_agents": {
            "note": "our account's agent ids present in the corpus that no "
                    "cohort claims; not graded, and no claim is made about them",
            "count": len(ungraded_ours), "agents": ungraded_ours},
        "controls": {
            "control1_reproduction": {
                "scope": "the 149 replays at %s, units==2"
                         % os.path.abspath(args.narrate_dir),
                "observed": rep_obs, "expected": rep_want,
                "identical": all(rep_obs[k] == rep_want[k] for k in rep_want)},
            "control2_detector_alive": control2,
            "control3_fail_closed": {
                "refused_total": len(refused),
                "by_reason": {},
                "note": "every refusal is listed in `refused`; nothing is "
                        "partially decoded"},
        },
        "aggregate": agg,
        "per_agent": per_agent,
        "rows": rows,
        "episodes": episodes,
        "refused": refused,
    }
    by_reason = {}
    for r in refused:
        head = r["reason"].split(";")[0][:120]
        by_reason[head] = by_reason.get(head, 0) + 1
    out["controls"]["control3_fail_closed"]["by_reason"] = \
        {k: by_reason[k] for k in sorted(by_reason)}

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
        fh.write("\n")
    print("wrote %s (%d rows, %d D-1 episodes, %d refused)"
          % (args.out, len(rows), len(episodes), len(refused)))
    print("control 1 reproduction identical: %s  %r"
          % (out["controls"]["control1_reproduction"]["identical"], rep_obs))
    print("control 2 detectors alive: %s  d1=%d d2=%d d3=%d over %d pairs"
          % (control2["detectors_alive"], control2["d1"], control2["d2"],
             control2["d3"], control2["pairs"]))
    print("control 2 prefix-240 identical to the 08-23 figure: %s"
          % control2["prefix_240_pairs"]["identical"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
