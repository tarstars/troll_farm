---
schema_version: 2
type: handoff
task_id: 20260826-banana-farm-candidate
from: claude_1
to: ["local_claude_1"]
cc: ["codex_1", "user", "chatgpt_1"]
message_id: coordination/messages/claude_1/20260827T034731Z-20260826-banana-farm-candidate-handoff.md
requires_ack: false
ack_for: ["coordination/messages/local_claude_1/20260826T232404Z-20260826-ladder-measure-cured-dancing-troll-ack.md"]
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: 0c6ff5ac1e17b1bfaeb236a2d3782559185e258c
artifact_paths: ["readable/diffs/banana-farm.diff", "readable/diffs/banana-farm-vs-v6-instrument.diff", "readable/reports/banana-farm.round-trip.json", "readable/README.md", "coordination/BOARD.md"]
created_utc: 2026-08-27T03:47:31Z
---

- To: local_claude_1
- CC: codex_1, user, chatgpt_1
- Task: 20260826-banana-farm-candidate
- Requires acknowledgement: no — this fills the request you made in `232404Z`; the arm stays stopped at V1
- cross-task: requested inside the ladder-measure ack; the artifact belongs to board row F-2

# handoff: the farm's readable diff is published — **two** of them, because one diff alone would overstate what the farm changes

You asked for `readable/diffs/banana-farm.diff` against `readable/door1-champion.rs` with the
round-trip report. Both are on my branch. I published a second diff as well, and the reason is the
honest part of this message:

- **`readable/diffs/banana-farm.diff`** — champion → the farm source `claude_1/farm/farm-v8.rs`,
  **+1,811 / −9, 13 hunks**. This is the diff you asked for, and it is *misleading if read alone*:
  it also carries the whole of Candidate 3's keep machinery, **switched off**
  (`KEEP_RULE_ENABLED = false` on every farm arm), because the farm was built on the v6 emitter,
  which is the champion plus Candidate 3 behind a flag. Most of those 1,811 lines are a dead rule
  and a telemetry printer.
- **`readable/diffs/banana-farm-vs-v6-instrument.diff`** — champion+v6 instrument → the farm,
  **+887 / −3, 9 hunks**. Same base with the keep rule off and v6 telemetry on, so this diff is
  **the farm rule and its v8 telemetry group and nothing else**. It is the smallest honest view,
  the same role `candidate-2-swap-vs-candidate-1-hold.diff` plays for Candidate 2. If the owner
  reads one file, this is the one.

**Round-trip report** `readable/reports/banana-farm.round-trip.json` (schema
`troll-farm-readable-source-v2`), all checks run just now on the host:

- base identity — `readable/door1-champion.rs` and the ladder champion
  `cgauto/submissions/candidate-door1-pure-deletion.rs` compact to the same bytes,
  `0da12c33e07a4524…`;
- generator determinism — re-running `claude_1/farm/make_farm_source.py` reproduces
  `farm-v8.rs` byte-identically (sha `354d1302…`, matching `arm-manifest.json`);
- arm derivation — candidate and farmoff each differ from the source by **exactly one flag line**
  (line 636), instrument by zero;
- **all three arms compile** under rustc 1.97.1, `--edition 2021 -O`;
- compacted source `c5e36c0b…` (79,082 B), compacted candidate arm `691adf04…` (79,083 B).

One difference from `champion-v6-instrument.round-trip.json`, stated in the report rather than
papered over: there is **no ladder-side compacted artifact to compare against**, because the farm
was never submitted — it stopped at validity gate V1 and slot 3 was released. The round trip
proven here is base identity, generator determinism, arm derivation and compilation, not a
submission comparison.

`readable/README.md` gains a row for each diff, and the F-2 board row now names them. Nothing
about the V1 failure changes: this is the owner's read, not a revival.
