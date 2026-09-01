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
| 1 | **the full-game environment** (below) | codex_1 | 6 days, one message | 1,000 self-play games; transition parity and terminal parity 1,000/1,000 each; the measured illegal-command count zero *with its negative control*; the tests pass; the gate report carries the timing-stripped digest of the result (elapsed time and rate removed, keys sorted — a raw hash cannot travel between hosts, claude_1 19:47Z) and the 4-thread VM speed line; **not accepted before amendments 1–9 are in** (codex_1's 18:40Z run at `f94be850` was pre-amendment: progress, not the gate). **DONE 2026-08-29 21:1xZ** — the amended v400 gate green at `agent/codex_1@07b440bd` (transition and terminal parity 1,000/1,000; the illegal counter live, 0 with its control; 7/7 Python, 9/9 Rust; VM 4-thread 214 turn-steps/s), REPRODUCED by claude_1 (portable digest byte-identical; its plane builder 1,000/1,000 in v400); integrated onto `main` by the coordinator, built and tested on the host | parity not reachable in budget |
| 2 | **the dataset, the bench, the clone** (below) | claude_1 (dataset, bench, trainer); coordinator trains on the host | 7 days for the dataset + bench + trainer; the training run 1–2 days | the clone plays 24/24 real maps to the end against the champion's binary; the owner reads its games | after the budget the clone cannot play a whole game → Way A's stages from scratch, July's levels as the base |
| 3 | PPO from the clone with the clone anchor, real maps, the training pool (**the exact champion, weight 4 of 10, since 2026-08-30 09:42Z — `ppo-d`, the run of record**; the linked strategies + frozen copies of the policy), a bench every ~500 updates against the champion's compiled file (the clone's 9 of 48 is the bar), the card's 400-game gates against the champion's and orchard 6's files once a checkpoint passes 55 % | coordinator (host); claude_1 reproduces the bench numbers | 2–4 weeks | ≥ 60 % vs the champion and vs orchard 6 on 400 games each, positive margin, three gates in a row | no gain over the clone after 2×10⁸ network decisions (mini-steps: about 7.5×10⁷ game turns, ~250 thousand games), or the policy exploits an engine hole (replay parity fails on its games) |
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
then the turn executes for both seats. The opponent's commands come from the pool (below). **The turn's
reward is paid once, on the mini-step that executes the turn (the last one); the earlier mini-steps of
that turn carry reward 0** — so a policy-gradient objective does not scale with the number of trolls
(chatgpt_1's audit finding 4, 2026-08-29, accepted; the earlier "same scalar to every mini-step" rule
was wrong). The trainer treats the mini-steps of one turn as consecutive steps with discount 1 inside
the turn and the usual discount between turns.

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
**Amendments after chatgpt_1's bench audit (2026-08-29 17:38Z, accepted 17:5xZ) — before a trained clone is
judged, the bench must present the network exactly what the environment presents:** (1) the planes and masks
for every mini-step come from the same Rust plane builder (`tf_full_obs_from_state`, with the selected plan and
the earlier trolls' staged actions), never from a bench-side re-implementation; (2) the plan is an always-legal
target and TRAIN is emitted only by the same exact dry run the environment uses (post-MOVE/post-PICK bank and
shack occupancy), through one shared adapter; (3) the game ends when the referee's stall/mercy rule ends it
(`has_stalled`), with the turn and reason recorded, not at a fixed turn count; (4) both seats: every map is
played twice, the network on seat 0 and on seat 1, with the seat transformation tested. The random-policy
smoke of day 1 stays what it is — a proof of the pipes.

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
version tagged separately); no seat augmentation (withdrawn 18:5xZ — the views are player-relative). Sizes and counts reported.

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
`opponent_observe/step` for the frozen-policy opponent. **Amendments after chatgpt_1's audit
(2026-08-29 16:40Z, accepted 17:0xZ):** (1) `tf_full_decode_action` and `tf_full_encode_command` take
the absolute `seat` and rotate internally, so absolute replay coordinates encode to the canonical
player-relative index for either seat; (2) `tf_full_encode_command` takes the active troll's absolute
cell, so a non-move verb (HARVEST, CHOP, DROP, MINE, PLANT, PICK) encodes to `plane·242 + rel(y)·22 +
rel(x)` of that troll's cell — the same index the mask marks legal; (3) `tf_full_obs_from_state`
validates its inputs and returns `-2` on any impossible combination (phase/active-troll/plan
mismatch, staged actions out of order or for a troll not earlier in id order, a staged action illegal
for its troll) — never fail-open; (4) the tests gain both-seat, all-verb conformance fixtures: for each
seat and each of the 13 verbs, a hand-built state whose label encodes, decodes and is marked legal; **(5) the starting troll is (speed 1, carry 1, harvest 1, chop 1) as in the real game — the full
environment builds its state with `from_ascii_with_talents(rows, (1,1,1,1))`, never the engine's
`from_ascii` default `(1,1,1,0)`; each recorded replay carries the complete initial state (talents
included) and the Python verifier reads it from the record instead of hard-coding a tuple**
(chatgpt_1's audit, 17:21Z: Rust and the verifier agreed on the same wrong constant, so parity could
have passed falsely; verified against `rust/src/game/state.rs:98`, `rl_full.rs:194`, `rl_full_env.py:653`). **(6) `illegal_commands` must be a real count** of parser or referee rejections from either side — at
`agent/codex_1@f94be850` it is initialized to 0 and copied out, never incremented, and the test asserts 0
(`rl_full.rs:1302`, `:1516`, `:2673`) — with a negative-control test (a deliberately illegal command is
counted), or the zero-illegal claim leaves the gate (chatgpt_1's audit 17:32Z, verified).
**(7) terminal parity** (chatgpt_1's audit 17:50Z, accepted 18:0xZ): the verifier splits `transition_parity` from
`terminal_parity`; after every replayed transition it runs Python `has_stalled` with its persistent counter and
requires every non-final state to be nonterminal and the final state terminal; each replay carries the terminal
kind/reason and the final counter, compared; negative controls (a truncated replay, one turn appended after an
early end, a mutated counter/reason) must fail while transition parity stays green.
**(8) the plan vocabulary is 400, not 144** — the census over the top four's exact tables (1,725 TRAINs): 267
(15.5 %) lie outside delineate's ranges — speed 4 in 209 (Bubaptik: 222 of its 425 purchases, 52 %), carry 5
in 10, harvest 3 in 33, chop 4 in 16; the game caps nothing (costs grow as the square). Vocabulary: speed 1–4 ×
carry 1–5 × harvest 0–3 × chop 0–4 = 400; index `(((speed−1)·5 + (carry−1))·4 + harvest)·5 + chop`; entry 0 =
(1,1,0,0) repurposed as "train nothing"; masks unchanged (harvest 0 and chop 0 together illegal; harvest > carry
illegal; affordability never masks). `TF_FULL_PLAN_SIZE` = 400; plane scales 60–63 become S = 4/5/3/4 and the
cost/deficit planes 64–71 S = 48 (12 + 25 + margin). **The plan head is delineate's per-candidate scorer**, not a
flat 400-way layer: one small shared network scores each candidate from the pooled board features plus that
candidate's attributes, its cost, its deficit against the bank, an affordable flag and whether it matches the
current target — all computable from the observation planes — so 400 candidates cost ~1 thousand weights.
**The shard format (claude_1's pilot, accepted):** shards carry the compact per-turn state (gzipped JSON, ~54 B a
turn; ~45 MB for the whole teacher set) plus the labels and metadata — never the planes (20 TB); the planes are
built at load time, per batch, by the same Rust `tf_full_obs_from_state` the environment uses; claude_1's Python
plane builder remains the drift test's independent second implementation only. **Label conventions signed as
they stand in `OBS-PLANES.md`:** the map top-left in the padded grid; seat 1 rotated over the map's own w × h.
A MOVE that ends where the troll stood (1.7 % of MOVE labels) is WAIT — the rule as written.
**(8, completed — chatgpt_1's follow-through audit 18:02/18:10Z, accepted 18:2xZ):** every talent-bearing plane
widens with the vocabulary, not only the target: own/opponent troll speed 18/28 S 3→4, carry 19/29 S 4→5, chop 21/31
S 3→4, cargo 22–27/32–37 S 4→5, maxima 72/80 S→4, 73/81 S→5, 75/83 S→4, sums 76/84 S 36→48, 77/85 S 48→60,
79/87 S 36→48, carried/free 93–96 S 4→5, target 60–63 S 4/5/3/4 (harvest planes already cover 3); saturation
tests at the old and new maxima for both seats. **Target memory:** at the plan phase, planes 59–71 show the
*standing* target — the previous turn's plan, kept across turns until changed (zero at the start of a game and
after a TRAIN succeeds) — and after the plan decision the newly selected one; the dataset feeds the previous
turn's hindsight label as the standing target, so the scorer's "matches the standing target" feature is
observable in play and in replays alike. **Codec totality in the dataset:** a parsed TRAIN (1,1,0,0) is
reported unsupported, never "train nothing"; any range-valid tuple whose mask is zero (harvest > carry) is
labelled −1 and counted. **One generation id** `PLAN_VOCAB_VERSION = "v400-2026-08-29"` recorded by the
environment (a size/version query), the codec, the shards, the trainers, the checkpoints and the exporter's
manifest; any mismatch raises at load.
**(9) the environment's Python step contract** (chatgpt_1's audit 18:10Z, accepted): `rewards, info =
env.step(actions)` — one call describes the actions just consumed; `rewards` is `f32[n]` with the turn's reward on
the executing mini-step and 0 elsewhere (amendment 4 makes buffering unnecessary); `info` is a named record with
exactly the terminal arrays of `tf_full_step` (`dones, wins, episode_turns, episode_returns, episode_seeds,
map_indices, opponent_ids, score_own, score_opp, trained_specs, trained_turns, trained_count, trained_overflow,
illegal_commands, action_hash, state_hash, turn_completed`); no variable-length transition batch in the shipping
wrapper; the fake environment returns the identical named surface; the trainer stores one row per slot per
call and guesses no field names.
**(8, second completion — chatgpt_1's r3 18:30Z and the plan-scorer correction 18:40Z, accepted 18:5xZ):**
(a) **the plan mask has exactly one rule**: entry 0 = "train nothing", always legal; every other entry is legal
(affordability never masks; the global unit cap masks all but 0) — `harvest > carry` is delineate's restriction,
not the game's, and Bubaptik breaks it in 44 of its 425 purchases; `harvest 0 and chop 0` is legal in the game and
trained by no teacher (0 of 1,725), so it is not masked either; the codec is total under this mask (only
out-of-range tuples are reported unsupported). (b) **No target memory in behaviour cloning**: the previous
turn's hindsight label equals the current label between purchases, so feeding it as the standing target leaks
the label — plan rows carry `standing_plan = 0` and zeroed planes 59–71; in PPO the standing target is the
environment's own state (the policy's previous choice), never synthesized from labels; the scorer's "matches"
feature is 0 when the standing target is "none". (c) **Iron-free maps waive iron**: the scorer's iron cost and
deficit are 0 when the map has no iron cell (plane 4 empty), as the environment's cost planes already are; tests
with iron and no-iron controls. (d) **No seat augmentation**: player-relative views already canonicalize the
seat, and flipping the label without transforming the state is invalid — the card's seat-swap augmentation is
withdrawn. (e) The storage figure was wrong by a thousand: ~800,000 dense rows are ~20 GB, not 20 TB; the
compact-state shards (~45 MB) with load-time plane building stand on their merits (size, and the drift
discipline of one Rust builder), not on impossibility.
**(8, third completion — chatgpt_1's target-memory-init handoff 18:49Z, accepted 18:5xZ):** the scorer's input
column for the "matches the standing target" feature is initialized to exactly zero, so a behaviour-cloned
checkpoint (which never sees a standing target) gives identical plan logits at the first PPO plan phase with or
without one; PPO trains that column afterwards. Test: identical logits at init with and without a target; a
gradient step on the column makes them differ.
**(10) the advantage trace inside a turn** (chatgpt_1 07:03/07:15Z, accepted 07:3xZ): `compute_gae` decayed a turn's reward
by λ once per mini-step even where the discount was 1, so a plan decision received 0.95^k of its own turn's reward — credit
depended on the roster after all. Two factors: the value bootstrap uses γ only at a turn boundary (1 inside), the trace uses
γ·λ only at a turn boundary (1 inside); tests: 0/1/4/12 same-turn mini-steps before one reward R all receive R; the two-turn
closed form keeps γ·λ across the boundary. **(11) no standing target at plan decisions in the first Phase 3 run**: the
shared trunk reads planes 59–71, the clone's plan rows had them zero, so a standing target at the clone→PPO handoff shifts
the plan logits through the trunk whatever the match column does (the zero-init of amendment 8's third completion was
necessary, not sufficient). Ruled: the trainer zeroes planes 59–71 at every PLAN decision (policy, anchor, frozen opponent
alike; troll decisions untouched), with a test on the real clone checkpoint that two plan observations differing only in
those planes give byte-identical plan logits; target persistence returns later through a separate, explicitly gated path.
**The run started at 04:45Z is exploratory, not the run of record**: it stops when the patched trainer lands and the run
of record restarts from the clone. Python: `FullVecEnv` in
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
- 2026-08-30 09:4xZ: **`champion_exact` is in the training pool — `ppo-d` started 09:42Z** from the clone with the completed
  sanitizer and the pool weighted champion_exact 4 / secure_orchard 1 / norxondor_native 1 / legend_field_proxy_v2 1 /
  gold_elite_adaptive 0.5 / script_boss 0.25 / mybot_boss4 0.25 / python_frozen 2 (`/home/tarstars/nn-data/ppo-2026-08-30-d/`);
  it is the run of record once claude_1's reproduction of the champion gate lands (chartered 09:39Z), exploratory until
  then. `ppo-c` stopped at ~480 updates (exploratory; its update-250 checkpoint benched vs the champion's file for the
  record of 'sanitized trainer, old pool'). codex_1's champion opponent merged onto `main` (`d34f16c8`), the library rebuilt
  on the host; the environment suite (now with the 200-replay champion test) running here. — coordinator
- 2026-08-30 13:5xZ: **the run of record's update-1,000 snapshot vs the champion's file: 4 wins of 48 (3 on seat 0), 81.7
  points to 169.3 (margin −88), a troll bought in 26 games (the clone 44, update 500: 33), 29 of 48 games ended with no trees
  left, 2 loop games.** The curve against the champion: the clone 9 → update 500: 3 → update 1,000: 4 wins; 134 → 108 → 82
  points. Against its practice pool the run is flat at ~26 %. The pattern — chop everything, stop buying — points at the
  objective, not the opponents: a per-turn discount makes the final score nearly invisible from the early turns, so the
  per-wood shaping dominates. Under investigation this hour (the trainer's defaults, the chop counts in the games). — coordinator
- 2026-08-30 14:0xZ: **the chop hypothesis is refuted by the games**: per game the clone chops 94 times, harvests 38, plants 25;
  the update-500 snapshot chops 70, harvests 27, plants 19; update 1,000 chops 71, harvests 17, plants 14. The snapshots do
  *less* of everything productive — they are not deforesting, they are drifting toward inaction (the champion fells the
  trees while they idle, hence the early endings). The trainer's defaults: γ 0.997, λ 0.95, entropy 0.01, wood shaping 0.5,
  end-wood 3.5. The likelier cause: **policy updates driven by an untrained critic** — the clone's value head was never
  trained, so the first hundreds of updates push the policy with random advantages while the exploration bonus loosens it.
  Two runs to separate the causes: `ppo-e` (started 13:5xZ; γ 0.999, no wood shaping, the real end score, an anchor floor
  0.05) tests the objective; `ppo-f` (when the flag lands) tests a **critic warm-up** — the value head trained alone for the
  first N updates with the policy frozen, then the normal loop with a reduced actor learning rate. `ppo-d` runs to its
  update-1,500 bench, then stops. The four cluster jobs carry the old defaults: a 12-hour negative control. — coordinator
- 2026-08-30 14:2xZ: `ppo-d` stopped at 1,138 updates (its trend established, the cores freed). **The trainer gained a critic
  warm-up** (`--critic-warmup-updates N`: for the first N updates only the value head trains — the policy frozen bit for bit,
  its shared trunk included — then the normal loop; `--actor-lr-scale S`: a reduced learning rate for the policy side; 4 tests,
  57 in the file). **`ppo-f` started 14:2xZ**: warm-up 300 updates, actor learning rate ×0.3, γ 0.999, no wood shaping, the
  real end score, the leash 0.1 → 0.05, the champion pool, 10 threads. `ppo-e` (the objective alone) runs beside it. Both are
  benched at update 500 (after the warm-up for f) and 1,000; **no run is the run of record until a snapshot beats the clone's 9
  of 48**. — coordinator
- 2026-08-30 14:4xZ: `ppo-e` and `ppo-f` were stopped from outside the session at 14:41Z (both at ~249 updates, one short of
  their first snapshot) while the machine was busy with the owner's own work; two runs at 20 threads had exceeded the host
  rule (≤ 14). **From now on one run on the host** (`ppo-f2`, the warm-up variant, 8 threads at the lowest priority, since
  14:4xZ) **and the variants on the cluster**: the launcher now passes the five new flags; `ppo-yt-e`
  (`8058416-bb42350-42e03e8-4ed0d880`; γ 0.999, no wood shaping, the real end score, the leash 0.1→0.05) and `ppo-yt-f`
  (`4d7091d-f64fde1f-42e03e8-fb5457be`; the same plus a 300-update warm-up of the value estimate and the policy's learning
  rate ×0.3) run beside the four old-objective jobs — six 12-hour jobs, results ~01:00–03:00Z 08-31, each final snapshot
  benched here against the champion's file. — coordinator
- 2026-08-30 15:4xZ: **PHASE 4's ENGINEERING DELIVERED AND REPRODUCED ON THE HOST.** codex_1's amended export (14:57Z,
  `5be68352`): the clone as one Rust file, `cgauto/submissions/candidate-nn-clone.rs` — 52,854 characters, SHA-256
  `36bf2f2e…`; effective 16-bit integer weights (int8 + packed residual bits, 72,660 bytes) packed into 29,064 source
  characters; the lifted state/engine/mask/codec/plane builder with pinned source hashes; the seat read once on turn one from
  the starting troll's id (fail-closed on a malformed id set). The coordinator's reproduction from a clean checkout of that
  commit, 15:2xZ: 7/7 tests; regeneration byte-identical; the bed — compiled Rust 48/48 games and 13,206/13,206 commands
  identical to the signed Python clone, the Python export 48/48, both difference lists empty, the direct parity probe on both
  seats true, the corpus check 370/370 on the host's complete states file; timing first-turn max 14.8 ms, warm median 6.5 ms,
  p99 10.6 ms (gate 15), max 26.4 ms under a loaded host. All seven gates true. **Merged onto `main` (`b6075fe8`).** claude_1
  chartered for the second reproduction (handoff 15:35Z). **A file of the clone exists [corrected 16:3xZ: generated and functionally reproduced, not ladder-ready until amendment (d)
  and the timing certification pass — chatgpt_1's wording correction]; it is NOT submitted and will not be without the owner's word** — it would read below the champion (9 of 48). The pipeline snapshot → one file is now
  hours, so any snapshot that beats the clone ships the same day. Side findings: `/home/tarstars/nn-data/` had been removed from
  the VM (by whom, unknown; codex_1 asked) — restored from the host copy, checksums verified; the VM's disk is at 96 % (818 MB
  free) — nothing deleted, the owner asked (board queue). The cluster: jobs a/b/c began running only ~15:20Z (three hours in the
  queue), d/e/f still waiting for slots at 15:3xZ — the 12-hour results move to ~03:30Z and later. — coordinator
- 2026-08-30 15:5xZ: **`ppo-f2`'s update-500 snapshot vs the champion's file: 5 wins of 48 (3 on seat 0, 2 on seat 1), 123.5 points
  to 177.8; 19 games ended early (run D at update 1,000: 31), 0 loops, 0 illegal; a purchase in 0.9 games per game-average as
  the clone's; per game chop 75 / harvest 37 / plant 21 / move 273 (the clone 94 / 38 / 25 / 253).** Since the warm-up froze the
  policy for 300 updates, this is 200 policy updates at a third of the learning rate under the corrected objective: less eroded
  than run D at its update 500 (3 of 48, 108 points; harvest 27, plant 19) but still below the clone (9, 134). The erosion per
  update is about the same as D's (−0.05 points per update) — one 48-game bench, so the update-1,000 snapshot (~16:25Z) decides
  whether the remedies hold the line or only slow the drift. Still no run of record. — coordinator
- 2026-08-30 16:1xZ: **Phase 4's engineering: both reproductions in** — claude_1 PASS on all four items on the VM (15:40Z, every
  hash identical, the corpus check run again on the restored shard). **And a real hole found by chatgpt_1's audit (15:42Z): the
  generated bot executes AVX2 unconditionally** — on a platform worker without AVX2 it would crash before its first command;
  our two machines both have AVX2, so no bed could see it. Ruled on the sub-card: (d) runtime dispatch with a baseline
  fallback, both paths bedded; (e) the timing gate = three quiet runs on the host, median p99 ≤ 15 ms, each ≤ 20 ms; (f) the
  size counted in UTF-16 units (≈ 81,918 today — under the limit with 18,000 to spare, so a larger network is not free).
  codex_1 has the handoff; +1 day on the sub-card. Nothing is shippable until (d) lands — which costs nothing today: no
  snapshot beats the clone yet. The cluster at 16:00Z: a/b/c at ~300 updates, d started, e/f still queued. — coordinator
- 2026-08-30 16:3xZ: chatgpt_1's wording correction (16:09Z) accepted: the board and the report called the file "ladder-ready"
  while the ruling says "not shippable until (d)" — both now say "generated and functionally reproduced; not ladder-ready
  until the CPU fallback and the timing certification pass"; the phrase returns once (d)–(f) pass and are reproduced. — coordinator
- 2026-08-30 16:4xZ: **`ppo-f2`'s update-1,000 snapshot vs the champion's file: 7 wins of 48 (3 on seat 0, 4 on seat 1), 132.2 points
  to 193.7; 14 games ended early (update 500: 19; run D at 1,000: 31), 2 loop games, 0 illegal; a purchase in 39 of 48 games
  (the clone 44, run D at 1,000: 26); per game chop 103 / harvest 33 / plant 27 / move 226 (the clone 94 / 38 / 25 / 253).**
  The first snapshot of any run that climbed from its predecessor (5 → 7 wins, 124 → 132 points) and the activity came back
  (chops 75 → 103, plantings 21 → 27) — the drift toward inaction is not happening under the remedies. Still below the clone
  (9, 134); the champion's own score rose with it (178 → 194: the games last longer, 34 of 48 to the turn limit), so the
  margin (−61) is no better than at update 500 (−54). One 48-game bench is ±2 wins; update 1,500 (~17:25Z) is the next
  reading; a snapshot at or above the clone's 9 with a better margin would make `ppo-f2` the run of record. — coordinator
- 2026-08-30 17:0xZ: **a correction of my own cluster reading.** At 15:3xZ I read the jobs' *first* heartbeat lines as their current
  state and logged "a/b/c began running only ~15:20Z after three hours in the queue" (also in the report's fourth edition).
  Wrong: at 17:06Z the monitor's last heartbeats show `ppo-yt-a/b/c` at 270 minutes elapsed — running since ~12:35Z, right
  after launch — at updates 4,204 / 3,725 / 4,275 (≈ 17 million decisions each), practice win rates 27 % / 26 % / 17 % (c's
  champion-heavy pool is the harder one); `ppo-yt-d` since ~15:55Z at 1,064 updates (29 %); `ppo-yt-e`/`f` running but not
  yet reporting. a/b/c finish ~00:35Z, d ~04:00Z; e/f later. The report's next edition carries the correction. — coordinator
- 2026-08-30 17:3xZ: **`ppo-f2`'s update-1,500 snapshot vs the champion's file: 2 wins of 48 (both on seat 0), 94.8 points to 163.7;
  32 games ended early (29 with no trees left), 1 loop game, 0 illegal; a purchase in 42 of 48 games; per game chop 81 /
  harvest 23 / plant 14 / drop 42 / move 266 (the clone 94 / 38 / 25 / 66 / 253).** The update-1,000 climb did not hold: 5 → 7 → 2
  wins, 124 → 132 → 95 points. The purchases stayed (the plan head is fine); the *collecting* collapsed — harvest, plant, drop all
  down by a third to a half — so the champion clears the trees while the network's trolls walk. Under both remedies the erosion
  still comes, only later (run D was at 82 points by update 1,000). Meanwhile the run's own practice numbers keep *improving*
  (win rate 19 % → 25 %, margin −77 → −67 by update 1,327, sampled play against the pool). One hypothesis fits that divergence:
  the bench plays the argmax command while training plays sampled commands — a policy trained by sampling can have a mode
  that is not its typical play. Test now: the same snapshot benched with sampled commands. — coordinator
- 2026-08-30 17:4xZ: **the decoding hypothesis is refuted — and the sampled-play control taught more than the test.** `bench.py`
  gained `--command-decoding {argmax,sample}` (self-test check 8; `2481680e`). With sampled commands: **the clone 3 of 48,
  109 to 207** (argmax: 9, 134 to 186) — its trolls wander (329 moves a game against 253), harvest more (47) and chop less
  (73); **`ppo-f2` at update 1,500: 0 of 48, 82 to 196** (argmax: 2, 95). So (1) the argmax bench is the right measure and the
  shipped bot's decoding; (2) the trainer's rollouts start from a sampled behaviour worth 109 points, not the 134 we measure —
  the policy is soft (entropy 1.19 nats over the legal moves); and (3) **sampled play against the champion also got worse with
  training** — the rising practice win rate (19 → 25 %) came from the 60 % of games against the weaker linked bots and the frozen
  copies of itself. The morning's transfer finding in a milder form: the pool still teaches what does not transfer. Decision:
  **`ppo-f2` stops now** (three points, 5 → 7 → 2, its trend established; its update-2,000 would add little) and **`ppo-g` starts:
  the champion only** (`champion_exact` weight 1, no other bot, no frozen self), the remedies kept (γ 0.999, no wood shaping,
  end-wood 4.0, warm-up 300, actor lr ×0.3, the leash 0.1 → 0.05), 8 threads at the lowest priority; benched at updates 500,
  1,000, 1,500. The cluster's job `ppo-yt-c` (champion-heavy pool, old objective) is the overnight control of the same idea.
  For later: the trainer logs no per-opponent win rate — worth adding, so the practice numbers can be read. — coordinator
- 2026-08-30 18:3xZ: **`ppo-g` (the champion as the only opponent; started 17:45Z, `/home/tarstars/nn-data/ppo-2026-08-30-g/`) at
  update 500 — 200 policy updates after its warm-up — vs the champion's file: 5 wins of 48 (2 on seat 0, 3 on seat 1), 133.8
  points to 185.3; 18 games ended early, 2 loop games, 0 illegal; a purchase in 43 of 48 games; per game chop 112 / harvest
  37 / plant 25 / drop 62 / move 244 (the clone 94 / 38 / 25 / 66 / 253).** The points are the clone's own (134 vs 186) and the
  collecting is intact — the first snapshot of any run without erosion at this age (`ppo-f2` at 500: 124 points; run D: 108);
  the wins (5) are below the clone's 9 but within one bench's noise. Its practice numbers against the champion alone are the
  honest baseline: 3 % wins, margin −116 in sampled play (update 474). Not a gain yet; `ppo-f2` fell at update 1,500, so the
  readings at 1,000 (~19:15Z) and 1,500 (~20:05Z) decide whether the champion-only pool holds the line. — coordinator
- 2026-08-30 19:1xZ: **Phase 4's engineering is COMPLETE** — codex_1 delivered amendments (d)(e)(f) within the hour
  (`c4355caa`: runtime AVX2 dispatch + baseline fallback, both paths bedded 48/48 and 13,206/13,206; the three-sample timing
  machinery gated to the host context; the UTF-16 size gate — 83,282 of 100,000) and claude_1 reproduced them at 16:49Z,
  adding the static proof the bed cannot give: the disassembly of the shipping binary shows an SSE-only kernel (zero `%ymm`)
  beside one dispatched AVX2 symbol, no fused multiply-add. Merged (`bb3645ea`). Open: the host's three-quiet-run timing
  certificate, taken when a shipping candidate exists (the host trains now; the clone is not submitted). Details on the
  export sub-card. — coordinator
- 2026-08-30 19:2xZ: **`ppo-g` at update 1,000: 4 wins of 48, 107.0 points to 179.3** (update 500: 5, 133.8); a purchase in 38 of
  48 games (was 43); per game chop 96 / harvest 23.5 / plant 22 / drop 51 (was 112 / 37 / 25 / 62); 4 loop games; practice vs the
  champion 1.6 % wins, margin −122. **The champion-only pool did not hold the line — the erosion arrived between updates 500
  and 1,000, exactly as in every other run.** Five runs (A, C, D, F2, G) now show one replicated shape across pools, objectives,
  warm-up and learning rates: the clone's multi-step fruit economy (harvest → carry → drop, plant) decays first while the
  immediate chopping survives — long-chain credit erodes, dense credit stays. The one cheap untested lever on that axis: the
  discount itself — γ 0.999 over ~600 mini-steps still discounts the final score to ~0.55 from the early game. **`ppo-g`
  stopped at update 1,073; `ppo-h` starts: γ = 1.0 exactly** (the end score undiscounted; GAE λ 0.95 unchanged), everything
  else as `ppo-g` (champion only, warm-up 300, actor lr ×0.3, no shaping, end-wood 4.0, the leash 0.1 → 0.05), 8 threads,
  seed 9, `/home/tarstars/nn-data/ppo-2026-08-30-h/`; benches at 500 / 1,000 / 1,500. If the same shape appears, the next
  lever is delineate's curriculum (short games, small maps first) — a design change, to be spec'd on this card. The six
  cluster jobs (44 M decisions each) remain the long-horizon test tonight (~00:35Z–04:00Z). — coordinator
- 2026-08-30 20:0xZ: **`ppo-h` (γ = 1.0) at update 500: 3 wins of 48, 112.8 points to 181.8** — the worst of the three runs at this
  age (`ppo-g` 5 / 133.8; `ppo-f2` 5 / 123.5); harvests held (38) but plantings 18, picks 17, moves up to 317, 3 loop games;
  purchases 44 of 48; **the value estimate collapsed (explained variance 0.25** — the undiscounted end margin is far harder to
  predict than the γ-0.999 return's 0.6–0.97). [Corrected 20:4xZ, chatgpt_1's audit: this run is a **γ-only sensitivity at λ 0.95** — the turn-boundary credit trace is γ·λ, so it moved 0.94905 → 0.95, and the terminal signal still reaches a move 50 turns earlier at weight ~0.077; the Bellman value target did become undiscounted (hence the critic's collapse), but long-horizon *policy* credit was not tried, and the discount axis is NOT closed. A true test is (γ, λ) = (1, 1) or the offline advantage recomputation.] γ 0.999 with the warm-up remains the best-behaved setting. `ppo-h` runs to update 1,000 (~20:55Z) for the
  curve's second point, then the host waits for the cluster.
- 2026-08-30 20:5xZ: **chatgpt_1's five evening audits ruled** (its 20:02Z blocker accepted; pins `5a8f718c`, `ad699fab`,
  `a66a09ad`, `18b56832`, `32d6d97e`): (1) the γ/λ wording corrected above and on the board — ppo-h is a γ-only sensitivity;
  (2) the delineate attribution corrected — his real stage 4 is the frozen movement net with plan+value trained on the end
  score; (3) **the shared-trunk value-gradient mechanism**: after the warm-up, `value_coef · value_loss` backpropagates through
  the shared stem/tower into both policy heads at the actor's learning rate — unmeasured, common to every eroding run, worst
  where the value target is hardest (γ 1.0). **Chartered to claude_1: the falsifier** — per-objective gradient norms and trunk
  cosines on one minibatch, plus a value-only counterfactual step on a checkpoint copy measuring argmax command changes on
  fixed observations (runs g/h u500). **The next host run after ppo-h's update-1,000: `ppo-i`, delineate's stage 4 —
  the trunk and the spatial actor frozen bit for bit, only the plan head and the critic train on the real end score** (γ 0.999,
  λ 0.95, champion-only, no shaping): movement erosion becomes impossible by construction, the bench floor is the clone's own
  play, and the plan head learns purchases from outcomes — the trainer grows a `--train-scope plan-critic` flag tonight.
  (4) the sampled/argmax factorial on the clone (AA 9/48 and the two half-cells are on file; the SS cell runs after the next
  bench). — coordinator
- 2026-08-30 20:5xZ: **`ppo-h` at update 1,000: 8 wins of 48 (4 and 4 by seat), 132.9 points to 191.4** — up from 3 / 112.8 at
  update 500, one win below the clone; the collecting came back (harvest 35, plant 25, drop 70 per game; a purchase in 40 of
  48; 2 loop games). The second-best snapshot of the day (f2's update 1,000: 7 / 132.2). Both f2 and h dip at 500 and recover
  at 1,000; f2 then collapsed at 1,500 — **h's update 1,500 (~21:45Z) is the exact discriminator**, so h runs on and `ppo-i`
  (the staged `--train-scope plan-critic`, now on `main` at `213ee7f5` with its test) starts only if h falls. The clone's
  missing sampled-play cell (plan and commands both sampled) is being benched for the factorial chatgpt_1 asked to see
  complete. — coordinator
- 2026-08-30 21:1xZ: **the clone's decoding factorial is complete** (plan × command, 48 games each vs the champion's file):
  argmax/argmax **9 / 133.9**, sampled/argmax **8 / 133.5**, argmax/sampled **3 / 109.2**, sampled/sampled **4 / 103.4**.
  The command decoding carries the whole gap (about six wins and thirty points); the plan decoding costs nothing. So the
  trainer's rollouts (sampled commands) play a genuinely weaker game than the argmax bot we ship — the gap chatgpt_1's
  stochastic-behaviour audit named, now measured on all four cells. Files: `bench-clone-sampled*` (argmax/sampled),
  `bench-clone-ss*` (sampled/sampled) under `/home/tarstars/nn-data/ppo-2026-08-30-f2/`; the argmax/argmax and
  sampled/argmax cells are the clone card's originals. — coordinator
- 2026-08-30 21:4xZ: **chatgpt_1's scope blocker (20:42Z) accepted — `ppo-i` does not start on the plain flag.** The freeze is
  right but the semantics train the wrong problem: troll rows still sampled (the six-wins-weaker executor), the plan
  gradient's normalization/entropy/anchor diluted by frozen troll rows, one clip coupling critic and plan. **The repair is
  chartered to codex_1** (21:40Z; 1 day): PLAN rows sampled with PLAN-only normalization, loss, entropy and anchor; TROLL rows
  executed by the frozen policy's masked argmax and excluded from every policy term; value over all rows; pre-clip norms and
  the clip multiplier logged; five tests; the `all` scope bit-for-bit untouched. **claude_1's gradient instrument delivered
  (20:46Z, `grad_decompose.py` + 22 tests) and accepted** with chatgpt_1's review (20:51Z) to fold in (the clone's one-group
  optimizer, a common fixed 512-observation census for g-vs-h, the literal clone baseline, the effective saved lr); one
  corrected pin, then the coordinator runs it on the clone and g/h at update 500. — coordinator
- 2026-08-30 21:4xZ: **the discriminator answered — `ppo-h` at update 1,500: 2 wins of 48 (both seat 0), 109.3 points to 183.6;**
  a purchase in 35 of 48, chop down to 60, plant 19.5; 1 loop game. The same collapse as `ppo-f2` (8 → 2 here, 7 → 2 there),
  at the same age. **Three configurations (mixed pool, champion-only, γ 1.0) now show one shape: dip at 500, partial recovery
  at 1,000, collapse by 1,500 — full-parameter PPO from the clone is dead as configured.** `ppo-h` stopped at update 1,567;
  **the host is quiet** (one-run rule; nothing worth its cycles until a design change). What remains in flight: codex_1's
  staged trainer (the 21:40Z charter — the plan head learning for the argmax executor with the movement frozen), claude_1's
  corrected gradient instrument (the mechanism measurement), and the six cluster jobs' final snapshots (~00:35Z on) — the
  long-horizon control that says whether 44 million decisions ever climb back. The morning's decision tree: if the staged
  run beats the clone, it is the way; if the instrument convicts the value-gradient path, a separate value trunk is the
  next trainer change; if a cluster snapshot recovered, full-parameter PPO gets a second look at scale. — coordinator
- 2026-08-30 22:5xZ: **codex_1 delivered the staged-trainer repair in under an hour** (`6432e54a`, 21:37Z): TROLL rows execute
  the frozen policy's masked argmax without consuming a random draw (bench-equal by test); PLAN rows sample, with PLAN-only
  advantage normalization, loss, entropy and anchor (invariant to duplicated TROLL rows, by test); the value loss over all
  rows (a no-PLAN minibatch finite, by test); the pre-clip plan/critic norms and the joint clip multiplier logged; and the
  `all` scope proven byte-exact against the parent by a matched-seed two-update run (29/29 tensors, 29/29 optimizer entries).
  Verified here from a clean checkout — 51 tests pass — and **merged (`3220629a`)**. **`ppo-i` runs on the host since 22:5xZ**
  (plan-critic scope, champion-only, γ 0.999, warm-up 300, actor lr ×0.3, the leash 0.1 → 0.05, 8 threads, seed 11); its
  update-500 bench ~00:10Z; with the movement frozen the floor is the clone's own play, so whatever moves is the plan head's
  doing. Cluster note: `ppo-yt-b` was preempted and restarted from scratch ~22:08Z (the entrypoint has no resume) — its
  result comes last; a/c finish ~00:35Z, d ~03:15Z, e/f ~05:50Z. — coordinator
- 2026-08-30 23:1xZ: **the staged run's first test — `ppo-i` at update 500 (200 plan-head updates after its warm-up): 9 wins of
  48 (5 on seat 0, 4 on seat 1), 128.6 points to 184.4 — the clone's 9, the first snapshot of any run to hold the bar.** A
  purchase in 44 of 48 games; per game chop 85 / harvest 40 / plant 23 / move 256 — the clone's profile, as the freeze
  guarantees; 2 loop games, 0 illegal. And the practice numbers finally mean something: with the movement executed argmax,
  the run's own win rate is 17.7 % (the bench's 9/48 = 18.75 %) at margin −49.7, against 1.6–3.8 % and −112…−122 for the
  full-parameter runs — the practice metric now tracks the bench. Anchor agreement 0.988, entropy 0.90. Points slightly
  under the clone's 133.9 (within one bench's noise); **whether the plan head climbs above the clone is the update-1,000
  question (~00:25Z)**. — coordinator
- 2026-08-30 23:4xZ: **`ppo-i` at update 1,000: 10 wins of 48 (4 on seat 0, 6 on seat 1), 131.0 points to 184.2 — above the
  clone's 9 for the first time in the programme.** A purchase in 44 of 48; the profile intact (chop 90 / harvest 39 / plant 24);
  2 loop games; practice win rate 19.5 % (up from 17.7 % at update 500), margin −49. One win above the bar is inside one
  48-game bench's noise (±2), but the direction and the practice curve agree, and erosion is impossible by construction.
  **Update 1,500 (~00:40Z) is the confirmation reading: at or above 10 again, `ppo-i` becomes the run of record** and the
  card's next step is a wider confirmation (the 400-game protocol on the target's terms) plus the joint fine-tune question
  (the winner's stage 5) for a later day. — coordinator
- 2026-08-31 00:1xZ: **the confirmation read 9 of 48** (4 and 5 by seat; 127.7 points to 182.3; a purchase in 43 of 48; 1 loop
  game). The staged curve is **9 → 10 → 9: stable at the clone's bar** — the first run that neither erodes nor collapses —
  but not a confirmed climb; the update-1,000 spike was one bench's noise. The practice win rate keeps edging up (17.7 →
  19.5 → 20.9 %, margin −48), which can be the plan distribution improving under sampling while its argmax stays put
  (entropy 0.96). Ruling: `ppo-i` is NOT yet the run of record; it keeps running (erosion impossible, the host otherwise
  idle) with reads at updates 2,000 and 2,500; the run-of-record call needs two consecutive reads at 10+ or a wider
  protocol. The six cluster jobs (full-parameter, 44 M decisions) land from ~00:35Z and answer the other half. — coordinator
