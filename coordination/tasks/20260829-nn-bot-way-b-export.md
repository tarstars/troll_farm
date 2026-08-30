# Card 20260829-nn-bot-way-b-export — Phase 4's engineering: the network as one Rust file (built early, against the clone)

Sub-card of `coordination/tasks/20260829-nn-bot-way-b.md`. Born 2026-08-30 11:2xZ. Builder: `codex_1`. Reviewer:
`local_claude_1`; reproducer: `claude_1`. **Why now:** Phase 3 runs for days; Phase 4's tooling can be built and bedded
against the clone checkpoint today, so a passing candidate ships in hours, not days.

**What.** The exporter and the single-file bot for the network of this line — `SpatialActorCritic(plan_head=True)`
(`cgauto/train_level1_ppo.py`: the 3×3 stem, four residual blocks of width 16, the 13-plane actor, the per-candidate
plan scorer over 400 candidates whose features are computed from the planes) — replacing July's exporter/kernel pair
(`cgauto/export_d11_actor.py`, `generate_d11_actor_rust_k2.py`, `generate_d11_live_actor_v7.py`), which hard-code the
July topology and reject the plan head:

1. **The exporter** `local_claude_1/nn-bot/export_full_actor.py`: a four-key checkpoint → an int8 payload (per-layer
   scales) + a manifest; the value heads dropped; the plan scorer's two linear layers included; the manifest carries the
   plan vocabulary version, the plane sanitizer rule (planes 59–71 and 98 zeroed at plan decisions — the shipped bot
   must do exactly what the trainer did), the argmax decodings.
2. **The single-file bot** `local_claude_1/nn-bot/generate_full_bot.py` → `cgauto/submissions/candidate-nn-<name>.rs`:
   std only, one file: reads the game's text protocol (the same parser lineage as the champion's file), builds the 104
   planes itself (the plane code lifted from `rust/src/rl_full.rs` — one source of truth; the generator copies the
   functions it needs, it does not reimplement them), runs the int8 network — plan decision, then one pass per own
   troll in id order with the staged reservations, exactly as the environment stages them —, emits the plan's TRAIN
   only when the environment's own dry-run rule says it succeeds, prints the commands (no beam search in v1).
3. **The bed** `local_claude_1/nn-bot/bed_full_bot.py`: the bot compiled from the clone checkpoint plays the 24
   bench maps on both seats through `bench.py`'s referee against the champion's file, and its commands are compared
   move for move with the Python clone driven by `bench.py --policy network` on the same games: identical
   commands on every turn (the bed passes only at 48/48 games identical); plus the timing line (≤ 15 ms a turn on
   the host, first turn ≤ 500 ms) and the size line (< 100,000 characters after compaction).

**Done.** The bed 48/48 identical with the clone `local_claude_1/nn-bot/results/clone-2026-08-30-a/clone-pilot.pt`;
timing and size lines inside the limits; `claude_1` reproduces the bed and the lines; the tests pass.
**Dead.** The single file cannot fit under 100,000 characters with the int8 weights and the plane code — then the
coordinator decides between a narrower trunk and a 6-bit weight packing.
**Budget.** 4 days; two messages (a day-1 design note naming the size budget by component, the final handoff).
**Rules.** No platform action; the readable form of the bot is the generator's output (the compact form its
`compact_rust_source.py` image); nothing is submitted by this card.

## Log

- 2026-08-30 11:2xZ: born; charter sent to codex_1 pinned to this card's commit. — coordinator
