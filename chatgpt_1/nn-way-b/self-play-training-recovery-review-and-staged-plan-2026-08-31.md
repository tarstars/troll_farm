# Self-play training recovery: review and staged, gated plan

Date: 2026-08-31  
Agent: `chatgpt_1`  
Task: `20260829-nn-bot-way-b`  
Primary dossier reviewed: `main@f9595b53066903cce8f1104bc915420b3650b484`, `local_claude_1/nn-bot/EXPERIMENT-2026-08-31.md`  
Prior adversarial review: `agent/chatgpt_1@b750ed7dfdfab623e2ebaca430e71e3b7b2f6982`, `chatgpt_1/nn-way-b/experiment-second-opinion-2026-08-31.md`

## Executive verdict

The current self-play trainer has two distinct failure modes and they must not be repaired in one broad experiment.

1. **Full-parameter PPO corrupts the cloned executor.** The policy receives mostly short-rollout, critic-bootstrapped advantages; per-minibatch normalization restores those weak/noisy differences to ordinary update scale; the value loss also changes the shared policy trunk. The cloned multi-step economy — harvest, carry, return, drop, plant — deteriorates before immediate actions such as chop.
2. **The staged plan-only run removes the rapid executor collapse but the plan policy still drifts.** PLAN actions are sampled during training and decoded by argmax at deployment; entropy continuously flattens the distilled policy; the environment asks for a fresh target every turn; previous-target information is hidden; all 400 plans remain explorable although only 106 were observed in teacher data. Run I's anchor remained near `0.1`; its drift is not evidence that the anchor decayed to `0.05`.

The repair strategy is therefore:

```text
protect the cloned executor
→ make plans persistent options rather than turn-by-turn votes
→ train plans from completed outcomes
→ isolate the critic from policy features
→ retain supervised replay protection
→ prove a robust plan gain
→ only then consider a narrowly constrained executor fine-tune
```

No full-parameter PPO run should be launched while this programme is in force.

## Gate discipline used by every stage

### Three evaluation populations

- **Scout:** 48 fixed map-seat cells. Used for frequent progress reads and replay inspection only.
- **Confirmation:** 192 fixed map-seat cells that are not used to select checkpoints or tune hyperparameters.
- **Promotion:** 400 games against the champion and 400 against orchard 6, under the existing project gate.

### Primary paired statistic

For every fixed map-seat cell:

```text
paired_delta = candidate_score_margin - baseline_score_margin
```

Report the mean paired delta and a 95% paired bootstrap interval over cells. Wins gained/lost, both seats, action counts, illegal commands, timeouts and loops are secondary diagnostics. Do not treat `10/48` versus `9/48` as a demonstrated gain.

### Publication requirements

Every gate record must pin:

- source commit and trainer hash;
- starting checkpoint hash;
- complete command/configuration;
- seed and map-panel hash;
- output/checkpoint hash;
- baseline identity;
- raw per-cell results, not only a summary;
- a plain `PASS`, `FAIL`, or `INCONCLUSIVE` verdict.

A stage may not consume the next stage's compute after `FAIL` until its failure has been reviewed.

---

# Stage 0 — freeze the evidence and make the measurements trustworthy

## Purpose

Close the remaining observability gaps before another causal training claim. Existing cluster runs may finish and be recorded, but they are exploratory evidence and do not substitute for this gate.

## Work

1. Pin the clone, G@500, H@500, I checkpoints, trainer version and all existing bench panels.
2. Finish the corrected `grad_decompose.py` instrument:
   - incompatible clone optimizer state is reported as unavailable, not loaded heuristically;
   - effective resumed learning rates are reported;
   - on-policy measurements and a shared fixed observation census are separated;
   - value-only counterfactual steps are measured on identical observations.
3. Add trainer telemetry for:
   - raw advantage mean, standard deviation and quantiles before normalization;
   - number/fraction of rows whose rollout contains observed terminal reward;
   - estimated bootstrap contribution to returns;
   - PLAN and TROLL row counts;
   - plan entropy, top-1 agreement and selected-plan support class;
   - aggregate epoch KL, not only the last minibatch's KL.
4. Lock and publish the 48-cell scout, 192-cell confirmation and 400-game promotion populations.
5. Re-run the unmodified clone twice on the scout panel and compare exact command/replay hashes.

