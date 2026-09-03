# How the strongest real players fund their trolls — the fine order, from data

Owner's question (verbatim intent): the resource-collection algorithm for the third troll looks
inefficient; "train, plant, gather" must happen in an extremely fine order. This page pulls the
exact turn-by-turn order and timing the four reconstructed top players actually used, in plain
words with numbers, so the order can be copied.

**Scope and honesty note.** Nothing here was re-queried from the raw per-turn corpus
(`data/processed/turns.jsonl.gz`, 13.3M seat-turns) — that would not have fit the time budget and
was not necessary: the reconstruction project already built, and *validated against the referee's
own per-turn diff with 0 disagreements*, exact per-turn states for 782 games of these four bots
(`local_claude_1/reconstructions/fits/README.md`). Every number below is copied from those
validated tables and profiles, with its own file and n. Where a document itself flags a number as
doubtful (a viewer-field artifact) or as a GUESS, that is carried over here. I did not invent or
extrapolate any figure; where the data is thin it says so.

Files read (all inside `/home/tarstars/prj/troll_farm-local_claude_1`, no writes except this one):
`local_claude_1/reconstructions/README.md`, `.../fits/README.md`,
`.../norxondor_gorgonax/ALGORITHM.md`, `.../MSz/ALGORITHM.md`, `.../delineate/ALGORITHM.md`,
`.../Bubaptik/ALGORITHM.md`, `.../profiles/norxondor_gorgonax.md`, `.../profiles/MSz.md`,
`.../profiles/Bubaptik.md` (§2), `.../profiles/delineate.md` (§2),
`local_claude_1/second-troll-census/README.md`, `codex_1/top10/field-comparison-2026-08-26.md`,
`docs/mechanics.md` (lines 40–110: pathing, harvesting, trees/cooldown, training, turn order,
scoring). Commands run: `grep -n '^#' docs/mechanics.md`; `awk '/^## 2\. Opening/,/^## 3\./'` over
`profiles/Bubaptik.md` and `profiles/delineate.md` to pull their opening-pattern tables.

---

## 0. The one mechanical fact that makes "fine order" a real constraint

`docs/mechanics.md` lines 74–76 and 102–107 give the referee's fixed per-turn priority, the same
for both players, every turn:

**MOVE(1) → HARVEST(2) → PLANT(3) → CHOP(4) → PICK(5) → TRAIN(6) → DROP(7) → MINE(8)**

TRAIN "rechecks affordability... at apply time, after MOVE and PICK but before DROP" (line 92–93).
Three consequences follow mechanically (not measured — deduced from the authoritative rule; flagged
as such throughout):

