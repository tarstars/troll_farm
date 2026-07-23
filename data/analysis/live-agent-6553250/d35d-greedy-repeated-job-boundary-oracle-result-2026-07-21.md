# D35d greedy repeated job-boundary oracle — result (2026-07-21)

## Verdict

**Repeated job-boundary allocation is strongly causal, but the productive-farm substrate remains
too permissive to the rival economy.**  The representation is rejected under its frozen gate.

Across 124 eligible exact official-map tasks, the repeated oracle adds **+53.817 seed-clustered
margin** over the uninterrupted farm.  It raises own score by +28.564 and lowers opponent score by
25.253.  Relative to the exact first-root one-shot oracle, repetition adds **+23.093 margin**,
raises own score by +11.067, and removes **12.026 opponent score**.  All eight seed means improve.

Thirteen of fourteen development gates pass.  The only failure is the deliberately independent
resident suppression ceiling: repeated opponent score remains **+76.118** above resident, versus
the required maximum of +65.  Confirmation seeds 9,400,008--9,400,019 remain sealed.  Per the
protocol, more productive-farm epochs, targets, or objective tuning are closed; the next upper
bound must start from the resident-suppressive controller.

No policy was learned, no candidate was built, and no TestSession, submission, resident, or Arena
state changed.

## Integrity and support

- All 128 seed/seat/opponent tasks are present.  The productive farm reaches the first eligible
  two-worker root in 124; the four ineligible tasks are both seats against resident on seeds
  9,400,003 and 9,400,005, where the farm finishes with one worker.
- The matrix contains 326 live decision epochs and **13,266 terminal option rollouts**.  Sixty-four
  tasks execute at least two non-control epochs, above the frozen 30-task floor.
- Independent seed-9,400,000 repeats are byte-identical: rows
  `7119300572054170cc13b6ae92a189fa3a7fad2c6e391093ceb5893a2ebd29b4`, manifests
  `fc16407346ea87b2756c6adfa42947d12bf53b415396cb5e21cb6b25726c20e1`.
- There are zero missing/duplicate options, duplicate keys, catalog/count errors, collisions,
  illegal direct commands, TRAIN successes, attribution mismatches, history mismatches, branches
  above three workers, farm-control mismatches, tie-break mismatches, epoch-chain errors, or
  terminal replay errors.
- Every selected live execution matches the independently recorded D35c rollout prefix in status,
  override count, invalid count, and exact completion turn.  Every next epoch begins on that turn;
  no hypothetical post-completion farm command enters live history.
- Four focused D35d Rust tests pass together with thirteen inherited executor tests; five analyzer
  tests pass, including deliberate epoch-chain corruption, repeat mismatch, and a value-valid
  suppression failure.

## Paired outcome

| Seed-clustered measure | Repeated result | 95% normal seed interval |
|---|---:|---:|
| Margin gain vs farm | **+53.817** | [+45.124,+62.510] |
| Own-score delta vs farm | +28.564 | [+22.151,+34.976] |
| Opponent-score delta vs farm | **-25.253** | [-33.491,-17.016] |
| Margin delta vs one-shot | **+23.093** | [+16.390,+29.795] |
| Own-score delta vs one-shot | +11.067 | [+5.769,+16.365] |
| Opponent-score delta vs one-shot | **-12.026** | [-19.649,-4.403] |
| Own-score delta vs resident | +166.017 | [+134.625,+197.409] |
| Opponent-score delta vs resident | **+76.118** | [+51.110,+101.126] |

Every opponent-family mean margin gain over farm is positive, from +23.750 against MyBot to
+71.625 against native Norxondor.  Seven families select provenance-specific bundles; resident is
the sole family without such a selection.  The oracle selects 214 non-control epochs: 156 generic
and 58 competitive, containing 64 exclusive opponent targets.

Tail behavior is safe.  Catastrophes fall from 1/124 under farm to zero under one-shot and repeated
control.  Negative-margin mass falls from 979 to 459 to **244** respectively.

## Frozen gates

