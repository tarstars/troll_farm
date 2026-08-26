# m061 — why one troll kept one goal for 171 turns, and what it cost

- Task `20260826-m061-stale-goal-read`, board row **D-3**. Author **claude_1**, reviewer
  **codex_1** (gate D3-G1, one round). Read-only: **0 builds, 0 panels, 0 ladder, 0 Arena.**
  No bot source, arm, resolver or corpus was touched.
- Everything below is read off the Candidate 3 **instrument** arm's own archive and the
  **rule-off** arm's archive beside it, both pinned into the worktree so this report does not
  depend on `/tmp` surviving:
  `claude_1/cure3/m061/inputs-manifest.json` records the source archives
  (`…/instrument/games/games.jsonl.gz` sha256 `0f497da5…`,
  `…/ruleoff/games/games.jsonl.gz` sha256 `bb781b82…`) and the sha256 of each extracted file.
- Readers/artifacts, all in `claude_1/cure3/m061/`: `read_m061.py` (joins the `NARRATE v6` wire
  to the referee transcript), `turntable-m061-s{0,1}-{candidate,ruleoff}.txt` (the full
  turn-by-turn tables, item 1), `episodes.py` + `episodes-instrument.json` and
  `ka-distribution.txt` (item 5), `fixprobe.py`/`idleprobe.json`/`rule-cost-table.txt` (item 4).

**One control before anything else.** The rule-off arm is the champion in play — its own score on
`m061` is **75** (seat 0) and **82** (seat 1), identical to the parent's, and its command stream
is byte-identical to the parent's on both seats (checked, not assumed). So every difference below
is the keep rule's and nothing else's.

---

## 0. The answer in five lines

1. A **`Tree` goal is released as *done* only when the troll's carry is full standing at that
   tree.** On `m061` the tree yields one fruit a visit against a carry of three, so *done* can
   never fire.
2. It is never released as *gone* (the tree is alive, health 20, all 200 turns) and never as
   *impossible*, because the champion's reachability test walks the **static** walkable map —
   **a teammate standing in a one-wide corridor is not an obstacle to it.**
3. So the goal is immortal, and the troll holding it is restricted to commands that carry it.
   That restriction **flips the champion's two-unit joint choice**: the goal-holder takes the
   tree, and the other troll is left with the always-present `WAIT` candidate.
4. The other troll then stands still **in the corridor between the goal-holder and the tree**,
   for 149 turns (seat 0) and 115 turns (seat 1) — so the goal-holder can never reach the tree,
   never fills its carry, and the goal is never *done*. The deadlock feeds itself.
5. **The cost is not the wasted turns.** It is that the stranded troll is no longer standing next
   to its shack, and the champion's late-game wood engine — `PICK` a fruit from the shack,
   `PLANT` it on your own cell, `CHOP` it, `DROP` the wood — has
   `is_adjacent(unit.cell, shacks[0])` as a hard gate (`readable/door1-champion.rs:1789`). That
   engine earns the champion **+44** (seat 0) and **+47** (seat 1) from turn 100 to turn 200.
   The candidate earns **0**. That is the whole of the −43 / −47.

---

## 1. The turn-by-turn account

Full tables: `turntable-m061-s0-candidate.txt`, `-s0-ruleoff.txt`, `-s1-candidate.txt`,
`-s1-ruleoff.txt` — 200 turns each, every own unit, every turn. Columns are the wire's own
(`chosen`/`want`/`r`/`k`, then the per-turn release census and `ka`) joined to the referee's
state (cell, carry) and the emitted command. `m061` is a corridor: a 13×6 map whose only floor is
the row `y=2`, `x=1..11`, one cell wide, with the two shacks in the row above at each end.

### 1.1 Seat 0 — unit 2, goal `TREE(7,2)`, turns 30 → 200 (171 turns)

Both trolls: `u0` carry 2 / chop 1 (the chopper), `u2` carry 3 / harvest 1 / chop 0 (the picker).
Our shack sits at `(1,1)`; the only fruit tree left after turn 27 is an `APPLE` at `(7,2)`.

