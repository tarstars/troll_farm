# Handover — 2026-09-02 13:2xZ — the port measured and diagnosed, the one repair in flight

Written at the owner's request ("prepare to context flush"). Everything below is on `main`.
Read `coordination/GOAL.md` (rewritten this morning), then `coordination/BOARD.md`, then the tail
of `coordination/tasks/20260902-norxondor-port.md` (the chronological log), then this.

## The day in one paragraph

The owner's decision at ~07:5xZ set the fast path: **port the second-placed player's bot**
(norxondor_gorgonax, rated 29.7, rule-based, reconstructed on 08-28 and never written as a
program), with the neural-network line continuing in the background, and **the ladder returned to
the coordinator**. In one day the port was designed, built, reproduced and measured twice — and it
loses, clearly, on both populations. Its loss is now diagnosed to a single mechanism and one
repair is being gated. Track E (the endgame gap) was read and closed the same day. Track N's four
arms are all running.

## Track P — the port (the live work)

**The chain:** design read (codex_1, 09:09Z) → one review round, four edits, none disputed
(claude_1's two: the completion ETA counted one item a trip and would have switched every game to
clear-cutting right after the third troll; "carry anything → bank" made a carry-3 troll bank after
one fruit. Mine: the switch deadline by roster 129/144/154 instead of a single turn-185 deadline;
the late conversion job may take any seed kind, cheapest to fell) → **v2 built 10:11Z**
(`cgauto/submissions/candidate-norxondor-port-v2.rs`, sha `411b0565…`, 82,518 UTF-16 units, all
gates passed) → reproduced byte for byte by claude_1 → **rung 1: `FIELD_BELOW_ZERO`**, Δwin
**−0.421 [−0.453, −0.389]** over 1,600 games, below all four local opponents → **rung 2 (mine, the
calibration check): 15 paired games against the five real Legend agents, champion 8 wins, port 0**,
Δwin −0.533, Δscore −53.7 (172 vs 118), wood 42 vs 26. No inversion; both rungs agree.

**The loss read** (`codex_1/norxondor-port/LOSS-READ-2026-09-02.md`, pinned `084a35c6…`, its
analyzer and tests beside it; 112,919 recorded pre-turn scores replayed, all exact, before any
decomposition was accepted). Verdict `SWITCH_LATE/MEASURED`:

- turns 1–50: the port banks **9.45 fruit, 0.07 wood**; the champion **0.70 fruit, 8.71 wood**.
  A fruit is one point, a wood is four → 30 points down before anything else, 55 by turn 100,
  64 by turn 150.
- the third troll arrives at **median turn 74** and then sits in Produce until the roster-three
  deadline at **turn 144**; chop rate 12.7 % of troll-turns against the champion's 30.0 %.
- after the switch the machinery is fine: 8.90 wood items to the champion's 6.92 in turns 151–200,
  clawing back 7 points.
- ruled out with a line of evidence each: the funding economy, the conversion job, the target
  choice. **Responsible: the Produce→Deforest switch.**

**The one repair, in flight.** `PRODUCE_ROSTER_CAP` 5 → **3**: Produce ends the turn after the
third troll exists. **codex_1 hit its account's usage limit at 12:55Z and cannot run until
2026-09-07**, so *the coordinator built v3 himself* — `readable/norxondor-port-v3.rs`,
`cgauto/submissions/candidate-norxondor-port-v3.rs`, sha
`84870bc95f862b4c4e6b5e6d6f692674af2a750803a8c3735d8964d30d2c4e83`, 82,572 UTF-16 units, both forms
compile; the diff is the constant, its comment and one use. **claude_1 is now the only independent
check** (handoff `20260902T131800Z`, ack-required): gates + reproduction + rung 1. That weakening is
written on the card and in the owner's queue.

**Pre-registered before v3's numbers exist** (12:55Z policy): rung 2 rerun only if rung 1 improves
on −0.421; the loss read's phase table recomputed for v3 whatever the verdict; **the coordinator's
expectation is that this narrows the gap without closing it**; and **if v3's field reading is still
below zero with its interval clear of zero, the card's dead condition applies and the port line
closes** — the successor to put to the owner would be narrower: our champion plus a cheaply funded
third troll (the piece both the loss read and Track E point at). Nobody starts that without the
owner's word.

## Track E — closed the same day (DONE, not dead)

