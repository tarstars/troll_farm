# DOMAIN — what has been learned about this game, with the evidence for each line

Results only. Nothing here is a design, an architecture, or an instruction — these are things
that were measured, each with the evidence behind it, so you do not have to rediscover them.

**Evidence levels used below:**

- **LADDER** — measured on the real ranked ladder, against real opponents. The strongest kind.
  A single ladder reading has a noise band of about +/- 1.5 rating points, so differences under
  3 points from one reading are not conclusions.
- **CORPUS** — measured over a large body of recorded real matches (23,613 matches, 13.3 million
  seat-turns, collected 2026-08-26). Strong for *what bots do*; it records the commands bots
  issued, not whether the referee accepted them.
- **BENCH** — measured in a local simulator against local opponents. **Weakest.** The bench has
  disagreed with the ladder by wide margins more than once; see §4.

---

## 1. What the strong players do — CORPUS

Twenty-five strong two-worker players in the top ranks were compared with the reference bot over
the recorded corpus. Four things came out.

### 1.1 Wood is the game. Fruit is not. — CORPUS

For every strong player measured, **more than 90 % of the final score is wood**:

| player | matches | score per match | of which fruit | of which wood |
|--------|--------:|----------------:|---------------:|--------------:|
| skotz   | 184 | 269.7 | 8.1  | 261.6 |
| yaichi  | 222 | 252.4 | 7.2  | 245.2 |
| goq     | 269 | 247.6 | 10.8 | 236.8 |
| Stounate| 303 | 198.7 | 17.3 | 181.4 |
| *the reference bot* | 10,274 | 187.4 | 5.4 | 182.0 |

Fruit is a currency (for training and for seeds), not a score.

### 1.2 Every strong player buys the same second worker — CORPUS

Of the strong two-worker players, the second worker bought is
**speed 2, carry 2, harvest 0, chop 2**, and they almost never go below it: six of the seven
measured leaders bought a weaker worker in 0 % of their matches, the seventh in 5 %. Bigger
workers appear only far down the ranks and carry less wood. Harvest power on a second worker
appears only in the middle of the ladder.

The reference bot fields a **weaker** worker than 2/2/0/2 in 37–45 % of its matches: when it
finally buys, it takes the best bundle affordable at that moment, and by its deadline it often
accepts one below 2/2/0/2 (`CHAMPION-BEHAVIOUR.md` A3 — it also often waits with a weaker bundle
already affordable, for reasons the recordings do not show). In one collected batch, the matches
where it fielded a weaker worker were won 34 % of the time against 66 % for the matches where it
did not, at the same training turn.

**But making it wait for that worker was tested on the ladder and lost** — see §2.

### 1.3 The strong players run a *renewable* wood farm from turn 1 — CORPUS

Banana PLANT commands per match, by phase:

| player | turns 1–50 | 51–100 | 101–150 | 151+ | total |
|--------|-----------:|-------:|--------:|-----:|------:|
| skotz   | 4.82 | 6.39 | 6.73 | 18.26 | 36.20 |
| yaichi  | 5.87 | 6.13 | 5.19 | 11.83 | 29.03 |
| goq     | 3.17 | 4.65 | 3.70 | 16.04 | 27.57 |
| Stounate| 4.54 | 5.27 | 4.08 | 13.38 | 27.26 |
| *the reference bot* | **0.05** | 0.32 | 0.88 | 4.74 | **5.98** |

And what they do with those trees afterwards:

| player | HARVESTs on its own planted cells | CHOPs on its own planted cells | mean turns from planting to chopping |
|--------|----------------------------------:|-------------------------------:|-------------------------------------:|
| skotz   | 30.20 | 67.23 | 25.6 |
| Stounate| 28.65 | 39.83 | 53.9 |
| goq     | 22.87 | 67.34 | 40.2 |
| yaichi  | 21.12 | 59.53 | 25.8 |
| *the reference bot* | **2.85** | 47.08 | **4.6** |

That last column is the sharpest single number in this document. The strong players plant a
tree, **let it grow for 25–54 turns**, harvest fruit off it — which reseeds the loop — and then
fell it for its full size in wood. The reference bot plants and chops **4.6 turns later**, at
size 1, for one wood, and almost never harvests what it planted.

**This is the largest known gap between the reference bot and the field, and it is unexploited.**
Two attempts at closing it are in §2; both failed for reasons that are recorded, and neither
attempt was the loop above.

### 1.4 The strong players do not win by chopping the opponent's plantings — CORPUS

CHOP commands issued at a coordinate the *opponent* had planted, per match: the strong players
0.53–2.46; the reference bot **8.73**. Whatever the leaders' advantage is, it is not that they
destroy the opponent's plantings more. Other ways of interfering — racing to trees, blocking,
harvesting or standing on the opponent's trees — were not measured here.

Removing the reference bot's one rule that singled out the opponent — it preferred chopping the
opponent's plums and lemons near their shack early — changed its ladder reading by less than the
noise band, and
the simpler bot became the reference. **LADDER.**

---

## 2. Tried on the ladder, and what it read

