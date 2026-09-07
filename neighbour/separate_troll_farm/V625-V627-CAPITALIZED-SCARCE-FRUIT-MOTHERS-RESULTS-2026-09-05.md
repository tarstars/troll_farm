# V625--V627 capitalized scarce-fruit mothers: sources mature after the bill window -- 2026-09-05

## Verdict

V625--V627 invested the first deficient plum, lemon, or one of each in a protected water-first
mother near the shack before reserving later fruit for the minimum useful `1/2/1/2` third worker.
The sources were real: V625 planted a plum mother by turn 220 in 17 of 24 rows, V626 planted a
lemon mother in 19, and V627 planted both selected mothers in 16. They did not fund a useful
workforce soon enough. V625 never trained the worker; V626 and V627 trained it in only two rows
each, at turns 213--219 and turn 210 respectively.

The final arms scored `+0.00/-8.46/+0.33`, `+0.00/-14.71/+1.17`, and
`+0.00/-14.13/-0.08` at turn 100/200/final. All failed the middle checkpoint and the required
+40 endpoint. The two trained V626 rows averaged -20.00 own score at the end versus their V468
baselines; the two trained V627 rows averaged -9.50. Capitalizing one finite fruit into a serial
power-one source therefore shifts the remaining shortage between plum and lemon but cannot repay
the source investment, worker bill, and late train before the match ends.

No frozen 192-game panel, fresh-map panel, duel, packaging audit, production change, or platform
publication ran.

## Candidate family

`build_v625_capitalized_scarce_fruit_mothers.py` applies V622's final staged-orchard controller to
the exact `candidate_v468_no_denial_bonus_module.rs` base. All arms remain command-identical to
V468 through turn 100 and keep the same `1/2/1/2` third-worker bill. The family adds:

- source modes for plum only, lemon only, or both types;
- first-deficient-fruit capitalization while no own crop of that type exists;
- a water-adjacent plot preference ahead of the existing shack/farmer-distance fit;
- typed attempted-plant reconciliation, own-source provenance, and deficit-time chop protection;
- a selected uncapitalized source rank ahead of ordinary deficit/travel order, followed by local
  repeated harvest and immediate banking;
- V622's post-train harvest--plant--mature-banana worker lane, with no fourth-worker spending.

V622's dead refill counter and urgency branch were removed to pay for this state without changing
the active mechanism. The three generated controllers differ only in their two source-mode
booleans.

| arm | capitalized sources | compact UTF-16 units | module SHA-256 |
|---|---|---:|---|
| V625 | plum | 99,925 | `007270980125348737964616ae0207754a32d3a5f16dadf353c6d84f813fdd8e` |
| V626 | lemon | 99,925 | `14d1d0767942dfff97e898891d1666fedb89f17367706f75fc4a8c6797fa4af7` |
| V627 | plum and lemon | 99,924 | `d65290c3c2ae1a9af62b668537140d298c2a04b480590511137da6351b66c085` |

All readable programs compiled independently with Rust 2021 and optimization. The compact files
remain 75--76 UTF-16 units below the platform limit.

## Test-first implementation and source-priority repair

`test_build_v625_capitalized_scarce_fruit_mothers.py` first failed collection because its builder
did not exist. Its final 13 tests cover exact V468 prefix retention, the common minimum staged
worker, registered and isolated source modes, the selected-kind predicate, one live mother per
type, water-first plots, bill/source protection, selected-source harvest rank, retained worker
lifecycle, removal of dead refill state, standalone compilation, emitted artifacts, and compact
size.

The first smoke exposed a real controller defect rather than a gate result to accept. When both
fruit types were deficient, the existing deficit-first nearest-source ordering could repeatedly
choose one type and never collect the first fruit needed to establish the other mother. A focused
regression test failed before adding the `capitalization_rank` key and passed afterward. The
unprioritized V625/V626/V627 intermediates trained zero later workers and scored respectively
`+0.00/-8.46/+1.46`, `+0.00/-11.92/-1.88`, and `+0.00/-8.08/+4.75`.
The repaired ordering created two trains each in V626 and V627, proving that the intended source
path executed, but worsened the final gates to the canonical results below.

The focused suite passed 13 tests, the complete repository suite passed 332 tests in 106.53
seconds, and all three final readable candidates compiled independently.

## Final smoke gate

Each arm ran map 9941000 in both seats against the registered 12-family opponent set, producing 24
paired games. All first command divergences were turn 101.

