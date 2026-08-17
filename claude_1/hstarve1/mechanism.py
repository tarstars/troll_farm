#!/usr/bin/env python3
"""H-STARVE-1 POOL #5 — mechanism note per NO_GOAL_ASSIGNED situation.

Authorized by `codex_1`'s GATE_ACCEPTED of the pool-#3 incidence revision
(`codex_1/reviews/h-starve-1-pool3-incidence-revision-review-2026-08-17.md`). Scope is exactly
the eight situations containing at least one `NO_GOAL_ASSIGNED` turn:

    OSC-001, OSC-005, OSC-008, OSC-009, OSC-028, OSC-031, OSC-032, OSC-033

The charter question (`ITERATION.md` item 5): **which generator path emits the WAIT-only list,
and is it deliberate (phase gating) or broken?**

This does NOT touch the 24 `GOAL_SPLIT_WRONG` situations. Per codex_1's acceptance, that token is
stage attribution and asserts nothing about whether `select()`'s joint-score choice was harmful.

## What is collected, and what it is not

For every `NO_GOAL_ASSIGNED` turn this records the routing branch the subject took and the
eligible actions the oracle reports the unit had — i.e. **what the generator was routed through
and what it declined to offer**, in the same turn.

That pairing is the whole mechanism claim, and it is deliberately narrow: it says *this branch,
holding this eligibility, emitted only WAIT*. It does not claim the branch is defective. Whether
an omission is deliberate phase gating or a gap is answered per situation from the branch's own
code, and where the reading is that the subject is behaving as designed, this says so.
"""
from __future__ import annotations

import collections
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "t1"))
sys.path.insert(0, str(HERE.parent / "banana-restoration-r2"))
import cause_table as CT        # noqa: E402
import coverage as C            # noqa: E402
import fixture_harness as H     # noqa: E402
import fuzz_panel as fp         # noqa: E402
import oracle as O              # noqa: E402
import trace_detectors as td    # noqa: E402

REVIEW_REF = "codex_1/reviews/h-starve-1-pool3-incidence-revision-review-2026-08-17.md"
TABLE = HERE / "cause-table-pool3-2026-08-17.json"
TOTAL_TURNS = 300      # subject :81


