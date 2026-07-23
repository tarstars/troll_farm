# D161a same-panel resident-dominance audit — result

Date: 2026-07-23  
Decision: **close the D40/q6 substrate for resident competition**

## Integrity

D161 evaluates all 1,024 already-consumed D148 tasks: maps `9,844,136--9,844,199`, two seats,
and eight opponent families. The unchanged D102 runner produced 2,048 sorted resident/D40 rows
with one worker and 20 workers. Both files are byte-identical at SHA-256
`144d8f880be8eb58e19e1ef0a3547c04280dac8644340628b60101c1c47c988b`.

Every shared D40 score, return, workforce, crop, mechanics, action-hash, and state-hash field
matches the D148 control. The 503 MB one-use arm corpus reconstructs exactly: 88,469 arms, 921
tasks with positive boundary count, and 103 legitimate zero-boundary D40 fallbacks. The 66,560-row
priority-pair population, 909-row manifest, replay terminals, 909 targets, 388 active targets, and
all frozen D148b transfer aggregates reproduce exactly. Every integrity gate passes.

The completed YT operation recorded by D148 uses the corrected canonical root
`//home/delivery_ml/research/tarstars/troll_farm`. D161 itself makes zero YT requests and zero
platform requests. Reserved maps `9,844,200--9,844,215` remain untouched.

Focused verification passes 9/9 Python tests and 3/3 unchanged D102 Rust runner tests.

## Same-panel result

| Policy or hindsight envelope | Mean margin vs resident | 95% map-cluster interval | Improve / regress | Positive families | Worst family | Catastrophes | Negative-margin mass |
|---|---:|---:|---:|---:|---:|---:|---:|
| Exact D40 | -37.791 | [-49.142, -26.440] | 34.96% / 64.65% | 1/8 | -96.930 | 93 | 23,346 |
| Exact best one use | -0.688 | [-12.726, 11.349] | 52.05% / 47.75% | 4/8 | -55.477 | 45 | 14,921 |
| Best one plus priority pair | +3.422 | [-8.697, 15.540] | 54.00% / 45.70% | 5/8 | -52.453 | 43 | 14,354 |
| Exact resident | 0.000 | control | control | control | control | 22 | 5,001 |

D148's hindsight envelope adds exactly `+41.212890625` over D40 on this panel: `+37.1025390625`
from exact best one use and `+4.1103515625` from the selected second intervention. This closes the
cross-panel uncertainty that stopped D158. The improvement is real, but it only lifts the combined
oracle to `+3.421875` over the resident, below the frozen `+5` threshold and without a positive
clustered lower bound.

The failure is structural, not a marginal gate miss. The combined terminal oracle still regresses
on 45.70% of tasks, loses `-52.453` against the resident family and `-49.523` against
`legend_balanced`, fails the first 16-map block at `-5.797`, raises catastrophes from 22 to 43, and
raises negative-margin mass from 5,001 to 14,354. Only the own/opponent score-direction gate passes;
the other nine frozen value and safety gates fail.

## Interpretation and next move

Do not restart D158, enlarge its recurrent model, or train another D40-fallback q6 selector. Even an
unobservable terminal oracle over that vocabulary is not a safe resident-dominant substrate, so a
learned approximation cannot repair it.

The next representation must make the exact resident the native KEEP action and introduce a
genuinely new multi-turn option. D160 establishes that worker scale cannot be opportunistic; the
option must reserve a bounded bill over multiple turns and either commit, abort back to the warmed
resident, or complete a worker transition. First prove mechanics and resident-relative value on a
small reused-map local panel. PPO, new maps, TestSession, Arena, and submission remain closed until
that causal option demonstrates headroom.

## Reproducibility

- protocol SHA-256: `33ed7bfa78df4b47afbf6bd66497c697169dab330d2baa5505898c471714723a`;
- lock SHA-256: `17a6668753cf41b3a102de252c3ef5dd0ae234cc5bafcd7d506b510e02698496`;
- analyzer SHA-256: `8a6ab976512e35df86518f0c9698e433678e264019885848c8813ea9f8da2aee`;
- machine-result SHA-256: `b6411b4c8b2db17f6f2e3efaab3ca193ef0630d3deae4cb255ba9dbdcbf1271a`.
