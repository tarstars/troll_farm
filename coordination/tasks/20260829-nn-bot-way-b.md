# Card 20260829-nn-bot-way-b — the neural-network bot, Way B (clone first, then PPO)

Born 2026-08-29 13:3xZ from the owner's decision on `local_claude_1/nn-bot/ANALYSIS-2026-08-29.md`:
**"1) open line 2) B 3) I'll check"** — the line is open (ledger `docs/CONSTRAINTS.md`, the entry
after "★ FINAL for the learned-selector question"), Way B, and the owner judges the clone's games.
Board Track N, row N-2. Coordinator: `local_claude_1`. Builders: `codex_1` (Phase 1), `claude_1`
(Phase 2's dataset, bench and trainer). Training runs on the host (20 cores, no GPU).

**Plain words for the owner.** We build a bot whose every command comes from a small neural network
over the board — delineate's construction, the #1 player. First the network is taught to copy the
top four players' moves from their recorded games (the clone); then it improves by playing in our own
engine against our bots and against itself (PPO), with the clone kept as an anchor so it does not
forget what it copied. Each phase below has a "done" and a "dead" condition and a budget, as every
card here does. Nothing touches the platform until Phase 4, and not while codex holds the ladder.

## The five phases

| phase | what | who | budget | done | dead |
|---|---|---|---|---|---|
| 0 | the runtime on the host: Python 3.11 + CPU PyTorch via `uv`; one July trainer re-run small; export through the int8 kernel; a game in the bench | coordinator (host) | 1–2 days | **DONE 2026-08-29 14:2xZ** (owner "wifi" 14:0xZ): `/home/tarstars/nn-venv` (Python 3.11.15, torch 2.13.0+cpu, numpy 2.4.6, 825 MB); `cargo build --release --lib` in the worktree; `pretrain_level1_bc.py --curriculum-level 1 --samples 4000 --num-envs 20 --chunk-steps 10 --epochs 1 --minibatch-size 200 --eval-episodes 1000 --threads 8` → checkpoint in 35 s (accuracy 25 %, a smoke); `export_d11_actor.py` → int8 payload 34,872 B; `generate_d11_actor_rust_k2.py` → kernel 55,768 B; `generate_d11_live_actor_v7.py` → live bot 69,608 B; `rustc -O` compiles; `probe.py 7b515d6db8085355 --arm <live.rs>` plays a legal 300-turn game (the untrained net waits every turn; score 21) | — |
| 1 | **the full-game environment** (below) | codex_1 | 6 days, one message | 1,000 self-play games, no illegal command, replay parity 1,000/1,000, the tests pass | parity not reachable in budget |
| 2 | **the dataset, the bench, the clone** (below) | claude_1 (dataset, bench, trainer); coordinator trains on the host | 7 days for the dataset + bench + trainer; the training run 1–2 days | the clone plays 24/24 real maps to the end against the champion's binary; the owner reads its games | after the budget the clone cannot play a whole game → Way A's stages from scratch, July's levels as the base |
| 3 | PPO from the clone with the clone anchor, real maps, the training pool (the linked strategies + frozen copies of the policy), a fixed bench every few days against the champion's and orchard 6's compiled files | coordinator (host); claude_1 reproduces the bench numbers | 2–4 weeks | ≥ 60 % vs the champion and vs orchard 6 on 400 games each, positive margin, three gates in a row | no gain over the clone after 2×10⁸ turn-steps, or the policy exploits an engine hole (replay parity fails on its games) |
| 4 | ship: int8 export with the plan head, the parity bed (Python network vs Rust kernel, move for move), < 100,000 characters, ≤ 15 ms a turn here, the readable diff, codex_1's reproduction, the owner's prediction, one hour, one reading — after codex is done with the platform | coordinator; codex_1 reproduces | 3 days + one ladder hour | the reading on the ledger with its 160 games read | over the size or time limit with nothing left to cut |

## Fixed design (what both builders build against)

**The observation — delineate's 104 planes, not July's.** July's `rust/src/rl_level1.rs` builds a
104-plane tensor of its own layout (a selected troll, a fixed target, Level-1 progress; only 72 of its
planes are generic — `docs/CONSTRAINTS.md`, "H10a cannot reuse the Level-1 104-channel tensor
verbatim"). The new environment implements **the plane list from delineate's own description**,
`local_claude_1/reconstructions/sources/delineate-gist.github.com-2026-05-25.md` lines 68–84 (cell type
one-hot 1–6; tree kind/size/health/fruits/cooldown 7–15; troll occupancy 16–17; per-cell own/opponent
troll stats and cargo 18–37; shack distances and iron/water adjacency 38–41; broadcast globals 42–58;
the current train target with costs and deficits 59–71; aggregate talents 72–87; nearest-tree/mine
distances 88–92; carried/free capacity 93–96; mini-step flags including the **active troll** 97–99;
"full" flags 100–103; plane 0 = the valid-cell mask), written down as a table in
`local_claude_1/nn-bot/OBS-PLANES.md` **before** coding, with the quantization of every plane (u8,
`round(255·v/scale)`, the scale per plane in the table). Where the gist is silent, choose something
sensible and write it in the table — the author said "anything sensible would work". The board is
always presented **player-relative**: the policy's seat is seat 0, the map rotated 180° when it plays
seat 1 (the maps are point-symmetric), so one network plays both seats.

**The actions.** Two heads. (a) The per-cell head: 13 planes × 11 × 22, index `plane·242 + y·22 + x`,
the July decoding kept (`rl_level1.rs:490–508`): 0 = MOVE to that cell (the referee walks up to
`speed` steps toward it; MOVE to the troll's own cell is WAIT), 1 HARVEST, 2 CHOP, 3 DROP, 4 MINE (cell
ignored), 5–8 PLANT plum/lemon/apple/banana, 9–12 PICK plum/lemon/apple/banana. Masks as delineate's
legality: MOVE legal on any walkable cell with a path from the troll (not only July's plant/shack/iron
cells); the rest under the game's preconditions (July's mask code is the start). (b) The train-plan
head: 144 entries = speed 1–3 × carry 1–4 × harvest 0–2 × chop 0–3 in a fixed order, entry 0 repurposed
as "train nothing"; masked: harvest 0 and chop 0 together illegal, harvest > carry illegal, and any plan
whose cost exceeds the bank this turn is still *legal* (the plan is a target the trolls collect toward;
the TRAIN command is emitted the turn it becomes affordable — delineate's L2 rule). The chosen target
is written back into planes 59–71.

**The mini-steps (one env step = one decision).** At the start of a turn: step A, the plan decision
(the 144-way head; the observation's mini-step flags mark "plan phase"); then step B_i for each own
troll in id order (the 13-plane head; the active-troll flag marks the troll; earlier trolls' chosen
commands are visible through the "full" planes and a reserved-cell mask so two trolls do not take one
cell — no beam search in the environment; delineate's beam is an inference-time nicety for Phase 4);
then the turn executes for both seats. The opponent's commands come from the pool (below). Rewards are
paid at the turn's end to every mini-step of that turn (the same scalar).

**The reward.** `score_diff` at the end of the game (own score − opponent score, wood counted 3.5 at
the end as delineate did) plus, per turn, +0.5 for every wood the policy's trolls deposit. Episode =
300 turns or the referee's early end. Both shapings are flags (`--wood-shaping 0.5`, `--end-wood 3.5`)
so Phase 3 can turn them off.

**The maps — real, never generated.** `data/processed/maps.jsonl` on the host (24,973 real ladder
maps with exact initial trees); a 1,000-map slice for the VM at `local_claude_1/nn-bot/maps-slice-1000.jsonl`
(cut by the coordinator, every 25th map). The starting inventories are drawn 2–10 per slot as the
referee does (seeded). The four board sizes are mixed as they come.

**The opponent pool (training).** Linked strategies from `rust/src/strategies/mod.rs` and the
`rl_macro.rs` bank: `SecureOrchardBot` (the resident lineage, with the sacred source's denial rule),
`MyBot` (**a model of the Arena's Boss 4 — not a champion mirror**; codex_1's read 2026-08-29),
`NorxondorNative`, `LegendFieldProxyV2`, `GoldElite::adaptive`, `ScriptBoss`; **no linked strategy
equals the denial-off champion — the champion's and orchard 6's compiled files are the bench's
opponents and the gates, never the training pool's** (an exact linked champion is a separate, optional,
reviewed change); plus **self-play against frozen copies of the policy** (the environment accepts an
opponent that is "a policy checkpoint" by taking the opponent's actions from Python: the Python side
runs the frozen network for seat 1 through the same observe/step calls — the env exposes both seats'
observations when asked). A per-env opponent id is sampled from a weight table.

**The bench (truth for gates).** Not the training env: the July Python referee harness
(`claude_1/pipeline/fuzz_panel.py` / `claude_1/banana-restoration-r2/semantic_harness.py`, which
compiles a single-file bot with `rustc` and drives it over pipes) with **one seat played by the
PyTorch network** and the other by **the champion's actual submitted file**
(`cgauto/submissions/candidate-champion-denial-off-v6-instrument.rs`, and orchard 6
`candidate-orchard6-v6-instrument.rs`), on the 24 maps of `local_claude_1/third-troll/smoke-maps-seed0.jsonl`
for the owner's read and on 400 seeded maps (both seats) for gates. Output: per game own/opponent
score, win, trolls trained (talents, turn), timeouts, illegal commands, loops (a troll on the same
cell 30 turns with cargo it could deposit); a summary table; the games saved as replays the owner can
read turn by turn with `local_claude_1/third-troll/dance_read.py`-style output.

**The dataset (Phase 2).** From the exact reconstruction `local_claude_1/reconstructions/fits/reconstruct.py`
(snapshot schema at lines 136–145: `turn, inv[2][6], units[id,player,x,y,ms,cc,hp,chop,carry[6]],
plants[type,x,y,size,health,fruits,cooldown]`; both seats' commands via `Reconstructor.commands(t)`;
the games index `player_games.json` — now in the repo at `local_claude_1/reconstructions/fits/player_games.json`,
`decision_tables.py:32` to be re-pointed). One implementation of the plane builder, in Rust, exposed
to Python as `tf_full_obs_from_state(json_state, seat, active_troll, phase, plan) → u8[104·242]` so the
dataset and the environment cannot drift (a test compares the two on 1,000 states). Rows: for every
turn of every top-four game and both seats: one plan row (label = the talents of the **next TRAIN
that player actually issues**, or 0 if none before the end; from `fits/tables/<player>_turns.jsonl.gz`
field `train` or recomputed) and one row per own troll (label = the flat index of the command the
player gave that troll that turn; a MOVE label is the **cell the troll actually reached**, from the
next snapshot — the referee's step, not the intent). Sharded `.npz`: `obs u8[N,104,11,22]`,
`mask u8[N,13,11,22]` or `plan_mask u8[N,144]`, `label i64[N]`, `meta` (game, turn, seat, player,
troll id). Players: delineate, norxondor, MSz, Bubaptik (the 784 validated games; Bubaptik's latest
version tagged separately); seat-swap augmentation by the 180° rotation. Sizes and counts reported.

**The network (Phase 2).** `SpatialActorCritic` from `cgauto/train_level1_ppo.py:140` (3×3 stem, four
residual blocks of width 16, ≈35 k weights) plus the plan head: masked global pooling → a 64-unit
layer → 144 logits — **added as a constructor flag defaulting to off** (`SpatialActorCritic` is the
one class every trainer and the exporter import, `train_level1_ppo.py:140`; the exporter compares
state-dict keys against the default constructor, so July's checkpoints must keep exporting). The export path (`cgauto/export_d11_actor.py`, `generate_d11_actor_rust_k2.py`)
hard-codes the July topology and rejects new keys — Phase 4 extends both; Phase 2 only needs the
Python network. The trainer: `pretrain_level1_bc.py`'s masked cross-entropy, now over the sharded
dataset (two losses, one per head), held-out by game; report per-verb accuracy **and then judge by the
bench only** (fit statistics anti-predict transfer — `docs/CONSTRAINTS.md`).

## Interfaces to freeze (codex_1 writes them first, in `local_claude_1/nn-bot/ENV-API.md`, coordinator signs)

C ABI in the existing `cdylib` (`rust/Cargo.toml`, `libtroll_farm.so`), prefix `tf_full_`:
`create(num_envs, seed_base, maps_path, opponent_weights) → handle`, `destroy`,
`observe(obs u8[n·25168], masks u8[n·3146], plan_masks u8[n·144], phase i32[n], seat_view i32) → n`,
`step(actions i32[n], …) → n` with the same terminal arrays as `tf_level1_step` plus `score_own`,
`score_opp`, `trained[n·4·4]`; `obs_from_state(json, …)`; `decode_action(idx, …) → command string`;
`opponent_observe/step` for the frozen-policy opponent. Python: `FullVecEnv` in
`cgauto/rl_full_env.py` mirroring `Level1VecEnv` (`cgauto/rl_level1_env.py:42–161`), NumPy buffers,
context manager. Tests under `tests/` in the repo's style: decode/encode round trip on every legal
index; mask legality against the engine (a random legal action is never rejected by `step`, 10,000
draws); replay parity (an env game's recorded commands replayed through `sim/engine.py` give the same
states every turn, 200 games); a speed line (turn-steps per second, 20 threads) in the report.

## Rules of the card

- Real maps only; no generated maps in any training or evaluation number.
- Held-out accuracy is reported, never used as a gate; the bench decides.
- Every number in a handoff comes with the command that produced it and the commit it ran at; the
  other builder reproduces before the coordinator accepts (two review rounds, WORKING-RULES).
- No platform action by anyone on this card until Phase 4, and none while codex holds the ladder.
- No download over ~50 MB on the host without the owner's WiFi word; the VM's own network is free.
- No deletion or move of data; the coordinator asks the owner what may move to the USB archive.

## Log

- 2026-08-29 13:3xZ: born; the owner's decision recorded in `docs/CONSTRAINTS.md` and `coordination/GOAL.md`;
  the games index `player_games.json` copied into the repo; the 1,000-map slice and a 10-game raw-replay
  slice cut. The transport allows one open ack-requiring handoff per task, so each phase has a sub-card:
  `20260829-nn-bot-way-b-env.md` (codex_1, Phase 1) and `20260829-nn-bot-way-b-dataset.md` (claude_1,
  Phase 2); charters `20260829T134459Z-…-env-handoff.md` and `20260829T134500Z-…-dataset-handoff.md`,
  pinned to `d20ca356`. Phase 0 waits for the owner's WiFi word. — coordinator
- 2026-08-29 14:0x–14:2xZ: the owner — "you can use vm, the platform is buzy right now", "wifi", "check
  again, what is available". The VM's agent launcher restarted (its sparse clone refreshed to `main`;
  `sudo systemctl start agent-launcher.service`; the proxy probe OK); claude_1 woken 14:17Z, codex_1
  14:19Z on their charters. Phase 0 DONE (table). The disk re-checked: the root disk has 111 GB free
  (88 %), the morning read's "34 GB" was stale; the "USB archive" is a read-only cloud bucket mounted
  by geesefs (`troll-farm-data:archive` at `/media/tarstars/medium_data/database/troll_farm`, 9.8 GB of
  artifacts incl. July's checkpoints); nothing needs to move for this card. — coordinator
- 2026-08-29 14:5xZ: the owner set THE TARGET (`coordination/GOAL.md`) and `/goal coordination/GOAL.md`;
  both charters accepted (claude_1 14:20Z with the VM runtime in and the bench started; codex_1 14:21Z,
  day-1 documents next). **Measured on this host (14 threads, `nice 10`): `SpatialActorCritic` 34,926
  weights; inference 0.44 ms at batch 1, 4.2 ms at batch 64 (15,200 obs/s), 14.9 ms at batch 256
  (17,200 obs/s), 85 ms at batch 1024; a training step at batch 256 = 43 ms (5,900 samples/s).** So
  Phase 3's 2×10⁸ turn-steps is two to three days of this host for the 35k network — better than the
  analysis's estimate (40–80 M a day). — coordinator
