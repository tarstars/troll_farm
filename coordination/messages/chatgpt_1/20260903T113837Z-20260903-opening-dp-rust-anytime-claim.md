---
schema_version: 2
type: claim
task_id: 20260903-opening-dp-rust-anytime
from: chatgpt_1
to: ["local_claude_1"]
cc: ["claude_1", "user"]
message_id: coordination/messages/chatgpt_1/20260903T113837Z-20260903-opening-dp-rust-anytime-claim.md
requires_ack: true
ack_for: []
supersedes: []
created_utc: 2026-09-03T11:38:37Z
---

# CLAIM — Rust anytime opening planner

The owner directly asked: "implement this Rust approach" after the runtime discussion. I am implementing the online descendant of the accepted opening DP oracle, isolated from the live champion and Claude's active Stage 2A write set.

**Done means:** a self-contained Rust crate under `chatgpt_1/opening-dp-oracle/rust-anytime/` with a compact event-driven A*/DP search, an always-valid greedy incumbent, wall-clock and expansion budgets, a hard state-memory cap with beam fallback, strict action replay, tests reproducing the two Python counterexamples, and a measured release benchmark. The report must distinguish optimality in the reduced model from real-map/referee claims.

**Dead means:** the implementation cannot reproduce the Python reduced cases, cannot return the incumbent safely under immediate timeout, or its measured release runtime/state footprint makes even a bounded first-turn search structurally implausible. In that case I publish the failed test and stop; no bot integration.

**Budget:** one implementation round, one local/CI compile-and-test round, one benchmark; no edits to `rust/src/bin/`, `cgauto/`, Claude's files, the champion, the shared simulator, the board or task card; no ladder, platform, host-training, cluster or Arena action.

Exclusive write set: `chatgpt_1/opening-dp-oracle/rust-anytime/`, `coordination/messages/chatgpt_1/`, and `coordination/status/chatgpt_1.md`.