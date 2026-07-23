# D32a deterministic field option A/B — result (2026-07-20)

## Verdict

**Reject permanent turn-75 farming as the next architecture.**  The clean six-game closed-loop
TestSession panel passes every preflight and causal-integrity gate, then fails all four frozen value
gates.  Against three exact opponent/map blocks, the farm changes terminal margin by `-42`, `+29`,
and `-74`: mean `-29`, only one positive block, and a worst regression far beyond the `-20` floor.
Mean own-score delta is also negative at `-5`.

D29b must not be threshold-retuned or field-calibrated.  No Arena agent was created, no submission
occurred, and the stable resident is unchanged.

## Integrity

All mandatory evidence passes:

- deterministic source regeneration, exact hashes, 62,725/96,426-byte sizes, and warning-denied
  optimized Rust compilation for both sources;
- exact six-job dry-run manifest and frozen bank hash;
- six completed unique games, exact seed echoes, zero diagnostics, and exact requested opponent
  snapshot IDs from replay enrichment;
- identical A/B turn-one maps matching the historical frozen map hashes;
- every fresh baseline exactly reproduces a member of its prior A/A block in scores, inventories,
  turns, workforce history, and both complete stdout hashes;
- player-0 actions are exact through turn 74 in all three pairs; and
- the forced option first diverges on turn 75 in every block.  Opponents first respond differently
  on turns 77, 88, and 80.

The old replay endpoint had expired for the historical games, so new TestSession responses retain
turn-one inputs and complete stdout streams directly.  Replay enrichment of the six new games then
supplied exact agent identities and reproduced those retained hashes.

## Value result

| Opponent | A score | B score | Own delta | Opponent delta | Margin delta |
|---|---:|---:|---:|---:|---:|
| delineate | 148–92 | 190–176 | +42 | +84 | **-42** |
| Escdemon | 225–249 | 218–213 | -7 | -36 | **+29** |
| laconic | 165–193 | 115–217 | -50 | +24 | **-74** |
| **Mean** |  |  | **-5** | **+24** | **-29** |

| Frozen gate | Observed | Result |
|---|---:|:---:|
| Mean margin delta >= +10 | -29 | **fail** |
| Mean own-score delta >= 0 | -5 | **fail** |
| At least 2/3 positive margins | 1/3 | **fail** |
| No block below -20 | -74 | **fail** |

## Analysis at different abstractions

1. **Causal evidence:** unlike D29's generated continuations and D31's replayed actions, these are
   actual closed-loop opponents on identical official maps.  The sign heterogeneity is policy
   response, not map or command drift.
2. **Economy:** production alone is not reliably valuable.  Against delineate, +42 own score is
   overwhelmed by +84 opponent score.  Against laconic, the farm simultaneously loses production
   and releases the opponent.  Only Escdemon converts the policy change into net suppression.
3. **Option architecture:** the permanent cold farm is not a robust basis for selection.  One
   positive block proves conditional value can exist, but the preregistered sample fails the gate
   required to justify a field-map-native selector.
4. **Model transfer:** D30's map-domain diagnosis was real but incomplete.  Even a perfectly
   calibrated D29 critic would be choosing an option whose field-native base-rate and downside are
   poor.  Recalibrating water features or the `+4` threshold cannot repair the underlying policy.
5. **Project direction:** retain the resident's suppressive interaction as a first-class behavior.
   The next architecture must add renewable production without a permanent policy replacement, or
   learn a complete closed-loop macro policy rather than select this farm branch.

## Harness incident and recovery

The first original D32 baseline response was lost before any field was persisted because the new
trace collector lacked the script-mode repository import path.  No B game or outcome was observed.
The failed zero-row artifact is retained.  D32a froze the sole import correction before restart and
repeated the unchanged six-row design.  Total operational calls were seven: one disclosed,
unobserved baseline plus six analyzable games.  This does not enter the value sample.

## Reproducibility

- recovery protocol SHA-256:
  `2e182f9e7a1b8e1deaab35a2dfa970165d52b7f0d40d28f3237dd37dbd13359b`;
- machine result SHA-256:
  `f58fc63ebda3d7731470b5eebf00f90e3123518e60c743afca3e79256fe8b36e`;
- enriched panel SHA-256:
  `fd9e1c019cc82c90c7b8cbcedcf320db87e4f30301d5959ce8517b5315387798`;
- dry-run panel SHA-256:
  `422883f8a37d62636a2d1f15a33e43926621021f6b70216246b8b638bac0d6da`;
- failed zero-row panel SHA-256:
  `262ff6e6046863b3cffcf36e34ca6dd3dbd1e25413b15b5495843fe11e72fac8`;
- baseline source SHA-256:
  `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55`; and
- option source SHA-256:
  `5138066175177a9b198c2c3f51deeef30d13d6207bee316227fae607662a6f82`.
