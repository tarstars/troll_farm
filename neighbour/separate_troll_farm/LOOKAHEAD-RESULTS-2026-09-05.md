# V439 lookahead: implementation verified, first policy not promoted

Production remains V439, submission 41245746 / agent 6704418, confirmed mature rank 28.
The seventh-place objective remains active. No platform games or submissions were requested
for this experiment. The initial eight-turn planner fails its predeclared development gate.

## What was built and independently checked

`lookahead_base.rs` is a separate V439 copy with full-controller cloning and ranked compatible
joint actions. Rank zero retains the original selector verbatim, including its tie behavior.
`lookahead_search.rs` clones pre-decision memory for each root, simulates future actions with
the independently verified model, and commits only the selected root's actual post-decision
memory. Physical seat/IDs, simultaneous TRAIN allocation, terminal cargo value, cache terrain
invalidation, ranked ties/stock constraints and continuation memory have executable fixtures.

Claude supplied the initial ranked-action and lexical minifier proposals, which were reviewed
and amended locally. Reported costs were USD 1.1640305 and 0.790231. A separate review attempt
exhausted its USD 1 budget (reported 1.139513) without returning findings; it is **not** counted
as a completed independent planner review. All three responses are archived. No neighbor writes.

The minifier preserves literals, protects format captures and qualified standard-library paths,
and checks token/alias invariants. Primary review caught a `std::cell`/local-variable collision;
compilation rejected that intermediate export. A Unicode-capture guard was also added. Exact
compilation and output tests are required in addition to the lexical invariants.

The final first-policy standalone is **92,250 UTF-16 units**, SHA
`a2d542af57b3f311b81b3f5a85932ae8a1271a0ba0c7efa0fa06a83adad9ccc7`.
Readable SHA `8bf8738513ec78803aab6e715a7d7e8afd058bb7c8b94fd66639f22914d5f510`;
module SHA `63144de206378b977b90d0633f3068e71633eb8ddfc11753232aeb3bccc0b72e`.
Unlike the earlier whitespace-only size calculation, this fits V439 plus the full model and search.

Rank-zero, shortened rank-zero and cached rank-zero variants each reproduce all 160 restored
production streams exactly. The complete search audit covers **43,263 turns**, with zero
readable/packaged differences. Both builds choose 846 changed roots in 9,635 searches.
This is observed-state verification, not an adaptive competition result.

Initial deadline-driven search produced a packaged/readable discrepancy. Removing the deadline
exposed 42 expensive turns, worst 9.25 seconds. Profiling reproduced over 18,000 compatible pairs
in one position. Exact distance caching and streaming top-k distinct-pair selection eliminate
the unnecessary full quadratic deduplication. Final maxima are **28.579/28.747 ms**, with zero
over-50-ms turns and identical commands to the preserved slow fixed-work planner. This is local
decision timing, not a platform guarantee or a full process-start check.

Full suite at this stage: **494 passed in 195.55 seconds**. The subsequent Unicode guard and
panel-report checks passed all 21 focused tests; the ASCII candidate export remained unchanged.

## Frozen eight-map, twelve-proxy development comparison

Both arms contain all 192 games; no execution, critical, unclassified or other command failures.
Neither arm exceeded 50 ms (maximum baseline 5.380 ms, search 27.693 ms). The local-only runner
applied 218 counted new-plant ordering corrections across the arms; the neighbor and historical
executables were not modified. This is reused development data, not a rank predictor.

| Policy | W/D/L | Match points | Own score | Opponent score | Margin | Wood |
|---|---:|---:|---:|---:|---:|---:|
| V439 | 173/5/14 | 175.5 | 238.458 | 110.563 | 127.896 | 44.292 |
| Eight-turn search | 173/5/14 | 175.5 | 236.406 | 110.005 | 126.401 | 43.495 |

Opponent-specific match points (16 games each): resident 10.5→11.5; compact_gold 11→10;
boss_real 14→14; legend_balanced 14→14; mybot and norx_native_three each 15→15;
gold_adaptive, legend_v3_hp2_four, legend_v7_hp2_four, legend_v8_hp2_four, script_boss and
silver_boss each 16→16. Full per-opponent W/D/L, scores, margins and issue counts are archived
in `fixed-fast-panel/analysis.json`.

Shared-map point deltas are 0,0,0,0,0,0,+1,-1. The eight-map bootstrap interval for mean
point delta per map is [-0.375,+0.375], conditional on these fixed proxies and consumed maps.
The planner changes 155 adaptive game streams and 7,214 commands after trajectories diverge,
but does not add net wins. Mean margin declines 1.495. It is not advanced to a real-agent screen.

The gained result is seed 9941006, seat 0 versus resident: 176–180 becomes 188–184.
The lost result is seed 9941007, seat 0 versus compact_gold: 313–301 becomes 306–309.

## Concrete diagnosis, not a coefficient sweep

The loss first diverges on turn 246: the search replaces `CHOP 3` on a damaged mature banana
with `MOVE 3 11 3`, while both policies keep `HARVEST 0`. A separate counterfactual harness
recreates the exact 253–245 factual state, clones its referee/random state and controller memory,
then varies only the root action. Continuation is V439, with either the planner's opponent
hypothesis or the actual adaptive CompactGold proxy. This is a one-root causal diagnostic, not
the repeated-search candidate's final result.

