# chatgpt_1 status

- Updated UTC: 2026-08-30T20:46:00Z
- Environment: interactive ChatGPT with connected GitHub access; no persistent local checkout or general executor
- Role: fresh-eyes architecture and validity contributor; no build, formal-review, integration, YT, platform or Arena authority
- Active programme: `20260829-nn-bot-way-b`
- Branch: `agent/chatgpt_1`

## Phase 3 — accepted diagnosis and live blocker

The coordinator accepted the evening validity audits at:

`coordination/messages/local_claude_1/20260830T205500Z-20260829-nn-bot-way-b-ack.md`

Accepted corrections include:

- `ppo-h` is gamma-only sensitivity at lambda `0.95`, not an undiscounted-credit test;
- delineate's recorded curriculum uses assigned targets and later a frozen movement executor while training plan/value, not a short-game or small-map episode cap;
- value loss has a direct gradient path through the shared actor trunk after warm-up;
- the clone decoding factorial is AA `9/48`, SA `8/48`, AS `3/48`, with SS still missing.

Claude is chartered to build the per-objective gradient falsifier:

`coordination/messages/local_claude_1/20260830T210000Z-20260829-nn-bot-way-b-gradient-handoff.md`

The latest audit specification requires restoring the checkpoint's Adam state and exact config, reporting global clipping, and using both on-policy minibatches and a common fixed observation census:

`agent/chatgpt_1@14a1bdd665e807f49f06188198774a2ddaa24797`
`chatgpt_1/nn-way-b/shared-trunk-value-gradient-audit-2026-08-30.md`

### Binding blocker on `ppo-i`

The coordinator integrated the first `--train-scope plan-critic` patch at:

`main@213ee7f586a6a0fc6fda22bee9571159a3efdf0f`

It correctly freezes `stem.*`, `tower.*`, and `actor.*`, but changes only parameter gradients. The rollout still samples TROLL commands, and the loss still mixes frozen TROLL rows into PLAN advantage normalization, policy loss, entropy, anchor KL, `approx_kl`, `clip_fraction`, and the `target_kl` stopping rule.

Binding blocker:

`coordination/messages/chatgpt_1/20260830T204230Z-20260829-nn-bot-way-b-plan-critic-scope-blocker.md`

Latest pinned review:

`agent/chatgpt_1@fb3d0c897c27397880d577130531d354fdcd91b3`
`chatgpt_1/nn-way-b/plan-critic-scope-review-2026-08-30.md`

Minimum clean Level-4-like semantics before launch:

```text
PLAN rows: sampled; PLAN-only advantage normalization, PPO loss, entropy, anchor KL, approx_kl, clip_fraction and target_kl
TROLL rows: frozen masked argmax; executed in the environment but excluded from PPO policy terms
value loss: all rows
```

Required tests cover TROLL RNG-independence and bench parity, PLAN gradient/anchor/KL invariance to duplicated TROLL rows, no-PLAN minibatches, frozen parameter identity, and checkpoint recording of the scope and executor decoding.

`ppo-i` must not start from `main@213ee7f5`; that code would train a plan selector on the measured `3/48` sampled command executor and gate it using the `9/48` argmax executor.

## Credit-horizon correction

Latest pin:

`agent/chatgpt_1@96373d590939b2f6a0439facf5091d8535c46ad2`
`chatgpt_1/nn-way-b/ppo-h-gamma-lambda-audit-2026-08-30.md`

The live recipe uses 32 mini-steps per rollout, only about 5–16 real turns depending on troll count. Even gamma `1`, lambda `1` would remove decay only inside that buffer; earlier decisions depend on critic bootstrap. The next honest credit test is a within-buffer estimator comparison plus a full-episode critic audit against realised return-to-go and a census of rows that actually share a buffer with terminal reward.

## Stochastic behaviour mismatch

Latest corrected factorial audit:

`agent/chatgpt_1@aa4d456934c22bd8ce2bf1589528150b34138926`
`chatgpt_1/nn-way-b/stochastic-behavior-mismatch-audit-2026-08-30.md`

Command sampling, not plan sampling, carries the measured deployment gap. The spatial head samples one categorical distribution over up to 3,146 entries, with many legal MOVE destinations. Future diagnostics should measure MOVE probability mass, legal-action multiplicity, entropy, and forward anchor gradients; plan and command temperatures must be separate if a matched-seed temperature control is later justified.

## Phase 4 — engineering complete

The portable one-file export is integrated and independently reproduced:

- runtime AVX2 dispatch plus baseline fallback;
- both paths 48/48 games and 13,206/13,206 commands identical;
- shipping fallback machine code verified AVX-free;
- deterministic regeneration and direct both-seat observation/mask/codec parity;
- corpus seat check 370/370;
- UTF-16 size 83,282 of 100,000.

A real shipping candidate still needs the quiet-host timing certificate and the owner's separate platform word. Nothing has been submitted.

## Next check

- coordinator ruling and corrected implementation for the `plan-critic` blocker;
- Claude's gradient-instrument claim, code, host outputs, and analysis;
- `ppo-h` update-1,000 evidence, interpreted only under the actual lambda and rollout horizon;
- returned YT checkpoints under scout/confirmation separation;
- any candidate that exceeds the clone's 9/48 scout bar.

## Boundaries

No build, experiment, training-process mutation, YT operation, platform submission, leaderboard read or Arena action was taken.
