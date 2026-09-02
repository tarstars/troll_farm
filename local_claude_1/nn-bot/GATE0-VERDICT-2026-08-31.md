# Gate 0, the measurement half — the verdict

claude_1, 2026-08-31, final form.

## What this reads, and how to check that it read the right thing

**The numbers of record are the v3 gradient set and the v2 calibrations.** Everything earlier is
superseded: the first (07:5xZ) gradient set is void in its `adam-resumed` half for the reason in
§2, and every `fraction_margin_crossed` printed before r5 is void for the reason in §7. Nothing
from those files is quoted here.

**The four gradient reports** are `grad-clone-v3.json`, `grad-ppo-g-250-v3.json`,
`grad-ppo-g-500-v3.json` and `grad-ppo-h-500-v3.json` in `/home/tarstars/nn-data/grad-decompose/`,
written 2026-08-31 12:08Z by the coordinator on the host.

* All four carry the same census, `census-clone-512-v2.npz`, sha `a5e14b65b62b…` — 512 positions
  (206 plan rows, 306 troll rows) drawn from 126 environments over 32 rollout steps. The four
  checkpoints were judged on the same board positions, as designed.
* All four carry the same instrument: `grad_decompose.py` sha `15017366…` and `train_ppo_full.py`
  sha `8f239a02…`. **I verified both against my own checkout** after merging main: they are
  byte-identical to the merged r5 instrument plus codex_1's final-policy-KL trainer. The set was
  produced by the code that was reviewed, not by an earlier copy.
* Checkpoints: clone `970097ed…`, G@250 `9dd5bd09…`, G@500 `b7247016…`, H@500 `51193624…`.
* The linearity self-check — the four objectives' gradients must re-sum to the combined gradient —
  closes to between 8.0 × 10⁻⁷ and 1.6 × 10⁻⁶ in the four runs. The decomposition is arithmetic,
  not an estimate.

**The three calibrations** are `calibration-clone-v2.json`, `calibration-ppo-i-1000-v2.json` and
`calibration-ppo-i-1000-scope-v2.json`, instrument sha `1597960f…`, each over a **matched**
population: 96 declared `(map, seat)` cells, 0 missing, 0 duplicate, `matched: true`.

Two words used throughout. The **trunk** is the part of the network both decisions share: the board
goes in, features come out, and three heads read those features — one that picks a troll's move,
one that picks what to buy, and one (the **critic**) that guesses how the game will end. The worry
chatgpt_1 raised is that the critic's guess, when it is bad, drags the shared trunk and so bends the
*moves* too, by a path nobody had measured.

---

## 0. The two scope limits this verdict is read under

Both come from chatgpt_1's blockers of 2026-08-31, upheld by the coordinator at 11:30Z and frozen
into the goal. They are conditions on every number below, not caveats appended to it.

* **`EARLY_GAME_LOCAL_ONLY` (the 09:52Z blocker).** Every gradient row here is measured on a
  *fresh-game* population: the instrument builds its own environment, so all 128 games start at
  turn 0 together and the window is 32 mini-steps — about 13 turns of a 300-turn game. The
  trainer's own environments are long-running and staggered. These are therefore early-game local
  counterfactuals, and they decide **nothing** about the historical mid-training trajectory G and H
  actually walked. Measuring a staggered/burned-in population is real environment-and-instrument
  work and is deferred to the post-Gate-0 bundle, not claimed here.
* **The clone row is a hypothetical no-warm-up first update (the 10:13Z blocker).** Run G's
  recorded configuration sets `--critic-warmup-updates 300`: for its first 300 updates every
  policy-side tensor including the shared trunk is bit-frozen and only the critic head moves.
  **G's actual first update therefore has no critic-to-policy trunk path at all, by construction.**
  The clone row is measured with warm-up 0, so it is a *hypothetical no-warm-up first update*:
  path-existence evidence, and nothing more. It is not the force at G's or H's clone→PPO handoff
  and is not offered as an explanation of their early damage.

---

## 1. The answer to Gate 0's causal question

**The path chatgpt_1 named is real, and the warm-up closes it.**

Each objective's push on the shared trunk, as a share of the move-and-buy objective's push, on the
same 512 positions. The row-class split is new in v3: PLAN rows are the purchase decision, TROLL
rows the movement decision.

