# D41e branch-gap complete-policy selector — frozen protocol (2026-07-21)

## Question and scope

D41d proves that D41c's rank-one proposals have causal continuation value only in the
`evacuation` and `rate` branches. A transparent retrospective discovery audit then identifies a
narrow branch/phase/gap rule with +13.806 mean one-deviation margin, 70.90% positive outcomes, and
positive means in all eight map folds and opponent families.

D41e asks whether applying that exact outcome-blind rule repeatedly as a complete policy improves
fresh terminal performance over D40 without damaging workforce, crops, opponent breadth, or tails.
It authorizes the two preregistered local development stages below, tests, analysis, and written
results. It does not authorize confirmation maps 9,720,000--9,720,031, a deployment candidate,
TestSession, submission, or Arena.

## Frozen inputs and selector

- exact D40 prior kernel SHA-256:
  `632f1b2c99c18073c4cd956863fcaa4b7e9773dd69bb745fc18f062337130f62`;
- D41c seed-411 checkpoint SHA-256:
  `1de76fc5751b2c41d3795d4d15cf3a56155ccdba5dbe69872fa29f890371671a`;
- released rank-aware environment SHA-256:
  `5839a7b888f2772e54a293a66ed5b186df378d5b8514f43a200898c8eef70173`;
- D41e retrospective discovery artifact SHA-256:
  `1d781d1bead197d26aa3ca41e1f86d6ae6ea05f90cf26385e74b8afed47ad4d7`.

At each complete-macro decision, compute the frozen residual gap
`residual(rank one) - residual(rank zero)`. Select exact-prior rank one if and only if either:

1. branch is `evacuation` and the gap is inclusively in **[0.020, 0.030]**; or
2. branch is `rate`, turn is **<100 or >=200**, and the gap is inclusively in
   **[0.280, 0.340]**.

Otherwise select exact D40 rank zero. `train` and `deficit` must have zero disagreements. There is
no learned value model, opponent identity, online outcome, random choice, temperature, threshold
tuning, top-k selection, or stateful budget. Values outside the D41d support caps fall back to D40.

## Fresh banks and execution order

Stage A uses official maps **9,770,000--9,770,063**, both seats, and all eight opponents: 1,024
tasks. Run exact D40 once, random once with NumPy seed 419, and the D41e policy twice from fresh
process state. Record every terminal row plus per-episode decisions and disagreements by branch and
phase. Exclude auto-reset tasks beyond the 1,024-task bank from every statistic.

Run Stage B only if every Stage-A gate passes. It repeats the same arms and rules on maps
**9,771,000--9,771,063**, with random seed 421. No Stage-A observation may alter code, thresholds,
gates, seeds, or execution geometry.

Every arm uses 64 environments. Candidate replicas must be behaviorally exact after excluding wall
time. Reward/margin identity, action legality, task identity, action/state hashes, and complete
terminal coverage are mandatory. A mismatch invalidates the stage rather than being omitted.

## Stage-A gates

All must pass:

1. exactly 1,024 unique terminal tasks per arm; byte-equivalent candidate replicas excluding time;
2. zero illegal actions, direct-command failures, provenance failures, relevant deposit-prediction
   failures, worker-cap breaches, reward identity failures, or nonterminal loops;
3. zero `train`/`deficit` disagreement, nonzero `evacuation` and `rate` disagreement, total
   disagreement in **[0.1%, 5%]**, and at least 64 episodes with an override;
4. paired mean margin versus D40 at least **+5** with descriptive normal 95% lower bound above zero;
5. mean own score no more than 2 points below D40;
6. at least five of eight opponent-family mean margin deltas positive and none below **-10**;
7. worker-two rate at least 95%, worker-three at least 88%, crop rate at least 97%, and none more
   than one percentage point below D40;
8. no increase in `margin <= -100` catastrophes; and
9. mean margin at least +150 above the same-bank random arm.

Failure closes this exact rule without threshold adjustment or a same-bank rerun. Diagnose the
mechanism from already-consumed rows, then either change representation under a new protocol or
expand prospective one-deviation labels.

## Conditional Stage-B and pooled gates

Stage B independently requires gates 1--3 and 5--9 above, plus paired mean margin at least **+3**
with lower descriptive 95% bound above zero. The pooled 2,048-task result must have mean paired
margin at least **+5**, lower bound above zero, at least six positive opponent-family means, no
family below -10, and no catastrophe increase.

Only a full two-stage pass opens a separate deployment-kernel size/parity protocol and the still
sealed confirmation bank. It does not itself authorize candidate construction or platform action.

## Retrospective evidence boundary

The thresholds were selected after inspecting D41d and are therefore discovery hypotheses, not
held-out evidence. The hashed discovery audit exists to reproduce that choice, not to add sample
size to D41e. D41d rows never enter the prospective Stage-A/B estimates or pooled gate.
