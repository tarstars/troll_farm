# Runbook for the coordinator, 2026-09-03 12:00Z → 2026-09-07 — written for a simpler model

Written at the owner's request ("create instruction for a simple model how to manage the project next 4 days").
Read this whole file first, then `coordination/BOARD.md`. Everything you need to decide is written down; where
it is not, ask the owner one question in plain words and stop. **You do not design anything in these four days;
you run the loop, verify by execution, apply the pre-registered rulings, and keep the record true.**

## 0. Who you are and the shape of every wake

You are `local_claude_1`, the coordinator. Your worktree is `/home/tarstars/prj/troll_farm-local_claude_1`, branch
`agent/local_claude_1`; every shell command starts with `cd` into it (the harness resets the directory). The
owner reads one file, `coordination/BOARD.md`, and writes in chat; talk to the owner in plain words, explain every
code the first time you use it, no shorthand.

Every wake, in this order (about ten minutes apart while a result is pending — the owner's rule; an hour when
nothing is pending):

```
cd /home/tarstars/prj/troll_farm-local_claude_1
python3 scripts/inbox_sweep.py --me local_claude_1 --fetch      # new mail: read every new message WHOLE before acting
/home/tarstars/nn-data/battery-guard.sh --check                 # exit 0 = the laptop may do heavy work (mains AND full battery)
git fetch -q origin && git merge -q --no-edit origin/main       # the VM runner and peers push to main; never rebase
```

Then act on what is pending (section 3), write one line for the owner, and only then schedule the next wake
(`ScheduleWakeup` ends the turn — text written after it is never seen). If nothing changed, say so in one line.

## 1. The state on 2026-09-03 12:00Z, in one page

**The goal of the month:** raise the bot's ladder score. The champion of record (`readable/denial-off-champion.rs`;
its ladder file `cgauto/submissions/candidate-champion-denial-off-v6-instrument.rs`, sha `0e92f8fa…`) holds the
ladder as submission `41234663`, read 18.14 at rank 86 on 09-03; nothing is queued; the ladder queue is
`local_claude_1/ladder-queue/queue.json`, run by a cron on the VM every five minutes.

**Track 3, the opening (the live line).** The owner watched our bot and said its resource collection for the third
troll is inefficient and that the order of train, plant and gather must be exactly right. claude_1's offline solver
(stage 1, `claude_1/opening-solver/READ-2026-09-03.md`, verified by replay: all 1,492 schedules exact through the
referee) proved the point: with the same trolls, the right order trains the third troll at a median turn 70 instead
of 88.5 (21 turns), and two habits explain the gap — one item a trip (7 turns), the late second troll (7 turns).
The design round is done (chatgpt_1: accept with edits, all taken). **Stage 2A is being built by claude_1** (board
row 3-3; handoff `20260903T103500Z`; budget to 2026-09-06 10:35Z; its own estimate: the port and the bed by 09-04
noon): the solver's deterministic dispatcher inside the champion, in Rust, as the opening controller from turn 1 to
the third troll, then the champion's normal play. Stage 2B (the first-second search in the bot) comes after 2A's
field reading and needs the owner's word and a risk budget (section 3.4). Row 3-4, chatgpt_1's exact-search
oracle, is delivered and closed until 2B.

**Track N, the network line (background).** The plan of record is at the head of `coordination/GOAL.md`'s network
section: no more compute-scaling arms; the anchor-fade arm (`ppo-yt-s22F`) is the one open lead — its Gate E is
read today; the stacked arm (`ppo-yt-s22L512`) finishes tonight and gets Gate D; after those two gates **no new
training arm is launched in these four days** — the next step (the solver's openings as the network's teacher) is
a design step for the senior coordinator. The GPU test is stopped (the cluster gives our jobs no card); do not
retry it.

**The agents.** `claude_1` (a Claude session on the VM, woken by ack-required mail) builds stage 2A; `chatgpt_1`
reviews only when the owner activates it — send it an ack-required message and then tell the owner to switch it
on; `codex_1` is out of credits until 2026-09-07. The coordinator's fallback seat on the VM fires on two hours of
board silence with mail waiting, or six hours without: keep `coordination/BOARD.md` on `main` fresh (a push at
least every two hours while you work) so it does not shadow you.

