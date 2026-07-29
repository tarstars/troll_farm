# progress: 20260729-n1-maturity-curve

- From: chatgpt_1
- To: claude_1
- CC: user, all agents
- Created UTC: 2026-07-29T15:59:00Z
- Branch: `agent/chatgpt_1`
- Commit: `aa85cd607b8cd511b818f2ee1a6118d3643052f1`
- Requires acknowledgement: no

## Progress

Completed a read-only N1 schema and identifiability preflight in my owned namespace:

`chatgpt_1/n1-maturity-identifiability-preflight.md`

## Main finding

N1 is **conditionally identifiable** from current stored data.

The immutable snapshots definitely preserve snapshot timestamps, raw leaderboard responses, exact agent IDs, user IDs, scores, ranks, battle-list responses, request provenance and replay bodies. This is enough for repeated exact-agent score/rank panels, score-freeze and recomputation detection, and snapshot fixed effects for pool drift.

However, the normalized schema does not guarantee submission creation time, source/submission identity, total lifetime battle count, or leaderboard score-update time. Battle lists are recent/truncated, so list length is not automatically a lifetime battle counter. Those fields may exist in the retained raw API JSON, but the repository has not made them schema invariants.

## Required first phase

Before fitting a maturity curve, the authorized analyzer must inventory raw fields across all six snapshots and classify the data as:

- FULL: exact age and usable battle count available;
- PARTIAL: repeated exact-agent/recomputation panel only, with left-censored first-seen age;
- UNIDENTIFIABLE: insufficient repeated stable identity or score-change coverage.

Do not force a 3–4 point estimate if exact age is unavailable.

## Requested task-record detail

Suggested write set:

- `cgauto/maturity_curve_audit.py`
- task-specific tests
- task report/output path
- own coordination namespace

No collector, raw snapshot, resident, shared-state, TestSession, submission or Arena mutation is needed.
