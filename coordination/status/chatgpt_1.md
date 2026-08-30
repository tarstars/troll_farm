# chatgpt_1 status

- Updated UTC: 2026-08-30T19:27:00Z
- Environment: interactive ChatGPT with connected GitHub access; no persistent local checkout or general executor
- Role: fresh-eyes architecture and validity contributor; no build, formal-review, integration, YT, platform or Arena authority
- Active programme: `20260829-nn-bot-way-b`
- Branch: `agent/chatgpt_1`

## Phase 3 — live diagnosis

The training validity corrections are integrated: within-turn credit does not decay across artificial mini-steps; PLAN calls zero planes 59–71 and 98 (`off-v2`); the exact linked champion is accepted after independent 200-game / 49,945-turn reproduction.

Five self-play attempts have now shown the same erosion pattern. `ppo-g`, with only the exact champion as opponent, preserved the clone at update 500 but fell to 4/48 by update 1,000. The coordinator stopped it and started `ppo-h` with gamma `1.0` as the next one-variable test.

`chatgpt_1/nn-way-b/ppo-h-gamma-lambda-audit-2026-08-30.md`, pinned at `agent/chatgpt_1@5a8f718cb30de3f21f6ffe9ab0c31fcfed84527a`, records a validity limitation:

- `compute_gae` uses `trace_factor = gamma * gae_lambda` at each turn boundary;
- `gae_lambda` remains `0.95`;
- the effective trace changes only `0.94905 -> 0.95` when gamma changes `.999 -> 1.0`;
- at 50 turns the direct terminal coefficient changes `0.07319 -> 0.07694`, and at 100 turns `0.00536 -> 0.00592`;
- advantages are then normalized per minibatch.

Therefore `ppo-h` may keep running, but it is a gamma-only sensitivity run, not a test of undiscounted terminal credit. The cheapest follow-up is to recompute one saved rollout under `(.999,.95)`, `(1,.95)`, and `(1,1)` before interpreting or extending it. Direct progress message:

`coordination/messages/chatgpt_1/20260830T192500Z-20260829-nn-bot-way-b-ppo-h-credit-progress.md`

The six YT jobs remain exploratory checkpoint searches. `coordination/messages/chatgpt_1/20260830T161400Z-20260829-nn-bot-way-b-yt-six-arms-disposition-r5.md` requires preserved exact configs, one frozen checkpoint-selection rule, the repeated 48-game bench as scout only, and matched-seed one-factor follow-ups before causal claims.

## Phase 4 — engineering complete

Codex's portable one-file export amendments (d/e/f) were accepted, integrated as `main@bb3645eaef5049b6639da0a913be7bd55b32ade8`, and independently reproduced by Claude.

Accepted evidence now includes:

- runtime AVX2 detection and a baseline non-AVX fallback;
- AVX2 and forced-fallback command parity, each 48/48 games and 13,206/13,206 turns;
- machine-code inspection confirming the shipping fallback kernel is AVX-free;
- deterministic regeneration and direct both-seat observation/mask/codec parity;
- full training-corpus seat check 370/370;
- UTF-16 size accounting, 83,282 of 100,000 units for the amended clone export.

The coordinator corrected the owner-facing “ladder-ready” wording and quarantined the malformed 16:09Z correction while applying its content. Phase 4 is complete as engineering. A real shipping candidate still needs the three-run quiet host timing certificate and the owner's separate platform word.

## Next check

- coordinator response to the gamma/lambda interpretation;
- `ppo-h` checkpoint results, labelled as gamma-only evidence;
- the offline three-estimator advantage diagnostic if accepted;
- returned YT checkpoints under scout/confirmation separation;
- any candidate that actually exceeds the clone's 9/48 scout bar.

## Boundaries

No build, experiment, training-process mutation, YT operation, platform submission, leaderboard read or Arena action was taken.
