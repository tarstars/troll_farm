# progress: 20260802-top-player-new-games-multiagent-analysis

- From: local_codex_1
- To: claude_1, chatgpt_1, user
- Created UTC: 2026-08-02T11:02:03Z
- Task: 20260802-top-player-new-games-multiagent-analysis
- Requires acknowledgement: no
- Platform mutation performed: no

## Shared corpus ready

The sanitized open-data package is ready for simultaneous analysis:

- `top-player-new-games-shared-2026-08-02.manifest.json` — SHA-256 `dea2d4b2…`;
- `top-player-new-games-shared-2026-08-02.sides.csv` — 5,672 side rows, SHA-256
  `e4e49234…`;
- `top-player-new-games-shared-2026-08-02.direct-game.json` — sanitized exact direct game
  `897780884`, SHA-256 `e1a94b84…`;
- `top-player-new-games-shared-2026-08-02.direct-trajectory.json` — 300 turns, SHA-256
  `c9d77aed…`;
- `top-player-new-games-ranking-rubric-2026-08-02.md` — shared vetoes and 100-point rubric,
  SHA-256 `390cd4bc…`.

Counts: 153 current-new open games, one direct current-vs-top20 game, 2,684 open top20-source
benchmark games, 2,836 union games, 5,672 side rows. Seven sealed-tagged games are excluded;
the extractor reads only `processed/open` plus the one open direct replay.

The current open record is 95W/2T/56L across seats 68/85 and splits 93 calibration-only,
56 discovery, four validation. The benchmark contains 2,853 top20 side rows and 169
top20-v-top20 games.

The direct slice is n=1, so no analyst may call a top20 mechanism broad or causal from it.
Begin the assigned independent tracks after fetching the integrated corpus commit. Initial
reports must use the task schema; cross-review starts only after all three handoffs.
