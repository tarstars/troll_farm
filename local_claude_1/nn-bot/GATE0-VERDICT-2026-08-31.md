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

This is the part that must be read before any number from the gradient reports is quoted.

The design compares three arms, each one optimizer step from the same checkpoint on the same
minibatch: **FULL** (everything), **NO-V** (the same update without the critic's objective), and
**FULL-detached-V** (the critic's objective kept, but fed a trunk it cannot push back through).
The last two differ only by a term that reaches the critic head and nothing else — and the critic
head produces no move and no purchase. **So NO-V and FULL-detached-V must leave the policy in the
same place.** That is not an approximation; it is arithmetic.

Under `adam-fresh` they do, to four decimals, in all three reports. **Under `adam-resumed` they do
not.** In `grad-ppo-g-500.json` the two arms that must agree move the purchase logits by 0.1344 and
0.1735 and flip 8 and 12 of 190 purchase choices — while the whole effect being claimed, FULL
against FULL-detached-V, is 0.0906. **The noise is larger than the signal.**

I reproduced it in the test harness and found the mechanism. Adam's step is
`learning-rate × m̂ / (√v̂ + ε)` — a *nonlinear* function of the gradient. Removing the critic's term
changes the gradient by about one part in 10⁵ (the three arms' gradient norms are 2.173309,
2.173385, 2.173283). On parameters whose accumulated second moment `v̂` is small — the purchase
head's, whose mean `v̂` is around 10⁻¹² after a real run — that one-part-in-10⁵ change does not
produce a one-part-in-10⁵ change in the step. It produces the differences above.

So **neither Adam variant answers the causal question**:

* `adam-resumed` is contaminated by an artefact the same size as the effect;
* `adam-fresh` is clean, but a *first* Adam step is exactly `learning-rate × sign(gradient)` — it
  is blind to gradient magnitude by construction, so it registers only changes big enough to flip
  a sign, and understates everything else. Its near-zero readings (the critic path accounts for
  0.2 % of the purchase-logit motion at g@500 and flips nothing) are a floor, not an estimate.

**Repaired:** the instrument now runs that control on itself and publishes it. Every variant of the
next-update block carries `arm_identity_check` — the two arms' largest policy-parameter difference,
and the same difference expressed in the units the comparisons are quoted in — and a `sound` flag
that is the check's verdict. A reader can now put the noise floor beside the effect. Three tests,
including a negative control that constructs the failing state and asserts the check catches it, so
the check cannot quietly go inert.

**Not repaired, and deferred:** a next-update estimator that is actually valid under the run's own
optimizer. The obvious candidate is a plain-gradient-descent arm, which is linear in the gradient
and so preserves the identity exactly; it needs to be added and validated on a host with the real
checkpoints. Deferred card filed.

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
updates, and it cannot explain erosion that is still going on at update 500 and beyond.

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

**The `adam-resumed` rows of the causal block should not be quoted at all**, for the reason in §2.
That is the block a reader would naturally reach for, being the run's real condition.

---

## 4. The critic calibration

The numbers stand; the anomaly of §1 does not touch them.

| run | decoding | slope | correlation | explained variance | rows |
|---|---|---:|---:|---:|---:|
| clone | argmax | −0.295 | −0.104 | −0.199 | 77,250 |
| I @ 1000 | argmax | 4.460 | 0.314 | 0.039 | 77,239 |
| I @ 1000 | scope | 4.599 | 0.288 | 0.032 | 84,155 |

Read plainly: the clone's critic head, never trained, is worse than guessing the average — expected,
and a clean check that the instrument is measuring something real. After a thousand updates the
critic has learned a genuine but very weak signal: it explains about 4 % of what actually happens,
and its predictions vary about four and a half times *less* than reality (the slope of 4.46 is how
much reality moves per unit of prediction). Its spread is 0.069 against reality's 0.977.

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

Open, and mine: a next-update estimator valid under a resumed optimizer (deferred card), and the
one remaining step on the 222 — a replay from the offending episode would settle whether it is
cross-seat move collision. Both are small.

Reproduce the control in §1 from a clean checkout:

```
python3 -c "import sys; sys.path.insert(0,'.');
from cgauto.rl_full_env import run_random_smoke;
r=run_random_smoke(episodes=240, num_envs=12, seed_base=91000, random_seed=11,
                   opponent_weights={'champion_exact':1.0});
print(r['illegal_commands'])"
```

Tests: `pytest tests/test_grad_decompose.py tests/test_critic_calibration.py` — 35 and 17, all green
on this machine with torch 2.13.0+cpu.
