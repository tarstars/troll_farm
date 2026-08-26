#!/usr/bin/env python3
"""The NARRATE **v6** decoder — task `20260826-candidate-3-keep-your-goal`.

Packet of record: `claude_1/cure3/g0-candidate-3-2026-08-26-r6.md` (r5 as amended by r6 C1–C5).

v6 is v5's payload with Candidate 2's exchange rule ABSENT and Candidate 3's absolute keep added:

  per unit   `r=` the resolver branch — P primary . L lateral/improving detour . R regressive
                  detour . W forced WAIT . N no MOVE this turn. **`H` (Candidate 1's hold) and
                  `S`/`X` (Candidate 2's exchange) are off this grammar**: a v6 payload carrying
                  one is a decode error, not a curiosity.
             `b=` blocked_turns, kept in the shape for the decoder's benefit and identically 0 —
                  `H` was its only writer. A nonzero `b` is a decode error.
             `k=` three-valued: `2` the unit was restricted and its emitted command carried the
                  kept goal . `1` the unit holds a valid kept goal whose emitted command does not
                  carry it (the not-live case, and the case where `resolve_move_conflicts` rewrote
                  a restricted command) . `0` no valid kept goal at the end of the turn, INCLUDING
                  a goal released as contested this turn — which is why `xc` and `k` are read
                  together and never separately.
  per turn   the v5 meta fields carried unchanged (`pz sp wc sw so sn sf`, r6 C4) plus the keep
             census of §5.2 and the two price tags `xd`/`xj` of §5.3.

**`m=` is deleted.** There is no margin constant to disambiguate a wire with, which is itself the
version's signature. **`rw=` is struck** (r6 C1): the `Bank` gone cause is asserted structurally
unreachable, and `rf + rt + ro == rg` is the falsifier for that assertion — strictly better than an
always-zero counter, because a zero field reads as a passing check while a broken invariant reads
as what it is.

## §5.4 field-set closure, asserted AT IMPORT

The v6 field set is defined ONCE, by `META_RE`'s alternation together with `UNIT_RE`'s groups.
Every field named in a §5.2 census equation, a §9 panel gate or a §3 `count` column must appear in
that alternation, and every field in the alternation must appear in at least one of them. This
module asserts that at import over its own constants and raises on a mismatch, so the two lists
cannot drift apart again. **The assertion is a decoder contract**: it tests the spec's internal
consistency, never the bot's behaviour, and it is not a gate on any arm.

## Refusal, all three directions

The version token is checked first and anything that is not `v6` is REFUSED, so a v5 replay handed
to this decoder cannot be read as v6 with the keep census reported absent. The converse —
`narrate5` and `narrate4` refusing a v6 payload — is asserted as a control by `refusal_controls()`,
not assumed.
"""
from __future__ import annotations

import re

VERSION = "v6"
LINE_BUDGET = 2000
BRANCH_CODES = "PLRWN"
KEEP_CODES = "012"

MSG_TOKEN = re.compile(r"^\s*MSG(\s|$)", re.IGNORECASE)
TARGET_RE = re.compile(
    r"^(NONE|SHACK|BANK\((-?\d+),(-?\d+)\)|CELL\((-?\d+),(-?\d+)\)|TREE\((-?\d+),(-?\d+)\))$")
UNIT_RE = re.compile(r"^u(\d+)=([^/]+)/([^/]+)/r=([^/]*)/b=([^/]*)/k=([012])$")
META_RE = re.compile(
    r"^(pz|sp|wc|sw|so|sn|sf|kp|kq|kl|kr|rd|rg|ri|rx|rf|rt|ro"
    r"|nl|nl_producer|nl_door|nl_admissibility|nl_other"
    r"|ka|kc|xc|xw|xn|xp|xg|xd|xj)=(\d+)$")

