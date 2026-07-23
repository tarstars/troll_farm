# Curriculum Level 4 discovery result — 2026-07-19

## Verdict

Pass.  The seed-83 transfer clone, four-million-decision PPO run, exact-bank functional
evaluation, and strict recipe-by-role action audit all clear their frozen prospective gates.
Discovery therefore authorizes exactly one independent seed-89 confirmation.  It does not yet
accept Level 4, alter the resident, establish opponent transfer, or authorize a submission.

The result is materially stronger than merely learning one fixed worker recipe: one shared actor
conditions on all eight requested first-worker recipes while jointly controlling the starter
farmer and trained worker through crop creation, renewable harvest, and post-training scoring.

## Functional result

The deterministic final actor was evaluated once on exact seeds 2,015,000--2,016,999 (2,000
episodes, 240 referee turns).  Teacher and random-legal controls were generated and hashed before
any Level-4 learning labels were consumed.

| Metric | Discovery PPO | Frozen gate | Margin |
|---|---:|---:|---:|
| Overall success | 1,988/2,000 (99.40%) | 88% | +11.40 pp |
| Nontrivial success | 1,128/1,135 (99.38%) | 83% | +16.38 pp |
| Worst recipe success | 98.82% | 75% | +23.82 pp |
| Worst height success | 99.00% | 75% | +24.00 pp |
| Tracked crop created | 99.50% | 90% | +9.50 pp |
| Renewable harvest | 99.50% | 87% | +12.50 pp |
| Advantage over random legal | +99.40 pp | >=50 pp | +49.40 pp |
| Paired teacher median delay | 0 turns | <=35 | 35 turns |

The recipe rates are 98.82% cheap planter, 99.62% compact farmer, 100% balanced producer,
99.21% harvest producer, 99.20% Level-1 anchor, 100% lean chopper, 99.21% standard chopper,
and 99.13% hybrid chopper.  Height buckets range from 99.00% to 99.80%.  Median
training/completion turns are 12/51 and median post-training score gain is 15.

Stage A had already passed at one million decisions with 99.30% overall success, 98.43% worst
recipe, and 98.80% worst height.  Continuing the preregistered run to four million decisions
improved overall success by 0.10 percentage points and reduced median completion from 52 to 51.

## Strict recipe-role action audit

The audit replayed the final checkpoint on the same exact bank and scored exact spatial commands
only at productive post-training teacher opportunities.  Waiting on the tracked unripe BANANA
crop was the sole exemption.

| Role/metric | Discovery PPO | Frozen gate | Margin |
|---|---:|---:|---:|
| Chopper exact productive choice | 95.97% | >=55% | +40.97 pp |
| Farmer exact productive choice | 90.54% | >=55% | +35.54 pp |
| Worst nonempty recipe-role cell | 86.10% | >=35% | +51.10 pp |
| Chopper productive verb | 99.73% | diagnostic | — |
| Farmer productive verb | 96.77% | diagnostic | — |
| Combined unjustified current waits | 252 | <=30,000 | 29,748 |

The weakest recipe-role cell is the standard-chopper recipe's farmer at 86.10%, still far above
the prospective floor.  There are 38,519 justified farmer waits on the tracked unripe crop, 227
unjustified farmer waits, and 25 unjustified chopper waits.  No recipe or role collapse is hidden
by the aggregate score.

## Learning-path evidence

The accepted Level-3 actor transferred zero-shot at 90.25% overall but exposed two composition
deficits: cheap planter at 67.06% and harvest producer at 70.36%.  The frozen 800,000-label clone
raised overall success to 97.80% and its recipe floor to 93.33%.  PPO then raised them to 99.40%
and 98.82%, respectively.  This progression supports the intended hypothesis: target channels
already carried useful recipe information, while online imitation plus masked PPO repaired the
two out-of-distribution recipe/renewable combinations.

Across four million PPO auxiliary labels, only 20 (0.0005%) were undefined in learner-diverged
states and were skipped under the frozen legal-label rule.  All reported losses remained finite.
Training consumed 4,092.77 wall seconds and 57,091.06 process CPU-seconds, equivalent to 69.75%
of the 20-logical-CPU host.  Final evaluation processed 229,900 decisions in 20.86 seconds.

## Reproducibility anchors

- frozen discovery protocol:
  `aef6cdd612d57423509f057b5aceaee669af43771b658cb369091b7befaa7418`;
- teacher control:
  `168eb4200be12345a9d7a28de76d6424612153b1c75f8b3923db853f1ddf257a`;
- random-legal control:
  `e5f52fe08177b53da23961b37800985a3585df54a7b735fe1d17f70c17450289`;
- transfer-clone checkpoint:
  `6ba4daa6a871103776d205046e11f9fc5a8381eba1807d93d515dec148c88259`;
- final PPO checkpoint:
  `a318c07268e03ce9e12ddadd021bed050d68e3f3bd50af213925fa3f0cdd01f2`;
- exact final evaluation:
  `3693a02a5cc47f135df0d352c09726effa4df87f202ddb95b09e1126c7be3142`;
- complete training summary:
  `4adf46c8088b85791095eb3654dbd3b8c6a2a9ba2917e32d74d4d7eef0f19774`;
- strict action audit:
  `a180cdfae9f2e799bf652bb352bc204d231e7a56e8d7ebec968989a1ac7265b6`.

## Next execution

Run exactly one independent confirmation from the accepted Level-3 checkpoint, not from this
Level-4 discovery actor.  Freeze its full protocol before controls or labels; use seed 89,
disjoint clone/PPO streams 6,800,000/6,900,000, and exact seeds 2,017,000--2,018,999.  Only a
functional and recipe-role action pass on that bank accepts Level 4.