def harvest_gate_blame(tr, uid, t):
    """Why did `idle_harvest_candidates` produce nothing on a turn the oracle calls harvestable?

    Replicates the subject's filter clause-by-clause (:1348-1362) and names the FIRST clause that
    rejects every fruiting plant. The oracle's HARVEST arm requires only capability, fruit and
    reachability from the unit; the subject additionally requires a path back to the shack, an
    unclaimed plant, and a round trip inside the clock. Listing which of those bites is the whole
    point — "one of these probably rejected it" is the kind of unverified proxy this track has
    already retracted three of.
    """
    st, u = tr.state(t), tr.unit(uid, t)
    if u is None:
        return "NO_UNIT"
    if u.harvest_power <= 0 or sum(u.carry) != 0:
        return "IDLE_HARVEST_PRECONDITION"       # carrying, or cannot harvest
    from_unit = td.bfs_distances(tr.smap.walkable, [u.cell])
    shack = tr.smap.shacks[0]
    starts = [c for c in ((shack[0]+dx, shack[1]+dy) for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)))
              if c in tr.smap.walkable]
    to_shack = td.bfs_distances(tr.smap.walkable, starts)
    turns_left = TOTAL_TURNS - t + 1
    fruiting = [p for p in st.plants if p.health > 0 and p.fruits > 0]
    if not fruiting:
        return "NO_FRUITING_PLANT"
    reasons = collections.Counter()
    for p in fruiting:
        if p.cell not in from_unit:
            reasons["UNREACHABLE_FROM_UNIT"] += 1
        elif p.cell not in to_shack:
            reasons["NO_PATH_BACK_TO_SHACK"] += 1
        elif any(o.player == 1 and o.cell == p.cell and sum(o.carry) == 0
                 for o in st.units) and u.cell != p.cell:
            reasons["OPPONENT_SITTING_ON_PLANT"] += 1
        else:
            speed = max(1, u.speed)
            travel = -(-from_unit[p.cell] // speed)
            home = -(-to_shack[p.cell] // speed)
            if travel + 1 + home + 1 > turns_left:
                reasons["ROUND_TRIP_EXCEEDS_CLOCK"] += 1
            else:
                reasons["WOULD_HAVE_QUALIFIED"] += 1
    return "|".join(f"{k}x{v}" for k, v in sorted(reasons.items()))


def main():
    table = json.loads(TABLE.read_text())
    targets = table["pool5_input_no_goal_assigned_situations"]
    if len(targets) != 8:
        raise SystemExit(f"expected the 8 accepted situations, got {targets}")
    only = sys.argv[1].split(",") if len(sys.argv) > 1 else targets
    cfg = json.loads(H.CONFIG.read_text())
    sits = H.load_situations(only)

    notes = []
    with tempfile.TemporaryDirectory(prefix="hs2-mech-") as wd:
        di, dp = Path(wd) / "i", Path(wd) / "p"
        di.mkdir(); dp.mkdir()
        instr = H.compile_candidate(C.INSTR, di)
        plain = H.compile_candidate(H.RESIDENT, dp)
        for sit in sits:
            err = C.check_parity(sit, cfg, plain, instr)
            C.check_final_stage(sit, err)
            spec = H.spec_for(sit, cfg)
            transcript, commands, _ = C.run_diagnostic(
                instr, fp.make_referee(spec), int(cfg["turns"]))
            tr = td.build_trace(transcript, commands)
            rows = CT.classify(sit, *CT.parse(err), tr)
            for r in rows:
                ng = [p for p in r.get("per_turn", []) if p["token"] == "NO_GOAL_ASSIGNED"]
                if not ng:
                    continue
                uid = r["unit"]
                acts = collections.Counter()
                blame = collections.Counter()
                for p in ng:
                    el = sorted(O.eligible_actions(tr, uid, p["turn"]))
                    acts["+".join(el) or "NONE"] += 1
                    if "HARVEST" in el:
                        blame[harvest_gate_blame(tr, uid, p["turn"])] += 1
                u0 = tr.unit(uid, ng[0]["turn"])
                notes.append({
                    "situation": sit["id"], "kind": sit["kind"], "unit": uid,
                    "no_goal_turns": len(ng),
                    "turn_span": [ng[0]["turn"], ng[-1]["turn"]],
                    "branches": dict(collections.Counter(p["branch"] for p in ng)),
                    "eligible_actions_declined": dict(acts),
                    "harvest_gate_blame": dict(blame),
                    "unit_capability": {"harvest": u0.harvest_power, "chop": u0.chop_power,
                                        "speed": u0.speed, "capacity": u0.capacity},
                    "carry_at_first_turn": list(u0.carry),
                })
                n = notes[-1]
                print(f"  {n['situation']}  unit {n['unit']}  {n['no_goal_turns']:>3} turns "
                      f"{n['turn_span']}  branches={n['branches']}  "
                      f"declined={n['eligible_actions_declined']}  "
                      f"harvest_gate={n['harvest_gate_blame'] or '-'}  "
                      f"cap=h{n['unit_capability']['harvest']}/c{n['unit_capability']['chop']}  "
                      f"carry={n['carry_at_first_turn']}")

    by_branch = collections.Counter()
    by_action = collections.Counter()
    for n in notes:
        for b, k in n["branches"].items():
            by_branch[b] += k
        for a, k in n["eligible_actions_declined"].items():
            by_action[a] += k
    print(f"\nNO_GOAL_ASSIGNED turns by routing branch: {dict(by_branch)}")
    print(f"eligible actions declined on those turns:  {dict(by_action)}")

    out = HERE / "mechanism-pool5-2026-08-17.json"
    out.write_text(json.dumps({
        "pool": 5,
        "review_ref": REVIEW_REF,
        "situations": targets,
        "notes": notes,
        "turns_by_branch": dict(by_branch),
        "eligible_actions_declined": dict(by_action),
    }, indent=1, sort_keys=True) + "\n")
    print(f"\nwrote {out.relative_to(HERE.parent.parent)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