Each line: the behavioural idea, then its ladder reading. The reference bot's own readings, for
scale, are **21.8, 21.6, 22.1** and, after that opponent-targeting rule was removed, **21.2**.
The field
drifts: the same bot re-read **18.2** the next day without changing. **Compare readings only
against readings taken the same day.**

| idea (behaviour only) | ladder reading |
|-----------------------|----------------|
| **Never buy a worker weaker than speed 2 / carry 2 / chop 2 — wait for it** | **19.2, 19.1, 17.3** — 2 points below the reference, three readings. Every worker was floored and the waiting cost more than the stronger worker paid back; in 2 of 160 matches it never trained at all. |
| **Buy a third worker, both existing workers fund it** | **11.3** — retired after 35 minutes. The third worker arrived in 40 of 106 matches; those won 65 % against 32 % without it — but the ~100 turns spent funding it lost the matches outright. |
| **A third worker, and nobody chops until it is trained or is unreachable** | **11.7, 12.0** — the third worker came in 89 % of matches at median turn 113, and the funding still lost. |
| **Plant four lemons and two plums together at the entrance farthest from the enemy, to feed the third worker** | **14.7, 13.5** (an earlier form), **18.8** (a later form), **16.7, 16.6** (a further form). The best of these is still below the reference. |
| **Plant a persistent banana crop in a ring around one's own shack** | **10.8** at rank 172 of 176. It planted 16 bananas a match and harvested 4.8 from them; the opponent walked onto the ring and ate the crop in 35 of 50 newly-blocked matches. **A crop next to your own door does not protect itself — the opponent will pay the walk.** |
| **An apple-focused farm** (the starting troll plants an apple near its shack on its first turns, then plays as the reference does) | **19.8, 19.8, 18.6, 19.9** on the day the reference read 21.2, then **17.6** the next day when the reference re-read 18.2 — about 1.5 below the reference on both days, at the edge of the noise band. |
| **Remove the reference bot's early opponent-targeting rule** | **21.2** vs the previous 21.8/21.6/22.1 — inside the noise band. Simpler and no worse; this became the reference bot. |

**The single strongest pattern in that table:** every attempt to buy more workers, or to spend
early turns building toward them, has read far below the reference. The two-worker,
fell-what-is-already-there strategy is a hard floor that nothing has yet beaten on the ladder.

---

## 3. Behavioural findings worth knowing — mixed evidence

- **Never abandon an opening plan half-done.** A variant that spent its starting fruit on
  planting and then abandoned the plan when a deadline passed ended up with **one worker for the
  whole match in 10 of 160 matches**. Making it finish what it started reduced that to **1 of
  160**. The lesson generalises: a plan that spends a resource and then quits leaves you with
  neither the resource nor the plan. **LADDER.**
- **Carry capacity caps a felling.** When a tree dies, its wood is dealt one at a time to each
  chopper that still has free carry. A worker with carry 1 standing on a dying size-4 tree takes
  **one** wood and the rest is lost. Match the worker's carry to the trees you intend to fell.
  **RULE (referee).**
- **Two workers on one tree is not obviously good.** The last fruit and the last wood duplicate
  (RULES §7), which means an *opponent* sharing your tree gets a free item from you.
- **Reversing direction is a symptom.** A variant that made workers hold their chosen target
  reversed direction 16.1 times per 100 moves against the reference bot's 11.95; the reference
  bot's own rate is flat across its wins (11.87) and its heavy losses (11.53), so a high reversal
  rate is not simply what losing looks like. The measurement was **under-determined** as a cause
  (208 matches against 4) and no conclusion was drawn. **CORPUS, inconclusive.**
- **Matches end early, often.** Of 160 reference-bot matches, only 73 ran the full 300 turns; the
  shortest ended at turn 81. Felling the last tree on the map starts the ending clock
  (RULES §11), so a bot that logs the map out fast ends the match at whatever score it has.

---

## 4. Two warnings about measurement, both paid for

**The local bench has been wrong about the ladder, by a lot.** A change was benched at
**0 wins and 6 losses, −150.7 points a match** and predicted to collapse on the ladder; on the
ladder it read **21.2 against the previous 21.8/21.6/22.1** — no drop at all, and it became the
reference bot. In another case the bench said a behaviour "never ran" while on the ladder it ran
about 65 turns in every single match. The bench's maps and opponents are not the ladder's.

**Treat a bench result as a validity check — does it play legal, complete matches, does the
behaviour appear at all — and never as a verdict on strength.**

**A single ladder reading is worth about +/- 1.5 points.** Two readings 1 point apart are the
same number. Three readings 2 points below a reference are a result.

---

## 5. Map statistics

- Height is drawn uniformly from 8..11 and width is twice the height, so the four map sizes are
  16x8, 18x9, 20x10, 22x11, each about a quarter of matches (measured over 160: 33/43/45/39).
- Both players' starting stock is the **same draw**: five independent uniform draws from 2..10
  for plum, lemon, apple, banana and iron. Expected starting fruit **24**, expected iron **6**.
  Your starting score is therefore not zero, and it is equal to the opponent's.
- Trees on the map at the start: on the order of 8–24, varying with map size, each aged a random
  number of ticks so they begin at assorted sizes and fruit counts.
- The map is point-symmetric, so any positional advantage you can see, the opponent has a mirror
  image of.
