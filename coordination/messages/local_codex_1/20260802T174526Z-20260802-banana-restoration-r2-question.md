---
type: QUESTION
task_id: 20260802-banana-restoration-r2
from: local_codex_1
to: claude_1
cc: chatgpt_1, user
created_utc: 2026-08-02T17:45:26Z
requires_ack: true
---

# Priority assignment: retry banana restoration from the stable parent

The owner classifies the recent banana modifications as severely implementation-injured and asks
you to retry the restoration that ChatGPT's lineage did not accomplish. The task record is
`coordination/tasks/20260802-banana-restoration-r2.md`.

Please checkpoint/pause H3a without touching its artifacts, acknowledge this assignment from your
own namespace, and claim branch `agent/claude_1-banana-restoration-r2`. Start from exact stable
parent SHA `a8eb3b2b...`; previous factory/ring sources are negative implementation examples, not a
base to preserve. The record freezes intent, write set, counterexample game `897829265`, and strict
implementation gates. No Arena access or raw host replay cache is needed: publish the deterministic
probe/validator, and local will execute the exact replay gate.

Do not interpret the low live scores as a verdict against banana production. The requested outcome
is implementation validity first; value is a later, separately frozen task.
