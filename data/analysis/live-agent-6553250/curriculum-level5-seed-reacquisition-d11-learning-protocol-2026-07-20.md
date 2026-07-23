# Curriculum Level 5 D11 seed-reacquisition learning protocol — frozen 2026-07-20

## Question and decision boundary

Can the accepted compact spatial actor learn exact post-depletion banana-source selection while
preserving its existing renewable economy and the full D11 recurrent opponent interaction?

The fixed-actor audit identifies a narrow mechanism: 99.921% recovery-verb agreement but only
7.147% exact source-cell agreement.  This protocol therefore tests a bounded behavior clone first.
PPO and any YT operation are conditional on clone failure.  No result in this protocol directly
authorizes deployment, resident replacement, or Arena submission.

The D11 environment, observation/action ABI, recipe catalog, reward, opponent, timeout, and
teacher are frozen.  Implementation work may only expose the already implemented D11 mode to the
clone/PPO drivers and report already available telemetry.

## Exact development bank and controls

- opponent mode: `crop-first-funded-trio-repeated-pressure-reacquire-180`;
- exact development interval: `[6500, 7000)` (500 episodes);
- 100 vector environments and timeout 240;
- deterministic D11 teacher once;
- random legal once with RNG seed 127;
- unchanged accepted actor once, before learning; and
- all three artifacts written and hashed before the first clone label is consumed.

The bank is valid only if the teacher reaches the original D11 control floors: 95% overall and
nontrivial, 90% every recipe, 93% every height, 95% crop and renewable harvest, first/third worker
training 98%/90%, both fresh funding receipts 100%, chopper/feeder productivity 98%/85%, rival crop
and own renewable harvest 98%/85%, one/two/three destructions 98%/95%/90%, zero illegal actions,
no success before turn 180, and caps of three workers and three destructions.  Random legal must
remain at or below 5% success.  A failed control closes learning without changing the task.

## Frozen behavior clone

- initialize from checkpoint SHA-256
  `b5daae9ecf81e52ebf35f9bcb9d0eb75110abf0cc5da570f136c5505d96c4882`;
- model/shuffle seed 131;
- online D11 teacher stream beginning at 7,100,000;
- exactly 800,000 teacher decisions;
- 100 environments, ten decisions per 1,000-row chunk;
- two shuffled epochs per chunk and minibatch 1,000;
- Adam `1e-3`, cosine decay to `1e-4`, gradient norm 1.0;
- 14 Torch threads and timeout 240; and
- one deterministic evaluation and one strict action audit on `[6500, 7000)`.

The clone passes only if all of these hold:

- overall >=90%, nontrivial >=88%, every recipe >=82%, and every height >=85%;
- terminal crop >=90%, renewable harvest >=95%, no success before turn 180, and paired-teacher
  median completion delay <=30 turns;
- first/third worker training >=98%/85%, both fresh funding receipt rates 100%, standard-chopper
  and feeder productivity >=98%/80%, rival crop and own renewable harvest >=95%/80%;
- at least one/two/three destructions in >=95%/85%/70%, with at most three workers and three
  destructions;
- farmer/chopper exact productive-command agreement >=55%/90%;
- empty-seed recovery MOVE-verb agreement >=99%, exact source agreement >=30% in aggregate and
  >=10% in every nonempty recipe; and
- at most 3,000 combined unjustified current-cell waits.

A full clone pass becomes the sole learned development candidate and skips PPO and YT.  A failed
gate opens the exact PPO/compute branch below; it does not permit clone-size, seed, schedule, or
threshold tuning.

## Conditional one-million-transition local/YT benchmark

If and only if the clone fails, package the frozen run for the neighboring project's proven YT
vanilla-GPU workflow.  Run the same one-million-transition job once locally and once on one YT RTX
4090 allocation:

- initialization: the exact clone unless it is non-finite or more than five percentage points
  below the prelearning actor in overall success; otherwise the accepted checkpoint;
