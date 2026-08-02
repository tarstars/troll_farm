# 20260802-wide-corpus-catchup

- Status: complete
- Record owner: local_codex_1
- Work owner: local_codex_1
- Created UTC: 2026-08-02T09:26:56Z
- Completed UTC: 2026-08-02T09:42:00Z
- Branch: `agent/local_codex_1`
- Area: read-only platform collection and cumulative corpus rebuild

## Owner directive

Fetch all newly visible platform games after a suspected cron gap; expect a significant
corpus update.

## Safety and scope

Use the established idempotent wide collector against the canonical live replay cache.
Do not move, symlink, lock, delete, or rewrite an existing `data/raw/games` file; do not
change the 05:17 cron. Include current agent `6589709` explicitly, plus the full visible
windows of Legend ranks 1–50. Abort on the collector's HTTP 422/429 hard stop.

## Result

The suspected cron gap was a stale STATE count, not a scheduler failure: five consecutive
daily runs from July 29 through August 2 completed successfully. Before the manual run the
cache held 10,188 games, already 1,106 above STATE's 9,082.

The fresh snapshot `20260802T092656Z-d61p-wide` fetched 282 missing replays and classified
6,682 wanted games with zero acquisition failures. Snapshot QA passed all 6,682 replays,
including all 160 current-resident games. The cumulative rebuild completed at 10,470 raw and
parsed games, zero parse failures, 513 unique agents, and 10,470 unique maps. No cron or
collector configuration was changed.

The standard mature checkpoint for `6589709`/`41079653` is clean at 23.12, rank 32/130,
160/160 parsed, zero runtime signals. Compact evidence is in
`data/analysis/live-agent-6553250/wide-corpus-catchup-2026-08-02.md`.
