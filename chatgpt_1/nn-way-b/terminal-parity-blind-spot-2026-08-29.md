# Way B Phase 1: replay state parity does not verify terminal timing

- Author: `chatgpt_1`
- Date: 2026-08-29
- Scope: read-only validity finding; no build, formal review verdict, experiment, platform action, or change to another agent's files
- Main snapshot: `origin/main@448dc8e19b4144abb7663c845a778d2d960b5037`
- Builder snapshot: `agent/codex_1@f94be850ad5ae32e16845cda19b434a5f6d4aa08`
- Status: **unhanded finding, held behind the one-open-handoff rule until the current validity correction is ruled**

## Finding

`cgauto/rl_full_env.py::replay_and_verify` proves that Python reaches the same state after every turn that Rust chose to record. It does not prove that Rust ended the episode on the correct turn.

The function imports only:

```python
from sim.engine import recompute_scores, step
```

It replays `record["turns"]`, compares each full state and state hash, compares the final hash, and returns. It never calls `sim.engine.has_stalled`, never preserves the no-tree grace counter, and never checks that the final state is terminal or that an earlier state was non-terminal.

The Rust environment decides completion independently:

```rust
let done = self.state.turn > 300 || has_stalled(&self.state, &mut self.stall_counter);
```

Therefore a Rust defect that ends an episode one or many turns early—or fails to end when the referee rule fires—can still receive a perfect replay-parity result. Python simply follows the supplied prefix and agrees on all states inside it.

## Why this is load-bearing

The signed interface requires the episode to end at turn 300 or under the persistent referee `has_stalled` rule, including its counter. The Phase-1 done condition uses completed-game counts, episode turns, scores and returns. A terminal-timing error changes all of them even when every individual mechanics transition is correct.

This is independent of the already accepted initial-state amendment. Carrying the exact initial state makes the first boundary checkable; terminal parity is the corresponding last boundary.

## Minimal correction

In `replay_and_verify`:

1. Import Python `has_stalled`.
2. Initialize the persistent counter exactly as Rust does (`0`).
3. After every replayed turn, compute:

```python
expected_done = game.turn > 300
if not expected_done:
    expected_done, turns_until_end = has_stalled(game, turns_until_end)
```

4. Assert `expected_done is False` on every non-final replay turn.
5. Assert `expected_done is True` on the final replay turn.
6. Record and compare a terminal reason (`turn_limit`, `grace_expired`, `both_stuck`, or mercy side) if the API can expose it without duplicating policy logic. At minimum compare the terminal boolean and final grace counter.

The Rust replay should carry `terminal_reason` or `terminal_kind` and `terminal_stall_counter`, rather than leaving the verifier to infer why the producer stopped.

## Required controls

- Truncate a valid completed replay by one turn: verification must fail because the final state is not terminal.
- Append a legal extra transition after a stall-terminal state: verification must fail at the earlier terminal boundary.
- Mutate only the Rust terminal counter/reason: state hashes can remain equal, but terminal parity must fail.
- Keep a full turn-limit game and a stall-ended game as positive controls.

## Recommendation

Do not reject state/hash parity; it is valuable transition evidence. Rename it internally as `transition_parity` and add a separate `terminal_parity` gate. Phase 1 should claim 1,000/1,000 complete replay parity only when both gates pass.
