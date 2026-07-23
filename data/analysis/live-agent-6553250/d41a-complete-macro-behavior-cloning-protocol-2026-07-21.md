# D41a complete-macro behavior cloning — frozen protocol (2026-07-21)

## Question and authorization

D40 passes every complete-policy initializer gate. D41a asks whether a tiny shared candidate scorer
can clone that teacher closely enough to survive its own closed-loop state distribution. This
protocol authorizes observation/batch infrastructure, teacher collection, and behavior cloning
only. PPO, confirmation, candidate construction, TestSession, submission, and Arena remain sealed.

## Environment and task splits

Retain the exact D40 environment, work-conserving teacher, nine action planes, corrected
transactional scheduler, TRAIN-relevant prediction telemetry, both seats, and all eight opponents.
Enumerate tasks deterministically as opponent-fastest within seat within official map seed.

- training stream starts at map seed **9,700,000** and contains 500,000 teacher decisions;
- teacher-forced validation uses maps **9,710,000--9,710,031**;
- closed-loop development uses maps **9,711,000--9,711,031**;
- confirmation maps **9,720,000--9,720,031** are sealed; and
- D37--D40 selection seeds remain forbidden.

Generate exact D40 and random closed-loop baselines on the development maps before training.

## Candidate-set observation

The first pre-data wrapper smoke test reached 135 legal candidates and correctly aborted the
initial 128-slot assumption before producing any artifact. The structural bound is therefore
amended to **768**: at most 242 board cells can hold plants, each plant contributes at most
`FELL/HARVEST/RENEW`, and mine/bank/idle candidates fit in the remaining headroom. A hard overflow
still aborts collection.

Expose at most 768 legal candidates per decision. Each candidate
receives one 44-float vector, computed identically in Rust collection and deployment:

1. bias, normalized turn, own worker count, own/opponent score;
2. stage and active TRAIN-goal one-hots;
3. exact D40 branch one-hot: TRAIN, deficit, shack evacuation, or rate;
4. exact affordability, current-worker-on-shack, and any-positive-deficit flags;
5. train-action or macro-job-kind one-hots;
6. normalized predicted ETA/reward, exact deficit reduction, and frozen D37 rate value;
7. provenance one-hot;
8. relevant predicted-deposit values and current outstanding deficits; and
9. normalized stable action/target/plant-cell coordinates.

Illegal candidates are absent rather than zero-padded inputs. Preserve their exact flattened action
IDs separately. The teacher label is a candidate index and must always be legal. No opponent identity
or outcome value is an actor input.

The actor is a shared MLP `44 -> 32 -> 16 -> 1` with ReLU activations. It scores candidates
independently; a masked argmax selects the exact action ID. This is 1,985 parameters before any
optional value head. Behavior cloning uses unweighted masked cross-entropy, Adam, two epochs per
streaming chunk, initial/final learning rates 1e-3/1e-4 with cosine decay, batch size 2,048, and
fixed model seeds **401, 402, 403**. No architecture or optimizer sweep is allowed.

## Integrity and performance gates

Infrastructure must first pass Rust/Python shape tests, legal-label checks, deterministic A/A
feature hashes, candidate-overflow checks, and exact teacher closed-loop reproduction through the
new batch interface.

Each model seed passes teacher-forced validation only if:

- overall top-1 accuracy is at least 99.0%;
- every D40 branch has at least 97.0% accuracy;
- action-plane macro F1 is at least 0.95; and
- no NaN, illegal argmax, or feature mismatch occurs.

A model seed passes closed-loop development only if all hold:

- mean margin is no more than 20 below exact D40 and at least 100 above random;
- worker-two rate is at least 90%, worker-three at least 80%, and own-crop rate at least 90%;
- every opponent family is no more than 35 margin below D40 and at least 40 above random;
- invalid direct commands, provenance failures, relevant prediction failures, decision loops, and
  worker-cap errors are zero; and
- deterministic repeated inference produces exact action/state hashes.

At least two of the three fixed model seeds must pass both gate groups. Choose the smallest passing
seed as the sole D41a checkpoint; do not rank-tune on score. The actor must remain <=2,000
parameters, <=8 KiB float32 weights, <=2 KiB int8 weights, and its generated inference kernel must
be <=15,000 source bytes. A pass opens a separately frozen PPO-development protocol initialized
from that clone. A failure closes this feature/model pair before PPO.

## Compute

Use the local 20-CPU machine for collection and the tiny CPU model. YT/GPU launch is not authorized:
the network is too small for transfer overhead to dominate until PPO has a validated local signal.
Preserve protocols, baselines, manifests, logs, checkpoints, exported weights, tests, and hashes.
