# GOAL — the farm's viewing is done; run the owner's one-variable experiment when they say yes; return the champion

Owner rulings 2026-08-27: ~06:00Z *"the farm now to diagnose … one hour round is enough"* —
delivered (reading 10.8 at rank 172/176, 160 games collected and decoded, ledger row FARM-1h).
07:10Z *"denial logic matters … chop plum or lemon first, banana farm next … of course (a)"* —
designed and discussed, then **parked** by the owner's 08:05Z ruling: *"we conducted a dirty
experiment … take our champion with the simplest code and highest rating and turn this plum-lemon
denial logic at the beginning of the game off. I predict one hour exposition to arena will show
drastical rating drop."* The design for that experiment is with the owner; **build nothing until
they say yes.**

You are `local_claude_1`, sole Arena controller. Rules: `coordination/WORKING-RULES.md`; record:
`coordination/BOARD.md`; ledger: `local_claude_1/ladder-measure/ledger-2026-08-26.md`; the night's
handover: `coordination/HANDOVER-2026-08-27-board-era-ladder-and-farm.md`.

## Each wake (hourly cron; also on ack-required mail)

1. `cd /home/tarstars/prj/troll_farm-local_claude_1 && python3 scripts/inbox_sweep.py --me local_claude_1 --fetch`;
   read every new message whole **before publishing anything**; `--mark` as its own step.
2. **Ladder.** The farm (`41201668`, agent `6667061`) stays up only until the next submission; its
   games are already collected (`local_claude_1/farm-watch/games-41201668/`). **Do not resubmit
   the farm.**
   - **The owner said yes (08:20Z) and the ablation is UP: submission `41202036`, 08:21:51Z**
     (`cgauto/submissions/candidate-champion-denial-off-v6-instrument.rs`, sha `0e92f8fa…`;
     built by `local_claude_1/denial-ablation/make_denial_off.py`, bed `fixtures_diff.py`,
     diff `readable/diffs/denial-bonus-off.diff`). **READ 09:25Z: 21.2 at rank 42/176 — no drop; its 160 games are collected**
     (`local_claude_1/denial-ablation/games-41202036/`). The reading step, as it was written, was:
     `python3 cgauto/cg_rank.py` → ledger row (score, rank, agent id, time) → **collect its
     games first** (`python3 local_claude_1/narrate/collect_submission_games.py --agent-id
     <agent> --submission-id 41202036 --scratch <scratchpad>/abl-41202036 --output-dir
     local_claude_1/denial-ablation/games-41202036 --observed-at-utc <date -u>`) → report the
     number to the owner in plain words against their prediction ("a sharp drop"; noise ≈ 1.5 a
     reading; the champion's own readings were 21.8 / 21.6 / 22.1).
   - **OWNER RULING 09:05Z — the ablation IS the champion now:** *"One point is not enough to make
     a decisive conclusion. But I like simplification of the algorithm, so let's name the current
     approach the champion."* The bot on the ladder (`41202036`, sha `0e92f8fa…`, the champion
     minus its four-line plum/lemon denial bonus) **stays up as the champion of record. Do NOT
     resubmit the old champion; the 12:00Z return clause is void.** The reading is still taken and
     reported against the prediction; if it shows a real drop, that goes to the owner as a fact,
     not as a revert.
3. Rule on anything that blocks a peer; land artifacts on `main` at each gate; mark stalls.
4. Board note (Moved / Stalled / Ladder / Decisions / Corrections) appended to
   `local_claude_1/goal-log-2026-08-26.md`, board rows updated in the same commit; fast-forward
   `main`; pull the checkout `/home/tarstars/prj/troll_farm`.

## Allowed without the owner
The hourly reading; collecting a resident's games; returning the champion as described; rulings
that unblock a peer; stalls; landing artifacts; slices ≤ 10 MB on request. **With the owner's
yes:** the ablation build and its one submission.

## Not allowed
Any other submission (no farm resubmission, no farm repair build, no keep-rule readings);
promotion or revert rulings; new charters beyond the ablation; rule changes; transfers > 10 MB;
deletions.

## Done when
The ablation's one-hour reading is in the ledger and reported to the owner against their
prediction (or the owner said no and the champion simply returned); the champion is back as the
resident; the board is truthful and `origin/main` == `agent/local_claude_1` == the checkout.
**Time box: 2026-08-27T18:00Z.**

## Waiting on the owner (do not act on these)
The farm — repair denial-first (designed) or close the line, after the ablation's reading; the
keep rule — two more readings or leave it; the analytics — a balanced keep-rule slice plus three
telemetry fields, or leave it.
