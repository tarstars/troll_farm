# D86a two-worker renewable role split — frozen protocol (2026-07-21)

## Question

The workforce branch D63–D77 established that predicting or adding extra workers does not by
itself improve the resident.  The current open field snapshot nevertheless contains a materially
different mechanism: agent `6480541` (`yaichi`) always keeps two workers, leaves the trained worker
as a dedicated chopper, and in eight of ten already-inspected games makes the initial worker run a
large successful `HARVEST -> PLANT` loop.  Can this *role allocation at fixed workforce* be
reconstructed from opening-visible state and transferred strongly enough to justify a closed-loop
resident challenger?

D86a is passive replay archaeology.  It may nominate D86b, but it cannot establish causal value,
change the resident, open a TestSession, submit, replace the resident, or access sealed data.

## Frozen inputs and contamination boundary

- Historical source: `top-player-opening-analysis-2026-07-17.json`, SHA-256
  `f869f12ef65c1971339e3d0676774fc11a7c951ad43bfaff7afb8641b91219be`.
- Current source: open D61p snapshot `20260721T105508Z-d61p`, analysis SHA-256
  `9f4050e5bab5843eba56586a9fba77bb01a5b20a4336254bd0f303e038cd8fc3`.
- State/command reconstruction starts from the raw games and processed trajectories named by those
  products.  It must not read `processed/sealed_confirmation/`.

The ten D61p yaichi games are **consumed discovery evidence**: their eight renewable and two
nonrenewable labels, broad action totals, map resource totals, and outcomes have already been
inspected.  They may be used to define the mechanism and reported as a current descriptive check,
but they may not fit a threshold or satisfy a pass gate.

The untouched historical yaichi games are ordered by numeric game id before any new action label is
decoded.  Games 1–15 are discovery; games 16–25 are validation.  The immutable split is:

- discovery: `893174122, 893407296, 893412043, 893876322, 894397581, 895446276,
  895446639, 895447009, 895447026, 895447237, 895883032, 895883103, 895883400,
  895883571, 895924585`;
- validation: `895925001, 895926495, 895926546, 895926772, 895927134, 895927164,
  895927169, 895927226, 895927242, 895927312`.

If any named raw replay or trajectory is unavailable, report support failure; do not substitute a
different game or move the split.

## Frozen reconstruction and behavior label

Decode exact official states with effective CHOP ids, require zero unknown updates, and reconcile
successful action effects against cargo and plant deltas.  Unit ordinal zero is the initial worker;
ordinal one is the first successfully trained worker.

A fruit token is `reinvested` when the initial worker successfully gains that species with HARVEST
and later successfully spends the same species with PLANT before it successfully DROPs that token.
Track tokens per species in acquisition order; pre-existing cargo and PICK gains do not count.

A game is in `renewable_mode` only when, by turn 100, the initial worker has:

1. reinvested at least three harvested fruit tokens;
2. completed at least three successful PLANT effects; and
3. both successfully HARVESTed and successfully PLANTed.

All other reconstructed games are `nonrenewable_mode`.  Also report thresholds one, two, four, and
eight descriptively; they cannot replace the frozen three-token label.

The intended role split is present when the game has exactly one successful TRAIN, the trained
worker spends at least 80% of its productive non-MOVE actions on successful CHOP, and the initial
worker owns at least 80% of all reinvested tokens.  Report first train, first reinvestment, action
counts by worker, successful material flows, plants, wood, score, margin, opponent, and seat.

## Frozen opening selector

Only these state-zero fields from the pre-existing analyzer may enter the selector:

`initial_plum`, `initial_lemon`, `initial_apple`, `initial_banana`, `initial_iron`,
`affordable_common_spec_count`, `tree_total`, `fruit_total`, `ripe_tree_count`,
`own_private_tree_count`, `own_private_fruit`, `own_near_tree_count`, `own_near_fruit`,
`water_adjacent_base_cells`, `own_nearest_tree_distance`, `own_nearest_iron_distance`, and
`shack_door_distance`.

Fit one deterministic, axis-aligned decision tree of depth at most two on the 15 discovery labels.
Every discovery leaf must contain at least three games.  Enumerate midpoints between observed
values; optimize discovery balanced accuracy, then ordinary accuracy, then fewer nodes, then the
lexicographic serialized rule.  Missing values always follow the nonrenewable branch.  No feature
engineering, scaling, interactions, opponent identity, seat, game id, outcome, current-game rows,
probability fitting, or post-hoc threshold changes are allowed.

As fixed baselines, evaluate always-renewable, always-nonrenewable, and each one-level stump under
the same discovery tie rules.  The selected depth-two tree must beat the best constant by at least
0.10 discovery balanced accuracy or it is replaced by that constant before validation is read.

## Frozen integrity and support gates

Require all:

1. all 25 named historical games decode, have matching trajectory lengths, zero unknown updates,
   exact terminal inventories/scores, and deterministic byte-identical rows under one and 20
   processes;
2. discovery has at least four renewable and four nonrenewable games;
3. validation has at least three renewable and three nonrenewable games;
4. both seats and at least six distinct opponent agents occur in the complete historical corpus;
5. at least 80% of historical renewable games exhibit the intended two-worker role split; and
6. at least 80% of the consumed current renewable games exhibit that same role split.

Support failure forbids lowering the label threshold, leaf size, class floors, or changing the
split.  It leaves the field observation descriptive rather than deployable.

## Frozen transfer gates

On the untouched ten-game historical validation block, require the frozen selector to achieve all:

1. balanced accuracy at least 0.75;
2. renewable precision at least 0.75;
3. renewable recall at least 0.75;
4. nonrenewable recall at least 0.60; and
5. at least a +0.10 balanced-accuracy advantage over the best frozen constant baseline.

Report confusion matrices by split, Wilson intervals, every leaf, feature distributions, current
D61p predictions, and outcome/production contrasts.  Outcome contrasts are observational only and
cannot rescue a failed behavior gate.

## Decision rule

- **Integrity, support, role, and all transfer gates pass:** open D86b.  Implement the selected
  opening-visible switch as a resident-compatible two-worker challenger and qualify it on disjoint
  closed-loop local seeds against the stable resident.
- **Selector transfer fails with support:** close static first-move selection for this archetype.
  Preserve action-local fresh-fruit reinvestment as a separate possible hypothesis only if at least
  80% of renewable games enter the loop after a directly observable successful HARVEST; it would
  require a new protocol and may not reuse validation for tuning.
- **Support fails because one mode is rare:** do not fit or integrate a selector.  Report whether a
  constant policy is descriptively plausible, but require a new closed-loop protocol before any
  code change.
- **Role consistency fails:** close the yaichi imitation hypothesis; its advantage is not the
  proposed semantic decomposition.
- **Integrity fails:** quarantine all behavioral conclusions and repair only reconstruction.

No D86a result authorizes platform writes, TestSession use, submission, resident replacement, or
sealed confirmation access.