1. **A PICK on the same turn as a TRAIN shrinks the very stock TRAIN is about to check** (PICK is
   priority 5, one step before TRAIN's priority 6). Picking a seed you don't strictly need on a turn
   you might also train can turn an affordable bill into an unaffordable one.
2. **A DROP on the same turn as a TRAIN does not help pay for it** — DROP is priority 7, after
   TRAIN's check. Fruit carried home only counts starting *next* turn. To train on turn T, the
   resources must already be sitting in the shack at the *start* of turn T (banked on turn T−1 or
   earlier).
3. **MINE is last (priority 8)** — mined iron never funds the same turn's TRAIN either.

This matches what all four bots measurably do: every one of them fires TRAIN the instant the
*pre-turn* shack stock clears the bill — "delay 0" in 88–100% of trainings (§5 below) — which is
exactly what the priority order rewards. None of the four documents found evidence of a bot
deliberately avoiding the PICK-before-TRAIN trap; it is presented here as the concrete "fine order"
rule an implementation must respect, not as something the top bots were observed doing on purpose.

---

## 1. Turns 1–10: the literal sequence, with frequency

Letter code (from the profiles): M=MOVE, H=HARVEST, C=CHOP, P=PLANT, K=PICK, D=DROP, I=MINE,
T=TRAIN, W=WAIT. One letter per turn = that troll's command that turn.

### norxondor_gorgonax — start troll, turns 1–10 (n=218 games; `profiles/norxondor_gorgonax.md` §2)

| pattern | games | share |
|---|---:|---:|
| `M K P K M P M M M M` | 22 | 10.1% |
| `M K P M M M M M M M` | 15 | 6.9% |
| `M K P M M K P M M M` | 12 | 5.5% |
| `M K P M M M M M H M` | 10 | 4.6% |
| `M K P M M M M H M M` | 8 | 3.7% |
| `M M M M M M H M M M` (no plant yet) | 8 | 3.7% |

Read as prose: **move off the shack (T1) → PICK a seed (T2) → PLANT it next door (T3) → move/wait
→ PICK again (T5–6) → PLANT again (T6–7)**, first HARVEST arriving around turn 8–11 in the
commonest lines. Verb-share-by-turn confirms this at the population level: turn 1 is 100% MOVE (plus
TRAIN in 46% of games — the turn-1 buyers); turn 2 is 72% PICK; turn 3 is 71% PLANT; first HARVEST
column only reaches double digits (12–36%) from turn 8 on. First action of the start troll: PICK in
71.6% of games, HARVEST in 28.4% (never PLANT or TRAIN first — the troll always leaves the shack
before doing anything else, since PICK/PLANT/HARVEST/TRAIN all require standing on or next to the
right cell and the troll spawns on the unwalkable shack cell). First harvest is of a **wild** tree in
97.7% of games (plum 40%, lemon 40%, apple 17%, banana 2%) — i.e. the first fruit that funds the
economy never comes from the seed just planted (see §3 on why: a fresh seed needs many turns to
bear fruit). First plant is LEMON in 62%, PLUM in 34%.

### MSz — start troll, turns 1–10 (n=216 games; `profiles/MSz.md` §2)

| pattern | games | share |
|---|---:|---:|
| `M K M P M K P K M P` | 15 | 6.9% |
| `M K P K M P M K P K` | 13 | 6.0% |
| `M K P K M P M K M P` | 9 | 4.2% |
| `M K M P M K M P M K` | 9 | 4.2% |
| `M K P K M P C M K P` (a chop appears by T7) | 6 | 2.8% |

Turn 1 is 99% MOVE + **97% TRAIN** (the turn-1 second troll, see §2) — the shack itself issues TRAIN
while the start troll is already moving off it (this is legal: TRAIN is a shack-level command, not
tied to the troll being on the shack cell). Verb share: turn 2 is 93% PICK; turns 3–4 alternate
PICK/PLANT (share of PLANT 0.46 at T3, 0.72 at T4); first PLANT median turn 4 (mean 3.63). First
action of the start troll is PICK in 94.4% of games (HARVEST 3.7%, MINE 0.9%, CHOP 0.9%). First
harvest wild in 89.4% of games (lemon 43%, plum 35%, apple 15%). This is the fastest planter of the
four: **3.89 plants in turns 1–10 alone** (vs. norxondor 1.68, delineate ~1, Bubaptik ~0.5).

### Bubaptik — start troll, turns 1–10 (n=191 games; `profiles/Bubaptik.md` §2)

| pattern | games | share |
|---|---:|---:|
| `M M K P K M P M M M` | 19 | 9.9% |
| `M M K P K M P M K P` | 16 | 8.4% |
| `M M K P K M P M K M` | 12 | 6.3% |
| `M M K P M M M M M M` | 9 | 4.7% |

Turn 1 is pure MOVE (the start troll steps off the shack); the shack-level **TRAIN fires on turn 2**
in 83% of the "all trolls together" turn-2 column. First action of the start troll is PICK in 74.3%,
HARVEST in 24.1%. First plant is PLUM in 64.4% (Bubaptik is the only one of the four whose first
seed is usually a plum, not a lemon — it is funding **speed 4**, priced in plums, where the other
three fund carry). First harvest wild in 91.1% (lemon 46%, plum 44%).

### delineate — start troll, turns 1–10 (n=223 games; `profiles/delineate.md` §2)

| pattern | games | share |
|---|---:|---:|
| `M K P K M P M M M M` | 17 | 7.6% |
| `M M M H M M D M M H` (mine-then-harvest opening) | 12 | 5.4% |
| `M K P K M P M K P M` | 10 | 4.5% |
| `M M M M M M M M M M` (pure scouting/idling) | 8 | 3.6% |
| `M M M I M M D M M I` (mining opening) | 4 | 1.8% |

delineate is the least uniform opener of the four: first action PICK only 46.2% of the time,
HARVEST 37.2%, **MINE 13.9%** (it is the only one of the four whose start troll sometimes mines
before it plants or harvests anything). Turn-1 TRAIN in only 5.8% of games (13/223) — it is the
slowest of the four to train its second troll (median turn 6–7, mean 19.9, because in over half the
games it waits past turn 25). First plant LEMON 66.8%, first harvest wild in 87.9%.

**Cross-bot pattern.** All four open with the identical skeleton **MOVE off the shack → PICK a seed
→ PLANT it adjacent → (PICK/PLANT again) → first HARVEST from a nearby wild tree around turn 8–11**,
differing only in (a) whether TRAIN is issued turn 1 (MSz always, norxondor 41%, Bubaptik turn 2
always, delineate rarely) and (b) plant kind (lemon-first for norxondor/MSz/delineate, plum-first
for Bubaptik, matching what each is funding — see §2).

---

## 2. The second troll — funded by the starting draw, not by anything gathered

| bot | median TRAIN-2 turn | first HARVEST (median) | first DROP (median) | funded by |
|---|---:|---:|---:|---|
| MSz | **1** (214/216 games) | 9 | 15 | starting draw only — mechanically forced: the shack has received zero fruit by turn 1 |
| Bubaptik | **2** (154/186 first purchases exactly on T2) | 9–11 | 17–19 | starting draw only — same mechanical reason |
| norxondor_gorgonax | 9 (turn-1 in 76/184 = 41%) | 8–9 | 17 | the draw alone when turn-1 test passes (41%); draw + a first quick harvest/drop for the slower 59% |
| delineate | 6–7 (turn-1 in only 13/223 = 5.8%) | 9 | 11 | the draw alone in the typical case (median TRAIN-2 turn precedes median first-DROP turn); a slower tail funds partly from gathered fruit |

This is a clean, mechanically-forced finding: three of the four bots' median second-troll purchase
happens at or before their own median first-DROP turn, so **the second troll is paid almost
entirely out of the shack's starting inventory** (2–10 units of each fruit/iron, `docs/mechanics.md`
line 15–18), never out of anything the trolls collect. What differs between bots is only the *rule*
for reading that starting draw:

- **MSz** (exact, 196/196 turn-1 trains; `MSz/ALGORITHM.md` §Phase 0): speed 2 iff plums≥5 else 1;
  carry 2 iff lemons≥5 else 1; harvest 2 iff apples≥5 **and** carry=2, else 1; chop always 1.
  Cost check: speed 2 at n=1 troll = 1+2²=5 plums — exactly the threshold, so the rule is just "buy
  the level the single-resource cost formula affords."
- **Bubaptik** (147/154 exact on turn 2): the highest level *each resource alone* affords
  (`1+k²≤stock`), independently per talent — talents end up `2 2 2 2`, `2 2 1 2`, `1 2 2 2`, etc.
  depending on the 2–10 draw of each resource.
- **norxondor** (76/76 and 0/108 exact split, reviewer-verified): an all-or-nothing floor test —
  train **2/2/1/1** (needs plums≥5, lemons≥5, apples≥2, iron≥2 simultaneously; cost at n=1:
  1+2²=5, 1+2²=5, 1+1²=2, 1+1²=2) turn 1 if every resource clears at once, else wait; talents then
  raised to whatever the stock affords, capped.
- **delineate**: no exact turn-1 rule found; each talent = the largest level the shack affords
  (`prior-art.md` 22/26 games), but it is rarely affordable turn 1 so it waits (median turn 6–7).

Talent mix at troll 2 (most common): norxondor `2/2/2/2` 41%, `2/2/1/2` 19%; MSz `2/2/2/1` 31%,
`2/2/1/1` 18%; delineate `2/2/2/2` 45/223, `2/2/1/2` 23/223; Bubaptik `2/2/2/2` 18/154,
`2/2/1/2` 16/154. All four buy a **hybrid** (some harvest and/or some chop), never a pure specialist,
for troll 2.

