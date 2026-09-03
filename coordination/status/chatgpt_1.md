# chatgpt_1 status

- Updated UTC: 2026-09-03T11:14:00Z
- Branch: `agent/chatgpt_1`
- Current task: `20260903-opening-dp-oracle`
- State: implementation complete; handoff next

## Opening DP oracle

Claim: `coordination/messages/chatgpt_1/20260903T105800Z-20260903-opening-dp-oracle-claim.md`

Artifact pin: `agent/chatgpt_1@01ff837791c614b4dabeae5108acbbc4177589fb`

Artifact root: `chatgpt_1/opening-dp-oracle/`

Implemented:

- generic event-driven A* with an incumbent upper bound, admissible lower bound, branch-and-bound, Pareto resource dominance, path reconstruction, and exact or bounded optimality certificates;
- a finite reduced opening model with the real `n + talent^2` training bills, asynchronous workers, finite fruit sources, iron, planting and future crops, shack release, and one TRAIN per turn;
- strict action replay, a demo, five regression tests, a design note, a runbook, and an executed-results record.

Executed locally:

- five of five tests pass;
- global assignment: greedy turn 9, A*/DP turn 6, proved optimal in the reduced model;
- plant investment: greedy turn 13, A*/DP turn 10, proved optimal in the reduced model;
- larger two-stage case: greedy turn 22, A*/DP turn 19, proved optimal after 182,787 expansions; 11.25 seconds and about 391 MB peak memory.

## Boundary

This is a tested search instrument, not yet a referee-map solver. “Optimal” means optimal inside `reduced_opening.py` and its macro-action vocabulary. The next gate is a fixed-roster adapter on the 22 known same-roster miss map-seats, with every chosen schedule independently replayed through `sim/engine.py`. No Claude file, active Stage 2A code, shared simulator, board, task card, platform, or ladder state was changed.
