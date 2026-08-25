---
schema_version: 2
type: handoff
task_id: 20260818-osc031-forecast-defect-fix
from: claude_1
to: ["codex_1"]
cc: ["local_claude_1", "user"]
requires_ack: true
ack_for: ["coordination/messages/local_claude_1/20260818T192838Z-20260818-osc031-predicate-resume-order.md"]
supersedes: []
message_id: coordination/messages/claude_1/20260818T193329Z-20260818-osc031-predicate-comparison-handoff.md
artifact_ref: agent/claude_1
artifact_commit: "2189ccf845c011f7ade2d6958f483509133708d1"
artifact_paths: ["claude_1/chop4c/make_predicate_probe.py", "claude_1/chop4c/predicate-probe.rs", "claude_1/chop4c/predicate-comparison-2026-08-18.json"]
created_utc: 2026-08-18T19:33:29Z
---

- To: codex_1 (predicate comparison review)
- CC: local_claude_1, user
- Task: 20260818-osc031-forecast-defect-fix
- Requires acknowledgement: yes

# handoff: the predicate comparison — measured, and one pair is indistinguishable

**Artifact `2189ccf845c011f7ade2d6958f483509133708d1`.** This also acks the resume order; the work started on session pickup as
directed. **No fix code.** Probe generated from the byte-exact resident with the byte-identity
guard; **parity IDENTICAL on each of the 34 fixtures**, checked per fixture before any row counted.

## The measurement — all 34 fixtures, every `predicted_opp_chop` call

```
calls                                    11,414
on-tree evidence exists (rule 1 fires)      412
DAMAGED_FLAT1 fires (no opponent on tree) 7,385
```

Of those **7,385** firings — every one an assumption made with **no opponent on the tree**:

| candidate predicate | would ADMIT the assumption | would SUPPRESS |
|---|---:|---:|
| **on-tree** | **0** (0.0%) | **7,385** |
| **adjacent** | **68** (0.9%) | 7,317 |
| **in-reach** | **68** (0.9%) | 7,317 |

## What I did not expect, and will not paper over

**Adjacent and in-reach are indistinguishable on this corpus — both 68, and the same 68.** There
is no fixture where an opponent is within one move of a tree but not orthogonally adjacent to it.
So **the measurement cannot separate them**, and any preference I stated between the two would be
taste dressed as evidence.

## Proposal

**Primary: on-tree.** It is the literal reading of the owner's ruling — the assumption fires only
on an opponent *actually observed at the tree* — and it suppresses all 7,385 evidence-free
firings while leaving the 412 evidenced ones untouched.

**If the owner wants a safety margin** for the opponent who is one step away, adjacent and
in-reach are **equally supported by this evidence (identical on all 34 fixtures)**, so that
choice cannot be made on these numbers. I flag it as **potentially load-bearing and therefore an
owner escalation**, not something I should settle: it changes behaviour on 68 calls, and the two
options are distinguishable only on corpora this one does not contain.

## Reproduction

```
python3 claude_1/chop4c/make_predicate_probe.py   # then run under the 4c harness, 34 fixtures
```

## Boundaries

No fix code, no door reopened, no class-wide claim beyond these 34 fixtures, no Arena action;
resident and dev copy untouched. Phase-2 build follows your review and any owner escalation.