**Context on our own bot** (not part of the reconstructions, but on file):
`local_claude_1/second-troll-census/README.md` measured our own lineage's second troll at mean
training turn 8.7 — already close to norxondor's 9 — but **below the `2/2/0/2` floor in 37% of the
covered talent vectors** (weaker in speed, carry or chop than the top bots ever buy), and the
within-batch A/B in that same file shows a floored-or-better second troll winning 66% vs. 34% for a
weaker one on the identical map/draw (n=159 real games). None of the top four ever buys a troll
weaker than `2/2/·/·` at position 2.

---

## 3. Planting

| bot | plants/game | first plant turn (median) | cell rule (accuracy) | kind order | water-adjacent |
|---|---:|---:|---|---|---:|
| norxondor | 29 | 3 | free cell min. d(shack)+d(troll): 86.7% | lemon 35%/plum 32%/banana 26%/apple 7% (banana only from ~turn 100) | 22.6% (no preference; apple 43%) |
| MSz | 29.5 | 4 | same rule: 77.6% | banana 39%/lemon 33%/plum 17%/apple 11% | 19.5% (apple 46%) |
| delineate | 39.7 | 5 (median first-plant turn 5 in profile; 3 in the fits table) | same rule: 89.9% | banana 48%/lemon 28%/plum 19%/apple 4% (banana explodes after turn 100) | 23% (not sought; rejected as a rule) |
| Bubaptik | 28.8 | 4 | same rule: 84.2% | plum 47%/lemon 30%/banana 21%/apple 2% | 23% |

All four are fit best (78–90% teacher-forced) by **the identical rule**: plant on the empty grass
cell that minimises (BFS distance to shack) + (BFS distance to the acting troll) — i.e. "the free
cell nearest to both home and the seed-carrier." Never farther than 4–6 cells from the shack; the
large majority (57–91% depending on bot) land at distance 1–2. The kind planted tracks which talent
is next being funded (lemon/plum first everywhere except Bubaptik, which funds speed with plums
first); bananas are the outlier — planted heavily but for a *different* purpose (§5's plant-and-cut
loop for norxondor; a fast late crop for MSz/Bubaptik; a slow but heavy crop for delineate).

