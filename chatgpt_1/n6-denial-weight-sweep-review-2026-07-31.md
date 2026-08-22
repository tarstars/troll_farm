# Independent review — N6 denial-distance weight sweep

- Reviewer: `chatgpt_1`
- Task: `20260730-n6-denial-weight-sweep`
- Reviewed integrated base: `e70a3b1d6d981168aa88b15960ea3c591827ba35`
- Review date: 2026-07-31
- Verdict: **`CLOSED_AT_DEVELOPMENT` accepted**

## Decision

Accept the frozen development closeout. Neither preregistered nonzero scalar alternative
passes every selection gate, so no arm may consume confirmation maps. Keep the resident
weight at 900, close further scalar tuning in this exact architecture, and do not create a
candidate or perform an Arena action.

The result does not disprove every possible denial scheduler. It closes the one permitted
450 / 900 / 1800 scalar sweep on the exact resident snapshot and frozen A2-0b substrate.

## 1. Wrapper normalization and scalar-only identity

The source materializer is fail-closed:

- it hashes the exact resident snapshot before reading it;
- it requires exactly one occurrence of
  `score += 900.0 / (1 + opponent_distance) as f64;`;
- it accepts only weights 450, 900, and 1800;
- LOW and HIGH replace only the numeric literal on that exact line;
- CONTROL is unchanged after normalization;
- an assertion compares the complete generated text with the exact expected transform.

The only shared normalization removes the exact leading crate-only attribute
`#![allow(dead_code, unused_imports)]` from all three generated modules. The runner applies
the equivalent outer attribute to each `include!` module. No policy byte beyond that
identical wrapper normalization and the registered scalar differs.

The implementation lock and compact manifest agree on the generated hashes:

| arm | weight | generated SHA-256 |
|---|---:|---|
| LOW | 450 | `a827f7c1542f800e94f33b2e924a07d191b9e1c5a9202450744e81d5a75dee94` |
| CONTROL | 900 | `9ac22932901aeff7d8c8855e54de23d5b9a83de6e4025bde5758f020b517ac03` |
| HIGH | 1800 | `bfba6c4be4bdeed7f8a30c375a30fefd63a8f91e294a53dd532af26a837040d6` |

The resident, referee, and continued-map-generator locks remain respectively
`fff6669b…`, `518c2228…`, and `8e841958…`. The runner includes generated sources through
compile-time environment paths and does not edit the resident, module registry, or Cargo
configuration.

## 2. Exact policy locus

The scalar applies only inside `MoisanBot::chop_candidates` when:

- the candidate plant is the bot's fixed `type_to_cut` focus species;
- the opponent roster has at most two trolls;
- the ordinary travel, growth, chop, return, remaining-turn, and capacity filters already
  admit the tree.

The surrounding `opponent_trolls <= 2` gate, focus-species choice, tree-throughput term,
candidate grammar, joint selector, path repair, and endgame logic are unchanged.

The runner's `focus_type` reproduces the resident's initialization exactly: it computes
BFS distance from walkable own-shack neighbors, compares the summed distances of LEMON and
PLUM trees in the initial common state, and uses the same deterministic ordering. The
resident calls `ensure_focus_type` before its first decision and retains the result.

## 3. First-divergence direction and denominator

For every alternative/task pair, the runner advances separate CONTROL and candidate games
only while their canonical states match. At each common state it obtains both resident
command vectors and both opponent command vectors. Any opponent-command mismatch is an
integrity failure. The first resident command mismatch is classified once.

The frozen ordering is implemented as an optional emitted-command focus intensity:

- MOVE contributes its emitted destination only when that cell currently contains a live
  focus-species tree;
- CHOP contributes the acting unit's current cell under the same condition;
- the command vector's intensity is the minimum Manhattan distance of such targets to the
  opponent shack;
- HIGH is directional for `None -> Some` or a smaller distance;
- LOW is directional for `Some -> None` or a larger distance;
- non-focus-to-non-focus differences are not directionally comparable.

Manhattan distance is the exact distance used by the changed source term. The analyzer's
denominator contains only rows marked both common-state and directionally comparable; the
numerator is the intended-direction subset. It does not divide by every command-divergent
task.

This telemetry describes emitted commands after the resident's move-conflict resolver,
not an inaccessible latent candidate target. That is the pre-lock operational metric. It
is also non-decisive to the final selection here: even a different directional
classification could not rescue LOW's negative value/seat/family gates or HIGH's four-of-
eight family result.

