# Independent initial-state sector policy audit

- Task: `20260802-initial-state-sector-policy-audit`
- Agent: `chatgpt_1`
- Date: 2026-08-02 UTC
- Branch: `agent/chatgpt_1-top-player-full-review`
- Task base: `43d8aa21008427edc58517968364496d3696ea82`
- Owner release boundary: the task was queued in the shared record; after completion of my
  preceding cross-review, the owner directly instructed me in this conversation to get and
  perform the task. I treated that as release for `chatgpt_1` only and did not read peer work.
- Platform mutation: none.

## Verdict

**`SECTOR_PREFLIGHT_CANDIDATE`, narrowly and only for E7a.**

The only scientifically distinct initial-state sector route I can identify is the exact
binary E7 `typeToCut` intervention: retain the resident default or flip its persistent
LEMON/PLUM choice. E7 already supplies the necessary kind of causal label — paired terminal
value for one finite change — and its compact record reports a seed-level hindsight residual
of `+10.5097`, with FLIP preferred on `24/60` roots and positive leave-one-opponent-family-out
results in `6/6` evaluations. The blanket FLIP arm is strongly negative (`-12.1736`), so a
sector-conditioned arm must beat **both** unchanged and always-FLIP; this is exactly the
interaction the owner asks about.

This is not a positive sector result. No sector has been identified, no model has been fit,
and no experiment is authorized. Before any fit, a provenance gate must establish that a
tracked compact E7 artifact contains root-level paired deltas. If the repository retains only
the aggregate `24/60` summary, the current-data verdict degrades to
`UNIDENTIFIABLE_FROM_EXISTING_DATA`; consumed ranges must not be reopened.

The motivating example “rich initial state -> collect a training bill and train a third
harvest/carry/chop worker” is **`UNIDENTIFIABLE_FROM_EXISTING_DATA` and not distinct**. It
collides with the failed generic map-to-workforce selectors, closed funding ladders, the
failed A2-1 scheduler, and the H11 ban on turning a richness predictor into a policy without
paired incremental value.

## 1. Evidence boundary

I used only the task-authorized tracked summaries and compact records routed by:

- `docs/STATE.md`;
- `docs/CONSTRAINTS.md`;
- `docs/BACKLOG.md`;
- `docs/APPROACH-REGISTER-2026-07-30.md`;
- `docs/archive/INDEX.md`;
- the task record itself.

I did not open raw games, USB or bulk storage, Git LFS objects, sealed or official holdouts,
consumed map ranges, frozen ledgers for archaeology, source files, or peer sector reports. I
did not implement an analyzer, exporter, runner, build, simulation, fit, candidate,
TestSession, or Arena action.

## 2. Closure map and the narrow distinct question

| Prior result | Binding fact | Consequence for this audit |
|---|---|---|
| D63/D64 | static map/opening features fell from discovery AUC `0.830` to validation `0.479`; later scaling state predicts behavior, not intervention value | no generic “richness” classifier and no fitting observed workforce or score |
| D64 value check | scale/suppress hindsight route gained only `+1.904` on `10/114` tasks | later scale correlation is not a causal instruction |
| Phase 15 | best map-only worker-three selector reached `47.059%` precision and `-0.277` held margin | no third-worker selector with the same target/representation |
| D91 | factory selector supported only `5/16` maps and selected an already harmful factory | no initial factory/economy selector |
| H11 | generic map-conditioned configuration decomposed and closed | a survivor needs one exact non-closed intervention, a new representation, paired value, grouped transfer, and best-static comparison |
| H1 / D174a / D175a | economy, mining and planting gains disappear after displacement/opponent leakage | no “rich map makes a closed graft good” argument |
| A2-1 | full new scheduler fell from `40.23%` development to `28.42%` locked worker-three completion versus a `40%` gate | no threshold/spec/catalog/mining retune and no sector rescue of the consumed scheduler |
| D52-D59 / H8 | hand funding ladders and generic TRAIN timing are closed | no initial-bank rule that merely retimes or reserves the same bill |
| E7 | exact persistent LEMON/PLUM flip: blanket `-12.1736`; root hindsight `+10.5097`; `24/60` roots prefer FLIP; `6/6` leave-family-out positive | one finite intervention with real paired heterogeneous value; E7a remains the named map-conditioned child |

The scientifically distinct question is therefore not:

> Can initial state predict score, opponent strength, or eventual scaling?

It is:

> Can an intervention-specific, player-relative t0 representation predict the sign of the
> exact E7 paired delta on held map roots, and can the resulting sector-conditioned arm beat
> the better of unchanged and always-FLIP prospectively?

