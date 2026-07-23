# D109a duration-only recurrent q6 PPO — frozen protocol

Date: 2026-07-22  
Status: frozen before D109 training or held evaluation

## Hypothesis

D108a passes mechanics, learning signal, and safety, improves its initialization by `+8.141`, and
reaches `-0.738` versus D40, but fails mean and opponent-family value. Every family improves from
initialization, the final training rollout is `+2.537`, mean KL is only `0.000362`, mean clipping is
`0.0104%`, entropy remains high, and 246/256 probe actions change. This prospective failure class
supports undertraining rather than a dead action representation, unsafe optimizer, or saturated
policy.

Test duration once, in isolation: train the identical architecture, initialization, paired reward,
and optimizer from scratch for approximately four times as many transitions on entirely new maps.
Do not load, continue, select, distill, or otherwise use the D108 checkpoint.

## Immutable inputs

- D108 result JSON:
  `d36abd2f1610163ae2a775978cb69a59ac48658e65b174e65c3ddeccad37083c`;
- frozen D108 trainer/model definition:
  `ed4ff4d23c88a7df0152334f739d169e6254a53d4111aa5f3c7c06f274669086`;
- q6 Rust environment and Python wrapper:
  `739fa02c00d92ba271f7a7a15fca893f18fffa258c02ba39c4a4cb08eaba2af1` and
  `8f102e1eca5a1bcc49ea932170b100eacea5848d7af097c0b21689229dc68911`;
- q6 expert bank:
  `87c6ed7d018983b72bcc158b6de0aafd6174873d180fb5f3af51f787f3c03fd8`;
- release library:
  `90284b35574e78740bdd1b1f81ea6ba5fdf03265a5ef029f1667a676748835cf`.

The D108 model remains exactly 12 recurrent state units, an 8-value shared action embedding, 4,452
actor parameters, 6,273 critic parameters, exact 379-value dynamic proposal features, exact D40
action zero, and four noncontrol batches. Model seed remains `10801` so duration is the causal
change.

## Training

- untouched training seeds `9,835,000--9,835,127`, both seats and all eight opponents;
- 128-map / 2,048-scenario cyclic pool with exact cached D40 baselines;
- 60 vector environments, 20 recurrent steps, 1,200 transitions per update;
- 64,800 total transitions / exactly 54 updates;
- 20 Rayon and PyTorch threads;
- three PPO epochs and ten environment sequences per minibatch; and
- the unchanged D108 optimizer/objective: Adam `3e-4`, epsilon `1e-5`, gamma `1`, GAE `0.95`,
  clip `0.20`, entropy `0.02`, value coefficient `0.5`, gradient norm `0.5`, target KL `0.03`.

Capture the same 256-row pre-update probe. Store only the final checkpoint. No early stop, learning
rate schedule, checkpoint selection, restart, seed sweep, family reweighting, imitation, or D108
checkpoint use is permitted. Vector widening from 20 to 60 is execution-only: on consumed maps it
raises exact-environment throughput from 31.1 to 45.5 transitions/s without changing observations,
actions, rewards, or task order.

## Held evaluation

Use untouched seeds `9,837,000--9,837,031`, both seats and all eight opponents: 512 tasks. Evaluate
exact control, the same initialized actor, and the final actor deterministically twice from new
environments. The complete 1,536-row TSVs must be byte-identical before value interpretation.

## Frozen gates

### Mechanics

Require exactly 64,800 transitions and 54 updates; finite losses/parameters; zero masked actions;
at least 10,000 training episodes; paired reward identity below `1e-4`; zero training failures; at
least 48 representative actions explored; 10%--95% training noncontrol rate; complete repeated
held matrices; held reward identity below `1e-4`; zero held failures; and at least 30 transitions/s.

### Signal

Require at least 40/256 probe choices to change, eight final probe actions, actor drift at least
`0.10`, eight held representatives, 10%--90% held intervention, and repeated intervention on at
least 10% of held tasks.

### Safety

Require 100% held crop creation and worker-three reach within five percentage points of exact held
D40.

### Fixed-policy value

Require mean held gain at least `+2`, strict improvement on at least 40% of tasks, every family at
least `-3`, at least six positive families, nonnegative own score or nonpositive opponent score,
and at least `+5` versus the identically initialized actor.

## Decision

- **Mechanics failure:** repair only; no value interpretation.
- **Signal failure:** close the current recurrent/shared scorer.
- **Safety or value failure:** close duration-only recurrent q6; do not extend again or tune on
  either D108 or D109 held panels. Return to opponent-conditioned objectives or a different
  controller abstraction on new maps.
- **Full pass:** open D109b deployable-size reconstruction and a final entirely new confirmation
  panel. D109a itself remains experimental evidence, not an automatic candidate.

No branch authorizes TestSession, Arena, candidate construction, submission, or resident change.
