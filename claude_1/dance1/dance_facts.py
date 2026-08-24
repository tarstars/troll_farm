#!/usr/bin/env python3
"""Real-game dance attribution: the fact table F1-F7, the mechanism layer, the classes.

Task: `20260824-real-game-dance-attribution`.  Definitions of record:
`claude_1/dance1/definitions-g1-r3-2026-08-24.md`, ruled **DEFINITIONS_ACCEPTED** by codex_1
(`20260824T172730Z`).  This module implements those definitions and nothing else: it decides no
bug, proposes no cure, and asserts nothing about any opponent's reasons.

Everything the record already owns is IMPORTED, never paraphrased:

- the detector: `trace_detectors.detect_d1`, unmodified;
- the adapter: `replay_to_trace`, unmodified;
- the blocker and IDLE criteria: `build_oscillation_library.measure_blocker` and
  `IDLE_WAIT_FRACTION`, unmodified, over the imported function's own population (peers alive at
  `turn_start`);
- the telemetry grammars: `narrate_decode` (v2) and `narrate3_decode` (v3, itself an import).

What is NEW carries the word NEW in the definitions and here: F3b (later-appearing peers),
`turns_alive_in_window`, the F4 summary labels, the F5 swap tick, F6, F7, `mech`, and the class
precedence.

Carried caution on every number this module produces: **D-1 off replays is an upper bound.**
Plant clocks are reconstructed by the adapter and the reconstruction error direction *invents*
dancing.  No count here may be quoted without it.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
for _p in (REPO / "claude_1" / "adapter1", REPO / "claude_1" / "banana-restoration-r2",
           REPO / "claude_1" / "narrate1", REPO / "claude_1" / "pipeline", HERE, REPO):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import replay_to_trace as rt                                  # noqa: E402
import trace_detectors as td                                  # noqa: E402
from build_oscillation_library import (                       # noqa: E402
    IDLE_WAIT_FRACTION, measure_blocker, orth,
)

# --------------------------------------------------------------------------
# progress(), re-stated from `detect_d1`'s own closure so F7 can ask "did the
# dancer make progress after the window".  It is a re-statement, not a second
# opinion: `dance_controls.K0` asserts it reports NO progress event on every
# transition strictly inside every window the detector emitted, which is the
# detector's own predicate.  A disagreement halts the panel.
# --------------------------------------------------------------------------

def progress_event(tr, uid, t):
    """Progress event for `uid` on the transition S_t -> S_{t+1} (A2)."""
    if t + 1 > tr.T:
        return True
    u0 = tr.unit(uid, t)
    u1 = tr.unit(uid, t + 1)
    if u0 is None or u1 is None:
        return True
    if u0.carry != u1.carry:
        return True
    cmd = tr.cmd_of(uid, t)
    if cmd is not None and cmd.verb in ("DROP", "PICK"):
        if tr.state(t).inventories[0] != tr.state(t + 1).inventories[0]:
            return True
    p0 = tr.state(t).plant_at(u0.cell)
    p1 = tr.state(t + 1).plant_at(u0.cell)
    if (p0 is None) != (p1 is None):
        return True
    return False


# --------------------------------------------------------------------------
# F1, F2
# --------------------------------------------------------------------------

def f1_dancer(tr, ep):
    uid = ep["unit"]
    u0 = tr.unit(uid, ep["turn_start"])
    u1 = tr.unit(uid, ep["turn_end"])
    return {
        "unit": uid,
        "speed": u0.speed, "capacity": u0.capacity,
        "harvest_power": u0.harvest_power, "chop_power": u0.chop_power,
        "carry_at_turn_start": list(u0.carry),
        "carry_at_turn_end": list(u1.carry) if u1 is not None else None,
    }


def f2_window(tr, ep):
    t0, t1 = ep["turn_start"], ep["turn_end"]
    return {
        "cell_a": list(ep["cells"][0]), "cell_b": list(ep["cells"][1]),
        "turn_start": t0, "turn_end": t1,
        "window_length_states": t1 - t0 + 1,
        "k": ep["k"],
    }


# --------------------------------------------------------------------------
# F3 / F3b -- peers.  F3 is the imported function verbatim; F3b is NEW and
# enters no class predicate.
# --------------------------------------------------------------------------

def f3_peers(tr, ep):
    """(blocker, peers) from the imported `measure_blocker`, plus the NEW liveness observable."""
    blocker, peers = measure_blocker(tr, ep)
    t0, t1 = ep["turn_start"], ep["turn_end"]
    for rec in peers:
        rec["turns_alive_in_window"] = sum(
            1 for t in range(t0, t1 + 1) if tr.pos(rec["unit"], t) is not None)
    if blocker is not None:
        # `blocker` is one of the `peers` records (same object), so it already carries the field.
        blocker = next(r for r in peers if r["unit"] == blocker["unit"])
    return blocker, peers


def f3b_late_peers(tr, ep):
    """NEW.  Own units absent at `turn_start` that appear later in the window."""
    uid = ep["unit"]
    t0, t1 = ep["turn_start"], ep["turn_end"]
    a, b = tuple(ep["cells"][0]), tuple(ep["cells"][1])
    adj = set(orth(a)) | set(orth(b))
    at_entry = {u.id for u in tr.state(t0).own_units()}
    later = {}
    for t in range(t0 + 1, t1 + 1):
        for u in tr.state(t).own_units():
            if u.id == uid or u.id in at_entry or u.id in later:
                continue
            later[u.id] = t
    out = []
    for pid, first in sorted(later.items()):
        cells = [tr.pos(pid, t) for t in range(first, t1 + 1)]
        cells = [c for c in cells if c is not None]
        n = t1 - first + 1
        waits = sum(1 for t in range(first, t1 + 1) if tr.cmd_of(pid, t) is None)
        entry_cell = tr.pos(pid, first)
        rec = {
            "unit": pid,
            "first_turn_present": first,
            "cell_at_first_presence": list(entry_cell) if entry_cell else None,
            "distinct_cells_from_first_presence": len(set(cells)),
            "wait_fraction_from_first_presence": round(waits / n, 4),
            "orth_adjacent_to_oscillation_cells": entry_cell in adj,
        }
        rec["late_stationary_adjacent"] = bool(
            rec["distinct_cells_from_first_presence"] == 1
            and rec["orth_adjacent_to_oscillation_cells"])
        out.append(rec)
    return out


# --------------------------------------------------------------------------
# F4 -- telemetry (the dancer's stated want).  NEW summary labels.
# --------------------------------------------------------------------------

def _periodic_period(seq):
    """Smallest p in 2..4 with seq[i] == seq[i+p] for all i, or None."""
    n = len(seq)
    for p in (2, 3, 4):
        if p >= n:
            break
        if all(seq[i] == seq[i + p] for i in range(n - p)):
            return p
    return None


def f4_label(chosen_seq):
    """`chosen_seq` is the per-turn `chosen` spelling over the whole window."""
    if not chosen_seq:
        return "MIXED", {}
    non_none = [c for c in chosen_seq if c != "NONE"]
    if not non_none:
        return "NONE", {}
    if len(non_none) == len(chosen_seq):
        distinct = sorted(set(non_none))
        if len(distinct) == 1:
            return "CONSTANT", {"target": distinct[0]}
        p = _periodic_period(chosen_seq)
        if p is not None:
            return "ALTERNATING", {"distinct_targets": distinct, "period": p}
    return "MIXED", {}


def f4_telemetry(ep, telemetry, version):
    """Per-turn `chosen` (and, on v3, `available`) for the dancer over the window.

    `telemetry` is {(turn, unit): row} for the game, or None when the game carries no telemetry
    (champion pass) or was refused whole.
    """
    uid, t0, t1 = ep["unit"], ep["turn_start"], ep["turn_end"]
    turns = list(range(t0, t1 + 1))
    chosen, available = [], []
    for t in turns:
        row = telemetry.get((t, uid))
        if row is None:
            # The dancer is alive on every turn of the window by construction (the detector reads
            # its position); a missing join row is a decode defect, not a NONE.
            raise KeyError("no telemetry row for unit %d on turn %d" % (uid, t))
        if version == "v3":
            chosen.append(row["chosen"])
            available.append(row["available"])
        else:
            kind, cell = row["intent_kind"], row["intent_cell"]
            chosen.append(kind if cell is None else "%s(%d,%d)" % (kind, cell[0], cell[1]))
    label, extra = f4_label(chosen)
    out = {"label": label, "chosen_sequence": chosen, "turns": turns}
    out.update(extra)
    if version == "v3":
        out["available_sequence"] = available
        out["available_has_real_target"] = any(
            a not in ("ABSENT", "NONE") for a in available)
    return out


def f4_refused(reason):
    return {"label": "REFUSED", "chosen_sequence": None, "refusal_reason": reason}


def f4_absent():
    """Champion pass: no telemetry exists at all.  Not `REFUSED`, which means a decode failure."""
    return {"label": "NO_TELEMETRY", "chosen_sequence": None}


# --------------------------------------------------------------------------
# F5 -- swap ticks.  NEW.  Purely positional, both legs in one transition.
# --------------------------------------------------------------------------

def f5_swaps(tr, ep):
    t0, t1 = ep["turn_start"], ep["turn_end"]
    lo = max(1, t0 - 2)
    hi = min(t1, tr.T - 1)
    uid = ep["unit"]
    ticks = []
    for t in range(lo, hi + 1):
        units = tr.state(t).own_units()
        pos_now = {u.id: u.cell for u in units}
        pos_next = {}
        for u in units:
            c = tr.pos(u.id, t + 1)
            if c is not None:
                pos_next[u.id] = c
        ids = sorted(pos_now)
        for i, a in enumerate(ids):
            for b in ids[i + 1:]:
                if a not in pos_next or b not in pos_next:
                    continue
                if pos_now[a] == pos_now[b]:
                    continue
                if pos_next[a] == pos_now[b] and pos_next[b] == pos_now[a]:
                    ticks.append({"turn": t, "pair": [a, b],
                                  "dancer_involved": uid in (a, b)})
    return {
        "ticks": ticks,
        "tick_count": len(ticks),
        "dancer_swap_ticks": sum(1 for x in ticks if x["dancer_involved"]),
        "f5_inspected_range": [lo, hi] if lo <= hi else None,
        "f5_lookback_turns_available": max(0, t0 - lo),
    }


def swap_ticks_whole_trace(tr):
    """Every swap tick in a whole trace -- K3's instrument, same predicate, no window."""
    out = []
    for t in range(1, tr.T):
        units = tr.state(t).own_units()
        pos_now = {u.id: u.cell for u in units}
        pos_next = {}
        for u in units:
            c = tr.pos(u.id, t + 1)
            if c is not None:
                pos_next[u.id] = c
        ids = sorted(pos_now)
        for i, a in enumerate(ids):
            for b in ids[i + 1:]:
                if a not in pos_next or b not in pos_next:
                    continue
                if pos_now[a] == pos_now[b]:
                    continue
                if pos_next[a] == pos_now[b] and pos_next[b] == pos_now[a]:
                    out.append({"turn": t, "pair": [a, b]})
    return out


