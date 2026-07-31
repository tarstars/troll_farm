# Dridriun fruit-control postmortem

Date: 2026-07-31
Game: `896352129`
Result: resident 252, Dridriun 276
Provisional verdict pending corrected re-review:
**`NARROWED_TO_DISTINCT_FRUIT_CONTROL_PRECHECK`**

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

Dridriun planted nine successive APPLE generations at `(9,2)`. The decoder separates
command pressure from material flow: all **83 HARVEST commands succeeded**, each produced
one APPLE unit, and zero were failed/zero-gain. The resident issued 84 CHOP commands, 82
classified successful. Eight trees disappeared on turns when both resident unit 3 and
Dridriun unit 1 issued successful CHOP; the ninth survived.

| planted | first HARVEST | commands | successful | fruit units | zero/failed | first resident CHOP | resident CHOP cmd/success | fate |
|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 3 | 14 | 33 | 33 | 33 | 0 | 63 | 14/14 | joint removal t80 |
| 83 | 94 | 4 | 4 | 4 | 0 | 91 | 10/10 | joint removal t102 |
| 105 | 116 | 6 | 6 | 6 | 0 | 120 | 10/10 | joint removal t129 |
| 132 | 144 | 6 | 6 | 6 | 0 | 147 | 10/10 | joint removal t156 |
| 159 | 170 | 10 | 10 | 10 | 0 | 182 | 10/10 | joint removal t191 |
| 194 | 206 | 5 | 5 | 5 | 0 | 207 | 10/10 | joint removal t216 |
| 219 | 230 | 1 | 1 | 1 | 0 | 224 | 10/9 | joint removal t233 |
| 236 | — | 0 | 0 | 0 | 0 | 241 | 10/9 | joint removal t250 |
| 253 | 266 | 18 | 18 | 18 | 0 | — | 0/0 | alive |

The first generation is the clearest error: **60 turns** elapsed between planting and the
resident's first chop. The 25 commands before contact are confirmed as 25 fruit units,
and the full generation produced 33. Later contact was usually earlier, but ten
low-lethality chop turns still allowed fruit production during removal. The problem is
therefore both target timing and time to kill, not literally “the bot never chopped.”

The 83 fruit units are observed carried-resource flow, not 83 causal recoverable points.
Earlier attack would replace other work, tree growth interacts with chop damage, and
Dridriun could replant or change policy.

## 2. Resident production under opponent capture capacity

The resident planted nine APPLE generations on its doors: six at `(8,4)` and three at
`(9,5)`. Five were planted by the harvest-capable starter; four by the trained
`harvest_power=0`, `chop_power=2` worker.

Access now uses explicit state indices. On each post-PLANT state, the selected opponent
unit is unit 1 (`movement=1`, `capacity=1`, `harvest=1`, `chop=1`); raw BFS spans 1–5
across all nine resident plants. For the four generations that later ripen, raw BFS/ETA
at planting is 3/3, 2/2, 3/3, 3/3. At each first-ripe state it is **3/3**. The old 2/1
label mixed semantics and is withdrawn. Unit 1 later co-locates on turn 225 and turns
240–244.

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

| generation | plant/ripe state | first ripe CHOP | actor `(ms,cc,hp,chop)` | free | opponent BFS/ETA at ripe | ripe CHOPs | max/removal fruit |
|---|---|---:|---|---:|---|---:|---|
| `205:8:4` | 205/213 | 214 | u0 `(1,1,1,1)` | 1 | 3/3 | 12 | 3/3 |
| `228:8:4` | 228/236 | 237 | u0 `(1,1,1,1)` | 1 | 3/3 | 8 | 3/3 |
| `264:8:4` | 264/272 | 273 | u3 `(2,2,0,2)` | 2 | 3/3 | 1 | 1/1 |
| `287:8:4` | 287/295 | 296 | u3 `(2,2,0,2)` | 2 | 3/3 | 1 | 1/1 |

For the first two generations, unit 0 is co-located, has `harvest_power=1`, carries
nothing, has one free slot, and therefore has a legal useful HARVEST alternative at first
ripeness. It nevertheless selects CHOP on every ripe command. Two later
`harvest_power=0` worker cycles destroy one fruit each.

The compact JSON contains all 22 ripe CHOP transitions for turns 214–225, 237–244, 273,
and 296. Each row records unit stats, carry/free capacity, tree health/fruit before and
after, command success and gain, plus the selected opponent harvester's raw BFS and
speed-adjusted ETA. It also contains all eight first resident contacts and all eight joint
removal transitions. Command turn `t` is explicitly `states[t-1] → states[t]`.

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
TestSession, or Arena action is authorized. The narrow verdict is not canonical until the
corrected compact passes independent re-review.
