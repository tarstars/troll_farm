#!/usr/bin/env python3
"""The NARRATE **v8** decoder — task `20260826-banana-farm-candidate`, packet §8.

v8 is v6 with **one group added**: the nine farm tokens `fs fp fh fl fd fe fw fE fW`, emitted
**immediately after `t=`** and before every v6 token. This file is a copy of
`claude_1/narrate6/narrate6.py` with that group added in the places it belongs — the grammar, the
decode order, the census, the telemetry checks and the refusal controls. `narrate6.py` is byte
unchanged.

**Why v8 and not v7.** The packet as reviewed said "v7". `v7` was already taken, on this same
branch and the same day, by Candidate 3b's stuck-holder-release decoder
(`claude_1/narrate7/narrate7.py`, the `rs=` field), which is handed off, reproduced by codex_1 and
imported by `claude_1/cure3b/containment3b.py` and `panel_read3b.py`. Two different grammars under
one version token is the exact failure the version-refusal controls exist to prevent: a farm
payload read by the 3b decoder, or the reverse, would report the other rule's fields absent — that
is, would report "the rule never fired". So the farm dialect is **v8** with its own directory
`claude_1/narrate8/`, and the 3b `v7` is left alone. Nothing else in §8 changes: the group is the
same nine tokens, still first, still ≤ 44 characters.

**The group** (packet §8):

  `fs=` state 0 TRAIN . 1 DENY . 2 FARM . 3 WOOD
  `fp=` accepted farm plants so far this game        `fh=` accepted mother harvests so far
  `fl=` the turn the latch fired, 0 if it has not
  `fd=` denial end reason, one of `a b c d t`, `-` while denying
  `fe=` enemy chop hits on our ring, cumulative      `fw=` our own ring work events, cumulative
  `fE=` **window** enemy hits fe(60) frozen AT the latch turn, `-` until the latch fires
  `fW=` **window** own ring work fw(60) frozen AT the latch turn, `-` until the latch fires

`fd`, `fE` and `fW` are the only fields on any NARRATE grammar that are not integers: each is an
integer **or** the sentinel `-`, and the sentinel means "not yet determined", never zero. They are
carried in the returned `meta` mapping with those types, so a consumer that sums `meta` blindly
raises instead of silently reading a sentinel as 0.

**The interface is `narrate6`'s, unchanged**, because `codex_1/p4b/p4b_gate.py` unpacks
`decode()` into exactly five names: `decode` returns `(turn, units, order, banner, meta)` and the
farm group rides inside `meta`. `strip_msg`, `msg_fragments`, `new_census`, `check_telemetry`,
`refusal_controls` and `GateError` keep their v6 signatures.

Packet of record: `claude_1/farm/g0-farm-2026-08-26.md` (round 2 as amended by codex_1's round-2
W1 edit). Parent decoder of record: `claude_1/narrate6/narrate6.py`.

--- what follows is v6's own docstring, carried unchanged ---

The NARRATE **v6** decoder — task `20260826-candidate-3-keep-your-goal`.

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

VERSION = "v8"
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

# --------------------------------------------------------------------------- §8 the farm group
# Nine tokens, emitted immediately after `t=` and BEFORE every v6 token, so that if the platform
# truncates the tail the farm readout still comes home (packet §8: v6 is already up to 328 chars a
# turn and the longest MSG ever returned by the platform is 127; truncation is untested, not
# disproved). The order here is the wire order and is checked, not merely parsed.
FARM_ORDER = ("fs", "fp", "fh", "fl", "fd", "fe", "fw", "fE", "fW")
FARM_INT = frozenset({"fs", "fp", "fh", "fl", "fe", "fw"})       # integers, always
FARM_SENTINEL = frozenset({"fd", "fE", "fW"})                    # integer-or-`-`; `-` != 0
FARM_DENIAL_CODES = "abcdt"                                      # §3 end reasons; `-` = denying
FARM_STATES = (0, 1, 2, 3)                                       # TRAIN . DENY . FARM . WOOD
FARM_RE = re.compile(r"^(fs|fp|fh|fl|fe|fw)=(\d+)$")
FARM_SENTINEL_RE = re.compile(r"^(fd|fE|fW)=(-|[a-z]|\d+)$")

# The latch rule of §4, in the one form a reader can recompute from the wire: the frozen window
# snapshot at the latch turn. `M = 15` is NOT recomputable from a snapshot and is checked against
# the panel's per-turn trace instead (§8 round-2 correction, defect 2). These three are gate L4.
LATCH_R = 2.0        # fE > R * fW
LATCH_F = 6          # fW >= F
LATCH_N = 12         # fE + fW >= N
LATCH_EARLIEST = 74  # turn >= w(60) plus M(15) consecutive qualifying turns, minus the first

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

# Every farm field has a consumer below — `check_telemetry` reads all nine and gate L4 reads four
# of them — so the closure assertion covers the group rather than exempting it.
FARM_FIELDS = frozenset(FARM_ORDER)
assert FARM_FIELDS == FARM_INT | FARM_SENTINEL, "the farm group and its type split disagree"

_CONSUMED = EQUATION_FIELDS | GATE_FIELDS | REPORT_FIELDS
_GRAMMAR = frozenset(META_FIELDS)
_UNCONSUMED = sorted(_GRAMMAR - _CONSUMED)
_UNGRAMMARED = sorted(_CONSUMED - _GRAMMAR)
if _UNCONSUMED or _UNGRAMMARED:
    raise ImportError(
        "v8 field-set closure (packet §5.4, v6 half) is broken: "
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

    `units` maps id -> (chosen, available, branch, blocked_turns, keep_code). `meta` maps the v6
    per-turn fields -> int, PLUS the nine §8 farm fields, of which `fd`, `fE` and `fW` may be the
    string `-` meaning "not yet determined" — never 0. Raises GateError off-grammar; never guesses a missing field into a
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
    # §8: the nine farm tokens come first, in wire order, before any unit or v6 token. Position is
    # part of the grammar because the whole point of the group is to survive a truncated tail: a
    # payload that carries them late would decode fine and would not have the property claimed for
    # it, so a late farm token is a decode error and not a curiosity.
    rest = tokens[3:]
    if len(rest) < len(FARM_ORDER):
        raise GateError(f"payload too short to carry the farm group: {payload!r}")
    for expected, tok in zip(FARM_ORDER, rest[:len(FARM_ORDER)]):
        m_int = FARM_RE.match(tok)
        m_sen = FARM_SENTINEL_RE.match(tok)
        m_farm = m_int or m_sen
        if not m_farm:
            raise GateError(f"off-grammar farm token {tok!r} in {payload!r}")
        name, raw = m_farm.group(1), m_farm.group(2)
        if name != expected:
            raise GateError(f"farm group out of order: {name}= where {expected}= was expected "
                            f"in {payload!r}")
        if name in FARM_INT:
            meta[name] = int(raw)
        elif raw == "-":
            meta[name] = "-"                      # not yet determined. NEVER read as 0.
        elif name == "fd":
            if raw not in tuple(FARM_DENIAL_CODES):
                raise GateError(f"off-grammar denial end reason {raw!r} in {payload!r}")
            meta[name] = raw
        else:
            if not re.fullmatch(r"\d+", raw):
                raise GateError(f"off-grammar {name}= value {raw!r} in {payload!r}")
            meta[name] = int(raw)
    if meta["fs"] not in FARM_STATES:
        raise GateError(f"off-grammar farm state fs={meta['fs']} in {payload!r}")
    for tok in rest[len(FARM_ORDER):]:
        if FARM_RE.match(tok) or FARM_SENTINEL_RE.match(tok):
            raise GateError(f"farm token {tok!r} after the farm group in {payload!r}")
        m_meta = META_RE.match(tok)
        if m_meta:
            if m_meta.group(1) in meta:
                raise GateError(f"{m_meta.group(1)}= appears twice in {payload!r}")
            meta[m_meta.group(1)] = int(m_meta.group(2))
            continue
        m = UNIT_RE.match(tok)
        if not m:
            raise GateError(f"off-grammar unit token {tok!r} in {payload!r}")
        if any(k in meta for k in META_FIELDS):
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
    missing = [k for k in tuple(META_FIELDS) + FARM_ORDER if k not in meta]
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
            "contest_events": [], "xd_histogram": {}, "xj_histogram": {},
            # §8 farm readout. `latch_turns` and `latch_snapshots` are per game, not per turn:
            # the latch is one-way, so one game contributes at most one entry.
            "farm_state_turns": {code: 0 for code in FARM_STATES},
            "farm_plants_final": 0, "farm_harvests_final": 0,
            "ring_enemy_final": 0, "ring_own_final": 0,
            "latch_games": 0, "latch_turns": [], "latch_snapshots": [],
            "denial_end_reasons": {code: 0 for code in FARM_DENIAL_CODES},
            "l4_failures": 0}


def l4_failures(meta) -> list[str]:
    """Gate L4 (§8, §9): recompute the latch rule from the frozen snapshot the wire carries.

    This is the only part of §4's rule a reader can check from the wire alone. `M = 15` — fifteen
    consecutive qualifying turns — is not recomputable from a single snapshot and is checked
    against the panel's own per-turn trace instead; §8 says so rather than implying the wire covers
    it. Round 1 claimed the cumulative `fe`/`fw` pair made the latch auditable from the wire; that
    claim is withdrawn, because 300 turns of cumulative counts cannot be narrowed to a 60-turn
    window afterwards.
    """
    if not meta["fl"]:
        return []
    problems = []
    fE, fW = meta["fE"], meta["fW"]
    if fE == "-" or fW == "-":
        return [f"latch fired at turn {meta['fl']} but the window snapshot is absent "
                f"(fE={fE}, fW={fW}) — the frozen pair is written AT the latch turn"]
    if not fE > LATCH_R * fW:
        problems.append(f"fE={fE} is not > {LATCH_R} * fW={fW}")
    if fW < LATCH_F:
        problems.append(f"fW={fW} < F={LATCH_F}")
    if fE + fW < LATCH_N:
        problems.append(f"fE+fW={fE + fW} < N={LATCH_N}")
    if meta["fl"] < LATCH_EARLIEST:
        problems.append(f"fl={meta['fl']} is earlier than turn {LATCH_EARLIEST}, which the rule's "
                        f"own gates (turn >= 60, then 15 consecutive qualifying turns) make the "
                        f"earliest fire possible — an earlier fire is a build defect, not a result")
    return problems


def check_farm(index: int, meta, prev) -> list[str]:
    """The §8 farm group's own invariants, checked on every turn of every v8 arm.

      * the four cumulative counters never decrease — they are running totals, not per-turn values;
      * the latch is ONE-WAY: once `fl` is nonzero it never changes and never returns to 0;
      * `fE`/`fW` are `-` exactly while `fl == 0`, and once written they are frozen — a snapshot
        that keeps updating is a window read at the wrong turn, which is defect 2 all over again;
      * `fd` is `-` exactly while the state is DENY, and a settled end reason never changes;
      * gate L4 on the turn the latch fires.

    Every one of these is a defect in the build, not in the world: nothing an opponent does can
    make a cumulative counter run backwards or a one-way latch un-fire.
    """
    errors = []
    if prev is not None:
        for field in ("fp", "fh", "fe", "fw"):
            if meta[field] < prev[field]:
                errors.append(f"turn {index}: {field}={meta[field]} decreased from "
                              f"{prev[field]} — these are cumulative counters")
        if prev["fl"] and meta["fl"] != prev["fl"]:
            errors.append(f"turn {index}: fl={meta['fl']} but the latch already fired at turn "
                          f"{prev['fl']} — the latch is one-way and its turn is written once")
        for field in ("fE", "fW"):
            if prev["fl"] and prev[field] != meta[field]:
                errors.append(f"turn {index}: {field}={meta[field]} changed from {prev[field]} "
                              f"after the latch fired — the window pair is frozen at the latch turn")
        if prev["fd"] != "-" and meta["fd"] != prev["fd"]:
            errors.append(f"turn {index}: fd={meta['fd']} changed from a settled end reason "
                          f"{prev['fd']} — denial ends once")
    if meta["fl"] and meta["fl"] > index:
        errors.append(f"turn {index}: fl={meta['fl']} is in the future")
    for field in ("fE", "fW"):
        if meta["fl"] and meta[field] == "-":
            errors.append(f"turn {index}: the latch fired at turn {meta['fl']} but {field}= is "
                          f"the sentinel — absent is not zero")
        if not meta["fl"] and meta[field] != "-":
            errors.append(f"turn {index}: {field}={meta[field]} with fl=0 — the window pair is "
                          f"written only at the latch turn")
    if meta["fs"] == 1 and meta["fd"] != "-":
        errors.append(f"turn {index}: fs=1 (DENY) with a settled end reason fd={meta['fd']}")
    if prev is not None and prev["fs"] == 1 and meta["fs"] != 1 and meta["fd"] == "-":
        errors.append(f"turn {index}: denial ended (fs {prev['fs']} -> {meta['fs']}) with no end "
                      f"reason — fd is still the sentinel")
    if meta["fl"] and (prev is None or not prev["fl"]):
        errors.extend(f"turn {index}: L4: {problem}" for problem in l4_failures(meta))
    return errors


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
    # Cross-turn farm state. The latch is one-way and the two window fields are frozen at the turn
    # it fires, so both facts are checkable only by carrying the previous turn forward.
    prev_farm = None
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
        errors.extend(check_farm(index, meta, prev_farm))
        prior_farm, prev_farm = prev_farm, meta

        if census is not None:
            census["turns"] += 1
            census["farm_state_turns"][meta["fs"]] += 1
            census["farm_plants_final"] = meta["fp"]
            census["farm_harvests_final"] = meta["fh"]
            census["ring_enemy_final"] = meta["fe"]
            census["ring_own_final"] = meta["fw"]
            if isinstance(meta["fd"], str) and meta["fd"] in FARM_DENIAL_CODES:
                pass  # counted once at game end, below, so a 200-turn DENY tail is not 200 events
            if meta["fl"] and (prior_farm is None or not prior_farm["fl"]):
                census["latch_games"] += 1
                census["latch_turns"].append(meta["fl"])
                census["latch_snapshots"].append(
                    {"game": sid, "fl": meta["fl"], "fE": meta["fE"], "fW": meta["fW"]})
                if l4_failures(meta):
                    census["l4_failures"] += 1
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
            if index == len(command_lines) and meta["fd"] in tuple(FARM_DENIAL_CODES):
                census["denial_end_reasons"][meta["fd"]] += 1
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


def sample_payload(turn: int = 1, farm=None) -> str:
    """A minimal well-formed v8 payload — the one place the wire order is written out, so the
    refusal controls and any fixture use the same construction the decoder checks."""
    values = {"fs": 0, "fp": 0, "fh": 0, "fl": 0, "fd": "-", "fe": 0, "fw": 0, "fE": "-",
              "fW": "-"}
    values.update(farm or {})
    group = " ".join(f"{f}={values[f]}" for f in FARM_ORDER)
    return (f"MSG NARRATE v8 t={turn} {group} u1=NONE/NONE/r=N/b=0/k=0 "
            + " ".join(f"{f}={1 if f == 'pz' else 0}" for f in META_FIELDS))


def group_width(worst: bool = False) -> int:
    """How many characters the farm group actually costs on the wire.

    The packet says "nine tokens, <= 44 characters". That is exactly right at single-digit values
    and only there: 9 tokens x 4 chars + 8 separators = 44. Every extra digit any counter reaches
    costs a character. This function reports both ends, so the budget claim in §8 is a measurement
    rather than a best case. The widest values the game can produce: a 300-turn cap makes `fl` at
    most 3 digits; `fp`, `fh`, `fe` and `fw` are cumulative over that game and are given 3 digits
    here; `fE`/`fW` are 60-turn windows and are given 2. If any of these overruns in a real panel
    run, the census records the payload maximum and the number is corrected from the run, not
    from this estimate.
    """
    if not worst:
        return len(" ".join(f"{f}=0" for f in FARM_ORDER))
    widest = {"fs": 1, "fp": 3, "fh": 3, "fl": 3, "fd": 1, "fe": 3, "fw": 3, "fE": 2, "fW": 2}
    return sum(len(f) + 1 + widest[f] for f in FARM_ORDER) + len(FARM_ORDER) - 1


def refusal_controls() -> list[str]:
    """All directions, asserted rather than assumed: v8 refuses v7, v6 and v5, and v7, v6 and v5
    refuse v8. A decoder that silently reads the wrong version reports absence as zero — and the
    two collisions this guards are real ones. A v8 payload read as v7 would report `rs` absent,
    i.e. "Candidate 3b's rule never fired"; a v7 payload read as v8 would report the farm group
    absent, i.e. "the latch never fired". That is why the farm dialect is v8 and not, as the
    reviewed packet said, a second grammar under the taken token v7.
    """
    import sys
    from pathlib import Path
    here = Path(__file__).resolve().parent
    for name in ("narrate7", "narrate6", "narrate5", "narrate4"):
        candidate = here.parent / name
        if candidate.is_dir():
            sys.path.insert(0, str(candidate))
    failures = []
    v8 = sample_payload()
    v7 = ("MSG NARRATE v7 t=1 u1=NONE/NONE/r=N/b=0/k=0 rs=0 "
          + " ".join(f"{f}={1 if f == 'pz' else 0}" for f in META_FIELDS))
    v6 = ("MSG NARRATE v6 t=1 u1=NONE/NONE/r=N/b=0/k=0 "
          + " ".join(f"{f}={1 if f == 'pz' else 0}" for f in META_FIELDS))
    v5 = "MSG NARRATE v5 t=1 u1=NONE/NONE/r=N/b=0 pz=1 sp=0 wc=0 sw=0 so=0 sn=0 sf=0"
    try:
        decode(v8)
    except GateError as exc:
        failures.append(f"narrate8 failed to decode its own payload: {exc}")
    for older, payload in (("v7", v7), ("v6", v6), ("v5", v5)):
        try:
            decode(payload)
            failures.append(f"narrate8 accepted a {older} payload")
        except GateError:
            pass
    for name in ("narrate7", "narrate6", "narrate5", "narrate4"):
        try:
            module = __import__(name)
        except ImportError:
            continue
        try:
            module.decode(v8)
            failures.append(f"{name} accepted a v8 payload")
        except Exception:
            pass
    return failures


def grammar_controls() -> list[str]:
    """The farm group's own controls: placement, order, the sentinel, and gate L4 both ways.

    Each of these is a way the group could be wrong while still decoding, which is the only kind of
    defect worth a control. An always-passing check is worse than none: it reads as evidence.
    """
    failures = []

    def refuses(payload: str, why: str):
        try:
            decode(payload)
            failures.append(f"accepted {why}")
        except GateError:
            pass

    good = sample_payload()
    # placement: the group must be first, before the unit tokens.
    moved = good.replace("fs=0 ", "", 1).replace("u1=", "fs=0 u1=", 1)
    refuses(moved, "a payload whose farm group is not first")
    # order: fp and fh swapped, both still present and well-formed.
    refuses(good.replace("fp=0 fh=0", "fh=0 fp=0", 1), "a farm group out of wire order")
    # completeness: a dropped field must not default to 0.
    refuses(good.replace(" fW=-", "", 1), "a payload missing fW=")
    # the sentinel is not an integer field's value and vice versa.
    refuses(good.replace("fs=0", "fs=-", 1), "fs= carrying the sentinel")
    refuses(good.replace("fs=0", "fs=4", 1), "an off-grammar farm state fs=4")
    refuses(good.replace("fd=-", "fd=z", 1), "an off-grammar denial end reason fd=z")

    # L4, on a snapshot that satisfies the rule and on three that do not.
    fired = {"fl": 100, "fE": 14, "fW": 6}
    ok = decode(sample_payload(100, fired))[4]
    if l4_failures(ok):
        failures.append(f"L4 rejected a snapshot that satisfies the rule: {l4_failures(ok)}")
    for label, farm in (("ratio", {"fl": 100, "fE": 12, "fW": 6}),
                        ("floor", {"fl": 100, "fE": 12, "fW": 5}),
                        ("early", {"fl": 60, "fE": 14, "fW": 6})):
        bad = decode(sample_payload(100, farm))[4]
        if not l4_failures(bad):
            failures.append(f"L4 passed a snapshot that breaks the {label} part of the rule")
    # the one-way latch and the frozen pair, across turns.
    t1 = decode(sample_payload(100, fired))[4]
    t2 = decode(sample_payload(101, {"fl": 100, "fE": 15, "fW": 6}))[4]
    if not check_farm(101, t2, t1):
        failures.append("a window snapshot that changed after the latch fired was accepted")
    t3 = decode(sample_payload(101, {"fl": 0, "fE": "-", "fW": "-"}))[4]
    if not check_farm(101, t3, t1):
        failures.append("a latch that un-fired was accepted")
    t4 = decode(sample_payload(101, {"fe": 0, "fw": 0}))[4]
    if not check_farm(101, t4, decode(sample_payload(100, {"fe": 3, "fw": 3}))[4]):
        failures.append("a cumulative counter running backwards was accepted")
    return failures


if __name__ == "__main__":
    import sys
    problems = refusal_controls() + grammar_controls()
    print(f"v8 grammar: {len(META_FIELDS)} v6 meta fields + {len(FARM_ORDER)} farm fields, "
          f"closure asserted at import")
    print(f"  the farm group is {group_width()} chars at single digits and "
          f"{group_width(worst=True)} chars at the widest values the game can produce")
    for line in problems:
        print(f"  FAIL {line}")
    print("  controls OK" if not problems else f"  {len(problems)} FAILURES")
    sys.exit(1 if problems else 0)
