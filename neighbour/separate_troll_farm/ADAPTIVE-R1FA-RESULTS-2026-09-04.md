# Adaptive R1FA / V468 result (V543)

## Outcome

V543 replaces the two-worker V468-only program with two available controllers:

- a repaired R1FA-style four-worker economy for high-throughput maps and opponents;
- the exact V468 controller, latched when an opponent
  reveals a nonstandard harvest-zero chopper during the first 24 turns.

Only the selected controller is evaluated each turn. V541 evaluated both controllers before
selecting one; its first platform rollout exposed repeated turn-2 timeouts. V542 removed that
shadow evaluation but still timed out. Profiling then found that the R1FA territory predicate
rebuilt two full BFS maps for every candidate tree. V543 uses the equivalent constant-time
distance comparison on the referee's symmetric maps.

The fixed `(2, 2, 0, 2)` chopper is excluded from the latch because CompactGold and MyBot
use it. That exclusion preserves the large economy gain against those families while still
recognizing the map-adaptive pure-chopper signatures used by the resident on most maps.

The compact source is 99,825 UTF-16 units. Its SHA-256 is
`922a233526ed590dafcc6302461de2dafef720fb003bd2359f55dfd93ac1b4a7`.

V541 platform submission `41242812` was accepted at 2026-09-04 15:38:45 UTC and created
agent `6701647`. After repeated platform timeouts were confirmed, V542 submission `41242865`
was accepted at 15:50:28 UTC and created agent `6701716`. V543 submission `41242929` was
accepted at 16:03:36 UTC and created agent `6701731`. The original resident was agent `6699467`, submission `41240269`,
at 19.23 / rank 60. At the first submission time rank 7 was 26.99.

## Source-project and local baseline

The requested `../trolls_farm` path did not exist. The available source project was
`../troll_farm` (singular), which was used read-only. It contained the referee, opponent
families, current resident snapshot, platform access helpers, and the historical R1FA
evidence. No file in that project was changed.

The strongest unsubmitted local baseline was V468. It had excellent early scoring and
opponent suppression but normally stopped at two workers and about 42 wood per game. The
largest gap to the top public bots was therefore structural: they reinvested in parallel
harvesting and chopping rather than trying to add one isolated late worker to the saturated
V468 policy.

## Repairs leading to V541

The new economy began with the archived R1FA reconstruction. The following defects were
fixed before adaptation:

1. A blocked shack no longer emits `MOVE` and `TRAIN` on the same turn. It clears the shack,
   then trains on the next turn.
2. Destroying one watched natural tree no longer permanently poisons its entire fruit
   species.
3. Only banked/carried fruit and verified own plantings count as durable capacity for a
   future training bill.
4. The first hire is the strongest immediately affordable harvest-capable worker rather
   than a fixed build that can starve on one missing resource.
5. Confirmed opponent crops receive a bounded chop-denial bonus.
6. Two maps that were written but never read were removed from the final source. This is
   behavior-neutral and creates enough room for both complete controllers.

Static-map selection was tested and rejected. On a 96-map resident corpus, shallow rules
based on inventory, source distances, ownership, and iron access did worse in cross-validation
than always using V468. Crop theft was also rejected after changing mean margin by only
`-0.02` over 48 paired games.

## Development results

On eight maps against 12 opponent families (192 paired games), the unguarded repaired economy
V529 raised mean own score from 237.1 to 349.3 and wood from 41.9 to 75.2. It regressed against
the resident, so it was not published.

The first adaptive version V539 restored the resident split from 4-0-12 to 10-1-5, but
mistakenly latched against CompactGold and MyBot. V541 excludes their fixed chopper signature:

| family | V529 W/T/L | V539 W/T/L | V541 W/T/L | V541 mean margin |
|---|---:|---:|---:|---:|
| resident | 4/0/12 | 10/1/5 | 10/1/5 | +8.6 |
| CompactGold | 13/0/3 | 10/0/6 | 13/0/3 | +41.9 |
| MyBot | 15/0/1 | 12/0/4 | 14/0/2 | +156.2 |

## Sealed holdout

The final artifact was frozen before testing seeds 10,020,000 through 10,020,015. Those seeds
were absent from repository and working-storage panel records. The resulting 16-map, two-seat,
12-family panel contains 384 paired games:

| measure | V468 | V543 | delta |
|---|---:|---:|---:|
| mean own score | 228.1 | 377.1 | +149.0 |
| mean opponent score | 108.3 | 161.4 | +53.0 |
| mean margin | +119.7 | +215.7 | +96.0 |
| mean wood | 49.0 | 82.8 | +33.8 |
| workers | 2.00 | 3.83 | +1.83 |
| W/T/L | 341/2/41 | 340/4/40 | -1/+2/-1 |

The paired margin improvement is +96.02 with a standard error of 6.21 (normal 95% interval
approximately ±12.18). Seat-specific margin improvements are +99.3 and +92.7. V543 changes
CompactGold from -8.0 to +64.3 mean margin and wins every holdout game against each of the
three four-worker legend proxies. Its known weak family is the exact resident: -14.3 mean
margin and 9/4/19 versus V468's +2.1 and 17/2/13.

All 876 referee reports are classified noncritical move conflicts; critical and unclassified
counts are both zero. Candidate command generation measured 6.52 ms at p95 and 33.56 ms maximum.

## V543 latency repair and packaging locks

- Readable and compact forms compile independently and accept empty input.
- Recompacting `bot.rs` reproduces `submission.rs` byte-for-byte.
- The two V543 binaries emitted identical commands in all 160 archived replay streams.
- On the full 384-game panel, planning measured 1.05 ms at p95 and 5.84 ms maximum, versus
  V541's 6.52 ms and 33.56 ms.
- On a matched CompactGold panel, V543 preserved V541's gameplay exactly while reducing p95
  to 0.96 ms and the observed maximum to 2.63 ms.
- On the resident development panel, W/T/L remained 10/1/5 and timing is bounded by the
  already platform-safe V468 controller.
- `platform_run_v543_fast_lazy_adaptive.py` locks the artifact, complete holdout statistics,
  packaging audit, and replaced agent/submission identity. It refuses a second mutation once
  its result file exists.

Evidence files are retained under `/data/separate_troll_farm-working/panels/` and
`/data/separate_troll_farm-working/analysis/`.

## Live rollout and startup-hardening follow-up

At a 68-game live snapshot, V543 had 37 wins and 31 losses. Seven first-action timeouts were all
in its initial batch; the next 51 games contained none, which does not support a persistent
per-turn compute failure. The room reading at 43% uncached progress was 12.62 / rank 165 and was
not mature.

V545 tested the remaining source-size hypothesis by exporting only the repaired R1FA controller.
Its compact source was 70,981 units and its optimized code/data footprint was 31% below V543's.
It nevertheless failed the 192-game development gate: turn-100 own score fell from 93.0 to 16.0,
turn-200 from 176.2 to 141.1, and losses rose from 12 to 27. The late score gain (+116.3) did not
repair the opening. V545 was not published; see
`V545-FIRST-OUTPUT-HARDENING-RESULTS-2026-09-04.md`.
