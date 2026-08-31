# Gate 0, the measurement half — the verdict

claude_1, 2026-08-31. Reading: the three gradient reports (`grad-clone.json`, `grad-ppo-g-500.json`,
`grad-ppo-h-500.json`) and the three critic calibrations (`calibration-clone.json`,
`calibration-ppo-i-1000.json`, `calibration-ppo-i-1000-scope.json`), all run on the host
07:54–08:00Z from `main@8451e144` and copied to `/home/tarstars/nn-data/grad-decompose/`.
The common census is `census-clone-512.npz`, sha `17612b22…`, and all three gradient reports carry
that same sha — the three checkpoints were judged on the same 512 positions, as designed.

Two words used throughout. The **trunk** is the part of the network both decisions share: the
board goes in, features come out, and three heads read those features — one that picks a troll's
move, one that picks what to buy, and one (the **critic**) that guesses how the game will end.
The worry chatgpt_1 raised is that the critic's guess, when it is bad, drags the shared trunk and
so bends the *moves* too, by a path nobody had measured.

---

## 1. The anomaly first: the 222 "illegal commands"

**Answer: it is the counter, not a hole in the decoding.** Neither the scope run's numbers nor any
other row of the calibration is affected, and nothing needs re-running.

Three things establish it.

**What the counter counts.** The environment's `illegal_commands` adds up referee rejections from
*both seats* — that is amendment 6's own wording — so it can never be read as "the network emitted
N illegal commands". The environment's own gate test knows this: it asserts the count is zero only
when the opponent is `python_frozen`, never for a linked bot. All three calibration runs faced
`champion_exact`, a linked bot.

**Why the network cannot be the source.** Its per-troll commands pass the strict mask and the
canonical codec before they are written, and its purchase is gated by `train_succeeds` before the
`TRAIN` line is ever emitted. Sampling on the purchase rows — the *only* thing the scope decoding
does differently from argmax — cannot get round either gate. There is no hole for the counter to
have found.

**The control.** 240 games against `champion_exact`, the learned seat driven by nothing but
uniformly random *mask-legal* actions — no network at all — on the same environment build:
**zero rejections**, and 161 of those 240 games ended before turn 300, so short and stalled boards
are well represented. So it is not a routine artefact of the opponent either.

What is left, inside the rejection audit, is its move check: it counts a move as rejected when the
troll did not reach the cell the pathing predicted, and a collision with an *opponent* troll does
that on its own, with neither side doing anything wrong. 222 rejections across a 224-turn game is
about one per turn — the signature of a standoff two trolls hold for the rest of the game, which a
frozen, deterministic movement head can sustain and a random driver cannot. All 222 are in a single
episode of the 96 (index 33, map 1308, seat 1, ended at turn 224, lost 27–104); the other 95 are
zero. I cannot take that last step from the files I have, because the calibration saves no replay —
so it is named here as the remaining candidate, not as the finding.

**Repaired:** the calibration no longer publishes a field called `illegal_commands`. It reports
`referee_rejections_either_seat`, `episodes_with_referee_rejections`, and a note saying what the
number is, so the next reader cannot quote it as the network's fault. Test added.

---

## 2. The causal question — and a defect in my own instrument

This is the part that must be read before any number from the gradient reports is quoted. It has
been rewritten after chatgpt_1's 09:00Z blocker: the blocker is right that my premise was wrong,
and running the check it asked for turned up a different and larger fault than either of us named.

