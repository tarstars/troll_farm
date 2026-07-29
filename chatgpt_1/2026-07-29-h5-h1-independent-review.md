# Independent review: H5 postmortem intelligence and H1 joint-economy bound

Updated: 2026-07-29T13:24:00Z
Reviewer: `chatgpt_1`
Session evidence inspected through: `f28cf772d5545fe8bac500a91e802c9fd366e815` plus the integrated H5/H1 commits visible on `session-2026-07-01`

## Executive verdict

- **H5: ACCEPT with one material causal correction.** The restored Yann Moisan postmortem is authentic and the live resident clearly descends from, and implements the documented core of, that #3 contest design. H13 is the strongest cheap lead. However, the current 2.94 practice-ladder gap to the current `yamo` agent is a diagnostic gap, not proof that 2.94 points are implementation fidelity. Current `yamo` may have changed after the contest; the postmortem is incomplete; and ratings are not a matched causal comparison.
- **H1: ACCEPT the closure of the resident patch; CORRECT the statistical and “upper bound” characterization.** The result robustly rejects harvesting/mining/planting/training-cap grafts on the current scheduler. The own-side-only optimistic sensitivity is already negative, and worker four is never affordable. But the reported confidence interval is conditional on a fixed accounting model, not a full uncertainty interval, and the construction has both upward and downward biases. Call it a robust finite-windfall accounting stress test, not a formal upper bound on every four-lever complementarity.
- **Backlog consequence:** prioritize H13 before H6 implementation and before an Architecture-2 programme. Preserve H6 only as the narrow candidate-pair depth audit in `chatgpt_1/h6-bounded-lookahead-preflight.md`. Treat H2 as unproven and constrained: a new architecture must first explain a renewable resource base, while H13 tests whether a fixed-two-worker design can recover a large part of the gap without new architecture.

## H5 source review

### Sources and identity

The archived primary source at `docs/reference/yann-moisan-postmortem-2026-05-26.txt` identifies Yann Moisan, dates the postmortem 2026-05-26, and records rank #3 Legend / 2022. The same page remains publicly available. The official contest page records the contest outcome; the CodinGame feedback thread contains contemporaneous strategy statements from putibuzu and others; delineate’s linked gist documents the #1 neural approach.

The repository’s restored `docs/reference/2026-07-11-yannbot-design.md` explicitly says it is a reproduction plan for Yann’s #3 design. The current resident source contains the same distinctive mechanisms:

- fixed two-worker strategy;
- strongest affordable second worker;
- wood-per-round-trip chop scoring;
- first-turn LEMON/PLUM `typeToCut` choice;
- denial scoring only while the opponent has at most two trolls;
- tree-state prediction;
- exact compatible-pair enumeration at two workers;
- endgame bank rush, planting, and opponent-shack waiting.

This is far more specific than a generic strategic resemblance. “The resident implements the published design family” is well supported.

### Material correction: the 2.94 gap is not yet attribution

The integrated H5 ledger says the current resident is 2.94 rating points below current `yamo`, and that this is “by construction” non-architectural. That inference is too strong for four reasons:

1. Yann’s postmortem describes the contest-final bot, while the practice-ladder `yamo` agent observed in July may have been changed after 2026-05-25.
2. The postmortem explicitly under-specifies parameters such as the alternative denial formula and training tradeoffs; the repository reproduction spec itself lists these as measurement gaps.
3. A ladder rating difference is not a same-map, same-opponent, same-window causal delta. Pool composition, battle sampling, and maturity differ.
4. Our resident contains validated improvements and later accretions. A behavioral difference can be an intended improvement, an unvalidated divergence, a current-yamo evolution, or a meta-distribution interaction—not necessarily a reproduction bug.

Therefore H13’s estimand must be split:

- **Design fidelity:** published contest-final statement versus resident source/behavior.
- **Current-yamo behavioral gap:** resident versus current `yamo` on matched opponents/maps/replay-derived states where possible.
- **Value attribution:** causal testing of one isolated deviation only after it is classified.

The 2.94 number is a prioritization signal and possible ceiling, not the expected value of “restore fidelity.”

### Strategy implications

The public field is genuinely split:

- Yann’s #3 bot is a two-worker heuristic without multi-turn search.
- putibuzu reports two workers, depth-3/5/7/9/12 rollouts, and a three-ply beam search.
- delineate reports a neural policy with no per-turn lookahead and millisecond inference.

This supports neither “search is necessary” nor “search is useless.” It supports H6 only as a resident-specific measured oracle-gap question. It also weakens any claim that scaling is the only architectural route: two top contest strategies deliberately stayed at two workers. Conversely, current practice-ladder correlations that price workers remain valid observations. The conflict must be resolved empirically, not by choosing one era’s ranking as authority.

### H5 review disposition

Accept:

- authenticity and relevance of the restored primary sources;
- correspondence between the published Yann design and resident mechanisms;
- H13 as the strongest cheap lead;
- source evidence that top strategies disagree about search and scaling.

Correct:

- change “2.94 points are by construction fidelity/meta drift” to “2.94 points define a diagnostic practice-ladder gap requiring matched decomposition”;
- do not treat missing pseudonym-attributable write-ups as proof that no private/public postmortem can exist; report only the searched absence;
- keep contest-final strategy and July practice-ladder behavior separate throughout H13.

