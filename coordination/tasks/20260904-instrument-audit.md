# Task 20260904-instrument-audit — where is our measurement lying to us?

- Born: 2026-09-04 03:2xZ on the owner's word ("do it"), after a day in which four of the coordinator's own numbers
  needed correcting and every one was caught by re-derivation rather than argument.
- Work owner: **the coordinator** (this is verification work, not design). No build, no ladder, no platform action.
- Done when: each instrument has a stated resolution and a stated bias, backed by numbers that reproduce.
- Budget: one pass. It costs one 1,600-game panel run and no new play beyond that.

## The question

We have killed seven lines on local instruments and we cannot find eleven rating points. Before spending another
build, establish what our instruments can and cannot actually resolve.

## Finding 1 — the ladder's own noise, measured rather than assumed

The champion of record (sha `0e92f8fa…`, the identical file every time) has been submitted **four** times:

| read | score | rank |
|---|---|---|
| 2026-08-28 15:22 | 18.19 | 85 |
| 2026-09-02 09:07 | **17.04** | 110 |
| 2026-09-03 06:22 | 18.14 | 86 |
| 2026-09-03 15:22 | **18.72** | 72 |

Mean 18.02, **spread 1.68**, standard deviation ≈ 0.71. **Nothing about the bot changed between these readings.**
So the project's working assumption of ±1.5 for a single reading is about right, and it follows that
**no ladder difference below roughly 1.7 is evidence of anything** — which retires the turn-2-second-troll build
(worth about seven game turns of one troll) as unmeasurable by a ladder hour, and confirms that orchard 6's 18.84
against the champion's 18.19, and orchard 8's 17.98, were always inside the noise.

## Finding 2 — the duel against the champion inverts against the ladder

Every bot for which both a duel and a ladder reading exist:

| bot | duel win rate vs the champion | ladder | the champion's own reading that week | ladder delta |
|---|---|---|---|---|
| the champion (against itself) | 0.2825 | 18.19 / 17.04 / 18.14 / 18.72 | — | 0 |
| **orchard 6** | **0.1625** (65 of 400 — clearly worse) | **18.84** | 18.19 | **+0.65** |
| the opening dispatcher | 0.0725 (29 of 400) | 14.59 | 18.72 | −4.13 |
| port v2 / v3.1 | 0.0400 / 0.0250 | never submitted | — | — |

**Two points, opposite signs.** The bot that loses the duel more heavily than orchard 6 (the dispatcher) reads far
below the champion; orchard 6, which also loses the duel, reads slightly *above* it. A duel against our own
clear-cutter measures who wins the race for one shared map, not strength against a field of 177 — this was suspected
on 2026-09-02 and is now quantified.

## Finding 3 — the field reading has been calibrated against the ladder exactly ONCE

The four-opponent field reading is our **selector**: it killed the port and it killed stage 2A. Yet of every bot that
has ever had one, only the opening dispatcher was also put on the ladder. **n = 1.** It agreed that once
(Δwin −0.2219 → 14.59 against 18.72), which is reassuring and is not calibration.

**The decisive second point is orchard 6**, because it is precisely the case where the duel inverted: if orchard 6's
field reading comes out **positive**, the field reading is vindicated and the duel alone is the faulty instrument; if
it comes out **negative**, then our selector would have killed a bot that reads *above* the champion on the real
ladder — a false negative, and we have to assume we may have killed good bots on it. That run is in flight
(`/home/tarstars/audit_orchard6.log` on the VM, the orchard 6 file at sha `32384936…`, the same one that read 18.84,
against the same four opponents on the same pinned 200-map panel).

## Log

- 2026-09-04 03:2x–03:3xZ born on the owner's word; findings 1 and 2 computed from `readings.jsonl` and the panel
  results; finding 3's decisive run launched. — coordinator

## Finding 4 — THE SELECTOR RETURNS "DEAD" FOR A BOT THE LADDER CANNOT TELL FROM THE CHAMPION

