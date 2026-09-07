# V455 to V458, grow-before-fell: measured and rejected — 2026-09-02

Design approved by the owner on 2026-09-02 (option 1 of the economy-gap follow-up): keep V439,
leave own planted trees to size 4 before felling, and let the second troll carry harvest power.
Built by `build_v455_grow_before_fell.py` from the V439 module; measured on the 8-map development
panel (seeds 9941000 to 9941007, both seats, 12 opponent families, 192 paired games against the
V439 baseline) with the new score-curve gate (`panel_gate.py`). Panels and gate files:
`/data/separate_troll_farm-working/panels/2026-09-02/`.

| candidate | changes | own score at 100 / 200 / 300 (baseline 85.0 / 169.2 / 238.5) | W/T/L (baseline 173/5/14) | gate |
|---|---|---|---|---|
| V455 | grow-before-fell, harvest talent, loop from turn 40 | 75.2 / 144.7 / 199.6 | 165/1/26 | FAIL, -38.9 |
| V456 | grow-before-fell, harvest talent, loop from turn 100 | 75.3 / 143.8 / 198.6 | 165/0/27 | FAIL, -39.9 |
| V457 | grow-before-fell only, loop from turn 100 | 84.5 / 166.3 / 234.5 | 169/0/23 | FAIL, -4.0 |
| V458 | grow-before-fell only, loop from turn 40 | 84.9 / 167.1 / 235.3 | 170/2/20 | FAIL, -3.2 |

## What the panels showed

**The harvest-talent change costs 39 points because it spends the orchard's seed.** With harvest
power 2 the second troll costs 5 apples instead of 1. The bot trains at the same turn as before
(median 12) and empties the apple stock, so the apple orchard, which needs one apple to plant its
mother, starts in 95 of 192 games instead of 185 and at turn 110 instead of 68. Harvests fall from
63 to 27 a game in every hundred-turn phase; wood is unchanged (44.3 against 43.6). The loop start
turn made no difference (V455 against V456). Any future harvest-talent variant must reserve the
orchard's apple, or pick harvest power 1 (2 apples) only when the stock allows.

**Grow-before-fell alone is neutral to slightly negative, and the mechanism is the single farm
slot.** Wood 44.3 to 42.8, plants 11.6 to 8.9 a game, WAIT 16.6 to 54.5 a game, games run 9 turns
longer, opponents gain 3.5 to 4.1 points. V439's entrance farm runs one tree at a time: when the
sapling is protected, the troll that used to fell it for one wood every five to seven turns has
no other work on these maps ("early exhausted" is in V439's own name) and waits. One slot growing
to size 4 then fruiting three times yields about 4 wood and 3 fruit per 40 turns of cell time;
the old conversion loop yields 6 to 8 wood in the same 40 turns from the same cell. Per troll-turn
the mature cycle is better, but troll time is not the binding constraint late in these games;
cell time and turns are. The top players escape this by running many trees at once (delineate
plants 41 a game and has 3.4 own trees standing at the end), which V439's farm cannot do.

## Consequences

1. Option 1 as designed is closed. The two changes are measured separately and neither helps.
2. The next candidate must add parallel farm slots, not a slower single one: several trees
   growing at once in the ring around the shack, planted whenever a troll carrying a banana passes
   an empty ring cell, harvested at size 4 for seeds and points, felled after fruiting, with the
   harvested bananas re-seeding the pipeline. That is a refactor of `CompactLeanBananaFarmBot`
   from one entrance to a set of slots, and it needs the owner's approval as a new design.
3. The gate worked as intended: it rejected in two minutes per candidate what the old 960-game
   no-regression count would have taken hours to reach, and it gave the mechanism through the
   turn-100/200 columns and the ring counters.

## Reproduction

```sh
cd /home/tarstars/prj/separate_troll_farm
python3 build_v455_grow_before_fell.py
B=$PWD/candidate_v439_full_baseline_bridge_module.rs
for v in v455_grow_before_fell v457_grow_before_fell_no_harvest_talent; do
  E7A_HALF_BASELINE_MODULE=$B E7A_HALF_CANDIDATE_MODULE=$PWD/candidate_${v}_module.rs \
    cargo build --release --bin candidate_compare_panel
  ALLOW_ANY_MAP_SEED=1 /data/separate_troll_farm-working/tmp/cargo-target-workspace/release/candidate_compare_panel \
    9941000 8 /data/separate_troll_farm-working/panels/2026-09-02/${v%%_*}-dev8.tsv 4
  /home/tarstars/venvs/nn-bot/bin/python panel_gate.py /data/separate_troll_farm-working/panels/2026-09-02/${v%%_*}-dev8.tsv
done
```
