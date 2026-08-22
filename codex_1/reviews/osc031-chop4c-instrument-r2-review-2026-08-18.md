# OSC-031 chop-clause instrument revision review — 2026-08-18

Verdict: **REVISION_REQUIRED** on one remaining reconciliation defect. No clause
distribution is accepted as a finding.

Pinned artifact: `5fc265cad50e19c8cc1d312001a718f2081b14c2` on
`agent/claude_1`. Regenerated instrument SHA-256:
`1cde93fa9deb62c6d07ebd759fa27b142f6bd7c6aea4e9ded3982a90fcd4f7c2`.

## Independently reproduced repairs

In a detached worktree at the pinned commit, the builder and `g4c2.py` both exit zero
and reproduce the committed JSON byte-for-byte. The stripped instrument is byte-equal
to the resident, and stdout parity is exact on OSC-031, OSC-001, and OSC-008. The
runner reports 727 OSC-031 invocations and 734 complete plant chains, exercises its
dropped-row, duplicate-terminal, and corrupted-row controls, and rejects all three.

This repairs the prior review's blockers 1 and 4: every reached clause now has an
explicit PASS/REJECT row, and stripping the exact logging fragments recovers the
resident byte-for-byte. The task-owner amendment also supersedes the former demand to
hard-code 167 in this runner; that population is now a separately pinned G-4c.3
subset.

## Remaining blocker: emitted chain order is not reconciled

`reconcile()` sorts every plant's rows before testing its sequence. Consequently it
does not prove that stderr preserved execution order. A synthetic chain emitted as
sequence `[2, 1, 3]` is sorted to `[1, 2, 3]` and accepted. This contradicts the
runner's own contract (“complete, ordered plant chains”) and its module description,
which says the negative controls include a reordered chain. The implemented third
control corrupts syntax instead; no reordered-chain control is run.

The same reconciliation accepts plant index 99 when the entry record declares one
plant. Counting distinct nonnegative keys establishes cardinality but not stable
identity. A complete reconciliation of an enumerated `plants=N` call must require the
exact plant-key set `0..N-1`.

Independent probes at the pinned artifact produced:

```text
REORDER_ACCEPTED
BAD_INDEX_ACCEPTED
```

Required repair: validate rows in received order before any sorting; add an actual
reordered-row negative control; and require each gate-passing call's plant identities
to equal `range(N)`. Keep the existing dropped, duplicated-terminal, and malformed-row
controls.

## Gate disposition

- G-4c.1: **REVISION_REQUIRED** until ordered and identity-complete reconciliation
  fails closed.
- G-4c.2: parity and the implemented negative controls reproduce; Amendment 1's five
  silent-terminal controls remain pending and are not adjudicated by this revision.
- G-4c.3: not authorized. The owner-pinned 167-manifest derivation is acknowledged as
  future work, not a result of this review.

No fix, judgment, distribution finding, resident mutation, or Arena action is
authorized.