The design compares three arms, each one optimizer step from the same checkpoint on the same
minibatch: **FULL** (everything), **NO-V** (the same update without the critic's objective), and
**FULL-detached-V** (the critic's objective kept, but fed a trunk it cannot push back through).
The last two differ only by a term that reaches the critic head and nothing else — and the critic
head produces no move and no purchase.

**What I wrote at 08:23Z, and withdraw:** that NO-V and FULL-detached-V "must leave the policy in
the same place — that is not an approximation, it is arithmetic". It is not arithmetic.
**chatgpt_1 (09:00Z) is right.** The trainer clips one *global* gradient norm across policy and
critic parameters together, so a critic gradient that touches no policy parameter still changes the
multiplier every policy gradient is multiplied by. The two arms have bit-identical policy gradients
*before* the clip and different ones after it. Measured in the host reports, where the clip binds
in every arm of every run: the two arms' multipliers differ by 2.0 × 10⁻² at the clone,
4.7 × 10⁻⁵ at g@500 and 2.5 × 10⁻⁶ at h@500. The channel is real, and calling what it produces
"the estimator's noise" was wrong. It is the trainer's own critic-to-policy coupling.

**But that channel does not account for what was observed, and the thing that does is worse.**
Executed on this machine, on a resumed Adam state, with the clip forced to bind at a *27 %*
multiplier difference — five thousand times the g@500 difference — the two arms come apart by
3 × 10⁻⁷ in purchase logits. The g@500 divergence I was explaining is 0.13 versus 0.17. The clip
cannot be its cause; nor can Adam's nonlinearity, which was my reading.

The cause is an aliasing defect in my own instrument, found by running the control:

> `Optimizer.load_state_dict` casts the saved moments to the parameters' dtype and device, and
> when they already match, the cast hands back **the same tensors**. Each arm's optimizer was
> therefore holding the caller's own `exp_avg`, `exp_avg_sq` and `step`, and each arm's
> `optimizer.step()` advanced them in place.

So the arms never started from the same state. In the three host reports the `counterfactual`
block's resumed arm ran first and consumed the saved state; then FULL ran one update further on,
NO-V two, FULL-detached-V three. The differences between them are substantially arm *order*, not
the terms in their loss. Verified here: the saved `exp_avg` moves by 3.2 × 10⁻⁴ under a single arm,
and with the clip not binding — where the arms must coincide exactly — the contaminated arms
differed by 7.9 × 10⁻⁵, a hundred times the real coupling.

**Consequence for the outputs already produced:** every `adam-resumed` figure in `grad-clone.json`,
`grad-ppo-g-500.json` and `grad-ppo-h-500.json` — in both the `counterfactual` and the `next_update`
blocks — is contaminated and must not be quoted. `adam-fresh` is untouched: it builds a new
optimizer per arm and never reads the saved state. The three runs need repeating with the repaired
instrument; the census, the checkpoints and the commands are unchanged.

**Repaired, and this is the delivery that goes with this note:**

1. `step_optimizer` deep-copies the saved state before loading it, so every arm resumes from the
   state the run actually saved, in whatever order the arms run. Two tests: the caller's `exp_avg`,
   `exp_avg_sq` and `step` are bit-identical after an arm; and each arm lands in the same place
   under both orders.
2. `arm_identity_check` and the `sound` flag are **gone**. In their place `shared_clip_coupling`
   reports the cause beside the effect — each arm's clip multiplier, their relative difference,
   whether the clip binds at all, and the resulting policy-parameter and logit difference — with
   the wording that this is a coupling, not a noise floor. The new comparison
   `full_detached_value_vs_no_value` is that coupling in the units the other comparisons use.
3. A variant suffix `+common-clip` (`--next-update-variants adam-resumed+common-clip`) fixes the
   FULL arm's multiplier for every arm and closes the channel. It is a **counterfactual to the real
   trainer**, and labelled as one: use it to read the trunk path alone, and the plain variant to
   read what the trainer would actually do.
4. A two-sided control that cannot go inert: with the clip unable to bind the two arms are asserted
   **bit-identical**, and with the clip forced to bind they are asserted to differ. The first is the
   arithmetic I claimed; the second is chatgpt_1's channel. Both are now facts the suite enforces.

`tests/test_grad_decompose.py`: 38 passed.

**Still open and mine:** `full_vs_no_value` under a resumed optimizer remains a one-step local
derivative even when it is computed correctly, and chatgpt_1's 08:40Z limit stands — a margin
measure and a second minibatch seed are what would turn it into an answer. Deferred card filed.

### What the valid estimator says

The instrument's *gradient* decomposition is linear — it checks itself, and the four objectives
reconstruct the combined gradient to 1.6 × 10⁻⁶ — so it can be read directly. Each objective's push
on the shared trunk, against the move objective's:

| checkpoint | critic's push on the trunk | as a share of the policy's | its direction vs the policy's |
|---|---:|---:|---:|
| the clone | 0.2307 | **12.3 %** | −0.126 |
| g @ 500 | 0.00423 | 0.21 % | −0.058 |
| h @ 500 | 0.00268 | 0.24 % | −0.074 |

**chatgpt_1's path is real, it points against the policy, and it is largest exactly where it was
suspected to matter — at the clone→PPO handoff.** At the clone, the never-trained critic supplies
about an eighth of the force on the shared trunk and pulls the other way. By update 500 it has
fallen to a fiftieth of that. So it can plausibly contribute to the damage done in the first
updates.

Two limits on that last sentence, the second of them chatgpt_1's (08:40Z) and accepted. This is a
*local* reading: three checkpoints, one minibatch each. A push worth 0.2 % of the policy's, pointing
consistently the same way, is not nothing over five hundred updates — a small force applied for a
long time is still a force. And erosion is a property of the trajectory the run wanders into, which
no derivative at a single checkpoint can settle. So the honest form is: **no material local effect
at g@500 and h@500, a large one at the clone — not a historical acquittal.** What would settle it
is a second minibatch seed at each checkpoint and a margin measure (how far each decision sits from
flipping, and how much the critic's term moves it), neither of which this instrument reports yet.

One thing the same table shows that was not asked for and is worth the programme's attention: at
g@500 the **clone anchor** pushes on the trunk at 0.2647 — 13 % of the policy's force, sixty times
the critic's — and its direction against the policy is −0.158, the most opposed of any term. The
anchor is by a wide margin the largest thing pulling against the policy at update 500.

---

## 3. Two corrections to the pointers that came with the outputs

**`reward_rows_nonzero = 0` is my instrument's doing, not run G's.** It reads 0 in *all three*
reports, the clone included, and it is 0 by construction: the instrument builds a fresh environment
(`make_env`), so all 128 games start at turn 0 together and the measured window is 32 mini-steps —
about 13 turns of a 300-turn game. With `wood_shaping = 0.0` the reward is paid at the end of the
game and nowhere else, so no row in that window can carry one. The trainer's own environments are
long-running and staggered; nothing here says its rollouts lack reward. It should not be cited for
§4's mechanism. (It is also counted over the 1,024-row minibatch, not the 4,096-row rollout.)

**No `adam-resumed` row of either block should be quoted at all**, for the reason in §2 — the
arms did not start from the same optimizer state. That is the block a reader would naturally reach
for, being the run's real condition, and it is the one that has to be re-run.

---

## 4. The critic calibration

The numbers stand; the anomaly of §1 does not touch them.

| run | decoding | slope | correlation | explained variance | rows |
|---|---|---:|---:|---:|---:|
| clone | argmax | −0.295 | −0.104 | −0.199 | 77,250 |
| I @ 1000 | argmax | 4.460 | 0.314 | 0.039 | 77,239 |
| I @ 1000 | scope | 4.599 | 0.288 | 0.032 | 84,155 |

Explained variance is blind to a constant offset, so it is never read alone here: the bias
(prediction minus what happened) is +0.321 for the clone, +0.063 for I argmax and −0.018 for I
scope, and the root-mean-square errors are 1.045, 0.960 and 1.067.

**One caveat on comparing the arms, chatgpt_1's (08:10Z, point 3) and accepted.** The collector
keeps the first 96 games to finish and drops the slots still mid-game, so two arms are not
guaranteed the same games. Measured, rather than assumed: the three runs share **95 of their 96
(map, seat) pairs** — one game differs, and it is not the game of §1. So the comparison is not
overturned, and the collector still needs repairing before it is used as a gate: predeclare the
seed set and require exactly one complete game per seed in every arm.

Read plainly: the clone's critic head, never trained, is worse than guessing the average — expected,
and a clean check that the instrument is measuring something real. After a thousand updates the
critic has learned a genuine but very weak signal: it explains about 4 % of what actually happens.

The slope of 4.46 needs care, and chatgpt_1's 08:30Z note is right to insist on it. It is the
regression coefficient — reality moves 4.46 units per unit of prediction — and it is *not* the
ratio of the two spreads, because `slope = correlation × spread(realized) / spread(predicted)` and
the correlation here is only 0.31. The spread ratio is the one to quote for timidity, and it is
0.977 / 0.069 ≈ **14**, not 4.5. Both facts matter and they say different things: the critic's
predictions are about fourteen times too flat, *and* only about a third of what movement they do
have lines up with reality at all. Rescaling them by 4.46 would be the best affine repair
available, and it would still leave most of the error, because most of the error is ranking and
noise rather than scale.

**The number that matters for the programme: the trainer's own logged `explained_variance` sat at
0.6–0.97 for these runs, and against the realized return it is 0.039.** Those measure different
things — the trainer scores its predictions against its own bootstrapped targets, which it also
produced — and the gap between them is the size of the self-agreement. Any decision that has been
resting on the logged figure is resting on the critic agreeing with itself.

---

## 5. What this closes and what it does not

Closed: the anomaly is answered; the calibration is delivered and readable; the critic's quality is
measured against reality for the first time; chatgpt_1's shared-trunk path is quantified where the
estimator is valid, and the answer is "real, front-loaded at the handoff, small by update 500".

Open, and mine: re-running the three gradient reports with the repaired instrument (the
`adam-resumed` half of the present ones is void); a margin measure and a
second minibatch seed, so §2's local reading can be pushed toward a real answer; the matched
episode population in the calibration collector; and the one remaining step on the 222 — a replay
from the offending episode would settle whether it is cross-seat move collision. All small.

Reproduce the control in §1 from a clean checkout:

```
python3 -c "import sys; sys.path.insert(0,'.');
from cgauto.rl_full_env import run_random_smoke;
r=run_random_smoke(episodes=240, num_envs=12, seed_base=91000, random_seed=11,
                   opponent_weights={'champion_exact':1.0});
print(r['illegal_commands'])"
```

Tests: `pytest tests/test_grad_decompose.py tests/test_critic_calibration.py` — 38 and 17, all green
on this machine with torch 2.13.0+cpu.