# --------------------------------------------------------------------------- §5.4 closure
# The alternation, read back out of the compiled pattern rather than re-typed: a second hand-kept
# list is exactly the defect C3 exists to prevent.
META_FIELDS = tuple(re.search(r"\^\((.*)\)=", META_RE.pattern, re.S).group(1).replace("\n", "")
                    .replace(" ", "").split("|"))

# §5.2 — the four census equations. Every name here must be in the grammar, and each equation is
# checked on EVERY turn.
EQUATIONS = (
    ("kp == kq + kl", ("kp",), ("kq", "kl")),
    ("rd + rg + ri + rx + xc == kr", ("kr",), ("rd", "rg", "ri", "rx", "xc")),
    # r6 C1: no `rw` term. The Bank gone cause has no sub-count, so this equation BREAKS if it
    # ever fires — that is the falsifier for the structural claim, and it is deliberate.
    ("rf + rt + ro == rg", ("rg",), ("rf", "rt", "ro")),
    ("nl_producer + nl_door + nl_admissibility + nl_other == nl",
     ("nl",), ("nl_producer", "nl_door", "nl_admissibility", "nl_other")),
)
EQUATION_FIELDS = frozenset(f for _, lhs, rhs in EQUATIONS for f in lhs + rhs)

# §9 — fields a panel gate or an invariant reads directly.
GATE_FIELDS = frozenset({"pz", "sp", "xc", "ka", "kq", "xd", "xj"})

# §9.8 as amended by r6 C5 — "Counted, not argued": the distributions the packet reports.
REPORT_FIELDS = frozenset(
    "kp kq kl kr rd rg ri rx rf rt ro nl nl_producer nl_door nl_admissibility nl_other "
    "wc sw so sn sf ka kc xc xw xn xp xg".split())

_CONSUMED = EQUATION_FIELDS | GATE_FIELDS | REPORT_FIELDS
_GRAMMAR = frozenset(META_FIELDS)
_UNCONSUMED = sorted(_GRAMMAR - _CONSUMED)
_UNGRAMMARED = sorted(_CONSUMED - _GRAMMAR)
if _UNCONSUMED or _UNGRAMMARED:
    raise ImportError(
        "v6 field-set closure (packet §5.4) is broken: "
        f"grammar fields with no consumer {_UNCONSUMED}; "
        f"consumed fields off the grammar {_UNGRAMMARED}")


class GateError(Exception):
    """Anything that would make a result mean something other than it says."""


def strip_msg(line: str) -> str:
    kept = [frag for frag in line.split(";") if not MSG_TOKEN.match(frag)]
    return ";".join(kept)


def msg_fragments(line: str) -> list[str]:
    return [frag for frag in line.split(";") if MSG_TOKEN.match(frag)]


