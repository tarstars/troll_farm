#!/usr/bin/env python3
"""The NARRATE **v4** decoder — task `20260825-dance-cure-candidate-1-hold`.

v4 is v3's payload (per own unit: the tick-local `chosen` target and the unit-local `available`
best, with ABSENT a third state that is not NONE) plus what the hold rule made necessary:

  per unit   `r=` the resolver branch — P primary · L lateral/improving detour · H hold ·
                  R regressive detour · W forced WAIT · N no MOVE this turn
             `b=` blocked_turns AFTER the decision (codex_1 definition 3)
  per turn   `pz=` passes of the two-phase fixed point
             `sp=` stale protections: members of K* that did not hold in the final pass
             `wc=` W-collisions: forced-WAIT movers whose own cell was granted to another mover

Wire form of a unit token: `u<id>=<chosen>/<available>/r=<code>/b=<n>` — no spaces inside a
token, so the v3 tokenizer is unchanged in shape and the two grammars still split the same way.

## Refusal, both directions

A v4 decoder that reads a v3 payload would silently report `r=`/`b=` as absent rather than as
missing, and a v3 decoder that read v4 would mis-parse `available` as `TREE(3,4)/r=H/b=1`. So the
version token is checked first and anything that is not `v4` is REFUSED. The v3 decoder's own
refusal of v4 is asserted as a control in `controls.py`, not assumed.

## The three measurements are REQUIRED fields

`pz`/`sp`/`wc` are not optional: a payload without them is off-grammar. They exist because the
construction ruling (local_claude_1 `20260825T085500Z`) ordered two facts reported that cannot be
derived from outside the resolver — how many passes the fixed point took, and which protected
holders turned out not to hold — and one, the base's pre-existing W-collision exposure, that the
ruling requires shown UNCHANGED between the arms. A field that may be missing is a field that can
quietly go missing on the arm where it matters.
"""
from __future__ import annotations

import re

VERSION = "v4"
LINE_BUDGET = 2000
BRANCH_CODES = "PLHRWN"

MSG_TOKEN = re.compile(r"^\s*MSG(\s|$)", re.IGNORECASE)
TARGET_RE = re.compile(
    r"^(NONE|SHACK|BANK\((-?\d+),(-?\d+)\)|CELL\((-?\d+),(-?\d+)\)|TREE\((-?\d+),(-?\d+)\))$")
UNIT_RE = re.compile(r"^u(\d+)=([^/]+)/([^/]+)/r=([^/]*)/b=([^/]*)$")
META_RE = re.compile(r"^(pz|sp|wc)=(\d+)$")


class GateError(Exception):
    """Anything that would make a result mean something other than it says."""


def strip_msg(line: str) -> str:
    kept = [frag for frag in line.split(";") if not MSG_TOKEN.match(frag)]
    return ";".join(kept)


def msg_fragments(line: str) -> list[str]:
    return [frag for frag in line.split(";") if MSG_TOKEN.match(frag)]


def decode(payload: str):
    """Round-trip the wire syntax back to (turn, units, order, banner, meta).

    `units` maps id -> (chosen, available, branch, blocked_turns). `meta` maps pz/sp/wc -> int.
    Raises GateError off-grammar; never guesses a missing field into a default.
    """
    tokens = payload.split()
    if not tokens or tokens[0] != "MSG":
        raise GateError(f"fragment is not an MSG token: {payload!r}")
    tokens = tokens[1:]
    if "NARRATE" not in tokens:
        raise GateError(f"no NARRATE token: {payload!r}")
    start = tokens.index("NARRATE")
    banner = tokens[:start]
    if len(banner) > 1:
        raise GateError(f"more than one banner token before NARRATE: {banner!r}")
    tokens = tokens[start:]
    if len(tokens) < 2 or tokens[1] != VERSION:
        raise GateError(f"unsupported NARRATE version {tokens[1] if len(tokens) > 1 else None!r}, "
                        f"this decoder reads {VERSION} only")
    if len(tokens) < 3 or not tokens[2].startswith("t="):
        raise GateError(f"no t= field: {payload!r}")
    turn = int(tokens[2][2:])
    units, order, meta = {}, [], {}
    for tok in tokens[3:]:
        m_meta = META_RE.match(tok)
        if m_meta:
            if m_meta.group(1) in meta:
                raise GateError(f"{m_meta.group(1)}= appears twice in {payload!r}")
            meta[m_meta.group(1)] = int(m_meta.group(2))
            continue
        m = UNIT_RE.match(tok)
        if not m:
            raise GateError(f"off-grammar unit token {tok!r} in {payload!r}")
        if meta:
            raise GateError(f"unit token {tok!r} after a per-turn field in {payload!r}")
        uid, chosen, available, branch, blocked = (
            int(m.group(1)), m.group(2), m.group(3), m.group(4), m.group(5))
        if not TARGET_RE.match(chosen):
            raise GateError(f"off-grammar chosen target {chosen!r} in {payload!r}")
        if available != "ABSENT" and not TARGET_RE.match(available):
            raise GateError(f"off-grammar available target {available!r} in {payload!r}")
        if branch not in tuple(BRANCH_CODES):
            raise GateError(f"off-grammar branch code {branch!r} in {payload!r}")
        if not re.fullmatch(r"\d+", blocked):
            raise GateError(f"off-grammar b= value {blocked!r} in {payload!r}")
        if uid in units:
            raise GateError(f"unit {uid} appears twice in {payload!r}")
        units[uid] = (chosen, available, branch, int(blocked))
        order.append(uid)
    missing = [k for k in ("pz", "sp", "wc") if k not in meta]
    if missing:
        raise GateError(f"missing per-turn field(s) {missing} in {payload!r}")
    return turn, units, order, bool(banner), meta


