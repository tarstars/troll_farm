# D41b exact-prior residual actor — preflight result (2026-07-21)

## Verdict

**PASS all seven gates and open one separately frozen residual-PPO development experiment.** The
standalone exact-prior kernel and zero-residual actor reproduce D40 exactly closed-loop. This is a
qualified learning initializer, not a submission candidate, and it authorizes no confirmation or
platform action by itself.

The authoritative artifact is `d41b-exact-prior-preflight-2026-07-21.json`, SHA-256
`4835c6394af31eede2830fba892520ad8f9c0b23394965649ea343fa18f053fe`.

## Exact development result

Both independent runs cover 512 tasks on maps 9,711,000--9,711,031 and make exactly 84,014
in-scope decisions.

| Branch | Decisions | Exact D40 matches, run A | Exact D40 matches, run B |
|---|---:|---:|---:|
| TRAIN | 40,073 | 40,073 | 40,073 |
| Deficit | 5,821 | 5,821 | 5,821 |
| Evacuation | 352 | 352 | 352 |
| Rate | 37,768 | 37,768 | 37,768 |
| **Overall** | **84,014** | **84,014** | **84,014** |

All 512 terminal rows match the D40 baseline on scores, margin, workforce, training count, crops,
invalidations, integrity counters, action hash, and state hash. Run A and run B also have identical
decision SHA-256 `813c9733...45b04545` and terminal SHA-256 `ce75ef00...c119e04`.

The unchanged behavior is strong on this block:

- mean own/opponent score: 221.139 / 175.146;
- mean margin: **+45.992**;
- worker two / worker three: 98.05% / 93.16%;
- crop creation: 100%; and
- invalid direct commands, provenance failures, relevant prediction failures, and worker-cap
  violations: zero.

## Deployment and integrity

- The Rust prior independently decodes and orders observation fields; it does not consume the
  teacher index. Its full standalone source is **5,978 bytes**, below the 10,000-byte gate.
- Rust's `(x, y)`/`Option<Cell>` ordering and stable action-ID totalization have focused tests.
- The reserved `44 -> 16 -> 1` residual has exactly **737 parameters**, 2,948 float32 bytes or 737
  int8 bytes. With zero final output it preserves the prior argmax at every visited decision.
- The full release library builds, the direct Rust prior-vs-D40 episode test passes, and fourteen
  focused Python macro/clone/prior tests pass.

The kernel SHA-256 is `632f1b2c99c18073c4cd956863fcaa4b7e9773dd69bb745fc18f062337130f62`.

## Interpretation and next step

D41b removes the D41a approximation bottleneck without changing D40 behavior. It also creates a
safer policy-improvement surface than earlier end-to-end PPO: the exact macro controller remains
frozen and only a small residual can change candidate ranking.

D41c may now run exactly one preregistered conservative residual-PPO pilot against terminal margin.
Its initialization must be byte-for-byte D40 under deterministic argmax; training must expose exact
prior ranks rather than recompute them in slow Python; and final evaluation must beat D40 on a new
development block without losing its workforce/crop invariants. Confirmation, candidate
construction, TestSession, submission, and Arena stay sealed until that gate passes.
