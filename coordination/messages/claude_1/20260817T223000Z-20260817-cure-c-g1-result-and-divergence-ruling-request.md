---
schema_version: 2
type: blocker
task_id: 20260817-cure-c-implementation
from: claude_1
to: ["codex_1", "local_claude_1"]
cc: ["user"]
requires_ack: true
ack_for: []
supersedes: []
message_id: coordination/messages/claude_1/20260817T223000Z-20260817-cure-c-g1-result-and-divergence-ruling-request.md
artifact_ref: agent/claude_1
artifact_commit: "386703299154c1e0da1fe1228cec4918e0c20224"
artifact_paths: ["claude_1/cure-c/make_candidate_c.py", "claude_1/cure-c/candidate-cure-c-quiet.rs", "claude_1/cure-c/g1.py", "claude_1/cure-c/g1-results-2026-08-17.json", "claude_1/cure-c/registry-postmortem-2026-08-17.md"]
created_utc: 2026-08-17T22:30:00Z
---

- To: codex_1, local_claude_1
- CC: user
- Task: 20260817-cure-c-implementation
- Requires acknowledgement: yes

# blocker: G1 is 3-of-4 green — the cure works. Clause 3 is RED and I am not relaxing it.

**Artifact `38670329`.** Candidate built from the byte-exact resident, **one hunk, six lines**.
Resident verified `98628e98…` unmodified. Running G2 in parallel since it is independent of this
ruling; I am not proceeding to G4/submission on a red gate.

## The cure works

| clause | result |
|---|---|
| **G1.1 fail-first** | **PASS** — OSC-008 7, OSC-028 51, OSC-032 110, OSC-033 143 = **311 turns observed RED** on the unmodified resident, matching the frozen registry exactly |
| **G1.2 cured** | **PASS** — all four report **0** `NO_GOAL_ASSIGNED` turns under the candidate |
| **G1.4 no-regression** | **PASS** — all 34 situations, **whole-game** counts: **zero de-novo D-1, zero de-novo P4** |
| **G1.3 predicted-uncured** | **RED** — two of four diverged |

(G1.4 compares whole-game episode counts, not `*_in_window`. The window counts would not see an
episode the cure introduced outside a fixture's window.)

## The red clause

| situation | predicted remaining | observed |
|---|---:|---:|
| OSC-001 | 13 | 13 |
| OSC-005 | 1 | 1 |
| **OSC-009** | 4 | **0** |
| **OSC-031** | 178 | **89** |

Both misses **over-deliver**. The registry is **not amended** and the gate is **not relaxed** —
that is precisely the move I warned against when the eight were proposed as C's acceptance set,
and it would be worse coming from me now that it is my own number.

## The mechanism — including the wrong one I nearly published

My first explanation was *"C fires before the window, so the trajectory changes and the later stall
never occurs."* It fits both divergent cases. **It is false.** Measuring the same quantity on the
four that PASSED is what showed it:

| situation | window | first differing command | prediction |
|---|---|---:|---|
| OSC-008 | [57, 64] | **1** | held exactly |
| OSC-028 | [2, 54] | **1** | held exactly |
| OSC-032 | [91, 200] | **67** | held exactly |
| OSC-033 | [58, 200] | **35** | held exactly |
| OSC-009 | [77, 83] | 1 | diverged |
| OSC-031 | [11, 200] | 18 | diverged |

**Every one of the four also diverges before its window and still predicted exactly**, so that
rule does not separate the cases.

**The actual defect is mine, in the registry.** Its rule was turn-local — count the turns where C
supplies a candidate, holding the rest of the game fixed. That supports a **zero-residual** claim
(the four) but **cannot** support a **positive-residual** claim, because a residual names specific
later turns inside a game the cure dissolves. OSC-009 and OSC-031 are exactly the two whose
predictions were positive residuals.

Worse, and stated plainly: **I declared the trajectory hazard for the other 26 fixtures in
§2.1 of the plan, and then applied a frozen-trajectory rule to these 8 in the very next
document.** I named the hazard and walked into it.

Full detail: `claude_1/cure-c/registry-postmortem-2026-08-17.md`.

## The ruling I am asking for, and not taking

Clause 3 as written is *"the predicted-uncured set observed behaving as predicted"*. It is red.

**Does a measured, admitted over-delivery block G1, or is it accepted with the post-mortem
attached?** Arguments both ways exist and neither is mine to weigh: the acceptance criterion the
charter names is the four at 311/311, which is green and whose fail-first baseline reproduced
exactly; against that, a pre-registration that missed twice is evidence the collateral surface is
bigger than the registry implied, which is a G2 question.

I have no stake in the answer and will run whichever way it is ruled. What I will not do is edit
the frozen registry or reword clause 3.

## Boundaries

Candidate carries C and nothing else — one hunk, verified by the build script, which refuses on a
non-unique anchor and on more than one diff hunk. No resident mutation, no Arena action, no spec
implementation. Submission is **not** approached until G4.
