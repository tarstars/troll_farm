# chatgpt_1 status

- Updated UTC: 2026-08-30T20:27:00Z
- Environment: interactive ChatGPT with connected GitHub access; no persistent local checkout or general executor
- Role: fresh-eyes architecture and validity contributor; no build, formal-review, integration, YT, platform or Arena authority
- Active programme: `20260829-nn-bot-way-b`
- Branch: `agent/chatgpt_1`

## Phase 3 — live diagnosis

Five self-play lines have shown the same erosion pattern: fruit-chain execution decays before immediate chopping. `ppo-g`, even against the exact champion only, fell from 5/48 at update 500 to 4/48 at update 1,000. `ppo-h` changed gamma to `1.0`; its update-500 checkpoint scored 3/48 and 112.8 points, with explained variance about 0.25.

### Open binding blocker

`coordination/messages/chatgpt_1/20260830T200200Z-20260829-nn-bot-way-b-ppo-h-credit-blocker.md`

The card's “discount swept/acquitted” conclusion is not supported while `gae_lambda` remains `.95`. At every turn boundary `compute_gae` uses `trace_factor = gamma * gae_lambda`, so `ppo-h` changes the trace only `0.94905 -> 0.95`. It is valid gamma-only sensitivity evidence, not an undiscounted long-horizon-credit test. The blocker requires relabelling plus an offline `(.999,.95)` / `(1,.95)` / `(1,1)` advantage comparison or a matched-seed lambda-1 confirmation before that causal axis is closed.

Pinned derivation:

`agent/chatgpt_1@5a8f718cb30de3f21f6ffe9ab0c31fcfed84527a`
`chatgpt_1/nn-way-b/ppo-h-gamma-lambda-audit-2026-08-30.md`

### Source-backed staging correction

`chatgpt_1/nn-way-b/curriculum-source-audit-2026-08-30.md`

The retained delineate source does not describe small maps, short games or an episode cap. It describes assigned build targets with resource-distance shaping, then freezing the movement/action executor while training the plan selector and value head, then joint fine-tuning. The closest bounded next step is an assigned-plan executor gate followed, if it passes, by plan-only PPO with trunk and spatial actor frozen.

### Common critic-to-actor path

`chatgpt_1/nn-way-b/shared-critic-trunk-audit-2026-08-30.md`

After critic warm-up, ordinary PPO re-enables the shared `stem`/`tower` and includes `value_coef * value_loss`. The value loss therefore backpropagates through the same trunk that produces spatial and plan logits. Every failed run shares this unmeasured path. A post-warm-up gradient decomposition must include value loss, and one value-only counterfactual optimizer step should measure resulting logit/top-1/fruit-action changes before another all-parameter long run.

The six YT arms remain exploratory checkpoint searches. Their common scout bench may rank checkpoints, but seed/treatment confounding prevents factor attribution without matched-seed confirmation.

## Phase 4 — engineering complete

The portable one-file export is integrated and independently reproduced:

- runtime AVX2 dispatch plus baseline fallback;
- both paths 48/48 games and 13,206/13,206 commands identical;
- shipping fallback machine code verified AVX-free;
- deterministic regeneration and direct both-seat observation/mask/codec parity;
- corpus seat check 370/370;
- UTF-16 size 83,282 of 100,000.

A real shipping candidate still needs the three-run quiet-host timing certificate and the owner's separate platform word. Nothing has been submitted.

## Next check

- coordinator acknowledgement/ruling on the gamma/lambda blocker;
- `ppo-h` update-1,000 evidence, interpreted as gamma-only;
- offline advantage and gradient decompositions;
- assigned-plan executor evidence or a source-backed staged-training charter;
- returned YT checkpoints under scout/confirmation separation.

## Boundaries

No build, experiment, training-process mutation, YT operation, platform submission, leaderboard read or Arena action was taken.
