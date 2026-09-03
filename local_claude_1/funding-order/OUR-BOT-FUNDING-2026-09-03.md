# How our bot funds its third troll — a turn-by-turn read of 159 real games (2026-09-03)

The owner watched "orchard 8" play and said: the third troll's resource collection looks
inefficient, and the order of TRAIN / PLANT / GATHER matters a lot. This is a read of the
actual recorded games to see exactly what the bot does, turn by turn, while it funds the
third troll — not a guess from the source code.

## Data and method

- **Corpus**: submission **41209711** ("orchard 6", agent 6671418), 160 collected ladder
  games with full per-turn replay, `local_claude_1/ladder-queue/games-41209711/games-agent6671418-submission41209711.jsonl.gz`.
  **Orchard 6 is the right stand-in for orchard 8** (the bot on the ladder now): I diffed
  `local_claude_1/third-troll/orchard6-readable.rs` against `orchard8-readable.rs` and the
  only non-comment difference (9 lines) is the opening's "never abandon" fallback when no
  second-troll build is affordable — every line of the third-troll funding logic (the bill,
  the orchard, the candidate scoring) is byte-identical between the two.
- **One game (900767891) could not be replayed** (a malformed single-token command, most
  likely from a crashed/old opponent bot on the other side of the board) and was dropped.
  **159 of 160 games are in every number below.**
- **All 159 games happen to be iron maps** — this batch drew no iron-free map, so the brief's
  requested iron/iron-free split is empty on the iron-free side; every "per map type" question
  below is really just "iron maps" (see the per-item bill table — iron is one of the four
  requirements here, never zero).
