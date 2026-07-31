# 20260731-doubtingiyov-tent-proximity-denial-policy

- Status: claimed — exact-game reconstruction pending
- Record owner: local_codex_1
- Work owner: local_codex_1
- Reviewer: chatgpt_1 (after its current serial review queue)
- Integrator: local_codex_1
- Area: B3.13 / enemy-tent tree denial and planted-tree split
- Base commit: 5663ed0e5aa23b5c08f2c2bd9b1f20119ea154b8
- Branch: agent/local_codex_1
- Progress lease: 15 minutes without concrete evidence
- Created UTC: 2026-07-31T14:15:00Z
- Last updated UTC: 2026-07-31T14:15:00Z

## Owner proposal

> Add to denial trees in one-cell proximity to enemy's tent. When there are more than two
> such trees, switch to full denial and just chop them with both trolls. If there is at
> least one tree, one troll chops and carries wood; another chops planted trees without
> carrying wood.

## Frozen interpretation for validation

- “One cell” means orthogonal map distance one from the enemy shack cell.
- The trigger counts currently standing trees in that adjacency set.
- At zero qualifying trees, the exact active far-denial-d3 policy is unchanged.
- At one or two, one troll prioritizes qualifying tent-adjacent trees and retains the
  normal wood-return leg; the other prioritizes opponent-planted trees and suppresses only
  return legs caused by that planted-tree denial role.
- Above two, both trolls prioritize qualifying tent-adjacent trees and suppress only
  return legs caused by that full-denial role (“just chop”).
- Existing endgame, ordinary production, unrelated carried-resource banking, legality,
  and deterministic tie-breaking remain unchanged.
- The exact active candidate artifact, not the sacred development source, is the parent.

## Outcome

Reconstruct the exact observed active-agent game against DoubtinGiyov, verify whether the
frozen triggers describe the tactical opportunity, and—only if mechanically coherent—
materialize a locally validated successor candidate. This task does not authorize another
Arena cycle.

## Exclusive write set

- this task record;
- `coordination/status/local_codex_1.md`;
- `coordination/messages/local_codex_1/*-20260731-doubtingiyov-tent-proximity-denial-policy-*.md`;
- `cgauto/analyze_doubtingiyov_tent_denial.py` and focused test;
- `data/analysis/live-agent-6553250/doubtingiyov-tent-proximity-denial-result-2026-07-31.*`;
- `local_codex_1/doubtingiyov-tent-proximity-denial/manifest.json`;
- `cgauto/make_tent_proximity_denial_candidate.py` and focused test;
- one new immutable successor candidate plus checksum under `cgauto/submissions/`;
- integrator-owned live docs/ledger disposition only after the exact-game verdict.

## Shared read-only paths

- exact Codingame battle/replay discovered by opponent name and active agent `6585578`;
- the matching exact raw replay and processed trajectory only;
- `cgauto/submissions/candidate-agent6561795-owner-far-denial-no-return-d3-slim.min.rs`;
- existing replay decoder, simulator/referee, and unsealed smoke-map tooling.

## Do not touch

- `rust/src/bin/yamo_orchard_live.rs` (byte-sacred);
- any other game, replay, map, range, frozen artifact, peer write set, raw collection, or
  the 05:17 cron;
- sealed/official/confirmation data.

## Acceptance

- Resolve exact battle/game, agent/submission identities, scores, and raw/trajectory
  hashes, or return `UNIDENTIFIABLE`.
- Reconstruct every resolved turn with zero unknown updates.
- Publish the enemy shack cell, all cardinal-adjacent tree generations, natural/planted
  provenance, health/fruit, first resident contact, command/success/removal, banking, and
  opponent bill consequences.
- Enumerate every 0 / 1–2 / >2 trigger transition and both resident trolls’ assignments,
  commands, carry/free capacity, and target categories.
- Separate observed accounting from any causal claim.
- If coherent, generate from the exact active artifact fail-closed; compile and test
  0/1/2/3-tree boundaries, banking/non-banking split, unrelated behavior, and deterministic
  command legality.
- Run bounded unsealed both-seat smoke tests; sacred SHA remains exact.
- Do not submit, restore, or start a TestSession/Arena cycle.

## Arena authority

Read-only exact-game discovery and replay collection are allowed. Platform mutation is
forbidden while owner-directed candidate `6585578` remains in flight. Any later submission
requires a distinct serialized task after this candidate reaches a terminal maturity
decision.
