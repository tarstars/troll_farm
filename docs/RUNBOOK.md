# RUNBOOK — autonomous sessions on a budget (2026-07-27)

How to advance this project when the high-capability model (Fable) is unavailable or
being conserved. Written by Fable; cheap sessions execute, they do not redesign.

## The goal phrase (use verbatim when starting an autonomous session)

> Advance `docs/BACKLOG.md` top-down. Every experiment runs under its already-frozen
> protocol; thresholds and kill rules are immutable; a kill rule firing is a successful
> outcome, not a failure. Stop at any failed gate or STOP marker. Never perform any
> arena/platform write, submission, or TestSession game — and no passive platform reads —
> without explicit user authorization in this session.

## Read order at session start

1. `docs/STATE.md` (live state; §4 names the active protocol and any STOP marker)
2. `docs/CONSTRAINTS.md` (check before proposing anything)
3. `docs/BACKLOG.md` (what is next and its gates)
4. The active frozen protocol (currently
   `data/analysis/live-agent-6553250/d169a-resident-option-interface-envelope-protocol-2026-07-27.md`)

## Model roles

- Session orchestrator: sonnet-class is sufficient for executing frozen protocols.
- Implementer subagents: sonnet. Reviewers of mechanical gates: haiku.
- Fable is reserved for two checkpoints only: adjudicating D169's gate (and D169b if it
  runs), and authoring D170 if D169 passes. Do not attempt D170 design with a cheaper
  model — leave the STOP marker in STATE §4 and end the session.

## Per-experiment obligations (unchanged house rules)

- Protocol (already frozen) → lock (hashes before run) → run → result doc with explicit
  per-gate verdicts. Byte-identical 1-vs-20-thread repeats. `LC_ALL=C` for text-matching
  verification. Bulk rows to the external `artifacts/` root (preflight
  `python3 cgauto/check_external_storage.py --required-free-gib 5`; stop if the USB
  volume is absent).
- Afterwards: one ledger entry in vol 2; a CONSTRAINTS bullet for anything closed; a
  STATE §4 update; commit experiment artifacts + doc updates together.
- Never reuse consumed seed ranges for selection; never adjust a threshold after seeing
  data; never tune a closed branch.

## STOP-and-ask triggers (end the session with a STOP marker in STATE §4)

- Any integrity gate failure without a mechanics-only repair already authorized by the
  protocol's own text.
- Any ambiguity about frozen semantics that would require a design decision.
- Anything that would touch the arena, submissions, or the sealed partitions
  (maps 9,844,200–215; the 11 sealed confirmation games; the official-map holdout).
- The D169 decision tree's STOP points (PASS → Fable adjudication; BORDERLINE after
  D169b; KILL → record and hold).

## Cheap filler tasks (safe for any session, any time)

- **B3.2** — execution-waste sweep on the newest corpus snapshot (read-only motion/idle
  audit over `data/raw/snapshots/20260727T130712Z-d61p/`; report or closure bullet).
- **B5.1** — make `cargo test --workspace` green: feature-gate or fix
  `rust/src/bin/d35c_provenance_competitive_bundle_oracle_impl.rs` (311 pre-existing
  compile errors) without changing any frozen module's behavior.
- Cargo cap rule (AGENTS.md): if `rust/target` > ~10 GB at session end, delete
  `rust/target/debug`, keep `release/`.

## Fable re-entry prompt (for the user, at a checkpoint)

> Read docs/STATE.md and the newest result doc in the ledger; adjudicate the frozen gate;
> update STATE/BACKLOG/CONSTRAINTS; author the next protocol if warranted.

## Compute guidance

- D169 is local-CPU (≈14k episodes + byte-identity repeat; hours on 20 threads). YT only
  for genuinely >1 h independent batches, under the established parity/runtime rules.
  GPU stays out of any selected path (CPU/GPU parity gate — see the atlas, §18).