- **Reconstruction**: exact per-turn state (positions, carries, every tree's size/fruits/health,
  both players' shack inventories) was rebuilt by replaying each game's recorded commands
  through the project's own referee mirror (`sim/engine.py`), then correcting that prediction
  turn by turn with the platform's own keyframe diff — the same method as
  `local_claude_1/reconstructions/fits/reconstruct.py`, which is cross-checked there against
  40,458 real turns with nothing left unexplained but the random tie-break. I found and fixed
  one method mistake along the way: **a diff-only read (no engine) freezes a tree's fruit
  count between the turns it is actually touched** (the platform does not re-send an unchanged
  cooldown/stage every tick), which made an early pass of this script show over half of all
  HARVEST commands firing at "0 fruit" — a reconstruction artefact, not the bot's behaviour.
  With the engine step restored, **zero** of 2,484 HARVEST commands fire on an empty tree,
  matching the bot's own source (it only ever issues HARVEST when `plant.fruits > 0`) — a
  clean internal consistency check that the corrected numbers below are sound.
- **Script**: `local_claude_1/funding-order/analyze_funding.py` (run: `python3 analyze_funding.py
  local_claude_1/ladder-queue/games-41209711/games-agent6671418-submission41209711.jsonl.gz 6671418`,
  full run in `/tmp/.../scratchpad/funding-read/full_run3.txt`, 13.6s for 159 games). It writes
  `local_claude_1/funding-order/summary.json` (per-game structured facts) beside this report.
- The bill for the third troll (talents 2/3/0/3, chop-throttled by iron distance — see §4) is,
  from the training-cost formula `n + stat²` at n=2 own trolls: **6 plum, 11 lemon, 2 apple,
  11 iron**. This matches the design note and the earlier read
  (`local_claude_1/third-troll/orchard6-vs-orchard7-read-2026-08-29.md`) almost exactly (that
  read, on the same batch, found 59% wins with the third troll and 68% of opponents already at
  3+ trolls — consistent with what follows).
- Where a number is a sample rather than a full count (the bill-progress curve is sampled every
  other turn to keep the run fast) I say so.

---

## 1. The opening: turns 1–12

Every game starts the same way structurally: the lone starting troll walks to a shack door,
then alternates **PICK a seed → walk to an orchard cell → PLANT** three times (2 lemon + 1
plum), interleaved with early fetching once it has spare turns. The second troll does not
exist yet in this window (median training turn 26, see §4) — turns 1–12 belong to the starting
troll alone in the great majority of games.

**Most common action for the starting troll, by turn (159 games):**

| turn | dominant action | share | what else happens |
|---|---|---|---|
| 1 | MOVE (to a shack door) | 159/159 (100%) | — |
| 2 | PICK (a seed) | 129/159 (81%) | 25 still MOVE |
| 3 | MOVE (to the orchard cell) | 95/159 (60%) | 60 already PLANT |
| 4 | MOVE | 95/159 (60%) | 55 PICK (the 2nd seed) |
| 5 | MOVE | 116/159 (73%) | 31 PLANT |
| 6 | MOVE | 107/159 (67%) | 23 PICK, 17 PLANT |
| 7 | MOVE | 84/159 (53%) | 56 PLANT |
| 8 | MOVE | 91/159 (57%) | 52 PICK |
| 9 | MOVE | 103/159 (65%) | 35 PLANT |
| 10 | MOVE | 101/159 (64%) | 30 PICK, 14 PLANT |
| 11 | MOVE | 119/159 (75%) | 13 PLANT, 13 DROP |
| 12 | MOVE | 105/159 (66%) | 22 PLANT, 16 PICK |

**The orchard finishes early**: the first orchard PLANT (a lemon or plum, at a door or one
step off it) lands at a **median turn of 5** (154/159 games plant at least one). All three
orchard seeds are typically down by turn 9–12. So the planting itself is *not* late — the
owner's "plant" step happens right at the start, before any real gathering. What eats turns 1–12
is walking between the shack (to pick a seed) and the orchard cell (to plant it) three separate
times, one seed per trip, rather than picking two seeds in one visit (the bot's PICK candidate
only ever asks for one item at a time — see §5).

The shack inventory at turn 1 already holds the full random starting draw (typically ~5–10 of
each fruit, ~4–6 iron); by turn 12 it is basically unchanged from turn 1 except for the 2–3
seeds withdrawn for planting — the bill's real accumulation has not started yet in this window
(see §4).

The second troll's talents, once trained, vary game to game (the opening search picks the
strongest affordable build): the six most common are (speed, carry, harvest, chop) =
(2,2,1,2) in 24 games, (2,1,1,2) in 21, (1,2,1,2) in 14, (2,3,1,2) in 10, (2,1,1,3) in 9,
(2,2,1,1) in 8 — a long tail of other combinations fills the rest of the 149 games that get one.

---

## 2. The planting

- **509 orchard plantings** (LEMON or PLUM, placed while we still had fewer than 3 own trolls)
  across 159 games — **3.2 per game**, slightly above the designed 3 (2 lemon + 1 plum);
  the extra ~0.2/game is occasional replanting before the "orchard raided" flag trips.
  328 lemon, 181 plum.
- **Distance to the shack**: 397/509 (78%) are planted exactly on a door (distance 0), 103
  (20%) one step further, 9 (2%) two steps — matching the "the doors are the orchard" design
  exactly.
- **Timing**: first orchard planting median turn 5, the full set typically down by turn ~13
  (the aggregate median planting turn including 2nd/3rd seeds is 13). A late tail exists
  (max turn 293) — almost certainly a *replant* after the opponent razes an orchard tree, not
  the initial planting.
- **A separate, later planting habit exists and is out of scope here**: 1,197 more PLANT
  commands (mostly BANANA 813, APPLE 331, turn range 48–296) come from the persistent-
  regeneration feature that replants whatever it just chopped, unrelated to the third-troll
  orchard. I excluded these from the "orchard" count above; flagging them so the ~3.2/game
  figure isn't confused with the ~10.5/game of all PLANT commands in the raw log.
