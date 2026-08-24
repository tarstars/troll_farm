---
schema_version: 2
type: handoff
task_id: 20260824-real-game-dance-attribution
from: claude_1
to: ["codex_1"]
cc: ["local_claude_1", "local_codex_1", "user"]
message_id: coordination/messages/claude_1/20260824T175000Z-20260824-real-game-dance-attribution-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: d75cb2f0b9fbb9dd9dd6f43d872a6e00d099abda
artifact_paths: ["claude_1/dance1/g2-execution-2026-08-24.md", "claude_1/dance1/owner-brief-2026-08-24.md", "claude_1/dance1/dance_facts.py", "claude_1/dance1/dance_controls.py", "claude_1/dance1/run_dance_panel.py", "claude_1/dance1/narrate3_decode.py", "claude_1/dance1/results/dance-panel-2026-08-24.json", "claude_1/dance1/results/dance-facts-instrument-2026-08-24.json", "claude_1/dance1/results/dance-facts-champion-2026-08-24.json", "claude_1/dance1/results/determinism-2026-08-24.json"]
created_utc: 2026-08-24T17:50:00Z
---

# handoff — G-2 execution: 462 episodes graded on both passes, six controls fired, class 3 lost its causal name

Artifact commit `d75cb2f0b9fbb9dd9dd6f43d872a6e00d099abda` on `agent/claude_1`, ten paths, all
declared above and all present at that commit. Report: `claude_1/dance1/g2-execution-2026-08-24.md`.
Owner brief: `claude_1/dance1/owner-brief-2026-08-24.md`. The fact table is published **whole** —
80 instrument rows and 382 champion rows with every peer record, every per-turn telemetry sequence
and every swap tick — so every count below is re-derivable from the JSON without running anything.

**The caution travels with every number: D-1 off replays is an upper bound.**

## What was graded

469 instrument games (149 v2 / 160 v2 / 160 v3) → 80 D-1 episodes. 306 champion games → 382
episodes. All four package digests verified against their shipping manifests. The champion episode
list of record was reproduced **exactly**: 382 matched on `(game, unit, turn_start, turn_end)`, 0
only here, 0 only in the record.

## The controls, each with the number it fired on

| control | number | result |
|---|---|---|
| K0 progress() agreement (added; self-check) | 462 in-window transitions | 0 disagreements |
| K1 batch-1 identity | 22 / 17 / 0 / 0 | exact |
| K2 mechanism reproduction | 38 episodes, 30 frozen situations | 0 mismatches |
| K3 swap-tick detector | positive 9/9; negative 3,256 ticks / 141 pairs | remedy applied |
| K4 telemetry decode | 469 games | 0 refused |
| K5 exhaustiveness | 4 batches | identity holds in all four |
| determinism | full re-run, separate out-dir | all three files byte-identical |

## The three things to attack first

1. **K3's negative side failed and I applied the pre-committed remedy rather than footnoting it.**
   The F5 predicate fires 3,256 times in 132 of 141 pre-cure game x seat pairs that R-1's premise
   said would be silent. Class 3 is `POSITIONAL_EXCHANGE` everywhere, and the name was resolved
   **before grading**, from a corpus containing none of the graded episodes. I publish one NEW
   diagnostic and refuse to read it: 1,597 of the 3,256 ticks (49 %) have both units commanding a
   `MOVE` onto each other's cell. That is consistent with "the predicate is too broad" and with
   "the ledger's premise about the old resident is wrong", and I do not pick.
2. **Three classes are EMPTY and one of them is the interesting one.** `BLOCKED_BY_IDLE_TEAMMATE`
   is **0 of 80** on the instrument pass — the library's dominant `M2` shape (14 of its 38
   episodes) does not occur in 469 real games. The real-game blocker is *working*: wait fraction
   0.00 in 33 of 34, standing on a plant in 24 of 34. `NO_TARGET` is 0 of 80 and `GOAL_FLIP` is 0
   of 80. **The empty classes are where I would look for a boundary that flatters the result**, and
   the fact rows are published so you can test whether a different boundary would have filled them.
3. **`UNCLASSIFIED` is 21 of 80 and I describe it rather than hide it.** Every one is the same
   shape: no blocker plus F4 `MIXED`. 30 of the 36 `MIXED` windows contain no `NONE` turn at all
   and 31 carry two or more distinct real targets, so the honest description is "the stated want
   changed during the window, without the clean period-2-to-4 alternation `GOAL_FLIP` requires" —
   not "we could not tell". If you think that shape deserved a class, say so; I did not invent one
   after seeing the count.

## Two deviations from what you accepted, named rather than left to be found

- **The v3 grammar is imported, not lifted-and-proved.** `narrate3_decode.py` imports
  `run_gp3_parity.decode` under an asserted source SHA-256 (`0537741d…f293bf`) and contains no copy.
- **K0 was added**, a self-check that the `progress()` re-statement F7 needs agrees with the
  detector's own closure. It replaces no defined control.

## Required tables, all produced

swap x blocker cross-tab (11 of 80 instrument episodes contain a dancer swap tick, only 3 carry
class 3 — r1's ordering would have given 11 and 26); class x window length with the blocker's
`distinct_cells_to_game_end` beside it (at k = 3 not one blocker stays put; at k > 3, 10 of 23 never
move again); late-peer sensitivity (**0 rows**, F3b empty throughout); blocker liveness (**0 rows**
— the inherited dead-peer artefact never fired); mech split of every no-blocker class.

## Scope

No bug ruling, no cure, no candidate, no behaviour change, no prevalence claim beyond the four
corpora graded, no origin claim for the dance, no statement about any opponent's reasons. No Arena
action, submission, TestSession, fetch, sealed-data access or resident mutation; resident SHA-256
unchanged.

Requested ruling: `EXECUTION_ACCEPTED` or `REVISION_REQUIRED`, one wake, from a fresh archive of
`d75cb2f0`. Please publish it `requires_ack: true` toward claude_1 — a receipt that authorizes
nothing does not wake me.

Deferrals: none.
