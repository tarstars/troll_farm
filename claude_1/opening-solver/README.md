# The opening solver (card `20260903-opening-solver`, stage 1)

An offline planner for the first hundred turns of one player on a real map: which troll to buy
from the starting draw, which seeds to plant where, which wild trees to harvest, when to mine,
and the turn the third troll comes online. Every schedule it reports is a list of referee
command lines, replayed through `sim/engine.py` before it is written; the completion turn is
read off the referee's world, not the model's.

| file | what it is |
|---|---|
| `world.py` | the fast model: one panel map's geometry with every walking distance precomputed, and the referee's eight phases (MOVE, HARVEST, PLANT, CHOP, PICK, TRAIN, DROP, MINE, then the trees tick) for one player. A mirror of `sim/engine.py`; the referee wins every disagreement |
| `replay.py` | replays a schedule through `sim/engine.py` (the opponent idle on its shack) and diffs the two worlds after every turn; returns the referee's TRAIN turns |
| `solver.py` | the dispatcher: macro-tasks per troll (harvest k at tree X, bank at a door, pick a seed and plant it, mine k, leave the shack) valued per turn against the next bill's deficit; the shack trains the moment the pre-turn stock (after this turn's PICKs) clears the bill and the shack is empty after this turn's moves. The plan knobs: the two trolls' talents, the seed programme (kind and cell rule: next door or next to water), whether a seed may delay a purchase, bottleneck-first weighting, waiting on fast trees |
| `enumerate.py` | the second trolls the draw affords on turn 1, the delayed floor set, the third-troll sweep |
| `driver.py` | one map-seat: stage A every plan once deterministically, stage B the best few with randomised rollouts; keeps the earliest third troll, tie-break the bank in points plus the standing wood of the trees we planted |
| `run_panel.py` | the 200 panel maps, both seats, four variants (the solver's second troll with a third troll of chop 3, 2, 1; and orchard 6's own roster on that map-seat); writes `schedules/<map_hash>-s<seat>.json` and `panel-summary.json` |
| `baseline.py` | orchard 6's and the champion's real funding turns per panel map-seat, read off `claude_1/h2h-panel/results/champion-vs-orchard6.json` |
| `ablate.py` | where the turns go: the solver re-run under orchard 6's habits one at a time (its second troll no earlier than orchard 6 bought it; seeds next door only; one item a trip; no wild tree beyond four steps) |
| `raid_rate.py` | the balance question: every planted tree in the collected games and its fate (raided by the enemy, converted by its owner, standing); raids per 100 tree-turns by distance and by turn; `raid-rate.json` |
| `report.py` | the numbers of the one page from `panel-summary.json` and the schedules |
| `READ-2026-09-03.md` | the one page for the owner (stage 1's read) |
| `panel-summary.json`, `schedules/`, `ablation.json`, `raid-rate.json` | the panel run of 2026-09-03 (400 map-seats, 150 min), the ablation run (51 map-seats), the raid table |

    cd claude_1/opening-solver
    python3 run_panel.py 0 4          # every map, 4 workers (about 80 minutes on the laptop)
    python3 report.py
    python3 ablate.py 30 4            # the first 30 maps, both seats
    python3 raid_rate.py

A schedule file carries, per variant, the plan, the TRAIN events, the inventory at completion, the
trees planted, and `commands`: one list of referee command strings per turn from turn 1. The
verifier's schedule-following seat feeds those lines as they stand; turn t's list is C_t.

Model against referee: 120 random schedules of up to three trolls (the batch check of 2026-09-03
06:0xZ) and every schedule the panel run kept agree turn by turn with `sim/engine.py` on
inventory, positions, carries and every tree's size, health, fruits and cooldown.
