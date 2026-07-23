# Norxondor worker-rich controller — Phase 10 verdict, 2026-07-18

## Outcome

**The Norxondor architecture is now understood well enough to reproduce its workforce ladder and
build productive multi-worker research controllers, but no integrated policy is promotion-ready.
Keep the exact 62,725-byte resident. Close direct schedule and signature switching; advance only
the state-level resident-versus-three-worker Monte Carlo branch experiment.**

The strongest standalone three-worker option repeatedly improves aggregate local results, and a
confidence-buffered label-aware portfolio gained **+6.213 mean margin** on untouched generated
seeds 210–239 with no negative opponent mean. That is an information-value result, not a bot:
opponent identity is unavailable in the arena. A state-observable signature study passed, but the
actual delayed common-prefix implementation then lost **−6.169 margin / −5.048 score** on new
seeds 270–299. The policies diverge before the signal, so the label-aware counterfactual cannot be
implemented by switching continuations late.

No resident source, candidate artifact, sealed map holdout, submission default, or arena state was
changed.

## 1. Policy recovery

Rank-4 agent `6480540` contributes 30 games, 8,738 decision rows, and 62 successful TRAIN events.
Its online workforce ladder is:

| Current workers | Affordability floor | Componentwise cap |
|---:|---|---|
| 1 | `(2,2,1,1)` | `(3,3,2,2)` |
| 2 | `(2,3,1,2)` | `(4,5,2,2)` |
| 3 | `(2,3,0,3)` | `(3,3,1,3)` |
| 4 | `(2,4,0,3)` | `(3,4,1,3)` |

At each stage it waits for the floor, then buys the maximum affordable stat vector clamped by the
cap. The recovered rule reproduces all 8,738 trigger decisions and all 62 specs in-sample, with
no false or missed TRAIN. Held-game validation keeps trigger timing exact and predicts 57/62
specs (91.94%); the worst fivefold spec fold is 7/9. All 62 trained workers eventually bank direct
fruit or score value, and ordinal productivity is 98.25–100%.

The final workforce distribution is 1 worker in 2 games, 2 in 7, 3 in 11, 4 in 7, and 5 in 3.
This resolves the earlier apparent contradiction: extra workers are not intrinsically
unaffordable. They become affordable when multiple current workers are assigned jointly to the
next stage's resource deficits. Transplanting only the purchase rule omits the mechanism that
funds it.

Evidence: `norxondor-workforce-ladder-study-2026-07-18.json`.

## 2. Controller decomposition

### Intent and routes

Of 10,406 MOVE rows, 10,391 targets (99.856%) equal the actual end-of-turn cell. Among eligible
episodes, 9,068/9,707 endpoints (93.417%) lie on a shortest route to the next non-MOVE action.
This supports an intent → goal → shortest-route decomposition rather than direct coordinate
imitation.

A row-level intent model reaches 71.56% fivefold accuracy. Predicting intent once at the start of
each of 4,427 MOVE episodes and persisting it raises accuracy to 74.11%, macro F1 to 0.525, and
worst-fold accuracy to 71.81%. The state-machine research gate passes.

### Goals

- DROP: all 1,469 observed endpoints are legal; 95.17% are in the nearest-path tie set.
- PICK: all 74 endpoints are legal.
- MINE: all 126 endpoints are legal; 84.13% are in the nearest-path tie set.
- CHOP ranker: 676/722 goals are covered; held exact accuracy 41.83% versus 23.27% minimum-cycle.
- HARVEST ranker: all 1,423 goals are covered; held exact accuracy 37.10% versus 4.85% baseline.
- PLANT: all 561 goals lie in the static bank-door footprint; 88.24% are currently free and
  82.17% are adjacent to an existing tree.

These layers authorize research prototypes, not exact imitation. Existing resident/Moisan/Silver
shortcuts fail complete-command agreement; rich local bots also emit hundreds or thousands of
false TRAIN commands.

Evidence: `norxondor-navigation-intent-study-2026-07-18.json`,
`norxondor-intent-state-machine-study-2026-07-18.json`, and
`norxondor-goal-selector-study-2026-07-18.json`.

