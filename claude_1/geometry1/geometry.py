#!/usr/bin/env python3
"""M-1 / M-2 — the dance geometry measure, to the accepted definitions.

Task `20260825-dance-geometry-measurements`.  Definitions of record:
`claude_1/geometry1/definitions-g0-2026-08-25-r2.md`, ruled **DEFINITIONS_ACCEPTED** by codex_1
(`20260825T142509Z`) on `agent/claude_1@2dc0d03c`, redelivered at `858b5c37` with the census
paragraph.  This module implements that text and nothing else: it decides no bug, proposes no
cure, and asserts nothing about the arm's reasons that a replay field does not prove.

Everything the record already owns is IMPORTED, never paraphrased: the adapter, `bfs_distances`,
`measure_game` / `target_cell` / `manhattan`, `f3_peers`, and the three joins.  The two pieces of
new code are declared in the definitions and carry their controls: the Python transliteration of
the arm's `next_cell` (`cure1-hold-v4.rs:167-187`, licensed by K-1/K-6) and the v2 join shim
(licensed by K-9).

Carried caution on every number here: **D-1 off replays is an upper bound.**
"""
from __future__ import annotations

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

import trace_detectors as td                                   # noqa: E402
from regressive_baseline import manhattan, target_cell         # noqa: E402

ORTH = ((0, 1), (1, 0), (0, -1), (-1, 0))

# --------------------------------------------------------------------------
# The arm's next_cell, transliterated (cure1-hold-v4.rs:167-187).  Structure
# preserved: target within `speed` -> the target itself; target off the map
# from `current` -> BFS from the reachable cells of minimum Manhattan distance
# to it; then the reachable cell within `speed` minimising (to_target, cell),
# ties broken by the cell tuple exactly as Rust's min_by_key does.
# --------------------------------------------------------------------------

def next_cell(walkable, current, target, speed):
    from_current = td.bfs_distances(walkable, [current])
    d = from_current.get(target)
    if d is not None and d <= speed:
        return target
    if target not in from_current:
        if not from_current:
            return current
        best = min(manhattan(target, c) for c in from_current)
        goals = sorted(c for c in from_current if manhattan(target, c) == best)
        to_target = td.bfs_distances(walkable, goals)
    else:
        to_target = td.bfs_distances(walkable, [target])
    cands = [c for c, dist in from_current.items() if dist <= speed and c in to_target]
    if not cands:
        return current
    return min(cands, key=lambda c: (to_target[c], c))


# --------------------------------------------------------------------------
# M-1, per eligible turn (definitions r2 §R2 for the statuses, §R1 for the
# classes).  The BFS metric is the ONLY metric that enters d1 > d0, a cost, a
# median or a class; the arm's Manhattan fallback is a diagnostic field.
# --------------------------------------------------------------------------

COST_BEARING = ("OK", "UNREACHABLE_D1")


def m1_row(trace, dancer_uid, peer_uid, t, target, own_cells_t, dist_cache):
    """One eligible turn -> the whole row.  `own_cells_t` maps uid -> cell at t."""
    x = own_cells_t.get(dancer_uid)
    m = own_cells_t.get(peer_uid)
    walkable = trace.smap.walkable
    row = {
        "turn": t,
        "dancer_cell": list(x) if x else None,
        "teammate_cell": list(m) if m else None,
        "target": list(target),
        "d0_arm_fallback": manhattan(x, target) if x else None,
        "d1_arm_fallback": manhattan(x, target) if x else None,
        "d0_metric": None,
        "d1_metric": None,
        "cost": None,
        "cost_is_inf": False,
        "blocked": False,
        "lateral_exists": None,
    }
    if m is None:
        row["status"] = "TEAMMATE_ABSENT"
        return row
    if m == x:
        row["status"] = "TEAMMATE_ON_DANCER_CELL"
        return row
    if m == target:
        row["status"] = "TARGET_OCCUPIED"
        return row

    key0 = ("D0", target)
    if key0 not in dist_cache:
        dist_cache[key0] = td.bfs_distances(walkable, [target])
    d0map = dist_cache[key0]
    if x not in d0map:
        row["status"] = "OFF_BASELINE_MAP"
        return row
    d0 = d0map[x]
    row["d0_metric"] = d0

    key1 = ("D1", target, m)
    if key1 not in dist_cache:
        dist_cache[key1] = td.bfs_distances(walkable - {m}, [target])
    d1map = dist_cache[key1]

    # lateral exists -- an UPPER BOUND on the arm's L availability (r2 §4):
    # the arm also excludes `reserved` and `forbidden_for_non_priority`, which
    # are within-turn resolver state a replay does not carry.
    occupied = set(own_cells_t.values())
    lateral = False
    for dx, dy in ORTH:
        c = (x[0] + dx, x[1] + dy)
        if c in walkable and c != m and c not in occupied:
            if d0map.get(c, manhattan(c, target)) <= d0:
                lateral = True
                break
    row["lateral_exists"] = lateral

    if x not in d1map:
        row["status"] = "UNREACHABLE_D1"
        row["blocked"] = True
        row["cost_is_inf"] = True
        return row
    d1 = d1map[x]
    row["status"] = "OK"
    row["d1_metric"] = d1
    row["blocked"] = d1 > d0
    row["cost"] = d1 - d0          # >= 0; removing a cell can never shorten a road
    return row


def cost_key(row):
    """Total order on costs: 1 < 2 < ... < inf.  Only for blocked rows."""
    return (1, 0) if row["cost_is_inf"] else (0, row["cost"])