# --------------------------------------------------------------------------
# F6 -- opponents.  Facts only; no claim about any opponent's reasons.
# --------------------------------------------------------------------------

def f6_opponents(tr, ep, f4):
    uid, t0, t1 = ep["unit"], ep["turn_start"], ep["turn_end"]
    a, b = tuple(ep["cells"][0]), tuple(ep["cells"][1])
    chosen = f4.get("chosen_sequence")
    per_turn = []
    for i, t in enumerate(range(t0, t1 + 1)):
        st = tr.state(t)
        opp = [u.cell for u in st.opp_units()]
        me = tr.pos(uid, t)
        target_cell = None
        if chosen is not None:
            spelling = chosen[i]
            if "(" in spelling:
                kind, _, rest = spelling[:-1].partition("(")
                xs, ys = rest.split(",")
                target_cell = (int(xs), int(ys))
        row = {
            "turn": t,
            "opponent_on_a": a in opp,
            "opponent_on_b": b in opp,
            "opponent_on_target": bool(target_cell is not None and target_cell in opp),
            "opponent_orth_adjacent_to_dancer": bool(
                me is not None and any(c in opp for c in orth(me))),
        }
        row["qualifies"] = any(row[k] for k in
                               ("opponent_on_a", "opponent_on_b", "opponent_on_target",
                                "opponent_orth_adjacent_to_dancer"))
        per_turn.append(row)
    n = len(per_turn)
    on_target = sum(1 for r in per_turn if r["opponent_on_target"])
    return {
        "per_turn": per_turn,
        "qualifying_turns": sum(1 for r in per_turn if r["qualifies"]),
        "turns": n,
        "opponent_on_target_turns": on_target,
        "opponent_on_target_at_least_half": bool(n and on_target * 2 >= n),
    }


