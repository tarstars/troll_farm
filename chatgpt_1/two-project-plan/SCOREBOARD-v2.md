# Joint scoreboard, version 2 — dated source evidence

2026-09-07; chatgpt_1; extension E4. This appends to SCOREBOARD.md; it does not rewrite that packet. M = tarstars/troll_farm@67b2acc1e828cf25a7e6e76c2814dfcd3268a45c; N = tarstars/separate_troll_farm@badf27efee7eca794c149f0707c087f7ed1eb0ff; W = M:neighbour/separate_troll_farm/working-storage/.

## What changed

All 33 neighbour rollouts previously listed in SCOREBOARD.md now have a calendar date; 31 of those also have an observed complete-poll timestamp or confirmation interval. V100 is an additional dated rollout, not a new independent recheck of V125. Thus the combined documentary inventory is **31 main + 34 neighbour = 65 rollout assertions**, plus the separately identified September 7 poll of the same V439 deployment. This is not 65 independent samples of one policy.

The new raw-ledger transcription is dated-neighbour.csv: **32 unique submission IDs**, with exact UTC timestamps and source paths. For 31 rows, the inspected final poll records matching expected/actual agent, at least 160 listed games, zero pending, 100/100 progress and inProgress=false. V353 records 161 rather than 160 games. V2 uses an older schema: its 65.1-minute poll and README assert maturity, but that poll does not supply the modern count certificate. The other two neighbour entries below are primary mature-result reports, not newly parsed raw archives.

A timestamp is the retained observer's reading, not necessarily the first instant rollout completed. Success fetching a room, an early objective flag and source commit time are not maturity. Later polls of one unchanged deployment do not increase the resubmission sample size. No games were replayed for this table.

## Source key

**L:** M:local_claude_1/ladder-measure/ledger-2026-08-26.md, blob ad0368aa2fee13d139585ca761a9d0b255f94943. These 15 rows retain the older ledger's precision and maturity assertions.

**J:** M:local_claude_1/ladder-queue/readings.jsonl, blob 2909dab7526e157f2cbb1f2d9ae04cc2c09c70f0. These 16 rows are the final records, not early_looks. Original audit.py verifies the transcription against that blob when a pinned checkout is supplied.

**D/V-number:** exact W source path in dated-neighbour.csv; the number is a publication label, not necessarily a new program. Most are W:root-artifacts/platform-readings-<label-and-description>.jsonl; V438 and V440 instead reside under W:monitor/v438/ and W:monitor/v440/. The CSV preserves all timestamp fractional seconds; this display omits those fractions.

**R543/R439:** N:V543-MATURE-PLATFORM-RESULTS-2026-09-04.md and N:V439-RESTORATION-MATURE-2026-09-05.md. **P:** the September 7 working-tree WORKSTATE.md snapshot in M, not the older N HEAD document. The unchanged old scoreboard supplies descriptions and original identity fields; LINEAGE-DIFF corrects its misleading V468 alias for our champion.

## One combined table

Times are UTC in 2026. A denotes the old diagnostic champion; B adds goal keeping; C is the main denial-off champion. Rank is the recorded place, not a fixed strength unit. A dash in the last column means no contemporaneous top-ten boundary has been joined. 'Daily' is a separately captured same-date boundary, not an exact same-minute pair.

