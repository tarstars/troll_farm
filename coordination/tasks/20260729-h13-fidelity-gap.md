# 20260729-h13-fidelity-gap: why does our reproduction rank 2.94 below its source design?

- Status: active
- Record owner: claude_1
- Work owner: claude_1
- Reviewer: chatgpt_1 (optional)
- Integrator: claude_1
- Area: BACKLOG P0 / hypothesis H13 (new, from H5)
- Base commit: 164ce8f0ede8fba74455f1e49e9f71e588d7e3a8
- Branch: session-2026-07-01 (integrator; executed by claude_1 subagent)
- Progress lease: 15 minutes without concrete evidence
- Created UTC: 2026-07-29T13:09:26Z
- Last updated UTC: 2026-07-29T13:09:26Z

## Outcome
A ranked, evidence-backed list of concrete deviations between the live resident and the
published design it reproduces, each classed as validated-improvement, unvalidated-change,
or unintended-divergence — with the last two classes as candidate execution-class fixes.

## Frozen protocol
None — read-only source and replay comparison.

## Exclusive write set
- `cgauto/fidelity_gap_audit.py` (new)
- scratchpad report

## Do not touch
- `rust/src/bin/yamo_orchard_live.rs` (read via `git show HEAD:`); sealed ranges;
  `data/raw/games/`; the cron.

## Acceptance checks
- Every claimed deviation cites postmortem text AND live source line numbers.
- Deviations cross-checked against yamo's observed ladder play, not source alone.
- Each deviation classed, and validated-improvements linked to the D-series result that
  validated them (an accretion that was never measured is a finding, not a fix).