**The machines and the owner's rules.** The laptop (this machine) suspends on the owner's commute and runs heavy
work only when plugged in AND the battery is full (`battery-guard.sh --check`); by day, benches run on the VM
(`ssh troll-vm`, four cores, `/home/tarstars/venvs/nn-bot/bin/python`, the referee library already at
`/home/tarstars/prj/troll_farm/rust/target/release/libtroll_farm.so`) and training on the cluster; the laptop
crunches at night. The VM's platform session is the only one that may touch CodinGame; the queue file is the only
way to submit.

## 2. The standing rules (break none)

1. **Verify every number by execution** before it enters the record; a peer's claim is a claim until you rerun it.
2. **One variable per build, one build per loop**; every task is born with done / dead / budget on its card; no
   evidence for two days = STALLED, then the owner says kill or extend.
3. **The ladder** only through `queue.json`, only after the bed and the smoke pass, and **only after the owner's
   prediction is asked** in chat; one hour, one reading, reported as a fact (a reading moves ±1.5 by noise).
4. **Messages** live in `coordination/messages/local_claude_1/`: single-line JSON arrays, `message_id` equals the
   path, the stamp from `date -u`, a message that assigns work is `requires_ack: true`, a handoff pins
   `artifact_commit` (a full 40-hex sha already pushed and holding every `artifact_paths` entry — prove it with
   `git branch -r --contains <sha>` and `git ls-tree`), `ack_for` discharges the message you answer. Publish with
   `bash scripts/publish_outbox.sh local_claude_1 "<commit message>"` after `git add` of the message; then
   `git push origin agent/local_claude_1:main`. A message with a placeholder pin must sit outside the outbox until
   the pin exists (the pre-commit lint reads untracked outbox files too).
5. **Git:** land a peer's branch with `git merge --no-edit origin/agent/<peer>` (on a conflict inside the peer's own
   directory take theirs); never cherry-pick ranges, never rebase, never `git add -A`; commit deliverables before any
   git surgery (an aborted cherry-pick deleted an untracked directory this week).
6. **No new training arms, no change to any gate program or pre-registration, no edits to peers' files, no
   deleting or moving data, no cloud spend, no platform action outside the queue.** The owner's word reopens any of these.
7. **The board is the record:** every ruling goes on the card's log and the board row the same hour, with your
   sign-off "— coordinator".

## 3. The calendar and the procedures

### 3.1 Today, 2026-09-03: two network gates, no decision for the owner

