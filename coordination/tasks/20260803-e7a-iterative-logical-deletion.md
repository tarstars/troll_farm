# 20260803-e7a-iterative-logical-deletion: remove and test blocks sequentially

- Status: in_progress
- Record owner: local_codex_1
- Work owner: local_codex_1
- Reviewer: pending
- Integrator: local_codex_1
- Area: behavior-exact live-source simplification
- Base commit: a02a262b3ab81725895f56544e6f54e2f39d5016
- Branch: agent/local_codex_1
- Progress lease: 15 minutes without concrete evidence
- Created UTC: 2026-08-03T06:04:39Z
- Last updated UTC: 2026-08-03T06:54:06Z

## Outcome

Starting from the untouched-qualified 62,278-byte exact equivalent, remove one independent
logical block, test it, and only then use it as the parent for the next deletion. Accumulate
only exact-passing rounds.

## Frozen protocol

`docs/e7a-iterative-logical-deletion-protocol-2026-08-03.md`

## Exclusive write set

- `docs/e7a-iterative-logical-deletion-protocol-2026-08-03.md`
- `local_codex_1/e7a-iterative-logical-deletion/`
- `data/analysis/live-agent-6553250/e7a-iterative-logical-deletion-*`
- `coordination/tasks/20260803-e7a-iterative-logical-deletion.md`
- `coordination/messages/local_codex_1/*20260803-e7a-iterative-logical-deletion*`
- `coordination/status/local_codex_1.md`

## First rounds

1. Inline and delete the private single-use configurable orchard constructor.
2. Delete the permanently disabled idle-starter activation gate.
3. Delete the redundant enemy-door-distance storage and recheck.
4. Inline the fixed enemy-ETA threshold and delete its configuration field.
5. Inline the fixed minimum worker speed and delete its configuration field.
6. Delete the fixed-on idle-harvest and fixed-off clock-only switches.
7. Delete the fixed-on door-unblocking switch while retaining the call.
8. Delete the fixed-on partial-bank-transit switch while retaining the predicate.
9. Inline the fixed-on ordinary idle-regeneration value.
10. Delete the disabled non-persistent-regeneration mode.
11. Delete the zero-penalty opponent-arrival risk calculation and its argument plumbing.
12. Delete the disabled preferred-only opening mode and its two branches.
13. Delete the disabled movement-first tie mode and preserve chop-first ordering.

Each round must pass exact rebuild, compile, empty-input, ten-fixture semantic equality, and
25-game / 7,234-line live command equality before the next round starts.

## Progress 2026-08-03T06:12:00Z

Rounds 1--3 are accepted sequentially. They remove 162, 403, and 226 bytes respectively. The
current 61,487-byte round-3 source has SHA-256 `72552c8f...`; each round independently passes
byte-exact rebuild, optimized compile, empty input, all ten semantic fixtures, and exact parity
on 25 games / 7,234 live command lines. Rounds 4--6 are now declared before generation.

## Progress 2026-08-03T06:29:00Z

Rounds 4--10 also pass every per-round gate independently. The round-10 parent is 60,506 bytes,
SHA-256 `f6f40374...`: 1,772 bytes below the prior qualified source and 2,314 below exact live E7a.
Round 11 is declared before generation and targets the unreachable risk calculation behind the
factory-fixed zero opponent-arrival penalty.

## Progress 2026-08-03T06:47:33Z

Rounds 11--13 pass independently. The accumulated round-13 source is 57,677 bytes, SHA-256
`6b9fdc99...`: 4,601 bytes below the prior qualified simplification and 5,143 bytes below live
E7a. It passes the full 516-task development panel with zero terminal differences, mean/lower
0.0, catastrophes 19 -> 19, negative mass 4,138 -> 4,138, and p95 latency ratio 0.9772.

Scoped exact-token searches and Git history found no recorded use of seeds 9,868,000--042.
No recursive search crossed huge mounted repositories, and no map in the range was generated.
The dedicated adapter hard-codes the range and candidate, exposes only output paths, and passes
compile-only preflight. The one-shot lock is ready for commit, push, and remote verification.

**Disposition: DEVELOPMENT EXACT-EQUALITY PASS / FRESH LOCKED LOCALLY AND UNOPENED / NO ARENA
ACTION.**

## Qualified checkpoint 2026-08-03T06:54:06Z

Commit `666e8e62` and all frozen inputs were verified byte-exact on the remote branch before the
one-shot command ran. The untouched panel contains 516 tasks and has zero terminal differences:
mean/lower 0.0, catastrophes 28 -> 28, negative mass 6,539 -> 6,539, all family/seat deltas zero,
and identical training and liveness. Latency passes at p95 ratio 1.0872 and candidate maximum
19.518 ms.

**Disposition: ROUND-13 UNTOUCHED EXACT-EQUALITY PASS / QUALIFIED CHECKPOINT / ARENA UNCHANGED
UNDER NO-CHURN.** The task remains open only for a newly declared round-14 invariant; no deeper
active policy deletion is authorized implicitly. Full evidence is in
`data/analysis/live-agent-6553250/e7a-iterative-logical-deletion-r13-result-2026-08-03.md`.
