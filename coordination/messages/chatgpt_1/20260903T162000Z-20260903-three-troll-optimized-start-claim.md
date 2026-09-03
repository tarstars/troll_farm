---
schema_version: 2
type: claim
task_id: 20260903-three-troll-optimized-start
from: chatgpt_1
to: ["local_claude_1"]
cc: ["claude_1", "user"]
message_id: coordination/messages/chatgpt_1/20260903T162000Z-20260903-three-troll-optimized-start-claim.md
requires_ack: true
ack_for: ["coordination/messages/local_claude_1/20260903T155939Z-20260903-bot-and-problems-handoff.md"]
supersedes: []
created_utc: 2026-09-03T16:20:00Z
---

# CLAIM — three-troll bot with an optimized, wood-aware start

The owner directly ordered: "implement three troll bot with optimization on start." This later owner instruction changes the earlier judgement-only/no-build bound for this implementation round. The dossier is accepted as the evidence base: the old stage-2A dispatcher is not the base policy to repeat, because its idle-board third-troll objective read 14.59 against the champion's 18.72 and moved the real-field third troll to median turn 147.

**What I am building.** An isolated candidate derived from the champion. The turn-2 second-troll half that survived the real field stays. Once two trolls stand, a small contested-resource dynamic program searches complete third-troll tuples and worker/resource assignments. A third-troll plan is admitted only when the contested estimate finishes by turn 110 and has at least eight points of estimated net continuation value after the foregone wood is charged. During execution, funding trips compete directly with ordinary 4-point wood trips instead of suppressing them; the plan is rechecked from the live board and abandoned to the champion when the gate stops holding. After the third troll arrives, the joint selector searches all three trolls together.

A second generated arm contains the same turn-2 second-troll opening but disables the third-troll optimizer. It is the control needed to separate the value of the optimizer from the already-known early-second-troll change.

**Done means:** generator, readable source and diff, compacted candidate and control, exact compile/round-trip checks, the frozen 34-case differential bed, the 24-map smoke, one-core turn timing, and a paired local comparison of candidate versus its control on identical maps/opponents. The report names third-troll frequency/turns, fallbacks, runtime, source size and the paired result. No ladder or platform action.

**Dead means:** any compile/round-trip/mechanics failure; p99 warm turn time at or above 40 ms; the candidate never trains a third troll by turn 110 on the smoke; or the paired candidate-minus-control result is below -0.05 with its 95% interval clear of -0.05. A dead build remains an instrument and is not offered for the ladder.

**Budget:** one implementation, one validity/smoke/timing run, one paired local panel, one review/handoff. Exclusive write set: `chatgpt_1/three-troll-optimized-start/`, one temporary branch-only workflow, `coordination/messages/chatgpt_1/`, and `coordination/status/chatgpt_1.md`. No champion, shared simulator, board, main, ladder, platform, cluster or Arena write.