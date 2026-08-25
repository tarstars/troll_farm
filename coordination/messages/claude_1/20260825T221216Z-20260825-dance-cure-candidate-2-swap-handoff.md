---
schema_version: 2
type: handoff
task_id: 20260825-dance-cure-candidate-2-swap
from: claude_1
to: ["codex_1", "local_claude_1"]
cc: ["user", "chatgpt_1"]
message_id: coordination/messages/claude_1/20260825T221216Z-20260825-dance-cure-candidate-2-swap-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: 7ea1df9fe214cf951c4c92a5feaa90538db34994
artifact_paths: ["claude_1/cure2/p3_read.py", "claude_1/cure2/p3-read-2026-08-25.md", "claude_1/cure2/results/p3-read-candidate-arm.json", "claude_1/cure2/arm-candidate.rs", "claude_1/cure2/cure2-candidate-config.json", "claude_1/cure2/results/panel-candidate.json", "claude_1/cure2/results/panel-swap-census.json", "claude_1/cure2/results/c16-scoping-control-primary.json"]
created_utc: 2026-08-25T22:12:16Z
---

- To: codex_1, local_claude_1
- CC: user, chatgpt_1
- Task: 20260825-dance-cure-candidate-2-swap
- Requires acknowledgement: yes — this is the P3 read the standing card put first

# The candidate-arm P3 read — **0 violations over 240 seat views**, and **228 of those zeroes are a guard returning before any stream comparison**

Subject `claude_1/cure2/arm-candidate.rs` (`5577cdce4789…`, `NARRATE_V5_ENABLED=false`), the
whole 240-view panel population, graded by `fuzz_panel.eval_p3` **imported**
(`claude_1/pipeline/fuzz_panel.py:1817`), not restated. Runner `claude_1/cure2/p3_read.py`.
Re-run byte-identical.

## The bar, and the decomposition that is the actual read

G-0 §8: *P3 games on orchard-eligible views (whole-game) = 0.* **Measured 0. Bar met.**

A bare 0 cannot tell "checked and held" from "never reachable", so every view is classified by
which of `eval_p3`'s three exits it took:

| exit | views |
|---|---|
| **A** — `not orchard_eligible`: returns `[]` before comparing the streams at all | **228** |
| **B** — eligible, streams compared and **equal** (the scoping's whole-game inertness) | **12** |
| **C** — a violation | **0** |

**No part of the zero comes from the candidate changing a stream and P3 finding it acceptable.**
95 % of it is a guard; the rest is inertness the design puts there deliberately and prices in §3.6.

**Exit C is reachable on this exact population**, so the zero is a live branch that did not fire,
not a dead one: on these same 12 eligible views the scoping-off arm fires P3 once (`m004:0`,
`results/c16-scoping-control-primary.json`).

## P3\* — the counterfactual, a size and never a verdict

`eval_p3(True, candidate, parent)` on the 228 **non-eligible** views — the same whole-stream
predicate where P3 does not reach. Not a property violation, never reported as one.

**The candidate changes 28 of 228 non-eligible views**, first divergence turns 2 … 194. Those 28
are **exactly** the 28 games the C-4/C-15 census recorded an exchange on, decoded off the
**instrument** arm's `sw=` wire — a different arm reached by a different route. That is gate G-C.

## A figure that changes meaning at a boundary — flagged because it will bite the cost table

C-15's published net cost is a delta of **own scores**; the C-16 and P3\* figures are deltas of
**margin**. Over this panel they differ **in sign**:

| aggregate, 240 views, candidate − parent | value |
|---|---|
| own score | **−24** |
| opponent score | **−80** |
| **margin** | **+56** |

The candidate banks 24 fewer of its own and holds the opponent 80 lower. Both are real; neither may
be quoted as the other. C-16's "+39 forgone margin" is a margin figure and is consistent. **The
G-1 cost table needs the units written out beside every one of these numbers.**

## Gates — each aborts the run rather than degrading the number

| gate | result |
|---|---|
| **G-S** subject identity | PASS — hash matches the panel config and the sidecar; `NARRATE_V5_ENABLED=false`; differs from `arm-instrument.rs` in exactly that one line |
| **G-Q** narration observed off | PASS — on all 240 views the candidate's `MSG` fragments are identical to the **parent's** (the champion's one-time banner and nothing else) |
| **G-P** population identity | PASS — 240 regenerated views agree with `results/panel-candidate.json` on map, seat, class, eligibility |
| **G-M** reproduction | PASS — every view reproduces that run's recorded candidate **and** parent margins |
| **G-B** eligible-class inertness | PASS — 12/12 byte-identical to the parent |
| **G-C** correspondence with the census | PASS — 28 changed off-class views = the census's 28 exchange-bearing games |
| **G-V** vacuity demonstration | PASS — 28 views where the streams differ, `eval_p3(False, …)` is `[]` and `eval_p3(True, …)` returns a divergence |

**G-V is why the run exists.** Without it "0 P3 violations" is a sentence with no measurement
behind it. It is also the run's own null handling: had no off-class view changed the stream, the
runner returns **INCONCLUSIVE**, by construction — not a pass.

**Two gates were wrong on their first draft and were corrected against the bytes, not around
them,** and I would rather you read that from me than find it: G-S first rejected the correct
subject by grepping for the token `MSG`, which is compiled into **both** arms and merely
unreachable in this one — the flag is the discriminator, not the token. G-Q then failed on turn 1
because both bots emit the champion's own `MSG yamo-…` banner; "no MSG at all" is the wrong
observation and "no MSG the parent does not also emit" is the right one. Neither correction
loosened a bar: both replaced a check that was testing the wrong thing with one testing the thing.

## What this does NOT say

- Not that the candidate is P3-neutral in any sense stronger than the scoping's whole-game
  inertness. It is not, §3.6 says so, and this run prices it rather than arguing it away.
- Not that the 28 off-class changes are harmless. P3\* is a size; P1, P4 and D-3 are what reach
  off-class and the panel grades them.
- Not anything about eligible-map dances — untouched by Candidate 2, the standing §3.6 cost.
- The eligible class is **seat-0-only** in this generator, so the 12/12 inherits that asymmetry.

## Queue effect

The candidate-arm P3 read is **closed**; **P3 is MEASURED**, with the decomposition above attached
wherever the 0 is quoted. Next: **C-12** (per-troll idle-with-work, `--p4b` **ON**), then the
**G-1 handoff** for the fresh-archive reproduction of the whole control set. Deferrals: carded
separately, self-addressed. No Arena action taken or proposed.
