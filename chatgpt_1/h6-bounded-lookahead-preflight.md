# H6 bounded-lookahead preflight

Updated: 2026-07-29T13:13:00Z
Agent: `chatgpt_1`
Branch: `agent/chatgpt_1`
Session head inspected: `f28cf772d5545fe8bac500a91e802c9fd366e815`
Status: preflight complete; analyzer implementation awaits canonical task record

## Verdict

Do **not** implement generic "2-3 ply lookahead" as currently phrased. Most natural meanings of that phrase are already closed. The only defensible residual is a narrow, resident-native **candidate-pair depth audit**:

> At exact live-resident states, enumerate compatible first-turn command pairs already produced by the resident, force one pair for one turn, then return to the exact resident. Measure whether pair-level intertemporal effects create a material terminal oracle gap, and whether a very short resident-objective leaf evaluator can rank those pairs inside the turn budget.

This is distinct only if it uses existing candidate commands and targets, changes no value term, adds no opponent-crop/farm bonus, and studies pair-level temporal consequences rather than primitive MOVE mutations or a new macro option grammar.

## Corrections to the motivating hypothesis

### 1. The two-worker selector is not greedy

The resident enumerates all compatible candidate pairs when there are exactly two own units and chooses the maximum sum. Greedy target reservation is used only for three or more units. The live resident is hard-capped at two workers, so a simple "better joint assignment" claim is false for the deployed roster.

Source: `rust/src/bin/yamo_orchard_live.rs`, `MoisanBot::select` around lines 1356-1416.

### 2. Size-at-felling is not ignored

`chop_candidates` predicts tree state after travel and then simulates growth/health while chopping. Its score is `1000 * final_wood / (travel + chop + return + drop)`. Therefore the scorer already sees size changes that occur during travel and chopping. The unmodeled residual is intentional delay or a different first-turn pair changing the future state, not ordinary travel-time growth.

Source: `rust/src/bin/yamo_orchard_live.rs`, `chop_candidates` around lines 1052-1119.

### 3. Broad search grammars are consumed

Binding closures in `docs/CONSTRAINTS.md` section (f):

- shared-state Monte Carlo: 209.487 ms median / 279.460 ms p95, zero decisions inside 50 ms;
- first-move rollout selection: failed live;
- broad and bank-only MOVE residual search: +0.508 at 92.852 ms p95;
- primitive command mutation and short asset-bonus horizons: closed for macro decisions;
- threatened-crop truncated MC: +3.160 versus +5.620 required at 210 ms p95;
- isolated turn-one continuation library: no opponent-robust activation.

Additional overlap:

- one-deviation sign selection is closed (`D41d-D42`);
- resident wrappers and bounded joint overlays are closed (`D36`);
- static selection over resident-native options is closed, despite a large hindsight envelope (`D169-D172`).

Any H6 protocol must name precisely why its grammar is not one of these.

## Proposed Phase 0: coverage and distinctness audit

No modified-bot simulation and no new planner code.

For an exact consumed official-map panel, instrument the unchanged resident to export, at each decision:

1. all candidates per own unit;
2. all compatible two-unit pairs;
3. chosen pair and total immediate score;
4. runner-up pair and score gap;
5. candidate semantic classes and targets;
6. predicted tree size/health/cooldown at arrival and at fell;
7. whether a one-turn delay or alternative existing pair can cross a tree-growth, banking, collision, or target-disappearance boundary within three turns.

Phase-0 pass conditions:

- at least 5% of relevant two-worker decision states have two genuinely distinct feasible pairs within 5% of the chosen immediate score;
- at least 2% of states have a verified intertemporal boundary within three turns;
- the residual is not solely MOVE destination mutation, fixed threatened-crop response, or an existing D163/D168 option;
- candidate export and one-tick shadow evolution add <=5 ms p95 before any continuation search.

If any condition fails, close H6 without building a rollout evaluator.

## Proposed Phase 1: exact pair-deviation upper bound

Only after Phase 0 passes.

For each qualifying state:

- take the top at most 8 compatible pairs from the resident's own candidate set;
- force one pair for exactly one turn;
- apply referee-exact action order and plant tick;
- return both sides to their frozen policies;
- evaluate complete terminal outcomes across the existing opponent-family panel and both seats.

This is an offline upper-bound instrument, not a deployable selector. It must use referee terminal semantics and exact resident fallback. It must not use generated-map results as acceptance evidence.

Required reporting:

- full-panel and active-state paired margin;
- clustered confidence intervals by map root;
- family, seat, map and turn distributions;
- catastrophes and negative-margin mass;
- semantic decomposition of winning pair changes;
- overlap with every closed grammar above.

Phase-1 continuation gate:

- full-panel oracle mean >= +2.0 with CI lower bound > 0;
- active-state mean >= +5.0;
- at least 6/8 opponent families nonnegative and worst family >= -1.0;
- catastrophes and negative-margin mass no worse than control;
- value is not concentrated in consumed/closed semantic classes.

Otherwise close H6.

## Proposed Phase 2: deployable leaf-ranking test

Only if the terminal pair oracle passes.

A deployable 2-3-turn evaluator must rank the Phase-1 pair choices without terminal rollouts. It may use only quantities aligned with the resident objective:

- realized banked score within the short horizon;
- remaining route time to the same candidate targets;
- resident candidate scores recomputed at the leaf;
- exact collision, inventory and tree state.

Forbidden leaf terms: new crop-origin bonuses, training bonuses, farm assets, score-behind modes, or hand-written semantic rewards.

Gates:

- >=90% precision when changing away from the live pair on independent map blocks;
- development mean >= +1.5 resident-relative with worst family >= -1;
- incremental optimized-Rust latency <=20 ms p95, leaving headroom under 50 ms for the resident and I/O;
- exact fallback output when abstaining;
- no source-size or deterministic-parity regression.

A terminal oracle without a qualifying leaf ranker is scientific evidence only, not an implementation lead.

## Recommended task write set

- `cgauto/bounded_lookahead_oracle_gap.py` (new)
- a Rust instrumentation/runner file under a new task-specific path, not the byte-sacred resident source
- `chatgpt_1/h6-bounded-lookahead-result.md`
- compact manifests/results under the task record's approved paths

The resident dev copy must remain byte-exact; no formatter over `rust/src/bin/` or `cgauto/`.

## Recommendation to integrator

Create H6 as a three-phase task with a hard stop after each gate. Phase 0 should be cheap and is the next unowned backlog item. Do not authorize a generic rollout implementation or a resident patch from this preflight alone.
