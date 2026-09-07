# Exact activated-prefix trace — 9947505 seat 1, adaptive resident (index 0)

Instrumented copy of the candidate module only (`make_trace.py` ->
`macroplan_trace_module.rs`); no terrain, stock, opponent or passive
substitution.  Baseline arm is the unchanged parent control module.
Sources at trace time: core `0dce250c`, `_a_module.rs` `99eb96ff`.
Raw log `trace.log` (turns 50..85), `trace.tsv`.

Own seat 1 = view player 0.  Shack 12,2.  Own units: `1` (ms1/cc1/hp1/chop1)
and `3` (ms3/cc2/hp0/chop2).  Enemy units `0` and `2`.

## Activation and the two LEMON trees

* t60 `MACRO activate spec=(2,1,1,1) bill=[P6,L3,A3,-,I3,-] bank=[0,0,8,4,1,1]`,
  eta 36 (< deadline 45).  Two LEMON trees stand: `LEMON@6,4 s4 h8 f3 cd0` and
  `LEMON@13,5 s4 h8 f3 cd0`.  `choose_spec` measured the nearest fruited LEMON
  at nav distance 3 from our door, so LEMON is 24 of the 36 planned turns.
* `LEMON@6,4`: enemy unit `2` (3/2/0/2) sits on it from t60; health 8 -> 6 (t63)
  -> 4 (t64) -> 2 (t65) -> gone at t66.  **Destroyed by the enemy.**
* `LEMON@13,5`: our unit `3` arrives t66 and the issued command list is
  `["CHOP 3", "HARVEST 1"]` at t66, `["CHOP 3", "DROP 1"]` at t67,
  `["CHOP 3", "HARVEST 1"]` at t68.  Health 8 -> 6 (t67) -> 3 (t68) -> gone at
  t69.  **Destroyed by our own worker, under the parent's own `CHOP 3` which the
  controller passed through unchanged.**  Unit `3` has `hp = 0`, so it was never
  a possible LEMON acquirer; it was simply not re-tasked.
* Meanwhile unit `1` spent t61..t76 shuttling one PLUM at a time from the tree
  adjacent to our own door (cc = 1, 2 turns per unit): PLUM 0 -> 6 by t76, plus
  IRON 1 -> 3.  Nearest-source selection took the abundant item at distance 0 and
  deferred the scarce, contested one.
* t76 `MACRO cancel bank=[6,0,8,4,3,3]`: every item except LEMON is funded, no
  LEMON tree is alive anywhere on the board, deadline t105 unreachable.

So the failure was **self-inflicted and ordering-driven**, not a census of
simultaneously ripe fruit: the bill was 3/4 funded and the missing kind was
felled by our own unoverridden worker while the acquirer was collecting the item
that was never at risk.

## The observed `move_blocked`

t72 parent base `["MOVE 1 11 1", "MOVE 3 12 1"]`.  The controller overrode unit
`1` with `HARVEST 1`, pinning it on 12,1 — the exact cell the parent had routed
unit `3` into on the assumption that unit `1` would vacate it.  t73 shows unit
`3` still at 11,1.  That is the single `move_blocked` in the run: an ownership /
endpoint conflict created by re-tasking, between two of our own units.
