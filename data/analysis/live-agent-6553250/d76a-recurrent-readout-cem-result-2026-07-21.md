# D76a recurrent-readout whole-policy CEM result (2026-07-21)

## Verdict

**Reject and close the fixed-reservoir readout CEM.** Whole-episode search repeatedly discovers
profitable individual policies, but its predeclared final distribution mean remains on the
balanced argmax plateau. On 256 untouched validation tasks it chooses balanced at all **17,230**
unlocked decisions and is exactly tied with balanced in every game.

The final readout is not a candidate. Do not select generation 7/9 elites, extend the search,
change CEM averaging, or reuse validation maps. The next whole-policy branch must evolve the
recurrent representation itself or use a qualitatively different controller.

## Search integrity

The corrected independent audit reconstructs, from seeds and raw populations:

- all ten 33-member recurrent populations plus balanced;
- all 10 x 2,176 complete generation rows;
- every antithetic sample, elite ranking, mean update, standard-deviation update, and hash;
- the fixed 1,020-parameter reservoir and 52-parameter readout serialization; and
- the final generation-ten mean.

All reconstruction, task, command, provenance, deposit, feature/recurrent finiteness, mask,
action-count, crop, and reward checks pass. The run takes 572.54 seconds at 19.05 effective cores.
Both 768-row validation matrices are byte-identical at SHA-256
`8de5d3a474d8a814bbd8356baf26a511d66fb435af401fc87160b6463e35f8c1`.
The zero-readout initial policy matches balanced exactly in all 256 tasks.

The first analysis artifact falsely quarantined mechanics because it compared once-rounded
reservoir bits with the writer's final complete-vector normalization. No experiment was rerun.
The corrected analyzer uses the actual serialization boundary and a new regression test; the
correction is recorded explicitly.

## Search dynamics

The search has real sample-level signal:

| Generation | Best sample mean delta | Strict wins | Own-score delta | Worst family |
|---:|---:|---:|---:|---:|
| 5 | +2.641 | 21.88% | +2.047 | 0.000 |
| 6 | +6.781 | 18.75% | +6.625 | -0.250 |
| 7 | **+16.891** | **70.31%** | +7.531 | -0.500 |
| 9 | +9.219 | 43.75% | +6.734 | -1.250 |

Generation 7's sample improves seven opponent families and uses fell on 1,196 of 2,895 unlocked
decisions. Generation 9 also improves six families. These are consumed training members, not
prospective candidates.

The distribution mean behaves differently. Its parameter L2 distance grows to **1.965**, yet it
mostly remains exact balanced: generation-ten mean makes only six fell choices on its 64-task
batch. Averaging several elite readouts cancels their different decision directions; with hard
argmax, parameter movement does not imply behavioral movement.

Generation 4 also exposes a protocol weakness without invalidating execution: balanced itself
reaches worker three in only 79.69% on that hard four-map batch, so every population member is
safety-ineligible and secondary ranking drives that update. The frozen rule was preserved rather
than changed mid-search.

## Prospective validation

| Measure | Final mean | Frozen gate |
|---|---:|---:|
| Non-balanced unlocked decisions | **0/17,230** | at least 20% — **fail** |
| Distinct non-balanced modes | 0 | at least 2 — **fail** |
| Mean margin delta | 0.000 | at least +5 — **fail** |
| Strict improvements | 0/256 | at least 55% — **fail** |
| Positive opponent families | 0/8 | at least 6 — **fail** |
| Mean own-score delta | 0.000 | at least -10 |
| Paired p10 delta | 0.000 | at least -60 |
| Worker-three reach | 91.02% | at least 90% |
| Crop creation | 100% | exactly 100% |

Every task ties, so the value failure is wholly explained by activity failure rather than a bad
active policy. The final network's hidden state is active (maximum magnitude 0.999998), but its
readout never changes the legal argmax.

## Multilevel interpretation

1. **Controller class:** fixed random recurrence plus a linear readout contains useful sampled
   behaviors, but one averaged readout is a poor representative under discrete argmax.
2. **Optimizer:** whole-episode objectives avoid PPO's own-versus-suppression credit error; strong
   samples improve own score as well as margin. CEM mean aggregation loses that signal.
3. **Safety:** absolute per-batch worker gates can make every policy ineligible when the paired
   balanced batch is itself hard. Future search should use paired degradation, not an absolute
   development threshold.
4. **Selection:** a lineage/tournament optimizer may retain actual policies rather than average
   incompatible readouts, but it must be preregistered on fresh maps and evolve recurrence to avoid
   reopening this closed fixed-reservoir recipe.
5. **Deployment:** no program was exported or submitted. The Arena resident remains the unchanged
   62,725-byte submission `41015603` / agent `6561795`.

## Next experiment

Freeze a full recurrent `(mu + lambda)` lineage search on fresh maps. Evolve reservoir and readout
weights together, retain actual policies through preregistered tournament selection, use paired
worker-three degradation for development safety, and prospectively evaluate only the final lineage
champion. This is a different representation/optimizer, not selection of D76's favorable elites.

## Artifacts

- protocol: `d76a-recurrent-readout-cem-protocol-2026-07-21.md`;
- search log SHA-256:
  `08df58b6080bca1dd2341d0d7ccb771de981f7bd7b2adbc8937ce4cdab2896ee`;
- final population SHA-256:
  `2c8bd3347d5af1cd3818a61a2a5db7e805ad6952a1bf12a083d260c3a3be81f5`;
- repeated validation SHA-256:
  `8de5d3a474d8a814bbd8356baf26a511d66fb435af401fc87160b6463e35f8c1`;
- corrected machine result: `d76a-recurrent-readout-cem-result-v2.json`, SHA-256
  `911eeb42cbb49d6a150542749d1c4d47a9d84d844b9d0dea0d4bf29de26ebaae`;
- analysis correction: `d76a-recurrent-readout-cem-analysis-correction.json`.