| turns | what `u2` actually did | goal | `k` | why nothing released it |
|---|---|---|---|---|
| 30 | stood on `(7,2)`, `HARVEST 2` | goal `TREE(7,2)` **recorded** this turn, `ka=1` | 2 | — |
| 31–37 | walked `(7,2)`→`(2,2)`→`(2,1)` carrying 1 apple, `DROP 2` at t37 | still held | 1 | the goal is **valid but not live** (`kl=1`): with fruit in hand the only candidates are bank candidates, so the rule restricts nothing and also releases nothing |
| 38–44 | walked back out `(2,1)`→`(7,2)`, `HARVEST 2` at t44 | still held | 1→2 | — |
| 45–51 | walked home again, `DROP 2` at t51 (**+1 own point**) | still held | 1 | not live again |
| **52–200** | **oscillated `(2,2)`↔`(1,2)`, 74 turns on each cell, never anywhere else** | still held, `ka` 23→171 | 1 | see §2 |

Meanwhile `u0`: it was parked at `(1,2)` — beside the shack — until turn 44. At t45, the moment
`u2` left the near end of the corridor, `u0` started walking toward the same apple tree (t45–48,
then a forced `WAIT` at t49 when `u2` came back the other way, then t50–51), and at **turn 52 it
stopped on `(3,2)` and emitted a bare `WAIT` on every one of the remaining 149 turns.** It never
left `(3,2)` again.

`(3,2)` is the third cell of a one-wide corridor. `u2`, restricted to `TREE(7,2)`, walks `(1,2)`→
`(2,2)`, finds `(3,2)` occupied, is given the regressive detour back to `(1,2)` by
`resolve_move_conflicts` (the wire says so directly: `r=P` on the even turns, `r=R` on the odd
ones), and repeats. That is a textbook D-1 dance, and the panel's own detector records it:
**D-1 episode, unit 2, cells `(2,2)`/`(1,2)`, turns 53–200, k=73**, against the rule-off arm's
single 3-turn D-1 blip on the same map.

**No release predicate fired on any of those 149 turns.** Counted, not asserted: over
turns 52–200 the wire reports `kr=0, rd=0, rg=0, ri=0, rx=0, rf=0, rt=0, ro=0, xc=0` — the
release census is identically zero on every turn.

### 1.2 Seat 1 — unit 2, goal `TREE(6,2)`, turns 31 → 200 (170 turns)

Same map, seats swapped: our shack at `(11,1)`, our tree a `LEMON` at `(6,2)`. Same disease with
the geometry mirrored, and one difference worth naming.

- t31: `u2` stands on `(6,2)`, `HARVEST 2`; the goal is recorded.
- t31–t85: the goal is held across five bank trips. This stretch is **productive** — `u2` harvests
  and banks lemons and the own score climbs 23 → 35. There are real releases in this window on
  the *other* troll (`rd` at t39 and t75, `rf` at t28, `xc` at t86), so the machinery works.
- **t86**: `u0` arrives at `(6,2)` — the goal tree's own cell — and stops. It emits a bare `WAIT`
  on all 115 remaining turns and never moves again.
- **t87–t200**: `u2` shuttles `(7,2)`↔`(8,2)`, 56 turns on each, never reaching `(6,2)` again.
  Own score frozen at 35 from t86 to the end.

Seat 1's holder is *not* idle for its whole life — it banked for 55 turns before the stall. That
distinction is what kills a blunt turn cap in §4.

---

## 2. The mechanism, in one sentence

> A `Tree` goal is released as *done* only when the holder's carry is full **at** the tree, and as
> *impossible* only when the tree is unreachable on the **static** map, so a goal on a tree that
> yields one fruit a visit and is blocked by the holder's own teammate satisfies neither test and
> lives forever — and because the champion's two-unit joint choice forbids both trolls the same
> cell, the immortal goal pins the tree to one troll and hands the other one the `WAIT` candidate,
> which parks it in the corridor that makes the goal unreachable in the first place.

Each clause is the code, read at the arm:

- **done** — `goal_done`, `Target::Tree`: `worked && at == Some(cell) && unit.free_capacity() <= 0`.
  `u2`'s carry capacity is 3 and a `HARVEST` yields 1; the champion leaves for the bank after one
  fruit. `free_capacity()` is never 0 at the tree. *This is the packet's own hypothesis — "the
  carry never filled" — and the wire confirms it.*
