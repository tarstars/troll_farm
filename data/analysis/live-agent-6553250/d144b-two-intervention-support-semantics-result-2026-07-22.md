# D144a/b two-intervention Monte Carlo — result

Date: 2026-07-22  
Decision: **open a separately frozen two-intervention trajectory teacher and policy fit**

## Outcome

The sampled two-intervention oracle passes every prospective value and relative-safety gate on
unused seeds `9,844,128--9,844,135`:

| Measure | Exact one use | Combined one/two use | Increment | Gate |
|---|---:|---:|---:|---:|
| Mean margin gain over D40 | +38.438 | +42.586 | **+4.148** | >= +3.0 |
| Tasks strictly improved beyond one use | — | **57/128 = 44.53%** | — | >= 20% |
| Positive opponent families | — | **8/8** | — | >= 6 |
| Worst family increment | — | **+1.750** | — | >= 0 |
| Crop creation | 100% | **100%** | 0 new failures | no regression |
| Worker-three reach | 87.50% | **87.50%** | 0 pp | >= -5 pp |

The increment comes mainly from own-score production (`+3.602`) plus modest opponent suppression
(`-0.547`). Family increments are compact Gold `+3.188`, adaptive Gold `+6.188`, balanced
`+4.625`, mybot `+3.625`, Norx `+1.750`, resident `+3.750`, script `+4.750`, and silver `+5.313`.

This is representation evidence, not a deployable candidate. It demonstrates that the plateau is
specific to one-use control, not the q6 proposal interface itself.

## Reproducibility and capacity

YT operation `d29f4ba8-8e972d8c-42e03e8-c28f4f16` completed 4/4 jobs with zero failures under
`//home/delivery_ml/research/tarstars/troll_farm`. The two complete 16,384-episode matrices are
byte-identical after reconstruction at SHA-256 `cbeb74ff...`. Each has exactly 128 control, 2,048
single-mode, and 14,208 double-mode episodes.

The MC jobs completed in 1,543.88 and 1,595.75 seconds at 10.61 and 10.27 episodes/s. They produced
identical intervention counts: 2,769 zero, 4,758 one, and 8,857 two. Thus 62.34% of double-mode
episodes reach two interventions, well above the frozen 40% gate. The exact jobs collect 11,046
arms plus 128 baselines at 25.08 and 18.38 arms/s. Every control and all 1,721 selected single
episodes exactly match the dense D112 comparator; all mapping, schedule, selection-hash, cap,
reward, feature, accounting, provenance, and failure gates pass.

The first operation `ada44f3b-2c9a7e95-42e03e8-501288eb` produced zero rows because worker Python
lacked NumPy. Repair 1 added only a pinned 19.1 MB Python 3.10 NumPy runtime and reproduced the
excluded smoke bytes before the new operation. It did not change simulation or scientific gates.

## Support-semantics repair

D144a correctly stopped before value interpretation because 118/128 tasks had a two-use sample,
below its raw 95% task gate. Exact baselines prove those are exactly all 118 tasks with any q6
boundary; the other ten are structurally forced control. D144b was frozen before opening target
value and replaced only the impossible denominator with stronger mechanics:

- 118/118 eligible tasks have at least one two-intervention sample;
- all 1,280 episodes belonging to the ten zero-boundary tasks execute zero interventions and
  exactly reproduce D112 control; and
- every other D144 mechanics gate remains true.

The repaired value analysis then passes. Unsupported tasks remain in the 128-task value and safety
denominators, so the final increment is conservative rather than eligibility-filtered.

## Next experiment

Do not submit or spend D126/final validation yet. First decompose the already-frozen MC population
without new simulation:

1. measure incremental-oracle saturation versus 16/32/64/111 double replicas and independent
   replica partitions;
2. compare each winning sequence with its exact first intervention alone to isolate conditional
   second-move value;
3. describe winning first/second boundary and action diversity; and
4. use those results to freeze either a selected-trajectory replay/feature teacher or a broader YT
   corpus, with held-block policy selection before any veto or Arena action.

## Frozen evidence

- D144a result SHA-256: `a13375a38a6e0ecf68b9d14fa5241790f0d45c632bd1e6299ff155b0391ca3aa`
- D144b lock SHA-256: `8ec8f6bb4cd49ae9e7b0778f9c92d2940208959f725c59e640225d17c31fdf2d`
- D144b result SHA-256: `0afef524f4f037dc8aa8e3603c5e549df7d799f09637562d51ca21f7b17e61ae`
- repaired download SHA-256: `d5c277469bd7ab790ccdf72929d8262ff745e65fa0fff3cba134651de65f4928`
- exact arms/baselines SHA-256: `801fd353...` / `928eaba0...`

