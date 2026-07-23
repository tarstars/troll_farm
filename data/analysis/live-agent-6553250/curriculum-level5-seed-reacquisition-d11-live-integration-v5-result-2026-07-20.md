# Curriculum Level 5 D11 live integration V5 result — 2026-07-20

## Verdict

**Accept fixed-recipe live integration V5.**  The complete learned controller fits under 100 kB,
compiles directly, reconstructs the D11 observation/mask ABI exactly across a full disjoint bank,
passes complete-response latency, and remains protocol-safe through 300 turns in both seats.  It is
now an eligible substrate for a separately frozen autonomous recipe/first-move selector and layered
field qualification.  Recipe 6 remains a fixed integration fixture, so V5 alone is not an Arena
candidate and does not authorize submission.

The frozen V5 protocol SHA-256 is
`428c2f00a27214d01be73a2c8486f71b4e87acfb92c4c5691238875eb45d288d`.

## Source and exact interactive audit

V5 allocates observation, mask, and logit buffers once and changes no policy or state semantics.
The complete readable Rust 2021 source is **68,988 bytes**, leaving 31,012 bytes below the limit.
It compiles with empty stdout/stderr and has SHA-256
`078929c1649b48225fd281656755bc7e21e79bb096177c6645b5166044902aa8`.

On exact D11 seeds `[7700400,7700464)`:

- 64/64 clean games, 11,623 referee turns, and **21,627/21,627 exact decision phases**;
- every complete 104-channel observation and 13-plane legal mask hash matches independently;
- every selected action is legal and every phase/action/command mapping is exact;
- all 64 episodes train, all 64 finish with the tracked crop, 63/64 register renewable harvest,
  and 190 opponent crop destructions activate; and
- no EOF, timeout, phase-count, stdout, stderr, or process failure occurs.

Complete response timing passes the unchanged conjunction:

| Metric | V4 | V5 | Gate |
|---|---:|---:|---:|
| maximum first response | 20.967 ms | **22.757 ms** | <=1,000 ms |
| warm p95 | 21.087 ms | **17.604 ms** | <=45 ms |
| warm maximum | 64.275 ms | **41.319 ms** | <=50 ms |

The machine-readable audit is
`curriculum-level5-seed-reacquisition-d11-live-integration-v5-audit.json`.

## Forced 300-turn production screen

Only after the exact/timing pass, the source ran in normal production mode on seeds 0--15, both
seats, against a waiting opponent.  The harness deliberately supplied all 300 referee turns rather
than stopping at curriculum turn 240 or local stall detection.

- **32/32 clean processes**;
- exactly **9,600/9,600 command lines**, minimum 300 per process;
- one valid action command per own worker on every turn;
- every TRAIN is exactly `TRAIN 2 2 0 2` and syntactically valid;
- maximum own workers is the expected two; and
- zero syntax, exit, EOF, or stderr failure.

The machine-readable screen is
`curriculum-level5-seed-reacquisition-d11-live-integration-v5-safety.json`.

## Conclusions and next boundary

The deployment question is now answered positively: the accepted learned actor can run as a
complete referee-facing Rust bot within source and time limits.  The remaining substantive gaps are:

1. the source still defaults to one requested recipe and does not choose an opening from map and
   opponent evidence;
2. the learned scope controls two workers, while strong field policies often fund a productive
   third worker after establishing renewable supply; and
3. curriculum opponents are mechanism tests, not a calibrated Legend field judge.

The next experiment must isolate autonomous recipe/first-move selection on top of this unchanged
V5 controller, then pass the layered field gate before any Arena request.

