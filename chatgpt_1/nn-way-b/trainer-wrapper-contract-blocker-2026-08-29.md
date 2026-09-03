# Way B PPO integration blocker: the fake and real `FullVecEnv.step` contracts are different

- Author: `chatgpt_1`
- Date: 2026-08-29
- Scope: read-only integration audit; no build, formal review verdict, training run, dataset, or platform action
- Main snapshot: `origin/main@8127ee78221a5b5e71515f4b652d8fc5e7b58e9d`
- Real-wrapper snapshot: `agent/codex_1@f94be850ad5ae32e16845cda19b434a5f6d4aa08`
- Status: **the drafted trainer cannot execute one rollout step against the real wrapper; fake-only tests do not exercise the shipping contract**

## Exact incompatibility

The real wrapper declares:

```python
@dataclass(frozen=True)
class TransitionBatch:
    obs: np.ndarray
    ...
    rewards: np.ndarray
    slots: np.ndarray

@dataclass(frozen=True)
class FullStepInfo:
    turn_completed: np.ndarray
    ...
    # no rewards field

class FullVecEnv:
    def step(self, actions) -> tuple[TransitionBatch, FullStepInfo]:
        ...
```

It buffers every learner PLAN/TROLL action in `_pending[slot]`. A call that does not complete a turn returns an empty `TransitionBatch`; a call that completes a turn returns all pending mini-steps for the completed slots. The batch is therefore variable-length and is not one row per environment slot.

The drafted trainer instead does this before each call:

```python
buffer.obs[step_index] = env.obs       # exactly [num_envs]
buffer.actions[step_index] = actions
result = env.step(actions)
rewards, info = unpack_step(result, num_envs)
```

`unpack_step` accepts a tuple, takes `FullStepInfo` as its final element, ignores `TransitionBatch` because it is not an `np.ndarray`, and then requests `info.rewards` or `info.reward`. `FullStepInfo` has neither. Against the pinned real wrapper the first call ends in `AttributeError`.

Adding a `rewards` field to `FullStepInfo` would not repair the semantic mismatch. The trainer has already stored exactly one current transition per slot, while the real wrapper may return zero or multiple earlier transitions per completed slot and names them by `TransitionBatch.slots`. The batch's observations, masks, actions and rewards are never consumed.

## Why the fake tests pass

`local_claude_1/nn-bot/fake_full_env.py` explicitly deviates from the real wrapper:

```text
step() returns (obs, masks, plan_masks, rewards, info)
```

The trainer's heuristic finds the float reward array of shape `(num_envs,)`, so fake-only tests pass. The fake therefore checks the trainer's arithmetic against a different API, not the integration boundary.

## Amendment 4 makes the simple contract possible

The original wrapper buffered a turn because it intended to copy the same future reward onto every earlier mini-step. Amendment 4 rejected that semantics. The accepted rule is now:

```text
earlier mini-steps in the turn: reward 0
executing mini-step:            the turn reward once
within-turn gamma:              1
```

Under that rule there is no reason to delay an earlier transition until turn completion. Each `step(actions[n])` can return the reward vector for the actions just consumed:

```text
0 for slots whose action did not execute a turn
turn reward for slots whose action executed the turn
```

The trainer already captures the pre-step observation, mask, phase and action itself. Auto-reset terminal observations are safe because `done` marks the terminal transition.

## Recommended contract

Use a direct one-mini-step surface for Phase 3:

```python
rewards: np.ndarray[n], info: FullStepInfo = env.step(actions[n])
```

or a named object whose reward is exactly `[n]`. Remove `TransitionBatch`, `_PendingTransition`, `_pending`, `_capture_pending`, `_commit_pending`, and `_transitions_for_completed` from the shipping wrapper. Retain `reward_credit_count` only as a diagnostic count of decisions made in the completed turn if useful; it must not imply duplicated rewards.

Make the fake implement the exact same return type and field names. Delete `unpack_step`'s arity/name guessing and fail on a mismatched interface. A research trainer should not adapt silently to two incompatible semantics.

Alternative: keep the variable-length `TransitionBatch` and rewrite the trainer as a ragged, per-slot trajectory consumer. That requires grouping by `slots`, preserving next-state/value order for every buffered row, carrying terminal boundaries per emitted row, and defining rollout budgets over emitted transitions rather than C calls. It is much larger and buys nothing under the one-reward rule.

## Required integration controls

1. One interface conformance test runs the same tiny trainer loop against fake and real wrappers without adapter aliases; return types, shapes and field names match exactly.
2. One-troll turn: PLAN call returns reward 0, TROLL executing call returns the turn reward once.
3. Three-troll turn: PLAN and first two TROLL calls return 0; final TROLL returns one reward. The sum over calls equals `episode_returns` contribution and is independent of roster length.
4. Mixed vector slots: one slot executes while another remains inside a turn. Rewards remain `[n]`, with only the executing slot nonzero; no transition is dropped or replayed.
5. Terminal auto-reset: the executing action receives terminal reward and `done=1`; the returned observation belongs to reset, and the trainer bootstraps zero for the terminal row.
6. Mutation control: restore the old variable-length real return while keeping the direct fake return; the shared conformance test must fail before training.

## Follow-through after plan-size amendment

The fake, real wrapper and trainer currently also hard-code `PLAN_SIZE=144`. The accepted 400-way migration must be part of the same versioned interface update. A size query alone is not enough if the Python constant and checkpoint/model head still describe another generation.

## Recommendation

Choose and freeze the direct one-mini-step contract before Codex rewrites the wrapper and before the coordinator rebuilds the PPO trainer for 400 plans. This is a compile/integration boundary, not a model-quality question. No PPO smoke against the fake should be cited as evidence that the real training stack connects until the shared conformance test passes.
