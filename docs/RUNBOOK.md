# RUNBOOK — autonomous sessions (rewritten 2026-07-29, post-terminal era)

How to advance this project in any session, at any model tier, without damaging it.
Written by Fable (`claude_1`); cheap sessions execute, they do not redesign.

## The goal phrase (use verbatim when starting an autonomous session)

> Advance the LIVE PRIORITIES section of `docs/BACKLOG.md` top-down (P0 audits first).
> Audits are read-only; any experiment runs only under an already-frozen protocol with
> immutable thresholds — a kill rule firing is a successful outcome. Follow
> `coordination/multi-agent-protocol.md`: check the inbox, claim before working, keep
> your write set. Never perform any arena/platform write, submission, or TestSession —
> and no new platform-read categories — unless the standing authorization in
> `docs/STATE.md` §3 covers it AND its conditions are met (QUALIFIED verdict, gain above
> the noise band, full runbook, owner notified). Autonomous sessions do not exercise the
> arena-controller role; leave a STOP marker instead. Stop at any failed gate, STOP marker, or owner-level decision (H2 go/no-go,
> anything touching the arena).

## Read order at session start

1. `docs/STATE.md` — live state; §4 names the taxonomy and what awaits the owner.
2. `docs/CONSTRAINTS.md` — before proposing anything (the closure record is the asset).
3. `docs/BACKLOG.md` — LIVE PRIORITIES at top; below the divider is historical record.
4. `coordination/README.md` + `python3 scripts/inbox_sweep.py --me <id> --fetch` —
   mandatory before writing anything; ack what requires it, from your own namespace.
5. For any hypothesis: `docs/rank-hypotheses-2026-07-29.md` AND its review in
   `docs/reviews/` — the review's verdicts are integrated policy.

## Model roles

- P0/P1 read-only audits: sonnet-class executes well; haiku reviews mechanical gates.
- Fable checkpoints (leave a STOP marker in STATE §4 and end the session rather than
  attempt these cheaply): authoring any new frozen protocol; adjudicating a gate;
  integrator conflict resolution under the coordination protocol; anything about H2
  programme design; any CONSTRAINTS reopening argument.
- The arena controller role (submissions) is never exercised by an autonomous session.

## Per-experiment obligations (unchanged house rules)

- Protocol (frozen) → lock (hashes) → run → result doc with per-gate verdicts.
  Byte-identical 1-vs-20-thread repeats; `LC_ALL=C` for text verification; bulk rows to
  the external root (preflight `python3 cgauto/check_external_storage.py
  --required-free-gib 5`; stop if the volume is absent).
- Afterwards: ledger entry in vol 2; CONSTRAINTS bullet for anything closed; STATE §4
  update; commit artifacts + docs together; push (`origin/session-2026-07-01`).
- Never reuse consumed seed ranges for selection; never adjust thresholds after data;
  never tune a closed branch. Phase markers after every phase (they also renew the
  coordination lease).

## Hard invariants (violating these breaks other agents' work)

- `rust/src/bin/yamo_orchard_live.rs` byte-exact, SHA-256 prefix `fff6669b` — verify at
  session start and end. Compile-then-restore if a protocol modifies it.
- No formatters over `rust/src/bin/` or `cgauto/` — experiment locks record file hashes.
- Sealed partitions stay sealed (STATE §3 list). `data/raw/games/` and the 05:17 cron
  stay undisturbed. `api_submit.py` default stays the live resident source.

## STOP-and-ask triggers (end the session with a STOP marker in STATE §4)

- Any integrity-gate failure without a mechanics-only repair authorized in the
  protocol's own text.
- Any ambiguity requiring a design decision; any CONSTRAINTS conflict.
- Anything touching the arena, submissions, or sealed partitions.
- The H2 Architecture-2 go/no-go and any owner-taxonomy change.

## Cheap filler tasks (safe any time)

- Weekly H12 surveillance refresh: rerun the comparative waste baseline + roster pricing
  on the newest corpus; report deltas only.
- B5.3 cold-file migration (only after ~2026-08-03; copy-verify-symlink per
  `docs/storage-policy.md`).
- Atlas upkeep after any integrated result (`python3 cgauto/make_ledger_atlas_pdf.py`).
- Cargo cap rule: `rust/target` > ~10 GB at session end → delete `debug/`, keep
  `release/` (`libtroll_farm.so` serves the ctypes tests).

## Fable re-entry prompt (for the user, at a checkpoint)

> You are claude_1 (integrator, arena controller). Read docs/STATE.md, sweep the inbox
> (`python3 scripts/inbox_sweep.py --me claude_1 --fetch`), read the newest ledger
> entries and any pending handoffs; adjudicate/integrate; update
> STATE/BACKLOG/CONSTRAINTS; author or revise protocols only as warranted; push.

## Compute guidance

Local 20-thread CPU for panels (≈4k paired episodes ≈ hours); YT for genuinely >1 h
independent batches under the parity rules; GPU only behind the CPU/GPU parity gate
(atlas §19). H10's spatial probe, if ever authorized, starts with the cheap CPU probe,
not the GPU programme.
