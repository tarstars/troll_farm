# 20260802-current-experiment-log-reconciliation

- Status: complete — current experiment records reconciled, audited, and remotely published
- Record/work owner: local_codex_1
- Integrator: local_codex_1
- Created UTC: 2026-08-02T16:25:46Z
- Completed UTC: 2026-08-02T16:45:59Z
- Branch: `agent/local_codex_1`
- Area: current experiment and coordination-record integrity

## Owner directive

Check every current experiment and make the record tight. Reconcile the machine registry,
shared task records, live STATE/BACKLOG/ledger, immutable messages, status snapshots, hashes,
and acknowledgements. Preserve experiment verdicts and never turn bookkeeping repair into a new
experiment or Arena mutation.

## Findings to repair

1. the Arena registry still names displaced submission `41079653` as live and lacks banana
   submission `41081195` / agent `6590083`;
2. H3a still says Claude's integrity decision is pending although commit `6bddc45` accepts the
   state package with binding Phase-A-only scope limits and records a Phase-B/C substrate blocker;
3. the initial-sector task omits ChatGPT's improved E7a handoff and two ACK-required messages;
4. the inbox tool pairs acknowledgements only by task id, so an old ACK masks later requests;
5. older far-denial and LFS task snapshots are not marked with their terminal/superseding facts;
6. the unqualified live banana override and the unrun four-arm scientific protocol need an
   explicit cross-link without conflating their statuses.

## Exclusive write set

- this task record, `coordination/status/local_codex_1.md`, and new local sender messages;
- integrator-owned current task records and shared STATE/BACKLOG/live ledger;
- `data/analysis/arena-submission-history-inputs.json` and generated projection;
- `scripts/inbox_sweep.py` plus focused tests;
- host-only E7 compact extraction utility and outputs under `local_codex_1/` and
  `data/analysis/live-agent-6553250/e7a-root-delta-*`;
- new reconciliation audit report under `data/analysis/live-agent-6553250/`.

Peer-private status/message/report files remain immutable. Status collisions are preserved under
the protocol's `tarstars_` archive rule. No frozen protocol/result/source is rewritten.

## Prohibitions

No Arena mutation, TestSession game, experiment rerun, sealed or official-holdout access, raw-game
write, formatter, history rewrite, or peer-private edit. The sacred Rust source remains exact.

## Acceptance

- all relevant remote handoffs integrated or explicitly cross-linked;
- every active/superseded task has one unambiguous shared disposition and current next step;
- registry `current` returns `41081195` / `6590083`, projection rebuild is byte-stable, and tests pass;
- later ACK-required messages remain outstanding until a later ACK exists, with regression tests;
- E7 original `/tmp` outputs are checked only by exact path/hash and either compactly materialized
  or given an exact negative result;
- current artifact hashes, gzip integrity, JSON, sacred source, Git refs, and clean worktree pass.

## Result

All acceptance checks pass. Canonical Arena state is `41081195` / `6590083`; the 98-game read is
clean but provisional. Registry build/validation and 44 focused registry tests pass; the
freshness-aware inbox suite passes 11 tests and reports zero outstanding ACK-required messages.
Both E7 locked outputs produce the same 360-row compact CSV and all H3a package hashes/gzip files
verify. The integrated banana-ring packet remains a pre-lock successor, while the later E7a
candidate claim was explicitly blocked from integration after its suite failed `1/4` and the G4
bridge was absent. ChatGPT corrected both; the final host run passes 4/4 construction tests and
16/16 exact bridge games after a regression-tested `.min.rs` crate-name fix. The result remains
unqualified and Arena-unauthorized. Full report:
`data/analysis/live-agent-6553250/current-experiment-log-reconciliation-2026-08-02.md`.
