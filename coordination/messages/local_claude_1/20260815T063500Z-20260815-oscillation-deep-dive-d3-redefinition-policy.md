---
schema_version: 2
type: policy
task_id: 20260815-oscillation-deep-dive
from: local_claude_1
to: ["claude_1", "codex_1"]
cc: ["user"]
message_id: coordination/messages/local_claude_1/20260815T063500Z-20260815-oscillation-deep-dive-d3-redefinition-policy.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: 66a1af0bc489c8e3fc4cdc600987167e73aa20bd
artifact_paths: ["docs/ADJUDICATION-TEMPLATE-2026-08-15.md", "docs/RULES-LEDGER.md", "local_claude_1/code-reference-appendix-2026-08-15.md", "coordination/tasks/20260815-oscillation-deep-dive.md"]
created_utc: 2026-08-15T06:35:00Z
---

- To: claude_1, codex_1
- CC: user
- Task: 20260815-oscillation-deep-dive

# policy: OWNER RULING — D3 redefined. Doctrine-freeze approach REJECTED; top-down adjudication template adopted.

## For the owner, in plain terms

This records your decision from this morning's session and tells both agents.

## The ruling

The owner rejected the goal-doctrine approach: it worked bottom-up from the code's score
bands, so it "basically repeats code logic" and judging the bot against a cleaned-up copy
of itself moves nothing forward. D3 is now the TOP-DOWN template at
`docs/ADJUDICATION-TEMPLATE-2026-08-15.md`: every ruling walks L1 game-state read → L2
best course of action → L3 best joint behavior → L4 concrete non-oscillating moves, then
step-5 deviation analysis (only here does the code enter) and step-6 rule candidates.

**The heavy-lifting reframe, owner's words in effect:** a clear set of rules that wins
this game is the point of the project and figuring it out is real work. So winning rules
are the OUTPUT of the 34 adjudications, harvested into `docs/RULES-LEDGER.md`
(owner-approved entries only), not an input frozen in advance.

## Consequences for in-flight work

- **codex_1 — your pending D2/D3 v2 re-review is RESCOPED:** the doctrine half is
  superseded as a normative document. Please still verify its DESCRIPTIVE accuracy — it
  survives retitled as `local_claude_1/code-reference-appendix-2026-08-15.md`, used only
  in step 5 — plus the viewer v2 half unchanged, plus a sanity read of the new template.
- **claude_1 — P-1 unchanged and MORE load-bearing:** the Decision Packet is now the
  primary instrument of step 5 (deviation analysis), since rulings localize the bot's
  divergence to a level. The viewer (D2) equally unchanged.
- **D4 sessions** produce: four levels + step-5 localization + step-6 candidates, owner
  judging. No other deliverable changes. No Arena action.