| Observed UTC | Project / artifact or change | Submission | Rating | Rank | Source / top-ten boundary |
|---|---|---:|---:|---:|---|
| 08-26 18:52 | M A, diagnostics | 41198581 | 21.8 | 40 | L / — |
| 08-26 22:20 | M B, keep goal | 41199973 | 18.4 | 82 | L / — |
| 08-27 00:28 | M B repeat | 41200547 | 19.2 | 68 | L / — |
| 08-27 02:31 | M A repeat | 41200776 | 21.6 | 40 | L / — |
| 08-27 04:31 | M A repeat | 41201060 | 22.1 | 37 | L / — |
| 08-27 06:33 | M B repeat | 41201376 | 21.0 | 43 | L / — |
| 08-27 07:57 | M banana-farm viewing run, mechanics failed | 41201668 | 10.8 | 172 | L / — |
| 08-27 09:25 | M C, denial off | 41202036 | 21.2 | 42 | L / — |
| 08-27 14:36 | M apple farm 1 | 41203549 | 19.8 | 49 | L / — |
| 08-27 16:41:18 | M apple farm 2 | 41203992 | 19.8 | 50 | L / — |
| 08-27 17:46 | M apple farm 3 | 41204464 | 18.6 | 78 | L / — |
| 08-27 18:53 | M apple farm 4 | 41204747 | 19.9 | 47 | L / — |
| 08-28 03:06 | M skill floor 1, delayed read | 41205061 | 19.2 | unavailable | L / — |
| 08-28 04:17 | M skill floor 2 | 41206278 | 19.06 exact stamp | unavailable | L / — |
| 08-28 05:37 | M skill floor 3 | 41206409 | 17.3 | 103 | L / — |
| 08-28 07:47:03 | M three heroes 1 | 41206680 | 11.71 | 169 | J / — |
| 08-28 08:52:05 | M three heroes 2 | 41206957 | 12.03 | 167 | J / — |
| 08-28 12:07:05 | M orchard 5, first | 41207673 | 14.65 | 144 | J / — |
| 08-28 13:12:08 | M orchard 5, repeat | 41207963 | 13.51 | 159 | J / — |
| 08-28 14:17:03 | M apple farm 6 | 41208249 | 17.59 | 99 | J / — |
| 08-28 15:22:03 | M C restored | 41208579 | 18.19 | 85 | J / — |
| 08-28 19:17:05 | M orchard 6 | 41209711 | 18.84 | 70 | J / — |
| 08-28 20:22:00 | M orchard 7, first | 41209967 | 16.66 | 114 | J / — |
| 08-28 21:27:03 | M orchard 7, repeat, 162 games | 41210228 | 16.64 | 117 | J / — |
| 08-28 23:05:25 | N V2, guarded early candidate | 41210542 | 23.03 | 32 | D/V2, weaker maturity schema / — |
| 08-30 06:34:28 | N V100, guarded lean farm | 41215495 | 24.03 | 25 | D/V100 / — |
| 08-30 10:36:40 | N V108, banana supply | 41216145 | 22.90 | 32 | D/V108 / — |
| 08-30 11:25:15 | N V115, exact V54 recheck | 41216293 | 23.53 | 29 | D/V115 / — |
| 08-30 12:10:23 | N V121, exact V54 recheck | 41216441 | 22.92 | 31 | D/V121 / — |
| 08-30 12:56:01 | N V125, exact V100 recheck | 41216602 | 23.76 | 26 | D/V125 / — |
| 08-30 13:38:17 | N V133, priority tuple | 41216748 | 22.30 | 35 | D/V133 / — |
| 08-30 14:23:58 | N V137, sparse farm guard | 41216910 | 23.35 | 28 | D/V137 / — |
| 08-30 15:12:56 | N V140, guarded compact tuple | 41217058 | 21.52 | 37 | D/V140 / — |
| 08-30 16:18:22 | N V152, early tuple / late scalar | 41217305 | 22.72 | 30 | D/V152 / — |
| 08-30 21:24:34 | N V231, entrance action tax | 41218295 | 24.01 | 25 | D/V231 / — |
| 08-30 22:18:02 | N V236, ahead-only entrance tax | 41218425 | 23.05 | 29 | D/V236 / — |
| 08-30 23:01:32 | N V248, dense apple permission | 41218538 | 22.45 | 32 | D/V248 / — |
| 08-30 23:47:15 | N V251, enemy-arrival guard | 41218608 | 23.81 | 27 | D/V251 / — |
| 08-31 00:31:08 | N V256, shorter distance guard | 41218724 | 23.65 | 28 | D/V256 / — |
| 08-31 05:16:08 | N V258, dynamic-only guard | 41219291 | 24.59 | 21 | D/V258 / — |
| 08-31 06:48:51 | N V266, small-deficit entrance tax | 41219458 | 22.85 | 30 | D/V266 / — |
| 08-31 07:32:09 | N V274, arrival and crop pressure | 41219594 | 23.32 | 28 | D/V274 / — |
| 08-31 13:40:10 | N V311, idle fruit rescue | 41221074 | 24.67 | 22 | D/V311 / — |
| 08-31 14:29:07 | N V314, underfoot apple harvest | 41221356 | 22.72 | 30 | D/V314 / — |
| 08-31 17:59:53 | N V350, exact V311 recheck | 41222477 | 24.79 | 20 | D/V350 / — |
| 08-31 18:45:29 | N V353, exact V314 recheck, 161 games | 41222732 | 23.22 | 29 | D/V353 / — |
| 08-31 19:30:46 | N V356/source V355, banking swap | 41222915 | 22.60 | 30 | D/V356 / — |
| 08-31 20:49:46 | N V370/source V368, crop finish | 41223244 | 25.21 | 17 | D/V370 / — |
| 08-31 22:34:11 | N V381/source V379, collecting finish | 41223623 | 24.73 | 22 | D/V381 / — |
| 09-01 00:39:47 | N V392/source V390, specialist pressure | 41223986 | 21.15 | 38 | D/V392 / — |
| 09-01 03:30:48 | N V414/source V413, doorway escape | 41224374 | 22.66 | 32 | D/V414 / — |
| 09-01 04:21:18 | N V417/source V416, empty-worker escape | 41224449 | 24.95 | 20 | D/V417 / — |
| 09-01 05:22:50 | N V421/source V420, joint clear | 41224609 | 23.54 | 27 | D/V421 / — |
| 09-01 06:17:06 | N V424, exact V368 recheck | 41224723 | 21.06 | 37 | D/V424 / — |
| 09-01 07:59:48 | N V438/source V437, payback-window swap | 41225002 | 22.07 | 35 | D/V438 / — |
| 09-01 09:02:57 | N V440/source V439, earlier swap | 41225204 | 22.91 | 29 | D/V440 / — |
| 09-02 09:07:10 | M C fresh baseline | 41230202 | 17.04 | 110 | J / — |
| 09-03 05:17:08 | M orchard 8 | 41234498 | 17.98 | 89 | J / — |
| 09-03 06:22:09 | M C restored | 41234663 | 18.14 | 86 | J / — |
| 09-03 14:17:17 | M opening dispatcher | 41236483 | 14.59 | 147 | J / — |
| 09-03 15:22:09 | M C restored | 41236823 | 18.72 | 72 | J / — |
| 09-04 07:22:11 | M optimized three-worker opening | 41239996 | 14.07 | 154 | J / 26.73 later daily snapshot |
| 09-04 08:27:09 | M C restored, NOT N's source V468 | 41240269 | 19.23 | 60 | J / 26.73 later daily snapshot |
| 09-04, exact mature-poll time not joined | N V543, adaptive four-worker economy | 41242929 | 13.92 | 155 | R543 / 26.73 later daily snapshot |
| 09-05 08:45:32–08:50:55 | N exact V439 restored and confirmed | 41245746 | 23.43 | 28 | R439 / 26.73 daily snapshot |

