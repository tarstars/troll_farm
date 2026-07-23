# D49 chopper-first reservation order — frozen protocol (2026-07-21)

## Question

D35 proves that joint, repeated target allocation has large value. D46 proves D40's trained
maximum-chop worker already selects `FELL_BANK` whenever legal, but D40 processes simultaneously
free workers in ascending unit-ID order. The chopper is normally trained last and therefore chooses
only after earlier producers have reserved acquisition and planting targets. D47 shows that
replacing adaptive scores with permanent roles is harmful, while D48 shows literal score bonuses
are saturated and unsuitable for continuous search.

D49 tests one coefficient-free scheduler change: let the chopper reserve first whenever it is part
of a simultaneously free post-funding batch, while preserving exact D40 scoring and all other
worker order.

## Frozen candidate

Before each worker-stage decision with at least three own workers:

1. identify the live worker with maximum `(chop_power, unit_id)`;
2. if that worker is present in the not-yet-assigned free-worker suffix, move only it to the front
   of that suffix; and
3. preserve the relative order of every other free worker.

Then choose exact D40 for the resulting current worker. No job kind, target, owner, rate, ETA,
phase, score, inventory, worker spec, TRAIN rule, deficit rule, evacuation rule, reservation rule,
or fallback changes. If the designated chopper is active, unavailable, already first, or worker
three does not exist, behavior is exact D40.

The default complete macro environment remains behaviorally unchanged. The sole new API,
`promote_max_chop_remaining_free_unit`, has environment source SHA-256
`c53388b444ae010a6a298b6ccc32be63badf20bfe4f8b8aa78b38767108d5360`; exact prior source remains
`632f1b2c99c18073c4cd956863fcaa4b7e9773dd69bb745fc18f062337130f62`.

## Stage A: activation-only audit

Use untouched official seeds **9,785,000--9,785,015**, both seats, and all eight frozen macro
opponents: 256 tasks. Run exact D40 control and the unchanged D49 candidate twice with 20 threads.
Ignore all score and margin fields.

Stage A passes only if:

1. all grids complete, candidate repeats are byte-identical, and there are zero mechanical,
   arithmetic, ordering, or default-control failures;
2. at least 256 eligible free-worker suffixes and at least 128 actual chopper promotions occur; and
3. candidate action hashes differ from D40 in 20%--90% of tasks.

Any failure closes D49 without value evidence. Do not broaden the reorder, sort all specialists,
change the tie break, or inspect outcomes on another bank.

## Conditional development

Only a Stage A conjunction opens untouched seeds **9,786,000--9,786,031**: 512 tasks. Run exact
D40 and two byte-repeat D49 arms. Require:

1. complete deterministic grids and zero illegal-command, provenance, relevant-deposit-prediction,
   ordering, worker-cap, reward-identity, action-count, or decision-loop failure;
2. action-hash changes in 20%--90% of tasks, at least 512 eligible suffixes, and at least 256
   promotions;
3. paired mean margin gain at least `+8`, 5%-trimmed gain at least `+5`, and the normal 95% lower
   bound across 32 map-seed means above `+3`;
4. mean own-score delta at least `+3` and mean opponent-score delta at most zero;
5. at least six of eight opponent-family mean margin deltas positive and the worst at least `-8`;
6. worker-two rate at least 95%, worker-three rate at least 88%, and crop rate at least 97%; and
7. catastrophe count (`margin <= -100`) and total negative-margin mass no worse than D40.

## Conditional confirmation

Only a development conjunction opens untouched seeds **9,787,000--9,787,031**. Run exact D40 and
two unchanged D49 repeats. Require the same integrity, activation, workforce, crop, and tail gates,
plus paired mean margin gain at least `+5`, trimmed gain at least `+3`, map-seed normal lower bound
above zero, own-score delta at least zero, opponent-score delta at most `+2`, at least six positive
opponent-family means, and no family below `-10`.

## Decision rule

A development and confirmation conjunction freezes D49 as a complete-policy research checkpoint
and opens separate source-size/runtime and field-domain qualification. It does not authorize a
candidate, TestSession, submission, or Arena action.

Any failure seals later banks and closes this exact reservation-order rule. Do not promote a
producer, fully sort the suffix, add target provenance, or combine D49 with a closed D46--D48 arm.