## Gate 0

**PASS only if all are true:**

- two clone reruns have identical per-turn command hashes, terminal states and scores on all 48 cells;
- the corrected gradient instrument completes for clone/G/H, with a common fixed observation census;
- the new telemetry is present in a deterministic smoke run and has negative-control tests;
- the three evaluation populations and their hashes are published before training;
- instrumentation does not change action streams under a matched-seed control.

**FAIL if any identity, replay, state, or action stream differs, or if raw advantage/bootstrap attribution is still unobservable.** On failure, stop training work and repair the measurement path.

---

# Stage 1 — isolate the entropy-softening hypothesis

## Purpose

Test the cheapest remaining causal explanation for slow plan drift without changing plan semantics, anchor strength, learning rate, opponent, seed, or executor.

## Work

Run a matched run-I arm with exactly one change:

```text
entropy_coef: 0.01 -> 0.0
```

Keep:

```text
train_scope = plan-critic
TROLL decoding = masked argmax
executor weights = frozen
same seed, maps, champion-only opponent, gamma, lambda,
learning rates, critic warm-up and anchor schedule as run I
```

Read checkpoints at updates 500, 1000, 1500, 2000 and 2500 on the 48-cell scout. Evaluate updates 1500 and 2500 once on the locked 192-cell confirmation panel.

## Gate 1

This is primarily a **causal gate**, not yet a promotion gate.

**`ENTROPY_CONFIRMED` if all are true:**

- frozen executor tensors are byte-identical to the starting clone;
- at both updates 1500 and 2500, paired mean score margin is better than run I at the same update;
- the pooled 384-cell paired bootstrap interval for `(entropy-zero - run-I)` has lower bound above zero;
- plan entropy does not rise above its starting value by more than `0.05` nats;
- clone top-1 plan agreement at update 2500 is at least five percentage points higher than run I's;
- no new illegal command, timeout, or activity-collapse signature appears.

**`ENTROPY_NOT_CONFIRMED` if the pooled interval includes zero or the same drift remains.** This does not validate the current trainer; it only says entropy alone is not a sufficient explanation. Later stages still begin with entropy zero to keep the new objective minimal.

---

# Stage 2 — replace turn-by-turn target voting with a persistent plan option

## Purpose

Make the plan action represent the strategic decision it is supposed to represent: a commitment to a purchase target, not a fresh vote every turn.

## Work

1. Introduce a persistent `PlanOption` with:
   - selected target;
   - decision turn;
   - elapsed turns;
   - affordability/deficit state;
   - completion and invalidation reason.
2. Invoke the plan policy only at a defined decision event:
   - game start;
   - successful purchase;
   - target invalidation;
   - explicit bounded timeout/cancel.
3. Between decision events, retain the target and do not resample it.
4. Make prior commitment visible at decision events. Do not leak a hindsight label.
5. Rebuild the supervised plan dataset at **decision events**, not every turn:
   - one row at game start and after each purchase/cancel boundary;
   - label = next actual purchase or stop;
   - held out by game;
   - no repeated hindsight target on every intervening turn.
6. Initially restrict exploration to:
   - `train nothing`;
   - the 106 plans observed in teacher data.
   Unsupported plans may be reopened only by a later explicit experiment.
7. Retrain only the plan head; the executor remains frozen.

## Gate 2

**Validity sub-gate — all required:**

- over 1,000 environment games, the target changes only at a recorded decision event;
- zero target changes occur between events;
- every training label is legal under its recorded mask;
- a leakage test proves no feature deterministically contains the hindsight label;
- event reconstruction is deterministic and held-out games share no rows with training games.

**Performance sub-gate — all required on the same event census and locked confirmation panel:**

- held-out event-level negative log-likelihood is no worse than the old plan head evaluated on that same census;
- held-out top-1 accuracy is no worse than the old plan head;
- on the 192-cell paired confirmation panel, the lower bound of the score-margin delta versus the original clone is above `-2.0` points per game;
- candidate wins are not more than four of 192 below the original clone;
- no illegal commands, timeouts or new loop mechanism.

