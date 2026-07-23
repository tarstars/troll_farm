# Curriculum Level 5 D11 prospective confirmation result — 2026-07-20

## Frozen basis

The development-accepted checkpoint was fixed before the prospective bank was opened:

- checkpoint SHA-256:
  `44c9a9ed3a232c01fccf9b99b16c3c785b26a1e2c656cb6c40674137138d8de6`;
- exact prospective interval: `[2031000, 2033000)`;
- opponent mode: `crop-first-funded-trio-repeated-pressure-reacquire-180`;
- 2,000 episodes, 100 vector environments, timeout 240;
- random-control RNG seed 127; and
- prospective protocol SHA-256:
  `a847042cbd7b6efb3262549c05c5cc07017d945b719524c238ca614c8e01c700`.

The declared order was followed once: teacher control, legal-random control, candidate functional
evaluation, then candidate strict action audit.  Both controls were written, validated, and hashed
before candidate inference began.  No alternative checkpoint or interval was inspected.

## Controls — pass

| Control metric | Result | Gate | Verdict |
|---|---:|---:|---|
| Teacher overall | 99.65% | >=95% | pass |
| Teacher nontrivial | 99.48% | >=95% | pass |
| Teacher worst recipe | 98.43% | >=90% | pass |
| Teacher worst height | 99.60% | >=93% | pass |
| Teacher crop / renewable | 99.80% / 99.75% | >=95% / >=95% | pass |
| Teacher three-destruction activation | 95.85% | >=90% | pass |
| Teacher illegal actions | 0 | 0 | pass |
| Legal-random overall | 0/2,000 = 0% | <=5% | pass |

Every frozen teacher funding, worker-training, productivity, opponent-crop, renewable-harvest,
one/two/three-destruction, horizon, and cap condition also passed.  The teacher artifact SHA-256 is
`f361f9c0e48e9ffa563086f2ed7cbe0fe679c7fd66a195b906cd5cb40caa733e`; legal random is
`fce2a700a8cf85fb27b7126b7bac1e51e2442794d42eed8acf9fdb269f31bae0`.

## Candidate functional and mechanism confirmation — pass

| Gate metric | Prospective result | Floor | Verdict |
|---|---:|---:|---|
| Overall success | 1,953/2,000 = 97.65% | 90% | pass |
| Nontrivial success | 1,131/1,164 = 97.16% | 88% | pass |
| Worst recipe | 95.67% | 82% | pass |
| Worst height | 96.79% | 85% | pass |
| Terminal crop | 98.30% | 90% | pass |
| Renewable harvest | 98.15% | 95% | pass |
| Paired teacher median delay | 0 turns | <=30 | pass |
| Original D11 opponent-mechanism gate | pass | pass | pass |

All eight recipes score at least 95.67%, and all four map heights score at least 96.79%.  The
opponent trains worker three in 97.80%, creates a crop in 99.95%, uses its chopper/feeder
productively in 100%/93.55%, renewably harvests in 91.10%, and reaches three destructions in
94.75%.  Both fresh-funding receipt rates are 100%, with caps of three workers and three
destructions.  The functional artifact SHA-256 is
`985cabd2f040065fe28ed690248613f30da15645239e7fc2b200d58849c96a24`.

## Candidate strict action confirmation — pass

| Action metric | Prospective result | Gate | Verdict |
|---|---:|---:|---|
| Farmer exact productive command | 92.70% | >=55% | pass |
| Chopper exact productive command | 97.10% | >=90% | pass |
| Empty-seed recovery MOVE verb | 99.93% | >=99% | pass |
| Empty-seed recovery exact source | 45.19% | >=30% | pass |
| Worst nonempty-recipe recovery exact source | 22.67% | >=10% | pass |
| Unjustified current-cell waits | 405 | <=3,000 | pass |

The audit covers 313,082 farmer and 313,082 chopper decisions.  Exact source selection clears its
per-recipe gate in all eight recipes, from 22.67% on cheap-planter to 59.60% on hybrid-chopper.
The strict action-audit SHA-256 is
`d6ea84c1d610eff4343ae35a0ad06b34ea9e6401a7ddd0bed18d464ca2d68d41`.

## Multilevel interpretation and decision

- **Command level:** the original actor already chose the recovery MOVE verb 99.921% of the time
  but the exact source only 7.147%.  The confirmed PPO actor preserves 99.93% verb agreement while
  raising exact prospective source choice to 45.19%; this directly repairs the diagnosed spatial
  bottleneck.
- **Closed-loop level:** the repair survives repeated depletion, a renewable three-worker rival,
  and three crop destructions while retaining 97.65% whole-task success.
- **Generalization level:** prospective overall success is 0.25 percentage points above the 500-seed
  development result, and the worst-recipe floor rises from 90.16% to 95.67%.  Recovery exact
  agreement is essentially unchanged at 45.42% development versus 45.19% prospective.
- **Goal level:** this confirms D11 learning evidence, not live Legend transfer.  The checkpoint is
  still a Python/Torch research model and has not passed compact export, implementation parity,
  Levels 1--4 regression, layered field evaluation, the 100k source constraint, or Arena testing.

**Decision:** accept the D11 learned checkpoint as the sole deployment-qualification input.  Next
freeze and execute compact export, exact Rust/Python logit and action parity, source-size
accounting, Levels 1--4 regression, and layered field evaluation.  Arena submission remains a
separate user-authorized action.
