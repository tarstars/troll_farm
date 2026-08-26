---
schema_version: 2
type: correction
task_id: 20260826-candidate-3-keep-your-goal
from: claude_1
to: ["claude_1", "local_claude_1"]
cc: ["codex_1", "user"]
message_id: coordination/messages/claude_1/20260826T122320Z-20260826-candidate-3-reopened-deferred.md
requires_ack: true
ack_for: ["coordination/messages/claude_1/20260826T115018Z-20260826-queue-drained-deferred.md"]
supersedes: ["coordination/messages/claude_1/20260826T115018Z-20260826-queue-drained-deferred.md"]
created_utc: 2026-08-26T12:23:20Z
---

- To: claude_1 (self-addressed successor queue item), local_claude_1
- CC: codex_1, user
- Task: 20260826-candidate-3-keep-your-goal
- Requires acknowledgement: yes

DEFERRED: **the queue that drained one ritual ago is refilled by the owner's `121330Z`, and it
refills with the items I wrongly closed rather than with new ones.** **Discharges `20260826T115018Z`**
(named in `ack_for`, not only in `supersedes`) — that card said the queue was empty *by closure*;
that premise is gone.

## What I did this ritual, and the whole of it

Acked the policy without dispute (`122010Z`), published a narrow correction retracting my own
`114802Z` close-ack so codex_1 is not acting on my instruction to disregard r6 (`122140Z`), and
executed the one pre-build step the policy names. **No code, no build, no panel, no `narrate6`, no
Candidate 2 stacking, no Arena action, no platform measurement, no lock, no timer.**

**The champion refresh is done and verified, not promised.** `readable/door1-champion.rs` in this
worktree went 2,206 → 2,210 lines and is now byte-identical to `origin/main`: sha256
`ad1ae4eff70a5569e03e2149882bb22510746f4f8592907a5dfb936943ef0bfb`, **the exact hash r5 §0 and r6
anchor every line number against**. All five diff hunks lie inside lines 1–24 (the header block);
no token below line 24 differs. The round-trip gate was re-run rather than cited: the refreshed file
and `cgauto/submissions/candidate-door1-pure-deletion.rs` both compact to
`0da12c33e07a4524a5411a624d0d0da12b2e2f815b176b75df9d6d97c5c3ca01`, exit 0 on both, matching the
value the file's own header declares. Program-preserving **as executed**.

## Deferred, in order, each with the signal that unblocks it

1. **codex_1's one review of r6** — the single live item and the one everything else hangs on.
   Requested at `113736Z` (`requires_ack: true`, artifact `claude_1/cure3/g0-candidate-3-2026-08-26-r6.md`
   at `agent/claude_1@7c1722e6`), **not** republished, because that handoff is valid, addressed to
   him and unacknowledged, and a second copy would split the record. Review surface is r6's four
   blocks C1–C4; the rest is r5 verbatim. **UNBLOCK-SIGNAL:** his ACCEPT, ACCEPT-WITH-EDIT (naming
   the exact one-line mechanical edit) or BLOCK. **On BLOCK the task closes at G-0** — no r7, and I
   will publish the close without arguing it.
2. **The build, on ACCEPT only** — and it is *one* of each, per the policy: build, **one** panel,
   **one** reproduction, the diff on `main`, **one** owner read, stop. Its first act is no longer
   the champion refresh (item done above), so it starts at the rule change itself.
   **UNBLOCK-SIGNAL:** item 1 returning ACCEPT or ACCEPT-WITH-EDIT.
3. **Candidate 3's G-1 row**, unblocked on the instrument side and blocked on mine. Ruling 3 wants
   an evaluable P4b row; codex_1's repair `453c4c89` supplies it and I ACCEPTed it at `114911Z` on
   an old-versus-new differential. The row is instrument-vs-rule-off, both v6. **UNBLOCK-SIGNAL:**
   item 2 — there is nothing to measure until the build exists.
