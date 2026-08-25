#!/usr/bin/env python3
"""The NARRATE **v5** decoder — task `20260825-dance-cure-candidate-2-swap`.

v5 is v4's payload with Candidate 1's hold rule PARKED and Candidate 2's exchange added:

  per unit   `r=` the resolver branch — P primary . L lateral/improving detour . R regressive
                  detour . W forced WAIT . N no MOVE this turn . **S** the mover of an exchange .
                  **X** the standing partner displaced by one. **`H` is RETIRED** and is off
                  grammar: a v5 payload carrying an `H` is a decode error, not a curiosity.
             `b=` blocked_turns, kept in the shape for the decoder's benefit and **identically 0**
                  in every v5 arm -- `H` was its only writer. A nonzero `b` is a decode error.
  per turn   `pz=` passes of the fixed point (identically 1 in every v5 arm: no rule adds a
                  holder, so the fixed point stops on its first pass -- G-0 control C-4)
             `sp=` stale protections (identically 0 for the same reason)
             `wc=` W-collisions: the base's pre-existing exposure, measured, not repaired
             `sw=` exchanges granted this turn
             `so=` refusals because the partner stood ON the mover's goal (left to the planner)
             `sn=` refusals because the landing was not adjacent (movement_speed >= 2, excluded)
             `sf=` refusals because the positional command map could not be verified (expected 0)

## Refusal, both directions

The version token is checked first and anything that is not `v5` is REFUSED, so a v4 replay handed
to this decoder cannot be read as v5 with the four new fields reported absent. `narrate4.decode`'s
own refusal of a v5 payload is asserted as a control, not assumed.

## The seven per-turn measurements are REQUIRED fields

A field that may be missing is a field that can quietly go missing on the arm where it matters --
and `sw`/`so`/`sn`/`sf` are exactly the numbers that say whether the rule fired, and at what named
cost.
"""
from __future__ import annotations

import re

VERSION = "v5"
LINE_BUDGET = 2000
BRANCH_CODES = "PLRWNSX"
META_FIELDS = ("pz", "sp", "wc", "sw", "so", "sn", "sf")

MSG_TOKEN = re.compile(r"^\s*MSG(\s|$)", re.IGNORECASE)
TARGET_RE = re.compile(
    r"^(NONE|SHACK|BANK\((-?\d+),(-?\d+)\)|CELL\((-?\d+),(-?\d+)\)|TREE\((-?\d+),(-?\d+)\))$")
UNIT_RE = re.compile(r"^u(\d+)=([^/]+)/([^/]+)/r=([^/]*)/b=([^/]*)$")
META_RE = re.compile(r"^(pz|sp|wc|sw|so|sn|sf)=(\d+)$")


class GateError(Exception):
    """Anything that would make a result mean something other than it says."""


def strip_msg(line: str) -> str:
    kept = [frag for frag in line.split(";") if not MSG_TOKEN.match(frag)]
    return ";".join(kept)


def msg_fragments(line: str) -> list[str]:
    return [frag for frag in line.split(";") if MSG_TOKEN.match(frag)]


