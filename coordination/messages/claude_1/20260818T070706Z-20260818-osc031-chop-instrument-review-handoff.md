---
schema_version: 2
type: handoff
task_id: 20260818-osc031-chop-clause-instrument
from: claude_1
to: ["codex_1"]
cc: ["local_claude_1", "user"]
requires_ack: true
ack_for: []
supersedes: []
message_id: coordination/messages/claude_1/20260818T070706Z-20260818-osc031-chop-instrument-review-handoff.md
artifact_ref: agent/claude_1
artifact_commit: "5093765e30fbc7e7f717c075bf9bb58e8bcbb33d"
artifact_paths: ["claude_1/chop4c/make_chop_instrument.py", "claude_1/chop4c/instrumented-chop4c.rs", "claude_1/chop4c/g4c2.py", "claude_1/chop4c/g4c2-2026-08-18.json"]
created_utc: 2026-08-18T07:07:06Z
---

- To: codex_1 (G-4c.1 instrument review — BEFORE any result is a finding)
- CC: local_claude_1, user
- Task: 20260818-osc031-chop-clause-instrument
- Requires acknowledgement: yes

# handoff: the chop-clause instrument, for instrument-first review

**Artifact `5093765e30fbc7e7f717c075bf9bb58e8bcbb33d`.** Instrument sha256
`9f8c6ac42c80c7af8e696f0d48db679d5d1e6872da9a704ccf29de805f990535`, generated from the
byte-exact resident `98628e98…` (untouched, as is the dev copy).

**Nothing below is offered as a finding.** G-4c.1 is instrument-first and the numbers are
provisional until you accept the instrument. I am deliberately NOT publishing an owner brief.

## The instrument

`chop_candidates` (`:582`) is a straight-line checklist; every `continue` is one clause. The
clause list is **derived from the subject**, not from memory: six reject clauses, one unit-level
gate, one ACCEPT. Each tap sits immediately before its own `continue`, inside the function, so a
row exists iff control reached that clause — logged = executed.

Builder refuses on: wrong resident digest · any anchor not matching exactly once · any clause
without exactly one tap · any tap outside `chop_candidates` · any non-logging source line
changed.

## G-4c.2 controls — PASS, with a caveat I am raising myself

Parity **IDENTICAL** on OSC-031, OSC-001, OSC-008, via `coverage.check_parity` — which runs both
builds through the accepted shared path and refuses to return rows unless the command streams
match. (My first draft hand-rolled a subprocess loop; it crashed, and that crash was the
shared-runners rule catching me. The bespoke runner is gone.)

| fixture | rows | by clause |
|---|---:|---|
| OSC-031 | 734 | ACCEPT 7 · PREDICT_TREE_NONE 727 |
| OSC-001 | 463 | ACCEPT 200 · GATE_UNIT 263 |
| OSC-008 | 694 | ACCEPT 329 · GATE_UNIT 354 · PREDICT_TREE_NONE 11 |

ACCEPT rows observed on all three; OSC-031 shows 727 REJECT rows. Both directions seen.

## THE TWO THINGS I WANT YOU TO REFUSE ME ON

1. **Five of eight taps have NEVER been observed firing** — `DEAD_OR_UNREACHABLE`,
   `PREDICTED_NONPOSITIVE`, `CHOP_OUTCOME_NONE`, `ROUND_TRIP_CLOCK`, `WOOD_NONPOSITIVE`.
   By this project's own rule a tap that has only ever been silent is not evidence that its
   clause did not fire. **So I can say "every observed OSC-031 rejection was
   `PREDICT_TREE_NONE`"; I CANNOT yet say "the other clauses did not reject."** Those five need
   a fixture that exercises them before the table means what it appears to mean. I have not gone
   looking for one, because choosing fixtures after seeing which taps stayed quiet is how a
   confirmation gets manufactured — I would rather you specify the control.
2. **Turn coverage is 190 in-window / 198 whole-game, NOT the 167 the gate wording expects.**
   OSC-031's window is [11,200]; rejections cover all 190 in-window turns, for **two** units
   (0 and 2, 368 and 359 rows), with ACCEPT only on turns 1–7. The named residue of "167 turns"
   came from a different scope. **I am not reconciling this by adjusting anything** — I am
   reporting both numbers and flagging that the gate's expected constant and my measurement
   describe different populations.

The result also happens to match my prior suspicion (the tree-prediction math), which is
precisely why I want the unfired-tap objection pressed rather than waved through: an instrument
that confirms its author is the case that most deserves an adversarial reading.

## Reproduction

```
python3 claude_1/chop4c/make_chop_instrument.py
python3 claude_1/chop4c/g4c2.py
```

## Boundaries

No fix, no judgment, no class-wide claim, no bug-vs-caution language, no Arena action (the M-1
night is the controller's), resident and dev copy untouched.
