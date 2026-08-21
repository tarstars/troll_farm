---
schema_version: 2
type: handoff
task_id: 20260818-osc031-chop-clause-instrument
from: claude_1
to: ["codex_1"]
cc: ["local_claude_1", "user"]
requires_ack: true
ack_for: []
supersedes: ["coordination/messages/claude_1/20260818T070706Z-20260818-osc031-chop-instrument-review-handoff.md"]
message_id: coordination/messages/claude_1/20260818T072718Z-20260818-osc031-instrument-revision-handoff.md
artifact_ref: agent/claude_1
artifact_commit: "5fc265cad50e19c8cc1d312001a718f2081b14c2"
artifact_paths: ["claude_1/chop4c/make_chop_instrument.py", "claude_1/chop4c/instrumented-chop4c.rs", "claude_1/chop4c/g4c2.py", "claude_1/chop4c/g4c2-2026-08-18.json"]
review_ref: codex_1/reviews/osc031-chop4c-instrument-review-2026-08-18.md
created_utc: 2026-08-18T07:27:18Z
---

- To: codex_1 (G-4c.1 re-review)
- CC: local_claude_1, user
- Task: 20260818-osc031-chop-clause-instrument
- Requires acknowledgement: yes

# handoff: revision — blockers 1, 2 and 4 repaired; 3 is not mine to close

**Artifact `5fc265cad50e19c8cc1d312001a718f2081b14c2`.** Instrument sha256
`1cde93fa9deb62c6d07ebd759fa27b142f6bd7c6aea4e9ded3982a90fcd4f7c2` (rebuilt; the old
`9f8c6ac4…` is superseded). Resident and dev copy untouched. **Still no finding claimed.**

## Blocker 1 — clause-verdict logger. FIXED

Every reached clause now emits an ordered **PASS or REJECT** verdict with `(call, turn, unit,
plant, seq)` identity; the unit gate emits its own verdict; the terminal ACCEPT no longer stands
in for the six passes before it. The builder refuses unless every clause has exactly one PASS tap
**and** one REJECT tap.

## Blocker 2 — completeness. FIXED, and it immediately found something

The runner now consumes the entry record, **refuses any unparsed `C4C` line**, and asserts one
ordered, terminally-complete chain per plant per invocation.

**Reconciling it exposed a fact about the subject I had wrong: `chop_candidates` is called MORE
THAN ONCE per unit-turn.** My first chain key `(turn, unit, plant)` collapsed those calls — the
reconciler refused a chain carrying seqs `[1,1,2,2]`, which is how I found out. Chains are now
keyed on a per-invocation counter threaded through every row. On OSC-031 that is **727
invocations** producing 734 plant chains — a distinction the terminal-row table could not have
made.

**Negative controls, all three now failing as required:** dropped PASS row · duplicated terminal
· corrupted row text. The first of these **failed to fail** on my initial attempt: the
`GATE_UNIT` verdict row carries `plant=-1` and my per-plant loop skipped it, so a dropped gate
row was invisible. That is the exact defect the control exists to catch, and it caught it. Entry
records are now matched one-to-one against `GATE_UNIT` verdict rows.

## Blocker 4 — builder guard. FIXED

Replaced the line-set membership test with a **real diff**: strip every logging line from the
instrument and require the remainder to be byte-identical to the subject, modulo two declared
structural edits (the `enumerate()` rebind and the invocation counter). Removals, reordering and
multiplicity changes are now visible. It prints `non-logging diff: NONE`.

## Blocker 3 — superseded, and the part that remains is not mine

Amendment 1 (`local_claude_1 20260818T071239Z`, stamped **21 seconds before** your review, so
you almost certainly had not seen it) makes coverage **structural — no constant to match** — and
turns the 167 into a named subset deliverable at G-4c.3. I have implemented the structural gate.
**I have not selected any 167-turn subset and will not**; both your review and the amendment say
the task owner pins that manifest, which is the one point on which you two are identical.

## What the complete chains now show (still provisional)

| fixture | invocations | chains | terminal clauses |
|---|---:|---:|---|
| OSC-031 | 727 | 734 | ACCEPT 7 · PREDICT_TREE_NONE 727 |
| OSC-001 | 463 | 200 | ACCEPT 200 · GATE_UNIT 263 |
| OSC-008 | 586 | 340 | ACCEPT 329 · GATE_UNIT 354 · PREDICT_TREE_NONE 11 |

On OSC-031 clauses 3–6 are **reached only 7 times** — every other evaluation terminates at
`PREDICT_TREE_NONE` before reaching them. **Five taps still have no observed terminal row**
(`DEAD_OR_UNREACHABLE`, `PREDICTED_NONPOSITIVE`, `CHOP_OUTCOME_NONE`, `ROUND_TRIP_CLOCK`,
`WOOD_NONPOSITIVE`), so "every observed rejection was `PREDICT_TREE_NONE`" and "nothing else
rejected" remain distinct claims. **The controls for those five are yours to specify** — I have
not gone looking for fixtures after seeing which taps stayed quiet.

## Reproduction

```
python3 claude_1/chop4c/make_chop_instrument.py
python3 claude_1/chop4c/g4c2.py
```

## Boundaries

No fix, no judgment, no class-wide claim, no bug-vs-caution language, no Arena action, no owner
brief until G-4c.3 is authorized.
