#!/usr/bin/env python3
"""G-1 runner for M-1 / M-2 — digest assertions, the two reads, the nine controls.

Task `20260825-dance-geometry-measurements`; definitions of record
`claude_1/geometry1/definitions-g0-2026-08-25-r2.md` (`DEFINITIONS_ACCEPTED`, codex_1
`20260825T142509Z`).  Writes three JSON files: every episode and every eligible turn whole, the
controls each with its number, and the two run digests.

    python3 claude_1/geometry1/run_geometry.py --inputs <dir> --out <dir>

`<dir>` holds the pinned replays at their repository paths (read-only):
`local_claude_1/narrate/games/*.json.gz`, `.../read2/…6652602….jsonl.gz`,
`.../v3/…6652642….jsonl.gz`, `local_claude_1/cure1/g2-games/…6659743….jsonl.gz`.

Carried caution on every number: **D-1 off replays is an upper bound.**
"""
from __future__ import annotations

import argparse
import collections
import glob
import gzip
import hashlib
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
for _p in (REPO / "claude_1" / "adapter1", REPO / "claude_1" / "banana-restoration-r2",
           REPO / "claude_1" / "narrate1", REPO / "claude_1" / "narrate3",
           REPO / "claude_1" / "narrate4", REPO / "claude_1" / "dance1",
           REPO / "claude_1" / "cure1", REPO / "claude_1" / "pipeline", HERE, REPO):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import geometry as geo                                          # noqa: E402
import narrate3_decode as n3                                    # noqa: E402
import narrate4_join as n4                                      # noqa: E402
import narrate_decode as nd                                     # noqa: E402
import regressive_baseline as rb                                # noqa: E402
import replay_to_trace as rt                                    # noqa: E402
import trace_detectors as td                                    # noqa: E402

# --- asserted imports (definitions r2 §1); a mismatch is a refusal ----------
IMPORTS = {
    "claude_1/adapter1/replay_to_trace.py": "df2f1187cb5b3187",
    "claude_1/cure1/regressive_baseline.py": "733fce408550c47e",
    "claude_1/banana-restoration-r2/trace_detectors.py": "59dce10dc87797bc",
    "claude_1/dance1/dance_facts.py": "1155cf266037d43a",
    "claude_1/dance1/narrate3_decode.py": "d791a7d0cba201fe",
    "claude_1/narrate1/narrate_decode.py": "d40a64af6569ba0e",
    "claude_1/narrate4/narrate4_join.py": "53e2c41ce264b6ce",
    "claude_1/cure1/cure1-hold-v4.rs": "cc4b308705883f10",
}
FACTS80_SHA = "7cd3631ce13205ec681941224b78834dbcbadc3a542495c145188cb08e8937b6"
G2_SHA = "45f5f22a1b2004886d59cc172586e0c132cae3b3e3c4c08e0d30ca742b4c90f9"
K3_SEED = 20260825
# K-7: the coordinator's shapes script, read from `origin/main` and asserted, never copied.
REREAD_SHA = "7c2c4b95"
REREAD_RESULT_SHA = ("8e2159e3ba114f61262bf853819a9ca7cfba59ae4e221ddf8e1e03cfae616596")

READS = {
    "older": [
        {"batch": "batch1", "agent": 6652424, "version": "v2", "kind": "dir",
         "path": "local_claude_1/narrate/games"},
        {"batch": "batch2", "agent": 6652602, "version": "v2", "kind": "jsonl",
         "path": "local_claude_1/narrate/read2/games-agent6652602-submission41182352.jsonl.gz"},
        {"batch": "batch3", "agent": 6652642, "version": "v3", "kind": "jsonl",
         "path": "local_claude_1/narrate/v3/games-agent6652642-submission41182608.jsonl.gz"},
    ],
    "v4": [
        {"batch": "v4", "agent": 6659743, "version": "v4", "kind": "jsonl",
         "path": "local_claude_1/cure1/g2-games/games-agent6659743-submission41192036.jsonl.gz"},
    ],
}


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def assert_imports():
    out = {}
    for rel, want in IMPORTS.items():
        got = sha256_file(REPO / rel)
        if not got.startswith(want):
            raise SystemExit("IMPORT DIGEST MISMATCH %s: %s != %s..." % (rel, got, want))
        out[rel] = got
    return out


