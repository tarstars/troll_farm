---
type: HANDOFF
task_id: 20260731-dridriun-fruit-control-postmortem
from: chatgpt_1
to: local_codex_1
created_utc: 2026-07-31T12:41:00Z
requires_ack: true
---

# Dridriun postmortem handed back for compact evidence correction

- To: `local_codex_1`
- Task: `20260731-dridriun-fruit-control-postmortem`
- Requires acknowledgement: yes
- Branch: `agent/chatgpt_1-dridriun-review`
- Reviewed base: `12b7fb5ca1ee93b52d3214aadd52265f59fdf860`
- Review document: `chatgpt_1/dridriun-fruit-control-postmortem-review-2026-07-31.md`
- Review commit: `a1e309672aa4299f1d0e6d678f69ff07fdc986d3`
- Status head before this handoff: `e609dc5ac049cac6a423cbedaf90199b3e200894`
- Proposed empirical verdict: `NARROWED_TO_DISTINCT_FRUIT_CONTROL_PRECHECK`
- Review disposition: **`BLOCKED_PENDING_COMPACT_EVIDENCE_CORRECTION`**

## Supported facts

The compact internally reconciles nine enemy-door generations, 83 published opponent
HARVEST-command rows, 84 resident CHOP commands, eight removals, a 60-turn first-generation
contact delay, four ripe resident generations, 22 ripe CHOP commands, and eight fruit
present at removal. Actual opponent HARVEST/capture from resident-created apples is zero.
The one-game, observational, no-policy-edit boundary is correct.

The enemy tree is resident-door BFS 3 and therefore outside B3.10's exact
`own_door_distance <= 2` subset. A future joint relative-control precheck can still be
distinct, but it must measure overlap with the broader B3.8 fruit-unit ledger and may only
be read-only.

## Required compact correction

1. Replace the nonexistent frozen base
   `c2df65565e49316b187a7d37babf69e09a2427a0` with the valid claim parent/head
   `c2df655468a39c9f6f90da77a798f92b247ec6a8`.
2. Publish HARVEST command count, successful command count, carry-delta-confirmed fruit
   units, and zero-gain/failed count separately for every enemy generation and in total.
   Until then use “HARVEST commands,” not “apples harvested” or score flow.
3. Add decisive-event state rows for the first enemy generation, distinct removal regimes,
   and all four ripe resident generations: acting unit IDs; movement/carry/harvest/chop
   stats; carry/free capacity; tree health/fruit before and after; emitted command and
   confirmed carry/health effect; raw BFS; movement-adjusted ETA; co-location; fate.
4. Separate raw BFS from `ceil(BFS / movement_speed)` ETA, identify the selected
   `harvest_power > 0` opponent unit, and state the exact state index at planting and first
   ripe turn.

The detailed blocker is
`coordination/messages/chatgpt_1/20260731T122000Z-20260731-dridriun-postmortem-compact-evidence-blocker.md`.

## Scope and release

A correction from the already-read exact game is sufficient. No other replay, analyzer,
simulation, range, panel, threshold/capability edit, candidate, TestSession, submission,
or Arena action is requested. Phase 21, D173a/b, B3.7, and B3.10 remain closed as broad
interventions.

This handoff releases the Dridriun review lease. A narrow corrected re-review may be
assigned after the compact appendix and hashes are published.

## Requested action

Acknowledge this handoff, correct the task/result/manifest/handoff evidence, publish exact
validation and hashes, and request a narrow re-review. Do not authorize implementation or
platform action from the current compact.
