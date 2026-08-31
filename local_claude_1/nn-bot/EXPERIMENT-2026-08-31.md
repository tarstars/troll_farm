# The self-play experiment, described in full — for a second opinion

2026-08-31, 05:0xZ. Written by the coordinator (`local_claude_1`) at the owner's request, as the
complete record of the neural-network line's training experiment: the data, the network, the
objective, every run, every number, what has been ruled out, and the two explanations left
standing. The intended first reader is `chatgpt_1`, asked for an adversarial review (the questions
are in §12); the owner reads it as the one self-contained description.

Everything here is on `main` or in `/home/tarstars/nn-data/` on the host; every claim carries its
file. Signed interface documents of record: `local_claude_1/nn-bot/OBS-PLANES.md` (the observation),
`local_claude_1/nn-bot/ENV-API.md` (the environment), the card
`coordination/tasks/20260829-nn-bot-way-b.md` (every ruling and every result, chronological).

## 1. The game and the goal

Troll Farm (CodinGame Spring Challenge 2026): two players, point-symmetric boards of width
2×height (height 8–11, so up to 11×22 = 242 cells), 300 turns, 50 ms a turn, one source file
under 100,000 characters. Trolls harvest fruit (1 point each), chop trees for wood (4 points a
wood at game end), mine iron, and buy ("train") new trolls with talents (speed, carry, harvest,
chop) paid in fruit and iron. The final score difference decides.

The line's goal (the owner's target of 08-29): a network-only bot that beats our best hand-written
bot ("the champion of record", ladder ≈ 18–21) and the "orchard 6" bot on the local bench —
≥ 60 % of 400 games each — exported as one Rust file. The approach is Way B: **clone the top four
players first, then improve the clone by self-play with the clone as an anchor.** The clone stage
succeeded. The self-play stage is the experiment described here, and so far it has not produced a
snapshot better than the clone; its failure pattern is the subject.

## 2. The training data (for the clone — the starting point of every run)

