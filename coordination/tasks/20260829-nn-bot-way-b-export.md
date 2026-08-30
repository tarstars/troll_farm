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
- 2026-08-30 13:0xZ: **amendment (a) — the seat.** The protocol carries no seat field (the reader is always "player 0"; the map's
  `0` is the reader's shack), and the map's geometry does not tell either: over the 26,850 real maps player 0's shack is in the
  left half in 14,340 (53 %) — chatgpt_1's half-rule (12:13Z) is false, its requirement is right. **The bot recovers its absolute
  seat on turn 1 from its own troll's id**: the referee numbers trolls in creation order, so player 0's starting troll is id 0
  and player 1's is id 1 — verified on every recorded game with a seat-0 row in the training set (370 games, 0 exceptions).
  Fail closed if the turn-1 ids are not exactly {0, 1}. Then rotate for seat 1 exactly as the environment does (the
  canonical player-relative frame), never mixing the two representations. **Amendment (b) — the direct parity test before
  the bed**: for a sample of states on both seats, the standalone's observation bytes, spatial mask, plan mask and decoded
  command must equal `tf_full_obs_from_state` and the canonical codec for the same state, plan and staged prefix.
  **Amendment (c)**: the id rule checked mechanically over the training set's turn-1 states as a test. The 48/48 bed stays
  the final end-to-end gate. — coordinator
- 2026-08-30 14:57Z: codex_1's amended delivery (`agent/codex_1@5be68352`, superseding its 14:40Z handoff): the exporter
  (`export_full_actor.py`: int8 coarse weights + packed residual bits = effective 16-bit integers in per-output groups of 64
  with four scale refits, 72,660 bytes; the 34,799 actor/plan parameters shipped, the 1,153 critic parameters not), the
  generator (`generate_full_bot.py`: lifts the signed state/engine/mask/codec/plane-builder/`MoveRouting` code with pinned
  source hashes; the sanitizer of planes 59–71 and 98; masked argmax; ascending-id staged decisions; the exact TRAIN dry run;
  std-only, single-threaded, AVX2/SSE; the payload packed as 29,064 Unicode scalars), the bed (`bed_full_bot.py`: the
  Python quantized checkpoint vs the signed clone stream, the compiled Rust bot vs the same, the direct parity probe on both
  seats, the timing and size lines, the turn-1 id corpus check), the candidate `cgauto/submissions/candidate-nn-clone.rs`
  (52,854 characters, SHA-256 `36bf2f2e…`), 7 tests, `codex_1/results/nn-bot-way-b-export/REPORT.md`. codex_1's numbers:
  48/48 and 13,206/13,206 both ways; first max 14.8 ms, warm median 6.5, p99 9.7 ms. — codex_1
- 2026-08-30 15:4xZ: **reviewed and reproduced by the coordinator on the host** from a clean checkout of `5be68352`: 7/7 tests;
  regeneration byte-identical; the bed — compiled Rust 48/48 games, 13,206/13,206 commands, the Python export 48/48, both
  difference lists empty, the direct seat-parity probe true on both seats (observation, both masks, DROP decoding), the corpus
  check 370/370 seat-0 turn-one games on the host's complete states file (SHA-256 `1df412f0…`), zero exceptions; timing
  first-turn max 14.839 ms, warm median 6.532 ms, p99 10.600 ms, max 26.442 ms (the host carried a training run and a bench);
  all seven gates true (`gates` in the bed's record). **Merged onto `main` as `b6075fe8`.** claude_1 chartered for the second
  reproduction on the VM (handoff 15:35Z; the training set restored on the VM for the corpus check). The card's Done line
  is met on the host; it closes when claude_1's reproduction lands. Nothing is submitted. — coordinator
- 2026-08-30 15:40Z: **claude_1's reproduction on the VM: PASS on all four items** (`claude_1/results/nn-bot-way-b-export/`):
  7/7 tests; regeneration byte-identical (`36bf2f2e…`, 52,854 characters; the readable form `39851d29…`); the bed 48/48 and
  13,206/13,206 both ways, both difference lists empty, the probe true on both seats; the corpus check 370/370 with the
  checksums verified first. VM timing for information: first max 22.3 ms, warm median 6.6, p99 14.6, max 28.6. Its
  observation: the warm p99 lives within a millisecond or two of the 15 ms line on both machines. — claude_1
- 2026-08-30 15:42Z: **chatgpt_1's audit (`chatgpt_1/reviews/nn-bot-way-b-export-portability-audit-2026-08-30.md`): the generated
  bot executes AVX2 unconditionally** (`#[target_feature(enable="avx2")] unsafe fn convolution_range`, called without runtime
  detection, no fallback) — on an x86-64 worker without AVX2 it dies with an illegal instruction before its first command;
  the beds cannot see it because both our machines have AVX2. Also: no predeclared rule for a timing sample that failed once
  (15.126 ms) and passed on rerun (9.718 ms); the size should be reported in code points, UTF-16 units and UTF-8 bytes
  (52,854 code points ≈ 81,918 UTF-16 units). — chatgpt_1
- 2026-08-30 16:1xZ: **the Done line is met (two reproductions) — and three amendments before any file of this line is called
  shippable** (handoff to codex_1 16:15Z; the budget +1 day): **(d)** runtime dispatch on `is_x86_feature_detected!("avx2")`
  with a baseline SSE2/scalar fallback of identical accumulation order (separate multiply and add, no fused ops on either path);
  the bed runs the compiled bot on both paths — 48/48 and 13,206/13,206 each — and reports the fallback's timing (must stay
  under the platform's 50 ms; the AVX2 path is the number of record); **(e)** the functional bed once; the timing gate three
  runs on the host of record with no training run on the machine, pass = median warm p99 ≤ 15 ms and every run ≤ 20 ms, all
  values recorded, the VM's numbers for information; **(f)** the size gate counts UTF-16 code units, with code points and
  UTF-8 bytes beside it. July's live bot used no intrinsics; nobody holds evidence about the platform's CPUs, and the failure
  mode (every game lost for an hour, invisible beforehand) is not worth the milliseconds. — coordinator
- 2026-08-30 16:31Z: **amendments (d)(e)(f) delivered** (`agent/codex_1@c4355caa`): the bot detects AVX2 once
  (`is_x86_feature_detected!`), falls back to a baseline SSE2+scalar kernel with the identical accumulation order (separate
  multiply and add); the bed compiles and runs BOTH paths — AVX2 48/48 and 13,206/13,206, forced fallback (`--cfg
  tf_nn_force_fallback`) 48/48 and 13,206/13,206, fallback p99 12.5 ms on the VM (limit 50); the bed always takes three
  timing samples and gates only in `--timing-context host-of-record-quiet` (`certified: null` on the VM); the candidate
  `4c5a096d…`: 54,218 code points, **83,282 UTF-16 units** (the gate), 141,410 UTF-8 bytes; 10/10 tests. — codex_1
- 2026-08-30 16:49Z: **claude_1 REPRODUCED the amendments** (`agent/claude_1@907acb42`): tests, regeneration and sizes
  byte-for-byte; both runtime paths 48/48 and 13,206/13,206; the corpus check run a third time (370/370). **And the check no
  bed can make, made statically: disassembly of the SHIPPING binary** — `convolution_range` is SSE-only (zero `%ymm`), all
  306 `%ymm` references live in one separate AVX2 symbol called from the single dispatch site, and neither build contains a
  fused multiply-add — the AVX-free path exists in the machine code we would submit, not only in the source. Its first
  timing run was contaminated by its own parallel builds (disclosed; VM timing is information by rule). — claude_1
- 2026-08-30 19:1xZ: **accepted and merged onto `main` (`bb3645ea`)** after the coordinator's own check from a clean checkout
  (10/10; hash, regeneration, the three size counts by an independent count; the dispatch markers). **Phase 4's engineering is
  COMPLETE** — built, amended and reproduced twice within one day. One step stays open, the coordinator's: amendment (e)'s
  host-of-record certificate (three quiet runs) is taken when a shipping candidate exists — the host carries the training run
  now and the clone will not be submitted; until that certificate and the owner's word, nothing here is called ladder-ready.
  codex_1's 16:33Z blocker (quarantine the 16:09Z correction) was already done at 16:40Z (entry 27, on `main` at `702afb31`). — coordinator
