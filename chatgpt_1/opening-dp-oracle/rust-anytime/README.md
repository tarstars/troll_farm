# Rust anytime opening planner

This crate is the deployable-shaped descendant of the Python opening DP oracle.
It answers a narrower question than the final bot integration:

> Can an event-driven A*/dynamic-programming search keep a valid opening plan at
> all times, improve it within a fixed first-turn budget, cap retained states,
> and fall back safely when the budget ends?

The answer is yes in the finite reduced opening model implemented here. The
larger regression case is solved and proved at turn 19 in roughly 0.36-0.38 s
instead of 11.25 s in Python, with about 84 MiB peak resident memory instead of
391 MiB. This is evidence about the search engine, not yet about real Troll Farm
maps.

## What is implemented

`src/search.rs` is a generic event-driven search engine:

- an always-valid incumbent, normally supplied by a cheap greedy or Monte Carlo
  planner;
- A* ordered by an admissible absolute completion-time lower bound;
- branch-and-bound against the incumbent;
- dynamic-programming/Pareto pruning of structurally equivalent states;
- stale-label removal;
- wall-clock, expansion-count and retained-state limits;
- a bounded beam fallback after the exact state cap is reached;
- strict replay of every returned action sequence;
- either an optimality certificate inside the supplied model or a reported
  lower/upper gap.

`src/model.rs` is a compact finite scheduling model used to test the engine. It
contains the real `n + talent^2` training bills, asynchronous trolls, finite
fruit sources, infinite iron, planting with delayed crops, shack release, and at
most one TRAIN per turn.

The reduced model deliberately omits the complete map, per-turn movement, exact
tree growth and a live opponent. It is not a substitute for `sim/engine.py` or
the maintained Rust referee.

## Commands

```bash
cd chatgpt_1/opening-dp-oracle/rust-anytime

cargo test --all-targets
cargo test --release larger_two_stage_case_is_19 -- --ignored --nocapture
cargo run --release -- small
cargo run --release -- bench
cargo run --release -- online
```

The crate has no third-party dependencies.

## Online usage pattern

```rust
use std::time::Duration;
use opening_dp_anytime::search::SearchLimits;

let mut limits = SearchLimits::online(Duration::from_millis(700));
limits.max_states = 250_000;
limits.beam_width = 4_096;

let result = problem.hybrid_solve(limits);
let plan = result.plan.expect("the greedy incumbent is feasible");
let first_action = plan.actions.first();
```

`hybrid_solve` first constructs the greedy incumbent. The expensive search only
improves it. A zero-duration test proves that the function can return the valid
incumbent without expanding a state.

The `wall_time` field is a search deadline, not a platform-level hard-real-time
certificate. On the CI host, 25/50/100 ms requests returned in about 30/55/113
ms because deadline polling and destruction of large tables happen around the
search. A bot must pass a conservative internal budget, leave headroom for input,
command generation and cleanup, and establish its own p99 timing certificate.
Do not pass the full 1,000 ms or 50 ms platform allowance directly.

The retained-state cap is a count cap rather than an exact byte cap. When it is
reached, A* storage is dropped before the beam search starts; the beam width is
clamped so its current and next frontiers fit within the configured count.

## Correct interpretation

A result marked `proven_optimal` is optimal only inside the supplied model and
action vocabulary. A real-map result needs all of the following:

1. construct states from the live board;
2. compile every macro-action to legal command lines;
3. make event transitions agree with the exact referee;
4. replay every selected complete schedule independently through
   `sim/engine.py` or the maintained Rust engine;
5. show that the macro-action vocabulary does not exclude the claimed better
   sequence.

Until that adapter exists, this crate is a Stage 2B search instrument and a
runtime prototype. It is not a candidate bot and changes no live policy.
