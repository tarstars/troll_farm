# D35d greedy repeated job-boundary oracle — protocol (2026-07-20)

## Question

D35c proves that exact opponent-crop provenance is a valuable target factor but
that one complete bundle cannot suppress enough of a renewable rival loop.
D35d tests the next missing horizon: **can the same frozen two-worker action
space reach the joint target when it is selected again after jobs complete?**

This is a model-based teacher test, not a deployable bot.  It uses exact local
opponent rollouts and greedily optimizes each epoch's terminal continuation.  It
does not claim to be a globally optimal bundle sequence.

## Fresh substrate

- D33 exact official maps, referee, and stall semantics.
- D35c productive `private2` farm, exact provenance tracker, generic catalog,
  competitive extension, executor, invalidation, and tie-breaking unchanged.
- Same eight mechanism opponents and independent stable-resident reference.
- Development seeds: **9,400,000--9,400,007**, both seats.
- Sealed confirmation seeds: **9,400,008--9,400,019**.
- One start per task: the first eligible two-worker root at or after turn 50.
  A task manifest must evidence tasks that never reach it.

## Frozen repeated controller

At a live decision epoch:

1. enumerate control plus the unchanged D35c no-train generic and provenance
   catalogs;
2. run every option to terminal with the exact warmed farm and opponent;
3. select maximum terminal margin, with ties choosing control, fewer overridden
   actions, then lexicographic key;
4. if control wins, stop replanning and use that farm continuation as terminal;
5. otherwise execute the selected complete bundle on the live branch;
6. preserve exact farm memory, opponent-state history, stall counter, crop
   provenance, and actual commands; and
7. replan before the first post-completion farm turn.

Permit at most **four selected non-control epochs**.  Do not start another epoch
after turn 220.  After the cap, cutoff, terminal state, or control selection, the
unchanged warmed farm owns the remainder.  Finished workers return to the farm
within an epoch exactly as in D35c.  No TRAIN goal is available.

The first-root one-shot D35c enriched oracle is recomputed on the exact common
state and is the paired horizon control.  Also record uninterrupted farm and
independent resident outcomes.

## Integrity gate

Before value analysis require:

1. every development task present in the manifest and at least 100 eligible
   start roots;
2. byte-identical one-seed rows, manifests, epoch choices, and terminal hashes;
3. exact farm controls and one-shot catalog identities;
4. zero attribution mismatches, duplicate option keys, collisions, invalid
   direct commands, hypothetical commands committed to live history, or workers
   above three;
5. every live epoch starts at the prior selected bundle's exact completion state
   and strictly advances turn unless terminal;
6. every selected epoch choice equals the recorded maximum terminal rollout
   under the frozen tie break; and
7. at least 5,000 terminal option rollouts and at least 30 tasks with two or more
   selected non-control epochs.

## Frozen development gate

The repeated representation passes only if all hold:

1. at least two non-control epochs execute in at least 25% of eligible tasks;
2. repeated mean margin gain over farm is at least +30;
3. repeated mean own-score delta from farm is at least -20;
4. repeated mean opponent-score delta from farm is at most **-20**;
5. relative to resident, repeated own-score advantage is at least +68 and
   opponent-score excess is at most **+65**;
6. versus the paired one-shot oracle, repeated opponent score falls by at least
   six points and mean margin does not fall;
7. all eight opponent-family repeated margin gains are nonnegative and at least
   six are +10 or better;
8. selected competitive targets span at least four opponent families and two
   distinct epochs; and
9. catastrophe frequency and negative-margin mass do not exceed farm or the
   paired one-shot oracle.

If all pass, freeze unchanged confirmation and export epoch-state/choice data
for scheduler learning.  If any fail, leave confirmation sealed and close the
productive-farm repeated substrate; the next architecture must begin from a
resident-suppressive objective rather than add more D35 target or epoch capacity.

## Planned artifacts

- wrapper: `rust/src/bin/d35d_repeated_job_boundary_oracle.rs`;
- implementation child reusing the frozen D35c catalog/executor;
- analyzer and focused epoch-state/tie/integrity tests;
- repeat and development rows/manifests, JSON analysis, and written verdict.
