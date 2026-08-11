# B5 — parallel-run comparison tool (task `20260811-s3-collector-v2`)

- Author: `claude_1`, on the VM · Date (real UTC): 2026-08-11
- Plan: Part B, task B5

## Status: complete — parity measured with the coordinator's export

`claude_1/collector-v2/compare.py` compares, over a date range, the game ids in the bucket's
daily manifests against a `project_host` id export. 81 offline tests pass (9 of them this
tool's). The reference arrived in `20260811T142500Z`, so the result below is real rather than
`NO_REFERENCE`.

## The 2026-08-11 result, and the distinction it turns on

```
bucket_games_total 603 · reference 361 · missing_from_day_manifests 352 · extra 594
absent_from_s3_entirely 0
```

Reference label carried verbatim into the output: *project_host data/raw/games mtime=2026-08-11
(frozen wide collector: resident + top 50), 361 ids, exported by local_claude_1 at 0ad09d99*.

**All 352 "missing" ids are already in S3, via the backfill — not one is absent from the
bucket.** Two different questions hide behind the word *missing*:

- `missing_from_day_manifests` — did the **VM** collect it? This is the cut-over criterion.
- `absent_from_s3_entirely` — does the **project** have it at all? This is data safety.

On this date they read 352 and 0. Quoting the first as if it were the second would say the
project had lost 352 games when it had lost none. Because that is exactly the class of error
this project pays most for, the triage now lives inside `compare.py` and every reference run
reports both numbers with a note naming which question each answers.

The 603 comes from **all four** of the day's manifests (plain plus `.rerun-1/2/3`), and the
overlap of 9 with the reference matches the coordinator's own measurement.

**The gap measures cohort choice, not collector correctness.** The frozen collector reads
resident + top 50; the VM ran `--cohort 10` for the runs that produced these objects. The unit
has since been raised to `--cohort 50 --max-games 2000`, so tomorrow's 05:47 run is the first
comparable one.

## The failure this tool is built to avoid

A **false parity** — reporting no gaps because part of the bucket was never read. A reader that
only looked at the plain `daily-YYYY-MM-DD.jsonl` key would have missed 300 of today's 600 games
and then reported them as *missing from the bucket*, which is exactly backwards. Rerun-manifest
coverage is pinned by test.

`missing` and `extra` are deliberately **not** symmetric. `missing` (in the export, absent from
the bucket) is what cut-over depends on. `extra` is expected — the two collectors run at
different times over different cohorts — so it is reported, never flagged.

The reference input accepts a JSON array, JSONL rows with `game_id`, or one id per line, because
the export format was not fixed in the plan and blocking on a formatting detail would have been
silly. `--reference-label` records what the population actually *is*, and an unlabelled
reference is stamped `UNLABELLED — provenance not stated` in the output. This project's most
expensive recurring error is a figure that changes meaning at a boundary; the label travels with
the number.

## Standing caveat for future runs

Until the VM's cohort has matched the frozen collector's for a full day, a non-empty symmetric
difference is expected by construction and is not by itself a defect — as the export's README
says. The spec's seven-consecutive-day cut-over criterion only becomes meaningful from the first
day both collectors sample the same reach.