- **Fruit lifecycle per planted tree (first fruit turn, first-harvest turn, opponent-stolen or
  never-harvested fruit) — not built**: this needs a per-cell fruit ledger across the whole
  game and I did not have time to build it this session. What I do have: of the 1,282 HARVEST
  commands that landed on an orchard cell, 787 (61%) caught it at 1 fruit, 213 (17%) at 2, and
  282 (22%) waited for a full 3 — so orchard trees are being worked steadily, not left standing
  full and idle, but I cannot say how much orchard fruit, if any, rotted unpicked or went to the
  opponent. **This is the thinnest part of the read; flagged rather than guessed.**

---

## 3. The gathering, turns 1–130 (funding is essentially always over by turn 130 — max
observed third-troll turn was 199, so a few very slow games run past this window; capping there
kept the run fast without losing the funding phase for 99%+ of games)

**Where the troll-turns go** (own troll-turns tallied by role: A = starting troll, B = second
troll, C = third troll once it exists; a troll-turn is one unit's one command on one turn):

| role | troll-turns | MOVE | CHOP | DROP | HARVEST | WAIT | MINE | PLANT | PICK |
|---|---|---|---|---|---|---|---|---|---|
| A (starting) | 20,232 | 61.1% | 12.2% | 9.4% | 6.5% | 4.3% | 2.4% | 2.2% | 1.9% |
| B (second) | 16,308 | 58.7% | 13.3% | 14.1% | 7.2% | 2.1% | 4.2% | 0.2% | 0.2% |
| C (third, once trained) | 4,811 | 45.9% | 43.2% | 10.1% | 0% | 0.4% | 0% | 0.2% | 0.2% |

Three things stand out:

1. **Walking is the largest single line item for every troll, by far** — roughly 6 turns in 10.
   Gathering itself (HARVEST + MINE + PICK + PLANT + DROP) is 20–25% of a troll's time; the
   rest is getting there and back.
2. **Troll C (the lumberjack, harvest power 0) never harvests** — the instant it's trained it's
   already in the wood economy (43% CHOP). Its presence in this table for turns ≤130 also
   means some of A's and B's CHOP share above is *after* the bill was already paid (post-
   funding, same window) or from the ~16% of games where funding was abandoned and the bot
   fell back to chopping early (see §4) — **I did not separate "chop before the third troll
   existed" from "chop after," which would sharpen this; flagged as a gap.**
3. **Explicit idling is small**: 1,230 WAIT troll-turns across 159 games (≈7.7/game, about 3%
   of all troll-turns), and 78% of those (956) are a troll parked on a tree with 0 fruit,
   clearly waiting out the regrowth clock rather than aimless idling elsewhere (274 turns).

**HARVEST, in detail** (2,484 events, turns ≤130):

- 1,282 (51.6%) on an orchard tree, 1,202 (48.4%) on a wild tree.
- Fruit count on the tree *before* the harvest: 1 fruit → 1,071 (43.1%), 2 fruits → 381
  (15.3%), a full 3 → 1,032 (41.5%). Orchard trees specifically skew towards small pickups:
  787/1,282 (61%) harvested at just 1 fruit.
- **Wild-tree harvest distance from the shack** (steps, walking distance): a wide spread —
  195 at distance 0, 216 at 1, 194 at 2, 199 at 3, then a real tail: 103 at 4, 80 at 5, 73 at 6,
  44 at 7, 66 at 8, and smaller counts out to 9, 10, 11, 12, 13, and even **16 (twice) and 24
  (once)**. **295 of 1,202 wild harvests (24.5%) happen 5 or more steps from the shack** — each
  one a multi-turn walk out and a multi-turn walk back, usually for a single fruit, while the
  orchard sits at distance 0–1.

**DROP, in detail** (4,687 events, turns ≤130): **3,627 (77.4%) carry exactly one item**; only
1,060 (22.6%) bring back two or more. Given that carry capacity 2–3 is common among the talent
builds actually trained (§1), this means the large majority of trips to the shack are not
using the capacity the troll was trained with.

**MINE**: 1,176 events (7.4/game) — expected, since all 159 games in this batch are iron maps.

---

## 4. The bill's progress

The third troll's bill (talents 2/3/0/3, or a cheaper axe when iron is far — see below) is
**6 plum, 11 lemon, 2 apple, 11 iron** (from `training_cost(n=2, ms=2, cc=3, hp=0, chop)`).
Bill progress was sampled every other turn while we held fewer than 3 own trolls (a speed/
completeness tradeoff); "turn requirement first met" is accurate to within about one turn.

**Turn each item's requirement is first met** (among the 134 games that trained a third troll):

| item | required | median turn met | mean | earliest | latest | games with data |
|---|---|---|---|---|---|---|
| PLUM | 6 | **1** | 27 | 1 | 199 | 124/134 |
| APPLE | 2 | **1** | 1 | 1 | 1 | 134/134 |
| IRON | 11 | **53** | 54 | 18 | 135 | 97/134 |
| LEMON | 11 | **77** | 84 | 47 | 191 | 85/134 |

**Lemon is the binding constraint, iron is the secondary one; plum and apple are essentially
free** — the random starting draw (expected ~24 fruit total, split four ways) almost always
already covers 6 plum and 2 apple, so those two numbers in the bill table are close to
decoration. The whole ~88-turn median wait (see below) is really a wait for 11 lemon and, in
parallel, 11 iron (gathered 1–3 at a time per MINE, per §3).

**Training timing**:

- Second troll: trained in 149/159 games (93.7%), median turn **26**.
- Third troll: trained in 134/159 games (84.3% of all games, 89.9% of games that got a second
  troll), median turn **88**, range 51–199.
- **283 TRAIN commands total (149 + 134), 0 failed** (every TRAIN that was issued produced a
  new troll on that same turn — the engine-level accounting balances exactly: e.g. in the
  worked example below, training the third troll deducts exactly 6 plum / 11 lemon / 2 apple /
  11 iron from the shack, to the unit).
- **The owner's suspected PICK-before-TRAIN ordering bug does not occur**: across all 283
  TRAIN commands in 159 games, **0 turns** had us also issue a PICK command that same turn. The
  bot's own logic already avoids this — the turn it decides to TRAIN, it stops generating PICK
  commands for that turn (the `early` candidate path that produces fruit/iron PICKs is switched
  off exactly when `train_now` is true). So this specific fine-order concern is not what is
  costing turns.
- **No meaningful delay between "bill complete" and "TRAIN fires"**: in the (smaller, n=36)
  sample where the completion turn could be pinned exactly from the sampled points, the gap was
  0 turns at the median. The bottleneck is the **income rate**, not decision latency — the bot
  spends the resources the instant it has them.
- **Talents actually trained for the third troll**: (2,3,0,3) in 98/134 (73%), (2,3,0,2) in
  31/134 (23%), (2,3,0,1) in 5/134 (4%) — this is the "cheaper axe when iron is far" rule
  firing (chop 3 within 5 steps of a door, chop 2 within 10, chop 1 within 16, from
  `IRON_STEPS_FOR_CHOP` in the source), working as designed.
- **25/159 games (15.7%) never fund a third troll at all**; 10 of those never even get a second
  troll. Several of the no-third-troll games show us far behind on score by the time the batch
  was collected (opponent 272–531 vs our 73–184) — consistent with being beaten to the wood
  race before funding finished, not with the funding logic itself malfunctioning. One
  no-third-troll game ends at turn 30 (a very short, likely-forfeited game) — a corpus
  oddity, not a funding story.
- **What the trolls do while nothing useful is possible**: overwhelmingly, park on a barren
  (0-fruit) tree and re-issue HARVEST/wait for the regrowth clock (§3) rather than idling
  elsewhere — 956 of 1,230 explicit-idle troll-turns.

---

## 5. The inefficiencies, ranked (each with a number; "turns lost" estimates are explicitly
approximate where marked)

