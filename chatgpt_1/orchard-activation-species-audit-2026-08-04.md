# Secure orchard activation and species audit

Task: `20260804-orchard-activation-species-audit`  
Data: eight exact one-hour Arena legs, 1,280 games  
Platform mutation: none

## Executive verdict

APPLE remains the correct species for the current protected, water-adjacent harvest mother. Idle-only activation has non-decisive replay direction; travel-only first-bank safety has non-decisive direction; adversarial kill safety has non-decisive direction. Any terminal-value claim still requires a fresh closed-loop comparison.

The repeated Arena evidence supports keeping a secure orchard, but not activating it
indiscriminately. The exact replay audit separates the activation cases that would survive
an idle-only gate, checks a first-bank safety gate, and compares an otherwise identical
BANANA mother on the same no-orchard states. Teacher-forced counterfactuals are interpreted
only through first divergence.

## Repeated Arena result

| Variant | Legs | Games | Mean Arena score | Median score | Wins | Catastrophes | Mean margin |
|---|---:|---:|---:|---:|---:|---:|---:|
| no-orchard | 4 | 640 | 23.108 | 23.905 | 343 | 69 | 8.233 |
| orchard | 4 | 640 | 23.692 | 23.350 | 381 | 91 | 6.128 |

Adjacent orchard-minus-no-orchard score deltas: `[1.6000000000000014, 2.0299999999999976, -0.35999999999999943, -0.9299999999999997]`; mean `+0.585`.

## Actual APPLE orchard activation

The orchard activated in **54/640** orchard-leg games (8.44%). Its underlying no-orchard starter verbs were `{'CHOP': 1, 'MOVE': 50, 'WAIT': 3}`.

| Gate/stratum | Games | Mean margin | Win rate | Catastrophes | Negative mass |
|---|---:|---:|---:|---:|---:|
| all activations | 54 | -32.75925925925926 | 0.5185185185185185 | 15 | 4273 |
| idle-only kept | 3 | -53.333333333333336 | 0.6666666666666666 | 1 | 223 |
| idle-only blocked | 51 | -31.54901960784314 | 0.5098039215686274 | 14 | 4050 |
| enemy-arrival-after-bank kept | 29 | -52.206896551724135 | 0.4482758620689655 | 9 | 2668 |
| enemy-arrival-after-bank blocked | 25 | -10.2 | 0.6 | 6 | 1605 |
| adversarial-kill-safe kept | 54 | -32.75925925925926 | 0.5185185185185185 | 15 | 4273 |
| adversarial-kill-safe blocked | 0 | n/a | n/a | 0 | 0 |
| idle + adversarial-kill-safe | 3 | -53.333333333333336 | 0.6666666666666666 | 1 | 223 |

Successful mothers: 52; games banking orchard fruit: 51; total banked APPLE: 5615; median first-bank delay: 13.0 turns.

## Exact initial-state pairs

The eight queues contain **0** exact matches on initial state, opponent
submission, and seat. These are reported as repeated deterministic comparisons, not as a
perfect randomized experiment because movement tie RNG may differ.

| Pair stratum | Pairs | Mean orchard-minus-no-orchard margin | Wins added | Catastrophes added |
|---|---:|---:|---:|---:|
| all | 0 | n/a | 0 | 0 |
| orchard activates | 0 | n/a | 0 | 0 |
| orchard inactive | 0 | n/a | 0 | 0 |
| activation: idle-only kept | 0 | n/a | 0 | 0 |
| activation: idle-only blocked | 0 | n/a | 0 | 0 |
| activation: first-bank safe | 0 | n/a | 0 | 0 |
| activation: enemy arrives before bank | 0 | n/a | 0 | 0 |
| activation: survives continuous attack to first harvest | 0 | n/a | 0 | 0 |
| activation: cannot survive continuous attack to first harvest | 0 | n/a | 0 | 0 |

## Why APPLE rather than BANANA?

The mother cell is always water-adjacent and is protected from ordinary chopping. Under that
geometry APPLE has effective cooldown **2**, while BANANA has cooldown **4**. A new APPLE
can first bank fruit after `travel + 11` turns; BANANA needs `travel + 19`. Mature APPLE
health is **20** versus BANANA **6**. For a persistent mother, being difficult to chop is an
advantage, not a defect.

On the 640 no-orchard trajectories, activation support was: APPLE 46, idle-only APPLE 0, BANANA 46, idle-only BANANA 0. Overlap: both 46, APPLE-only 0, BANANA-only 0.

Where both species could activate, the projected uninterrupted bank ceiling averaged 133.15217391304347 APPLE versus 64.80434782608695 BANANA, a mean APPLE advantage of 68.34782608695652 fruit.

A BANANA self-sustained orchard is therefore not a stronger version of this mechanism. It is
a different, lower-yield and more fragile mother. BANANA is attractive for cut/replant wood
production because it is easy to chop; that is precisely the opposite objective from a
protected harvest mother.

## Recommendation

Do not change activation from replay association alone. Keep current APPLE orchard and run a fresh closed-loop three-arm panel (current, idle-only, idle-only plus first-bank safety). The existing replays do not show a clean enough direction for an immediate gate change.

## Reproducibility

- full command-parity games: 696/1280;
- exact deployed command prefix through the activation window: 911/1280;
- replay packages: 8 with exact SHA verification;
- row table: `chatgpt_1/orchard-activation-opportunities-2026-08-04.csv`;
- machine report: `chatgpt_1/orchard-activation-species-audit-2026-08-04.json`;
- raw replay bodies remain in the existing Git LFS namespace; no duplicate raw data is written.
