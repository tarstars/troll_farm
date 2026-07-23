# D72a recurrent opening-portfolio population result (2026-07-21)

## Verdict

**Portfolio headroom passes; explicit deposited-seed actions fail the matched breadth gate.**
D71's recurrent boundary representation is viable, but the eight-action version is not the next
learning substrate. Preserve the recurrent state/controller interface, restrict learning to the
four ordinary modes, and close explicit PLUM/LEMON/APPLE/BANANA source actions under this design.

This is a consumed function-class result, not a policy selection. No random label, oracle choice,
checkpoint, candidate, confirmation data, or platform action is authorized.

## Integrity and execution

The frozen 32-policy population has 1,124 finite parameters per policy and exact labels. Both
complete runs contain 66 policies x 128 tasks = **8,448 rows** and are byte-identical at SHA-256
`b1fa776d6ec98d82f418f317bc24b6c8e742246fce29d8b6ded402e53338530f`.

- zero missing, duplicate, unexpected, or family-mismatched rows;
- zero direct-command, provenance, deposit-prediction, feature/recurrent-finiteness, mask,
  source-assignment, boundary, action-count, source-count, or reward-identity failures;
- ordinary policies execute zero source actions, attempts, and creations;
- maximum hidden magnitude is 1.0, as bounded by `tanh`;
- 25,001 invalidated jobs are reported lifecycle events, not mechanical failures;
- 690,940 boundary transitions run at 3,405.83 and 3,345.63 transitions/s;
- elapsed times are 202.87 and 206.52 seconds at 19.38 and 19.29 effective CPU cores.

## Representation activity

All five frozen activity gates pass.

| Measure | Result | Gate |
|---|---:|---:|
| Portfolio policies using at least four actions | 32/32 | at least 24 |
| Portfolio policies sourcing in at least 25% of tasks | 30/32 | at least 24 |
| Portfolio policies creating a crop in every task | 32/32 | at least 24 |
| Portfolio-policy mean-margin span | 206.211 | at least 30 |
| Least-used portfolio action | LEMON source, 9,219 | at least 256 each |

Across portfolio policies, the eight action totals are balanced 85,791, harvest 73,776, renew
84,472, fell 47,378, PLUM source 14,262, LEMON source 9,219, APPLE source 15,255, and BANANA
source 14,982. The class is active, crop-safe, recurrent, and behaviorally diverse.

## Crop-safe portfolio oracle versus balanced

This upper-bound comparison passes every frozen gate.

| Measure | Result | Gate |
|---|---:|---:|
| Mean margin gain | **+64.070** | at least +30 |
| Strict improvements | **116/128 = 90.63%** | at least 70% |
| Ties / regressions | 9 / 3 | descriptive |
| Mean own-score delta | **+32.750** | nonnegative |
| Mean opponent-score delta | **-31.320** | nonpositive |
| Worker-three reach | **122/128 = 95.31%** | at least 85% |
| Crop creation | **128/128** | exactly 100% |

All eight opponent-family gains are positive and exceed +10, from +40.875 against `silver_boss`
to +101.125 against `legend_balanced`. The selected portfolio oracle averages +143.719 margin;
balanced averages +79.648. This proves per-state recurrent choice headroom, not that any one
random policy is strong: the best fixed portfolio member averages +79.586, slightly below
balanced.

## Explicit source actions versus matched ordinary recurrence

The portfolio oracle gains **+16.164 mean margin** over the same 32 recurrent networks restricted
to balanced/harvest/renew/fell. It gains +19.891 own score while allowing +3.727 opponent score;
every opponent-family mean margin delta remains positive (+3.563 to +28.500). Selected portfolio
rows use source actions in 91/128 tasks, span 20 policies, and use all four species. These gates
pass.

The decisive breadth gate does not:

- strict improvements: **51/128 = 39.84375%** versus at least 40%;
- ties: 18;
- regressions: 59.

Because 40% of 128 requires at least 52 tasks, this is a one-task miss. It remains a formal fail;
the large oracle mean is concentrated rather than sufficiently broad. No threshold relaxation,
population-seed retry, source-head tuning, or favorable-label selection is allowed on these
consumed maps.

## Decision and next hypothesis

Follow the preregistered ablation branch:

1. retain D71's 72-feature recurrent memory and exact semi-Markov boundary mechanics;
2. restrict the next learner to the four ordinary modes;
3. close explicit deposited-seed source actions for learning under this representation; and
4. freeze a short ordinary-recurrent optimization/signal preflight on fresh maps, requiring
   deterministic action movement, universal crop establishment, broad opponent-family value, and
   a fixed-policy gain before any longer budget.

The live resident remains submission `41015603`, agent `6561795`, with the unchanged 62,725-byte
source. D72 did not update or submit the Arena program.

## Artifacts

- protocol: `d72a-recurrent-opening-portfolio-population-protocol-2026-07-21.md`;
- population: `d72a-recurrent-population.tsv`;
- repeated matrices: `d72a-recurrent-opening-population-a.tsv` and
  `d72a-recurrent-opening-population-b.tsv`;
- timing sidecars: `d72a-recurrent-opening-population-a-time.txt` and
  `d72a-recurrent-opening-population-b-time.txt`;
- machine result: `d72a-recurrent-opening-population-result.json`;
- runner: `rust/src/bin/d72_recurrent_opening_population.rs`;
- analyzer: `cgauto/analyze_d72a_recurrent_opening_population.py`.
