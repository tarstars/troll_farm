# G-1 review — real-game dance attribution definitions

- Task: `20260824-real-game-dance-attribution`
- Reviewer: codex_1
- Reviewed artifact: `agent/claude_1` @
  `3c87ab0b69e07d602a14f536f6b8e8153b8c91a6`,
  `claude_1/dance1/definitions-g1-2026-08-24.md`
- Verdict: **REVISION_REQUIRED**

The definitions are published before counting, the F5 same-transition exchange predicate cannot
be triggered by two units traversing the same cells on different turns, and the first-match
precedence is mechanically disjoint and exhaustive. `NO_TARGET` is appropriately denied when v3
shows a real `available` target, and raw facts remain recoverable under precedence.

Two contract mismatches block acceptance.

## R1 — F3's population is broader than the mandatory imported implementation

F3 promises a record for **every other own unit alive in the window**. The required imported
`measure_blocker` does not do that: at `build_oscillation_library.py:198` it iterates only
`tr.state(turn_start).own_units()`. A peer born after entry, or otherwise absent at entry but alive
later in the window, is omitted. The proposed prose simultaneously calls this “every other own
unit alive in the window” and “exactly the fields `measure_blocker` already emits”; those are not
the same fact domain.

Required repair: choose and publish one meaning before grading. Either narrow F3 explicitly to
peers alive at `turn_start` and carry a separate observable count/list of later-appearing peers,
or broaden the measurement without claiming verbatim import. In either case, state how a
later-appearing stationary adjacent peer affects blocker classification. Do not silently change
the accepted library function.

## R2 — K2 cannot reproduce the frozen classifier under the proposed mapping

The frozen classifier has four possible outputs, not just M1/M2/M3. It returns `M3` only when
`peers` is empty; when peers exist but none qualifies as a blocker, it returns `UNCLASSIFIED`.
The proposed classifier instead lets any no-blocker episode enter `GOAL_FLIP`,
`FIXED_TARGET_NO_BLOCKER`, or `NO_TARGET`, including peer-present/no-blocker episodes. Therefore
the statement that K2 reproduces the frozen library's M1/M2/M3 labels over all 38 episodes is not
a fully specified exact comparison, and “M3 maps to no blocker” broadens M3 beyond the frozen
predicate.

Required repair: publish an exact K2 crosswalk for **every frozen output**, including legacy
`UNCLASSIFIED`, and define the pass comparison at the F3 mechanism layer. At minimum it must
distinguish `no peers` (legacy M3) from `peers present, no blocker` (legacy UNCLASSIFIED), list
every disagreement, and forbid telemetry from retroactively turning a K2 mechanism mismatch into
a pass. The final real-game class may still use telemetry, but K2's claimed reproduction must be
separate and exact.

## Non-blocking requirements to retain

- Clamp F5's two-turn lookback at the trace boundary and record the effective inspected range.
- Treat telemetry decode refusal as an episode-level `UNCLASSIFIED` fact row for K5 accounting;
  “refused whole” must not mean silently removing D-1 episodes from the detector total.
- K3's negative side remains a joint test of detector and historical-bot premise. Any non-zero
  result prevents the causal name `SWAP_FLAP`, as the proposal already says.
- Report the precedence-sensitive cross-tab (swap × blocker) so `SWAP_FLAP` does not erase the
  co-occurring blocker mechanism from the owner brief.

No batch was graded and no count was inspected in this review.

DEFERRED: G-2 fresh-archive execution review remains triggered only by a valid post-G-1 handoff
naming a canonical full commit and artifact paths.
