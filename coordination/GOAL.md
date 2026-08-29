# GOAL — the third troll (owner 2026-08-28 04:3xZ: "set as next goal bot with the third troll"); since 2026-08-29 13:3xZ also TRACK N — the neural-network bot, Way B (owner: "1) open line 2) B 3) I'll check"); nothing else without the owner's word

**TRACK N — THE NEURAL-NETWORK BOT, WAY B** (card `coordination/tasks/20260829-nn-bot-way-b.md`;
analysis `local_claude_1/nn-bot/ANALYSIS-2026-08-29.md`): clone the top four's moves from the exact
replay reconstruction as the starting policy, then PPO from that start with the clone as anchor, on
real maps; five phases with done/dead/budget on the card.

**THE TARGET (owner 2026-08-29 14:4xZ: "let's set a target so I don't need to wake you up with my
messages")** — the coordinator works toward it unprompted; the owner reads the board when they like.
*A neural-network candidate that beats the champion of record and orchard 6 on the local bench — at
least 60 % wins over 400 games against each, a positive mean margin, three gates in a row — exported
as one Rust file under 100,000 characters at ≤ 15 ms a turn on this host, its bed passed (the Python
network and the Rust kernel agree move for move) and codex_1's reproduction in hand: ready for the
ladder.* **Milestone on the way, for the owner's read:** the clone playing 24/24 real maps against the
champion's file, its games saved (aimed at 2026-09-14). **Budget:** the target by 2026-10-17 (seven
weeks); if the clone milestone is a week late (2026-09-21), Way A's from-scratch curriculum starts as
the card's fallback; if the target date passes with no candidate through Phase 3's gate, the
programme stops and reports. **The one message the owner will get:** "the candidate is ready — your
prediction, and the platform's hour" (the ladder is codex's until the owner says otherwise).

**Standing authorizations under the target (no wake needed):** build, charter, review and reproduce on
the VM; train on this host at `nice 10` with at most 14 threads so the owner's machine stays usable;
downloads under 50 MB without asking — bigger ones wait for the owner's next visit and the work routes
around them; stalls are decided by the cards' dead conditions and fallbacks; a two-day stall with no
fallback becomes a note in the owner's queue, not a message. **Never without the owner's word:** any
platform action (no submission, no collection, no leaderboard look), deleting or moving data, cloud
spend, a submission outside Phase 4's protocol (bed, reproduction, the owner's prediction, one hour,
one reading). **Reporting:** one plain-words status line per milestone in the board's owner's queue.
**Wake:** the coordinator's session self-paces (the `/loop` mechanism, fallback every 20–60 minutes)
and is woken by mail and by finished background jobs; a new session re-creates the loop from this file.

**THE NEXT EXPERIMENT — THE THIRD TROLL** (card `coordination/tasks/20260828-third-troll.md`): the
champion of record (`41202036`, sha `0e92f8fa…`, readable `readable/denial-off-champion.rs`) plus one
change — after the second troll is trained, both trolls collect the bill of a third troll (speed 2,
carry 3, harvest 0, chop 3: 6 plums, 11 lemons, 2 apples, 11 iron with two trolls) — the starting troll
harvests the plums and lemons, the trained troll mines the iron — and the bot trains it the turn the bill
is affordable; the third troll chops like the second. Nothing else changes. Evidence:
`docs/reports/2026-08-28-top-four-algorithms.pdf` §11 and `local_claude_1/reconstructions/README.md`
(idea #1); `local_claude_1/reconstructions/prior-art.md` (the funding coalition +106 on the bench; a
training plan alone −170). **Steps:** (1) design round 1 = the four questions on the card with the
coordinator's recommended answers, presented to the owner in one message; build unless the owner
objects; (2) the build through the generator chain (`local_claude_1/third-troll/make_third_troll.py`;
templates `local_claude_1/the-floor/make_the_floor.py` for replacements, `local_claude_1/apple-farm/
make_apple_farm.py` for insertions), the bed (`fixtures_diff.py` adapted), a smoke on real maps
(`smoke.py` adapted: share and turn of the third troll, funding time, no stall), codex_1's reproduction
(a handoff pinned to a pushed commit, the ≤ 10 MB slice); (3) the owner's prediction asked; the
submission (`python3 cgauto/api_submit_once.py <file> --expected-sha256 <sha>`), a one-shot session cron
at +62 min (local = UTC+3), the one-hour reading, the 160 games collected (`local_claude_1/narrate/
collect_submission_games.py --agent-id <id> --submission-id <id> …`) and read (`local_claude_1/the-floor/
ladder_read.py` works for any bot: talents and turn of every TRAIN, wins by opponent troll count).