def new_census():
    return {"rows": 0, "chosen_ne_available": 0, "discarded_want": 0, "lone_unit_turns": 0,
            "payload_max_chars": 0, "turns": 0,
            "available_states": {"ABSENT": 0, "NONE": 0, "CONCRETE": 0},
            "branches": {c: 0 for c in BRANCH_CODES},
            "blocked_values": {}, "hold_turns": 0, "max_passes": 1,
            "stale_protections": 0, "w_collision_events": 0, "w_collision_turns": 0}


def check_telemetry(sid, tr, command_lines, census=None, rule_off=False):
    """Grammar round-trip, roster/turn alignment, the v3 invariants, and the v4 controls.

    The v4 controls come straight from the construction ruling:
      * `pz` <= movers + 1 on EVERY turn (termination, checked from the wire, not asserted in
        prose). `movers` is read off the branch codes: P, L, H, R and W are movers; N is not.
        The self-target pre-pass also reports W and is NOT a mover, so the bound is checked in
        the direction that can only be too generous, never too strict.
      * with the rule off: exactly one pass, no `H`, no nonzero `b`, no stale protections.
      * `b` is consistent across turns per unit: it rises by exactly 1 on an H and is 0 on
        anything else — the consecutive-H counter of definition 2, checked rather than trusted.
    """
    errors = []
    prev_blocked = {}
    for index, line in enumerate(command_lines, 1):
        frags = line.split(";")
        msgs = msg_fragments(line)
        if len(msgs) != 1:
            errors.append(f"turn {index}: {len(msgs)} MSG tokens, expected exactly 1")
            continue
        if not MSG_TOKEN.match(frags[0]):
            errors.append(f"turn {index}: the MSG token is not first in the command list")
        payload = msgs[0].strip()
        if len(payload) > LINE_BUDGET:
            errors.append(f"turn {index}: MSG payload {len(payload)} chars exceeds {LINE_BUDGET}")
        try:
            turn, units, order, banner, meta = decode(payload)
        except GateError as exc:
            errors.append(f"turn {index}: {exc}")
            continue
        movers = sum(1 for u in units.values() if u[2] in "PLHRW")
        if meta["pz"] < 1:
            errors.append(f"turn {index}: pz={meta['pz']} — a turn always runs at least one pass")
        if meta["pz"] > movers + 1:
            errors.append(f"turn {index}: pz={meta['pz']} exceeds movers+1={movers + 1} — "
                          f"the fixed point did not terminate within its bound")
        if rule_off:
            if meta["pz"] != 1:
                errors.append(f"turn {index}: rule-off ran pz={meta['pz']} passes, expected 1")
            if meta["sp"] != 0:
                errors.append(f"turn {index}: rule-off reports sp={meta['sp']}, expected 0")
            for uid, (_, _, branch, blocked) in units.items():
                if branch == "H":
                    errors.append(f"turn {index}: rule-off emitted r=H for u{uid}")
                if blocked:
                    errors.append(f"turn {index}: rule-off emitted b={blocked} for u{uid}")
        for uid, (chosen, available, branch, blocked) in units.items():
            was = prev_blocked.get(uid, 0)
            if branch == "H":
                if blocked != was + 1:
                    errors.append(f"turn {index}: u{uid} held with b={blocked}, expected "
                                  f"{was + 1} (previous {was})")
            elif blocked:
                errors.append(f"turn {index}: u{uid} branch {branch} with b={blocked}, "
                              f"expected 0")
        prev_blocked = {uid: u[3] for uid, u in units.items()}
        if census is not None:
            census["turns"] += 1
            census["payload_max_chars"] = max(census["payload_max_chars"], len(payload))
            census["max_passes"] = max(census["max_passes"], meta["pz"])
            census["stale_protections"] += meta["sp"]
            census["w_collision_events"] += meta["wc"]
            census["w_collision_turns"] += 1 if meta["wc"] else 0
            held = False
            for uid, (chosen, available, branch, blocked) in units.items():
                census["rows"] += 1
                census["branches"][branch] += 1
                census["blocked_values"][str(blocked)] = \
                    census["blocked_values"].get(str(blocked), 0) + 1
                held = held or branch == "H"
                census["available_states"][
                    "ABSENT" if available == "ABSENT"
                    else "NONE" if available == "NONE" else "CONCRETE"] += 1
                if chosen != available:
                    census["chosen_ne_available"] += 1
                    if chosen == "NONE" and available not in ("NONE", "ABSENT"):
                        census["discarded_want"] += 1
            census["hold_turns"] += 1 if held else 0
        if banner != (index == 1):
            errors.append(f"turn {index}: banner present={banner}, expected {index == 1}")
        if turn != index:
            errors.append(f"turn {index}: telemetry says t={turn} — turn misalignment")
        if order != sorted(order):
            errors.append(f"turn {index}: ids not ascending: {order}")
        # Production tie parity, unchanged from v3: on a lone-unit turn select's ids.len()==1
        # branch IS the max_by that `available` reuses, so the two must agree, ties included.
        if len(order) == 1:
            uid = order[0]
            chosen, available = units[uid][0], units[uid][1]
            if census is not None:
                census["lone_unit_turns"] += 1
            if available != "ABSENT" and chosen != available:
                errors.append(f"turn {index}: lone-unit tie parity broken — "
                              f"chosen {chosen} != available {available}")
        if tr is not None and index <= tr.T:
            live = sorted(u.id for u in tr.state(index).own_units())
            if order != live:
                errors.append(f"turn {index}: roster {order} != live own units {live}")
    return errors
