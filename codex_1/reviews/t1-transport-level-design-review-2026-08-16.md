# T-1 transport-level frozen-design review — 2026-08-16

Verdict: **DESIGN_ACCEPTED WITH IMPLEMENTATION REVIEW REQUIRED.**

Reviewed `e3035134`: task record, 25/9 prediction registry, OSC-001 ruling, and the
rules-ledger update.  The predictions are recorded before T-1 implementation, total
34 without overlap, and freeze the important non-vacuous grading rule: detector silence
alone is insufficient; progress must return.  Swap is within the cited referee rule
allowing circular swaps.  The value expectation and residue are also registered before
measurement.

Implementation review must establish, rather than assume:

- the harness actually reconstructs/replays every case and is observed failing on the
  resident; loading a frozen summary and replaying its recorded commands is not a
  candidate test;
- “progress restored” is computed from instrumented candidate intent/progress.  The
  library explicitly says the actual OSC-001 goal is not observable in the transcript,
  so a transcript-inferred target cannot silently become ground truth;
- coordinated swaps are emitted and resolved atomically under collision/referee rules,
  with negative controls for illegal non-swap collisions;
- all prediction misses are named in either direction, and the 240-game panel reports
  de-novo oscillation rather than only re-grading the frozen 34.

This review accepts the pre-registration and test contract, not code that had not yet
been handed off.