def decode(payload: str):
    """Round-trip the wire syntax back to (turn, units, order, banner, meta).

    `units` maps id -> (chosen, available, branch, blocked_turns, keep_code). `meta` maps the 32
    per-turn fields -> int. Raises GateError off-grammar; never guesses a missing field into a
    default.
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
        uid, chosen, available, branch, blocked, keep = (
            int(m.group(1)), m.group(2), m.group(3), m.group(4), m.group(5), m.group(6))
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
        units[uid] = (chosen, available, branch, int(blocked), keep)
        order.append(uid)
    missing = [k for k in META_FIELDS if k not in meta]
    if missing:
        raise GateError(f"missing per-turn field(s) {missing} in {payload!r}")
    return turn, units, order, bool(banner), meta


def new_census():
    return {"rows": 0, "turns": 0, "payload_max_chars": 0,
            "chosen_ne_available": 0, "discarded_want": 0, "lone_unit_turns": 0,
            "available_states": {"ABSENT": 0, "NONE": 0, "CONCRETE": 0},
            "branches": {c: 0 for c in BRANCH_CODES},
            "keep_codes": {c: 0 for c in KEEP_CODES},
            "w_collision_events": 0, "w_collision_turns": 0,
            "totals": {f: 0 for f in META_FIELDS},
            "ka_max": 0, "xd_max": 0, "xj_max": 0,
            "restricted_turns": 0, "contested_turns": 0, "phased_turns": 0,
            "three_plus_selector_turns": 0, "parked_with_goal": 0,
            "contest_events": [], "xd_histogram": {}, "xj_histogram": {}}


def check_telemetry(sid, tr, command_lines, census=None, rule_off=False):
    """Grammar round-trip, roster/turn alignment, the carried v4/v5 invariants and the v6 census.

    Checked UNCONDITIONALLY on every v6 arm, because the packet pre-committed it:

      * `pz == 1` and `sp == 0` on every turn — R5 adds no holder, so the fixed point stops on its
        first pass and there is nothing to protect.
      * `b == 0` for every unit on every turn: `blocked_turns` has no writer in a v6 arm.
      * `sw == so == sn == sf == 0`: there is no exchange rule in a Candidate 3 arm. These are
        v5's fields carried with v5's meanings (r6 C4), and a nonzero one is a defect in R5.
      * no `H`, `S` or `X` — enforced by the grammar itself, since they are not in BRANCH_CODES.
      * the four §5.2 equations, every turn.
      * `k` and the census agree: a turn with `kq=0` carries no `k=2`, and the number of units
        reporting `k>0` never exceeds `kp`. Without this the counters and the per-unit codes could
        drift apart and each would still look self-consistent.

    With `rule_off=True` the arm must additionally report `kp=0` on every turn and carry no
    `k>0`: the containment arm must not merely produce the base's commands, it must not even reach
    the rule (r5 §9.1).
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
        if meta["pz"] != 1:
            errors.append(f"turn {index}: pz={meta['pz']}, expected exactly 1 — no rule in a v6 "
                          f"arm adds a holder")
        if meta["sp"] != 0:
            errors.append(f"turn {index}: sp={meta['sp']}, expected 0 with no holder")
        for field in ("sw", "so", "sn", "sf"):
            if meta[field]:
                errors.append(f"turn {index}: {field}={meta[field]}, expected 0 — there is no "
                              f"exchange rule in a Candidate 3 arm")
        for name, lhs, rhs in EQUATIONS:
            if sum(meta[f] for f in lhs) != sum(meta[f] for f in rhs):
                errors.append(f"turn {index}: {name} broken — "
                              + ", ".join(f"{f}={meta[f]}" for f in lhs + rhs))
        for uid, (_, _, _, blocked, _) in units.items():
            if blocked:
                errors.append(f"turn {index}: u{uid} reports b={blocked}, expected 0")
        keep2 = [uid for uid, u in units.items() if u[4] == "2"]
        keep_any = [uid for uid, u in units.items() if u[4] != "0"]
        if not meta["kq"] and keep2:
            errors.append(f"turn {index}: kq=0 but units {sorted(keep2)} report k=2")
        if len(keep_any) > meta["kp"]:
            errors.append(f"turn {index}: {len(keep_any)} units report k>0 but kp={meta['kp']}")
        if len(keep2) > meta["kq"]:
            errors.append(f"turn {index}: {len(keep2)} units report k=2 but kq={meta['kq']}")
        if rule_off:
            if meta["kp"]:
                errors.append(f"turn {index}: rule-off reports kp={meta['kp']}, expected 0")
            if keep_any:
                errors.append(f"turn {index}: rule-off emitted k>0 for u{sorted(keep_any)}")
        if census is not None:
            census["turns"] += 1
            census["payload_max_chars"] = max(census["payload_max_chars"], len(payload))
            for field in META_FIELDS:
                census["totals"][field] += meta[field]
            census["ka_max"] = max(census["ka_max"], meta["ka"])
            census["xd_max"] = max(census["xd_max"], meta["xd"])
            census["xj_max"] = max(census["xj_max"], meta["xj"])
            census["w_collision_events"] += meta["wc"]
            census["w_collision_turns"] += 1 if meta["wc"] else 0
            census["restricted_turns"] += 1 if meta["kq"] else 0
            census["contested_turns"] += meta["xn"]
            census["phased_turns"] += 1 if meta["xp"] else 0
            census["three_plus_selector_turns"] += 1 if len(order) >= 3 else 0
            if meta["xd"]:
                key = str(meta["xd"])
                census["xd_histogram"][key] = census["xd_histogram"].get(key, 0) + 1
            if meta["xj"]:
                key = str(meta["xj"])
                census["xj_histogram"][key] = census["xj_histogram"].get(key, 0) + 1
            if meta["xc"]:
                census["contest_events"].append({"game": sid, "turn": index, "xc": meta["xc"],
                                                 "xg": meta["xg"]})
            for uid, (chosen, available, branch, _blocked, keep) in units.items():
                census["rows"] += 1
                census["branches"][branch] += 1
                census["keep_codes"][keep] += 1
                census["available_states"][
                    "ABSENT" if available == "ABSENT"
                    else "NONE" if available == "NONE" else "CONCRETE"] += 1
                if chosen != available:
                    census["chosen_ne_available"] += 1
                    if chosen == "NONE" and available not in ("NONE", "ABSENT"):
                        census["discarded_want"] += 1
                # The v6 parked count, under its own name. It does NOT discharge P4b and is not
                # permitted to (r5 §9.6).
                if keep != "0" and branch == "N" and chosen == "NONE":
                    census["parked_with_goal"] += 1
            if len(order) == 1:
                census["lone_unit_turns"] += 1
        if banner != (index == 1):
            errors.append(f"turn {index}: banner present={banner}, expected {index == 1}")
        if turn != index:
            errors.append(f"turn {index}: telemetry says t={turn} — turn misalignment")
        if order != sorted(order):
            errors.append(f"turn {index}: ids not ascending: {order}")
        if tr is not None and index <= tr.T:
            live = sorted(u.id for u in tr.state(index).own_units())
            if order != live:
                errors.append(f"turn {index}: roster {order} != live own units {live}")
    return errors


