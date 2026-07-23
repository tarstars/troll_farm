# D92 factory dual-value opponent-crop targeting

Date: 2026-07-21  
Status: rejected on the consumed D89 development panel; no fresh maps opened

## Question

D89 validated complete two-worker renewable production but increased the rival's own crop output.
D92 asks whether the already-frozen ETA-6 dual-value rule can recover that competitive pressure
while the starter keeps the banana factory running. The test uses only maps `9,914,032--9,914,047`,
which D89 already consumed, and compares each treatment with exact D89 and resident controls in
both seats against all eight local opponent families.

Two causal compositions were tested:

1. **Broad dual value:** apply the rule to the resident-derived starter and the trained wood role.
2. **Trained-only dual value:** leave the starter inner policy exactly unchanged and double the
   trained worker's target value only for a known opponent-created crop reachable within ETA 6.

The second composition is the intended isolation. Source tests prove that its constructor does not
modify the starter policy.

## Results

| Treatment versus D89 | Changed tasks | Mean margin | 95% normal CI | Improve / tie / regress | p10 | Worst |
|---|---:|---:|---:|---:|---:|---:|
| Broad dual value | 159 / 256 | -6.371 | [-12.337, -0.405] | 69 / 104 / 83 | -70 | -157 |
| Trained-only dual value | 90 / 256 | -5.609 | [-7.350, -3.869] | 12 / 183 / 61 | -28 | -64 |

Broad targeting suppresses `13.883` opponent score per task, including `31.160` score-equivalent
from opponent-created sources, but destroys `20.254` own score. It therefore proves that the
target rule can interrupt the rival loop, while also proving that applying it to the productive
starter costs more than it denies.

The trained-only isolation is more decisive. It produces 898 opponent-crop target selections,
732 more than D89's incidental 166, yet opponent score changes by **+0.188**, not downward. Own
score falls `5.422`, wood falls `1.355`, and margin falls `5.609`. The 90 changed tasks contain only
12 improvements and 61 regressions. Family margin deltas versus D89 are:

| Opponent family | Mean margin delta |
|---|---:|
| compact_gold | -9.344 |
| gold_adaptive | -19.281 |
| gold_elite | -9.344 |
| mybot | -2.750 |
| printer_bot | -2.219 |
| sched_bot | +0.000 |
| script_boss | -1.125 |
| silver_boss | -0.812 |

Versus resident, trained-only remains a productive but unsafe D89 descendant: `+73.832` mean
margin, p10 `-76`, worst `-251`, and Gold-adaptive family mean `-26.219`.

## Verdict

Reject D92 without prospective testing. The exact dual-value composition is closed; do not retune
its ETA, multiplier, or target threshold on these maps.

The causal distinction is useful:

- a broad controller can suppress rival-created production, but only by sacrificing even more of
  our production;
- the trained worker reaches many nominal rival crops but is too late or too low-leverage to alter
  the rival's score, so its existing productive target order dominates.

The next experiment must change capacity or timing, not target weights. Audit whether D89's
complete renewable factory creates a real, repeatable window to fund and deploy worker three while
the existing two roles remain productive. Instrument affordability, shack occupancy, bill
deficits, and the first legal training window on the consumed panel before testing any TRAIN
intervention.

## Artifacts

- `d92a-factory-dual-value-development-9914032-9914047.tsv` — broad three-profile run,
  SHA-256 `15a0315d20d7564146ae156a0599b5371b40f05c6dd52b00344ef229d86dc46e`.
- `d92b-factory-trained-dual-value-development-9914032-9914047.tsv` — four-profile isolated run,
  SHA-256 `9164d7cb847a0a024a0886e69983d7c44fa6e34f13f51650436bdb4f1fb41e31`.
- `rust/src/bin/yamo_orchard_live.rs` — disabled-by-default treatment constructors and telemetry.
- `rust/src/bin/ownership_aware_complete_economy.rs` — paired causal harness.

