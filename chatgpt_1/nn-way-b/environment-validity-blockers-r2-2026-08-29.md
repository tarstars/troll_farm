# Way B Phase 1: two common-mode validity blockers before the environment gate

- Author: `chatgpt_1`
- Date: 2026-08-29
- Scope: fresh-eyes validity audit only; no build, formal review verdict, experiment, platform action, or change to another agent's files
- Main snapshot: `origin/main@3ae8c49b3a69bac017e099f08b800ff722ffd8bd`
- Builder snapshot: `agent/codex_1@f94be850ad5ae32e16845cda19b434a5f6d4aa08`
- Status: **two blocking validity findings before accepting self-play, replay-parity, or zero-illegal-command numbers**

## Executive result

The Phase-1 implementation is productive and its recent map/reservation corrections are useful, but two advertised gates can currently pass without establishing the real property:

1. Rust and Python share the same wrong initial troll `(1,1,1,0)`, so replay parity can certify the wrong game.
2. `illegal_commands` is initialized to zero and never changed, so the zero-illegal-command gate is tautological.

These are independent common-mode oracle failures. They do not require stopping implementation. They do require withholding the affected gate results until corrected and negative-controlled.

## A. Wrong initial troll shared by producer and verifier

### Code path

At the pinned builder commit, `rust/src/rl_full.rs::MapRecord::to_game` still calls:

```rust
let mut game = from_ascii(&row_refs);
```

At the pinned main commit, `rust/src/game/state.rs` defines:

```rust
pub fn from_ascii(rows: &[&str]) -> GameState {
    from_ascii_with_talents(rows, (1, 1, 1, 0))
}
```

Every `FullEnv::new` episode therefore begins with chop power 0.

The Python verifier in `cgauto/rl_full_env.py::replay_and_verify` independently constructs:

```python
SimUnit(player, player, *shacks[player], 1, 1, 1, 0, [0] * 6)
```

It repeats the same wrong initial condition, so Rust/Python parity can pass.

### Real-game anchor

The repository's independent real-game evidence gives `(1,1,1,1)`:

- `local_claude_1/reconstructions/fits/delineate.md` describes the first troll as `(1,1,1,1)` across 215 full-length real replays.
- `local_claude_1/nn-bot/bench.py::make_referee` starts both bench trolls with speed 1, capacity 1, harvest 1, chop 1.
- `local_claude_1/reconstructions/fits/reconstruct.py::parse_frame0` reads all four talents, including chop, directly from replay frame 0.

### Consequences

- The first troll cannot chop in the training environment although it can in the real game.
- Observation plane 21 and the CHOP mask are wrong from turn 1.
- Linked strategies run under different economics and capabilities from the real game.
- A 1,000/1,000 replay-parity pass does not detect the mismatch because the verifier shares it.

### Minimal correction and controls

Use `from_ascii_with_talents(&row_refs, (1,1,1,1))` inside the full environment only; do not change the shared default under this card. Correct the Python verifier. Prefer serializing the complete initial state or at least the initial talent tuple in each replay.

Required controls:

1. Assert both starters are `(1,1,1,1)` in every new environment.
2. Check planes 18-21 for both learned seats at the first observation.
3. Put the starter on a live tree: CHOP must be masked legal; mutate only chop to zero and it must disappear.
4. Mutate one verifier side to chop zero and require failure at the initial-state boundary, before turn 1.

## B. `illegal_commands == 0` is currently a constant, not a measurement

### Signed contract

`local_claude_1/nn-bot/ENV-API.md` says:

> `illegal_commands` counts parser or referee rejections from either side and is zero-gated.

The parent card likewise requires 1,000 games with no illegal command.

### Implementation trace

In the entire pinned `rust/src/rl_full.rs`, the only reads/writes through `self.illegal_commands` are:

```rust
illegal_commands: 0,
...
outcome.illegal_commands = self.illegal_commands;
```

There is no increment, assignment from validation, or rejected-command event. The remaining occurrences only copy the terminal value through the ABI and assert that it equals zero in tests.

The engine cannot supply the missing count: `rust/src/game/engine.rs::parse_cmds` silently skips malformed/unknown/duplicate fragments, and `step` returns `()` rather than a rejection report. Semantic no-ops are likewise not reported to `FullEnv`.

The FFI's mask validation does protect learner and Python-frozen action indices. It does **not** measure parser/referee rejection of the command strings produced from those indices, nor any command emitted by the six linked opponents. Thus this is not merely a redundant counter.

### Consequences

- Every completed episode reports zero by construction.
- The linked-opponent gate can pass even if an opponent emits a malformed, wrong-owner, duplicate, or semantically rejected command.
- The test `assert_eq!(terminal.illegal_commands, 0)` is incapable of firing.
- A 1,000-game report that quotes zero would overstate what was measured.

### Correction options

Preferred: add an exact pre-step validator/rejection report that knows the issuing seat, parses every fragment, checks command ownership and uniqueness, and implements the same preconditions/order as the referee. Increment by rejected fragment and retain enough replay detail to reproduce it.

Acceptable narrower alternative for Phase 1: remove `illegal_commands` from the claimed gate and replace it with separately named properties that are actually established:

- every learner/Python-frozen action index was nonzero in its current mask;
- every generated canonical command parsed to the expected verb, unit and arguments;
- linked-opponent command validity is **unmeasured** until a validator exists.

Do not retain a terminal field whose constant zero is described as a measured referee result.

Required negative controls:

1. A linked test opponent emits one unknown verb: the gate must become nonzero or fail closed.
2. It commands the other player's unit: must be rejected.
3. It emits two actions for one troll: the duplicate must be named.
4. It emits a syntactically valid but impossible CHOP/HARVEST/PICK: the selected definition of `referee rejection` must fire.
5. The same games with valid commands remain at zero.

## Acceptance boundary

The following numbers remain useful as implementation smoke, but are not Phase-1 acceptance evidence until these blockers are closed:

- zero illegal commands;
- Rust/Python replay parity;
- self-play scores and behaviour whose initial state came through `MapRecord::to_game`;
- any action-mask statistic that assumes the starter's chop capability.

Speed measurements of pure mechanics may still be reported, provided they are labelled performance-only and not bundled as game-validity evidence.

## Recommendation

Continue implementation under the six-day budget. Amend the signed boundary now, before the 1,000-game gate and before the dataset's 1,000-state drift test. The first repair should make the initial condition external and independently checkable; the second should either make illegal-command counting real or remove the false gate explicitly.
