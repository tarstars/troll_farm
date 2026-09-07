# Persistent-planner deployment pruning result

## Decision

The fresh planner-pruning route is **closed locally and must not be submitted**. It produced a
clean, substantially smaller program, but changed matched Rust 1.90 compile time by only 1.45%.
That is far short of the pre-measurement advancement requirement: at least 20% faster than the
failed combined planner and close to V439 (target at most about 6.8 seconds). No platform request,
competitive screen or publication was made.

## Delegated implementation and primary repair

Claude was given a bounded implementation/evidence task under a USD2.50 cap, with platform and
neighbor writes prohibited. It correctly stopped when blindly reusing all five standalone-V439
dead-region boundaries deleted the planner's live `#[derive(Clone)]` on `AppleOrchardBot`. The
resulting first package, compact SHA
`ee8726e5c56c020b4eac2bbdb08e20a84040411fa1879dac919255cdff02fa59`, did not compile and is not a
candidate.

Primary reviewed the failure and repaired the exporter with a source-specific end marker that
retains the live derive while deleting the same unused `OrchardCycle` body. The other four spans
are unchanged. Focused tests cover both frozen hashes, byte-exact reproduction of the old compact
source, ordered unique markers, retention of the derive, deterministic output, destination and
overwrite refusal, size, build commands and benchmark rotation: **16 passed in 4.54 seconds**.

## Exact repaired artifact

Fresh directory:
`/data/separate_troll_farm-working/planning/2026-09-05/pruned-persistent-v2/`.

- readable SHA `642e96acab97f308709ad25edaea5fe3dcdd75869c272422f7437de6c9f90b65`,
  232,543 UTF-16 units;
- compact SHA `3b5bf178b23757b1b8b67e44180c3f59ffb7252435d213e32c41c253b1e601f8`,
  83,145 UTF-16 units, down from 92,938;
- manifest SHA `41e620e8fffa10be97c0babf258c0aff631c8d2ffd34fbc7b8407a272b2e3080`;
- compact/readable/fixture builds all succeeded with zero diagnostics under the matched compiler;
- all nine embedded Rust planner/ranking/navigation fixtures passed.

Three alternating builds per arm gave medians: pruned planner **7.981 s**, unpruned combined
planner **8.098 s**, V439 **6.302 s**. The pruning saved only 0.117 s / 1.45% relative to the
contemporaneous combined control and remained 1.679 s / 26.64% slower than V439. V439's historical
warnings were retained in the diagnostic record; both planner arms were diagnostic-free.

Because compiler advancement failed, the expensive 160-stream command-equivalence run was not
opened. The deletion-only source and Rust fixtures establish a valid local package, not platform
deployability or competitive strength. The exact compact SHA above is closed and must not be
retried remotely. Live V439 and canonical `bot.rs`/`submission.rs` remain unchanged.
