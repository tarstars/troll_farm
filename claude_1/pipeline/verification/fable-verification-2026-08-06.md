# Fable independent verification of gate repairs #1 and #2

Every number below re-run by me from the committed tools, not taken from the
implementing subagents. Panel: `claude_1/pipeline/fuzz_panel.py`, 240 games
(6 seeds x 120 maps... per committed config), parent
`a8eb3b2b…` = cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs.

## Blocking counts (of 240)

| run | raw, uncalibrated (repair #1) | raw + P4 terminal calibration (repair #2) |
|---|---|---|
| **parent vs itself (FLOOR)** | 223 | **118** |
| chatgpt_1 `bbe54a48` | 217 | **116** |
| chatgpt_1 tip `7ad9d784` | 221 | **146** |

## Why repair #1 alone was unusable

Under the uncalibrated raw gate the shipped, arena-rated parent failed 223/240
(93%) and **both candidates scored better than the parent** — the gate ranked a
known regression as superior to its own reference implementation, i.e. it carried
no information. Cause: P4 counted the post-completion coast to the sim horizon as
a liveness stall — **198 of 204 stall windows ended at turn 199**.

## After repair #2 the gate ranks correctly

The tip `7ad9d784` now scores clearly WORSE than the parent (146 vs 118),
independently reproducing the conclusion of my packet review that the tip induced
regressions. `bbe54a48` sits at the floor (116 vs 118) — it neither fixes nor
breaks what the panel measures.

## Remaining calibration defect: D-9 is candidate-invariant

Per-detector breakdown of the three calibrated runs:

| run | D-9 | D-1 | P4 |
|---|---|---|---|
| floor (parent vs itself) | **74** | 32 | 30 |
| bbe54a48 | **74** | 27 | 25 |
| 7ad9d784 | **74** | 0 | 79 |

**D-9 fires exactly 74 times in every run regardless of which bot is under test.**
In a parent-vs-parent run D-9's paired clauses (train_late / train_missing /
stats-differ) cannot fire by construction, so all 74 come from the UNPAIRED
clause: "any PLANT/PICK BANANA before TRAIN while |own units| == 1"
(trace_detectors.py:1189-1203). The shipped parent does its own pre-TRAIN banana
funding — so the clause's proxy assumption (banana-before-TRAIN implies the TRAIN
was displaced) is false on this lineage.

Consequence: D-9 contributes a constant 74-game offset to every candidate's score
and **can never discriminate** — it is 63% of the remaining floor and pure noise
in the acceptance decision. Proposed absolute fix (no parent reference, consistent
with the raw ruling): fire only when TRAIN was actually AFFORDABLE at that turn
and the bot spent on banana instead. This modifies `trace_detectors.py`, a SHARED
acceptance artifact the integrator runs as a host gate — owner/integrator scope,
not changed unilaterally. Referred, not applied.
