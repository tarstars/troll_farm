---
schema_version: 2
type: handoff
task_id: 20260904-start-game-optimizer-build
from: chatgpt_1
to: ["local_claude_1"]
cc: ["user", "claude_1", "chatgpt_2"]
message_id: coordination/messages/chatgpt_1/20260904T130226Z-20260904-start-game-optimizer-build-handoff.md
requires_ack: true
ack_for: ["coordination/messages/local_claude_1/20260904T123413Z-20260904-start-game-optimizer-build-handoff.md"]
supersedes: []
artifact_ref: agent/chatgpt_1
artifact_commit: 4c1cc68331e18ebb33b69cb4f769db228bac2ff3
artifact_paths: ["chatgpt_1/judgement/2026-09-04-what-next-after-optimizer-blocker.md", "coordination/status/chatgpt_1.md"]
created_utc: 2026-09-04T13:02:26Z
---

# HANDOFF — close the failed build; run one champion-prefix orchard experiment

The requested four-question judgement is complete at the artifact pin. No implementation, panel, holdout, ladder, platform, Arena or cluster action followed the judgement request.

## One next experiment

**Offline paired champion-prefix orchard-only oracle.** Run the unchanged champion through its own second `TRAIN`; disable all later training; then search a small near-shack orchard rotation with `NO_PLANT` legal and replay both candidate and continuously advanced champion to turn 300 under the same opponent scenarios.

Working rating prior: **about +2.5, wide range 0 to +4 and explicitly uncalibrated**. Falsify if the paired final-margin lower 95% bound is not above zero, own-score lower bound is negative, the no-plant champion is normally selected, the effect reverses under high raid, wood calibration fails, or the champion's second-troll talent/turn changes. Even a positive result below roughly +15 paired margin is probably too small for a ladder slot.

## Prelude finding

chatgpt_2's finding strengthens but does not replace my blocker diagnosis. The turn-35 fallback is the same architectural disease: an irreversible roster change is handed to a continuation validated for another roster. It does not explain every inactivity alarm in my smoke; planting execution still creates alarms on maps where the early second troll matches the resident. The fix belongs primarily in the optimizer before `TRAIN` or `PLANT`. A progress deadline around macros is a secondary safety belt and cannot undo a bad commitment.

The harness `stalled` flag is a relative long-inactivity alarm, not a crash, referee termination or automatic loss label. It remains a valid fail-closed mechanics condition.

## Repair disposition

**Close the current card and candidate. Preserve the design.** A new card is required because the registered 24/24 condition failed and the real repair is architectural, not threshold tuning:

- remove the custom second-troll prelude;
- keep the champion byte-identical through its own second troll;
- cache the baseline champion continuation;
- generate a small finite-forest plan frontier;
- exact-rerank that frontier against the shadow champion;
- disable third training in the first experiment;
- give every macro a measurable progress event and deadline.

This is credible offline. With four opponent archetypes and two seeds, eight retained plans imply roughly 64 candidate continuations plus cached baselines per map. Online feasibility is unproved and must not be inferred from the reduced planner's 378 ms benchmark.

## Measurement answer

The 2.19 rating range across five identical champion submissions is observed **one-read variability**, not an irreducible physical floor. One-hour single readings cannot settle most sub-2.2 changes. Under an optimistic independent-noise calculation using sd 0.82, about six readings per arm are needed for roughly one rating point of 95% half-width and about 21 per arm for half a point; drift can make this worse.

Exact paired simulation can resolve small score mechanisms but cannot convert them reliably to ladder rating. Therefore most micro-edits are not ladder-measurable under the current one-hour habit. Use paired replay and a sealed fresh holdout for screening; reserve an interleaved multi-read ladder block for a candidate whose plausible effect exceeds about 2.2 rating points.

## Owner-facing decision

**CLOSE the current build and charter the single offline champion-prefix orchard-only paired experiment.** Do not reopen the early-second or third-troll line.
