# D46 persistent post-funding chopper role — frozen protocol (2026-07-21)

## Question

D40 trains a producer `(2,2,1,1)` and then a chopper `(2,2,0,2)`, but after funding it routes all
workers through the same rate ordering. Independent top-player archaeology shows that strong
renewable economies keep later wood workers in persistent felling roles. D45a also establishes,
without authorizing coefficient selection, that job-kind/workforce allocation materially changes
whole-game outcomes while the D40 workforce ladder remains safe.

D46 tests one coefficient-free structural hypothesis: preserve D40's complete funding and supply
policy, but give the post-funding chopper persistent felling work.

## Frozen candidate

At every decision compute exact D40 prior order. Select D40 rank zero except when all conditions
hold:

1. the D40 branch is `rate`;
2. our side has at least three workers;
3. the current worker is the designated chopper: maximum `(chop_power, unit_id)` among our live
   workers, so the larger ID breaks a chop-power tie; and
4. at least one legal candidate is `FELL_BANK`.

Then choose the legal `FELL_BANK` candidate with the lowest exact D40 prior rank. If that is already
rank zero, record eligibility but not an override. No target, owner, ETA, phase, health, score,
inventory, or coefficient is added. TRAIN, deficit, shack evacuation, worker specs, active-job
reservations, provenance, and every non-designated worker remain exact D40.

## Development execution

Use untouched official seeds **9,778,000--9,778,031**, both seats, and all eight frozen macro
opponents: 512 tasks. Run:

- exact D40 control;
- D46 candidate A; and
- independent D46 candidate repeat B.

Use 20 threads. Preserve complete TSVs with action counts, hashes, role-eligible decisions,
role-overrides, and role-integrity failures. Candidate A/B must be byte-identical. No parameter
search, alternative designated-worker rule, ablation, or outcome-conditioned branch is allowed.

## Development gates

Development passes only if all hold:

1. all three 512-task grids are complete and clean, candidate A/B are byte-identical, and control
   reproduces exact D40 actions by construction;
2. zero illegal commands, provenance failures, deposit-prediction failures, role-integrity
   failures, worker overflow, reward arithmetic failures, or decision loops;
3. at least 20% and at most 90% of tasks change action hash, with at least 512 total role-eligible
   decisions and at least 256 actual overrides;
4. paired mean margin gain over D40 is at least `+8`, 5%-trimmed gain at least `+5`, and the normal
   95% lower bound across 32 map-seed means is above `+3`;
5. mean own-score delta is at least `+3` and mean opponent-score delta is at most zero;
6. at least six of eight opponent-family mean margin deltas are positive and the worst is at least
   `-8`;
7. worker-two rate is at least 95%, worker-three at least 88%, and crop rate at least 97%; and
8. catastrophe count (`margin <= -100`) and total negative-margin mass do not exceed D40.

## Conditional confirmation

Only a complete development pass opens untouched seeds **9,779,000--9,779,031**. Run exact D40 and
the frozen D46 candidate twice. Confirmation requires the same integrity, workforce, crop, role,
and tail gates, plus:

- task action-hash change in [20%,90%];
- paired mean margin gain at least `+5`, 5%-trimmed gain at least `+3`, and seed-mean normal lower
  bound above zero;
- mean own-score delta at least zero and opponent-score delta at most `+2`;
- at least six positive opponent-family means and no family below `-10`.

## Decision rule

A development and confirmation conjunction freezes D46 as a complete-policy research checkpoint
and opens a separate deployment-size/runtime and field-domain qualification protocol. It does not
itself authorize a candidate, TestSession, submission, or Arena action.

A development failure seals confirmation and closes this exact role policy. A confirmation failure
closes it as non-transferable. Do not change the designated-worker tie break, allow other job kinds,
add a phase threshold, or retune gates on either bank.
