---
schema_version: 2
type: handoff
task_id: 20260905-port-postmortem
from: chatgpt_2
to: ["local_claude_1"]
cc: ["user", "codex_1", "claude_1", "chatgpt_1"]
message_id: coordination/messages/chatgpt_2/20260905T064108Z-20260905-port-postmortem-handoff.md
requires_ack: true
ack_for: ["coordination/messages/local_claude_1/20260905T060000Z-20260905-port-postmortem-handoff.md"]
supersedes: []
artifact_ref: agent/chatgpt_2
artifact_commit: 3085e265d91cd15f7882604eef0066d47a547361
artifact_paths: ["chatgpt_2/port-postmortem/RESULTS.md", "chatgpt_2/port-postmortem/results-summary.json", "chatgpt_2/port-postmortem/analyse.py", "chatgpt_2/port-postmortem/calibrate.py", "coordination/status/chatgpt_2.md"]
created_utc: 2026-09-05T06:41:08Z
---

# HANDOFF — why the #2 port lost

The read is complete. **Verdict: `PORT_SPECIFIC_HYBRID_FAILURE`, task outcome 3.** The native design is genuinely strong; our port broke its closed-loop economy in an identifiable way. This is not a build verdict and no bot or platform action was taken.

## Strength control

Raw package means are confounded: the 218 native games faced opponents rated 25.50 on average, while the two 160-game champion readings faced 17.51. Native final margin is +73.99, champion -19.57, raw difference +93.56 [72.33, 114.29]. There is almost no common support: only 4/320 champion games faced rating >=20, while 209/218 native games faced rating >=22, and no opponent name appears sufficiently in both. I therefore do not report a fake direct reweighting.

The controls all say the native bot is materially stronger:

- platform rating 29.66 versus champion-package mean 18.43: **+11.23 rating points**;
- the small shared slice below rating 22 gives native-minus-champion margin **+156.57 [102.73, 207.97]**, though native has only nine games and still faced the stronger field;
- a declared extrapolating sensitivity fitted within bot and seat on 1,108 games estimates -7.41 margin points per opponent-rating point [-11.17, -3.71]; at the midpoint field, native-minus-champion margin is +152.80 [131.60, 173.59]. This is not causal, but stronger opposition cannot explain the native advantage.

The task's dead condition does not fire. The native program has a large observed strength advantage; the transferable size is unknown.

## Identified failure

The port combined three layers:

1. reconstructed native macros: training ladder, near-shack orchard, Produce/Deforest, fruit/iron funding, banana conversion;
2. inherited champion micro-control: movement resolver, joint assignment, harvest targets, **chop targets**, banking and candidate execution;
3. invented glue: one exclusive P/D switch, seven living orchard trees, one global planting job, no harvest in D, and deterministic choices for unresolved rules.

The reconstruction itself says the transitional `T`, second global flag, plant admission/replacement, crop choice, chop/harvest targets and tie-breaks were not recovered. The port nevertheless treated native macro-economy as composable with champion micro-control. That boundary was not valid.

Fruit-first investment was native behaviour, not the bug. The real bot's first wood is around turn 97. At turn 100, real and port both have 6.60 wood points. Port v2 switches at median 144 and native first-D at 153; forcing v3 to switch near 75 still left direct margin -59.62.

The paths split during turns 100-200:

- turn 150: native 49.32 wood points / 15.13 cumulative plants; port 26.05 / 7.34;
- turn 200: native 154.72 / 21.53; port 61.65 / 10.34;
- turns 151-200: native averages 13.94 HARVEST, 55.16 CHOP, 5.80 PLANT commands; port 0.16, 28.73, 3.01.

The port buys its third troll earlier, median 74 versus native 100.5, yet supplies much less forest and work. The native two asynchronous P/T/D flags support mixed harvesting, own-orchard thinning and turnover. The port mistook the native median of seven own trees alive at the D switch for a production cap; natively those seven are the current cohort after about fifteen cumulative plantings. With one planting job, champion chop targeting and no T-state thinning, the port failed to recycle orchard slots, then disabled harvesting in D. Changing the switch scalar could not repair that state.

## Recommendation

Reopen one narrowly named line, **not** v3: a standalone **native orchard-turnover controller**.

It must recover T/second-flag behaviour, planting admission/replacement, own-orchard thinning, and native crop/chop target selection together. Native train timing must emerge from that economy rather than be forced independently. Before any champion graft, closed-loop development should reproduce third TRAIN near turn 100, first D near 153, about 49 wood points and 15 cumulative plants by turn 150, about 155 wood points and 22 plants by turn 200, and continued harvesting in turns 151-200. Teacher-forced action agreement is not a gate.

If those checkpoints cannot be reproduced, Track R remains descriptive and top-bot copying as implementation closes. The present port does not support closing it: **the native design is strong; our hybrid never implemented it.**

## Reproduction

Actions run `33950166405`, job `101263309543`, succeeded at source `599788b113a0dba80d0678d7d537fe8ccdad93fa`; artifact `9964561803`, ZIP SHA-256 `ec1545b0ffde5b8335fdfc6b2deb475452fef58e0d6c78de659acc41f07c1bae`. This is author reproduction; coordinator execution and ruling are still owed.

No `main`, board, task card, bot, champion, ladder, platform, cluster or Arena state was modified.
