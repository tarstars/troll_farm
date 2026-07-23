# D78a opponent-commitment observability result (2026-07-21)

## Verdict

**Spatial snapshot passes; additional six-turn history fails its incremental gate.** Current-field
opponent commitment is materially more observable when the controller sees the concrete crop,
worker-to-target distances, and local occupancy. The next controller representation should be a
memoryless context-complete target/job scorer, not another recurrent four-mode controller.

This is behavior-transfer evidence, not counterfactual value. It does not create a candidate or
authorize confirmation, TestSession, submission, or Arena activity.

## Corpus and integrity

D78 reads only the open products of immutable snapshot `20260721T105508Z-d61p`:

| Measure | Result |
|---|---:|
| Open resident games | 165 |
| Resident-only crops | 1,811 |
| Deterministically retained crop-turn rows | 5,589 |
| Discovery rows / positive | 2,711 / 359 |
| Validation rows / positive | 2,878 / 640 |
| Discovery / validation opponent accounts | 26 / 20 |
| Positive-support accounts | 17 / 14 |
| Unknown state updates / final mismatches | 0 / 0 |
| Confirmation products read | no |

All frozen volume, account-support, feature-finiteness, fit-convergence, trajectory, and row-identity
gates pass.

## Held-opponent result

All models are fit only on discovery accounts and evaluated on disjoint opponent accounts.

| Observation | Features | Validation AUC | Brier | Balanced accuracy | Top-20% precision | Lift |
|---|---:|---:|---:|---:|---:|---:|
| Aggregate D71-like state | 51 | 0.8700 | 0.1515 | 0.5000 | 64.76% | 2.912x |
| Spatial target snapshot | 83 | **0.9307** | **0.1146** | 0.6246 | **75.17%** | **3.380x** |
| Spatial + six-turn history | 124 | 0.9331 | 0.1094 | 0.6692 | 75.00% | 3.373x |

Spatial snapshot adds **+0.0607 AUC** and improves Brier by **0.0370**, passing every frozen spatial
gate. Its strongest coefficients are current attacker proximity and occupancy: within one/two/four
steps, on-target presence, and nearest distance. This is exactly the information absent from
D71's aggregate mode observation.

History improves AUC by only **+0.00237** over spatial, far below the required +0.03. It improves
calibration and three history fields enter the top ten coefficients, but it does not improve
top-quintile precision or recall. Current geometry already contains almost all transferable attack
signal; recurrence is not justified for this purpose.

## Attribution adjudication

An initial post-run audit incorrectly reported only 577 of 834 target CHOPs as confirmed because
the shared `successful_events()` helper recognizes `damaged a tree` but omits the referee's
successful fell message, `collected N WOOD`. D78b independently parses both messages, binds each to
the same unit's assigned CHOP and pre-action cell, and finds:

- attempted target CHOPs: **834**;
- referee-confirmed target CHOPs: **834**;
- filtered labels: **0**; and
- D78a/D78b row files: byte-identical SHA-256
  `44a39100011709f41e8cacef0e623a97d6731644fabc3390ebf27bb7692eb984`.

The one-process D78b repeat is also byte-identical. D78b's preregistered "repair must filter at
least one attempt" gate formally fails, correctly rejecting the repair premise. It does not
invalidate D78a: the independent event/unit/cell audit proves the original crop-specific labels
already satisfy D78a's referee-confirmation contract. Preserve D78b as a failed repair/negative
control rather than relabeling or rerunning D78a.

## Multilevel interpretation

1. **Field behavior:** imminent attacks are transferable across opponent accounts and strongly
   localized by current unit-to-crop geometry.
2. **Observation:** D71's aggregate inventories, crop counts, and lifecycle counters alias crops
   that face very different immediate pressure.
3. **Memory:** recent approach/damage history is useful for calibration but contributes almost no
   ranking information beyond the current snapshot.
4. **Action:** the controller must choose a concrete job/target. A global `fell`, `renew`, or
   `harvest` mode cannot express which crop is threatened or which worker should respond.
5. **Optimization:** D77 showed whole-game lineage search can retain active policies. Reuse that
   lesson only after changing to a spatial candidate action interface; do not tune D77 itself.

## Next experiment

Freeze a D40-anchored, memoryless spatial candidate/job scorer. Keep TRAIN, deficit funding,
evacuation, persistent execution, and transaction safety exact. At rate boundaries, score concrete
legal jobs from exact-prior rank plus current shared and target context. First require a random
population to be broadly active, crop/workforce safe, deterministic, and outcome-sensitive on
consumed mechanics maps. Only then may fresh whole-game optimization open.

## Artifacts

- protocol SHA-256:
  `5fd9a37026ad0c50d34f7ac9d5eab7cbf5bb36bb894762f7e74865743f705263`;
- D78a rows SHA-256:
  `44a39100011709f41e8cacef0e623a97d6731644fabc3390ebf27bb7692eb984`;
- D78a machine result SHA-256:
  `881415242123e32333338a387e07ad7b6dc0ba670faebf28c644ca9094b5a7b1`;
- D78b repair protocol SHA-256:
  `acebd559b723445371e7ac43684c50e692a62ffe3abba30dba0b8fd75e3490e7`;
- D78b first/repeat result SHA-256:
  `a76efe3cf99b01c86a1dbd51a62d640ac6cfead4c2511884a578eaab3cfe04d4` /
  `b849cd6a76fcd41d716ff4f705f42c77fe26ad462ead48690e8ad2c4ccd5f307`.
