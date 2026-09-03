---
schema_version: 2
type: correction
task_id: 20260902-norxondor-port
from: codex_1
to: ["claude_1", "local_claude_1"]
cc: ["user"]
message_id: coordination/messages/codex_1/20260902T101135Z-20260902-norxondor-port-correction.md
requires_ack: true
ack_for: []
supersedes: ["coordination/messages/codex_1/20260902T095100Z-20260902-norxondor-port-handoff.md"]
created_utc: 2026-09-02T10:11:35Z
artifact_ref: agent/codex_1
artifact_commit: 7e45fa4c6b3acddcda97cbb9da077d4d9520aded
artifact_paths: ["codex_1/norxondor-port/DESIGN-2026-09-02.md", "codex_1/norxondor-port/BUILD-2026-09-02-v2.md", "readable/norxondor-port.rs", "readable/diffs/norxondor-port-v2.diff", "cgauto/submissions/candidate-norxondor-port-v2.rs", "cgauto/submissions/candidate-norxondor-port-v2.rs.sha256"]
---

- To: claude_1, local_claude_1
- CC: user
- Task: 20260902-norxondor-port
- Requires acknowledgement: yes — this is the corrected build for reproduction and the same-field panel

# CORRECTION — v2 applies the complete design review and replaces the incomplete v1 delivery

This supersedes the 09:51Z handoff. That delivery applied claude_1's review but not the
coordinator's 09:23Z policy, which became visible only in the final fetch. Its `f15159ca…` v1
submission remains immutable and must not enter reproduction or the panel.

The complete-review artifact is `candidate-norxondor-port-v2.rs`, SHA-256
`411b0565ecda0139c96daaec02d26df0a7304c9b0aefa5c3823ff54ac1a9a8c1`, at the pinned commit. It adds
the unaffordable-floor roster cutoffs (129 / 144 / 154) while preserving the turn-185 hopeless-floor
projection as an earlier exit. It also broadens the one D-mode job from banana-only to deposited
banana first, then the size-1 sapling with least health. Same-turn affordable TRAIN still wins at a
cutoff. The design note and readable diff carry these rules.

## Corrected validation

- stable Rust compile: PASS for readable and compact forms
- targeted mechanics: 15/15 PASS, including all three roster cutoffs and non-banana fallback
- new-bot preflight bed: 34/34 played; 34/34 deterministic; 34/34 compact equals readable; zero
  telemetry errors; sidecar matches the v2 artifact
- 24 pinned maps on both seats: 48 games, zero policy errors, zero opponent errors, zero timeouts
- pipe-inclusive timing on 14,083 turns: p99 8.624 ms, maximum 18.482 ms
- switch trace over those 48 games: roster 2 median 129 (8/12 at cutoff), roster 3 median 144
  (16/25 at cutoff), roster 4 median 145 (5/11 at cutoff 154); every earlier switch was the retained
  projection and no switch passed its roster cutoff
- protected orchard source remains SHA-256
  `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`

The direct duel is still informational, not the selector: v2 won 1/48, scoring 117.1 versus 182.6
on average, with mean margin -65.52. Please reproduce v2 byte-for-byte and run the carded
same-local-field rung 1. No network, platform, Arena, ladder, or queue mutation was made.
