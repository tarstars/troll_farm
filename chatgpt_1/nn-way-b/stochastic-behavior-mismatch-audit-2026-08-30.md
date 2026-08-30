# PPO stochastic-behaviour versus deployment-policy audit

Date: 2026-08-30
Agent: `chatgpt_1`
Programme: `20260829-nn-bot-way-b`
Reviewed main: `e02e88c8afadc31dc16109ed85eb3c547913943e`
Revision: r2 — incorporates the retained plan-sampling control and the spatial action multiplicity

## Verdict

Every Phase-3 run so far shares one untested mismatch:

```text
selection/deployment policy = masked argmax
PPO behaviour policy        = temperature-1 categorical sampling
```

The project has already measured that these are not equivalent for the clone:

```text
argmax plan + argmax commands:   9/48, 133.8 points
sampled plan + argmax commands:  8/48, 133.2 points
fully sampled play:              3/48, about 109 points
```

The retained `bench-sample.json` and its README explicitly say that only the plan head was sampled in the 8/48 control and “it changes nothing.” The later fully sampled result is much worse. This localises most of the observed deployment/behaviour gap to **troll-command sampling**, or to its interaction with plan sampling. The missing decisive arm is argmax plan + sampled commands.

The eroded `ppo-f2` snapshot fell to 0/48 under sampled play. Therefore PPO does not begin by collecting trajectories from the 9/48 clone the project intends to improve. It begins from a substantially weaker stochastic policy with the same weights.

This does not prove that sampling or entropy causes the later argmax erosion. It does make it the first common variable that must be isolated before opponent mix, gamma, or curriculum is treated as the remaining explanation.

## Exact implementation join

### Trainer

`local_claude_1/nn-bot/train_ppo_full.py` collects every learner action with:

```python
distribution = Categorical(logits=masked_logits(logits, legal_t))
actions = distribution.sample()
```

The same untempered distribution is reconstructed for PPO log-probabilities. The default entropy coefficient is `0.01`.

### Bench

`local_claude_1/nn-bot/bench.py::NetworkPolicy._sample` divides logits by `temperature`, masks illegal actions and samples the resulting softmax. The default is `temperature = 1.0`. Its documentation explicitly says sampled command decoding is “the way the PPO trainer plays them.” Plan and command sampling can be switched independently.

### Deployment/export

The bench's gate of record and the generated Rust bot use masked argmax. Positive logit scaling would not change this deployed action choice.

## Why troll-command sampling is especially broad

The spatial head is one flat categorical distribution over `13 × 11 × 22 = 3,146` entries.

For a TROLL row:

- every reachable walkable cell can contribute a legal MOVE entry;
- a large connected map can therefore expose tens or hundreds of MOVE alternatives;
- legal non-MOVE verbs exist only at the active troll's current cell;
- behaviour cloning reports only 41% exact MOVE-cell accuracy, versus 80–97% for many non-MOVE verbs.

A softmax draw is affected by **total probability mass**, not only the best logit. Even when the best single action is useful, a large collection of individually lower MOVE logits can hold most of the probability mass. Temperature-1 sampling can then choose a poor destination frequently while argmax remains stable.

This is an action-representation/exploration interaction, not merely generic “PPO noise.” A fixed entropy coefficient also has phase- and state-dependent meaning because maximum entropy grows with the number of legal actions.

## Why critic warm-up does not close the mismatch

During critic warm-up the actor parameters are frozen, but rollouts still call `distribution.sample()`.

Thus the value head learns the return of the 3/48-like stochastic behaviour, not the value of the 9/48 argmax policy. When actor updates begin, PPO improves the sampled policy it actually executed. There is no guarantee that this also improves the mode used at deployment.

At the exact clone the anchor KL is zero. The entropy term has a nonzero gradient toward a flatter distribution. This makes the early update geometry worth measuring, but is not yet proof that entropy dominates the PPO gradient.

## Cheapest decisive diagnostics

All of these are read-only benches or offline tensor calculations.

### 1. Complete the decoding matrix

The existing evidence is:

| arm | plan | troll commands | result |
|---|---|---|---|
| AA | argmax | argmax | 9/48, 133.8 |
| SA | sample at T=1 | argmax | 8/48, 133.2 |
| AS | argmax | sample at T=1 | **missing** |
| SS | sample at T=1 | sample at T=1 | 3/48, about 109 |

Run only the missing AS arm first, on the same maps, seats and game seeds. If AS already reproduces most of the 3/48 loss, plan sampling is discharged and the next work belongs entirely to the spatial behaviour policy.

Report wins, scores, endings, loops, purchases and fruit-chain command counts.

### 2. Confidence and probability-mass census

For PLAN and TROLL rows separately, report:

- legal-action count;
- legal MOVE count versus legal non-MOVE count;
- top-1 probability;
- top-2 margin in logits and probability;
- entropy and `entropy / log(legal_count)`;
- probability mass on all MOVE entries versus all non-MOVE entries;
- probability mass outside top 1 and top 5;
- sampled-versus-argmax disagreement;
- TROLL split by selected argmax verb (`MOVE`, `PICK`, `PLANT`, `HARVEST`, `DROP`, `CHOP`, other).

For MOVE argmax rows, additionally report the sampled destination's distance from the argmax destination and whether it changes the semantic target class.

### 3. Diagnostic temperature sweep

Without training, run the AS arm at fixed temperatures such as `1.0`, `0.5`, and `0.25`. This is diagnostic, not checkpoint selection. A positive temperature scale preserves every argmax action, so it asks only how much sharpening is required for sampled behaviour to resemble the deployment policy.

### 4. Gradient decomposition

On one saved post-warm-up minibatch, measure policy-parameter gradient norms and pairwise cosine similarities for:

- clipped PPO policy loss;
- entropy bonus;
- anchor KL;
- PLAN versus TROLL rows;
- fruit-chain rows versus the rest.

At step zero also verify numerically that anchor KL gradient is zero and entropy gradient is not. Report the entropy contribution by legal-action-count bucket, because a fixed coefficient is not a fixed exploration pressure across masks.

## Controlled next run, only if diagnostics support it

Add a recorded `--policy-temperature` used consistently in:

- rollout sampling;
- update-time policy log-probabilities and entropy;
- anchor distributions and KL;
- any sampled frozen-policy path intended to match the learner.

Apply temperature before legal masking. Checkpoint config must record it. Add tests that old/new log-probabilities use the same temperature and that positive scaling leaves argmax actions unchanged.

Choose the temperature by a frozen rule before the run, preferably from held-out clone logits or the decoding diagnostic, not by repeatedly selecting on the champion gate. Then compare against the current recipe with the same seed and every other flag identical.

Entropy is a separate factor. If it remains suspect after gradient decomposition, test `entropy_coef = 0` as its own matched-seed arm rather than changing temperature and entropy together.

A longer-term representation fix could sample a verb and a MOVE destination hierarchically, but that changes the policy architecture and is not the first control.

## Recommendation

```text
DO NOT call the current stochastic rollout policy “the 9/48 clone.”
RUN the missing argmax-plan / sampled-command arm first.
MEASURE MOVE probability mass and legal-action multiplicity.
TREAT command-sampling temperature and entropy as untested common factors across all eroding runs.
CHANGE one of them at a time, with a matched seed, only after the offline diagnostics.
```

No trainer, checkpoint, environment, dataset, YT operation, platform, or Arena state was changed by this audit.
