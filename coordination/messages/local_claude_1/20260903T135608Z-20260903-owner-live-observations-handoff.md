---
schema_version: 2
type: handoff
task_id: 20260903-owner-live-observations
from: local_claude_1
to: ["claude_1"]
cc: ["user"]
message_id: coordination/messages/local_claude_1/20260903T135608Z-20260903-owner-live-observations-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: e7a78476f5eaee701cc877ceb6099a74f0789df0
artifact_paths: ["coordination/tasks/20260903-owner-live-observations.md", "coordination/BOARD.md"]
created_utc: 2026-09-03T13:56:08Z
---

- To: claude_1
- CC: user
- Task: 20260903-owner-live-observations (new card, born from the owner's own watching)
- Requires acknowledgement: yes. Two things are owed: **first** your stage-2A handoff, **then** this read.
  Acknowledge with your start time and an estimate for each.

# HANDOFF — the owner watched the live games and named three things; measure them. Plus: your stage-2A handoff is owed

## First, and quickly: your stage-2A handoff

Your four field runs finished at 13:08:13Z (`ALL-DONE`) and I have already read them. Do not re-run anything. What is
owed is the paperwork: the report's last section and the handoff pinning a commit that holds the four run JSONs and
your `field.json`. For your information, so we are working from the same numbers — I ran the same four pairings myself
from a fresh archive of your pinned commit, and **our two runs agree to the digit**: 29 / 174 / 35 / 322 wins of 400
against the champion of record, orchard 6, the old champion with denial on and the network clone, with identical
scores. My aggregation reads **FIELD Δwin −0.2219 [−0.2562, −0.1862], Δmargin −28.71 [−32.74, −24.85], verdict
`FIELD_BELOW_ZERO`**, and the only opponent you hold is the network clone (−0.0225, interval straddling zero). Report
your own aggregation as you measured it; if it differs from mine anywhere, say so plainly and we find out why.

**Two things you should know before you write it up.** (1) I corrected my own arithmetic on the third troll: the
"17–18 turns earlier" figure compared your 70.5 against orchard 6's 88.5, which comes from a different population.
Paired map for map on the identical 24-map slice against the identical resident, it is **14.0 turns at the median**
(mean 15.5, earlier on 19 maps of 24, later on 5 — once by 39). Use the paired figure. (2) **The owner put the build on
the ladder** at 13:10:07Z as submission `41236483`, against my stated advice, and it is playing now; at 40 minutes it
reads 14.90 where the champion read 18.14. So stage 2A is **not** closed and you should not write it up as dead — record
the field reading as the fact it is and leave the verdict to the owner and me.

## Second, the new read — the card at the pin carries it whole

The owner's words, watching `41236483` play:

> "I can see that trolls switches a lot and waste time on switches. Also endgame misses chopping tree left and
> chopping down plants which were planted by enemy"

Three claims, measured separately, **on real games and not on examples**. Both populations are already collected, so
this costs no new play: the champion of record's 160 ladder games (`local_claude_1/ladder-queue/games-41234663/`) as
the control, and the dispatcher's 160 from the hour now running (`games-41236483/`, collected about 14:12Z).
`local_claude_1/apple-farm/ladder_read.py` is the decoding pattern; your own `claude_1/endgame-gap/` and
`endgame_sig.py` are the nearest instruments.

1. **Switching** — per troll per turn, how often the target changes *while the previous target is still valid and
   reachable*, the turns actually lost to it, split by phase: turns 1 to the third troll (your dispatcher's window in
   the new bot) and after it (the champion's own play). **The phase split is the point of this one.** You fixed a
   two-cell dance during the build with a 5 % hold and position-free references, and the owner is reporting switching
   in the games of the build that contains that fix — so either the fix is incomplete or what the owner sees is the
   champion's ancient thrash, not yours. Say which. The champion's own 160 games decide whether this is new or old.
2. **Trees left standing** — at the final turn, how many trees stand, with size, health and distance from our shack;
   then, doing the same arithmetic `chop_candidates` does, how many **could** have been felled and banked in time
   against how many were ruled out by the carry-home test, splitting the ruled-out group by cause: too far to return,
   hands full, chop unfinishable, unreachable.
3. **Enemy-planted trees** — reconstruct provenance from the recorded turns (a plant appearing on a cell with an
   opponent troll adjacent the turn before), then report how many the opponent plants a game, how many we fell, how
   many still stand at the end, and the fruit the opponent took from the ones we left. **State how reliable that
   inference is and how many plants it cannot attribute** — I will not accept a provenance number without its error rate.

## What I already established from the source, so you do not spend the time — and what it does NOT settle

- **The protocol carries no planter.** The `Plant` record the referee sends is `kind`, `cell`, `size`, `health`,
  `fruits`, `cooldown`. There is no owner field. So observation 3 is not a missing filter; it is bookkeeping the bot
  does not keep. Cost that inference honestly before anyone proposes a rule that leans on it.
- **One rule plausibly explains both endgame observations.** In `chop_candidates`, a tree is skipped unless the troll
  can reach it, fell it and **carry the wood home before the last turn**
  (`if turns > TOTAL_TURNS - view.turn + 1 { continue; }`), and `free_capacity() <= 0` excludes a full-handed troll
  before the loop starts. That is right if wood only scores from inside the shack, and it means the candidate list
  empties late with trees still standing — which is what the owner saw, and which reconciles his eyes with your own
  Track E read (a fifth of late troll-turns with no command, 84 % of them terminal waits with "nothing reachable").
  **Both are correct.** So the live question is what an *unbanked* cut is worth as denial — a felled tree is one the
  opponent cannot harvest or fell either. That has never been measured. Treat my two mechanisms as leads to confirm or
  refute, not as findings.

**Bounds.** This card is a read: no build, no ladder, no platform action, no design. If the measurement says a rule
change could recover points, say so with a size and stop — the design round needs the owner's word. Dead condition on
the card: an observation whose cost is below the field panel's resolution (about ±5 points a game) is recorded as
seen-and-small and nothing follows. Budget two days, to 2026-09-05 14:00Z.

**And the operating lesson from this morning, restated because it cost us 103 minutes:** send the progress message
with the commit, not after the last gate, and never launch a long run and then wait on a notification you have not
proved will arrive — if you background work, detach it (`setsid nohup … < /dev/null`) and write to a log you can read
back on the next wake.

— coordinator
