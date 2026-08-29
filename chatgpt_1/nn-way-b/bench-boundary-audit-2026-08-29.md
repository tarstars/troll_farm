# Way B Phase 2 bench boundary audit: the current smoke is not yet the policy environment's truth bench

- Author: `chatgpt_1`
- Date: 2026-08-29
- Scope: fresh-eyes interface/validity audit; no build, formal review verdict, experiment, platform action, or change to another agent's files
- Main snapshot: `origin/main@448dc8e19b4144abb7663c845a778d2d960b5037`
- Builder snapshot: `agent/claude_1@0ac974d87cd07804d9e7647045e726858996d80c`
- Task: `20260829-nn-bot-way-b-dataset`
- Status: day-1 random-policy smoke is useful as a pipe test; four amendments are required before the trained clone is judged through this bench

## Summary

`local_claude_1/nn-bot/bench.py` successfully proves that a Python policy and a compiled bot can be driven through the July referee on 24 maps. It does not yet implement the signed policy semantics that Phase 1 and the dataset use.

The load-bearing mismatches are:

1. A plan action is treated as a pre-turn TRAIN command, not as an always-legal train target resolved after spatial commands.
2. The plan selected for the turn and earlier trolls' staged actions are absent from the later troll's explicit view/mask contract.
3. The loop always executes the requested number of turns and never applies the referee's early terminal rule.
4. The compiled bot is always seat 0 and the Python policy always seat 1, while the final gate promises both seats.

These do not invalidate the random-policy smoke as a smoke. They would invalidate a clone-versus-champion result if left unchanged.

## 1. Plan semantics differ in exactly the cases the plan head exists to model

### Signed environment semantics

The parent card and `ENV-API.md` define a plan action as a **target**, not an immediate command:

- every valid talent tuple is legal even when it is currently unaffordable;
- troll mini-step observations carry that chosen target in planes 59-71;
- after all spatial commands are staged, Rust dry-runs the exact turn;
- it emits TRAIN only if that target succeeds under post-MOVE/post-PICK inventory and shack occupancy.

### Current bench semantics

`bench.py::play` does this before asking any troll for its command:

```python
plan = policy.plan(view)
if plan is not None:
    if ref.can_train(tuple(plan), seat) is None:
        frags.append("TRAIN ...")
    else:
        illegal.append(...)
```

Only afterwards does it call `policy.command(view, uid)`.

So the bench classifies a deliberately unaffordable future target as illegal and makes the TRAIN decision against the pre-command state.

### Concrete divergent cases

- **Starter vacates the shack this turn.** The pre-turn check says `shack_occupied`; the signed environment sees the MOVE first and can train.
- **A troll PICKs the last missing fruit this turn.** The pre-turn check says `unaffordable`; the signed environment executes PICK before TRAIN and can train.
- **A troll consumes stock with PICK before TRAIN.** The pre-turn check appends TRAIN, but the exact post-PICK dry run may suppress it.
- **A unit moves onto the shack this turn.** The pre-turn check appends TRAIN, but the exact post-MOVE dry run rejects it.

The same network and action sequence can therefore train on different turns in training and in the truth bench.

### Required amendment

The bench policy interface must distinguish:

```text
plan target selected
TRAIN command actually emitted after exact turn dry-run
```

Collect all spatial commands first, then run the same plan-to-command adapter as Phase 1 against the complete pair of command lines. The simplest safe architecture is one shared pure helper with the same phase order and a parity test over the four cases above. Do not call an unaffordable plan target an illegal command.

## 2. Later troll decisions do not receive the signed mini-step context

The signed environment gives each later troll:

- the current turn's selected plan target;
- earlier own trolls drawn at their staged end cells;
- a reservation-aware mask that prevents duplicate planned end cells.

The current `SeatView` exposes none of `plan_target`, `plan_index`, or `staged_actions`. `play` calls every `policy.command(view, uid)` against the same referee state, and `SeatView.legal(uid)` computes each troll's legal commands independently. It does not reserve the end cell of an earlier chosen troll.

A stateful policy object could secretly remember what its own previous method returned, but that is not the explicit observation/mask contract and the bench's independent legality check would still use a different mask.

### Required amendment

Before each troll decision, expose the exact mini-step context used by the network:

```text
selected plan index/target
active troll id
ordered staged actions for earlier own troll ids
player-relative observation
reservation-aware mask
```

The clone adapter should consume the same plane builder and mask semantics as the dataset/full environment. The bench remains an independent referee, but not a second policy interface.

Add a two-troll control where troll A reserves troll B's current cell and B must vacate; verify that the bench and `FullVecEnv` present the same mask and choose the same canonical commands.

## 3. The bench does not end games when the referee ends them

`play` executes:

```python
for turn in range(1, turns + 1):
    ...
    ref.apply_two(bot_line, policy_line)
    ref.grow()
```

There is no persistent no-tree grace counter, no `has_stalled`/mercy check, and no break before the fixed turn count.

The signed full environment ends at 300 turns **or** under the persistent referee `has_stalled` rule. Continuing after that boundary changes inventories, training, final scores, loops, and the owner's replay.

### Required amendment

Give the independent bench its own tested terminal adapter:

1. preserve the no-tree grace counter across turns;
2. after each complete phase+growth transition, apply the exact terminal predicate;
3. stop immediately on terminal;
4. record `terminal_turn` and `terminal_reason`;
5. include one turn-limit and one early-stall positive control, plus a negative control that would continue one extra turn.

This is the same last-boundary property that Phase 1's replay verifier must check independently.

## 4. The current bench is one-sided

The source and its own output say:

```text
compiled bot = seat 0
Python policy = seat 1
```

`BotProcess` receives `ref.map_header()` and `ref.turn_text()`, both the seat-0 protocol view. There is no seat selector or transformation path in the CLI or `play`.

That is sufficient for the day-1 pipeline smoke. It is not the parent card's 400-map **both-seats** gate.

### Required amendment

Add an explicit, tested seat adapter. For each map/seed pair, evaluate the policy once as each absolute seat against the same compiled bot policy and name the pairing. The compiled single-file process must receive the same player-relative protocol it would receive in that seat, and its commands must map back to absolute ids/cells without changing tie rules.

Do not relabel a 180-degree data augmentation as a both-seat game unless the command/referee path is also transformed and round-tripped. Add a seat-swap involution test: transform state and commands twice and recover the original bytes/ids/cells.

## Acceptance controls before a clone result is called a bench result

1. Four plan-timing cases above: bench and `FullVecEnv` emit TRAIN on the same turn or both suppress it.
2. For every mini-step in a two-troll case, observations, active id, plan target, staged context and action masks match the signed policy interface.
3. A turn-300 game and an early-stall game end on the same turn and reason as the exact engine.
4. Every evaluation map is run with the learned policy in both seats; pairing is explicit in the report.
5. The random-policy 24-map smoke remains reported separately as a pipeline smoke, not reused as proof of these four properties.

## Recommendation

Continue the day-2 label pilot; these issues do not prevent extracting exact replay labels. Before plugging the clone into the bench, amend the policy adapter and add the controls above. The desired independence is: separate referee and compiled-opponent process, **shared signed policy semantics**.
