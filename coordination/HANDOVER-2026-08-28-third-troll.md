# HANDOVER 2026-08-28 — from the apple farm's rounds, through the floor and the reconstruction of the four top players, to the third troll

Delta since `coordination/HANDOVER-2026-08-27-apple-farm-five-rounds.md` (2026-08-27 15:40Z) through
2026-08-28 ~04:40Z, written at the owner's request ("prepare for flushing the context") by `local_claude_1`.
Trunk at writing: `origin/main` == `agent/local_claude_1` == the checkout `/home/tarstars/prj/troll_farm`.

## Resume here

- **The goal is the third troll** (owner 04:3xZ: "set as next goal bot with the third troll"): card
  `coordination/tasks/20260828-third-troll.md` — the champion of record plus one change: after the second
  troll, both trolls collect the bill of a 2/3/0/3 lumberjack (6 plums, 11 lemons, 2 apples, 11 iron),
  trained the turn it is affordable; the design questions with recommended answers are on the card;
  `coordination/GOAL.md` carries the protocol. **First step of the next session: present design round 1
  to the owner in one message (the four questions), then build** through the generator chain (templates:
  `local_claude_1/the-floor/make_the_floor.py`, `local_claude_1/apple-farm/make_apple_farm.py`; the bed
  and smoke scripts under `local_claude_1/the-floor/` are the ones to adapt), charter codex_1 to
  reproduce, ask the owner's prediction, submit, read after one hour, collect the games.
- **The ladder:** the floor (`cgauto/submissions/candidate-the-floor-v6-instrument.rs`, sha `31cd23c0…`)
  is up as round 3, submission `41206409` (04:21:54Z), **its last round**: reading at 05:24Z (session
  cron `68fe25fd`; crons die with the session — re-create from the ledger's submission time at +62 min,
  local = UTC+3), games into `local_claude_1/the-floor/games-41206409/`, **no round 4**. Readings so
  far 19.2 (round 1), 19.1 (round 2) — both 2.0 below the champion's 21.2/42. The floor stays up unread
  until the third-troll bot is ready; the champion of record `41202036` returns only on the owner's word.
- **`cg_rank.py` (the leaderboard) fails at login for most of the night** (`JSONDecodeError` in
  `get_codingamer_from_handle`; it worked at 03:39Z and 04:2xZ, failed at 03:0xZ, 03:1xZ, 04:16Z). The
  fallback used for two readings: the rating is the API's `score` field stamped on our agent in every
  collected game (identical across the batch); the rank is "unreadable". The submission endpoint and the
  collector work regardless. The collector needs the agent id: it is in `cg_rank.py`'s room line when
  that works, else read it from the battle window (the previous round's id + the pattern, or the first
  battle's players).
- **The apple farm** is paused after four readings (19.8/49, 19.8/50, 18.6/78, 19.9/47; mean 19.5);
  its four packages are collected and read (`local_claude_1/apple-farm/games-*/`); rounds 5–6 only on
  the owner's word.
- **Track R is done**: the four top players' algorithms — `docs/reports/2026-08-28-top-four-algorithms.pdf`
  (the owner's report, 8 pages, two review rounds, 0 overfull lines; source `.tex`, `review1.md`,
  `review2.md` beside it) and `local_claude_1/reconstructions/` (README.md with the ranked ideas and
  the "which other players are restorable" table; four `ALGORITHM.md`; `sources/` with the write-ups
  verbatim and the game author's statistics; `profiles/profile_bot.py`; `fits/reconstruct.py` — exact
  per-turn states; `prior-art.md`; `REVIEW-2026-08-28.md`).
- Ritual unchanged: `cd /home/tarstars/prj/troll_farm-local_claude_1 && python3 scripts/inbox_sweep.py
  --me local_claude_1 --fetch` → read every new message whole → `--mark` as its own step → commit the
  seen state. Every shell command carries its own `cd`; `git pull` for the checkout must run in a
  separate call (the harness resets the cwd to the checkout).
- **Nothing is waiting on the owner** except design round 1 of the third troll and, later, the prediction.

## The day, in order (2026-08-27 15:40Z → 2026-08-28 04:40Z)

1. **The apple farm's rounds.** Round 2 (`41203992`) read 19.8/50 at 16:41Z (the 16:06Z timer fired
   late); round 3 (`41204464`) 18.6/78 at 17:46Z (56 % wins against the weakest opponents — a batch
   anchored low); round 4 (`41204747`) 19.9/47 at 18:53Z (66 % wins). The rule ran in every farm-map
   game (62/50/57/64 % wins there); the identical-play games 43/53/56/68 %. Owner 18:51Z: the rest
   later.
2. **The second-troll census** (owner 17:1xZ: "more powerful second troll?"): every strong bot buys the
   same `2/2/0/2` troll, later and never weaker; ours was weaker in 37–45 % of games and lost those
   twice as often within a batch (`local_claude_1/second-troll-census/`, board row T-4).
