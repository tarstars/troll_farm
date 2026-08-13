# E7a half-size tree-edge reversal fresh result — 2026-08-03

Status: **TERMINAL FRESH REJECTION / NO ARENA ACTION**

## Exact locked run

- Candidate: 31,407 bytes, SHA-256
  `acbada47b9a3cf279ff5356a32e2965eb44cbb5ccc8d7b7e8c6f5dda3f92e847`.
- Range: seeds 9,866,000--9,866,042, 43 maps.
- Panel: both seats x six frozen opponent families = 516 paired tasks.
- Pre-run lock commit: `4fab81bc9745b496c80742451ba4c864525e6b87`, remotely verified before
  execution.
- Launcher/evaluator SHA-256:
  `8dc160a69ebb7f370dbd9b191c7cf5321c2b9b74482a59f546fb57dcda96ea2f`.
- Generated runner SHA-256:
  `542003188108650d365692b6c64ab3e67ffbc9fcac4e84403e39433847bfcccd`.
- Execution: the exact locked command ran once, exited zero, and saved 516 tasks in 98.920
  seconds.
- TSV SHA-256:
  `3ecbf8a19bc17de77afac50822d76e2b45077d8145cc37ef65abea26fe804656`.
- Result JSON SHA-256:
  `8dde5e2681a23f484a96d5ad75b94d9d9370e3a0fb57fd7688ccd64921155200`.
- Sacred source remained exact at SHA-256 `fff6669b...`.

## Verdict

`REJECTED_OPEN_PANEL`. Eleven of thirteen gates pass:

- mean paired margin **+6.29264**;
- bootstrap 95% lower bound **-1.34690**, above the frozen -2 floor;
- catastrophes worsen **12 -> 16** — gate failure;
- negative-margin mass worsens **4,567 -> 4,826** — gate failure;
- both seats are positive: +5.1860 and +7.3992;
- worker-two coverage is 516/516 with median delay zero;
- period-2 episodes >=6 improve **103 -> 0**, candidate maximum four;
- latency p95 ratio is 0.8151 and maximum is 0.837 ms;
- zero critical and unclassified failures.

Five of six family means are nonnegative, so the breadth gate itself passes:

| Opponent family | Mean delta |
|---|---:|
| compact-gold | +6.1628 |
| gold-adaptive | **-4.9186** |
| legend-balanced | +5.8140 |
| mybot | +15.1977 |
| norx-native-three | +8.7093 |
| resident | +6.7907 |

## Tail attribution boundary

The catastrophe transition is nine newly catastrophic tasks against five rescues. Five of the
nine new catastrophes share seed 9,866,014; the two worst rows are gold-adaptive seat 0 on seeds
9,866,014 and 9,866,002 at deltas -359 and -249. This concentration is diagnostic only. Removing
the seed, excluding rows, or relaxing either tail gate is forbidden.

The range is consumed and this exact source is transfer-rejected despite its positive central
value and complete liveness repair. It will not be submitted to the Arena. A successor requires
a distinct logical source, diagnostic attribution on preserved rows, and a newly collision-audited
untouched range with its own remotely published lock.
