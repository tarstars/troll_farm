# 20260803-e7a-claude-incremental-simplification: continue exact bot reduction

- Status: assigned_pending_ack
- Priority: direct owner assignment; supersedes Claude's queued, unreleased work
- Record owner: local_codex_1
- Work owner: claude_1
- Reviewer / integrator: local_codex_1
- Area: behavior-exact incremental E7a source simplification
- Base commit: `fd5962be40dab92dbaee000fabbdd5a90b234f87`
- Required branch: `agent/claude_1-e7a-incremental-simplification`
- Worktree: `/home/tarstars/prj/troll_farm-claude_1`
- Progress lease: begins when Claude publishes its acknowledgement; 15 minutes between concrete
  evidence or phase markers
- Created UTC: 2026-08-03T07:33:14Z
- Last updated UTC: 2026-08-03T07:33:14Z

## Objective

Continue the owner's incremental simplification programme from the fully qualified round-13
source. Delete one named logical block at a time, test the resulting program, and advance a
candidate only after exact equality is established. Size alone is not a reason to delete active
policy logic.

## Exact parent

- Source:
  `local_codex_1/e7a-iterative-logical-deletion/candidate-r13-remove-movement-tie-mode.rs`
- Bytes: 57,677.
- SHA-256: `6b9fdc99c960b4ddc969729d9452b1e5b7b252b06f8314a8567e969e27f5ba34`.
- Qualification: exact on ten semantic fixtures, 7,234 public-live command lines, 516
  development tasks, and 516 remotely locked untouched tasks.
- Report:
  `data/analysis/live-agent-6553250/e7a-iterative-logical-deletion-r13-result-2026-08-03.md`.

## Required reading

Before work, read `docs/STATE.md`, `docs/CONSTRAINTS.md`, the live ledger tail, this task, and
`docs/e7a-iterative-logical-deletion-protocol-2026-08-03.md`. The existing round-1--13 artifacts
are immutable evidence, not files to edit.

## Exclusive write set

Claude owns only:

- `claude_1/e7a-incremental-simplification/`;
- `coordination/messages/claude_1/*20260803-e7a-claude-incremental-simplification*`;
- `coordination/status/claude_1.md`.

`local_codex_1` retains the task record, shared state/ledger, development/untouched evidence,
integration, and Arena authority. Claude must not edit `local_codex_1/`, `cgauto/submissions/`,
the existing protocol or locks, shared coordination records, or the sacred source.

## Round discipline

1. Fetch immediately before branching and base the required branch on exact commit `fd5962be`.
2. Inspect only tightly scoped source/artifact paths; do not run broad searches over mounted
   repositories.
3. Before generating round 14, write a short immutable private contract naming one block, its
   exact invariant, replacement, supported-state argument, and rejection condition.
4. Generate the candidate with an exact builder: parent hash, unique anchor counts, strict size
   decrease, and byte-identical rebuild must be machine-checked.
5. No identifier renaming, formatting, minification, compression, or combined unrelated edits.
6. Run optimized standalone compilation, empty-input behavior, and all ten frozen semantic
   fixtures. Any difference rejects the round.
7. Publish one candidate, manifest, builder, contract, static/semantic evidence, and a host-run
   request containing exact paths, hashes, and command. At most one host request may be open.
8. `local_codex_1` runs the host-only 25-game / 7,234-line live command comparison. Claude must
   not treat the round as accepted or start the next candidate until a pushed exact-pass message
   is visible.
9. Development and untouched panels occur only at an integrator-selected accumulated checkpoint.
   Claude must not reserve or open map ranges.

## Initial deliverable

Return a ranked inventory of at most five remaining deletion candidates, clearly separating:

- provably unreachable blocks;
- fixed-value configuration plumbing;
- active behavior that must remain.

Then implement only the strongest safe round-14 block. Prefer a real logical deletion over small
identifier or expression shortening.

## Hard safety boundaries

- Keep `rust/src/bin/yamo_orchard_live.rs` byte-exact at SHA prefix `fff6669b`.
- Never format across `rust/src/bin/`, `cgauto/`, or any locked candidate.
- Do not touch `data/raw/games/` or the 05:17 collection cron.
- No Arena submission or other platform mutation.
- Claude has no host replay-cache dependency for source work; host-only replay execution is an
  explicit integrator handoff, not a blocker.

## Completion / stop

The task completes when either:

- a sequence of locally acknowledged exact rounds reaches an integrator-selected qualification
  checkpoint and is handed off with full provenance; or
- Claude finds no further block with a defensible invariant and hands off a ranked stop analysis.

Stop immediately on sacred-hash drift, ambiguous parent provenance, a non-unique builder anchor,
compile/semantic divergence, or a local live-parity rejection.
