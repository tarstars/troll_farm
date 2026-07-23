# D42 context-complete continuation selector — frozen protocol (2026-07-21)

## Question and boundary

D41h shows that a tiny nonlinear scorer over the existing 100 candidate features can retain broad
value and reduce the negative tail, but cannot reach the frozen positive precision floor. D42 asks
whether the missing signal is live spatial/economic context rather than model capacity.

This protocol authorizes implementation tests, one outcome-blind discovery manifest, exact paired
one-deviation outcomes on fresh official maps, grouped model discovery, and a conditional disjoint
continuation replication under the representation below. It authorizes no complete-policy run,
confirmation, deployment candidate, TestSession, submission, or Arena action.

D41d, D41f, D41e, D41g, and D41h labels may motivate the representation and fixed optimizer, but
may not train, select, calibrate, or replicate D42. No D42 feature, model setting, threshold, or gate
may change after the first discovery outcome is observed.

## Fresh outcome-blind banks

Discovery uses maps 9,773,000--9,773,063, both seats, and all eight frozen opponents. Replay exact
D40 and enumerate only early (`turn < 100`) or late (`turn >= 200`) `rate` decisions with at least
two candidates and D41c rank-one residual gap in [0.200,0.340]. Stratify by opponent, phase, and the
six fixed bins [0.200,0.240), [0.240,0.260), [0.260,0.280), [0.280,0.300), [0.300,0.320), and
[0.320,0.340]. Select at most 24 hash-smallest task-deduplicated states per stratum, using only
`SHA256(map_seed:seat:opponent_index:decision_ordinal)`.

For every selected state compare uninterrupted D40 with exactly the rank-one action followed by
D40. Replay identity must match map, seat, opponent, decision ordinal, turn, branch, candidate count,
rank-zero action, rank-one action, and residual gap within `1e-6`. Run the first 128 manifest rows
twice before the full execution and require byte-identical terminal/action/state fields and paired
deltas. All action, worker-cap, direct-command, provenance, deposit-prediction, and reward-identity
checks must be clean.

Only if grouped discovery passes may the numeric full-fit model and threshold be applied to a new
manifest constructed identically from maps 9,774,000--9,774,031 with at most 16 rows per stratum.
The external outcomes remain unopened otherwise.

## Exact 194-feature representation

Start with the exact D41g 100-vector in its frozen order. Append 46 shared context values, then 16
rank-zero job-context values, 16 rank-one values, and the 16 rank-one-minus-rank-zero differences.
Opponent identity, map seed, seat, task ID, outcome, cohort/bin, hashes, and terminal values are not
inputs.

The 46 shared values are, in order:

1. own inventory items 0--5 divided by 20 (6);
2. opponent inventory items 0--5 divided by 20 (6);
3. opponent worker count divided by 3 and active own-job count divided by 3 (2);
4. current worker movement, capacity, harvest, and chop stats divided by 4 (4);
5. current worker carry items 0--5 divided by 10 and free capacity divided by 10 (7);
6. active own-job counts for the six job kinds divided by 3 (6);
7. summed predicted active-job deposits for items 0--5 divided by 20 (6);
8. live plant counts for natural, own, opponent, and ambiguous provenance divided by 20 (4);
9. total fruits on own and opponent plants divided by 40 (2);
10. water-cell and walkable-cell counts divided by 242 (2); and
11. current-worker path distance to the nearest opponent worker, capped at 50 and divided by 50 (1).

For a candidate job, decode its actual action target and append:

1. target x divided by 21 and y divided by 10 (2);
2. path distances from current worker, own shack, opponent shack, and nearest opponent worker to
   the target, each capped at 50 and divided by 50 (4);
3. target plant health/20, size/10, fruits/20, and cooldown/20, or zeros without a plant (4);
4. target adjacent-to-water, occupied-by-own-unit, occupied-by-opponent-unit, and opponent within
   path distance two indicators (4); and
5. for a renewal planting cell, `(opponent_shack_distance - own_shack_distance)/50` and an
   adjacent-to-water indicator, or zeros without a planting cell (2).

Unreachable distance is exactly 50 before scaling. All context values must be finite and deterministic.
The exact combined vector length is 194.

## Single frozen model and grouped discovery

Use `194 -> 8 ReLU -> 1`, positive indicator (`margin_delta > 0`) target, binary cross-entropy with
logits, full-batch Adam, learning rate 0.01, weight decay 0.01, and exactly 600 epochs. Use eight
whole-map folds `(map_seed - 9,773,000) mod 8`; standardization is fit only on each training fold.
Initialization seed is `4,210 + fold` for folds 0--7 and `4,218` for the full fit. There is no early
stopping, alternate seed, width, loss, regularization, ensemble, or feature selection.

Evaluate exactly one threshold: the top 50% of eligible out-of-fold scores with deterministic ties.
Discovery passes only with:

- at least 400 selected rows, including at least 160 with gap below 0.280;
- mean paired margin at least +12 and normal 95% lower descriptive bound above +8;
- positive rate at least 65% and negative rate at most 27%;
- early mean at least +14 and late mean at least +5;
- positive mean in all eight held-out map folds; and
- at least six positive opponent means with none below -10.

If discovery passes, fit the same model twice to all discovery rows and require bit-identical weights
and predictions. Convert standardization into raw first-layer weights with maximum prediction error
`1e-5`. Freeze the full-data threshold reproducing the out-of-fold selected share. The deployable
model has exactly 1,570 scalars including threshold and must remain below 100,000 source bytes when
combined with the current slim resident in a pre-deployment estimate.

## Conditional external continuation gate

Apply the frozen raw model and threshold once to the disjoint external bank. Require:

- at least 160 selected rows, including at least 64 below gap 0.280;
- mean margin at least +8 with normal 95% lower bound above zero;
- positive rate at least 60% and negative rate at most 32%;
- both early and late means positive;
- positive mean on at least six opponent families and none below -15; and
- exact feature/replay integrity and zero action/provenance/prediction failures.

A pass opens a separately frozen complete-policy experiment beginning at map 9,775,000. A failure
at manifest integrity, grouped discovery, determinism, parity, size, or external replication closes
D42 without scoring later banks or tuning this representation.
