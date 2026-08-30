# The first clone — its games for the owner's read (2026-08-30 04:5xZ)

This is the Phase 2 milestone of the neural-network line (card `coordination/tasks/20260829-nn-bot-way-b.md`):
a network that has only *copied* the top four players' recorded moves — no self-play yet — playing whole
games against the champion of record's actual submitted file.

## What is in this directory

| file | what |
|---|---|
| `clone-pilot.pt` | the trained network (454 kB; the four-key checkpoint, plan vocabulary `v400-2026-08-29`) |
| `clone-pilot.json`, `train.log` | the training report: 4 epochs over 817,811 recorded decisions from 748 games (delineate, norxondor, MSz, Bubaptik's latest version), ~30 min an epoch on this host |
| `bench-argmax.json` | the bench, plan head decoded by argmax: 48 games = the 24 owner's-read maps × both seats, against `cgauto/submissions/candidate-champion-denial-off-v6-instrument.rs` (sha `0e92f8fa…`) |
| `bench-argmax-replays.jsonl` | the 48 games, turn by turn — **the games to read** |
| `bench-sample.json` | the same bench with the plan head *sampled* instead of argmax (a control; it changes nothing) |

## How to read a game

```
cd /home/tarstars/prj/troll_farm-local_claude_1
PYTHONPATH=. /home/tarstars/nn-venv/bin/python local_claude_1/nn-bot/bench.py \
    --read local_claude_1/nn-bot/results/clone-2026-08-30-a/bench-argmax-replays.jsonl --game 10
```

`--game N` is 1…48 (`0` = all). The header names the map, the seats and the scores; each line is one turn:
the champion's commands on the left (its `MSG NARRATE` telemetry included), the clone's on the right.
The table of the 48 games — map, seat, scores, trolls trained (talents and turn), how the game ended,
loops — is the `rows` list in `bench-argmax.json`. Game 10 (map `89e90612…`, the clone on seat 1) is a
win, 225 to 217; game 1 (map `7b515d6d…`, seat 0) is a loss, 76 to 167, with no troll trained; game 34
(map `7a082aa2…`, seat 1) has the clone's one long loop (87 turns on one cell) and still 185 to 201.

## The numbers, plainly

- **Training** (no self-play, no reward — copying only): plan accuracy 0.74, command accuracy 0.65 over the
  training rows; per verb, MOVE 41 % (the exact cell reached, one of up to 242 — the hard label), CHOP 90 %,
  DROP 97 %, HARVEST 93 %, MINE 80 %, PLANT 85–100 % (apple 40 %), PICK 15–23 %. No games were held out on
  this first run (the trainer's default); the bench is the judge, as the card says.
- **The bench, 48 games vs the champion of record**: the clone **won 9** (4 on seat 0, 5 on seat 1), scored
  **133.8 on average to the champion's 186.2** (margin −52); it played every game legally to the end —
  **0 illegal commands, 0 timeouts**; 31 games reached turn 300, 8 ended with no trees left, 9 by the
  referee's mercy rule; 1 game with a loop.
- **It buys trolls** — in 44 of 48 games, at turn 1, and it buys *its teachers'* trolls: (2,2,2,2) ×8,
  (2,2,1,2) ×6, (3,2,2,2) ×6, (2,2,2,1) ×5, (1,3,1,2) ×4 … — harvest-carrying workers, where the champion
  buys (2,2,0,2). The four games without a purchase were its worst (92 points).
- **For scale**: a random-legal policy on the same bench scored 13.5 to the champion's 157; the clone is ten
  times that, at 72 % of the champion's score, winning one game in five on its first day.

## What I saw reading the games (the top-down read you asked for)

- The clone's *second* troll behaves like a teacher's: it walks to trees, harvests, plants lemons, brings
  fruit home.
- Its *first* troll often falls into **pick-and-drop churn** at the shack — `PICK LEMON` one turn, `DROP`
  the next, for stretches of ten or twenty turns (game 10, turns 12–40). That is the copying showing: PICK
  and DROP are 13 % of the recorded moves, and with no goal of its own the clone alternates them. It is
  the obvious first thing for PPO (Phase 3) to unlearn, because it costs points every turn.
- It never chops as a plan, only when it happens to stand on a tree — the deforestation the top players run
  is not in its behaviour yet; that is where the champion's 186 comes from.
- The sampled decoding (a control) is the same player: 8 wins, 133.2; it buys a second troll more often.

## What happens next (no word needed from you)

Phase 3 starts from this checkpoint: PPO in our own engine against the linked bots and frozen copies of
itself, with this clone as the anchor, on real maps — gates every few days on this same bench (400 games
against the champion's file and against orchard 6). The target stands: ≥ 60 % over 400 games against
both, three gates in a row, exported and bedded — ready for the ladder by 2026-10-17.
