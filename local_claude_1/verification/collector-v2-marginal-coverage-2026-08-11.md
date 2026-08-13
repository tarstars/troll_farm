# Does collector v2's `--max-games` cap lose real games? Measured: no

- Date (real UTC): 2026-08-11 ~14:0x–14:2xZ
- Author: `local_claude_1`
- Why: my own policy message `20260811T130600Z` told `claude_1` that the cap was costing
  ~950 permanently-lost replays per run and to treat it as the highest-value item before
  05:47 UTC. That claim was an **inference**, not a measurement, and it is **wrong**.
  This file is the measurement.

## Measurement 1 — the VM's entire day-1 haul was already in the corpus

Sources: the VM's own daily manifests in `s3://troll-farm-data/games/manifest/daily-*`
(`daily-2026-08-11` + `daily-2026-08-11.rerun-1`), and `project_host:data/raw/games/`.

| Quantity | Value |
|---|---:|
| Games the VM collected on 2026-08-11 | 600 |
| Of those, **not** already in the local corpus | **0** |
| Local collection dates of those 600 | 2026-07-27 … 2026-08-11 |

338 of the 600 were first collected locally on 27–28 July — a fortnight before the VM
"discovered" them. The VM's marginal contribution to what the project holds was **zero**,
and since the backfill already put all 15,291 local games into S3, the 600 were redundant
with S3 as well.

## Measurement 2 — the candidate pool itself is ~100% already held

Live sweep of participant battle windows through the frozen `PublicClient`, cookieless,
read-only, at the time of writing:

| Cohort | Games visible now | Not in our corpus |
|---|---:|---:|
| top-10 (what the VM samples) | 1,136 | **1** (0.1%) |
| full frozen cohort (resident + top 50, 21 selected) | 2,488 | **1** (0.0%) |
| visible to the full cohort but never to top-10 | 1,352 | **0** |

So the ~1,253 daily "candidates" the VM discovers are overwhelmingly replays we have held
for days or weeks. **What the cap dropped was redundant re-fetching, not new data.**

## What this means

1. **There is no ongoing permanent loss caused by the cap.** My "every day the timer fires,
   that many replays leave existence" was unfounded. B1's retention finding is sound —
   unfetched games *do* expire — but it does not follow that the dropped candidates were
   unfetched-and-new; they were fetched long ago by the `project_host` cron.
2. **The real defect is deduplication, not disk.** Collector v2 spends its whole fetch
   budget re-downloading games the project already owns, because it has no knowledge of the
   15,291 ids in the backfill manifests. Seed its known-id set from
   `games/manifest/backfill-*.jsonl` (and its own prior daily manifests) and skip on hit —
   then a 300-game budget covers the genuine daily inflow several times over. The inflow is
   about **361 new games/day**, measured as files newly written by the 05:17 cron today.
3. **Disk cleanup on the VM stays worth doing** — 8.5 GB of stale `/tmp` scratch is real —
   but it is hygiene, not an emergency, and it should not be done under time pressure I
   manufactured.
4. **The cohort gap is a cut-over question, not a loss question.** The VM cannot see 1,352
   games the full cohort can, but 0 of those are unheld today. It matters for the spec's
   cut-over criterion, not for tonight.

## Note on the cut-over criterion (separate finding)

Today's id sets: VM 600, `project_host` cron 361, **overlap 9**, union 952. The two
collectors sample nearly disjoint slices, so the spec's criterion — "the VM's manifests
contain every id the cron collected" — is currently far from satisfied and is measuring
cohort choice rather than collector correctness. Retiring the cron while the VM runs
`--cohort 10` would drop ~350 games/day of coverage. Worth restating before Phase 2 cut-over.

## Method limits, stated

The corpus-membership test is by game id, not by content — a game held locally but stored
corrupt would count as held. The sweep is a single point in time; windows roll, so the "1
missing" is a snapshot, not a stable constant. Neither limit affects the conclusion, which
turns on a 0.0–0.1% miss rate rather than a marginal one.
