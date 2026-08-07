# Round-36 simplified E7a replay corpus

This directory publishes all 160 finished games for round-36 agent `6594200`, submission
`41090606`, observed after the Arena run settled on 2026-08-04.

The compressed JSONL contains one complete replay per line, ordered by game ID. It preserves
referee input, every replay frame, commands, tooltips, scores, ranks, game IDs, agent IDs, and
submission identity through the battle index. Personal presentation fields are not copied:
player names become `PLAYER_0` and `PLAYER_1`; user IDs, avatars, public handles, and TestSession
handles are removed. The manifest pins every source and exported replay hash.

The compressed replay file is an exact-path Git LFS object. In a clone made with automatic LFS
smudging disabled, materialize only this corpus with:

```bash
git lfs pull \
  --include="data/shared-lfs/r36-agent-6594200/games-agent6594200-submission41090606.jsonl.gz"
```

Rebuild from the authorized external staging cache on the project host:

```bash
python3 cgauto/export_agent_replays.py \
  --agent-id 6594200 --submission-id 41090606 \
  --battle-list data/external/r36-agent-6594200/battles-agent6594200-submission41090606.json \
  --raw-root data/external/r36-agent-6594200/games \
  --output-dir data/shared-lfs/r36-agent-6594200 \
  --observed-at-utc 2026-08-04T16:25:25Z
```