## 3. Exact-engine counterfactual ladder

All rollout blocks use generated Bronze maps, both seats, eight diverse opponents, the exact game
engine, and 16 worker threads. They are discovery/replication evidence, not official-map or arena
evidence.

| Prototype | Result | Verdict |
|---|---|---|
| Ladder + CompactGold | −164.59 score / −170.19 margin vs Compact | Kill: continuation treats the new hybrids as the wrong roles |
| Ladder + Silver | −14.43 score / +0.83 margin; mean 1.47 workers | Kill: starter chops instead of funding the first floor |
| One explicit funder | +33.70 score / +76.65 margin vs Silver; mean 2.43 workers | Mechanism works, but workforce gate misses |
| Two funders | +68.56 score / +105.68 margin; mean 3.82 workers | Research pass; replicated at +65.59 / +100.89 |
| Soft two→one funder | +7.29 score / +4.57 margin vs resident | Aggregate improvement, only 4/8 nonnegative matchups |
| Stop at exactly 3 workers | +24.94 score / +8.18 margin vs resident on seeds 120–149 | Best macro option; 6/8 positive, but −66.35 adaptive and −12.57 script regressions |

This establishes the structural mechanism: a temporary two-worker funding coalition can buy the
third worker, after which all three return to productive continuation work. Continuing blindly to
workers four and five overcommits against several architectures.

## 4. Portfolio value and its limits

On seeds 120–149, a cell oracle between resident and the exact-three-worker option reaches mean
margin 70.53, **+35.24** above resident. A same-block opponent-label oracle reaches 53.33,
**+18.04**. This motivated a prospective information-value test.

The naive mapping frozen on seeds 150–179 gained +9.456 on 180–209 but failed: `sched_bot` and
`silver_boss` changed sign, producing a −15.18 worst opponent delta. A seed-balanced confidence
rule was then fit on all discovery seeds 150–209: choose three-worker only when its normal 95%
lower bound is positive. It retained CompactGold, GoldElite, MyBot, and PrinterBot; resident was
kept for Adaptive Gold, SchedBot, ScriptBoss, and SilverBoss.

Applied unchanged to new seeds 210–239, that information ceiling gained **+6.213 mean margin**.
All four selected branches remained positive (10.88 to 16.70), all resident branches were exact
zero deltas, and the worst opponent mean was zero. The cell oracle on the same block was +23.46,
showing additional state-level heterogeneity beyond opponent archetype.

Evidence: `norxondor-portfolio-upper-bound-2026-07-18.json` records the failed naive selector;
`norxondor-portfolio-confirmation-2026-07-18.json` records the frozen confidence selector and
prospective pass.

## 5. Observable signature and failed implementation

Instrumentation records the first successful opponent TRAIN as it becomes visible and the turn
our third worker appears. On seeds 240–269, all 240 alternative-label cells reveal an opponent
trained-unit signature strictly before worker three. A conservative fivefold classifier using
TRAIN stat vector plus broad turn band achieves:

- 75.83% overall branch accuracy;
- 52.08% alternative recall and 99.21% precision;
- one false alternative in 240 resident-label cells (0.417%);
- +7.546 paired information-value margin; worst opponent −0.383.

The gate therefore authorized one common-prefix prototype. Four safe signature regions were
frozen. The implementation ran the exact resident until a safe signature appeared, then committed
permanently to the three-worker Silver continuation.

On untouched seeds 270–299 it failed:

- final workforce: 2 in 434/480 cells, 3 in only 46/480;
- score delta versus resident: **−5.048**;
- margin delta versus resident: **−6.169**;
- worst matchups: PrinterBot −30.42, CompactGold −10.45, GoldElite −10.45.

The failure explains the plateau. Signatures measured on a three-worker trajectory are not
policy-invariant: spending the prefix under the resident changes funding time and sometimes the
opponent response. Late switching also abandons resident commitments without leaving enough time
to repay worker three. Do not tune the four signature regions; signature-only switching is closed.