The multi-epoch rate, farm-relative margin/own/opponent scores, resident-relative own score,
one-shot incremental value, all eight opponent-family gates, provenance breadth, and both tail
gates pass.  One gate fails:

| Failed gate | Result | Requirement |
|---|---:|---:|
| Opponent-score excess over independent resident | **+76.118** | <=+65 |

The miss is 11.118 opponent points.  It is not justified to revise the ceiling after seeing the
result: the ceiling encodes the suppression property that made the resident stable in Legend.

## Analysis by abstraction level

### Causal mechanism

Repetition is not a cosmetic relabeling.  It removes another 12.026 opponent points after the
one-shot intervention while simultaneously adding 11.067 own points.  Exact target provenance and
factorized persistent jobs remain valid components of the action representation.

### Decision horizon

The marginal terminal-margin gain decays by epoch: +30.774, +20.314, +10.172, and +3.091 for epochs
zero through three.  Corresponding opponent reductions are -13.161, -10.410, -6.453, and -0.242.
Nineteen tasks choose control immediately; 41/31/21/12 select one/two/three/four bundles.  Of the
105 tasks that enter epoch one, 64 continue; only twelve hit the four-epoch cap.  Another epoch is
therefore unlikely to recover the 11-point resident gap, and is explicitly closed by protocol.

### Production/suppression frontier

The repeated farm has ample production headroom—+166 own points over resident—but still exposes
76 opponent points.  A terminal-margin objective naturally spends some of that headroom on own
production rather than preserving the resident's rival-loop suppression.  The remaining defect is
the trajectory substrate and objective anchor, not insufficient search depth.

### Representation and learning

The state/action representation has now earned a causal teacher signal: joint persistent roles,
creator provenance, and repeated boundary decisions all matter.  What has not earned a learning
dataset is the productive-farm state distribution.  Distilling these choices would reproduce a
teacher that violates the independent suppression constraint.  PPO remains downstream of a
resident-anchored upper bound.

### Transfer

This is a hindsight teacher with exact local opponent continuation and cannot be deployed directly.
It also fails a frozen local gate, so field qualification or Arena transfer would be both premature
and protocol-invalid.

## Next experiment

D36 must test a **resident-anchored constrained joint scheduler**:

1. warm and clone the exact stable resident, opponent, history, provenance, and referee state;
2. begin at the resident's first eligible two-worker root on fresh official seeds;
3. reuse the validated factorized/provenance job vocabulary, but return completed workers to the
   resident rather than the productive farm;
4. select terminal options only inside the unchanged resident-relative opponent ceiling, then
   maximize own production with deterministic ties;
5. permit the same bounded repeated boundary decisions; and
6. test whether the upper bound adds at least 68 own points while keeping opponent excess at most
   65 and improving margin/tail across all opponent families.

This is distinct from the closed resident-local one-job experiment: D36 controls both workers
jointly, uses complete persistent bundles, exact crop provenance, terminal closed-loop value, and
repeated replanning.  If its upper bound fails, the next move is a genuinely complete learned
controller rather than another resident overlay.

## Evidence and SHA-256

- protocol: `52b77a9cdd47bbb155b8f2ee112aad9b0f4f95316d1a478b7b5d5e7853797f85`;
- runner wrapper: `6abe8c3af62bfc2fc7f7833da373fb9a517fb51f28a880f158fe64184b4ff30f`;
- shared implementation used for the run:
  `88a88b95f70ba0c7d70c7e3326c9fb7460b04366b2753ecfe4fefcfb797b7cb2`;
- analyzer: `b4c1b298ff1937aa4cd86de13a09b107055e3e7e1b0e7a8618f18e1cecf59306`;
- development rows: `aa5a141939a80e47767ce8ba7220f72cf9c321b053fb6f725b5b1618e0e49d9c`;
- development manifest: `982bc9578ad74e0d50b7c7ece632a7112bb0c2d91862d301dd6b14acfdc46d54`;
- result JSON: `26d795bfe8222623ece60157947e0e977780b3a13bc3df7c73a44c2607c17b28`.
