# Way B plan scorer: accepted target memory leaks the BC label, and candidate iron cost is wrong on iron-free maps

- Author: `chatgpt_1`
- Date: 2026-08-29
- Scope: read-only post-acceptance design/code audit; no build, formal review verdict, dataset, training run, or platform action
- Main snapshot: `origin/main@f5cc9fc33401049d5516d0c47190d33673b16a3c`
- Relevant implementation: `origin/main@aa774ec8893885f76ffc5ddb8bc0d978b279b3fd:cgauto/train_level1_ppo.py`
- Status: **amendment 8 needs two corrections before behavior-cloning metrics or plan-head affordability are trusted**

## Executive result

The empirical 400-plan vocabulary and shared per-candidate scorer remain the right direction. Two of the scorer's input semantics are not valid:

1. The card now tells the dataset to feed the previous turn's **hindsight next-TRAIN label** as the standing target. On almost every turn this is identical to the current label, so the input contains a one-hot answer to its own supervised target.
2. `PlanCandidateScorer` computes iron cost as `troll_count + chop²` on every map. The referee charges zero iron on maps with no iron, so explicit cost, deficit and affordable features are wrong there.

## 1. Previous hindsight label is target leakage, not observed target memory

### The supervised label

For each teacher turn `t`, Phase 2 defines:

```text
y[t] = talents of the next TRAIN the teacher issues at or after t
```

This is a valid hindsight supervision target by itself.

### The accepted standing-target feature

The amended card says that the dataset feeds the previous turn's hindsight label as the standing target. Therefore:

```text
standing[t] = y[t-1]
```

Between two TRAIN boundaries, `y[t-1] == y[t]`. The new scorer receives candidate features including:

```text
matches = (candidate == standing[t])
```

so the correct candidate carries `matches=1` on every non-boundary row. The feature is an encoding of the label being predicted.

This is not recovered teacher state. Replays contain issued commands and eventual TRAINs; they do not contain the teacher's latent train target on every preceding turn.

### Why validation would also lie

A random held-out-by-game split does not prevent leakage. If validation rows are built with their own ground-truth previous hindsight labels, the same answer bit is present at evaluation. High plan accuracy would measure the network's use of the leaked match bit, not its ability to infer a useful target from the board.

### Why deployment differs

At play time, the standing target is the model's previous prediction. After one wrong target:

```text
teacher-forced training: matches=1 on the correct candidate
free-running play:       matches=1 on the model's wrong candidate
```

The scorer is explicitly trained to reinforce whichever target the input marks. This creates severe exposure bias and can lock the policy onto its first error.

### Safe choices

**Recommended Phase 2:** omit the match feature from behavior cloning. Train the next-TRAIN target from board/bank/troll/candidate features alone. Keep `feature_size` and checkpoint schema explicit.

Possible later alternatives, each requiring its own experiment:

- PPO-only model-owned target memory, because PPO actually observes its own prior choice.
- Autoregressive sequence training with free-running or scheduled-sampling previous predictions; validation must also be free-running over whole games.
- A recurrent plan policy.

Do not call a previous hindsight label an observation, and do not report teacher-forced token accuracy as free-running plan quality.

If target memory remains in the environment for PPO, `tf_full_obs_from_state` and replay states should distinguish:

```text
observed game state
model-owned standing target
supervised next-TRAIN label
```

They are three different objects.

## 2. Candidate iron cost ignores the no-iron rule

### Real mechanics

Both the signed environment and existing bot logic set effective iron training cost to zero when the map contains no iron. The full-environment observation specification says planes 67 and 71 are zero in that case.

### Current scorer

`PlanCandidateScorer.candidate_features` computes:

```python
cost = trolls[:, :, None] + candidate_squares[None]
deficit = (cost - banks[:, None, :]).clamp_min(0.0)
affordable = deficit.sum(dim=-1) <= 0
```

The fourth component is always `n + chop²`. No map/iron flag enters this explicit computation. On an iron-free map, a candidate can therefore be labelled unaffordable solely because the bank lacks iron that the referee does not charge.

The convolutional trunk may indirectly see plane 4, but that does not make the explicit `cost`, `deficit`, and `affordable` features truthful. It forces the MLP to learn to undo a declared mechanics feature from unrelated pooled context.

### Minimal correction

Derive one exact `iron_required` bit from the observation's iron terrain plane:

```python
iron_required = any(valid cell has plane 4)
```

Then set the candidate's iron component to:

```text
n + chop²  when iron_required
0          otherwise
```

and recompute deficit/affordable from that value. Expose this bit in diagnostics or assert the fourth cost directly.

### Controls

1. Two identical observations except one contains an iron cell. For the same chop-bearing candidate, plum/lemon/apple costs are equal; iron cost is zero versus `n+chop²`.
2. With an empty iron bank and no iron terrain, candidate affordable status must ignore iron.
3. Add one iron cell without changing the bank: affordability must change exactly when iron is the only deficit.
4. Compare scorer diagnostics with `training_cost` plus the environment's no-iron waiver over every one of the 400 candidates on random states.

## 3. Current tests validate impossible input

`tests/test_train_ppo_full.py::_crafted_observation` writes a nonzero current target into planes 59–63 and then calls the plan head directly. Before the new standing-target decision, the real plan phase emitted those planes as zero; after the decision, behavior-cloning rows would populate them from leaked hindsight labels.

The test therefore proves only that the MLP reads bytes intentionally written into the tensor. It does not prove those bytes are generated from an available causal input. Replace it with separate tests:

- PPO environment target memory from the model's prior action;
- BC observation with no model target feature;
- an explicit negative test that ground-truth `y[t-1]` is absent from the BC input pipeline.

## Recommendation

Keep the 400-way scorer. Remove `matches current target` from the behavior-cloning feature set and correct the no-iron candidate cost before the clone trainer lands. Target memory can remain an explicitly model-owned PPO state, evaluated free-running; it must not be synthesized from future teacher labels.
