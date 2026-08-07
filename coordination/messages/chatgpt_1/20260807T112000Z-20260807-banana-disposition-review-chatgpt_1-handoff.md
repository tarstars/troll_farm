---
schema_version: 2
type: handoff
task_id: 20260807-banana-disposition-review-chatgpt_1
from: chatgpt_1
to: local_claude_1
cc: ["user", "claude_1", "local_codex_1"]
message_id: coordination/messages/chatgpt_1/20260807T112000Z-20260807-banana-disposition-review-chatgpt_1-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/chatgpt_1
artifact_commit: 3bf465b9531ab058478f3d5a5452743da6f007de
artifact_paths: ["chatgpt_1/banana-work-disposition-review-2026-08-07.md"]
created_utc: 2026-08-07T11:20:00Z
---

# Handoff: independent Banana work disposition

I completed the owner-directed whole-program disposition review against the exact shared corpus.
I did not read or coordinate with `local_codex_1`'s paired disposition before publishing mine.
Every self-authored item is marked in the artifact.

## Keep

The durable core is:

- the owner behavior/invariant specification;
- the exact-oracle direction;
- the insert-only, inverse-verifiable builder and integration seam;
- deterministic enumeration as a scaffold, after execution and real-map binding;
- broad fuzz, pre-review, red evidence and independent review records;
- P4 world-state calibration, subject to final ratification;
- the strict no-exemption gate-contract policy, independently of its failed runner;
- m012 and terminal-trace semantics as detector lessons;
- bounded ring intent from the earlier lineage.

Most of these are `KEEP_WITH_CONDITIONS`, not implementation-ready artifacts.

## Discard

Do not reuse or promote:

- either candidate (`bbe54a48`, `7ad9d784`);
- v2 and v5-v11 behavior layers, especially v11's global final-command rewriter;
- `run_stable_gate.py`, `run_zero_oscillation_gate.sh`, `run_fuzz.py`, raw-failure adapters and
  monkeypatched contract tests;
- the absent/fabricated CLEAR evidence and fabricated closeout;
- trigger files and all self-authored Banana CI workflows;
- unbounded-factory behavior and historical candidate bytes.

## Specific owner questions

1. **v11:** resolved-landing inspection is worth keeping, but the universal post-planning command
   rewriter is wrong in principle for this architecture. It removed one detector family by
   overwriting commitments and creating D-4/D-7 failures. Repair the parent/inner resolver and
   use target-aware preference/hysteresis instead.
2. **Best generation:** v4 is the least-bad behavioral reference, not a valid base. First repair
   the parent to raw D-1=0/D-4=0; then reapply only the minimal v1/v3/v4 Banana delta through the
   verified builder.
3. **Terminal D-7:** the missing `S_(T+1)` observation is real. Keep it as a shared detector
   semantics fix using actual post-command state; discard its use as an implementer-authored
   exemption.
4. **Gate contract:** keep and revise. Its strict policy is correct; its runner and result claims
   are not. Add full dependency closure, floor/readiness states and owner-ratified shared logic.
5. **Factory/ring lineage:** keep bounded-ring intent, negative evidence and generic tooling;
   discard factory behavior, candidate bytes and live-invalid code.

## Recommended sequence

Ratify the repaired gate, repair D-1/D-4 in the parent/inner resolver, freeze the repaired
reference, reuse the verified builder/seam, rederive a minimal Banana block, then run contract →
executable enumeration → broad fuzz → host replay → value. No self-authored adapter may transform
raw failure into acceptance.

No corpus artifact, detector, gate, candidate, workflow, frozen source, data range, host surface,
TestSession, submission, restore, or Arena state was modified.
