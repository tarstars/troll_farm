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
   - **After the owner's yes:** build the ablation instrument — the diagnostics champion
     (`claude_1/cure3/cure3-keep-v6.rs`, flags KEEP=false NARRATE=true, i.e. bot A) with the
     `score += 900.0 / (1 + opponent_distance)` bonus in `chop_candidates` removed — under
     `local_claude_1/denial-ablation/` by the same generator-and-compactor chain as
     `claude_1/ladder-measure-b/make_candidate3_v6.py` (compile, round trip, sha recorded, the
     file must differ from bot A); readable diff `readable/diffs/denial-bonus-off.diff`; submit
     with `cgauto/api_submit_once.py <file> --expected-sha256 <sha>`; read it after **one hour**
     with `python3 cgauto/cg_rank.py`; write the ledger row; collect its games before the next
     submission; report the reading to the owner in plain words against their prediction.
   - Then **return the champion** (`cgauto/submissions/candidate-champion-v6-instrument.rs`, sha
     `72673124…`) as the resident — also by **2026-08-27T12:00Z** if no yes has come by then.
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