| # | inefficiency | hard number | rough cost |
|---|---|---|---|
| 1 | **One-item trips** | 3,627 of 4,687 drop-offs (77.4%) carry a single item, despite the trained talents commonly giving 2–3 carry capacity | the largest, most confident finding; every such trip re-pays the full round-trip walk for one unit of goods |
| 2 | **Walking dominates everything** | 61%, 59% and 46% of A's, B's and C's troll-turns respectively are MOVE, vs. 20–25% on any gathering action | walking is not "wasted" by itself, but it is the resource that (1) squanders — each avoidable extra trip is mostly walking |
| 3 | **Partial-tree harvesting** | 43.1% of all 2,484 HARVEST commands fire at exactly 1 fruit on the tree; only 41.5% catch a full 3 | ambiguous cost (leaving fruit to ripen has its own opportunity cost) but it does mean most trips bring home a fraction of a tree's yield |
| 4 | **Far wild-tree trips while the orchard sits at the door** | 295 of 1,202 wild harvests (24.5%) are 5+ steps from the shack, up to 16 and 24 steps in two cases, vs. the orchard's distance 0–1 | rough: a 24-step one-way trip alone is ~24–48 turns of walking (speed 1–2) against an ~88-turn median funding window, for what is usually a 1–3 fruit gain |
| 5 | **Idle waiting** | 1,230 explicit WAIT troll-turns / 159 games = 7.7/game, ≈3% of all troll-turns, 78% of it parked on a barren tree waiting for regrowth | small; not a major time sink by this measure |
| 6 | **Doors / trolls blocking each other** | 61 "stuck" MOVE commands (issued a move, landed on the same cell) out of 24,136 MOVE commands = **0.25%** | negligible — the joint move-conflict resolver in the code is doing its job |
| 7 | **PICK/TRAIN misordering** | **0** of 283 TRAIN commands co-occurred with a PICK | does not occur — the design already prevents it (§4) |
| 8 | **Late planting** | median first orchard plant at turn 5, all three seeds down by ~turn 13 | not late — the opposite of the owner's hypothesis for the *initial* planting specifically |
| 9 | **The protected-tree rule blocking useful chops** | by design, no wild/orchard tree is chopped while funding is active and reachable | real (it is a deliberate denial-avoidance trade, not a bug) but **not quantified here** — would need a "wood we could have banked instead" counterfactual, out of scope this session |
| 10 | **CHOP during the funding window** | 12.2% (A) / 13.3% (B) of troll-turns ≤130 are CHOP | **not cleanly attributable** — mixes wood-economy time *after* the bill was already paid within the same 130-turn window and the ~16% of games where funding was abandoned; flagged rather than blamed |