4. **The Candidate 2 re-run stacked on top** — restored from "closed" to postponed, and it is the
   only thing that can falsify r5 §7's "plan-keeping needs no new machinery" via `m061`'s
   `PICK`↔`DROP` two-cycle. Recorded last ritual as *never tested*; that is now **pending**, still
   not supported. **UNBLOCK-SIGNAL:** items 2 and 3 complete.
5. **Review of charter `20260826-deferred-card-lint`** — named, **not chartered** (`110544Z`), so
   the standing manual rule continues and was run again this ritual: fetch immediately before
   composing, and after publishing re-run the sweep and confirm the card appears under
   "unacknowledged, ack required". **UNBLOCK-SIGNAL:** a charter, if one ever comes.
6. **The banana farm** is the owner's stated next item (`113907Z` (c)), assessment to the **owner**
   first, **no charter yet**. I hold no banana-farm work, claim none, open none.
   **UNBLOCK-SIGNAL:** a charter naming me.

## Ruled since the last card — recorded so the reversal is not lost

- **`RW_COUNTER` is ruled, not procedurally closed.** Last card said "closes unruled — not a
  technical verdict for either side." Superseded: `rb=`/`rw=` are **not emitted** and **r6 C1 stands
  unless codex_1 objects in the same review**. The switch stays open exactly as r6 published it
  (recommended `false`); I do not treat the ruling as pre-deciding an objection codex_1 has not yet
  had the chance to make.
- **The r5 BLOCK was mechanical and its substance accepted** — the regex/equation mismatch was mine
  and I repaired it as r6's C2/C3. It does not count against the bound.
- **Three items accepted as refinements of `110544Z`/`110904Z`**: `DONE_ON_HARVEST = true`; the
  `type` gone-cause only where the idle-harvest producer actually filters by kind; the Bank has no
  accepts/fullness predicate in the champion.

## Open questions nobody has ruled on — carried, not closed

- **P4b's v6 arm is exercised only by fixture**, never by a real archive. Last card said this was so
  because the ceiling had closed the only v6 producer; that reason is now void — the producer is
  Candidate 3 and it is live again — so **an ACCEPT would make a real v6 archive reachable for the
  first time**. Not a finding and not work. **UNBLOCK-SIGNAL:** item 2.
- **`format_readable.py`'s header template is wrong for any non-minified parent.** Recorded in
  `docs/readable-format.md`; the generator itself is still **not chartered**. Today's refresh
  consumed `origin/main`'s hand-corrected header and did not fix the generator.
- **The residual walk-back the capacity middle does not close** (producer switch: a unit carrying
  some wood in endgame, or a fruit under `safe_regeneration`, routed to bank candidates only, its
  `Tree` goal not-live-and-preserved, walking back past a better tree). Its measurement rides on the
  panel in item 2. The `nl_producer` field r6 makes required is the observable for it.

## Owned by `local_claude_1` — visible, not claimed

The **23 of 34 fixtures `NOT_REPRODUCIBLE_ON_BASE`** on every arm; the shipping-form question.

## Carried unchanged — none of these were closed today

The 16 parked-unit episodes on 107 of 384 unit lives (277 blind); the non-discriminating absolute
per-troll idle-with-work bar; C-15's −24 own-score points against C-16/P3\*'s +56 margin points,
never summed; 28 of 228 non-eligible views changed; the scoping's two-sided price; the seat-0-only
eligible class; C-8's four silenced-without-progress cases; two windows excluded by G-D; the
unmeasured death direction of A-2; C-13's P-13b poison count not reproducible by construction; no
corpus turn ever granting two exchanges; the tick budget breached on `m078:0` and `m090:0`; and
**nothing measured says the candidate's C-5 = 5 is benign** — that STOP AND ASK stands and is the
owner's.

**No Arena action taken and none proposed.** The champion is on the ladder as submission `41197542`
by the coordinator's hand; nobody else touches the Arena, and I have not.
