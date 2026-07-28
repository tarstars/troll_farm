# D170a — family-robust closed-loop option policy (B2.2)

Status: FROZEN protocol, authored 2026-07-28 (Fable), following D169's PASS
(envelope +10.671 [+9.420, +11.922]). Execute exactly; no threshold, objective,
architecture, budget, or seed-range change after any outcome is seen. This protocol
resurrects the four-objective comparison D158 froze but never ran (killed for substrate
reasons), now on the valid resident-native substrate — answering the skipped-D109
question: does a family-robust objective with own-score protection prevent the family
rotation (r=−0.014) and own-score suppression that killed pooled-margin training?

## Question

Can a small, observable-feature policy, trained closed-loop over the D169 option
vocabulary, capture ≥ +2.0 mean paired margin on fresh held data with no opponent family
sacrificed — turning the measured +10.7 selection ceiling into transferable value?

## Environment (sequential wrapper over the D169 machinery — reuse, do not reimplement)

- Substrate: exact warmed resident; the 13 D169 arms' arming conditions define the
  decision points. At each armable state, in deterministic within-game order, the policy
  chooses KEEP or invoke that armable option. **Budget: one activation per game** (matches
  the envelope's semantics). After activation, exact resident to terminal.
- Reward: terminal **paired margin vs the same-map/seat exact-resident control**
  (computed once per map/seat and cached — the paired baseline is the variance reducer).
- Opponents: the 8-family panel exactly as in the D148/D169 harness.
- Integrity requirements inherited from D169 verbatim: control parity vs D161 on any
  consumed-panel run; inactive games byte-exact vs control; purity/vocabulary/provenance/
  reward-identity/accounting; `LC_ALL=C` for text verification; frozen D162/D163/D167/
  D168/D169 modules hash-verified and unmodified — compose only.

## Policy (frozen)

- Inputs, observable-only (opponent identity NEVER a feature): the 64-field state family
  as computed by the existing builders, plus a decision block: turn, observed opponent
  worker count (the B3.1 trigger feature), armable-option one-hot, and that option's
  affordance scalars (e.g. banked-seed count for OPT_RETURN). Executor assembles from
  D169's existing computations; document the final field list in the lock.
- Architecture: 16-unit GRU over per-decision inputs + linear head over
  {KEEP, invoke}. Parameter cap 12,288. Sampled actions in training; deterministic
  argmax at evaluation.

## Phase 1 — objective comparison (the resurrected D158 four-way)

Same maps, same seeds, same transition budget for all variants; family labels appear in
the LOSS only (we choose training opponents locally), never in policy inputs.

- O1 pooled paired margin (control objective).
- O2 upside-capped margin: reward clipped at +50.
- O3 margin + own-score protection: reward − 0.5 · max(0, −own_score_delta).
- O4 group-DRO + protection: per-family EMA (decay 0.99) of mean reward; each episode's
  loss weight = softmax over families of (−EMA/10) evaluated for its family; plus O3's
  protection term.
- Training maps: seeds **9,850,000–9,850,255** (fresh; before lock, grep both ledger
  volumes for any overlap of `9,85` ranges and verify sealed ranges 9,844,200–215 and
  the official-map holdout are untouched — abort on any overlap).
- Budget per fit: 32,768 decision-transitions (≈4k games; decisions are sparse). Stage-A
  sanity stop at 8,192: finite losses, every option ≥ 2% of sampled decisions, crop
  safety exact, else that fit stops as mechanics-fail. Two seeds per objective = 8 fits,
  one deterministic training thread each (byte-reproducibility law).

## Phase 2 — admission and selection (out-of-fit only)

- Selection blocks: seeds **9,851,000–9,851,127** as eight independent 16-map blocks.
  Leave-one-block-out evaluation for every fit.
- Admission per fit (ALL required): LOBO pooled mean ≥ +1.5; worst held block ≥ 0;
  worst family mean ≥ −1; mean own-score delta ≥ −0.5; crop/workforce safety exact;
  catastrophes ≤ control.
- Selection among admitted fits: max worst-held-block → tie: max pooled mean → tie:
  lowest seed. Fit-side statistics are forbidden as selectors (D131/D134).
- **Kill (backlog rule):** no fit admitted → the closed-loop program CLOSES. Record in
  CONSTRAINTS/ledger/STATE; hold at Tier 0/3. No rescue, no budget extension.

## Phase 3 — veto and confirmation (one attempt each, no substitution)

- Veto (consumed 1,024 panel, veto-only — never trained or selected on): mean ≥ +1.0;
  no family < −2; catastrophes ≤ control; negative mass ≤ control. Fail → CLOSE (no
  substituting another admitted fit — that would be selection on the veto).
- Confirmation (sealed fresh block **9,852,000–9,852,063**, opened exactly once, single
  run): mean ≥ **+2.0**; clustered 95% CI floor > 0; all families ≥ −1; catastrophes ≤
  control; negative mass ≤ 1.1 × control. Fail → CLOSE.

## Phase 4 — deployability (only after confirmation passes)

int8 + persistent-buffer port per the K2/V5 pattern: ≥ 99% action agreement with the f32
policy on ≥ 512 held decisions plus a margin-neutrality spot check; warm decision p95 ≤
20 ms (hard budget 50); combined single-file source ≤ 100,000 bytes (resident slim is
62,725). Then **STOP — candidate construction and any arena action require explicit user
authorization** under the B4.1 promotion protocol. Leave the STOP marker in STATE §4.

## Prohibitions

No training or selection on the consumed 1,024 panel (veto-only); no fitting to D169
envelope winners (D100b); no GPU in any selected path (parity law); no fresh-range
expansion beyond the three declared ranges; no threshold/λ/τ/cap/architecture tuning
after outcomes; no second confirmation run; frozen modules untouched.

## Outputs (house convention)

`d170a-family-robust-option-policy-{lock,result}*` (+ per-phase result sections or files);
runner(s) `rust/src/bin/d170a_*` extending D169's env; trainer
`cgauto/train_d170a_family_robust_option_policy.py` (+ analyzer); bulk rows and
checkpoints on external `artifacts/experiments/d170a-family-robust-option-policy/`
(checkpoints are bulk — external root, never git). Ledger entry per phase; result doc
ends with explicit per-gate verdicts and the phase decision tree outcome.

## Decision tree (pre-adjudicated; executors follow, do not improvise)

- Phase 1 mechanics-fail on all fits → CLOSE (record; Tier 0/3).
- Phase 2 no admission → CLOSE. Admission → Phase 3.
- Phase 3 veto or confirmation fail → CLOSE. Pass → Phase 4.
- Phase 4 pass → STOP for user (arena authorization decision). Any deployability gate
  fail → record; the policy remains a validated research result; STOP for Fable review
  (a port problem is repairable engineering, not a science failure — but the repair gets
  its own protocol).