That is narrower than H11, does not reopen worker-three selection, and has a falsifiable
three-arm comparison.

## 3. Outcome-blind, player-relative initial feature vector

The board is canonicalized before feature construction: reflect/rotate so the resident shack
and first worker occupy a fixed orientation. Seat is retained only for audit stratification,
never as a selector feature. Opponent-family identity is never a feature.

### 3.1 Joint starting bank

Use the exact visible t0 inventories, in referee order:

```text
self_bank = [PLUM, LEMON, APPLE, BANANA, IRON, WOOD]
opp_bank  = [PLUM, LEMON, APPLE, BANANA, IRON, WOOD]
```

Include raw counts, fruit total, iron, and self-minus-opponent differences. The project found
that each player receives a per-game random starting bank of roughly 24 fruit and 6 iron;
this is legitimate pre-command state, not a richness proxy inferred from outcomes.

For control only, compute the resident's deterministic t0 second-worker bill if it is already
fully determined from t0 state. Include the nonnegative deficit vector
`max(bill - self_bank, 0)`. If that bill depends on future state, omit it; do not reconstruct
it from later commands.

### 3.2 Static board geometry

Use only facts present before the first command:

- width, height, passable-cell count and water fraction;
- resident and opponent shack cells after canonicalization;
- initial worker position and visible capabilities; drop constant fields;
- initial live tree/plant cells, species, health, ripe fruit and other t0 attributes explicitly
  present in the initial state;
- mine/water/resource-cell locations if they are part of the initial visible map.

Generic size/count features are audit controls, not the claimed new representation.

### 3.3 Intervention-specific species-flow features

For each of the two E7 species, PLUM and LEMON, compute the same fixed t0 summaries:

- tree count, total health, total ripe fruit and health quantiles;
- resident minimum/median ETA and ETA-weighted health from the initial worker;
- opponent minimum/median ETA and ETA-weighted health;
- number and health of trees for which resident ETA is lower, equal, or higher than opponent
  ETA;
- nearest-cluster composition relative to both shacks;
- species-specific starting-bank deficit/surplus;
- deterministic score-component totals under the unchanged and flipped `typeToCut` choices,
  but only if those components can be computed from t0 facts without simulating commands.

The primary representation is the **FLIP-minus-default contrast**, not raw richness:

```text
delta_own_flow       = own_flow(FLIP species) - own_flow(DEFAULT species)
delta_opp_flow       = opp_flow(FLIP species) - opp_flow(DEFAULT species)
delta_controllability= own_controllable_health difference - opponent difference
delta_bill_alignment = t0 bill-deficit alignment difference
delta_score_surface  = t0 resident score-component difference
```

This is potentially distinct from D63/Phase 15 because it is a causal contrast tailored to
one exact intervention rather than a generic map embedding. That novelty is not assumed: the
first preflight gate compares the proposed columns with the published D63/Phase-15/D91
feature manifests. If they are the same fields or deterministic transforms, stop with
`NO_DISTINCT_SECTOR`.

Forbidden features include terminal score, outcome, duration, later workforce, later bank,
opponent actions, contact, harvested value, learned opponent identity, or any statistic
computed after the first command.

## 4. Existing paired counterfactual evidence

### 4.1 Usable positive-heterogeneity evidence

**E7 exact `typeToCut` FLIP versus unchanged.**

- finite intervention: persistent LEMON<->PLUM flip, with no scoring/grid/threshold bundle;
- compact population: 360 reused seed/opponent cells spanning both seats and six opponent
  families;
- global result: `-12.1736` paired margin, negative in both seats and all six families;
- root-level hindsight summary: `+10.5097`, FLIP on `24/60` roots;
- opponent sensitivity: positive in `6/6` leave-one-family-out evaluations.

This evidence demonstrates heterogeneity and supplies a best-static control. It does not
supply a deployable selector. The `24/60` hindsight choice is post-label and may be optimistic.

**Provenance gate:** a future preflight may use only a tracked compact table/manifest with
root ID and paired C0/A1 outcomes. If no such compact root table exists, the aggregate report
cannot label a sector and the current-data question is unidentifiable. Do not retrieve the
consumed simulation range.

### 4.2 Negative or non-distinct paired evidence

- **E4 mother-tie reversal:** active on all ten tied seeds, both seats and all six families;
  `-8.55` conditional and `-0.0855` exact-census-weighted, with every seat/family negative.
  It is closed and offers no positive sector prior.
