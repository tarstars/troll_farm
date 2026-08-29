# Full-game vector environment API

Status: signed interface, 2026-08-29. This document freezes the
boundary between `rust/src/rl_full.rs`, `cgauto/rl_full_env.py`, the dataset builder, and a frozen
Python opponent. Implementation starts only after signature.

## Constants and memory rules

| name | value |
|---|---:|
| `TF_FULL_OBS_CHANNELS` | 104 |
| `TF_FULL_HEIGHT` | 11 |
| `TF_FULL_WIDTH` | 22 |
| `TF_FULL_OBS_SIZE` | 25,168 |
| `TF_FULL_ACTION_PLANES` | 13 |
| `TF_FULL_ACTION_SIZE` | 3,146 |
| `TF_FULL_PLAN_SIZE` | 144 |
| `TF_FULL_MAX_RECORDED_TRAINS` | 4 |

All numeric buffers are native-endian, C-contiguous arrays owned by the caller. Rust borrows them
only for the call. The opaque handle owns games, maps, opponents, staged commands, and replay logs;
one handle is not safe for concurrent calls. `usize` is the platform C `size_t`. Strings passed at
creation are NUL-terminated UTF-8; JSON state calls use an explicit byte length and do not require a
terminator.

Return status is `0` on success: `-1` null pointer, `-2` invalid scalar/buffer contract,
`-3` file or JSON error, `-4` action outside the current mask, and `-5` wrong mini-step phase.
Action validation is batch-atomic: on `-4` or `-5`, no slot advances.

## Episode construction

`maps_path` is a nonempty JSONL file of real-map records in
`local_claude_1/nn-bot/maps-slice-1000.jsonl` format. Required fields are `w`, `h`, `rows`,
`shacks`, and `trees0`; the rows are authoritative for terrain and shacks, and `trees0` is the
exact initial tree state. Missing or malformed input is an error. There is no generated-map
fallback.

Each slot has an incrementing `episode_seed`, starting at `seed_base + slot`. A deterministic
SHA1PRNG seeded by that value selects a map uniformly, a learned seat uniformly, an opponent by
the supplied weights, and five inclusive-uniform starting stocks in `2..10` for PLUM, LEMON,
APPLE, BANANA and IRON; the same stock is assigned to both players and WOOD starts at zero. Reset
increments the batch's next seed. A terminal record's seed therefore reconstructs the episode.

The episode ends after turn 300 or the referee's persistent no-tree grace/stuck/mercy rule in
`game::engine::has_stalled`, whichever comes first. The fast-state port must reproduce that rule,
including its counter across turns; a forced 300-turn approximation is forbidden.

## Opponent pool

`opponent_weights` points to seven non-negative finite `f32` values in this fixed order:

| id | label | implementation |
|---:|---|---|
| 0 | `secure_orchard` | `resident_policy::bot::moisan::SecureOrchardBot` |
| 1 | `norxondor_native` | `NorxondorNative::new(true)` |
| 2 | `legend_field_proxy_v2` | producer `(2,2,1,1)`, chopper `(2,2,0,2)`, `late_chop=true` |
| 3 | `gold_elite_adaptive` | `GoldElite::adaptive()` |
| 4 | `script_boss` | `ScriptBoss::new()` |
| 5 | `mybot_boss4` | `MyBot::new()` |
| 6 | `python_frozen` | commands supplied through the external-opponent API below |

At least one weight must be positive. An episode samples once and keeps that opponent.

Identity correction required by the charter: `rust/src/strategies/mybot.rs` explicitly describes
`MyBot` as a model of the Arena's **Boss 4**, not a mirror of any project champion. In particular it
does not mirror the current denial-off champion, submission `41202036`, SHA-256 `0e92f8fa...`.
`SecureOrchardBot` is the resident lineage with the sacred source's denial rule, so it is not that
denial-off champion either. The actual champion and orchard 6 remain truth-bench binaries unless a
separate exact linked strategy is added and identified by hash.

## Mini-step state machine

Main-side `phase[n]` values are:

- `0 PLAN`: choose one of 144 train plans;
- `1 TROLL`: choose one of 3,146 spatial actions for `active_troll[n]`;
- `2 EXTERNAL_WAIT`: the learned side is complete and a `python_frozen` opponent still needs
  decisions; both main masks are zero and main action must be `-1`.

Every turn begins with PLAN. The environment then visits the learned player's trolls in ascending
id order using the roster at the start of the turn. After the last troll:

- a linked opponent supplies its complete command set and the full referee turn executes; or
- a Python opponent enters its own PLAN and ascending-id TROLL sequence. Its final mini-step
  executes both stored command sets.

The observation and mask returned after a plan action already contain that plan. Earlier own troll
decisions are staged as specified in `OBS-PLANES.md`; the game state itself is unchanged until both
players' turn commands are complete. There is no beam search.

Plan index is
`(((movement-1) * 4 + (carry-1)) * 3 + harvest) * 4 + chop`. Entry 0 is train nothing.
Entry 0 is always legal. A nonzero entry is legal when harvest and chop are not both zero and
`harvest <= carry`; current affordability does not affect the plan mask. If global unit capacity
prevents any further TRAIN, only entry 0 is legal.

The selected plan is the turn's target. At execution, Rust performs an exact dry run of the staged
commands and emits `TRAIN movement carry harvest chop` only when that command succeeds under the
post-MOVE/post-PICK bank and shack occupancy. This prevents unaffordable TRAIN spam while preserving
same-turn MOVE/PICK effects. A failed or zero plan emits no TRAIN. A successful exact target sets the
one-turn observation latch described for plane 98.

## Spatial action index, mask, and command text

Flattening is `plane * 242 + y * 22 + x`.

| plane | command |
|---:|---|
| 0 | `MOVE id x y`; selecting the troll's current cell is canonical WAIT |
| 1 | `HARVEST id` |
| 2 | `CHOP id` |
| 3 | `DROP id` |
| 4 | `MINE id` |
| 5-8 | `PLANT id PLUM/LEMON/APPLE/BANANA` |
| 9-12 | `PICK id PLUM/LEMON/APPLE/BANANA` |

For planes 1-12 only the active troll's current spatial index may be nonzero. MOVE is legal for its
current cell and every in-bounds grass cell reachable by BFS from the troll, including a starter
whose source is its non-walkable shack. Other verbs use the referee preconditions:

- HARVEST: a living tree with fruit, positive harvest power, and free capacity;
- CHOP: a living tree and positive chop power; full capacity does not make CHOP illegal;
- DROP: positive cargo at Manhattan distance at most one from own shack;
- MINE: positive chop power, free capacity, and current cell adjacent to iron;
- PLANT: current cell is empty grass and the troll carries that fruit seed;
- PICK: free capacity, current cell adjacent to own shack, and that fruit is in the bank.

An action whose staged end cell duplicates an earlier own troll reservation is masked as described
in `OBS-PLANES.md`. MOVE/current is the nonempty fallback. Selecting any zero mask entry is a hard
environment error, not a silently skipped referee command.

Command helpers use uppercase canonical text without a trailing semicolon:

```c
int32_t tf_full_decode_action(
    int32_t action_index, int32_t troll_id, int32_t width, int32_t height,
    uint8_t *output_utf8, size_t output_capacity);

int32_t tf_full_encode_command(
    const uint8_t *command_utf8, size_t command_length,
    int32_t expected_troll_id, int32_t width, int32_t height);

int32_t tf_full_decode_plan(int32_t plan_index, int8_t *talents_4);
```

Decode returns the byte length written (excluding NUL), writes a NUL terminator, and returns `-2`
for an invalid index/coordinate or `-6` for a short output buffer. Encode returns the flat action
index or a negative status. Plan 0 decodes to four zeros. These functions do not require a handle.

## C ABI

Size queries let the Python wrapper reject a mismatched library:

```c
size_t tf_full_obs_size(void);       // 25168
size_t tf_full_action_size(void);    // 3146
size_t tf_full_plan_size(void);      // 144

void *tf_full_create(
    size_t num_envs,
    uint64_t seed_base,
    const char *maps_path,
    const float *opponent_weights_7,
    float wood_shaping,
    float end_wood_value);

void tf_full_destroy(void *handle);
```

`wood_shaping` and `end_wood_value` are explicit constructor flags; Phase 3 defaults are 0.5 and
3.5, and zero/4.0 produces unshaped referee scoring. Both must be finite and non-negative. This is
the deliberate elaboration of the parent card's abbreviated four-argument create signature.

Observation writes all buffers and returns `num_envs`:

```c
int32_t tf_full_observe(
    void *handle,
    uint8_t *obs_n_25168,
    uint8_t *masks_n_3146,
    uint8_t *plan_masks_n_144,
    int32_t *phase_n,
    int32_t *seat_view_n,
    int32_t *active_troll_n);
```

`seat_view` is the absolute learned seat (0 or 1); the observation itself is already canonical and
player-relative. `active_troll` is the referee troll id in TROLL phase and `-1` otherwise. In PLAN,
the spatial mask is zero; in TROLL, the plan mask is zero.

Both step calls share the following output contract. The main call consumes actions for PLAN/TROLL
slots. The opponent call consumes only slots waiting for the external opponent; ignored slots must
contain `-1`.

```c
int32_t tf_full_step(
    void *handle, const int32_t *actions_n,
    uint8_t *obs_n_25168, uint8_t *masks_n_3146, uint8_t *plan_masks_n_144,
    int32_t *phase_n, int32_t *seat_view_n, int32_t *active_troll_n,
    float *rewards_n, uint8_t *turn_completed_n, uint8_t *reward_credit_count_n,
    uint8_t *dones_n, uint8_t *wins_n, uint16_t *episode_turns_n,
    float *episode_returns_n, uint64_t *episode_seeds_n, uint32_t *map_indices_n,
    uint8_t *opponent_ids_n, int32_t *score_own_n, int32_t *score_opp_n,
    int8_t *trained_specs_n_4_4, uint16_t *trained_turns_n_4,
    uint8_t *trained_count_n, uint8_t *trained_overflow_n,
    uint16_t *illegal_commands_n, uint64_t *action_hash_n, uint64_t *state_hash_n);

int32_t tf_full_opponent_step(/* the identical argument list */);
```

As in `tf_level1_step`, terminal fields are zero for unfinished slots, completed slots auto-reset,
and returned observations belong to the reset episode. `trained_specs[n,4,4]` and
`trained_turns[n,4]` contain the first four successful learned-side TRAINs; `trained_count` is the
total and `trained_overflow` is `max(total-4,0)`. `wins` compares the referee score, not shaped
reward. `illegal_commands` counts parser or referee rejections from either side and is zero-gated.
Hashes cover the complete ordered command stream and terminal state.

## Reward credit across mini-steps

Before a full turn executes, reward, `turn_completed`, and `reward_credit_count` are zero. On the
call that executes it:

- per-turn reward is `wood_shaping * learned wood deposited this turn`;
- on the terminal turn, add `(own fruit + end_wood_value * own wood) - (opponent fruit +
  end_wood_value * opponent wood)`;
- `turn_completed=1` and `reward_credit_count=1+number_of_learned_trolls_decided_this_turn`.

`FullVecEnv` buffers that turn's plan and troll transitions. When `turn_completed` arrives it emits
all buffered transitions with the identical returned scalar, satisfying the fixed design without
pretending that an early mini-step knows a future end-of-turn reward. `episode_returns` is the sum
of one reward per full turn, not the reward multiplied by mini-step count.

## Python-frozen opponent ABI

```c
int32_t tf_full_opponent_observe(
    void *handle,
    uint8_t *obs_n_25168, uint8_t *masks_n_3146, uint8_t *plan_masks_n_144,
    int32_t *phase_n, int32_t *seat_view_n, int32_t *active_troll_n,
    uint8_t *needs_action_n);
```

