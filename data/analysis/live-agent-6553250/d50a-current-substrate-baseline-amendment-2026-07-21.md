# D50a current-substrate baseline amendment (2026-07-21)

## Trigger

Before reading any D50 support or distance result, the frozen anchor check compared the first
phase matrix with the July 19 legacy matrices. The complete phase A/B matrices are byte-identical,
but 187/1,280 anchor cells differ from their historical rows: 9 `v2_hp2_farm`, 5 `v2_hp2_late`,
13 `v2_bal_farm`, 25 `norx_compact`, 4 `farm3`, 2 `farm4`, 0 `lean`, and 129 `norx_funded`.
Differences begin in turn-50/turn-100/final counters and are deterministic across the two new
processes. This is current-substrate drift relative to the July 19 runner, not D50-repeat
nondeterminism.

The mismatch makes a mixed historical/current union an invalid incremental comparator. No
coverage boolean, nearest distance, opponent group, score, ranking, or gate from D50 has been read.

## Frozen correction

Keep both completed phase matrices unchanged. With the exact same current runner binary/source,
regenerate the five legacy catalogs on the same 160 maps:

1. `baseline` (160 x 8);
2. `economy` (160 x 31);
3. `structural` (160 x 11);
4. `legend_proxy` (160 x 8); and
5. `legend_proxy_v2` (160 x 8).

The five current matrices replace the July 19 matrices **only as D50's union comparator**. The old
files remain immutable evidence of the detected drift. Freeze a checksum manifest before invoking
the support analyzer.

Mechanical acceptance now requires:

- exact unique grids of 1,280, 4,960, 1,760, 1,280, and 1,280 rows;
- exact D50 A/B byte identity;
- all eight D50 anchor rows to match their corresponding regenerated component rows after mapping
  only the label; and
- the original opening and activation gates unchanged.

## Preserved support gates

The original absolute confirmation floors remain unchanged: overall macro/full 56/36,
catastrophic macro 7, worker-rich macro 12, and rich-immediate macro/full 4/1. To preserve the
original intended increment if the current baseline shifted, additionally require:

- overall macro/full increments of at least +5/+3 over the regenerated current union;
- catastrophic macro increment at least +3;
- worker-rich macro increment at least +4; and
- rich-immediate macro/full increments at least +2/+1.

No legacy-covered current-substrate game may be lost. All other reporting, stop rules, and the ban
on fresh/platform evidence remain unchanged.
