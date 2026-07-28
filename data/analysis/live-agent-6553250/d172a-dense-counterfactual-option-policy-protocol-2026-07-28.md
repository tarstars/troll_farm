# D172a — dense counterfactual credit: can observables predict the envelope's positive contexts?

Status: FROZEN protocol, authored 2026-07-28 (Fable), under the owner's Tier-2 reopening.
Execute exactly; no threshold, feature-set, function-class, τ, or seed-range change after
any outcome is seen.

## Question

D169 proved a +10.671 [+9.42, +11.92] per-game selection ceiling over the resident-native
options; D170b proved on-policy terminal-reward learning cannot find the rare positive
contexts (~200 samples/arm vs SD≈26 noise → all objectives learn always-KEEP). D172 asks
the remaining question: with **exact, zero-noise counterfactual labels** at every armable
state, can a small observable-feature policy select options profitably on held maps,
closed-loop? A NO here is the final closure of the learning route.

## Why this is not the closed offline-value class (design rationale, binding)

- Labels are exact deterministic counterfactuals — margin(option-at-s → resident) −
  margin(resident) with identical prefixes — not regression targets fitted from another
  policy's trajectories (the D153–D156 disease).
- Decision states are the exact resident's own visited states by construction (the
  deterministic prefix), so there is no train/deploy covariate shift at budget-1: the
  policy's pre-intervention distribution IS the labeling distribution (the Phase-12–14
  disease does not apply).
- The decision is per-option invoke/keep with a frozen threshold — no 64-way ranking, no
  scalar carrying two meanings (the D116/D127 diseases).
What remains untested — and is the actual question — is feature expressiveness: whether
the 64-field state + affordance/trigger block separates positive contexts at all
(D100b's warning: hindsight winners were trajectory-specific on the old substrate).

## Phase 0 — label-pipeline validation

Reuse the D169 envelope machinery unmodified (hash-verify its lock). Validate the
per-decision label semantics by recomputing a 32-(task,arm) sample of D169's consumed-
panel arm values and matching them **byte-exact**. Any mismatch → BLOCKED.

## Phase 1 — training corpus

- Maps: seeds **9,860,000–9,860,511** (512 fresh maps; pre-lock grep both ledger volumes
  for `9,86` overlaps; sealed ranges untouched) × 8 families × both seats = 8,192 tasks.
- For every task: enumerate all armable decision states under the exact resident (the 13
  D169 arms' arming events, budget-1 semantics) and label each (state, option) with its
  exact counterfactual value. Record per state the full observable feature vector (the
  D170 feature builder: 64-field state + turn + opponent-worker-count trigger +
  armable-option one-hots + affordance scalars) — document the final field list in the
  lock.
- Local 20-thread or YT (established parity rules; ~10⁵ episodes expected). Byte-identity
  jobs1-vs-jobs20 on a 16-map subsample (full double-run not required at this scale;
  the subsample substitutes, frozen here).

## Phase 2 — signal floor (cheap early kill)

Frozen floor: **≥ 8% of armable states have max-option label ≥ +2.0**, present in both
seats and ≥ 6 families. Below floor → **CLOSED-AT-SIGNAL** (the value density is too
thin even for perfect labels; record and stop — this is the cheapest honest death
available and must not be softened).

## Phase 3 — fits and selection

- Function classes (both, frozen): (a) linear per-option scorer on the feature vector;
  (b) MLP feature→16→per-option heads, ≤ 12,288 params. Two seeds each = 4 fits,
  deterministic single-thread, supervised on the exact labels (Huber loss on value;
  runtime rule: invoke the argmax option iff predicted value > **τ = +1.0**, frozen —
  the margin over zero pays for generalization error; else KEEP; budget-1).
- Selection blocks: seeds **9,861,000–9,861,127** as 8×16 LOBO. For each fit, execute
  the learned policy closed-loop on held tasks vs paired control.
- Admission (ALL): LOBO pooled mean ≥ **+1.5**; worst held block ≥ 0; worst family ≥ −1;
  activation in 5–60% of tasks; crop/workforce exact; catastrophes ≤ control.
  Selection among admitted: max worst-held-block → pooled mean → lowest seed.
- No admission → **CLOSED-AT-SELECTION**.

## Phase 4 — veto and confirmation (one attempt each)

- Veto (consumed 1,024 panel, veto-only, no substitution): mean ≥ +1.0; no family < −2;
  tails ≤ control. Fail → CLOSED.
- Confirmation (sealed **9,862,000–9,862,063**, opened exactly once, single run): mean ≥
  **+2.0**; clustered CI floor > 0; all families ≥ −1; catastrophes ≤ control; negative
  mass ≤ 1.1 × control. Pass → **CONFIRMED** — STOP. Deployability port and any arena
  action are separate dispatches; the arena additionally requires a NEW owner
  authorization at that gate (the D171a grant was scoped and never carried over).

## Prohibitions

No τ/threshold/feature/class changes post-outcome; no training or selection on the
consumed panel (veto-only); no fitting to D169's consumed-panel winners; frozen modules
untouched (compose only); one deterministic training thread per fit; `LC_ALL=C`;
checkpoints/bulk external (`artifacts/experiments/d172a-dense-counterfactual-option-policy/`).

## Outputs

House convention `d172a-dense-counterfactual-option-policy-{lock,result-2026-07-28.md,
result.json}` + per-fit results; corpus manifest with row counts and hashes; phase
markers to `.superpowers/sdd/d172a-phase-markers.md` after every phase AND every 128
corpus maps (API-drop resilience). Ledger integration is the controller's.

## Decision tree

Phase 0 mismatch → BLOCKED. Phase 2 below floor → CLOSED-AT-SIGNAL. Phase 3 no admission
→ CLOSED-AT-SELECTION. Phase 4 fail → CLOSED. Confirmation pass → CONFIRMED, STOP for
deployability dispatch + owner arena decision. Any CLOSED = the final closure of the
Tier-2 learning route; record accordingly.
