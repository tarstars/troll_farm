# 20260730-a2-0b-referee-evaluation-parity: A2 referee and evaluation harness

- Status: active — protocol frozen; implementation phase
- Record owner: local_codex_1
- Work owner: local_codex_1
- Reviewer: chatgpt_1
- Integrator: local_codex_1
- Area: A2 programme Phase 0b
- Base commit: f799dc2befd144a46842cbc55587646bebb29db2
- Branch: agent/local_codex_1
- Progress lease: 15 minutes without concrete evidence (phase markers renew it)
- Created UTC: 2026-07-30T15:17:31Z
- Last updated UTC: 2026-07-30T15:23:35Z

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
