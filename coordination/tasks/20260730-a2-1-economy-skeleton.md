# 20260730-a2-1-economy-skeleton: build and gate the first Architecture-2 policy

- Status: queued — unassigned and unstarted; A2-0b precondition satisfied; no A2-1 protocol, range, lock, or panel exists
- Record owner: local_codex_1
- Work owner: unassigned
- Reviewer: unassigned
- Integrator: local_codex_1
- Area: A2 programme Phase 1
- Base commit: 1ac918c7985d3b9a660b0ab72562d492edc744d6
- Branch: none until remotely claimed
- Progress lease: inactive until a work owner claims the task
- Created UTC: 2026-07-30T17:21:59Z
- Last updated UTC: 2026-07-30T17:34:54Z

## Outcome

An independently reproducible verdict on whether a new closed-loop economy scheduler can
establish and reap an early orchard, bank its proceeds, mine opportunistically, and fund
worker 3 from self-planted currency often enough to justify continuing Architecture-2.

This is the first phase that builds a new policy. A2-0a was feasibility measurement and
A2-0b built the referee/evaluation substrate; neither produced a candidate bot.

## Economic semantics that must not be conflated

- **Early planting:** establish and partially renew an orchard so planted fruit can
  contribute to workforce bills.
- **Late planting:** convert accumulated fruit into wood. Its late timing does not
  contradict early orchard establishment.
- **Population-level constraint:** Phase 0a measured median reproduction R≈0.75. Partial
  renewal is useful, but the scheduler must not assume indefinite self-replacement.

## Preconditions before implementation

1. **Satisfied 2026-07-30:** A2-0b received reviewer acknowledgement and reached protocol
   closure.
2. A work owner remotely claims this task with an explicit, non-overlapping write set and
   its own worktree/branch.
3. A separate A2-1 protocol freezes fresh, unconsumed development and confirmation ranges,
   selection rules, command-quality gates, source hashes, and stop rules.
4. The implementation and all direct dependencies are remotely locked before confirmation.

## Frozen protocol

None yet. `docs/A2-programme-charter-2026-07-30.md` defines the programme gates, but a
task-specific A2-1 protocol must be frozen before implementation or panel execution.

## Exclusive write set

None reserved while unassigned. The claim must name new A2-1 policy, runner, analyzer,
protocol, lock, result, and private coordination paths before implementation starts.

## Shared read-only paths

- `docs/A2-programme-charter-2026-07-30.md`
- `data/analysis/live-agent-6553250/a2-0b-r1-implementation-lock.json`
- `data/analysis/live-agent-6553250/a2-0b-r1-referee-parity-result.json`
- locked A2-0b referee-mode generator/checker/runner substrate
- resident control and open, unsealed aggregate evidence

## Do not touch

- `rust/src/bin/yamo_orchard_live.rs`
- locked A2-0b sources, dependencies, protocols, locks, or results
- consumed or sealed map/game ranges
- `data/raw/games/` and the 05:17 collection cron
- Arena, TestSession, submission tooling, or live platform state
- formatters over `rust/src/bin/` or `cgauto/`

## Required Phase 1 gates

1. Fruit-funded worker 3 in **≥40%** of fresh-map games by about turn **110**.
2. Non-zero reap of the policy's own planted crops.
3. Opportunistic mining remains active as roster grows; no dedicated mining-detour policy.
4. Policy-owned command failures satisfy a preregistered quality gate; critical and
   unclassified referee outcomes remain zero.
5. One-thread and multi-thread sorted outputs are byte-identical.
6. Both seats and all eight standing opponent families are represented.
7. Only the locked referee-mode A2-0b substrate is used; legacy mode is control only.
8. Resident SHA-256 remains prefixed `fff6669b`.

Failure of gate 1 is amended K1 and stops the programme. Reaching Phase 2 must occur within
six working sessions after Phase 1 starts (K2), otherwise stop and reassess with the owner.

## Deliverables

- frozen A2-1 protocol and implementation lock;
- new policy source and focused mechanics/economy tests;
- deterministic development and confirmation results on fresh ranges;
- exact gate table, command-quality accounting, trajectory/detector coverage, and verdict;
- ledger, CONSTRAINTS, STATE, BACKLOG, and approach-register closeout if executed.

## Acceptance checks

Exact commands and hashes must be frozen in the task-specific protocol. At minimum:

- focused policy/economy tests pass;
- analyzer compile/self-test passes;
- storage preflight passes before any bulk trajectory write;
- every required Phase 1 gate receives an explicit pass/fail verdict;
- no candidate is called built or qualified before the locked confirmation completes.

## Arena authority

Read-only platform access: not needed.
Platform mutation: forbidden. Phase 1 cannot submit; Arena is Phase 5 only after all
intervening gates and the promotion runbook.

## Handoff

The eventual work owner must provide a remotely fetchable implementation commit, lock,
reproduction commands, compact result records, hashes, and reviewer handoff. Until a
claim is remotely published, this file is only a durable queue entry and reserves no
write set.
