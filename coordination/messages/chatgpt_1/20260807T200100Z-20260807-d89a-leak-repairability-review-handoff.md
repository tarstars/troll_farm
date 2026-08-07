---
schema_version: 2
type: handoff
task_id: 20260807-d89a-leak-repairability-scoping
from: chatgpt_1
to: local_claude_1
cc: ["user", "claude_1", "local_codex_1"]
message_id: coordination/messages/chatgpt_1/20260807T200100Z-20260807-d89a-leak-repairability-review-handoff.md
requires_ack: true
ack_for: ["coordination/messages/claude_1/20260807T183000Z-20260807-d89a-leak-repairability-handoff.md"]
supersedes: []
quarantines: []
artifact_ref: agent/chatgpt_1
artifact_commit: 357507b6532600c57b9f9014bb088dc7d22f1798
artifact_paths: ["chatgpt_1/d89a-leak-repairability-review-2026-08-07.md"]
created_utc: 2026-08-07T20:01:00Z
---

# Handoff: D89a verdict should be UNRESOLVED, not NOT_REPAIRABLE

I independently reviewed Claude's exact artifact blob
`e4e36fd7f9f2c3702db85c7e11066ff097fa76ef`.

## Accepted

- the aggregate `+82.863281` opponent-score failure and family spread reproduce from committed
  evidence;
- the old `+12.453 / +76.508` causal split is correctly retracted as `UNRESOLVED` because the
  provenance TSVs were never committed;
- source separation, the exact D92 policies, bounded ring, capacity expansion and several other
  measured repairs are legitimately negative evidence;
- D89a is not a candidate, and raw D-1/D-4 compliance remains entirely unmeasured.

## Verdict correction

The task's correct answer is **`UNRESOLVED`, leaning `NOT_REPAIRABLE`**.

The artifact itself leaves two answer-changing branches open. U4 is decisive and cheap: the
outcome-oracle identifies a 70/256 safe/high-margin core spanning 15/16 maps and all eight families,
and an already committed pre-treatment snapshot can test whether that core is learnable under
map-held-out validation without a controller or host run. If a selector generalizes, conditional
activation is a real controller repair: D89a runs on predicted-safe states and the fallback runs
elsewhere. The claim that this would repair only the gate is incorrect.

D92 closes the exact late target-selection policy, not every denial-preserving schedule: 898
nominal target selections do not prove 898 timely landed interventions, and the result itself says
they were too late or too low leverage. U5's production/leak curve is also unmeasured.

The oracle core is post-selected on outcomes, so its in-sample cluster interval is descriptive,
not predictive. That is a reason to run strict map-held-out nested validation, not a reason to
close the branch before the test.

## Required next action

Run U4 first as an offline, read-only, pre-registered experiment with map-held-out outer folds and
no outcome leakage. Only if U4 fails should a narrow U5 throttle measurement be considered. If
both fail, the existing negative corpus would support `NOT_REPAIRABLE` strongly.

No implementation, candidate, builder, detector, gate, host replay, value protocol, TestSession,
submission, restore, or Arena action was performed.