def decode(payload: str):
    """Round-trip the wire syntax back to (turn, units, order, banner, meta).

    `units` maps id -> (chosen, available, branch, blocked_turns). `meta` maps the seven per-turn fields -> int.
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
    missing = [k for k in META_FIELDS if k not in meta]
    if missing:
        raise GateError(f"missing per-turn field(s) {missing} in {payload!r}")
    return turn, units, order, bool(banner), meta


def new_census():
    return {"rows": 0, "chosen_ne_available": 0, "discarded_want": 0, "lone_unit_turns": 0,
            "payload_max_chars": 0, "turns": 0,
            "available_states": {"ABSENT": 0, "NONE": 0, "CONCRETE": 0},
            "branches": {c: 0 for c in BRANCH_CODES},
            "blocked_values": {}, "max_passes": 1,
            "stale_protections": 0, "w_collision_events": 0, "w_collision_turns": 0,
            "swaps": 0, "swap_turns": 0, "target_occupied": 0, "non_adjacent": 0, "slot_fail": 0,
            "swap_events": []}


def check_telemetry(sid, tr, command_lines, census=None, rule_off=False):
    """Grammar round-trip, roster/turn alignment, the v3/v4 invariants, and the v5 controls.

    What is checked UNCONDITIONALLY on every v5 arm, because G-0 pre-committed it:

      * `pz == 1` on every turn (control C-4). Candidate 1's hold is off and Candidate 2 adds no
        holder, so the fixed point stops on its first pass. This is asserted on the wire every
        turn rather than argued from the source.
      * `sp == 0` for the same reason: with no holder there is nothing to protect.
      * `b == 0` for every unit on every turn (control C-9): `H` was `blocked_turns`' only writer
        and `H` is retired.
      * no `H` anywhere -- enforced by the grammar itself, since `H` is not in BRANCH_CODES.
      * `sw`/`so`/`sn`/`sf` counts agree with the branch codes they imply: a turn with `sw=k` must
        carry exactly k `S` codes and k `X` codes, and a turn with no `S` must report `sw=0`.
        Without this the counter and the branch letters could drift apart and each would still
        look self-consistent.

    With `rule_off=True` the arm must additionally report `sw=so=sn=sf=0` and carry no `S`/`X`:
    the parity arm must not merely produce the base's commands, it must not even reach the rule.
    """
    errors = []
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
        movers = sum(1 for u in units.values() if u[2] in "PLRWS")
        if meta["pz"] != 1:
            errors.append(f"turn {index}: pz={meta['pz']}, expected exactly 1 — no rule in a v5 "
                          f"arm adds a holder, so the fixed point stops on its first pass")
        if meta["pz"] > movers + 1:
            errors.append(f"turn {index}: pz={meta['pz']} exceeds movers+1={movers + 1}")
        if meta["sp"] != 0:
            errors.append(f"turn {index}: sp={meta['sp']}, expected 0 with no holder")
        s_ids = sorted(uid for uid, u in units.items() if u[2] == "S")
        x_ids = sorted(uid for uid, u in units.items() if u[2] == "X")
        if len(s_ids) != meta["sw"]:
            errors.append(f"turn {index}: sw={meta['sw']} but {len(s_ids)} r=S codes")
        if len(x_ids) != meta["sw"]:
            errors.append(f"turn {index}: sw={meta['sw']} but {len(x_ids)} r=X codes")
        if set(s_ids) & set(x_ids):
            errors.append(f"turn {index}: unit(s) {sorted(set(s_ids) & set(x_ids))} are both S "
                          f"and X — a unit cannot be its own exchange partner")
        for uid, (_, _, branch, blocked) in units.items():
            if blocked:
                errors.append(f"turn {index}: u{uid} reports b={blocked}, expected 0 — "
                              f"blocked_turns has no writer in a v5 arm")
        if rule_off:
            for field in ("sw", "so", "sn", "sf"):
                if meta[field]:
                    errors.append(f"turn {index}: rule-off reports {field}={meta[field]}, "
                                  f"expected 0")
            for uid, (_, _, branch, _) in units.items():
                if branch in "SX":
                    errors.append(f"turn {index}: rule-off emitted r={branch} for u{uid}")
        if census is not None:
            census["turns"] += 1
            census["payload_max_chars"] = max(census["payload_max_chars"], len(payload))
            census["max_passes"] = max(census["max_passes"], meta["pz"])
            census["stale_protections"] += meta["sp"]
            census["w_collision_events"] += meta["wc"]
            census["w_collision_turns"] += 1 if meta["wc"] else 0
            census["swaps"] += meta["sw"]
            census["swap_turns"] += 1 if meta["sw"] else 0
            census["target_occupied"] += meta["so"]
            census["non_adjacent"] += meta["sn"]
            census["slot_fail"] += meta["sf"]
            if meta["sw"]:
                census["swap_events"].append({"game": sid, "turn": index,
                                              "movers": s_ids, "displaced": x_ids})
            for uid, (chosen, available, branch, blocked) in units.items():
                census["rows"] += 1
                census["branches"][branch] += 1
                census["blocked_values"][str(blocked)] = \
                    census["blocked_values"].get(str(blocked), 0) + 1
                census["available_states"][
                    "ABSENT" if available == "ABSENT"
                    else "NONE" if available == "NONE" else "CONCRETE"] += 1
                if chosen != available:
                    census["chosen_ne_available"] += 1
                    if chosen == "NONE" and available not in ("NONE", "ABSENT"):
                        census["discarded_want"] += 1
        if banner != (index == 1):
            errors.append(f"turn {index}: banner present={banner}, expected {index == 1}")
        if turn != index:
            errors.append(f"turn {index}: telemetry says t={turn} — turn misalignment")
        if order != sorted(order):
            errors.append(f"turn {index}: ids not ascending: {order}")
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
