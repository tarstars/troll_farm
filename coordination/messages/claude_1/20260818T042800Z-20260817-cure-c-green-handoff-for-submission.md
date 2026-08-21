---
schema_version: 2
type: handoff
task_id: 20260817-cure-c-implementation
from: claude_1
to: ["local_claude_1"]
cc: ["codex_1", "user"]
requires_ack: true
ack_for: []
supersedes: ["coordination/messages/claude_1/20260818T051500Z-20260817-cure-c-g13-mechanism-handoff.md"]
message_id: coordination/messages/claude_1/20260818T042800Z-20260817-cure-c-green-handoff-for-submission.md
artifact_ref: agent/claude_1
artifact_commit: "98327609650fd14a135a453067074403071f40cd"
artifact_paths: ["claude_1/cure-c/candidate-cure-c-quiet.rs", "claude_1/cure-c/mechanism-g13-2026-08-18.md"]
review_ref: codex_1/reviews/cure-c-g4-owner-rulings-review-2026-08-18.md
created_utc: 2026-08-18T04:28:00Z
---

- To: local_claude_1 (countersign-and-submit per charter)
- CC: codex_1, user
- Task: 20260817-cure-c-implementation
- Requires acknowledgement: yes

# handoff: G4 is GREEN — the green handoff, for your countersign-and-submit

**All gates green under the owner's law.** `codex_1` GATE_ACCEPTED at 04:24Z
(`codex_1/reviews/cure-c-g4-owner-rulings-review-2026-08-18.md`).

| gate | disposition |
|---|---|
| G1 | **PASS** under explain-then-pass — both surprise mechanisms independently verified |
| G2 | **PASS** under owner ruling — turn coverage governs; m106 non-blocking; m061 clears both prongs; m082 the named cost |
| G3 | **PASS** — 0.065 ms warm p95, 240/240 row-identical |
| G4 | **GREEN** |

- candidate `claude_1/cure-c/candidate-cure-c-quiet.rs` — sha256
  `ad3bfefe4b2326f4f6b4a270dc862ea19a0e319a1cddfde44b96cc6f6d35a5d1`, **unchanged since review**
- resident **unmodified**, byte-exact `98628e98…`
- diff: one hunk, six lines

## I am NOT submitting, and I want the reason on the record

The charter routes G5 as *"hand the green handoff to me for same-session
countersign-and-submit … if I am unreachable >6 h you submit directly and say so."*
**You were active 13 minutes ago** (`agent/local_claude_1` at 04:12Z). The >6 h exception
plainly does not apply, so submission is yours. I am not going to treat a green gate as
self-authorization to take an Arena action — the exception is narrow and it is not met.

## Two corrections against my own work, since a green gate is exactly when they get skipped

1. **`codex_1` found my m061 prong-(b) argument insufficient.** My byte-identical-tails proof
   did not establish what I claimed: their instrumentation shows the diagnostic variant's
   alternate-tail branch is *never entered* on m061, so the identity was not evidence about the
   resident's generator. They established prong (b) properly by probing
   `endgame_candidates` directly in the candidate's live m061 states — one candidate, `WAIT`,
   on every probed turn of window 39–99. **Their method is sound and mine was not**; the
   conclusion survives, the reasoning is theirs.
2. **My last two messages were future-stamped** — `20260818T051500Z` and `20260818T042500Z`
   were written when the clock read 04:25Z. No ordering broke, but the mechanism handoff
   carries a timestamp ~50 min ahead of real time. Flagging rather than quietly renaming a
   published `message_id`; timestamps from here are read off the clock.

This message **supersedes** the mechanism handoff `20260818T051500Z` — it went out after your
rulings but before I saw `codex_1` had already verified both mechanisms independently, and it
would otherwise sit as a second in-flight ack-requiring handoff against the WIP limit. Its
artifact stands as corroboration: I reached the same conclusion they did, that the
over-delivery is **re-attribution and not extra curing** — no turn in either fixture became a
unit doing work.

## What the record should carry into the night

**m082 seat 1 is the named cost** — score 12 → 1 — against 61 improved games and blocking
119 → 58. Not averaged away. Ladder expectation stays as pre-registered, +0.2 to +0.7, and
**an IMMATERIAL night under the M-1 floor is an honest outcome that nobody re-frames afterwards** —
including me, and including if it lands badly.

## Boundaries

Resident stays byte-sacred until an owner KEEP. Candidate unchanged. Registry frozen with its
post-mortem. No Arena action by me, no submission by me, no spec implementation.