`claude_1/endgame-gap/READ-2026-09-02.md` (pinned `447ff1d9…`): the late MOVE gap is real
(0.17 moves per troll-turn in turns 251–300 against the field's 0.37–0.62) but **it is not idle
production** — 84 % of our idle late turns are terminal waits on a board our own clear-cut has
emptied; when we trail at turn 250 the last fifty turns go +34 to +80, and that 46-point gap
decomposes as roster ×0.70 · idleness ×0.85 · output ×0.93. Any endgame rule is worth ≤ 6 points a
game. **No rule; the layer is the roster and a map kept alive.** Two signatures carried to the
port's loss read.

## Track N — the network line (background, all four arms running)

- **Host** (`/home/tarstars/nn-data/…-0902c/`): `ppo-host-s22` (the stack, 2,709 updates) and
  `ppo-host-s22L` (doubled budget, 5,419), relaunched 12:2xZ on mains; ~4.6 s an update.
- **Cluster** (slots came after five hours pending): `ppo-yt-s22L` op `371ec5d0…`, `ppo-yt-s512`
  op `50c1737e…`.
- **Their reads were written blind this morning**:
  `local_claude_1/nn-bot/PREREG-2026-09-02-depth-rollout512.md` — the depth gate compares s22L's
  *end* (updates 5,250/5,419) with s22's end (2,500/2,709) because the trainer anneals the learning
  rate over the whole budget; s512 by the standard gate at 1,500/2,500 against s22; every gate run
  with `PYTHONHASHSEED=0`.
- Ledger unchanged: clone 26 · r22 31/29 · **s22 29/33/33** of 144; parity 72.

## The ladder (the coordinator's again since 09-02)

The champion of record was resubmitted at 08:00Z as `41230202` and read **17.04 at rank 110 of 177**
at 09:05Z — the same file read 21.2/42 on 08-27 and 18.2/85 on 08-29: **the field rises about a
point a day while our bot stands still.** It holds the ladder; its 160 games are collected. The VM
runner (`local_claude_1/ladder-queue/runner.py`, cron every 5 min) now **syncs the checkout to
`main` before every tick**, so a queue pushed from anywhere reaches it.

## Autonomy built today (the owner: "I want this research to move on without me pushing it")

1. The coordinator paces itself with scheduled wakes (10 minutes in an active phase, an hour when
   quiet).
2. **The VM fallback seat** — `/home/tarstars/coordinator-watchdog.sh`, cron at :20, prompt
   `/home/tarstars/coordinator-wake-prompt.txt`, repo copy `local_claude_1/coordinator-fallback/`:
   when `BOARD.md` on `origin/main` is older than **one hour** (lowered from three while the laptop
   runs on battery) **and** mail waits, it runs one headless coordinator wake on the VM.
3. The bots wake through the launcher on ack-required mail.
4. A **battery guard** (`/home/tarstars/nn-data/battery-guard.sh`, pid file beside it) stops every
   host training within a minute of the mains going away; it fired at 09:11Z and the arms were
   relaunched at 12:2xZ.

## Rules learned today (they cost time; keep them)

- **A message that assigns work must be `requires_ack: true`** — the launcher only rings an agent
  for messages in its wake set. My 10:33Z acknowledgement chartered claude_1's next two steps and
  woke nobody; 45 minutes were lost.
- **Pin the maps.** The daily collector appends to `data/processed/maps.jsonl`; two arms prepared on
  different days train on different corpora (the first s22L carried 6,373 maps against s22's 6,218 —
  aborted while queued). Cluster: `--maps yt_work/ppo/<control>/maps.jsonl`, then compare the hash
  *inside* the payload tarball. Host: the pinned copy
  `/home/tarstars/nn-data/maps-host-corpus-0901-31088.jsonl` (sha `f56dee62…`).
- **An adjudication message must carry the `quarantines: [...]` array**, or the sweep rejects it;
  and check an `ack_for` target's branch with `git ls-remote`, not local remote-tracking refs (my
  09-01 ruling named a message on a branch that had vanished, blocking every agent's `--mark`).
- **`ssh troll-vm '<cmd>'` starts in `$HOME`** — always `cd /home/tarstars/prj/troll_farm &&` or
  pipe a script with `bash -s`.
- **The host is a laptop**: check `/sys/class/power_supply/AC/online` before training or benching.
- Two reviewers caught **disjoint** holes in the same design. Keep both halves of a review round.

## Open, not mine to do

- **codex_1's credits** (owner's queue item 0): out until 09-07.
- The clean-room package (Track C) still waits on chatgpt_1's gate-7 look and the owner's own read;
  `root_codex`'s branch is gone from origin and its reproduction request stands open for whichever
  agent the owner names.
- The owner's prediction, asked before any ladder hour for a candidate.

## The next three things, in order

1. claude_1's handoff on v3: gates, byte-identity reproduction, rung 1's FIELD line.
2. The ruling on it — rung 2 if it improved, the dead condition if it did not, either written on
   the card and the board with a recommendation in the owner's queue.
3. Track N's arms as they land: retrieve, bench in the pre-registered order, gates with
   `PYTHONHASHSEED=0` (host s22 first, ~4 h from 12:2xZ).
