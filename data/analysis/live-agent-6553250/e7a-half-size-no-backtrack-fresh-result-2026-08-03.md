# E7a half-size no-backtrack fresh result — 2026-08-03

Status: **TERMINAL FRESH REJECTION / NO ARENA ACTION**

## Exact locked run

- Candidate: 31,248 bytes, SHA-256
  `a767e36228c872ad566b4347825f5282f95e50ae9f59fcf5a42b682989d85fea`.
- Range: seeds 9,865,000--9,865,042, 43 maps.
- Panel: both seats x six frozen opponent families = 516 paired tasks.
- Pre-run lock commit: `db1903bf060607d02a95539d5f32bb16485e3d68`, remotely verified before execution.
- Launcher/evaluator SHA-256:
  `dc9c803f66fa2511011793efce2073e0c1928b207388228718bf2d0a34616b14`.
- Generated runner SHA-256:
  `227b2d8282293c4adfab028c8229a62cdd7844ce0d80fc9a23b05b6e3de633ab`.
- Execution: the exact locked command ran once, exited zero, and saved 516 tasks in 105.477
  seconds.
- TSV SHA-256:
  `cfebefafd692a6d19851cb28e150be5724b9aab3c45f50a62951867a967465cc`.
- Result JSON SHA-256:
  `4613597dd3e2fab4a5e9dd0b949181c2ce301a5b045ec92670efb77bf2695bb3`.
- Sacred source remained exact at SHA-256 `fff6669b...`.

## Verdict

`REJECTED_OPEN_PANEL`. Twelve of thirteen gates pass:

- mean paired margin **+3.91667**;
- bootstrap 95% lower bound **-1.18217**, above the frozen -2 floor;
- catastrophes improve **14 -> 8**;
- negative-margin mass improves **3,908 -> 3,549**;
- both seats are positive: +3.7248 and +4.1085;
- worker-two coverage is 516/516 with median delay zero;
- period-2 episodes >=6 improve **90 -> 0**, candidate maximum zero;
- latency p95 ratio is 0.8445 and maximum is 1.367 ms;
- zero critical and unclassified failures.

The strict family-transfer gate fails because only four of six family means are nonnegative:

| Opponent family | Mean delta |
|---|---:|
| compact-gold | +6.3721 |
| gold-adaptive | +4.1395 |
| legend-balanced | **-2.9884** |
| mybot | +5.5814 |
| norx-native-three | +11.8372 |
| resident | **-1.4419** |

Legend-balanced has total delta -257 over 86 tasks; the single seed 9,865,000 seat-1 row is
-265, but removing an observed row or relaxing the gate is forbidden. Resident has total delta
-124 and 50 negative rows, so its sign is not one corrupt outlier.

## Evidence boundary

The range is consumed and this exact source is transfer-rejected. Its positive overall mean,
lower-bound pass, smaller catastrophe tail, and complete liveness repair do not override the
predeclared family gate. There will be no rerun, row exclusion, threshold adjustment, or Arena
submission for this hash.

Diagnostic attribution may now replay the preserved 516 rows, but a next attempt requires a
distinct logical successor, a newly collision-audited untouched range, and another remotely
published one-shot lock.
