# chatgpt_1 status

- Updated UTC: 2026-08-30T07:38:00Z
- Environment: interactive ChatGPT with connected GitHub access; no persistent local checkout or general executor
- Role: fresh-eyes architecture and validity contributor; no assigned build, formal review, integration, or Arena authority
- Active programme: `20260829-nn-bot-way-b`, Phase 3 live-training validity
- Branch: `agent/chatgpt_1`

## Current work

Continuously polling canonical branches, processing direct obligations, and auditing the live clone-to-PPO join. Phase 1 is accepted; Phase 2 produced a legal clone and its 48-game owner-readable bench; the first 2×10^8-decision Phase-3 run began on the host.

## Open validity correction

The acknowledgement-required message is:

`coordination/messages/chatgpt_1/20260830T073600Z-20260829-nn-bot-way-b-phase3-live-validity-correction-r3.md`

It is the consolidated final correction, superseding r2.

Two blockers affect the run:

1. `compute_gae` applies `gae_lambda` on every artificial within-turn mini-step. With `lambda=0.95`, a plan receives only `0.95^k` of the turn reward when `k` troll decisions follow. Within-turn trace factor must be 1; only real turn boundaries use `gamma*lambda`.
2. BC and the 48-game clone bench give PLAN rows planes 59–71 and 98 equal to zero on every decision. `FullEnv` introduces standing-target planes 59–71 on ordinary PPO turns and plane 98 after a purchase. All these planes enter the shared convolutional trunk, so zeroing only the scorer's direct match column does not preserve the trained/benched clone. The existing test fixes the pooled trunk vector and bypasses the mismatch.

The current Phase-3 run is exploratory only until both are repaired and the run is restarted from the original benched clone.

## Next check

- coordinator acknowledgement and run disposition;
- GAE roster-invariance regression and a two-turn closed form;
- actual clone checkpoint, full-model PLAN logits for zero target / standing target / plane-98 latch;
- identical PLAN context across cloning, bench, fake and shipping environment;
- patch integration and restart from the clone, not the affected PPO policy;
- then resume checkpoint/bench monitoring.

## Boundaries

No code, build row, formal review verdict, experiment, dataset, training run, main integration, submission, leaderboard read, or Arena action is claimed or authorized here.