- **gone** — `gone_cause`, `Target::Tree`: fires only if the plant is absent, `health <= 0`, or has
  changed kind. The apple at `(7,2)` is `health 20` and `APPLE` on turn 30 and on turn 200; the
  lemon at `(6,2)` is `health 11` and `LEMON` at the end. Never fires.
- **impossible** — `goal_impossible` runs a BFS over `view.walkable`, which is derived from the
  static map and never removes an occupied cell. The arm's own comment says it: *"a standing
  teammate is never an impossibility — it is the exchange rule's business"*. The exchange rule is
  Candidate 2, and Candidate 3 does not have it.
- **the pin** — `best_pair`/`select` maximise over pairs subject to `compatible(a.target,
  b.target)`, which forbids two units aiming at the same cell. `main_candidates` always begins
  `vec![wait()]`, a candidate whose target is `None` and therefore compatible with everything. With
  `u2` restricted to `TREE(…)` commands only, the best compatible pair is (`u0` = `WAIT`, `u2` =
  the tree), and the wire shows exactly that: `u0` reports `want=TREE(7,2)` — it still wants the
  tree — with `r=N` and a bare `WAIT`, for 149 turns.

**And the counterfactual is on the wire too.** In the rule-off arm on the same turns, the claim
goes the other way: `u0` holds the tree and emits a `MOVE` toward it that the resolver rewrites to
`WAIT` (`r=W`, *forced* wait — a different code from `r=N`), while `u2` sits at `(2,2)` with no
move. The champion stalls here as well — but it stalls **with `u0` still standing on `(1,2)`,
beside its shack.** The keep rule did not invent the stall; it moved the wrong troll.

---

## 3. The cost, attributed

| | candidate | champion | delta |
|---|---|---|---|
| `m061:0` own score | 32 | 75 | **−43** |
| `m061:1` own score | 35 | 82 | **−47** |

**Seat 0.** The candidate's own score changes for the last time on **turn 52**, at 32. The
champion's score on turn 52 is **31** — the candidate is *one point ahead*, and that point is the
keep rule's doing: the extra apple `u2` fetched on turns 38–51 because the rule made it go instead
of waiting. From turn 52 to turn 200 the candidate gains **0**; the champion gains **+44**, all of
it between turns 100 and 200 (its score is 31 at t99 and 75 at t200).

- stale goal, via the stranded teammate: **−44**
- the goal-holder's own extra trip: **+1**
- anything else: **0**

**Seat 1.** The candidate's own score changes for the last time on **turn 86**, at 35. The
champion's score on turn 86 is also **35** — dead level. From turn 87 the candidate gains **0**
and the champion gains **+47**, again entirely between turns 100 and 200 (35 at t99, 82 at t200).

- stale goal, via the stranded teammate: **−47**
- anything else: **0**

**What the champion is doing in those turns, and why the candidate cannot.** From turn 100 the
champion runs a wood engine: `PICK` a fruit out of the shack, `PLANT` it on the cell it is standing
on, `CHOP` the new tree to death, `DROP` the wood (4 points a unit), repeat — roughly +8 every 17
turns. `main_candidates` (`readable/door1-champion.rs:1783-1798`) emits that `PICK` candidate, at a
dominating score of 7500, only when **all** of: `carried == 0`, `view.turn >= 100`,
`view.plants.len() <= 2`, at least two own units, no plant already on the unit's cell, and
`is_adjacent(unit.cell, view.shacks[0])`.

On both seats, at turn 100, the candidate arm satisfies **every one of those** except the last:
`plants.len()` is 1, the turn is 100, both trolls are alive, `u0` carries nothing, its cell is
empty, and the shack holds fruit. But `u0` is standing on `(3,2)` with its shack at `(1,1)` (seat
0) and on `(6,2)` with its shack at `(11,1)` (seat 1). **One predicate, false for 100 turns, on
both seats.** That is the −90.

---

## 4. Each release fix: where it fires on `m061`, and what it costs on the other 119 maps

