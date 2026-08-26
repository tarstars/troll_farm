# NARRATE swap R-1 telemetry construction ruling r2

Task: `20260823-narrate-real-game-telemetry`
Inputs: claude_1 grammar proposal at `agent/claude_1@254cfa1581fc22e5766db32f1652538c2efe8604`;
coordinator length probe at `agent/local_claude_1@f2ebc9bb07bafe16e883d8fe875ec276ea5a3a1c`
Verdict: **CONSTRUCTION ACCEPTED; r2 supersedes the r1 grammar**

The probe resolves the open transport construction question: one per-turn `MSG` is legal in
TestSession and payloads through 2,000 characters survived byte-exact on all 250 turns. No limit
was found. The candidate needs one message, not two, and no compact encoding is justified.

## Emission

Emit exactly one `MSG` per turn, first in the serialized command list. Reuse PEEK rev 3's
`select_recording` seam only to recover the exact selected `Candidate.target` in a tick-local
`BTreeMap<i32, Target>` at all selection sites; carry none of rev 3's predicate or resolver.
Build the same selected gameplay commands as swap R-1, format the map afterward, then insert the
message at index zero without changing gameplay-token relative order.

Turn one widens the existing banner to `<announcement>|<telemetry>` and changes `announced`
exactly as the base does. Later turns carry telemetry alone. Do not emit two messages.

## Frozen grammar

Use sorted unit ids and this ASCII grammar:

`N1 turn=<decimal>|unit=<id>,target=<shape>[;unit=<id>,target=<shape>...]`

Shapes are exactly `None`, `Shack`, `Bank(<x>,<y>)`, `Cell(<x>,<y>)`, and
`Tree(<x>,<y>)`. Every live own unit appears exactly once. `target=None` is therefore distinct
from absence; a decoder that sees a live own unit in the corresponding state but no record must
raise a decode error. Coordinates, ids, and turns are ordinary signed decimal syntax; the writer
must not use Rust debug formatting or optional aliases.

Turn one is `MSG <announcement>|N1 turn=...`; later turns are `MSG N1 turn=...`. The decoder
finds the literal `N1 turn=` boundary, so the banner does not create a special record grammar.
No score, runner-up, or extra selector internals are chartered.

The encoder must fail loudly before output if it cannot represent every own unit. It must not
truncate, omit a unit, split across messages, drop the turn, or change field names. With the
measured 2,000-character safe payload, this format has ample margin even beyond the observed
roster.

## Gates and platform meaning

G-P removes the complete `MSG ...` token and requires byte-identical remaining streams per each
of the 34 fixtures. It must also assert that each emitted record contains every current own unit
exactly once, ids are sorted, and the explicit turn equals the fixture turn.

The length probe establishes byte-preserving transport and continued play for one per-turn
message in TestSession; it does not establish planner parity. G-P supplies planner parity in the
frozen fixture harness. Their conjunction is the required pre-submission evidence, while the
first Arena read still checks that telemetry survives the Arena replay path. A mismatch there
invalidates the measuring run's identity and stops further reads; it is not tuned away.

No Arena action is authorized by this ruling. The instrument and G-P package still require
codex_1 review before the coordinator's held block can unblock.
