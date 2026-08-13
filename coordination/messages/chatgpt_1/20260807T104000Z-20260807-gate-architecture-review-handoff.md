---
schema_version: 2
type: handoff
task_id: 20260807-gate-architecture-review
from: chatgpt_1
to: local_claude_1
cc: ["user", "claude_1", "local_codex_1"]
message_id: coordination/messages/chatgpt_1/20260807T104000Z-20260807-gate-architecture-review-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/chatgpt_1
artifact_commit: 8daad3f21ec2112f82d4b78cf275c9f90064a054
artifact_paths: ["chatgpt_1/gate-architecture-review-2026-08-07.md"]
created_utc: 2026-08-07T10:40:00Z
---

# Handoff: acceptance-gate architecture review

Final verdict: **`REVISION_REQUIRED`**.

## Accepted directions

The mandatory floor self-test, complete provenance manifest, `UNPROVEN` status for unexercised
detectors, safety/regression/calibration taxonomy, committed bite-tests, and per-map rather than
aggregate reasoning should be preserved.

## Blocking findings

1. The proposal places D-1 and D-4 in tolerant Tier B and permits floor-relative deltas/waivers.
   This directly violates the binding raw-zero/no-exemption owner rule.
2. It moves D-9 to report-only Tier Q, although D-5..D-9 remain standing blockers. A defective or
   uncalibrated required detector must make the gate unready, not green.
3. Section 8's requirement that the unmodified parent be accepted is impossible while the
   independently established parent floor contains 35 D-1 and 6 D-4 episodes. The parent must be
   repaired first; the two-sided test must use the repaired reference.
4. The waiver ledger is more auditable than runtime parent comparison but remains semantically an
   exemption and can mask a new causal defect with the same signature.
5. Per-map count delta `<= 0` can replace one episode with a different or more severe same-map
   episode; strict `= 0` would also reject genuine fixes. Use normalized signature-multiset
   dominance for any owner-permitted comparative detector; D-1/D-4 remain absolute zero.
6. Tier recomputation is underdefined and candidate-dependent: the parent-only FST cannot compute
   variance across candidates. A frozen calibration corpus and versioned tier manifest are
   required.
7. Required Q/U detectors need a `GATE_UNREADY`/`UNPROVEN` state, not automatic report-only
   treatment.
8. D-9's `74` and the host's `196` are reconciled: 74 affected games versus 196 individual
   episodes. The design also uses game incidence for D-1 `32` versus 35 episodes and D-6 `9`
   versus 15 episodes. Equal affected-game counts alone do not prove identical signatures or
   multiplicities.
9. The FST hash key omits material transitive inputs such as the panel runner, referee, map
   generator, harness helpers and toolchain versions.

The complete report includes the exact coordinator reproduction command and SHA-bound inputs. It
makes no host-run or candidate verdict claim.

## Owner-rule incompatibilities

The current D-1/D-4 Tier-B treatment, D-9 report-only treatment, and unmodified-parent acceptance
criterion are explicitly incompatible with the standing owner rule.

No gate, detector, candidate, workflow, host run, value protocol, TestSession, submission,
restore, or Arena action was performed.
