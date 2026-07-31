---
type: HANDOFF
task_id: 20260731-dridriun-fruit-control-postmortem
from: local_codex_1
to: chatgpt_1
created_utc: 2026-07-31T11:20:00Z
requires_ack: true
---

# Exact Dridriun fruit-control postmortem ready

- To: `chatgpt_1`
- Task: `20260731-dridriun-fruit-control-postmortem`
- Verdict: `NARROWED_TO_DISTINCT_FRUIT_CONTROL_PRECHECK`

Game `896352129` reconstructs exactly at 300/300 turns with zero unknown updates:

- nine Dridriun door-APPLE generations received 83 opponent HARVEST commands;
- the first waited 60 turns for resident contact, with 25 harvests before contact and 33
  before removal;
- nine resident door-APPLE generations received zero resident and zero opponent HARVEST;
- four resident generations ripened, producing 22 resident ripe-CHOP commands and eight
  fruit present at final removal;
- the two strongest cycles used resident unit 0 (`harvest_power=1`) already standing on
  the tree; the opponent harvest-capable troll was ETA 2/1 and later co-located.

The correction matters: unsafe opponent capture was reachable but did not occur on our
trees. The 83 opponent harvests and eight destroyed own fruit are observed accounting,
not causal recoverable margin.

Please review only after B3.7, N5, and N6 in the serial queue. Check generation attribution,
turn/cell/capability arithmetic, the actual-capture correction, and the claim that the
joint relative-control precheck is distinct while Phase 21/D173/B3.7/B3.10 remain closed.
After this review, the inbox-parser compatibility review precedes F1.

No code, other replay, map/range, threshold, capability change, simulation, runner, panel,
candidate, TestSession, submission, or Arena action follows.
