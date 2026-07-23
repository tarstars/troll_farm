# D28 resident handoff-state experiment — result (2026-07-20)

## Verdict

**Close basic resident-state retention.**  Keeping the turn-75 resident object paused improves the
cold turn-150 restart by only +2.698 margin, and continuously shadowing observations improves it
by +2.646.  Neither approaches the frozen +10 mechanism gate; neither passes the policy gates
against the resident.  Prospective seeds 52,000--52,059 remain unopened.

No candidate was built, no source was submitted, and no Arena action occurred.

## Integrity

- The D28 release runner compiles and all nine focused/inherited tests pass.
- Smoke produced 400/400 rows twice and is byte-identical.
- Development produced the complete 9,600-row matrix: 120 maps, both seats, eight opponents, and
  five branches.  It completed in 147.252 seconds with 24 workers.
- Every turn-75 root and every turn-150 farm state agrees across branches, including the executed
  farm-prefix command hash.
- All 7,680 eligible D28 control comparisons exactly reproduce D24/D26 resident, permanent-farm,
  and cold-return terminal states and command hashes.
- All branches reach turn 150 and execute their intended phases.  Paused and shadow command
  streams differ from cold in 100% of cells.

## Development result

| Handoff state | Margin vs resident | 95% interval | Own score | Margin vs cold | 95% interval | Worst opponent | Negative mass | Verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Paused | +3.658 | [-0.537, +7.853] | +30.911 | +2.698 | [+1.042, +4.355] | -14.883 | 1.058x | reject |
| Shadow | +3.606 | [-0.604, +7.817] | +30.856 | +2.646 | [+1.002, +4.291] | -14.883 | 1.058x | reject |

Both branches pass the 5%-trimmed margin, own-score, resident-catastrophe, phase-execution, and
cold-improvement-confidence gates.  They fail mean margin, overall confidence, opponent breadth,
worst opponent, catastrophe frequency, negative mass, and the required magnitude of improvement
over cold.

Paused opponent means are -14.883 adaptive Gold, -3.000 Compact Gold, -3.000 fixed Gold, +3.517
Script, +5.513 MyBot, +9.762 Scheduler, +10.688 Silver, and +20.671 Printer.  Only five of eight
are nonnegative.  Catastrophic frequency is 15.73% versus 15.00% resident; negative-margin mass is
62,441 versus 59,015.

## Mechanism analysis

### State retention is real but small

The paused improvement over cold is statistically positive, but its median seed effect is zero:
85/120 seed means tie, 25 improve, and 10 worsen.  The mean is carried by a small subset with a
maximum +49.375 seed effect.  Retaining early orchard/opening state occasionally matters, but it
cannot explain D27's broad -20.649 cost of returning from the farm.

### Observation without execution adds nothing

The shadow and paused terminal metrics are nearly identical.  Their resident-versus-control means
differ by only 0.052, and their negative-tail values are exactly equal.  Feeding the resident 75
observations while discarding its commands does not preserve productive value.  An
actual-command observation API is therefore not warranted.

### The remaining loss is policy-level

D27 measured cold return versus permanent farm at -20.649.  Paused state recovers +2.698, leaving
approximately -17.951 attributable to activating the resident's post-150 scheduling rather than
continuing the farm.  The return reduces opponent production, but it reduces own production still
more.  No bookkeeping-only handoff can repair that objective mismatch.

### Command divergence is not outcome relevance

Both retained variants have different command hashes from cold in every cell, yet most seed means
and nearly all aggregate metrics are unchanged.  Future readiness checks should retain command
activation as a sanity check but never treat it as evidence of useful behavioral coverage.

## Next direction and cross-project consistency check

Do not extend the cutoff grid or build a more elaborate resident-state bridge.  An immediate D28
reading suggested exclusive planting masks, but the subsequent project-history audit rejects that
move before execution: the complete-economy ownership diagnostic already showed that only 1.11%
of the farm-induced opponent wood came from our crops, while 95.83% came from opponent-created
crops.  GoldElite also already restricts planting to Manhattan radius three around our shack.
Private placement is closed and must not be repeated.

The remaining high-value object is the permanent resident/farm option itself.  D25's aggregate
tabular forest captured +28.888 margin under the strict crossed audit and failed only its 75%
precision floor (73.23%), while D26--D28 show that structural switching cannot replace selection.
The next eligible representation is therefore a **small canonical spatial option-value critic**:
raw player-relative map/state planes plus a compact trajectory summary, trained and audited from
scratch on a much larger preregistered map corpus with simultaneous unseen-map/unseen-family
folds.  This does not retune or revive the closed D25 forest; its purpose is to test whether spatial
equivariance removes the measured map-compatibility overfit.  It must retain exact resident
fallback and clear size/latency feasibility before any candidate work.

## Evidence and hashes

- protocol: `d28-resident-handoff-state-protocol-2026-07-20.md`;
- runner: `rust/src/bin/d28_handoff_state.rs`;
- analyzer: `cgauto/d28_handoff_state_analysis.py`;
- smoke TSV, repeat TSV, and JSON;
- development TSV and JSON.

SHA-256:

- protocol: `4b5d3c7c1945cba426a4d35f9d79f75546f7d9eb50925a668bb62aaac22547c6`;
- runner: `681275d1e31b057e24dbc478b0cf2efc2423da3f1d17f2e10c904e50e229699b`;
- analyzer: `af28b145bdfed648c7647c9b0e45ecea264fd3404ec7d13505f23f3ce6dd92c9`;
- development TSV: `01e413e44cb55cb9cd2143409e4d64f8cf436087c7aa12489238b556af9e88db`;
- development JSON: `b74e9d05ca78ce4f4a8cc18dd948ce1192eb6d9d7c041e3f23adb8a5297c5811`.
