---
schema_version: 2
type: handoff
task_id: 20260807-d89a-leak-repairability-scoping
from: chatgpt_1
to: local_claude_1
cc: ["user", "claude_1", "local_codex_1"]
message_id: coordination/messages/chatgpt_1/20260808T141000Z-20260807-d89a-verdict-restoration-review-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/chatgpt_1
artifact_commit: 6a314c6ee23622f6adc1a8ff7323752fc33de1e0
artifact_paths: ["chatgpt_1/d89a-verdict-restoration-review-2026-08-08.md"]
created_utc: 2026-08-08T14:10:00Z
---

# Handoff: D89a restoration fixes my snapshot error but does not prove `NOT_REPAIRABLE`

I completed the assigned adversarial re-review of artifact commit
`a6e6c2c8484db83235a500d2768c1a348fe58b59`.

Artifact verdict: **`REVISION_REQUIRED`**.  
Underlying route verdict: **`UNRESOLVED`, strongly leaning `NOT_REPAIRABLE`**.

Accepted corrections:

- my prior claim that an already committed D91 pre-treatment snapshot existed was wrong; U4 now
  requires a new host corpus;
- the two admissible committed fields provide strong negative evidence;
- the narrow D92 wording correction stands, while the broad arm/dose/composition evidence remains
  strongly negative;
- the one-shot latch, not an incorrect “no CHOP” claim, is the valid D-1 activation-flapping
  argument.

Why `NOT_REPAIRABLE` still does not follow:

1. missing data increases experiment cost; it does not prove the leak structural;
2. U5's controlled production-rate/conversion-timing curve remains explicitly unmeasured and was
   `UNRESOLVED` even in the original artifact;
3. the oracle-70 point mean is `+0.829` and clears the exact `<= +1` gate; `+8.002` is a
   post-selection confidence calculation, not the frozen gate and not a ceiling on all policies;
4. the 70-task prefix maximizes coverage, not safety. D91c permits 32 selected tasks, and the first
   32 sorted outcomes necessarily have mean no greater than the first 70; the safety/coverage
   frontier was not analyzed;
5. scalar-normal/correlated-ranking calculations are useful power diagnostics, not upper bounds on
   nonlinear multivariate learnability;
6. insufficient 16-map fold precision means a larger independent experiment is needed — the task's
   definition of `UNRESOLVED` — rather than structural impossibility;
7. the exact opponent-production decomposition remains unavailable;
8. the load-bearing selector/simulation analyzer and machine-readable outputs are not committed.

The owner has enough negative evidence to stop funding Route B. If so, record “not pursued due
negative prior and experiment cost.” Evidential `NOT_REPAIRABLE` still requires at least a frozen
U5 throttle study, or an explicit redefinition away from “structurally impossible.”

Complete review:
`chatgpt_1/d89a-verdict-restoration-review-2026-08-08.md`.

No bot, candidate, detector, panel, host run, value protocol, TestSession, submission, restore, or
Arena action was performed or authorized.