- **Source**: 748 recorded ladder games of the top four players (delineate, norxondor_gorgonax,
  MSz, Bubaptik's latest version), replayed turn by turn through our referee-exact engine
  (`local_claude_1/reconstructions/fits/reconstruct.py`; 0 disagreements with the referee's log on
  all 784 top-four games it was validated on).
- **Size**: **817,811 supervised decisions** = 224,400 plan rows (one per turn: which troll the
  player bought next, as one of 400, or "nothing") + 593,411 command rows (one per troll per turn).
- **Format** (`/home/tarstars/nn-data/dataset-v400-2026-08-30/`, checksums in `SHA256SUMS`):
  compact per-turn states (58 bytes a turn — troll positions/talents/cargo, tree kind/size/health/
  fruit/cooldown, both banks; `states-pilot.jsonl.gz`, 12.9 MB), the 748 boards
  (`maps-pilot.json`), and the labels (`labels-pilot.npz`). Observations are **not** stored; they
  are rebuilt at load time by the same Rust code the environment uses.
- **The plan vocabulary, 400 entries** (`v400-2026-08-29`, checked at every load): speed 1–4 ×
  carry 1–5 × harvest 0–3 × chop 0–4; index `(((s−1)·5+(c−1))·4+h)·5+chop`; entry 0 = "train
  nothing". delineate's own 144-way box was rejected because 267 of the top four's 1,725 recorded
  purchases fall outside it (Bubaptik buys speed-4 trolls in half of its purchases).
- **The command label**: one of 13 action kinds × 242 cells; a MOVE is labelled with the cell the
  troll actually **reached** that turn. The plan label is hindsight: the next troll actually
  bought. Rows between a purchase and the game's end with no later purchase are labelled "nothing"
  (67 % of plan rows).
- **The clone's training** (`train_clone.py`; log `/home/tarstars/nn-data/clone-2026-08-30-a/train.log`):
  4 epochs, batch 512, Adam lr 1e-3, cross-entropy on both heads, no held-out games on this first
  run (the bench is the judge). Final agreement with the teachers: plan 0.74, command 0.65 (MOVE
  41 % — one cell of up to 242 is the hard label; CHOP 90 %, DROP 97 %, HARVEST 93 %, PICK 15–23 %).
  Checkpoint `clone-pilot.pt`, sha `970097ed…`.

## 3. The observation (what the network sees at every decision)

A tensor of **104 planes × 11 × 22**, uint8-quantized (each plane a documented scale), always in
the *player-relative* frame (seat 1's board is rotated so "my shack" is always the same corner).
The full signed table is `OBS-PLANES.md`; the groups:

| planes | content |
|---|---|
| 0–6 | terrain: valid/grass/water/rock/iron, own and opponent shack |
| 7–15 | trees: kind (plum/lemon/apple/banana), size, health, fruit, cooldown |
| 16–37 | trolls: occupancy, talents and cargo per cell, own and opponent |
| 38–41 | walking distances to both shacks' doors; adjacency to iron/water |
| 42–58 | broadcast scalars: turn number, both banks (six resources each), both referee scores, troll counts |
| 59–71 | the standing train target and its costs/deficits (broadcast) |
| 72–87 | talent maxima and sums, own and opponent |
| 88–92 | distances to the nearest living tree of each kind and to a mining cell |
| 93–103 | cargo/fullness marks, the plan-accepted bit (97), the trained-last-turn latch (98), the **active troll** one-hot (99; all-zero = plan phase) |

**The plan sanitizer** (`plan_target_memory: "off-v2"`): planes 59–71 and 98 were identically zero
throughout cloning (the hindsight label would leak through them), so at every PLAN decision the
trainer and the shipped bot zero them. Troll decisions see all 104 planes untouched.

## 4. The network (`SpatialActorCritic(plan_head=True)`, `cgauto/train_level1_ppo.py`)

35,952 parameters, one shared body, three heads:

| part | structure | parameters |
|---|---|---|
| stem | Conv 3×3, 104→16, ReLU | 14,992 |
| tower | 4 residual blocks (two 3×3 convs of width 16 each, ReLU) | 18,560 |
| actor (troll commands) | Conv 1×1, 16→13 → 13×11×22 = 3,146 logits | 221 |
| plan (purchases) | per-candidate scorer: masked global pool (16) + 14 candidate features → MLP 30→32→1, one shared scorer over all 400 candidates; entry 0 has its own learned bias | 1,026 |
| critic (value) | masked global pool (16) → Linear 16→64 → tanh → Linear 64→1 | 1,153 |

The plan scorer's 14 per-candidate features: the four talents (scaled), the four costs
(`troll count + talent²`, /48), the four deficits (`max(cost − bank, 0)`, /48), an affordable
flag, and a "matches the standing target" flag whose weight column started at zero (so the clone's
plan logits could not move through it at the PPO hand-over). Both policy heads write into one
3,146-wide logit row (plan logits in columns 0–399 under the plan mask), so sampling,
log-probability, entropy and the PPO ratio are one code path. Illegal actions get
`finfo(float32).min` before the softmax.

delineate's own network, for scale: ~101k parameters, 104 planes, per-troll sequential inference —
ours is the same shape at a third of the size.

## 5. The environment and the decision loop

`rust/src/rl_full.rs` + `cgauto/rl_full_env.py`: the full 300-turn game, 128 boards stepping
together, real ladder maps. Parity-proven: 1,000 self-play games replayed through an independent
rules copy with 0 disagreements and 0 illegal commands; reproduced by a second agent.

A turn is a sequence of **mini-steps**: first the PLAN decision (400-way, masked; the only mask
rule is that entry 0 is always available), then one decision per own troll in id order (13×242,
masked to legal), then the turn executes for both players at once. The opponent of each board is
drawn from a weighted pool of eight: our hand-written bots (`secure_orchard`,
`norxondor_native`, `legend_field_proxy_v2`, `gold_elite_adaptive`, `script_boss`, `mybot_boss4`),
a frozen copy of the learner (`python_frozen`, refreshed every 100 updates), and
**`champion_exact`** — an in-process copy of the champion proven move-for-move identical to its
submitted file on 200/200 recorded games and all 49,945 turns.

**TRAIN dry run**: a purchase command is emitted only if the environment's own affordability check
passes — the same rule in training, in the bench and in the shipped file.

## 6. The reward and the estimator

- **Reward**: the referee's end-score difference (own − opponent), with banked wood valued at
  `--end-wood` per unit at game end, ×`reward_scale = 0.02`, paid **once per turn on the mini-step
  that executes the turn** (earlier mini-steps of the turn carry 0). Optional dense shaping
  `--wood-shaping` (0.5 point per wood banked, on by default) was **off** in every run after D.
- **GAE**: within a turn's mini-steps, discount 1 and trace 1 (they are one decision); across turn
  boundaries, discount `γ` and trace `γ·λ`. Defaults γ 0.997, λ 0.95. Advantages are normalized
  per minibatch (mean/std).
- The audited subtlety (found 08-30 20:02Z): with λ = 0.95 the per-turn *policy credit* trace is
  `γ·λ` ≈ 0.95 for every γ we tried, so the γ sweep (0.997/0.999/1.0) changed the **value target's**
  horizon, not the policy's credit horizon. At 50 turns the terminal signal reaches a move with
  weight ≈ 0.077. A true undiscounted-credit run — (γ, λ) = (1, 1) — has not been run.

## 7. The trainer (`train_ppo_full.py`; the full config of the last run, from its own start record)

PPO, clip 0.2, 2 epochs over the 128×32 = 4,096-decision rollout in minibatches of 1,024;
entropy bonus 0.01; value coefficient 0.5; global gradient-norm clip 0.5; Adam lr 2.5e-4,
linearly annealed; target-KL 0.03 (early-stops an update's epochs). **The anchor**: a KL penalty
toward the clone's distribution on every decision, coefficient 0.1 decaying linearly (to 0.05 over
100 M decisions in the remedy runs; to 0 over 50 M in run D). **The critic warm-up**
(`--critic-warmup-updates 300`): the first 300 updates train only the two critic linear layers —
every other tensor is bit-frozen — because the clone's value head starts as noise. **The actor
learning-rate scale** (0.3 in the remedy runs): everything that is not the critic learns at
0.3×lr. The convolution trunk counts as *policy* (a value gradient through it would move decisions
even with the heads untouched) — which is also why the warm-up freezes it.

**The staged scope** (`--train-scope plan-critic`, the winner's recorded stage 4, built 08-30
21:37Z after four audit objections were folded in): stem, tower and the troll-command head are
bit-frozen for the whole run; troll rows execute the frozen policy's **masked argmax** (exactly
the shipped decoding, no RNG draw) and contribute nothing to the policy loss, entropy or anchor;
PLAN rows keep sampling, and the PPO loss, advantage normalization, entropy and anchor are
computed **over PLAN rows only**; the value loss uses all rows; the pre-clip plan/critic gradient
norms and the joint clip multiplier are logged. The default `all` scope is proven bit-identical to
the pre-change trainer by a matched-seed run (29/29 tensors, 29/29 optimizer entries).

## 8. The measurement (the bench — the only number that counts)

`bench.py`: the checkpoint plays the champion of record's **actual submitted file** (sha
`0e92f8fa…`) through the real referee harness on 24 real ladder maps, once on each seat = 48
games; plan and commands decoded by **masked argmax** (the shipped decoding); every game checked
for illegal commands (always 0), timeouts (0), loops, end reasons; all 48 games saved turn by
turn. The clone's baseline: **9 wins of 48, 133.8 : 186.2** (4 on seat 0, 5 on seat 1). A
random-legal policy scores 13.5 points on this bench. One bench's noise: ±2 wins (binomial,
p≈0.19, n=48 → σ≈2.7 points of score).

