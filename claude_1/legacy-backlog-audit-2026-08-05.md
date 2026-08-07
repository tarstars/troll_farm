# Legacy-backlog audit — claude_1 — 2026-08-05

- Scope: every unacknowledged ACK-required message path addressed to (or cc-ing) `claude_1`,
  as reported by `python3 scripts/inbox_sweep.py --me claude_1 --fetch` (read-only run,
  2026-08-05; authority `refs/remotes/origin/**`, 697 authoritative messages scanned).
- Count from sweep: **28** unacknowledged ACK-required paths.
- Method: each message read at its authoritative ref; current state established from
  `coordination/tasks/*` (origin/agent/local_codex_1), later same-task messages (any sender),
  `docs/STATE.md` (origin/agent/local_codex_1, updated 2026-08-05), and claude_1's own
  published messages across all `origin/agent/claude_1*` refs.
- Classification rule: no classification without a citation; uncertain cases default to
  `still actionable`.

## Summary

| classification | count |
|---|---|
| already completed | 23 |
| superseded | 4 |
| still actionable | 1 |
| **total** | **28** |

## Per-path dispositions

Abbreviations: `msgs/` = `coordination/messages/`, `tasks/` = `coordination/tasks/`.
All task records and local_codex_1/claude_1 evidence paths resolve on
`origin/agent/local_codex_1` / `origin/agent/claude_1` unless another ref is named.

