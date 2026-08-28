# delineate (#1, 30.89) — the algorithm, as far as it can be written down

Writer W5, 2026-08-28 ~03:55Z. Every number carries its sample size (n) and a source tag:
**[gist]** the author's own write-up (`sources/delineate-gist.github.com-2026-05-25.md`, verbatim);
**[forum]** his forum reply #29 (`sources/delineate-forum.codingame.com-2026-05-25.md`);
**[stats]** the game author's statistics over delineate's 673 Legend games at the contest's end
(`sources/delineate-eulerschezahl.github.io-stats-2026-05-25.md`);
**[profile]** our corpus profile, 223 ladder games of agent 6479768, positions from the referee's replay log
(`profiles/delineate.md`); **[fits]** the decision-rule fits over the 215 full-length games of the same corpus,
states reconstructed exactly (`fits/delineate.md`, `fits/delineate_fit_results.json`; I re-ran `fits/fit_rules.py`
in a scratchpad copy for the printed figures); **[prior-art]** `prior-art.md` §1.1–§2;
**[champion]** `readable/denial-off-champion.rs`. "Talents" are a troll's four numbers in the game's order,
speed / carry / harvest / chop, written a/b/c/d. Anything marked **GUESS** is mine, not measured.

## 1. What kind of program this is

delineate's bot is a **learned policy network**: a neural network (about 101,000 numbers, submitted as a
98,000-character file [gist]) that takes the board as input and outputs directly which action each troll
takes — **no search, no look-ahead, no written rules** ("There's no turn search/lookahead being done"
[gist]). It was trained by **PPO** (Proximal Policy Optimization: the network plays very many games and after
each batch its numbers are nudged so that actions which preceded a better final score difference become
more likely). Inference takes 2–3 ms of the 50 ms budget [gist]. So "the algorithm" exists at two levels
only: the *shape* of the network — what it sees, what it can output, how outputs become commands (sections
2–3) — and the *training recipe* — the curriculum and reward numbers the author imposed (section 4). The
per-turn judgement is the network's output and is written nowhere. Hence two honest routes to "a program".
**Route A — replicate the recipe:** simulator, 104-plane observation, network, five training levels, days of
training. The author's own first attempt (plain PPO on the full game) reached ~25th and "could never learn
to mine iron"; the final network "improved remarkably in the final 36 hours" [gist] — reproducible in
outline, but the result depends on compute and on details the gist omits (listed in section 4). Our repository
built a five-level PPO curriculum of the same shape (ledger Arc A: tasks learned at 98–99 %, int8 deployment
at 7 ms) whose field value stayed "unproven" [docs/LEDGER-MAP.md §3]. **Route B — imitate the measured
behaviour with rules:** sections 5–6 give the numbers and a rule set on our champion's building blocks. It
can reproduce the *habits* (which trolls, which trees, when) but not the map-by-map judgement, and the
record says a fitted description is not an algorithm until it wins games closed-loop [prior-art §2].

## 2. The actions and the per-turn procedure (as the author describes it)