**The decoding factorial** (the clone, same maps/seeds): plan×command argmax/argmax **9 / 133.9**;
sampled/argmax **8 / 133.5**; argmax/sampled **3 / 109.2**; sampled/sampled **4 / 103.4**. The
command decoding carries the whole gap; sampled play wanders (329 moves a game vs 253). Training
rolls out sampled play — so a run's own practice win rate (also 60 % weak opponents in the mixed
pool) can rise while argmax play falls, and did.

## 9. The runs and their results

All runs start from the clone (`970097ed…`), anchor to it, and are benched at every 500 updates
(1 update = 4,096 decisions). "Wins" = of 48 vs the champion's file, argmax play.

| run | scope | pool | γ | shaping | warm-up | lr scale | anchor | wins by update (500/1000/1500/2000/2500) | points |
|---|---|---|---|---|---|---|---|---|---|
| A (04:45Z) | all | mixed weak + frozen | 0.997 | 0.5 | — | 1.0 | 0.1→0 | @1000: **2** | 87:183 |
| C (08:39Z) | all | mixed weak | 0.997 | 0.5 | — | 1.0 | 0.1→0 | @250: **3** | 107:177 |
| D (09:42Z) | all | champion 4/10 + mixed | 0.997 | 0.5 | — | 1.0 | 0.1→0 | **3, 4** | 108:184, 82:169 |
| F2 (14:45Z) | all | champion 4/10 + mixed | 0.999 | 0 | 300 | 0.3 | 0.1→0.05 | **5, 7, 2** | 124, 132, 95 |
| G (17:45Z) | all | champion only | 0.999 | 0 | 300 | 0.3 | 0.1→0.05 | **5, 4** | 134, 107 |
| H (19:15Z) | all | champion only | **1.0** | 0 | 300 | 0.3 | 0.1→0.05 | **3, 8, 2** | 113, 133, 109 |
| I (22:55Z) | **plan-critic** | champion only | 0.999 | 0 | 300 | 0.3 | 0.1→0.05 | **9, 10, 9, 6, 5** | 129, 131, 128, 124, 122 |

