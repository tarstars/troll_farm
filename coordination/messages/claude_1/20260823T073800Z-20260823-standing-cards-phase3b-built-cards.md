---
schema_version: 2
type: update
task_id: 20260820-pair-selector-anti-benching
from: claude_1
to: ["claude_1"]
cc: ["local_claude_1", "codex_1", "user"]
message_id: coordination/messages/claude_1/20260823T073800Z-20260823-standing-cards-phase3b-built-cards.md
requires_ack: true
ack_for: ["coordination/messages/claude_1/20260823T071201Z-20260823-standing-cards-gp-delivered-cards.md"]
supersedes: []
created_utc: 2026-08-23T07:38:00Z
---

- To: myself (the queue items)
- CC: local_claude_1, codex_1, user
- Task: 20260820-pair-selector-anti-benching
- Requires acknowledgement: yes (self-addressed; the cards below are the queue items)

# standing cards — Phase 3b is BUILT and gated at G-a/G-c; the remaining gates split into three

Replaces `20260823T071201Z`, named in `ack_for`.

**Delivered this wake, off the board.** The Phase 3b build, `agent/claude_1@09ed550f`, handed off
at `20260823T073600Z`: G-a + G-c PASS 34/34 on both subjects, 8/8 controls fired, one hunk. That
discharges the r2 design card. Also delivered earlier this wake: the ACK of codex_1's G-P review
(`ACCEPTED_WITH_PLATFORM_CONDITION`), whose platform condition I hold unchanged — G-P is offline
and proves nothing about platform non-interference.

DEFERRED: 20260820-pair-selector-anti-benching, **G-b** — Δ-B inertness by same-state fork.
BLOCKED on a ruling, and the reason is a measurement, not a preference: **Δ-B fires zero times on
34 fixtures × 2 subjects**, so §5's "every naturally reached Δ-B state" is an empty set and the
fork as designed would return green over nothing. Counting Δ-B is not measuring its inertness, and
I will not report it as such.
UNBLOCK-SIGNAL: a written codex_1/`local_claude_1` ruling on how G-b is run over a non-empty state
set — panel-width naturally reached states, or explicitly synthesised states declared as such —
with a G-b over zero states recorded UNMEASURED rather than PASS.

DEFERRED: 20260820-pair-selector-anti-benching, **G-d** — panel with named costs, every changed
game named. Ordered after G-b: pricing a change whose Δ-B is unmeasured prices the wrong object.
Conditions travelling with it and not renegotiable by me: no fixture-only result promotes this, the
blast radius is 20 of 34 fixtures with every first selected tick at turn 100 (the replant block's
own guard), progress is not claimed, and it is never reported as addressing OSC-004/017/034 or
OSC-032/033 — including the two of those whose streams it changes.
UNBLOCK-SIGNAL: G-b measured and ruled.

DEFERRED: 20260820-pair-selector-anti-benching, **G-e** — the two-clause bar of
`20260822-alpha-progress-regrade`: healed **with progress**, never merely detector-silent, graded
by the re-grade instrument at `79dfdd63`. Ordered after G-d.
UNBLOCK-SIGNAL: G-d delivered.

DEFERRED: 20260821-corpus-prevalence (b) — the prevalence measurement, deliverables 2–4. BLOCKED,
unchanged and untouched by this wake.
UNBLOCK-SIGNAL: `data/processed/games.jsonl` readable from my host with sha256
`a882e52787fa474cba4cdbe6b08a20d5e3925fe8d743bc201da8f816eb1e4e14`, OR a written owner/coordinator
instruction placing the execution on `project_host`, OR a written ruling re-titling the card onto
`6536563`.

DEFERRED: 20260821-swap-r1-cure — the G-2-verdict → G-3 → G-4 chain. Unchanged. The NARRATE
instrument built from swap R-1's source is a measuring instrument, not a candidate, and codex_1's
G-P review says in terms that it grades swap R-1 as nothing.
UNBLOCK-SIGNAL: a written `local_claude_1`/owner ruling on the residual 13 and on the cure-arm
basket criterion.

## Not mine, and not to be discharged by me

`local_claude_1`'s AAAAA submission block named "G-P delivered **and** reviewed" as its unblock
signal, and codex_1's review at `20260823T072259Z` satisfies that signal — but the card is
`local_claude_1`'s and only `local_claude_1` discharges it. I start no Arena run and I have taken
no Arena action.

cross-task: this message carries cards for four tasks and is filed under
`20260820-pair-selector-anti-benching`; `ack_for` names its predecessor under
`20260823-narrate-real-game-telemetry`. My standing cards travel as ONE self-addressed message
spanning every open task, so a replacement must cross the task boundary or the predecessor's cards
sit discharged by nothing.
