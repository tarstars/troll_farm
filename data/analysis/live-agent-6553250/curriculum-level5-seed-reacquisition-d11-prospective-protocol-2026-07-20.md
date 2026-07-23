# Curriculum Level 5 D11 prospective confirmation protocol — frozen 2026-07-20

## Decision boundary

The sole preregistered four-million-transition PPO checkpoint passed the complete development
functional, opponent-mechanism, and action gates on `[6500, 7000)`.  This opens exactly one
prospective confirmation under the parent D11 learning protocol.  The prospective result can
accept or reject D11 learning evidence; it cannot by itself authorize export, deployment,
resident replacement, or Arena submission.

No checkpoint selection is permitted after this freeze.  The sole candidate is:

- checkpoint:
  `curriculum-level5-seed-reacquisition-d11-ppo-final-local-l5b.pt`;
- checkpoint SHA-256:
  `44c9a9ed3a232c01fccf9b99b16c3c785b26a1e2c656cb6c40674137138d8de6`;
- development functional evaluation SHA-256:
  `a028ddd1717954130e1674f90cad257d1c50f7ded05b46839218b80fdd211d98`;
- development strict action audit SHA-256:
  `e967d83884b42737ebcce9c7690b3bf8f74c2704e0cd8d289d556d2ce3ee5a6c`;
- training summary SHA-256:
  `32b0166580899ef8ceafc0636300304581f3912ab4d7882b561f9c2bb76d3bb2`.

## Exact unopened bank and environment

- exact prospective interval: `[2031000, 2033000)` (2,000 episodes, no omissions);
- opponent mode: `crop-first-funded-trio-repeated-pressure-reacquire-180`;
- 100 vector environments, timeout 240 turns;
- deterministic teacher control once;
- legal-random control once with RNG seed 127, reused from development;
- sole candidate functional evaluation once; and
- sole candidate strict action audit once.

At freeze, no result from this interval has been generated or inspected.  All control artifacts
must be completely written and hashed before the candidate checkpoint is loaded for prospective
evaluation.  Teacher runs first, random second, functional candidate evaluation third, and action
audit fourth.  A failed control invalidates and closes prospective confirmation; it does not permit
another seed bank, random seed, checkpoint, or threshold.

## Frozen controls

Teacher must pass the original D11 control floors: overall and nontrivial success >=95%; every
recipe >=90%; every height >=93%; crop creation and renewable harvest >=95%; first/third worker
training >=98%/90%; both fresh-funding receipt rates 100%; standard-chopper/feeder productivity
>=98%/85%; rival crop and own renewable harvest >=98%/85%; at least one/two/three destructions in
>=98%/95%/90%; zero illegal actions; no success before turn 180; and no more than three workers or
three destructions.  Legal-random success must be <=5%.

The exact control commands are:

```bash
PYTHONPATH=. .venv/bin/python -m cgauto.rl_level5_env \
  --policy teacher --episodes 2000 --num-envs 100 --seed-base 2031000 \
  --max-turns 240 \
  --opponent-mode crop-first-funded-trio-repeated-pressure-reacquire-180 \
  --output data/analysis/live-agent-6553250/curriculum-level5-seed-reacquisition-d11-prospective-teacher-2031000-2032999.json

PYTHONPATH=. .venv/bin/python -m cgauto.rl_level5_env \
  --policy random --random-seed 127 --episodes 2000 --num-envs 100 \
  --seed-base 2031000 --max-turns 240 \
  --opponent-mode crop-first-funded-trio-repeated-pressure-reacquire-180 \
  --output data/analysis/live-agent-6553250/curriculum-level5-seed-reacquisition-d11-prospective-random-2031000-2032999.json
```

## Frozen candidate gates

Functional acceptance requires all of the following on all 2,000 seeds:

- overall success >=90%, nontrivial success >=88%, every recipe >=82%, every height >=85%;
- terminal crop creation >=90%, renewable harvest >=95%, no success before turn 180, and
  paired-teacher median completion delay <=30 turns;
- first/third worker training >=98%/85% and both fresh-funding receipt rates 100%;
- standard-chopper and feeder productivity >=98%/80%;
- rival crop and own renewable harvest >=95%/80%;
- at least one/two/three destructions in >=95%/85%/70%; and
- no more than three opponent workers or three destructions.

Strict action acceptance additionally requires:

- farmer exact productive-command agreement >=55%;
- chopper exact productive-command agreement >=90%;
- empty-seed recovery MOVE-verb agreement >=99%;
- empty-seed recovery exact source agreement >=30% in aggregate and >=10% in every nonempty
  recipe; and
- at most 3,000 combined unjustified current-cell waits.

The exact candidate commands, run only after both controls pass and are hashed, are:

```bash
PYTHONPATH=. .venv/bin/python -m cgauto.evaluate_level5_checkpoint \
  --checkpoint data/analysis/live-agent-6553250/curriculum-level5-seed-reacquisition-d11-ppo-final-local-l5b.pt \
  --opponent-mode crop-first-funded-trio-repeated-pressure-reacquire-180 \
  --episodes 2000 --num-envs 100 --seed-base 2031000 --max-turns 240 --threads 14 \
  --teacher-baseline data/analysis/live-agent-6553250/curriculum-level5-seed-reacquisition-d11-prospective-teacher-2031000-2032999.json \
  --output data/analysis/live-agent-6553250/curriculum-level5-seed-reacquisition-d11-prospective-candidate-2031000-2032999.json

PYTHONPATH=. .venv/bin/python -m cgauto.analyze_level3_policy \
  data/analysis/live-agent-6553250/curriculum-level5-seed-reacquisition-d11-ppo-final-local-l5b.pt \
  --seed-base 2031000 --episodes 2000 --num-envs 100 --threads 14 --max-turns 240 \
  --curriculum-level 5 --gate-profile d11 \
  --output data/analysis/live-agent-6553250/curriculum-level5-seed-reacquisition-d11-prospective-candidate-action-audit-2031000-2032999.json
```

The prospective candidate passes only if the functional, mechanism, and strict action gates all
pass.  No individual metric may be waived, averaged away, or replaced post hoc.

## Frozen implementation anchors

- parent learning protocol SHA-256:
  `48922c1f7fe4d20936f3d6c1e8aed6b6040c9eb900e231d109fd931057fc368b`;
- Python Level-5 environment SHA-256:
  `29328f0b614c6d57ccee4bae2a962815ec2d9cc281eaabcc9b34943a90d1331c`;
- prospective evaluator SHA-256:
  `1ff9fe1c788abaaec525ba8dbd840877a73eee229ccc0759f3ca05b5fa610a99`;
- strict action-audit implementation SHA-256:
  `ba0d4accc0f8f0838429147a1d859ac2ea62d459aeaeef7b52b363b7dc5b4706`;
- release library SHA-256:
  `381ba5623afb13d77fed09a80dbc2fabc0dd483781a56e9f3c65477783a1dab7`.

If the prospective candidate passes, the next authorized work is compact export, exact
Rust/Python logit and action parity, source-size accounting, Levels 1--4 regression, and layered
field evaluation.  Arena transfer remains separately authorized.
