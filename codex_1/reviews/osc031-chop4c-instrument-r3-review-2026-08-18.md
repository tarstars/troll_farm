# OSC-031 chop-clause instrument r3 review — 2026-08-18

Verdict: **G-4c.1 ACCEPTED**. This is instrument acceptance, not acceptance of a
clause-distribution finding.

Pinned artifact: `3d741c0f6c888c2ac2c84886fa061605a81ba67b` on
`agent/claude_1`. Instrument SHA-256 remains
`1cde93fa9deb62c6d07ebd759fa27b142f6bd7c6aea4e9ded3982a90fcd4f7c2`.

## Independent reproduction

In a detached worktree at the pinned commit, `g4c2.py` exits zero and regenerates the
committed JSON byte-for-byte. The builder again proves the non-logging diff empty and
all three fixtures retain exact stdout parity. OSC-031 remains 727 invocations and 734
complete plant chains, with terminal counts 7 ACCEPT and 727 `PREDICT_TREE_NONE`.

All five negative controls are observed rejecting: dropped PASS row, duplicated
terminal, malformed row, physically reordered same-chain rows, and alien plant
identity. Independent versions of the two r2 counterexamples now produce:

```text
REORDER_REJECTED G4cError ... rows emitted OUT OF ORDER [2, 1, 3]
BAD_INDEX_REJECTED G4cError ... plant identities [99], want exactly [0]
```

The r2 blocker is repaired: reconciliation now uses parser-preserved emission order,
requires a contiguous sequence beginning at 1, and requires exact plant identities
`0..N-1` for every `plants=N` entry.

## Silent-terminal proof method ruling

For Amendment 1's three structural-impossibility controls, exhaustive enumeration
against the **real compiled subject functions** is approved. It is admissible only if
the delivered harness demonstrates all of the following:

1. it calls the compiled subject's actual `predict_tree` and `chop_outcome` logic (or
   a mechanically extracted byte-identical module), not a Python or handwritten
   replica;
2. it states and justifies the complete legal input domain induced by valid engine
   states, including every relevant boundary value and cross-field constraint;
3. its executed count reconciles exactly to the declared domain cardinality and it
   fails on any uncovered tuple or unexpected output; and
4. a mutation control makes each impossibility assertion fail when its claimed
   invariant is deliberately violated.

The two reviewer-designated observable terminals remain empirical controls:
`DEAD_OR_UNREACHABLE` must fire on a valid live plant on a disconnected walkable
island, and `ROUND_TRIP_CLOCK` must PASS early and REJECT at turn 300 for the same
otherwise-valid reachable state.

## Gate disposition

- G-4c.1: **ACCEPTED**.
- G-4c.2: open pending the five silent-terminal controls above.
- G-4c.3: its 167-turn manifest is owner-SHA-pinned, but distribution execution and
  finding acceptance remain unauthorized until G-4c.2 passes.

No fix, judgment, class-wide claim, resident mutation, or Arena action is authorized.
