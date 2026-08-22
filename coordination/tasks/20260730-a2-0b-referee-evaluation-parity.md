# 20260730-a2-0b-referee-evaluation-parity: A2 referee and evaluation harness

- Status: closed — QUALIFIED, reviewed, and protocol-closed
- Record owner: local_codex_1
- Work owner: local_codex_1
- Reviewer: chatgpt_1
- Integrator: local_codex_1
- Area: A2 programme Phase 0b
- Base commit: f799dc2befd144a46842cbc55587646bebb29db2
- Branch: agent/local_codex_1
- Progress lease: 15 minutes without concrete evidence (phase markers renew it)
- Created UTC: 2026-07-30T15:17:31Z
- Last updated UTC: 2026-07-30T17:34:54Z

## Outcome

A frozen and tested parity harness for Architecture-2 that preserves the accepted
resident experiment rig while closing X1's two referee gaps. It must preserve post-map
SHA1PRNG state for equal-best movement, enforce or independently prove referee-legal
commands, reproduce a known resident baseline, and remain byte-identical across thread
counts before any A2 Phase 1 result is trusted.

## Protocol status

Frozen at `docs/a2-0b-referee-evaluation-parity-protocol-2026-07-30.md`, with binding
source correction
`docs/a2-0b-referee-evaluation-parity-rng-amendment-2026-07-30.md`. No panel execution
begins until the implementation lock is remotely published.

## Exclusive write set

- `docs/a2-0b-referee-evaluation-parity-protocol-2026-07-30.md` (new)
- `docs/a2-0b-referee-evaluation-parity-r1-protocol-2026-07-30.md` (new)
- `rust/src/game/a2_continued_mapgen.rs` (new)
- `rust/src/game/a2_referee_parity.rs` (new)
- `rust/src/game/mod.rs`
- `rust/src/bin/a2_0b_referee_parity.rs` (new)
- `tests/test_a2_0b_referee_parity.py` (new, if needed)
- `cgauto/analyze_a2_0b_referee_parity.py` (new)
- `data/analysis/live-agent-6553250/a2-0b-*` (new records only)
- `coordination/tasks/20260730-a2-0b-referee-evaluation-parity.md`
- `coordination/status/local_codex_1.md`
- `coordination/messages/local_codex_1/`
- `local_codex_1/a2-0b/`

Conditional integrator closeout paths:

- `docs/A2-programme-charter-2026-07-30.md`
- `docs/APPROACH-REGISTER-2026-07-30.md`
- `docs/STATE.md`
- `docs/CONSTRAINTS.md`
- live ledger volume named in `docs/STATE.md` §5

## Shared read-only paths

- referee source pinned by X1
- `rust/src/game/engine.rs`
- `rust/src/game/official_mapgen.rs`
- resident control snapshot and existing panel/analyzer sources
- existing unsealed lock/result records
- waste-sweep detector library and promotion tooling

## Do not touch

- `rust/src/bin/yamo_orchard_live.rs`
- existing frozen engine, official-map generator, runners, locks, or results
- sealed map/game ranges
- `data/raw/games/` and the 05:17 collection cron
- Arena, TestSession, submissions, or platform state
- formatters over `rust/src/bin/` or `cgauto/`

## Required gates

1. Accepted D33 initial-state identity remains unchanged.
2. New RNG-continuous generation produces the identical initial `GameState` while retaining
   the next SHA1PRNG state.
3. Direct reachable movement consumes no RNG; every non-direct path selection consumes
   exactly one bounded referee RNG draw, including `nextInt(1)`.
4. Every direct command in the reproduction panel is referee-legal, with reason-counted
   failure on any invalid command.
5. One-thread and multi-thread result rows are byte-identical after deterministic ordering.
6. Both seats and all eight standing opponent families are represented.
7. A preregistered known resident result is reproduced within its frozen identity/tolerance
   gate before the A2 harness is accepted.
8. All six standing waste detectors execute on the harness trajectory schema.
9. Resident SHA-256 remains prefixed `fff6669b`.

## Arena authority

No read or mutation is needed. Arena, TestSession, and submission tooling are forbidden.

