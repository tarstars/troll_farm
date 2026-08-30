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
| 3 | PPO from the clone with the clone anchor, real maps, the training pool (the linked strategies + frozen copies of the policy), a fixed bench every few days against the champion's and orchard 6's compiled files | coordinator (host); claude_1 reproduces the bench numbers | 2–4 weeks | ≥ 60 % vs the champion and vs orchard 6 on 400 games each, positive margin, three gates in a row | no gain over the clone after 2×10⁸ network decisions (mini-steps: about 7.5×10⁷ game turns, ~250 thousand games), or the policy exploits an engine hole (replay parity fails on its games) |
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