**Distance from own shack, exact (all four; from the profiles' distance tables), share by distance:**

| bot | d=1 | d=2 | d=3 | d=4+ |
|---|---:|---:|---:|---:|
| norxondor | 57% | 21% | 14% | 8% (never >4) |
| MSz | 42% | 49% | 6% | 3% (rarely >4, up to 6) |
| delineate | 43% | 28% | 18% | 11% (up to ~6) |
| Bubaptik | 43% | 25% | 13% | 19% (mean 2.4, tail to 12) |

**Time from planting to first fruit — derived from `docs/mechanics.md` §Trees/cooldown, not directly
measured per-tree in the corpus** (flagged as a mechanical deduction, cross-checked against the
closest measured proxies below). A newly planted size-0 tree ticks on its own creation turn
(line 96), so it becomes **size 1 on the turn it is planted**. From there, three more full cooldowns
are needed to reach size 4 (only a size-4 tree, at cooldown 0, produces a fruit instead of growing),
then one more cooldown for the first fruit. Base cooldown (ticks/step) PLUM/LEMON 8, APPLE 9,
BANANA 6; near water (league 3+) PLUM/LEMON 3, APPLE 2, BANANA 4. So, turns from planting to first
fruit ≈ 4 × cooldown:

| kind | away from water | near water |
|---|---:|---:|
| PLUM / LEMON | ~32 turns | ~12 turns |
| APPLE | ~36 turns | **~8 turns** |
| BANANA | ~24 turns | ~16 turns |

This is exactly why **MSz plants apples next to water in 46% of its apple plants** (`MSz/ALGORITHM.md`
Phase 4; own apple trees alive rise from 0.67 at turn 100 to 1.49 at turn 290, 56% water-adjacent) —
apple is the *worst* fruit to farm inland (9-tick cooldown) but competitive next to water (2-tick),
and MSz is the only one of the four that farms apples at all (32% of its harvested fruit). The
closest independent confirmation: norxondor's own trees alive at turn 10 include lemon/plum already
present (planted turn 3, needs ~32 turns to bear fruit inland — consistent with first HARVEST from
own trees staying rare, 2.3% at turn 1–100 in the norxondor profile's "first harvest origin," rising
to only 54.7% "own" by the 1–100 phase bucket and not exceeding wild until turn 100+). **Caveat:**
no document measures "turns from PLANT to first HARVEST of that same tree instance" directly; the
above is arithmetic from the authoritative mechanics, not a corpus count.

---

## 4. Gathering — which trees, how much per trip, idle time, mining

| measure | norxondor | MSz | delineate | Bubaptik |
|---|---:|---:|---:|---:|
| first harvest origin: wild | 97.7% | 89.4% | 87.9% | 91.1% |
| whole-game harvest origin: own / wild / opp | 69% / 30% / 1% | 75% / 22% / 3% | 72% / 27% / 1.5% | 64%(profile 72%) / — / — |
| fruits per HARVEST command | 1.147 | 1.146 | ~1.08 (85/78.8) | ~1.10 (86/78) |
| harvests per game | 78.2 | 112.4 | 78.8 | 78 |
| DROP items/trip: mean (median) | 1.81 (2) | 1.68 (1) | — (57% one-item, [fits]) | 1.64 |
| share of one-item DROPs | — | **61%** (`fits/MSz.md` §5, n=24,521) | 57% (`fits`) | — (\"farmer drops single fruits, choppers 3 wood\") |
| WAIT command ever issued | practically never (blank column in verb table) | practically never | practically never | **yes** — 0 in early game, rising to 0.66/10 turns after turn ~130, the only one of the four that idles a troll on purpose |
| first MINE (median turn) | 72 (late; only when iron is in deficit for the next floor, 1,036/1,036) | **20** (early; the cheap chop-1 trolls stockpile iron ahead of the carry-4/chop-3 troll) | 34 | 55 |
| MINE fades after | turn 180 | turn 180 | turn 150 | last TRAIN (never after) |

**Which tree first, in prose.** All four harvest a nearby **wild, already-fruited** tree first
(88–98% of first harvests) because a just-planted seed needs 8–36 turns to bear its first fruit
(§3) — the wild trees near the shack (present on the map at game start, already aged) are the only
source of fruit fast enough to matter before the second troll's bill or the third troll's bill comes
due. Only from roughly turn 50–100 on does "own-planted" overtake "wild" as the harvest source (own
share crosses 50% around turn 40–70 depending on the bot).

**Harvest power in the fine order.** No document ever equates "fruits per HARVEST command" (~1.1–1.15
for all four) with harvest-power directly — this figure is an average over every troll on the roster
across the whole game, most of which end up with harvest 0–1. It is *not* a reliable per-troll
harvest-power reading; treat it only as "the median HARVEST nets slightly more than 1 fruit."

**Idle turns.** Only Bubaptik measurably WAITs — and only from mid-game (turn ~130) on, when "a
troll with nothing worth doing stands still" (`Bubaptik/ALGORITHM.md` §Phase D). The other three
never show a WAIT column entry above 0.02 in the funding phase: every troll is always assigned a
job (move-toward, harvest, plant, pick, mine, chop, or drop) during the funding window. This is a
meaningful contrast worth flagging for an "inefficient" bot: **top bots essentially never leave a
troll idle before the wood phase.**

---

## 5. The third troll (and fourth) — the bill, the wait, and what happens in between

### Bills, computed from `docs/mechanics.md`'s cost formula (`plum=n+speed², lemon=n+carry²,
apple=n+harvest², iron=n+chop²`, n = trolls already owned) — every number below matches what the
ALGORITHM.md documents independently report from the replays, confirming the formula:

| bot | troll | n (owned before) | talents | plums | lemons | apples | iron |
|---|---|---:|---|---:|---:|---:|---:|
| norxondor | 3rd (troll_3) | 2 | 2/3/1/2 (64% of games) | 6 | 11 | 3 | 6 |
| norxondor | 4th (troll_4) | 3 | 2/3/0/3 (47%) | 7 | 12 | 3 | 12 |
| MSz | 3rd (troll_3) | 2 | 2/4/1/c | 6 | 18 | 3 | 6/11/18 (c=2/3/4) |
| MSz | 4th (troll_4) | 3 | 2/4/0/3 (89%) | 7 | 19 | 3 | 12 |
| Bubaptik | 3rd–5th | 2/3/4 | 4/3/h/c | 18/19 | 11/12/13 | 2+n | 6+n... |
| delineate | 3rd | ~2 (varies) | carry 4, chop 3, harvest 1 kept | (spec = largest affordable per talent, no fixed floor) | | | |

### Timing and the gap between stages

| bot | troll 2 (median) | troll 3 (median) | turns of funding (2→3) | troll 4 (median) | turns of funding (3→4) |
|---|---:|---:|---:|---:|---:|
| norxondor | 9 | 100–106 | ~91–97 | 132–138 | ~30–34 |
| MSz | 1 | 95–97 | ~94–96 | 128–129 | ~32–33 |
| delineate | 6–7 | 111 | ~104 | 144–146 | ~33–35 |
| Bubaptik | 2 | 115 | ~113 | 150 | ~35 |

**A striking cross-bot regularity**: the gap between the *third* and *fourth* troll is consistently
**~30–35 turns** for all four bots, despite the gap between the *second* and *third* being far larger
and more variable (~90–113 turns). The lumberjack bill (carry-4-class, 11–19 lemons) is much steeper
than the starter bill, and only two low-carry trolls are collecting during that whole first gap;
once the third troll (carry 3–4) joins the harvest/mine effort, the fourth troll's bill — similar in
size to the third's — clears in roughly a third of the time. This is the "funding coalition" the
existing `prior-art.md` closed-loop study names explicitly: a purchase rule alone (without two
trolls jointly harvesting toward the next bill) lost −170 margin; adding the coalition gained +106
(cited in `README.md` and every ALGORITHM.md's §"funding warning"). **All four top bots run this
coalition **implicitly**: they never assign one troll to chop while the other funds; every troll
harvests/mines during the whole "P" (produce) phase.**

**Trigger precision, all four ("delay" = turns between the bill first clearing and the TRAIN
firing):**

| bot | delay 0 | delay 1 | delay 2+ |
|---|---:|---:|---:|
| norxondor | 439/444 (98.9%) | 5/444 | 0 |
| MSz | 441/444 (99.3%) | 3/444 | 0 |
| Bubaptik | troll 3: 139/147 (95%); troll 4: 67/77 (87%) | — | — |
| delineate | 251/412 (60.9%) | 110/412 (26.7%) | 51/412 (12.4%) |

norxondor and MSz are essentially exact — they train the very turn the pre-turn shack stock clears
the bill, never a turn earlier (impossible) and almost never a turn later. delineate is the loosest
of the four (60.9% zero-delay) — consistent with it being a learned network rather than a fixed
rule, and consistent with `delineate/ALGORITHM.md`'s own framing that its habits are approximated,
not copied exactly, by any rule.

**What happens in between (interleaving), in prose per bot:**

- **norxondor**: turns 1–100 are "almost pure fruit economy" — only 7 CHOP commands per game in
  that whole window (`norxondor_gorgonax/ALGORITHM.md` §2.2); mining is strictly deficit-driven
  (1,036/1,036 mining trips happened while iron was short for the next floor); the harvested *kind*
  matches the next bill's deficit in 53% of trips (a preference, not a hard rule).
- **MSz**: the two cheap trolls harvest lemons first (1,635 of 2,724 turn 1–50 harvest trips are
  lemon), the chop-1 trolls mine ~1 iron per trip continuously from turn ~11, and the shack's plum
  and apple stocks are measurably held **flat at the bill's exact threshold** (plums plateau at 5.0
  from turn 65–130, apples at ≈3.0 from turn 50–125) — the bot harvests each resource only up to
  what the next TRAIN needs and lets any surplus fruit hang unpicked on the tree (`MSz/ALGORITHM.md`
  Phase 2d, citing Astrobytes' deficit-weight description independently).
- **delineate**: no coalition language in the document, but the same effect is measured: "the
  bottleneck is fruit, not wood... the farmer harvests lemons all game" (3,543 of 9,741 harvest
  trips over the whole game are lemon).
- **Bubaptik**: "everybody feeds the next troll's bill" — harvest plums/lemons, drop 1–2 at a time,
  mine iron between turns 11–130; early chopping that does happen (1.5/10 turns) is denial, not
  wood banking (50% opponent-planted, 41% wild — essentially none of its own).

---

## 6. The recipe — a fine order an engineer can implement, with the numbers

**Turn 1.** Check whether the pre-turn shack draw alone affords a legal second troll under the
`cost = n + talent²` formula (n=1 troll owned): if every needed resource clears at once, TRAIN it
immediately (this is what MSz does, always, and norxondor does 41% of the time) — buy each talent
independently as the highest level its single resource affords (Bubaptik's and MSz's rule), never
below `2/2/·/·` in speed/carry. **Do not PICK anything that same turn if it would touch a resource
the TRAIN needs** (PICK applies at priority 5, TRAIN at priority 6 — a same-turn pick shrinks the
stock the train check sees). Meanwhile the start troll's very first command is always MOVE (off the
unwalkable shack cell), never PICK/PLANT/HARVEST/TRAIN directly.

**Turns 2–7.** PICK a seed at the shack → walk 1 cell → PLANT it on the empty cell that minimises
(distance to shack + distance to the troll) — this single rule matches 78–90% of over 20,000
recorded plants across all four bots. Plant the fruit kind whose talent is next needed (lemon/plum
for carry/speed; never banana or apple this early — an apple takes ~36 turns to bear fruit inland,
worse than any other kind). Repeat pick→plant 1–2 more times, then peel off toward the nearest
**wild, already-mature** tree (not the seed just planted — it cannot fruit for 8–36 turns depending
on kind and water) and HARVEST it; walk home and DROP **before**, not during, the turn you next
intend to TRAIN (DROP is priority 7, after TRAIN's check — fruit banked this turn cannot pay for
this turn's purchase).

**Turns ~10–100 (the funding coalition).** Every troll harvests or mines; none is dedicated to
chopping and none sits idle (only Bubaptik ever issues WAIT, and only after turn ~130). Mine iron
**only when the next troll's iron bill is not yet covered** (measured exactly deficit-driven for
norxondor, 1,036/1,036 trips) — an idle iron stockpile is never built ahead of need except by MSz's
cheap trolls, which mine early (median turn 20) specifically because the *later* chop-3 troll's iron
bill is large and known in advance. Hold chopping to near zero (norxondor: 7 chops in 100 turns) —
wood is worth 4x a fruit but the ladder's bottleneck is fruit/iron, not wood, until the roster is
built. TRAIN the third troll (carry-3/4, still harvest-capable, chop 1–2) the exact turn its bill —
computed fresh every turn from the *pre-turn* shack stock — clears: zero delay in ~90–99% of
recorded purchases for norxondor/MSz/Bubaptik.

**Turns ~100–145 (the second lumberjack).** Continue the same coalition; the fourth troll's bill
clears roughly 30–35 turns after the third across all four bots (far faster than the 90–113-turn
first gap, because the third troll's own carry/chop power now contributes to the funding effort).
Train it the instant its bill clears, capped chop 3, harvest usually dropped to 0 (its apple cost
`n+0²=n` is still paid, but no apple talent is bought).

**From the last planned TRAIN on.** Switch every troll to CHOP→DROP; stop mining and training
entirely (norxondor: 0 TRAINs after the switch in 193/193 affordable-but-not-taken turns). Only
norxondor's data supports the fast "plant-and-cut" loop (PICK a banana → PLANT it shack-adjacent →
CHOP it one turn later at size 1, already lethal to a chop-3 troll → DROP 1 wood — turning a 1-point
fruit into 4 wood points every ~4 turns per troll, 1,116 such cycles measured). MSz and delineate do
**not** do this — their own trees are grown to size 4 (median age 26–46 turns) before felling; see
§7's contradiction note.

---

## 7. Contradictions and thin spots — cite the data

1. **"Plant-and-cut" is not universal — only norxondor's signature.** A hasty reading of the
   reconstructions' shared README might suggest all four top bots run the fast banana loop. The
   per-player numbers say otherwise: norxondor cuts its own bananas at **median age 1 turn, size 1**
   (1,116 runs; `norxondor_gorgonax/ALGORITHM.md` §3.5). MSz cuts its own trees at **median age
   26–37 turns, mostly size 4** (only 792 of 7,656 own-tree chops land within 4 turns of planting;
   `MSz/ALGORITHM.md` §3, explicitly: "no plant-and-cut conversion"). delineate fells its own
   bananas at **size 4, median age 17 turns** (`delineate/ALGORITHM.md` §5b). Bubaptik sits in
   between — a real but slower version (median age 7 turns for its post-last-TRAIN banana cuts,
   `Bubaptik/ALGORITHM.md` §2 Phase C) — not the 1-turn instant cycle. The README itself (line 49–56)
   correctly scopes this to norxondor; it is flagged here only because it is easy to over-generalize.
2. **The "size at chop" fields inside the *profiles* disagree with the exact *fits* tables for all
   four bots, and the profiles say so.** E.g. norxondor's profile reports "63% of chops on size-1
   trees," but the exact per-turn fits say size 4 in 56%, size 1 in 19% (`norxondor_gorgonax/ALGORITHM.md`
   §3.3, and the identical caveat is repeated in `delineate/ALGORITHM.md` §5b and `MSz/ALGORITHM.md`
   §3.6). Cause: the profile's "stage" field is read from the viewer *after* that turn's growth tick,
   the fits rebuild the *pre-chop* exact state from the referee's own diff. **Trust the fits number,
   not the profile's size-at-chop line, for any of the four bots.**
3. **Data is thin for the "third troll's exact per-tree harvest target" and "time from planting to
   first harvest of that same tree instance."** No document in the corpus measures the latter
   directly (§3's table is arithmetic from `docs/mechanics.md`, not a corpus count); the former
   caps out at 51–70% teacher-forced accuracy for the best available rule in every bot's document,
   with an explicit warning in all four that a rule reproducing recorded decisions still lost
   **−172.7 margin** closed-loop when actually played (`norxondor_gorgonax/ALGORITHM.md` §5.8,
   citing `prior-art.md` Phase 14) — i.e., copying the *funding/training* order (this report's
   focus, and the part that is exact) is safe; copying the *target-choice* rules (which specific
   tree) is not validated and should not be treated as settled.
4. **Bubaptik's own bill table in §5 above is compressed** — its per-ordinal bill depends on the
   chop level bought (2/3/4), which floats with the iron stock rather than following a fixed floor
   like norxondor/MSz; see `Bubaptik/ALGORITHM.md` §3.1 for the full breakdown (not repeated here
   for space).
5. **delineate has no fixed bill table at all** — it is a learned network, not a rule; §5's
   "spec = largest affordable per talent" is the closest measured description
   (`delineate/ALGORITHM.md` §5b, 22/26 games), not an exact floor/cap like the other three.

---

## Appendix — quick file index

- `local_claude_1/reconstructions/README.md` — the cross-player summary this report expands on.
- `local_claude_1/reconstructions/norxondor_gorgonax/ALGORITHM.md`,
  `.../MSz/ALGORITHM.md`, `.../delineate/ALGORITHM.md`, `.../Bubaptik/ALGORITHM.md` — the primary
  sources for §2, §5, §6, §7.
- `local_claude_1/reconstructions/profiles/{norxondor_gorgonax,MSz,delineate,Bubaptik}.md` — the
  primary source for §1's turn-by-turn opening tables and §4's gathering numbers.
- `local_claude_1/reconstructions/fits/README.md` — the validation method (0 disagreements vs. the
  referee's own diff over 784 games) that makes these numbers trustworthy.
- `local_claude_1/second-troll-census/README.md` — the one place our own bot's second-troll timing
  is compared to the field (§2's context note).
- `codex_1/top10/field-comparison-2026-08-26.md` — the independent per-turn-corpus confirmation
  that the heavy planters (a wider field than just the top 4) run a persistent plant→harvest→chop
  wood loop, and that our own bot (at the time of that study) issued 0.05 banana plants/game in
  turns 1–50 against 3.2–5.9 for the leaders.
- `docs/mechanics.md` lines 40–110 — the authoritative rules behind §0 and §3's arithmetic.
