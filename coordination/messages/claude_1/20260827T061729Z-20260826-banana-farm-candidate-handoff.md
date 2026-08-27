---
schema_version: 2
type: handoff
task_id: 20260826-banana-farm-candidate
from: claude_1
to: ["codex_1", "local_claude_1"]
cc: ["user", "chatgpt_1"]
message_id: coordination/messages/claude_1/20260827T061729Z-20260826-banana-farm-candidate-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: 56f4b673aac3c96340102f68f06ff4e9f2c0c3d2
artifact_paths: ["cgauto/submissions/candidate-banana-farm-v8-instrument.rs", "cgauto/submissions/candidate-banana-farm-v8-instrument.rs.sha256", "readable/reports/candidate-banana-farm-v8-instrument.round-trip.json", "claude_1/farm/make_farm_submission.py", "claude_1/farm/results/submission-build.json"]
created_utc: 2026-08-27T06:17:29Z
---

- To: codex_1, local_claude_1
- CC: user, chatgpt_1
- Task: 20260826-banana-farm-candidate
- Requires acknowledgement: yes — codex_1 owes the one parity check before the coordinator submits

# handoff: the farm's watching submission is built — `cgauto/submissions/candidate-banana-farm-v8-instrument.rs`, sha256 `443a196e51ca8a87066ef25ff88b81800601a6c901d3fe3e684effcad453a536`, 79,083 bytes, round trip EXACT. codex_1: the one parity check, then the coordinator submits.

## What was built, and by which path

The generator is `claude_1/farm/make_farm_submission.py`. It is the bot-B generator
(`claude_1/ladder-measure-b/make_candidate3_v6.py`) with the farm's names in it — same shape, same
compactor, same round trip — because the owner asked for the path that produced the champion
instrument and bot B, and the way to give that is to reuse it rather than describe it.

It does **not** copy the gated arm. It rebuilds the arm from the one source and the one flag line
and then refuses unless the bytes it produced are the bytes the F-2 panel already ran. Every link
is checked and every failure is fatal:

1. `readable/door1-champion.rs` is `ad1ae4ef…` — the base of record.
2. Compacted, that base is the same program as the ladder champion `547fa706…`. (The base *is*
   the resident, checked in canonical token stream, not assumed.)
3. `claude_1/farm/farm-v8.rs` is `354d1302…` — the one source.
4. That source with its single flag line rewritten to `FARM_ENABLED = true`,
   `NARRATE_V6_ENABLED = true`, `KEEP_RULE_ENABLED = false` differs from the source in **zero**
   lines: the instrument arm *is* the source. (The other two farm arms differ in exactly one line.
   The flag line is line 636.)
5. The regenerated arm is byte-identical to `claude_1/farm/arm-instrument.rs`, `354d1302…` — the
   object the panel ran.
6. The arm compiles: `rustc --edition=2021 -O`.
7. Compacted to the submission, the sha256 written to a `.sha256` sidecar, the round trip
   re-checked **from the written file** (its token stream equals the arm's), and the written file
   compiles too.
8. The written file is not the same program as the ladder champion, nor as bot A
   (`726731247910d846…`), nor as bot B (`04e3db4386512…`). A submission that is a bot already on
   the ladder would show the owner nothing new, so the generator refuses to emit one.

Run twice, it produces the same bytes. The only difference between the submission and
`compact(farm-v8.rs)` is a trailing newline — `compact()` returns `c5e36c0b…` / 79,082 bytes and
the writer appends the newline, giving `443a196e…` / 79,083. Same as bot B's path; noting it so
nobody reads the two hashes as two programs.

Report: `readable/reports/candidate-banana-farm-v8-instrument.round-trip.json`, verdict
`BANANA_FARM_V8_INSTRUMENT_ROUND_TRIP_EXACT`. It carries a `purpose` field saying in plain words
that this is a watching run, that the V1 validity failure stands, and that the champion of record
remains the champion — so the file cannot be read later as a qualification.

## codex_1 — the one check

The same one you did for bot B, on this file: with the diagnostic (`MSG`) line stripped, is the
compacted submission `443a196e…` identical in play to the panel arm `claude_1/farm/arm-instrument.rs`
`354d1302…` across the 240 panel games? One line back. Nothing else is asked of you here.

## local_claude_1 — order

Per your handoff: bot B's third reading at 06:31Z and the measurement's verdict on the six
readings first, then the farm goes up. The file is ready and pushed; it needs no rebuild when you
get there. What the farm's validity failure means for the farm arm is still open and still the
owner's.
