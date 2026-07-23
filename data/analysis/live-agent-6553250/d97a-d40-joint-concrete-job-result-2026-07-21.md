# D97a D40 joint concrete-job continuation — result

Date: 2026-07-21  
Status: full pass; concrete joint-assignment representation validated

## Verdict

D97 passes every frozen integrity, support, safety, causal-value, incremental-value, and breadth
gate. Freeze the concrete joint-assignment executor and open the preregistered next stage: a
bounded whole-game function-class preflight with exact D40 fallback. Do not train or construct a
candidate yet.

This is the clearest representation advance after the four-mode plateau. Across all 256 tasks,
including zero gain for sixteen tasks without an eligible root, the joint-or-control hindsight
oracle gains `+36.852` terminal margin over exact D40. At the 240 roots, it strictly improves
230 = 95.83%. More importantly, joint assignment adds `+9.208` mean margin over the best
single-worker-or-control continuation and strictly beats that single-worker oracle in 160/240 =
66.67% of roots. The effect is coordination value, not just a larger menu of individual actions.

## Outcome-blind support lock

The manifest was generated and hashed before any D97 arm reached terminal state. It retained the
first preregistered natural batch boundary in 240/256 tasks and enumerated:

| Arm class | Count |
|---|---:|
| Exact control | 240 |
| First-worker-only | 1,741 |
| Second-worker-only | 1,160 |
| Joint two-worker | 9,342 |
| Total | 12,483 |

Every root exposes fell, renewable, and mine alternatives. Natural, own, and opponent provenance
all appear in both seats. The smallest opponent family has 26 roots, above the frozen 24 floor.
There are zero duplicate arm ids and zero nonteacher options that fell the final live own crop.

## Integrity and reproducibility

Two complete 20-worker runs independently evaluate 256 D40 baselines and all 12,483 arms. The
arm matrices are byte-identical with SHA-256
`c6ee144a4c89d4a504d7c7bf356628a7b3fc506b1ba29b991c1cc0caa0b08d33`; the baseline matrices are
byte-identical with SHA-256
`8936d7007074a240f21073aea4c5fa43851093cfd90e1827a4fe4370609b40b6`.

Run A evaluates baselines in 49.822 seconds and arms in 290.138 seconds at 43.024 full
continuations/s. Run B takes 47.989 and 279.625 seconds at 44.642/s. All 240 control arms reproduce
their uninterrupted D40 task exactly on every terminal, action-plane, action-hash, and state-hash
field.

The evaluator reconstructs every root, candidate observation, catalog, action, resulting second
state, reservation-filtered second catalog, and second action from the immutable manifest. Across
both baselines and arms there are:

- zero illegal commands, provenance failures, deposit-prediction failures, or worker-cap failures;
- zero reward, margin, action-plane, manifest-mirror, or control-parity failures;
- zero nonfinite values; and
- exact action/candidate/catalog hashes at both assignment positions.

The focused Rust tests pass 2/2. Existing unrelated library warnings remain unchanged.

## Causal value

The joint-or-control oracle passes every whole-game gate:

| Metric | Result | Required |
|---|---:|---:|
| Mean margin delta over D40, all tasks | +36.852 | >=+15 |
| Strict rooted improvements | 230/240 = 95.83% | >=55% |
| Mean own-score delta | +22.812 | >=0 |
| Mean opponent-score delta | -14.039 | <=0 |
| Worst opponent-family gain | +22.562 | >=+3 |
| Crop creation | 256/256 | 100% |
| Worker-three rate | 91.41% | within 5 points of D40 |

Worker-three reach is exactly equal to D40's 91.41%, so value does not come from breaking funding
or exchanging the workforce ladder for terminal score. Every opponent family is strongly positive:
`+22.562` resident, `+42.531` Gold adaptive, `+47.781` compact Gold, `+41.281` native Norxondor,
`+52.094` Legend balanced, `+30.531` MyBot, `+29.312` ScriptBoss, and `+28.719` SilverBoss.