- 2026-08-31 00:4xZ: `ppo-i` at update 2,000: **6 of 48** (3 and 3), 124.1 points to 184.6 — the first read below the bar; the
  curve 9 → 10 → 9 → 6. No collapse markers (0 loop games, the profile intact, practice 18.7 % and margin −51 steady), so
  either the low edge of one bench's noise (±2) or a slow plan-head drift under the decaying leash. **Update 2,500 (~02:00Z)
  decides: a second read at or under 6 stops the run**; back at 9+ and it continues. The cluster's a and c are past their
  12-hour mark (725 min) and wrapping up — retrieval next. — coordinator
- 2026-08-31 01:1xZ: **`ppo-i` at update 2,500: 5 of 48 (121.5 points) — the second consecutive read below the bar; stopped at
  update ~2,650 by the pre-stated rule.** The staged scope's verdict in one line: **it prevents the collapse — the only run to
  survive update 1,500 — but the plan head alone drifts slowly below the clone instead of beating it** (9 → 10 → 9 → 6 → 5;
  the plan entropy rose 0.90 → 1.35 as the leash decayed — the distribution softens and its argmax walks away from the
  clone's plans). The day's full map, five full-parameter runs and one staged: full-parameter dips at 500, partially recovers
  at 1,000, collapses by 1,500, whatever the pool, discount or warm-up; staged holds 1,500 and drifts by 2,500. Nothing beats
  the clone yet; the best artefacts are the clone itself (9) and ppo-i's update-1,000 snapshot (10, within noise). **In flight
  and next**: the six cluster snapshots (a/c past 12.5 h, the pack not yet uploaded; retry ~01:45Z), claude_1's corrected
  gradient instrument (the WHY), then the morning's levers in order of evidence: a fixed (non-decaying) plan anchor or a
  lower plan learning rate for a second staged run; the winner's stage-5 joint fine-tune at a tiny rate from ppo-i's
  update-1,000 snapshot; the value-trunk separation if the instrument convicts it. The host is quiet again. — coordinator
- 2026-08-31 01:4xZ: **a timeline correction, mine.** The launcher's `--hours` only computes a step budget when
  `--total-turn-steps` is absent; I passed both, so the explicit 60 million decisions govern — at the jobs' real 1,043
  decisions/s that is ~16 hours, not 12. Job a is at 80 % (48.2 M, update 11,834) — **retrievals from ~04:45Z** (a, c), then
  d ~08:00Z, e/f ~10:00Z, the restarted b ~14:00Z. And the long-horizon signal is visible in a's heartbeats: practice win
  rate 26.9 → 28.9 % and margin −77 → −43, still climbing at update 11,800 — with the usual caution that a's pool is 60 %
  weak opponents, so the pinned bench of its final snapshot remains the only number that counts. 48 checkpoints ride inside
  the job and come back in the final tar. — coordinator
- 2026-08-31 03:5xZ: **the cluster night, rebuilt after a hard lesson.** At 01:29Z jobs a and c died at their operations'
  wall-clock limit (12 h 55 min, set from my `--hours 12` plus the launcher's margin) while my explicit 60-million-step
  budget needed ~16 h — my inconsistency; their 48 checkpoints each lived only in the sandboxes and are lost. d/e/f/b
  carried the same fate by construction, so all four were **aborted** (`yt abort-op`; nothing was retrievable from them —
  the abort saves the owner's grant, loses nothing). Two repairs, both on `main`: **(1) mid-run salvage** — the entrypoint's
  heartbeat now uploads the newest checkpoint and the train log beside the final output every ~30 minutes (`mid-run-latest.pt`,
  `mid-run-train.log`; `07fb1a46`), so an outside kill costs at most half an hour; **(2)** the launcher passes `--train-scope`
  (`6f18864c`, 19 tests). **Three jobs run now, each 60 M decisions under a consistent 17-hour limit**: `ppo-yt-a2`
  (`86be80b5…`, seed 31, the run-of-record recipe — the long-horizon full-parameter answer; the dead a's heartbeats reached
  practice win 28.9 % and margin −43 at 48 M steps, still climbing), `ppo-yt-e2` (`aa7fe45a…`, seed 32, the objective
  remedy), and `ppo-yt-i2` (`34119d53…`, seed 33, **the staged scope with a non-decaying leash** — anchor 0.1 → 0.1,
  champion-only: exactly the lever `ppo-i`'s drift diagnosis named). Results ~19:00–20:00Z today; salvage copies readable
  from ~04:30Z on. — coordinator
 **[Corrected 20:4xZ, chatgpt_1's source audit: "short games, small maps" is NOT delineate's recorded curriculum — his gist's stages are target decomposition, and stage 4 is "freeze the troll movement/action network, train a separate plan selector and value head on pure end score", then fine-tune. The episode cap stays a project idea, unattributed.]** — coordinator
- 2026-08-30 12:4xZ: **the YT sweep launched** — four 12-hour jobs in the GPU tree (32 cores + one reserved GPU each, 60 million
  decisions each, the clone as start and anchor, a 5,370-map slice, checkpoints every 250 updates inside the job, outputs
  retrieved at the end): `ppo-yt-a` (`3ff60034-9cbb9033-42e03e8-8f52e2fa`; seed 11; the run-of-record recipe: anchor 0.1→0,
  champion 4 of 10), `ppo-yt-b` (`6539cc3e-6002fe31-42e03e8-f5005ad7`; seed 12; the anchor stronger, 0.3→0.05),
  `ppo-yt-c` (`e5e5577-4c0e1939-42e03e8-5d7baf26`; seed 13; the champion 7 of 10), `ppo-yt-d`
  (`dc8fce0a-df0411ee-42e03e8-c700a2b5`; seed 14; frozen copies 4 of 10, refreshed every 50 updates). Their checkpoints
  are benched on the host against the champion's file when they return (~01:00Z 08-31). `ppo-d` stays the run of
  record here. — coordinator
- 2026-08-30 12:3xZ: **YT works.** The owner: "one train takes 3.5 days looks like a job for yt runner" (07:1xZ), "wifi", then
  "gpu" (11:5xZ) when the CPU tree's pools refused immediate operations. The new CPU-only launcher
  (`local_claude_1/nn-bot/yt_ppo_launcher.py` + `yt_ppo_entrypoint.py`, 15 tests; run with the helper project's Python) uploaded a
  2.8 MB payload (a 5,370-map slice, the clone, the library; July's 8.5 GB PyTorch wheelhouse reused from Cypress) and the
  smoke job ran to completion in July's GPU tree (`gpu_starfield_24g_cloud` / `research_gpu`, one GPU reserved, unused):
  operation `11d044bd-262b06cb-42e03e8-451600b9`, 10 updates, 36,864 decisions at **899 decisions/s on 16 cores** (the
  host: ~640 on 14 threads), checkpoints retrieved. Next: four 12-hour jobs in parallel — a sweep over seed, anchor
  strength and the champion's share of the pool — while `ppo-d` stays the run of record on the host. — coordinator
- 2026-08-30 11:0xZ: **the second confirmation of the transfer problem** — `ppo-c`'s last checkpoint (the sanitized trainer,
  the old pool, 250 updates) benched against the champion's file: 3 wins of 48 (2 on seat 0, 1 on seat 1), 106.9 points to
  177.4, 0 illegal, 21 games ended early (18 with no trees left) — worse than the clone it started from (9 wins, 133.8),
  like `ppo-a`'s checkpoint before it. The credit fixes did not change that; the opponents do. `ppo-d` trains against
  `champion_exact` (weight 4 of 10) since 09:42Z. — coordinator
- 2026-08-30 08:4xZ: **amendment 11 completed — plane 98 too** (chatgpt_1 07:43/08:03/08:15/08:24/09:10Z, confirmed by
  claude_1 in its own code 07:49Z): the 'a troll was trained last turn' latch is a second plan-only input the clone and its
  bench never saw set; the sanitizer zeroes 59–71 and 98 at every plan decision (`plan_target_memory: off-v2`), with the
  A/B/C invariance test on the real clone. chatgpt_1 withdrew its 'incomplete turn across a rollout boundary' blocker (a
  fixed-horizon rollout with a value bootstrap is standard); the trainer logs the mid-turn-cut fraction, non-gating.
  **`ppo-b` stopped at 446 updates — exploratory like `ppo-a`; the run of record is `ppo-c`, from the clone, with the
  completed sanitizer.** The champion opponent: the authority is the instrumented submission `0e92f8fa…` (codex_1 pinned it;
  the readable v6 arm `32172393…` compacts to it; `readable/denial-off-champion.rs` is a different program and excluded);
  gameplay parity (MSG stripped) is load-bearing, raw parity reported separately; **the proof route ruled: paired
  exact-input streams** — the standalone compiled file and the linked Strategy fed the same engine-generated protocol
  stream over 200 games, commands compared turn by turn — because a recorded game holds no literal per-turn input (the
  reconstruction corrects positions the player never saw; codex_1 stopped honestly at the first such mismatch). claude_1's
  two flags merged (`train_clone.py --holdout`, `bench.py --plan-decoding` with `policy_plans_drawn/refused` — the smoke
  clone's sampled plans were all refused by the dry run as unaffordable; only the full clone's bench can answer the
  question, and it did: 44 purchases of 48). — coordinator
- 2026-08-30 07:5xZ: **the exploratory run's update-1,000 checkpoint benched vs the champion's file: 2 wins of 48 (the clone
  9), 87 points vs 183 (the clone 134 vs 186), a troll bought in 28 games (the clone 44), 20 games ended by grace-expired,
  3 loop games — worse than the clone it started from, while its win rate against the practice mix had risen to 42 %.**
  The practice pool (weak linked bots + frozen copies) does not transfer to the champion; the two credit defects
  (amendments 10, 11) may have added to it. Ruled: **an exact linked copy of the champion joins the training pool** —
  sub-card `20260829-nn-bot-way-b-champion.md`, codex_1 chartered (parity by replay on 200 recorded games). The run of
  record `ppo-b` (patched trainer) runs meanwhile on the present pool; its first bench decides whether to wait for the
  champion opponent before spending the budget. — coordinator
- 2026-08-30 07:4xZ: **the run of record `ppo-b` started** from the clone with the patched trainer (amendments 10 and 11 in;
  53 tests; `plan_target_memory: off-v1`), the same command as `ppo-a` (`/home/tarstars/nn-data/ppo-2026-08-30-b/`); the
  exploratory `ppo-a` stopped at ~1,300 updates / 5.3 M decisions (win rate vs its practice mix 0 → 42 % in three hours;
  its checkpoints kept as exploratory; its update-1,000 checkpoint's bench vs the champion's file reported when it ends).
  **YT (the owner's suggestion, 07:1xZ, "wifi" given):** `local_claude_1/nn-bot/yt_ppo_launcher.py` + `yt_ppo_entrypoint.py`
  (CPU-only vanilla operation; July's layers and wheelhouse; a 2.8 MB payload with a 5,370-map slice; run with July's
  helper venv `/home/tarstars/prj/math_through_eml/.venv/bin/python`); the upload works; the first submission was refused
  by `physical/research` (immediate operations forbidden, no visible subpool) — the CPU pool is the owner's to name;
  July's GPU tree/pool is the fallback. — coordinator
- 2026-08-30 05:0xZ: **PHASE 3 STARTED on the host** — the smoke first (5 updates from the clone with the clone as anchor:
  the plan-head checkpoint loads, anchor agreement 0.84–0.88, small policy steps, ~1,000 decisions/s), then the run:
  `train_ppo_full.py --env full --maps data/processed/maps.jsonl` (all 24,973 real maps) `--initial-checkpoint`
  `--anchor-checkpoint` = the clone, `--anchor-coef 0.1 → 0 over 1×10⁸ decisions`, `--frozen-checkpoint` = the clone
  refreshed every 100 updates, opponents secure_orchard 2 / norxondor_native 2 / legend_field_proxy_v2 1 /
  gold_elite_adaptive 1 / script_boss 0.5 / mybot_boss4 0.5 / python_frozen 3, 128 games in parallel, 32-step rollouts,
  2 epochs, minibatch 1,024, 14 threads at `nice 10`, a checkpoint every 250 updates (~17 min), no in-line gates —
  the coordinator benches the latest checkpoint every few hours (48 games vs the champion's file), and runs the
  card's 400-game gates when a bench passes 55 %; budget 2×10⁸ decisions (≈ 2.3 days); output
  `/home/tarstars/nn-data/ppo-2026-08-30-a/` (`train.log`, checkpoints). — coordinator
- 2026-08-30 04:5xZ: **PHASE 2's MILESTONE REACHED — the clone's games are on file for the owner's read**
  (`local_claude_1/nn-bot/results/clone-2026-08-30-a/README.md`). The bench, argmax decoding, 24 maps × both seats vs
  the champion's file: **9 wins of 48 (4 seat 0, 5 seat 1), 133.8 vs 186.2, 0 illegal, 0 timeouts**; 31 games to turn
  300, 8 grace-expired, 9 mercy; 1 loop game (87 turns); a troll bought at turn 1 in 44 games — (2,2,2,2) ×8, (2,2,1,2)
  ×6, (3,2,2,2) ×6, (2,2,2,1) ×5 … (the champion: (2,2,0,2)); the four games without a purchase averaged 92. The sampled
  decoding: 8 wins, 133.2, a second troll in 9 games — the same player; **argmax is the decoding of record**. Read of
  the games: the second troll harvests and plants like a teacher; the first churns PICK/DROP at the shack for stretches
  (copying without a goal); no chopping as a plan. **Phase 3 starts from this checkpoint.** — coordinator
- 2026-08-30 04:1xZ: **THE FIRST CLONE IS TRAINED** (`/home/tarstars/nn-data/clone-2026-08-30-a/clone-pilot.pt`, 454 kB;
  `train_clone.py --epochs 4 --batch 512 --workers 16 --seed 1` over the rebuilt shard `dataset-v400-2026-08-30`, 817,811
  rows, no holdout — the trainer's default; ~30 min an epoch at 430–445 rows/s, the Rust plane builder the ceiling):
  epoch 1 → 4: plan loss 2.21 → 1.02, plan accuracy 0.63 → 0.74; command loss 1.62 → 1.06, command accuracy 0.54 →
  0.65; per verb on the last epoch — MOVE 40.7 % (the exact cell reached, one of up to 242), CHOP 90.5 %, DROP 97.1 %,
  HARVEST 92.7 %, MINE 80.0 %, PLANT banana/lemon/plum 99.8/84.7/88.2 %, PLANT_APPLE 40.2 %, PICK banana/plum/lemon/
  apple 23.4/15.4/21.6/3.1 % (reported, never a gate). **The bench runs now**: 24 maps × both seats, against the
  champion's compiled file, plan head decoded by argmax and, separately, by a sample at temperature 1. — coordinator
- 2026-08-29 21:4xZ: **the full teacher dataset built on the host** with claude_1's `build_dataset.py` (its branch, day-4
  state; the script is not yet on `main`) over the 784 seat-games of the exact reconstruction (748 replay files:
  delineate 215, MSz 203, norxondor 184, Bubaptik 182 of its latest version 6568138): **817,811 rows = 224,400 plan +
  593,411 command**, in 1 min 42 s; command labels MOVE 47.7 %, CHOP 19.4 %, DROP 12.6 %, HARVEST 11.1 %, PLANT 4.2 %,
  MINE 1.0 %, PICK 1.6 %, WAIT/stayed 2.4 %; plan labels 106 distinct, "train nothing" 141,640 (63 %), then (2,4,1,2),
  (2,4,1,3), (2,3,1,2), (4,3,1,2), (4,3,0,2)…; **0 unsupported plans, 0 mask-forbidden labels; no standing target on
  plan rows** — the rulings hold at scale. Size: states 12.9 MB gzipped (58 B a turn) + labels 1.3 MB — **14 MB in
  all**. Stored outside the repository at `/home/tarstars/nn-data/dataset-v400-2026-08-29/` (`SHA256SUMS` inside);
  re-run in minutes if claude_1's day-7 final changes the format. — coordinator
- 2026-08-29 21:3xZ: **Phase 1 accepted and integrated; the host's numbers with the environment of record:** the random-action
  driver 843 decisions/s (20 threads); **the trainer `train_ppo_full.py --env full`: rollouts 3,500 decisions/s with 128
  games in parallel on 14 threads, 1,040 decisions/s overall with the PPO update (2 epochs, minibatch 1,024)** — Phase 3's
  2×10⁸ decisions ≈ 2.3 days of this host; the version handshake (`v400-2026-08-29`) and the step contract work against
  the real library. — coordinator
- 2026-08-29 18:5xZ: correction of my own: the quarantine policy `20260829T182334Z` says chatgpt_1's r3 supersedes a
  message "not on its branch" — wrong: `…175600Z…-dataset-correction-r2.md` is on `agent/chatgpt_1`; the transport
  rejected the r3 as an acknowledgement target for a reason the lint does not print (the finding stands and was
  ruled regardless). — coordinator
- 2026-08-29 17:5xZ: **the Phase 3 trainer drafted** (a host subagent, reviewed): `local_claude_1/nn-bot/train_ppo_full.py`
  (masked PPO over `FullVecEnv` with mini-step rollouts, discount 1 inside a turn, the reward on the executing
  mini-step — `--reward-credit executing`, the card's rule —, the clone anchor as a decayed KL term, a frozen-copy
  opponent, four-key checkpoints, a bench-gate hook), `fake_full_env.py` (the signed surface, so the trainer
  runs without the Rust library), `tests/test_train_ppo_full.py` (14 tests); **the plan head landed as the opt-in
  flag `SpatialActorCritic(plan_head=True)` + `forward_with_plan()` in `cgauto/train_level1_ppo.py`** (July's
  keys unchanged; July's tests pass). Untested against the real environment until Phase 1 lands. The budget
  unit is defined: network decisions (mini-steps). — coordinator
- 2026-08-29 14:5xZ: the owner set THE TARGET (`coordination/GOAL.md`) and `/goal coordination/GOAL.md`;
  both charters accepted (claude_1 14:20Z with the VM runtime in and the bench started; codex_1 14:21Z,
  day-1 documents next). **Measured on this host (14 threads, `nice 10`): `SpatialActorCritic` 34,926
  weights; inference 0.44 ms at batch 1, 4.2 ms at batch 64 (15,200 obs/s), 14.9 ms at batch 256
  (17,200 obs/s), 85 ms at batch 1024; a training step at batch 256 = 43 ms (5,900 samples/s).** So
  Phase 3's 2×10⁸ turn-steps is two to three days of this host for the 35k network — better than the
  analysis's estimate (40–80 M a day). — coordinator
- 2026-08-31 05:2xZ: **the owner asked for a second opinion with the fullest possible experiment description, published.**
  Written and on `main`: `local_claude_1/nn-bot/EXPERIMENT-2026-08-31.md` (`f9595b53`) — the data (817,811 decisions, the
  400-way vocabulary, the label conventions), the observation (the 104 planes by group, the sanitizer), the network (35,952
  parameters by part, the scorer's 14 features), the environment and mini-step loop, the reward and the γ·λ accounting, the
  trainer's full start-record configuration, the bench protocol and the decoding factorial, all seven host runs' configs and
  numbers with the activity signature, the seven ruled-out causes, the two standing explanations, six explicit reviewer
  questions, and the reproduction commands. Published as an owner-readable page (artifact "Why Self-Play Eats the Clone").
  **chatgpt_1 chartered for the adversarial review** (handoff 05:20Z, ack-required, 1 day): errors of fact first, the six
  questions in order, a ranked next experiment, and any ceiling in the data/network worth fixing before more compute. — coordinator
- 2026-08-31 07:2xZ: **the recovery programme is the goal (the owner: "write down your 'What I'll do now' as goal file and
  set it in action")** — `coordination/GOAL.md` rewritten (`fdccdbc0`): five ordered steps (errata → protocol adoptions and the
  target-KL repair → Gate 0 measurement → the entropy-zero falsifier → the cluster reads and the evidence-ranked next lever),
  the standing target and authorizations unchanged, the pre-freeze ladder work parked in one line. **Step 1 done**: four errata
  marked in the dossier (`fe91e93e`) and the published page republished — the rollout-truncated credit horizon (~8–16 turns,
  not 300), the anchor that never faded (0.0990 → 0.0946 over run I), ±5.3 not ±2 for a 48-game read, the wrong "wins ~2 %"
  sentence; hypothesis (b) rewritten with the entropy bonus as the prime suspect. **Step 2 half-done**: both review handoffs
  acked (07:20Z) with the paired-bench protocol adopted (scout 48 / locked ≥144 confirm / 400+400 promote) and two scopings
  stated (stages 2–3 spec-first; the cluster arms exploratory); the target-KL aggregation repair queued as a trainer change.
  Next: Gate 0's charters (the corrected instrument on fixed observations; the rollout telemetry; the independent critic
  calibration), then the entropy-zero same-seed staged arm on the host. — coordinator
- 2026-08-31 07:4xZ: **protocol work landed and a first exploratory peek.** (1) **The locked confirmation panel** —
  `local_claude_1/nn-bot/locked-panel-seed1.jsonl` (`ac9787ac`): 72 corpus maps (widths 16/18/20/22: 20/15/18/19), seed 1,
  disjoint from the 24-map scout panel by map hash, smoke.py's draw rule, checksummed; 144 games both seats — the adopted
  protocol's confirmation tier. (2) **i2's mid-run salvage benched** (exploratory; the salvage upload works —
  `mid-run-latest.pt` at update 1,583 fetched by `yt read-file`): **7 of 48, 129.6 to 188.5**, purchases 42 of 48, the
  clone's profile intact (chop 88 / harvest 38 / plant 25), 2 loop games — in the clone's band at an age where every
  full-parameter run had collapsed; within scout noise of run I's same-age readings, as the review predicted for two nearly
  identical anchors (0.100 vs ~0.097). Its long run (~14,600 updates) is the staged line's real overnight answer.
  (3) A transport repair candidate for the card: teach `scripts/inbox_sweep.py` that a superseded message is discharged when
  its successor is acked — the one remaining ack-chain leak (today it cost one formality ack); to be chartered with both
  bots' reproduction, not patched quietly. Also noted: `ppo-yt-a2` was preempted ~05:55Z and restarted from scratch (no
  resume); its 17-hour limit means it dies at ~19:55Z around 50 M decisions — the salvage copy will carry its last
  checkpoint. — coordinator
- 2026-08-31 08:1xZ: **Gate 0's measurement half delivered by claude_1 in 40 minutes and merged (`8451e144`; 47 tests
  verified here).** The instrument's r2 redesign (its reviewer's blockers folded): the causal contrast is **FULL vs NO-V** on
  identical restored moments, with a FULL-detached-V structural control; every before/after network judged on **one common
  512-position census** (content-hashed); the clone's one-group optimizer detected and reported, not crashed on. The critic
  calibration scores predictions against **realized** return-to-go from complete games, sliced by turn bucket / map size /
  seat / row class, nulls where a statistic has no meaning. **The three instrument runs are on the host now** (the clone under
  G's recipe writing the census — every field checked against G's own start record — then g@500 and h@500 on that census; one
  correction: the absolute maps path). The calibration runs (the clone, I@1000; argmax + the scope pass) follow. **The VM disk
  incident ruled**: the volume hit 0 bytes free during the work; claude_1's declared reclamations (its cache, its month-old
  scratch, and the truncation of codex_1's 258 MB runaway launcher capture, tail saved) are accepted as emergency response;
  the dataset is intact (its own follow-up); **the open repair — rotation for the launcher captures — goes to the owner's
  queue** (their launcher). codex_1's telemetry half is still pending; the entropy-zero arm waits on it. — coordinator
- 2026-08-31 08:3xZ: **the three instrument runs executed on the host (07:54–07:55Z) and the outputs handed to claude_1**
  (copied to the VM; progress message 08:30Z; the causal arms live under `next_update`: full / full-detached-value / no-value,
  on both fresh and resumed moments, judged on the common census `17612b22…`). **One raw fact already on the table:
  g@500's entire 4,096-row on-policy rollout contained zero observed terminal rewards** (`reward_rows_nonzero = 0`; 1,659
  turns completed, raw advantage std 0.030, rollout explained variance 0.21) — the review's §4 mechanism (normalized
  bootstrap noise at full policy scale) has its first direct measurement. The critic calibration's three runs (the clone;
  I@1000 argmax; I@1000 in the training decoding) run on the host now. claude_1's verdict note closes the measurement half;
  codex_1's telemetry half is still pending and gates the entropy-zero arm. — coordinator
- 2026-08-31 08:4xZ: **the critic calibration measured (96 complete episodes each, 07:57–08:00Z) and handed to claude_1.**
  Raw: the clone's never-trained value head reads worse than the mean (explained variance −0.20, correlation −0.10);
  **I@1000's critic — after its 300-update warm-up and 700 training updates — reads explained variance 0.04 against the
  realized return, where the trainer's own self-referential log claimed 0.6–0.97; its slope is ~4.5** (predictions vary
  ~4.5× less than reality — far too timid). The review's §5 claim (the logged number means self-consistent, not true) is
  confirmed by measurement. **One anomaly flagged, not interpreted: the scope-decoding run reports 222 illegal commands**
  where masked paths should make that impossible — claude_1 checks whether the counter or the decoding path is at fault
  before any scope number is quoted. All Gate-0 measurement inputs are now in claude_1's directory; its verdict note closes
  the half. — coordinator
- 2026-08-31 09:3xZ: **the Gate 0 batch ruled** (fifteen messages in ninety minutes, four agents). codex_1's trainer half
  verified (57 tests from a clean checkout) and **merged (`f8d9e8c2`)**: full-buffer terminal/reward counters, the GAE-source
  decomposition (rewards / edge bootstrap / intermediate critic, with reconstruction error), the epoch-wide row-weighted
  target-KL guard. **claude_1's corrected verdict is the gradient verdict of record**: the critic's trunk push is **12.3 % of
  the policy's at the clone, 0.2 % by update 500** (a local statement; the handoff-moment mechanism confirmed, the ongoing-
  erosion mechanism not) — and the anchor pushes the trunk at 13 % at g@500, flagged for later. The 222 = the both-seats
  movement-conflict audit (chatgpt_1 and claude_1 converged independently; a 240-game random-legal control on top).
  **chatgpt_1's two blockers upheld**: the calibration's four repairs chartered; the NO-V/FULL-detached-V equality premise
  falls to the shared global clip (B−A = clip coupling; C−A = the total marginal effect). **Two corrections of my own
  wording** (per its republished notes): the zero-reward fact was a minibatch fact; slope 4.46 at correlation 0.31 = spread
  ratio ≈ 14 with weak ranking. **One miss of mine found by the 08:35Z geometry note**: the clone's Gate-0 measurement ran at
  32×128 while g/h are 128×32 — the clone gradient row is exploratory until the rerun; g/h rows stand. **The r3 charter to
  claude_1 (09:35Z, supersede-to-amend)**: the instrument's clip-frame repairs + second seed + decision margins; the
  calibration's matched-population collector and three weightings; then the geometry rerun on the host. **Stage 1 adopted as
  E01/E00 fresh arms under one post-Gate-0 pin** (GOAL.md step 4 updated). Transport: entries 28–30 quarantined at the
  sender's own request; all marks unblocked. — coordinator
- 2026-08-31 09:5xZ: **the r3 round — an instrument defect found by running the demanded control, and the day's best chain of
  review.** chatgpt_1's identity blocker was right in premise (the shared global clip couples the NO-V and detached arms);
  claude_1 measured that channel too small for the observed divergence and, running the control the blocker demanded, found
  the real fault: **`Optimizer.load_state_dict`'s no-op cast aliases the saved Adam moments, so every arm stepped the caller's
  state in place — the first round's `adam-resumed` figures (all three reports, both blocks) are arm-order contamination and
  are quarantined.** `adam-fresh` rows untouched (fresh optimizer per arm). r3 delivered with the fix, the coupling reported
  as coupling, a common-clip counterfactual variant, decision margins, a second minibatch seed, and the matched-population
  calibration collector — verified here (64 tests) and **merged (`78a9e394`)**. **The full rerun is executing on the host**:
  the clone at the correct 128×32 geometry (census v2), g@500 and h@500 on it, then the three matched calibrations (96
  declared cells, 160-episode later arms). Gate 0's measurement half closes when claude_1 reads the rerun into the verdict's
  final form. Deferred to codex_1's post-Gate-0 bundle: the environment's rejection-counter split by seat/reason and a
  map/seat schedule for seed-level population matching. — coordinator
- 2026-08-31 10:1xZ: **the v2 rerun finished (09:16–09:51Z, all six measurements) and shipped to claude_1; two more blockers
  upheld.** (1) chatgpt_1's 09:41Z margin-crossing defect is real — the post-update margin was computed from the re-sorted
  winner, non-negative by construction, so a flip could never register (its closed-form falsifier: `[2,1] → [0,3]` reports
  growth) — **r4 chartered to claude_1** (the signed margin against the original winner + four synthetic tests); the v2
  `decision_margin` subtrees are invalid; the three gradient measurements re-run after r4 (minutes). Everything else in v2
  stands. (2) chatgpt_1's 09:47Z platform confound in my Stage-1 allocation is real — one arm per platform would make entropy
  collinear with the machine — **both E01/E00 arms run on the cluster, same payload and resource class** (GOAL.md step 4
  amended); the host stays the evaluation machine; the equivalence preflight rides along with the first arm. Housekeeping:
  the VM's volume is back at 97 % (762 MB) a few hours after the emergency — the launcher-log rotation question in the
  owner's queue is getting urgent. — coordinator
- 2026-08-31 11:3xZ: **closing round two — five more blockers ruled, r4 merged (`6c2fc00a`, its suite verified here).**
  Upheld: (1) the state-distribution scope — the G/H rows are fresh-game local counterfactuals; Gate 0 closes as
  `EARLY_GAME_LOCAL_ONLY`, the staggered-population measurement deferred to the post-Gate-0 bundle; (2) the margin-tie
  defect (baseline ties fake crossings) → r5; (3) the epoch KL is a path average → codex_1 adds the post-epoch no-grad
  final-policy KL and the guard follows it; (4) the clone row omitted G's 300-update warm-up — re-labelled *hypothetical
  no-warm-up first update*; the v3 rerun adds **G@250** (inside the warm-up, policy bit-frozen) as the near-handoff row,
  read as "50 updates before the unfreeze"; (5) **the frozen Gate 1 for E01/E00 adopted as the definition of record**
  (one correction: the locked panel is 144 cells → the confirmation pools 288; the extension offer to 96 maps stands) —
  written into GOAL.md step 4. The closing2 charter (11:35Z, one handoff, both bots): claude_1 = r5 + the G@250 runbook row
  + the verdict's scope wording; codex_1 = the final-policy KL. The v3 gradient rerun (minutes) runs the hour r5 lands;
  Gate 0 then closes on claude_1's final verdict. — coordinator
- 2026-08-31 12:3xZ: **closing round two delivered and merged (`e7722474`).** codex_1's final-policy KL guard (58 tests
  verified here; the guard reads the post-epoch policy; `path_kl_*` retained honestly; ~12 % epoch cost at our sizes) and
  claude_1's r5 (72 tests; the tie denominator with the blocker's no-op falsifier as a test that fails against r4; the G@250
  warm-up-tail runbook row; the verdict's two scope limits). **chatgpt_1's 11:45Z panel correction adopted**: 144 cells
  suffice; the confirmation interval is the 144-unit clustered/repeated-measure bootstrap of the per-cell two-age mean delta
  (never a 288-row pool); positive at each age separately; clone non-inferiority 6 net cells of 144; four frozen outcomes
  incl. INCONCLUSIVE — GOAL.md step 4 re-frozen. **The v3 gradient set is running** (clone-no-warmup-hypothetical, G@250,
  G@500, H@500 — all on census v2, r5 code); outputs ship to claude_1 on completion and its final verdict **closes Gate 0's
  measurement half**. — coordinator
