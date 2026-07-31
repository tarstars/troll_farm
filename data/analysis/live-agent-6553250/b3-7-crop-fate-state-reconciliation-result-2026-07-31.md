# B3.7 crop-fate census — live-state reconciliation

Date: 2026-07-31
Verdict: **`ALREADY_COMPLETE_CONVERSION_BY_DESIGN`**

## Why this reconciliation exists

The full-corpus B3.7 audit completed on 2026-07-29 and is preserved in ledger volume 2,
but the live backlog still called it `IN FLIGHT`. This record corrects live state; it does
not rerun the analyzer or create a new empirical claim.

## Exact measured populations

Resident: 220 games and 2,433 crops.

- 98.97% were chopped by the resident;
- 0.90% were harvested by the resident, matching D101's 0.94%;
- 0.12% were taken by the opponent;
- 0% remained alive at game end;
- 96.8% of self-chopped crops never bore fruit before conversion.

Top-five cohort: 200 games and 8,913 crops.

- 29.81% were harvested by the owner;
- 42.98% were self-chopped;
- 15.71% were chopped by the opponent;
- 11.28% remained alive at game end.

The selected top-five fate percentages are reported exactly as the completed audit did;
they are not forced to exhaust an independently reclassified 100%.

## Capability and servicing

Resident live crops per harvest-capable worker remain near zero, rising only 0.08→0.40
from turns 25→300, versus roughly 2.5–3.0 for the top five. Every one of 220 observed
resident trained workers has `harvest_power = 0`, versus 9.5% of the top cohort.

When resident ripe fruit goes unserviced, a capable worker is in reach 87.4% of the time
(73.2% excluding the orchard-mother reserve), yet only 41 true residual episodes remain,
with median duration two turns. The top five have 3,922 such episodes at median 19 turns
and 1,010 crops still ripening at game end; the resident has one. True resident capacity
waste is about 1.6%.

## Interpretation and boundary

The resident is not racing its own orchard and is not harvest-capacity-limited. It has
architecturally chosen crop-to-wood conversion: only one designated mother tree is treated
as a recurring fruit source, while almost every other crop is wood inventory.

Theft exists but is secondary: opponent wood share on contested resident self-chopped
trees is 18.2%, or 2.60 wood per resident game. The plant-pacing hypothesis describes the
top-five cohort's mixed orchard; it does not apply to the current resident and does not
justify a pacing rule. This fate-level conclusion corroborates D175a's causal factory
closure.

No planting rule, harvest-capability change, orchard redesign, analyzer rerun, source edit,
bulk access, panel, candidate, or Arena action follows.
