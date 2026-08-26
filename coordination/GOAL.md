# GOAL — run the ladder measurement L-1 (cured dancing troll vs champion), 2026-08-26 evening → ~08-28

You are `local_claude_1`, sole Arena controller. Rules: `coordination/WORKING-RULES.md`; card:
`coordination/tasks/20260826-ladder-measure-cured-dancing-troll.md`; ledger:
`local_claude_1/ladder-measure/ledger-2026-08-26.md` (the plan and the read table live there).

## Cadence
- Wake **every 2 hours** (`sleep 595` × 12 between wakes, foreground). Each wake: `cd` into the
  worktree; `inbox_sweep --fetch`; read all new mail whole; then the ledger step below; board note
  (Moved / Stalled / Ladder / Decisions / Corrections) appended to `local_claude_1/goal-log-2026-08-26.md`;
  `main` fast-forwarded; the checkout pulled.

## The ledger step (every wake)
1. If the current resident was submitted ≥ 2 h ago and its read is not yet in the table:
   `python3 cgauto/cg_rank.py`, write the row (bot, submitted, ids, read time, score, rank).
2. Then submit the next bot in the plan with `api_submit_once.py` and the sha from the ledger;
   write its row's submission part. **Bot B may be submitted only after codex_1's byte-identity
   check is published** (ack-required); until then, keep reading A and do not submit.
3. After the 16th read: resubmit **A** as the resident; compute mean(A), mean(B), the difference
   and the noise band; write the verdict line in the ledger and a plain-words sheet
   `local_claude_1/ladder-measure/owner-sheet-2026-08-2x.md`; then stop (done).

## Allowed without the owner
Reads and the planned submissions only; rulings that unblock a peer on L-1 or on the fixture
generator (0-3); marking stalls; landing artifacts on `main`. Ladder snapshot check at ~02:30Z
(payload decode of one collected game — record the result on the board; it is 0-3's gate).

## Not allowed
Any submission outside the plan; any KEEP/REVERT/promotion ruling; new charters; rule changes;
transfers > 10 MB; deletions.

## Done when
16 reads in the ledger, A resubmitted, verdict line + owner sheet written, board row L-1 closed,
`main` == branch == checkout. **Time box:** 2026-08-28T12:00Z — then write what is and is not
done, resubmit A if B is up, archive this file under `coordination/goals/`, set "no active mission".
