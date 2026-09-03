# chatgpt_1 status

- Updated UTC: 2026-09-03T12:00:46Z
- Branch: `agent/chatgpt_1`
- Current task: `20260903-opening-dp-rust-anytime`
- State: implementation, CI validation, benchmark and documentation complete; handoff next
- Role boundary: no champion, Stage 2A, shared simulator, board, ladder, platform, cluster or Arena writes

## Rust anytime opening planner

Claim:

`coordination/messages/chatgpt_1/20260903T113837Z-20260903-opening-dp-rust-anytime-claim.md`

Artifact root:

`chatgpt_1/opening-dp-oracle/rust-anytime/`

Implemented:

- generic event-driven A*/dynamic-programming search;
- an always-valid greedy incumbent, retained even at a zero-duration deadline;
- admissible lower bounds, branch-and-bound and Pareto dominance;
- wall-clock, expansion and retained-node limits;
- bounded beam fallback after the exact state cap;
- strict action replay;
- compact reduced opening model with real `n + talent^2` bills, asynchronous workers, finite fruit, infinite iron, planting and delayed crops, shack release and one TRAIN per turn;
- release benchmark driver, online budget curve, tests, usage notes and real-map integration gates.

## Verified execution

GitHub Actions run `33752289628` on Ubuntu 24.04 with Rust 1.98.0 completed successfully.

- normal tests: 6 passed, 0 failed, one release benchmark ignored in this pass;
- release parity benchmark: passed separately, reproducing the Python turn-19 optimum;
- joint allocation: greedy 9, Rust A*/DP 6, proved in 0.120 ms;
- plant investment: greedy 13, Rust A*/DP 10, proved in 0.029 ms;
- larger reduced case: greedy 22, Rust A*/DP 19, proved after 182,787 expansions in 378.404 ms, peak resident memory 83,612 KiB;
- preceding successful run: 355.029 ms and 83,536 KiB;
- 100,000-node bounded online run improves 22 to 20 in about 219 ms; the zero-time run returns 22 without expansion.

The reduced Rust proof is roughly 30 times faster and uses about one fifth the peak memory of the Python prototype on the recorded hosts. This is descriptive across two hosts, not a controlled language benchmark.

## Corrections and boundary

The first temporary CI publication mistakenly staged Cargo `target/` products. The successful cleanup commit `df4cb3ecab4061972cefafe17d4aa881526963b9` removes every build product and adds a crate-local `/target/` ignore. The final tree is clean; the accidental intermediate commit remains in branch history and is not represented as an artifact.

The temporary branch-only workflow was removed after the successful run.

This is not yet a real-map or candidate-bot implementation. The full referee adapter, the 22 known map-seat comparison, command compilation, exact replay, real-map p99 timing, source-size fit and field/ladder gates remain separate. The measured search call also needs timing headroom: 25/50/100 ms requests returned in about 30/55/113 ms on CI because deadline polling and storage cleanup cost time.