**PASS only if both sub-gates pass.**  
**FAIL if commitment semantics are violated or the event-level clone materially regresses.** On failure, repair supervised plan learning before any RL.

---

# Stage 3 — build an episode-level option trainer with an isolated critic

## Purpose

Remove the two structural causes of unreliable credit: 32-mini-step policy returns and value gradients through policy features.

## Work

1. Collect complete episodes with the executor frozen.
2. Store only plan decision events for the plan-policy update:
   - observation and legal support;
   - selected plan and old log-probability;
   - commitment interval and outcome;
   - realized terminal score margin and exact return-to-go.
3. Compute plan-policy returns from completed games. Do not bootstrap plan-policy advantages across a rollout boundary.
4. Give the critic its own encoder, or detach policy features before the critic. A value-only update must not change plan or executor logits.
5. Use separate plan and critic optimizers and separate clipping.
6. Start with `entropy_coef = 0`.
7. Add fixed supervised replay on the event-level teacher census every update:

```text
loss = plan_RL_loss
     + fixed_teacher_cross_entropy_or_KL
     + separate_critic_loss
```

8. Normalize advantages once over the complete PLAN update batch, not independently in each minibatch. Log raw values first. If raw advantage variance is below a frozen floor, skip the policy update rather than amplifying numerical noise.
9. Keep the initial supported action set at `nothing + 106 teacher plans`.

## Gate 3

**PASS only if all are true:**

- every policy row is linked to a completed episode and realized return-to-go;
- reported policy bootstrap fraction is exactly zero;
- a value-only optimizer step changes plan logits and executor logits by exactly zero within numerical tolerance (`max_abs_shift <= 1e-8` in float32 test fixtures);
- executor parameters remain byte-identical after a 1,000-update smoke;
- repartitioning the same PLAN batch into different minibatches changes the aggregate policy gradient by less than `1e-6` relative error;
- a constant-return negative control produces zero plan-policy gradient after centering;
- a replay-only control preserves the event-clone top-1 decisions;
- 1,000 smoke episodes complete with zero illegal commands and zero timeouts.

**FAIL if policy credit still depends on rollout bootstrap, critic updates move policy logits, or the fixed executor changes.** No gameplay-improvement run starts before this gate passes.

---

# Stage 4 — run the first honest plan-only RL pilot

## Purpose

Test whether strategic purchase choices can improve a protected cloned executor when trained from completed outcomes.

## Frozen treatment

```text
persistent PlanOption
complete-episode plan returns
separate critic
executor frozen and argmax
entropy = 0
fixed teacher replay
teacher-supported plan mask
champion-only opponent for the first causal pilot
```

Use a fixed budget of **50,000 completed games**. Publish checkpoints every 5,000 games. The 48-cell scout may nominate at most three checkpoints using a rule frozen before the run. Those candidates receive one evaluation on the untouched 192-cell confirmation panel.

## Gate 4

**PASS if one nominated checkpoint satisfies all:**

- the lower bound of the 95% paired bootstrap interval for score-margin delta versus the Stage-2 event clone is above zero on 192 cells;
- it wins at least eight more of 192 cells than the event clone loses to it;
- zero illegal commands and zero timeouts;
- mean harvest, drop and plant counts are each at least 90% of the event clone's counts;
- no loop class increases by more than two games;
- two adjacent scout checkpoints do not show a collapse trend.

**FAIL if no checkpoint passes within 50,000 games, or if apparent score improvement comes with an activity-collapse or legality regression.** Do not extend the budget automatically; diagnose the failed gate first.

---

# Stage 5 — prove that the plan gain replicates

## Purpose

Separate a real training recipe from one favorable seed or one reused evaluation panel.

## Work

Run the Stage-4 configuration from three independent seeds. Use the checkpoint at the same fixed completed-game budget, not the best checkpoint from each curve. Evaluate on three disjoint 192-cell confirmation panels, assigned before training.

## Gate 5

**PASS only if:**

- at least two of three seeds have a paired score-margin interval whose lower bound is above zero versus the event clone;
- the pooled 576-cell paired interval has lower bound above zero;
- no seed is worse than the event clone by more than `5.0` mean score-margin points;
- all seeds preserve executor identity, legality and the Stage-4 activity floors.

