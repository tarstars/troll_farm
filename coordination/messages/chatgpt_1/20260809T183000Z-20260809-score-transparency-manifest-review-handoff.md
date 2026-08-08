---
schema_version: 2
type: handoff
task_id: 20260809-score-transparency-manifest
from: chatgpt_1
to: ["local_claude_1"]
cc: ["user", "claude_1", "local_codex_1"]
message_id: coordination/messages/chatgpt_1/20260809T183000Z-20260809-score-transparency-manifest-review-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/chatgpt_1
artifact_commit: 7c7a7c3b309b228312c6fbb7dbe32b3197260534
artifact_paths: ["chatgpt_1/score-transparency-manifest-review-2026-08-09.md"]
created_utc: 2026-08-09T18:30:00Z
---

# Handoff: accept the transparency direction; revise the model before scheduling

I completed the requested committed-source review of the owner manifest.

Disposition: **`ACCEPT_DIRECTION — REVISE_PREMISE_BEFORE_SCHEDULING`**.

## Central correction

The bot is not merely "weights on actions". Its behavior is a hybrid pipeline:

1. persistent-state/mode selection;
2. candidate generation, filtering and early returns;
3. scalar scoring;
4. pair compatibility and score aggregation;
5. forced candidate replacement;
6. post-selection movement rewriting;
7. persistent commitment updates.

A static `intention -> number` table would document the middle while leaving the same eligibility,
compatibility and planner/resolver opacity that caused the oscillation misdiagnoses.

## Answer to the owner's prioritization question

The first deliverable should be one code-generated, versioned **Decision Packet** for a turn. It
must expose:

- mode and candidate generators entered;
- every candidate and exclusion reason;
- intent, semantic target, predicted landing, priority class and score terms;
- pair compatibility/stock rejection reasons;
- selected pair and alternatives;
- command before/after resolver rewriting, with typed reason;
- realized execution and progress when an accepted referee is available.

This packet is the maintainable bridge and debugging substrate. The prose bridge, oscillation
library and hierarchy audit should be generated from or checked against it.

## Other review conclusions

- "Big steps encode intention" is partly true but must remain a per-band hypothesis. Many
  intentions are encoded by control flow and candidate availability rather than scores.
- The `3900` chop range is a reason to audit, not by itself proof of a bad crossing; only
  co-reachable alternatives should be compared.
- The two-worker selector sums scores, so the audit must include team-level pair trades and
  compatibility, not only per-action ranges.
- A manually maintained bridge is rejected as the authority. Candidate metadata and generated
  documentation need drift checks, while independently judged situations remain the truth layer.
- The oscillation situation library is worth starting now with source-pinned literal states and
  explicit trust labels. Full-game outcomes from an unaccepted referee stay provisional;
  `m040-s1` is specifically provisional.

Full review:

`chatgpt_1/score-transparency-manifest-review-2026-08-09.md`

No implementation, candidate, detector, gate, referee, host run, TestSession, submission, restore
or Arena action was performed or authorized.