orchard 6's four-opponent field reading, run on the exact file that read 18.84 (sha `32384936…`), same pinned panel,
same four opponents, same champion baselines, zero faults:

| opponent | orchard 6 | the champion | Δwin |
|---|---|---|---|
| the champion of record | 65 / 400 | 113 | −0.1200 [−0.1750, −0.0650] |
| orchard 6 *(self-play — structurally invalid, see finding 3)* | 174 / 400 | 324 | −0.3750 |
| the old champion, denial on | 21 / 400 | 147 | −0.3150 [−0.3725, −0.2550] |
| the network clone | 340 / 400 | 331 | **+0.0225** [−0.0375, +0.0800] |
| **FIELD** | | | **−0.1969 [−0.2344, −0.1581]**, `FIELD_BELOW_ZERO` |

**Set beside the opening dispatcher, which we killed yesterday:**

| | field Δwin | field Δmargin | ladder | the champion that week | ladder delta |
|---|---|---|---|---|---|
| orchard 6 | **−0.1969** [−0.234, −0.158] | **−18.74** [−23.5, −14.1] | 18.84 | 18.19 | **+0.65** |
| opening dispatcher | **−0.2219** [−0.256, −0.186] | **−28.71** [−32.7, −24.9] | 14.59 | 18.72 | **−4.13** |

**The two Δwin figures are 0.025 apart — smaller than the width of either one's own confidence interval — while their
ladder outcomes are 4.78 apart.** Our pre-registered kill rule ("below zero with the interval clear of zero") fires on
both. **So the instrument that killed the port and killed stage 2A returns a confident "dead" for a bot the ladder
cannot distinguish from the champion.** Even dropping the invalid self-play cell, orchard 6's remaining three average
−0.1375 and still read dead.

Stated carefully, because the noise cuts both ways: orchard 6's 18.84 against 18.19 is **inside** the 1.68 spread, so
orchard 6 is not *better* than the champion — it is **indistinguishable** from it. That is the point. The field reading
claims a large, confident negative where the ladder finds no difference at all, and assigns nearly the same number to a
bot that is ladder-neutral and one that is four points worse.

## Finding 5 — the same run shows the repair: use MARGIN, not the win indicator

The win indicator throws away every drawn game, and draw rates swing from 0.8 % to 43.5 % between matchups (finding 2),
so it compresses everything into a band narrower than its own error bars. **Score margin uses the whole game and does
not.** On the three bots for which we have both a field reading and external evidence:

| | field Δmargin | external verdict |
|---|---|---|
| orchard 6 | **−18.74** [−23.5, −14.1] | ladder-neutral (+0.65, inside noise) |
| opening dispatcher | **−28.71** [−32.7, −24.9] | ladder −4.13 |
| the port v2 | **−75.7** | 0 wins of 15 against the five real Legend agents |

The margin separates them with non-overlapping intervals and ranks them in the right order; the win rate does not.
A provisional slope from the two ladder points: about **0.5 ladder points per unit of Δmargin**, so **Δmargin ≈ −19 is
ladder-neutral** and −29 is about four points down. **n = 2. This is a working rule, not a law**, and the next bot with
both measurements either confirms it or replaces it.

## Rulings

1. **Δwin is retired as a kill criterion.** No card may kill a build on the win-rate field reading alone.
2. **Δmargin with its 95 % interval is the selector** from now on, with the provisional bar that a candidate is dead
   only if its Δmargin interval lies clear below about −20. Every card carrying the old condition is revised **before**
   its reading is taken, never after — the wood-charging card is amended in this pass.
3. **A candidate that is itself one of the four panel opponents must have that cell dropped** and the field averaged
   over the remaining three.
4. **Nothing below 1.7 on the ladder is evidence** (finding 1), so a ladder hour cannot settle a small change and
   should not be spent on one.
5. **What this does not overturn:** stage 2A's death, which rests on its own ladder reading of 14.59 against 18.72, and
   the port's, which rests on 0 wins of 15 against the real Legend agents — both independent of the panel. The orchard
   line's closure was the owner's call on ladder readings, all of which now sit inside the noise.

