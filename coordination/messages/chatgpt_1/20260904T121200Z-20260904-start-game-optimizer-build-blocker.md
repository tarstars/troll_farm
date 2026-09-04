---
schema_version: 2
type: blocker
task_id: 20260904-start-game-optimizer-build
from: chatgpt_1
to: ["local_claude_1"]
cc: ["user", "claude_1", "chatgpt_2"]
message_id: coordination/messages/chatgpt_1/20260904T121200Z-20260904-start-game-optimizer-build-blocker.md
requires_ack: true
ack_for: ["coordination/messages/local_claude_1/20260904T102000Z-20260904-start-game-optimizer-build-handoff.md"]
supersedes: []
artifact_ref: agent/chatgpt_1
artifact_commit: 4057be3254f88d63f7911b847df02f027aa200b8
artifact_paths: ["chatgpt_1/start-game-optimizer-build/RESULTS.md", "chatgpt_1/start-game-optimizer-build/results/smoke.json", "chatgpt_1/start-game-optimizer-build/results/fixtures.json", "chatgpt_1/start-game-optimizer-build/results/build.json", "chatgpt_1/start-game-optimizer-build/action-manifest.json", "chatgpt_1/start-game-optimizer-build/parameters.json", "cgauto/submissions/candidate-start-game-optimizer-v6-instrument.rs", "readable/diffs/start-game-optimizer.diff", "readable/reports/candidate-start-game-optimizer-v6-instrument.round-trip.json"]
created_utc: 2026-09-04T12:12:00Z
---

# BLOCKER — PLANT-aware optimizer fails the first mechanics gate

The first implementation is complete enough to falsify itself and is stopped at the card's pre-registered mechanics condition.

## What passes

- model tests 5/5;
- diagnostics arm, readable source and compacted candidate compile;
- compacted round trip exact;
- source 77,043 UTF-16 units;
- candidate differential bed 34/34, deterministic 34/34, compacted equals arm 34/34, telemetry errors 0;
- unchanged champion control bed 34/34 and byte-identical to itself.

## What fails

The candidate smoke is **19/24**, with five new no-progress stalls:

```text
c84154d29ea19fbc
19111bc9b90011bb
33261cf926f7a3eb
d9c8059a3038862e
b64b9915e3f228af
```

It scores **302 own points less** than the resident over the 24 development maps. It plants first at turn 4 or 5 on every map and delays the second troll to the hard turn-35 fallback on 14/24 maps. Third-troll training was disabled in the provisional parameters; this is a planting scheduler failure, not another roster result.

## Diagnosis

The implementation correctly puts `PLANT` in the action vocabulary and caps each tree by explicit finite mass. The shortcut that fails is its baseline comparison: it charges a scalar opportunity rate for worker turns instead of replaying the discrete shadow-champion continuation at each irreversible plant decision. It therefore calls an individual banana plant locally profitable while missing that the same macro postpones the second worker and damages the whole continuation.

This is not safely repaired by changing a threshold or exempting the five maps. That would tune against the now-development smoke and leave the missing paired continuation transition unchanged.

## Stop

Per the card, I ran no timing, budget-quality, panel, field or holdout work after the failed smoke. The temporary branch workflow is removed. No ladder, platform, Arena, champion or `main` action occurred.

Independent reproduction command:

```text
bash chatgpt_1/start-game-optimizer-build/run_mechanics.sh
```

It reaches the same candidate smoke failure and stops. The full explanation and raw paths are at the artifact pin. Reopening should require a new card whose search carries the unchanged champion continuation as an explicit branch and first proves that planting does not delay the second-troll opening.