**Spatial actions.** The main output is **13 logits per cell** (a logit is an un-normalised score; the
highest wins) on an 11 × 22 board: "action types: move, harvest, plant X, chop, pick X, drop, mine" — 1 move,
1 harvest, 4 plant kinds, 1 chop, 4 pick kinds, 1 drop, 1 mine = 13; 13 × 11 × 22 = 3,146 logits [gist]. A
move is chosen as a destination cell: "the first 'movement' logit of every valid cell it can go to" (every
cell within the troll's speed) "plus all the legal non-movement logits at the troll's current cell location"
[gist]. The corpus agrees: all 70,148 MOVE commands in 223 games target a cell 1–3 steps away (mean 1.46)
[profile] — the destination is re-decided every turn.

**Train-plan actions.** A second head scores **144 candidate trolls**: "movement: 1-3, carry: 1-4,
harvest: 0-2, chop: 0-3 … 3x4x3x4 = 144" [gist]. Masks: harvest 0 *and* chop 0 illegal; harvest > carry
illegal; id 0 (1/1/0/0) "repurposed to mean 'done training trolls'" [gist] (121 usable choices by my
count: 144 − 12 − 12 + 1). Each candidate's logit comes from a shared small network fed "target attributes,
costs, deficits, and whether it matches the previous target", so similar trolls share what was learned
[gist]. The chosen target is written back into the observation (costs, deficits): that is how the troll
actions "know" what to collect.

**Per turn, verbatim** [gist]:

> - generate the obs from the current game state and run it through the network to get the train-plan logits
> - update the obs given the train-plan action chosen (max logit)
> - for each of my trolls:
>   - update the obs (just the active_troll plane needs to be updated)
>   - run inference to get the troll's action logits (the first "movement" logit of every valid cell it can go to, plus all the legal non-movement logits at the troll's current cell location)
> - given all the troll action logits, run a beam search over possible combinations of troll moves to find the highest probability moveset for all trolls (i.e. pick a troll, try each of its top X moves, use those moves to invalidate some other troll moves, pick the best moves for the next troll, etc)

One network evaluation for the plan, then one per troll (the "active troll" plane marks which one is
asked), then a **beam search** — a small enumeration keeping the best few partial combinations — used
*only* to make the trolls' moves compatible (no two of ours on one cell), never to look ahead. "When in the
plan selection phase, the non train-plan logits are masked. When in the troll action phase, only the possible
valid moves for that troll are allowed" [gist]. In training each real turn was split into these mini-steps
("a troll plan 'move' (not visible to the opponent), … the first troll, … the second troll, etc") [gist].
Why one inference per troll: one inference for all trolls "seems to have trouble with some basic path
finding … It still has some trouble with basic path finding at times" [forum]. Gaps: the order in which
trolls are queried, the beam width X, and whether TRAIN is issued the turn the plan head first selects it.

## 3. What the network sees

104 **planes** (a plane = one number per cell) on the largest board, 11 × 22; smaller maps are padded and
masked [gist]:

| planes | contents |
|---:|---|
| 0 | valid-cell mask |
| 1–6 | cell type one-hot: grass, water, rock, iron, own shack, opponent shack |
| 7–15 | tree: any tree; kind one-hot plum/lemon/apple/banana; size, health, fruits, cooldown |
| 16–17 | troll occupancy: own, opponent |
| 18–27 | own troll on this cell: speed, carry, harvest, chop, carried resources (6 items) |
| 28–37 | the same for an opponent troll |
| 38–41 | distance to own shack, distance to opponent shack, adjacent to iron, adjacent to water |
| 42–58 | global (same on every cell): turn, own inventory (6), opponent inventory (6), both scores, both troll counts |
| 59–71 | current train target: has target; target speed/carry/harvest/chop; costs; deficits |
| 72–87 | aggregate talents: own max, own sum, opponent max, opponent sum (× 4 talents) |
| 88–92 | distance to the nearest plum tree, lemon tree, apple tree, banana tree, mine spot |
| 93–96 | carried / free capacity: own carried, own free, opponent carried, opponent free |
| 97–99 | mini-step state: train queued, done-training target, **active troll** |
| 100–103 | own troll full; own full with only wood/iron; opponent full; opponent full with only wood/iron |

Each cell holds only the troll on it, but "the network as a whole has full information of all trolls,
trees, ..." (eulerscheZahl, post #28). The author: "I don't think the exact observation planes are all that
important … anything sensible would work" [gist]. **Network:** 1 × 1 convolution stem; 4-block ResNet trunk
(a convolutional network with skip connections) masked to valid cells; the 13-per-cell spatial head; a
pooled global vector concatenated with the global state; two value heads (shaped rewards for levels 1–3,
true score difference for 4–5); the train-plan head [gist].

## 4. The curriculum and the reward numbers — the only "rules" the author wrote

A **curriculum** is a ladder of easier tasks; **reward shaping** = small intermediate rewards for progress
instead of only the final score. All from [gist].

