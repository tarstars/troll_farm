# Fresh-eyes integration audit — Way B full-game neural policy

- Author: `chatgpt_1`
- Date: 2026-08-29
- Status: **owner-directed advisory**, not the assigned review verdict
- Parent task: `20260829-nn-bot-way-b`
- Main snapshot read: `origin/main@bcef07ef1767af4f411577f7038c2f286a1f49a9`
- Rust environment snapshot read: `agent/codex_1@2c5519f8d3b2973bf6943a754496d8299be3ce4e`
- Dataset/bench snapshot read: `agent/claude_1@0ac974d87cd07804d9e7647045e726858996d80c`
- Signed interface source: `agent/codex_1@a1256c643fd57260cdc4adba605462214bd63dcb`
- Rust file reviewed: `rust/src/rl_full.rs`, blob `03bca877a6dea17f1849214a87b60fbcf06148b0`
- Scope: read-only interface and first-slice code review. I ran no build, test, environment, dataset, trainer, panel, submission, or Arena action.

## Verdict

**Continue the mechanics prototype, but do not lock the dataset codec or start PPO against the current contract.**

Two codec defects can make valid seat-1 or non-MOVE expert commands become wrong/masked labels. The reconstructed-state ABI also accepts semantically impossible mini-step contexts instead of failing closed. Separately, the signed reward-credit rule duplicates one full-turn reward across a variable number of mini-step transitions; unless the trainer treats those transitions specially, the optimized return depends on troll count and disagrees with `episode_returns`.

These are interface defects, not reasons to abandon Way B. They are cheapest to repair now, before the Python builder and trainer copy the assumptions.

## 1. BLOCKER — the command codec has no coordinate-frame input

### Record

The parent card and `OBS-PLANES.md` make the policy player-relative: seat 1 is rotated inside the real `w × h` board. The action mask is therefore player-relative too.

The dataset contract labels MOVE with the cell the troll actually reached in the next referee snapshot. That snapshot cell is absolute. A seat-1 label must be transformed to:

```text
relative_x = w - 1 - absolute_x
relative_y = h - 1 - absolute_y
```

But the signed helpers are:

```c
int32_t tf_full_decode_action(action_index, troll_id, width, height, ...);
int32_t tf_full_encode_command(command, length, expected_troll_id, width, height);
```

They carry no `seat` or coordinate-frame argument. The implementation maps `MOVE x y` directly to `y * 22 + x`, and decodes the same way. Therefore the helper cannot, by itself, turn an absolute seat-1 reached cell into the player-relative action index used by the observation and mask.

### Consequence

Unless every caller independently remembers to rotate first, seat-1 MOVE labels are mirrored incorrectly. A held-out accuracy calculation can still look internally consistent if the same wrong convention is used on both sides, while the live environment chooses actions in the other frame.

The coordinator's signature note says `tf_full_encode_command` is what the reached-cell MOVE-label rule needs. Under the current signature, that statement is true only for seat 0 or for an undocumented pre-rotated command.

### Required repair

Freeze one explicit convention before the dataset pilot:

```text
A. Add `seat` to encode/decode and make command text absolute referee coordinates; or
B. Rename the helpers `*_relative` and require/pre-test a separate absolute↔relative transform.
```

I recommend A because it leaves one source of truth.

Required negative control: use a non-maximal board, for example `20 × 10`, and an asymmetric cell. Prove for both seats and all board sizes:

```text
absolute reached cell
→ encode(seat)
→ player-relative action index
→ decode(seat)
→ the original absolute command
```

Testing only seat 0 or a point-symmetric centre cell cannot catch this defect.

## 2. BLOCKER — non-spatial commands cannot be encoded to a legal flat action

### Record

The signed mask places planes 1–12 only at the active troll's **player-relative current cell**. That is the canonical flat label for HARVEST, CHOP, DROP, MINE, PLANT, and PICK.

`encode_command_text`, however, has no active-cell argument. For every non-MOVE command it returns:

```text
plane * 242
```

which means coordinate `(0, 0)`. The source comment says a state-aware caller must move that plane index to the active troll's cell, but that operation is absent from the signed API contract.

### Consequence

A general caller of `tf_full_encode_command` gets a mask-zero label for almost every non-spatial command. The dataset contract requires flat labels for every command, not only MOVE. Two independent builders can therefore implement different undocumented relocation rules and still each appear reasonable.

### Required repair

Do not overload one stateless helper with two incompatible jobs. Freeze either:

```c
int32_t tf_full_encode_command_for_state(
    command, length, seat, active_troll_id, json_state, ...);
```

or a smaller exact helper:

```c
int32_t tf_full_encode_command(
    command, length, expected_troll_id,
    seat, active_absolute_x, active_absolute_y,
    width, height);
```

Then test every verb on both seats and assert:

```text
mask[label] == 1
and decode(label, seat) == canonical command
```

If the project intentionally uses `tf_full_encode_command` for MOVE only, rename/document it as such and give the dataset builder a separate state-aware verb encoder. The current general name and return contract are unsafe.

## 3. BLOCKER BEFORE THE 1,000-STATE PARITY GATE — reconstructed mini-step context is fail-open

### Record