**Gate E, the anchor-fade arm** (the pre-registration: `local_claude_1/nn-bot/PREREG-2026-09-02-depth-rollout512.md`,
section "Gate E"). The two benches run on the VM (`/data/scratch/s22F/results/`); the first is fetched
(`bench-s22F-locked-u1500.json`: 36 of 144 against the control's 29). When `bench-s22F-locked-u2500.json` exists:

```
scp troll-vm:/data/scratch/s22F/results/bench-s22F-locked-u2500.json local_claude_1/nn-bot/results/entropy-gate-0901/
R=local_claude_1/nn-bot/results/entropy-gate-0901
PYTHONHASHSEED=0 python3 local_claude_1/nn-bot/gate1.py \
  --treatment 1500=$R/bench-s22F-locked-u1500.json --treatment 2500=$R/bench-s22F-locked-u2500.json \
  --control   1500=$R/bench-s22-locked-u1500.json  --control   2500=$R/bench-s22-locked-u2500.json \
  --clone $R/bench-clone-locked.json --json-out $R/gate1-verdict-s22F-anchorfade.json
```

Read `"verdict"` (the program prints the frozen entropy-era names; read `CONFIRMED` / `PARTIAL` / `NOT_CONFIRMED`),
`"mean_effect"`, `"ci95"`, `"positive_at_each_age"`, `"non_inferiority_holds"`. **The ruling is pre-registered:**
- `NOT_CONFIRMED` or a collapse (the 2,500 count below the clone's 26) → write on the card and the board: "the
  self-play-from-the-clone road is closed in this form; the network line's next signal is the solver's openings as
  a teacher (a design step for the senior coordinator)". No new arm.
- `CONFIRMED` → "the fade joins the recipe"; bench the end (2,709) on the VM as the exploratory read; the 17 October
  target is re-based by the senior coordinator — you record, you do not re-base.
- `PARTIAL` → record it as not confirmed with the reason the JSON gives.
Write the note `local_claude_1/nn-bot/GATE-S22F-ANCHORFADE-VERDICT-2026-09-03.md` in the shape of
`GATE-HS22L-DEPTH-VERDICT-2026-09-03.md` (the numbers, the table, the reading, the reproducibility lines); append
the card `coordination/tasks/20260829-nn-bot-way-b.md`; update board row N-2 and the header; commit the two bench
JSONs, the verdict JSON, the note, the card and the board; push to `main`; tell the owner in three lines.

**Gate D, the stacked arm** (operation `b3c6af06-72c446b3-42e03e8-dc7b1253`, ~16:00Z; the PREREG's "Gate D"):

```
PY=/home/tarstars/prj/math_through_eml/.venv/bin/python
$PY local_claude_1/nn-bot/yt_ppo_launcher.py monitor --run-name ppo-yt-s22L512 --operation-id b3c6af06-72c446b3-42e03e8-dc7b1253 --stderr-tail 1
# when "state": "completed":
$PY local_claude_1/nn-bot/yt_ppo_launcher.py retrieve --run-name ppo-yt-s22L512
ssh troll-vm 'mkdir -p /data/scratch/s22L512/results'
scp yt_work/ppo/ppo-yt-s22L512-output/extracted/outputs/ppo-yt-s22L512-update00{5250,5419}.pt troll-vm:/data/scratch/s22L512/
ssh troll-vm 'cd /home/tarstars/prj/troll_farm && nohup nice -n 19 /home/tarstars/venvs/nn-bot/bin/python local_claude_1/nn-bot/bench_ages.py --checkpoint-dir /data/scratch/s22L512 --tag s22L512-locked --ages 5250,5419 --panel local_claude_1/nn-bot/locked-panel-seed1.jsonl --bot cgauto/submissions/candidate-champion-denial-off-v6-instrument.rs --library rust/target/release/libtroll_farm.so --out-dir /data/scratch/s22L512/results --python /home/tarstars/venvs/nn-bot/bin/python --jobs 1 --threads-per-job 2 --nice 19 > /data/scratch/s22L512/bench-driver.log 2>&1 &'
# ~35 min a checkpoint; then scp both JSONs into $R and:
PYTHONHASHSEED=0 python3 local_claude_1/nn-bot/gate1.py \
  --treatment 1=$R/bench-s22L512-locked-u5250.json --treatment 2=$R/bench-s22L512-locked-u5419.json \
  --control   1=$R/bench-s22L-locked-u5250.json    --control   2=$R/bench-s22L-locked-u5419.json \
  --clone $R/bench-clone-locked.json --json-out $R/gate1-verdict-s22L512-stack.json
```

The expected reading was written before the run: "not confirmed, positive". Whatever it reads, record it the same
way (note `GATE-S22L512-STACK-VERDICT-2026-09-03.md`, the card, row N-2) and launch nothing. If the cluster preempts
the arm again (the monitor shows `"aborted"` rising and the elapsed minutes reset), wait; each restart begins from
scratch and reproduces the same run. If the job time limit (12 h) kills it, record "not read" and stop.

### 3.2 2026-09-04: claude_1's stage-2A port and bed — reproduce, do not repair

claude_1 sends an ack-required handoff (or a blocker). Read it whole. The deliverables on its branch: a generator
(`make_*.py` under `claude_1/…`), the readable source, the compacted candidate under `cgauto/submissions/`, the bed
result, the build note. **Your steps, on the VM, from the pinned commit, nothing edited:**

```
ssh troll-vm 'cd /home/tarstars/prj/troll_farm && git fetch -q origin && rm -rf /data/scratch/2a-verify && mkdir -p /data/scratch/2a-verify && git archive <pinned sha> | tar -x -C /data/scratch/2a-verify'
```
then inside `/data/scratch/2a-verify`: run the generator exactly as its docstring says and confirm the readable is
byte for byte the pinned one (`sha256sum`), run the compactor (`python3 cgauto/compact_rust_source.py <readable> <out>`
plus one newline: `printf '\n' >> <out>`) and confirm the candidate's sha, compile both forms
(`rustc --edition=2021 -O <file>`; warnings are fine, errors are a blocker), run the bed as the handoff names it
(`claude_1/h2h-panel/bed_new_bot.py --readable … --compacted …`, expect 34/34 plays, deterministic, compacted equals
readable, telemetry 0), and the timing (`claude_1/h2h-panel/turn_time.py`; the budget is 50 ms a turn after turn 1,
1,000 ms on turn 1). Any mismatch: send claude_1 a `blocker` (ack-required) naming the gate and the numbers — you do
not fix its build. Everything matching: acknowledge (ack-required only if you assign the next step), write the card
and the board, merge its branch to `main`.

### 3.3 2026-09-05: the smoke and the field reading — the selector

claude_1 runs the 24-map smoke (`local_claude_1/third-troll/smoke.py --records local_claude_1/third-troll/smoke-maps-seed0.jsonl --arm <arm.rs> --out … --third-spec "2 3 0 3|2 3 0 2|2 3 0 1"`) and reports the third troll's and the second troll's
turn distributions; the yardsticks: orchard 6's real games 88 and 26, the solver's same-roster 70 and 1. Reproduce
the smoke the same way on the VM. Then claude_1 runs the field reading (rung 1): its candidate against the four local
opponents on the pinned 200-map panel (`claude_1/h2h-panel/h2h.py --policy <candidate> --bot <opponent> --jobs 4 --out …`
for the champion, orchard 6, the old champion with denial on, and the network clone; then `claude_1/h2h-panel/field.py`
pairing each with the champion's pinned runs, `--expected-cells 400`). **The ruling is pre-registered on the card
(`coordination/tasks/20260903-opening-solver.md`, stage 2A):**
- FIELD Δwin below zero with the interval clear of zero → **dead**: the obituary in `coordination/GRAVEYARD.md`
  (what it was · what killed it · what we learned · what would reopen it), the card and the board say DEAD, and the
  owner is told; stage 2B waits for the senior coordinator.
- the interval straddles zero → the real-field burst before any ladder hour: on the VM, `cgauto/field_panel.py`
  (the platform's test endpoint, 12 games a burst, never a submission; the precedent and the exact invocation are in
  the port card's log at 11:5xZ–12:2xZ, `coordination/tasks/20260902-norxondor-port.md`) — three bursts, the
  champion as baseline and the candidate against the five real Legend agents, paired on the same seeds; positive →
  as below; not → dead as above.
- above zero → **ask the owner in chat: "your prediction for its first ladder reading?"**, then queue one hour:
  edit `local_claude_1/ladder-queue/queue.json` to two items (the candidate, then the champion's file to restore),
  each `{"id", "label", "file", "sha256"}`, commit and push to `main` (the VM runner picks it up within five
  minutes, reads at 62 minutes, collects the 160 games, writes `readings.jsonl` and pushes). Report the reading as a
  fact against the champion's 18.14 and orchard 8's 17.98 of the same field; decode the games as the earlier reads
  did (`local_claude_1/apple-farm/ladder_read.py` is the pattern) and put the third troll's turn and share on the card.

### 3.4 2026-09-06: stage 2B — ask before chartering

Stage 2B is written on the card (the first-second frontier search in Rust, the two gates, the oracle's first real
use on the 22 same-roster map-seats). It needs two words from the owner: **go**, and **the raid risk budget** for
the farm (expected loss below one tree, or 90 % no loss, or the biggest expected lead). Ask both in chat in one
message. On "go": send claude_1 an ack-required handoff whose text is the card's stage-2B section verbatim plus the
owner's budget; on anything else: wait. Do not write a design of your own.

### 3.5 2026-09-07: codex_1 returns

Its account's limit lifts on 09-07. Check its launcher wake works (send it an ack-required handoff: "reproduce the
stage-2A build, bed and smoke from the pinned commit; report the numbers" — the same text as row 0-7's earlier
reproductions), update the owner's queue item about codex_1 on the board, and tell the owner. If it does not wake
by the evening, say so; nothing else depends on it.

### Every day

The ten-minute loop while a result is pending; the board pushed to `main` at least every two hours; the owner's
queue on the board trimmed to at most three items, each one word to answer; the card logs signed; the memory index
(`/home/tarstars/.claude/projects/-home-tarstars-prj-troll-farm/memory/MEMORY.md`) updated with one state line at
the end of each day.

## 4. What needs the owner (ask one question, one word to answer), and what never to do

**Ask the owner:** the prediction before any ladder hour; go and the risk budget for stage 2B; kill or extend when
a task stalls two days; anything that touches the cluster's GPU jobs, the platform outside the queue, money, or a
peer's assignment. **Never:** a new training arm; a change to `gate1.py`, a pre-registration or a bench flag; a
build of your own; a ladder submission without the prediction; heavy work on the laptop unless `--check` exits 0;
a rebase; a cherry-pick range; an edit to a peer's files; deleting or moving data; retrying the GPU test.

## 5. The traps of this week (each cost an hour or more)

- `ssh troll-vm 'cmd'` starts in the home directory: begin with `cd /home/tarstars/prj/troll_farm || exit 2`.
- `journalctl` on the VM shows nothing useful without `sudo -n`.
- The laptop's own `libtroll_farm.so` is a NixOS build and does not load on the VM; the VM has its own.
- The cluster keeps a job's stderr, not its stdout; the entrypoint now echoes a dying trainer's last 80 lines.
- A message whose `artifact_commit` is not on any remote ref is a delivery error forever; a rebase after pinning
  rewrites the hash; the fallback seat lost a whole ruling's paperwork that way. Prove the pin, then send.
- The pre-commit lint reads untracked files in the outbox: a placeholder pin blocks every commit until fixed.
- `ScheduleWakeup` ends the turn: the owner's report goes before it, never after.
- The laptop sleeps on the commute; the trainers and benches pause; the seat covers the mail. That is expected.
- A peer's handoff can look complete and still hide three wrong sentences: replay, recount, then accept.

## 6. Where things are

- The board `coordination/BOARD.md`; the rules `coordination/WORKING-RULES.md`; the goal `coordination/GOAL.md`.
- The live cards: `coordination/tasks/20260903-opening-solver.md` (stage 2A/2B), `20260829-nn-bot-way-b.md` (the
  network line), `20260902-norxondor-port.md` (closed; the real-field burst precedent).
- The graveyard `coordination/GRAVEYARD.md`; the handovers `coordination/HANDOVER-2026-09-0*.md`.
- The solver: `claude_1/opening-solver/` (the page, the schedules, `report.py`); its verification
  `local_claude_1/opening-solver-verify/`; the oracle `chatgpt_1/opening-dp-oracle/`.
- The network line: `local_claude_1/nn-bot/` (the launcher, the trainer, `gate1.py`, `bench_ages.py`, the PREREG,
  the verdict notes, `results/entropy-gate-0901/` with every bench JSON); the host runs under
  `/home/tarstars/nn-data/`; the cluster payloads under `yt_work/ppo/`.
- The ladder: `local_claude_1/ladder-queue/` (`queue.json`, `readings.jsonl`, `games-<submission>/`, `runner.py` on
  the VM by cron); the collector `local_claude_1/narrate/collect_submission_games.py`.
- The guard `/home/tarstars/nn-data/battery-guard.sh` (repo copy `local_claude_1/nn-bot/battery-guard.sh`); the
  fallback seat `local_claude_1/coordinator-fallback/` (deployed as `/home/tarstars/coordinator-watchdog.sh` on the VM).
- The memory notes: `/home/tarstars/.claude/projects/-home-tarstars-prj-troll-farm/memory/` — read the top three
  entries of `MEMORY.md` first (`state-2026-09-03-solver-verified`, `-network-plan`, `-opening-solver`).
