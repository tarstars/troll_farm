# E7a iterative logical deletion — round 13 checkpoint

Status: **UNTOUCHED EXACT-EQUALITY PASS / QUALIFIED CHECKPOINT / NOT DEPLOYED**

## Outcome

Starting from the previously qualified 62,278-byte equivalent, thirteen logical blocks were
removed sequentially. Every round was built from the last accepted parent and independently
tested before the next deletion. The accumulated source is 57,677 bytes: 4,601 bytes smaller
than that parent and 5,143 bytes smaller than exact live E7a (62,820 bytes).

Candidate SHA-256:
`6b9fdc99c960b4ddc969729d9452b1e5b7b252b06f8314a8567e969e27f5ba34`.

## Accepted rounds

| Round | Deleted block | Bytes removed | Resulting bytes |
|---:|---|---:|---:|
| 1 | Private single-use configurable orchard constructor | 162 | 62,116 |
| 2 | Permanently disabled idle-starter gate and helper | 403 | 61,713 |
| 3 | Redundant enemy-door-distance storage and recheck | 226 | 61,487 |
| 4 | Fixed enemy-ETA configuration field | 63 | 61,424 |
| 5 | Fixed minimum-worker-speed configuration field | 96 | 61,328 |
| 6 | Fixed-on idle-harvest and fixed-off clock-only switches | 185 | 61,143 |
| 7 | Fixed-on door-unblocking switch | 93 | 61,050 |
| 8 | Fixed-on partial-bank-transit switch | 110 | 60,940 |
| 9 | Fixed-on ordinary idle-regeneration field | 92 | 60,848 |
| 10 | Disabled non-persistent-regeneration mode | 342 | 60,506 |
| 11 | Zero-penalty opponent-arrival risk calculation | 1,341 | 59,165 |
| 12 | Disabled preferred-only opening and deadline mode | 1,254 | 57,911 |
| 13 | Disabled movement-first tie mode | 234 | 57,677 |

The active side of every fixed switch was retained. No identifiers were renamed; no source was
compressed, reformatted, or newly minified.

## Test after every deletion

Each of the thirteen programs passed:

- byte-identical rebuild from its exact parent;
- optimized standalone Rust compilation;
- empty input with clean exit and no output;
- all ten frozen semantic fixtures exactly against live E7a;
- 25/25 public liveness-counterexample games, 7,234 command lines, with zero command
  differences, unknown updates, or stderr.

The inherited maximum period-2 episode remains 128 on the public packet. These deletions preserve
behavior; they do not claim to repair oscillation.

## Full development equality

Round 13 then ran 43 consumed official-generator maps, both seats, and six opponent families:
516 paired tasks.

- Different terminal tasks: **0/516**.
- Mean paired delta / bootstrap lower bound: **0.0 / 0.0**.
- Catastrophes: **19 -> 19**.
- Negative-margin mass: **4,138 -> 4,138**.
- Scores, resources, turns, training, workers, liveness, critical and unclassified fields:
  exact on every task.
- Candidate p95 latency ratio: **0.9772**; pass.

Development JSON SHA-256:
`5bd74e48ded38322ca6a8690c73bb7abda8490de25d164a00152e6250c53c8db`.

## One-shot untouched equality

Seeds 9,868,000--9,868,042 were narrowly collision-audited, locked, committed, pushed, and
remotely verified at commit `666e8e62` before any map was generated. The range was then run once
over the same 516-task design.

- Verdict: `UNTOUCHED_EXACT_EQUALITY_PASS`.
- Different terminal tasks: **0/516**.
- Mean paired delta / bootstrap lower bound: **0.0 / 0.0**.
- All six family means and both seat means: **0.0**.
- Catastrophes: **28 -> 28**.
- Negative-margin mass: **6,539 -> 6,539**.
- Training coverage / median delay: **516/516 / 0 turns**.
- Period-2 episodes of length at least six: **127 -> 127**.
- Candidate p95 latency ratio / maximum: **1.0872 / 19.518 ms**; pass.
- Critical and unclassified issues: zero.

Fresh result JSON SHA-256:
`77d5579594f4bb8619fe96a9f5b140b5ccf2728b1fc28b8785490b762001157a`.
Fresh TSV SHA-256:
`b72ae97a56060f07df9e2f4d3c1b76c57d625500112740e2565d793992c3a99b`.

## Decision and continuation boundary

Round 13 is a fully qualified smaller equivalent. Its measured and expected score gain is
exactly zero, so publishing it would only reset the mature rank-11 submission. Arena remains
unchanged under the no-churn rule.

Further deletion is allowed from this checkpoint only after another logical block and invariant
are recorded before generation. Active policy choices must not be removed merely to reduce size.