The per-game activity counts (the collapse's signature; the clone's row for contrast):

| snapshot | chop | harvest | plant | drop | move | purchases (games of 48) |
|---|---|---|---|---|---|---|
| clone | 94 | 38 | 25 | 66 | 253 | 44 |
| D @1000 | 71 | 17 | 14 | 46 | 210 | 26 |
| F2 @1500 | 81 | 23 | 20 | 42 | 266 | 42 |
| G @1000 | 96 | 23.5 | 22 | 51 | 236 | 38 |
| I @1000 | 90 | 39 | 24 | 68 | 249 | 44 |

Run I's practice telemetry, uniquely, tracked its bench (win rate 17.7→20.9 % vs the bench's
19–21 %; margin −48 to −50) because its executor is the shipped argmax and its opponent the
champion alone. Its plan entropy rose 0.90 → 1.35 as the anchor decayed, and the drift below the
bar (6, 5) came exactly then. H's value fit collapsed under the undiscounted target (explained
variance 0.25 vs 0.6–0.97 elsewhere).

**In flight** (the cluster, results ~19:00–20:00Z 08-31): a2 = run-D recipe at 60 M decisions
(the long-horizon answer; its killed first attempt's telemetry reached practice 29 % / margin −43
at 48 M, still climbing — soft numbers, pool-inflated); e2 = F2's recipe at 60 M; **i2 = run I's
recipe with the anchor pinned at 0.1 for the whole run** — the direct test of the leash-decay
explanation.

## 10. What has been ruled out, with the evidence

1. **The opponents' pool** as the sole cause — G eroded against the champion alone.
2. **The dense wood shaping / end-wood mispricing** — off in every run after D; the shape remained.
3. **The value-target horizon (γ)** — 0.997 / 0.999 / 1.0 all collapse; γ 1.0 only makes the
   critic's fit worse. (The *policy credit* horizon was never actually varied — see §6.)
4. **The untrained critic alone** — the 300-update warm-up (F2, G, H, I) delays the dip, does not
   prevent the collapse.
5. **The argmax/sampled measurement artefact** — sampled play degraded alongside argmax play
   (F2 @1500 sampled: 0/48).
6. **Trainer bugs of the first morning** — the per-troll reward decay, the plan-label leak planes,
   the plane-98 latch: found by audit, fixed, and the shape persisted after the fixes.
7. **An environment hole** — the parity gates (1,000 games, 0 disagreements) and per-bench checks
   (0 illegal commands ever) stand; the erosion also shows in ordinary play statistics, not in
   rule exploitation.

## 11. The two explanations left standing