## 4. Matrix and issue integrity

The analyzer requires the exact development task set:

- seeds 9,858,000–9,858,031;
- both seats;
- all eight frozen opponent families;
- exactly 512 unique tasks and 512 rows for each of LOW, CONTROL, and HIGH;
- no duplicate `(seed, seat, family, arm)` key.

The compact result records 512 rows per arm, 1,536 total, no duplicates, and source/matrix
integrity true. The external panel hash is
`f57817b3d4906c3d7941df2ab8257069ccd199b8280843db156c13f255bd41ae`.

Development integrity requires both paired games terminal; zero critical and unclassified
issues; zero `unit_not_owned` issues; no opponent-command mismatch; and a common state at
every reported command divergence. In the frozen referee taxonomy, unknown/unsupported
commands and the defensive fallback are critical, while any reason outside the supported
noncritical set is unclassified. Thus the stated critical/unclassified gates cover the
protocol's unsupported/fallback boundary.

The pre-lock smoke additionally established deterministic sorted TSV identity across one
and four workers, 48/48 exact rows, zero critical/unclassified/opponent-command mismatch,
exact trajectory alignment, and successful execution of all six standing detectors.
Focused pytest reports ten passing tests and the analyzer self-test passes.

## 5. Arithmetic reconciliation

### LOW 450

- command divergence: `378 / 512 = 73.828125%`;
- intended directional among comparable: `15 / 97 = 15.463917525773196%`;
- mean margin delta: `-0.75390625`;
- seat deltas: `-1.11328125`, `-0.39453125`;
- positive family deltas: 3/8;
- own-score delta: `+0.033203125`;
- opponent-score delta: `+0.787109375`;
- identity check: `0.033203125 - 0.787109375 = -0.75390625`.

LOW passes activation and integrity only. It fails the 60% directional gate, positive
mean gate, both-seat gate, and six-family gate.

### HIGH 1800

- command divergence: `273 / 512 = 53.3203125%`;
- intended directional among comparable: `12 / 77 = 15.584415584415584%`;
- mean margin delta: `+0.55859375`;
- seat deltas: `+0.4140625`, `+0.703125`;
- positive family deltas: 4/8;
- own-score delta: `+0.830078125`;
- opponent-score delta: `+0.271484375`;
- identity check: `0.830078125 - 0.271484375 = 0.55859375`.

HIGH passes activation, integrity, positive mean, and both-seat gates. It fails the 60%
directional gate and the required six positive families. The eight equally weighted
family means average exactly to `0.55859375`; the two equally weighted seat means do too.

The later +20 confirmation threshold is not a development-selection gate and is correctly
reported only as scale context.

## 6. Adjudication and boundary

`choose_development_arm` may select only an arm whose complete gate dictionary is true.
Neither arm is eligible, so `selected_arm` is null and the analyzer returns
`CLOSED_AT_DEVELOPMENT`. The tie rule is irrelevant, but its implementation correctly
prefers the larger mean and then LOW for an exact tie because it is the smaller absolute
scalar perturbation.

The compact manifest records `confirmation_maps_consumed: false`. Fresh confirmation maps
9,859,000–9,859,127 remain outside this result. There is no confirmation inference,
trajectory detector comparison, candidate, resident edit, TestSession, submission, or
Arena action.

The accepted consequence is narrow:

- keep the live scalar 900;
- do not retry zero, capable-only, another nonzero scalar, or a second grid under this
  architecture;
- do not generalize the negative result to every state-dependent, roster-dependent, or
  otherwise structurally different denial scheduler.

## Validation performed

- Cross-read the frozen protocol, task, implementation lock, handoff, human result,
  development JSON, and compact manifest.
- Inspected the materializer, development analyzer, confirmation boundary, focused tests,
  runner source, resident focus/scalar locus, selector, and move resolver.
- Recomputed divergence percentages, score identities, seat/family aggregation, and every
  development gate.
- Checked the referee issue taxonomy used by the integrity gate.

No panel was rerun. No external panel, trajectory, confirmation map/range, or bulk artifact
was opened. No source, runner, analyzer, test, frozen result, resident, module registry,
Cargo file, candidate, TestSession, submission, or Arena state was changed.
