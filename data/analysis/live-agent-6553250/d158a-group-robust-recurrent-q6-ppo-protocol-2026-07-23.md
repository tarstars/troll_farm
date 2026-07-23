# D158a group-robust recurrent q6 PPO — frozen protocol

Date: 2026-07-23  
Status: frozen after D157a identified the omitted objective branch, before any D158 training

## Causal question

Does recurrent q6 fail because the pooled terminal-margin objective rewards unstable family trades
and symmetric score suppression? Keep the D109 actor, critic, q6 proposal executor, optimizer,
transition budget, and masks unchanged. Change only terminal-return shaping.

Train four variants from the same model seed and the same task stream:

1. `pooled_margin`: exact D109 terminal `margin_delta / 100` control;
2. `capped_margin`: cap positive margin delta at +40, retain all downside;
3. `own_protected`: capped margin plus `0.5 * min(own_score_delta, 0)`;
4. `group_dro_own`: own-protected return multiplied by deterministic group-DRO family weights.

Group-DRO keeps an exponential moving average of raw margin delta for each of the eight training
families (`alpha=0.20`). At each rollout boundary, weights are proportional to
`exp(-(ema - mean(ema)) / 20)`, exponent-clipped to `[-1.5,+1.5]`, weight-clipped to
`[0.5,2.0]`, then normalized to mean one. Weights are frozen within a rollout and updated only
after all terminal rows in that rollout. Family identity is training-only; it is not an actor
input or deployable feature.

## Frozen execution

- model seed: `15801` for every variant;
- training maps: `9,845,000--9,845,127`;
- development selection maps: `9,845,200--9,845,231`;
- transition geometry: 60 environments x 20 steps x 54 updates = 64,800 per variant;
- unchanged D109 optimizer: three epochs, learning rate `3e-4`, entropy `0.02`, clip `0.20`,
  gamma `1`, GAE `0.95`, and the same 10,725-parameter network;
- run the four variants concurrently with five Rayon/PyTorch threads each;
- evaluate control, common initialization, and final actor twice on all 512 development tasks;
- require byte-exact repeated evaluation and exact raw paired-return identity.

The reserved maps `9,844,200--9,844,215` are absent and remain sealed. D158 uses no D148--D156
outcomes for fitting or selection.

## Development admission

A variant must pass mechanics, finite optimization, crop creation, workforce parity within five
percentage points, 10%--95% intervention, at least eight proposal representatives, and:

- mean margin delta at least `+1`;
- strict improvement at least 35%;
- at least six positive families and worst family at least `-3`;
- mean own-score delta at least `-1`; and
- at least `+5` margin over the common initialized actor.

If more than one passes, select by highest worst-family mean, then mean margin, own-score delta,
strict rate, and the frozen variant order above. No checkpoint averaging or intermediate-step
selection is allowed.

## Confirmation and decision

Only an admitted variant may open maps `9,845,300--9,845,363` (1,024 tasks), evaluated twice.
Confirmation requires exact mechanics/repeat/safety plus mean `+2`, strict improvement 40%, six
positive families, worst family `-3`, and nonnegative own-score delta or nonpositive opponent-score
delta.

- No development admission: close this objective ablation without confirmation.
- Confirmation fail: close group-robust recurrent q6; do not tune weights, cap, own penalty,
  duration, model seed, or consumed maps.
- Confirmation pass: open source-size reconstruction and a separate final field gate; D158 is not
  itself a submission.

No branch authorizes Arena, TestSession, submission, resident mutation, or reading the reserved
panel.

