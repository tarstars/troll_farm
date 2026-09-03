# Way B validity blocker: the environment and its replay verifier share the wrong starting troll

- Author: `chatgpt_1`
- Date: 2026-08-29
- Scope: fresh-eyes validity finding only; no build, formal review verdict, experiment, platform action, or change to another agent's files
- Main snapshot read: `origin/main@3ae8c49b3a69bac017e099f08b800ff722ffd8bd`
- Builder snapshot read: `agent/codex_1@d0aca8baa1378ed69f99e85e8a51b5805c13bfac`
- Finding: **BLOCKING before any self-play or replay-parity number is accepted**

## Finding

The full-game Rust environment starts both initial trolls with talents `(movement=1, carry=1, harvest=1, chop=0)`. The real game starts the first troll as `(1,1,1,1)`.

This would already make the training environment a different game. More importantly, the current Python replay verifier independently hard-codes the same wrong `chop=0`, so the advertised Rust-versus-Python replay-parity gate can pass while both sides agree on the same invalid initial state.

## Exact code path

`agent/codex_1@d0aca8baa1378ed69f99e85e8a51b5805c13bfac:rust/src/rl_full.rs`:

1. `MapRecord::to_game` calls `from_ascii(&row_refs)` without an explicit talent tuple.
2. `FullEnv::new` obtains its initial `state` through that `to_game` call.

`origin/main@3ae8c49b3a69bac017e099f08b800ff722ffd8bd:rust/src/game/state.rs`:

```rust
pub fn from_ascii(rows: &[&str]) -> GameState {
    from_ascii_with_talents(rows, (1, 1, 1, 0))
}
```

Therefore every full-environment episode begins with chop power 0.

`agent/codex_1@d0aca8baa1378ed69f99e85e8a51b5805c13bfac:cgauto/rl_full_env.py`, `replay_and_verify`:

```python
units = [
    SimUnit(player, player, *shacks[player], 1, 1, 1, 0, [0] * 6)
    for player in (0, 1)
]
```

The supposedly independent verifier therefore reconstructs the same chop-0 start.

## The real-game record

Two independent repository paths identify chop power 1:

- `origin/main@3ae8c49b3a69bac017e099f08b800ff722ffd8bd:local_claude_1/reconstructions/fits/delineate.md` describes the first troll as `(1,1,1,1)` from 215 full-length real replays.
- `origin/main@3ae8c49b3a69bac017e099f08b800ff722ffd8bd:local_claude_1/nn-bot/bench.py`, `make_referee`, constructs both real-bench starters with speed 1, capacity 1, harvest 1, and chop 1.

The reconstruction code also reads all four talents, including `chop`, directly from replay frame 0 rather than inferring them (`local_claude_1/reconstructions/fits/reconstruct.py::parse_frame0`).

## Consequences

1. The learned policy cannot chop with its first troll until it trains another unit, although real players can.
2. Linked opponent strategies are evaluated from a starting state unlike the state for which their real-game behaviour was designed.
3. Observation plane 21 and the CHOP action mask are wrong from turn 1.
4. Training-plan economics and the timing/value of a second troll change because the first troll cannot collect wood by chopping.
5. A 1,000/1,000 replay-parity result would not catch the defect: the Rust producer and Python verifier currently share it.

This is a classic common-mode oracle failure. Replay parity proves an implementation against the verifier only after the verifier's initial condition is independently anchored to the real game.

## Minimal repair

Do not change the shared `from_ascii` default under this card; other curriculum code may rely on it. In `MapRecord::to_game`, construct the full-game state explicitly with:

```rust
from_ascii_with_talents(&row_refs, (1, 1, 1, 1))
```

Change `replay_and_verify` to construct `(1,1,1,1)` starters as well.

Preferably add the starting talent tuple to the replay record, or record the complete initial state, so the parity verifier consumes evidence emitted by the environment rather than silently repeating a second hard-coded constant.

## Required negative controls

Before accepting an environment run:

1. Assert that both initial units in every newly created `FullEnv` have `(ms,cc,hp,chop) == (1,1,1,1)`.
2. Assert on both learned seats that observation planes 18-21 encode `1,1,1,1` at the starting troll.
3. Construct a legal state with the starting troll on a live tree and confirm CHOP is in the action mask; mutate only `chop` to 0 and confirm it disappears.
4. Mutate the Python verifier's initial chop to 0 while replaying a chop-1 Rust record and require parity to fail at the initial-state boundary, before turn 1. This requires the replay record to expose enough initial-state identity.
5. Keep the existing turn-by-turn parity test after these controls.

## Recommendation

Treat this as a validity amendment to Phase 1, not as a later model-quality issue. The current environment may continue to be developed, but no self-play count, speed result, or replay-parity count should be accepted until the initial state and the independent verifier are corrected and the common-mode negative control fires.
