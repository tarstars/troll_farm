# D77a full recurrent lineage whole-policy search result (2026-07-21)

## Verdict

**Reject and close this full recurrent lineage representation and optimizer.** Retaining actual
policies instead of averaging CEM elites does preserve active, profitable policies inside several
search batches. It does not produce a robust final controller: the preregistered selection
champion has fitness **+0.719**, below the required +2, and uses non-balanced modes in only
**0.989%** of untouched validation decisions, below the required 20%.

The champion is not a candidate. Do not select another survivor, extend the lineage, increase
mutation, retune fitness, or reuse the selection and validation panels. The next branch must change
the information and action representation rather than repeat another optimizer over these four
ordinary modes.

## Search integrity and execution

The independent audit reconstructs all of the following exactly:

- ten 32-policy populations, their balanced controls, and all 21,120 generation rows;
- the separate eight-policy selection population and all 1,152 selection rows;
- every founder, parent copy, Gaussian mutation, lineage edge, parameter hash, objective, ranking,
  and survivor set;
- the one-row frozen champion and the validation population; and
- two byte-identical 768-row validation matrices, SHA-256
  `596b81f388fbc39c97cedee604676e11086f5dec4114fda02c94fd33d2c62da7`.

There are zero command, provenance, deposit, feature/recurrent finiteness, legal-mask, reward,
crop, or action-count failures. Founder zero matches balanced exactly. Search plus selection takes
528.27 seconds at 19.49 effective CPU cores; validation repeats are exact.

## Search dynamics

The full recurrent search contains real whole-game signal:

| Generation | Best lineage | Mean margin delta | Own-score delta | Strict improvements | Active modes |
|---:|---|---:|---:|---:|---|
| 3 | `l0065` | **+12.125** | +3.688 | 50.00% | harvest, renew, fell |
| 4 | `l0080` | **+8.156** | +5.563 | 51.56% | harvest, renew, fell |
| 6 | `l0141` | +6.125 | +3.031 | 28.12% | renew, fell |
| 10 | `l0231` | +5.344 | +2.188 | 21.88% | harvest, renew, fell |

Generation four improves all eight opponent families and has p10 delta zero, showing that the
four-mode controller can be useful on a particular fresh map batch. This is stronger evidence than
the D76 distribution mean and confirms that actual-policy retention solved the narrow averaging
problem.

It does not solve generalization. Population diversity falls from eight founders after generation
one to one founder after generation six. Later batches increasingly reward sparse deviations near
balanced. This is not a mechanical failure: it is the search response to unstable cross-map value
under the current observable features and coarse action modes.

## Frozen champion selection

The separate selection panel chooses `l0225`, a depth-eight descendant of founder `l0012`, hash
`125037a34b95c04c57593d62874e70e65023e1686190c52854938554292d8d32`.

| Selection measure | `l0225` | Frozen gate |
|---|---:|---:|
| Robust fitness | **+0.719** | at least +2 — **fail** |
| Mean margin delta | +0.719 | descriptive |
| Mean own-score delta | +0.805 | descriptive |
| Strict improvements | 6.25% | descriptive |
| Non-balanced decisions | 89 / 9,016 = 0.987% | descriptive |
| Worker-three reach | 89.06% | no paired degradation |

The selection rule is reconstructed exactly. The winner is simply too close to balanced to satisfy
the preregistered search-activity condition.

## Prospective validation

| Measure | Frozen champion | Frozen gate |
|---|---:|---:|
| Non-balanced unlocked decisions | **155 / 15,667 = 0.989%** | at least 20% — **fail** |
| Distinct non-balanced modes | 2 | at least 2 |
| Mean margin delta | **+0.344** | at least +5 — **fail** |
| Strict improvements | **17 / 256 = 6.64%** | at least 55% — **fail** |
| Ties / regressions | 91.80% / 1.56% | descriptive |
| Positive opponent families | 6 / 8 | at least 6 |
| Worst opponent family | `norx_native_three`, **-5.406** | at least -5 — **fail** |
| Mean own-score delta | +0.445 | at least -10 |
| Mean opponent-score delta | +0.102 | descriptive |
| Paired p10 delta | 0.000 | at least -60 |
| Worker-three reach | 89.84% | at least 85%, no paired degradation |
| Crop creation | 100% | exactly 100% |

The 155 non-balanced decisions comprise ten `renew` and 145 `fell`; `harvest` never executes.
The small positive mean is concentrated in 17 tasks, with a range from -110 to +100. The controller
is behaviorally a sparse balanced overlay, not an end-to-end learned policy.

## Multilevel interpretation

1. **Optimizer:** actual-policy `(mu + lambda)` retention avoids CEM mean cancellation. That narrow
   hypothesis succeeds; changing population size or mutation is not the next bottleneck.
2. **Representation:** active policies win individual batches but their interventions do not remain
   valuable across fresh maps. Seventy-two instantaneous/lifecycle features plus hidden recurrence
   do not expose a stable condition for choosing among the four coarse modes.
3. **Action abstraction:** `balanced`, `harvest`, `renew`, and `fell` alter an entire job batch.
   They hide the opponent action, target provenance, funding commitment, and partial job progress
   that determine whether a deviation is productive.
4. **Selection pressure:** robust cross-family survival rationally converges toward balanced because
   sparse abstention is safer than broad action under ambiguous state. This is evidence about the
   interface, not evidence that the game has no policy headroom.
5. **Data:** the next representation should be grounded in current-field trajectories, especially
   observable opponent-history and commitment signals, before another expensive search.
6. **Deployment:** no source was exported or submitted. The Arena resident remains the unchanged
   62,725-byte submission `41015603` / agent `6561795`; its rank movement is not a D77 deployment.

## Next experiment

Reuse the already collected and QA-passed immutable current-field snapshot
`20260721T105508Z-d61p`. Measure which opponent-history and action-progress features separate
successful active interventions from balanced abstention. Then preregister a new controller
interface around those observables; do not begin with another four-mode recurrent optimizer or
duplicate the same-day network collection.

## Artifacts

- protocol: `d77a-full-recurrent-lineage-search-protocol-2026-07-21.md`;
- search log SHA-256:
  `d7f4f2d2615a5c885c4fa11cab7b55a947b1ec232a5d8a202b977ea321178c41`;
- champion SHA-256:
  `e7350678c0ec5d1de78389a6ba81bdf8e91aa5aa60d157d8d06f1344d545c0ae`;
- repeated validation SHA-256:
  `596b81f388fbc39c97cedee604676e11086f5dec4114fda02c94fd33d2c62da7`;
- machine result: `d77a-full-recurrent-lineage-result.json`, SHA-256
  `5f39193cba528e24586b1493c64da02871157063682f2ae60289927df3c9d53f`.
