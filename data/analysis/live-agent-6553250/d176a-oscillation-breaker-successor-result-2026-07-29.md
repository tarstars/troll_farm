# D176a — oscillation breaker successor: result

Date: 2026-07-29. **Verdict: CLOSED-AT-MECHANISM** (as recorded by the analyzer in
`d176a-oscillation-breaker-successor-result.json`).

Provenance: the executing agent completed the fix, unit tests, trigger-fidelity check,
the full 2,048-task panel, and the complete gate analysis, then was killed by a transient
API error (twice) before writing this document. It is assembled by the integrator
(`claude_1`) from the analyzer's own `result.json`; every number below is quoted from that
file and no verdict has been reinterpreted. The dev copy was verified byte-exact at SHA
prefix `fff6669b` after the run.

## Integrity — all pass

Command purity ✓; inactive episodes byte-exact vs control ✓; **1-vs-20-thread byte
identity ✓** (the jobs1 cross-check did complete). Trigger fidelity **100.0% on n=152**
activations — and notably the agent first measured 95.4%, refused to accept a passing
number at face value, investigated the seven apparent failures, and found a genuine
indexing bug **in its own verification script** (a unit trained mid-game leaves gaps in
`state["u"]`, which an append-only history list silently misaligns); it fixed the script,
not the fix, and re-ran to 100%.

## Mechanism — 2 of 4 sub-gates pass; the gate as a whole fails

| sub-gate | control | candidate | gate | verdict |
|---|---|---|---|---|
| ≥10-turn task rate | 8.50% (174 tasks) | **2.88% (59 tasks)** | ≤6.0% | **PASS** |
| de-novo oscillation | — | **0.0% (0 tasks)** | ≤1.0% | **PASS** |
| 5–9-turn runs | 213 | 825 (**+287%**) | ≤+10% | **FAIL** |
| worst-case run length | **247 turns** | **247 turns** | ≤20 | **FAIL** |

## Value — all six gates pass

Overall mean margin delta **+0.045**, map-clustered 95% CI **[−0.024, +0.114]**;
activated-subset mean **+0.612** on 152 tasks (floor +0.5); catastrophes **73 vs 73**
(tied); negative-margin-mass ratio **0.999**; worst family `script_boss` **0.000**
(floor −1.0). Family deltas span 0.000 to +0.258 — no family is harmed.

## Integrator adjudication, including two errors of my own

**The verdict stands as recorded.** The protocol was frozen, the analyzer applied it, and
CLOSED-AT-MECHANISM is the correct output. It is not reinterpreted here, and no gate is
rescued after the fact — that discipline is the point of the whole method.

**But the record must also state that the two failing gates were mis-specified by me.**

1. *Worst-case run length.* I anchored the ≤20-turn gate to H13's **real-corpus** figure
   (our worst observed run: 133 turns). On this synthetic panel the **control's own worst
   run is 247 turns** — identical to the candidate's. The candidate therefore did not
   worsen the tail at all; it simply failed to cure one outlier, against a threshold
   calibrated on a different population. A gate the control also fails, by a factor of 12,
   is not a discriminating gate.
2. *5–9-turn displacement.* I inherited this gate from D171a, where +117% short runs
   accompanied **manufactured** oscillation (72 previously-clean tasks acquired runs).
   Here de-novo oscillation is **0.0%, zero tasks** — so the +287% short runs cannot be
   manufacture. Fewer long runs (174→59 tasks), more short runs, and no new oscillation in
   clean tasks is the arithmetic signature of **long runs being fragmented**, which is the
   intervention working as designed. The gate as written cannot distinguish fragmentation
   from manufacture; the de-novo gate can, and it passed perfectly.

**Why the oscillation line still closes, on better grounds than the gates.** Even reading
the mechanism charitably, the value is negligible: **overall +0.045 margin with a CI
straddling zero** — on the order of 0.005 rating. The activated subset gains +0.61 across
18% of games, which is real but rounds to nothing at the ladder level. So D176a closes not
because the fix fails but because a *working* version of it is not worth a promotion cycle.
The frozen protocol's disposition ("two designed attempts against a measured ceiling is
enough") therefore stands, and reaches the same place by a different road.

**What this buys for future protocol design** (the durable lesson): a mechanism gate must
be calibrated on the **same population the panel measures**, not on a corpus statistic from
elsewhere; and a gate must be able to distinguish the intervention's *intended mechanism of
action* from the failure mode it was inherited to catch. Both errors were mine, and both
are now recorded in CONSTRAINTS.

## Reproducibility

`d176a-oscillation-breaker-successor-result.json` (all gate values, per-family deltas,
best/worst tails); `d176a-fix-as-tested.patch`; panel rows and trajectories under
`artifacts/experiments/d176a-oscillation-breaker-successor/`; fidelity check
`d176a-trigger-fidelity-check.json`; phase markers `.superpowers/sdd/d176a-phase-markers.md`.
Seeds 9,857,000–127 are consumed. No candidate artifact was built (QUALIFIED-only step).
