---
schema_version: 2
type: handoff
task_id: 20260810-manifest-implementation
from: chatgpt_1
to: claude_1
cc: ["user", "local_claude_1", "local_codex_1"]
message_id: coordination/messages/chatgpt_1/20260810T100000Z-20260810-decision-packet-spec-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/chatgpt_1
artifact_commit: 593c995f7640775f32344431d74cbc3bd4881c8b
artifact_paths: ["chatgpt_1/decision-packet-spec-2026-08-10.md"]
created_utc: 2026-08-10T10:00:00Z
---

# Handoff: M1 Decision Packet specification frozen for implementation

I completed the assigned M1 specification for exact subject
`submitted-agent6593838-readable-no-orchard.rs`, SHA-256 `98628e98…`.

The packet is a complete pipeline trace, not a score dump. It specifies:

- exact source/tool/state identity and trust labels;
- code-owned stage, intent, priority-class and source-site registries;
- mode selection, generator entry/skip and early-return events;
- finite opportunity accounting with typed exclusion reasons;
- every candidate, exact f64 score and term decomposition;
- state-conditioned and site-reachable attainable ranges with proof status;
- every two-unit pair, compatibility/stock rejection and exact tie order;
- forced candidate replacement;
- resolver inputs, alternatives, ranking, pre/post commands and typed rewrite reason;
- persistent-state updates;
- optional execution evidence separated as unavailable, provisional or accepted;
- blind/reveal projections for independent M3b adjudication;
- independent packet replay and non-interference requirements;
- literal M1/M2/M3 fixtures, provisional `m040-s1`, anti-overfit controls and mutation suite.

Two requirements are deliberately stronger than a conventional trace:

1. the verifier must reconstruct selection and resolver output without calling the candidate's own
   helpers;
2. every score term carries a real attainable range, proof method and assumptions, so syntactic
   but unreachable bounds and latent-but-single-call-site variability cannot pass.

Existing N4 capture machinery may be reused, but it is SHA-locked to a different resident and is
not completion until retargeted and revalidated against `98628e98`.

Implementation path and full acceptance checklist:

`chatgpt_1/decision-packet-spec-2026-08-10.md`

Tooling/analysis only. No bot behavior, candidate, detector, gate, host-value protocol,
TestSession, submission, restore or Arena action is authorized.
