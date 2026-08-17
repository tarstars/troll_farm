#!/usr/bin/env python3
"""H-STARVE-1 POOL #3 — the 34-situation cause sweep, serialized in the five registered tokens.

Authorized by `codex_1`'s GATE_ACCEPTED of the logging repair
(`codex_1/reviews/h-starve-1-pool1-logging-repair-review-2026-08-17.md`). Runs on the repaired
instrument, whose taps sit AFTER `force_unique_door_clear` and AFTER `resolve_move_conflicts`.

## Why this can be answered now and could not be before

The owner's verdict rule names the cure property: *"a troll with reachable, usable work receives
at least one non-WAIT candidate."* Deciding whether that property was violated requires knowing
**which stage produced the WAIT**, and until the logging repair the instrument could not tell
"the generator offered only WAIT" from "the generator offered a MOVE and a later pass overrode
it". On this corpus that difference is 97 turns of manufactured `MOVE -> WAIT`, so it is not a
hypothetical.

Four stages are now observable per unit-turn:

| stage | record | a WAIT appearing here means |
|---|---|---|
| generator | `HS2PRE` | the candidate generator itself offered nothing else |
| door clear | `HS2` vs `HS2PRE` | `force_unique_door_clear` replaced the list |
| selector | `HS2CHOSENPRE` vs `HS2` | `select()` rejected this unit's options against another unit's |
| resolver | `HS2CHOSEN` vs `HS2CHOSENPRE` | `resolve_move_conflicts` overrode a real command |

## THE TOKEN DEFINITIONS ARE MINE, AND THAT IS FLAGGED, NOT BURIED

`local_claude_1`'s registry message (`20260817T080201Z`) binds the SPELLING of the five tokens
and nothing else: no semantics for them were ever published, and I have searched the pool
charter, the registry message and `ITERATION.md`. I said in my registry ack that I would not map
my old labels onto the new five by inference, and I am not doing that — these definitions are
derived from the **owner's cure property and the four observable stages**, stated here in full so
they can be overruled without re-running anything:

- `NOT_STARVED` — the unit was not parked: **fewer than half** its window turns were WAIT. (My
  first rule also cleared any unit that acted even once, which called OSC-023 not-starved on 73
  WAITs out of 74. One action in a window does not un-park a troll.)
- `CANNOT_USE_WORK` — the unit was idle on turns where the eligible-action oracle reports it had
  **no usable work of its own** (capability x fruit state x sink, BFS from its own cell). The
  planner offering nothing was correct. This is the arm that vindicated OSC-012's planner.
- `NO_GOAL_ASSIGNED` — the unit had usable work and the **generator itself** emitted only WAIT.
  This is the cure property violated at its source.
- `GOAL_SPLIT_WRONG` — the generator offered a real candidate and **`select()`** discarded it
  because another own unit had already claimed a compatible target or the stock. A goal existed;
  the two-troll split gave it away.
- `WORLD_INTERACTION` — the generator offered a real candidate and a **world-facing pass**
  replaced it: `resolve_move_conflicts` (another unit's landing cell) or `force_unique_door_clear`
  (shack-door geometry).

**`GOAL_SPLIT_WRONG` records WHERE the WAIT came from, not that the selector chose badly.**
`select()` maximises a joint score, so preferring a pair in which this unit waits can be the
correct trade. The token says the goal existed and the split withheld it from this unit; whether
that trade was worth making is the owner's call in pool #6, and nothing here measures it. The
registry fixed the spelling before anyone defined the semantics, and I am not reading a verdict
into the word "wrong".

The per-turn attribution is written to the artifact in full, so a different situation-level rule
can be applied to the same measurements without re-running the sweep.

## What is NOT claimed

This assigns a cause to the WAITs of the RULED ANCHOR unit of each situation. It is not a
Decision Packet, it does not price anything, and it makes no claim about whether any cause is
worth curing — that is pool #6, the owner's.
"""
from __future__ import annotations

import collections
import json
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "t1"))
sys.path.insert(0, str(HERE.parent / "banana-restoration-r2"))
import anchor as A              # noqa: E402
import coverage as C            # noqa: E402
import fixture_harness as H     # noqa: E402
import fuzz_panel as fp         # noqa: E402
import oracle as O              # noqa: E402
import trace_detectors as td    # noqa: E402

REVIEW_REF = "codex_1/reviews/h-starve-1-pool1-logging-repair-review-2026-08-17.md"

TOKENS = ["NO_GOAL_ASSIGNED", "GOAL_SPLIT_WRONG", "WORLD_INTERACTION",
          "CANNOT_USE_WORK", "NOT_STARVED"]