**(a) The value gradient bends the policy through the shared trunk.** After the warm-up,
`value_coef · value_loss` backpropagates through stem+tower (which the optimizer counts as
"policy", at 0.3×lr — reduced, not removed). The value target is hard (a ±100-point margin,
explained variance 0.6–0.97 at best), so this flow is large and noisy. Consistent with: every
full-parameter run collapsing; the only trunk-frozen run (I) never collapsing; the hardest-target
run (H) dipping deepest. Not yet directly measured — the instrument (`grad_decompose.py`,
claude_1, 22 tests) separates the four objectives' gradients per network part and applies a
value-only counterfactual step; one reviewer correction is pending, then it runs on the clone and
on G/H @500.

**(b) The anchor is the only thing holding the clone's behaviour, and it fades.** Wins are ~2 %
of champion games, so the clone's habits are never reinforced by return — only held by the KL
penalty, which measures the *sampled* distribution (argmax choices can walk within a small KL).
Consistent with: run I holding the bar exactly while its leash was ≥ ~0.09 and drifting as it
approached 0.05; the plan entropy rising in step. Directly tested by i2 (leash pinned at 0.1)
tonight.

These two are not exclusive; the staged scope + a non-fading leash addresses both at once, which
is what i2 is.

## 12. The questions for the reviewer

1. Is the diagnosis complete? Name any cause consistent with all of §9–10 that §11 misses —
   e.g., PPO's advantage normalization over a ~98 %-loss stream; the entropy bonus (0.01) as a
   persistent softening force against a distilled (near-deterministic) policy; the target-KL 0.03
   interacting with the anchor; Adam moment staleness across the warm-up boundary; the reward
   scale 0.02 against a value head of 1,153 parameters.
2. Is the (γ, λ) accounting in §6 right, and is a (1, 1) run worth cluster time, given §10.3?
3. The staged scope (§7): any remaining semantic hole after the four folded objections — anything
   that still trains a different problem than "purchases for the argmax executor on end score"?
4. The bench (§8): 48 games at ±2 wins is the gate for every decision here. Should the per-500
   reads move to 96 or 144 games (cost: ~20–40 min each), and should the run-of-record rule
   (two consecutive reads ≥ the clone) change?
5. The next lever if i2 holds the bar but does not climb: a joint fine-tune at ≤ 0.05×lr from
   I @1000 (the winner's stage 5), a separate value trunk, or reward reshaping (e.g., margin
   clipping, win-bonus) — rank them, or name a better one.
6. Anything in the data or the clone (§2–4) that caps the ceiling — e.g., the 400-way vocabulary,
   the hindsight "nothing" majority (67 % of plan rows), MOVE labelled by reached-cell — worth
   fixing *before* more self-play compute.

## 13. Reproduction

Everything below runs from the repo root on the host, `PYTHONPATH=.`, python
`/home/tarstars/nn-venv/bin/python` (3.11, torch 2.13 CPU), library
`rust/target/release/libtroll_farm.so`.

- One training run (run I's exact command is the `start` record's `argv` in
  `/home/tarstars/nn-data/ppo-2026-08-30-i/train.log`):
  `local_claude_1/nn-bot/train_ppo_full.py --env full --maps data/processed/maps.jsonl
  --initial-checkpoint <clone> --anchor-checkpoint <clone> --frozen-checkpoint <clone>
  --opponent-weights '{"champion_exact":1}' --train-scope plan-critic --gamma 0.999
  --wood-shaping 0.0 --end-wood 4.0 --critic-warmup-updates 300 --actor-lr-scale 0.3
  --anchor-coef 0.1 --anchor-coef-final 0.05 --anchor-decay-steps 100000000 …` (the full dump: §7).
- One bench: `local_claude_1/nn-bot/bench.py --maps local_claude_1/third-troll/smoke-maps-seed0.jsonl
  --bot cgauto/submissions/candidate-champion-denial-off-v6-instrument.rs --games 0
  --policy network --checkpoint <pt> --plan-decoding argmax --both-seats --out … --replays …`
- Read any game: `bench.py --read <replays.jsonl> --game N`.
- The tests: `tests/test_train_ppo_full.py` (51), `tests/test_rl_full_env.py` (7),
  `tests/test_yt_ppo_launcher.py` (19), the bench's `--self-test` (8 checks).
- The run directories (log + snapshots every 250 updates + all benches with games):
  `/home/tarstars/nn-data/ppo-2026-08-30-{a,b,c,d,e,f,f2,g,h,i}/`.
