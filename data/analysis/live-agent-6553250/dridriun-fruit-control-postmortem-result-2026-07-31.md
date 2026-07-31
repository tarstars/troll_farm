# Dridriun fruit-control postmortem

Date: 2026-07-31
Game: `896352129`
Result: resident 252, Dridriun 276
Verdict: **`NARROWED_TO_DISTINCT_FRUIT_CONTROL_PRECHECK`**

## Decision

The owner's three observations are real, but the exact replay sharpens them:

1. the resident did eventually chop most enemy-door apples, but often only after a long
   harvest stream;
2. the opponent did not actually harvest fruit from the resident's planted apples in this
   game, although a harvest-capable troll could reach and occupy the ripe tree;
3. the resident definitely chopped ripe own-door apples while its harvest-capable starter
   stood on them and never harvested.

These are not evidence for an immediate policy edit. They do define a joint
**relative-control** question not tested by any one previous arm: deny a recurring enemy
stream, avoid creating capturable fruit, and harvest controlled ripe stock before
conversion. A successor may only be a read-only corpus precheck.

## Exact integrity and geometry

The raw 300-turn replay and trajectory decode with zero unknown updates.

| artifact | SHA-256 |
|---|---|
| raw game | `eee9f3485204dea948efa36d39b2fb7783752cec419e931bc08577f943adb1c0` |
| exact trajectory | `b4f42a5f46791de61aaa5a91e4c19f35aba3b711e9399666565fdb61a3983593` |

Resident shack is `(8,5)` and Dridriun's is `(9,3)`. The decisive cells are unusually
close:

- Dridriun's apple `(9,2)` is an opponent door and BFS 3 from a resident door.
- Resident apple cells `(8,4)` and `(9,5)` are resident doors and only BFS 1 from an
  opponent door.

## 1. Enemy-door orchard: denial came late and removal stayed slow

Dridriun planted nine successive APPLE generations at `(9,2)`. They produced **83
observed opponent HARVEST commands**. The resident issued 84 CHOP commands against those
generations and removed eight; the ninth remained alive and was harvested 18 times before
game end.

| planted | first opponent harvest | harvests | first resident chop | resident chops | removed |
|---:|---:|---:|---:|---:|---:|
| 3 | 14 | 33 | 63 | 14 | 80 |
| 83 | 94 | 4 | 91 | 10 | 102 |
| 105 | 116 | 6 | 120 | 10 | 129 |
| 132 | 144 | 6 | 147 | 10 | 156 |
| 159 | 170 | 10 | 182 | 10 | 191 |
| 194 | 206 | 5 | 207 | 10 | 216 |
| 219 | 230 | 1 | 224 | 10 | 233 |
| 236 | — | 0 | 241 | 10 | 250 |
| 253 | 266 | 18 | — | 0 | alive |

The first generation is the clearest error: **60 turns** elapsed between planting and the
resident's first chop. Dridriun harvested 25 apples before resident contact and 33 before
removal. Later contact was usually earlier, but ten low-lethality chop turns still allowed
fruit production during removal. The problem is therefore both target timing and time to
kill, not literally “the bot never chopped.”

The 83 harvests are observed flow, not 83 causal recoverable points. Earlier attack would
replace other work, tree growth interacts with chop damage, and Dridriun could replant or
change policy.

## 2. Resident production under opponent capture capacity

The resident planted nine APPLE generations on its doors: six at `(8,4)` and three at
`(9,5)`. Five were planted by the harvest-capable starter; four by the trained
`harvest_power=0`, `chop_power=2` worker.

At planting, the nearest opponent harvest-capable troll was BFS 1–5 away. For the first
two ripe `(8,4)` cycles the distance was only 2 and 1. That troll later co-located with
the ripe tree on turn 225 and turns 240–244.

Important correction: **Dridriun harvested zero apples from these resident generations.**
It contested/chopped them instead. Thus “we produced fruit the opponent could harvest” is
an exact reach/capability risk, not an observed opponent capture in this replay.

Five resident apple generations were converted before fruit appeared. Four did ripen.
This is why the population statement “conversion-by-design” remains true while the user's
specific failure is still real.

## 3. Ripe own-door apples were chopped, not harvested

Across the four ripe resident generations:

- resident HARVEST commands: **0**;
- resident CHOP commands while fruit was present: **22**;
- fruit stock present on the final removal turns: **8** total.

The two strongest episodes were starter-controlled:

| planted | cell | first ripe chop | ripe chop commands | max fruit | fruit at removal |
|---:|---|---:|---:|---:|---:|
| 205 | `(8,4)` | 214 | 12 | 3 | 3 |
| 228 | `(8,4)` | 237 | 8 | 3 | 3 |

Unit 0 had `harvest_power=1`, stood on the tree, and selected CHOP every turn. This is
exactly the owner's “we had leverage but did not collect” observation. Two later
`harvest_power=0` worker cycles destroyed one fruit each.

The eight-point final stock is direct one-game accounting, not a causal gain. HARVEST
would delay wood conversion and DROP/scheduling costs remain; D173a/b showed that these
costs can reverse broad harvest-before-chop changes.

## Why this is distinct only as a precheck

- **Phase 21** generically doubled opponent-crop target value within ETA 6. It can address
  enemy-tree urgency, but not unsafe own planting or own-tree HARVEST choice, and it lost
  −7.77 rating in the Arena.
- **D173a/b** addressed harvest-before-chop for capable assignments, including the third
  symptom in broad form. They did not address early enemy-orchard denial or production
  restraint, and both failed family, catastrophe, and negative-mass gates.
- **B3.7** correctly says the resident orchard is conversion-by-design. This game isolates
  the rare tail where conversion lasted long enough to create fruit.
- **B3.10** closes generic near-camp fruit targeting at a 4.84/game gross ceiling. It does
  not measure a recurring opponent-door orchard stream or the joint relative-control
  predicate.
- **H3a** proves source reproducibility only.

The only defensible continuation is a read-only existing-corpus precheck asking whether a
strict relative-control predicate isolates enough repeated flow without reproducing the
closed broad arms. It must report actual opponent capture separately from mere reach and
must preserve wood/scheduling costs.

No source edit, threshold, capability change, runner, range, panel, candidate, submission,
TestSession, or Arena action is authorized.
