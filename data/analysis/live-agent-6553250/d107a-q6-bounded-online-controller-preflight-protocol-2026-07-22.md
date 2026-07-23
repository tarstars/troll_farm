# D107a q6 bounded online controller preflight — frozen protocol

Date: 2026-07-22  
Status: frozen before controller population generation or fresh-panel execution

## Question

D106a proves that the compact q6 expert bank supplies broad, replicating one-deviation value, but
its frozen static ridge cannot abstain safely. Before building PPO, does the same proposal bank form
a mechanically exact, sufficiently active, repeated whole-game control interface, and do multiple
online interventions expose value beyond a matched one-intervention controller?

D107a is a representation preflight, not policy selection. It evaluates a frozen random linear
population only to measure action support, closed-loop activity, and population-oracle headroom.
No hindsight policy or trajectory may become a candidate, parent, resident, or supervised label.

## Immutable inputs and ABI

- q6 64-expert population:
  `87c6ed7d018983b72bcc158b6de0aafd6174873d180fb5f3af51f787f3c03fd8`;
- D106a result JSON and report:
  `22b6e15a62a96df5a1661ed267680370dee24a43fc03029d26b3f15b2be4f551` and
  `e29b37a60a94fddb058591f7a3c976af97ee2f59b60036df73d62852d8eee6f4`;
- D107a controller generator:
  `ec2d216e307c8999895d7ea5c8ac0a013bfe8c237018638c37473018a873db0f`;
- D107a whole-game runner:
  `b15214ee87ca925cb43b565f31815f169d6e18c4105abbb4d776a3cc687e860a`.

At the first eligible two-worker `Rate` boundary of each D40 training batch, provided live own
crops exist and at least 30 turns remain, reconstruct all 64 q6 proposals. Every expert always
uses its original D104 assignment budget: four for the first worker and three after a nonteacher
first choice. Deduplicate exact paired actions, retaining all 64 endorsement bits. Exact D40 is
always present and legal.

Score each noncontrol proposal using D106a's exact 379-value arm-minus-control ABI: 45 semantic
values, 64 endorsement bits, and 270 products of the semantic vector with six observable live
context values. Choose the largest score only when it is strictly positive; otherwise choose exact
D40. Ties are lexical. An intervention budget counts selected noncontrol *batches*, not proposal
enumerations or individual worker assignments. Other decisions remain exact D40.

## Frozen outcome-blind controller population

Generate one zero controller followed by 64 matched one-use/four-use pairs. Use NumPy PCG64 seed
`10701`, draw each 379-vector independently from `Normal(0, 0.25)`, and round to eight decimals.
Replace coefficient zero—the arm-minus-control noncontrol indicator—with
`-0.15 * (1 + index mod 16)`, giving a fixed `-0.15` through `-2.40` abstention ladder. Matched
pairs share every coefficient and differ only in intervention budget, one versus four.

This ladder was calibrated without terminal fields on D106a's already-consumed proposal geometry:
39/64 vectors activate on 10%--90% of first eligible roots. No reward, score, outcome, selected arm,
or fresh state was inspected. Do not change the seed, scale, ladder, population size, or threshold
after fresh execution.

## Fresh panel and execution

Use untouched seeds `9,829,000--9,829,007`, both seats, and all eight D40 opponents: 128 tasks.
Run the complete 129-policy population twice, each time with 20 workers and new output paths.
Sort output deterministically. The second run is reproducibility only and may not alter analysis.

## Integrity gates

All must pass before activity or value interpretation:

1. the generator reconstructs exactly and yields one zero plus 64 coefficient-identical
   one/four pairs, each with 379 finite values;
2. each run contains exactly 128 D40 baselines and `129 * 128 = 16,512` policy rows with complete
   policy/task grids, and the two baseline files and two population files are byte-identical;
3. all 128 zero rows reproduce D40 terminal fields and action-plane counts exactly;
4. every episode has finite rewards, reward-identity error at most `1e-5`, zero invalid direct
   commands, provenance failures, and deposit-prediction failures;
5. noncontrol intervention batches never exceed the policy budget; zero has none; every recorded
   intervention contains one or two nonkeep assignments; and all counters reconcile;
6. at every enumerated boundary, supporter occurrences equal exactly 64 expert occurrences and
   there is at least one legal proposal including control; and
7. crop creation remains 100%, while the worker-three rate is no more than five percentage points
   below matched D40 for both one-use and four-use populations.

An integrity failure authorizes only a behavior-neutral repair and a new protocol/hash if needed.

## Frozen activity gates

Read activity before terminal margins. Require all of:

1. at least 110/128 zero-control trajectories expose one or more eligible boundaries;
2. zero-control q6 support averages at least 14 unique noncontrol proposals per eligible boundary,
   never fewer than six, with mean expert occurrences per boundary exactly 64;
3. at least 32/64 four-use controllers intervene on 10%--90% of tasks, and at least 48 intervene
   on at least one task;
4. at least 24 four-use controllers use two or more interventions on at least 10% of tasks;
5. at least 24 matched pairs have strictly more total four-use than one-use interventions; and
6. aggregate four-use selections include joint proposals, all four jobs, natural/own/opponent
   provenance, both seats, and all eight opponent families.

If activity fails, stop before margins and redesign only the controller/mask representation on new
maps. Do not tune this population on the fresh panel.

## Conditional population-headroom gates

For each task construct two descriptive hindsight oracles: D40 plus all 64 one-use rows, and D40
plus all 64 four-use rows, maximizing terminal margin with lexical ties. These oracles are
unselectable. Require all of:

1. four-use oracle mean gain at least `+20` over D40 and strict improvement in at least 70% of all
   tasks;
2. every opponent-family four-use oracle mean gain at least `+8`;
3. four-use oracle mean own-score delta is nonnegative and mean opponent-score delta nonpositive;
4. four-use oracle adds at least `+3` mean margin beyond the matched one-use oracle and strictly
   beats it on at least 20% of tasks;
5. selected four-use oracle trajectories preserve 100% crop creation and remain within five
   percentage points of D40's worker-three rate; and
6. four-use oracle winners span at least 16 distinct controllers, both seats, all opponent
   families, joint interventions, at least three jobs, and at least two provenance classes.

## Decision

- **Integrity failure:** repair measurement only; do not interpret outcomes.
- **Activity failure:** close this parameterization and redesign the online action/mask ABI.
- **Activity passes, headroom fails:** retain q6 one-step evidence but close repeated bounded
  intervention as the immediate learning target.
- **Full pass:** freeze the D107a executor and proposal ABI, then open D108a: a recurrent masked
  controller trained directly on whole episodes with exact D40 action zero and a maximum of four
  noncontrol batches. Training and validation must use new maps; D107a rows remain diagnostics only.

No branch authorizes TestSession, Arena, candidate construction, submission, or resident change.