| Root action | Hypothesis value at 8 | At 16 | Final margin | Actual-proxy value at 8 | Final margin |
|---|---:|---:|---:|---:|---:|
| Baseline CHOP | 7.865 | 12.462 | +33 | 11.865 | +12 |
| Selected MOVE | 9.923 | 3.000 | +21 | 10.120 | +4 |

The claimed eight-turn improvement reverses both at a later horizon under the same hypothesis
and at eight turns against the actual proxy. Merely increasing one fixed horizon is not a
general cure: the actual-proxy sixteen-turn cargo value also prefers moving, despite its worse
final margin. A falsifiable next mechanism is requiring gains to persist across short and longer
horizons, with unchanged root choices and explicit renewed runtime/competitive gates.

Evidence root: `/data/separate_troll_farm-working/planning/2026-09-05/`. Key artifacts:
`fast-final.*`, `top-k-benchmark/report.json`, preserved failed benchmark directories,
`fixed-fast-panel/{manifest.json,dev8.tsv,analysis.json}`, and `counterfactual.{tsv,log}`.

## Persistent-horizon follow-up: earns a real-agent screen

The second predeclared policy retains the same three roots, start turn and continuation, but
requires a gain at both eight and sixteen turns and maximizes the smaller gain. Exact terminal
values fill subsequent checkpoints when the game ends early. The causal turn-246 trap now retains
the baseline CHOP; this is an executable test, not only a source check.

Its 160-stream audit again covers 43,263 turns with zero packaged/readable differences, zero
over-50-ms decisions and zero model fallbacks. There are 388 changed roots in 9,635 searches.
Maximum readable/short decision times are 41.367/43.573 ms. The exact exported programs pass
320 interactive open-stdin startup checks across both physical seats: correct first commands,
mean 1.636 ms, maximum 3.772 ms. This remains machine-specific timing, not a platform guarantee.

| Policy | W/D/L | Match points | Own score | Opponent score | Margin | Wood |
|---|---:|---:|---:|---:|---:|---:|
| V439 | 173/5/14 | 175.5 | 238.458 | 110.563 | 127.896 | 44.292 |
| Persistent-horizon | 176/5/11 | 178.5 | 239.505 | 110.161 | 129.344 | 44.411 |

All 192 games complete in each arm, with zero command/execution failures. Maximum panel decision
time is 44.740 ms, with no over-50-ms turn. Shared-map point deltas are +1,0,+1,0,0,0,+1,0;
conditional eight-map bootstrap interval for mean point delta per map is [0.125,0.75]. No unseen
opponent generalization or independent holdout claim follows from this reused development sample.
The local runner counts 233 Java ordering repairs. Detailed per-opponent outcomes are archived
in `persistent-horizon-panel/analysis.json`.

This passes the predeclared local advancement rule. `LOOKAHEAD-FIELD-PROTOCOL-2026-09-05.md`
freezes a new six-block real-agent screen and separate unopened confirmation. Publication is
not yet earned. The exact compact candidate is 92,430 UTF-16 units, SHA
`9f01587b4f71b8e5bbbe15e86a69aac274fe1ac476725951e6bf67db304b1c5d`;
readable SHA `a6256d053284e62cc66b1ca6fe123ad591e7a7bfe69913bf9fad172b7dca8479`.

## Field failure and independently reviewed packaging repair

The first candidate request failed compilation before gameplay; the original screen is closed
and cannot advance. See `LOOKAHEAD-FIELD-FAILURE-2026-09-05.md` for both requested games,
failure denominators and the separate deployment diagnostic. The actual export now adds only
explicit lint allows, preserving the frozen gameplay bytes. Its clean local builds and 498-test
suite do not yet prove platform compilation or competitive strength.

Claude independently reviewed the search implementation (reported USD 1.1371425), completing
the previously unfinished review. It found no branch-memory, horizon-bookkeeping or seat-algebra
error. Primary review disposition of its three proposed defects:

- Confirmed code observation, unmeasured effect: the hypothetical opponent first initializes at
  turn 220. Its plant/opening history therefore differs from a controller fed earlier observations.
  A warm/cold command reproducer is the next diagnostic; the review did not execute its claimed
  divergence or establish a strength effect. No gameplay change is bundled into the repair.
- Rejected as a defect: abandoning search when any root is outside the verified model domain is
  an intentional conservative fallback. Skipping invalid alternatives is a separate policy choice;
  the measured persistent-horizon audit had zero such fallbacks.
- Rejected: unit-0 ownership is established by the Java referee's `Board.createMap` initialization,
  which resets `Unit.idCounter` and initializes players in order, and by the existing physical-seat
  checks. The proposed nearest-shack heuristic is invalid once units travel across the map.

Two useful additional fixture gaps were identified: end-to-end branch selection from physical
seat one and wrapper stall-counter equivalence over an exhausting game. These are follow-up tests,
not evidence of a demonstrated defect. Review prompt/output remain archived as
`claude-planner-final-review-{prompt.md,response.json}` in the planning evidence directory.
