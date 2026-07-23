# D74a paired online option-value result (2026-07-21)

## Verdict

**Reject one-boundary option values and move to multi-batch option sequences.** Exact paired
continuations expose substantial but sparse local value: the crop-safe hindsight oracle gains
**+8.901 mean terminal margin** and improves every opponent family, but only **222/576 = 38.54%**
of states improve strictly. This fails the frozen 55% breadth gate.

The fixed discovery-only ridge ranker also fails on untouched validation maps. It activates in
81.94% of states, realizes **-0.778 mean advantage**, and captures -10.46% of oracle value. No
selector, candidate, confirmation run, resident update, or platform action is authorized.

## Integrity and execution

The outcome-blind manifest contains 576 exact balanced-trajectory states, evenly divided between
discovery and validation and across all 96 opponent/seat/phase strata. Its SHA-256 is
`d45041b6f69ab0abf44d5d23331e79a40a6b4bfa0b89e71671f4a063989a947d`.

Both complete 2,304-continuation matrices are byte-identical at SHA-256
`089191ce7ae7c0c617366f3d4b192beb4ccbc00f23fdadef7891190e865cf07f`.

- all 576 states have all four paired actions;
- exact state reconstruction, turn, feature-bit hash, and task identity pass;
- 356/356 represented balanced tasks have identical terminal continuations from every sampled
  boundary;
- direct-command, provenance, deposit-prediction, crop, and reward-identity failures are zero;
- all continuations preserve positive own crop creation;
- the runs sustain 40.79--43.29 complete continuations/s at 19.52--19.57 effective CPU cores.

The 8,018 invalidated jobs in each matrix are ordinary lifecycle events, not integrity failures.

## One-deviation headroom

| Measure | Result | Frozen gate |
|---|---:|---:|
| Valid paired states | 576 | at least 480 |
| Oracle mean advantage | **+8.901** | at least +5 |
| Strict oracle improvements | **222/576 = 38.54%** | at least 55% — **fail** |
| Lowest opponent-family oracle mean | +6.375 (`silver_boss`) | at least +1 |
| Non-balanced modes best at least 24 times | harvest 108, fell 104 | at least two |
| Oracle own-score delta | +4.392 | own nonnegative or opponent nonpositive |
| Oracle opponent-score delta | -4.509 | own nonnegative or opponent nonpositive |

Balanced remains oracle-best in 351 states, harvest in 108, fell in 104, and renew in 13. Oracle
value is concentrated: median and p10 are zero, while p90 is +33. Early and middle states average
+12.109 and +11.375 oracle advantage; late states average only +3.219. Every opponent family is
positive, ranging from +6.375 to +13.611.

Individual deviations are noisy and heavy-tailed:

| Action | Mean advantage | Positive | Ties | Negative | Range |
|---|---:|---:|---:|---:|---:|
| Harvest | +0.132 | 29.51% | 42.01% | 28.47% | -123 to +144 |
| Renew | -0.295 | 3.65% | 91.32% | 5.03% | -89 to +99 |
| Fell | +1.929 | 24.13% | 55.21% | 20.66% | -168 to +160 |

No one-boundary deviation changes terminal worker count in any of the 576 states. Its causal
effect is production/suppression allocation within an already established workforce, not a
workforce transition. This also explains why a single `renew` batch is usually inert: the option
often needs later materialization or reinvestment decisions before terminal value appears.

## Frozen grouped ranker

The ridge model is fit only on the 288 discovery states with `alpha=10` and the exact 72 features.
Discovery performance is optimistic (+5.076 mean realized advantage, 48.96% oracle capture), but
does not transfer:

| Validation measure | Result | Frozen gate |
|---|---:|---:|
| Activation | 236/288 = 81.94% | 20%--80% — **fail** |
| Mean realized advantage | **-0.778** | at least +2 — **fail** |
| Positive among activated | 20.34% | at least 55% — **fail** |
| Non-balanced modes selected | 3 | at least 2 |
| Worst opponent mean | -4.611 (`norx_native_three`) | at least -3 — **fail** |
| Positive opponent families | 4/8 | at least 6 — **fail** |
| Oracle value capture | -10.46% | at least 25% — **fail** |

The representation can fit sparse discovery outcomes but cannot distinguish intervention states
from the much larger tie/regression region on disjoint maps. Threshold or ridge tuning on these
consumed labels is not allowed and would not repair the failed causal breadth gate.

## Multilevel interpretation

1. **Mechanics:** exact same-state replay and paired terminal labeling are deterministic and fast
   enough for large offline causal audits.
2. **Action horizon:** ordinary semantic modes are temporally extended jobs. One selected batch is
   too short to express capitalization, renewable cycling, or sustained denial broadly.
3. **Value target:** large positive tails prove useful local opportunities exist, but sparse,
   heavy-tailed one-deviation labels are a poor direct policy target.
4. **Modeling:** D73's suppression-heavy PPO and D74's overactive ranker fail in the same direction:
   both underprice the cost of intervening in states where balanced is already good.
5. **Deployment:** the unchanged 62,725-byte live source, submission `41015603`, agent `6561795`,
   remains the Arena resident. Rank 33 is not caused by D74 or any local code update.

## Next experiment

Follow the frozen failure branch. Test short multi-batch ordinary-option sequences from fresh
balanced states, with exact paired controls and no threshold reuse from these labels. First ask
whether temporal persistence makes improvement broad and whether a second option decision adds
causal value beyond the best one-deviation prefix. Only a passing sequence headroom audit can
reopen a selector or prospective complete-policy test.

## Artifacts

- protocol: `d74a-paired-online-option-value-protocol-2026-07-21.md`;
- manifest: `d74a-option-value-manifest.tsv` and summary JSON;
- repeated matrices: `d74a-paired-option-values-a.tsv` and
  `d74a-paired-option-values-b.tsv`;
- machine result: `d74a-paired-option-value-result.json`, SHA-256
  `d5080f068dd5f1bae3b89787fa395d2947d12144931e67fae15db439d3cd8049`;
- runner: `rust/src/bin/d74_paired_option_values.rs`;
- analyzer: `cgauto/analyze_d74a_paired_option_values.py`.