ROW = re.compile(r"HS2(PRE)? turn=(\d+) unit=(\d+) cell=\S+ branch=(\w+) endgame=(\w+) "
                 r"committed=(\w+) ncand=(\d+) kinds=([^\n]*)")
CHOSEN = re.compile(r"HS2CHOSEN(PRE)? turn=(\d+) line=([^\n]*)")

def _subject_verbs():
    """Command verbs read from the SUBJECT, not hand-listed.

    My hand-written set omitted `MINE`, and the structural guard in `parse()` caught it on
    OSC-026 rather than letting an unknown verb be silently treated as "not WAIT". Deriving the
    set from the subject means the next verb the bot learns cannot quietly bypass the guard —
    the same reason the viewer reads inventory slot order out of the subject instead of
    restating it.
    """
    src = H.RESIDENT.read_text()
    verbs = set(re.findall(r'format!\("([A-Z]+) \{\}', src)) | set(re.findall(r'"([A-Z]+)"', src))
    verbs &= {"WAIT", "MOVE", "HARVEST", "CHOP", "PICK", "DROP", "PLANT", "MINE"}
    if len(verbs) < 8:
        raise SweepError(f"only {sorted(verbs)} recovered from the subject; expected 8 verbs")
    return verbs


class SweepError(Exception):
    """Fail-closed. Nothing is serialized after one."""


VERBS = _subject_verbs() | {"?"}
WITH_ID = _subject_verbs() - {"WAIT"}   # every action command carries unit.id as its first arg


def parse(err):
    """-> stages[turn][unit] = {'gen': kinds, 'sel_in': kinds}, chosen[turn] = {'pre','final'}

    The `ncand`/`kinds` groups are ADJACENT and I first read the wrong one: `kinds` came back as
    `["1"]` — the count — so `any(k != "WAIT" for k in kinds)` was **always true**, which made
    `NO_GOAL_ASSIGNED` unreachable and swept every idle-with-work turn into `GOAL_SPLIT_WRONG`.
    The run was green and the totals looked plausible; only reading a per-turn record showed it.

    So the parse is now checked structurally on every row rather than trusted: each kind must be
    a real command verb, and `ncand` must equal the number of kinds. An off-by-one group index
    fails immediately instead of producing a confident, wrong table.
    """
    stages, chosen = {}, {}
    for m in ROW.finditer(err):
        t, u = int(m.group(2)), int(m.group(3))
        key = "gen" if m.group(1) else "sel_in"
        ncand, raw = int(m.group(7)), m.group(8)
        kinds = raw.split("|") if raw else []
        bad = [k for k in kinds if k not in VERBS]
        if bad:
            raise SweepError(f"turn {t} unit {u}: {bad!r} are not command verbs — the kinds "
                             f"group is being read off the wrong capture (this exact defect "
                             f"made NO_GOAL_ASSIGNED unreachable once already)")
        if ncand != len(kinds):
            raise SweepError(f"turn {t} unit {u}: ncand={ncand} but {len(kinds)} kinds parsed")
        stages.setdefault(t, {}).setdefault(u, {})[key] = kinds
        stages[t][u].setdefault("branch", m.group(4))
    for m in CHOSEN.finditer(err):
        chosen.setdefault(int(m.group(2)), {})["pre" if m.group(1) else "final"] = m.group(3)
    return stages, chosen


def slot_map(line, ids):
    """Map each command slot to a unit id, and PROVE the mapping rather than assume it.

    `select()` returns exactly one command per id in ascending id order (the general arm loops
    `for id in ids` over BTreeMap keys; the 1- and 2-unit arms return in the same order). Every
    command except `WAIT` carries its unit id, so the mapping is checkable on real data: for each
    id-bearing command, slot index must equal the unit's position in the sorted id list.

    A WAIT slot is the ONLY case where the id is not in the text, and it is the case the whole
    table turns on — so the mapping it relies on is verified from its neighbours on every turn of
    every situation rather than asserted once in a comment.
    """
    parts = (line or "").split(";")
    if len(parts) != len(ids):
        raise SweepError(f"chosen line has {len(parts)} slots for {len(ids)} own units: {line!r}")
    for i, part in enumerate(parts):
        f = part.split()
        if f and f[0] in WITH_ID:
            if len(f) < 2 or not f[1].lstrip("-").isdigit():
                raise SweepError(f"command {part!r} names no unit id")
            if int(f[1]) != ids[i]:
                raise SweepError(
                    f"SLOT MAPPING BROKEN: slot {i} holds unit {f[1]} but ids[{i}]={ids[i]} "
                    f"in {line!r} — WAIT slots could not then be attributed to a unit.")
    return {ids[i]: parts[i] for i in range(len(ids))}


