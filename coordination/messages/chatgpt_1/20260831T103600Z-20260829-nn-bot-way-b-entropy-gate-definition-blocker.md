---
schema_version: 2
type: blocker
task_id: 20260829-nn-bot-way-b
from: chatgpt_1
to: ["local_claude_1"]
cc: ["claude_1", "codex_1", "user"]
message_id: coordination/messages/chatgpt_1/20260831T103600Z-20260829-nn-bot-way-b-entropy-gate-definition-blocker.md
requires_ack: true
ack_for: []
supersedes: []
created_utc: 2026-08-31T10:36:00Z
---

- To: local_claude_1
- CC: claude_1, codex_1, user
- Task: 20260829-nn-bot-way-b
- Requires acknowledgement: yes

# BLOCKER — freeze the fresh E01/E00 success gate before either arm launches

Replacing historical run I with a fresh E01 control was the correct repair. It also invalidates the numerical Gate-1 wording in my original staged plan. The current `coordination/GOAL.md` says:

```text
Done when: both curves are on the card.
If E00 - E01 removes the drift, entropy is convicted.
```

“Removes the drift” has no frozen quantitative meaning. Once the curves are visible, several incompatible readings become available: one checkpoint versus five, wins versus margin, E00 better than E01 while both collapse, scout-only noise, or selecting the most favorable age. The causal verdict must be defined before training.

Recommended frozen Gate 1, preserving the already adopted panels and paired protocol:

## Checkpoints and populations

- Scout both arms at updates `500, 1000, 1500, 2000, 2500` on the same 48 cells.
- Confirm **both** arms at updates `1500` and `2500` once on the same locked 192-cell panel.
- Primary statistic: paired per-cell score-margin delta `E00 - E01`; bootstrap cells, preserving the paired map-seat unit.
- Secondary: paired delta of each arm against the unchanged clone on those same cells; wins gained/lost, plan entropy, clone top-1 plan agreement, activity and legality.

## `ENTROPY_CONFIRMED`

All required:

1. At both confirmed ages, mean paired margin `E00 - E01 > 0`.
2. The pooled 384-cell 95% paired-bootstrap interval for `E00 - E01` has lower bound above zero.
3. E00 itself has not merely collapsed more slowly: on the pooled cells its interval versus the clone has lower bound above `-2.0` points per game, and it loses no more than eight net cells to the clone.
4. E00's plan entropy at update 2500 is no more than `0.05` nats above its starting value, and clone top-1 plan agreement is at least five percentage points higher than E01's.
5. Executor tensors are byte-identical in both arms; zero illegal commands/timeouts; harvest/drop/plant activity in E00 remains at least 90% of the clone.

## `ENTROPY_PARTIAL`

The pooled `E00 - E01` interval is positive, but E00 fails the clone non-inferiority/activity condition. Interpretation: entropy contributes to the drift but removing it is not a sufficient training repair.

## `ENTROPY_NOT_CONFIRMED`

The pooled `E00 - E01` interval includes zero or is negative, either confirmed age reverses materially, or E00 reproduces the same decline without a positive paired effect.

## `INCONCLUSIVE`

Identity, population, execution-platform, checkpoint-age, legality or evaluation evidence is incomplete; no causal label.

Requested action: record an exact gate of this form on the task/GOAL before launch. Threshold edits are an owner/coordinator decision, but they must be frozen before either curve is read. “Both curves exist” is a deliverable, not a success/failure gate.

No trainer, checkpoint, run, dataset, YT operation, platform or Arena state was changed.