- **Level 1 — build one prescribed troll** (example 3/4/0/1). Shaping: "a rough calculation for how many
  turns it would take to collect the required resources" for each missing resource ("3 more lemons and a
  lemon tree 4 steps away … with 2 trolls"); "positive (or negative) rewards every time it moved closer (or
  farther away) from the target". "I don't think it matters how accurate this is." Formula not given (gap).
- **Level 2 — random targets**, fed into the observation; incremental rewards plus "a big reward" on
  reaching them (size not given — gap); the TRAIN executes automatically when affordable, then a new target.
- **Level 3 — a random target troll count, 2 to 5,** drawn at game start; reward = level-2 shaping plus the
  real end-game score difference. To teach chopping: **+0.5 immediately per wood deposited, end-game wood
  counted 3.5 instead of 4**; briefly "a slight bonus for taking a chop action after it has finished all its
  troll building tasks". Starting directly at level 3 also worked.
- **Level 4 — choose the targets.** Self-chosen targets under shaping were gamed ("a +100 bonus every time
  it finished building a target unit … it would learn to build lots of cheap units"). So the level-3
  movement network was **frozen** and a new "troll plan selector" head with its own value head was trained
  on **the actual end-game score difference with no reward shaping at all**.
- **Level 5 — fine-tune everything** on the end-game difference; from 50th–100th to first in the last 36 h.
- **Failed first attempt:** ResNet + PPO on the whole game, ~25th, "could never learn to mine iron … The
  benefits to mining iron are extremely far in the future."

Not given (gaps for Route A): PPO hyper-parameters, batch sizes, number of games, hardware and wall-clock,
the opponent pool (self-play implied, never stated), the turns-to-collect formula, the completion and chop
bonus sizes, and the manual patches for "getting stuck moving in an endless circle or … forever mining iron".

## 5. The measured behaviour

**5a. Game author's statistics [stats], n = 673 games.** 525-146-2 (78.0 % wins), score 418 vs 298, 297.0
turns. Trolls at the end: 1 → 4 games (1 %), 2 → 254 (38 %), 3 → 179 (27 %), 4 → 179 (27 %), 5 → 53 (8 %),
6 → 4 (1 %). Average talents: train-1 **1.96/2.22/1.52/2.00**, train-2 **2.47/3.35/0.98/2.50**, train-3
**2.67/3.70/1.04/2.90**, train-4 2.72/3.89/1.02/2.89. Score (own/opponent): turn 0 23/18, 25 17/15 (the first
troll is bought from the starting fruit), 100 47/36, 150 85/66, 200 168/132, 250 296/214, 295 421/296. Wood
in the shack: 0.6 at turn 25, 1.8 at 50, 5.5 at 100, 14.1 at 150, 35.1 at 200, 67.2 at 250, 98.7 at 295 —
deposited early and continuously (the +0.5 shaping shows). Lemons peak 8.9 (turn 125), bananas 9.1 (turn 200)
then spent, iron 5.1–5.3 at 100–125. Trees planted by turn 295: plum 8.3, lemon 8.8, apple 1.5, **banana
21.4** (by 100: 1.9/2.6/0.3/1.8; by 200: 4.9/5.4/0.7/9.4). Comparison rows from the same table: norxondor (#2)
4 trolls in 41 % of games, plants 10.0/11.1/2.1/8.7; MSz (#10) 8.6/9.3/3.1/8.9, carry-4 later trolls;
yamo (#3) two trolls, 5.5 bananas; wala (#6) four trolls in 94 %, 37 bananas.

**5b. Our corpus [profile] n = 223 games (opponents mostly Bubaptik 148, tass 30); [fits] n = 215.**
Win rate 0.785; 415 vs 253; **93 % of points are wood** (98 wood per game: 75 from its own trees, 12.5 from
the opponent's, 11 from the map's [fits]). Trolls at the end mean 2.91: two in 98 games (44 %), three in 64
(29 %), four in 45 (20 %), five in 16 (7 %); win rate 69 % with two, 91 % with four [profile].

*Training.* Troll 2 in every game, median turn 6–7 (mean 19.9; 165/223 in turns 1–25; turn-1 TRAIN in only 13
games — it usually mines or plants first): 2/2/2/2 in 45 games, 2/2/1/2 in 23, 2/3/1/2 in 17, 1/2/2/2 in 11;
harvest-capable in 222/223, chop 2 in 147/223. Troll 3 in 125 games (56 %), median turn 111 (p25–p75 90–131):
carry 4 in 88/125, chop 3 in 76/125, harvest 1 in 93/125 (top 2/4/1/3, 3/4/1/2, 3/4/1/3, 2/4/1/2). Troll 4 in 61
games (27 %), median 144–146: 3/4/1/3 in 25/61, 2/4/1/3 in 15/61, chop 3 in 59/61. Troll 5 in 16, median 166.
No TRAIN failed (425). **The spec rule:** each talent is the largest level the shack can pay at that moment,
`talent = floor(sqrt(bank[resource] − troll_count))` (plums → speed, lemons → carry, apples → harvest,
iron → chop), exact in 22/26 games, the exceptions keeping harvest lower [prior-art n = 26]; over all 412
TRAINs the chosen troll maximises carry × chop among the affordable ones in 97 %, speed + carry + chop in
94 %, all four talents in only 80 % (harvest is not maxed: ≥ 2 in 109/215 second trolls, 16/121 third, 11/60
fourth); a strictly bigger troll was affordable in 83/412 [fits]. **The timing rule:** train the turn the
target is affordable — delay 0 turns in 251/412, 1 in 110, 2–5 in 34, 6+ in 17 [fits]. The bottleneck is
fruit, not wood (carry 4 costs 2 + 16 = 18 lemons at roster 2, chop 3 costs 11 iron; wood at the TRAIN median
0–15), which is why the farmer harvests lemons all game (3,543 of 9,741 harvest trips) [fits]. What predicts
scaling past two [prior-art n = 26]: a fully affordable first bill (64 % continue vs 22 %) and a tree at the door.

*Planting.* 39.7 plants per game, all successful [profile]: banana 48 % (4,176 of 8,636 [fits]), lemon 28 %,
plum 19 %, apple 4 %. First plant lemon in 149/223 games. Kind by period [fits]: turns 0–49 lemon 440, plum
246, banana 164, apple 53; after turn 100 banana 3,657 vs lemon 1,750, plum 1,285, apple 282. Rate 0.7 per 10
turns before 120, 1.9 after 150 [profile]. Cell: 43 % adjacent to the shack (3,677), 28 % at distance 2, 18 %
at 3, 7 % at 4 [fits]; 99.6 % own half; 23 % water-adjacent — water is *not* sought (water rules fit 17–20 %);
2,287 plants without moving, 3,730 after one step; 84 % of planted cells touch a living tree [fits]. Own
trees alive: 3.1 at turn 50, 4.8 at 100, 6.4 at 150, 7.8 at 200, 7.0 at 250, 3.5 at 300 [fits].

*Harvesting.* 78.8 commands, 85 fruits per game; lemon 42 %, plum 23 %, banana 21 %, apple 15 %; own trees
72 %, wild 27 %, opponent's 1.5 % [profile]. 58 % of harvest trips end at distance 1–2 from the shack; 51 % go
to a tree with 3 fruits; 93 % of harvest runs last one turn — the carry-1 farmer alternates HARVEST, DROP
(57 % of drops carry one item) [fits]. Peak 4.0 per 10 turns at turns 100–150, 1.2 in the last ten [profile].

*Chopping.* 172 CHOP commands, 129 land per game; first wood median turn 26 [profile]. Whose trees: own
64 %, opponent-planted 24 %, wild 13 %; in turns 1–100 **56 % of chops hit the opponent's plantings**
(own 17 %), in 201–300 own 80 % [profile]. By period, the share of chop destinations on the opponent's half /
within 2 cells of the opponent's shack [fits, n = 7,651 trips]: turns 0–49 **84 % / 56 %**, 50–99 74 / 50,
100–149 46 / 33, 150–199 29 / 21, 200–249 22 / 15, 250–299 14 / 9 — "early choppers camp at the opponent's
shack and cut the young trees the opponent plants there … again and again as they are replanted; late
choppers cut the home orchard" [fits]. Destination trees: size 4 in 66 %, carrying fruit in 47 %, the nearest
living tree in only 28 % [fits]; own bananas felled at size 4 (1,861 runs), median age at felling 17 turns
[fits]; 3,155 chops without moving (1,355 right after planting on that cell, 1,300 right after a DROP)
[fits]. *Conflict:* the profile's "size 1 in 64 % of chop strokes" is read from the viewer's stage field,
the fits' "size 4 in 66 % of destinations" from exact states validated against the referee — trust the fits;
the "plant, one tick, fell" reading in the profile summary is therefore doubtful. Rate ~3 per 10 turns from
turn 11 to 130, rising to 10.5 by the end; wood banked per game by period 7.4 / 32.6 / 58.1 [profile].

*Mining.* 171/223 games, 7.8 MINE, 11.5 iron per game; first MINE median turn 34; fades after turn 150 [profile].

*Roles (share of action turns, moves excluded) [fits].* Start troll 1/1/1/1 (215 units): HARVEST 34 %, DROP
29 %, PLANT 16 %, CHOP 15 %, PICK 6 % — the farmer at the shack. 2/2/2/2 (43 units): CHOP 49 %, HARVEST
14 %, PLANT 10 %. 3/4/1/3 (40 units): CHOP 72 %, DROP 20 %, HARVEST 4 %. One farmer, then lumberjacks.

*Opening [profile].* First action of the start troll: PICK a seed at the door 46 % (103/223), HARVEST 37 %,
MINE 14 %; commonest 10-turn pattern (17 games) `M K P K M P M M M M` — door, pick, plant, pick, step, plant.

*Endgame.* No visible switch [fits]: last PLANT median turn 296 (10th pct 282), last HARVEST 292, first chop
of an own tree median 96; own trees drawn down over the last 50 turns but never to zero; 877 bananas still
planted in turns 275–299 over 215 games. Last 30 turns [profile]: CHOP 37 % of commands, MOVE 38 %, DROP 12 %,
PLANT 6 %, HARVEST 5 %; 31 chops, 4.8 plants, 17.8 wood per game; last DROP median turn 299; trees left
standing own 3.3 / wild 5.9 / opponent's 4.3. Zero MSG, zero timeouts, byte-exact replays [prior-art].

**5c. Which simple rule reproduces its choices (teacher-forced) [fits].** Accuracy = share of decisions
whose target is in the rule's best set; the tie-adjusted figure (random tie-break) is the honest one.

| decision (n) | best rules | accuracy (tie-adjusted) |
|---|---|---|
| chop target, all 7,651 | size / (travel + 1) | 48.0 % (24.7) |
| | min(size, free carry) / (travel + chop turns + 1) | 45.8 % (22.0) |
| | champion's wood / (travel + chops + return + 1) | 41.8 % (20.5) |
| | nearest tree | 27.9 % (19.4) |
| chop target, turns 1–100 (1,426) | wood per turn, opponent-half trees × 2 | 66.2 % |
| | wood / (travel + chops + 1) | 62.6 % (13.2) |
| | nearest opponent-planted tree | 44.0 % |
| chop target, turns 201–300 (3,761) | size / (travel + 1) | 53.7 % (28.1) |
| plant cell (8,636) | empty cell minimising d(shack) + d(troll) | 89.9 % (3,782 ties) |
| | nearest empty cell to the troll / to the shack | 78.7 % / 50.3 % |
| plant kind (8,636) | banana after turn 100, else the scarcer of plum/lemon | 50.0 % |
| harvest target (9,741) | nearest tree with fruit and no own troll on it | 70.5 % (57.0) |
| | champion-style min(fruits, free) / (travel + harvest + return + 1) | 66.0 % (45.0) |

W4's verdict: "no single-formula rule reproduces the chop choice"; the early game is denial at the enemy
shack (the exact order among their young trees is not recovered), the late game "biggest tree per travel
turn" from the home orchard, fruit on a tree is no deterrent. Excluding own-planted trees makes every rule
worse (≤ 23 %): it chops its own trees deliberately. Unfitted: the choice *between* harvest, plant and chop.

## 6. A rule-based imitation (Route B) — pseudo-code on the champion's building blocks

Building blocks in [champion]: `bfs_distances`; `training_cost(n, talents)` = plums n + speed², lemons
n + carry², apples n + harvest², iron n + chop²; `predict_tree` / `chop_outcome` (turns to fell a tree with a
given chop power, growth included); the chop value `1000·min(size, free) / (travel + chops + return + 1)`;
`ticks_until_fruit`; `select` (best compatible candidate per troll) and `resolve_move_conflicts`. An
**approximation** of the habits in section 5; expected gaps follow the code.

```
STATE: target (troll spec being saved for, or none); k = TRAINs so far; raid_on (bool)

each turn:
  # 1. training plan  (stand-in for the train-plan head)
  n = own trolls; turns_left = 300 - turn
  LADDER = {0: 2/2/1/2, 1: 2/4/1/3, 2: 3/4/1/3, 3: 2/4/1/3};  DEADLINE = {0: 30, 1: 190, 2: 220, 3: 230}   # deadlines GUESS
  if target is none and k <= 3 and turn <= DEADLINE[k]: target = LADDER[k]     # bill open from the start [fits: delay 0 in 61 %]
  if target and affordable(training_cost(n, target)):
      spec = per talent the largest s with n + s*s <= bank, capped 3/4/2/3            # [prior-art 22/26; fits 94-97 %]
      if k >= 1: spec.harvest = min(spec.harvest, 1)                                  # later trolls: harvest >= 2 in only 13 % [fits]
      emit TRAIN spec; k += 1; target = none
  elif k == 0 and turn >= 30: emit TRAIN best affordable spec with chop >= 1        # champion's deadline fallback
  deficits = training_cost(n, target) - bank if target else 0
  raid_on = turn <= 100 and opponent has planted trees within 2 cells of its shack    # [fits: 84 % of early targets]  GUESS on the trigger

  # 2. candidates per troll, one score scale (champion style; higher wins)
  for troll in own trolls:
      C = [WAIT]
      if carrying wood/iron or free capacity == 0:            C += BANK       # wood goes home at once [stats: 1.8 wood at turn 50]
      if carrying a fruit whose deficit > 0:                    C += BANK
      if carrying a fruit whose deficit <= 0 (bananas always):                 # plant it on the way home
          cell = empty grass cell minimising d(shack) + d(troll), own half     # [fits 89.9 %]
          if 6 + chop_turns(kind, size 1) + d(cell, shack) < turns_left:  C += PLANT at cell (7000 - d)
      if at the shack door and (bananas >= 1 or plums/lemons > next bill + 3):
          kind = banana if turn > 100 else the scarcer of plum/lemon                                       # [fits 50 %]
          C += PICK kind (score 7500)
      for tree with fruit and no own troll on it:  C += HARVEST-trip (6000 - travel - wait, +500 if deficits[kind] > 0)   # [fits 70 %]
      if deficits[iron] > 0 and troll.chop > 0 and turn <= 150:  C += MINE-trip (6100 - travel)
      for tree reachable in time (own, wild or opponent's):
          t = travel + chop_turns + 1; wood = min(predicted size, free)
          value = 1000 * wood / t                                                                          # [fits 46 % raw]
          if raid_on and tree planted by the opponent and d(tree, their shack) <= 2 and size <= 2: value *= 3     # denial  GUESS on the factor
          if turn > 150: value = 1000 * size / (travel + 1)                                                # late rule [fits 54 % raw]
          C += CHOP-trip (value)
      role weights: start troll x1.5 on HARVEST/PLANT/PICK, x0.5 on CHOP; trained trolls x1.5 on CHOP   # [fits roles]  GUESS on the factors
      candidates[troll] = C

  # 3. team choice  (stand-in for the beam search)
  commands = select(candidates, bank); resolve_move_conflicts(commands)   # no two trolls on one cell, no two PICKs of a last seed

  # 4. endgame: no switch [fits]; plant only if 6 + chop_turns + return <= turns_left; every carrier banks by turn 299;
  #    a troll with no fellable tree in reach harvests (the champion's idle-harvest block)
```

*What it should reproduce:* troll 2 on turns 1–7 by the max-payable rule; troll 3 near turn 110 and troll 4
near 145 when the farmer's lemons reach the carry-4 bill (56 % / 27 % of games); lemon-first planting beside
the shack, bananas from turn 100 at a rising rate; the early raid on the opponent's nursery; wood in the
shack from the first felling; chopping rising from ~3 to ~10 per 10 turns; last DROP at turn 299.

*Expected gaps.* (1) The map-dependent style — "sometimes 'attack' or 'rush' … sometimes a more macro game"
[gist] — is the plan head's judgement; the deadlines, the raid trigger and the role factors are GUESSes, and
opening formulas tuned on small samples have not transferred here [prior-art §2 item 4]. (2) The chop target:
best tie-adjusted fit 28 % — the rule set will chop different trees than the network in most turns. (3) The
choice between harvesting, planting and chopping is unfitted. (4) Whether the raid is a rule or falls out of
a value function is undecided; W4's data favours a rule. (5) Route B failed here whenever judged by
teacher-forced accuracy alone (Escdemon 56 % → 52 % integrated; a Norxondor clone −172 margin closed-loop
[prior-art §2 item 2]): the rule set must be scored by playing games on official maps.

## 7. Sources and confidence

| claim | source | n | confidence |
|---|---|---|---|
| network shape, action space, masks, per-turn procedure, no search, 2–3 ms | [gist], [forum] | author's text | HIGH (first-hand) |
| observation planes | [gist] | — | HIGH, with the author's "not important" caveat |
| curriculum and reward numbers (0.5 / 3.5, 2–5 trolls, +100 example, 36 h) | [gist] | — | HIGH that they were used; the omitted numbers are real gaps |
| trolls, talents, plants, wood and score curves | [stats] | 673 games | HIGH (game author's count, contest-final bot) |
| ladder timing, planting, harvesting, raid phases, roles, endgame | [profile], [fits] | 223 / 215 games | HIGH for the habits; opponents narrow (Bubaptik 66 %) |
| spec rule (max payable per talent) and train-at-affordability | [prior-art] 22/26; [fits] 412 TRAINs | two independent counts agree | MEDIUM-HIGH |
| chop / plant / harvest target rules | [fits] | 7,651 / 8,636 / 9,741 decisions | MEDIUM: teacher-forced; tie-adjusted chop fit only 25–28 % |
| section 6 deadlines, raid trigger and factor, role factors | — | — | GUESS |
| Route A reproducible from the gist alone | [gist] + ledger Arc A | — | LOW without the missing training details |

**Prior art in this repository [prior-art §1.1, §2].** The L1 readiness audit (2026-07-31) decoded 199
delineate games into 145,448 exact per-unit rows: the final commands and 378 TRAINs are exact labels, but
the train-plan target, the 3,290 logits, the alternatives and the beam are unobservable — verdict
"primitive-only"; the successor was never started. Before tonight the only fit on it was Phase 9's
18-class objective lookup, 60.4 % held-game accuracy on 17,743 unit-turns (26 games), below the gate.
Pooled imitation of the top five fails (worst held agent 39 %): different architectures. The one
reconstruction that ever worked here came from a write-up, not replays (yamo's post-mortem → our resident),
which is the template section 6 follows: the author's rules, the gaps named, each gap measured.

Not found anywhere: the author's code or weights; the turns-to-collect formula; the opponent pool; the troll
query order; the beam width; any water rule (measured: none); the exact raid ordering. `prior-art.md`,
`profiles/delineate.md` and `fits/delineate.md` all appeared during the night and are folded in as of 03:55Z.
