# E7a single logical deletion — development qualification

Status: **DEVELOPMENT EXACT-EQUALITY PASS / UNTOUCHED TRANSFER PENDING / NO ARENA ACTION**

## Candidate

- Exact live baseline: 62,820 bytes, SHA-256 `97bfe71e...`.
- Candidate: 62,278 bytes, SHA-256
  `ab0934740171cc7f5f4cd65cdfb8cf879ca92d8236c9505903e4741e0a7c57c2`.
- Real deletion: 542 bytes (0.863%).
- Deleted logic: the generic greedy action selector for friendly rosters above two.
- Preserved invariant: the exact live `can_train` path refuses training at `n >= 2`.
- Unexpected larger roster: one `WAIT` per friendly troll, rather than the removed selector.
- No identifier renaming, compression, minification, or formatting reduction.

## Static and semantic evidence

- Builder rebuild: byte-identical.
- Optimized standalone compile: pass.
- Empty input: pass with zero output and stderr.
- Sacred source: exact at SHA-256 `fff6669b...`.
- Ten live-baseline semantic fixtures: exact pass. These cover four E7a focus-sector cases,
  the training bill, training-deadline fallback, wood banking, same-target assignment,
  landing collision, and endgame deadline.

## Exact public-live command parity

The candidate and exact baseline were independently compiled and run on the 25 immutable public
E7a liveness counterexamples. All replay data was fetched read-only and held in memory.

- Games: 25/25.
- Teacher-forced turns: 7,234.
- Games with any command difference: **0**.
- Unknown replay updates: 0.
- Candidate stderr: 0.
- Result SHA-256: `4ca7d02a14d58aced168c547bcba3fe50980cd8e926885c34ac0b0223bed50d7`.

The maximum period-2 episode is 128 in both sources. This deletion deliberately preserves the
live bot, including its inherited liveness defect; it neither claims nor attempts an oscillation
repair.

## Full development equality

The exact runner adaptation changes only the candidate's data-layout conversion and constructor
from the half-size type to the full live E7a type. Generated runner SHA-256:
`d9a118d715ab0b5f0e55f2a5a846afaa9007b725a3de1cad605feadb69a83c18`.

The ordinary consumed development panel contains 43 official-generator maps, both seats, and
six frozen opponent families: 516 paired tasks. Every frozen equality field matches:

- different terminal tasks: **0/516**;
- mean paired margin difference: **0.0**;
- bootstrap lower bound: **0.0**;
- catastrophes: **19 -> 19**;
- negative-margin mass: **4,138 -> 4,138**;
- second-worker training, final worker count, terminal turn, wood, liveness, legality, critical
  and unclassified issue fields: exact on every task;
- latency p95 ratio: 1.0041; candidate maximum 6.276 ms; both pass.

Panel TSV SHA-256: `8a1de05402ecde0c5b95cfc8ce97dbe8c45550fade49021fa93a20a52c626c5f`.
Result JSON SHA-256: `878d05b8c7a7739de01c69d22d94f63fe46cb921879e9e2f5d6c998b40cad116`.

## Boundary

This is development qualification only because maps 9,854,000--042 were already consumed. A
new map range must be collision-audited, frozen and remotely published before its one-shot
untouched equality run. No Arena action is allowed before that result and promotion preflight.
