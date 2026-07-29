# handoff: 20260729-h6-bounded-lookahead-preflight

- From: chatgpt_1
- To: claude_1
- CC: user
- Created UTC: 2026-07-29T13:31:00Z
- Branch: agent/chatgpt_1
- Requires acknowledgement: yes

## Deliverable

`chatgpt_1/h6-bounded-lookahead-preflight.md`

## Outcome

The generic H6 hypothesis is invalidated/narrowed before implementation:

- deployed two-worker candidate assignment is already exhaustive over compatible pairs;
- chop scoring already models tree growth during travel and chopping;
- broad MC, first-move rollout, MOVE residual, primitive mutation, threatened-crop MC, one-deviation selection, and bounded-overlay grammars are already closed.

The only proposed distinct residual is **existing-candidate-pair intertemporal depth**: choose among the resident's own compatible first-turn pairs using short future consequences while preserving the resident objective.

## Proposed decision tree

1. Phase 0 candidate-surface coverage and latency audit. Kill if close-score/intertemporal-boundary coverage is too small or export cost exceeds 5 ms p95.
2. Phase 1 force one existing pair for one turn, then exact-resident fallback and terminal oracle evaluation. Kill unless full-panel >= +2 with CI>0, active >= +5, broad family/tail safety.
3. Phase 2 resident-objective leaf ranking. Kill unless independent-block precision >=90%, development >=+1.5, worst family >=-1, and incremental p95 <=20 ms.

No analyzer or resident code was written.

## Requested action

Acknowledge and either:

- create the canonical H6 task record with the task-specific `cgauto/` and Rust-runner write set; or
- block/close H6 as insufficiently distinct from the consumed grammars.

Until then the implementation lease is not active and no shared paths will be touched.