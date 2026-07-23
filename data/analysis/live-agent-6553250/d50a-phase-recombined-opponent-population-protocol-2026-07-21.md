# D50a phase-recombined opponent-population coverage — frozen protocol (2026-07-21)

## Question

The old eight-model zoo, 31 Gold configurations, 11 structural controllers, and both eight-member
Legend proxy catalogs fail as individual universal field models. Their **union** nevertheless
macro-covers 51/80 held-out field games, including 4/19 catastrophic, 8/28 worker-rich, and 2/9
rich-immediate games. Rich-proxy residuals are small through turn 100 and then diverge by hundreds
of production points.

D50a tests a different abstraction: can a fixed population of phase-wise recombinations span the
missing late trajectories as a set? This is opponent-domain reconstruction on already consumed
exact Arena maps. It is not candidate evaluation, policy optimization, or evidence for promotion.

## Frozen component vocabulary

Use these eight already-defined deterministic controllers. Labels in parentheses identify their
exact historical audit anchors.

1. `v2_hp2_farm` (`legend_v2_hp2_cheap_farm`): producer `(2,2,2,1)`, chopper `(2,2,0,2)`, no
   late producer-to-chopper switch.
2. `v2_hp2_late` (`legend_v2_hp2_cheap_late_chop`): the same specs with the internal turn-150
   late-chop transition.
3. `v2_bal_farm` (`legend_v2_balanced_cheap_farm`): producer `(2,2,1,1)`, cheap chopper, no late
   transition.
4. `norx_compact` (`norx_compact`).
5. `farm3` (`farm3_hold0_cap20`): fixed three-worker Gold economy, one chopper, one planter,
   hold 0, cap 20.
6. `farm4` (`farm4_s30_hold120_cap24`): fixed four-worker Gold economy, two choppers, one planter,
   stagger 30, hold 120, cap 24.
7. `lean` (`lean_m1c2h0k2`): fixed two-worker lean Gold economy with `(1,2,0,2)` first spec.
8. `norx_funded` (`norx_funded_silver`).

No component parameter may be changed after execution.

## Frozen population

Construct exactly 120 policies:

- eight unchanged anchors, one for each component; and
- for every ordered pair of **different** components, switch once from the early component to the
  late component either after turn 100 or after turn 150: `8 * 7 * 2 = 112` policies.

The late component is instantiated when the game starts but receives decisions only after the
cut. It therefore begins from the actual interactive state with its own empty controller memory;
this is part of the frozen policy definition. The early component supplies the exact opening.
No per-game model selection, observed opponent identity, replay command, future state, randomness,
or outcome feedback enters a policy.

## Data and execution

Run exact `b100_e6` as local player 0 against all 120 policies on the same 160 consumed Phase-21
initial states. Use the corrected absorbing terminal/stall semantics and the unchanged turn-50,
turn-100, final, opening, and terminal instrumentation in `field_continuation_audit`.

Run the entire 19,200-cell matrix twice with the same thread count and require byte identity. The
input evidence is frozen by SHA-256:

- observed field signatures:
  `c94e3a188913b45c853242bb6a83e5d07f5726dea6c866a1cb1130450d5ae9bc`;
- exact map dataset:
  `d7e4419fad0594673c795e01b6db9b758d646b9b865f612910513f47ddc18ff0`;
- legacy baseline/economy/structural/v1/v2 matrices:
  `dc1f4f9221a091931aa3e7f4186f3c82ad474a00cb11792c3532fbf92fdb8e76`,
  `a1dc43771ea9f87802061c7886688293d55e73e25f9c7a52cf7153bf0f36cf25`,
  `518d2c592d6f0248e58950642011f64b7b3ffd15a34b53b93566abc6ea603283`,
  `3589dc34dc887290810a182d782d6cff828ff36902722658c6b49f2ed26dcae6`, and
  `c181438efdb03aa5e57856ce55d08e3c98fbfa8929152edc847a77bd1e4f3c96`.

Keep the existing SHA partition. Do not use discovery outcomes to alter the catalog or gates.

## Integrity and activation gates

D50a passes mechanics only if:

1. both grids contain exactly 160 x 120 unique cells, have the expected labels, contain every
   checkpoint, and are byte-identical;
2. all eight anchor trajectories exactly match their corresponding historical rows after mapping
   only the model label;
3. every switch preserves its early anchor's exact first command; and
4. at least 40% of the 17,920 switch cells have a complete terminal/checkpoint signature different
   from the corresponding early anchor, and at least 80/112 switch policies activate on at least
   10% of maps.

## Held-out population-support gates

Score each phase policy with the already-frozen `field_continuation_coverage` tolerances. Coverage
means that **some** member of the fixed population covers the observed game; it does not select a
single proxy. Compare the union of legacy and phase policies on the 80 confirmation games.

The legacy confirmation union is fixed at:

| Cohort | Games | Macro | Full |
|---|---:|---:|---:|
| Overall | 80 | 51 | 33 |
| Catastrophic | 19 | 4 | 2 |
| Worker-rich | 28 | 8 | 3 |
| Rich immediate | 9 | 2 | 0 |

Pass only if the augmented union reaches all of:

1. overall macro coverage at least 56/80 and full coverage at least 36/80;
2. catastrophic macro coverage at least 7/19;
3. worker-rich macro coverage at least 12/28;
4. rich-immediate macro coverage at least 4/9 and full coverage at least 1/9; and
5. no previously covered confirmation game is lost (the union calculation should make this an
   invariant, checked explicitly).

Also report discovery and confirmation nearest-distance changes, covering-policy multiplicity,
coverage by named opponent, and which phase/cut combinations add each newly covered critical game.

## Decision rule

- **Pass:** retain the complete frozen population as a field-domain ambiguity set and open a
  separately preregistered fresh-map robust complete-policy search. D50a itself cannot select or
  qualify a submission.
- **Fail with broad activation:** close fixed phase recombination. The next opponent model must be
  state/history-conditioned or procedurally generated inside the scheduler rather than switched
  between complete hand-written controllers.
- **Fail activation/integrity:** repair only the experiment machinery under a new amendment; do
  not inspect or reuse value/support conclusions from an invalid matrix.

No fresh map, TestSession game, candidate, source-size gate, submission, Arena action, or resident
change is authorized.
