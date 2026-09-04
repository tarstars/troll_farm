---
schema_version: 2
type: handoff
task_id: 20260904-start-game-optimizer-design
from: chatgpt_1
to: ["local_claude_1"]
cc: ["user", "claude_1", "chatgpt_2"]
message_id: coordination/messages/chatgpt_1/20260904T075826Z-20260904-start-game-optimizer-design-handoff.md
requires_ack: true
ack_for: ["coordination/messages/local_claude_1/20260904T072434Z-20260904-start-game-optimizer-design-handoff.md"]
supersedes: []
artifact_ref: agent/chatgpt_1
artifact_commit: cf3064e3fc81c0a75da40a8064063827792aa013
artifact_paths: ["chatgpt_1/start-game-optimizer/DESIGN-2026-09-04.md", "coordination/status/chatgpt_1.md"]
created_utc: 2026-09-04T07:58:26Z
---

# HANDOFF — proper start-game optimizer design complete

The one design round is complete at the artifact pin. No build, bot integration, platform, ladder, Arena, cluster or `main` action was taken.

## Design verdict

**ACCEPT FOR A FUTURE BUILD, CONDITIONAL ON THE ORCHARD-KINETICS NO-CODE GATE.** The proper optimizer is a final-value planner over a finite contested forest, with `PLANT` inside the searched action space and the unchanged champion as incumbent and control. It is not another faster way to buy a troll.

## Answers to the card's eight questions

1. **Objective:** paired final score-margin improvement at game end under a frozen champion continuation and fixed opponent scenarios. Own-score improvement is reported separately and guarded. Troll arrival, plant count and standing wood are diagnostics only.
2. **Action vocabulary:** target-level `MOVE`; searched `HARVEST`, `PICK`, `PLANT`, `DROP`, `CHOP`, `MINE`, `TRAIN` and event `WAIT`; joint assignment for every own troll. `PLANT` chooses species, cell, worker and timing. `NO_PLANT` and `NO_TRAIN` are always legal.
3. **Finite forest:** final wood is capped by the minimum of explicit surviving tree mass and relaxed worker travel/chop/carry capacity. Planting adds a tree only after paying the seed and worker turns and after its exact growth release; no `rate × turns remaining` forecast may invent trees.
4. **Opponent:** deterministic paired scenarios — clear-cutter, orchard builder, mixed strong opening and high-raid stress, at least two seeds each — calibrated to the measured raid and planting process. Idle is diagnostic only. Live observations invalidate and repair plans.
5. **Horizon and hand-back:** evaluate through turn 300; choose the opening horizon from `{80,100,120,150}` by a fixed value-saturation rule using orchard kinetics. Hand-back to a shadow champion is one way, at the horizon or earlier when no replay-valid plan clears a four-point advantage or repair times out.
6. **Compute:** initial internal stops are 850 ms on turn 1 and 35 ms on later planning events, with exact p99 gates. Use packed state, shared geometry, a preallocated arena and bounded Pareto labels. Future source must stay below 100,000 UTF-16 units; memory no more than 128 MiB with platform headroom.
7. **Build gates:** exact macro replay, action manifest, both arms independently clean, 24/24 development smoke, forecast error bounded, budget-quality curve, then a sealed fresh holdout revealed only after source and thresholds are frozen. Fresh-holdout value bar: paired mean margin at least +8 with its lower 95% bound above zero, own-score lower bound non-negative, and non-negative mean in three of four opponent archetypes.
8. **Falsification:** no build if orchard kinetics cannot make eight net points on 60% of development maps. Stop if the search normally returns no-plant champion, overstates wood by more than 1.5 times at the 90th percentile, misses the online/offline gap, fails mechanics/runtime, or fails the sealed holdout.

## Required input from the live orchard read

The design consumes, rather than duplicates, `20260904-orchard-kinetics`: species/water growth and wood-release curves; worker-turn costs for planting, maintenance, felling and banking; raid survival by time/distance; the champion's existing 9.8-tree value; the best orchard size/timing; and whether any extra-troll tuple becomes positive once that orchard is explicit.

The next project action is verification of this design. A build is a separate owner decision after the orchard read passes the no-code gate.
