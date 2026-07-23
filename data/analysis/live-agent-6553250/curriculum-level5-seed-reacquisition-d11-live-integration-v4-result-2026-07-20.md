# Curriculum Level 5 D11 live integration V4 result — 2026-07-20

## Verdict

V4 **accepts complete live ABI semantics but fails and closes on maximum response latency**.  The
persistent own-removal provenance bit eliminates every remaining state-reconstruction discrepancy:
all 21,695 decision phases across the full 64-game bank match exactly.  One warm response takes
64.275 ms versus the frozen 50 ms maximum, so the preregistered conjunction fails despite safe
first-response and p95 latency.

The frozen V4 protocol SHA-256 is
`7cef1c1bc8cc5e19a6271e953d2260695279658ab1c029ff38f1d0cb324363d4`.

## Static and semantic result

V4 is 68,774 bytes, compiles directly without diagnostics, and has source SHA-256
`ba93357bfcb6e201ed04a0b9c32e1304f1a64104f83649009fa3551fb2bec581`.

On exact D11 seeds `[7700300,7700364)` it completes:

- **64/64 games**, 11,586 referee turns, and 21,695 worker-decision phases;
- exact complete observation and mask hashes in every phase;
- legal selected actions and exact action-to-command mapping throughout;
- 64 successful training episodes, 63 terminal-crop episodes, and renewable harvest in 64/64;
- 183 opponent crop destructions; and
- zero process, phase-count, stdout, or stderr failure.

This accepts the live parser, navigation, 104-channel observer, legal mask, sequential two-worker
sequencing, tracker, action decoder, and TRAIN integration.  The earlier V1--V3 defects are closed.

## Timing result

Complete interactive response time includes flushed text protocol, parsing, observation and mask,
one or two K2 forwards, formatting, IPC, and output flushing:

- maximum initialization plus first response: **20.967 ms** (gate <=1,000 ms);
- warm p95: **21.087 ms** (gate <=45 ms);
- warm maximum: **64.275 ms** (gate <=50 ms; **fail**).

The production 300-turn screen remains closed because timing is a conjunction.  The V4 actor phase
allocates new 25,168-byte observation, 3,146-byte mask, and 3,146-f32 logit vectors for every worker
decision, even though all sizes are static.  This is the same avoidable allocator exposure already
removed successfully from K2 inference.

## Next boundary

V5 may persist exactly those three buffers in the controller and reuse them with `mem::take` while
the observer borrows the remaining state.  It may not change a byte of observation, mask, tracker,
actor, action, or command semantics.  V5 must prove exact parity again on a disjoint bank and pass
the unchanged latency maximum before the production screen opens.

