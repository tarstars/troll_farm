# Pre-registration — 2026-09-02 07:3xZ — the depth question (s22L) and the 512-step rollout (s512), written before any of their numbers exist

## Why this file exists

The card (09-02 04:5xZ) says any promotion claim from the doubled-budget arm needs a fresh frozen
gate written **before** its numbers are seen. This is that gate, plus the pre-registered reads for
the other three arms launched this morning. At the time of writing: `ppo-yt-s22L` (relaunched
07:18Z, operation `371ec5d0-7528153d-42e03e8-30941f24`) and `ppo-yt-s512` (07:18Z, operation
`50c1737e-2212e43a-42e03e8-a7d614ed`) are **pending a cluster slot**; no checkpoint of either exists
anywhere; the two host arms were stopped at update 21 (the host is on battery — see the last
section) and restart identically when the machine is back on mains. Nothing below was shaped by a
result.

## The arms and their controls (one variable each)

| arm | platform | differs from its control in | control (already benched on the locked panel) |
|---|---|---|---|
| `ppo-yt-s22L` | cluster | `--total-turn-steps 22200000` (5,419 updates) vs 11,100,000 (2,709) | `ppo-yt-s22` (29 / 33 / 33 at 1,500 / 2,500 / 2,709) |
| `ppo-yt-s512` | cluster | `--rollout-steps 512 --num-envs 8` (batch 4,096 held) vs 128 × 32 | `ppo-yt-s22` |
| `ppo-host-s22` | host | `--rollout-steps 128 --num-envs 32` vs 32 × 128 | `ppo-host-r22` (hr22: 28 / 31) |
| `ppo-host-s22L` | host | `--total-turn-steps 22200000` vs 11,100,000 | `ppo-host-s22` (once benched) |

Every arm shares its control's map corpus **byte for byte**: on the cluster the 6,218-map slice
(sha256 `16577bf1c96a…`, verified inside all three payload tarballs); on the host the pinned copy of
the 09-01 corpus, `/home/tarstars/nn-data/maps-host-corpus-0901-31088.jsonl` (31,088 lines,
69,696,037 bytes, sha256 `f56dee62b956…`) — see "the map-slice confound" below for why a copy.

## Gate A — the depth gate (s22L vs s22; later host s22L vs host s22)

**Question.** Is the stack trained at a doubled budget a better artefact *at its end* than the
stack at the standard budget at its end?

**Treatment measurements:** s22L at update **5,250** (its last regular checkpoint) and **5,419**
(its final one). **Control measurements:** s22 at **2,500** and **2,709**. **Pairing:** measurement
1 = s22L@5250 − s22@2500 and measurement 2 = s22L@5419 − s22@2709, per cell (map, seat) on the
locked 144-cell panel `local_claude_1/nn-bot/locked-panel-seed1.jsonl`; the rest exactly as
`gate1.py`: the 144-unit clustered bootstrap of the per-cell two-measurement mean (10,000 draws,
seed 1), the mean positive at each measurement, clone non-inferiority of at most 6 net cells
against `bench-clone-locked.json`. **Read as** `DEPTH_CONFIRMED` / `DEPTH_PARTIAL` /
`DEPTH_NOT_CONFIRMED` / `INCONCLUSIVE` (the program prints the frozen entropy-era names; its rule is
variable-agnostic and printed with every verdict). The exact invocation — the frozen `gate1.py`,
untouched; its age labels are measurement numbers and nothing else reads them:

```
cd /home/tarstars/prj/troll_farm-local_claude_1 && R=local_claude_1/nn-bot/results/entropy-gate-0901 && \
PYTHONHASHSEED=0 python3 local_claude_1/nn-bot/gate1.py \
  --treatment 1=$R/bench-s22L-locked-u5250.json --treatment 2=$R/bench-s22L-locked-u5419.json \
  --control   1=$R/bench-s22-locked-u2500.json  --control   2=$R/bench-s22-locked-u2709.json \
  --clone $R/bench-clone-locked.json --json-out $R/gate1-verdict-s22L-depth.json
```

**Why the ends and not equal ages — the anneal caveat.** The trainer anneals the learning rate
linearly to zero over the *total* budget (`train_ppo_full.py`: `fraction = 1 − update /
total_updates`, `--anneal-lr` on by default). At update 2,500 s22's rate is 7.7 % of base while
s22L's is 54 %: **s22L is not "s22 continued", it is a different schedule from update 1**, and the
only like-for-like comparison of the two budgets is end against end (both at rate ≈ 0). This also
qualifies the record: s22's "rise with age" (29 → 33 → 33 at 1,500 / 2,500 / 2,709) coincides with
its rate annealing from 45 % to 0, and a level that *holds* from 2,500 to 2,709 is what a
near-zero learning rate produces whatever the merit. Depth and schedule are confounded inside
"doubling the budget"; Gate A answers the practical question (is the end artefact better), not the
mechanism.

