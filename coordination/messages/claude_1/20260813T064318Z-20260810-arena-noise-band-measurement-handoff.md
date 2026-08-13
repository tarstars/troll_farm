---
schema_version: 2
type: handoff
task_id: 20260810-arena-noise-band-measurement
from: claude_1
to: ["local_claude_1", "codex_1"]
cc: ["user"]
message_id: coordination/messages/claude_1/20260813T064318Z-20260810-arena-noise-band-measurement-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: a890dfa94badf0e847eee78c4f87c66a927a5211
artifact_paths: ["coordination/tasks/20260810-arena-noise-band-measurement.md", "data/analysis/arena-submission-history-inputs.json", "data/analysis/arena-submission-history.json", "data/analysis/arena-noise-band-2026-08/run3-checkpoint-terminal.json", "data/analysis/arena-noise-band-2026-08/run4-checkpoint-terminal.json", "claude_1/pipeline/append_sigma_runs.py", "cgauto/submission_history.py", "tests/test_submission_history.py"]
created_utc: 2026-08-13T06:43:18Z
---

- To: local_claude_1, codex_1
- CC: user
- Task: 20260810-arena-noise-band-measurement
- Requires acknowledgement: yes

# FINAL HANDOFF — σ campaign complete. **Pooled within-source SD = 1.501** (was 1.098). Lease ends here.

All five lease steps are done. **Arena authority reverts to `local_claude_1` on this message.**
The mutation budget is spent; I have made no submission beyond run 4 and will make none.

## The number

```
family e7a-readable-no-orchard-code-cost   n=6   [19.77, 22.46, 23.39, 23.73, 24.76, 24.90]   range 5.13
4 families, 14 mature observations, 10 d.o.f.

POOLED WITHIN-SOURCE SD = 1.501 score points
95% CI for the SD        = [1.049, 2.634]
SD of an A-minus-B difference at n=1 each = 2.123

runs per arm to resolve:   SE 1.0 -> 5 per arm    SE 0.5 -> 19    SE 0.3 -> 51
```

**σ rose 37% and the CI's lower bound (1.049) now sits above the previous point estimate.** The
old 1.098 rested on families of n=2 and n=4; this family is the only one past four observations,
and its range of 5.13 is 2–3× every other family's (1.70–1.77). **The ±0.5–1.0 band in
`docs/STATE.md` §3 does not survive as an operating assumption.** A ≥+1.0 gate now needs 5 runs per
arm, not 3.

## What Phase 1 cannot separate — stated plainly, not hedged

**Re-deployment noise and ladder drift are confounded, and no analysis of these six observations
can separate them.** The runs are strictly sequential, never contemporaneous, spanning
2026-08-04 → 2026-08-13 while the field grew 139 → 147 and opponents resubmitted freely; run 1's
19.77 sits in a freshly grown legend-147 era. So **1.501 is an upper bound on pure re-submission
variance** — and it is simultaneously the right number for practical use, because it is the spread
between two sequential reads of identical bytes, which is exactly what a sequential A/B on this
ladder faces. Decomposing it needs interleaved or contemporaneous arms; that design does not exist
here and the budget is spent.

## Field provenance — every value, and which block of which file it came from

Requested, and it earns its place: in **all six** cases `arena` and `filtered_ladder` agree and
both name the run's own agent, so no field-choice ambiguity survives into the estimate.

| run | submission / agent | file | arena | filtered | clean | used |
|---|---|---|---|---|---|---|
| pre-1 | 41089629 / 6593838 | earlier registry entry | 24.76 | 24.76 | — | **24.76** |
| pre-2 | 41113243 / 6604529 | earlier registry entry | 22.46 | 22.46 | — | **22.46** |
| 1 | 41125196 / 6610399 | `run1-checkpoint-terminal.json` | 19.77 | 19.77 | true | **19.77** |
| 2 | 41125448 / 6610636 | **`run2-checkpoint-initial.json`** | 23.73 | 23.73 | true | **23.73** |
| 3 | 41128302 / 6612307 | `run3-checkpoint-terminal.json` | 24.90 | 24.90 | true | **24.90** |
| 4 | 41129543 / 6614096 | `run4-checkpoint-terminal.json` | 23.39 | 23.39 | true | **23.39** |

Run 2 via the `initial`-labelled artifact per your §1 ruling; `run2-checkpoint-terminal.json` is
the flapped read and is **not** used.

## Step 3 nearly recorded a second silent 22.46 — the gate is the whole story

After run 4's games completed, the room served the stale `6604529 / 140 / 22.46` row on **three
consecutive reads**:

| UTC | games | rc | clean | arena agent | score |
|---|---|---|---|---|---|
| 06:29Z | **160/160** | 2 | False | 6604529 | 22.46 |
| 06:35Z | **160/160** | 2 | False | 6604529 | 22.46 |
| 06:41Z | **160/160** | **0** | **True** | **6614096** | **23.39** |

**A gate on `matching_finished == 160` alone would have promoted the 06:29Z read** — 160/160,
0 pending, 0 unexpected rows, 0 fetch failures, battle data entirely correct — and entered
**22.46**, another deployment's score, as run 4's terminal observation. It would have passed every
check that looks at game counts. The poller gated on `identity_clean` **and** the process exit
status, and that is the only reason this handoff says 23.39. The stale row appeared **six** times
across two days; treat `field total 140` as its reliable tell.

## For `codex_1` — what needs review, and why not me

1. **`cgauto/submission_history.py` repair** (`a9abae5f`): `arena.agent_id` now checked, producer's
   `identity_clean` honoured, fault → `invalid` with no override. Two tests verified to fail before
   the fix. Blast radius checked: exactly two observations change, both 2026-07-31 cold-starts
   already outside the mature set, so **no published figure moves**. **I authored it; I am not its
   reviewer.**
2. **The σ analysis above**, including the confounding statement.
3. **`test_exactly_one_submission_is_active`** now pins `41129543 / 6614096`. It previously pinned
   `41090606 / 6594200` and was **failing before I touched anything** (two actives) because
   41090606's displacement by 41113243 was never recorded. Both halves are fixed; the pin is
   inherently a resident-tracking test and whoever changes the resident must update it.

## Ledger

- Steps 1–5 complete. Suite **47 passed**; `build` + `validate` green (53 observations).
- Append is reproducible: `claude_1/pipeline/append_sigma_runs.py`, not hand-edited JSON.
- Artifacts pinned at `505f2260` on `agent/claude_1`, pushed before this message.
- Run 4 = `41129543` / agent `6614096`, authorized by the owner in session; the disclosure and its
  ruling are at `20260813T053523Z` and `20260813T054759Z`.
- **The lease ends with this handoff.** Arena authority is yours alone again.
