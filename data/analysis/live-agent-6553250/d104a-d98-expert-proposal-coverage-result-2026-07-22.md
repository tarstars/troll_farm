# D104a D98 expert-proposal coverage — result

Date: 2026-07-22  
Status: full pass; compact online proposal-controller branch opened

## Verdict

The 64 frozen D98 independent scorers fail as static whole-task policies but succeed decisively as
a live action-proposal library. At the same D97 root they expose 16.642 distinct noncontrol
assignments on average, never fewer than seven, and expose at least one joint assignment at every
root. Their proposal-union oracle gains `+31.859` margin over D40, captures 86.45% of D97's full
joint-catalog oracle, and retains `+3.883` value beyond D97's complete best-single oracle.

Open a recurrent opponent-aware controller that chooses among deduplicated proposals online. Do
not select an expert, proposal, or arm from D104a; the union result remains hindsight-only. Before
training, compress the library outcome-blindly enough to respect the 100 kB source limit and prove
that the compact union retains the causal value gates.

## Integrity and execution

Both runs contain exactly `240 x 64 = 15,360` proposal rows and are byte-identical, SHA-256
`54bd509e60d83d3caa09d9dfed310b1e7422e186935917ec529bd854c7f07cd9`. Every proposal preserves
the paired boundary and maps exactly to one immutable D97 arm, including both actions, labels,
classes, state/observation/catalog hashes, and arm kind. There are zero reconstruction failures.

All frozen input/source hashes match. The audit independently reproduces D97's exact controls,
terminal integrity, `+36.852` joint-or-control gain, and `+9.208` rooted increment over the best
single.

The first implementation replayed each root separately for every expert and was stopped before
output after 330.97 seconds. A behavior-neutral repair uses the existing exact same-turn branch
preview: replay each root once, then preview all 64 actions without advancing the opponent or game
turn. The accepted one-worker run takes 21.81 seconds and the 20-worker run 2.60 seconds, an 8.39x
speedup. This workload parallelizes well because its 240 roots are independent and sufficiently
coarse, unlike D102/D103's quota-bound complete-episode schedules.

## Proposal support

| Measure | Result | Frozen floor |
|---|---:|---:|
| Supported proposal rows | 15,360 / 15,360 | 95% |
| Mean unique noncontrol proposals/root | 16.642 | 6 |
| Minimum / maximum unique proposals | 7 / 25 | descriptive |
| Roots with at least three proposals | 240 / 240 | 90% |
| Roots with a joint proposal | 240 / 240 | 80% |
| Experts active in at least 25% of roots | 50 / 64 | 48 |

The union spans fell, harvest, renew, and mine; natural, own, and opponent provenance; reversed
worker orders; both seats; and all eight opponent families. It contains 2,646 unique joint, 836
first-only, and 512 second-only root occurrences after per-root deduplication.

## Causal value retained

| Proposal-union oracle vs D40 | Result |
|---|---:|
| Mean margin | +31.859 |
| D97 full-oracle capture | 86.45% |
| Own score | +21.035 |
| Opponent score | -10.824 |
| Strict rooted improvements | 223 / 240 = 92.92% |
| Worst opponent-family gain | +18.750 |
| Crop creation | 100% |
| Worker-three reach | 91.41%, exactly D40 |

The union selects 148 joint, 45 first-only, 31 second-only, and 16 control arms at eligible roots.
Joint proposals are selected at 61.67% of roots and strictly beat the full best-single oracle at
107/240 = 44.58%. Mean incremental value over that best-single oracle is `+3.883`, so the library
retains genuine coordination rather than merely aggregating good individual jobs.

All eight family gains are positive and large: `+18.750..+45.313`. Selected proposals retain all
four jobs, all three observed provenance classes, reversed role orders, both seats, and every
family.

## Interpretation

D100b's static-selection failure and D104a's proposal-union success are compatible. A D98 weight
vector is not a transferable whole-game policy, but the population collectively supplies a rich,
safe local action basis. The missing component is online state-dependent authority allocation,
not another larger pair catalog or a task-level expert selector.

The result also narrows the next learner. It should score only the deduplicated proposal set plus
exact D40 control, carry recurrent crop-flow and opponent-pressure state, and optimize complete
trajectories with explicit production/downside constraints. It must not rescore D99's full
Cartesian catalog, select an expert globally, or use online Monte Carlo.

## Next eligible branch

Begin D104b with outcome-blind compact-library selection because all 64 exact weight vectors are
too large for a practical 100 kB submission. Use proposal coverage only—not terminal outcomes—to
choose the smallest frozen subset under a strict cap, then evaluate that one subset against the
already-consumed D97 continuations. Only retained support and value can open a fresh-map recurrent
environment and short mechanics/signal preflight. No candidate or platform action opens from
D104a.

## Artifacts

- `d104a-d98-expert-proposal-coverage-protocol-2026-07-22.md`
- `d104a-d98-expert-proposals-{a-jobs1,b-jobs20}.tsv`
- `d104a-d98-expert-proposal-coverage-result.json`
- `rust/src/bin/d104_d98_expert_proposal_coverage.rs`
- `cgauto/analyze_d104a_d98_expert_proposal_coverage.py`

