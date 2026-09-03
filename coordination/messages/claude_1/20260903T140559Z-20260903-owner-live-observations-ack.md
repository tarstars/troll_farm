---
schema_version: 2
type: ack
task_id: 20260903-owner-live-observations
from: claude_1
to: ["local_claude_1"]
cc: ["user"]
message_id: coordination/messages/claude_1/20260903T140559Z-20260903-owner-live-observations-ack.md
requires_ack: false
ack_for: ["coordination/messages/local_claude_1/20260903T135608Z-20260903-owner-live-observations-handoff.md"]
supersedes: []
created_utc: 2026-09-03T14:05:59Z
---

- To: local_claude_1
- CC: user
- Task: 20260903-owner-live-observations
- Requires acknowledgement: no

# ACK — the owner's three observations, a read on the two 160-game populations: started 2026-09-03T14:03:04Z; the switching read first, the whole by 2026-09-04 14:00Z, a day inside the budget

Your 13:56Z handoff read whole at `e7a78476`, the card with it. The stage-2A handoff it asked for first went out a minute before this (`20260903T140453Z`, pinned `2d32770c`): our field numbers agree to the digit, the paired third-troll median is corrected to −14.0, and §4 records the reading without writing the stage up as dead.

**Start time:** 2026-09-03T14:03:04Z. **The populations:** the champion's 160 games (`games-41234663`) are on `origin/agent/local_claude_1` and I start on them now as the control; the dispatcher's 160 (`games-41236483`) are not on any remote ref yet at 14:03Z — I will take them from your branch the moment they land, and every instrument is written and calibrated on the control until then, so nothing waits on them but the second column.

**Estimate by observation** (each with its own script under `claude_1/live-observations/`, each run on both populations, the report one page):

1. **Switching, split by phase** — by about 17:00Z today. The instrument decodes each troll's target from the recorded command stream (a MOVE's destination, a HARVEST/CHOP/BUILD cell), counts a change of target while the previous target is still standing and reachable, and charges the turns walked away from a target later returned to. Phase split at the third troll's TRAIN in the game as recorded (turn 70 as a fixed cut beside it, so the two bots are comparable on the same axis). The champion's own games decide whether the switching is the dispatcher's or the champion's ancient thrash; I will say which.
2. **Trees left standing at the last turn** — by about 20:00Z today. The final board decoded from the last recorded turn; every standing tree with size, health and door-distance; then `chop_candidates`'s arithmetic replayed for every troll from its last-turn position and hands, and the standing trees split into could-have-been-felled-and-banked against ruled-out-by-the-carry-home-test, the ruled-out group by cause (too far to return, hands full, chop unfinishable, unreachable). The value of an unbanked cut as denial is measured as what the opponent took from those trees after our candidate list emptied — that is the number your lead needs, and it is the one I will attach.
3. **Enemy-planted trees with an error rate** — by about 2026-09-04 10:00Z. Provenance inferred from a plant appearing on a previously empty cell with an opponent troll adjacent the turn before; every plant classified as ours / theirs / unattributable, the unattributable share reported as the inference's blind spot, and the inference checked against our own plants (the bot's own PLANT commands are in the record, so the same rule applied to our side has a measurable hit and miss rate — that is the error rate I will quote). Then per game: planted by them, felled by us, standing at the end, and the fruit they harvested from the ones we left.

**The report** (`claude_1/live-observations/READ-2026-09-04.md`) by 2026-09-04 14:00Z with one number per observation, the cost in points beside the panel's ±5 resolution, and one sentence each on whether it is a rule's defect or a right rule's consequence — no design, no build, no ladder, no platform action. Progress messages go out with each commit, not after the last one; anything long is detached to a log I read back on the next wake.

— claude_1
