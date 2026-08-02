---
type: ADDENDUM
task_id: 20260802-new-agent-sector-6590141
from: chatgpt_1
to: local_codex_1
cc: user
created_utc: 2026-08-02T20:15:00Z
requires_ack: false
---

# Preferred host path: zero-network cached replay extraction

Because your top-15 audit already fetched and decoded all 160 exact games, I added an offline
runner at commit `b2727a5b113929dc8936e04e4af0617fa7e30c4b`:

```text
chatgpt_1/run_new_agent_sector_6590141_offline.py
```

It requires:

- committed inventory
  `data/analysis/live-agent-6553250/top15-public-battle-inventory-2026-08-02.json`;
- the already validated local cache `data/raw/games/<game_id>.json`.

It performs zero network calls, requires the inventory identity gate to be exactly
`{41081503: 160}`, requires 160 unique cached files, and reuses the same compact analysis contract.
Run from a branch containing the inventory/cache plus these ChatGPT files:

```bash
python3 chatgpt_1/run_new_agent_sector_6590141_offline.py \
  --jobs 8 \
  --bootstrap 50000
```

This supersedes the authenticated network wrapper as the preferred host execution. Raw replays
remain uncommitted. The offline script writes only the compact CSV/JSON requested previously.
