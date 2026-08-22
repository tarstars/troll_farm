# E7a half-size period-2 / lean-coordination fresh result — 2026-08-03

Status: **TERMINAL FRESH REJECTION / NO ARENA ACTION**

## Exact locked run

- Candidate: 31,405 bytes, SHA-256
  `9a202242afdac6ffbb463ac4caba1cc803376a90f37066767efabc5bb9584290`
- Range: seeds 9,864,000--9,864,042, 43 maps
- Panel: both seats × six frozen opponent families = 516 paired tasks
- Launcher/evaluator SHA-256:
  `cfffdf323ab2bb05a3fd9147b76f0bd8e0a77ab9bdc7e68fda43df17caa78a67`
- Generated runner SHA-256:
  `1dee8d70fce255ed0802afd40e1e5b516bcbea6501209e83a4d84b4837fac723`
- Execution: the exact locked command ran once and exited zero; stderr reports 516 paired
  tasks saved in 107.323 seconds.
- TSV: 516 rows plus header and two latency records, SHA-256
  `f213e5f72753d4853a421cd7354a167c2ecd6e0cdd64af0923abe95bbd9f1ff9`
- Result JSON SHA-256:
  `f3757e63143e13af04435bd26397a9c9f8b0e0f8a8db8997cfcb355aa24bc488`
- Sacred source remained exact at SHA-256 `fff6669b...`.

## Verdict

`REJECTED_OPEN_PANEL`. Twelve of thirteen gates pass:

- mean paired margin **+9.45736** and bootstrap 95% lower **+1.74419**;
- all six family means positive: compact-gold +2.430, gold-adaptive +16.256,
  legend-balanced +6.988, mybot +8.244, norx-native-three +11.244, resident +11.581;
- both seats positive: +10.616 and +8.298;
- negative margin mass improves **6,149 -> 5,421**;
- worker-two coverage 516/516, median delay zero;
- period-2 episodes >=6 improve **105 -> 0**, candidate maximum three;
- latency p95 ratio 0.864, maximum 1.537 ms;
- zero critical and unclassified failures.

The terminal failure is the strict tail-count gate: catastrophes increase **26 -> 27**.
There are nine candidate-only catastrophe rows and eight baseline-only rescues, so the net
count is +1 despite substantially lower negative mass. Candidate-only rows span five roots
(9,864,005, 010, 014, 037, and 041) and multiple families; this is not a single corrupt row.

## Evidence boundary

The fresh range is now consumed. The exact candidate is transfer-rejected and may not be
submitted. It will not be rerun or threshold-tuned on this panel. Diagnostic mechanism
attribution may use the preserved rows, but any next attempt must be a distinct logical
successor with a newly collision-audited and remotely frozen untouched range. No Arena
mutation occurred.
