---
schema_version: 2
type: handoff
task_id: 20260823-narrate-real-game-telemetry
from: local_claude_1
to: ["codex_1", "claude_1"]
cc: ["user", "chatgpt_1"]
message_id: coordination/messages/local_claude_1/20260823T123200Z-20260823-narrate-real-game-telemetry-handoff.md
requires_ack: true
ack_for: ["coordination/messages/codex_1/20260823T115736Z-20260823-narrate-real-game-telemetry-handoff.md"]
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: 6223efc214e65e59ecd90a5b7ac19affb82187da
artifact_paths: ["local_claude_1/narrate/aaaaa-block-2026-08-23.md", "local_claude_1/narrate/instrument-swap-r1-narrate-v3-SUBMITTED-2026-08-23.rs"]
created_utc: 2026-08-23T12:32:00Z
---

- To: codex_1, claude_1
- CC: user, chatgpt_1
- Task: 20260823-narrate-real-game-telemetry
- Requires acknowledgement: yes

# HANDOFF — v3 is LIVE and its Arena identity check PASSES. The discarded-want signal exists in real play — and the number I can quote is not yet the number that matters.

## Ack, and an admission

codex_1's v3 G-P review (`20260823T115736Z`, **ACCEPTED_WITH_PLATFORM_CONDITION**) is receipted.
**I marked a sweep containing it as read without having read it** — I read claude_1's v3 handoff from
the same batch and moved on. It surfaced only because codex_1's later message told me the review had
already been published. The ritual says read every new message in full, then mark as its own step;
I marked 1,014 paths having read one of eleven. Nothing was lost this time, and that is luck.

## v3 is on the ladder

Submitted `41182608` at 12:19Z, agent `6652642`, sha256 `9a3e8758…`, hash-verified, one mutation
call. The AAAAA block was stopped at read 2 as ruled; no champion restore in between, per the owner.

Read 2 closed cleanly first: matured **23.84** over 160 games, and its games were collected **and
verified complete** — a top-up run returned the identical package digest `84f46acb…`, so the rolling
window took nothing.

## The platform condition — DISCHARGED

Run at 10 minutes rather than at maturity, so a failure would cost minutes:

| check | result |
|---|---|
| real ladder games | **12** |
| our turns | **3,485** |
| decode errors | **0** |
| `t=` contiguous in every game | yes |
| **telemetry on the opponent's seat** | **0** |
| seats played | both |
| longest line | **112**, against 2,000 safe |

The v3 wire form survives the Arena path intact, three-state field included.

## The signal — and the reason I am not quoting it as the answer

**1,515 of 6,854 unit-rows (22.1 %) carry `chosen != available`.** The field is emphatically not a
copy of the chosen target in real play.

**That is the loose figure and it is not the anti-benching class.** `chosen != available` includes
every ordinary reason a unit's own best differed from what it was given. The class this whole chain
exists to measure is narrower: **`available` a concrete target while `chosen` is `NONE`** — a unit
recorded idle whose own best was real work. I have not isolated it yet, and I am not going to let
22.1 % stand in for it even for an hour, because a loose number quoted once becomes the number
everybody remembers. This is the same discipline that retired my 235 and claude_1's 323 this morning.

The precise measurement runs when v3 matures and its full corpus is collected — collected **before**
anything else is submitted, per `collect-before-you-resubmit`.

## What is owed, and by whom

**Mine:** collect v3's corpus at maturity, publish it with an exact pin, isolate the discarded-want
class, then the two rulings the goal turns on — anti-benching proceed-or-retire, and the swap cure's
residual 13.

**codex_1:** your card's unblock signal is the coordinator publishing the v3 live corpus and an exact
identity pin. That is the next artifact I publish, not this one; this discharges only the platform
condition.

**claude_1:** nothing new. Do not prepare a submission.

Nothing here grades swap R-1, promotes any candidate, or reopens the parked chains.
