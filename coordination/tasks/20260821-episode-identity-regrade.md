# 20260821-episode-identity-regrade — a window is a property of the bot that produced it

- Status: **OPEN — coordinator-chartered 2026-08-21 ~10:55Z**, on the accepted finding of
  `20260821-p4-stalls-real-end-regrade` (claude_1 `4502c655`, codex_1 ACCEPTED
  `20260821T100154Z`): the champion's replay reproduces **11 of 34** recorded episodes
  (OSC-001 002 005 012 013 017 021 024 026 027 030); on the other **23** it is a different
  game on the same map/seed/opponent — including OSC-032/033 and **all 8 cases graded
  "FIXED on the champion"**. Nothing in the harness refuses a wrong game (`spec_for` refuses
  only a wrong map), and `sweep34` measures `progress_restored` over the RECORDED window's
  turn bounds on the candidate's run.
- Record owner: local_claude_1 · Work owner: **claude_1** · Reviewer: **codex_1**
  (instrument-first) · Integrator: local_claude_1
- Priority: **immediately after cure α's current G-1 remedy step** — α's G-2 ("005/027/012/001
  → FIXED, none lost") cannot be read without this gate, and the anti-benching Phase 3c has
  the same dependency.
- Base: champion of record `547fa706…` (diagnostic); frozen library
  `oscillation-library-98628e98/library/`; no resident, dev-copy or Arena touch.
- Created UTC: 2026-08-21T10:55:00Z

## Deliverables (measurement and tooling; no fix to any bot)

1. **Episode identity in the shared harness** (`claude_1/t1/fixture_harness.py`): lift the
   two-part gate out of `claude_1/regrade1/real_end_regrade.py` — (a) the window's frozen
   commands against the replay's, (b) the board at the window's first turn against
   `world_state_at_entry` — and make `sweep34`'s grader call it before it reads any recorded
   turn bound. A fixture that fails identity is graded **`NOT_REPRODUCIBLE_ON_BASE`**, never
   FIXED and never NOT_FIXED. Fail-closed: a fixture whose entry state cannot be compared is
   `NOT_REPRODUCIBLE_ON_BASE` too, and said so.
2. **Re-grade the 34 on the champion with identity enforced**, side by side with the current
   `sweep34-door1-base.json`: FIXED / NOT_FIXED / NOT_REPRODUCIBLE_ON_BASE per case, and for
   each verdict that changes, the reason. Expected, to be measured not assumed: the 8 FIXED
   become NOT_REPRODUCIBLE; the NOT_FIXED on the 11 reproduced cases stand.
3. **Real-end annotation** per graded row (the frozen `has_stalled` turn and the grace-only
   bound), as the re-grade card recommended — annotation, not a horizon cut.
4. A short note for the owner: what "FIXED on the champion" meant before and after, and
   what it means for the investigation's tally and for cure gates going forward.

## Gates

- G-1 codex_1 instrument review: the lifted gate is byte-equivalent to the accepted one
  (digest or a pinned test), and the grader's call order is shown (identity before bounds).
- G-2 controls: the gate rejects the champion on OSC-032 (different board, all-WAIT window)
  and accepts the subject bot on all 34; a constructed same-count/wrong-cell board is
  rejected; a fixture with a deliberately corrupted `world_state_at_entry` fails closed.
- G-3 the side-by-side table + the owner note.

## What this does NOT do

No re-ruling: the 18 BUG, the six BUG and the owner's 032/033 disposition are the owner's;
the table annotates, and any proposal to re-open goes to the owner as a question. No change
to any candidate. No new library — whether to **re-freeze the library on the champion** is
an owner decision raised separately.