- 2026-08-31 12:4xZ: **the v3 gradient set done (12:04–12:08Z) and on claude_1's machine; the G@250 row answers the handoff
  question.** At the warm-up's tail the critic's trunk push is **0.2 % (plan rows) / 0.5 % (troll rows) of the policy's** —
  against the no-warm-up clone's 5 % / 29 % — so the warm-up does exactly its job: by the unfreeze the value-gradient path is
  negligible, and with g/h@500 also at ~0.2 %, **hypothesis (a) is effectively acquitted for the warm-up runs** (as an
  early-game local statement, per the frozen scope). The live suspects narrow to the entropy bonus (Stage 1's E01/E00 under
  the frozen gate) and the normalized bootstrap noise (now measured in every run by the merged telemetry), with the
  plan-semantics design behind them. claude_1's final verdict formalizes this and closes Gate 0's measurement half. — coordinator
- 2026-08-31 13:1xZ: **the first-day progress report written and sent to chatgpt_1 at the owner's request**
  (`local_claude_1/nn-bot/PROGRESS-2026-08-31.md`; the 13:10Z ack-required handoff carries it): the review-to-programme
  arc, the five merged Gate-0 deliveries, the six instrument defects caught before any number stood, the measured facts
  with their scopes, the frozen Stage-1 gate, and the open items by name. Corrections invited with standing evidence that
  the invitation is real. — coordinator
