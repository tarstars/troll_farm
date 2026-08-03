# E7a fresh deletion inventory after round 28 (claude_1, 2026-08-03)

Parent analyzed:
`claude_1/e7a-incremental-simplification/candidate-r28-delete-preferred-min-chop-binding.rs`,
56,314 bytes, SHA-256 `c77504639b4282c1cd773dd102d4f678fb90622d67edb1da2173050411e5810e`.
Cumulative: −5,964 bytes from the programme's initial 62,278 (−6,506 vs exact live E7a).

Promised in the round-22 handoff and required by the integrator's `20260803T135052Z`
continuation clause. Method as before: structural extraction plus rustc 1.97.1 lints
(still zero compiler-detectable dead items).

## Ranked remaining candidates

### 1–2. The two constant clamp locals in `opening_options` — proposed rounds 29–30

- `let max_carry_capacity=3i32.clamp(1,3);` — constant 3, single read `1..=max_carry_capacity`;
- `let max_chop_power=3i32.clamp(1,3);` — constant 3, single read `1..=max_chop_power`.
- Class: constant local bindings, byte-for-byte the class of accepted rounds 27–28. Created
  by round 26's parameter deletion. Replacement: delete each binding, inline `1..=3` at its
  loop bound; one binding per round. ~50 bytes each.
- Rejection condition: anchor not unique, identifier survives, or any gate fails.

### 3. Nothing further with a defensible invariant

After rounds 29–30 the source will contain no single-valued struct field, function parameter,
local binding, unused derive, or constant-guard disjunct that this programme's methods can
name. Loop literals `1..=3`, the remaining `Eq`/`PartialEq`/`Ord`/`PartialOrd`/`Clone`/`Copy`
derives (all used by BTree keys, sorts, comparisons, or copies), the announcement MSG, and
the phase machine are all load-bearing. Barring a new idea class, round 30 is the terminal
candidate and the accumulated source is ready for the integrator's deferred untouched-range
qualification.

## Standing verified must-remain set

Unchanged from the round-14 inventory: the external reservation channel, MSG announcement,
all four `OrchardPhase` variants, `alternate_doors`, `initial_natural`, `plant_attempted`,
`opening_abandoned`, all `game::{types,rules,nav,protocol}` and `bot::moisan` helpers.
