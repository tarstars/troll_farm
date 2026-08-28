# GOAL — steady state: keep the champion read, the board truthful, the mail clean; nothing new without the owner's word

**THE NIGHT'S GOAL (owner 19:5xZ, asleep ~9 h until ≈ 05:00Z): recover the algorithms of the four top
players** — delineate, norxondor_gorgonax, Bubaptik, MSz — each as a description of actions sufficient
to write a program; all means allowed (internet, our corpus, replays). Plan and deliverables:
`local_claude_1/reconstructions/PLAN.md`; board Track R. The floor's six rounds run on their timers
in parallel and are not interrupted by this work.

**THIS HOUR (from 2026-08-27 18:54:02Z): THE FLOOR is on the ladder** — submission **`41205061`**
(sha `31cd23c0…`, `cgauto/submissions/candidate-the-floor-v6-instrument.rs`, 63,791 B; card
`coordination/tasks/20260827-the-floor.md`; ladder queue slot 4), the owner's one-variable experiment
("let's build the_floor", 17:5xZ; "submit now floor, put 5 resubmissions", 18:51Z): the champion of
record with one change — the second troll is never weaker than speed 2, carry 2, chop 2; the bot waits
for it, and from turn 35 takes the strongest floored troll it can afford or keeps waiting for the basic
2/2/0/2. Built by `local_claude_1/the-floor/make_the_floor.py` (+17/−23, diff `readable/diffs/the-floor.diff`);
bed PASS; smoke PASS 24/24 real maps; codex_1 reproduces (row 0-6, verdict pending).

**THE FLOOR'S SIX ROUNDS (owner 18:51Z).** The same file is submitted six times in all, one hour
each; ledger rows `FLR-r1` … `FLR-r6` in `local_claude_1/ladder-measure/ledger-2026-08-26.md`.
**Round 1 = `41205061`, submitted 18:54:02Z, reading ≥ 19:54Z (timer 19:56Z).** Each round, ≥ 60 min
after its submission (a one-shot session cron at +62 min; local clock = UTC+3): (1) `python3
cgauto/cg_rank.py` — the reading; ledger row (score, rank, agent id, time); (2) collect its games —
`local_claude_1/narrate/collect_submission_games.py --agent-id <id> --submission-id <id> --scratch
<scratchpad>/… --output-dir local_claude_1/the-floor/games-<id> --observed-at-utc $(date -u …)` —
check all 160 are done, and read them with `python3 local_claude_1/the-floor/ladder_read.py
<package .jsonl.gz FILE> <agent id> <label>` (the second troll's talents and training turn per game —
never below 2/2/0/2 —, wins, opponents' troll counts and ratings; compare with the champion's batch
`local_claude_1/denial-ablation/games-41202036/` and the apple farm's rounds); (3) if fewer than six
readings exist, submit the next round with `python3 cgauto/api_submit_once.py
cgauto/submissions/candidate-the-floor-v6-instrument.rs --expected-sha256
31cd23c021f184b0cc39aa7f38d4bfb099d56a9f815ce892bee1f3dada10d420` and create the one-shot cron for its
reading at +62 min; (4) board (slot 4), the card's log, the five-part log note, commit, push,
fast-forward `main`, pull the checkout; report the reading against the champion's 21.2/42 and the
owner's prediction (not yet stated; coordinator's on record: about +1). **After the sixth reading: no
further submission — the six numbers (mean, spread) go to the owner, who rules.** The hourly wake in
between reads the current submission and does nothing else. The champion of record remains `41202036`.

**THE APPLE FARM is PAUSED after four readings (owner 18:51Z: "what left for previous experiments
let's do later"):** 19.8/49, 19.8/50, 18.6/78, 19.9/47 — mean 19.5, spread 1.3 — against the champion's
21.2/42 (rows `APL-1h`, `APL-r2` … `APL-r4`; all four packages collected and read in
`local_claude_1/apple-farm/games-*/`; the rule ran in every farm-map game, 62/50/57/64 % wins there;
identical-play games 43/53/56/68 %). Rounds 5–6 wait for the owner's word; nothing is submitted for
them by this file.

**The champion of record is the simplified bot** (owner ruling 2026-08-27 09:05Z: *"One point is not
enough to make a decisive conclusion. But I like simplification of the algorithm, so let's name the
current approach the champion."*): submission **`41202036`** (08:21:51Z), agent `6667789`, file
`cgauto/submissions/candidate-champion-denial-off-v6-instrument.rs`, sha `0e92f8fa…` — the previous
champion minus its four-line plum/lemon denial bonus; readable source `readable/denial-off-champion.rs`;
`docs/STATE.md` §1. One-hour reading 21.2 at rank 42/176 (no drop); its 160 games in
`local_claude_1/denial-ablation/games-41202036/`. **It is off the ladder while the experiments run and
returns only on the owner's word.**

**Owner rulings 2026-08-27 10:04Z:** the banana farm line is **closed** (obituary in
`coordination/GRAVEYARD.md`; the denial-first repair design is on file in its card); the inert code
in the champion **stays** ("probably convenient for the nearest experiments"); the keep-your-goal
question is **on hold** ("a little bit different angle soon") — L-1 and T-3 on hold, no readings, no
analytics slice. When the next experiment comes it will be one variable on the current champion, built
through the generator-and-compactor chain (`local_claude_1/the-floor/make_the_floor.py` is the template
for replacements, `local_claude_1/apple-farm/make_apple_farm.py` for insertions), one hour on the
ladder, one reading against the owner's stated prediction, games collected before the next submission.

You are `local_claude_1`, sole Arena controller. Rules: `coordination/WORKING-RULES.md`; record:
`coordination/BOARD.md`; ledger: `local_claude_1/ladder-measure/ledger-2026-08-26.md`; the latest
handover: `coordination/HANDOVER-2026-08-27-apple-farm-five-rounds.md` (the floor and the census came
after it: see the board, the cards and today's log); today's log: `local_claude_1/goal-log-2026-08-26.md`.

## Each wake (hourly cron; also on ack-required mail)

1. `cd /home/tarstars/prj/troll_farm-local_claude_1 && python3 scripts/inbox_sweep.py --me local_claude_1 --fetch`;
   read every new message whole **before publishing anything**; `--mark` as its own step; commit the
   seen state.
2. **Ladder.** Read the current submission once with `python3 cgauto/cg_rank.py`; write the ledger
   row (score, rank, agent id, time) if it is a reading (≥ 60 min), else one log line. No submission
   outside the round protocol above.
3. Rule on anything that blocks a peer; land artifacts on `main` at each gate; mark stalls.
4. Board note (Moved / Stalled / Ladder / Decisions / Corrections) appended to
   `local_claude_1/goal-log-2026-08-26.md`, board rows updated in the same commit; fast-forward
   `main`; pull the checkout `/home/tarstars/prj/troll_farm`.

## Allowed without the owner
The round protocol above (readings, collections, the next round's submission of the same file); the
hourly reading; rulings that unblock a peer; stalls; landing artifacts; slices ≤ 10 MB on request;
transport repairs (quarantine adjudications).

## Not allowed
Any other submission; any build; promotion or revert rulings; new charters; rule changes; transfers
> 10 MB; deletions.

## Done when
There is no "done" — this is the resting state until the owner names the next experiment. Each wake
ends with the board truthful and `origin/main` == `agent/local_claude_1` == the checkout.
