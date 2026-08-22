---
schema_version: 2
type: handoff
task_id: 20260808-phase1-work-allocation
from: claude_1
to: local_claude_1
cc: ["user", "chatgpt_1", "local_codex_1"]
message_id: coordination/messages/claude_1/20260808T183000Z-20260808-detector-bitetest-audit-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: 890879e64efaf289f792b3da8fc75abcd11ce59b
artifact_paths: ["claude_1/banana-restoration-r2/detector-bitetest-audit-2026-08-08.md"]
created_utc: 2026-08-08T18:30:00Z
---

# Item 4 audit: 0 of 9 pairs establish truth validity, and D-6 enforces a predicate the design retired

Audit only; no detector, test, gate, candidate or harness touched. Suite still 28/28.

## The headline, verified by me directly

**`founding_safety_oracle` is called by ZERO detectors** — `grep -c` across
`trace_detectors.py` returns 0. Design finding **F4**
(`design-banana-fsm-2026-08-06.md:1170`) records that this oracle *replaces* arrival-order
with exact executable-HARVEST safety. **`detect_d6` still implements the superseded
arrival-order predicate** (`eta_opp_h(c,t) <= min_u eta_u(c,t)`, `eta_opp_x <= 2`), and both
its bite-tests pass because they were written from that same superseded predicate.

On the audit's fixture the replacement oracle judges the **near-miss** unsafe twice over
(`opp_harvest_turn == our_harvest_turn == 26`; `opp_destroy_turn = 12 < 26`) while
`detect_d6` returns PASS.

**This is GAR-3 in its purest form, and it is my defect:** a spec revision that landed in the
design document and never reached the code that enforces it. D-6 fires 9 games / 15 episodes
on the floor, all adjudicated by a predicate the design says is wrong.

## Audit results

- **0 of 9 pairs establish truth validity.** One discriminates a *definitional* property (D-5
  ring geometry — only because I-12 is a definition); one discriminates a conceptual revision
  (D-8) but **circularly**, since `detect_d8` calls the very oracle its spec names. The other
  seven discriminate implementation only.
- **Exactly one independent truth label exists** — `founding_safety_oracle`, for D-6, and it
  is unused. `asset_survival_oracle` is non-circular for D-8 in principle, but all four D-8
  fixtures set opponent `cp=0`, which makes it provably identical to the oracle D-8 already
  calls. **D-1, D-2, D-3, D-4, D-7, D-9 have no oracle available at all.**
- **Mutation: 64 mutants, 20 caught / 44 survived — a 31% kill rate.** No mutant was ever
  caught by a detector other than its own. Worst: D-7 1/8, D-9 1/4, D-1 2/8, D-6 2/9.
  Best: D-8 6/11; D-3 has the suite's only two-sided threshold pin.
- Notable survivors: **D-1's A≠B≠A shape clause is deletable**; **D-7's door-cell and
  inventory-increase conjuncts are each deletable**; **D-6's clauses (a1) and (b) each
  deletable in full**; D-8's growth-aware chop arithmetic is replaceable by static
  `ceil(health/chop)` *despite an explicit helper-level assertion of the round-3
  counterexample*.

## What this means for the programme

The bite-tests answer "does the detector obey its spec" and mostly cannot answer "is the spec
right" — which is exactly what GAR-3 predicted, now measured rather than argued. A 31% kill
rate means the suite pins roughly a third of the behaviour it appears to cover.

I am **not** proposing repairs here; the audit was scoped to measurement, and D-6's fix is a
detector-semantics change under your ownership. The one thing I would flag as urgent
independent of scope: **any verdict currently citing D-6 rests on a retired predicate**, and
the floor's 9 D-6 games should not be quoted until that is resolved.

Deliverable carries the per-detector table (implementation / calibration / truth validity),
the full mutation ledger, and a named falsification probe for each detector.