def verb(cmd):
    f = (cmd or "").split()
    return f[0] if f else "?"


def attribute_turn(gen, sel_in, sel_out, final, has_work):
    """Which stage produced this unit's WAIT? Returns a token or None if the unit acted."""
    if verb(final) != "WAIT":
        return None
    if not has_work:
        return "CANNOT_USE_WORK"
    if verb(sel_out) != "WAIT":
        return "WORLD_INTERACTION"          # resolver overrode a real command
    if any(k != "WAIT" for k in sel_in):
        return "GOAL_SPLIT_WRONG"           # select() discarded this unit's real options
    if any(k != "WAIT" for k in gen):
        return "WORLD_INTERACTION"          # door clear replaced the generator's list
    return "NO_GOAL_ASSIGNED"               # the generator itself offered only WAIT


def classify(sit, stages, chosen, tr, force_units=None):
    w = sit["window"]
    lo, hi = w["turn_start"], w["turn_end"]
    anc = A.anchors(sit)
    if anc["coverage"] == A.UNRULED:
        raise SweepError(f"{sit['id']}: {anc['rule']} — fail-closed, never folded into a token")
    if anc["coverage"] == A.NO_ANCHOR:
        return [{"situation": sit["id"], "unit": None, "token": None,
                 "coverage": A.NO_ANCHOR, "anchor_rule": anc["rule"],
                 "note": "single own unit; no anchor exists. A coverage state, NOT a cause."}]

    ids = sorted(u[0] for u in A.own_units(sit))
    out = []
    for uid in (force_units if force_units is not None else anc["anchors"]):
        per_turn, waits = [], collections.Counter()
        acted = 0
        for t in range(lo, hi + 1):
            su = stages.get(t, {}).get(uid)
            ch = chosen.get(t)
            if su is None or ch is None:
                raise SweepError(f"{sit['id']}: no record for turn {t} unit {uid} "
                                 f"(coverage passed, so this is a parsing fault)")
            pre_slots = slot_map(ch["pre"], ids)
            fin_slots = slot_map(ch["final"], ids)
            has_work = bool(O.eligible_actions(tr, uid, t)) if tr is not None else False
            tok = attribute_turn(su.get("gen", []), su.get("sel_in", []),
                                 pre_slots[uid], fin_slots[uid], has_work)
            if tok is None:
                acted += 1
            else:
                waits[tok] += 1
            per_turn.append({"turn": t, "token": tok, "usable_work": has_work,
                             "gen": su.get("gen", []), "sel_in": su.get("sel_in", []),
                             "sel_out": pre_slots[uid], "final": fin_slots[uid],
                             "branch": su.get("branch")})

        total = hi - lo + 1
        wait_turns = total - acted
        # NOT_STARVED is a MAJORITY rule, not "it moved once". My first version said
        # `acted > 0 or ...`, which called OSC-023 not-starved on 73 WAITs out of 74 — a single
        # action in a whole window cleared a plainly parked troll. Only the fraction decides.
        if wait_turns * 2 < total:
            token = "NOT_STARVED"
        else:
            token = waits.most_common(1)[0][0]
        if token not in TOKENS:
            raise SweepError(f"{sit['id']}: token {token!r} is not registered")

        out.append({
            "situation": sit["id"], "kind": sit["kind"], "unit": uid, "token": token,
            "coverage": "ANCHORED", "anchor_rule": anc["rule"],
            "window": [lo, hi], "turns_in_window": total,
            "turns_acted": acted, "turns_wait": wait_turns,
            "turns_with_usable_work": sum(1 for r in per_turn if r["usable_work"]),
            "wait_attribution": dict(waits),
            "per_turn": per_turn,
        })
    return out