- model seed 137 and D11 environment stream beginning at 7,200,000;
- 100 environments x 100-decision rollouts, total and Stage-A boundary both 1,000,000;
- four PPO epochs, minibatch 1,000, Adam `2.5e-4` linearly decaying to zero;
- gamma 0.99, GAE lambda 0.95, clip 0.2, entropy 0.01, value coefficient 0.5,
  reward scale 0.01, gradient norm 0.5, target KL 0.03; and
- constant online legal-teacher auxiliary coefficient 0.10.

Record package/build time, queue delay, allocation startup, rollout time, optimization time,
evaluation time, artifact transfer, total wall time, effective transitions/s, result metrics, and
hashes separately.  Backend parity requires finite outputs and local/YT functional metrics within
3 percentage points overall and 5 points for recipe, height, crop, and renewable floors.

YT wins only if parity holds and projected end-to-end time for the frozen four-million-transition
run, including measured fixed overhead, is at most 80% of local projected time.  Otherwise local
wins.  Benchmark checkpoints are throughput evidence, not selectable candidates.

## Conditional four-million-transition PPO

Run exactly one fresh job on the selected backend:

- same frozen initialization rule as the benchmark;
- model seed 139 and D11 environment stream beginning at 7,400,000;
- Stage A at 1,000,000 and final at 4,000,000 transitions; and
- every other optimizer, rollout, and teacher-auxiliary parameter identical to the benchmark.

Stage A requires overall/nontrivial 85%/82%, recipe/height floors 75%/78%, crop/renewable
80%/90%, paired delay <=35 turns, and every original fixed-actor opponent-mechanism gate.  Failure
stops before the remaining three million transitions.  Final acceptance uses the exact clone gates,
including the recovery-specific action audit.  There is no adaptive checkpoint selection.

## Prospective boundary

One development pass—clone or conditional PPO—opens exactly one prospective confirmation on the
already reserved interval `[2031000, 2033000)`.  Freeze and hash teacher and random controls before
evaluating the sole candidate.  The candidate must pass the same final functional, mechanism, and
action gates on all 2,000 seeds.  The interval remains unopened until development acceptance, and
no alternative checkpoint may be substituted after it is observed.

A prospective pass accepts D11 learning evidence only.  Deployment still requires compact model
export, Rust/Python logit and action parity, source-size accounting, regression against accepted
Levels 1--4, layered field evaluation, and a separately authorized Arena transfer.

## YT scope

YT is deliberately excluded from controls, the actor baseline, the clone, and ordinary evaluation.
Its only authorized operation here is the conditional identical PPO benchmark and, if it wins the
frozen 20% end-to-end threshold, the one preregistered four-million-transition PPO run.  No shared
math-project namespace or existing table may be modified.

## Pre-implementation anchors

- D11 development result:
  `247a17d9d523e1a97f41f2596ac77d18e80cbffb35dfdab1c0b1500046e847c1`;
- D11 action diagnosis audit:
  `f7c2a4461e3dcc257f93d9af2014ca6c4925942374706204f336d7245a98b50f`;
- Rust D11 environment source:
  `245fd4c8cd48861d40a7a600f65527c6b88fa53a22dc55f00ce5b5196d9555f6`;
- Python Level-5 environment:
  `29328f0b614c6d57ccee4bae2a962815ec2d9cc281eaabcc9b34943a90d1331c`;
- PPO/evaluation driver:
  `012fdd132dbee19b0e968aa2f80f46127de3c7e9e16e7256c1b9a539ebf8fb49`;
- behavior-clone driver:
  `899ab556fe4aa9f69699afe995235f12fd24abde88a1ffdbb49071ea7b9820c6`;
- action-audit implementation:
  `dccaa98da556e693d502d052d4879945b41adf2a8efdae923990eea16de41277`;
- release library:
  `381ba5623afb13d77fed09a80dbc2fabc0dd483781a56e9f3c65477783a1dab7`;
- development interval `[6500, 7000)`, unopened at freeze;
- clone/PPO streams 7,100,000 / 7,200,000 / 7,400,000, unopened at freeze; and
- prospective interval `[2031000, 2033000)`, still unopened and inaccessible.
