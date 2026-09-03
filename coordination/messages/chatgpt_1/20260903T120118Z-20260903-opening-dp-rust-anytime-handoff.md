---
schema_version: 2
type: handoff
task_id: 20260903-opening-dp-rust-anytime
from: chatgpt_1
to: ["local_claude_1"]
cc: ["claude_1", "user"]
message_id: coordination/messages/chatgpt_1/20260903T120118Z-20260903-opening-dp-rust-anytime-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/chatgpt_1
artifact_commit: 60510f60cde1bd6b472a8f93b0c8ffaeb44dd00f
artifact_paths: ["chatgpt_1/opening-dp-oracle/rust-anytime/Cargo.toml", "chatgpt_1/opening-dp-oracle/rust-anytime/Cargo.lock", "chatgpt_1/opening-dp-oracle/rust-anytime/.gitignore", "chatgpt_1/opening-dp-oracle/rust-anytime/README.md", "chatgpt_1/opening-dp-oracle/rust-anytime/RESULTS.md", "chatgpt_1/opening-dp-oracle/rust-anytime/INTEGRATION.md", "chatgpt_1/opening-dp-oracle/rust-anytime/src/lib.rs", "chatgpt_1/opening-dp-oracle/rust-anytime/src/main.rs", "chatgpt_1/opening-dp-oracle/rust-anytime/src/search.rs", "chatgpt_1/opening-dp-oracle/rust-anytime/src/model.rs"]
created_utc: 2026-09-03T12:01:18Z
---

# HANDOFF — Rust anytime A*/DP opening planner

The owner asked to implement the Rust online form discussed after the opening-oracle review. The isolated implementation is complete at the pin above. It does not touch Claude's active Stage 2A controller or the champion.

## Delivered

- a generic event-driven A*/dynamic-programming engine;
- a legal greedy incumbent computed before expensive search;
- admissible lower bounds, branch-and-bound and Pareto dominance;
- wall-clock, expansion and retained-node budgets;
- a bounded beam fallback after the exact node cap;
- strict replay of every returned action sequence;
- a compact reduced opening model carrying the real `n + talent^2` training bills, asynchronous workers, finite fruit, infinite iron, planting and delayed crops, shack release and one TRAIN per turn;
- zero-time fallback, state-cap fallback, infeasibility and parity tests;
- release benchmark and online budget driver;
- the exact real-map integration and go/no-go gates.

## Verified execution

GitHub Actions run `33752289628`, Ubuntu 24.04, Rust 1.98.0: all steps succeeded.

- `cargo test --all-targets`: 6 passed, 0 failed, one release benchmark ignored in that pass;
- the ignored release parity test passed separately;
- joint worker allocation: greedy turn 9, exact turn 6, proved in 0.120 ms;
- planting before a distant trip: greedy 13, exact 10, proved in 0.029 ms;
- larger reduced case: greedy 22, exact 19, proved after 182,787 expansions in 378.404 ms with 83,612 KiB peak resident memory; a preceding successful run measured 355.029 ms / 83,536 KiB;
- with a 100,000-node cap, bounded search improves 22 to 20 in about 219 ms;
- with a zero-duration budget, it returns the replay-valid turn-22 incumbent without expanding a state.

The Python reference took 11.25 s and about 391 MiB on the same logical state graph. The exact search counts and optimum reproduce; the speed ratio is descriptive across hosts, not a controlled language benchmark.

## Safety and scientific boundary

The measured `wall_time` is an internal search budget, not yet a hard platform certificate. On CI, requests of 25/50/100 ms returned in about 30/55/113 ms because deadline polling and destruction of large tables also cost time. A bot must use substantial headroom and prove quiet-host p99 timing.

This is still a reduced-model implementation. It does not establish a real-map improvement or referee parity. The next valid use is the fixed-roster adapter on the 22 same-roster map-seats where the current rollout loses to orchard 6, compiling each macro sequence to commands and independently replaying it through `sim/engine.py` or the maintained Rust engine. `INTEGRATION.md` gives the full gate sequence.

The temporary branch-only CI workflow was removed after the successful run. The first CI publication accidentally staged Cargo `target/`; cleanup commit `df4cb3ecab4061972cefafe17d4aa881526963b9` removed every build product and added the crate-local ignore. The final artifact tree is clean; the accidental intermediate commit remains only in branch history.

No shared Rust file, Claude file, champion source, task card, board, platform, ladder, host-training, cluster or Arena state was modified.