The cost column is the one to read. It is measured the only way a 0-build budget allows: for every
kept-goal holding run in all 240 games, the turn a rule would have fired, and **what the holder
actually went on to emit on the turns the rule would have removed** — the `CHOP`/`HARVEST`/`DROP`/
`PLANT`/`PICK` it would no longer do. Full table: `rule-cost-table.txt`.

`+risk` below is the number that matters: the sum of the own-score margins of the **winning**
non-`m061` games a rule would reach into. The whole of the cure's win outside `m061` is **+25**.

| rule | fires on `m061` s0 / s1 | runs cut | turns removed | work commands removed | non-`m061` games touched | of those, **winning** games | **+risk** |
|---|---|---|---|---|---|---|---|
| (a) cap 20 | t49 / t50 | 64 | 1,842 | 834 | 62 | 4 | **+39** |
| (a) cap 30 | t59 / t60 | 57 | 1,238 | 635 | 55 | 4 | **+39** |
| (a) cap 40 | t69 / t70 | 42 | 724 | 341 | 40 | 4 | **+39** |
| (a) cap 60 | t89 / t90 | 7 | 291 | 30 | 5 | 2 | **+30** |
| (b) give-up price `xd` > 0 | **never** | 84 | 1,709 | 1,074 | 68 | 7 | +44 |
| (b) `xd` > 1000 | **never** | 68 | 1,044 | 837 | 55 | 5 | +39 |
| (c) picked-to-plant fruit | **never** | — | — | — | — | — | — |
| (d) 2-cell dance, 20 turns | t72 / t108 | 26 | 536 | 195 | 24 | **0** | **+0** |
| (d′) 2-cell dance **and no work**, 12 turns | t64 / t100 | 14 | 614 | 171 | 12 | **0** | **+0** |
| (d′) 2-cell dance **and no work**, 20 turns | **t72 / t108** | **6** | **317** | **58** | **4** | **0** | **+0** |

**(a) A turn cap fires, and is the wrong instrument.** A cap at 30 cuts 57 holding runs, of which
55 are not on `m061`, and removes 635 productive commands. Four of the games it reaches into are
games the cure *wins* — `m068:0` (+16), `m092:1` (+14), `m031:0` (+8), `m053:0` (+1) — worth **+39**
together, more than the entire +25 the cure earns outside `m061`. The reason is visible in
`ka-distribution.txt`: of the 57 games with a goal older than 30 turns, **54 end in `rf`** — the
tree died — because a long kept goal is normally a chopper standing at one tree hitting it until it
falls. That is the cure working. A cap cannot tell it from the disease. *(One thing a cap has
going for it, and it should be said: no rule in this table cuts a run that later ended in `rd`,
"goal achieved" — 0 of them, for every threshold. A cap destroys work in progress, not completed
work.)*

**(b) A "strictly better goal available" rule never fires here, and this is the sharpest negative
result in the report.** The packet already built the price tag for exactly this: `xd`, the basis
points of score the unit gives up by obeying the kept goal instead of taking its best free
candidate (`give_up_bps`). On `m061` seat 0, **`xd` is 0 on all 200 turns**. On seat 1 it is
non-zero on exactly six turns, **8–13**, all of them before the stale goal is even recorded.
The keep rule gives up *nothing measurable in score* on this map, because the alternative the
selector would have taken is the `WAIT` candidate. **The instrument's own price tag is blind to
this defect**, and any release rule keyed to it — at any threshold — would fire on 55 to 68
other games, put +39 to +44 of the win at risk, and leave `m061` exactly as it is. This form
should not be proposed for Candidate 3b.

**(c) "Release a picked-to-plant fruit when planting is no longer possible" is already implemented
and is not this bug.** That is `gone_cause`'s `Target::Cell` arm, counted as `ro`; it fires 149
times in the panel. Both stale goals on `m061` are `Tree` goals — the wire says `TREE(7,2)` and
`TREE(6,2)` on every turn the holder carries them. The rule cannot fire on either seat.

