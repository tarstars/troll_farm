# GOAL — keep the board moving (2026-08-26, owner "goal"); hourly wakes, rulings only, one pre-authorized Arena action

You are `local_claude_1`: coordinator, integrator, sole Arena controller. Work this goal **one wake
at a time**, under `coordination/WORKING-RULES.md` (read it first; §8–9 are your job description).
The board `coordination/BOARD.md` is the record; this file is the leash.

## Cadence

- **One wake per hour** (`sleep 3600` foreground between wakes), plus one wake at **~02:30Z** for
  the collector's ladder snapshot (`data/raw/snapshots/<latest>/leaderboard.json`, pseudo `tass`).
- A wake that finds **no new mail and no stall ends in one line** in the log. Do not invent work.
- Every wake: `cd /home/tarstars/prj/troll_farm-local_claude_1 && python3 scripts/inbox_sweep.py
  --me local_claude_1 --fetch`; **read every new message whole before publishing anything**; mark
  seen as its own step; end the wake with the five-part board note (Moved / Stalled / Ladder /
  Decisions for the owner / Corrections) appended to `local_claude_1/goal-log-2026-08-26.md` and
  the board rows updated in the same commit; `main` fast-forwarded and the checkout
  `/home/tarstars/prj/troll_farm` pulled (`--ff-only`).

## Allowed without the owner

1. Rule on items that **block a peer**: gate verdicts that need the coordinator's accept/kill after
   the one allowed round; a hash or reproduction confirmation; a "which of two files" question.
2. **Submit the champion + v6 instrument (row 0-3a) as the ladder resident when codex_1 accepts its
   parity gate** — pre-authorized by the owner ("the instrument replaces the champion"):
   `python3 cgauto/api_submit_once.py <file> --expected-sha256 <sha>` from the file on `main`; log
   the submission id on the board's ladder queue; nothing else on the Arena.
3. Mark **STALLED** any row with no evidence for two days or over budget; write the kill-or-extend
   line into the Decisions-for-the-owner section of the board note.
4. Land finished artifacts on `main` at their gate (diffs, packets, verdicts); write graveyard
   paragraphs for tasks that close.
5. **Row 0-2 (integrate the peer branches)** once D-3 closes: per its card — `main` wins on shared
   files, peers' own trees verbatim, quarantine re-verified by hand, ack-required notice to rebase.
6. Copy files to the VM only if ≤ 10 MB (larger transfers need the owner's Wi-Fi word).

## Not allowed without the owner

New charters or tracks; any Arena action other than item 2 (Candidate 3b's ladder block needs the
owner's word on its panel verdict); changing a rule in WORKING-RULES; spending a second review
round; re-tuning or reopening a closed candidate; transfers > 10 MB; deleting anything.

## Done when ALL of these hold (then write the state and stop)

- T-1 delivered and reviewed (the six remaining tables, the wood-farm question answered).
- 0-3a on the ladder (submission id logged) — or dead with its reason.
- Candidate 3b (D-4): panel verdict written, pass or fail; on a pass the ladder-slot question is in
  the owner's queue, not acted on.
- D-3 closed (accept or not-reproducible).
- 0-2 merged, quarantine clean, peers told to rebase.
- Board truthful; `origin/main` == `agent/local_claude_1` == the checkout; goal log complete.

**Time box:** 2026-08-27T23:00Z. Then write what is and is not done in the goal log, archive this
file under `coordination/goals/`, set GOAL.md to "no active mission", and stop.
