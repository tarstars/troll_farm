# HANDOVER 2026-08-27 (third) — the apple farm: from the owner's economy question to five ladder rounds

Delta since `coordination/HANDOVER-2026-08-27-simplified-champion.md` (11:45Z) through 2026-08-27
~15:40Z, written at the owner's request ("prepare for context flush") by `local_claude_1`.
Trunk at writing: `origin/main` == `agent/local_claude_1` == the checkout `/home/tarstars/prj/troll_farm`.

## Resume here

- **The champion of record is unchanged: the simplified bot `41202036`** (sha `0e92f8fa…`, readable
  `readable/denial-off-champion.rs`, last reading 21.2 at rank 42). It is **off the ladder** while the
  apple farm's five rounds run; it returns only on the owner's word.
- **On the ladder: the apple farm, round 2 — submission `41203992`, 15:04:07Z** (the same file as
  round 1: `cgauto/submissions/candidate-apple-farm-v6-instrument.rs`, sha
  `8c6bc206417c6d22b593372ce42e74ce5698646c1f8a860073f349a2a082708c`, 66,082 B). Owner ruling 15:0xZ:
  *"let's just resubmit apple farm 5 times and see where it lands"* — five one-hour rounds, six
  readings in all; **round 1 read 19.8 at rank 49 (14:36Z)**. The protocol is **`coordination/GOAL.md`
  → "THE FIVE ROUNDS"**: reading (`python3 cgauto/cg_rank.py`) → ledger row `APL-r<n>` → collect its
  games (`local_claude_1/narrate/collect_submission_games.py`, package into
  `local_claude_1/apple-farm/games-<id>/`) → `python3 local_claude_1/apple-farm/ladder_read.py <package>
  <agent id> <label>` → submit the next round (`python3 cgauto/api_submit_once.py <file>
  --expected-sha256 <sha>`) → a one-shot session cron at +62 min (local clock = UTC+3) → board, card
  log, five-part log note, commit, fast-forward `main`, pull the checkout. **After the sixth reading:
  no submission; the six numbers (mean, spread) go to the owner, who rules.**
- **Crons alive in this session:** `7cdf713d` one-shot at 16:06Z (= 19:06 MSK) = round 2's reading and
  round 3's submission; `a956cd82` hourly at :37 (reads the current submission, does nothing else).
  Session-only crons survive a context flush but **die with the session** — in a new session, read the
  ledger's last `APL-r<n>` submission time and re-create the pending one-shot cron at +62 min.
- Ritual unchanged: `cd /home/tarstars/prj/troll_farm-local_claude_1 && python3
  scripts/inbox_sweep.py --me local_claude_1 --fetch` → read every new message whole → `--mark` as its
  own step → commit the seen state. Every shell command carries its own `cd`.
- **Nothing is waiting on the owner** until the sixth reading (~20:30Z).

## The day since 11:45Z, in order

1. **12:0xZ — the owner's economy question** ("when is it more profitable to collect apples than to
   chop wood?"). Answered from the referee rules: fruit 1 point, wood 4, but a felled tree yields only
   min(size, free carry) wood — our starting troll takes 1 wood (4 points) from any tree; a water-side
   apple regrows a fruit every 2 turns (dry: every 9) — the fastest income in the game; a troll on a
   shack-adjacent tree cell banks 0.5 points a turn without moving; the champion's chopping averages
   ~0.31 points per troll-turn. Census of the 24,021 real ladder maps (`data/processed/maps.jsonl`,
   main checkout only): a water-side apple already adjacent to our shack 1.9 %; a water-side **door**
   (plantable) in 40.3 % of games, empty at the start 36.5 %, two empty 10.0 %.
2. **~13:10Z — "let's do it."** Design presented (bounded change, brainstorming gate), discussed, and
   ruled **"1 c / 2 yes"**: (1c) the starting troll plants the apple on turns 1–3, runs the normal
   opening, and once the second troll exists returns and harvests to the end — no parked troll;
   (2) the trained troll keeps harvest power 0. Card `coordination/tasks/20260827-apple-farm-instrument.md`.
3. **13:2xZ — build.** `local_claude_1/apple-farm/make_apple_farm.py`: four pure insertions (+120/−0)
   applied identically to the champion's diagnostics arm and its readable source (`farm_cell` /
   `farm_unit` in `impl MoisanBot`, `farm_candidates` in `impl YamoBot`, a hook before
   `by_id.insert`, a skip in `chop_candidates`); compile, compact, round trip exact, distinct from every
   bot; diff `readable/diffs/apple-farm.diff`. Bed `fixtures_diff.py` PASS (34/34 play; differs 2/34 =
   the two fixture worlds with a water-side door; deterministic; compacted == arm; telemetry 0). Smoke
   `smoke.py` on 24 REAL maps with a water-side door vs the resident on the same map and scripted
   opponent: planted turn 3 on 24/24, 91–145 harvests, no own chop on the farm, own score +118 a game
   (weak scripted opponents; a fact, not a verdict). The champion's window held no new games since
   09:25Z (collector re-run, identical package).
4. **13:34:48Z — submitted as `41203549`** (agent `6668182`). Row 0-5: codex_1 reproduced the build and
   bed at once; its smoke was blocked (the 53 MB corpus is not on the VM) → `smoke.py --write-records /
   --records` and a 67.5 KB slice `smoke-maps-seed0.jsonl` (replays the corpus run identically) →
   **REPRODUCED on all three** (14:07Z; +2831 on the slice). Row closed, ack sent.
5. **14:36Z — the one-hour reading: 19.8 at rank 49 of 176**, 1.4 below the champion's 21.2/42. My
   prediction "a rise, visible within the hour" was wrong on the number; the owner had stated none.