| checkpoint | all rows | PLAN rows | TROLL rows | direction vs the policy (all rows) |
|---|---:|---:|---:|---:|
| clone, *hypothetical no-warm-up first update* | **16.4 %** | 5.4 % | **29.3 %** | +0.001 |
| G @ 250 — warm-up tail, 50 updates before the unfreeze | 0.37 % | 0.21 % | 0.50 % | −0.083 |
| G @ 500 | 0.22 % | 0.12 % | 0.39 % | −0.058 |
| H @ 500 | 0.24 % | 0.10 % | 0.26 % | −0.074 |

Read plainly: in a first update with no warm-up, the never-trained critic supplies about a sixth of
the total force on the shared trunk, and nearly a third of it on the movement decision. Fifty
updates before G's policy actually unfreezes, that has already fallen to half a percent, and by
update 500 to a fifth of a percent. **The 300-update warm-up is doing real work**, and the run that
skipped it is a counterfactual, not a history.

One consistency check that the instrument passes and is worth naming: at the clone and at G@250 the
**anchor** objective's gradient is ~10⁻⁸ — numerically zero — because during warm-up the policy is
still sitting bit-exactly on the clone weights the anchor pulls toward, so its penalty is exactly
zero. An instrument that reported a live anchor force there would be wrong. It reports none.

### Does the path move any decision?

The gradient share says how hard the critic pushes. It does not say whether anything changes hands.
The next-update counterfactual answers that directly: from each checkpoint, take one optimizer step
on the same minibatch under three arms — **FULL** (everything), **NO-V** (the same update without
the critic's objective), and **FULL-detached-V** (the critic's objective kept but fed a trunk it
cannot push back through) — and compare the decisions afterwards. Run under three optimizer
variants (`adam-resumed`, `adam-fresh`, `adam-resumed+common-clip`) and **two independent minibatch
draws** of the same rollout.

**At G@250, G@500 and H@500 the critic's objective moves nothing.** Across all three checkpoints,
all three optimizer variants and both minibatch seeds — eighteen readings — FULL versus NO-V gives:

* **0 of 206 purchase decisions changed, 0 of 306 movement decisions changed**, every time;
* **0 margin crossings**, every time, and `tied_baseline_rows: 0` — no row was discarded, so the
  denominator is the whole population and the zero is not a zero-by-omission;
* the largest fraction of rows losing even a tenth of their margin is **0.49 %** — a single
  purchase row of 206, at H@500 on the second minibatch — and thirteen of the eighteen readings
  show no such row at all; no row anywhere lost half its margin;
* mean absolute logit shifts of 4 × 10⁻⁵ to 3.6 × 10⁻³ against starting margins of 0.70 to 0.91.

**At the clone it does move decisions.** With no warm-up, FULL versus NO-V on the first minibatch
changes **3 of 206 purchase decisions and 1 of 306 movement decisions**; 8.3 % of purchase rows lose
at least a tenth of their margin, 3.4 % at least a quarter, 1.9 % at least half. On the second
minibatch draw no decision changes hands, but 2.4 % of purchase rows still lose a tenth of their
margin. So the effect at the clone is real, is of the order of one or two decisions per hundred, and
varies with which rows the update happens to draw — which is exactly why the second seed was
required.

*A limit on that clone row, named rather than hidden:* only the `adam-fresh` variant is available at
the clone. Its saved optimizer state has one parameter group where the PPO trainer builds two, so
`adam-resumed` and `adam-resumed+common-clip` report `available: false` with that reason rather than
guessing. The clone's decision-level numbers are therefore fresh-optimizer numbers.

### The clip channel, measured and closed

chatgpt_1's 09:00Z blocker was right that NO-V and FULL-detached-V are not obliged to coincide: the
trainer clips one *global* gradient norm across policy and critic parameters together, so a critic
gradient that touches no policy parameter still changes the multiplier every policy gradient is
multiplied by. Measured in the v3 set, that channel is real and tiny. The two arms' clip multipliers
differ by 3.3 × 10⁻² at the clone, 2.5 × 10⁻⁴ at G@250, 4.7 × 10⁻⁵ at G@500 and 2.5 × 10⁻⁶ at H@500;
what that buys is a logit shift of 6.7 × 10⁻⁵ at the clone and ~2 × 10⁻⁶ elsewhere, **zero decisions
changed and zero margin movement anywhere**. Under `adam-resumed+common-clip`, which fixes one
multiplier for all arms, the two arms come out **exactly 0.0** apart on every field. That is the
two-sided control firing as designed: the channel exists, it is quantified, and closing it makes it
vanish identically rather than approximately.

### The verdict

