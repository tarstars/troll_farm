# HANDOVER 2026-08-29 11:5xZ — the orchard series (third troll card, design rounds 3–7), the readings, what is on the ladder

Delta since `coordination/HANDOVER-2026-08-28-third-troll-on-the-ladder.md` (2026-08-28 09:2xZ) through
2026-08-29 11:5xZ, written by `local_claude_1` at the owner's request ("prepare for context flush").
Trunk at writing: `origin/main` == `agent/local_claude_1` == the checkout `/home/tarstars/prj/troll_farm`.

## Resume here

- **On the ladder: orchard 7, round 2** (`candidate-orchard7-v6-instrument.rs`, sha `eb383fd1…`, submission
  `41210228`, since 2026-08-28 21:27Z, read 16.6 at rank 117 at 22:29Z). **The VM queue is EMPTY** — the
  runner ticks every 5 min and does nothing ("queue empty"); the last bot stays up. To continue: add items
  to `local_claude_1/ladder-queue/queue.json` IN THE VM CHECKOUT (`ssh troll-vm`, `/home/tarstars/prj/troll_farm`,
  `git pull --ff-only origin main` first; the runner does not pull) — the next tick submits the first pending
  item. Scripts that did it: `/tmp/queue_orchard7.sh`-style (pull, edit queue.json, commit, push) and
  `orchard*_now.sh` (retire the current item in state.json, then a tick submits the next).
- **The readings of the orchard series** (all against TODAY's champion: the champion of record re-read
  **18.2 at rank 85** on 08-28 15:22Z — yesterday 21.2/42 on the same bytes; the field moved):
  - three heroes 11.7 / 12.0 (the funding phase loses; the dance small);
  - orchard 5 (plant first, 2+1, chop follows iron, raid stop, preference, way home) **14.7 / 13.5**;
    no second troll in 10/160 games each round (planting spent the lemons; the turn-35 deadline abandoned);
  - **orchard 6 (orchard 5 + the orchard on the cells beside the tent, one door free) 18.8 at rank 70 —
    the best of the series, above today's champion**: 95–65 (59 %) vs rating 16.5, the third troll in
    134/160, 10 single-troll games (the abandon defect still in it);
  - **orchard 7 (orchard 6 + never abandon the opening + a 2+2 fruit reserve before planting + orchard
    cells within 2 steps of the tent) 16.7 / 16.6**: 55 % / 51 %, the third troll in 147/145 of 160,
    single-troll games 1/1 (the fix works), vs 4+-troll bots 63 % / 38 %.
  Readings are ±1.5 each; 6 > 7 twice. Packages: `local_claude_1/ladder-queue/games-<id>/`; read with
  `local_claude_1/the-floor/ladder_read.py <pkg> <agent> <label>` (every TRAIN; own_trolls per game in
  `ladder-read.json`) and `local_claude_1/third-troll/dance_read.py <pkg> <agent> [--game ID]` (turns).
- **The owner's next decision (not yet asked):** which of orchard 6 / orchard 7 to keep working from, or
  whether to re-read the champion. My view: orchard 7's fixes are right by the game state (no lone-troll
  games), its two readings are lower than 6's one — a third reading of each would settle it; the owner
  reads games and finds the defects faster than the bench does (five of the seven designs came from a
  game the owner watched).
- **The generator chain** (all under `local_claude_1/third-troll/`, each stacked on the previous:
  `make_third_troll.py` (9) → `make_three_heroes.py` (+7) → `make_orchard.py` (+5) → `make_orchard2.py`
  (+10) → `make_orchard3.py` (+2) → `make_orchard4.py` (+3) → `make_orchard5.py` (+4) → `make_orchard6.py`
  (+4) → `make_orchard7.py` (+4)); `mk.STACKED = True` makes the diff-count check use the real diff.
  Bed: `fixtures_diff.py --arm <abs> --submission <abs> --out <abs>`; smoke: `smoke.py --records
  smoke-maps-seed0.jsonl --arm <arm> --out <json> --third-spec "2 3 0 3|2 3 0 2|2 3 0 1"`; `probe.py <map>
  --arm <arm>` prints a local game's turns. Diffs `readable/diffs/orchard*.diff`.
- **codex_1's reproduction (row 0-7)** was last re-pointed at the orchard (first version); it is far behind
  the builds — re-charter at orchard 7 (or whichever the owner keeps) or close the row.
- Ritual: sweep → read whole → `--mark` → commit; first command `cd …-local_claude_1 && git pull --ff-only
  origin main` (the VM pushes to main); `git pull` for the checkout in a separate call.

## The orchard series, in one table (owner's words → the rule → local smoke → ladder)

| # | owner's read | rule added | smoke (24 real maps) | ladder |
|---|---|---|---|---|
| orchard | "let's do orchard" + "use the gates logic … the farthest gate from the enemy" | 4 lemons + 2 plums at the far gate, after the second troll; protected; dance fix | third troll 21/24 at 119, +1193 | stood down |
| orchard 2 | ghhttt game: far ore, enemy raids, too big | chop follows the iron (3/2/1/none); stop planting when raided; 2+1 | 23/24 at 103, +784 | stood down |
| orchard 3 | "lemon planted on 90th step … plant lemon, lemon, plum first"; concurrent picking | plant first from turn 1; each troll locked to one resource | 24/24 at 94 (one 25-turn camp) | stood down (13.8 at 16 min) |
| orchard 4 | (the camp) | the resource assignment a preference, not a lock | 24/24 at 94, funding 70 | superseded |
| orchard 5 | migcuk game: "trolls collect farthest fruits" | the way home in the fruit/ore scores | 24/24 at 94, +719 | **14.7 / 13.5** |
| orchard 6 | "no lemon and plum on adjacent to tent cells" | the doors are the orchard, one door free | 24/24 at 88, +819 | **18.8 / 70** |
| orchard 7 | games 900722253/450/3150: lemons spent, deadline abandons, plum 9 steps away | never abandon; 2+2 reserve; cells within 2 of the tent | second troll 24/24, third 24/24 at 88, +831 | **16.7 / 16.6** |

## Operational notes (new)

- The session was away 11:3x–18:0xZ on 08-28 and again overnight; the VM runner carried the queue both
  times and pushed every reading and package to `main`. After an absence: `git pull --rebase origin main`
  in the worktree, then read `readings.jsonl`.
- A shell heredoc without quotes ate backticks in a ledger row once (fixed); write files from quoted
  heredocs or python.
- The "stalled" detector in the smoke compares an idle run with the resident's over the same window; the
  bare-map idles are not defects, a troll camping on an immature tree was (orchard 4's fix).
