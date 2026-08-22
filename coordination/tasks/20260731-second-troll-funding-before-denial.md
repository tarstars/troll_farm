# 20260731-second-troll-funding-before-denial

- Status: confirmed; combined successor locally validated and materialized
- Record owner: local_codex_1
- Work owner: local_codex_1
- Reviewer: chatgpt_1 after materialization
- Integrator: local_codex_1
- Area: opening workforce funding / tent-denial precedence
- Base commit: 43783602634df28ea8dc93db41d36ae8428419fc
- Branch: agent/local_codex_1
- Created UTC: 2026-07-31T17:00:00Z
- Last updated UTC: 2026-07-31T17:15:00Z

## Owner observation and rule

> looks like this rule blocks training the second troll. Check it. If it is, prioritise
> collection of resources for the second troll over denial logic

Owner follow-up:

> also include diagonal trees into denial policy

## Preliminary diagnosis

The B3.15 on-site ownership predicate only filters same-tree candidates. The direct
precedence defect is inherited from B3.13: `apply_tent_denial` runs after
`YamoBot::commands` and can overwrite the sole worker's `early_candidates` resource
collection whenever a live tree is cardinal-adjacent to the enemy tent.

In a read-only scan of the latest 40 exact B3.15 results, many complete games with an
enemy-adjacent tree from turn 1 issue their first `TRAIN` only at the hard turn-35
downgrade. Exact causal attribution and a bounded successor remain to be materialized.

## Exclusive write set

- this task, own status/messages;
- one compact exact-game/cohort analyzer and compact evidence under `cgauto/`,
  `data/analysis/live-agent-6553250/`, and `local_codex_1/`;
- one fail-closed successor generator, immutable candidate/checksum, and focused tests.

## Do not touch

- sacred `rust/src/bin/yamo_orchard_live.rs`;
- immutable parent artifacts, existing analyzers/results, peer namespaces, sealed ranges,
  `data/raw/games/`, and the 05:17 cron;
- Arena/TestSession under this diagnostic task.

## Acceptance

- Lock an exact full-length B3.15 game with enemy-adjacent activation before worker 2.
- Prove current source reproduces the recorded stream and show the pre-wrapper opening
  command that denial overwrites through the delay.
- The successor must preserve the inner opening resource command while own roster is one
  and the opening objective remains active; after training or explicit opening
  abandonment, denial must remain exact-parent.
- After that opening precedence gate, tent proximity must use the full eight-neighbor
  ring rather than only cardinal neighbors. Focused tests must prove diagonal activation
  after worker 2 and non-activation over opening collection before worker 2.
- Re-run B3.15, sticky-bank, and tent-proximity boundaries; run exact replay and bounded
  unsealed both-seat smokes; preserve sacred SHA.
- Materialize only. Any live replacement requires a distinct serialized Arena task.

## Exact result

- Exact full game `897560637`, resident `6585801`/`41071204` seat 0 versus FRHT
  `6535596`/`40941012`: valid 127–231 loss, 300 turns, zero unknown updates.
- The exact live source reproduces 300/300 recorded command lines with zero stderr.
- A BANANA is cardinally adjacent to the enemy tent from turn 1. The inner opening
  planner emits `MOVE 0 8 0`; the later tent-denial wrapper replaces it with
  `MOVE 0 7 1`.
- The wrapper overwrites 18 active opening decisions through turn 40:
  turns 1–17 and 29. The recorded bot first TRAINs only on hard downgrade turn 35.
- In a fixed 40-game B3.15 slice, 35 games are full length. Of 21 with cardinal
  activation by turn 34, 14 TRAIN at turn 35 and seven earlier. Of the other 14,
  zero TRAIN at 35 and all 14 earlier. This is descriptive breadth, not causal value.
- Root cause is B3.13 post-planner precedence, not the B3.15 on-site ownership predicate.

## Successor and gates

- Candidate:
  `cgauto/submissions/candidate-agent6585801-second-funding-first-diagonal-denial-slim.min.rs`.
- Size: 68,893 bytes; SHA-256
  `b8382910116bbfaeade378732508bf4281a7f4ee793ae8f14ae41992ece37af4`.
- While own roster is below two and the opening objective remains active, the denial
  wrapper returns the inner opening command unchanged. After worker two exists or the
  opening is abandoned, denial resumes over all eight enemy-tent neighbors.
- The successor preserves the inner command on all 18 exact overwritten decisions.
- Five new compiled boundaries pass: cardinal and diagonal opening precedence, diagonal
  activation with two workers, activation after abandonment, and deterministic bounded
  rebuild. All 11 inherited on-site/sticky/tent tests also pass.
- On eight unsealed both-seat smoke cells versus fixed `ringfix3`, worker 2 TRAIN is
  earlier in 7/8 cells and unchanged in 1/8; never later. All terminate with zero stderr.
- Direct `rustc`, exact sidecar/size, and sacred SHA pass.
- This task made no Arena mutation.