**The clearest, best-supported fix targets are #1 and #4**: trips that bring back one item when
the troll can carry two or three, and long solo detours to a wild tree while three ripe,
zero-distance orchard trees may be sitting untouched. Both are directly visible in the PICK/
HARVEST/DROP candidate scoring (`fruit_candidates`, `bank_candidates` in
`local_claude_1/third-troll/orchard6-readable.rs`), which scores every candidate turn by turn
rather than planning a multi-fruit round trip.

---

## 6. One median game, told plainly: game 900768779 (turns 1–90)

This is the game whose third-troll training turn (88) sits at the median of all 134 games that
funded one — chosen for being typical, not for a good outcome (this particular game was in fact
a **loss**, 300 to 311, decided later in the game, unrelated to the funding phase itself). Our
seat was player 1; shack at (15,6).

- **Turn 1**: the starting troll (call it Alpha) already holds a decent starting draw — 7 plum,
  5 lemon, 10 apple, 10 banana, 4 iron sitting in the shack, more than enough plum and apple for
  the eventual bill. Alpha walks toward a shack door.
- **Turn 2**: Alpha PICKs a lemon seed from the shack (lemon 5 → 4).
- **Turns 3–8**: Alpha walks to the orchard cell.
- **Turn 9**: **PLANT** — the first lemon goes into the ground.
- **Turn 10**: Alpha PICKs a second lemon seed (a plum seed goes down too a little later, off
  the sampled turns).
