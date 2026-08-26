# 20260826-fresh-fixture-dataset: Track 0-3 — fixtures as a generated dataset from real instrumented games of the current bot (owner 1: retire old data, build fresh)

- Status: **OPEN — CHARTERED 2026-08-26T15:45Z by owner ruling**. Board row 0-3. Starts **after T-1's first two tables** and once the v6 instrument (row 0-3a) has been on the ladder for a day.
- Record owner: local_claude_1 · Work owner: **codex_1** · Reviewer: claude_1 (one round) · Arena: nothing.
- **Done means:** a script `scripts/cut_fixtures.py` (or under `codex_1/fixtures/`) that, given the collector's corpus and a bot hash, cuts **windows of interest** from that bot's **real ladder games with v6 telemetry** — dances, parked trolls, blocked trolls, stalls, the turn-100 shack engine not starting, long-kept goals (`ka` > 30) — into a library tagged with the bot hash, the game id, the seat and the window; a regenerate-on-demand rule (run it again on the next bot's games; nothing is frozen against an older bot); the harness's grading reads this library; a first library cut from the instrument's first day of games, with counts per class, on `main`.
- **Dead means:** the collector's games do not carry the telemetry (then the instrument row is the defect, not this one).
- **Budget:** 1–2 days, 0 ladder, 0 bot changes.
- Created UTC: 2026-08-26T15:45:00Z · Last updated UTC: 2026-08-26T15:45:00Z

## The loop this serves (owner's words)
Fix the bot → local panel on fresh replays (minutes) → submit the instrument → the collector brings back new games → regenerate the fixtures → read. Old results are kept as numbers, never as gates.

## Do not touch
`data/raw/games/`; the cron; the Arena.
