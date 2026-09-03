# Rust anytime planner: executed results

## Reproduction identity

- GitHub Actions run: `33752289628`
- Tested branch head: `743f62f4547652ccc6291e7fffc628400ecb721a`
- Verified source was retained unchanged by cleanup commit:
  `df4cb3ecab4061972cefafe17d4aa881526963b9`
- Runner: Ubuntu 24.04
- `rustc 1.98.0 (88d9e12ae 2026-08-18)`
- `cargo 1.98.0 (797e8a9bc 2026-08-05)`
- Build profile for measurements: release, thin LTO, one codegen unit
- Third-party dependencies: none

The workflow completed successfully. It ran canonical formatting, all normal
tests, the ignored larger parity test, the exact small examples, the larger
proof benchmark, and the online budget curve. Build products were then removed
from the branch and `/target/` was added to the crate-local `.gitignore`.

## Tests

```text
cargo test --all-targets
6 passed; 0 failed; 1 ignored
```

The ignored release test was run separately and passed:

```text
cargo test --release larger_two_stage_case_is_19 -- --ignored --nocapture
1 passed; 0 failed
```

Covered properties:

1. training costs use `n + talent^2`;
2. joint worker assignment improves turn 9 to the proved turn 6 optimum;
3. planting improves turn 13 to the proved turn 10 optimum;
4. a zero-duration search returns the replay-valid greedy incumbent;
5. reaching the state cap invokes the bounded beam and keeps a valid incumbent;
6. an infeasible model is not reported as a proved solution;
7. the larger Rust model reproduces the Python optimum at turn 19.

## Exact small cases

| case | greedy | Rust A*/DP | proof time | expanded | generated | nodes | peak queue |
|---|---:|---:|---:|---:|---:|---:|---:|
| joint worker assignment | 9 | **6, proved** | 0.120 ms | 81 | 140 | 93 | 24 |
| plant now vs distant harvest | 13 | **10, proved** | 0.029 ms | 17 | 27 | 18 | 5 |

Both returned sequences were replayed through the model's transition function,
and every recorded action identified exactly one successor.

## Larger reduced opening

| implementation | greedy | optimum | expanded | elapsed | peak resident memory |
|---|---:|---:|---:|---:|---:|
| Python prototype | 22 | **19, proved** | 182,787 | 11.25 s | 390,804 KiB |
| Rust, successful CI run | 22 | **19, proved** | 182,787 | 378.404 ms | 83,612 KiB |
| Rust, preceding successful run | 22 | **19, proved** | 182,787 | 355.029 ms | 83,536 KiB |

The Rust implementation traversed the same number of expanded and generated
states as the Python reference on this case:

```text
expanded:          182,787
generated:         333,966
retained nodes:    200,337
peak priority queue: 24,841
dominance-pruned:  107,699
bound-pruned:       25,930
```

Using the latest run, the algorithm is about 29.7 times faster and uses about
4.7 times less peak resident memory than the Python prototype. Host differences
mean those ratios are descriptive rather than a controlled cross-language
benchmark, but the reproduced optimum and search counts are exact.

## Online-budget experiment

The online driver used a greedy turn-22 incumbent, `max_states = 100,000`, and
beam width 2,048.

| requested search budget | returned turn | measured elapsed | lower bound | gap | mode at stop |
|---:|---:|---:|---:|---:|---|
| 0 ms | 22 | 0.001 ms | 1 | 21 | incumbent only |
| 1 ms | 22 | 1.105 ms | 6 | 16 | A* deadline |
| 5 ms | 22 | 5.284 ms | 9 | 13 | A* deadline |
| 10 ms | 22 | 10.946 ms | 9 | 13 | A* deadline |
| 25 ms | 22 | 29.903 ms | 11 | 11 | A* deadline |
| 50 ms | 22 | 55.038 ms | 13 | 9 | A* deadline |
| 100 ms | 22 | 113.398 ms | 15 | 7 | A* deadline |
| 250 ms | **20** | 219.256 ms | 15 | 5 | state cap, then beam exhausted |
| 750 ms | **20** | 219.024 ms | 15 | 5 | state cap, then beam exhausted |

The 100,000-state cap deliberately prevents this configuration from reaching
the 200,337-node exact proof. The full uncapped reduced proof takes less than
400 ms on this runner, so a first-turn search is plausible for this reduced
case. No equivalent statement is yet justified for a full real map.

## Findings that matter for deployment

- The mandatory fallback works: zero search time still returns a valid plan.
- The compact Rust search is fast enough to make a first-turn experiment
  reasonable.
- The current generic representation still reaches about 84 MiB on a
  200,337-node reduced proof. A submitted implementation should use a
  domain-specific arena and compact state IDs.
- The elapsed search call can exceed the requested budget by several
  milliseconds because deadline polling and table destruction also cost time.
  The caller must use headroom and pass a smaller internal budget than the
  platform allowance.
- The 50 ms later-turn allowance is not a license to rerun this whole search.
  Later turns should validate the stored plan and perform a much smaller local
  repair with a deterministic fallback.

## Scientific boundary

All numbers here belong to `reduced_opening.rs`. They do not establish a better
turn on any real panel map, referee parity, source-size fit, or safe runtime in
the submitted bot. Those are separate gates described in `INTEGRATION.md`.