Evidence: `norxondor-opening-signature-study-2026-07-18.json` and
`norxondor-signature-portfolio-study-2026-07-18.json`.

## 6. Attack-angle matrix

| Abstraction level | Angle | Evidence | Status / next discriminator |
|---|---|---|---|
| Stat formula | Recovered staged max-affordable ladder | Exact triggers; 91.94% held specs | Keep as a macro option |
| Resource control | Temporary two-funder coalition | Replicated large gain vs Silver | Keep mechanism; stop at worker three |
| Task control | Episode intent state machine | 74.11% held accuracy | Keep for a future native continuation |
| Spatial control | Equivalent endpoints + goal rankers | Legal/high-coverage goals, moderate held exactness | Research only |
| Complete policy | Direct ladder transplant | Compact and plain Silver fail | Closed |
| Fixed schedule | Soft / exact-three-worker | Strong aggregate, sharp opponent regressions | Keep only as portfolio branch |
| Opponent identity | Confidence-buffered policy table | +6.21 prospective information ceiling | Non-deployable; identity unavailable |
| Opening signature | First TRAIN stats + time | Safe CV information gain | Useful observation, not sufficient controller |
| Late switching | Resident prefix then three-worker | −6.17 prospective margin | Closed |
| State search | Counterfactual macro-option rollouts from one shared state | Large cell oracle; path dependence exposed | **Next priority** |
| Full imitation | Native Norxondor intent/goal controller | Components pass, integrated controller absent | Longer parallel research path |
| Model quality | Learn arena-conditioned continuation/value weights | Local archetype variance remains high | Required before any arena claim |

## 7. Phase 11 — next executable move

Freeze the exact resident and exact-three-worker option. Do not adjust their schedules while
building the selector.

1. Capture a shared early decision state (turn 3 or the first observed opponent worker) before
   either policy has materially diverged.
2. Condition the eight-model ambiguity set on observable opponent stats, positions, inventory
   changes, and action transitions; unknown signatures retain the resident default.
3. From the same cloned state, roll out both macro options under every compatible opponent model.
   Use a horizon long enough to include worker-three repayment; short asset bonuses are forbidden.
4. Select by a robust criterion: resident unless the alternative's lower-tail or worst-model
   advantage clears a frozen buffer. Compare this with mean, minimax, and oracle ceilings offline.
5. Validate the complete selected policy on nested seed blocks. Required gates remain positive
   paired score and margin overall, at least five of eight nonnegative opponent means, and worst
   opponent mean at least −5 versus resident.
6. Profile the one-shot decision under the 50 ms turn budget. Only then consider bounded parallel
   rollouts and source compaction under 100 kB.
7. No candidate, sealed holdout, submission, or arena action follows unless the actual integrated
   policy—not its information oracle—passes.

This is a valid Monte Carlo use case because the decision is macro, path-dependent, and has a
measured +23 to +35 per-cell oracle ceiling. Earlier turn-one Monte Carlo was retired because its
option library was inert; that conclusion does not apply to this later resident-versus-worker-three
branch.

## Artifacts added in Phase 10

- `cgauto/norxondor_workforce_ladder_study.py`
- `cgauto/norxondor_navigation_intent_study.py`
- `cgauto/norxondor_intent_state_machine_study.py`
- `cgauto/norxondor_goal_selector_study.py`
- `cgauto/norxondor_research_rollout_study.py`
- `cgauto/norxondor_portfolio_upper_bound.py`
- `cgauto/norxondor_opening_signature_study.py`
- `rust/src/strategies/norxondor_research.rs`
- `rust/src/bin/norxondor_research_time.rs`
- matching Python and Rust tests and the JSON/TSV evidence named above.

## Validation

- `python3 -m pytest -q`: **352 passed**.
- `cargo fmt --manifest-path rust/Cargo.toml --check`: passed.
- `cargo test --manifest-path rust/Cargo.toml --release`: passed; pre-existing warnings and
  intentional ignored tests remain.
- `git diff --check`: passed.
- All 17 `norxondor-*.json` artifacts parse.
- Resident artifact: 62,725 bytes, SHA-256
  `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55`, unchanged.
