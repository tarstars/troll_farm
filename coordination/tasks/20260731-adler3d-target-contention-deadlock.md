# 20260731-adler3d-target-contention-deadlock

- Status: candidate submitted through distinct owner-directed Arena task; peer review queued
- Record owner: local_codex_1
- Work owner: local_codex_1
- Reviewer: chatgpt_1 after materialization
- Integrator: local_codex_1
- Area: live incident / equal-score same-tree contention deadlock
- Base commit: 74c06112b00e29a46377d87a939fcc96c8cbe0ae
- Branch: agent/local_codex_1
- Progress lease: 15 minutes without concrete evidence
- Created UTC: 2026-07-31T15:30:00Z
- Last updated UTC: 2026-07-31T16:15:00Z

## Owner observation

> immediate problem in game against adler3d: trolls stuck

## Exact incident

- Game `897552551`, active agent/submission `6585739`/`41070944`, resident seat 1,
  opponent Adler3D agent/submission `6481971`/`40751095`, valid 97–99 loss.
- Official reconstruction is 300/300 turns with zero unknown diff updates.
- On decision turns 50–91, resident unit 1 remains at `(10,4)` and emits 42 consecutive
  `WAIT` commands.
- Resident unit 2 emits 41 alternating MOVE commands on turns 51–91; its alternating
  `(9,4)` / `(8,4)` decision states span turns 51–92 (42 states).
- Both units are full of wood throughout the interval.
- Instrumented exact-parent replay shows an equal-score same-tree contention:
  `CHOP 1 + WAIT` and `WAIT + MOVE 2 10 4` each total 90. The selector retains the
  first equal pair, and collision resolution repeatedly detours unit 2 backward.
- The earlier causal transition is role loss: unit 1 was the productive adjacent-tree
  worker, acquired one wood, and then ceased to be bank-bound when the qualifying tree
  disappeared. The ordinary far-denial planner was free to retarget the full carrier.
- The exact far-denial-d3 parent reproduces every stuck command through turn 91. The
  active tent-proximity artifact reproduces all 300 recorded commands, so this incident
  is inherited rather than introduced by B3.13.
- The tent-proximity trigger later breaks the deadlock at turn 92 in the observed game.
  Restoring far-denial-d3 would therefore not repair the incident.

## Owner clarification and frozen patch

> trolls with wood, when decided to bring wood to tent, should do it

Persist a bank commitment for the productive worker selected in the one-or-two
tent-adjacent band. Once that worker has cargo, every subsequent command remains on the
bank path until `DROP` succeeds or cargo is empty—even if the adjacent-tree trigger
disappears or another denial target scores higher. Do not apply this commitment to the
non-banking planted-tree worker or the >2 full-denial workers. Do not change the global
selector, its equal/unequal-score tie order, target compatibility, movement conflict
resolution, or policy scores.

## Exclusive write set

- this task record;
- `coordination/status/local_codex_1.md`;
- `coordination/messages/local_codex_1/*-20260731-adler3d-target-contention-deadlock-*.md`;
- one compact incident analyzer and focused tests under `cgauto/` and `tests/`;
- one fail-closed sticky-bank generator and focused tests under `cgauto/` and `tests/`;
- one immutable successor candidate plus checksum under `cgauto/submissions/`;
- compact result report under `data/analysis/live-agent-6553250/`;
- compact manifest under `local_codex_1/adler3d-target-contention-deadlock/`;
- optional exact raw/trajectory cache only under
  `data/external/adler3d-target-contention-deadlock/` after external-storage preflight;
- integrator-owned backlog/approach/ledger disposition after validation.

## Shared read-only paths

- exact Codingame game `897552551`;
- active B3.13 candidate and its far-denial-d3 parent;
- replay decoder, state serializers, simulator/referee, and unsealed smoke tooling.

## Do not touch

- `rust/src/bin/yamo_orchard_live.rs` (byte-sacred);
- either parent artifact;
- the current Arena cycle, except read-only submission-scoped health checks;
- any other replay, map, frozen artifact, peer write set, raw collection, or the 05:17
  cron;
- sealed/official/confirmation data.

## Acceptance

- Lock exact game/agent/submission/seat identities and raw/trajectory hashes.
- Reconstruct every turn with zero unknown updates and publish the exact 42-turn deadlock
  interval, unit state, commands, candidate-pair scores, selector decision, and conflict
  outcome.
- Prove the exact parent reproduces the stuck interval and the active candidate reproduces
  the recorded 300-command stream.
- Generate fail-closed from the exact active artifact and add only the productive-role
  bank commitment.
- Compiled regression must retain bankward progress across trigger disappearance and
  higher-scoring retarget opportunities until an exact `DROP`; the non-banking/full-
  denial roles and global selector remain byte-unchanged.
- Re-run B3.13 boundary tests and bounded unsealed both-seat smokes; sacred SHA remains
  exact.
- Materialize and push only. No submit, restore, or second Arena cycle while exact
  `6585739`/`41070944` is in flight.

## Arena authority

Read-only incident discovery is allowed. This task explicitly forbids platform mutation.
Any later submission requires the current B3.13 cycle to terminate and a distinct
serialized Arena task.

## Materialization

- Candidate:
  `cgauto/submissions/candidate-agent6585739-owner-tent-banker-commitment-slim.min.rs`.
- Size: 68,464 bytes.
- SHA-256:
  `f26e3781e972006cb2698420bba3474f1a038708225beeb562f3ab2242593e4a`.
- Generator SHA-256:
  `e61cc8ffc26d707fa451424aa66e9f08ca0337a6a40946d2ce1b11aa80cb2772`.
- Focused test SHA-256:
  `a7a38dd679febbc21d43f4b4925c1bde405e1db7ec4de02f0bc9a0fc6c72645b`.
- Eight focused tests pass: three new commitment regressions plus all five original
  tent-proximity boundaries.
- Exact active artifact reproduces 300/300 recorded Adler3D commands. The successor first
  diverges at turn 48, stays bankward at turns 48–91, and replaces the turn-50 parent
  `WAIT` with `MOVE 1 10 3`.
- Eight unsealed local smoke cells (seeds 1300–1303, both seats versus `ringfix3`)
  terminate with zero stderr.
- Sacred source SHA remains exact:
  `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`.
- No submit or restore occurred.

## Exact evidence and disposition

- Raw replay SHA-256:
  `d17832e1427c40e0870a8c5df478b0694016584e6d8d021e42e942f5c7dac5c3`.
- Trajectory SHA-256:
  `7024f7f8ebdc772d7e8d901652fd0ecee4fa8f756dbfe14d2e39834dc8689768`.
- Candidate implementation commit:
  `47b2294b7baf8dedaba818a61ea4339a83b6c389`.
- Compact report:
  `data/analysis/live-agent-6553250/adler3d-target-contention-deadlock-result-2026-07-31.md`.
- The candidate is locally ready for review. It is not scientifically value-qualified
  and is not authorized for Arena while exact-source restoration
  `6585755`/`41071034` remains in flight.
- Review handoff:
  `coordination/messages/local_codex_1/20260731T160000Z-20260731-adler3d-target-contention-deadlock-handoff.md`.
- Subsequent owner override and live execution are recorded separately under
  `20260731-owner-tent-banker-commitment-arena`; this incident task itself made no
  platform mutation.
