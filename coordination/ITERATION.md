# ITERATION POOL — oscillation verdict (opened 2026-08-17)

**Owner's goal:** decide whether the resident's (`98628e98…`) oscillations are
BENIGN (write the harmless ruling, ignore them) or SYMPTOMS OF ILLNESS (charter the
cure). Already established: the dance itself is priced at ≈ +0.045 (T-1 graded 1/25);
the live question is the PARKED troll.

**Verdict rule (frozen in advance):** benign = parked-idle does not explain the margin
deficit and no cheap cure exists; illness = parked-idle explains it → cure = the
generator-coverage property ("a troll with reachable, usable work receives at least
one non-WAIT candidate"), tested on the 34 fixtures + 240-game panel.

**Scope lock:** nothing enters this pool without an explicit owner addition. Progress
is updated in THIS file by the integrator at every session; every session summary
begins with `Pool: N/M done`.

## Pool (P0 = the diagnosis chain, in dependency order)

- [x] 0. Pool opened; charters + codex queue order published (local_claude_1)
- [ ] 1. Instrument repairs — HARD GATE, nothing accepted from this track before it:
      anchor-unit fix (4× restated), exact coverage, direct candidate logging,
      eligible-action oracle (capability × fruit state × sink), negative controls
      observed firing (walled-in + zero-capability arms) (claude_1)
- [ ] 2. Instrument re-review (codex_1 — TOP of queue)
- [ ] 3. Full 34-situation sweep → cause table in the owner's three-level vocabulary:
      no-goal-assigned / goal-split-wrong / world-interaction / cannot-use-work /
      not-starved (claude_1)
- [ ] 4. Margin decomposition on the EXISTING 240-game panel data: does margin track
      parked-idle turns or oscillation episodes? Prices the illness; no new runs
      (local_claude_1; codex_1 verifies method)
- [ ] 5. Mechanism note per no-goal case: which generator path emits the WAIT-only
      list; deliberate (phase gating) or broken (claude_1, small)
- [ ] 6. OWNER SESSION — the verdict: per-cause ruling, harmless-ruling or
      cure-charter; ledger entries (owner + local_claude_1)

## Parallel (non-blocking)

- [ ] 7. **RESTATED 2026-08-17 (integrator's record correction):** Spec v3 was already
      reviewed 2026-08-16T06:00Z — verdict **REVISION_REQUIRED**
      (`codex_1/reviews/banana-farm-two-specs-v3-review-2026-08-16.md`), unread by the
      integrator for ~26 h. 7a: spec REVISION (**local_claude_1**) — (i) score-delta
      abort bias characterized in BOTH directions (wood=4pts can mask enemy banana
      gain → late/never abort; the "safe direction" assurance is false), (ii)
      K_futility=10 labelled a heuristic + constructed long-in-flight-chop negative
      case (or a real bound). 7b: codex_1 re-review in queue gaps. Then owner
      approval. No new design decisions.
- [ ] 8. Methods ledger consolidation `docs/METHODS-LEDGER.md` (local_claude_1, ~1 h)
- [x] 9. OWNER-ADDED 2026-08-17: WIP limit — one in-flight ack-requiring handoff per
      agent per task; protocol §10 rule + sender-side lint check, tests observed
      firing (local_claude_1)
- [x] 10. OWNER-ADDED 2026-08-17: evidence gate — cause-label handoffs require
      `review_ref:` resolvable on an authoritative ref; lint check + tests; plus
      `scripts/pool_status.py` (pool state computed, not maintained) (local_claude_1)
- [x] 11. OWNER-ADDED 2026-08-17: coordd promote-or-park DECISION DATE set:
      2026-08-31 or pool close, whichever later; no standing dual plane
      (runbook amended) (local_claude_1)

## Parked — explicitly OUT of this iteration

Full bridge-as-code (term census B0 / property audit B1 / band enforcement B3 — shaped
by the verdict session's rulings, not before); T-1 half-swap fixture (recorded debt);
viewer Phase 2; full Decision Packet contract; ALL Arena actions (resident untouched).

## Progress log (newest first)

- 2026-08-17 (pool #4 DELIVERED, pending codex method check): margin decomposition
  on the 240-game floor (`local_claude_1/pool4/`, artifact `561a5353`): the
  whole-bot no-progress STALL is the billable event (stall games −12.5 vs par,
  p≈1e-4; ceiling ≈1.4 corpus points if cured); the DANCE is mostly a MARKER
  (dance-only games −9.6 with just 14 dancing turns, p≈0.005). Feeds verdict
  session #6 next to the cause table.
- 2026-08-17 (pool #1 delivered → REOPENED): claude_1 delivered all five repairs
  (`94e19320`); integrator verification against the frozen library RULED the anchor
  question claude_1 had routed up: per-kind rule (D1 → `classification/blocker`;
  blocker-less pair → unique non-dancer; single-unit OSC-026 → NO_ANCHOR correct;
  **P4_STALL → window.unit itself**). claude_1's own-invented rule excluded the
  P4 window unit — the OSC-031 defect again — so #1 is reopened for the offered
  one-function change + reconciling the single-unit count (handoff says 3, library
  says 1). Then straight to codex (#2, rule above = the spec).
- 2026-08-17 (later): **integrator record correction** — pool #7's premise was wrong:
  the Spec v3 REVISION_REQUIRED verdict had been delivered 08-16 06:00Z in a
  no-ack-required message the integrator never opened; the spec thread was blocked on
  the INTEGRATOR (revision), not on codex_1, for ~26 h. Root cause: seen-state
  (`--mark`) never adopted, so verdict-bearing acks could rot unread; ritual fixed
  (sweep + read ALL new + `--mark`). Also: evidence-gate token registry extended with
  the five pool-#3 serializations (codex_1's catch; 33/33 tests, new tokens observed
  firing+releasing); claude_1 synced the gates from trunk and delivered pool-#1
  oracle progress (capability×fruit×sink with paired positive-twin controls;
  OSC-012 planner vindicated 0/193 eligible; OSC-001 old predicate overstated 5×).
- 2026-08-17: owner added items 9–11 (best-practice fixes); all three DONE same
  session — lint gates live (31/31 transport tests green, both gates observed
  firing), `pool_status.py` live, coordd decision date set. Check progress any
  time: `python3 scripts/pool_status.py`.
- 2026-08-17: pool opened; item 0 done (charter message
  `coordination/messages/local_claude_1/20260817T072116Z-20260817-iteration-pool-and-queue-order.md`).
