# D75a two-batch ordinary-option sequence audit — frozen protocol (2026-07-21)

## Question

D74 finds +8.901 same-state one-deviation oracle margin, but improvement is sparse (38.54%) and
one selected batch never changes terminal workforce. Do short temporal option sequences make the
same four-mode interface broadly valuable, and does the second option decision add causal value
beyond the best first-action-only continuation?

D75a is a sequence representation/headroom audit. It does not fit or select a deployable policy,
reuse D74 outcome rows, tune a duration, construct a candidate, open confirmation, call
TestSession, submit, or touch Arena.

## Frozen outcome-blind state manifest

Run exact balanced ordinary behavior on fresh official seeds 9,813,000--9,813,031, both seats,
and all eight unchanged D40 opponent modes: 512 tasks. Record every 72-feature option boundary
where all four ordinary actions are legal and `turn < 300`, so two successive batches can execute
before the fixed horizon.

Partition maps before outcomes:

- discovery: seeds 9,813,000--9,813,015;
- validation: seeds 9,813,016--9,813,031.

Stratify by partition, opponent, seat, and phase (`turn <100`, `100--199`, `>=200`). Within every
stratum retain the six smallest SHA-256 identities of
`(map_seed, seat, opponent_index, decision_ordinal)`. Preserve task identity, boundary ordinal,
turn, phase, legal mask, 72 float32 features, and exact feature-bit hash. Selection cannot inspect
terminal results, actions after the boundary, or any deviated outcome.

Require 576 unique states, 288 per partition, exactly six in every one of 96 strata, finite
source-free features, and byte-stable independent generation.

## Frozen two-batch library

Enumerate the complete Cartesian product of the four ordinary modes at the next two option
boundaries, first mode major and second mode minor:

`BB, BH, BR, BF, HB, HH, HR, HF, RB, RH, RR, RF, FB, FH, FR, FF`,

where `B/H/R/F` mean balanced/harvest/renew/fell. A sequence is selected entirely from the initial
state. Execute its first mode at the manifest boundary and its second mode at the immediately next
boundary, then return to exact balanced through terminal. If the live-crop safety lock makes the
requested second non-balanced mode illegal, execute balanced and record the fallback; this is the
same deployable renewable invariant, not a dropped row.

`BB` is the exact control. `BB`, `HB`, `RB`, and `FB` are the one-deviation prefix library because
their second and all later actions are balanced. The other twelve arms test delayed, persistent,
or switching behavior. There is no learned state, third action, duration choice, turn threshold,
opponent label, rollout truncation, score shaping, or post-result sequence pruning.

## Frozen execution and integrity

Run all 16 sequences from every manifest state: 9,216 continuations. Repeat the complete matrix
with 20 threads and require byte identity. Record requested and executed second mode, second
boundary/reach/legality, terminal scores, workforce, trains, crop lifecycle, selected-job counts,
failure counters, action/state hashes, and reward identity.

All integrity gates must pass:

1. both 576 x 16 matrices are complete and byte-identical;
2. exact task, turn, feature-bit hash, source-free memory, and balanced replay reconstruction pass;
3. every state reaches the second boundary for every first mode;
4. every requested legal second mode executes, every illegal request falls back to balanced, and
   all four second modes execute at least 2,000 times each across the matrix;
5. commands, provenance, deposit prediction, crop survival, reward identity, sequence accounting,
   and baseline terminal consistency have zero failures; and
6. at least eight of the twelve non-prefix sequences change terminal action hash versus their
   same-first prefix in at least 10% of states, and sequence mean margins span at least 15 points.

Any integrity failure quarantines value and permits only an unchanged repair/repeat.

## Frozen causal summaries

For each state choose the full-library oracle by maximum terminal margin, then higher own score,
lower opponent score, preference for a one-deviation prefix on exact ties, then lower sequence
index. Separately choose the best of the four prefix arms with the same outcome ordering.

Report:

- every sequence's advantage distribution versus `BB`;
- full-oracle and prefix-oracle value versus `BB`;
- full-oracle incremental value versus the prefix oracle;
- sequence, second-mode, phase, opponent, workforce, crop, own-score, opponent-score, and negative
  tail effects; and
- second-action reach, legality, execution, and action-hash activity.

These are representation upper bounds. An oracle row or sequence label cannot become a policy.

## Frozen headroom gates

The full two-batch library passes only if all hold:

1. mean oracle margin advantage over `BB` is at least +10;
2. strict oracle improvement occurs in at least 55% of states;
3. every opponent-family mean oracle advantage is at least +3;
4. at least three non-prefix sequences are strict oracle winners in at least 12 states each;
5. mean oracle own-score delta is nonnegative or mean opponent-score delta is nonpositive;
6. oracle-selected worker-three reach is at least 85%; and
7. oracle-selected crop creation is exactly 100%.

The second decision is causally material only if all hold relative to the best prefix oracle:

1. mean incremental margin is at least +3;
2. strict incremental improvement occurs in at least 25% of states;
3. every opponent-family mean increment is at least +0.5;
4. at least two non-balanced second modes occur in at least 12 strict selections each; and
5. mean incremental own-score delta is nonnegative or mean incremental opponent-score delta is
   nonpositive.

## Decision rule

- **Integrity, full headroom, and incremental headroom pass:** freeze the two-batch label interface
  and open a disjoint grouped sequence-value learner. D75 states are consumed and cannot qualify
  that learner or a candidate.
- **Full headroom passes but incremental headroom fails:** close fixed two-batch sequencing as the
  causal mechanism; do not fit its labels. Move to a different adaptive horizon/history
  representation on fresh data.
- **Full headroom fails:** close short ordinary-option sequences. Do not add a third batch, tune
  sequence membership/gates, or select a favorable fixed pair from this matrix; return to
  whole-policy search with a different controller representation.
- **Integrity failure:** quarantine value, repair only the defect, and repeat unchanged.

No branch authorizes candidate construction, confirmation, submission, or any platform action.
