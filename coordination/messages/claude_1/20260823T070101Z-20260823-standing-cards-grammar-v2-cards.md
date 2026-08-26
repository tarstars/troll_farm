---
schema_version: 2
type: update
task_id: 20260823-narrate-real-game-telemetry
from: claude_1
to: ["claude_1"]
cc: ["local_claude_1", "codex_1", "user"]
message_id: coordination/messages/claude_1/20260823T070101Z-20260823-standing-cards-grammar-v2-cards.md
requires_ack: true
ack_for: ["coordination/messages/claude_1/20260823T065801Z-20260823-standing-cards-narrate-cards.md"]
supersedes: []
created_utc: 2026-08-23T07:01:01Z
---

- To: myself (the queue items)
- CC: local_claude_1, codex_1, user
- Task: 20260823-narrate-real-game-telemetry
- Requires acknowledgement: yes (self-addressed; the cards below are the queue items)

# standing cards — one of the NARRATE build's two signals has landed; four cards

Replaces `20260823T065801Z`, named in `ack_for` (`supersedes` is inert for discharge). Re-issued
inside the hour, and the reason is a signal change, not a re-think: the length figure arrived.

DEFERRED: 20260823-narrate-real-game-telemetry — the intention-logging instrument on swap R-1, and
gate G-P. Front of the queue, owner-directed. Grammar **v2** (readable, built to the measured
2,000-character budget) delivered at `agent/claude_1@c300e6466ab77a9d55a21f2f2654e7ac61ef81e8` via
handoff `20260823T070100Z`; it replaces the `N1` compressed grammar, which was never emitted
anywhere. No instrument file exists and `candidate-swap-r1.rs` is untouched.
UNBLOCK-SIGNAL: **codex_1's written pre-build construction ruling on the v2 grammar and the
emission point — now the only outstanding signal.** `local_claude_1`'s length figure landed at
`20260823T065700Z` (2,000 characters byte-exact on 250 of 250 turns, no boundary reached, the
two-`MSG` question withdrawn) and is satisfied.

DEFERRED: 20260820-pair-selector-anti-benching — the Phase 3b build. Unblocked, queued behind
NARRATE. codex_1's r2 design ruling (`75085260b026750201061760804257f422c88a6b`) and the
coordinator's build authorization `20260823T063300Z` have both landed and the adapter it was
ordered behind is delivered. Nothing is pre-built.
UNBLOCK-SIGNAL: none — unblocked, queued. Conditions travelling with the build: no fixture-only
result promotes it, scope stays the 101 turns of the one game, progress is not claimed, never
reported as addressing OSC-004/017/034 or 032/033.

DEFERRED: 20260821-corpus-prevalence (b) — the prevalence measurement, deliverables 2–4. BLOCKED,
unchanged. The adapter is delivered and is no longer part of this wait; the card's question is
still unanswerable here because `6561795` appears in none of the 290 in-repo games, and I have not
re-titled it onto the older `6536563`.
UNBLOCK-SIGNAL: `data/processed/games.jsonl` readable from my host with sha256
`a882e52787fa474cba4cdbe6b08a20d5e3925fe8d743bc201da8f816eb1e4e14`, OR a written owner/coordinator
instruction placing the execution on `project_host`, OR a written ruling re-titling the card onto
`6536563`.

DEFERRED: 20260821-swap-r1-cure — the G-2-verdict → G-3 → G-4 chain. Unchanged. The instrument
about to be built from its source is a measuring instrument, not a candidate, and grades nothing
here.
UNBLOCK-SIGNAL: a written `local_claude_1`/owner ruling on the residual 13 and on the cure-arm
basket criterion.

## Note to myself on re-issue discipline

The wake-set rule says do not re-issue an unchanged card just because I woke. This re-issue is
inside the hour and it is legitimate under the same rule: the NARRATE card's UNBLOCK-SIGNAL
genuinely changed — one of two required signals was satisfied by a named published message. The
other three cards ride along because all four travel in one message; none of them changed.

cross-task: `ack_for` names a card message of `20260821-corpus-prevalence` lineage under this
message's task `20260823-narrate-real-game-telemetry`. My standing cards travel as ONE
self-addressed message spanning every open task, so a replacement must cross the task boundary or
the predecessor's cards sit discharged by nothing.
