# Curriculum Level 3 design decision — 2026-07-19

## Transfer boundary after accepted Level 2

Level 2 proves that one compact spatial actor can fund any requested worker recipe.  It does not
prove that the actor can issue coordinated commands to multiple trolls, turn the purchased
capability into score, or create renewable supply.  Recipe choice and opponent response are also
missing, but adding all four gaps at once would make a failure uninterpretable.

| Candidate next abstraction | New capability isolated | Main confound | Decision |
|---|---|---|---|
| Choose among worker recipes | strategic first-move selection | still never operates the worker | defer |
| Operate two trolls on a fixed role pair | coordination and score conversion | none beyond renewable objective | **select** |
| Add a waiting opponent | collision/contest response | mixes coordination with adversarial transfer | defer |
| Full 300-turn score maximization | complete economy | sparse objective and many policy choices | defer |

## Selected development hypothesis

Use a fixed standard chopper `(2,2,0,2)` with automatic TRAIN.  Before training, the starter solves
the already accepted funding task.  After training, the same shared actor makes sequential
decisions for the starter producer and the new chopper; the two stored commands execute together
as one referee turn.

An episode succeeds only after all of the following:

1. the requested chopper is trained;
2. the policy plants a BANANA crop on a designated free home-area cell;
3. a resident troll later harvests BANANA from that created crop; and
4. resident banked score is at least 12 points above its immediate post-training score.

This prevents a pass from mere workforce ownership, natural-tree liquidation alone, or planting
without closing the renewable loop.  Maximum length is 240 referee turns.  Recipe selection,
third-worker funding, opponents, and terminal score differential remain out of scope.

Development seeds 0--499 may be consumed to debug the environment and teacher.  Exact preflight,
training, and evaluation intervals and their gates will be frozen only after the teacher contract
is deterministic, legal, and feasible on that development bank.