def episode_cost_class(rows):
    """r2 §R1: n/a with no eligible turn, 0 with no blocked turn, else the LOWER median."""
    population = [r for r in rows if r["status"] in COST_BEARING]
    blocked = sorted((r for r in population if r["blocked"]), key=cost_key)
    if not rows:
        return {"cost_class": "n/a", "cost_median": None, "cost_median_is_inf": False,
                "n_blocked": 0, "n_eligible": len(population)}
    if not blocked:
        return {"cost_class": "0", "cost_median": None, "cost_median_is_inf": False,
                "n_blocked": 0, "n_eligible": len(population)}
    mid = blocked[(len(blocked) - 1) // 2]          # LOWER median, never an average
    if mid["cost_is_inf"]:
        cls, median, is_inf = "inf", None, True
    else:
        c = mid["cost"]
        median, is_inf = c, False
        cls = "1-2" if c <= 2 else "3-5" if c <= 5 else ">5"
    return {"cost_class": cls, "cost_median": median, "cost_median_is_inf": is_inf,
            "n_blocked": len(blocked), "n_eligible": len(population)}


# --------------------------------------------------------------------------
# M-2, the charter partition as r2 §R3 makes it: identity-aware, mutually
# exclusive, with an explicit UNDETERMINED bucket.  Nothing is defaulted.
# --------------------------------------------------------------------------

def occupant(trace, cell, t):
    """(uid_or_None, 'known'|'unknown') -- the own unit on `cell` at turn `t`."""
    if t < 1 or t > trace.T:
        return None, "unknown"
    ids = [u.id for u in trace.state(t).own_units() if u.cell == cell]
    if len(ids) > 1:
        return ids, "multiple"
    return (ids[0] if ids else None), "known"


def m2_classify(trace, f, t):
    """r2 §R3 -> (label, detail).  Labels: STANDING / TRANSIENT / NOTHING_OF_OURS /
    UNDETERMINED."""
    u_t, k_t = occupant(trace, f, t)
    if k_t == "multiple":
        return "UNDETERMINED", {"reason": "MULTIPLE_OCCUPANTS", "occupants": u_t}
    if k_t == "unknown":
        return "UNDETERMINED", {"reason": "TURN_UNAVAILABLE", "unknown_turns": [t]}
    u_p, k_p = occupant(trace, f, t - 1)
    u_pp, k_pp = occupant(trace, f, t - 2)
    u_n, k_n = occupant(trace, f, t + 1)
    if "multiple" in (k_p, k_pp, k_n):
        return "UNDETERMINED", {"reason": "MULTIPLE_OCCUPANTS"}
    unknown_turns = [s for s, k in ((t - 1, k_p), (t - 2, k_pp), (t + 1, k_n))
                     if k == "unknown"]

    def tri(value, needs):
        """`value` when every turn in `needs` is known, else None (unknown)."""
        return None if any(s in unknown_turns for s in needs) else value

    if u_t is not None:
        t1 = tri(u_p != u_t, [t - 1])
        t2 = tri(u_p == u_t and u_pp != u_t, [t - 1, t - 2])
        t3 = tri(u_n != u_t, [t + 1])
        t4 = False
        preds = {"T1": t1, "T2": t2, "T3": t3, "T4": t4}
    else:
        t4 = tri(u_p is not None, [t - 1])
        preds = {"T1": False, "T2": False, "T3": False, "T4": t4}
    firing = sorted(k for k, v in preds.items() if v is True)
    if firing:
        return "TRANSIENT", {"transient_because": firing, "occupant": u_t}
    unknown_preds = sorted(k for k, v in preds.items() if v is None)
    if unknown_preds:
        return "UNDETERMINED", {"reason": "BOUNDARY_UNKNOWN",
                                "unknown_predicates": unknown_preds,
                                "unknown_turns": sorted(unknown_turns),
                                "occupant": u_t}
    if u_t is not None:
        return "STANDING", {"occupant": u_t}
    return "NOTHING_OF_OURS", {"occupant": None}


def moving_ids_at(trace, by_tu, t, tent, target_of):
    """The ARM's own `moving_ids` (cure1-hold-v4.rs:826-831), reconstructed.

    The arm projects each own unit's landing with `next_cell` from the target it CHOSE that turn
    (the NARRATE `chosen` field, which is pre-resolution) and calls a unit a mover exactly when
    that landing differs from its current cell.  The replayed command line is post-resolution and
    would misreport a denied mover, so the projection is used, not the verb.
    """
    out = set()
    walkable = trace.smap.walkable
    for u in trace.state(t).own_units():
        row = by_tu.get((t, u.id))
        if row is None:
            continue
        target = target_of(row["chosen"], tent)
        if target is None:
            continue
        if next_cell(walkable, u.cell, target, u.speed) != u.cell:
            out.add(u.id)
    return out


def arm_transient(trace, f, t, moving_ids):
    """The ARM's own predicate (cure1-hold-v4.rs:864-876), for K-6 only.

    `None => false` (an unknown previous cell is PERMANENT to the arm) is preserved.
    Returns True / False / 'unknown' when the turn itself is off the trace.
    """
    if t < 1 or t > trace.T:
        return "unknown"
    blocker = None
    for u in trace.state(t).own_units():
        if u.cell == f:
            blocker = u
            break
    if blocker is None:
        return None                     # `granted.contains(&landing)` -- resolver state
    if blocker.id in moving_ids:
        return True
    prev = trace.pos(blocker.id, t - 1) if t - 1 >= 1 else None
    if prev is None:
        return False                    # None => false, the arm's own rule
    return prev != f
