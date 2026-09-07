# V472 to V475, a third troll funded by mined iron: measured and rejected — 2026-09-02 (loop iteration 5)

Queue item 1 after iteration 4, the last untested wood lever: train a third troll the way R1FA,
astrobytes and delineate do (around turn 100, with mined iron). Built on the V468 base by
`build_v472_third_troll.py`, which reuses the opening's bill-gathering (`early_candidates`: harvest
and mine jobs for whatever a training bill still lacks) for the starter after the second troll
exists, emits TRAIN when the bill is affordable, and lapses after a last turn. Development panel
of 8 maps and 192 paired games against V468; `panel_gate.py`, `panel_diagnostics.py`, and a split
of each panel by whether the third troll was actually trained.

| candidate | third troll and gatherers | window | own score at 100 / 200 / 300 (V468: 93.0 / 176.2 / 247.2) | trained in | third-train turn (median) | own delta when trained / when not | gate |
|---|---|---|---|---|---|---|---|
| V472 | 2/2/0/2, starter gathers everything | 20 to 160, 120 turns left | 88.6 / 171.3 / 251.9 | 20 of 192 | 155 | +24.9 / +2.3 | FAIL, +4.6 |
| V473 | 1/2/0/2, starter gathers | 20 to 160 | 88.2 / 171.3 / 249.7 | 30 of 192 | 114 | +4.6 / +2.1 | FAIL, +2.5 |
| V474 | 2/2/0/2, second troll mines the iron | 20 to 160 | 75.3 / 164.4 / 245.7 | 46 of 192 | 137 | +11.6 / -5.7 | FAIL, -1.5 |
| V475 | as V474 | 20 to 200, 90 turns left | 75.3 / 163.3 / 245.5 | 58 of 192 | 142 | +5.8 / -5.0 | FAIL, -1.7 |

## What the panels showed

- **A 2/2/0/2 third troll pays when it arrives**: +24.9 own score and +7 wood in the games where
  V472 completed its bill, even at a median turn of 155 with about 145 turns left. A 1/2/0/2 troll
  arrives earlier and pays almost nothing (+4.6): speed 1 with carry 2 is not a chopper.
- **The bill is the problem.** At n=2 the 2/2/0/2 bill is 6 plum, 6 lemon, 2 apple and 6 iron.
  The starter carries one item per trip, so it completes the bill on only 2 of 8 maps (20 games).
  Handing the iron to the fast second troll (V474/V475) lifts completion to 46 and 58 games but
  stops the only chopper for its mining trips: own score is 17.7 behind at turn 100 in every game,
  the third troll still arrives around turn 140, and the games where it does not arrive at all end
  5 to 6 points down. Widening the window (V475) trains more trolls, later, for less.
- The top players afford the same bill by turn 100 because their farms produce plums and lemons
  as a by-product and their mining happens in otherwise idle time; here the starter's time is the
  apple engine and the second troll's time is all the wood there is.

## Consequences

1. Item closed. A third troll only pays with an economy that produces its bill as a by-product;
   on this bot every gatherer is already the income.
2. With this item the queue's autonomous work is exhausted: the remaining entries depend on a farm
   that failed, need the owner's approval (the opponent pool), or duplicate this item. Per the
   charter the loop stops and reports.
3. Across the day, V455 to V475 (21 candidates, 5 iterations) fail the +40 bar. The only measured
   gain is V468's +3 on fresh maps, now the development base. The picture the panels paint is
   consistent: V439's economy is one starter on a two-turn apple cycle and one chopper, and every
   single-mechanism addition either idles a troll or spends the income it needs; reaching a top
   player's 415 needs several mechanisms at once (farm output, a second harvester, an early third
   troll), which cannot be measured one at a time under the current gate.
