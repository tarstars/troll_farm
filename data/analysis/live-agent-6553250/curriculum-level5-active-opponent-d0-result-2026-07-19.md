# Curriculum Level 5 complete active-opponent D0 — result, 2026-07-19

## Verdict

**Reject the deterministic complete Rhea/SchedBot baseline as the first opponent-interaction
curriculum.**  It is deterministic, fast, and materially active, but the unchanged Level-4
teacher reaches only 57.4% on consumed development seeds 0--499 versus the frozen 90% feasibility
floor.  Per protocol, no prospective Level-5 seed, training stream, clone, or PPO run is opened.

The result does not reject active-opponent learning.  It rejects this full gather/bank/plant/chop/
train policy as a single first jump from `WAIT`.  A narrower no-growth natural forager was reserved
before outcomes and may be tested only under a new protocol on fresh development seeds.

## Implementation integrity

- Level 5 changes only player-1 commands; Level-4 recipe, player-0 control, reward, objective,
  horizon, observation/action ABI, and teacher are unchanged.
- The opponent is the deterministic FastState baseline inside `rhea_bot`, not rolling-horizon
  search; no RNG, time budget, mutation, or tuned constant enters the environment.
- Six focused Rust tests pass, including repeated active-opponent state/terminal identity and all
  prior shared-actor Level-3/4 tests.
- Fourteen focused Python ABI, determinism, active/waiting divergence, Level-4, and PPO tests pass.
- Identical Level-5 batches reproduce observations, masks, rewards, terminal rows, opponent score,
  and workforce exactly.

One expected readiness defect is recorded rather than repaired: after the opponent occupies the
teacher's fixed planned crop cell, the unchanged teacher can request an illegal BANANA plant.  D0
counts 186 such selections.  Replanning, reserving the cell, or changing the baseline would alter
the frozen teacher/opponent and is therefore not allowed on these consumed seeds.

## Frozen D0 gates

| Measure | Teacher result | D0 requirement | Verdict |
|---|---:|---:|---|
| Overall success | 287/500 = **57.40%** | >=90% | fail |
| Nontrivial success | **55.93%** | >=85% | fail |
| Worst recipe success | **43.94%** | >=75% | fail |
| Worst height success | **53.97%** | >=80% | fail |
| Tracked crop present | **57.60%** | >=90% | fail |
| Renewable harvest | **62.20%** | >=85% | fail |
| Material opponent activation | **100%** | >=50% | pass |

The opponent trains more than one worker in all 500 episodes.  Its mean/median score at termination
is 87.28/64.5, and material activation is 100% in every recipe.  The abstraction is therefore not
accidentally equivalent to waiting; it is substantially beyond the current teacher's feasible
support.

Random legal solves 0/500, creates a tracked crop in 24.8%, and completes a renewable harvest in
1.6%.  This confirms discrimination but cannot rescue teacher infeasibility.

## Accepted-Level-4 zero-shot diagnostic

The accepted seed-89 Level-4 final actor, replayed once on exactly the same consumed seeds, reaches:

- 259/500 = **51.80%** overall;
- 39.06% worst recipe and 46.03% worst height;
- 53.40% crop creation and 53.60% renewable harvest;
- median successful completion turn 90, versus 52 on its Level-4 confirmation bank; and
- 100% material/multiworker opponent activation.

Paired outcomes are 223 both-success, 64 teacher-only, 36 actor-only, and 177 both-fail.  The actor
does not merely fail to imitate an otherwise adequate teacher: the task generator itself is not
ready for this opponent.

## Failure decomposition

Of 213 teacher failures:

- 212 end without the tracked crop still present;
- 189 never complete a renewable harvest;
- 24 do harvest but fail another terminal milestone; and
- all 213 train the requested player-0 worker.

Opponent mean score is 156.00 in teacher failures versus 36.29 in successes.  Long failed episodes
give the complete opponent time to compound its own economy, but the first structural break is the
teacher's single fixed crop-site assumption.  This is not evidence for lowering success floors or
tuning the opponent's planting/training constants.

## Multi-level interpretation

### Action level

The accepted mask and actor remain valid.  The scripted teacher's planned destination ceases to be
legal after adversarial occupation.  Active interaction therefore first requires dynamic target
recovery, not more PPO epochs on undefined labels.

### Economy level

The full baseline simultaneously depletes natural supply, moves through shared paths, plants,
chops, banks, and trains multiple workers.  Its 100% multiworker activation adds an entire rival
growth loop, not just the first missing contention mechanism.

### Curriculum level

One deterministic policy toggle was syntactically isolated but behaviorally too broad.  A valid
next step should activate movement and natural-resource competition while forbidding rival
planting and training, leaving dynamic crop occupation and opponent compounding for later levels.

### Transfer level

This local result has no Arena implication.  It neither promotes nor weakens the exact resident;
it only prevents wasting a prospective bank and a multi-million-decision PPO run on an infeasible
teacher/task pair.

## Decision and retained hypothesis

Close the fixed complete-baseline Level-5 D0 without tuning.  Keep its deterministic harness as a
future regression/opponent-strength target.  The next eligible question is the preregistered
no-growth natural forager on fresh development seeds 500--999: one opponent starter may move,
harvest natural fruit/mine, and bank, but may not plant, chop, pick, or train.  Its protocol and
feasibility floors must be frozen before execution.

## Reproducibility anchors

- development protocol:
  `d9103fb9bc6eea8ced9709050e4d3725cc2d7679c4faa3088a73ff538b83c037`;
- teacher control:
  `12c2865039863e7b35b70e26a550b54a53f2a81a82fff8a3b580ac8c14cdf583`;
- random-legal control:
  `e6492de64d8380f82dc8d5c8bea6efcb03546e8b8f5e6f51362300987bfc67cc`;
- accepted-Level-4 zero-shot replay:
  `525629b696a51598495a2d0e693e19d308d0fef7a02ce2c8306ec0ebbbbe636f`.
