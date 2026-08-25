# Candidate 2 (the swap) — final page: measured, reproduced, and stopped at two questions that are yours (owner page v3, 2026-08-25 23:15Z)

Task `20260825-dance-cure-candidate-2-swap`, under your ruling of this afternoon (swap, no lock,
the swap back impossible by construction and proved — rule R-1a). Plain words; every code
explained at first use. **Nothing has touched the ladder; nothing will until you rule.** This
page replaces v1 (17:33Z, the stop) and v2 (18:15Z, the diagnoses); it carries the complete,
reviewer-reproduced evidence.

## Where it stands, in one paragraph

The rule was designed and **proved** in 21 minutes (design gate accepted by `codex_1`), built in
an hour, and stopped where we had told it to stop. The build is correct: with the rule off the bot
is **byte-for-byte the champion** on all 34 frozen situations and all 240 panel games. With the
rule on, on the same 240 games, **dances fall from 27 (on 25 games) to 13 (on 12)** and no other
detector moves. Sixteen controls then ran — every one reproduced by `codex_1` from a fresh
archive — and all of them hold: the referee really executes every exchange (66 of 66); the
one-turn memory the proof relies on is right on all 54,800 turns; the whole thing is
deterministic across runs and rebuilds (1,096 of 1,096); the loop counters are proven live
(deleting the standing test sends the consecutive-swap counter from 0 to 344); the orchard-map
guard does real work (0 orchard violations on, 9 off); the trolls are **less idle** with the rule
(idle-with-work 0.38 % vs 0.73 %, worst troll 11.5 % vs 95 %, no troll newly parked, three
un-parked). **The candidate is not qualified**, because two things we committed to stop on before
counting did fire, and both are decisions, not measurements.

## The two questions — both yours

**1. The loop.** On 4 of 240 games (and 2 of 34 situations) the pair trades places every second
turn. Diagnosed from the wire: after the swap the planner hands each troll the goal of the square
it now stands on — the goals stay attached to the cells, not the trolls — so the same block
re-forms the other way and the rule fires again, legally, two turns later. It happens only when
the landing is itself a work square (11 of 12 loop exchanges). **Cost: 5 points on one game of
240**; the other three looping games score exactly as the champion. Also seen from the progress
side: of the 13 dances the exchange touches, **9 end with progress** (three are exactly frozen
library episodes, four would have run to the last turn) and **4 are silenced without progress**
(one is a loop game).

Per your rule nobody adds a lock, a timer or a cooldown. Options:
- **A (recommended): a planner rule — "a troll keeps its goal."** Kept until done or gone, or a
  clearly better one appears (a margin). Then the mover walks on to its own tree and the worker
  steps back onto its tree when the mover has passed: one exchange, both working. Read from the
  wire, that is what every loop game "would have done". One build + panel before any read.
- **B: narrow the swap rule** — never displace a partner standing on the very square it works.
  Kills the loop and the mid-chop displacement, and most of the cure with it (the standing worker
  *is* on its work square in most real dances). Not recommended.
- **C: proceed to the real-game read with the loop measured** (5 points, 4 games in 240). The loop
  will appear in real games too; the read costs the ladder slot.
- **D: stop Candidate 2.**

**2. `m061` and the champion bug.** One map loses 75 points across its two seats (net −24 over
the whole panel: +51 on seven games, −75 on this one). Diagnosed at the code line: the exchange
frees the blocked troll, which fells the map's *last* tree; with no trees left, a fallback in the
**champion's** planner returns a bare `WAIT` and throws away the replant actions it had just built
(two `PICK`s worth 7,500) — both trolls then stand goal-less for 131 and 96 turns with fruit in
hand. Not the swap's code; an R-2 violation in the champion ("a troll with available work must be
employed"), reported unanswered on 08-21, now priced. No gate sees it, because the stall begins
after the arm exhausted the world itself. Recommend chartering the one-line fix (the fallback
*extends* the list instead of replacing it) as **Candidate 0** with its own panel: a likely pure
gain, and it removes a 75-point artifact from every later judgement of Candidate 2.

**3. Order.** My recommendation stands: Candidate 0 first (hours), then Candidate 3 = "keep your
goal" (a day), re-run Candidate 2's panel on top of both, then ask you for the real-game read.

## The evidence table (all reproduced by `codex_1` from a fresh archive)

| what was checked | result |
|---|---|
| rule off = champion, byte for byte (34 situations + 240 games) | yes |
| dances on the 240-game panel, rule off → on | 27 on 25 games → **13 on 12**; blocking 0 → 0; other detectors unchanged |
| exchanges | 46 on 28 games; refused 675 times (teammate on the goal) and 280 (fast troll), by rule |
| a pair swapping back on the very next turn (the proof's falsifier) | **0** in 48,000 turns |
| a pair swapping twice within 6 turns (the pre-committed stop) | **12 on 4 games**, 5 on 2 situations — **open, yours** |
| the counters can count a bad swap (gutted rule) | 17 → 350 and 0 → 344 |
| dances the exchange ends with progress / silences without progress | **9 / 4** of 13 touched |
| referee executes the exchange; memory correct; deterministic | 66/66; 54,800/54,800; 1,096/1,096 |
| orchard rule (P3) on the candidate | 0 violations on 240 views (228 not orchard maps, 12 compared equal, 0 fired); the guard fires 9 times if switched off |
| idle-with-work (safety net), rule off → on | 0.73 % → **0.38 %**; worst troll 95 % → 11.5 %; parked-troll episodes 27 → 16; none added |
| score, panel (own points) | **−24 net**: seven games +51, `m061` −75 |
| score, panel (margin points, own minus opponent) | **+56** (the opponent's score fell 80) |
| score forgone on orchard maps by keeping the guard | +39 margin points — kept, because the guard is a hard rule |
| score, 34 frozen situations (own points) | **+35** (5 better, 1 worse — the loop game, −5) |

Caveats that travel with it: panel games are our own referee model, not the ladder; a "dance"
counted off replays is an upper bound; the eligible orchard class is seat-0-only in the panel
generator; parked-troll episodes are measurable on 107 of 384 troll-lives (the rest never had a
full window of available work).

## What happens next without you

Nothing on Candidate 2 — it waits on 1 and 2. Two small tool follow-ups are chartered after this
mission (the panel gate learns to read the new telemetry; a lint for a message-card defect that
recurred today). The peers owe nothing; the ladder holds the harmless Candidate 1 instrument.

## Where everything lives

`claude_1/cure2/g1-packet-2026-08-25.md` (the complete packet, `agent/claude_1@04ff5234`), the
rule and proof `claude_1/cure2/definitions-g0-2026-08-25.md`, the diagnoses
`m061-diagnosis-2026-08-25.md` and `loop-anatomy-2026-08-25.md`, one report per control in
`claude_1/cure2/`; `codex_1/reviews/dance-cure-candidate-2-swap-*.md` (G-0, C-7, C-8, C-11,
C-13, C-16, P3, C-12, G-1 complete + canonical addendum); the task record
`coordination/tasks/20260825-dance-cure-candidate-2-swap.md`; rule R-1a in `docs/RULES-LEDGER.md`.
