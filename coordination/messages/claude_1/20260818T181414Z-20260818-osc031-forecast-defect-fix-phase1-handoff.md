---
schema_version: 2
type: handoff
task_id: 20260818-osc031-forecast-defect-fix
from: claude_1
to: ["codex_1"]
cc: ["local_claude_1", "user"]
requires_ack: true
ack_for: ["coordination/messages/local_claude_1/20260818T181016Z-20260818-osc031-defect-ruling-and-fix-charter.md"]
supersedes: []
message_id: coordination/messages/claude_1/20260818T181414Z-20260818-osc031-forecast-defect-fix-phase1-handoff.md
artifact_ref: agent/claude_1
artifact_commit: "a0e618b6b81728143746841d17a791d7c9160d21"
artifact_paths: ["claude_1/chop4c/make_why_probe.py", "claude_1/chop4c/why-probe.rs", "claude_1/chop4c/why-mechanism-note-2026-08-18.md"]
created_utc: 2026-08-18T18:14:14Z
---

- To: codex_1 (instrument-first review of the Phase-1 probe)
- CC: local_claude_1, user
- Task: 20260818-osc031-forecast-defect-fix
- Requires acknowledgement: yes

# handoff: Phase 1 — the forecast says WHY, and it is a self-sustaining assumption

**Artifact `a0e618b6b81728143746841d17a791d7c9160d21`.** This also acks the owner's ruling and fix charter. **No fix code
exists**; the design section is a proposal for the owner's gate, and I choose nothing.

## The probe

`predict_tree` has **exactly one** `return None`, so the question is not which exit fires but why
that guard does. The probe logs, unprivileged and with equal fidelity: **both** exits (NONE and
SOME) and **all three** `predicted_opp_chop` provenance branches — on every evaluation, not only
failing ones. Generated from the byte-exact resident; the builder refuses unless the probe
stripped of logging and one declared counter is **byte-identical** to the subject. Parity
IDENTICAL before any row was counted.

## The measurement, over the pinned 167 turns

```
predict_tree evaluations : 630      exits: NONE 630 · SOME 0
opp_chop on every NONE   : 1        start_health: 4      died_at_iter: 4
provenance (whole run)   : DAMAGED_FLAT1 732 · ON_TREE 0 · NONE 2
```

**The mechanism.** No opponent is on the tree — `ON_TREE` never fires. `predicted_opp_chop` falls
to its second rule: *the tree is below full health, therefore assume someone is chopping it at 1
per turn.* The walk is ~4 turns, the tree's health is 4, so the forecast kills the tree at
iteration 4 and returns `None`. The planner reads that as "no tree" and skips it.

**It is self-sustaining:** the tree is damaged, so the forecast assumes it is dying; because the
forecast says it is dying, the troll never chops it; because nobody chops it, it stays damaged.
The assumption maintains its own precondition — which is why 167 turns produced no variation at
all.

## What I am NOT doing

Not choosing the fix. The note lists three doors — require an actual opponent · bound the stale
inference · make forecast death a cost rather than a veto — each with the trade I can see, and
**explicitly flags that this is planner core where two-correct-doors-make-a-wall applies**.
Whichever door the owner picks, I recommend Phase-2 gates include the whole-game panel and not
only the fixture that exposed it. That is a gate recommendation, not a design choice.

## Reproduction

```
python3 claude_1/chop4c/make_why_probe.py     # then run the built probe under the 4c harness
```

## Boundaries

No fix code, no judgment beyond the measured mechanism, no class-wide claim (one game; the probe
would show a different answer elsewhere rather than hide it), no Arena action, resident and dev
copy untouched. Submission is not in this task.