**Under both scope limits in §0: the critic-to-policy trunk path is not a material influence on the
policy in G and H as they were actually configured.** In the warm-up tail and at update 500 it is
0.1–0.5 % of the policy's trunk force and moves no decision, on two minibatch seeds and three
optimizer variants. It is large — 5 % on purchases, 29 % on movement, and worth a few decisions per
hundred — only in the hypothetical no-warm-up first update, which is not what either run did.

This is a **local** verdict. A push worth 0.2 % of the policy's, pointing consistently the same way,
is not nothing over five hundred updates, and erosion is a property of the trajectory a run wanders
into, which no derivative at a single checkpoint can settle. **It is neither a historical acquittal
nor a historical indictment** — it says the mechanism proposed for the early damage is not visible
where it was proposed to act.

### What *is* large at update 500

The same table shows something that was not asked for and is worth the programme's attention. At
update 500 the **clone anchor** pushes on the trunk at **13.4 % of the policy's force at G and
18.4 % at H**, pointing against the policy (−0.158 and −0.076) — fifty to seventy times the
critic's. The anchor, not the critic, is by a wide margin the largest thing pulling against the
policy at update 500. That is by design; whether the design is right at that coefficient is a
question for Stage 1, not a finding here.

---

## 2. The anomaly: the 222 "illegal commands"

**Answer: it is the counter, not a hole in the decoding.** Nothing needed re-running, and the v2
calibrations confirm it: the two argmax arms report **0** referee rejections, and the 222 sit in a
**single episode** of the scope arm (`episodes_with_referee_rejections: 1`).

Three things establish it.

**What the counter counts.** The environment's `illegal_commands` adds up referee rejections from
*both seats* — amendment 6's own wording — so it can never be read as "the network emitted N illegal
commands". The environment's own gate test knows this: it asserts the count is zero only when the
opponent is `python_frozen`, never for a linked bot. All three calibration runs faced
`champion_exact`, a linked bot.

**Why the network cannot be the source.** Its per-troll commands pass the strict mask and the
canonical codec before they are written, and its purchase is gated by `train_succeeds` before the
`TRAIN` line is ever emitted. Sampling on the purchase rows — the only thing the scope decoding does
differently from argmax — cannot get round either gate.

**The control.** 240 games against `champion_exact` with the learned seat driven by nothing but
uniformly random *mask-legal* actions — no network at all — on the same environment build: **zero
rejections**, with 161 of the 240 games ending before turn 300, so short and stalled boards are well
represented. It is not a routine artefact of the opponent either.

What is left, inside the rejection audit, is its move check: it counts a move as rejected when the
troll did not reach the cell the pathing predicted, and a collision with an *opponent* troll does
that on its own, with neither side doing anything wrong. 222 rejections across a 224-turn game is
about one per turn — the signature of a standoff two trolls hold for the rest of the game, which a
frozen deterministic movement head can sustain and a random driver cannot. I cannot take the last
step from these files, because the calibration saves no replay, so it is named as the remaining
candidate rather than as the finding.

**Repaired:** the calibration no longer publishes a field called `illegal_commands`. It reports
`referee_rejections_either_seat`, `episodes_with_referee_rejections` and a note saying what the
number is, so the next reader cannot quote it as the network's fault. Test added.

---

## 3. What the critic actually knows

The v2 calibrations, over the matched population, against the **complete-episode Monte-Carlo return
under each run's own discount** — not the truncated λ=0.95 GAE target with a rollout-edge bootstrap
that the trainer fitted. The two are read beside each other, never one in place of the other.

| run | decoding | slope | correlation | explained variance | bias | RMSE | rows |
|---|---|---:|---:|---:|---:|---:|---:|
| clone | argmax | −0.295 | −0.104 | −0.199 | +0.321 | 1.045 | 77,250 |
| I @ 1000 | argmax | 4.324 | 0.299 | 0.037 | +0.050 | 0.950 | 76,771 |
| I @ 1000 | scope | 4.555 | 0.284 | 0.032 | −0.029 | 1.073 | 84,227 |

Explained variance is blind to a constant offset, so it is never read alone: the bias column is
prediction minus what happened.

Read plainly: the clone's critic head, never trained, is **worse than guessing the average** —
expected, and a clean check that the instrument measures something real. After a thousand updates
the critic has learned a genuine but very weak signal: it explains about **4 %** of what actually
happens.

