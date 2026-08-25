# `project_host` collected-game-id exports (B5 parity reference)

`project-host-game-ids-YYYY-MM-DD.txt` — one numeric game id per line, sorted ascending,
no header. Produced for the collector-v2 comparison tool (`compare.py`), which refuses to
report parity without a reference and says `NO_REFERENCE` otherwise.

## How it is derived, and what that means

The id set is the set of files in `project_host:data/raw/games/` whose **mtime falls on
that UTC date**. The 05:17 UTC cron writes each replay as it fetches it, so mtime is the
collection time. It is not a collector log — if a file were ever rewritten in place, its
mtime would move with the rewrite; nothing does that today, and the corpus is append-only
in practice.

## The comparison is between different cohorts — read the difference correctly

`project_host`'s frozen wide collector reads **resident plus the top 50** leaderboard
agents; collector v2 on the VM currently runs `--cohort 10`. The two id sets are therefore
expected to differ **by construction**, in both directions:

- ids here but not in the VM's manifests: mostly outside the top-10 cohort, plus whatever
  the VM's `--max-games` cap dropped;
- ids in the VM's manifests but not here: games the VM saw within its cohort during a
  different window than the 05:17 run.

A non-empty symmetric difference is therefore **not** by itself a collector defect. Parity
in the cut-over sense (spec: seven consecutive days) only becomes meaningful once the VM's
cohort and cap match or exceed the frozen collector's reach.

| Date | Ids | Notes |
|---|---:|---|
| 2026-08-11 | 361 | cron ran 05:17 UTC; VM collector's first day, capped at 300/run |