`tf_full_obs_from_state` validates only seat, phase membership, and plan-index range. The signed JSON contract says PLAN has active troll `-1`, plan `0`, and no staged actions; a TROLL mini-step has one real active own troll and only earlier same-seat trolls in ascending-id `staged_actions`.

The implementation does not enforce those invariants. In particular:

- PLAN accepts a nonzero plan target and staged actions;
- PLAN accepts an arbitrary active troll id;
- TROLL can accept a nonexistent active troll when the optional mask pointer is null, returning an observation with no plane-99 active troll;
- `prior_target_trained` accepts any nonzero byte rather than exactly `0|1`;
- staged actions need not be unique, ordered, earlier than the active troll, or even legal under the mask;
- a negative staged action is coerced to action 0 with `max(0)`;
- other invalid staged actions are silently ignored instead of rejecting the snapshot.

### Consequence

The ABI can return status 0 for a state that cannot occur in the environment. That weakens the advertised drift gate: extraction bugs may be normalized into deterministic but false planes rather than becoming a hard failure.

### Required repair

Add one `validate_snapshot_context` used before both observation and mask generation. At minimum:

```text
phase PLAN:
  active_troll_id == -1
  plan_index == 0
  staged_actions empty

phase TROLL:
  active_troll_id is an own living troll
  staged ids are unique and strictly increasing
  every staged id is smaller than active_troll_id
  every staged action is in range and legal at its own mini-step
  no active or opponent troll appears in staged_actions

all phases:
  prior_target_trained in {0,1}
  every unit/plant/resource coordinate is in bounds
  every plant kind is one of PLUM/LEMON/APPLE/BANANA
```

Malformed context should return a stable error and never silently reinterpret the input. Add a negative-control table containing one example for every rejected invariant.

## 4. DESIGN STOP BEFORE PPO — one turn's reward is duplicated by roster size

### Record

The signed API defines one reward when a full turn executes. It then says `FullVecEnv` buffers that turn's plan and troll transitions and emits **the identical scalar** for all of them. With `n` learned trolls, one referee turn therefore contributes the same reward `n + 1` times to the decision trajectory.

At the same time, `episode_returns` is explicitly defined as the reward summed once per full turn, not multiplied by mini-step count. `reward_credit_count = n + 1` exposes the discrepancy but does not resolve it.

### Consequence

A conventional PPO/GAE loop over emitted mini-step transitions optimizes a different return from the reported episode return:

```text
training reward for a turn = (n + 1) * full_turn_reward
reported episode reward    =             full_turn_reward
```

Because `n` changes when the policy trains trolls, this is not a harmless constant rescaling. It creates an objective-level incentive to increase the number of decisions, and it changes the effective discount horizon as the roster grows. The clone/PPO comparison can then confound game value with action-factor count.

### Required decision

Freeze temporal credit before Phase 3. The cleanest sequential formulation is:

```text
intermediate plan/troll mini-steps: reward 0, gamma_internal = 1
mini-step that executes the turn:   full turn reward, gamma_turn = configured gamma
```

The reward then propagates through the factorized decisions without being counted multiple times. A macro-action PPO formulation that sums the plan/troll log-probabilities is also coherent, but larger.

Dividing the scalar by `reward_credit_count` is not by itself a complete fix: GAE and discounting must also know which transitions are inside one referee turn.

Required invariants:

```text
sum(training transition rewards in episode) == episode_returns
adding a no-op factor inside a fixed turn does not change return or advantage
changing troll count without changing the referee trajectory does not rescale past/future rewards
```

This issue need not stop observation/mask implementation, but it must stop trainer/PPO acceptance until settled.

## 5. CONTRACT DRIFT — map and plant validation disagree with the signed text

`ENV-API.md` calls `shacks` a required map-record field while also saying rows are authoritative. `MapRecord` does not deserialize or verify `shacks`; a missing or contradictory field is accepted. Choose one contract: remove the redundant field from the requirement, or deserialize it and require exact equality with the two shack cells parsed from rows.

`JsonPlant` accepts an arbitrary type string. Observation generation catches `item_index` panics and can emit a generic living-tree plane without a kind plane; later engine functions may panic on the same invalid type. Reject invalid plant kinds at parse time instead of carrying a half-valid game.

## 6. Recommended immediate sequence

1. Keep implementing the mechanics behind the signed observation layout; no architecture rollback is needed.
2. Amend the action codec before Claude freezes dataset labels.
3. Add strict snapshot-context validation before calling the 1,000-state test meaningful.
4. Add a cross-builder conformance fixture with both seats, all verbs, multiple board sizes, and staged earlier trolls.
5. Decide turn-boundary reward/discount semantics before the PPO wrapper or trainer is accepted.
6. Keep `local_claude_1` as the assigned reviewer. This memo is an early integration alarm, not a competing verdict.

## Bottom line

Way B remains viable. The immediate danger is not the 104-plane representation; it is a split convention at the Rust/Python boundary. The current helper signatures cannot fully express the canonical labels that the task requires, and the reward contract makes the optimized return depend on how many mini-step factors the policy has. Repairing those contracts now is much cheaper than diagnosing a clone that trains successfully on the wrong labels or a PPO run that improves the wrong objective.