- 2026-09-04 03:5xZ findings 4 and 5 measured and ruled. — coordinator

## Finding 6 — our test sets are no longer tests (chatgpt_1, 2026-09-04, accepted)

chatgpt_1's judgement round raised one thing the coordinator's own audit missed, and it is the most uncomfortable item
on this page: **the 24-map smoke slice and the pinned 200-map panel are development data now, not honest holdouts.**
Every build since August has been shaped against those same maps — orchard 5 through 8, the three heroes, the port and
its repair, stage 2A, chatgpt_2's three-troll pair, the wood-charging gate. A set you tune against stops measuring
generalisation, and it will flatter each successive candidate a little more.

**Accepted as a ruling.** Any card whose result would justify a ladder hour must report its number on a **fresh holdout
panel not used to choose the rule or its threshold**. The existing slices stay useful for mechanics — a stall is a stall
on any map — but a *value* number read only on them is a development number and must be labelled as one.

Two more of chatgpt_1's measurement points are adopted with it:

- **Every optimizer must publish its action vocabulary.** An optimum computed without `PLANT` in the action space
  cannot answer the owner's question, and neither of our two optimizers had it (verified in source, 06:3xZ).
- **Both arms must independently pass mechanics before any value number is read** — the lesson chatgpt_2's build paid
  for, now general.

And one correction it makes to *this card*, which stands: **the −20 margin bar has only two calibration points.**
It is a working rule, not a law, and the third bot with both a field reading and a ladder reading either confirms it or
replaces it.

- 2026-09-04 07:1xZ finding 6 added from chatgpt_1's judgement round; accepted with two of its companion rulings. — coordinator

## Finding 1, UPDATED 2026-09-04 08:3xZ — a fifth reading widens the ladder's noise floor from 1.68 to 2.19

The champion of record was restored after the three-troll bot's hour and read again. It is the **identical file**
(sha `0e92f8fa…`) for the fifth time:

| read | score | rank |
|---|---|---|
| 2026-08-28 15:22 | 18.19 | 85 |
| 2026-09-02 09:07 | **17.04** | 110 |
| 2026-09-03 06:22 | 18.14 | 86 |
| 2026-09-03 15:22 | 18.72 | 72 |
| **2026-09-04 08:27** | **19.23** | **60** |

Mean **18.26**, **spread 2.19**, standard deviation **0.82**. The 19.23 is the highest reading this project has ever
recorded — above orchard 6's 18.84 — and **it was produced by changing nothing at all.** That is worth stating
plainly: our best ladder result to date came from resubmitting the same bot on a different day.

**The ruling tightens: nothing below about 2.2 on the ladder is evidence**, up from 1.7. What that retires and what it
leaves standing:

| | difference from the champion that day | verdict |
|---|---|---|
| orchard 6 (18.84) | +0.65 | **inside the noise — never evidence of anything** |
| orchard 8 (17.98) | −0.16 | **inside the noise** |
| stage 2A (14.59) | −4.13 | outside — real |
| the three-troll bot (14.07) | −4.65 | outside — real |

So both deaths that rest on a ladder reading survive the tightening comfortably, and both orchard readings are now
*more* clearly non-evidence than before. It also raises the bar for any future candidate: **a build must be expected to
move the rating by more than about 2.2 before a ladder hour can settle anything**, which makes chatgpt_1's sealed
holdout and paired-margin gate the load-bearing instrument rather than the ladder.

A caveat on the cause, stated rather than assumed: the drift is not proven to be measurement error alone. The field
itself changes daily — 177 players whose own bots move — so part of this 2.19 is a moving opponent population rather
than sampling noise. Either way it is variance we cannot attribute to our own changes, which is what the ruling needs.

- 2026-09-04 08:3xZ finding 1 updated with the fifth reading; the floor moves 1.68 → 2.19. — coordinator