**The slope needs care**, and chatgpt_1's 08:30Z note is right to insist on it. 4.32 is the
regression coefficient — reality moves 4.32 units per unit of prediction — and it is *not* the ratio
of the two spreads, because `slope = correlation × spread(realized) / spread(predicted)` and the
correlation is only 0.30. The spread ratio is the one to quote for timidity: 0.967 / 0.0669 ≈ **14**
for the argmax arm and ≈ 16 for the scope arm. Both facts matter and they say different things: the
critic's predictions are about fourteen times too flat, *and* only about a third of what movement
they do have lines up with reality at all. Rescaling by 4.3 would be the best affine repair
available and would still leave most of the error, because most of the error is ranking and noise
rather than scale.

**The number that matters for the programme: the trainer's own logged `explained_variance` sat at
0.6–0.97 for these runs, and against the realized return it is 0.037.** Those measure different
things — the trainer scores its predictions against its own bootstrapped targets, which it also
produced — and the gap between them is the size of the self-agreement. Any decision resting on the
logged figure is resting on the critic agreeing with itself.

**Where the signal is, by game turn** (I @ 1000, argmax) — new in v2, and it matters for §0:

| turns | 0–9 | 10–24 | 25–49 | 50–99 | 100–149 | 150–199 | 200–299 |
|---|---:|---:|---:|---:|---:|---:|---:|
| explained variance | −0.004 | −0.003 | 0.006 | 0.018 | 0.033 | 0.040 | 0.050 |
| correlation | −0.071 | −0.050 | 0.118 | 0.260 | 0.353 | 0.357 | 0.401 |

**The critic knows nothing in the first twenty-five turns and acquires its weak signal late.** This
cuts directly across `EARLY_GAME_LOCAL_ONLY`: the gradient window of §1 is about thirteen turns of a
three-hundred-turn game, which is precisely where the critic's predictions carry no signal at all.
Whether that makes §1's trunk push an *under*-statement (a well-informed late-game critic pushes
harder) or an *over*-statement (an uninformed critic produces large, meaningless errors and so large
gradients) **cannot be settled from these files**, and it is the sharpest reason the staggered
population is worth measuring. It is stated here as an open question, not resolved in either
direction.

Two further slices: seat 1 is better predicted than seat 0 (EV 0.046 vs 0.022), and purchase and
movement rows are alike (0.041 vs 0.034). Weighting one plan row per turn instead of every mini-step
changes nothing material (0.041 vs 0.037); the ninety-six per-game initial predictions carry
essentially no signal (EV 0.004).

**The collector's population is now matched, which it was not in v1.** All three arms are restricted
to the same 96 declared `(map, seat)` cells, with 0 missing and 0 duplicates; the PPO arms requested
160 games and dropped 64 to hold the match. The v1 caveat that two arms were not guaranteed the same
games is discharged, not merely bounded.

*Independent of the above, and reported for honesty:* on the instrument's own fresh early-game
rollout the critic's explained variance **against its own GAE targets** is 0.22 at G@250, 0.21 at
G@500, −0.01 at H@500 and −1.18 at the clone. Even by its own yardstick it is weak on a fresh
population, and H's is no better than the mean.

---

## 4. The two instrument defects found on the way, and what they cost

This section is the record of how the numbers above became trustworthy. Both defects were mine.

**The optimizer-aliasing defect (found 08-31, mine, self-inflicted).** My original arm comparison
withdrew a claim I had made — that NO-V and FULL-detached-V "must leave the policy in the same
place, that is not an approximation, it is arithmetic". chatgpt_1's 09:00Z blocker is right that the
shared clip breaks that. But running the control the blocker asked for turned up something larger:

> `Optimizer.load_state_dict` casts the saved moments to the parameters' dtype and device, and when
> they already match, the cast hands back **the same tensors**. Each arm's optimizer was therefore
> holding the caller's own `exp_avg`, `exp_avg_sq` and `step`, and each arm's `optimizer.step()`
> advanced them in place.

The arms never started from the same state: the resumed arm ran first and consumed the saved state,
then FULL ran one update further on, NO-V two, FULL-detached-V three. **Every `adam-resumed` figure
in the first (07:5xZ) gradient set is contaminated and must not be quoted** — which is why the set
was re-run, and why this verdict reads only v3. `step_optimizer` now deep-copies the saved state
before loading it; two tests hold the caller's moments bit-identical after an arm and land each arm
in the same place under both orders. The `arm_identity_check`/`sound` flag pair is gone, replaced by
`shared_clip_coupling`, which reports the cause beside the effect, and by a two-sided control that
cannot go inert: with the clip unable to bind the arms are asserted **bit-identical**, and with it
forced to bind they are asserted to **differ**.

**The margin statistic, twice wrong (r4 and r5).** r3's margin measure had two defects, both found
by chatgpt_1 in closed form, both now falsifiers in the suite.

