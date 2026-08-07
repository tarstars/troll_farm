# Exact E7a restore replay corpus

This directory publishes the full visible finished-game queue for active exact-E7a restore agent
`6592131`, submission `41086057`, collected on 2026-08-03.

The compressed JSONL contains one full replay object per line, ordered by game ID. It preserves
referee input, frames, commands, scores, game IDs, agent IDs, and submission identity through the
battle index. Personal presentation fields are not copied: player names become `PLAYER_0` and
`PLAYER_1`; user IDs, avatars, public handles, and TestSession handles are removed. The manifest
records every source and exported hash.

The compressed replay file is an exact-path Git LFS object. To materialize only this corpus in a
smudge-disabled clone:

```bash
git lfs pull --include="data/shared-lfs/e7a-restore-agent-6592131/games-agent6592131-submission41086057.jsonl.gz" --exclude="*"
```

Rebuild from an authorized local raw cache:

```bash
python3 cgauto/export_agent_replays.py \
  --agent-id 6592131 --submission-id 41086057 \
  --battle-list data/raw/battles/6592131.json \
  --raw-root data/raw/games \
  --output-dir data/shared-lfs/e7a-restore-agent-6592131 \
  --observed-at-utc 2026-08-03T17:57:57Z
```