| # | path | task | classification | evidence |
|---|---|---|---|---|
| 1 | msgs/chatgpt_1/20260802T133031Z-20260802-top-player-full-review-replication-handoff.md | 20260802-top-player-full-review-replication | already completed | tasks/20260802-top-player-full-review-replication.md: "Status: completed — cross-reviewed, reconciled, and integrated"; addressee ack msgs/local_codex_1/20260802T134650Z-…-replication-ack.md |
| 2 | msgs/chatgpt_1/20260802T133631Z-20260802-top-player-full-review-replication-question.md | 20260802-top-player-full-review-replication | already completed | requested cross-review release was published: msgs/local_codex_1/20260802T134700Z-…-replication-release.md (type RELEASE) |
| 3 | msgs/chatgpt_1/20260802T140900Z-20260802-top-player-full-review-replication-cross-review-handoff.md | 20260802-top-player-full-review-replication | already completed | integrator disposition published: msgs/local_codex_1/20260802T141909Z-…-replication-integrated.md; task record status "completed" |
| 4 | msgs/chatgpt_1/20260802T143000Z-20260802-initial-state-sector-policy-audit-handoff.md | 20260802-initial-state-sector-policy-audit | already completed | addressee acks msgs/local_codex_1/20260802T143306Z-…-audit-ack.md and 20260802T162546Z-…-audit-ack.md; tasks/20260802-initial-state-sector-policy-audit.md: "ChatGPT measurement-only handoffs integrated" |
| 5 | msgs/chatgpt_1/20260802T163300Z-20260802-banana-ring-b100-successor-handoff.md | 20260802-banana-ring-b100-successor | already completed | option 1 (local builds) was taken: msgs/local_codex_1/20260802T164116Z-…-successor-ack.md + 20260802T165603Z-…-successor-claim.md |
| 6 | msgs/chatgpt_1/20260802T163500Z-20260802-e7a-sector-candidate-claim.md | 20260802-e7a-sector-candidate | already completed | addressee ack msgs/local_codex_1/20260802T164437Z-…-candidate-ack.md; tasks/20260802-e7a-sector-candidate.md: "Status: complete" |
| 7 | msgs/chatgpt_1/20260802T164500Z-20260802-e7a-sector-candidate-host-run-request.md | 20260802-e7a-sector-candidate | already completed | host build performed and integrated (commit fc77657) per msgs/chatgpt_1/20260802T170000Z-…-candidate-handoff.md "host-validated, and integrated"; local ack 20260802T165135Z |
| 8 | msgs/chatgpt_1/20260802T165200Z-20260802-e7a-sector-candidate-pricing-request.md | 20260802-e7a-sector-candidate | already completed | pricing integrated (commit 61d929c) per msgs/chatgpt_1/20260802T170000Z-…-candidate-handoff.md §"Frozen consumed-panel price" |
| 9 | msgs/chatgpt_1/20260802T170000Z-20260802-e7a-sector-candidate-handoff.md | 20260802-e7a-sector-candidate | already completed | addressee ack msgs/local_codex_1/20260802T172759Z-…-candidate-ack.md; candidate published live per msgs/local_codex_1/20260802T174640Z-20260802-e7a-sector-owner-override-publication-integrated.md; task record "complete" |
| 10 | msgs/chatgpt_1/20260804T060000Z-20260804-orchard-activation-species-audit-claim.md | 20260804-orchard-activation-species-audit | already completed | claimed work delivered (msgs/chatgpt_1/20260804T064500Z-…-audit-handoff.md) and received by integrator: msgs/local_codex_1/20260804T090715Z-…-species-audit-ack.md |
| 11 | msgs/chatgpt_1/20260804T064500Z-20260804-orchard-activation-species-audit-handoff.md | 20260804-orchard-activation-species-audit | already completed | addressee reviewed both handoffs: msgs/local_codex_1/20260804T090715Z-20260804-orchard-activation-species-audit-ack.md ("I reviewed both handoffs") |
| 12 | msgs/chatgpt_1/20260804T064900Z-20260804-orchard-design-spec-handoff.md | 20260804-orchard-activation-species-audit | already completed | same ack covers the design records: msgs/local_codex_1/20260804T090715Z-…-species-audit-ack.md ("audit and design records received") |
| 13 | msgs/local_codex_1/20260802T122000Z-20260802-top-player-new-games-multiagent-analysis-correction.md | 20260802-top-player-new-games-multiagent-analysis | already completed | evidence-record-only correction on a closed task; tasks/20260802-top-player-new-games-multiagent-analysis.md: "Status: integrated — COMPLETE_WITH_EXTERNAL_LEASE_TAKEOVER at `73eb3ea`" |
| 14 | msgs/local_codex_1/20260802T155655Z-20260802-owner-banana-factory-b100-arena-claim.md | 20260802-owner-banana-factory-b100-arena | already completed | serialized cycle it announced is closed: msgs/local_codex_1/20260802T160120Z-…-arena-integrated.md; tasks/20260802-owner-banana-factory-b100-arena.md: "submitted once; … read-only" |
| 15 | msgs/local_codex_1/20260802T162547Z-20260802-h3a-conditioned-value-unblock-question.md | 20260802-h3a-conditioned-value-unblock | already completed | requested gate-4 progress/release was delivered: msgs/claude_1/20260803T074000Z-20260803-h3a-conditioned-value-unblock-handoff.md (all four gates pass, Phase A complete); H3a since "PAUSED FOR OWNER PRIORITY" (docs/STATE.md §4) |
| 16 | msgs/local_codex_1/20260802T162548Z-20260802-current-experiment-log-reconciliation-claim.md | 20260802-current-experiment-log-reconciliation | already completed | tasks/20260802-current-experiment-log-reconciliation.md: "Status: complete — current experiment records reconciled, audited, and remotely published" |
| 17 | msgs/local_codex_1/20260802T165603Z-20260802-banana-ring-b100-successor-claim.md | 20260802-banana-ring-b100-successor | already completed | announced build concluded: msgs/local_codex_1/20260802T172800Z-…-successor-handoff.md (SMOKE_QUALIFIED, owner-directed publication) |
| 18 | msgs/local_codex_1/20260802T172800Z-20260802-banana-ring-b100-successor-handoff.md | 20260802-banana-ring-b100-successor | superseded | banana line moved to tasks/20260802-banana-restoration-r2.md (docs/STATE.md §4: "BANANA R2 f29/280/2f58 INVALID"; claude_1's active r2 thread, latest msgs/claude_1/20260805T143000Z-20260802-banana-restoration-r2-handoff.md) |
| 19 | msgs/local_codex_1/20260802T184718Z-20260802-top15-public-battle-audit-claim.md | 20260802-top15-public-battle-audit | already completed | conflict-check ask is vacuously satisfied and verifiable: no top15 path exists in any claude_1 namespace on any remote ref; owner proceeded (msgs/local_codex_1/20260802T185507Z / 190033Z progress) |
| 20 | msgs/local_codex_1/20260802T191058Z-20260802-e7a-sector-agent-description-pdf-claim.md | 20260802-e7a-sector-agent-description-pdf | already completed | claimed write set delivered same hour: msgs/local_codex_1/20260802T191608Z-…-pdf-handoff.md; artifacts at docs/reports/2026-08-02-e7a-sector-agent-description.{md,tex,pdf} |
| 21 | msgs/local_codex_1/20260802T191608Z-20260802-e7a-sector-agent-description-pdf-handoff.md | 20260802-e7a-sector-agent-description-pdf | already completed | deliverable present and hash-documented at docs/reports/2026-08-02-e7a-sector-agent-description.pdf; tasks/20260802-e7a-sector-agent-description-pdf.md: "Status: handoff_ready" |
| 22 | msgs/local_codex_1/20260802T195210Z-20260802-e7a-half-size-logical-simplification-claim.md | 20260802-e7a-half-size-logical-simplification | superseded | tasks/20260802-e7a-half-size-logical-simplification.md: "Status: superseded_by_owner_rescope" (rescoped into single/iterative logical deletion); docs/STATE.md: "E7a HALF-SIZE … transfer-rejected" |
| 23 | msgs/local_codex_1/20260803T053400Z-20260803-e7a-single-logical-deletion-handoff.md | 20260803-e7a-single-logical-deletion | already completed | tasks/20260803-e7a-single-logical-deletion.md: "Status: complete_qualified_not_deployed"; message itself is a final result with requires-ack: no in body header |
| 24 | msgs/local_codex_1/20260803T060439Z-20260803-e7a-iterative-logical-deletion-claim.md | 20260803-e7a-iterative-logical-deletion | superseded | iteration ran through round 36 and terminated in tasks/20260804-r36-simplified-arena.md ("Status: complete — exact source active and settled read recorded"); docs/STATE.md: "round 36 … no further mutation" |
| 25 | msgs/local_codex_1/20260803T065406Z-20260803-e7a-iterative-logical-deletion-handoff.md | 20260803-e7a-iterative-logical-deletion | superseded | round-13 checkpoint superseded by rounds 14-36; terminal state in tasks/20260804-r36-simplified-arena.md and docs/STATE.md §1 (live `6594200`/`41090606`, settled 22.81/rank 32) |
| 26 | msgs/local_codex_1/20260804T113500Z-20260804-readable-no-orchard-rust-manual-claim.md | 20260804-readable-no-orchard-rust-manual | already completed | tasks/20260804-readable-no-orchard-rust-manual.md: "Status: complete — Markdown and validated 43-page PDF published" |
| 27 | msgs/local_codex_1/20260804T145839Z-20260804-r36-simplified-arena-handoff.md | 20260804-r36-simplified-arena | already completed | the read-only-while-settling directive has expired: tasks/20260804-r36-simplified-arena.md "complete — … settled read recorded"; docs/STATE.md §1 "settled 22.81/rank 32/137 over 160" |
| 28 | msgs/local_codex_1/20260804T164235Z-20260804-collect-r36-games-handoff.md | 20260804-collect-r36-games | still actionable | ask: "acknowledge only after confirming you can see the manifest and either materialize the payload or report your Git LFS limitation" — no claude_1 message on any ref mentions collect-r36 / r36-agent-6594200; the confirmation is still owed |

## Still actionable shortlist

1. **msgs/local_codex_1/20260804T164235Z-20260804-collect-r36-games-handoff.md**
   (task `20260804-collect-r36-games`). Residual action for claude_1: in a smudge-disabled
   clone, verify `data/shared-lfs/r36-agent-6594200/` README + manifest are visible, attempt
   `git lfs pull --include="data/shared-lfs/r36-agent-6594200/games-agent6594200-submission41090606.jsonl.gz"`,
   confirm 5,774,722 bytes at SHA-256 `59f6283b…`, then publish a v2 ack reporting either
   successful materialization or the exact LFS limitation. This path is deliberately
   excluded from the bulk ack_for below. Recommended: fold the eventual r36 corpus analysis
   into claude_1's score-hypothesis-program thread rather than opening a new task.

Note (out of scope of this table): the sweep also reports 190 "new (unseen)" paths; per the
rollout, seen-state may be advanced only after the signed ACK/audit commit is remotely
verified. This draft performs no --mark and writes no watermark.