# --------------------------------------------------------------------------
# F7 -- how it ended.  One label, fixed precedence, with the turn it fired.
# --------------------------------------------------------------------------

def f7_end(tr, ep, blocker, peers):
    uid, t0, t1 = ep["unit"], ep["turn_start"], ep["turn_end"]
    held_one_cell = [r["unit"] for r in peers if r["distinct_cells_in_window"] == 1]
    hold_cell = {}
    for pid in held_one_cell:
        c = tr.pos(pid, t0)
        if c is not None:
            hold_cell[pid] = c
    for t in range(t1 + 1, tr.T + 1):
        alive = tr.pos(uid, t) is not None
        # 1. progress.  Only asked when the dancer is alive on BOTH ends of the transition:
        #    `progress_event` returns True for a dead unit, and death is its own label below.
        if alive and t < tr.T and tr.pos(uid, t + 1) is not None:
            if progress_event(tr, uid, t):
                return {"label": "DANCER_PROGRESS", "turn": t}
        # 2. a peer that held one cell during the window moves off it.
        for pid, cell in sorted(hold_cell.items()):
            c = tr.pos(pid, t)
            if c is not None and c != cell:
                return {"label": "HOLDING_PEER_MOVED", "turn": t, "unit": pid}
        # 3. a swap tick involving the dancer.
        if alive and t < tr.T:
            here = tr.pos(uid, t)
            nxt = tr.pos(uid, t + 1)
            if nxt is not None and nxt != here:
                for u in tr.state(t).own_units():
                    if u.id == uid:
                        continue
                    if u.cell == nxt and tr.pos(u.id, t + 1) == here:
                        return {"label": "SWAP_TICK_WITH_DANCER", "turn": t, "unit": u.id}
        # 4. the dancer's death.
        if not alive:
            return {"label": "DANCER_DIED", "turn": t}
    return {"label": "GAME_END_NO_EVENT", "turn": None}


