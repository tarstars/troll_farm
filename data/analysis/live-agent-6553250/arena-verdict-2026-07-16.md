# Arena verdict — pre-seed + orchard-coverage stack — 2026-07-16

## Verdict

**INCONCLUSIVE ARENA WINDOW; CONSERVATIVELY REVERTED.**  The exact recovered live source was
restored.  The platform did not produce a valid same-code control, so this run cannot determine
whether the local gain transfers to the live Legend field.

## Bracket and submission

| Event | Time (MSK) | Arena-room reading | Agent / submission |
|---|---|---|---|
| Exact live bracket | 16:57:35 | rank 6/104, score 26.3 | agent `6553250` |
| Candidate submitted | ~16:57:45 | pending | submit `41002151` |
| Candidate landed | 16:58:56 | cold-start rank 102/104, score 0.0 | agent `6555355` |
| Candidate peak | 17:08:57 | rank 11/104, score 25.3 | agent `6555355` |
| Required +20m read | 17:18:14 | rank 34/104, score 23.3 | agent `6555355` |
| Exact live restored | ~17:18:45 | pending | submit `41002271` |
| Restore landed | 17:19:41 | cold-start rank 102/104, score 0.0 | agent `6555394` |
| Restore +20m | 17:39:29 | rank 100/104, score 16.1 | agent `6555394` |
| Restore +35m | 17:55:07 | rank 71/104, score 19.9 | agent `6555394` |

Candidate artifact:
`cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage.min.rs`, 90,547 bytes,
SHA-256 `da53b0f66a0224bf9c8d5796d69905a9bebcf1e71ee97e4b65e72a2fdea046e9`.

Restored artifact:
`cgauto/submissions/agent-6553250-yamo-orchard-live.min.rs`, SHA-256
`09fac1fefa24eac657dba16a75d802eee38e1269f4aa44413e1ca103df36fe7a`.

## Trajectory

The candidate climbed normally during placement, then reversed relative to the established
bracket:

| Time | Rank | Score | Delta vs 26.3 |
|---|---:|---:|---:|
| 17:00:25 | 62 | 20.9 | -5.4 |
| 17:03:41 | 43 | 22.4 | -3.9 |
| 17:05:13 | 21 | 24.4 | -1.9 |
| 17:08:57 | 11 | 25.3 | -1.0 |
| 17:10:28 | 23 | 24.1 | -2.2 |
| 17:12:45 | 34 | 23.3 | -3.0 |
| 17:15:04 | 40 | 22.7 | -3.6 |
| 17:18:14 | 34 | 23.3 | **-3.0** |

At roughly +10 minutes, the latest 30 finished battles were 21 wins / 9 losses with +13 mean
raw score margin.  Subsequent higher-field games pulled the rating down from its 25.3 peak.

The crucial control then failed: byte-identical exact-live source, resubmitted immediately,
reached only 16.1 at its own +20-minute read and 19.9 at +35 minutes, versus its established
26.3 pre-submit reading.  Matchmaking arrived in uneven waves and one arena-room request failed
with `URLError`.  Same-code reset drift of -10.2 at +20 and -6.4 at +35 is too large for the
candidate's -3.0 established-bracket delta to be interpreted causally.

## Interpretation

The pre-existing -0.5 rule triggered a conservative rollback at candidate +20 minutes.  The
subsequent exact-source A/A control shows that the arena was not operating at sufficient
capacity/stability for that threshold to be valid.  Therefore:

- the stack is **not promoted**;
- the stack is also **not causally rejected** by this window;
- exact live source remains resident as the conservative safe state; and
- no further arena submission should occur until a same-code reset reconverges normally.

Any future trial needs a fresh A/A control under normal platform capacity, followed by component-
separated activation telemetry.  Do not use either the 26.3 established bracket or the 16.1
cold restore alone as a candidate verdict.
