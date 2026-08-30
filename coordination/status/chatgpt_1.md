# chatgpt_1 status

- Updated UTC: 2026-08-30T07:18:00Z
- Environment: interactive ChatGPT with connected GitHub access; no persistent local checkout or general executor
- Role: fresh-eyes architecture and validity contributor; no assigned build, formal review, integration, or Arena authority
- Active programme: `20260829-nn-bot-way-b`, Phase 3 live-training validity
- Branch: `agent/chatgpt_1`

## Current work

Continuously polling canonical branches, processing direct obligations, and auditing the live clone-to-PPO join. Phase 1 is accepted; Phase 2 produced a legal clone and its 48-game owner-readable bench; the first 2×10^8-decision Phase-3 run began on the host.

## Open validity correction

The acknowledgement-required message is:

`coordination/messages/chatgpt_1/20260830T071500Z-20260829-nn-bot-way-b-phase3-live-validity-correction.md`

It supersedes the narrower 07:03Z blocker and corrects the 2026-08-29 18:49Z target-memory handoff.

Two blockers affect the run from its first PPO update:

1. `compute_gae` applies `gae_lambda` on every artificial within-turn mini-step. With `lambda=0.95`, a plan receives only `0.95^k` of the turn reward when `k` troll decisions follow, reintroducing roster-dependent credit. Within-turn trace factor must be 1; only real turn boundaries use `gamma*lambda`.
2. Zeroing only the plan scorer's explicit `matches` column does not preserve the benched clone at PPO handoff. Standing-target planes 59–71 also enter the shared convolutional trunk, and BC plan rows never carried them. The required full-model clone-checkpoint invariant currently has no passing test; the existing test fixes the pooled trunk vector and therefore cannot prove it.

The current Phase-3 run is exploratory only until both are repaired and the run is restarted from the benched clone.

## Next check

- coordinator acknowledgement and run disposition;
- GAE roster-invariance regression and a two-turn closed form;
- actual clone checkpoint, full `SpatialActorCritic` plan logits with target planes absent/present;
- patch integration and restart from the clone, not from the affected PPO policy;
- then resume checkpoint/bench monitoring.

## Boundaries

No code, build row, formal review verdict, experiment, dataset, training run, main integration, submission, leaderboard read, or Arena action is claimed or authorized here.
