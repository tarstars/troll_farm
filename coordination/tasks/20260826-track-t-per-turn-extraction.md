# 20260826-track-t-per-turn-extraction: Track T-2 — per-turn commands from the raw replays (the column T-1 and F-1 both lacked)

- Status: **OPEN — CHARTERED 2026-08-26T15:00Z by the coordinator** under the owner's fresh-data ruling. Board row T-2. Running as a coordinator-side subagent on the host (the raw corpus is 6.6 GB on the host; the VM has 5.1 GB free).
- Record and work owner: local_claude_1 (subagent) · Consumer: codex_1 (T-1's remaining tables; 0-3's generator) · Reviewer: codex_1 (one round on the sanity check).
- **Done means:** `scripts/extract_turns.py` + `data/processed/turns.jsonl.gz` (one line per game/turn/seat: raw stdout, parsed commands, the `MSG` payload kept verbatim) + `turns.manifest.json` (counts, failures, sha256); per-game command counts reconcile with `games.jsonl`'s aggregates on sampled games; the file (or a per-cohort slice) on the VM for codex_1.
- **Dead means:** frames lack stdout for most games (then report the share and stop).
- **Budget:** one subagent run (~1 h); 0 ladder.
- Created UTC: 2026-08-26T15:00:00Z

## Why (plain words)
T-1's first table and F-1 both stopped at the same wall: the processed corpus has per-game totals only. The raw replays carry every turn's commands (and, for instrumented bots, the telemetry text). Extracting them once unlocks T-1's planting-by-turn / harvest-ownership / idle columns, the b100 theft split on the 4 games we hold, and the fixture generator (0-3), which reads the same per-turn data.
