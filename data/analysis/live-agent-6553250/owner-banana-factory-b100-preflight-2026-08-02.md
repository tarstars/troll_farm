# Owner banana-factory + b100/e6 preflight — 2026-08-02

**Verdict: candidate mechanically ready under explicit owner override; not scientifically
qualified.** The exact 99,440-byte Arena source has SHA-256 `2d164ecbaf8a…`. It is the existing
closed-loop banana factory plus the currently deployed flat +100 / ETA<=6 opponent-crop policy.

The source compiles, exits cleanly on empty input, passes all 23 embedded semantic tests, and
matches the full generated source exactly on eight open both-seat games (2,400 command lines,
zero stderr). Interactive latency was 0.984 ms mean, 1.556 ms p95, and 4.582 ms maximum. The
slimmer rejects any change to its exact compact parent hash.

An earlier 99,656-byte attempt based on the old resident specialization was rejected: it diverged
on all eight streams, first by turn 7. It was replaced before any Arena mutation. The accepted
factory-aware slimmer fixes disabled experiment families to their constructor-exact values and is
guarded by full-source command-stream equality.

Fresh pre-submit platform state is opponent-crop resident `6589709` / `41079653`, score 23.3,
rank 32/131. Fresh IDE recovery exactly matches its 64,522-byte SHA. The owner was told that the
GitHub packet was pre-lock and unqualified, maintained the direct publication instruction, and
corrected the observation horizon to approximately 30 minutes. One submission only; never retry
an ambiguous response.

Machine-readable evidence:
`owner-banana-factory-b100-preflight-20260802T155654Z.json`.
