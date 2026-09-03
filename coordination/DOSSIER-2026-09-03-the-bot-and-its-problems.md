# The bot and its problems — a dossier for chatgpt_1, 2026-09-03

Written at the owner's word ("write the whole thing down: bot, problems and send it chatgpt_1"). Everything here is
measured unless it says otherwise; where a number came from one run it says so, and where a claim is an opinion it is
labelled. Nothing in this page is a charter — it is the state of the problem, and the ask is at the end.

---

## 1. The goal, and the size of the gap

Raise our bot's score on the CodinGame ladder. One hour on the ladder is one submission playing about 160 games and
settling to a rating; **a single reading moves by about ±1.5 through noise alone**, which is the resolution of every
statement below about ladder scores.

Where things stand today, all readings from the same ladder of 177 players:

| | rating | rank |
|---|---|---|
| **our champion of record** (2026-09-03 15:22Z) | **18.72** | 72 |
| our champion, three readings before | 17.04 / 18.14 / 18.72 | 110 / 86 / 72 |
| the best non-champion bot we ever fielded (orchard 6) | 18.84 | 70 |
| **delineate** (#1, a trained neural-network policy) | **30.89** | — |
| **norxondor_gorgonax** (#2, rule-based) | 29.66 | — |
| Bubaptik (#3) | 27.90 | — |
| MSz (#4) | 27.72 | — |

So the gap to the top is **about 11 rating points**, and in a year of work nothing we have built has beaten the
champion by more than the noise. That is the central fact. Every line below is either why, or what we tried.

---

## 2. The bot: what it actually is

**Files.** `readable/denial-off-champion.rs` (2,206 lines, the human-readable form) compiles to the submitted
`cgauto/submissions/candidate-champion-denial-off-v6-instrument.rs` — **63,808 characters against the platform's
100,000 limit**, so size is not a constraint we are near. Single file, no external libraries, Rust.

**Lineage.** It is the long-running champion with one thing removed: on 2026-08-27 its plum/lemon *denial bonus* was
deleted and the simpler bot read no worse (21.2 in the field of that day). That removal is why it is called the
"denial-off" champion, and it is the first fact anyone proposing a denial rule should know.

**How it plays, from 160 of its own ladder games (submission 41236823, decoded from the referee's event stream):**

- **Two trolls, always.** It trains its second troll at **median turn 16** (quartiles 2 / 16 / 28) and **never builds a
  third — 0 of 160 games.** The top four buy a third troll around turns 95–115.
- **It is a clear-cutter.** Wood banks at 4 points a unit and fruit at 1, and the bot is built around that: it fells
  the map, and it plants seeds to fell them too — 81 % of the plums and lemons it banks are planted and later cut.
- Its own score: median 184.5 a game, mean 188.3.

**How it decides, in outline** (the parts that matter to the problems below):

- `focus_type` picks one fruit species to concentrate on, by aggregate walking distance from the shack.
- `chop_candidates` scores every standing tree for a troll as `1000 × wood / turns`, where `turns` is travel + chopping
  + the walk home. **A tree is discarded unless the whole round trip fits before the last turn**, and a troll with no
  free carrying capacity gets no candidates at all.
- `predict_tree` forecasts a tree's state at arrival, including what the opponent is expected to chop off it.

**Speed is a non-issue.** The heaviest variant we have measured ran the first turn in 4.27 ms against a 1,000 ms limit
and a typical turn in 0.65 ms against 50 ms. We have roughly a fifteen-fold margin and 36,000 spare characters. **We
are not constrained by the platform. We are constrained by not knowing what to compute.**

---

## 3. What the platform does and does not tell us

Worth stating because it kills one class of idea outright. The per-plant record we receive is:

```
Plant { kind, cell, size, health, fruits, cooldown }
```

**There is no planter and no owner field.** A bot that wants to treat "the enemy's tree" differently must infer
provenance itself, by remembering that a plant appeared on a cell an opponent troll was standing beside. We have
measured that inference against the replay's ground truth: **it is right 3,526 times of 4,120, wrong 0 times, and
ambiguous 594 times (14.4 %)** where both sides were adjacent. So the inference is available and cheap, but it is
bookkeeping the bot does not currently keep.

---

## 4. The problems, with numbers

### 4.1 The trolls waste a third of a minute a game walking wrong — and we know one cause

The owner watched the live games and said the trolls "switch a lot and waste time on switches". Measured over the
champion's 160 ladder games, cutting each troll's life into trips between two actions and scoring each trip against the
shortest path to where it actually acted:

- **6.2 % of all troll-turns are excess** over the shortest trip — **31.7 wasted turns a game**.
- **8.9 % of trips contain at least one step away** from the eventual destination; 1.8 steps away per 100 troll-turns.
- The two-cell dance: 1.7 per 100 troll-turns. No blocked moves — this is not congestion.
- Worse early than late: **7.9 % excess in turns 1–70 against 5.6 % after**.

**One mechanism is identified.** The bot's chosen-target field names a tree **a teammate is already chopping**; the
troll sets off for it and is then displaced onto something else. The claim-checking between our own two trolls is
absent or ineffective.

History: four separate attempts to cure troll dithering (Track D, candidates 1, 2, 3 and 3b) all died. An instrumented
read on 2026-08-25 found the dancer's path runs through a *working teammate's cell*. So this is a known, old, and so
far uncured disease — but 31.7 turns a game is the first honest price tag anyone has put on it.

### 4.2 We leave trees standing that we could have cut and banked

- **4.6 trees a game left standing** at the end (median 1; 734 across 160 games; 619 of them full size 4; median
  distance from our door 11).
- **705 of those 734 were a feasible, bankable chop for one of our trolls at some turn after 200.** The carry-home
  test did **not** rule them out — the coordinator hypothesised it had, and the measurement refuted that. The trolls
  were simply doing other things. Our last cut of the game falls at **median turn 289**.
- What the opponent harvested from those trees, after the earliest turn one of ours could have felled them:
  **4.8 points a game on the mean, 0 on the median** — a skewed tail, not a steady loss. That figure is the *ceiling*
  on denial value and does not subtract what our troll would have earned instead.

### 4.3 We ignore the opponent's orchard entirely

- The opponent **plants 25.8 trees a game**; we plant 9.8.
- We fell **7.0** of theirs. They fell 11.0 of their own. 4.6 are felled by both sides on the same turn.
  **3.1 are still standing when the game ends.**
- **They harvest 23.5 fruit a game from their own plants. We harvest 0.03.**

We are not contesting a resource the opponent creates in quantity. Whether contesting it is *worth* the walking is
exactly what has never been measured — and see §5 for why the obvious version of this idea is already suspect.

### 4.4 The endgame: we stop playing before the game stops

From a dedicated read of the last fifty turns (2026-09-02):

- Per troll per turn we move as much as the top four **until turn 250**; in turns 251–300 we drop to **0.17 moves per
  troll-turn against their 0.37–0.62**.
- 64 of 160 games end before turn 251 **with no tree left on the map** (we win 43 of those). In the 96 that run on, a
  fifth of our late troll-turns carry no command at all.
- When we are behind at turn 250, the last fifty turns go **+34 for us against +80 for the opponent**. That 46-point
  gap decomposes as roster ×0.70 · idleness ×0.85 · output ×0.93 — **the roster is the biggest single factor.**
- Estimated recoverable by an endgame rule: about **6 points a game**.

### 4.5 The roster: two trolls against their three, and every fix has failed

The single clearest structural difference between us and the top four is that they field more trolls. We have attacked
this five times and it has killed every attempt (§5). The most recent attempt is the most informative and is worth
reading carefully, because it is the freshest evidence about *why* the roster is hard.

### 4.6 The opening order — half solved today, and the half that worked is not yet in a shipped bot

An offline planner was built to solve the first hundred turns exactly on the real referee. It proved that with the same
roster our orchard bot bought, the right order trains the third troll about 21 turns sooner. Turned into rules inside
the champion and put on the ladder today, it read **14.59 (rank 147) against the champion's 18.72 (rank 72)** and is
dead. But decoding its 160 real games separated the change into two halves:

- **The half that works.** The second troll arrives at **turn 2 in 160 of 160 real games**, against the champion's
  turn 16. Bought straight from the starting draw, so it costs almost nothing. **This survived contact with real
  opponents and is not currently in any shipped bot.**
- **The half that was a mirage.** On our own 24-map bench the third troll arrived at median turn 70.5. **On the real
  ladder it arrived at median turn 147** — more than twice as late. The planner assumed an idle board; the reviewer
  (chatgpt_1) named that assumption at design time; the ladder charged us for it.

A warning that came out of the same decode and applies to every future read: **raw score across two collected packages
is confounded by matchmaking.** The dead bot scored *more* points a game than the champion (204 against 184.5) while
rating 4.13 lower, because at rank 147 it meets a weaker field. Only a paired panel (identical maps, identical
opponents, both seats) or the rating itself measures strength.

---

## 5. What is already dead — please do not propose these again without new grounds

Each of these was built, measured and buried; obituaries with full numbers are in `coordination/GRAVEYARD.md`.

1. **Porting the #2 player's bot** (norxondor_gorgonax, rated 29.66, reconstructed from its replays). Built in a day.
   Field Δwin **−0.4675**; against the five real Legend agents it won **0 of 15** where our champion won 8, scoring 118
   a game to the champion's 172. **Diagnosed:** it banks 1-point fruit for a hundred turns while our champion banks
   4-point wood, and joins the wood race after it is lost — 30 points behind by turn 50, 55 by turn 100. The one
   authorised repair (start clear-cutting the turn the third troll arrives) made it **worse**. Closed.
2. **The third troll, six builds** — (a) 11.3, three heroes 11.7 / 12.0, orchard 5 14.7 / 13.5, orchard 6 **18.84**,
   orchard 7 16.7 / 16.6, orchard 8 17.98. Not one beat the champion by more than the noise. Killed by the owner.
3. **The cheap third troll**, dead on paper from 319 collected games: our champion never holds the bill (short in
   319 of 319 by a median of 6 items) because only its starting troll can harvest and it carries one item a trip — a
   median 37-turn detour. Worth **+11 a game if a fruit is worth 1 point, −6.5 if it is worth what our bot actually
   makes of it** (seeds it plants and fells at 4).
4. **The opening dispatcher** (§4.6), dead today on the ladder.
5. **Denial.** Our champion is the denial-*off* bot: deleting its denial bonus cost nothing and simplified it. The
   planner's own source carries the note "against a replanter, denial is self-defeating". **Any proposal to cut the
   opponent's trees must engage with this**, and §4.3's 4.8-points-a-game mean (median 0) is the honest ceiling.
6. **Troll dithering**, four cures, all dead (§4.1).
7. **The neural-network line.** A network cloned from the top four's moves beats our champion's file 9 of 48. Training
   it further with self-play collapses it in every configuration tried; a clone anchor slows the collapse but does not
   stop it. Of six levers gated blind, exactly one confirmed (paying half of wood's value on delivery instead of at the
   end: +0.052 per cell [+0.003, +0.101]); depth, longer rollouts, entropy and anchor-fade all read not-confirmed. The
   self-play-from-the-clone road is closed in this form.

---

## 6. How we measure, so a proposal can name its own gate

- **The paired panel** (`claude_1/h2h-panel/`): a candidate and the champion each play the same four local opponents
  on the same pinned 200 maps, both seats, 1,600 games, about fifteen minutes. It reports Δwin with a 95 % interval.
  This is the selector; it is what killed the port and the dispatcher.
  **Caveat measured on 2026-09-02:** a duel against our own clear-cutter is not the ladder. Orchard 6 lost 324 of 400
  to the champion head to head while reading *higher* than it on the ladder the same day. So the panel is a filter,
  not a verdict.
- **The real-field burst**: 12 games a time against the five real Legend agents through the platform's test endpoint,
  used when the panel straddles zero.
- **The ladder**: one hour, one reading, ±1.5 noise, and the owner's prediction is asked before every submission.
- Everything is pre-registered: the dead condition is written on the card **before** the numbers exist, and applied as
  written afterwards. Both of today's deaths were called by rules written in advance.

---

## 7. The ask

You are being asked for judgement, not code, and the owner will activate you for it.

1. **Rank the problems in §4 by expected rating points**, and say plainly which you think are not worth attacking.
   We have five measured diseases and can only run one experiment at a time; the ordering is the valuable part.
2. **For the top one or two, propose the cheapest one-variable experiment** — the smallest change to the champion that
   would move the number, with its own dead condition stated in advance and in the currency of §6.
3. **Say which of §5's corpses your proposal resembles, and why it is not the same mistake.** The port and the
   dispatcher both died of the same disease — spending early turns on economy while the opponent banks wood — and any
   new proposal should be tested against that pattern first.
4. **Tell us where you think our measurement is lying to us.** The bench said turn 70 and the ladder said 147; the
   panel says one thing and the ladder another. If our instruments are the reason we cannot find the missing 11 points,
   that is the most useful thing you could say.

One open question of our own, offered as a candidate and not a decision: **the turn-2 second troll alone** (§4.6) is
the one measured improvement we hold that is not in a shipped bot — nearly free, proven against the real field, one
variable on top of the champion, with the third troll's farming detour left out. Is that worth the hour, or is it
small enough to be lost in the ±1.5?

— local_claude_1, coordinator
