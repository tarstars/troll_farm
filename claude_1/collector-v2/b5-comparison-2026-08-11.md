# B5 — parallel-run comparison tool (task `20260811-s3-collector-v2`)

- Author: `claude_1`, on the VM · Date (real UTC): 2026-08-11
- Plan: Part B, task B5

## Status: tool complete and exercised; the parity result is BLOCKED on an input you own

`claude_1/collector-v2/compare.py` compares, over a date range, the game ids in the bucket's
daily manifests against a `project_host` id export, and reports what each side has that the
other does not. 70 offline tests pass (8 of them this tool's).

**The plan says the coordinator supplies the `project_host`-exported id list in the task
thread. It has not arrived, so no parity number exists yet** — and the tool refuses to produce
one from nothing. A run without a reference reports `NO_REFERENCE` with the note *"NOT a parity
result and must not be quoted as one"*, rather than a comforting zero.

## What the first live day does show

```
verdict NO_REFERENCE · range 2026-08-11 .. 2026-08-11 · bucket_games_total 600
```

600 distinct games for 2026-08-11, read across **both** of the day's manifests — the plain
`daily-2026-08-11.jsonl` (300) and `daily-2026-08-11.rerun-1.jsonl` (300). That is a live
cross-check of two things at once: the rerun objects are readable and their id sets are
disjoint, so the two collector runs did not re-collect the same games.

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

## What I need to finish B5

The `project_host` id export for 2026-08-11 (and onward). Send it in the task thread in any of
the three formats and I will publish the parity result. Note the caveat the numbers will carry:
the deployed unit runs `--cohort 10 --max-games 300` because the VM's disk is 94% full, and both
runs today dropped candidates (`953` and `653` of 1,253). **Missing ids against a full
`project_host` export are therefore expected right now, and they measure the cap, not a defect
in the collector.**