# --------------------------------------------------------------------------
# The mechanism layer -- F3 alone, telemetry structurally absent.
# --------------------------------------------------------------------------

MECH_VALUES = ("NO_PEERS", "BLOCKER_IDLE_ON_PLANT", "BLOCKER_IDLE_NO_PLANT",
               "BLOCKER_WORKING", "PEERS_NO_BLOCKER")

#: total function mech -> the frozen classifier's own output (many-to-one)
MECH_TO_LEGACY = {
    "NO_PEERS": "M3",
    "BLOCKER_IDLE_ON_PLANT": "M2",
    "BLOCKER_IDLE_NO_PLANT": "M1",
    "BLOCKER_WORKING": "M1",
    "PEERS_NO_BLOCKER": "UNCLASSIFIED",
}


def mech(blocker, peers):
    """The mechanism label.  Reads F3 and nothing else -- no telemetry, no swap, no F3b."""
    if not peers:
        return "NO_PEERS"
    if blocker is None:
        return "PEERS_NO_BLOCKER"
    if blocker["idle_by_analysis_criterion"]:
        return ("BLOCKER_IDLE_ON_PLANT" if blocker["plant_on_cell_at_entry"] is not None
                else "BLOCKER_IDLE_NO_PLANT")
    return "BLOCKER_WORKING"


# --------------------------------------------------------------------------
# The real-game classes.  Precedence 1-7, first match wins (instrument pass);
# 1-3 then NO_TELEMETRY with no further predicate (champion pass).
# --------------------------------------------------------------------------

#: The name of class 3.  The definitions (§3, K3) pre-commit the rename: "Any non-zero negative
#: result prevents the causal name `SWAP_FLAP`; the class is renamed to a purely descriptive
#: `POSITIONAL_EXCHANGE` and re-ruled, not footnoted."  The panel resolves this from K3's negative
#: side BEFORE it grades anything, and records which name it used; no code path may set it from a
#: class distribution.
SWAP_CLASS = "SWAP_FLAP"


def set_swap_class_name(name):
    global SWAP_CLASS
    if name not in ("SWAP_FLAP", "POSITIONAL_EXCHANGE"):
        raise ValueError("class 3 has exactly two permitted names: %r" % name)
    SWAP_CLASS = name


def instrument_classes():
    return ("BLOCKED_BY_IDLE_TEAMMATE", "BLOCKED_BY_WORKING_TEAMMATE", SWAP_CLASS,
            "GOAL_FLIP", "FIXED_TARGET_NO_BLOCKER", "NO_TARGET", "UNCLASSIFIED")


def champion_classes():
    return ("BLOCKED_BY_IDLE_TEAMMATE", "BLOCKED_BY_WORKING_TEAMMATE", SWAP_CLASS,
            "NO_TELEMETRY")


TELEMETRY_ONLY_CLASSES = ("GOAL_FLIP", "FIXED_TARGET_NO_BLOCKER", "NO_TARGET", "UNCLASSIFIED")


