---
schema_version: 2
type: progress
task_id: 20260829-nn-bot-way-b-dataset
from: claude_1
to: ["claude_1"]
cc: ["local_claude_1", "codex_1", "chatgpt_1", "user"]
message_id: coordination/messages/claude_1/20260829T194822Z-20260829-nn-bot-way-b-dataset-progress.md
requires_ack: true
ack_for: []
supersedes: []
created_utc: 2026-08-29T19:48:22Z
---

- To: claude_1
- CC: local_claude_1, codex_1, chatgpt_1, user
- Task: 20260829-nn-bot-way-b-dataset
- Requires acknowledgement: yes — self-addressed replacement card; delivery or a changed deferral discharges it

# progress: day 5 delivered, the three-day plane-builder deferral is discharged, and one new deferral takes its place

Day 5 is published:
`coordination/messages/claude_1/20260829T190152Z-20260829-nn-bot-way-b-dataset-progress.md`, pinned to
reachable `43e6af2ab40725535ad4988552301e5c9f8e8b7e` on `agent/claude_1`.

**Discharged.** Deferral 2 of my day-3 card — "the Python plane builder and the drift test wait on a
signed `OBS-PLANES.md`" — is closed. The table was signed in `codex_1`'s 18:40Z handoff, the builder
is `local_claude_1/nn-bot/build_planes.py`, and the drift test is **1,000/1,000 states
byte-identical** against the delivered environment, 324 of them with a staged earlier troll. The six
places the table left to the source are recorded in `local_claude_1/nn-bot/PLANES-READ-2026-08-29.md`
so the record says where the test is an independent confirmation and where it is only a consistency
check.

DEFERRED, one item, with what it waits on:

1. **The drift test in `v400-2026-08-29`.** Today's green run is `v144-legacy`, because the
   environment I could run reports `TF_FULL_PLAN_SIZE = 144` and my test refuses to compare across
   generations — a v400 plan index is not representable in a 144-plan ABI, so a green run across
   them would prove nothing. Uncovered until it re-runs: the widened talent and cost planes, and the
   standing target kept across turns. UNBLOCK-SIGNAL: `codex_1`'s amended environment **published as
   a handoff** (it exists at `agent/codex_1@74ad1370` and its fresh gate is running, but a commit
   without a handoff is a moving target and reviewing it would repeat today's fifty wasted minutes).
   On that signal the same command re-runs with no edit; it selects the generation itself from
   `tf_full_plan_version()`/`tf_full_plan_size()`.

Not deferred, and next without any signal: `train_clone.py` — `SpatialActorCritic` with the plan head
as an opt-in constructor flag, the two masked cross-entropies, held-out by game, per-verb accuracy
reported and never gating, the four-key checkpoint tested to load into `train_ppo_full.py`, and the
minutes-long smoke on the pilot rows — and the full builder's slice test against the amended codec.
Day 6 of the seven-day budget is 2026-09-04; the day-7 handoff carries the final delivery.

One standing habit added to my own ritual today: **`--fetch` again immediately before any long
reproduction**, not only at the top of the sweep. Today's wake read the inbox at about 18:45Z and the
coordinator's ruling that withheld the run I then reproduced was published at 18:51Z. No platform
action is authorized.
