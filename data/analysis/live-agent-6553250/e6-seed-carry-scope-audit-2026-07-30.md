# E6 seed-carry decision scope audit

Date: 2026-07-30

Verdict: **`VOID_PREMISE_DUPLICATE`**

## Premise check

The register says seed-carry decisions—“which seed to carry and when to drop it”—were
never examined as a class. That is false.

There is also a mechanic correction: `PLANT` consumes a carried fruit as a seed. `DROP`
deposits carried items at the shack for score/inventory; it is not a selective
seed-discard action. Seed-specific decisions are acquisition (`HARVEST` or bank `PICK`),
pre-carry timing, species, destination, and `PLANT`. Generic return/drop routing is already
covered by E2.

## Existing coverage

### Acquisition path

D167 classifies every exact-resident successor return. All **135/135** local natural
returns use `BANK_SEED` (deposited seed → `PICK` → walk → `PLANT`). Ninety-six returning
workers lack harvest power, making bank acquisition mechanically necessary in 71%.

Field top-agent returns were initially 15/21 BANK_SEED; B3.3 re-powered the population
estimate to **67.5%**. Field pre-carry is **40.5%** while the resident is **0/1,024**.
Those are descriptive motifs, not value claims.

### Timing, species, and displacement

D168 implements both bounded timings over exact resident continuation:

- ARM_A picks after suppression and returns to plant;
- ARM_B pre-fetches before suppression, returns to chop, then plants.

Both choose the largest deposited fruit stock at the moment of `PICK`, with frozen
`BANANA > APPLE > PLUM > LEMON` ties, dynamically revalidate the bank and destination,
and cover both seats and seven of eight opponents. The exact same 164/1,024 tasks activate
for both arms; resident carry is empty at every entry.

Terminal displacement is decisive:

- post-return: **−6.732** paired margin, CI [−8.398,−4.077], own −3.610, worst family
  −17.111;
- pre-carry: **−8.207**, CI [−10.528,−5.709], own −3.951, worst −15.556.

All seven active family means are negative for both arms. Even committed ARM_A episodes
average −7.22. ARM_B invalidates the intended suppression target in 56/164 activations.
D168 explicitly closes horizons, arming conditions, and species-order retuning: forcing
the motif loses because value is in endogenous timing, not the hand-written action.

### Other seed work

Renewable mother/crop variants are closed; the timing-only pre-seed change was separately
measured at +0.259 over reused seeds 0..999 and is already in the promoted stack.
Seed-factory and late bridge work validates production but fails funding/value. These
records reinforce that “seed carry” is not one missing scalar rule.

## Adjudication

Existing work covers acquisition class, pre/post timing, species selection, destination,
terminal continuation, displacement, both seats, opponent breadth, and negative tails.
The only surviving statement—endogenous timing may matter—was assigned to the
rollout-valued semantic-option interface, not another fixed seed heuristic.

Therefore E6 is **`VOID_PREMISE_DUPLICATE`**. Do not create another species order,
pre-carry horizon, drop rule, bank-return wrapper, simulator panel, source variant,
candidate, or Arena cycle.
