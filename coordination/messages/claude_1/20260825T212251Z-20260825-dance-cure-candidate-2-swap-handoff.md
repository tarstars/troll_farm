---
schema_version: 2
type: handoff
task_id: 20260825-dance-cure-candidate-2-swap
from: claude_1
to: ["codex_1", "local_claude_1"]
cc: ["user", "chatgpt_1"]
message_id: coordination/messages/claude_1/20260825T212251Z-20260825-dance-cure-candidate-2-swap-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: a84e764abb1d3506db3e23d214d6dba7226788ca
artifact_paths: ["claude_1/cure2/c8-report-2026-08-25.md", "claude_1/cure2/c8_positive_control.py", "claude_1/cure2/results/c8-positive-control-panel.json", "claude_1/cure2/results/c8-positive-control.json", "claude_1/cure2/results/c8-inert-control.json"]
created_utc: 2026-08-25T21:22:51Z
---

- To: codex_1, local_claude_1
- CC: user, chatgpt_1
- Task: 20260825-dance-cure-candidate-2-swap
- Requires acknowledgement: yes — C-8 is a control-set item and this is its result

# handoff — C-8 PASSES: the exchange ends **9** real dances with progress restored, and silences **4** more without restoring anything

C-7 showed the counters can count a bad swap. C-8 is the other direction, and the answer is
**PASS with a named cost**.

| | distinct cases, 240 games |
|---|---|
| dances **without** the rule (D-1 episodes on `arm-ruleoff.rs`) | **27**, in 25 games |
| of those, the exchange fires in-window with shared history | **13** |
| → detector silent **and** `progress_restored` | **9** |
| → detector silent, **progress not restored** | **4** |
| no exchange fires in the window | 14 (12 games granted none at all; 2 windows open after divergence) |

**Three of the nine passes are exactly a frozen library episode** — same unit, bounds, cells and
`k` (`m110:1`=OSC-001, `m059:1`=OSC-002, `m066:0`=OSC-027). Four of the nine are dances that
would otherwise have run to the **last turn of the game** (`k` up to 97).

## The cost, first, because one clause alone would have got this wrong

**4 of the 13 firing cases are detector-quiet-but-stalled**: `m070:1`(=OSC-005), `m078:1`,
`m090:1`, `m040:0`. The exchange silences D-1 and produces no progress inside the window. That is
the 08-09 20/20 failure mode; a single-clause grader would have reported 13 of 13 and been wrong
four times. `m090:1` is the sharpest — **three** exchanges in one eight-turn window, no progress
from any of them. A reported diagnostic (never part of any verdict) says three of the four units
progress *after* the window and the fourth's window ends at turn 200 so the question cannot be
asked. **I am not netting the four away with it and I ask that you do not either.**

## The route you may expect me to have taken is closed, and I measured that rather than asserting it

Pointing `fixture_harness.py` at the candidate arm returns **12/12 `NOT_REPRODUCIBLE_ON_BASE`,
0 graded**, on the twelve fixtures that grant an exchange (189 of 189 frozen lines differ on
OSC-002). The identity gate is right: the library's subject is the **resident**, the candidate is
another lineage, and a window is a property of the bot that produced it. So C-8 uses a window the
candidate's own lineage produces — the same bot with the rule switched off — and both clauses are
the harness's own: `fixture_harness.had_progress` **imported, not re-implemented**, and
`trace_detectors.detect_d1` for the dance.

## Four gates and three controls

- **G-D** divergence identity — the arms' first differing command turn (MSG stripped) must be
  **exactly** the first exchange turn, and the dance must open at or before it. Turns `1…d-1` are
  then literally shared history. The 2 cases that fail it are published with their reason and
  excluded from the claim, never dropped.
- **G-B** panel identity — **240/240** games reproduce their `panel-swap-census.json` exchange
  count; the corpus re-derives as **46 exchanges in 28 games**, the published figure.
- **G-R** duplicate agreement — all 34 fixtures are re-runs of panel games, so a `--panel` run
  plays each twice. **16 duplicated cases, 0 disagreements**, and the headline counts are
  deduplicated: 27 cases over **240** games, not 43 over 274.
- **G-E** wire honesty — every counted exchange turn carries an `S`/`X` unit.
- **N-1 inertness** — the identical pipeline with the rule-on arm replaced by the **rule-off arm**:
  **0 fires, 0 passes** on all 27 cases. **N-2 clause liveness** — `progress_restored` on the
  rule-off arm is False on **27 of 27** windows, so it is not a clause that cannot say no.
  **N-3** — the 3 frozen-episode matches above. The whole `--panel` run was executed twice and the
  JSON is byte-identical.

## Unchanged, and stated again so no table softens it

- The candidate's **C-5 = 5** repeats are not made benign by C-8. The pre-committed STOP AND ASK
  stands and is the owner's ruling.
- **P3 / orchard-safety on the candidate arm is UNMEASURED, not passed.**
- The rule does not end every dance: 12 of the 25 dancing games granted no exchange at all and
  every one of those dances persists.

Report `claude_1/cure2/c8-report-2026-08-25.md`, pinned at `agent/claude_1@a84e764a`. Next on my
card is **C-16** (the R-B red half). No Arena action taken and none proposed.
