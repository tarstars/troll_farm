# Frozen plan — recurring fruit service in the dispatch controller (2026-09-07)

Frozen BEFORE any source edit. Prior sources archived under `archive/`.

## Reproduction (done first, on real known-map adaptive trajectories)

`trace-verbs.txt` counts every emitted verb of all 192 real games of the frozen
candidate `f07c76f1` on the UNMODIFIED known development maps 9947500..07 against
the 12 adaptive opponents, both seats (source: the previous run's `panel.tsv`
command columns, not a synthetic fixture).

  verb      baseline   candidate
  HARVEST      11520         754
  CHOP         26484       28126
  DROP         17220        5637
  PICK          2252         329
  PLANT         2390         329
  MOVE         45732       61498
  WAIT          3091        6564

Hypothesis CONFIRMED, and sharpened: the candidate does not merely under-price
fruit, it fells the fruit supply. It chops MORE than the baseline while banking
a third as many loads and idling twice as often. `jobs_for` offers HARVEST only
for fruit hanging at this instant, priced as one trip worth 1 point per unit,
against a CHOP worth WOOD_POINTS=4 per unit over the same trip; chop wins every
comparison, the tree dies, and its recurring fruit service is gone for the rest
of the game. That is the 46.72-point fruit deficit.

## One candidate: an integrated recurring fruit service model

1. `fruit_supply`: fruit a tree actually produces in a horizon under the
   referee's law — a plant only fruits at `MAX_SIZE`, then one fruit per
   effective cooldown. Arrival time and growth-to-maturity are subtracted.
2. `fruit_service`: repeated harvest-and-bank trips for ONE worker's actual
   `(ms, cc, hp)`, over the finite horizon: first partial load from its current
   cell, then full round trips from the door. Banked = min(trip capacity,
   supply). `busy` counts only the trips used, `turns` the elapsed time, so
   other productive work is done between visits.
3. HARVEST is priced as that whole service, not one load. Its bill promise stays
   capped at the FIRST delivered load, exactly like CHOP.
4. CHOP subtracts the service the roster we ACTUALLY own would still bank from
   that tree (best over own hp>0 units, from the door). Not a blanket ban: the
   retention expires when nobody can harvest (hp0 roster), the tree is contested
   (opponent door/unit closer), it is unreachable, or the endgame horizon no
   longer fits a trip. A tree is priced once per chop offer, never split.
5. `plant_job` values a new tree by its LIFETIME service after ripening, so a
   cc1 troll's repeated visits can repay the seed (the old want-1=0 valuation
   could not). Seed spend, reservation and ownership paths are unchanged.
6. `HIRE_SPECS` gains `(1,2,2,1)` and `(2,2,2,1)`: predeclared, capability-aware,
   so `hire_plan`'s existing marginal fruit-vs-timber throughput ledger can
   express a useful harvester. No mandatory hire, no HARVEST bonus constant.

No tuning scan, no second variant, no new constant fitted to these eight maps.

## Comparison and decision rule

Baseline: policy-flat parent `95ee691e`. 192 known development pairs, seeds
9947500..9947507, 12 existing adaptive opponents, both seats,
`ALLOW_ANY_MAP_SEED=1`; all 192 baseline command arrays verified against
`gap20260906T210944Z-3184968-1`. Positive whole-panel W+0.5D AND 0 candidate
issues supports further evaluation. Prior 146.5 is descriptive only.

## Prerequisites before the panel (all required, else no panel)

Focused fixtures pass under actual Rust 1.90; compact export <= 100,000 UTF-16;
original == pruned == compact on the 16 archived streams; per-turn max < 50 ms
measured with nothing else running; run-local Cargo target built after freeze.