## Progress — 2026-07-30T15:28:38Z

The isolated continued-map/RNG layer and source-shaped movement selector are implemented
without changing the historical engine or generator. A direct Rust module harness passes
6/6 tests, including field identity over 1,024 seeds, direct-move zero draws, bound-one
draws, and true-tie selection. Collision resolution accepts already-resolved targets so
the final parser can consume RNG in referee command order.

## V1 development verdict — 2026-07-30T15:38:42Z

**BLOCKED_BEFORE_IMPLEMENTATION_LOCK.** Frozen G3 required zero referee errors across
both players/modes. The 16-map/256-task smoke observed 10,782 legacy-checker and 10,132
referee-path issues, overwhelmingly source-defined noncritical `MOVE_BLOCKED`. No
implementation lock or confirmation run occurred. Evidence:
`data/analysis/live-agent-6553250/a2-0b-v1-development-blocker-result.json`.

Per the frozen verdict, v1 is preserved. The active task proceeds only through a
separately frozen r1 repair protocol that models and accounts for supported noncritical
errors while requiring zero critical or unsupported errors.

## R1 protocol freeze — 2026-07-30T15:47:00Z

R1 is frozen at
`docs/a2-0b-referee-evaluation-parity-r1-protocol-2026-07-30.md`. It changes only G3:
24 source-defined noncritical reasons are permitted with focused state-effect tests and
complete accounting; critical, fallback, and unclassified outcomes remain zero-gated.
All v1 RNG, resident reproduction, thread, detector, isolation, and storage gates remain
binding.

## R1 development verdict — 2026-07-30T16:02:00Z

**READY_FOR_IMPLEMENTATION_LOCK.** The final-source 16-map/256-task development panel is
fully terminal with zero critical and zero unclassified issues in both modes. All
ownership, reason, phase, matrix, sorting, and margin invariants pass. The 24-reason
state-effect suite passes 18/18 tests. A one-map trajectory probe covers 16 tasks in each
mode and executes all six standing detectors without error. Evidence:
`data/analysis/live-agent-6553250/a2-0b-r1-development-result.json`.

No confirmation panel has run. The next step is to publish and remotely verify the
implementation commit, then publish a separate hash lock before any 128-map execution.

## R1 implementation lock — 2026-07-30T16:04:00Z

Implementation commit `cd424a19a1f746d72afcfc8b7c824284cdda4012` is remotely verified
on both agent and session branches. The complete direct dependency lock is
`data/analysis/live-agent-6553250/a2-0b-r1-implementation-lock.json`.

No source or locked dependency may now change. Confirmation is authorized only on the
fixed consumed 128-map range, first at one thread and then at 20 threads with external
trajectory dumping. Reviewer acknowledgement remains asynchronous.

## R1 confirmation verdict — 2026-07-30T16:18:00Z

**QUALIFIED.** The locked 2,048-task panel is fully terminal, one/20-thread TSVs are
byte-identical, and the historical legacy target reproduces exactly at 49 catastrophes /
12,749 negative mass. Both modes have zero critical and zero unclassified issues. All
2,048 legacy plus 2,048 referee trajectories decode exactly and run all six detectors.

Continued RNG changes 1,781 tasks; the referee calibration tail is 53 catastrophes /
13,646 negative mass. This is a semantics-change description, not a Phase 1 value
estimate. Canonical result:
`data/analysis/live-agent-6553250/a2-0b-r1-referee-parity-result.json`.

No Phase 1 panel has started.

## Protocol closure — 2026-07-30T17:34:54Z

`chatgpt_1` reviewed and accepted `QUALIFIED` at
`coordination/messages/chatgpt_1/20260730T171700Z-20260730-a2-0b-referee-evaluation-parity-ack.md`.
The named reviewer requirement is satisfied. A2-0b is protocol-closed and may serve only
as the locked substrate for a separately claimed and preregistered A2-1 experiment.

Phase 1 inherits four conditions: locked referee mode only; fresh unconsumed selection and
confirmation ranges; a preregistered policy-owned command-quality gate; and legacy mode
as historical control only. Any locked-dependency change invalidates this closure and
requires A2-0b repetition.
