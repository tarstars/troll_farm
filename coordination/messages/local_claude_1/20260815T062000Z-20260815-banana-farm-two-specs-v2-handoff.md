---
schema_version: 2
type: handoff
task_id: 20260815-banana-farm-two-specs
from: local_claude_1
to: ["codex_1"]
cc: ["user", "claude_1"]
message_id: coordination/messages/local_claude_1/20260815T062000Z-20260815-banana-farm-two-specs-v2-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: 8c34f1534b12291763ad55b87e74cb0b241988c3
artifact_paths: ["docs/superpowers/specs/2026-08-15-banana-farm-spec-a-unconditional.md", "docs/superpowers/specs/2026-08-15-banana-farm-spec-b-conditional.md"]
created_utc: 2026-08-15T06:20:00Z
---

- To: codex_1 (re-review request)
- CC: user, claude_1
- Task: 20260815-banana-farm-two-specs

# handoff: Spec A/B v2 — abort sensor reworked per your review; re-review requested

## For the owner, in plain terms

Your reviewer proved the farm's give-up test was measuring the wrong thing (a defect
inherited from the original CBF design, not new). Version 2 withdraws that test honestly
and puts TWO correctly-specified alternatives in front of you as decision S-1.

## What changed (finding → fix)

- **F1 sensor invalid → §7 rewritten.** Banked-banana-delta sensor withdrawn with all
  three failure directions stated (our replant loop keeps `d_us` at 0; opponent banks own
  bananas; W/K cannot restore provenance) and inheritance from CBF §4 verified and noted.
  Observability grounded in the source: `Plant` has NO owner field (:58–59), both
  inventories readable (:245–256), `scores` (:289), `harvest_power` (:40,47–48,282).
- **OWNER-DECISION S-1 — two candidate sensors, fully specified:** (a) provenance —
  transactional crop-ownership contract (single writer, six transitions, ambiguity fails
  closed to NOT-ours, opponent replacement can never inherit tracking — your F2);
  (b) score-delta — snapshot `view.scores` at FARM entry, abort on K consecutive
  faster-growth turns after W. **Drafted recommendation: (b) primary** — it does not
  hang a one-way abort on the plant-lifecycle inference layer that failed six Banana R2
  rounds, and its bias errs toward aborting (the safe direction); (a) stays on record as
  the only sensor measuring the owner's literal rule.
- **F3 multi-banana cargo → §6:** PLANT exactly one, bank the surplus, resume.
- **F4 measurement overclaim → §12:** exact SE arithmetic (4/arm → 1.06; 2.0 pts =
  1.89 SE), "cleanly resolves" retracted, pre-registered rule as OWNER-DECISION M-1
  (≥2.5 winner / 1.0–2.5 second night pooled / <1.0 indistinguishable).
- **Entry side unchanged** per your concurrence (A-1 materialization, B-1 no floor);
  B-1's justification re-grounded off the dead sensor.
- **§3–§8 byte-identity re-verified independently by me**: identical, SHA `2ae7b9f7…`.

Owner decisions now stacked for return: A-1 (entry anchor), S-1 (sensor), M-1 (decision
rule), plus doctrine freeze and viewer scope. No implementation before the oscillation
gate and owner spec approval; no Arena action.
