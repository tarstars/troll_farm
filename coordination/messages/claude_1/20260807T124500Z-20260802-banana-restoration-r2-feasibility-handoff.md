---
schema_version: 2
type: handoff
task_id: 20260802-banana-restoration-r2
from: claude_1
to: local_claude_1
cc: ["user", "chatgpt_1", "local_codex_1"]
message_id: coordination/messages/claude_1/20260807T124500Z-20260802-banana-restoration-r2-feasibility-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: 4d5aabeff9ef4e21b735fbc09258b6621a3fe5d1
artifact_paths: ["claude_1/banana-restoration-r2/feasibility-raw-zero-2026-08-07.md", "claude_1/pipeline/verification/fable-verify-floor-calibrated.md"]
created_utc: 2026-08-07T12:45:00Z
---

# Raw-zero feasibility scoping — the deliverable you asked for, and one number that reframes it

You asked me to scope raw `D-1 == 0` / `D-4 == 0` honestly before committing, and said a
structural-infeasibility finding would be legitimate. Delivered. Every load-bearing claim
re-derived by me, not accepted from the investigation that produced the document.

## The finding you most need, and it was not in my own brief

**Driving D-1 and D-4 to raw zero — a perfect result on the standing rule — moves the gate
from BLOCK 118/240 to BLOCK 106/240. The gate still blocks.**

Re-derived from the committed floor report, per `### mNNN seat S` section:

| quantity | value |
|---|---|
| blocking games | 118 |
| games blocking **only** on D-1 and/or D-4 | **12** |
| **floor if D-1 and D-4 were raw zero** | **106** |
| games where D-9 blocks / is sole blocker | 74 / **63** |
| floor if D-1, D-4 and D-9 were all zero | 42 |

The strict rule is necessary but nowhere near sufficient. The largest single blocker is
**D-9**, the detector already shown to be candidate-invariant (74 games on floor,
`bbe54a48` and tip alike — it measures nothing about any candidate). **Detector calibration
strictly dominates bot repair as the next move**, on these numbers: inner-policy surgery on
a rated bot would buy 12 of 118 games, while the biggest blocker is a measurement defect
that costs nothing to fix and is already referred to `local_codex_1`.

## Feasibility verdicts

- **D-4 — FEASIBLE_WITH_CONDITIONS.** One root cause, tightly localised: single-door bank
  serialisation, 6/6 on 1-door maps, 0/210 elsewhere.
- **D-1 — UNRESOLVED, leaning INFEASIBLE at acceptable cost.** Two root causes. D1-A (34/35
  episodes) is feasible-with-conditions via an untried memoryless guard; D1-B (1/35) is
  measured but **not localised in source**. A raw-zero rule is **conjunctive over episodes**
  — D1-A being feasible does not make D-1 = 0 feasible while one episode is unlocalised.

## The strongest evidence, with a correction that strengthens it

D-1's threshold sits byte-for-byte at the lower edge of the `run_5_9` bucket used by this
project's two oscillation-breaker experiments. **D176a — the best breaker ever built here,
which passed its de-novo gate perfectly — moved that bucket 213 -> 825 (+287%)** and left
the worst run unchanged at **247 turns**.

Correction owed to the record, which I checked and which makes the point stronger rather
than weaker: your integrator judged that 5-9 gate **mis-specified**, because de-novo
oscillation was 0.0%, so +287% is the signature of *long runs being fragmented* — the
intervention working as designed. Correct in its own frame, and it does not rescue us:

> D176a cut the >=10-turn rate 8.50% -> 2.88% **by fragmenting long runs into short ones**.
> D-1 fires on the short bucket. Fragmentation is a success under a rate-based gate and a
> **regression under a raw-zero gate** — the same behaviour, scored opposite ways.

So the best intervention this project has built would have *increased* raw D-1 substantially,
and its one 247-turn survivor is fatal on its own under a zero rule.

## Rating risk — the part the gate cannot see

27 of 41 episodes assess as **benign artifact**, not defect: in 21/35 D-1 episodes the
contested tree was the only reachable plant, i.e. idleness expressed as motion, with a
recoverable-time upper bound of ~2.7 turns/game. The opponent-artifact hypothesis is
**refuted** (idle 12.5%, harvester 15.6%, chopper 11.1% — no signal), and the mechanism
replicates in the real corpus (B3.4: 18/194 real games, teammate parked 17/18). So these are
real, not harness ghosts — but mostly harmless.

The gate cannot see arena rating, and the orchard ablation already demonstrated on this
project that removing behaviour which looked useless made the rating **significantly worse**.

## Recommendation

Do **not** open inner-policy repair on the rated parent yet. Calibrate D-9 first, re-derive
the floor, and re-ask the question against a gate that can actually reach ACCEPT. If the
strict rule is retained exactly as written, my present read is that raw D-1 = 0 is not
reachable on this parent at a cost proportionate to the 12 games it unblocks — the honest
finding you invited, now on the table with its evidence.

I am not asking for the rule to be changed, and I have not assumed it will be. I will
implement whichever way you and the owner rule.
