---
schema_version: 2
type: handoff
task_id: 20260903-three-troll-optimized-start
from: chatgpt_2
to: ["local_claude_1"]
cc: ["user", "claude_1"]
message_id: coordination/messages/chatgpt_2/20260904T052926Z-20260903-three-troll-optimized-start-handoff.md
requires_ack: true
ack_for: ["coordination/messages/local_claude_1/20260904T043848Z-20260903-three-troll-optimized-start-handoff.md"]
supersedes: []
artifact_ref: agent/chatgpt_2
artifact_commit: 5b11f9f0dab68b9ff4b0930fe362aba23e96c0d6
artifact_paths: ["chatgpt_2/three-troll-optimized-start/"]
created_utc: 2026-09-04T05:29:26Z
---

# HANDOFF — recovered three-troll optimized-start artifact under `chatgpt_2`

The delivery requested by the owner is complete. The artifact commit above was pushed to
`agent/chatgpt_2` before this message was created. It is a merge commit whose second parent is the
incoming-assignment/main commit `d01d5025e22d3acdc68c94782813d15eda770c6c`, so the pin is reachable
from this agent's branch and contains current `main`.

## Delivered

The complete rescue subtree is now available at `chatgpt_2/three-troll-optimized-start/`, including:

- compacted candidate: `candidate-three-troll-optimized-v6-instrument.rs`;
- compacted control: `candidate-turn2-second-control-v6-instrument.rs`;
- readable candidate and control;
- all four generated-source SHA-256 sidecars;
- `make_candidate.py` and `optimizer.rs.in`;
- diffs, build/result analyzer, all raw logs and JSON results;
- corrected `README.md`, corrected `RESULTS.md`, and `PROVENANCE.md`.

## Recovery and static verification

- Source rescue ref: `rescue/chatgpt1-three-troll-optimized-start-2026-09-03`.
- Source rescue commit: `8da821a28db9658062bfb772e2e63b6f47f4868d`.
- Rescue subtree SHA: `918db257e9a96ac326b748a2caeb1269c32695d9`.
- Historical payload: 47 files — 19 root blobs plus 28 files under `results/`.
- Corrected publication preserves all 47 historical files and adds one provenance page.
- The raw results tree remains exactly `8bf76bf3b077de79b221d7919984014a8ed8aa55`.
- Candidate blob remains exactly `3007ed78a5fc51ff0228968fc57799e724728f4a`, 90,070 units.
- Control blob remains exactly `8b5e5da0b6f4200b354f5295156f56d629f37f6b`, 90,071 units.
- Readable-source, generator, optimizer, sidecar, diff, log and raw-JSON blobs are reused from the
  rescue tree. Only README/RESULTS were amended; PROVENANCE is new.
- The generator resolves its directory through `Path(__file__).resolve().parent`, so moving the
  subtree from `chatgpt_1` to `chatgpt_2` does not require a code change. README now shows the correct
  invocation path.
- The candidate sidecar remains
  `d994b3fb6a1271105167efc09f85aae83623cd27b1534713cba32de922df1933`.

This connector-only recovery did not rerun compilation or games. The incoming handoff records the
coordinator's independent byte-for-byte regeneration and zero-error compilation of both arms; this
pass independently checked tree completeness, required paths, preserved blob identities, sizes,
sidecars, branch ancestry and namespace placement.

## Scientific disposition

The verdict remains **`DEAD_AS_BOT`**. Candidate smoke was 19/24 and control smoke was 15/24 against
the required 24/24; the five and nine stalled maps are the first issue for any revival. The control
is not mechanics-valid.

The later instrument ruling is recorded in README/RESULTS: paired win-rate difference is retired as
a selector because draw-rate variation made it unreliable. Paired score-margin difference with its
95% interval is now the selector. The historical `+0.0500` win-difference headline is retained only
as historical evidence, not as promotion evidence.

No `main`, board, champion, ladder, platform, cluster or Arena action was taken. This delivery does
not reopen the dead card.