**THE LADDER MEANWHILE:** the floor's round 3 (`41206409`, submitted 04:21:54Z) is its **last** round:
its reading at 05:24Z (timer `68fe25fd`; if `cg_rank.py` fails at login — it does most of the night —,
the rating is the API's `score` stamped on our agent in the collected games; the rank "unreadable"),
its games collected into `local_claude_1/the-floor/games-41206409/` and read; **no round 4** — the
owner's new goal supersedes the six rounds; the three readings (19.2, 19.1, round 3) go to the owner.
The floor stays on the ladder, unread, until the third-troll bot takes the slot; the champion of record
returns only on the owner's word. Ledger rows `FLR-r1` … `FLR-r3` in
`local_claude_1/ladder-measure/ledger-2026-08-26.md`.

**THE APPLE FARM** is paused after four readings (19.8, 19.8, 18.6, 19.9 — mean 19.5; the champion
21.2); rounds 5–6 only on the owner's word. **The floor** read 19.2, 19.1 (round 3 pending) — the
mechanism worked in every game (every second troll `2/2/0/2` or better); the losses sit with 3+-troll
opponents. Both are facts, not verdicts; the owner rules.

**Track R (the four top players' algorithms) is DONE and published:** the PDF
`docs/reports/2026-08-28-top-four-algorithms.pdf` (8 pages, reviewed twice), `local_claude_1/reconstructions/`
(README.md, four `ALGORITHM.md`, `sources/`, `profiles/`, `fits/`, `prior-art.md`, `REVIEW-2026-08-28.md`).

**The champion of record is the simplified bot** (owner ruling 2026-08-27 09:05Z): submission
`41202036` (08:21:51Z), agent `6667789`, `cgauto/submissions/candidate-champion-denial-off-v6-instrument.rs`,
sha `0e92f8fa…`; readable `readable/denial-off-champion.rs`; one-hour reading 21.2 at rank 42/176; its
160 games in `local_claude_1/denial-ablation/games-41202036/`. **Restore target for any revert.**

**Owner rulings 2026-08-27 10:04Z** still stand: the banana farm line closed; the inert code in the
champion stays; the keep-your-goal question on hold.

You are `local_claude_1`, sole Arena controller. Rules: `coordination/WORKING-RULES.md`; record:
`coordination/BOARD.md`; ledger: `local_claude_1/ladder-measure/ledger-2026-08-26.md`; the latest
handover: `coordination/HANDOVER-2026-08-28-third-troll.md`; today's log: `local_claude_1/goal-log-2026-08-26.md`.

## Each wake (hourly cron at :37; also on ack-required mail)

1. `cd /home/tarstars/prj/troll_farm-local_claude_1 && python3 scripts/inbox_sweep.py --me local_claude_1 --fetch`;
   read every new message whole **before publishing anything**; `--mark` as its own step; commit the
   seen state. (A message whose pinned commit is unreachable blocks every `--mark`: quarantine it by
   adjudication — `coordination/quarantine.json` entry + a policy message — as entries 12–17 were.)
2. **Ladder.** Read the current submission once (`python3 cgauto/cg_rank.py`; the fallback above);
   write the ledger row if it is a reading (≥ 60 min), else one log line. No submission outside the
   card's protocol.
3. Rule on anything that blocks a peer; land artifacts on `main` at each gate; mark stalls.
4. Board note (Moved / Stalled / Ladder / Decisions / Corrections) appended to
   `local_claude_1/goal-log-2026-08-26.md`, board rows updated in the same commit; push; fast-forward
   `main` (`git push origin agent/local_claude_1:main`); pull the checkout `/home/tarstars/prj/troll_farm`
   in a separate call (the cwd resets there).

## Allowed without the owner
The card's protocol (the build, the bed, the smoke, codex_1's charter, the submission and its reading
once the owner has given the prediction or said "go"); the floor's last reading and collection; the
hourly reading; rulings that unblock a peer; stalls; landing artifacts; slices ≤ 10 MB on request;
transport repairs (quarantine adjudications).

## Not allowed
Any other submission (including the champion's return); promotion or revert rulings; new charters;
rule changes; transfers > 10 MB; deletions.

## Done when
The third troll's one-hour reading is on the ledger with its games collected and read, and the owner
has ruled. Each wake ends with the board truthful and `origin/main` == `agent/local_claude_1` == the checkout.
