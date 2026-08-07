# E7a single logical deletion — untouched equality result

Status: **UNTOUCHED EXACT-EQUALITY PASS / QUALIFIED BUT NOT DEPLOYED**

## What was deleted

The candidate removes the generic greedy action selector for friendly rosters above two trolls.
The exact live policy has a hard training cap at two, so that selector cannot run in supported
play. The exact zero-, one-, and two-troll paths are unchanged. If an unexpected larger roster
is ever supplied, the candidate fails safe with one `WAIT` per friendly troll.

- Exact live baseline: 62,820 bytes, SHA-256
  `97bfe71e3f2f05e1b8fa3c697c5e5db3624ac9739e90954e9fa9be79a8e48595`.
- Candidate: 62,278 bytes, SHA-256
  `ab0934740171cc7f5f4cd65cdfb8cf879ca92d8236c9505903e4741e0a7c57c2`.
- Real reduction: 542 bytes (0.863%).
- No renaming, minification, compression, or formatting-only reduction.

## Evidence before the untouched gate

- Exact rebuild, optimized compile, and empty input: pass.
- Ten frozen semantic fixtures: exact.
- Twenty-five public liveness-counterexample games: 7,234 teacher-forced command lines, zero
  differences.
- Ordinary development panel: all 516 terminal tasks exact, including scores, resources,
  training, workers, turns, liveness, and issue fields.

## One-shot untouched gate

The seed range 9,867,000--9,867,042 was collision-audited without broad recursive searches,
then frozen and remotely verified before any map was generated. The one-shot run covered 43
official-generator maps, both seats, and six opponent families: 516 paired tasks.

- Verdict: `UNTOUCHED_EXACT_EQUALITY_PASS`.
- Different terminal tasks: **0/516**.
- Mean paired margin delta / bootstrap 95% lower bound: **0.0 / 0.0**.
- All six family means and both seat means: **0.0**.
- Catastrophes: **30 -> 30**.
- Negative-margin mass: **6,084 -> 6,084**.
- Second-worker training coverage and median delay: **516/516 / 0 turns**.
- Period-2 episodes of length at least six: **106 -> 106**.
- Latency p95 ratio: **1.0260**; candidate maximum: **8.215 ms**; pass.
- Critical and unclassified issues: zero.
- Run time: 116.524 seconds.

Fresh result JSON SHA-256:
`973ebe786006532b76dcd089157026ff2cecd473b965fcbffc3397f0aeeea340`.
Fresh panel TSV SHA-256:
`86ce79fcf630d58432e62128eaa99f64adc8018b94ded283feb460e06dccf9f7`.

## Promotion decision

The source is fully qualified as a smaller, behavior-exact equivalent of live E7a. It has zero
measured or expected score improvement, however. Publishing it would reset the mature rank-11
submission without a gain outside rating noise, so the no-churn rule applies: **the Arena bot is
unchanged**. Keep this candidate as the simplified equivalent source; deploy it only as part of a
later materially improving successor or under an explicit owner instruction.
