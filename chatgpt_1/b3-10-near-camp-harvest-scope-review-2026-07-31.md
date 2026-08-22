# Independent review — B3.10 near-camp harvest scope

- Reviewer: `chatgpt_1`
- Task: `20260731-b3-10-near-camp-harvest-scope`
- Reviewed coordinator head: `75ebdb157d1935c6cbe255e43b12faa87d25ec32`
- Review date: 2026-07-31
- Verdict: **`CLOSED_BY_EXISTING_VALUE_AND_ROBUSTNESS_EVIDENCE`**

## Decision

Accept the proposed closure without a result correction.

The compact result correctly treats B3.8 as a stock-accounting ceiling, not as a feasible
action oracle. Its count semantics, arithmetic, D173 gate values, D174a boundary, and
closure wording all reconcile with the frozen evidence. No exact untested intervention
remains inside B3.10's direct-fruit-only scope.

## 1. Individual-fruit-unit semantics

`cgauto/training_currency_audit.py` tracks a FIFO queue of individual fruit-ripening
units over each plant lifetime. A unit enters the audit once, only when it was never
harvested by the resident and an own unit came within the frozen BFS-3 reach condition
before removal. Resident-harvested units are removed from the queue and excluded.
Opponent-harvested, chop-destroyed, and still-live units are finalized once with an exact
fate.

Therefore B3.8's observations are individual one-point fruit units, not turns, plant
snapshots, opportunities repeatedly counted over time, or full plants. The report's
statement that banking one such unit adds one own score point is consistent with the
resident score definition.

## 2. Count reconciliation

The frozen B3.8 ledger entry and the audit source agree on these nested counts:

| population | units |
|---|---:|
| near camp, own-door BFS distance at most 2 | 1,144 |
| near camp and PLUM/LEMON/APPLE bill-relevant | 956 |
| near camp with optimistic walking detour at most 2 | 496 |
| preceding subset and PLUM/LEMON/APPLE bill-relevant | 425 |

The compact result correctly distinguishes 496 total direct-score units from 425
bill-relevant units. The latter is not the direct-score ceiling used in this review.

The 71.8% quantity is also correctly limited to a scope classification: those events are
outside the lifetime chop-dominant subset used to cross-tabulate D173b-adjacent geometry.
It does not establish that a safe command exists or that D173b would causally recover the
remaining events.

## 3. Direct-value arithmetic

Across 205 resident games:

- all-credit own-score ceiling: `496 / 205 = 2.4195121951219513` per game;
- deliberately generous deny-plus-capture ceiling:
  `2 * 496 / 205 = 4.839024390243903` margin per game;
- headroom to the frozen 20-margin opportunity reference:
  `4.839024390243903 - 20 = -15.160975609756097`.

The factor-two construction is a valid upper bound for the direct fruit stock: it gives
one point to the resident and simultaneously removes one point from the opponent for
every unit, even though many audited units were not destined to become opponent score.
It is intentionally more generous than the evidence.

The source's “detour” is only
`BFS(unit at first reachable turn -> fruit cell) + BFS(fruit cell -> own door)`. It omits
the mandatory `HARVEST` and `DROP` action turns and credits the fruit at first reach. The
human result states these omissions and therefore does not misrepresent the 496 units as
feasibly collectible.

## 4. Existing intervention evidence

The D173 values in the compact result match the frozen results:

| arm | overall mean | compact_gold | catastrophes | control catastrophes | negative-mass ratio |
|---|---:|---:|---:|---:|---:|
| D173a | +2.93505859375 | -2.0625 | 54 | 49 | 1.0958506549533298 |
| D173b | +1.0625 | -1.390625 | 52 | 49 | 1.0811828378696369 |

Both variants also fail their mechanism gates. D173b's assignment-faithful repair removes
99.9% of the locally addressable harvest-capable subset, yet aggregate harvest slack,
door queue, and idle-with-work still worsen through displacement and downstream state
changes.

These arms are not an exact causal test of a new near-camp walking target, and the result
does not present them as one. They are appropriately used as corroborating evidence that
the B3.8 stock ceiling omits real family, tail, action, and scheduling costs. A walking
intervention would add costs that the gross 4.8390 ceiling already excludes.

## 5. Scaling rationale is correctly excluded

D174a verifies both boundaries relied on by the result:

- the resident has an unconditional workforce-two training cap before affordability;
- after repairing that cap and increasing iron acquisition 10.6-fold, worker 3 still
  appears in 0/2,048 tasks because the live `TUNED_CARRY` PLUM/LEMON bill is roughly
  double B3.8's synthetic cheap-helper bill and remains unmet in essentially every game.

B3.10 therefore cannot multiply its direct-fruit stock by a speculative worker-scaling
payoff. The report prices fruit only, as required.

## 6. Closure boundary

The accepted conclusion is narrow and defensible:

- close a direct near-camp fruit target, distance-threshold tuning, and worker-harvest
  capability proposal based on the old B3.8 count;
- do not interpret “outside D173b” as evidence of action value;
- do not reuse the synthetic-bill scaling story;
- do not open a successor panel from this audit.

The 4.8390 figure is not a causal estimate and is not a universal upper bound on every
possible production or harvest architecture. It is the deliberately generous direct-score
swing available from the frozen B3.8 event stock. The canonical report already preserves
that boundary.

## Validation performed

- Cross-read task, handoff, compact JSON, human result, and manifest.
- Cross-read the B3.8 ledger entry and the event/detour implementation in
  `cgauto/training_currency_audit.py`.
- Cross-read D173a, D173b, and D174a frozen result records.
- Recomputed all direct-value arithmetic exactly.
- Confirmed compact JSON and human wording agree on counts, bounds, gates, verdict, and
  prohibited continuation.

No analyzer, replay, map/range, bulk artifact, simulation, source edit, panel, candidate,
TestSession, submission, or Arena action was performed.