**FAIL if improvement is seed-specific or disappears on disjoint panels.** A failed replication returns the project to Stage 3/4 diagnosis; it does not justify executor unfreezing.

---

# Stage 6 — optional constrained executor improvement

This stage is permitted only after Gate 5 passes. The plan-only candidate remains the fallback.

## Stage 6A — command head only

Unfreeze only `actor.*`; keep `stem.*`, `tower.*` and the separate critic arrangement frozen. Use:

- no entropy bonus;
- actor learning rate no greater than `0.05` times the plan learning rate;
- fixed teacher command replay on every update;
- explicit KL to the cloned command distribution;
- completed-episode returns;
- the already validated persistent plan policy.

### Gate 6A

**PASS only if:**

- fixed teacher-census command top-1 accuracy drops by at most `0.5` percentage points overall;
- HARVEST, DROP, PLANT and PICK accuracy each drop by at most `1.0` point;
- mean command KL to the clone is at most `0.02` nats on the fixed census;
- the 192-cell paired score-margin interval versus the Stage-5 plan-only candidate has lower bound above zero;
- harvest, drop and plant counts each stay above 95% of the plan-only candidate;
- zero illegal commands and zero timeouts.

**FAIL means ship/continue with the plan-only candidate.**

## Stage 6B — last residual block, only after 6A passes

Optionally unfreeze the last residual block at one tenth of the Stage-6A actor learning rate. Keep teacher replay, clone KL, separate critic and every 6A gate.

### Gate 6B

Apply the same gate as 6A against the 6A candidate, plus require that a value-only step still produces zero policy-logit shift. Failure reverts to 6A.

The full trunk is never released in one step.

---

# Stage 7 — promotion and export

## Local promotion gate

The final candidate must satisfy the existing target, without using the scout or confirmation panels for tuning:

- 400 games against the champion, both seats;
- 400 games against orchard 6, both seats;
- at least 60% wins and positive mean margin against each;
- three consecutive gates;
- zero illegal commands and zero timeouts;
- no unexplained engine or replay divergence.

## Export gate

- Python policy and generated Rust bot are command-identical on the parity bed;
- UTF-16 source length is below 100,000 code units;
- three quiet-host runs each satisfy the warm-turn limit of 15 ms;
- cold start satisfies the recorded platform bound;
- baseline CPU fallback and optimized path are both proven;
- the owner gives a separate platform word.

**PASS:** candidate is ladder-ready.  
**FAIL:** no submission; return to the earliest failed technical or performance gate.

---

# Decision tree

```text
Gate 0 fails
    -> measurement repair only

Gate 1 confirms entropy
    -> entropy zero is frozen for later stages
Gate 1 does not confirm entropy
    -> do not claim it as cause; later clean trainer still starts at zero

Gate 2 fails
    -> repair plan semantics / event clone; no RL

Gate 3 fails
    -> repair credit or critic separation; no RL

Gate 4 fails
    -> do not add compute blindly; inspect plan returns, replay force and action support

Gate 5 fails
    -> no executor fine-tune; recipe is not robust

Gate 5 passes
    -> Stage 6 is optional, conservative and reversible

Gate 7 passes
    -> owner may authorize platform use
```

## Ranked recommendation from the current state

1. Complete Gate 0 and read the in-flight cluster outputs as exploratory context.
2. Run the Stage-1 entropy-zero falsifier because it is cheap and changes one variable.
3. In parallel with that read, design Stage 2, but do not run its RL successor until Gate 1 is recorded.
4. Treat Stages 2 and 3 — persistent options plus completed-outcome training with critic isolation — as the actual training repair.
5. Do not run a `gamma=1, lambda=1` arm with `rollout_steps=32` and call it long-horizon; the buffer still cuts direct credit.
6. Do not start a joint fine-tune from I@1000 merely because it scored `10/48`; that result is within the scout panel's noise and the plan-only recipe did not replicate yet.

## Final diagnosis in one sentence

**The clone is a useful skill that current PPO treats as disposable initialization; successful training requires protecting that skill, moving strategic decisions to their natural commitment timescale, and attaching them to completed outcomes through a critic that cannot rewrite policy features.**

No trainer, checkpoint, run, YT operation, dataset, platform, ladder, leaderboard or Arena state was changed by this document.