For a waiting `python_frozen` slot, the opponent observation is canonical relative to the opponent,
`seat_view` is its absolute seat, and `needs_action=1`. Other slots are all-zero with phase and
active troll `-1`. The caller runs the frozen checkpoint under `torch.no_grad()`, submits the masked
argmax through `tf_full_opponent_step`, and repeats until the turn executes. The frozen opponent is
inference-only; its transitions and rewards are not added to the learner rollout.

## Observation from reconstructed replay state

```c
int32_t tf_full_obs_from_state(
    const uint8_t *json_utf8, size_t json_length,
    int32_t seat, int32_t active_troll_id, int32_t phase,
    int32_t plan_index, uint8_t prior_target_trained,
    uint8_t *obs_25168, uint8_t *mask_3146_or_null,
    uint8_t *plan_mask_144_or_null);
```

The JSON object is a strict superset of `Reconstructor.snapshot()`:

```json
{
  "w": 20,
  "h": 10,
  "rows": ["..."],
  "turn": 17,
  "inv": [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]],
  "units": [{"id": 0, "player": 0, "x": 1, "y": 2, "ms": 1,
             "cc": 1, "hp": 1, "chop": 1, "carry": [0, 0, 0, 0, 0, 0]}],
  "plants": [{"type": "PLUM", "x": 2, "y": 2, "size": 4,
              "health": 12, "fruits": 3, "cooldown": 8}],
  "staged_actions": [{"troll_id": 0, "action_index": 244}]
}
```

`w`, `h`, and `rows` come from `Reconstructor.map`; the remaining required fields are the snapshot
unchanged. `staged_actions` is optional and contains only earlier same-seat trolls in ascending id
order. It is necessary to reproduce later troll mini-steps and their reservation masks. PLAN uses
`active_troll_id=-1`, `plan_index=0`, and no staged actions. A mask pointer may be null when only
planes are requested. This single function is the Rust side of the 1,000-state dataset drift test.

## Replay extraction for parity tests

Every environment slot records its map, initial bank, absolute seats, and both players' canonical
command strings before stepping. A completed replay remains attached to the reset slot until read:

```c
int64_t tf_full_take_replay(
    void *handle, size_t slot, uint8_t *output_json_or_null, size_t output_capacity);
```

With a null output, return required bytes without consuming. With enough capacity, write that many
UTF-8 JSON bytes and consume the stored replay. Return `-2` for a bad slot, `-6` for a short buffer,
and `0` when no completed replay is waiting. `tests/` replays these commands through
`sim/engine.py` and compares every turn's canonical state plus the terminal hash.

## `FullVecEnv` Python surface

`cgauto/rl_full_env.py` exports `FullVecEnv`, a context manager mirroring `Level1VecEnv`:

```python
FullVecEnv(
    num_envs: int,
    seed_base: int,
    maps_path: Path,
    opponent_weights: dict[str, float],
    *,
    wood_shaping: float = 0.5,
    end_wood: float = 3.5,
    frozen_opponent: Callable | None = None,
    library: Path = DEFAULT_LIBRARY,
)
```

Public arrays have shapes `obs[n,104,11,22]`, `masks[n,13,11,22]`,
`plan_masks[n,144]`, `phase[n]`, `seat_view[n]`, and `active_troll[n]` with the dtypes above.
`step(actions)` validates shape `(n,)`, drives any Python-frozen opponent until all affected turns
execute, and returns buffered mini-step transitions plus copied terminal metadata. `close()` is
idempotent. The wrapper verifies all three Rust size queries before allocation.

## Implementation prerequisites surfaced by the interface read

1. `rust/Cargo.toml` is an integrator-owned hotspot. Robust parsing of the real-map JSONL and the
   reconstructed-state JSON needs `serde`/`serde_json`; Phase 1 therefore needs the coordinator's
   explicit signature to include those two dependency edits (and `Cargo.lock`). A handwritten JSON
   parser is not an acceptable silent substitute.
2. None of the linked strategies is byte-identical to the current denial-off champion. This API
   records that fact rather than misnaming `MyBot`; adding an exact linked champion is a separate
   reviewed change, while the fixed binary bench remains authoritative.
