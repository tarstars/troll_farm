# Third-troll independent reproduction — 2026-08-28

Verdict: **REPRODUCED**.

Run from `agent/codex_1` after merging `origin/main` through charter commit
`de979e41c20aafa5a885416291e7d4a3256a95c8`.

## Build

- 2/3/0/3 arm SHA-256: `30bf84226f26b82b8121fcf7605bc28104dff2daf0ed4595d90fcc1b53b2fbbe`
- 2/3/0/3 compacted submission SHA-256: `89493fa0d68e1dea1079c35ca4b0a8ed9b36273ccb25f5663d51c1a9e48ded33` (65,342 bytes)
- 2/2/0/2 compacted submission SHA-256: `684104f136f93ac620447dadf95e9d491b467ac68eef8e4180f8081b114c00bf` (65,342 bytes)
- Both readable diffs report +123 / -29. Regeneration left all generated tracked files byte-identical.

## Fixture bed and equivalence

- Plays: 34/34.
- Differs from champion: 27/34.
- Deterministic: 34/34.
- Compacted equals arm: 34/34.
- Telemetry errors: 0.
- Arm trained in 1/34; champion trained in 1/34.
- Third troll in fixtures: none; wrong specification: none; more than three trolls: none.
- Selection-only equivalence: identical play on 58/58 games (34 situations and 24 real maps).

## Smoke

- Mechanics okay on 23/24 maps. The expected exception is bare map `c84154d29ea19fbc`, where both bots idle after turn 200 and the arm starter idles 30 turns longer.
- Third troll trained in 5/24 games.
- Median third-troll turn: 158.
- Median funding duration: 144 turns.
- No third troll: 19 times, all `bill never paid by turn 200`.
- Own-score delta: +497 across all 24 games; +82 on the five third-troll games.

## Readable diff

Nothing in `readable/diffs/third-troll.diff` can train a fourth troll, train the third before the second, train it in the last 100 turns, or leave a troll without a command list.

Commands run once each:

```text
python3 local_claude_1/third-troll/make_third_troll.py
python3 local_claude_1/third-troll/make_third_troll.py 2202
python3 local_claude_1/third-troll/fixtures_diff.py
python3 local_claude_1/third-troll/select_equivalence.py
python3 local_claude_1/third-troll/smoke.py --records local_claude_1/third-troll/smoke-maps-seed0.jsonl
```