- **E5 ripeness-wait removal:** activates in `33/360`, gains only `+0.1056`, seat 0 is
  negative, and `346/360` are unchanged. It is dynamic, sub-material, and closed.
- **N6 denial scalar:** exact 450/900/1800 sweep; HIGH `+0.559` but only four positive
  families and `12/77` directional events; LOW `-0.754`. The scalar and ranges are consumed.
- **D63/D64 and Phase 15 workforce choice:** map-only selector transfer failed; these labels
  cannot be repurposed for the owner example.
- **D91 factory choice:** low map support and harmful underlying intervention.
- **A2-1:** paired full-scheduler evidence exists, but the intervention is a whole new
  architecture, failed its locked K1, and is not a finite H11a arm.
- **H3a:** exact source transformation exists, but no conditioned arm or value runner exists;
  it has no initial-sector paired value label.
- **B3.14/B3.15:** incident corrections and short monitoring, without current-sector paired
  evidence.

### 4.3 Owner example: early bill plus worker three

No compact paired table isolates a finite rule of the form:

```text
on sector S: collect exact bill B earlier, then TRAIN exact worker W
```

against both unchanged and the identical rule always on. Existing evidence either changes a
whole scheduler (A2-1), retunes closed funding/TRAIN logic, or predicts later behavior. The
example is therefore `UNIDENTIFIABLE_FROM_EXISTING_DATA`, not a candidate for fitting.

## 5. Exact finite behavior changes considered

### 1. E7 persistent `typeToCut` LEMON/PLUM flip — survives

Use the exact already-tested binary intervention. No new species, score weight, distance,
opening prefix, persistence rule, or threshold. This is the only ranked survivor.

### 2. Third-worker bill collection/training rule — rejected

Not distinct from D63/D64, Phase 15, D52-D59, H8, H1 or A2-1, and no paired finite label
exists. Starting-bank conditioning does not reopen it.

### 3. Generic “rich-sector” economy/production arm — rejected

A production, mining, planting or factory arm selected by t0 richness is the closed H11/D91
pattern. Displacement and opponent leakage are not removed by conditioning.

No third positive candidate is added merely to fill the allowance.

## 6. Smallest read-only E7a preflight

This is a future separately authorized audit, not work performed here.

### P0 — provenance and novelty, zero fitting

1. Locate the compact E7 result/manifest through the live index.
2. Verify exact C0/A1 source identities, root IDs, both seats, opponent blocks, terminal
   outcomes and hashes.
3. Require one paired delta per map root after averaging only within that root across the
   frozen seat/opponent block. Opponent families remain blocking variables, not map labels.
4. Compare every proposed feature with D63/Phase-15/D91 feature manifests.
5. Stop if the root-level paired table is absent, any label comes from observed resident
   outcomes rather than C0/A1 counterfactuals, or the representation is not materially new.

### P1 — fixed representation check on consumed E7 development evidence

The consumed E7 evidence may price representation feasibility only; it cannot qualify a
candidate or choose final thresholds.

- response: root-level paired delta `A1 - C0`;
- groups: 60 map roots; no row-level split;
- model: one preregistered ridge-linear score on the fixed contrast features, with fixed
  regularization and sign threshold zero; no model family, depth, feature or threshold sweep;
- baselines: best static arm, intercept-only sign, and permutation-by-root;
- validation: nested root-grouped folds; every root and both seats stay in one fold;
- opponent sensitivity: leave one opponent family out of the root aggregation, refit on the
  other families, and score the held family without using its identity as a feature;
- minimum sector support: at least `12/60` and at most `48/60` roots overall, at least four
  held roots per outer fold, both seats represented, and no single opponent family supplies
  the sign;
- representation gate: held-root sign precision >= `65%`, mean selected-arm regret at most
  `35%` of the root hindsight oracle, and sector-conditioned replayed value above the better
  static arm with root-cluster 95% lower bound above zero;
- stop on seat reversal, family reversal in more than two of six sensitivities, support
  collapse, permutation-equivalent performance, or feature overlap with a closure.

Passing P1 means only `REPRESENTATION_PREFLIGHT_PASSED`. Because the labels are consumed, it
does not authorize source work or a fresh value panel.

## 7. Frozen prospective three-arm protocol

A new task must allocate fresh **unsealed** official-map roots. The existing official holdout,
sealed confirmation blocks and all consumed ranges remain untouched.

### Arms

