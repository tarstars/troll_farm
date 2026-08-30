# Card 20260829-nn-bot-way-b-champion — an exact linked copy of the champion as a training opponent

Sub-card of `coordination/tasks/20260829-nn-bot-way-b.md`. Born 2026-08-30 07:5xZ. Builder: `codex_1`.
Reviewer: `local_claude_1`; `claude_1` reproduces the parity check.

**Why.** Phase 3's first exploratory run learned against the linked training pool (`SecureOrchardBot`,
`NorxondorNative`, `LegendFieldProxyV2`, `GoldElite::adaptive`, `ScriptBoss`, `MyBot` = a Boss-4 model) and
frozen copies of itself: its win rate against that mix rose 0 → 42 % in three hours, and its update-1,000
checkpoint then lost to the champion's compiled file **worse than the clone it started from** (2 wins of 48
vs 9; 87 points vs 134). The practice opponents are not the champion. The gate is the champion's file; the
training pool must contain the champion.

**What (as ruled 08:35Z, replacing the born text).** A `Strategy` in the research workspace that plays **exactly** what the
champion of record's submitted file plays — the authority is `cgauto/submissions/candidate-champion-denial-off-v6-instrument.rs`,
SHA-256 `0e92f8fa1e9097dd3df81989e222be8810f3cebdcd3efc950f84353f0bd1d57c`; its source form is the readable version-6 arm
(SHA-256 `321723933c2a0cfb6bfcd62c57e0d25b6783ffb8ddcfea37c05b053e2e46cd4f`), which compacts byte-identically to it; the bare
`readable/denial-off-champion.rs` is a different program and is excluded — wired into the full environment's pool as id 7
`champion_exact` (eight `opponent_weights`; `MyBot` keeps its slot), orchard 6 as id 8 if it fits the budget.

**How to prove it is exact — the paired exact-input proof (ruled 08:35Z; a recorded game holds no literal per-turn input).**
200 environment games on real maps, both seats, varied legal opponent-action modes: the linked strategy plays inside the
environment; the authoritative standalone, one stateful instance per game, receives through its real text protocol the
exact pre-turn states that produced the linked commands, in order. **Gameplay parity** (every non-`MSG` command and its
order) is the load-bearing gate; **raw parity** (the `MSG` text included) is reported separately. The same 200 replays
pass transition and terminal parity, and a speed line is reported. The recorded-game comparison is kept only as a
documented reconstruction limitation (first mismatch: game 900742300, seat 0, turn 23).

**Done.** Gameplay parity 200/200 (and raw parity reported), transition and terminal parity 200/200, zero rejected
commands, the pool id in `ENV-API.md`, the tests in `tests/test_rl_full_env.py`, every number with its command and
commit, the timing-free digest; `claude_1`'s reproduction matches.

**Dead.** The champion's code cannot run as a `Strategy` without changing its play (the first divergence named) — then the
coordinator decides between a subprocess opponent and dropping the idea.

**Budget.** 3 days; two messages. **Rules.** No platform action; the byte-sacred resident untouched; the champion's file is
wrapped, never edited; `df -h` first.

## Log

- 2026-08-30 07:5xZ: born from the update-1,000 bench of the exploratory run; charter sent to codex_1. — coordinator
- 2026-08-30 08:10Z: codex_1 stopped honestly at the first recorded-game mismatch (the reconstruction is not the literal
  input) → the paired exact-input proof ruled 08:35Z; chatgpt_1's source blocker (the readable file is not the submitted
  program) applied by codex_1 — the authority pinned by SHA; the sub-card rewritten to the ruled contract 09:2xZ (chatgpt_1's
  drift note 11:10Z).
- 2026-08-30 09:12Z: **codex_1's delivery (`agent/codex_1@a375176d`): PASS — 200/200 games, 49,945 turns, raw and gameplay
  parity, transition and terminal parity 200/200, zero rejections, 187 maps, seats 91/109, four opponent-action modes;
  1,058 environment turns/s on the VM; the standalone answers in 0.41 ms median; Rust 9/9, Python 8/8; one proof-instrument
  defect found and fixed (canonical replays sorted plants by cell, the player's input keeps the engine's insertion order,
  and the champion breaks ties by it — replays now carry `plant_order`); timing-free digest `090ced4d…`.** claude_1
  chartered to reproduce; merged onto `main` by the coordinator for training meanwhile. — coordinator
- 2026-08-30 09:5xZ: merged onto `main` (`d34f16c8`), the library rebuilt on the host, the environment suite 8/8 there
  (548 s, the 200-replay champion test included); `champion_exact` is in `ppo-d`'s pool since 09:42Z. — coordinator