*r4 — the crossing falsifier (09:41Z).* The post-update margin was computed by re-sorting the new
logits and taking `top1 − top2`, which measures the confidence of whoever won *afterwards*: it is
non-negative by construction, can never register a crossing, and reads a flip to a confident new
winner as the margin *growing*. `[2, 1] → [0, 3]` — a decision changing hands — was reported as +3.
The margin is now held against the row's **original** winner, so it is signed and goes negative
exactly when the decision changes hands; that case now reads −3. A cross-check assertion makes the
two views unable to disagree silently: if any row's argmax changed while its signed margin stayed
positive, the instrument **stops** rather than reporting a number.

*r5 — the tie denominator (10:04Z).* With the signed margin in place, a row whose baseline margin
was exactly **zero** satisfied `end <= 0` for free: already on the boundary before the update, and
counting it made an unchanged tie look like an update-caused crossing. chatgpt_1's no-op falsifier,
now a test: rows `[2,1] → [2,1]` and `[1,1] → [1,1]`, nothing moved, no argmax changed — and r4
reported `fraction_margin_crossed = 0.5`. The margin population is now `rows & (start > 0)`, shared
by every margin statistic alike, with the discarded rows kept visible as **`tied_baseline_rows`**.
A class of nothing but ties returns `null`. The flip cross-check deliberately keeps running over
*every* row with a margin, ties included. Three of the four new tests fail against r4 and pass
against r5.

**What that cost:** every `fraction_margin_crossed` printed before r5 is void, and the whole
gradient set was re-run — the same rollout geometry, the same census file, no new training, minutes
of host time. In the v3 set `tied_baseline_rows` is **0** in every row class of every comparison, so
the r5 repair discards nothing here; it is a guard that happened not to bind on this data, which is
worth knowing and is why the field is published rather than assumed.

Two further repairs that the numbers above rest on: `--minibatch-seeds` re-runs the whole next-update
counterfactual on a differently shuffled minibatch of the *same* rollout (a conclusion that only
holds for the rows one update happened to draw is not a conclusion), and `--cells-out` /
`--restrict-to-cells` make the calibration population matched, with a declared cell that never comes
up **failing** the run instead of quietly shrinking the sample.

One correction to a pointer that came with the original outputs, still worth carrying:
**`reward_rows_nonzero = 0` is my instrument's doing, not run G's.** It reads 0 in all four v3
reports, the clone included, and it is 0 by construction: the instrument builds a fresh environment,
so all 128 games start at turn 0 and the window is about 13 turns; with `wood_shaping = 0.0` the
reward is paid at the end of the game and nowhere else, so no row in that window can carry one. The
trainer's own environments are long-running and staggered; nothing here says its rollouts lack
reward. It is also counted over the 1,024-row minibatch, not the 4,096-row rollout.

---

## 5. What this closes, and what it does not

**Closed.** The anomaly is answered and the counter repaired. The calibration is delivered over a
matched population and readable. The critic's quality is measured against reality for the first
time, and against game turn. chatgpt_1's shared-trunk path is quantified with a valid estimator, at
the decision level as well as the gradient level, on two minibatch seeds and three optimizer
variants, with the clip channel measured and closed — and the answer is the verdict in §1.
**This closes Gate 0's measurement half.**

**Open, and named.**

* The staggered/burned-in population that would lift `EARLY_GAME_LOCAL_ONLY`. This is environment
  and instrument work, deferred to the post-Gate-0 bundle. §3's turn slices raise its value: the
  window §1 measures in is the window where the critic knows least.
* The clone's `adam-resumed` arms, unavailable on an optimizer-layout mismatch. A one-group→two-group
  adapter would make the clone row comparable with the others; small, and not needed for the verdict.
* The last step on the 222: a replay from the offending episode would settle whether it is cross-seat
  move collision. The calibration saves no replay.
* The anchor's 13–18 % counter-push at update 500 — surfaced here, owned by Stage 1.

**Reproduce.** The control in §2, from a clean checkout:

```
python3 -c "import sys; sys.path.insert(0,'.');
from cgauto.rl_full_env import run_random_smoke;
r=run_random_smoke(episodes=240, num_envs=12, seed_base=91000, random_seed=11,
                   opponent_weights={'champion_exact':1.0});
print(r['illegal_commands'])"
```

Tests on this machine, torch 2.13.0+cpu, python 3.11.15:
`pytest tests/test_grad_decompose.py tests/test_critic_calibration.py tests/test_train_ppo_full.py`
— 50, 22 and 57 passed, 1 skipped.
