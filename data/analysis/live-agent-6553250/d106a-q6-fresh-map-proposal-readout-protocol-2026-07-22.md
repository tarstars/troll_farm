# D106a q6 fresh-map proposal readout — frozen protocol

Date: 2026-07-22  
Status: frozen before new-map root generation or proposal inspection

## Question

D105b's q4 union remains broad on fresh maps but only 47 experts clear the frozen 25%-root activity
floor, versus 48 required, so outcomes stayed sealed. Does the next preregistered precision—six
bits—restore prospective individual activity without losing q4's union breadth, and if so does its
fresh union expose learnable held same-state value?

D106a is a precision robustness adjudication followed conditionally by the exact D105b terminal
and readout experiment. Existing q6 proposals on consumed D105a roots remain unread. No alternate
width, population, threshold, outcome-selected expert, PPO run, candidate, or platform action is
permitted.

## Immutable inputs

- D105b protocol and support result:
  `42b5dd0f689b8d8d7e110d7babf6bcf4ea41b21811c3a28017cbbd8c3720962a` and
  `c431b2619147837a16db15eaeda9488cdb94cd6a3f179b2b44aa3bbc98dbdb59`;
- q4 matched-control population:
  `d32a0c0b6de7856e86ef55090e07807dc52bb676db626e5e2e7d69dd72d50b90`;
- q6 candidate population:
  `87c6ed7d018983b72bcc158b6de0aafd6174873d180fb5f3af51f787f3c03fd8`;
- D97 root generator, D104 proposal runner, and D97 continuation runner:
  `f39748d916be4634b9c2e48dc2e0460fbf3d7c56985d4339786b2b39f2276b23`,
  `c68652529212d9d5067d533d3abee8865667aa821b544b8adce2b7aaff096393`, and
  `e7dd8a8d743c320548897ad264a515223fdb40e05571e01569654aeafafb68e4`;
- union builder and cardinality adapter:
  `e2872dcaadd8826210ee2e902daf7dec4e5522f2910fcf4117fb7699e9bf8a96` and
  `6f5c8e062e7449ed30f5701c1a9b73609fe250a4f3102ccce5ac8427f3866546`.

Six-bit coefficients use the already frozen D105a per-expert symmetric quantizer and require 7,344
packed bytes or 9,180 conservative base85 bytes. No scale is stored because positive per-expert
scale cancels inside each expert argmax.

## New task split and cardinality handling

Use untouched seeds `9,827,000--9,827,015`, both seats, and all eight D40 opponents: 256 tasks.
The first eight maps are discovery; the last eight are held validation. The bank becomes
development-only after this protocol.

Generate D97's unchanged first eligible root/catalog outcome-blindly. Require at least 220 roots.
If the count is at most 240, apply D105b's frozen measurement adapter: pad the smallest existing
roots onto the smallest unused IDs until the D104 audit cardinality reaches 240, run the unchanged
proposal binary, then strip every clone. If the genuine count exceeds 240, stop before proposals
and freeze a behavior-neutral multi-chunk measurement amendment; do not discard genuine roots.

Run q4 and q6 on the identical adapted roots. Proposal reconstruction may inspect only current
state, legal actions, and population weights.

## Frozen q6 selection gates

For each precision deduplicate noncontrol proposals per genuine root and measure support. Q6 is
locked before terminal outcomes only if every condition holds:

1. exact 64-expert/genuine-root grids and 100% legal paired manifest arms for both precisions;
2. at least 14 q6 unique noncontrol proposals per root on average, minimum six, and a q6 joint
   proposal at every root;
3. at least 48 q6 experts emit noncontrol proposals in at least 25% of genuine roots;
4. q6 has at least one more such active expert than matched q4;
5. q6 spans all four jobs, natural/own/opponent provenance, both seats, all families, and reversed
   role order;
6. relative to each root's q4 noncontrol union, q6 has at least 85% mean recall, at least 50%
   minimum recall, and at least 75% mean Jaccard similarity; and
7. q6 base85 coefficient payload is at most 10,000 bytes.

If any gate fails, stop before terminal value. Do not inspect q8 or weaken the D105b activity floor.
If all pass, serialize a q6 union manifest and outcome-blind selection lock before continuations.

## Conditional fresh headroom

Evaluate exact D40 plus the q6 union twice with two independent ten-worker runs and require byte
identity. Reuse every D105b integrity condition. At each rooted task choose the hindsight-best
control or union proposal; unrooted tasks remain D40. Require exactly the unchanged D105b gates:

1. mean gain at least `+25` across all 256 tasks;
2. strict rooted improvement at least 85%;
3. every family mean gain at least `+12`;
4. own-score delta nonnegative and opponent-score delta nonpositive;
5. crop creation 100% and worker-three reach within five points of D40;
6. mean rooted increment over best-single at least `+2`;
7. a joint winner strictly beats best-single in at least 30% of roots; and
8. winner breadth of three jobs, two provenance classes, both seats, all families, and reversed
   role order.

Only a full headroom pass opens fitting. Hindsight arms remain unselectable.

## Conditional discovery readout

Reuse D105b's feature map exactly: 45 proposal-semantic fields, 64 expert-endorsement bits, and the
outer product of the semantic vector with six observable root-context fields, all expressed as an
arm-minus-control vector. Opponent identity, map seed, seat label, terminal state, and future
information remain excluded.

Fit on every noncontrol discovery arm only. Target same-root margin delta clipped to `[-100,100]`;
give each root equal total weight rescaled to mean row weight one; divide features by discovery RMS;
fit no-intercept ridge with fixed `alpha=100`. On held roots choose the highest-scoring noncontrol
arm only if its score is strictly positive, otherwise exact control; ties are lexical. The
semantic-only and endorsement-only versions are diagnostics only.

Require the unchanged held gates across 128 tasks:

1. 15%--80% rooted activation, at least three jobs, two provenance classes, both seats, all
   families, and at least 10% joint selection;
2. mean realized gain at least `+2` over all held tasks;
3. strict improvement in at least 20% of held roots and 55% of activated roots;
4. every held family mean at least `-3` and at least six positive;
5. at least 15% held union-oracle value capture; and
6. crop creation 100% with worker-three reach within five points of held D40.

## Decision

- **Selection fail:** close q6 before outcomes; do not inspect q8 on these maps.
- **Selection passes, headroom fails:** close the proposal bank as nonreplicating.
- **Headroom passes, readout fails:** retain q6 action support but close offline ridge; next test
  direct online/recurrent learning on new maps.
- **All pass:** freeze q6 and the proposal feature ABI, then open a bounded complete online
  controller preflight on new maps.
- **Integrity failure:** repair measurement only.

No branch authorizes TestSession, Arena, candidate construction, submission, or resident change.
