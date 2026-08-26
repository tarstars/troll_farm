---
schema_version: 2
type: update
task_id: 20260826-candidate-3-keep-your-goal
from: claude_1
to: ["claude_1"]
cc: ["codex_1", "local_claude_1", "user"]
message_id: coordination/messages/claude_1/20260826T133600Z-20260826-candidate-3-post-reproduction-deferred.md
requires_ack: false
ack_for: ["coordination/messages/claude_1/20260826T122620Z-20260826-candidate-3-build-authorised-deferred.md"]
supersedes: ["coordination/messages/claude_1/20260826T132600Z-20260826-candidate-3-g1-deferred.md"]
created_utc: 2026-08-26T13:36:00Z
---

- To: claude_1 (self)
- CC: codex_1, local_claude_1, user
- Task: 20260826-candidate-3-keep-your-goal
- Requires acknowledgement: no — a replacement card, not a request

# DEFERRED — D-1 is done except for one ruling and one owner read

## First, the transport defect this card exists to fix

My `122620Z` card was still sitting in my own sweep under **"unacknowledged, ack required"** this
ritual. My `132600Z` card named it in `supersedes` **only**. **`supersedes` is inert; only `ack_for`
discharges** — the rule I have already been bitten by twice (`20260807T113000Z`, `20260812T074913Z`,
both quarantined for the neighbouring defect). This card names `122620Z` in **`ack_for`**, which is
the thing that actually clears it, and supersedes `132600Z` as the card it replaces.

I did not catch this by reading my own template. I caught it because the sweep printed it. The
standing manual rule (item 4 below) is the only reason it surfaced, and it surfaced **late**.

## What is now finished

- **The build, the panel, the diff, the reproduction.** All four. codex_1's independent run from a
  fresh archive of `d34429cc` matches mine in every leaf but wall-clock duration (`132717Z`, acked
  by me at `133400Z`). Panel budget **spent**; reproduction budget **spent**.
- **The verdict, measured twice:** the rule works and **is too strong**. `ka=171` vs the
  pre-registered 30; **−65 own-score points**; blocking 52 → 40; D-1 27 → 23. **DO NOT ADVANCE.**
  No margin is tuned back in, there is no r7, and no ladder slot is booked.
- **Candidate 2's stacked re-run — CLOSED as not-triggered.** Its trigger was an own-score *gain*.
  The measurement is −65. It is not pending; it did not fire. I am not carrying it forward as if
  the question were still open.

## Deferred, each with the signal that unblocks it

1. **The coordinator's §9.10 ruling on D-1.** Everything the ruling needs is published. Nothing on
   my side blocks it. **UNBLOCK-SIGNAL: none from me — it is the coordinator's to write.**
2. **The owner's read of `readable/diffs/candidate-3-keep-your-goal.diff`** — the last budgeted item
   on the row. **UNBLOCK-SIGNAL: the owner.**
3. **P4b integration (`20260826-p4b-pipeline-integration`).** The accepted v4/v5/v6 decoder does not
   expose `evaluate_rows`; my `claude_1/pipeline/p4b_gate.py` does, and callers use it. Destination
   is **already my write set — no transfer is needed if I own it**, and I volunteer. What is missing
   is a **charter**, because D-1 is bounded and must not grow. **It gates no D-1 decision**: the
   candidate fails on its own numbers, so an evaluable P4b row would be a checklist item on an
   already-failed candidate. **UNBLOCK-SIGNAL: a coordinator charter naming the owner, the
   compatibility contract, and a fresh differential gate.**
4. **Charter `20260826-deferred-card-lint`** — still **named, not chartered**. The manual rule stays
   and is what caught the defect at the top of this card. I now run it as three steps, not two:
   fetch before composing; after publishing, re-run the sweep; and **confirm the card I meant to
   discharge is gone from the unacknowledged list** — the third step is new and is exactly the one
   whose absence let `122620Z` survive `132600Z`. **UNBLOCK-SIGNAL: a charter.**
5. **F-2 (banana farm CBF), mine after D-1.** Blocked on T-1 + F-1 + the owner's go, all three
   codex_1's or the owner's. I hold no banana-farm work and open none.
   **UNBLOCK-SIGNAL: T-1's table, F-1's split, and the owner's go.**

## Open and carried — not closed by anything that happened today

- **The spec has no impossibility bound for `Shack` reachability** (codex_1's F4, accepted). A real
  hole in my specification.
- **`rt=0` is unexercised.** F7/F8 add no positive coverage claim and I make none.
- **`format_readable.py`'s header template is wrong for any non-minified parent**; the generator is
  still not chartered and today's work did not fix it.
- **Track 0-1** — 23 of 34 fixtures `NOT_REPRODUCIBLE_ON_BASE`, `local_claude_1`'s and unassigned on
  the board; visible, not claimed.
- **Nothing measured says the candidate's C-5 = 5 is benign.** That STOP AND ASK is still the
  owner's and was not discharged by the build, the panel, or the reproduction.

No Arena action taken and none proposed. The champion is on the ladder as `41197542` by the
coordinator's hand; I have not touched it.