- **Turns 11–29**: Alpha shuttles between the orchard cell and nearby cells, planting the
  remaining seeds and doing a little early iron mining and fruit fetching (plum climbs from 7
  toward the bill's 6-and-done, iron creeps from 4 to 5) — no second troll yet, so this is one
  troll covering both planting and the start of gathering.
- **Turn 35**: **TRAIN 2 1 1 2** fires — the second troll (call it Bravo, speed 2 / carry 1 /
  harvest 1 / chop 2) is born. The training cost (plum 5, lemon 2, apple 2, iron 5 at n=1) is
  deducted exactly: plum 6→1, apple 10→8, iron 5→0 (visible at turn 40's inventory).
- **Turns 40–85**: Alpha and Bravo split the work — both mine iron (Bravo: MINE/DROP cycles at
  turns 45–80; Alpha: MINE at turn 60, DROP at 55/65) and fetch lemon (Bravo HARVESTs at turn
  70, both keep moving). Iron climbs steadily (0→2→4→5→7→10→11→12, overshooting the 11 needed
  by one because a mining trip brings back 2 at a time). **Lemon is the slow one**: 3 → 3 → 4 →
  4 → 5 → 5 → 6 → 9 → 11, only crossing the required 11 around turn 78–80, matching the
  aggregate median of 77 almost exactly.
- **Turn 88**: shack holds plum 6, lemon 11, apple 8, iron 12 — the bill (6/11/2/11) is met on
  every count. **TRAIN 2 3 0 3** fires immediately, no turns wasted waiting once the last
  requirement (lemon) is in hand. The cost (plum 6, lemon 11, apple 2, iron 11 at n=2) is
  deducted exactly, visible at turn 90: plum 6→0, lemon 11→0, apple 8→6, iron 12→1.
- **Turn 90**: the new third troll (Charlie, 2/3/0/3) is already CHOPping wood, two turns after
  being born — no ramp-up, straight into the wood economy, same as Alpha (also CHOP by turn 90).

The shape matches the aggregate exactly: seeds down almost immediately (turn 9 here vs. median
5), lemon is the pacing item (turn ~80 here vs. median 77), no gap between "bill complete" and
"TRAIN fired," and the third troll starts chopping within two turns of existing. The visible
inefficiency in this specific game's early window is the same as the aggregate's #1 and #2: a
lot of single-purpose walking (turns 3–8 just to reach the orchard, turns 11–29 shuttling one
seed/one fruit/one load of iron at a time) rather than combined trips.

---

## Where this read is thin (say so plainly)

- **No iron-free maps** in this 159-game batch — the iron/iron-free split the brief asked for
  could not be done; every number above is really "on iron maps."
- **Fruit lifecycle per orchard tree** (first-fruit turn, first-harvest turn, unharvested or
  opponent-harvested fruit) was not built — see §2. The harvest-yield distribution stands in for
  it but does not answer "did fruit rot."
- **CHOP turns are not split by before/after the third troll's training turn** (§3, §5 #10),
  so the 12–13% CHOP share for the first two trolls during the "funding window" mixes real
  early chopping (rare/abandoned-funding games) with ordinary post-funding wood economy inside
  the same fixed 130-turn cutoff.
- **The protected-tree rule's cost** (#9) — wood left un-chopped while funding is active — is
  not quantified; would need a wood-value counterfactual.
- **Bill-progress sampling is every other turn**, so "turn item X was met" is accurate to about
  ±1 turn, and coverage of the IRON/LEMON completion-turn tables is 97/134 and 85/134 games
  respectively (the rest crossed the requirement at a turn outside the sampled points, most
  likely right around the TRAIN turn itself).
