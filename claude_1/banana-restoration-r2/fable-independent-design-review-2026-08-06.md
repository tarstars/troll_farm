# Fable independent critical review of the revised FSM design + comparison to the agent's work

Reviewer: claude-fable-5 (orchestrator), reviewing NOT from the revision agent's report but
from the design document, the oracle code, the materialized manifest, and the referee
mechanics in `research-banana-r2.rs`. Artifact: `design-banana-fsm-2026-08-06.md` +
`conversion_race_oracle.py` + `enumeration_manifest.py`/`enumeration-manifest.json` at the
round-6 revision head. This document is the deliverable for the owner's two tasks:
(1) my own critical review, (2) a comparison of my findings against the agent's claims.

## Task 1 — independent critical review

### What I verified by running/reading, not by trusting the report

| Finding | My independent check | Verdict |
|---|---|---|
| **F3 oracle over-count** | Extracted the referee's `resolve_move_conflicts_with_priority_and_forbidden`: it reserves a distinct landing cell per own unit, so two same-player units cannot end a turn on one cell; CHOP gates on `unit.cell == plant.cell`. Therefore ≤1 chopper on the tree per turn. The fix's `power = max(arrived)` (one chop/turn, best arrived single power, growth tick between) is the **exact worst-case**, not merely a smaller number. | CLOSED — correct against source |
| **F4 founding not exact** | Read `founding_safety_oracle`: frozen post-PLANT `t+1` anchor, resident-on-ring harvest ETA 0, `our_harvest_turn < opp_harvest_turn` AND `< opp_destroy_turn` both STRICT, with the cross-player last-fruit-duplication reasoning making equal turns unsafe. Replaces arrival-order with executable-HARVEST. | CLOSED — correct and complete |
| **F8 manifest was prose** | Ran `enumeration_manifest.py` myself: regenerates **byte-identical** (sha `dc9ab5eb…`), 1,594 rows, digest `d29d80c2…`, target universe 70, "uncovered targets: NONE". A real generated artifact with a computed coverage proof, not a described grid. | CLOSED — materialized, deterministic |
| **F1 causal phase** | Design now defines a 5-phase intra-turn order (read → arbitration → delegate → observe command-events incl. EV10 in PHASE-4 → select+post-edit PHASE-5). An event cannot be consumed before the phase that produces it. | CLOSED — the causal bug is structurally removed |
| **F10 §C honesty** | Counted the table's PRIMARY-class cells myself: **8 IBC / 6 AC / 3 EW = 17**. The livelock defects DEF-09/10 are correctly demoted IBC→AC ("an ENFORCED runtime decision verified by A-4 + enumeration, not a structural impossibility"); DEF-14 IBC→EW. The over-claim chatgpt_1 flagged is gone. | CLOSED — tally is honest |
| Oracle self-test | Ran `conversion_race_oracle.py`: OK (ST1–ST7, no-summation invariant, founding-safety outcomes, trace_detectors cross-check). | PASS on my machine |

F2, F5, F6, F7, F9: read and judged design-adequate (S6 demoted to a Mealy output; carrier-yield generalized with a physically-releasing ASIDE; count-based fungible-inventory reservation replacing lineage lots; EV20 dynamic + S3; side-effect-free per-channel telemetry). I did not find a defect in these.

### My own residual concerns (NOT raised by either prior reviewer)

1. **RC-1 (worst-case realism of F3):** `max(arrived)` assumes the opponent always keeps its
   strongest-arrived chopper on the tree cell, swapping units for free across turns. That is
   the correct *worst-case for us*, so it is safe for a survival gate — but it means the
   oracle is pessimistic where a real opponent mis-plays. Acceptable for a safety gate; worth
   one sentence in §A.7 so a future reader does not mistake pessimism for a bug.
2. **RC-2 (coverage universe = 70):** "no uncovered targets over 70" is only as strong as the
   target set's completeness. The manifest proves every enumerated target is witnessed; it
   does NOT prove the 70 targets are the complete set of behaviours. That is the standing
   limit of any coverage argument and is honestly the enumeration tier's job, not a defect —
   but the design should state that the 70 = |EV|+|T-ids|+|collisions|+|ST|+|reds| is the
   claimed-complete set, so the claim is auditable.
Neither is blocking; both are one-line documentation asks.

## Task 2 — comparison: my analysis vs the agent's reported work

- **Agreement on all 10 findings.** Every finding the agent reported as closed, I independently
  judged closed — and for the three I scrutinised hardest (F3, F4, F8) I confirmed the
  *mechanism*, not just the outcome: the referee conflict rule for F3, the executable-HARVEST
  anchor for F4, a byte-identical regeneration for F8.
- **No unverifiable claim.** The agent's headline numbers (1,594 rows; 8/6/3 §C tally; oracle
  self-test green; deterministic manifest) all reproduced exactly on my own runs. No claim was
  taken on faith and none failed.
- **Two things the agent did NOT surface that I did:** RC-1 and RC-2 above — both
  documentation-level, neither a correctness defect. This is the expected residue: the agent
  fixed what the reviewer named; the independent pass finds the softer edges around the fixes.
- **Net:** the agent's work is accurate and complete against the ten findings. My independent
  review does not contradict it; it adds two non-blocking clarity asks.

## Disposition (my recommendation to the coordinator)

The design is materially stronger and, on my independent check, closes all ten findings
correctly. I recommend it go back to `chatgpt_1` for the next design-only round with RC-1/RC-2
folded in as clarifications (not corrections). I did not find a blocking defect. No
implementation until the reviewer accepts.