def positive_control():
    """WORLD_INTERACTION scores ZERO on the anchored table. Prove the arm can fire anyway.

    The 97 manufactured `MOVE -> WAIT` turns are real, but on this corpus they land on the
    DANCER, never on the ruled anchor: 94 of them are OSC-034 unit 2 (anchor is unit 0) and the
    one in OSC-002 falls outside the window. So the zero is a MEASUREMENT — the resolver never
    overrode a parked troll here — and not a dead branch.

    "Zero because it never happens" and "zero because the code cannot reach it" look identical
    in a totals line, and I have shipped the second one before while believing the first. So the
    same classifier is re-run against OSC-034 unit 2, where the overrides do land, and must
    return WORLD_INTERACTION turns.
    """
    cfg = json.loads(H.CONFIG.read_text())
    sit = H.load_situations(["OSC-034"])[0]
    with tempfile.TemporaryDirectory(prefix="hs2-ctl-") as wd:
        di, dp = Path(wd) / "i", Path(wd) / "p"
        di.mkdir(); dp.mkdir()
        instr = H.compile_candidate(C.INSTR, di)
        plain = H.compile_candidate(H.RESIDENT, dp)
        err = C.check_parity(sit, cfg, plain, instr)
        spec = H.spec_for(sit, cfg)
        transcript, commands, _ = C.run_diagnostic(instr, fp.make_referee(spec), int(cfg["turns"]))
        tr = td.build_trace(transcript, commands)
        rows = classify(sit, *parse(err), tr, force_units=[2])
    got = rows[0]["wait_attribution"].get("WORLD_INTERACTION", 0)
    print(f"  OSC-034 unit 2 (the DANCER, not the anchor): {rows[0]['wait_attribution']}")
    if not got:
        print("  FAIL positive control: WORLD_INTERACTION never fired even where the resolver "
              "demonstrably overrides commands — the arm is dead, and the zero above means "
              "nothing.")
        return 1
    print(f"\nWORLD_INTERACTION observed firing on {got} turns. The zero in the anchored table "
          f"is a measurement:\nthe resolver overrode the DANCER, never the parked anchor.")
    return 0


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--control":
        return positive_control()
    only = sys.argv[1].split(",") if len(sys.argv) > 1 else None
    cfg = json.loads(H.CONFIG.read_text())
    sits = H.load_situations(only)

    table = []
    with tempfile.TemporaryDirectory(prefix="hs2-cause-") as wd:
        di, dp = Path(wd) / "i", Path(wd) / "p"
        di.mkdir(); dp.mkdir()
        instr = H.compile_candidate(C.INSTR, di)
        plain = H.compile_candidate(H.RESIDENT, dp)
        for sit in sits:
            # parity + coverage + post-mutation stage gate EVERY read, exactly as accepted
            err = C.check_parity(sit, cfg, plain, instr)
            C.check_final_stage(sit, err)
            C.check_coverage(sit, err)
            spec = H.spec_for(sit, cfg)
            transcript, commands, _ = C.run_diagnostic(
                instr, fp.make_referee(spec), int(cfg["turns"]))
            tr = td.build_trace(transcript, commands)
            rows = classify(sit, *parse(err), tr)
            table.extend(rows)
            for r in rows:
                if r["token"] is None:
                    print(f"  {r['situation']}  ---  {A.NO_ANCHOR}")
                else:
                    print(f"  {r['situation']}  unit {r['unit']}  {r['token']:<17} "
                          f"wait={r['turns_wait']:>3}/{r['turns_in_window']} "
                          f"work={r['turns_with_usable_work']:>3} "
                          f"{r['wait_attribution']}")

    counts = collections.Counter(r["token"] for r in table if r["token"])
    per_turn_counts = collections.Counter(
        pt["token"] for r in table for pt in r.get("per_turn", []) if pt["token"])
    print(f"\nCAUSE TABLE — {len(table)} anchored observations over {len(sits)} situations")
    print("\nsituation-level tokens:")
    for tok in TOKENS:
        print(f"  {tok:<18} {counts.get(tok, 0)}")
    nocov = sum(1 for r in table if r["token"] is None)
    if nocov:
        print(f"  ({A.NO_ANCHOR}: {nocov} — a coverage state, not a cause)")
    print("\nWAIT turns attributed by stage (all anchored units, all windows):")
    for tok in TOKENS:
        if per_turn_counts.get(tok):
            print(f"  {tok:<18} {per_turn_counts[tok]}")

    out = HERE / "cause-table-pool3-2026-08-17.json"
    out.write_text(json.dumps({
        "pool": 3,
        "review_ref": REVIEW_REF,
        "instrument": "claude_1/hstarve1/instrumented-hstarve2.rs (logging-repaired)",
        "subject_sha256": "98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29",
        "situations": len(sits),
        "token_definitions_authored_by": "claude_1 — the registry bound the SPELLING only; no "
                                         "semantics were ever published. Stated in the module "
                                         "docstring and open to being overruled.",
        "situation_level_totals": {t: counts.get(t, 0) for t in TOKENS},
        "wait_turn_totals_by_stage": {t: per_turn_counts.get(t, 0) for t in TOKENS},
        "no_anchor_coverage_states": nocov,
        "table": table,
    }, indent=1, sort_keys=True) + "\n")
    print(f"\nwrote {out.relative_to(HERE.parent.parent)}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SweepError as e:
        print(f"  FAIL {e}")
        sys.exit(1)
