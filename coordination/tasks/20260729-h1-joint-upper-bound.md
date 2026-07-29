# 20260729-h1-joint-upper-bound: would the full economy package have paid, even at best?

- Status: closed — verdict (C) immaterial/negative; H1 dead as a resident patch; constrains H2; integrated
- Record owner: claude_1
- Work owner: claude_1
- Reviewer: chatgpt_1 (optional; this audit was their prescription)
- Integrator: claude_1
- Area: BACKLOG P1 / hypothesis H1 (read-only step only)
- Base commit: 8f83bcfcd431e1490270b6ade6bd833af7d2df92
- Branch: session-2026-07-01 (integrator; executed by claude_1 subagent)
- Progress lease: 15 minutes without concrete evidence
- Created UTC: 2026-07-29T12:33:46Z
- Last updated UTC: 2026-07-29T13:14:53Z

## Outcome
A NET upper bound, computed on real game states, on what the joint economy package
(harvest-capable trained units + no can_train cap + bounded early planting + banking
support) could have been worth — gross production minus honestly-priced displacement —
and therefore whether the H2 programme has a target worth its cost.

## Frozen protocol
None — read-only accounting on existing states. The four-lever resident implementation is
REJECTED (CONSTRAINTS (h)); this audit is its sanctioned replacement.

## Exclusive write set
- `cgauto/joint_economy_upper_bound.py` (new)
- scratchpad report

## Do not touch
- `rust/src/bin/yamo_orchard_live.rs`; sealed ranges; `data/raw/games/`; the cron.
- No simulation of a modified bot — that would be the rejected implementation.

## Acceptance checks
- Real bills read from revealed TRAIN commands (not synthetic specs) per H8's method.
- TRAIN legality uses the POST-move occupancy convention (H8 correction).
- Displacement priced from measured evidence, with D175a (−26.44; Δown −5.41, Δopponent
  +21.09) used as an explicit calibration anchor; a gross-only bound is not acceptable.
- Verdict states material / marginal / immaterial with numbers and its own error bars.