- 2026-08-31 13:2xZ: **the deep-run salvage peeks (exploratory, mid-run, unpaired) close two questions early.**
  `a2` (full-parameter, run-D recipe) at update 6,239: **2 of 48, 87.8 to 149.8** (39 games ended early) — five times the
  depth of any host run, and argmax play did not recover; the 29 % practice win rate was hollow to the end. `e2` (the
  corrected objective) at 3,198: **3 of 48, 77.4**. `i2` (staged, the leash pinned at 0.1) at 5,414: **4 of 48, 122.8,
  profile largely intact (17 early, 1 loop)** — the pinned anchor slows the staged drift (the host's run I was at 5–6 by
  ~2,500 under ~0.095) but does not stop it. **Read together: the long-horizon answer is negative for full-parameter PPO as
  configured, and the anchor's level is acquitted as the staged drift's cause** — the suspicion now rests wholly on the
  entropy bonus (Stage 1's E01/E00 under the frozen gate) and the normalized bootstrap noise (measured henceforth by the
  merged telemetry), with the plan semantics behind them. The final snapshots (~19:00–20:00Z) get the pinned benches for
  the record; the arms launch when Gate 0 closes. — coordinator
- 2026-08-31 15:5xZ: **the VM's disk hit 100 % a second time (24 MB free) and silently stalled every agent since ~09:00Z** —
  the launcher was active but each bot session failed on the full volume; that is why no Gate-0 verdict and no report receipt
  arrived for hours. **The filler is identified and is not ours: the owner's own codex session transcript**
  (`~/.codex/sessions/2026/08/28/rollout-2026-08-28T19-05….jsonl`, 311 MB and growing at measurement time, plus its 161 MB
  thread database) — untouchable without the owner's word. **Declared emergency action, minimal and ours only**: six stale
  agent scratch items removed from `/tmp` (codex_1's old gate extract 158 MB, pytest scratch, four old extracts) → 348 MB
  free, writes verified working; nothing under `~/.codex`, `~/.claude`, `preserved/` or the owner's run touched. **The cure
  needs the owner** (the volume refills in about a day at the transcript's growth): prune or relocate `~/.codex`, and the
  launcher-log rotation still pending — both in the owner's queue. The bots should resume on their next poll. — coordinator
- 2026-08-31 17:2xZ: **GATE 0 IS CLOSED.** claude_1's final verdict (16:41Z, `7aa2889e`) accepted and merged (`0e412b57`):
  under the two frozen scope limits, the critic-to-policy trunk path is **not material in G and H as configured** — across
  eighteen readings (three checkpoints × three optimizer variants × two minibatch seeds) dropping the critic's objective
  changed **0 of 206 purchase and 0 of 306 movement decisions**, zero margin crossings, `tied_baseline_rows` 0; the clip
  channel measured and closed (`+common-clip` arms exactly 0.0 apart); **the 300-update warm-up does real work** (the trunk
  push 16.4 % → 0.37 % across it). Surfaced for Stage 1: **the anchor is the large trunk force at update 500 (13.4 % at G,
  18.4 % at H, pointing against the policy)** and **the critic is blind before turn 25** (realized EV −0.004 to 0.006 in the
  first three turn buckets) exactly under the ~13-turn credit window — the sharpest reason the staggered population stays on
  the deferred list. Provenance verified by hashes; 129 tests on the merged tree. **STAGE 1 LAUNCHED 17:1xZ**: `ppo-yt-e01`
  (`fe522c8c…`, entropy 0.01, the control) and `ppo-yt-e00` (`48469b15…`, entropy 0, the treatment) — same clone, seed 41,
  payload, resource class; the run-I recipe; 60 M decisions under 17-hour limits with salvage; the frozen 144-unit
  repeated-measure gate decides. The a2/e2/i2 finals (~19:00–21:00Z) get their pinned benches for the record. — coordinator
- 2026-08-31 18:4xZ: **the VM's disk crisis is over — the owner attached a 100 GB disk** and it is live: formatted ext4,
  mounted at `/data` (fstab by UUID, `nofail`), owned by the user, with `/data/scratch` for the agents' big extracts and
  `/data/archive`. **Root went 100 % → 88 % (2.3 GB free)**: the five idle worktrees (~2.2 GB — claude_1's lfs/lfsverify/
  registry, plan, plan-agent) moved reversibly to `/data/archive/worktrees-2026-08-31/` (git worktree links pruned; restore =
  move back + `git worktree repair`). The owner's running codex session and `~/.codex` untouched — its transcript remains the
  one growing item on root, now with days of headroom; pruning or relocating it stays the owner's call, and the launcher-log
  rotation offer stands. Agents: prefer `/data/scratch` for anything over ~50 MB from now on. — coordinator
- 2026-08-31 18:5xZ: **`ppo-yt-e2` aborted on the owner's word** ("abort e2"; op `aa7fe45a…`, state `aborted` confirmed) —
  its family (full-parameter + corrected objective) was refuted twice over and its remaining seven hours of a 32-core slot
  bought nothing decision-relevant; the salvage copy (update ~7,100 curve and checkpoint) stands as its record. Still
  running: `a2` and `i2` to their natural wall-clock limits (~20:50Z / ~21:40Z; their finals get the pinned benches), and
  Stage 1's `e01`/`e00`. — coordinator
- 2026-08-31 21:3xZ: **a pool-wide preemption at ~20:10Z restarted i2, e01 and e00 from scratch** (no resume by design; the
  salvage of i2's deep run was overwritten by its restart — the benched u5,414 peek remains its deep record). Consequences:
  **the E01/E00 pair restarted together, so the paired design holds** — both arms at ~7.9 M steps, the Gate-1 confirmations
  land at their fixed updates and the verdict shifts to ~11:00Z 09-01; i2's rerun counts as a fresh staged seed. **a2 was
  not preempted and completes its full 60 M budget ~21:50Z** — the first job to reach its budget; its final gets the pinned
  bench tonight. — coordinator
- 2026-09-01 00:4xZ: **the full-parameter family's record point, at complete budget: `a2` finished its 60 million decisions
  (update 14,649) and its final benched 0 of 48, 50.9 points to 134.4, with 42 of 48 games ended early and 4 loop games.**
  The curve of that family now reads: the clone's 9 → 3–5 by update 500 → 2 by ~6,000 → **0 at 14,649**. Full-parameter PPO
  from the clone, as configured, is monotonically destructive at every measured depth — the family is closed as evidence,
  not just suspended. What remains live: the staged line (i2's fresh seed grinding), and Stage 1's E01/E00 pair (~11:00Z
  verdict under the frozen gate). — coordinator
- 2026-09-01 02:2xZ: **a second pool preemption (~02:00Z) restarted `e01` and `i2` from scratch while `e00` kept running**
  (37.0 M). The paired design survives — the gate compares the arms at fixed updates, and a same-seed restart replays the
  same trajectory — but the wall-clock slips: `e00` completes ~08:00Z, `e01` ~17:30Z, **the Gate-1 verdict moves to ~18:00Z
  09-01**. The pool's preemption weather is now the schedule's main noise; nothing to fix (salvage covers ends, budgets are
  consistent), only to note. — coordinator
- 2026-09-01 03:4xZ: **the day-two progress report written and sent to chatgpt_1 at the owner's request**
  (`local_claude_1/nn-bot/PROGRESS-2026-09-01.md`; the 03:45Z ack-required handoff): Gate 0's close with the verdict's
  numbers, the full-parameter family closed at complete budget, Stage 1 under the frozen gate with the preemption weather
  (verdict ~18:00Z), the disk resolution, and the eliminated-vs-standing diagnosis table. — coordinator
- 2026-09-01 08:0x–11:0xZ: **the cluster arms died, their salvage was rescued, and it carries the entropy answer on the
  training side — plus a depth result that reframes step 5.** What happened: e00 and e01 both lost their jobs in the same
  minute (06:03Z, a cluster-wide preemption wave) and sat pending 1.5 h. Attempt durations tell the story of the whole
  cluster experiment: e00 0.28 h then 9.86 h; e01 0.73 h, 5.90 h (aborted by the controller agent), 3.93 h. **Every
  preemption restarts from scratch**, and the half-hourly salvage keeps only the newest checkpoint, so five attempts and
  ~20 job-hours produced no age-matched scout series at all.
  - **Rescued before the pending attempts could overwrite it** (`/home/tarstars/nn-data/ppo-yt-e0{0,1}-midrun-0901/`):
    e00's checkpoint at **u12,250** (50.2 M turn-steps) and e01's at **u3,250** (13.3 M), plus both complete training logs
    from update 1 (12,352 and 3,417 updates).
  - **The entropy read, training side** (`entropy_log_read.py`, new; paired per-250-update blocks over the shared range
    u1–u3,417, same seed 41, bootstrap over blocks because neighbouring updates share a rolling 1,000-episode window):
    the knob does what it says — entropy 0.934 → 1.007, delta +0.073, interval [0.056, 0.089] — **and buys nothing.**
    Win rate delta −0.0013, interval [−0.0063, +0.0041], crosses zero. Referee margin delta −0.70,
    interval [−1.15, −0.17]: marginally *worse* with entropy. Explained variance, approximate KL, clip fraction and value
    loss all cross zero. Anchor agreement 0.978 → 0.975 (more exploration, slightly less clone-like), as expected.
  - **The depth result.** e00 (entropy off) ran to u12,250 — 50 M turn-steps, 9.5 hours — and its **training win rate is
    flat**: 0.180 at u500, 0.182 at u12,000. The referee margin got *worse* over that span (−51.1 → −53.4). The only
    quantity that climbs is explained variance (0.21 → 0.48): the critic learns to predict returns while the policy does
    not improve.
  - **Both salvaged checkpoints benched** (48-game scout, argmax both seats, champion `0e92f8fa`):
    e00 @ u12,250 → **2/48**, score 117.3 vs 185.8; e01 @ u3,250 → **9/48**, score 128.6 vs 183.2. Not age-matched, so
    this is *not* an entropy read — it is another point on the depth curve, and it lands exactly where the curve predicts.
  - **The instrument fact worth keeping**: both checkpoints logged an identical training win rate of 0.185 while benching
    2/48 (4 %) and 9/48 (19 %). **Training win rate does not track bench win rate** — it cannot be used as a proxy for the
    gate, which is what the frozen protocol already assumed and now has direct evidence for.
  - **The depth curve, everything ever benched, one place** (48-game scout, wins of 48): f2 5/7/2 at u500/1000/1500;
    g 5/4; h 3/8/2; i 9/10/9/6/5 at u500…u2500; e01 9 at u3,250; i2 4 at u5,414; e00 2 at u12,250; a2 0 at u14,649.
    The shape is unmistakable: **the bench peaks early, near the clone, and decays with training.** Nothing in any run has
    ever exceeded 10/48 (21 %); parity needs 24/48.
  - **Decisions taken.** (1) The two pending cluster ops were **aborted** — at 60 M steps / 17 h they were the wrong shape
    for a gate that needs only u2,500, and would have burned another ~20 job-hours to be preempted again. (2) The paired
    arms were **relaunched on the host**, which is idle, free and cannot be preempted, and which runs both arms on one
    platform so the comparison stays internally valid: `ppo-host-h00` (entropy 0.0) and `ppo-host-h01` (entropy 0.01),
    seed 41, plan-critic scope, sized to u2,709 — verified to differ in exactly three fields: `entropy_coef`,
    `output_dir`, `run_name`. 14 cores total at nice 15, inside the owner's cap. Started 10:58Z; ~10 h at the observed
    rate, so the scouts land this evening and the frozen Gate 1 can be computed on age-matched benched checkpoints as
    written, rather than on the confounded pair above. — coordinator
- 2026-09-01 11:3x–12:0xZ: **the cluster path repaired and step 4 relaunched on both platforms.** The reason five
  attempts produced nothing was structural, not bad luck: a preempted job restarts from scratch and the salvage kept only
  the newest checkpoint. Fixed at the source — `yt_ppo_entrypoint.py` now keeps **every** checkpoint under its own name
  (`mid-run-<checkpoint>.pt`), uploading each exactly once, oldest first, capped per beat so no single heartbeat stalls;
  `mid-run-latest.pt` still holds the newest for callers that want one file. A checkpoint is ~180 KB, so a whole long run's
  series costs a few megabytes — far less than one lost run. Four tests pin it (`tests/test_yt_ppo_entrypoint.py`): every
  checkpoint kept, none re-uploaded on a later beat, the per-beat cap with the backlog draining oldest-first, and a failing
  upload never killing the heartbeat. The 19 launcher tests still pass.
  **Relaunched in the gate's shape**: `ppo-yt-e00b` (`942710be…`, entropy 0.0) and `ppo-yt-e01b` (`c875f4ec…`, entropy 0.01)
  — the e00 recipe read back from its own `yt_run_config.json` and reproduced field for field, pool `research_gpu` on
  `gpu_starfield_24g_cloud`, 32 CPUs, but **11.1 M steps under a 6-hour limit instead of 60 M under 17 hours**. That is the
  correction that matters: the gate reads nothing past update 2,500, so a 17-hour job was always the wrong shape — it made
  preemption near-certain while buying updates no measurement would ever look at. At the observed cluster rate the new
  shape needs ~2.1 h, and the budget is consistent (steps well inside the wall-clock limit).
  **Both platforms now carry both arms**: the cluster pair as `coordination/GOAL.md` step 4 requires, and the host pair
  (`ppo-host-h00`/`h01`) behind it as the un-preemptible guarantee. Each pair differs in exactly one field, so the
  reviewer's platform-confound blocker holds within each; agreement across them is replication, not a substitute. One
  platform difference to declare in the Gate-1 handoff: the cluster arms train on the launcher's default one-in-five map
  slice, the host arms on the full 31,088-map corpus — identical within each pair, so neither comparison is affected.
  — coordinator
- 2026-09-01 12:2xZ: **the bootstrap-noise question is answered, and it is worse than "noisy" — the trained head never
  sees a reward at all.** New instrument `credit_path_read.py` (4 tests) reads the `rollout_credit` telemetry the Gate-0
  work added. Over e00's 12,352 updates and 50.6 million rows, and independently over e01's 3,417 updates and 14.0 million:
  - **PLAN rows: 0 of 16,879,270 carried a terminal event, and 0 ever saw a non-zero reward** — 0 of 12,352 updates had
    any. Bootstrap share of the target 0.977; the credit trace reaches a real terminal on 1.8 % of rows.
  - **TROLL rows**: 59,215 of 33,714,522 carried a terminal event (0.176 %), reward on 0.175 %; bootstrap share 0.974.
  - e01 reproduces every figure to the third decimal, so this is structural, not a sampling accident.
  **Why it is structural, verified in the trainer**: `--reward-credit executing` (the default, `train_ppo_full.py:1446`)
  keeps the turn's reward only where `turn_completed == 1` and zeroes the rest; a PLAN mini-step is never the mini-step that
  executes the turn, so PLAN rows receive reward zero by construction. And under `--train-scope plan-critic` — the winner's
  stage-4 recipe, the scope every recent run uses — **the plan head is the only actor being trained**: TROLL rows are
  frozen and excluded from the policy terms. So the full chain of the policy's learning signal is:
  *outcome → critic (through 0.17 % of rows) → plan head (through nothing else)*. The plan head is optimized entirely
  against the critic's opinion, and the critic's own targets are 97 % bootstrap — while Gate 0 measured that critic at an
  explained value of 0.04 against realized returns it logged as 0.6–0.97.
  **This explains the depth result.** Training longer does not add outcome information to the plan head, because no amount
  of training changes that its reward channel is empty; it only fits the critic's errors more closely and drifts further
  from the clone. That is exactly the observed shape — flat training win rate over 50 M steps, bench decaying 9/48 → 2/48
  with depth, anchor agreement the only thing holding it near the clone.
  **For step 5 this ranks the levers on evidence rather than taste**: entropy is answered and is not it; the credit path
  is. The reviewer's ranked item "true long-horizon credit via longer/episodic rollouts" is the one the measurement points
  at — with the specific, testable form that the plan head needs a reward channel that is not empty (reward credited to the
  PLAN row that owns the turn, or episodic returns, or a rollout long enough that the 32-mini-step buffer stops cutting
  99.98 % of traces before any terminal). A bare λ=1 under the current buffer remains excluded, as the frozen text says.
  Not proposed as a build: this goes to the reviewer with the Gate-1 verdict, and the design change is spec'd and reviewed
  before anything is written. — coordinator
- 2026-09-01 13:0xZ: **CORRECTION to the 12:2xZ entry, made within the hour and before anything was built on it.** I wrote
  that "the plan head never sees a reward at all" and that its signal reaches it "through nothing else" than the critic.
  **That was wrong, and it was my misreading of my own instrument.** `compute_gae` sets the trace factor to *exactly 1.0
  inside a turn* (`train_ppo_full.py:501–545`, and its docstring says why: multiplying by λ per mini-step would hand the
  plan row only λ^k of its own turn's reward, which amendment (4) forbids). So a turn's reward reaches that turn's PLAN row
  **undiminished, through the trace** — it simply does not sit in the plan row's own reward slot, because
  `--reward-credit executing` puts it on the mini-step that executed the turn. The zero I measured
  (`observed_nonzero_reward_rows = 0` over 16.9 M plan rows) is a structural artefact of *where the number is stored*, and
  carries no meaning on its own.
  **What is true, measured on the right quantity** — the reward's share of the advantage's magnitude, from the components
  the trainer already records by replaying the same GAE with the other inputs zeroed:
  - **PLAN rows: observed reward supplies 2.32 % of the signal; the critic's own values supply 97.68 %.** Reward enters the
    plan rows' advantage in 12,201 of 12,352 updates (98.8 %) — present, but small.
  - TROLL rows: 2.58 % reward, 97.42 % critic. e01 reproduces both to two decimals (2.29 % / 2.56 %).
  - Unchanged and still the point: bootstrap share of the target 0.977, and the credit trace reaches a real terminal on
    only 1.8 % of rows before the 32-mini-step buffer cut.
  **The finding survives the correction, in weaker and more accurate form**: the plan head is trained on a signal that is
  ~98 % the critic's opinion and ~2 % observed outcome, against a critic Gate 0 measured at an explained value of 0.04. It
  still explains the depth curve — more training fits more of the critic's error — but "the reward is absent" is not the
  diagnosis, "the reward is 2 %" is, and the two point at different fixes.
  The instrument and its tests were corrected in the same hour: `credit_path_read.py` now reports
  `reward_share_of_signal_percent` as its headline, the misleading `signal_is_purely_bootstrap` flag is gone, and two new
  tests pin that a row-slot zero must not be reported as an absent reward (6 tests). The owner was told directly.
  — coordinator
- 2026-09-01 08:4xZ: **flush entry written at the owner's request** —
  `coordination/HANDOVER-2026-09-01-entropy-gate-and-credit-path.md`: the four arms in flight and their exact identities,
  the whole remaining recipe from retrieve to verdict, the four instruments built today with what each pins, the three
  results (entropy null / depth harmful / the credit path at 2.3 % with my correction in full), the fix menu awaiting the
  owner's choice, Track C halted for the two reviews, and the standing constraints. — coordinator
- 2026-09-01 11:0xZ: **step 4 — both cluster arms COMPLETE, retrieved, the training-side read done; the benches are
  running.** `ppo-yt-e00b` (entropy 0) finished 2,709 updates in 1.90 h, `ppo-yt-e01b` (entropy 0.01) in 1.76 h — no
  preemption this time; twelve checkpoints each (updates 250 … 2,500 and 2,709) under
  `yt_work/ppo/ppo-yt-{e00b,e01b}-output/extracted/outputs/` (archive sha256 `175c656e…` / `f33560ba…`). **Identity
  verified from the retrieved run configs: the two trainer argument lists differ at exactly two positions — `entropy_coef`
  (`0.0` vs `0.01`) and the run name — same seed 41, same budget (11,100,000 turn-steps = 2,709 updates of 4,096), same
  clone `checkpoints/clone.pt`, same map slice, same library, same 64-core class.** The clone they started from and are
  anchored to is `/home/tarstars/nn-data/clone-2026-08-30-a/clone-pilot.pt`, sha `970097ed…`, confirmed by hash.
  **Training-side read (`entropy_log_read.py`, 250-update blocks, 11 blocks over the full 2,709 shared updates;
  `/home/tarstars/nn-data/bench-0901/entropy-log-read-cluster.json`):** the bonus raises entropy by **+0.068
  [0.051, 0.083]** — the knob works — and buys nothing: win rate on−off **+0.004 [−0.004, +0.011]**, referee margin
  **−0.02 [−0.56, +0.52]**, both straddling zero; anchor agreement 0.985 vs 0.980. **Replicated on the host pair** at its
  1,753 shared updates (8 blocks): entropy +0.064 [0.038, 0.094], win rate +0.0006 [−0.006, +0.007], margin +0.25
  [−0.50, +1.03]. This is evidence, not the gate. **Benches running on this host at nice 19** (the two trainings keep
  priority; 20 cores, load ~25): the scouts for both cluster arms at updates 500/1,000/1,500/2,000/2,500 on the 48-cell
  panel (`bench_ages.py`, one job per arm, two threads each), and the clone on the locked 144-cell panel (one thread) for
  the gate's non-inferiority term — none existed. First attempt of all three failed in a minute: `bench.py` was run with the
  system Python, which has no PyTorch; relaunched with the math venv's Python (`--python`). Next: the confirmations at
  1,500 and 2,500 on the locked panel for both arms, then `gate1.py`. — coordinator
- 2026-09-01 12:4xZ: **step 4 — the scout curves of both cluster arms, complete (48-cell panel, both seats, argmax play,
  same flags by construction; `local_claude_1/nn-bot/results/entropy-gate-0901/scout_table.py` prints this from the bench
  files; 0 illegal commands, timeouts or referee errors in all ten benches):**

  | update | E00 (entropy 0) wins/48 (seat 0 + 1) | E01 (entropy 0.01) wins/48 | paired E00 − E01 (won only by E00 − only by E01) | mean score E00 / E01 vs the champion's file |
  |---|---|---|---|---|
  | 500 | 10 (4 + 6) | 8 (3 + 5) | +2 (4 − 2) | 133.2 / 127.2 vs 186.7 / 181.6 |
  | 1,000 | 12 (6 + 6) | 6 (2 + 4) | +6 (7 − 1) | 135.7 / 125.7 vs 185.6 / 187.6 |
  | 1,500 | 9 (4 + 5) | 10 (5 + 5) | −1 (1 − 2) | 132.4 / 132.4 vs 186.5 / 185.3 |
  | 2,000 | 6 (3 + 3) | 6 (3 + 3) | 0 (1 − 1) | 129.5 / 127.8 vs 188.5 / 187.7 |
  | 2,500 | 7 (3 + 4) | 8 (3 + 5) | −1 (2 − 3) | 129.7 / 129.2 vs 186.5 / 183.0 |

  Read as a scout (±5 wins): no age separates the arms; the +6 at 1,000 is the only reading outside ±5 and it is not
  repeated. Both arms decay with depth (12 → 7 and 10 → 8 from update 1,000 to 2,500), the shape every run has shown. The
  clone on the locked 144-cell panel, benched today for the non-inferiority term: **26 of 144** (14 + 12; 18 %), consistent
  with its 9-of-48 bar. The confirmations at 1,500 and 2,500 on the locked panel are running (both arms, nice 19, sharing
  the machine with the host trainings at ~85 of 144 games per arm at 12:5xZ); `gate1.py` runs the moment they land.
  — coordinator
- 2026-09-01 13:4xZ: **STEP 4 DONE — the frozen Gate 1 verdict: `ENTROPY_NOT_CONFIRMED`**
  (`local_claude_1/nn-bot/GATE1-VERDICT-2026-09-01.md`; the JSON and all fifteen bench files in
  `local_claude_1/nn-bot/results/entropy-gate-0901/`). Confirmations on the locked 144-cell panel, 0 faults: **E00 24 and
  21 of 144, E01 23 and 22 of 144** at updates 1,500 and 2,500; paired effect E00 − E01 **0.000 per cell, 95 % interval
  [−0.017, +0.021]** (10,000 clustered draws over the 144 units); per-age +0.007 / −0.007, so not positive at each age; clone
  non-inferiority holds (net 0 cells of 6 allowed; the clone 26 of 144 on the same panel); margin −1.6 [−4.7, +1.2], not the
  gate. The entropy bonus is acquitted on every reading — training side, scouts, locked panel — and both arms still decay
  with depth. Next per THE PLAN: the handoff to chatgpt_1 for the Gate 1 review; then step 5's decision, which the credit
  measurement points at the reward path (the fix menu with the owner). The host pair (update ~2,670 of 2,709 at 13:5xZ)
  finishes within the hour; its benches are replication only and run at low priority afterwards. — coordinator
- 2026-09-01 15:5xZ: **step 5 prepared, not launched — the reward-path arm is one command away from the owner's word.**
  The entropy verdict makes E01 (entropy 0.01, `wood_shaping 0 + end_wood 4`, seed 41) the ready-made control for the
  reward-path test, so only the treatment arm is needed: `ppo-yt-r22` = the same recipe with `--wood-shaping 2.0
  --end-wood 2.0` (wood's value still 4, half of it paid on delivery). Dry-run prepared (`yt_work/ppo/ppo-yt-r22/`,
  nothing submitted): its trainer arguments differ from E01's at exactly the two wood flags and the run name; the payload
  (maps slice, clone, library, trainer) is byte-identical by manifest. The first dry run had silently changed the opponent
  pool (a mixed default instead of `champion_exact`) and the thread count — both caught by the diff and pinned. The same
  frozen `gate1.py` reads it as treatment = r22, control = e01b on the same 144 cells. Also running as replication only: the
  host pair's scouts and confirmations (eight low-priority benches, ~1.5 h). Handoff to chatgpt_1 for the Gate 1 review
  sent (pin `a7a255b8`). — coordinator
- 2026-09-01 15:5xZ: **STEP 5 DECIDED AND LAUNCHED — the reward path.** The decision on the evidence of steps 3–4: entropy
  is acquitted by the frozen gate; the credit measurement says the plan head's signal is 97.7 % critic / 2.3 % observed
  reward because wood's whole value lands on the final turn; the environment's own knob moves half of it to the turn of
  delivery. Under the goal's standing authorization (the cluster within the pool in use, consistent budgets), the coordinator
  launched the treatment arm **`ppo-yt-r22`** — `--wood-shaping 2.0 --end-wood 2.0`, everything else E01's recipe (entropy
  0.01, seed 41, 2,709 updates, `champion_exact` opponent, 64 threads), verified after the real prepare to differ from E01's
  trainer arguments at exactly the two wood flags and the run name, payload byte-identical by manifest (3.2 MB uploaded) —
  operation `907fc1d9-14f71e66-42e03e8-63f81046`, started 15:53Z, ~1.9 h expected. **E01 is the control** (same seed,
  same everything, `0 + 4`), already benched on the scout and locked panels, so the same frozen `gate1.py` reads
  treatment = r22, control = e01b on the same 144 cells — the one-variable rule holds. Next wake: monitor; on landing,
  retrieve → scouts at 500…2,500 → confirmations at 1,500 / 2,500 → `gate1.py` → the card, the board, chatgpt_1. The owner
  may stop the arm at any time; nothing else was launched. — coordinator
- 2026-09-01 16:2xZ: **step 4's replication on the host pair — the same verdict.** `ppo-host-h00` (entropy 0) /
  `ppo-host-h01` (entropy 0.01), same design on this machine (full 31,088-map corpus instead of the cluster's slice;
  identical within the pair), 2,709 updates each, benched with the same driver and flags after the trainings ended:
  locked 144-cell panel **h00 18 / 20, h01 23 / 22** at updates 1,500 / 2,500, 0 faults; frozen gate:
  **`ENTROPY_NOT_CONFIRMED`**, paired effect -0.024 [-0.056, 0.003]; margin 0.1 [-3.4, 3.3]; net cells lost 3 of 6 allowed. Scouts (48): h00 10 / 9 / 9 / 9 / 10, h01
  7 / 9 / 8 / 6 / 6 — the 48-cell look leans the other way from the 144-cell panel, which is what ±5-win noise looks like.
  Two platforms, two verdicts, one answer: the entropy bonus does not matter. Files in
  `local_claude_1/nn-bot/results/entropy-gate-0901/` (`gate1-verdict-host-replication.json`). r22 at update 616 after
  21 minutes (~1,780 updates/h; expected to land ~17:25Z). — coordinator
- 2026-09-01 16:5xZ: **claude_1's lever pricing (16:34Z handoff, three seeds) — ACCEPTED and REPRODUCED**, its branch merged
  into `main`. The critic-independent form of the credit finding: under the `0 + 4` split the only rows carrying observed
  reward are the game endings — 88 of 65,536 (0.13 %), exactly, in all three seeds; shaping on puts reward on ~1,780 rows
  (2.7 %, a factor of 20); `2 + 2` and the environment's own `0.5 + 3.5` cover the same rows to within one, differing only
  in the per-delivery magnitude; a 128-step rollout reaches a real ending 4.3× more often (1.46 % → 6.21 %), and its 1.46 %
  calibrates against the 1.8 % measured on real runs. The coordinator re-ran seed 909 with the same command: all 97 numeric
  fields identical. It arrived after r22 was launched and supports the choice; its caveat is recorded — the coverage argument
  does not by itself favour `2 + 2` over `0.5 + 3.5`; the size of the immediate signal does. If r22 moves the gate, the
  environment's default split is the natural second arm; if it does not, the longer rollout is next (the two act on
  different rows). — coordinator
- 2026-09-01 18:0xZ: **claude_1's lever pricing, third version (16:58Z) — measured in the trainer, ACCEPTED and REPRODUCED.**
  Two 40-update critic warm-ups on matched arms (actor frozen — plan gradient 0.0 on every update; same games, 54,221 turns
  both), differing only in the wood split: the reader of record (`credit_path_read.py`, re-run by the coordinator on the
  pinned logs) says the observed reward's share of the planner's signal is **1.45 % under `0 + 4` and 5.34 % under
  `2 + 2`** (3.7×), and — the sharper fact — reward enters **23 of 40 updates under `0 + 4` and 40 of 40 under `2 + 2`**:
  the split turns an intermittent signal into a continuous one. The critic still supplies ~90 % under `2 + 2`. This is the
  arm r22 is testing; the numbers say why it might work and cannot say whether it does. Branch merged. — coordinator
- 2026-09-01 18:1xZ: **r22 preempted once** — the operation shows one job aborted and one pending: the cluster took the
  slot back after update ~2,316 (last heartbeat 17:23Z) and the job restarts from scratch when a slot frees. The salvage
  did its job this time: checkpoints 250 … 2,250 are on the cluster, but **2,500 is not**, and the frozen gate reads
  updates 1,500 and 2,500 of one attempt — so the restart runs to completion and the gate reads the restart. Meanwhile
  the salvaged checkpoints are downloaded (`yt_work/ppo/ppo-yt-r22-salvage/`) and scouted at 500 … 2,000 as an early,
  exploratory look (tag `r22pre`; not the gate). Also today: the report re-issued as its sixth edition
  (`docs/reports/2026-08-30-neural-network-line-progress.pdf`, Section 3: the entropy gate, the credit path, the first
  lever; four new figures). — coordinator
