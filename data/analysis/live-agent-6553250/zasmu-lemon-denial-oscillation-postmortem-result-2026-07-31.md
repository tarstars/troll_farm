# Zasmu lemon-denial and oscillation postmortem

Date: 2026-07-31
Game: `896352750`
Result: resident 206, zasmu 184
Verdict: **`NARROWED_TO_FEASIBILITY_PRECHECK`**

## Decision

The owner's economic diagnosis is right: this replay contains a renewable lemon source
that the resident's natural-tree sweep never suppresses. The current policy removes five
initial lemons, but zasmu's protected planted tree produces enough lemons to pay the next
training bill by itself and continues supplying the following bill.

That does not justify disabling LEMON chopping. The five removals also produce nine
resident wood, and the resident wins by 22. Denial and production value are entangled.
The defensible successor is therefore a read-only corpus precheck that asks whether the
*denial bonus*, separately from wood value, can possibly beat stock, regeneration, chop
burden, and bill timing.

The visible opening churn is also real but smaller than it looks under the frozen
detector: three short A-B-A returns through turn 100 and no sustained ≥10-state episode.
D176a already closed an effective fix for that class on value, so no oscillation change
follows.

## Integrity and geometry

The raw game and exact trajectory reconstruct 217 resolved turns with zero unknown
updates.

| artifact | SHA-256 |
|---|---|
| raw game | `c7209f23ad36bb9fa363a57cfd0152c71a7aea5a30fbf38c13c48aff3521a817` |
| exact trajectory | `a62b5b48aad1f4e5d2250f8ec7ef477f937001208aad72053ae11a27466e424d` |

Zasmu's shack is `(5,6)` and the resident's is `(14,3)`. The decisive planted lemon at
`(7,8)` is BFS 3 from a zasmu door and BFS 17 from a resident door. Zasmu's later replant
at `(5,7)` is an own door and BFS 14 from the resident.

## Opening oscillation: short returns, not the sustained class

Using the frozen position-only pattern—consecutive states where
`position[t] == position[t-2] != position[t-1]`—the resident has five A-B-A episodes in
the game, all on starter unit 1:

| resolved turns | cells | states | opening ≤100 |
|---|---|---:|---|
| 61–63 | `(5,8)` ↔ `(6,8)` | 3 | yes |
| 66–68 | `(5,7)` ↔ `(4,7)` | 3 | yes |
| 90–92 | `(12,5)` ↔ `(11,5)` | 3 | yes |
| 123–125 | `(15,2)` ↔ `(14,2)` | 3 | no |
| 153–156 | `(6,4)` ↔ `(7,4)` | 4 | no |

Thus the first 100 turns contain three backtracking return edges with no productive
action by that unit on the return. All MOVE commands land, and no teammate is adjacent
during those opening episode states. They are genuine short target/path reversals, but
the longest run is four states and the B3.2/D176a sustained threshold is ten.

This exact replay cannot assign counterfactual value to the three steps. D176a already
reduced sustained incidence to 2.88%, below yamo's 2.9%, with only +0.045 overall margin.
The oscillation line remains closed.

## Lemon stock and the actual clear burden

The map starts with six LEMON trees: total health 40, no fruit. By the state immediately
before the resident's first lemon chop (resolved turn 25), growth plus zasmu's turn-6
plant produce:

- seven standing LEMON trees;
- 84 total health;
- seven fruit already standing.

The resident then has chop powers 1 and 3. Even an impossible no-travel, continuously
productive clear needs `84 / (1+3) = 21` turns. Real geometry is much worse: the trees
span both sides of the map, and the protected planted tree is 17 BFS from the resident.

The resident first contacts a lemon on turn 26 and removes its fifth initial lemon on
turn 67—42 elapsed turns inclusive. It issues 28 lemon CHOP commands and deals 60 damage:

| initial cell | first chop | CHOP commands | removed | fruit destroyed | wood collected |
|---|---:|---:|---:|---:|---:|
| `(11,3)` | 28 | 4 × power 3 | 31 | 2 | 2 |
| `(8,6)` | 26 | 12 × power 1 | 37 | 3 | 1 |
| `(3,4)` | 40 | 4 × power 3 | 43 | 2 | 2 |
| `(16,5)` | 54 | 4 × power 3 | 57 | 3 | 2 |
| `(16,0)` | 64 | 4 × power 3 | 67 | 3 | 2 |

Direct totals are 13 fruit present at removal and nine resident wood collected. One
initial lemon at `(3,9)` remains for zasmu. At turn 67 two mature lemon trees still stand
with 24 health and six fruit: the natural survivor and zasmu's planted orchard. The
resident never achieves extinction; all lemons disappear only on turn 120, when zasmu
self-converts its own remaining supply after harvesting it.

The 13 fruit and nine wood are exact accounting, not counterfactual score effects.

## Zasmu's harvest-and-replant loop defeats the bill-denial objective

Zasmu plants `(7,8)` on turn 6 with a starting-endowment seed picked on turn 1. It first
harvests on turn 26—the same turn as the resident's first lemon chop—and harvests it 19
times through turn 95. The resident never chops it. Gross reproduction is 19 from one
seed, or +18 before conversion.

The remaining natural lemon at `(3,9)` supplies six more harvests. On turn 97, zasmu unit
2 carries two lemons harvested there on turns 93–94 and spends one to plant `(5,7)`.
That second plant is later converted before ripening, but it proves the exact
harvest-to-replant transition the owner saw.

The resource provenance lines up exactly with scaling:

| TRAIN turn | resulting workers | lemon bill | bank before → after | provenance |
|---:|---:|---:|---|---|
| 2 | 2 | 5 | 6 → 1 | starting bank |
| 62 | 3 | 11 | 11 → 0 | 10 harvests from `(7,8)` + the one banked remainder |
| 106 | 4 | 12 | 14 → 2 | 15 later harvests − one harvested seed replanted |

After turn 2, zasmu harvests 25 lemons, spends 23 on the next two TRAIN bills and one on
the demonstrated replant, and still has two banked after reaching four workers.

So the current sweep succeeds mechanically—five trees die—but fails its presumed scaling
denial goal. It attacks finite natural stock while leaving a protected renewable source
that matures before the first chop and funds both later workers.

## What a feasibility precheck must ask

A read-only population audit may test a strict gate before any implementation:

1. How much target currency is already banked or carried?
2. What is the standing target-species health, and what is the lower-bound clear time
   after travel and available chop power?
3. How much can opponent harvest-capable labor collect and replant before that clear?
4. Does the opponent reach the next observable TRAIN bill before scarcity can occur?
5. After removing the `900/(1+distance)` denial bonus, does the tree remain worthwhile
   for its own wood/conversion value?

If the bill is already covered, or a protected replant matures before a feasible clear,
the precheck should classify the denial component as futile. It must not forbid a chop
that is independently good wood production.

This is distinct only as accounting. E7 forbids blanket LEMON↔PLUM inversion; N6 closes
retuning the denial-distance scalar; H4 forbids treating reachability as causal bill
control. No source edit, threshold, weight, focus flip, oscillation breaker, simulator,
runner, panel, candidate, submission, TestSession, or Arena action is authorized.
