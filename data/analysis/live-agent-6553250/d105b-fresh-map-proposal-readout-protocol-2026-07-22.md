# D105b fresh-map proposal readout — frozen protocol

Date: 2026-07-22  
Status: frozen before fresh root generation, proposal reconstruction, terminal continuation, or fit

## Question

D105a proves on consumed D97 roots that the locked four-bit bank preserves a broad, high-value
joint proposal union. Does that union replicate on fresh maps, and can one fixed discovery-only
readout use current-state expert endorsements plus concrete job semantics to select profitable
proposals on held maps while retaining exact D40 abstention?

D105b is a bounded same-state signal preflight. It changes one two-worker assignment at the first
eligible D40 boundary and then returns permanently to D40. It does not evaluate a repeated
whole-game controller, train PPO, construct a candidate, access the platform, submit, or mutate the
resident.

## Immutable implementation

- D97 outcome-blind root/catalog generator:
  `f39748d916be4634b9c2e48dc2e0460fbf3d7c56985d4339786b2b39f2276b23`;
- D104 proposal runner:
  `c68652529212d9d5067d533d3abee8865667aa821b544b8adce2b7aaff096393`;
- D97 continuation runner:
  `e7dd8a8d743c320548897ad264a515223fdb40e05571e01569654aeafafb68e4`;
- outcome-blind union-lock builder:
  `e2872dcaadd8826210ee2e902daf7dec4e5522f2910fcf4117fb7699e9bf8a96`;
- locked D105a q4 population:
  `d32a0c0b6de7856e86ef55090e07807dc52bb676db626e5e2e7d69dd72d50b90`;
- D105a selection lock:
  `2e045d4b22cc8eb605ac343f61ca96f03c867ee24d866963bb7c5256849affd6`.

The D97 executor, exact D40 teacher, candidate catalog, collision handling, persistence,
transactions, provenance, and terminal continuation remain unchanged.

## Fresh task split and outcome-blind lock

Use official local seeds `9,826,000--9,826,015`, both seats, and all eight unchanged D40 opponent
modes: 256 tasks. Seeds `9,826,000--9,826,007` are discovery and
`9,826,008--9,826,015` are held validation. This entire bank becomes development-only after this
protocol and can never support candidate confirmation.

Generate D97's unchanged first eligible two-worker Rate root and complete concrete arm catalog for
every task. Before any arm reaches terminal:

1. run all 64 locked q4 experts at every root with the unchanged D104 proposal ABI;
2. require a complete expert/root grid and every proposal to match a legal manifest arm;
3. retain exactly the deduplicated proposal union plus the exact control arm at each root;
4. preserve manifest order and serialize all source hashes, selected-arm identity hash, support,
   and `outcomes_read=false` in an immutable lock.

No outcome, winner, opponent-family statistic, expert success, or alternate precision may affect
the arm union.

Require before terminal access: at least 220 roots; at least 14 unique noncontrol proposals per
root on average and at least six at every root; a joint proposal at every root; at least 48 experts
noncontrol-active in 25% of roots; and union coverage of all jobs, natural/own/opponent provenance,
both seats, all families, and reversed role order.

## Continuation and integrity

Evaluate exact D40 for all 256 tasks and every locked arm twice with two independent ten-worker
runs. Sort using the unchanged D97 output order and require byte-identical arm and baseline files.
Require exact manifest/action mirrors, one control per root, control parity with uninterrupted D40,
finite rewards, exact margin and action-plane accounting, at most three own workers, and zero
illegal direct commands, provenance failures, deposit-prediction failures, duplicate/missing arms,
or crop-creation failures.

Any integrity failure quarantines value and permits measurement repair only under the unchanged
lock.

## Frozen fresh-union headroom gates

At each rooted task choose hindsight-best control or union proposal by higher margin, higher own
score, lower opponent score, fewer nonteacher actions, then lexical arm id. Unrooted tasks remain
D40. Compare the complete union with the best control-or-single proposal. Require all:

1. mean union gain over D40 across all 256 tasks at least `+25`;
2. strict improvement in at least 85% of rooted tasks;
3. every opponent-family mean gain at least `+12`;
4. mean own-score delta nonnegative and opponent-score delta nonpositive;
5. crop creation exactly 100% and worker-three reach within five points of D40;
6. mean rooted increment over best-single at least `+2`;
7. a joint winner strictly beats best-single in at least 30% of roots; and
8. winners span at least three jobs, two provenance classes, both seats, all families, and reversed
   worker-role order.

Hindsight winners remain unselectable. Only a full headroom pass opens the readout fit.

## Frozen proposal feature map

For every locked arm, form an outcome-blind raw representation from the manifest and q4 proposal
matrix. It contains:

- a 45-field semantic vector: noncontrol bias; arm-kind one-hot; first/second executed class
  one-hots over `keep/fell/harvest/renew/mine`; first/second provenance one-hots over
  `none/natural/own/opponent/ambiguous`; normalized prior ranks; target presence and normalized
  row/column; eight predicted-deposit values divided by ten; nonteacher-action fraction; second
  candidate/catalog sizes; and expert vote share;
- 64 binary expert-endorsement fields; and
- the outer product of the semantic vector with six observable root-context fields: turn/300,
  decision ordinal/200, live own crops/20, root candidate count/100, first catalog size/16, and
  first worker ordinal/2.

Subtract the exact control representation for the same root, leaving control identically zero.
Opponent identity, nickname, map seed, seat label, terminal fields, D105a winners, and future state
are excluded. This is a memoryless current-field readout; recurrence is deliberately deferred
until current-state learnability is known.

## Frozen discovery fit and held selection

Use every noncontrol discovery arm. Target its terminal margin delta from the same-root control,
clipped to `[-100,100]`. Give every root equal total weight, rescaled so mean row weight is one.
Scale each feature by discovery root-mean-square, replacing zero scales by one. Fit one no-intercept
ridge readout with `alpha=100`:

`beta = (X'WX + 100 I)^-1 X'W y`.

No threshold, alpha, clipping, feature, map, arm, or opponent selection may use held outcomes. On
each held root, score every noncontrol arm and choose the highest only when its predicted value is
strictly positive; otherwise choose exact control. Prediction ties use lexical arm id. Semantic-only
and endorsement-only fits may be reported as fixed diagnostic ablations, but cannot replace the
combined primary readout.

## Frozen held-signal gates

Across held validation, counting unrooted tasks as zero gain, require all:

1. activate on 15%--80% of held roots and use at least three job kinds, two provenance classes,
   both seats, all families, and at least 10% joint proposals;
2. mean realized margin gain at least `+2` across all 128 held tasks;
3. strict improvement in at least 20% of held rooted tasks and at least 55% of activated roots;
4. every family mean gain across held tasks at least `-3`, with at least six positive families;
5. capture at least 15% of the held union-oracle mean gain; and
6. selected crop creation exactly 100% and worker-three reach no more than five points below held
   D40.

The readout is a signal artifact, not a candidate.

## Decision rule

- **Headroom and held readout pass:** freeze the proposal feature ABI/readout as initialization
  evidence and open D105c, a fresh complete recurrent/online controller preflight with D40
  fallback and a bounded intervention budget.
- **Headroom passes, readout fails:** retain the q4 action basis but close this offline ridge target;
  next test direct online policy learning or a genuinely recurrent representation on new maps.
- **Fresh headroom fails:** close the D104/D105 proposal bank as consumed-panel-specific.
- **Integrity failure:** repair measurement only.

No branch authorizes TestSession, Arena, candidate construction, submission, or resident change.
