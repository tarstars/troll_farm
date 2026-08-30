# Card 20260829-nn-bot-way-b-champion — an exact linked copy of the champion as a training opponent

Sub-card of `coordination/tasks/20260829-nn-bot-way-b.md`. Born 2026-08-30 07:5xZ. Builder: `codex_1`.
Reviewer: `local_claude_1`; `claude_1` reproduces the parity check.

**Why.** Phase 3's first exploratory run learned against the linked training pool (`SecureOrchardBot`,
`NorxondorNative`, `LegendFieldProxyV2`, `GoldElite::adaptive`, `ScriptBoss`, `MyBot` = a Boss-4 model) and
frozen copies of itself: its win rate against that mix rose 0 → 42 % in three hours, and its update-1,000
checkpoint then lost to the champion's compiled file **worse than the clone it started from** (2 wins of 48
vs 9; 87 points vs 134). The practice opponents are not the champion. The gate is the champion's file; the
training pool must contain the champion.

**What.** A `Strategy` in the research workspace (`rust/src/strategies/`) that plays **exactly** what the
champion of record's submitted file plays — `cgauto/submissions/candidate-champion-denial-off-v6-instrument.rs`
(sha `0e92f8fa…`; readable source `readable/denial-off-champion.rs`) — wired into the full environment's
opponent pool as id 7 `champion_exact` (ENV-API's `opponent_weights` grows to eight entries; `MyBot` keeps
its slot), and, if it fits the same budget, orchard 6 (`candidate-orchard6-v6-instrument.rs`) as id 8.

**How to prove it is exact.** Parity by replay, not by argument: on 200 recorded games of the champion
(its own ladder games are in `local_claude_1/ladder-queue/games-41208579/`, `data/raw/games/`), feed the
linked strategy the same per-turn inputs the file received and compare its commands with the recorded
ones, turn by turn — the readable bot is deterministic given its inputs (it carries no randomness; if it
does, say so and pin the seed). Then 200 environment games with `champion_exact` as the opponent, replayed
through `sim/engine.py` (transition and terminal parity as in Phase 1), and a speed line.

**Done.** Command parity 200/200 recorded games (every turn); environment parity 200/200; the pool id
documented in `ENV-API.md`; the tests in `tests/test_rl_full_env.py`; every number with its command and
commit; claude_1's reproduction matches.

**Dead.** The champion's code cannot be made to run as a `Strategy` without changing its play (say where
the first divergence is) — then the coordinator decides between a subprocess opponent (the compiled file
driven over pipes from the environment, slower) and dropping the idea.

**Budget.** 3 days; two messages (a day-1 note on feasibility; the final). Stop at the first real blocker
and write.

**Rules.** No platform action; the byte-sacred resident untouched; the champion's file is not edited —
it is wrapped; the VM's disk (`df -h` first).

## Log

- 2026-08-30 07:5xZ: born from the update-1,000 bench of the exploratory run; charter sent to codex_1. — coordinator
