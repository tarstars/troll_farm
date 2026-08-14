---
schema_version: 2
type: handoff
task_id: 20260731-dridriun-fruit-control-postmortem
from: claude_1
to: ["local_claude_1", "codex_1"]
cc: ["user"]
message_id: coordination/messages/claude_1/20260814T203210Z-20260731-dridriun-fruit-control-postmortem-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: 2eb8d23cd364e9eaf279b5a0f2dde08ab00c9790
artifact_paths: ["claude_1/reviews/b3-11-dridriun-corrected-narrow-rereview-2026-08-14.md"]
created_utc: 2026-08-14T20:32:10Z
---

- To: local_claude_1, codex_1
- CC: user
- Task: 20260731-dridriun-fruit-control-postmortem
- Requires acknowledgement: yes

# A-4 delivered: **CONCUR** — correction holds, conclusion stays measurement-only

## For the owner, in plain terms

This was a post-game review of one match against an opponent called Dridriun, asking whether the
enemy was stealing fruit from trees our bot planted. Four defects were found in the original
write-up, the author fixed them, and my job was to check the fixes.

**They hold.** In that game the opponent took **zero** of our apples. It *could* have — it had a
unit able to harvest, sitting about three turns away — but it never did. So the honest reading is
*"the chance existed and was not taken, once"*, which is very different from *"the opponent can't
do this"* or *"stopping it is worth something."*

The record itself is careful about that, and I checked that too: it explicitly forbids turning
this into a bot change, a target, or a threshold, and it states that one game cannot establish how
often this happens or what it is worth.

## Result

Artifact `2eb8d23c`; review at
`claude_1/reviews/b3-11-dridriun-corrected-narrow-rereview-2026-08-14.md`.
**Verdict: CONCUR.** Separation: author `local_codex_1` dormant, I have never touched this
postmortem; the earlier `chatgpt_1` re-review is `RECORDED / UNREPLICATED`, so this one reproduces
rather than relays.

| check | result |
|---|---|
| pinned hashes — compact JSON, human report | **both match on disk** |
| opponent harvested zero resident apples | **confirmed 3 ways**: `opponent_harvests=0`, `actual_opponent_capture=False`, `opponent_harvest_of_resident_apples_observed=False` |
| capture reachable | harvest-capable opponent unit at raw BFS/ETA `[3,2,3,3]` post-PLANT, `[3,3,3,3]` first-ripe |
| capture not realized | `actual_opponent_capture = False` |
| withdrawn "mixed 2/1" ETA label | no 1s in either ripe-cycle vector — reflected in data, not just announced |
| measurement-only | `source_or_policy_change`, `runner_or_panel`, `candidate_or_platform_action` all **False**; verdict is a *precheck* |
| supporting counts | harvest `83/83/0`, first-gen `25 = 25`, resident CHOP `84/82`, appendix `8+8+22 = 38` |

**The boundary worth quoting forward** is in the record itself:
`existing_broad_failed_interventions_may_not_be_repackaged = True`. A narrowed precheck must not
become a vehicle for re-proposing the broad interventions that already failed — Phase 21, D173a/b,
B3.7 and B3.10 stay closed.

## What I did not verify

The handoff states a direct trajectory reconstruction compares **all 38 rows field-exact** to the
compact. I verified the **row counts** (8 + 8 + 22 = 38) but not field-exactness against an
independent reconstruction — that is re-derivation and outside A-4's scope. **I neither assert nor
dispute it**, and flag it so my CONCUR is not read as having reproduced the appendix row by row.
Same treatment as the one unverifiable claim in A-3.

## Queue state

**A-3 and A-4 both delivered** (`78ac3a52`, this message). A-1 accepted, A-2 delivered and
independently verified, A-5 delivered and awaiting acceptance, **A-6 stays shut until A-5 is
accepted**. D89a-LI and the F1 action-target audit remain unclaimed and will stay that way.

No re-derivation, no measurement, no Arena action anywhere in A-3 or A-4.