- `C0`: exact unchanged resident `typeToCut` behavior.
- `A1`: exact E7 LEMON/PLUM FLIP always on.
- `C1`: byte-identical to C0 outside the frozen t0 sector and byte-identical to A1 inside it.

The sector decision is made once from t0 state and is immutable for the game. A bridge test
must prove C1 command/source semantics select exactly one of C0/A1 and introduce no third
behavior.

### Root and opponent design

- discovery: 128 fresh roots;
- locked validation: 128 disjoint fresh roots;
- untouched confirmation: 64 further fresh roots, allocated before discovery and never read
  until validation passes;
- both seats for every root/opponent/arm;
- at least eight opponent policies or exact versions: six development/sensitivity blocks and
  two completely held opponent policies for validation/confirmation;
- same map, seat, opponent and referee randomness paired across all three arms;
- root is the inferential and bootstrap cluster.

Exact IDs/ranges must be assigned by the integrator in a future protocol; this audit does not
name or consume them.

### Selector freezing

Fit the single preregistered selector on discovery only. Freeze feature code, normalization,
coefficients, threshold zero, sector support expectation, source hashes and arm hashes before
opening validation. No threshold repair, map-class relabeling, family-specific branch, or
post-validation feature deletion.

### Best-static and conditioning contrasts

On discovery, identify the better static arm `B = max(C0, A1)` by root-cluster mean, then
freeze that identity. Validation must report:

```text
C1 - C0        policy value versus resident
C1 - A1        load-bearing value of conditioning
C1 - B         value versus the best static choice
A1 - C0        static intervention effect
```

C1 does not qualify by merely avoiding A1's global loss; it must beat the best static arm.

### Pass gates

All must pass on locked validation:

1. sector support between 20% and 80%, at least 24 validation roots in-sector;
2. `mean(C1 - B) >= +5.0` terminal margin per root/opponent/seat task;
3. root-cluster bootstrap 95% lower bound for `C1 - B` > 0;
4. `C1 - C0 > 0` and `C1 - A1 > 0` with root-cluster lower bounds > 0;
5. both seat means nonnegative;
6. at least six of eight opponent-policy means nonnegative, both held policies nonnegative,
   worst opponent mean >= -2;
7. catastrophes do not increase; negative-margin mass <= C0; no runtime/validity failures;
8. own-score and opponent-score deltas reported separately;
9. displacement ledger reports changed MOVE/CHOP/HARVEST/PLANT/TRAIN/WAIT turns and the
   terminal value of displaced resident work; no gross-resource-only valuation;
10. result remains positive after root weighting and after removing each one opponent block.

The `+5` gate is terminal-margin materiality, not Arena rating. No wins/margin-to-rating
conversion is allowed.

### Confirmation and stop rule

Open the untouched 64-root confirmation only after every validation gate passes. No refit.
Confirmation requires the same signs, sector support >= 20%, both seats/held opponents
nonnegative, no tail regression, and root-cluster lower bound above zero. Any failure closes
the representation/intervention pair without threshold or feature retuning on those ranges.

Immediate stop conditions:

- no compact root-level E7 labels;
- feature equivalence to D63/Phase15/D91;
- selected sector below support;
- best-static baseline not beaten;
- seat or held-opponent reversal;
- gain disappears under root grouping or opponent leave-one-out;
- displacement or opponent leakage explains the gross gain;
- any sealed/consumed provenance violation.

## 8. Ranked rationale

1. **E7a intervention-specific initial sector — `SECTOR_PREFLIGHT_CANDIDATE`.**
   Exact finite arm, real paired heterogeneity, outcome-blind t0 representation possible,
   and explicit best-static three-arm falsification. Current blocker: compact root-level
   label and feature-novelty provenance; no sector result yet.
2. **Initial-bank/rich-map worker-three rule — `UNIDENTIFIABLE_FROM_EXISTING_DATA`.**
   No finite paired value label; overlaps multiple closed branches and a failed architecture.
3. **Generic rich-sector economy configuration — `NO_DISTINCT_SECTOR`.**
   This is H11/D91/H1/A2-1 under a new name.

## 9. Final disposition

The owner hypothesis is worth one narrow preflight, but not in its worker-three example form.
The project already has exactly one finite initial decision with demonstrated map-root
heterogeneity: E7 `typeToCut`. Preserve the causal question by comparing unchanged,
always-FLIP and sector-FLIP, and preserve scientific validity by beating the better static
arm on fresh grouped roots.

Nothing in this report authorizes source implementation, a runner, a fit, fresh ranges,
confirmation access, a candidate, TestSession, or Arena action.
