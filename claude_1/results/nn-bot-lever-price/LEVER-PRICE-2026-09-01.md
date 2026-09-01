# Pricing step 5's levers before they cost cluster time — 2026-09-01

**Task:** 20260829-nn-bot-way-b (Track N, THE GOAL's step 5) · **by** claude_1 · **stamp**
2026-09-01T16:20:28Z · no platform action, no cluster, no training, nothing launched.

## The question

The Gate 1 verdict acquitted the entropy bonus, and the credit measurement of the same morning
gave the programme its live suspect: **observed reward supplies 2.32 % of the plan head's
learning signal and the critic's own values supply 97.68 %; the trace reaches a real game ending
on 1.8 % of rows.** The fix menu the owner is choosing from has four levers, and the first two
both claim to put more real signal inside the credit window:

1. slide the payoff into the turns — `wood_shaping + end_wood`, keeping the sum at 4;
2. look further ahead — `--rollout-steps` 32 → 128 with `--num-envs` 128 → 32.

Nothing in the record says **how much** either one actually moves it. Each costs a cluster arm
plus a 144-cell gate to find out. This measures both offline first.

## What was done

One rollout was collected with **the clone itself** (`clone-pilot.pt`, sha `970097ed…` — the same
clone both entropy arms started from), then the *same recorded action sequence* was replayed in a
fresh environment under each other reward split, and the *same buffer* was re-cut into windows of
32 and 128 mini-steps. So every number below comes from **one set of games**: the splits and the
window lengths are the only things that move.

This is sound because the reward split is an output of the simulator and not an input to it. That
is not assumed — it is checked: the replays reproduce the collection's state hashes, turn
boundaries and episode endings exactly (`identical_game: true` for every split, in the JSON).

The decomposition is not re-implemented. The instrument loads the trainer and calls its own
`compute_gae` and `rollout_credit_telemetry`, so these numbers and the Gate-0 numbers are made by
the same code. `--reward-credit executing` is applied exactly as the trainer applies it.

**Sample:** 64 environments × 1,024 mini-steps after an 896-mini-step burn-in (so the environments
have staggered rather than all sitting at turn 0) = **65,536 rows, 21,630 turns, 88 episode
endings**, opponent `champion_exact`, `--train-scope plan-critic`, γ 0.999, λ 0.95.

## What it found

### Lever 1 — the wood split: 20× more rows that see any reward at all

| split | rows carrying observed reward | share of rows | summed reward magnitude |
|---|---|---|---|
| **0 + 4** (what every run of record used) | **88** | **0.13 %** | 6,592 |
| 0.5 + 3.5 (the environment's own default) | 1,782 | 2.72 % | 6,661 |
| **2 + 2** (the coordinator's recommendation) | **1,781** | **2.72 %** | 7,204 |

The first row is the finding, and it is sharper than the 97.68 % because it needs no critic to
state: **under `0 + 4` the only rows in the entire buffer that carry any observed reward are the
88 that are episode endings.** 99.87 % of the rows the trainer learns from are taught by the
critic alone, because there is nothing else there to teach them.

**The coverage is bought by turning shaping on at all, not by how large it is.** `0.5 + 3.5` puts
reward on 1,782 rows and `2 + 2` on 1,781 — the same rows, the wood deliveries. The choice
between 0.5 and 2.0 changes what each delivery is worth, not how many rows stop being blind.

The summed absolute magnitude rises 9.3 % from `0+4` to `2+2`. Two things contribute and this
measurement does not separate them: the spent-wood bias the coordinator already flagged (wood
delivered then spent on training collects the immediate part and never reaches the final score),
and plain arithmetic (one signed lump split into signed pieces need not preserve absolute
magnitude). It is not evidence that the split is *not* value-preserving in the sense meant.

### Lever 2 — the rollout length: 4.3× more traces that reach a real ending

| window | plan rows whose trace reaches a real ending | troll rows |
|---|---|---|
| **32 mini-steps** (the runs of record) | **1.46 %** | 1.71 % |
| **128 mini-steps** | **6.21 %** | 6.65 % |

Identical across all three splits, as it must be — same games.

**This is also the calibration.** The measurement of record puts that fraction at **1.8 %** on
real training runs at the same window size; this collection, from the clone on a different sample,
puts it at **1.46 %**. The instrument is reading the same quantity at the same scale, so the 4.3×
it reports for the longer window is trustworthy.

### The two levers do not compete

They act on different rows. Lever 1 puts reward on the 2.6 % of rows that are wood deliveries,
scattered through the game. Lever 2 extends how far a trace reaches, which only helps the rows
near an ending. Neither one subsumes the other, and running one first costs nothing that the
other needs.

## What this measurement cannot say

**The share-of-signal number is not comparable to the 2.32 % of record, and is not reported as a
headline.** The reason is measured, not guessed: the clone's value head returns |V| ≈ 0.79 on
average (max 1.42) while a terminal reward is about 75. The runs of record had a critic warmed up
for 300 updates, whose outputs are on the scale of the returns, which is exactly why its component
dominates there. Priced at the clone the ratio inverts, and it would say nothing about a run in
progress. Everything above is deliberately critic-independent: counts of rows, shares of rows, and
trace reach — none of them depend on what the value head happens to output.

Getting a comparable share would need a warmed-up critic on this host, which is a training run,
which is what the arm itself would do. That is the reason to run the arm, not a substitute for it.

**Other limits.** One 64-environment sample per seed, one opponent (`champion_exact`), and the
clone rather than a mid-run policy — a policy that delivers wood at a different rate would move
the 2.72 %. The burn-in staggers the environments but does not make them a uniform sample of a
long run's episode phases.

## Replication — three seeds

Both headline factors were re-measured on two further seeds under identical settings
(`lever-price-seed910.json`, `lever-price-seed911.json`). Every replay reproduced its
collection's games exactly in all three runs.

| seed | endings | reward rows `0+4` | `0.5+3.5` | `2+2` | lever 1 factor | traced w32 | traced w128 | lever 2 factor |
|---|---|---|---|---|---|---|---|---|
| 909 | 88 | 88 | 1,782 | 1,781 | **20.2×** | 1.46 % | 6.21 % | **4.3×** |
| 910 | 82 | 82 | 1,671 | 1,671 | **20.4×** | 1.46 % | 5.79 % | **4.0×** |
| 911 | 84 | 84 | 1,764 | 1,764 | **21.0×** | 1.10 % | 4.85 % | **4.4×** |

Two things survive the replication exactly rather than approximately. **In every seed the number
of reward-carrying rows under `0+4` equals the number of episode endings** (88/88, 82/82, 84/84) —
the claim that nothing but an ending pays under that split is not an estimate. And in every seed
`0.5+3.5` and `2+2` cover the same rows to within one. The trace-reach figure at the window of
record (1.46 %, 1.46 %, 1.10 %) sits beside the 1.8 % of record in all three.

## What it suggests, for the owner's choice

Nothing here decides anything; the choice is the owner's and the ranking beside it is
chatgpt_1's. As evidence:

- Lever 1 is confirmed to do what it claims, and the size of the effect is large: **0.13 % → 2.72 %
  of rows carrying reward, a factor of 20.** The recommendation to run it first is supported.
- Lever 2 is also confirmed, and its effect is real but smaller on this axis: **1.46 % → 6.21 %**,
  a factor of 4.3.
- If the split is chosen, the coverage argument does not favour `2 + 2` over the environment's own
  `0.5 + 3.5`; only the per-delivery magnitude differs. If a reason to prefer `2 + 2` exists it is
  the size of the immediate signal, not how many rows receive it.

## Reproduction

At the commit this report is pinned to on `agent/claude_1`, with `/home/tarstars/venvs/nn-bot/bin/python`
(NumPy 2.4.6, CPU PyTorch 2.13.0):

```sh
nice -n 19 /home/tarstars/venvs/nn-bot/bin/python claude_1/nn-bot/lever_price.py \
  --clone local_claude_1/nn-bot/results/clone-2026-08-30-a/clone-pilot.pt \
  --maps local_claude_1/nn-bot/maps-slice-1000.jsonl \
  --num-envs 64 --seed 909 --burn-in 896 --steps 1024 \
  --split 0+4 --split 2+2 --split 0.5+3.5 \
  --window 32 --window 128 --threads 8 \
  --out claude_1/results/nn-bot-lever-price/lever-price-2026-09-01.json
```

Runs in about four minutes on this host at nice 19. The tests:

```sh
/home/tarstars/venvs/nn-bot/bin/python -m pytest tests/test_lever_price.py -q   # 8 passed
```

Every test was written before the code it tests and watched to fail first. The one that matters
most is `test_window_bootstrap_is_the_value_of_the_step_after_the_window`: a re-cut short window
must bootstrap from the value just past **its own** edge, not from the long buffer's edge, or
every short window would be handed the long window's information and lever 2 would be understated.

- instrument `claude_1/nn-bot/lever_price.py` sha256 `6bd6546525d7cdc8…`
- result `claude_1/results/nn-bot-lever-price/lever-price-2026-09-01.json` sha256 `3d9de52e4805e6af…`
