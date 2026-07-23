# D73a four-mode recurrent PPO signal result (2026-07-21)

## Verdict

**Reject and close this recurrent PPO recipe.** The recurrent actor learns a deterministic,
history-dependent four-mode policy and passes every mechanics, optimization-signal, determinism,
crop, workforce, and throughput gate. Its single frozen policy nevertheless loses **1.758 mean
margin** to exact balanced on the prospective 256-task panel and regresses three opponent
families, including `silver_boss` by **-55.125**.

The checkpoint is not a candidate. Per the frozen branch, do not extend the budget, tune the
initialization/seed/width/rate/entropy/truncation, select an intermediate state, or retry PPO.
Move to paired online option values so that productive sacrifice and opponent suppression receive
an explicit same-state contrast.

## Environment and mechanics

The new 72-feature ordinary-action ABI first matches the established D62 environment exactly on
all 4 modes x 16 tasks:

- 64/64 terminal comparisons exact in scores, workers, trains, crops, action/state hashes, and
  failure counters;
- independent repeat exact;
- maximum reward-telescoping error `7.2941e-6`.

The frozen PPO run then completes exactly 131,072 transitions and 32 updates:

| Measure | Result | Gate |
|---|---:|---:|
| Completed episodes | 1,900 | at least 1,500 |
| Crop-creating training episodes | 1,900/1,900 | descriptive pass |
| Unlocked transitions | 97,500 | descriptive |
| Unlocked action rates B/H/R/F | 31.41% / 27.99% / 9.85% / 30.75% | each at least 2% |
| Illegal actions | 0 | zero |
| Direct/provenance/deposit failures | 0 / 0 / 0 | zero |
| Maximum training reward error | `1.0937e-5` | below `1e-4` |
| Throughput | 569.76 transitions/s | at least 400 |
| Effective CPU use | 17.18 cores | at least 12 |

Both 768-row evaluation matrices are byte-identical at SHA-256
`f94b25ff6faa7d14e7aede5a66e2e49f034dfb468408cd0de9b2230ec74e2a13`.
Every evaluated policy has 256/256 crop creation and zero mechanical failures. Final worker-three
reach is 242/256 = 94.53%.

## Optimization signal

All five signal gates pass:

- actor L2 drift: **0.5854**;
- frozen probe actions changed: **272/512**;
- final probe modes: balanced, harvest, fell (three modes);
- final evaluation uses all four modes; and
- non-balanced choices occupy **60.26%** of unlocked evaluation boundaries.

The final policy gains **+17.152 mean margin** over the reconstructed untrained recurrent actor,
strictly improving 149/256 tasks. Recurrence and PPO therefore produce genuine policy movement;
the failure is not D62's prior-induced deterministic inertia.

## Prospective fixed-policy value

| Policy | Mean margin | Own score | Opponent score | Worker three | Crops |
|---|---:|---:|---:|---:|---:|
| Balanced | +57.457 | 233.969 | 176.512 | 94.53% | 100% |
| Untrained recurrent | +38.547 | 215.277 | 176.730 | 94.53% | 100% |
| Final recurrent | +55.699 | 192.230 | 136.531 | 94.53% | 100% |

Against balanced, the final policy:

- changes mean margin by **-1.758**, failing the required +5;
- improves 131/256 = 51.17%, passing breadth but with 107 regressions and 18 ties;
- reduces opponent score by **39.980** but reduces own score by **41.738**;
- improves `compact_gold`, `gold_adaptive`, `legend_balanced`, `mybot`, and
  `norx_native_three` by +7.000 to +21.531;
- regresses `resident` by -9.500, `script_boss` by -4.281, and `silver_boss` by -55.125.

The actor's dominant learned intervention is `fell` (6,248 of 11,148 unlocked final decisions),
while harvest and renew appear only 275 and 195 times. PPO learned broad opponent suppression but
did not price the displaced productive economy precisely enough. The +17 gain over initialization
does not rescue a policy below balanced.

## Multilevel interpretation

1. **Infrastructure:** the 72-feature recurrent ABI, hidden resets, sequence PPO update, reward,
   masks, parallelism, and deterministic evaluator are validated and reusable.
2. **Representation:** a small recurrent actor can express and learn state-dependent action timing;
   D72's headroom was not merely a random-oracle artifact.
3. **Credit:** undifferentiated on-policy margin increments favor a suppression-heavy trajectory.
   They do not expose the same-state opportunity cost of replacing productive work with felling.
4. **Generalization:** average optimization hides opponent-specific failure. Five positive families
   coexist with a single -55 family, so a longer identical run is not an evidence-based fix.
5. **Deployment:** no local program or Arena resident was updated. Live submission `41015603`,
   agent `6561795`, remains the unchanged 62,725-byte source.

## Next experiment

Freeze paired online option-value collection on fresh balanced trajectories. At each selected
natural boundary, compare all four legal modes from the same reconstructed state, then return to
the same balanced continuation. First require broad, crop-safe one-deviation headroom and
learnable grouped ranking. Only then may one fixed selector be evaluated prospectively. This is
the predeclared D73 failure branch, not another PPO retry.

## Artifacts

- protocol: `d73a-four-mode-recurrent-ppo-signal-protocol-2026-07-21.md`;
- parity: `d73a-opening-recurrent-environment-parity.json`;
- checkpoint: `d73a-four-mode-recurrent-ppo-final.pt`, SHA-256
  `7ef81f78b08fa0bc2cc9d218c48435f2a5fe37f5f6606ca4635bb6678e42fd42`;
- repeated evaluation: `d73a-four-mode-recurrent-ppo-evaluation-a.tsv` and
  `d73a-four-mode-recurrent-ppo-evaluation-b.tsv`;
- machine result: `d73a-four-mode-recurrent-ppo-signal-result.json`;
- wall-clock sidecar: `d73a-four-mode-recurrent-ppo-time.txt`.
