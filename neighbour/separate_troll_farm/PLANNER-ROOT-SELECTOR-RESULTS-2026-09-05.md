# Action-specific root selector for the persistent planner — negative result

## Outcome

**The advancement gate fails in every whole-map fold, so no Rust candidate was opened.** Keeping
the planner's already-generated spatial roots and replacing only its generic 16-ply simulator with
a tiny action-specific evaluator does not reproduce the planner's selections. The predeclared
model fires on 0, 1, 16, 5 and 0 of the five validation folds' searches, reaching at most 8.6%
override recall at 43.8% precision. The strongest optimistic frontier, which is *not* selected
evidence, reaches only 4.1--10.4% precision at the gate's 60% recall.

## What was measured

The frozen instrumented planner binary of the root-rank audit was re-run on all 160 exact archived
streams of agent 6704418, retaining every alignment check of that audit: stdout, per-turn
search/change/fallback counters, and the requirement that the emitted line *is* the selected root.
Each search was then joined with the decoded observed `GameState` of its turn. The join reproduces
every frozen total: 160 games, 43,263 turns, 9,635 searches (964/2,040/6,631 by root count),
9,247/251/137 selected slots, 388 direct root changes, 422 changed turns in 101 games, 0 fallbacks.

For each of the 15,302 non-baseline roots, 166 integer features were derived only from the
observed state, the candidate root command line and the baseline root line. Unlike the closed
aggregate distillation, these are actor-specific and spatial: verb transition per slot, acting
troll stats/cargo/location, MOVE destination BFS distance and its path relation to the baseline
destination (`on_path` / `beyond`), plant at and adjacent to the destination, own and enemy shack
distances, current-cell plant health/size/fruits/cooldown with rule-exact CHOP kill and wood yield
(`ChopTask`: `min(size, free capacity)` only when `chop_power >= health`) and HARVEST yield
(`min(3, fruits, harvest_power, free capacity)`), PICK/PLANT/DROP inventory and legality effects,
target overlap inside the root, remaining turns, and the planner leaf's own conservative
bankability `((d-1)+ms-1)/ms + 1 <= 301 - turn`. No planner value, future state, outcome, game id,
seed or opponent source is read; the test suite asserts this by name and by construction.

Because the roots are exact command lines, choosing the right slot *is* exact command agreement.
The emittability ceiling that capped the previous distillation study does not apply here.

## Results (predeclared depth 5, min leaf 20, cut 0.5; five whole-map folds)

| fold | maps | overrides | fired | precision | recall | slot acc. | FP on unchanged |
|---|---|---|---|---|---|---|---|
| 0 | 26 | 73 | 0 | 0.000 | 0.000 | n/a | 0.0000 |
| 1 | 26 | 77 | 1 | 0.000 | 0.000 | n/a | 0.0005 |
| 2 | 25 | 81 | 16 | 0.438 | 0.086 | 1.000 | 0.0052 |
| 3 | 25 | 91 | 5 | 0.400 | 0.022 | 1.000 | 0.0017 |
| 4 | 25 | 66 | 0 | 0.000 | 0.000 | n/a | 0.0000 |

Gate required >=90% precision, >=60% recall, >=90% slot accuracy on triggered overrides and
<=0.2% false positives in **every** fold; 14 of 20 checks fail. All 12 robustness settings
(depth 2--5 x min leaf 20/50/100) fail identically; no setting was chosen on validation.

**Memory split.** Of the 388 direct root changes, 101 are the first change of a game and are still
evaluated in exact V439 policy memory; 287 occur after the planner has already committed
counterfactual memory. Recall on the exact-V439 subset is **0.000 in all five folds** — the model
never once triggers the state a deployable wrapper would actually face first. Every one of the 22
true positives is a counterfactual-memory search (best fold recall 11.3%).

**Direct root-change labels only.** Told a change happens and asked only to rank the slots, the
model reaches 58.4--71.2% argmax slot accuracy, versus 58.4--71.2% for always picking slot 1 in
the same folds. The lift is zero. On the harder two-alternative overrides it is 51.5--66.1%
against a 50% coin.

**Heuristic baselines.** Always-rank-0 never fires: 0% recall, 0% false positives. Rank-1-only
fires on every multi-root search: 100% recall, 4.47% precision, 89.6% false positives on unchanged
searches, and 64.7% exact command agreement over all overrides.

**Optimistic frontier** (reported, not claimed): best precision at >=60% recall is 4.05, 4.29,
4.97, 9.52 and 10.39 percent by fold; best recall inside the 0.2% false-positive budget is
6.85, 0.0, none, 2.2 and 6.06 percent.

## Interpretation

The 16-ply simulator's preference among three already-generated V439 roots is not a function of
cheap local action semantics. Immediate wood, fruit, distance and bankability arithmetic is
visible in the features and is simply not what separates a chosen root from a rejected one: the
gain threshold `MIN_GAIN = 1.0` is a *minimum over two horizons* of a difference of full referee
rollouts including an adaptive opponent hypothesis, and the deciding quantity is at least eight
plies away. The one place the model finds any signal — counterfactual-memory searches at 40--44%
precision — is exactly the regime a deployed wrapper cannot enter without first having taken an
earlier override it also could not predict.

## Recommendation

Close the cheap-evaluator route for this planner. Neither aggregate features (closed
2026-09-05) nor action-specific per-root features can stand in for its simulator. A future cheap
policy must come from a different mechanism, not from imitating this one.

## Evidence and files

- Analyzer `analyze_planner_root_selector.py`; tests `test_analyze_planner_root_selector.py`
  (25 focused tests, all passing).
- Report `/data/separate_troll_farm-working/planning/2026-09-05/root-selector/root-selector-report.json`,
  SHA `89cb64f7eaea0c56f3d506642a2e3d94ba31b2ac8a8869e29ebeabf067068e53`.
- Frozen inputs re-hashed at run time: root-rank report
  `c0375ded90f3f105264e97c7784b33bc8324483f42e9cedf736b3f3a84d5024e`; instrumented source
  `b5453ac97af2daaf51f4f1bb10e9fc1a83df93c435fa718f5adfe59ed9acb800`; instrumented binary
  `e5fc6e7a1b2478a905c7467e08451c2df347bd62d31fdd31cea4029c22a24008`; plus `combined.rs`,
  the 160-stream benchmark report and the game archive through the root-rank auditor's own guard.

## Limitations

The archive is on-policy exact V439, so every planner deviation is a counterfactual root choice on
a V439 trajectory and never a played game; 287 of 388 overrides are evaluated after the planner's
memory has already diverged. Imitating the simulator would establish nothing about competitive
strength even if it had succeeded. No candidate, panel, platform game or publication was opened.
