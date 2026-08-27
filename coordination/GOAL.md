# GOAL — watch the banana farm on the ladder (one-hour rounds), then return the champion; owner decisions pending

Owner rulings 2026-08-27 ~06:00Z: *"the farm now to diagnose — we collect new information from the
ladder and diagnose using telemetry"*, *"one hour round is enough"*, and (on the keep-your-goal
rule) *"bring [the verdict], then we'll see"* — delivered: **under-determined**.

You are `local_claude_1`, sole Arena controller. Rules: `coordination/WORKING-RULES.md`; record:
`coordination/BOARD.md`; ledger: `local_claude_1/ladder-measure/ledger-2026-08-26.md`; the night's
handover: `coordination/HANDOVER-2026-08-27-board-era-ladder-and-farm.md`.

## Each wake (hourly cron; also on ack-required mail)

1. `cd /home/tarstars/prj/troll_farm-local_claude_1 && python3 scripts/inbox_sweep.py --me local_claude_1 --fetch`;
   read every new message whole **before publishing anything**; `--mark` as its own step.
2. **Ladder:** the farm (`41201668`, 06:35Z) is the resident **for viewing, not measurement**. Read
   it with `python3 cgauto/cg_rank.py` once an hour, write the row (score, rank, agent id, time),
   and note anything its annotated games show. **Do not resubmit the farm** without an owner ruling;
   after the owner's word — or by 2026-08-27T12:00Z if none comes — **return the champion**
   (`cgauto/submissions/candidate-champion-v6-instrument.rs`, sha `72673124…`) as the resident.
3. Rule on anything that blocks a peer; land artifacts on `main` at each gate; mark stalls.
4. Board note (Moved / Stalled / Ladder / Decisions / Corrections) appended to
   `local_claude_1/goal-log-2026-08-26.md`, board rows updated in the same commit; fast-forward
   `main`; pull the checkout `/home/tarstars/prj/troll_farm`.

## Allowed without the owner
The hourly farm reading; returning the champion as described; rulings that unblock a peer; stalls;
landing artifacts; slices ≤ 10 MB on request.

## Not allowed
Any other submission (no new candidate, no keep-rule readings, no farm repair); promotion or
revert rulings; new charters; rule changes; transfers > 10 MB; deletions.

## Done when
The farm's viewing is closed with its readings in the ledger and one plain-words note on what its
annotated games showed; the champion is back as the resident; the board is truthful and
`origin/main` == `agent/local_claude_1` == the checkout. **Time box: 2026-08-27T18:00Z.**

## Waiting on the owner (do not act on these)
The farm — bounded repair or close the line; the keep rule — two more readings or leave it; the
analytics — a balanced keep-rule slice plus three telemetry fields, or leave it.
