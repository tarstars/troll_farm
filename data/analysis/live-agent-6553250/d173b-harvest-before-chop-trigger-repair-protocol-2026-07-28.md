# D173b — trigger-fidelity repair and re-run of D173a

Status: FROZEN protocol, authored 2026-07-28 (Fable), adjudicating D173a's CLOSED as an
implementation-fidelity invalidation (house precedent D170a→D170b): the implemented
trigger fired on CHOP-candidate *existence* at the unit's cell, not on CHOP being the
unit's *actual assigned action* — 41/60 sampled activations were transit units diverted
mid-plan, outside the frozen scope. The frozen narrow fix was never tested. D173a's
run stands as the record of the over-broad variant (overall +2.935 [+1.346,+4.524],
activated +5.763, but worst family −2.06, catastrophes +5, mass 1.096, all mechanism
gates failed — that variant is CLOSED as tested and may not be tuned).

**D173b inherits the D173a protocol in its entirety** (same fix concept, binding
constraints, panel seeds 9,854,000–127 re-run from scratch, integrity/mechanism/value
gates, verdict rule, compile-then-restore flow) with exactly two deltas:

## Delta 1 — trigger fidelity (the repair)

The candidate is emitted ONLY when ALL hold on the current turn:
(a) the unit's currently-assigned winning action — the task the resident's assignment
    would execute this turn absent this fix — is CHOP on the tree at the unit's own cell;
(b) that tree bears ripe fruit;
(c) the tree is at shack-distance ≤ 2;
(d) the unit is harvest-capable (actual harvest_power ≥ 1).
Implementation must read the assignment outcome (or reproduce its winning-task
determination exactly), not candidate existence. Unit tests must include: transit unit
passing a fruited choppable tree → NOT emitted; unit whose winning action is CHOP on its
fruited own-cell tree → emitted; plus the D173a test set updated to the corrected
semantics.

## Delta 2 — pre-panel fidelity verification (frozen)

Before the full panel: on a 64-task activation sample, ≥ **90%** of activations must show
CHOP as the unit's issued action within the two turns before or the same turn absent the
fix (the same check the D173a root-cause used, where the broad trigger scored 19/60).
Below 90% → BLOCKED (no further self-repair).

Everything else — panel size/seeds, all six-detector displacement checks, the ≥70%
sub-class mechanism gate, value gates (overall ≥0 with CI ≥ −0.5; activated ≥ +1.0;
worst family ≥ −1.0; catastrophes ≤ control; mass ≤ 1.05×), QUALIFIED→candidate-and-stop
/ CLOSED→restore rules, outputs (d173b- prefix), and prohibitions — identical to D173a.
Expected activation falls sharply vs D173a's 50.9% (the genuine sub-class was ~202/2,048
episodes in the corpus diagnosis); low activation is fine — the activated-subset and
mechanism gates carry the verdict.