**Exploratory, not the gate** (pre-registered so it cannot be picked afterwards): (i) the schedule
effect at matched age — s22L@1500 / 2500 against s22@1500 / 2500 through the same `gate1`
statistic, labelled exploratory; (ii) the curve s22L@3000 / 4000 on the locked panel. **Bench order
when the run lands:** 5,250 and 5,419 first (the gate), then 2,500, 1,500, 4,000, 3,000 as capacity
allows.

The same gate, verbatim with the host files (`bench-hs22L-locked-u{5250,5419}` against
`bench-hs22-locked-u{2500,2709}`), reads `ppo-host-s22L` against `ppo-host-s22` when both have
landed.

## Gate B — the 512-step rollout (s512 vs s22)

The standard `gate1` protocol, unchanged: treatment s512 at 1,500 / 2,500, control s22 at 1,500 /
2,500 (benched), clone non-inferiority, `PYTHONHASHSEED=0`. **Question:** does a four-times-longer
trace (about 130–170 game turns of look-ahead) add to the stack — the reviewer's "true
long-horizon credit" lever taken one step further? **Expectation written before the data:** lever
2 alone (32 → 128 steps) read +0.017 [−0.004, +0.042] and helped late; s22 over r22 read +0.007
[−0.021, +0.035]; a further 4× is a guess in the same direction, and eight environments per rollout
make each update's data four times more correlated (fewer distinct games per update), which could
hurt. Either outcome is informative.

## Gate C — the host stack (host s22 vs hr22)

The standard `gate1` protocol at 1,500 / 2,500 against `bench-hr22-locked-u{1500,2500}.json`: the
replication, on the second platform and the full map corpus, of the cluster's s22-vs-r22 read
(+0.007, rising 29 → 33).

## Two instrument facts recorded today, before the data

1. **The frozen gate's interval is not bit-reproducible across processes.** `gate1.py` iterates a
   Python `set` of (map hash, seat) cells when it builds the per-cell vector the bootstrap
   resamples, and a set's order follows the string hash, which Python randomizes per process.
   Re-running the recorded verdicts under 40 hash seeds each: **hr22 — NOT_CONFIRMED 40 / 40**
   (lower bound −0.0035 three times, 0.0000 thirty-seven times); **r22 — CONFIRMED 40 / 40** (lower
   bound +0.0035 thirty-eight times, +0.0069 twice). The endpoints move by one quantum (1/288 =
   0.0035); **no verdict of record flips.** From now on every gate run sets `PYTHONHASHSEED=0`
   (written into the invocations above) so the printed interval is reproducible; the one-line
   repair (sort the cells before resampling) is offered to chatgpt_1 for acknowledgement together
   with the label rename — the file is not touched without it.
2. **The map-slice confound, found and fixed before it cost anything.** The launcher's default
   slices whatever `data/processed/maps.jsonl` holds on the day of `prepare`, and the daily
   collector (05:17 local) appends to that file — 31,088 → 31,863 maps overnight 09-01 → 09-02,
   append-only, verified byte for byte (the 09-01 corpus is exactly the first 31,088 lines of
   today's file, 69,696,037 bytes, the size the s22 manifest recorded). The **first launch of s22L**
   (04:54Z, operation `5f5afe7-4ade45ef-42e03e8-24076e87`) was prepared after that append and
   carried a 6,373-map slice against s22's 6,218: "the one changed field" was true of the trainer
   arguments and false of the payload. The job had not started (pending for 2.4 h); it was aborted
   at 07:15Z and relaunched with s22's slice shipped verbatim (`--maps
   yt_work/ppo/ppo-yt-s22/maps.jsonl`). Its first manifest is kept as
   `results/entropy-gate-0901/s22L-first-launch-0454Z-payload-manifest.json`. **Recipe amendment:**
   pin `--maps` to the control's file explicitly and compare the maps hash *inside the payload
   tarball* (`tar -xzOf … data/maps.jsonl | sha256sum`), not only `trainer_args`; host arms train
   from a pinned corpus copy under `/home/tarstars/nn-data/`, never from the live collector output.

## The host this morning

The host is a laptop. At 07:2xZ it was on battery (43 %, profile power-saver, all twenty cores held
at 800 MHz of 4,800): the two host arms ran four times slower than yesterday's (17 s an update
against 4.5) and were **stopped at update 21** so as not to drain the owner's battery — their runs
are deterministic and restart from the clone with nothing lost when the machine is back on mains.
No bench runs on battery either; every bench is four times slower there too. The bench of
s22@2,709 that finished at 06:40Z already carried 2.4× the usual think-time, so the machine came off
mains between 04:54Z and 06:40Z.
