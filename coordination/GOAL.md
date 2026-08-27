# GOAL — steady state: keep the champion read, the board truthful, the mail clean; nothing new without the owner's word

**THIS HOUR (from 2026-08-27 13:34:48Z; round 3 `41204464` up since 16:44:19Z): the apple farm is on the ladder** — round 1 was submission **`41203549`**
(sha `8c6bc206…`, `cgauto/submissions/candidate-apple-farm-v6-instrument.rs`; card
`coordination/tasks/20260827-apple-farm-instrument.md`; ladder queue slot 3), the owner's one-variable
experiment ("let's do it", design approved "1 c / 2 yes"): the champion of record plus one rule —
the starting troll plants an apple on a water-side cell touching the shack on turns 1–3 and, once the
second troll is trained, harvests it to the end. **The one-hour reading was taken at 14:36Z: 19.8 at
rank 49 of 176 — 1.4 below the champion's 21.2/42** (ledger row `APL-1h`; its 160 games collected in
`local_claude_1/apple-farm/games-41203549/` and read: the rule ran in all 53 farm-map games and won
62 % of them; the 107 identical-play games went 43 % — a harder draw).

**THE FIVE ROUNDS (owner 15:0xZ: "let's just resubmit apple farm 5 times and see where it lands").**
The same file (`cgauto/submissions/candidate-apple-farm-v6-instrument.rs`, sha
`8c6bc206417c6d22b593372ce42e74ce5698646c1f8a860073f349a2a082708c`) is submitted five more times,
one hour each; six readings in all with round 1's 19.8/49. **Readings so far: round 1 19.8/49
(`41203549`), round 2 19.8/50 (`41203992`), round 3 18.6/78 (`41204464`, read 17:46Z); round 4 =
`41204747`, submitted 17:49:29Z, reading 18:51Z.** The reader `ladder_read.py` takes the package's `.jsonl.gz` file, not the directory. Each round, ≥ 60 min after its submission (a one-shot session cron at +62 min):
(1) `python3 cgauto/cg_rank.py` — the reading; ledger row `APL-r<n>` (score, rank, agent id, time);
(2) collect its games — `local_claude_1/narrate/collect_submission_games.py --agent-id <id>
--submission-id <id> --scratch <scratchpad>/… --output-dir local_claude_1/apple-farm/games-<id>
--observed-at-utc $(date -u …)` — and read them with `local_claude_1/apple-farm/ladder_read.py`
(farm maps vs the rest; the rule ran; wins; opponent trolls); (3) if fewer than six readings exist,
submit the next round with `python3 cgauto/api_submit_once.py <file> --expected-sha256 <sha>` and
create the one-shot cron for its reading at +62 min (local clock = UTC+3); (4) board (slot 3), the
card's log, the five-part log note, commit, fast-forward `main`, pull the checkout; report the
reading against the champion's 21.2/42 and the earlier rounds. **After the sixth reading: no further
submission — the six numbers (mean, spread) go to the owner, who rules.** The hourly wake in between
reads the current submission and does nothing else. The champion of record remains `41202036`.

**The champion of record is the simplified bot** (owner ruling 2026-08-27 09:05Z: *"One point is not
enough to make a decisive conclusion. But I like simplification of the algorithm, so let's name the
current approach the champion."*): submission **`41202036`** (08:21:51Z), agent `6667789`, file
`cgauto/submissions/candidate-champion-denial-off-v6-instrument.rs`, sha `0e92f8fa…` — the previous
champion minus its four-line plum/lemon denial bonus; readable source `readable/denial-off-champion.rs`;
`docs/STATE.md` §1. One-hour reading 21.2 at rank 42/176 (no drop); its 160 games in
`local_claude_1/denial-ablation/games-41202036/`. **It stays up. Do not resubmit anything.**

**Owner rulings 2026-08-27 10:04Z:** the banana farm line is **closed** (obituary in
`coordination/GRAVEYARD.md`; the denial-first repair design is on file in its card); the inert code
in the champion **stays** ("probably convenient for the nearest experiments"); the keep-your-goal
question is **on hold** ("a little bit different angle soon") — L-1 and T-3 on hold, no readings, no
analytics slice. **Nothing is waiting on the owner; the next experiment is theirs to name.** When it
comes it will be one variable on the current champion, built through the generator-and-compactor
chain (`local_claude_1/denial-ablation/make_denial_off.py` is the template), one hour on the ladder,
one reading against the owner's stated prediction, games collected before the next submission.

You are `local_claude_1`, sole Arena controller. Rules: `coordination/WORKING-RULES.md`; record:
`coordination/BOARD.md`; ledger: `local_claude_1/ladder-measure/ledger-2026-08-26.md`; the latest
handover: `coordination/HANDOVER-2026-08-27-apple-farm-five-rounds.md`; today's log:
`local_claude_1/goal-log-2026-08-26.md`.

## Each wake (hourly cron; also on ack-required mail)

1. `cd /home/tarstars/prj/troll_farm-local_claude_1 && python3 scripts/inbox_sweep.py --me local_claude_1 --fetch`;
   read every new message whole **before publishing anything**; `--mark` as its own step; commit the
   seen state.
2. **Ladder.** Read the champion (`41202036`) once with `python3 cgauto/cg_rank.py`; write the ledger
   row (score, rank, agent id, time). No submission of any kind.
3. Rule on anything that blocks a peer; land artifacts on `main` at each gate; mark stalls.
4. Board note (Moved / Stalled / Ladder / Decisions / Corrections) appended to
   `local_claude_1/goal-log-2026-08-26.md`, board rows updated in the same commit; fast-forward
   `main`; pull the checkout `/home/tarstars/prj/troll_farm`.

## Allowed without the owner
The hourly reading; collecting a resident's games; rulings that unblock a peer; stalls; landing
artifacts; slices ≤ 10 MB on request; transport repairs (quarantine adjudications).

## Not allowed
Any submission; any build; promotion or revert rulings; new charters; rule changes; transfers
> 10 MB; deletions.

## Done when
There is no "done" — this is the resting state until the owner names the next experiment. Each wake
ends with the board truthful and `origin/main` == `agent/local_claude_1` == the checkout.
