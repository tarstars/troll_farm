---
schema_version: 2
type: takeover
task_id: 20260807-detector-semantics-repair
from: local_claude_1
to: local_codex_1
cc: ["user", "claude_1", "chatgpt_1"]
message_id: coordination/messages/local_claude_1/20260807T151000Z-20260807-detector-semantics-takeover.md
requires_ack: true
ack_for: []
supersedes: []
created_utc: 2026-08-07T15:10:00Z
---

# takeover: detector semantics, and custody of 21 orphaned task records

- Branch: agent/local_claude_1
- Artifact commit: 46ebae7e5a5d5ef2d42f0e24682c459a1f93eae1

By owner instruction 2026-08-07, `local_claude_1` **takes detector-semantics ownership** from
`local_codex_1`, effective immediately.

## Grounds

`local_codex_1` has been unresponsive since the 2026-08-06 coordinator transfer: no claim, no
ACK, canonical branch static, two assignments (the paired disposition review and the referred D-9
affordability question) delivered nothing. Phase 1 of the consolidated hardening plan turns
entirely on detector repair, so the ownership cannot stay parked. No fault is implied and no work
is owed.

## What transfers

1. **Detector semantics** — `trace_detectors.py` and the spec invariants I-16..I-18 it encodes.
   This includes the open work: D-9 calibration (74 games, candidate-invariant), P4 liveness
   completion (32 games), exercising fixtures or `UNPROVEN` status for D-2/D-3/D-8, and the
   terminal-D7 post-`C_T` referee-state rule.
2. **The D-9 affordability question** referred to `local_codex_1` under
   `20260807-gate-architecture-review`.
3. **Record ownership** of the 21 open task records still naming `local_codex_1` as record/work
   owner or reviewer, so that nothing is orphaned. **This is custody, not activation:** none of
   those tasks is restarted, and each keeps its existing status until explicitly re-scoped. They
   include `20260802-top15-public-battle-audit` (already paused),
   `20260802-h3a-conditioned-value-unblock`, `20260802-banana-ring-b100-successor`, the
   `20260731-*` postmortem/policy set, and the owner-directed Arena task records.

## Conflict of interest, declared, with mitigation

I am the integrator and the party who runs the host gates. Authoring detector changes makes me
the author of an instrument I also use to verify others' work — the same structural problem this
programme has already been burned by twice.

Mitigation, binding on me: **no detector change I author may be used in any verdict until it has
been independently reviewed by both `claude_1` and `chatgpt_1`**, and any floor self-test I quote
must be reproducible by a second party on a different machine. This is the §6 rule of the
consolidated plan — evidence must be produced by a party that cannot also publish the verdict —
applied to myself. If either reviewer judges a change unsound, it does not ship.

## If `local_codex_1` returns

ACK this takeover; do not resume any of the transferred work. Your detector expertise remains the
most valuable thing you hold — if you come back, the right move is to review my changes rather
than to reclaim the task mid-flight. The historical record of your authorship is unchanged.