| arm | delta t100 | delta t200 | delta final | candidate score | candidate wood | opponent score delta | workers | candidate W/T/L |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| V625 | +0.00 | -8.46 | +0.33 | 215.79 | 51.29 | +36.46 | 2.00 | 16/0/8 |
| V626 | +0.00 | -14.71 | +1.17 | 216.62 | 51.54 | +32.54 | 2.08 | 16/0/8 |
| V627 | +0.00 | -14.13 | -0.08 | 215.38 | 51.17 | +33.67 | 2.08 | 16/0/8 |

V468 scored 94.67/160.67/215.46 at turn 100/200/final, banked 53.21 wood, and went 19/1/4.
The final source arms added harvests but converted them into neither wood nor a timely roster:

| measure per game | V468 | V625 | V626 | V627 |
|---|---:|---:|---:|---:|
| total plants | 13.38 | 12.08 | 12.12 | 12.62 |
| banana plants | 7.96 | 8.42 | 8.29 | 7.62 |
| harvests | 2.00 | 9.04 | 10.12 | 10.83 |
| chops | 182.79 | 146.12 | 146.29 | 146.46 |
| moves | 275.67 | 317.33 | 327.54 | 318.83 |
| waits | 11.00 | 50.21 | 47.12 | 55.83 |
| wood | 53.21 | 51.29 | 51.54 | 51.17 |

V625 planted 1.38 plums, 1.83 lemons, 0.46 apples, and 8.42 bananas per game. V626 planted 0.54
plums, 2.92 lemons, 0.38 apples, and 8.29 bananas; V627 planted 1.58 plums, 2.92 lemons, 0.50
apples, and 7.62 bananas. More typed fruit production displaced chops and stretched games to
295.6--296.4 turns without raising wood.

## Capitalization and bill audit

V625's first turn-101--220 plum mothers appeared at median turn 124. V626's lemon mothers appeared
at median turn 138. In V627 the first plum appeared at median turn 124, but serial collection
pushed the first lemon to median turn 161.5. The dual arm had both mothers in place by turn 220 in
only 16 rows.

The turn-220 checkpoint includes bank plus all own carried stock. Excluding the two rows that had
already trained and rows whose games ended before the checkpoint, the remaining bill state was:

| arm | surviving untrained rows | mean plum | mean lemon | mean apple | mean iron | plum-short rows | lemon-short rows |
|---|---:|---:|---:|---:|---:|---:|---:|
| V625 | 23 | 2.22 | 4.78 | 4.00 | 6.04 | 8 | 19 |
| V626 | 21 | 1.57 | 5.48 | 4.00 | 6.05 | 13 | 7 |
| V627 | 21 | 1.86 | 5.00 | 4.00 | 6.05 | 10 | 15 |

Every audited untrained row had the required three apples and six iron. Plum-only capitalization
solved plum more often but left lemon short; lemon-only solved lemon more often but consumed the
same serial farmer window and left plum short. The dual source made lemon later and usually lacked
one or both. Only two V626 rows crossed the joint bill, at turns 213 and 219, and only two V627
rows crossed it, both at turn 210. Those workers arrived after the failed turn-200 checkpoint and
had too little runway to recover their costs.

The mechanism is not a missing source-recognition rule: source-aware priority materially created
late trains. It is the chronology of using one power-one starter to acquire a seed, travel, plant,
wait for maturity, harvest repeated fruit, and bank six lemons while also acquiring three plums.
A direct harvest-and-chop third worker is closed under this exact-prefix serial source path.

The canonical panels, gate and diagnostic JSON, turn-220 states, unprioritized intermediates,
standalone binaries, panel runners, and build logs are archived under
`/data/separate_troll_farm-working/archive/2026-09-05-v625-v627-capitalized-scarce-fruit-mothers/`.

## Decision

Queue item 35 closes single-starter mother capitalization as a way to fund the minimum useful
third worker. Queue item 36 tests a structurally different bridge: train a stock-light
`1/1/1/0` producer for `3/3/3/2`, use its independent action stream to multiply local fruit, and
only then attempt a harvest-and-chop worker. This lowers the still-binding lemon and iron bill
without pretending that another serial source-ordering adjustment can meet the current deadline.

Production remained byte-identical: `bot.rs` SHA-256
`b8d2c4e298d7d748612b64b1a91c3d88826c467846f9544d0df1b86279588372` and `submission.rs`
SHA-256 `922a233526ed590dafcc6302461de2dafef720fb003bd2359f55dfd93ac1b4a7`.
The neighboring read-only repository remained at
`370fa63cae12eda129ff5553c33a7086dfcb87c2`; its pre-existing modified stats file and untracked
panel JSON were not touched.