## H1 methodology review

### What the analyzer gets right

`cgauto/joint_economy_upper_bound.py` fixes the two central errors in earlier affordability audits:

- it reads each game’s revealed live worker talent vector rather than substituting a synthetic cheap helper;
- it uses post-MOVE shack occupancy for TRAIN legality.

It also:

- credits fruit and iron before charging collection displacement, making the resource side intentionally optimistic;
- cascades worker-three payment before asking whether worker four is affordable;
- reports the D175 opponent-leak extrapolation separately from an own-side-only optimistic sensitivity;
- documents possible double counting of holistic worker value and direct fruit value;
- keeps the four-lever resident implementation rejected and performs no modified-bot simulation.

These choices make the result useful and much more trustworthy than B3.8/B3.9’s synthetic-spec headline.

### Why the resident-patch closure is robust

Three findings survive the model caveats:

1. Worker four is affordable in 0/220 games even after optimistic finite-resource credit.
2. The primary full-displacement estimate is strongly negative.
3. More importantly, the **own-side-only** optimistic sensitivity—setting added opponent leakage to zero—is still negative, about −2.49 rating with only 6/220 games positive.

That last sensitivity removes the dominant, acknowledged D175 extrapolation. It is sufficient to reject the proposed four-lever graft on the resident, especially given the unpriced coordination and policy-selectability costs would generally make a real implementation worse.

### Corrections to interpretation

#### 1. It is not a formal upper bound on every joint complementarity

The model is upward-biased in several useful ways:

- resources are credited without requiring a fully specified feasible scheduler;
- collection walking is often treated as shared/en-route;
- field worker value may overlap future production value, causing double counting;
- opponent adaptation and coordination breakage are ignored.

But one component is downward relative to the literal four-lever hypothesis: additional early crops are credited using D175’s planting-only reap rate of 0.4523%, while harvest-capable trained workers are one of the four proposed complements. The analyzer excludes the peer reap-rate bracket because crop survival/protection is a fifth mechanism, which is reasonable, but this means the grounded calculation is not a mathematical upper bound on all fruit enabled by the four levers. It is a conservative grounded bracket combined with optimistic existing-resource credit.

Use: **finite-windfall accounting stress test** or **grounded net accounting bound under stated collection and planting brackets**.

#### 2. The reported CI is conditional, not total uncertainty

The normal-approximation CI varies per-game outcomes while holding fixed:

- margin-per-rating conversion;
- worker-existence price;
- D175 opponent/own elasticity;
- value per chop turn;
- action-turn assumptions;
- early-crop reap and fruit-yield constants;
- dependence among games, opponents, and maps.

It therefore does not propagate the dominant model uncertainty and is not a confidence interval for the real causal effect of an implemented package. Clustered or bootstrap uncertainty would improve sampling uncertainty, but no statistical resampling can identify the missing structural counterfactual.

The correct claim is “negative throughout the reported credible sensitivity set,” not “causal effect equals −21.33 with CI …”.

#### 3. Worker-value pricing is coarse

Every affordable worker three receives a constant +22.7 margin regardless of talent vector, training turn, remaining horizon, map, or opponent. This is defensible as a generous field-derived scalar, but not a state-specific upper bound. The analyzer itself notes holistic-value overlap. This coarseness does not rescue the resident patch because the own-side result remains negative and worker four never appears, but it limits fine attribution among levers.

### H1 review disposition

Accept:

- H1 is closed as a resident patch;
- finite natural-tree windfall cannot create the renewable stream needed for worker four;
- Architecture-2, if pursued, must demonstrate renewable production rather than reuse this package;
- the result does not itself close H2.

Correct:

- narrow “upper bound” terminology;
- label numerical intervals as model-conditional sampling intervals;
- avoid treating the D175 opponent ratio as independently validated outside its intervention scale;
- preserve the own-side-only sensitivity as the load-bearing rejection result.

## Consequences for active work

1. **H13 becomes P0.** Its first deliverable should be a fidelity matrix, not a candidate: published claim → resident implementation → current-yamo observed behavior → prior D-series validation status.
2. **H6 remains P1 and phase-gated.** H5 demonstrates that successful agents span no-search and deep-search designs; it does not justify generic rollout. Use the candidate-pair preflight already published.
3. **H2 is deferred, not dead.** H1 demands a renewable-base proof; H5 shows a strong fixed-two-worker design may still have recoverable execution/fidelity value. Revisit H2 after H13 and the H6 Phase-0 verdict.
4. **Do not reopen B4.4 planting tempo from H5 alone.** Yann’s contest statement and July practice replay statistics concern potentially different binaries and measurement definitions. Re-audit provenance before citing either as causal evidence.

## Recommended integration wording

- H5: “The resident implements the documented core of Yann Moisan’s #3 contest design. Current `yamo` leads it by 2.94 practice rating points, creating a high-value fidelity/meta-drift diagnostic; the gap is not yet causally attributable.”
- H1: “A grounded finite-resource accounting stress test is negative even with zero added opponent leakage, closing the four-lever resident graft. The exact numerical interval is conditional on the accounting model; H2 remains open but must prove a renewable resource base.”
