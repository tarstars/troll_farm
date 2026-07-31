# 20260731-second-troll-funding-before-denial

- Status: claimed; exact mechanism audit in progress
- Record owner: local_codex_1
- Work owner: local_codex_1
- Reviewer: chatgpt_1 after materialization
- Integrator: local_codex_1
- Area: opening workforce funding / tent-denial precedence
- Base commit: 43783602634df28ea8dc93db41d36ae8428419fc
- Branch: agent/local_codex_1
- Created UTC: 2026-07-31T17:00:00Z
- Last updated UTC: 2026-07-31T17:05:00Z

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
