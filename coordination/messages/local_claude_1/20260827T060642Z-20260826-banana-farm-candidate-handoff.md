---
schema_version: 2
type: handoff
task_id: 20260826-banana-farm-candidate
from: local_claude_1
to: ["claude_1", "codex_1"]
cc: ["user", "chatgpt_1"]
message_id: coordination/messages/local_claude_1/20260827T060642Z-20260826-banana-farm-candidate-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: ada5607900e237db4264ccf9c23d17e54253f368
artifact_paths: ["coordination/BOARD.md"]
created_utc: 2026-08-27T06:06:42Z
---

- To: claude_1, codex_1
- CC: user, chatgpt_1
- Task: 20260826-banana-farm-candidate
- Requires acknowledgement: yes — an owner ruling changes what happens to the farm arm

# handoff: OWNER RULING — the farm goes on the ladder to be **watched**, not promoted: claude_1 compacts the farm-on instrument arm into a submission file with its hash and round-trip report; codex_1 does the one parity check; the coordinator submits it as the resident, replacing the champion

The owner is awake, read the night's record, and ruled: *"I want to see with my eyes how the current banana farm plays. Demote the current ladder champion and put the banana farm on the platform."* This overrides last night's release of the queue slot **for viewing purposes only**: the farm failed its validity gate and that verdict stands unchanged — this is not a promotion, not a qualification, and no verdict about the farm's value comes out of it. The champion of record remains the champion.

**claude_1:** produce `cgauto/submissions/candidate-banana-farm-v8-instrument.rs` from `claude_1/farm/arm-instrument.rs` (farm ON, v8 telemetry ON) by exactly the path that produced the champion instrument and bot B — one source, one flag line, compacted, plus the `.sha256` sidecar and `readable/reports/…round-trip.json`, with the generator refusing on any base-hash mismatch. The telemetry arm is the one we want: its games come home annotated, which is the point of watching it. **codex_1:** the single check you did for bot B — with the diagnostic line stripped, the compacted file is identical in play to the panel arm on the 240 games; one line back.

**Order:** the coordinator takes bot B's third reading when it matures (06:31Z), writes the measurement's verdict on the six readings, and then submits the farm. Both of you: nothing else changes; the farm's repair-or-close decision is still open and still the owner's.
