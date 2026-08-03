# 20260803-e7a-claude-incremental-simplification: continue exact bot reduction

- Status: round22 development checkpoint exact; round23 continuation authorized
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
- Last updated UTC: 2026-08-03T13:50:52Z

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
8. Round 14's 25-game / 7,234-line live command comparison was run by `local_codex_1`. From
   round 15 onward, Claude runs the published credential-free packet comparison locally, commits
   the exact-pass JSON in its namespace, and stops immediately on any difference or failed gate.
9. Development and untouched panels occur only at an integrator-selected accumulated checkpoint;
   the integrator may also spot-check the online replay route at those checkpoints.
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
- Claude has no host replay-cache or platform-credential dependency: the frozen offline packet is
  the per-round live-command equality gate.

## Completion / stop

The task completes when either:

- a sequence of locally acknowledged exact rounds reaches an integrator-selected qualification
  checkpoint and is handed off with full provenance; or
- Claude finds no further block with a defensible invariant and hands off a ranked stop analysis.

Stop immediately on sacred-hash drift, ambiguous parent provenance, a non-unique builder anchor,
compile/semantic divergence, or a local live-parity rejection.

## Round-14 host result 2026-08-03T09:47:56Z

Claude's 57,529-byte round-14 candidate (`c71a0141...`) is exact on all 25 public liveness
counterexamples and 7,234 teacher-forced command lines: zero different games, unknown updates,
or liveness differences. The result JSON SHA-256 is `f02c103d...`.

The owner additionally directed publication of the 18 MB frozen audit for Claude-local future
parity gates. Its content matches the preregistered SHA-256 `8c29f433...` and is remotely
published through an exact-path Git LFS rule.

## Credential-free gate correction 2026-08-03T09:55:13Z

The audit itself is not a replay corpus: it contains decoded summaries and game selection fields,
but no `frames` or `view` payloads. The original evaluator calls Codingame's
`gameResult/findByGameId` endpoint for every selected game, so the audit alone cannot authorize a
Claude-local gate on a host without platform credentials.

The integrator therefore froze a compact, deterministic gzip packet containing the exact 25
teacher-forced transcripts and 7,234 exact live-baseline output lines:

- packet:
  `data/analysis/live-agent-6553250/e7a-live-command-parity-offline-packet-2026-08-03.json.gz`;
- packet SHA-256: `fb8e968ff65fc55c6f6f9d2f2b678434ab2dfda8eba84fdb6d0384d41856c7e2`;
- evaluator:
  `local_codex_1/e7a-iterative-logical-deletion/evaluate_live_command_parity_offline.py`;
- builder/provenance:
  `local_codex_1/e7a-iterative-logical-deletion/build_live_command_parity_offline_packet.py`.

The credential-free evaluator imports no Arena client and performs no network calls. On round 14
it reproduces the online result exactly: 25 games, 7,234 turns, zero different games, maximum
period-2 episode 128, and `LIVE_COMMAND_PARITY_PASS`. Its result SHA-256 is `56c30255...`.

The packet and evaluator were pushed and remotely hash-verified in commit
`9caa06dc024c278ade577bed40c7a9a705b0cdcd`. Round 15 is authorized by the accompanying policy
message; the exact-equality and immediate-stop rules remain unchanged.

## Round-22 checkpoint intake 2026-08-03T13:45:35Z

Claude completed rounds 15–22, consuming the single-valued `YamoOpeningPolicy` record and its
plumbing one declared block at a time. The 56,651-byte head candidate has SHA-256
`2943ad840ccaf2332ab515ab768aa8c97bac2de894a7eda6228b92ea5f0707cc`; every delegated local gate
reports exact. The branch and immutable evidence were integrated without changing the sacred
source. The integrator accepted round 22 as an accumulated checkpoint and started the same
516-task development equality panel used at round 13. Untouched-range expenditure and the two
remaining deletion rulings will be published with the checkpoint verdict.

## Round-22 checkpoint verdict 2026-08-03T13:50:52Z

Round 22 passes the 516-task development equality panel: 43 consumed maps, both seats, and six
opponent families produced zero terminal-field differences. Mean delta and bootstrap lower bound
are both 0; catastrophes, negative-margin mass, training, issues, and period-2 metrics are exact.
Candidate p95 latency is 1.02094 times baseline. Evidence:
`local_codex_1/e7a-iterative-logical-deletion/candidate-r22-delete-opening-policy-record-development.json`,
SHA-256 `bed4bc677c17fcb32fb07969303ee19866b71bab8b66c39161f8e9d62b71d903`.

Disposition:

1. Defer the next untouched range until the current fixed/dead-code cascade terminates or Claude
   publishes a stop inventory. Running it now would qualify an immediately superseded source.
2. Approve folding the constant-false `15<=0||` disjunct as one separately contracted round.
3. Removing unused derived impls is legitimate generated-dead-code deletion, not formatting, if
   source order and spacing are otherwise byte-exact. Split by trait: one round for all current
   `Debug` derives, one for `Hash` on `PlantKind`. The round-22 parent contains 12 `Debug` tokens,
   not the handoff's stale count of 13, because deleting `YamoOpeningPolicy` removed one.
4. Record the audit discrepancy as taxonomy-only evidence: game `897833625` differs by one
   CHOP/MOVE histogram position, while the hash-pinned transcript/output packet and online parity
   agree. It does not weaken command equality.
5. Record the eager credential import as tooling debt, not a current blocker. The online builder
   and evaluator inherently require the Arena API; the delegated offline evaluator is already
   stdlib-only. If replay decoding is reused in cloud tooling, split it from `battle_taxonomy` and
   lazy-load credentials.

Claude may proceed from round 22 under the existing one-block, exact-builder, semantic-fixture,
and offline-parity discipline. Development and final untouched qualification remain integrator
gates; Arena remains unchanged.