def refusal_controls() -> list[str]:
    """All three directions, asserted rather than assumed: v6 refuses v5 and v4, and v5 and v4
    refuse v6. A decoder that silently reads the wrong version reports absence as zero."""
    import sys
    from pathlib import Path
    here = Path(__file__).resolve().parent
    for name in ("narrate5", "narrate4"):
        candidate = here.parent / name
        if candidate.is_dir():
            sys.path.insert(0, str(candidate))
    failures = []
    v6 = ("MSG NARRATE v6 t=1 u1=NONE/NONE/r=N/b=0/k=0 " +
          " ".join(f"{f}={1 if f == 'pz' else 0}" for f in META_FIELDS))
    v5 = "MSG NARRATE v5 t=1 u1=NONE/NONE/r=N/b=0 pz=1 sp=0 wc=0 sw=0 so=0 sn=0 sf=0"
    try:
        decode(v6)
    except GateError as exc:
        failures.append(f"narrate6 failed to decode its own payload: {exc}")
    try:
        decode(v5)
        failures.append("narrate6 accepted a v5 payload")
    except GateError:
        pass
    for name in ("narrate5", "narrate4"):
        try:
            module = __import__(name)
        except ImportError:
            continue
        try:
            module.decode(v6)
            failures.append(f"{name} accepted a v6 payload")
        except Exception:
            pass
    return failures


if __name__ == "__main__":
    import sys
    problems = refusal_controls()
    print(f"v6 grammar: {len(META_FIELDS)} meta fields, closure asserted at import")
    for line in problems:
        print(f"  FAIL {line}")
    print("  refusal controls OK" if not problems else f"  {len(problems)} FAILURES")
    sys.exit(1 if problems else 0)
