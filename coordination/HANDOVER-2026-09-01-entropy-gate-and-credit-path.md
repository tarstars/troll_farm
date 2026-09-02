# Handover — 2026-09-01 08:4xZ — the entropy gate mid-flight, and the credit path measured

Written at the owner's request ("prepare for context flush"). Everything below is on `main`.
Read `coordination/GOAL.md` step 4 first, then the tail of
`coordination/tasks/20260829-nn-bot-way-b.md` (the chronological log; append new entries at the
file end), then this.

## Where the work stands in one paragraph

Step 4 of the recovery programme — the entropy falsifier — is **running, not finished**. Four
training arms are in flight: two on the cluster (`ppo-yt-e00b`, `ppo-yt-e01b`) that should reach
their 2,709 updates around 09:45Z, and two on this host (`ppo-host-h00`, `ppo-host-h01`) that are
slower and will land overnight. Nothing has been benched yet, so **no Gate-1 verdict exists**.
The two instruments that turn finished runs into a verdict are built, tested and merged, so the
remaining work is mechanical. Separately, the credit-path measurement is done and is the most
consequential result of the day.

## The four arms in flight

| arm | platform | entropy | where | note |
|---|---|---|---|---|
| `ppo-yt-e00b` | cluster, op `942710be-34351794-42e03e8-40fd77b2` | 0.0 | `//home/delivery_ml/research/tarstars/troll_farm/runs/ppo-yt-e00b` | started 08:16:55Z, ~1,830 updates/h |
| `ppo-yt-e01b` | cluster, op `c875f4ec-47d02772-42e03e8-eae6a5ec` | 0.01 | same root, `.../ppo-yt-e01b` | started 08:17:38Z |
| `ppo-host-h00` | this host, pid at launch 2998243 | 0.0 | `/home/tarstars/nn-data/ppo-host-h00-0901/` | update 427/2,709 at 08:44Z |
| `ppo-host-h01` | this host, pid 2998245 | 0.01 | `/home/tarstars/nn-data/ppo-host-h01-0901/` | update 430/2,709 |

All four: seed 41, `--train-scope plan-critic`, clone `970097ed…` as initial/anchor/frozen
checkpoint, `--total-turn-steps 11100000` (= 2,709 updates), `--checkpoint-every 250`. **Each
pair was verified to differ in exactly one field** (`entropy_coef`; plus `output_dir`/`run_name`),
which is what makes each platform's comparison valid on its own. The cluster pair uses the
launcher's default one-in-five map slice, the host pair the full 31,088-map corpus — identical
*within* each pair, so neither comparison is affected, but it must be declared in the handoff.

Cluster start command shape (the pool has no default and must be named):

```
yt_ppo_launcher.py start --run-name ppo-yt-e00b \
  --pool-tree gpu_starfield_24g_cloud --pool research_gpu \
  --cpu-limit 32 --gpu-limit 1 --memory-limit 51539607552 \
  --job-time-limit-hours 6 --heartbeat-minutes 5 --async
```