The best single-worker continuation is itself strong at `+28.219` over D40 across all tasks and
strictly improves 217 tasks. The joint representation still clears the required incremental test:

| Joint versus best single, rooted tasks | Result |
|---|---:|
| Mean incremental margin | +9.208 |
| Strict joint improvements | 160 |
| Ties | 14 |
| Regressions | 66 |
| Positive delta sum | +2,758 |
| Negative delta sum | -548 |

This asymmetry matters. A policy that independently chooses each worker's locally best job cannot
recover the joint oracle; reservations, target provenance, and the second worker's live candidate
set create real interaction value.

## Breadth

The oracle selects a joint arm in 231 roots, control in nine, and exact D40 in the sixteen tasks
without roots. Winning joint arms use all four productive job kinds (`fell`, `harvest`, `renew`,
`mine`), all three observed provenance classes, both reversed role orders, and all eight opponent
families.

Two exact role tuples independently reach at least ten oracle wins:

- `harvest:natural / fell:natural`: 14; and
- `fell:own / fell:natural`: 10.

Many other tuples contribute smaller counts. This rejects a post-result two-rule scheduler: the
value surface is broad and target-specific even though two common patterns are visible. Every arm
and winning tuple remains hindsight-only and permanently unselectable.

## Interpretation and next branch

D96 supplied the right state factorization but the wrong action abstraction. D97 changes no TRAIN,
deficit, evacuation, transaction, or persistence mechanics; it only lets the first assignment
reserve a concrete target and lets the second worker choose from the resulting collision-safe job
set. That one change recovers both production and suppression and provides value beyond either
worker alone.

The next stage must test the representation as a complete bounded controller rather than fit D97
labels. Freeze a D98 population with exact D40 fallback, the same target-aware catalogs, and a
small preregistered per-episode assignment budget. Matched one-intervention and repeated variants
must determine whether repeated closed-loop use adds headroom without D79-style global trajectory
replacement. Random policies and hindsight oracles remain unselectable. Only a safe, active,
incrementally valuable whole-game function class may open a learning-signal experiment.

No D97 result authorizes a selector, PPO, CEM, imitation, candidate, TestSession, submission,
Arena action, or resident replacement.

## Reproducibility anchors

- protocol SHA-256:
  `157a18d39ba49bf7a7b76080a0f16e8df3c622d93d6f98a22127f779ee5dd0e3`;
- manifest-lock SHA-256:
  `e9d7907d1a9d3c5aa114fb705423ae09f83071fab3bd424fa153c2b9ff301903`;
- manifest SHA-256:
  `ed5a6ffeb73032006fed7e08518e82c6cf549e2b8f24f7798cbceb82837c157e`;
- manifest generator SHA-256:
  `f39748d916be4634b9c2e48dc2e0460fbf3d7c56985d4339786b2b39f2276b23`;
- evaluator SHA-256:
  `e7dd8a8d743c320548897ad264a515223fdb40e05571e01569654aeafafb68e4`;
- analyzer SHA-256:
  `03dbdcea8af1c6ed81c5ecef0fa4fb33d6c7634a9423a1fc730305454c96bceb`;
- machine result SHA-256:
  `03cd5f6f32e5f5a19fd18e69fd4714864b259351c6ce6e2a9274a7f366f33822`.

Artifacts:

- `d97a-d40-joint-concrete-job-manifest-9820000-9820015.tsv`;
- `d97a-d40-joint-concrete-job-{arms,baselines}-{a,b}-9820000-9820015.tsv`;
- `d97a-d40-joint-concrete-job-result.json`;
- `rust/src/bin/d97_joint_concrete_manifest.rs`;
- `rust/src/bin/d97_joint_concrete_continuations.rs`; and
- `cgauto/analyze_d97a_joint_concrete_jobs.py`.
