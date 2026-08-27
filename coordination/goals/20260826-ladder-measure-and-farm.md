# GOAL — overnight 2026-08-26/27: run the ladder measurement L-1 and push the banana-farm candidate F-2 to the ladder queue; hourly wakes (cron 38e277ae at :13)

You are `local_claude_1`, sole Arena controller. Rules: `coordination/WORKING-RULES.md`. Cards:
`coordination/tasks/20260826-ladder-measure-cured-dancing-troll.md` (L-1, ledger
`local_claude_1/ladder-measure/ledger-2026-08-26.md`) and
`coordination/tasks/20260826-banana-farm-candidate.md` (F-2, design input
`docs/BANANA-FARM-CONTRACT-2026-08-26.md`). The owner is asleep ~20:00Z → ~05:00Z.

## Each wake (hourly, cron; also on any ack-required mail if the session is awake)
1. `cd /home/tarstars/prj/troll_farm-local_claude_1`; `inbox_sweep --fetch`; read every new message whole before publishing anything; mark seen as its own step.
2. **L-1 ledger step:** if the resident was submitted ≥ 2 h ago and its read is not in the table → `python3 cgauto/cg_rank.py`, write the row. Then submit the next bot in the plan (A1 → B1 → B2 → A2 → A3 → B3 → B4 → A4 → A5 → B5 → B6 → A6 → A7 → B7 → B8 → A8) with `api_submit_once.py` and the ledger's sha; write the submission row. After A8's read: resubmit A as the resident; compute mean(A), mean(B), difference, noise band; verdict line + plain-words sheet `local_claude_1/ladder-measure/owner-sheet-2026-08-27.md`.
3. **F-2:** rule on whatever blocks a peer (design round verdicts up to two; a hash confirmation); land artifacts on `main` at each gate; when the panel is reproduced with the validity gates PASSED, book ladder slot 3 in the ledger (submission after A8, not before); if validity FAILS, write the obituary line and put the repair question in the owner's queue — do not submit.
4. Mark stalls; append the five-part board note to `local_claude_1/goal-log-2026-08-26.md`; update board rows in the same commit; fast-forward `main`; pull the checkout `/home/tarstars/prj/troll_farm`.
5. ~02:30Z: check the collector snapshot (`data/raw/snapshots/<latest>/leaderboard.json`, pseudo `tass`) and decode one collected game's diagnostic line (the 328-char payload) — record the result on the board (row 0-3's data gate).

## Allowed without the owner
The reads and the planned submissions of L-1; F-2's slot-3 submission only after A8 and only with validity PASSED; rulings that unblock a peer; stalls; landing artifacts; copies ≤ 10 MB.

## Not allowed
Any other submission; KEEP/REVERT/promotion rulings; new charters or tracks; rule changes; a third design round; transfers > 10 MB; deletions.

## Done when
L-1: 16 reads, A resubmitted, verdict + sheet written. F-2: design accepted, built, panel reproduced, slot 3 booked or the obituary written. Board truthful; `main` == branch == checkout. **Time box:** 2026-08-28T12:00Z; then write the state, resubmit A if B or the farm is up, archive this file, set "no active mission".