The GPU slot is reserved, never used — a CPU-only job needs it only so a GPU pool tree will
schedule it (the owner's word of 2026-08-30).

## What to do when the arms finish — the whole remaining recipe

1. Retrieve: `yt_ppo_launcher.py retrieve --run-name ppo-yt-e00b --output-dir
   yt_work/ppo/ppo-yt-e00b-output` (run with the math venv python; checkpoints land under
   `extracted/outputs/`, not `outputs/`). If a run was preempted instead, its checkpoints are in
   the cluster salvage — `yt list <run>/outputs` now shows **every** checkpoint, not just the
   newest (see the fix below); pull with `yt read-file`.
2. Scout benches, both arms, five ages:
   ```
   bench_ages.py --checkpoint-dir <dir> --tag e00b --ages 500,1000,1500,2000,2500 \
     --panel local_claude_1/third-troll/smoke-maps-seed0.jsonl \
     --bot cgauto/submissions/candidate-champion-denial-off-v6-instrument.rs \
     --library rust/target/release/libtroll_farm.so --out-dir <out> --jobs 2
   ```
   Run from the worktree root — the panel, bot and library paths are relative to it.
3. Confirmation benches at u1500 and u2500 on the 144-cell locked panel
   (`local_claude_1/nn-bot/locked-panel-seed1.jsonl`), same driver, `--panel` swapped.
4. The verdict:
   ```
   gate1.py --treatment 1500=<e00b u1500>.json --treatment 2500=<e00b u2500>.json \
            --control  1500=<e01b u1500>.json --control  2500=<e01b u2500>.json \
            [--clone <clone bench>.json]
   ```
   E00 (entropy 0) is the **treatment**, E01 (entropy 0.01) the **control**; the effect is
   E00 − E01 on paired cells.

**Host CPU discipline:** the owner's standing cap is host training at ≤14 threads, low priority.
The two host arms use exactly 14 cores at nice 15. Benching on this host while they run adds
load — keep benches to a couple of jobs at `--nice 19` and say so, or wait.

## The instruments built today (both tested before their data existed)

- **`local_claude_1/nn-bot/gate1.py`** + `tests/test_gate1.py` (9 tests) — the frozen Gate 1 of
  `GOAL.md` step 4. Resamples whole map-seat cells so a cell's two ages move together (the
  reviewer's 11:45Z correction: never a 288-row pool); one test asserts the interval stays wide
  enough to prove the ages are not pooled as rows. All four verdicts reachable; INCONCLUSIVE
  beats any statistic on incomplete evidence, including a huge effect on too small a panel.
  **Where the frozen text is silent** — which combination gives PARTIAL rather than CONFIRMED —
  the file states its reading explicitly, prints it as `decision_rule` with every verdict, and
  the reviewer can overturn it without touching the arithmetic.
- **`local_claude_1/nn-bot/bench_ages.py`** + `tests/test_bench_ages.py` (7 tests) — benches both
  arms at fixed ages with identical flags by construction; one test asserts two arms' commands
  differ in exactly two places (checkpoint, output path). A directory holding two runs'
  checkpoints raises rather than silently picking one.
- **`local_claude_1/nn-bot/entropy_log_read.py`** — the paired training-side read of two arms'
  logs, block-bootstrapped because neighbouring updates share a rolling episode window.
- **`local_claude_1/nn-bot/credit_path_read.py`** + `tests/test_credit_path_read.py` (6 tests) —
  what the learning signal is made of. **Read its docstring before using it**; its headline was
  corrected today (below).
- **`local_claude_1/nn-bot/yt_ppo_entrypoint.py`** + `tests/test_yt_ppo_entrypoint.py` (4 tests)
  — the cluster salvage now keeps **every** checkpoint under its own name, uploaded once, oldest
  first, capped per beat. Keeping only the newest is what made the first cluster attempt worthless.

## The three results of the day

1. **Entropy is a null, on the training side.** Over 3,417 paired updates at one seed, the bonus
   raised entropy by +0.073 (interval [0.056, 0.089]) — the knob works — and bought nothing:
   win-rate delta −0.0013 with the interval straddling zero, referee margin 0.70 *worse*. This is
   evidence, **not** the gate; the gate is benched argmax play on fixed panels.
2. **Depth actively hurts.** The entropy-off arm ran 50 M turn-steps and its training win rate is
   flat (0.180 at u500, 0.182 at u12,000) while its margin decayed. Benched: **2/48 at u12,250**
   against **9/48 at u3,250**. Every run ever benched shows the same shape — the score peaks near
   the clone and decays with training; nothing has passed 10/48, parity needs 24/48.
   **Instrument warning:** those two checkpoints logged an *identical* training win rate of 0.185
   while benching 4 % and 19 %. Training win rate does not track bench win rate.
3. **The credit path — and a correction I made to myself.** I first wrote that "the plan head
   never sees a reward at all". **That was wrong.** `compute_gae` sets the trace factor to exactly
   1.0 *inside* a turn (`train_ppo_full.py:501–545`) precisely so a turn's reward reaches its plan
   row undiminished; the reward is simply not stored in the plan row's own slot, because
   `--reward-credit executing` puts it on the mini-step that executes the turn. Measured on the
   right quantity: **observed reward supplies 2.32 % of the plan head's learning signal and the
   critic's own values supply 97.68 %**, reproduced by the second arm to two decimals. The trace
   reaches a real game ending on 1.8 % of rows. The finding survives in weaker, accurate form and
   still explains the depth curve — but "the reward is absent" is not the diagnosis, "the reward
   is 2 %" is, and the two point at different fixes.

## The fix menu given to the owner (their decision, nothing launched)

The reward formula, read from the simulator (`rust/src/rl_full.rs:1904–1915`):

```
each turn:  reward  = wood_shaping × (wood delivered this turn)
at the end: reward += (my fruit + end_wood × my wood) − (opponent's the same)
```

Our runs use `wood_shaping = 0`, `end_wood = 4` — **the entire payoff arrives in one lump on the
final turn**, while the trainer looks ahead only ~8–10 turns of a ~285-turn game.

1. **Slide the payoff into the turns — one flag pair, no new code.** Keeping
   `wood_shaping + end_wood = 4` preserves wood's true value exactly while making a fraction of it
   arrive when it is earned (`0+4` is what we ran; `2+2` makes half immediate; the environment's
   own default is `0.5+3.5`). Caveat to state: wood delivered and later spent on training gets the
   immediate part without appearing in the final score — a small bias toward delivering wood,
   which is what the champion does anyway. **My recommendation: run this first, as a paired
   experiment exactly like the entropy one, judged by the same frozen gate.**
2. **Look further ahead**: `--rollout-steps` 32 → 128 with `--num-envs` 128 → 32, holding the
   batch at 4,096 — same compute, traces spanning ~35 turns instead of ~9.
3. **Whole-game returns for the planner** if 1–2 do not move it (critic as baseline only).
4. **Repair the critic** last, because 1–3 improve its targets anyway.

**Nothing from this menu has been launched.** The owner was asked and has not yet chosen; the
one-variable rule says do not stack it on the entropy arms.

## Track C — halted, waiting on the owner

The clean-room package is **delivered, verified and merged** (`cleanroom/package/`, 33 files, zero
`.rs`, the champion as a stripped binary with a 9,502-seat-turn parity proof, 26 cited
observations). Per the owner's stop it **halts** for two reviews: chatgpt_1's adversarial
cross-review (chartered 07:45Z, ack-required) and **the owner's own read**. No implementer exists
until the owner's explicit word after both; the implementer mechanism is their open choice (my
recommendation: a launcher entry `fresh_1` cwd'd at the package).

## Open, not mine to do

- The owner runs chatgpt_1; it has **four** items waiting: two progress reports, the clean-room
  cross-review, and tonight's Gate-1 review when the verdict exists.
- `~/.codex → /data` symlink at the next codex restart; the owner's word on launcher-log rotation
  and on clearing stale `/tmp` older than ~12 h.
- The owner's choice from the fix menu above.

## Standing constraints (verbatim force)

No platform action; no deleting or moving data; no cloud spend beyond the pool in use; **never
touch the owner's running codex process or `~/.codex`**; host training ≤14 threads at low
priority; cluster budgets consistent (the wall-clock limit must be enough for the step budget —
the 60 M-steps-under-17-hours shape is what made five preemptions worthless); the owner is not to
be woken by the loop.