**(d) What the data actually suggests: release on the holder's own dance, and only when it is not
working.** The failure has a shape the programme already has a detector for — the holder occupies
two cells and nothing else, turn after turn. Applied naively (row "2-cell dance, 20 turns") it is
already clean: 26 runs cut, **not one of them in a game the cure wins**. Adding the second clause
— *and emitted no `CHOP`/`HARVEST`/`DROP`/`PLANT`/`PICK` in the window* — is what separates the
disease from the cure, because a chopper standing at one tree swinging is a one-cell "dance" too.
With both clauses at a 20-turn window the rule touches **four** games outside `m061`
(`m001:1` −2, `m005:0` −8, `m034:0` ±0, `m107:0` −8; **all already losing, sum −18**), removes
**58** productive commands in total, and fires on `m061` at **turn 72** (seat 0) and **turn 108**
(seat 1) — both comfortably before turn 100 matters on seat 0, and 8 turns after it on seat 1.

**What it would recover, and the honest limit on that number.** The ceiling is exactly the
champion's engine: **+44** on seat 0 and **+47** on seat 1, and it is available only if `u0` is
standing beside its shack when the gate opens. At the firing turn on seat 0 (t72) `u0` is at
`(3,2)`, two steps from `(1,2)`, with 28 turns to spare; on seat 1 (t108) `u0` is at `(6,2)`, five
steps from `(11,2)`, and the gate is already open. Both are geometrically recoverable. **Whether
they actually recover is not determinable from these archives**: releasing the goal changes the
selection on the very next turn, and everything after the cut is a different game. No number in
this report is a simulation, and I am not going to write one down as if it were. *Measuring the
recovery needs one build and one panel — which is precisely the bound Candidate 3b's card should
carry, and which this card correctly forbids.*

---

## 5. The `ka` distribution over all 240 games

Full table, every game named: `claude_1/cure3/m061/ka-distribution.txt`. `ka` is the wire's own
field — the age of a valid kept goal — and I checked in all 240 games that its maximum equals the
longest run of turns on which some unit reports `k>0`, so the two readings of "how old" agree.

| `ka_max` | games |
|---|---|
| 0 (no goal ever recorded) | 16 |
| 1–10 | 78 |
| 11–20 | 82 |
| 21–30 | 7 |
| 31–40 | 15 |
| 41–50 | 24 |
| 51–60 | 11 |
| 61–100 | 5 |
| **>100** | **2 — `m061:0` (171) and `m061:1` (170)** |

**57 of 240 games hold a goal older than 30 turns.** Their own-score deltas sum to **−101**;
take out the two `m061` seats and the other 55 sum to **−11**, and 39 of those 55 are exactly
±0. A long kept goal is, on this panel, normally harmless: 54 of the 57 long goals end in `rf`
(the tree died under the chopper). Only two end at the final buzzer still held, and both are
`m061`.

Across the panel there are 1,364 goal-holding runs over 9,521 turns, median length 1 turn, mean
7.0, p99 53. The release census over the whole panel reproduces the G-1 packet's §2.4 exactly
from these archives — `kr 1,626 = rd 805 + rg 815 + ri 0 + rx 0 + xc 6` and
`rg 815 = rf 666 + rt 0 + ro 149` — which is the check that this reader is reading the same wire
the packet did.

**One honesty note on the counting.** A run of `k>0` turns is one *goal* only if the unit did not
release and immediately re-record inside the same turn; the wire cannot distinguish those two
cases per unit. On 98.3% of turns (47,166 of 48,000) at most one troll holds a goal at all, and
`ka` — which resets to 1 on a new goal — agrees with the run length in every one of the 240 games,
so this does not affect any number above. It is stated because it is the kind of thing that
should not be discovered at the gate.

---

## 6. What this does not say

- It does not propose Candidate 3b, book a ladder slot, or touch the Arena. The fix is a new
  candidate with its own card and its own bound; this task was chartered to find the cause.
- It does not claim any recovered points on `m061`. §4 gives firing turns verified against the
  wire and a ceiling taken from the champion's own run; the recovery itself is unmeasured and
  labelled unmeasured.
- The `+risk` column is a *reachability* count, not a prediction: it says which winning games a
  rule would have reached into and how much margin sits in them, not how much of that margin
  would actually be lost. A rule with `+risk +0` cannot cost the +25 by construction; a rule with
  `+risk +39` might cost none of it, and that is what a panel would be for.
