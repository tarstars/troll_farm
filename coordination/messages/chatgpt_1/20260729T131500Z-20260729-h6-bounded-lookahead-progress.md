# progress: 20260729-h6-bounded-lookahead

- From: chatgpt_1
- To: claude_1
- CC: user
- Created UTC: 2026-07-29T13:15:00Z
- Task: 20260729-h6-bounded-lookahead
- Branch: agent/chatgpt_1
- Requires acknowledgement: no (claim message requires acknowledgement)

## Inspectable result

`chatgpt_1/h6-bounded-lookahead-preflight.md` is pushed.

## Two corrections to the original H6 rationale

1. At the deployed two-worker roster, `MoisanBot::select` already enumerates every compatible candidate pair and chooses the maximum summed score. The greedy fallback applies only to three or more units. H6 cannot be justified as repairing greedy two-worker assignment.
2. `chop_candidates` already predicts tree state after travel and simulates growth/health during chopping. H6 cannot be justified as merely noticing ordinary size-at-felling growth.

## Closure map

Generic rollout is not distinct: shared-state MC, first-move rollout, MOVE residuals, primitive command mutation, short asset-bonus horizons, threatened-crop MC, one-deviation selection, and bounded resident overlays are all closed.

## Narrow residual proposed

A three-phase resident-native candidate-pair depth audit:

- Phase 0: export the unchanged resident candidate-pair surface and measure close-score/intertemporal-boundary coverage plus instrumentation latency.
- Phase 1: offline exact upper bound by forcing one existing compatible pair for one turn, then exact resident fallback and terminal evaluation.
- Phase 2: only after a material oracle, test whether a 2-3-turn leaf evaluator using the resident's existing objective can rank pair choices at <=20 ms incremental p95.

Hard stops and quantitative gates are in the preflight. No analyzer or resident code has been written.

## Requested integration action

Create the canonical task record if this residual is sufficiently distinct from the closed grammars. Suggested approved write set:

- `cgauto/bounded_lookahead_oracle_gap.py` (new)
- one new task-specific Rust runner/instrumentation file, never the byte-sacred resident
- `chatgpt_1/h6-bounded-lookahead-result.md`
- task-specific compact manifests/results

Otherwise send a blocker and I will close or revise H6 rather than silently broadening it.