def classify_instrument(m, f4, f5, f6, version):
    """Classes 1-7, first match wins.  Returns (class, sub_tags, reason)."""
    if m == "BLOCKER_IDLE_ON_PLANT":
        return "BLOCKED_BY_IDLE_TEAMMATE", ["ON_PLANT"], "mech=BLOCKER_IDLE_ON_PLANT"
    if m == "BLOCKER_IDLE_NO_PLANT":
        return "BLOCKED_BY_IDLE_TEAMMATE", ["NOT_ON_PLANT"], "mech=BLOCKER_IDLE_NO_PLANT"
    if m == "BLOCKER_WORKING":
        return "BLOCKED_BY_WORKING_TEAMMATE", [], "mech=BLOCKER_WORKING"
    # no blocker from here down
    if f5["dancer_swap_ticks"] > 0:
        return SWAP_CLASS, [], "no blocker; %d dancer swap tick(s)" % f5["dancer_swap_ticks"]
    label = f4["label"]
    if label == "ALTERNATING":
        return "GOAL_FLIP", [], "no blocker; F4=ALTERNATING"
    if label == "CONSTANT":
        tags = ["OPPONENT_ON_TARGET"] if f6["opponent_on_target_at_least_half"] else []
        return "FIXED_TARGET_NO_BLOCKER", tags, "no blocker; F4=CONSTANT"
    if label == "NONE":
        if version == "v3" and f4.get("available_has_real_target"):
            return ("UNCLASSIFIED", ["AVAILABLE_REAL_TARGET"],
                    "no blocker; F4=NONE but the v3 discarded best candidate is a real target on "
                    "at least one window turn")
        return "NO_TARGET", [], "no blocker; F4=NONE throughout"
    if label == "REFUSED":
        return "UNCLASSIFIED", ["TELEMETRY_REFUSED"], "no blocker; telemetry refused whole"
    return "UNCLASSIFIED", [], "no blocker; F4=%s" % label


def classify_champion(m, f5):
    """Classes 1-3, then `NO_TELEMETRY` for every remaining row with no further predicate."""
    if m == "BLOCKER_IDLE_ON_PLANT":
        return "BLOCKED_BY_IDLE_TEAMMATE", ["ON_PLANT"], "mech=BLOCKER_IDLE_ON_PLANT"
    if m == "BLOCKER_IDLE_NO_PLANT":
        return "BLOCKED_BY_IDLE_TEAMMATE", ["NOT_ON_PLANT"], "mech=BLOCKER_IDLE_NO_PLANT"
    if m == "BLOCKER_WORKING":
        return "BLOCKED_BY_WORKING_TEAMMATE", [], "mech=BLOCKER_WORKING"
    if f5["dancer_swap_ticks"] > 0:
        return SWAP_CLASS, [], "no blocker; %d dancer swap tick(s)" % f5["dancer_swap_ticks"]
    return "NO_TELEMETRY", [], "no blocker, no swap tick; no telemetry exists on this pass"


# --------------------------------------------------------------------------
# One episode, end to end.
# --------------------------------------------------------------------------

def episode_row(tr, ep, game_id, agent_id, seat, telemetry, version, pass_kind,
                refusal_reason=None):
    """`telemetry`: {(turn, unit): row} | None.  `pass_kind`: 'instrument' | 'champion'."""
    blocker, peers = f3_peers(tr, ep)
    f3b = f3b_late_peers(tr, ep)
    m = mech(blocker, peers)
    if pass_kind == "champion":
        f4 = f4_absent()
    elif telemetry is None:
        f4 = f4_refused(refusal_reason or "telemetry refused")
    else:
        f4 = f4_telemetry(ep, telemetry, version)
    f5 = f5_swaps(tr, ep)
    f6 = f6_opponents(tr, ep, f4)
    f7 = f7_end(tr, ep, blocker, peers)

    if pass_kind == "champion":
        cls, tags, reason = classify_champion(m, f5)
    else:
        cls, tags, reason = classify_instrument(m, f4, f5, f6, version)
    if any(r["late_stationary_adjacent"] for r in f3b):
        tags = tags + ["LATE_PEER_STATIONARY_ADJACENT"]

    window_len = ep["turn_end"] - ep["turn_start"] + 1
    return {
        "game": game_id, "agent": agent_id, "seat": seat,
        "f1_dancer": f1_dancer(tr, ep),
        "f2_window": f2_window(tr, ep),
        "f3_peers": peers,
        "f3_blocker": blocker,
        "f3b_late_peers": f3b,
        "f4_telemetry": f4,
        "f5_swap": f5,
        "f6_opponents": f6,
        "f7_end": f7,
        "mech": m,
        "class": cls,
        "sub_tags": tags,
        "class_reason": reason,
        "blocker_short_lived": bool(
            blocker is not None and blocker["turns_alive_in_window"] < window_len),
        "k_bucket": "k=3" if ep["k"] == 3 else "k>3",
    }