Later observation, not another rollout: **09-07 V439, same submission 41245746 / agent 6704418, 23.35 / rank 28 of 178**, from P. It is not entered a second time into a noise estimate.

## Captured target boundary, without backfilling older dates

| Snapshot | Rank 7 | Rank 10 | Source |
|---|---|---|---|
| 09-04 22:49 UTC | putibuzu 26.99, agent 6479779 | R1FA 26.73, agent 6479863 | N:V587-RANK7-GAP-RESULTS-2026-09-04.md |
| 09-05 pre-confirmation freeze | putibuzu 26.99, agent 6479779 | R1FA 26.73, agent 6479863 | W:baseline-restoration/2026-09-05/pre-confirmation-board.top80.json |
| 09-06 policy-flat freeze | viewlagoon 26.99, agent 6481504 | R1FA 26.73, agent 6479863 | W:planning/2026-09-06/policy-flat-field/plans/leaderboard.top80.json |
| 09-07 known-map freeze | viewlagoon 26.99, agent 6481504 | FreZzz 26.73, agent 6482071 | W:planning/2026-09-07/chopup-known-map-diagnostic/freeze/leaderboard.top80.json |

The last three whole-file Git blobs are respectively 2cd9ac7a26283d59f834a9e776e25ffb18c38ee3, a61ab72a75ac4a0a4a0b0f623d346de2b0a7eaa, and 5291c46634937fb7eadaf9fe503c29cbf11d7d68. Same rating at rank ten does not mean same opponent. CreationTime inside a player record is not the collection timestamp.

## Same-day comparisons and variability

On August 28, M C read 18.19, orchard 6 read 18.84 and N V2 read 23.03: numerical differences +4.84 and +4.19, respectively. These are same-calendar-day observations but neither randomized matched blocks nor the final V439 source. They support the neighbour as an important comparison lineage; they do not attribute a gain to one wrapper.

September 4's M C=19.23 and September 5's restored V439=23.43 are **not same-day**. The same-date neighbour V543=13.92 is a different program with seven startup failures in its rollout. Excluding those failures would change the question, not repair the primary deployment result.

V368's exact source read 25.21 as V370 on August 31 and 21.06 as V424 on September 1: a 4.15 range from two different rollouts. The code did not improve and then regress by that amount. Two observations are not a stable variance estimate. The neighbour's earlier '23 readings, spread 1.1' remains a source claim whose exact membership has not been reconciled; do not pool changed candidates to estimate identical-file noise.

M's recent five identical-file readings give mean 18.264, sample SD 0.81549 and range 2.19; those are arithmetic reproduced by extension_audit.py, not a guarantee that future ladder noise is stationary. The August 27 reading of the same source at 21.2 also warns that a wider historical interval is a different population. Repeated room polls are never new arms.

## What remains incomplete

This is a stronger, dated replacement for the **previously enumerated** table, not certification of every August 20–September 7 rollout. Earlier main August 20–25 records, other neighbour ledger families including original V54, and the precise membership of the 23-reading aggregate still require a full archive inventory. Most older exact-date top-ten snapshots remain unjoined. A dash is not a guessed boundary. The optional pinned-checkout audit scans all available copied reading files and flags unfamiliar schemas; it was not executed here because complete checkouts were unavailable.

The 65 count is explicitly the inventory of this displayed table. It must not be promoted to 'all experiments performed' or '65 independently verified archives'. The new CSV was locally checked for 32 unique submissions and parseable timestamps; comparison with the remote raw records was by direct inspection, not a bulk local extraction.
