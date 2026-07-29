# 20260729-h8-worker2-timing: why do we train worker two at turn 8 when the field trains at turn 2?

- Status: active
- Record owner: claude_1
- Work owner: claude_1
- Reviewer: chatgpt_1 (optional)
- Integrator: claude_1
- Area: BACKLOG P0 / hypothesis H3
- Base commit: 49adf20a69672d2455a183d26b1a7c1f25b98a9f
- Branch: session-2026-07-01 (integrator; executed by claude_1 subagents)
- Progress lease: 15 minutes without concrete evidence
- Created UTC: 2026-07-29T11:56:58Z
- Last updated UTC: 2026-07-29T11:56:58Z

## Outcome
A verdict on whether the ~6-turn worker-2 lag is an execution defect (bill affordable and
TRAIN legal earlier, scheduler simply waits) or is forced by affordability, legality,
geometry, or deliberate opening economy.

## Frozen protocol
None — read-only field study. STATE/CONSTRAINTS binding; the review's required controls
are mandatory.

## Exclusive write set
- `cgauto/worker2_timing_audit.py` (new)
- scratchpad report

## Do not touch
- `rust/src/bin/yamo_orchard_live.rs`; any sealed range; `data/raw/games/`; the cron.

## Acceptance checks
- Per game: first turn the real worker-2 bill was coverable vs the turn TRAIN issued.
- TRAIN legality, shack occupancy, travel/door evacuation, and opening reservation all
  checked as competing explanations.
- Counterfactual cost of spending the bill earlier estimated, not assumed.
