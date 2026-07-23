# D104a D98 expert-proposal coverage — frozen protocol

Date: 2026-07-22  
Status: frozen before implementation or proposal reconstruction

## Question

D103 localizes D40's opponent-growth loss to a mixed post-scale/common-horizon (`+25.715`) and
terminal-duration (`+30.748`) failure. D100b also proves that choosing one D98 policy from map,
seat, or opponent identity does not transfer. Before building another complete learner, determine
whether the 64 frozen D98 independent scorers are useful in a different role: a diverse library of
**current-state joint assignment proposals** that a future online trajectory controller could
choose among at every natural two-worker boundary.

D104a is a retrospective representation audit. It reconstructs proposals only and joins them to
terminal continuations already measured and consumed by D97. It may not fit or select an expert,
train a model, change an action, run a new terminal outcome, create a candidate, access the
platform, submit, or change the resident.

## Why this is a new abstraction

- D98 applies one fixed independent scorer for an entire task.
- D100b selects one fixed scorer from static task information.
- D104a instead treats every scorer as an action proposer at the same live state. A later policy
  would be free to choose a different proposal at each boundary from observable trajectory state.

This does not reopen D99's from-scratch pair scorer or D100's pair residual. The prospective action
would be a complete collision-safe assignment already proposed by a frozen independent surface;
the future learner would allocate authority among proposals rather than rescore the full Cartesian
pair catalog.

## Immutable inputs

Require these exact SHA-256 values:

- D97 manifest:
  `ed5a6ffeb73032006fed7e08518e82c6cf549e2b8f24f7798cbceb82837c157e`;
- D97 arm matrix:
  `c6ee144a4c89d4a504d7c7bf356628a7b3fc506b1ba29b991c1cc0caa0b08d33`;
- D97 baseline matrix:
  `8936d7007074a240f21073aea4c5fa43851093cfd90e1827a4fe4370609b40b6`;
- D98 population:
  `3bff0c4a9ddffdf33bac305a23a99e1f5a04655c5d6bb7af428697b237db253e`;
- D97 manifest generator:
  `f39748d916be4634b9c2e48dc2e0460fbf3d7c56985d4339786b2b39f2276b23`; and
- D98 population runner:
  `49a2c204ec1df3aaf79facdcd39e44cd250458535494a8cf4b6b8de1ff077dfd`.

Use only the 64 `four_00..four_63` weight vectors. `one_*` duplicates and `zero_control` are not
proposal experts.

## Exact proposal reconstruction

For every one of D97's 240 frozen roots, replay exact D40 to the recorded decision and require the
root turn, state hash, observation hash, candidate count, worker identity, live own crops, and
first catalog hash to match the immutable manifest.

Reconstruct D98's 56 global features at the current Train batch using the same completed-batch
bookkeeping as the frozen D98 runner. Each expert then proposes a local pair from this common root:

1. score D97's exact renewable-safe first catalog with D98's exact 153-feature independent dot
   product, first-position bit, and remaining budget four; fixed score zero means keep;
2. apply the selected first action to a cloned exact root;
3. if the result is still a same-turn ordinary Rate worker decision, rebuild the exact D97 second
   catalog with live reservations and score it with the second-position bit and remaining budget
   three after a nonkeep first action, otherwise four; and
4. form the exact D97 arm id from the two selected concrete labels.

The expert is a local proposer, so its D98 whole-game intervention history is deliberately absent;
all experts see the same actual root and the controller's common initial budget. This is the ABI a
future online mixture would use, not a replay of 64 diverged D98 trajectories.

If a selected first action does not preserve the paired boundary, record it as unsupported rather
than inventing an unmeasured continuation. Never substitute another option. Add exact D40 control
to every root's proposal set independently of expert outputs.

Run proposal reconstruction once with one worker and once with twenty workers, sort by
`(root_id, expert)`, and require byte-identical TSVs.

## Integrity gates

All must pass before value is interpreted:

1. both runs contain exactly `240 x 64 = 15,360` unique rows and are byte-identical;
2. every frozen source/input hash matches;
3. every root reconstructs all frozen identities and every expert reconstructs the frozen D98
   weight hash;
4. every supported proposal maps to exactly one immutable D97 arm with matching first/second
   actions, labels, class, and arm kind;
5. unsupported proposals are reported explicitly and no outcome is synthesized for them;
6. the immutable D97 control, best-single, and joint-or-control summaries reproduce the published
   D97 values, including `+36.852` all-task joint-or-control gain and `+9.208` rooted incremental
   gain over the best single; and
7. all joined terminal rows retain zero D97 command/provenance/deposit/reward/crop/workforce
   integrity failures.

Any failure permits measurement repair only under the unchanged inputs and thresholds.

## Proposal support gates

Require all of the following:

1. at least 95% of expert/root proposals are supported D97 arms;
2. mean unique supported noncontrol proposals per root is at least six;
3. at least 90% of roots expose at least three unique supported noncontrol proposals;
4. at least 80% of roots expose a supported joint proposal;
5. the union spans all four job kinds, natural/own/opponent provenance, both worker orders, both
   seats, and all eight opponent families; and
6. at least 48/64 experts make a supported noncontrol proposal in at least 25% of roots.

## Frozen proposal-union value gates

At each root choose hindsight only among exact control and unique supported expert proposals, with
tie order higher margin, higher own score, lower opponent score, fewer nonkeep actions, then
lexical arm id. Tasks without a D97 root contribute exact D40 and zero delta. The proposal library
passes only if all hold:

1. proposal-union oracle mean margin gain over D40 is at least `+25` across all 256 tasks;
2. it captures at least 65% of the immutable D97 joint-or-control oracle gain;
3. it strictly improves at least 75% of rooted tasks;
4. every opponent-family all-task mean gain is at least `+10`;
5. mean own-score delta is nonnegative, mean opponent-score delta is nonpositive, crop creation is
   exactly 100%, and worker-three reach is within five percentage points of D40;
6. on rooted tasks it gains at least `+3` mean margin beyond D97's full best-single-or-control
   oracle;
7. a joint proposal is selected in at least 40% of roots and strictly beats the full best-single
   oracle in at least 20% of roots; and
8. selected proposals span at least three job kinds, two provenance classes, both worker orders,
   both seats, and all eight opponent families.

No expert id, proposal, arm, root, target, or hindsight winner is selectable from this audit.

## Decision rule

- **Full pass:** freeze the proposal ABI and open D104b: a fresh-map, complete recurrent
  opponent-aware controller that chooses among deduplicated proposals online, with exact D40
  fallback, explicit authority accounting, robust whole-trajectory objectives, and a separate
  mechanics/signal preflight before expensive PPO or lineage search.
- **Support failure:** close the D98 bank as an action library. Do not enlarge it, rescale weights,
  add D99 pairs, or inspect favorable experts.
- **Value failure:** close expert-mixture control even if proposal diversity is broad; the missing
  value is not exposed by these actions.
- **Integrity failure:** repair measurement only and repeat the exact audit.

No branch authorizes fresh terminal maps, a candidate, packaging, TestSession, submission, Arena,
or resident mutation.
