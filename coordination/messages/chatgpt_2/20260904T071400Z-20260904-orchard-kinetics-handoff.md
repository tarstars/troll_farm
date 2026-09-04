---
schema_version: 2
type: handoff
task_id: 20260904-orchard-kinetics
from: chatgpt_2
to: ["claude_1"]
cc: ["local_claude_1", "user"]
message_id: coordination/messages/chatgpt_2/20260904T071400Z-20260904-orchard-kinetics-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/chatgpt_2
artifact_commit: e7da3d35a3d93b1d580840d8f52bffc77754a9ad
artifact_paths: ["chatgpt_2/orchard-kinetics/"]
created_utc: 2026-09-04T07:14:00Z
---

# HANDOFF — supplementary orchard action-space review

This is a narrow contribution to your live read, not a claim on the card and not a bot build. The owner’s amendment is correct: in my three-troll optimizer `PLANT` was outside the searched state graph. The artifact at the pin above traces the exact boundary and supplies a nine-test single-tree kinetics micro-instrument.

## Findings to carry into the read

1. **Do not add planting only to the dispatcher.** The forecast, admission test and emitted policy must share one mutable future-forest state. Otherwise execution creates wood that the value model still assumes cannot exist.
2. **Use one event-driven search for orchard and roster.** The original `chatgpt_1/opening-dp-oracle` is the right architectural base: asynchronous workers, delayed crops, a `PLANT` transition, dominance and exact-or-bounded certificates. My fixed-deficit `opening_assignment` is the wrong base because it assumes fixed sources and additive resource curves.
3. **Keep the units explicit.** A mature size-four tree yields up to four wood units, and each wood is four score points: gross standing potential is 16 points per mature tree, not four.
4. **Search all species.** For an untouched mature tree, health is banana 6, plum/lemon 12, apple 20, while every species yields four wood. Thus a chop-1 troll needs 6/12/20 chop turns respectively. Banana also does not consume a plum/lemon/apple training resource. Water-side apple matures fastest, so species must remain a frontier rather than a hard-coded orchard mix.
5. **Compare two optimized worlds:** best turn-300 value with `PLANT` and `TRAIN`, minus best turn-300 value with the same orchard action space but that `TRAIN` disabled, under identical opponent scenarios. Anything else confounds orchard value with troll value.
6. **The control must pass mechanics.** The prior no-optimizer arm’s 15/24 smoke result cannot support a value claim.

## Exact micro-instrument

`orchard_kinetics.py` mirrors the referee’s single-tree `PLANT`, end-turn growth and conservative one-tree `CHOP` rules. It reports water/inland growth milestones, mature health, fell turns, cohort standing score and a clearly labelled piecewise hazard approximation. `test_orchard_kinetics.py` passed 9 of 9 tests in-session.

The instrument deliberately excludes map movement, banking, ownership inference, opponent policy and simultaneous multi-chopper last-wood duplication. Those belong in the real-map event search and exact replay.

## Suggested next implementation after this no-build read

A fixed-roster real-map adapter for the existing DP oracle: exact empty planting cells near the shack, seed acquisition, planting, maintenance, felling and training in one action space; replay every selected schedule through the maintained engine; compare `PLANT` enabled versus disabled and against the champion’s realized 9.8-tree baseline. Only then add the roster frontier or online Rust budget.

No shared source, task card, board, champion, ladder, platform, cluster or Arena state was modified.
