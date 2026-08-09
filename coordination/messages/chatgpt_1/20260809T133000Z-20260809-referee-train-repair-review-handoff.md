---
schema_version: 2
type: handoff
task_id: 20260809-referee-train-repair
from: chatgpt_1
to: local_claude_1
cc: ["user", "claude_1", "local_codex_1"]
message_id: coordination/messages/chatgpt_1/20260809T133000Z-20260809-referee-train-repair-review-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/chatgpt_1
artifact_commit: 2a2e7001f40497f80b07c4a10b691121182e0e8b
artifact_paths: ["chatgpt_1/referee-train-repair-review-2026-08-09.md"]
created_utc: 2026-08-09T13:30:00Z
---

# Handoff: TRAIN repair exposes real defects but is not engine-conformant

I completed the assigned adversarial acceptance review of exact artifact commit
`306892189b7c705cb3251c107cc6669295785e0c` against the frozen acceptance contract.

Verdict: **`REVISION_REQUIRED — NOT ACCEPTED`**.  
Gate disposition: **the panel remains `GATE_UNREADY`**.

## Accepted and worth preserving

- explicit known-verb dispatch and fail-closed unknown verbs;
- discovery and implementation direction for the previously discarded MINE verb;
- bill, iron guard, spawn field and occupied-shack mechanics in isolation;
- both real `m040` identities remaining non-vacuous;
- the new `m040-s1` full-wood D-1/P2 episode, which demonstrates that repairing TRAIN exposes a
  real two-worker banking defect rather than merely changing a number;
- corpus-bump direction and the honest record of the initially surviving cap mutation.

## Acceptance blockers

1. **Wrong mechanics authority.** The referee enforces the resident bot's `n >= 2` and final-20-turn
   self-restraint as game legality. `rust/src/game/engine.rs::apply_train` enforces neither, and the
   frozen contract explicitly requires `n >= 2` TRAIN to succeed when affordable and the shack is
   free.
2. **Malformed TRAIN fails open.** Short arity is a no-op, extra fields are ignored, and
   non-integers become zero. Contract C3 requires a structured fail-closed row.
3. **Only TRAIN is reordered.** The rest of the command line remains textual rather than the fixed
   engine phase order, so PICK/DROP funding, MINE/DROP, PLANT/CHOP and other interactions can produce
   a different world.
4. **No one-command-per-unit parser.** Each fragment is delegated separately, so one unit can
   execute multiple non-TRAIN actions in one turn.
5. **No differential oracle.** No committed test runs the same case through `sim.engine.step` and
   compares the complete post-state.
6. **Result/provenance schema is incomplete.** Rows lack command-execution status, TRAIN/spawn event
   records and the referee hash; an unsupported command aborts before the unready row is retained.
7. **Version pinning fails open.** Missing version keys inherit the current values from DEFAULTS and
   are falsely labelled current.
8. **`m040` tests are partial.** They do not pin exact spawn/bill/events/hashes or old rows as
   machine-readable `instrument_invalid` evidence; the floor bot is not SHA-pinned in the test.
9. **Load-bearing evidence is scratch-only.** The floor configs/results and mutation runner/results
   are not committed, and the modified config is omitted from the implementation handoff's
   `artifact_paths`.
10. **MINE remains unvalidated against the differential engine and shares the phase/parser drift.**

The full clause-by-clause matrix and corrective sequence are in:

`chatgpt_1/referee-train-repair-review-2026-08-09.md`.

Required next implementation shape: engine-authoritative TRAIN without bot caps; strict
parse-before-mutate; first non-TRAIN command per unit; full phase ordering; differential state
checks; explicit next-id/event/provenance schema; strengthened `m040` fixtures; committed evidence
packet; then execution review and a fresh adversarial acceptance pass.

The reported `118 -> 119` result may be honest and the new episode is useful, but neither is
accepted as gate calibration while the referee can still diverge from the engine.

No bot, candidate, detector, value protocol, host panel, TestSession, submission, restore or Arena
action was performed or authorized.
