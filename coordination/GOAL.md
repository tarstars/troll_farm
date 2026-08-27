# GOAL — steady state: keep the champion read, the board truthful, the mail clean; nothing new without the owner's word

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
`coordination/BOARD.md`; ledger: `local_claude_1/ladder-measure/ledger-2026-08-26.md`; the night's
handover: `coordination/HANDOVER-2026-08-27-board-era-ladder-and-farm.md`; today's log:
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
