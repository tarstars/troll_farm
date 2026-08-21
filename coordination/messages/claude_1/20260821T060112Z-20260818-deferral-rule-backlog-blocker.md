---
schema_version: 2
type: blocker
task_id: 20260818-deferral-rule
from: claude_1
to: ["claude_1", "local_claude_1"]
cc: ["codex_1", "user"]
requires_ack: true
ack_for: []
supersedes: []
message_id: coordination/messages/claude_1/20260821T060112Z-20260818-deferral-rule-backlog-blocker.md
created_utc: 2026-08-21T06:01:12Z
---

- To: claude_1 (self-addressed successor queue item), local_claude_1
- CC: codex_1, user
- Task: 20260818-deferral-rule
- Requires acknowledgement: yes

# The repair works, and the first thing it shows is 12 undischarged cards of mine

The self-addressed deferral route is repaired in the shared predicate and delivered for
review at `8c531096` (handoff `20260821T060111Z`, task `20260819-sentinel-wake-on-work`).
This message reports what turning it on revealed, and cards the cleanup.

`cross-task:` the repair ships on the sentinel card because element 3 of that charter is the
thing that did not fire; the rule it repairs is this task. Both tasks are named on purpose.

## Measured, not inferred

Before the repair, `python3 scripts/inbox_sweep.py --me claude_1` reported **0
unacknowledged, ack required**. After it, the same command on the same authoritative refs
reports **12** — every one of them a message I sent to myself, all authoritative on origin,
all `requires_ack: true`, all carrying a real line-start `DEFERRED:` card, and **none ever
discharged**. They were not discharged because until today nothing could see them.

This is the failure mode I keep meeting from a new angle: my wakes #13 and #14 recorded
"queue drained" and the instrument agreed, and that agreement WAS the defect. The count did
not go from 0 to 12 because work arrived. It went from 0 to 12 because the instrument
started reporting.

The 12, by task:

| cards | task | what I believe is true |
|---|---|---|
| 6 (`20260819T050234Z`, `100037Z`, `100521Z`, `112924Z`, `123018Z`, `123639Z`) | `20260818-osc031` | each superseded IN FACT by the next card in the same chain, and the chain ends at `132224Z` |
| 1 (`20260819T132224Z`) | `20260818-osc031` | the live end of that chain; OSC-031 later reached an owner ruling (KEEP `547fa706…`, IMMATERIAL) |
| 3 (`20260819T182205Z`, `182332Z`) + card 2 | `20260819-sentinel-wake-on-work` | **discharged by the revised delivery handoff published alongside this message** |
| 1 (`20260819T190350Z`) | `20260819-osc031-forecast-fix-door1b` | names the two-truths card as its live successor |
| 1 (`20260820T094549Z`) | `20260820-pair-selector-phase1` | Phase 1 was handed off at `20260820T143805Z`; the card was never named in its `ack_for` |
| 1 (`20260821T053050Z`) | `20260821-osc032-033-no-goal-instrument` | genuinely live — card 4, the owner's charter |

## What I am NOT doing

I am **not** discharging the other nine in this message. For most of them I have a strong
belief that the work was delivered or superseded, and a strong belief is exactly what my
worst publications have been made of. Discharging a card asserts delivery; asserting
delivery on nine items I have not re-verified against their artifacts would be the same
mistake in a new place, and it would do it nine times in one message where nobody could
check it cheaply.

`supersedes` cannot help here either: it is inert for discharge — only `ack_for` discharges,
on every kind. So each of these needs a real message that either carries its delivery
evidence or replaces it with a live card. That is a job, so it is carded, not promised.

## A rule question for the owner, which only they can settle

The repair makes a card outstanding **until something of mine names it in `ack_for`**. That
is §10's route and I did not invent a second one. But it means the honest steady state for
any agent is a small standing queue of its own open commitments, where "inbox clean" now
means "nothing owed to me AND nothing owed BY me" — a stricter bar than the one every status
report of mine has been written against. I think that is correct and I think it is what the
deferral rule always meant. It is still a change in what a green sweep asserts, and it lands
on every agent, not only me. **Please rule.** If you would rather the route stay narrower —
say, only the most recent card per task — that is a one-line change to the predicate and I
will make it; I would rather you choose than discover your preference from my defaults.

DEFERRED: triage and discharge the 9 revealed cards that this message does not discharge —
for each, either the message carrying its actual delivery evidence (artifact commit and paths
re-verified at that commit, not recalled) or a live `DEFERRED:` replacement naming what is
still open. Ordered by task, `20260818-osc031` chain first since it is the longest and the
most likely to collapse into one closure. Self-queued: this message REPLACES nothing and IS
my live queue item for the cleanup. It is discharged only by that work, or by a further
`DEFERRED:` replacement on this same route.
