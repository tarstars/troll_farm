# HANDOVER 2026-08-21 — four owner rulings executed; the investigation is one sitting from closed

Entry: this file → `coordination/ITERATION.md` (the 08-21 board entries) → task
records. Ritual unchanged: `python3 scripts/inbox_sweep.py --me local_claude_1
--fetch` → read ALL new → `--mark` as its own step. Ack obligation = `to`
recipients only; cards are discharged only by delivery or a DEFERRED
replacement. Supersedes `coordination/HANDOVER-2026-08-20-automation-era.md`,
which is still the reference for how the automation works.

## The state in five lines

1. **The system still runs itself and graded its own night.** night_runner
   closed session 2 at 00:53Z (pairs `[1.9, −0.6, 0.4, 1.1, −1.7]`, mean
   **+0.220** = IMMATERIAL below the 1.0 floor, empirical pair SD 1.413), took
   the owner-approved branch unattended, opened **session 3** and published the
   OWNER MORNING SHEET at 00:54Z with no human in the loop
   (`coordination/messages/local_claude_1/20260821T005401Z-...-progress.md`).
2. **Session 3 is LIVE and is the next owner moment.** Door-1 challenger vs the
   VERY-OLD resident `98628e98…` — the gold standard for the composed +1.240,
   measured directly instead of chained across nights. Ledger
   `local_claude_1/door1-vs-old-2026-08-20.md`, state
   `…-state.json`. Progress at flush: **pair 1 = 0.0** (A1 23.7 @26, B1 23.7
   @26), A2 submitted 04:49:00Z. Standard 5-pair block, same pre-registered
   arithmetic (σ_pair 1.5, bar 1.315, floor 1.0), the nine named costs travel
   with the verdict, KEEP/REVERT is the owner's.
3. **FOUR owner rulings landed this morning, all executed and published**
   (`81acd945`): **KEEP** the Door-1 challenger — `547fa706…` is the **champion
   of record**, cure-C `ad3bfefe…` retired, and the anti-benching task's subject
   rebased to the door-1 base by its own charter clause; **D3 = HOLD**, no Arena
   slot for the P1+P2 benching candidate, because its pre-emption condition was
   "gates green" and codex_1's unified review (claude_1 concurring) is
   `PACKAGE_REPRODUCED; BOTH CANDIDATES BLOCKED AS QUALIFIED CURES`; **4b: all
   six harmless stamps HELD**; **OSC-032/033 CHARTERED as a look**. Ruling
   message: `…/20260821T044224Z-20260819-osc031-forecast-fix-door1b-policy.md`.
4. **The oscillation investigation is one short sitting from closed.** All 34
   cases are re-graded against the CHAMPION in
   `local_claude_1/session-inputs/4b-sitting-package-2026-08-21.md`: 8 FIXED, 18
   already ruled BUG under R-2 with the cure on the shelf, **6 held stamp
   candidates**, 2 chartered. The six are re-offered as a **look-and-rule sheet
   with viewer links** (`claude_1/viewer/out/<CASE>.html`) in 4a's shape — the
   owner declined to stamp games they had not watched, which is their standing
   top-down rule and my miss, not a change of mind.
5. **Two measured facts to carry forward.** On the frozen 34 the kept champion
   beats cure C **8 FIXED to 3 with no case lost** (OSC-003/006/014/020/034
   gained) — the Arena called the same step immaterial; different questions,
   both honest. And **OSC-031 is still NOT FIXED on the champion**: its chop
   defect was cured, what still fires there is the benching.

## Open cards and who holds them

| party | owes |
|---|---|
| VM services | session 3's marks and its block verdict; the tree/sheet machinery is unchanged |
| claude_1 | **NEW CARD:** `coordination/tasks/20260821-osc032-033-no-goal-instrument.md` (ack by delivery or DEFERRED). Also: sentinel build, now **unblocked** |
| codex_1 | instrument-first review of the OSC-032/033 probe application, before any result is a finding |
| local_claude_1 next session | read session 3's verdict with the owner; run the 4b look-and-rule sitting when they want it |
| OWNER | session 3 KEEP/REVERT when the block completes; the 4b sitting (6 cases, viewer); the open extend-vs-replace design question; coordd date 08-31 |

## Rulings I made as coordinator (not the owner's, do not re-litigate)

- **`actionable_set()` MAY be extracted into `scripts/inbox_sweep.py`** as a
  behaviour-preserving refactor `main()` itself calls, landing as its own
  reviewed change before the sentinel, with a test pinning `main()` and the
  function to one answer. This unblocked claude_1's card, blocked since 08-19.
  Reason, generalized: one predicate, one code path — a sentinel that disagrees
  with the sweep is worse than no sentinel (two-doors-wall family).
- **codex_1's P3 ruling upheld:** the locked panel configuration makes
  candidate-equals-parent an absolute invariant, so an intentional selector edit
  does not make it inapplicable. Door-1 carries a named absolute regression
  unless the owner changes the rule.

## Still open, nobody may build against it

The owner's **extend-versus-replace** design question from Phase 3: may the
`idle_regeneration` fallback extend `out` instead of replacing it? Scope is
**101 of OSC-013's 170 idle turns and none of OSC-004/017/034**; a change
justified by the 101 must never be reported as addressing the rest.

## Housekeeping done this session

VM disk **95% → 66%** (1.0 G → 6.5 G free): 7.1 G of abandoned agent scratch in
`/tmp` reaped under an age filter, an `lsof` check, and a preserved bundle of
five worktrees' unpushed 08-02 commits
(`~/preserved/tmp-scratch-lfs-probe-2026-08-21.bundle`, verify: complete).
Worktrees pruned. It will refill; **no reaper is chartered and nobody owns one.**

Parked, no cost: sentinel+latch, viewer readability card, two-doors-wall
brainstorm, Specs A/B implementation (separately gated).
