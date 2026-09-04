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