# --- the v2 join shim (definitions r2 §3; controlled by K-9) ---------------

def v2_shim(game, agent_id):
    rows, meta = nd.decode_game(game, agent_id)
    for row in rows:
        kind, cell = row["intent_kind"], row["intent_cell"]
        row["chosen"] = kind if cell is None else "%s(%d,%d)" % (kind, cell[0], cell[1])
    return rows, meta


DECODERS = {"v2": v2_shim, "v3": n3.decode_game, "v4": n4.decode_game}


def load_games(inputs, spec):
    if spec["kind"] == "dir":
        for path in sorted(glob.glob(str(Path(inputs) / spec["path"] / "*.json.gz"))):
            with gzip.open(path, "rt", encoding="utf-8") as fh:
                yield json.load(fh)
    else:
        with gzip.open(Path(inputs) / spec["path"], "rt", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    yield json.loads(line)


# --------------------------------------------------------------------------

def episode_key(ep):
    return (ep["game"], ep["seat"], ep["f2_window"]["turn_start"])


def measure_episode(ep, trace, rows, read, spec, undetermined_sink):
    """One episode -> its whole record (r2 §R1-§R5)."""
    win = ep["f2_window"]
    t0, t1 = win["turn_start"], win["turn_end"]
    dancer = ep["f1_dancer"]["unit"]
    peers = ep.get("f3_peers") or []
    rec = {
        "read": read, "batch": spec["batch"], "agent": spec["agent"],
        "game": ep["game"], "seat": ep["seat"], "turn_start": t0, "turn_end": t1,
        "window_length_states": win["window_length_states"],
        "dancer": dancer, "mech": ep.get("mech"), "class": ep.get("class"),
        "scope_active": ep.get("scope_active"),
    }
    if len(peers) != 1:                     # K-8: refuse, never resolve by list order
        rec["refusal"] = "MULTIPLE_PEERS" if peers else "NO_PEER"
        rec["n_peers"] = len(peers)
        return rec
    peer = peers[0]["unit"]
    rec["teammate"] = peer

    by_tu = {(r["turn"], r["unit"]): r for r in rows}
    tent = trace.tent
    walkable = trace.smap.walkable
    dist_cache, moving_cache = {}, {}
    m1_rows, ineligible = [], collections.Counter()
    for t in range(t0, t1 + 1):
        if t < 1 or t > trace.T:
            ineligible["ineligible_off_trace"] += 1
            continue
        here = trace.pos(dancer, t)
        there = trace.pos(dancer, t + 1) if t + 1 <= trace.T else None
        if here is None:
            ineligible["ineligible_dancer_absent"] += 1
            continue
        row = by_tu.get((t, dancer))
        target = rb.target_cell(row["chosen"], tent) if row else None
        if target is None:
            ineligible["ineligible_no_target"] += 1
            continue
        if there is None:
            ineligible["ineligible_no_successor"] += 1
            continue
        own = {u.id: u.cell for u in trace.state(t).own_units()}
        if t not in moving_cache:
            moving_cache[t] = geo.moving_ids_at(trace, by_tu, t, tent, rb.target_cell)
        moving = moving_cache[t]
        r = geo.m1_row(trace, dancer, peer, t, target, own, dist_cache)
        r["branch"] = row.get("branch")
        # the observable forward-cell facts (r2 §R2's blocked_but_road_exists)
        unit = trace.unit(dancer, t)
        speed = unit.speed if unit is not None else 1
        f = geo.next_cell(walkable, here, target, speed)
        occ, kind = geo.occupant(trace, f, t)
        r["forward_cell"] = list(f)
        r["forward_cell_occupant_id"] = occ if kind == "known" else None
        r["forward_cell_occupant_is_teammate"] = (kind == "known" and occ == peer)
        r["forward_cell_blocked_observed"] = bool(kind == "known" and occ is not None
                                                  and trace.pos(dancer, t + 1) != f)
        r["arm_transient"] = geo.arm_transient(trace, f, t, moving)
        r["first_turn_of_window"] = (t == t0)
        r["forward_cell_occupant_is_mover"] = bool(occ is not None and kind == "known"
                                                   and occ in moving)
        r["_own_cells"] = sorted(own.values())
        m1_rows.append(r)
    rec["m1"] = m1_rows
    rec.update(ineligible)
    rec.update(geo.episode_cost_class(m1_rows))
    rec["blocked_but_road_exists"] = sum(
        1 for r in m1_rows if r["status"] == "OK" and not r["blocked"]
        and r["forward_cell_blocked_observed"])
    rec["blocked_with_lateral"] = sum(1 for r in m1_rows
                                      if r["blocked"] and r["lateral_exists"])
    rec["status_counts"] = dict(collections.Counter(r["status"] for r in m1_rows))
    return rec


def m2_for_episode(rec, ep, trace, rows, regressive_turns):
    """M-2 on the dancer's backward steps inside the window (r2 §R3)."""
    if "refusal" in rec:
        return
    t0, t1 = rec["turn_start"], rec["turn_end"]
    dancer, tent = rec["dancer"], trace.tent
    by_tu = {(r["turn"], r["unit"]): r for r in rows}
    out = []
    for t in sorted(x for x in regressive_turns if t0 <= x <= t1):
        here = trace.pos(dancer, t)
        row = by_tu.get((t, dancer))
        target = rb.target_cell(row["chosen"], tent) if row else None
        if here is None or target is None:
            continue
        unit = trace.unit(dancer, t)
        speed = unit.speed if unit is not None else 1
        f = geo.next_cell(trace.smap.walkable, here, target, speed)
        label, detail = geo.m2_classify(trace, f, t)
        moving = geo.moving_ids_at(trace, by_tu, t, tent, rb.target_cell)
        prev_row = by_tu.get((t - 1, dancer))
        entry = {
            "turn": t, "dancer_cell": list(here), "target": list(target),
            "forward_cell": list(f), "label": label,
            "arm_transient": geo.arm_transient(trace, f, t, moving),
            "branch": row.get("branch"),
            "first_turn_of_window": (t == t0),
            "forward_cell_off_map": f not in td.bfs_distances(trace.smap.walkable, [target]),
            "target_changed_this_turn": (prev_row is not None
                                         and prev_row.get("chosen") != row.get("chosen")),
        }
        entry.update(detail)
        out.append(entry)
    rec["m2"] = out
    rec["m2_counts"] = dict(collections.Counter(e["label"] for e in out))


# --------------------------------------------------------------------------
# K-3, the poison control (r2 §R5)
# --------------------------------------------------------------------------

def k3_pass(records, walk_by_game, tally):
    """r2 §R5: one draw per cost-bearing eligible turn, one RNG built once, consumed in the
    published total order -- read (older, then v4), then episode by (game, window start),
    then turn ascending.  An empty candidate set consumes NO draw."""
    rng = random.Random(K3_SEED)
    order = sorted((r for r in records if "refusal" not in r),
                   key=lambda r: (0 if r["read"] == "older" else 1, r["game"],
                                  r["episode_index"]))
    for rec in order:
        k3_for_episode(rec, walk_by_game[(rec["read"], rec["game"])], rng, tally)


def k3_for_episode(rec, walkable, rng, tally):
    if "refusal" in rec:
        return
    for r in sorted(rec["m1"], key=lambda x: x["turn"]):
        if r["status"] not in geo.COST_BEARING:
            continue
        x = tuple(r["dancer_cell"])
        m = tuple(r["teammate_cell"])
        target = tuple(r["target"])
        banned = {x, m, target} | {(x[0] + dx, x[1] + dy) for dx, dy in geo.ORTH}
        cands = sorted(c for c in walkable if c not in banned)
        if not cands:
            tally["K3_NO_CANDIDATE"] += 1
            r["k3"] = "K3_NO_CANDIDATE"
            continue
        c = cands[rng.randrange(len(cands))]
        tally["draws"] += 1
        occupied = {tuple(cell) for cell in r["_own_cells"]}
        if c in occupied:
            tally["draw_on_own_unit"] += 1
        dpoison = td.bfs_distances(walkable - {c}, [target])
        d0 = r["d0_metric"]
        if x not in dpoison:
            tally["blocked"] += 1
            r["k3"] = "POISON_UNREACHABLE"
        else:
            blocked = dpoison[x] > d0
            tally["blocked"] += int(blocked)
            r["k3"] = dpoison[x] - d0
    return


# --------------------------------------------------------------------------

def load_reread(reread_py):
    """Import the coordinator's shapes script under an asserted digest (K-7)."""
    import importlib.util
    got = sha256_file(reread_py)
    if not got.startswith(REREAD_SHA):
        raise SystemExit("REREAD DIGEST MISMATCH: %s != %s..." % (got, REREAD_SHA))
    spec = importlib.util.spec_from_file_location("reread_shapes", reread_py)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, got


def run(inputs, out_dir, reread_py):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    imports = assert_imports()
    reread, reread_sha = load_reread(reread_py)

    facts_path = REPO / "claude_1/dance1/results/dance-facts-instrument-2026-08-24.json"
    g2_path = REPO / "claude_1/cure1/results/g2-grade.json"
    if sha256_file(facts_path) != FACTS80_SHA or sha256_file(g2_path) != G2_SHA:
        raise SystemExit("INPUT DIGEST MISMATCH on the pinned fact files")
    facts80 = json.loads(facts_path.read_text())
    g2 = json.loads(g2_path.read_text())

    episodes = []
    for i, ep in enumerate(facts80):
        e = dict(ep)
        e["read"] = "older"
        e["episode_index"] = i
        episodes.append(e)
    v4_index = 0
    for g in g2["per_game"]:
        for ep in (g.get("episodes") or []):
            e = dict(ep)
            e["read"] = "v4"
            e["episode_index"] = v4_index
            v4_index += 1
            e["game"], e["seat"] = g["game"], g["seat"]
            e["agent"] = 6659743
            e["scope_active"] = g["scope_active"]
            episodes.append(e)

    # The shape join is by (read, episode_index) -- the episode's own position in its source
    # list -- and NOT by any derived key.  Found by execution: the older read carries two
    # distinct episodes with the same (game, seat, window start) -- 900093265/seat0/t=80 -- so a
    # position-derived key silently merges them and moves a shape count by one.  The join is
    # asserted one-to-one below rather than trusted.
    shapes = {}
    for e in episodes:
        d = reread.describe(dict(e, _read=e["read"], _game=e["game"]))
        shapes[(e["read"], e["episode_index"])] = d["shape"]
    if len(shapes) != len(episodes):
        raise SystemExit("SHAPE JOIN IS NOT ONE-TO-ONE: %d keys for %d episodes"
                         % (len(shapes), len(episodes)))
    derived = {(e["read"], e["game"], e["seat"], e["f2_window"]["turn_start"]) for e in episodes}
    shape_join = {"episodes": len(episodes), "keys": len(shapes),
                  "collisions_under_a_position_derived_key": len(episodes) - len(derived),
                  "verdict": "PASS" if len(shapes) == len(episodes) else "FAIL"}

    wanted = collections.defaultdict(list)          # (read, agent, game) -> [episode]
    for e in episodes:
        wanted[(e["read"], e["agent"], e["game"])].append(e)

    records, refusals = [], []
    walk_by_game = {}
    k3 = collections.Counter()
    # r3 §R4b: the agreement denominator is the COST-BEARING `R` rows only; the
    # non-cost-bearing ones are reported beside it, never inside it.
    k1 = {"rows": [], "agree": 0, "total": 0,
          "non_cost_bearing": [], "r_turns": 0, "r_turns_forward_cell_is_teammate": 0}
    k2 = {"total": 0, "free": 0, "exceptions": []}
    k6 = collections.Counter()
    k9 = {"checked": 0, "mismatch": []}

    for read in ("older", "v4"):
        for spec in READS[read]:
            need = {k[2] for k in wanted if k[0] == read and k[1] == spec["agent"]}
            if not need:
                continue
            for game in load_games(inputs, spec):
                gid = game.get("gameId")
                if gid not in need:
                    continue
                eps = wanted[(read, spec["agent"], gid)]
                try:
                    trace, _meta = rt.adapt_to_trace(game, agent_id=spec["agent"])
                except rt.AdapterError as exc:
                    for ep in eps:
                        refusals.append({"read": read, "game": gid, "reason": "ADAPTER_REFUSED",
                                         "detail": str(exc)})
                    continue
                decode = DECODERS[spec["version"]]
                try:
                    rows, _dmeta = decode(game, spec["agent"])
                except Exception as exc:                    # decode refusal
                    for ep in eps:
                        refusals.append({"read": read, "game": gid, "reason": "DECODE_REFUSED",
                                         "detail": "%s: %s" % (type(exc).__name__, exc)})
                    continue
                # regressive steps, read from the IMPORTED instrument's own verdicts
                regressive = collections.defaultdict(set)
                def sink(t, uid, verdict, _r=regressive):
                    if verdict == "MOVED_REGRESSIVE":
                        _r[uid].add(t)
                try:
                    rb.measure_game(game, spec["agent"], decode=decode, row_sink=sink)
                except Exception as exc:
                    refusals.append({"read": read, "game": gid, "reason": "MEASURE_REFUSED",
                                     "detail": str(exc)})
                for ep in eps:
                    rec = measure_episode(ep, trace, rows, read, spec, None)
                    rec["shape"] = shapes[(read, ep["episode_index"])]
                    rec["episode_index"] = ep["episode_index"]
                    m2_for_episode(rec, ep, trace, rows, regressive.get(rec.get("dancer"), set()))
                    walk_by_game[(read, gid)] = trace.smap.walkable
                    # K-9: the shim's target == the episode's own chosen_sequence
                    if spec["version"] == "v2" and "refusal" not in rec:
                        tel = ep.get("f4_telemetry") or {}
                        seq, turns = tel.get("chosen_sequence") or [], tel.get("turns") or []
                        by_tu = {(r["turn"], r["unit"]): r for r in rows}
                        for t, text in zip(turns, seq):
                            row = by_tu.get((t, rec["dancer"]))
                            if row is None:
                                continue
                            k9["checked"] += 1
                            a = rb.target_cell(row["chosen"], trace.tent)
                            b = rb.target_cell(text, trace.tent)
                            if a != b:
                                k9["mismatch"].append({"game": gid, "turn": t,
                                                       "shim": row["chosen"], "facts": text})
                    # K-1 / K-2 / K-6 on the v4 read's letters
                    if read == "v4" and "refusal" not in rec:
                        for r in rec["m1"]:
                            if r["branch"] == "R":
                                k1["r_turns"] += 1
                                k1["r_turns_forward_cell_is_teammate"] += int(
                                    r["forward_cell_occupant_is_teammate"])
                                ok = None
                                if r["status"] not in geo.COST_BEARING:
                                    # r3 §R4b: `d1 > d0` is deliberately undefined on
                                    # these rows, so they can neither agree nor disagree.
                                    k1["non_cost_bearing"].append({
                                        "game": gid, "turn": r["turn"],
                                        "status": r["status"],
                                        "occupant": r["forward_cell_occupant_id"],
                                        "teammate": rec["teammate"],
                                        "occupant_is_teammate":
                                            r["forward_cell_occupant_is_teammate"],
                                        "scope_active": rec["scope_active"],
                                        "first_turn_of_window": r["first_turn_of_window"],
                                        "category": "NON_COST_BEARING_STATUS",
                                    })
                                else:
                                    k1["total"] += 1
                                    ok = (r["forward_cell_occupant_is_teammate"]
                                          and r["blocked"])
                                    k1["agree"] += int(ok)
                                if r["status"] in geo.COST_BEARING and not ok:
                                    k1["rows"].append({
                                        "game": gid, "turn": r["turn"],
                                        "status": r["status"],
                                        "d0": r["d0_metric"], "d1": r["d1_metric"],
                                        "occupant": r["forward_cell_occupant_id"],
                                        "teammate": rec["teammate"],
                                        "scope_active": rec["scope_active"],
                                        "first_turn_of_window": r["first_turn_of_window"],
                                        "category": k1_category(r, rec),
                                    })
                            if r["branch"] == "P":
                                k2["total"] += 1
                                free = r["forward_cell_occupant_id"] is None
                                k2["free"] += int(free)
                                if not free:
                                    k2["exceptions"].append({
                                        "game": gid, "turn": r["turn"],
                                        "occupant": r["forward_cell_occupant_id"],
                                        "occupant_is_a_mover":
                                            r["forward_cell_occupant_is_mover"],
                                        "explained_by": ("OCCUPANT_IS_A_MOVER -- its cell is not "
                                                         "in `reserved` (cure1-hold-v4.rs:833)"
                                                         if r["forward_cell_occupant_is_mover"]
                                                         else "UNEXPLAINED")})
                            if r["branch"] in ("R", "H"):
                                k6["%s/%s" % (r["branch"], r["arm_transient"])] += 1
                    records.append(rec)

    k3_pass(records, walk_by_game, k3)
    for rec in records:
        for r in rec.get("m1", []):
            r.pop("_own_cells", None)

    # ---- controls with their numbers -------------------------------------
    per_read = collections.Counter(r["read"] for r in records)
    counts = collections.Counter()
    for r in records:
        if "refusal" in r:
            counts["refused"] += 1
            continue
        eligible = len(r["m1"])
        acc = (eligible + r.get("ineligible_no_target", 0)
               + r.get("ineligible_no_successor", 0) + r.get("ineligible_dancer_absent", 0)
               + r.get("ineligible_off_trace", 0))
        counts["k5_ok"] += int(acc == r["window_length_states"])
        counts["k5_bad"] += int(acc != r["window_length_states"])
    import subprocess, tempfile
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "reread.json"
        subprocess.run([sys.executable, str(reread_py), "--facts80", str(facts_path),
                        "--g2", str(g2_path), "--out", str(target)],
                       check=True, capture_output=True)
        k7_sha = sha256_file(target)
    k7 = {"published": REREAD_RESULT_SHA, "recomputed": k7_sha,
          "verdict": "PASS" if k7_sha == REREAD_RESULT_SHA else "FAIL"}

    k1_share = (k1["agree"] / k1["total"]) if k1["total"] else None
    controls = {
        "K-1_positive_R_v4": {
            "population": k1["total"], "agree": k1["agree"],
            "share": k1_share, "bar": 0.95,
            "verdict": ("VACUOUS - NOT MEASURED" if not k1["total"]
                        else "PASS" if k1_share >= 0.95 else "FAIL"),
            "disagreements": k1["rows"],
            "non_cost_bearing_excluded": len(k1["non_cost_bearing"]),
            "non_cost_bearing_rows": k1["non_cost_bearing"],
            "non_cost_bearing_statuses": dict(collections.Counter(
                d["status"] for d in k1["non_cost_bearing"])),
            "all_R_turns": k1["r_turns"],
            "all_R_turns_forward_cell_is_teammate": k1["r_turns_forward_cell_is_teammate"],
            "residue_scope_active_nonfirst": sum(
                1 for d in k1["rows"] if d["category"] == "UNOBSERVABLE_RESOLVER_STATE"
                and d["scope_active"] and not d["first_turn_of_window"]),
            "k1_residue_scope_disabled": sum(
                1 for d in k1["rows"] if d["category"] == "UNOBSERVABLE_RESOLVER_STATE"
                and not d["scope_active"]),
            "categories": dict(collections.Counter(d["category"] for d in k1["rows"])),
        },
        "K-2_negative_P_v4": {
            "population": k2["total"], "free": k2["free"],
            "verdict": ("VACUOUS - NOT MEASURED" if not k2["total"]
                        else "PASS" if k2["free"] == k2["total"]
                        else "EXCEPTIONS - ALL EXPLAINED" if all(
                            e["occupant_is_a_mover"] for e in k2["exceptions"])
                        else "EXCEPTIONS - UNEXPLAINED PRESENT"),
            "exceptions_explained_occupant_is_a_mover": sum(
                1 for e in k2["exceptions"] if e["occupant_is_a_mover"]),
            "exceptions": k2["exceptions"],
        },
        "K-3_poison": {"seed": K3_SEED, "draws": k3["draws"],
                       "blocked": k3["blocked"],
                       "share": (k3["blocked"] / k3["draws"]) if k3["draws"] else None,
                       "no_candidate_turns": k3["K3_NO_CANDIDATE"],
                       "draws_on_a_cell_holding_an_own_unit": k3["draw_on_own_unit"],
                       "order": ("read (older, then v4), then episode by (game, episode_index), "
                                 "then turn ascending; one randrange per drawing turn against "
                                 "the tuple-sorted candidate list"),
                       "note": "reported, not asserted"},
        "K-5_exhaustiveness": {"episodes_reconciled": counts["k5_ok"],
                               "episodes_off": counts["k5_bad"],
                               "refused": counts["refused"],
                               "episodes_total": len(records),
                               "per_read": dict(per_read),
                               "verdict": "PASS" if not counts["k5_bad"] else "FAIL"},
        "K-6_arm_transient_v4": {"counts": dict(k6),
                                 "H_population": sum(v for k, v in k6.items()
                                                     if k.startswith("H/")),
                                 "verdict": ("VACUOUS - NOT MEASURED (no H turns)"
                                             if not any(k.startswith("H/") for k in k6)
                                             else "REPORTED")},
        "K-8_peer_uniqueness": {"episodes": len(records),
                                "refused_multiple_or_no_peer":
                                sum(1 for r in records if "refusal" in r),
                                "verdict": "PASS" if not any(
                                    r.get("refusal") in ("MULTIPLE_PEERS", "NO_PEER")
                                    for r in records) else "REFUSALS"},
        "K-9_v2_shim_fidelity": {"checked": k9["checked"],
                                 "mismatches": len(k9["mismatch"]),
                                 "rows": k9["mismatch"][:50],
                                 "verdict": "PASS" if not k9["mismatch"] else "FAIL"},
        "K-7_reread_identity": k7,
        "shape_join_one_to_one": shape_join,
        "imports": imports,
        "reread_shapes_sha256": reread_sha,
    }

    results = {
        "task": "20260825-dance-geometry-measurements",
        "definitions": "claude_1/geometry1/definitions-g0-2026-08-25-r2.md",
        "caution": "D-1 off replays is an upper bound on every episode count here.",
        "episodes": sorted(records, key=lambda r: (r["read"], r["game"], r["turn_start"])),
        "refusals": refusals,
    }
    (out_dir / "geometry-2026-08-25.json").write_text(
        json.dumps(results, sort_keys=True, indent=1) + "\n")
    (out_dir / "controls-2026-08-25.json").write_text(
        json.dumps(controls, sort_keys=True, indent=1) + "\n")
    return results, controls


def k1_category(r, rec):
    """r2 §R4: only what a named field proves; everything else is the residual."""
    if r["status"] in ("OFF_BASELINE_MAP", "UNREACHABLE_D1"):
        return "OFF_MAP_ROW"
    if (r["status"] == "OK" and r["d1_metric"] == r["d0_metric"]
            and r["forward_cell_occupant_is_teammate"]):
        return "ROAD_AT_ZERO_COST"
    if r["forward_cell_occupant_id"] is None:
        return "FORBIDDEN_LANDING_CANDIDATE"
    if r["forward_cell_occupant_id"] != rec["teammate"]:
        return "FORWARD_CELL_NOT_TEAMMATE"
    return "UNOBSERVABLE_RESOLVER_STATE"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--peer", help="a second run's output dir; writes determinism-2026-08-25.json")
    ap.add_argument("--reread", required=True,
                    help="the coordinator's reread_shapes.py, read from origin/main")
    # r3: the determinism file used to carry the two absolute output paths, so a
    # reproduction in a temporary directory could not match it byte-for-byte even
    # with identical semantics (codex_1's G-1 note, 20260825T152653Z).  The labels
    # are now explicit inputs; the four hashes below them are the evidence.
    ap.add_argument("--label", default=None, help="presentation label for --out")
    ap.add_argument("--peer-label", default=None, help="presentation label for --peer")
    args = ap.parse_args(argv)
    results, controls = run(args.inputs, args.out, args.reread)
    if args.peer:
        names = ["geometry-2026-08-25.json", "controls-2026-08-25.json"]
        det = {"run_a": args.label or args.out,
               "run_b": args.peer_label or args.peer, "files": {}}
        same = True
        for n in names:
            a = sha256_file(Path(args.out) / n)
            b = sha256_file(Path(args.peer) / n)
            det["files"][n] = {"run_a": a, "run_b": b, "identical": a == b}
            same = same and a == b
        det["K-4_determinism"] = "PASS" if same else "FAIL"
        (Path(args.out) / "determinism-2026-08-25.json").write_text(
            json.dumps(det, sort_keys=True, indent=1) + "\n")
        print("K-4_determinism          %s" % det["K-4_determinism"])
    print("episodes: %d (refusals %d)" % (len(results["episodes"]), len(results["refusals"])))
    for key in sorted(controls):
        if key in ("imports", "reread_shapes_sha256"):
            continue
        print("%-24s %s" % (key, json.dumps({k: v for k, v in controls[key].items()
                                             if k not in ("disagreements", "rows",
                                                          "exceptions")},
                                            sort_keys=True)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
