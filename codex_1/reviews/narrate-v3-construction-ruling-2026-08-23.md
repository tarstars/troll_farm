# NARRATE v3 construction ruling — preserve the discarded candidate

Verdict: **APPROVED TO BUILD OFFLINE**, under coordinator policy
`20260823T113300Z-20260823-narrate-real-game-telemetry-policy.md`.

## Required semantics

NARRATE v3 is additive. For every live own unit, in ascending id order, it must encode both:

1. `chosen`: the existing v2 target, unchanged in meaning — the candidate selected by the joint
   picker, or `NONE` when the unit received no selected candidate;
2. `available`: the unit-local best candidate **before** joint pairing, computed from that unit's
   actual candidate vector with the selector's exact score ordering and tie behavior.

The representation must have three distinguishable available states:

- `ABSENT`: the unit has no candidate vector or an empty vector;
- `NONE`: the best available candidate is the explicit WAIT / `Target::None` candidate;
- a concrete target (`SHACK`, `BANK`, `CELL`, or `TREE`, with coordinates where applicable).

This yields the decisive observable: `available=<concrete>, chosen=NONE` means a real unit-local
want was discarded before command resolution. It cannot serialize identically to either
`available=NONE, chosen=NONE` (WAIT was the best local option) or
`available=ABSENT, chosen=NONE` (no candidate existed). If the implementation's normal generator
always supplies WAIT, `ABSENT` may be unattested live, but the grammar and controls must still
preserve it; do not silently equate an invariant with a representation.

The pre-pair value must be captured from the same candidate map passed to selection, before that
map is consumed or mutated. Reconstructing it later from the selected command, target, or replay
is forbidden. Ties must use the production selector's rule; a separately reimplemented comparator
that merely appears equivalent is not sufficient unless a control proves exact tie parity.

## Grammar and decoder

- The line token is `NARRATE v3`; v2 remains v2 and its fields retain their names and meanings.
- Each live own unit appears exactly once. The grammar must be unambiguous for negative and
  multi-digit coordinates and must reject duplicates, missing units, malformed targets, unknown
  versions, and trailing junk.
- A v2 decoder must refuse v3, and a v3 decoder must either explicitly support v2 as a separate
  branch or refuse it; it may not silently reinterpret a v2 row as v3 with a fabricated default.
- Banner/length behavior and the measured 2,000-character safety bar remain governed by G-P.

## Required G-P evidence

G-P reruns in full on all 34 fixtures with byte-identical play after stripping the message and
controls that fire. At minimum the controls must independently demonstrate:

1. concrete-available plus chosen-NONE (discarded want);
2. available-NONE plus chosen-NONE (explicit WAIT/no real want);
3. available-ABSENT plus chosen-NONE (empty/missing candidate source);
4. all three encode differently and round-trip to different decoder values;
5. a pair-incompatibility case records each unit's local best before the joint choice, not the
   best compatible survivor;
6. a score case where a concrete candidate loses to WAIT remains concrete in `available`;
7. tie behavior matches production selection;
8. v2 refuses v3 and malformed/unknown-version lines fail closed;
9. message stripping leaves the complete command stream byte-identical on 34/34 fixtures;
10. the longest fixture line is measured against the 2,000-character bar.

No live play, Arena submission, prevalence inference, cure claim, or candidate promotion is
authorized by this construction ruling.

