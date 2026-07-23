# D21 competitive closed-loop actor — frozen preflight protocol (2026-07-20)

## Question

Can the accepted D11 spatial actor serve as a viable initialization for complete-policy
optimization when the episode objective is actual full-game score margin rather than curriculum
completion or a hindsight intervention label?

This protocol first qualifies the environment and measures the unchanged actor.  A bounded PPO
pilot is conditional on that preflight.  Nothing here authorizes source integration, a candidate,
a sealed field block, submission, or Arena activity.

## Frozen environment

- Reuse the exact 104 x 11 x 22 observation and 13 x 11 x 22 action ABI accepted through D11.
- Reuse the eight randomized worker recipes and automatic first `TRAIN`; cap our policy at the
  resulting two workers for this iteration.
- Continue every episode to exactly turn 300.  Curriculum success must not terminate it early.
- Select one of six deterministic opponent mechanisms from an independent hash of the map seed:
  complete baseline, renewable planter, one-shot reaper, funded pair, sustained funded trio, and
  crop-first funded trio with repeated pressure and seed reacquisition.
- Give zero reward for the first half of a sequential joint decision and, after each referee turn,
  reward `(new score margin - old score margin) / 100`.  Thus undiscounted episode return must
  equal final margin / 100 exactly apart from floating-point accumulation.
- Keep the existing legal-action mask and online legal teacher.  No terminal asset bonus,
  curriculum progress, hand-authored opponent reward, or opponent identity channel is allowed.

## Preflight controls

Use exact seeds `[8,000,000, 8,000,480)`, 80 vector environments, and 300 turns.  Run once each:

1. the deterministic scripted teacher;
2. random legal actions with RNG seed 2101; and
3. the unchanged accepted D11 checkpoint
   `curriculum-level5-seed-reacquisition-d11-ppo-final-local-l5b.pt`, SHA-256
   `44c9a9ed3a232c01fccf9b99b16c3c785b26a1e2c656cb6c40674137138d8de6`.

Repeat the teacher on the same block and require byte-identical aggregate and episode rows.
Record per-opponent and per-recipe win rate, mean margin, own score, opponent score, training
completion, crop creation, renewable harvest, legal-action failures, and throughput.

The preflight passes only if:

1. all 1,440 episodes complete at turn 300 with no illegal selected action;
2. every opponent and every recipe has at least 40 actor episodes;
3. return identity holds in every episode within `1e-4` margin points;
4. repeated teacher rows are identical;
5. both teacher and accepted actor beat random legal by at least +20 mean margin;
6. the actor trains its requested worker in at least 90% of episodes and creates a renewable crop
   in at least 70%; and
7. actor outcomes contain both wins and losses and at least four opponent means are finite and
   distinct, proving that the objective is not saturated.

Failure closes this Level-6 formulation before training.  It does not permit reward shaping or a
different opponent mix on the consumed block.

## Conditional bounded PPO pilot

Only a passing preflight opens one local pilot:

- initialization: the exact accepted D11 checkpoint above;
- model seed 2107; training stream beginning at 8,200,000;
- 100 environments x 100 decisions, exactly 1,000,000 transitions;
- four epochs, minibatch 1,000, Adam `2.5e-4` linearly decaying to zero;
- gamma 1.0, GAE lambda 0.95, clip 0.2, entropy 0.005, value coefficient 0.5,
  reward scale 1.0, gradient norm 0.5, target KL 0.03; and
- online legal-teacher auxiliary coefficient 0.05 to preserve renewable mechanics without
  making imitation the primary objective.

Evaluate only the final checkpoint on reserved local validation seeds
`[8,100,000, 8,100,960)`.  No adaptive checkpoint or hyperparameter selection is allowed.  The
pilot is useful only if it improves mean margin over the unchanged D11 actor by at least +5,
improves at least four of six opponent means, has no opponent regression below -15, retains at
least 90% training completion and 70% crop creation, and remains finite/legal throughout.

A pilot pass authorizes an exact-engine paired qualification against the resident and strategic
panel.  It still does not authorize deployment or Arena use.

## Compute rule

Run controls and this single pilot locally.  The prior D11 YT benchmark was 9.82x faster but failed
its frozen backend-parity conjunction, and D21 is a new reward/environment workflow.  YT becomes
eligible only after a separate identical 1M local/YT parity benchmark is preregistered for a later
replica stage.
