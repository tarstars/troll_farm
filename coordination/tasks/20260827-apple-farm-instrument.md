# Task — the apple-farm instrument (the owner's one-variable experiment, 2026-08-27)

- Born 2026-08-27 ~13:10Z by the owner's word ("let's do it"; design approved "1 c, 2 yes").
- Record owner: local_claude_1 (coordinator) · Work owner: **local_claude_1** (builds it itself, as with the denial ablation: the owner is waiting and a bot's wake latency doubles the loop) · Reviewer: **codex_1** (reproduces the build afterwards, as row 0-4 did) · Arena: the coordinator submits (ladder queue slot 3).
- Status line: **READ 14:36Z — 19.8 at rank 49/176, 1.4 below the champion's 21.2/42; the games collected and read; the owner rules (keep for a second hour / return the champion / refine).** Submission `41203549`, 13:34:48Z, agent `6668182` (build: arm sha `82c8ddd1…`, submission sha `8c6bc206…`, 66,082 B, +120/−0; bed PASS 34/34 with 2 differing; smoke PASS 24/24 real maps; codex_1 REPRODUCED all three 14:07Z).

## The rule (owner, plain words)

If a grass cell touching our shack also touches water, the starting troll plants an apple there on turns 1–3 (a water-side apple regrows a fruit every 2 turns), runs the normal opening (collects the training bill, trains the second troll), and once the second troll exists returns to the cell and harvests it to the end of the game — HARVEST and DROP alternating without moving, half a point a turn. No own troll ever fells the farm tree. The trained troll is unchanged (harvest power 0). Everything else is the champion.

Why: a water-side full apple is the fastest income in the game (one fruit every 2 turns = 0.5 points a turn for the weakest troll, against the champion's ~0.31 wood points per troll-turn on average). Census of the 24,021 real ladder maps: at least one water-side door 40.3 % of games, empty at the start 36.5 %, two empty 10.0 %; a water-side apple already standing there 1.9 %. Owner's two design answers: (1c) plant first, harvest after training — no parked troll; (2) the trained troll stays harvest-0 (one variable).

## Done means

1. The build through the generator chain `local_claude_1/apple-farm/make_apple_farm.py` (four pure insertions applied identically to the diagnostics arm and the readable champion; compile; compact; round trip; distinct from every bot on the ladder; `readable/diffs/apple-farm.diff` +N/−0).
2. The 34-situation differential bed (`local_claude_1/apple-farm/fixtures_diff.py`): plays, deterministic, compacted == arm, telemetry 0 errors (a "differs" count is a fact, not a gate).
3. A **smoke** run of full local games on real ladder maps that have a water-side door (`local_claude_1/apple-farm/smoke.py`), read only for the mechanics: the apple is planted on the farm cell by turn ≤ 4; the farm troll harvests and banks after the second troll; no own CHOP on the farm cell; the champion's other behaviour on the same maps compared for a sanity margin. Not a value gate.
4. The champion's current games collected; the instrument submitted; **one-hour reading** against the owner's stated prediction (coordinator's on record: a rise, visible within the hour); its 160 games collected before anything else is submitted.
5. codex_1's independent reproduction of the build (both hashes, the bed).

## Dead means

The bed or the smoke shows the rule not firing on a map that has a water-side door, a troll stuck or blocked, or the compacted file behaving differently from the arm — then no submission, the obituary names the defect, and the owner decides whether a bounded repair is chartered.

## Budget

1 build, 1 bed, 1 smoke, 1 hour on the ladder, 1 reproduction. Nothing else is promoted, reverted or chartered by this card.

## Known simplifications (on record, not defects)

- If the training bill is affordable at turn 1 (instant training), the farm troll plants on turns 1–3 and then waits on the cell ~10 turns for the tree to bear fruit (the "chop meanwhile" refinement was not taken).
- The farm keeps one apple in the shack for the bill until the second troll exists; with 0 apples in the shack and no tree the troll waits on the cell (practically unreachable: we start with 2–10 apples and every harvest returns one).
- Two water-side doors (10 % of games) are not used: one farm, one troll.

## Known gap found by the bed (on record; the ladder bytes are unchanged)

On the two fixture worlds that have a water-side door (OSC-026, OSC-030) the farm troll **waits** where the champion moves: those worlds start with **0 apples in the shack**, so the rule has nothing to plant and its fallback is WAIT — a parked troll. On the real ladder the shack holds 2–10 apples at the start and every harvest returns one, so the path needs an opponent to fell the young tree while the shack is empty (a 2-apple draw, ~1 game in 9, and an early enemy chop at our shack — rare together). The one-line fix is drafted: with no tree, nothing carried and no apple in the shack, the farm returns the troll to the champion's normal behaviour instead of WAIT. Not applied mid-hour (it would contaminate the reading); to be applied as "the same rule made safe" if the farm becomes the champion, or as the next build if the owner asks.

## Log

- 13:0xZ design presented (waits on the cell while growing; trained troll harvest-0) → owner: "let's discuss it" → the two problems and proposals explained → **owner: "1 c / 2 yes"** (plant first; harvest-0 stays).
- 13:2xZ build: `make_apple_farm.py` first run clean (+120/−0, round trip exact, distinct from every bot). Bed PASS (34/34 play; differs 2/34; deterministic; compacted == arm; telemetry 0). Smoke first run 8/12 "BAD" = my script's door order (right-left-down-up) differed from the bot's (down-right-up-left) on maps with two wet doors — the bot had planted and harvested on all 12; order fixed, re-run: PASS 24/24.
- 13:33Z collector re-run for the champion `41202036`: identical package to 09:25Z (sha `3fe5dc49…`) — no new games; the duplicate directory removed.
- **13:34:48Z submitted as `41203549`** (sha `8c6bc206…`, 66,082 B). Early look 13:35Z: 5.2 at rank 174, 26 s in (not a reading). One-shot cron for the reading at 14:36Z.
- 13:48Z–14:07Z codex_1: build and bed REPRODUCED; smoke blocked (corpus absent on the VM) → unblocked by the 67.5 KB slice → **REPRODUCED on all three** (+2831 on the slice).
- **14:36Z the reading: 19.8 at rank 49/176** (61 min in; agent `6668182`). Games collected (`games-41203549/`, 160, sha `7e542953…`) and read with `ladder_read.py` (fixed once: our starting troll's id is the seat number):

  | bucket | apple farm (this batch) | the champion (its 09:25Z batch) |
  |---|---|---|
  | all 160 | 79–81 (49 %), own 213.7 / opp 255.1 | 85–75 (53 %), own 183.5 / opp 197.3 |
  | maps with a farm cell | **33–20 (62 %)**, own 284.9 / opp 318.7 — the rule ran in all 53 (planted turn 3 in 44; ~126 harvests; ~116 apples banked; replanted after an enemy felling in 36) | 25–35 (42 %), own 190.7 / opp 231.4 (60 games) |
  | maps without one (identical play) | **46–61 (43 %)**, own 178.5 / opp 223.6 | 60–40 (60 %), own 179.2 / opp 176.8 |
  | opponents with 3+ trolls | 54 % | 50 % |

  Reading of the table: the farm turned its maps from our worse class into our better one (≈ +38 points of win rate, difference-in-differences), while the identical-play games went 17 points worse — the batch's draw was harder. Two costs: the opponents fell the tree and take its wood (36 replants), and on farm maps the opponent scored +87 against the champion's batch (+47 elsewhere). The prediction "a rise, visible within the hour" was wrong on the number.
- 15:0xZ deeper cuts (owner: "what analytics of apple farm shows?"): **score composition** on farm maps — the farm's 285 = 116 apples + 42 wood × 4 = 168 (the champion there: 191 = 3 fruit + 47 wood × 4 = 187): +113 apple points, −5 wood; on no-farm maps identical (178.5 vs 179.2, same wood). **Wins by opponent troll count on farm maps** — vs 2 trolls 21/24 (champion 15/30), vs 3 trolls 7/12 (4/12), vs 4+ trolls 5/17 (6/18). **The felling war** — never felled in 17 games (142 harvests, but the 464-point opponents; 7 wins); felled and replanted in 36 (7 replants a game on average, up to 20; 106 harvests; 26 wins); 2-troll opponents fell it in 21 of 24 games and lose anyway. **The draw on no-farm maps (identical play)** — 39 three-troll opponents, 11 wins, vs the champion's 30 and 18. Apples banked ≈ harvests (116 / 118).
- **15:0xZ owner: "let's just resubmit apple farm 5 times and see where it lands."** Round 1's package re-checked (final). **Round 2 submitted 15:04:07Z as `41203992`**; reading cron 16:06Z; the protocol is GOAL.md's "THE FIVE ROUNDS".