6. **The analysis** (`ladder_read.py` over the farm's 160 games and the champion's 160; card log):
   on the 53 farm-map games the rule ran in every game (planted turn 3 in 44; ~126 harvests; ~116
   apples banked; replanted after an enemy felling in 36, seven replants a game) and won **62 %**
   (the champion 42 % on such maps): 285 = 116 apples + 42 wood×4 vs 191 = 3 + 47 wood×4; wins vs
   2-troll opponents 21/24 (champion 15/30), vs 3-troll 7/12 (4/12), vs 4+ 5/17 (6/18). On the 107
   no-farm games — byte-identical play — 43 % vs the champion's 60 %. **Why lower** (corrected after
   the owner asked): not a harder draw by rating (the farm's opponents were weaker, 19.8 vs 20.7 —
   the signature of converging lower); **repeated opponents** — two 3-troll bots paired five times each
   on no-farm maps, 0 wins in 10 (agents `6480516`, `6491567`), while the champion's batch drew
   `6481270` sixteen times and beats it; against the 28 common opponents 46/109 vs 62/120; the farm
   bot lost the middle of its batch (15, 17 of 40) and its rating anchored. On farm maps the farm flips
   only close games (its losses there have a median margin of 236 — 4-troll bots at 400+) and the
   opponents take a cut (felling and harvesting the tree: +87 for them on farm maps). Honest estimate
   of the farm's rating effect: small and positive (half a point to a point), inside one reading's
   noise (the keep-goal bot read 18.4/19.2/21.0 on three submissions).
7. **15:0xZ — the owner: five more rounds.** Round 1's package re-checked (final); **round 2 submitted
   15:04:07Z as `41203992`**; cron `7cdf713d` at 16:06Z; GOAL.md "THE FIVE ROUNDS".

## Ledger (`local_claude_1/ladder-measure/ledger-2026-08-26.md`)

| row | bot | submitted | id | agent | read | score | rank |
|---|---|---|---|---|---|---|---|
| ABL-1h…5h | the champion (simplified) | 08:21:51Z | 41202036 | 6667789 | 09:25–12:57Z | **21.2** | 42 |
| APL / APL-1h / APL-2h | the apple farm, round 1 | 13:34:48Z | 41203549 | 6668182 | 14:36Z, 14:57Z | **19.8** | 49 |
| APL-r2 | the apple farm, round 2 | 15:04:07Z | 41203992 | (at the reading) | due ≥ 16:04Z | — | — |
| APL-r3 … r6 | rounds 3–6 | each after the previous reading | | | | | |

## Artifacts landed today (all on `main`)

- `local_claude_1/apple-farm/`: `make_apple_farm.py` (generator; the template for a multi-line
  insertion experiment: anchors that occur exactly once in both files, the same text in both, +N/−0
  asserted), `champion-apple-farm-v6-instrument.rs` (+ `.sha256`), `apple-farm-readable.rs` (the
  readable champion with the rule; becomes `readable/apple-farm-champion.rs` only if it wins),
  `fixtures_diff.py`, `smoke.py` (`--write-records` / `--records`), `smoke-maps-seed0.jsonl` (the
  24-map slice), `ladder_read.py` (the per-game reader of a collected package; the pattern for any
  bot: farm maps vs the rest, did the rule run, wins, opponents' troll counts and ratings),
  `results/{build,fixtures,smoke}.json`, `games-41203549/` (160 games, 6.78 MB, sha `7e542953…`,
  plus `ladder-read.json`).
- `cgauto/submissions/candidate-apple-farm-v6-instrument.rs` (+ `.sha256`), `readable/diffs/apple-farm.diff`,
  `readable/reports/candidate-apple-farm-v6-instrument.round-trip.json`.
- `local_claude_1/denial-ablation/games-41202036/ladder-read.json` (the champion's batch, read the same way).
- Cards: `20260827-apple-farm-instrument.md` (the log holds the two-batch table and the "why"),
  `20260827-apple-farm-verify.md` (0-5, DONE). Messages: `134051Z` (0-5 charter), `140222Z` (the
  slice), `144403Z` (ack — REPRODUCED). Both peers' queues are drained.

## Operational notes

- **Reading a collected package:** frame 0's `view` holds the map (`global.inputmodule`: "w h\nrows");
  every keyframe's `inputmodule` holds both inventories (player 0's line, then player 1's: plum lemon
  apple banana iron wood); each of our frames holds our full `stdout` line (the `MSG NARRATE v6` line,
  then the commands). **Our starting troll's unit id is our seat number** (troll 0 for player 0, troll
  1 for player 1). `scores[index]`, `agents[].score` = each agent's current rating.
- **The bot's door order** (`ortho_neighbors`) is down, right, up, left; any predictor of the farm cell
  must walk doors in that order (my first smoke run mislabelled 4/12 maps for this).
- **Ladder readings are noisier than ±1.5 suggests when read as win rates:** a new submission's batch
  is a rating climb whose opponents are matched to its trajectory, with a few opponents repeated many
  times; compare buckets within a batch, and never call the opponent-rating mean a "draw".
- **Known gap in the farm rule (card):** with 0 apples in the shack and no tree the farm troll waits
  (fixture-world case; on the ladder needs a 2-apple draw and an early enemy felling). One-line fix
  drafted (fall back to normal behaviour), NOT applied — apply as "the same rule made safe" if the farm
  becomes the champion.
- Big data stays out of the VM: the 53 MB map corpus lives only in the main checkout's
  `data/processed/` (gitignored); give peers tool-written slices ≤ 10 MB.
- The collector, the submit tool and the sweep are as before; `git rev-parse --short A B` fails —
  one ref per call; set the board's "Last updated" by pattern.
