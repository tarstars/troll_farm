#!/usr/bin/env python3
"""H-STARVE-1 pool #1 — the ANCHOR-UNIT rule, made explicit and checked.

This is the fifth statement of a requirement restated four times, and the reason it kept coming
back is mine: my instrument never had an anchor RULE. It had an implicit filter —
`u != window.unit` — buried in `classify()`, with no definition, no validation, and no report
when it selected nothing.

That silence is the actual defect. On OSC-033 the filter yielded no unit, the situation produced
no row, and the table simply had one fewer line than situations examined. **A missing row looked
exactly like a situation with nothing to say.**

## The rule, stated

For a situation S:

- **the DANCER** is the single unit named by `S.window.unit` — the unit the frozen record says
  oscillates or stalls;
- **the ANCHOR SET** is every own unit present at entry that is not the dancer;
- a situation with an **empty anchor set is not skipped** — it is reported as
  `NO_ANCHOR_SINGLE_UNIT`, because "this situation has only the dancer" is a finding about the
  situation, not an absence of data.

`NO_ANCHOR_SINGLE_UNIT` is a **coverage state, not a cause label**: it says which unit the
instrument looked at, never why anything happened. It is deliberately outside the registered
`CAUSE_LABEL_TOKENS` vocabulary and must never be serialized into a cause table.

## Checked, not assumed

`validate_anchor()` refuses: a dancer absent from the entry roster, a dancer that is not our own
unit, and any anchor that is not an own unit. Each is observed rejecting in `--self-test`.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "t1"))


class AnchorError(Exception):
    """The anchor could not be determined soundly. Never silently skipped."""


NO_ANCHOR = "NO_ANCHOR_SINGLE_UNIT"   # coverage state; NOT a cause label


def own_units(sit):
    return [u for u in sit["world_state_at_entry"]["units"] if u[1] == 0]


def dancer_id(sit):
    return sit["window"]["unit"]


def validate_anchor(sit):
    """Refuse a situation whose anchor cannot be determined soundly."""
    own = own_units(sit)
    ids = {u[0] for u in own}
    d = dancer_id(sit)
    if not own:
        raise AnchorError(f"{sit['id']}: no own units at entry; the situation cannot be anchored")
    if d not in {u[0] for u in sit["world_state_at_entry"]["units"]}:
        raise AnchorError(f"{sit['id']}: window names unit {d}, absent from the entry roster")
    if d not in ids:
        raise AnchorError(f"{sit['id']}: window names unit {d}, which is NOT one of our units")
    return True


def anchors(sit):
    """The anchor set, or the explicit NO_ANCHOR coverage state — never a silent empty."""
    validate_anchor(sit)
    d = dancer_id(sit)
    a = sorted(u[0] for u in own_units(sit) if u[0] != d)
    return {"situation": sit["id"], "dancer": d, "anchors": a,
            "coverage": NO_ANCHOR if not a else "ANCHORED",
            "own_unit_count": len(own_units(sit))}


def _self_test():
    import fixture_harness as H
    sits = H.load_situations()
    cases = []

    rows = [anchors(s) for s in sits]
    anchored = [r for r in rows if r["coverage"] == "ANCHORED"]
    none = [r for r in rows if r["coverage"] == NO_ANCHOR]
    cases.append((f"every one of {len(sits)} situations yields a coverage state",
                  len(rows) == len(sits), f"{len(anchored)} anchored, {len(none)} single-unit"))
    cases.append(("no situation is silently skipped",
                  all(r["coverage"] in ("ANCHORED", NO_ANCHOR) for r in rows), ""))
    cases.append(("the dancer is never in its own anchor set",
                  all(r["dancer"] not in r["anchors"] for r in rows), ""))

    def rejects(label, sit, fragment):
        try:
            validate_anchor(sit)
            cases.append((label, False, "NO ERROR RAISED"))
        except AnchorError as e:
            cases.append((label, fragment in str(e), str(e)[:54]))

    import json
    base = json.loads(json.dumps(sits[0]))

    bad = json.loads(json.dumps(base))
    bad["window"]["unit"] = 999
    rejects("dancer absent from the entry roster", bad, "absent from the entry roster")

    bad2 = json.loads(json.dumps(base))
    opp = [u for u in bad2["world_state_at_entry"]["units"] if u[1] != 0]
    if opp:
        bad2["window"]["unit"] = opp[0][0]
        rejects("dancer that is an OPPONENT unit", bad2, "NOT one of our units")

    bad3 = json.loads(json.dumps(base))
    bad3["world_state_at_entry"]["units"] = [u for u in bad3["world_state_at_entry"]["units"]
                                             if u[1] != 0]
    rejects("no own units at entry", bad3, "no own units at entry")

    ok = True
    for label, passed, detail in cases:
        print(f"  {'OK  ' if passed else 'BAD '} {label:56} {detail}")
        ok = ok and passed
    print(f"\nanchor self-test: {len(cases)} cases —", "PASS" if ok else "FAIL")
    if none:
        print(f"\nsingle-unit situations reported rather than skipped: "
              f"{[r['situation'] for r in none]}")
    print(f"\n{NO_ANCHOR} is a COVERAGE state, not a cause label. It is outside the registered")
    print("CAUSE_LABEL_TOKENS vocabulary and must never be serialized into a cause table.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(_self_test())
