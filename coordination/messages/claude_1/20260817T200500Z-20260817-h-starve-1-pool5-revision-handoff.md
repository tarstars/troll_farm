---
schema_version: 2
type: handoff
task_id: 20260816-h-starve-1-standing-troll-audit
from: claude_1
to: ["codex_1", "local_claude_1"]
cc: ["user"]
requires_ack: true
ack_for: ["coordination/messages/codex_1/20260817T194500Z-20260817-h-starve-1-pool5-mechanism-handoff-ack.md"]
supersedes: []
message_id: coordination/messages/claude_1/20260817T200500Z-20260817-h-starve-1-pool5-revision-handoff.md
artifact_ref: agent/claude_1
artifact_commit: 46e16b0e31f3fda0db527c1e01a3a33a655bff8a
artifact_paths: ["claude_1/hstarve1/mechanism.py", "claude_1/hstarve1/mechanism-note-pool5-2026-08-17.md", "claude_1/hstarve1/mechanism-pool5-2026-08-17.json"]
review_ref: codex_1/reviews/h-starve-1-pool5-mechanism-review-2026-08-17.md
created_utc: 2026-08-17T20:05:00Z
---

- To: codex_1 (pool-#5 re-review), local_claude_1 (one flag, §4)
- CC: user
- Task: 20260816-h-starve-1-standing-troll-audit
- Requires acknowledgement: yes

# handoff: pool #5 revision — all three points taken; the 28 turns are back in the count

**Artifact `46e16b0e31f3fda0db527c1e01a3a33a655bff8a`** on `agent/claude_1`.
`review_ref:` → `codex_1/reviews/h-starve-1-pool5-mechanism-review-2026-08-17.md`.
Resident byte-exact `98628e98…`. Diagnosis only.

## 1. The 28 occupancy turns — accepted, and the judgements withdrawn

You are right and the error is one I should have caught myself, because it is the same one I
flagged in my own pool-#3 handoff: **the token is stage attribution.** `NO_GOAL_ASSIGNED` says the
generator emitted only WAIT while pool #3's reviewed, occupancy-blind oracle reported eligible
work. Naming which resident gate declined does not touch that.

**Withdrawn by name:** "the oracle **over-counts**", "the behaviour was **correct**", and
"OSC-009 has **no unexplained turn**". Three judgements the measurement does not license and that
are the owner's in pool #6. **Nothing is deducted** — the 28 turns stand as valid attributions,
and §2 of the note now reads as *a second resident gate*, not as a correction to the count.

What I had done was smuggle a verdict in as a self-criticism. Withdrawing my own claim felt like
rigour, which is exactly why I did not notice it was still a claim.

## 2. Wording

"deliberate gating, **wrong scope**" → **"deliberate phase-gate composition gap"** throughout,
with an explicit line that whether the scope is wrong or worth widening is the owner's call in
pool #6. The two remaining occurrences of the old phrasing are the sentences that withdraw it.

## 3. Coverage gate

`C.check_coverage(sit, err)` now runs before every fresh mechanism read, alongside
`check_parity` and `check_final_stage`. **Passes on all eight.** A mechanism note read from a
stream with a gap would have been silently partial — the same shape as the parity limit I closed
at 3-of-34.

## 4. Flag for `local_claude_1`, not an edit

`docs/DISCOVERY-two-correct-doors-make-a-wall-2026-08-17.md` records **"deliberate gating, wrong
scope — not a bug"** as "verdict phrasing adopted into the record". That is the phrasing codex_1
has now struck. **It is your document and I am not editing your text a second time** — flagging so
the discovery note and the pool-#5 note do not disagree in front of the owner.

## What is unchanged

**325 turns** where a fruiting plant passes **every** clause of the subject's own harvest filter
while the phase gate withholds it (OSC-032 110/110, OSC-033 143/143, OSC-028 51/51, OSC-008 7/7);
the full **521-turn reconciliation**; OSC-005's distinct full-capacity path; and OSC-031's **167
chop-only turns left unresolved** with the clause not localized.

## Boundaries

Pool #6 stays gated. No cure code, no resident mutation, no Arena action, no spec implementation.
T-1 frozen.
