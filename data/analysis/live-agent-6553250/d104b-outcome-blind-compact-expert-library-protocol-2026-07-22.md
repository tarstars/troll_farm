# D104b outcome-blind compact expert library — frozen protocol

Date: 2026-07-22  
Status: frozen before subset construction or value join

## Question

D104a proves that the union of 64 frozen D98 experts exposes 16.642 distinct noncontrol proposals
per D97 root and retains `+31.859` hindsight margin, but the 64 unique decimal weight vectors alone
occupy roughly 115 kB. Can a proposal-coverage-only subset of at most twelve experts retain enough
support and causal value to serve as the action generator for a sub-100 kB online controller?

D104b is compression of a validated action representation, not policy or arm selection. Expert
selection may inspect only proposal identities and current-state action semantics. Terminal scores,
D97 winners, D104a oracle rows, opponent-family deltas, and outcome ranks remain unread until the
single subset is irrevocably fixed.

No new simulation, fitting, policy execution, candidate, platform access, submission, or resident
change is permitted.

## Immutable inputs

- D104a proposals:
  `54bd509e60d83d3caa09d9dfed310b1e7422e186935917ec529bd854c7f07cd9`;
- D104a result:
  `c27e5ac38aabbb91ce02f175dd130d7edc01b6d9294f2817186ca26dd951f8bc`;
- D98 population:
  `3bff0c4a9ddffdf33bac305a23a99e1f5a04655c5d6bb7af428697b237db253e`;
- D97 manifest:
  `ed5a6ffeb73032006fed7e08518e82c6cf549e2b8f24f7798cbceb82837c157e`;
- D97 arms:
  `c6ee144a4c89d4a504d7c7bf356628a7b3fc506b1ba29b991c1cc0caa0b08d33`;
- D97 baselines:
  `8936d7007074a240f21073aea4c5fa43851093cfd90e1827a4fe4370609b40b6`.

## Frozen outcome-blind greedy subset

Construct each expert's set of supported noncontrol tokens `(root_id, arm_id)` from D104a. Also
mark whether each token is joint. Begin with an empty ordered subset. At each step evaluate every
unused expert by this exact lexicographic tuple, choosing the maximum and breaking the final tie by
the lower expert index:

1. number of roots currently below three unique noncontrol proposals for which the expert adds a
   new token;
2. number of roots currently without a joint proposal for which the expert adds a joint token;
3. total number of new noncontrol tokens; and
4. negative expert index.

After adding an expert, recompute support. Stop at the first prefix satisfying every selection gate:

1. mean unique noncontrol proposals per root at least six;
2. minimum unique noncontrol proposals at every root at least three;
3. a joint proposal at at least 90% of roots;
4. all four jobs, natural/own/opponent provenance, both seats, all eight opponent families, and a
   reversed worker-role order occur in the union; and
5. exact selected decimal coefficient payload is at most 30,000 bytes.

Fail if no prefix through twelve experts passes. Do not inspect values of shorter, longer, alternate,
or manually chosen subsets. Serialize the selected expert order, weight hashes, support trajectory,
and SHA-256 lock before loading D97 terminal arms.

Coefficient payload is the UTF-8 byte length of the selected population rows' 153 parameter fields
joined exactly by tabs and newlines, excluding labels/kind/budget/header. It is a conservative
source-size proxy, not a final packaging claim.

## Integrity gates

1. all immutable hashes match and the D104a 15,360-row grid has zero duplicate/missing keys;
2. expert hashes reconstruct from the D98 population and match every D104a row;
3. subset construction completes before the arm/baseline files are read;
4. rerunning selection produces the identical ordered subset and lock;
5. every compact proposal maps to the same immutable D97 arm as D104a; and
6. D97 control/terminal integrity and the full D104a union metrics reproduce exactly.

Any failure permits measurement repair only.

## Frozen compact-union value gates

After the subset is locked, use exact D97 control plus its deduplicated proposals at each root with
the unchanged D104a hindsight tie order. Tasks without roots remain D40. Require all:

1. mean margin gain over D40 at least `+25`;
2. retain at least 80% of D104a's `+31.859375` proposal-union gain;
3. capture at least 65% of D97's full joint-or-control gain;
4. strictly improve at least 75% of rooted tasks;
5. every opponent-family mean gain at least `+10`;
6. mean own-score delta nonnegative, opponent-score delta nonpositive, crop creation exactly 100%,
   and worker-three reach within five points of D40;
7. mean rooted gain at least `+2` beyond D97's complete best-single oracle;
8. select a joint proposal in at least 35% of roots and have it strictly beat the best-single
   oracle in at least 15%; and
9. selected proposals retain at least three jobs, two provenance classes, both seats, all families,
   and a reversed worker-role order.

No expert or proposal is individually selectable from favorable outcomes.

## Decision rule

- **Full pass:** freeze the compact expert order and open the fresh-map D104c recurrent
  opponent-aware proposal-controller mechanics/signal preflight.
- **Selection/support failure:** close exact embedded D98 experts as a deployable library. Do not
  raise the twelve-expert or 30 kB caps after inspection.
- **Value failure:** close coverage-only compression; do not choose an outcome-favorable subset or
  weaken the retained-value gates.
- **Integrity failure:** repair measurement only.

No result authorizes PPO-scale training, packaging, TestSession, Arena, submission, or resident
mutation.
