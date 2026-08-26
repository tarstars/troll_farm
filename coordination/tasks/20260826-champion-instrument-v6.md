# 20260826-champion-instrument-v6: the champion with v6 telemetry, for the ladder (owner 1a: "replaces")

- Status: **OPEN — CHARTERED 2026-08-26T15:45Z by owner ruling** ("the instrument replaces the champion on the ladder"). Board row 0-3a.
- Record owner: local_claude_1 · Work owner: **claude_1** (it holds `narrate6` and the arm generator) · Reviewer: codex_1 (one round) · Arena: **local_claude_1 submits** once the gate passes.
- **Done means:** an arm = the champion readable `readable/door1-champion.rs` (`ad1ae4ef…`, compaction `0da12c33…`) **plus v6 telemetry only** (`MSG` lines; no rule change), compacted for submission, with: probe parity — the arm with `MSG` stripped byte-identical in play to the champion on all 240 panel games and 34 fixtures; determinism; 0 decode errors; file + sha256 + round-trip report on `main`; then submitted by the coordinator as the ladder resident.
- **Dead means:** parity fails and cannot be made to pass without touching play (then the champion stays on the ladder and this is written up).
- **Budget:** ½ day, 1 review, 1 submission (the coordinator's). No panel value read — this arm changes nothing in play.
- Created UTC: 2026-08-26T15:45:00Z · Last updated UTC: 2026-08-26T15:45:00Z

## Why (owner's words, plain)
The project's evidence base becomes **real ladder games of the current bot with telemetry**. Every day the collector brings home the games; with telemetry in them, each troll's goal, kept/released state and reason are on the record. This arm is the champion in play and an instrument on the wire.

## Do not touch
Play logic; the resolver; the Arena (coordinator only); `data/raw/games/`.
