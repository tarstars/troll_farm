#!/usr/bin/env python3
"""Phase 1 — is the pair the picker PREFERS actually executable?

The probe says every benched-with-work turn is blocked at the winner by `compatible()` — the two
units' targets are the same cell. This asks the next question, from the referee's own rules
(`sim/engine.py:134-150`: a MOVE into an occupied cell is dropped unless the occupant vacates):
**on those turns, is the winning partner command a MOVE onto the cell the benched unit occupies?**

If it is, the picker's choice is self-defeating by construction: it prefers the partner's promise
to walk to a cell, and in the same breath orders the occupant of that cell to WAIT, so the
promise cannot be kept — this turn or any turn, because nothing changes.

Positions come from the shared replay trace, not from the instrument.
"""
import json, re, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
for p in ("claude_1/t1", "claude_1/banana-restoration-r2", "claude_1/pipeline"):
    sys.path.insert(0, str(REPO / p))
import fixture_harness as H     # noqa: E402

MECH = HERE / "mechanism-all24-2026-08-20.json"
OUT = HERE / "deadlock-all24-2026-08-20.json"
SUBJECT = REPO / "cgauto/submissions/submitted-sub41153619-cure-c-quiet.rs"
MOVE = re.compile(r"^MOVE (\d+) (-?\d+) (-?\d+)$")


def main():
    mech = json.loads(MECH.read_text())
    cfg = json.loads(H.CONFIG.read_text())
    ids = [s["id"] for s in mech["situations"]]
    sits = {s["id"]: s for s in H.load_situations(ids)}
    results, tot = [], {"turns": 0, "onto_benched_cell": 0, "other_move": 0, "not_a_move": 0}
    with tempfile.TemporaryDirectory(prefix="ps1-dl-") as wd:
        b = H.compile_candidate(SUBJECT, Path(wd))
        for s in mech["situations"]:
            tr, _, _, _ = H.run_situation(sits[s["id"]], b, cfg)
            uid = s["unit"]
            c = {"onto_benched_cell": 0, "other_move": 0, "not_a_move": 0}
            for r in s["benched_turns"]:
                cmd = r.get("partner_kept_cmd", "")
                m = MOVE.match(cmd)
                if not m:
                    c["not_a_move"] += 1
                    continue
                cell = (int(m.group(2)), int(m.group(3)))
                c["onto_benched_cell" if tr.pos(uid, r["turn"]) == cell else "other_move"] += 1
            n = sum(c.values())
            tot["turns"] += n
            for k in c:
                tot[k] += c[k]
            results.append({"id": s["id"], "unit": uid, "benched_turns": n, **c})
            print(f"  {s['id']:9} unit {uid}  benched {n:4}  onto-benched-cell {c['onto_benched_cell']:4}"
                  f"  other-move {c['other_move']:4}  not-a-move {c['not_a_move']:4}")
    print(f"\nTOTAL {tot}")
    OUT.write_text(json.dumps({"task": "20260820-pair-selector-anti-benching", "phase": 1,
                               "subject_sha256": mech["subject_sha256"],
                               "referee_rule": "sim/engine.py:134-150 — a MOVE into an occupied "
                                               "cell is dropped unless the occupant vacates",
                               "totals": tot, "situations": results}, indent=2) + "\n")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
