# Why the troll dances — what the real games say (owner brief, 2026-08-24)

Task `20260824-real-game-dance-attribution`, chartered by you today ("do it"). Both gates passed
independently: the class definitions were fixed *before* any count and accepted by `codex_1`
(third revision, 17:27Z); the execution was re-run by `codex_1` from a fresh archive and reproduced
byte-for-byte, six controls fired (17:56Z). Built by `claude_1`; the lineage half by me. Every
number below has one source, named at the end.

**One caveat on every number:** a "dance" here is detector D-1 — one of our trolls stepping back
and forth between two cells for at least 7 turns with zero progress (nothing chopped, picked,
dropped or banked). Measured off replays it is an **upper bound**: the replay reader has to
reconstruct plant clocks it cannot see, and that error *invents* dances rather than hiding them.
"462 episodes" means "at most 462". The bias is the same for every bot and every cohort.

## The answer in one paragraph

Our bots dance in about **one game in six** — the champion in 16.8 % of its real two-troll games,
the very-old bot in 17.4 %, cure C in 16.9 %; the swap-carrying instrument reads 14.6 %, not
distinguishable — and we dance **more than our opponents** (10–13 % in the same games). The dance
did not arrive with any recent change: on the same ladder, alternating two-hour slots, champion
versus very-old came out **+0.00 points apart over 2,268 games**. When we look at what the dancing
troll was actually doing, two shapes account for everything. **In four episodes out of ten a
teammate is standing on a plant next to the dance, working it — chopping, picking, planting on
that one cell — and will not move**; in a quarter of those it never leaves that cell for the rest of
the game. **In the other six of ten there is no teammate in the way at all**: the troll bounces
either while wanting one fixed thing the whole time, or while its stated target keeps changing
inside the window. **No troll ever danced because it wanted nothing.**

## The numbers

Lineage (share of two-troll games with at least one dance; `local_claude_1/dance-lineage/`):

| bot | games | dance rate | trolls blocking each other |
|---|---:|---:|---:|
| July pre-cure bot `v1.2.2-farmcap` | 51 | **0 %** | 43 % of games |
| very-old `98628e98…` (the fixture library's bot) | 1,808 | 17.4 % | 0 |
| cure C `ad3bfefe…` | 1,098 | 16.9 % | 0 |
| **champion (door 1)** `547fa706…` | 1,821 | **16.8 %** | 0 |
| instrument (swap rule + telemetry), 3 batches | 446 | 14.6 % | 0 |
| opponents, in the same games | — | 10–13 % | 14–15 % |

What the dancing troll was doing (`claude_1/dance1/`; instrument = 469 games with the troll's
stated intention every turn, 80 episodes; champion = 306 games, no intentions, 382 episodes):

| what was there | instrument (80) | champion (382) |
|---|---:|---:|
| a teammate next to the dance, standing still and **working** its cell | 34 (42 %) | 146 (38 %) |
| a teammate next to the dance, standing still and **idle** | **0** | 16 (4 %) |
| a teammate alive but none in the way | 46 (58 %) | 214 (56 %) |
| no teammate alive at all | 0 | 6 (2 %) |

Inside the instrument's 46 "nobody in the way" episodes: 22 wanted **one fixed target** the whole
window and still bounced; 21 had a **changing target** (two or more different real targets inside
a 7–40-turn window — not the tidy every-other-turn flip we had expected, which occurred **0**
times); 3 were the two trolls **trading places**. The class "wanted nothing" is **empty, 0 of 80**;
the newer instrument, which also records the candidate the picker threw away, shows the picker
overruling a real want on exactly **2 turns** across its 34 episodes.

Of the 34 working blockers: 24 stand on a live plant; all 34 are busy nearly every turn (idle on
≤ 5 % of turns, exactly 0 % in 29); **10 never leave that cell again** for the rest of the game.
How dances end (instrument): 52 by the dancer simply making progress, 16 when the parked
teammate finally moves, 9 run to the last turn, 3 by a place-swap. Champion: 218 / 75 / 79 / 10.
Half of all episodes are the minimum 7-turn window (34 of 80; 159 of 382) — and at that length the
"blocker" always moves on later, while at longer windows 10 of 23 blockers never move again. Two
different objects, most likely; the criterion does not separate them, and no count was adjusted.

## What the dance is not

- **Not the swap rule's doing.** The champion has no swap rule and dances at the very-old bot's
  rate. And the "two trolls traded places" detector, which we expected to be silent on the July
  bot, fired 3,256 times there — so that class is now named descriptively (`POSITIONAL_EXCHANGE`)
  and carries no causal claim; whether the detector is too broad or the ledger's premise about the
  old bot was wrong is **not known**.
- **Not the fixture library's disease.** The library's dominant shape — a troll parked *idle* on a
  plant while its teammate dances in front of it (14 of its 38 episodes) — occurs **0 times in 80
  real instrument episodes** and 16 times in 382 champion ones. Same geometry, different idleness:
  the real blocker is *working*. Every earlier cure conversation was about the idle case.
- **Not a troll with nothing to do.**

## The one thing to rule on, if you want a next step

**Is "a teammate working the plant it is standing on, for as long as it takes, right next to the
dance" acceptable play or a defect?** That is where four episodes in ten are. Rule R-2 (a troll
with work must be employed) does not obviously reach it — the teammate *is* employed; it is the
dancer that is not. Nothing is chartered against it; no cure is proposed.

## Not established

Why any dance happens (the facts are correlations with the window, not causes); that batch 3 of
the instrument dances more (18.8 % vs 11 %; different days, different opponents); that the
instrument and the champion differ (gaps untested); whether the short windows are real dances or
detector noise; anything about opponents' reasons (their bots carry no telemetry); prevalence
beyond these corpora.

## Where the evidence lives

- Lineage grading: `local_claude_1/dance-lineage/lineage-grading-2026-08-24.md` + `results/`
  (`agent/local_claude_1@6595935e`); champion package `dance-lineage/door1-games/` (`@4b9bd563`).
- Definitions (r3, accepted): `claude_1/dance1/definitions-g1-r3-2026-08-24.md`
  (`agent/claude_1@7405b779`); execution report, fact tables and `claude_1`'s own brief:
  `claude_1/dance1/g2-execution-2026-08-24.md`, `results/*.json`, `owner-brief-2026-08-24.md`
  (`agent/claude_1@4c92432f`); rulings `codex_1/reviews/real-game-dance-attribution-*.md`.
- Every count above was re-derived by the coordinator from the published fact rows before this
  brief was written.
