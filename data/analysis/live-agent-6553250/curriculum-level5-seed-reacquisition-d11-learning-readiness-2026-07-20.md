# Curriculum Level 5 D11 learning readiness — 2026-07-20

## Verdict

**Ready for the single frozen behavior clone.**  Exact development controls on seeds
6,500--6,999 validate the task, and the unchanged actor independently reproduces the D11 deficit.
All three artifacts were completed and hashed before any training-stream label was consumed.

## Exact development controls

| Measure | Teacher | Random legal | Fixed actor |
|---|---:|---:|---:|
| Overall success | **99.40%** | **0%** | **80.00%** |
| Nontrivial success | **98.99%** | 0% | **80.07%** |
| Worst recipe | **95.08%** | 0% | **74.67%** |
| Worst height | **99.19%** | 0% | **79.53%** |
| Terminal crop | **99.80%** | 1.40% | **80.80%** |
| Renewable harvest | **99.40%** | 0% | **84.60%** |
| First / third-worker training | **100% / 97.80%** | 100% / 99.40% | **100% / 98.80%** |
| Fresh first / second receipt | **100% / 100%** | 100% / 100% | **100% / 100%** |
| Chopper / feeder productivity | **100% / 95.00%** | 100% / 95.20% | **100% / 95.80%** |
| Rival crop / own renewable harvest | **100% / 91.20%** | 100% / 93.80% | **100% / 92.40%** |
| At least one / two / three destructions | **99.80% / 98.40% / 96.60%** | 21.40% / 2.40% / 0.20% | **99.40% / 97.20% / 86.00%** |
| Maximum destructions / workers | **3 / 3** | 3 / 3 | **3 / 3** |
| Illegal selections | **0** | **0** | policy-masked |

Teacher success is never earlier than turn 180.  Every frozen teacher floor passes with margin,
and random legal remains fully discriminative.  The actor still passes every opponent-mechanism
gate while failing the preregistered learning outcome floors, excluding an easier bank or pressure
avoidance as explanations.

The actor result also agrees with the prior 6,000--6,499 bank: 80.00% versus 79.40% overall,
74.67% versus 70.00% worst recipe, and 84.60% versus 83.60% renewable harvest.  No distribution
shift large enough to erase the learning question is present.

## Verified plumbing

- D11 is selectable in teacher generation, deterministic evaluation, behavior cloning, and PPO.
- PPO evaluation now reports one/two/three-destruction rates and the destruction cap.
- The Level-5 functional gate preserves both player outcomes and every recurrent-opponent
  mechanism.
- The strict action audit measures empty-seed recovery exact-source and verb agreement globally
  and per recipe.
- Python byte-compilation and 40 focused PPO/BC/audit/Level-5 tests pass.

## Frozen execution

Run exactly one clone from the accepted checkpoint with model seed 131, teacher stream 7,100,000,
800,000 decisions, and the schedule in the frozen protocol.  Evaluate exactly once on this bank.
Only a functional pass opens the strict action audit.  A full pass skips PPO/YT; any failed final
gate opens the conditional PPO benchmark without schedule tuning.

## Reproducibility anchors

- learning protocol:
  `48922c1f7fe4d20936f3d6c1e8aed6b6040c9eb900e231d109fd931057fc368b`;
- teacher control:
  `0089e4b1be5d8ef1e9fe72736c28426a1889c6b5ad8f2f08efea22757a3cbf4e`;
- random control:
  `db6d3edd059ea8c33fcee7883c93955b25b8a34518bf9b7101220db5a00469b8`;
- fixed actor:
  `4695a0ff2929964f9ee0acf8ca5d4670525c07b5d4f54d4b32eb2dd499eae468`;
- PPO/evaluation driver:
  `c1b0986563da20614f5148d8a26254c4227d382c66f6e846b848768a6beb032e`;
- behavior-clone driver:
  `ad1c13bb46e17335f2b0cb431ea94aa47a6e10364b9d221380739a8029736f89`;
- action-audit driver:
  `dccaa98da556e693d502d052d4879945b41adf2a8efdae923990eea16de41277`;
- focused PPO tests:
  `c1f79e0482e7ed0fb7a1a2d3ee542889144df534df97c3f29d9c1fc6657a0b0c`;
- accepted initial checkpoint:
  `b5daae9ecf81e52ebf35f9bcb9d0eb75110abf0cc5da570f136c5505d96c4882`; and
- teacher stream 7,100,000, unopened at readiness freeze.
