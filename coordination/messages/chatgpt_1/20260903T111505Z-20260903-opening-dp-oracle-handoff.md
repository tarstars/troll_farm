---
schema_version: 2
type: handoff
task_id: 20260903-opening-dp-oracle
from: chatgpt_1
to: ["local_claude_1"]
cc: ["claude_1", "user"]
message_id: coordination/messages/chatgpt_1/20260903T111505Z-20260903-opening-dp-oracle-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/chatgpt_1
artifact_commit: 01ff837791c614b4dabeae5108acbbc4177589fb
artifact_paths: ["chatgpt_1/opening-dp-oracle/oracle.py", "chatgpt_1/opening-dp-oracle/reduced_opening.py", "chatgpt_1/opening-dp-oracle/test_oracle.py", "chatgpt_1/opening-dp-oracle/demo.py", "chatgpt_1/opening-dp-oracle/README.md", "chatgpt_1/opening-dp-oracle/DESIGN.md", "chatgpt_1/opening-dp-oracle/RESULTS.md"]
created_utc: 2026-09-03T11:15:05Z
---

# HANDOFF — opening dynamic-programming / A* oracle prototype

The owner asked me to write down and implement the exact-search approach proposed after reviewing the opening solver. The implementation is complete at the pin above and remains isolated from Claude's active Stage 2A code.

## What is implemented

1. A generic event-driven A* / dynamic-programming engine with:
   - a greedy or Monte-Carlo incumbent as an upper bound;
   - an admissible absolute lower bound;
   - branch-and-bound;
   - Pareto dominance over structurally equivalent states;
   - stale-label removal and strict path replay;
   - an exact certificate when the frontier closes, or a live lower/upper optimality gap when a budget stops the search.
2. A finite reduced opening model with the real `n + talent^2` training bills, asynchronous workers, finite fruit sources, iron, planting and delayed crops, shack release, and one TRAIN per turn.
3. A demo, five tests, the design/proof boundary, the real-map adapter sequence, and recorded measurements.

## Executed results

- Tests: 5 of 5 pass.
- Joint allocation example: local greedy trains on turn 9; A*/DP finds and proves turn 6.
- Planting example: local greedy trains on turn 13; A*/DP plants first and proves turn 10.
- Larger two-stage reduced case: greedy 22; A*/DP 19, proved after 182,787 expansions; 11.25 seconds and about 391 MB peak memory.

## Ruling boundary

This is not yet a real-map solver. “Optimal” means optimal inside `reduced_opening.py` and its macro-action vocabulary. Nothing here establishes an optimum under `sim/engine.py`, and no claim about the 21-turn panel result changes.

My recommendation is to integrate this as a Stage 2B instrument without delaying Stage 2A. The first real adapter should fix one roster and run first on the 22 map-seats where the current same-roster rollout loses to orchard 6. Every selected schedule must compile to commands and replay independently through `sim/engine.py`; the report should contain the incumbent turn, oracle turn, lower bound, gap, expansions, time, and memory.

No Claude file, champion source, shared simulator, task card, board, platform, ladder, host job, cluster job, or Arena state was modified.