3. **The floor** (owner 17:5xZ "let's build the_floor"): five replacements (+17/−23) — the second troll
   never weaker than 2/2/0/2; the turn-35 deadline takes the strongest floored troll or keeps waiting.
   Built (`local_claude_1/the-floor/make_the_floor.py`), bed PASS, smoke PASS 24/24 (the resident was
   below the floor on 11/24; +149), codex_1 REPRODUCED (row 0-6; after one machine-dependent report
   field was removed from the generator's output). Owner 18:51Z: "submit now floor, put 5 resubmissions"
   → round 1 `41205061` 18:54:02Z.
4. **The seven-hour stall.** The session made no progress between 19:50Z and 02:58Z (the owner's night
   messages arrived in that window). Round 1's reading was taken at 03:06Z (19.2, from the rating stamp);
   round 2 (`41206278`, 03:14:28Z) read 19.1 at 04:17Z — 76–84, 5/37 against 4+-troll bots; round 3
   submitted 04:21:54Z. The mechanism worked in every game (156/156 floored second trolls; two games in
   160 never trained in 300 turns — the unconditional wait's cost).
5. **Track R** (owner 19:5xZ: "recover algorithms of 4 top players … enough for writing a program; all
   means are good"; the hook goal set): eight workers between 03:00Z and 03:45Z — W1 internet
   (delineate's own gist, the game author's statistics for 69 Legend players, the contest thread with 12
   write-ups; nothing by norxondor, Bubaptik, MSz), W2 prior art (norxondor's ladder recovered in July,
   the 21 imitation closures, the tools), W3 profiles from the raw replays' referee log (exact positions
   and tree origins), W4 fits on exact states (0 disagreements on 784 games), four writers; three
   reviewers (R1 the documents, R2 and R3 the PDF). Findings: the top splits into two-troll choppers
   (our family) and 3–4-troll build-up economies; all four train within a turn of affordability, plant
   29–40 trees on the cell minimising d(shack)+d(troll), take wood from their own trees late; norxondor
   is a fast rule-based produce→deforest bot; no chop-target formula fits.
6. **The PDF** (owner ~03:45Z): written, reviewed twice (37 + 27 corrections), overflow checked,
   published 04:05Z at `/home/tarstars/prj/troll_farm/docs/reports/2026-08-28-top-four-algorithms.pdf`.
7. **The owner's questions** (04:2xZ–04:4xZ): which other players are restorable (a ranked table in
   README.md: Escdemon, aangairbender, Konstant, xSkyline, putibuzu, 0x6E0FF high; wala, laconic_pixel …
   medium; yaichi/skotz from games; delineate not as rules); Escdemon is the highest of the "high" group
   on the ladder (#14), wala the strongest described bot (#5); the shortest path to points = the third
   troll → the new goal.

## Ledger (`local_claude_1/ladder-measure/ledger-2026-08-26.md`)

| row | bot | submitted | id | agent | read | score | rank |
|---|---|---|---|---|---|---|---|
| ABL | the champion (simplified) | 08-27 08:21:51Z | 41202036 | 6667789 | 09:25Z | **21.2** | 42 |
| APL-1h, r2, r3, r4 | the apple farm | 13:34Z, 15:04Z, 16:44Z, 17:49Z | 41203549, 41203992, 41204464, 41204747 | | 14:36Z, 16:41Z, 17:46Z, 18:53Z | **19.8, 19.8, 18.6, 19.9** | 49, 50, 78, 47 |
| FLR-r1, r2 | the floor | 18:54:02Z, 03:14:28Z | 41205061, 41206278 | 6668560, 6669701 | 03:06Z, 04:17Z | **19.2, 19.1** | (62 at 45 min), unreadable |
| FLR-r3 | the floor, last round | 04:21:54Z | 41206409 | (at the reading) | due ≥ 05:22Z | — | — |

## Operational notes (new since the last handover)

- **Session crons die with the session and can fire late** (one fired 34 min late; the 19:56Z one never
  got its turn during the stall). After a flush: `CronList`, then re-create the pending one-shot from the
  ledger's last submission time.
- **The outbox lint** refuses a message whose `ack_for` names another task unless the body carries a
  `cross-task:` line; and the pre-push lint refuses a push while an uncommitted message in the outbox
  pins an unpushed commit — set the message aside, push the artifact commit, restore, commit, push.
- **Stale pins** (a peer's rebase rewriting a pinned commit) block every `--mark`: quarantine by
  adjudication (`coordination/quarantine.json` + a policy message); this was the fifth occurrence.
- **A generated report must not carry machine-dependent fields** (the rustfmt check broke codex_1's
  byte-identity reproduction once).
- `local_claude_1/the-floor/ladder_read.py` reads any bot's package (talents and turn of every TRAIN,
  the floor split, wins by opponent troll count); it takes the package's `.jsonl.gz` FILE.
- The raw replays (`data/raw/games/<id>.json`, main checkout, 16 GB) carry the referee's per-turn log;
  `local_claude_1/reconstructions/profiles/profile_bot.py` and `fits/reconstruct.py` parse them exactly.
- `local_claude_1/reconstructions/fits/tables/` (22 MB, gzipped) was committed — above the 10 MB slice
  rule for peers; move out of the tree if the owner objects.
