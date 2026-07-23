# Curriculum Level 5 regenerative-planter prospective protocol — frozen 2026-07-19

## Scope

Confirm the D3 zero-shot result once on the previously unopened exact interval
2,021,000--2,022,999.  Freeze the deterministic one-worker regenerative planter, D2 pre-creation
player-0 recovery invariant, teacher, random seed 89, 240-turn horizon, 100-env batch, and accepted
Level-4 checkpoint exactly as used in D3.

No failed seed may be inspected before the decision.  No behavior clone, PPO transition, checkpoint
selection, opponent change, threshold change, deployment, or Arena action is authorized.

## Control gates

Teacher must reach:

- >=99% overall and nontrivial success;
- >=98% in every recipe and every height;
- >=99% player-0 crop presence and renewable harvest;
- zero illegal selections;
- >=99% opponent crop creation, >=80% opponent own-crop harvest, >=95% positive opponent score;
  and
- exactly one opponent worker in every episode.

Random legal must remain <=5% overall.  Any control failure stops the actor replay.

## Fixed-actor gates

Evaluate checkpoint
`b5daae9ecf81e52ebf35f9bcb9d0eb75110abf0cc5da570f136c5505d96c4882` once.  It must reach:

- >=95% overall and >=93% nontrivial success;
- >=90% in every recipe and >=93% in every height;
- >=97% player-0 crop presence and renewable harvest;
- paired-teacher median completion delay <=10 turns; and
- the same opponent activation and exactly-one-worker gates as the teacher.

Passing accepts this isolated interaction abstraction without a new checkpoint.  Failure rejects
prospective zero-shot transfer and permits diagnosis only after the binary decision is recorded.

## Development anchors

- D3 result:
  `curriculum-level5-natural-planter-d3-result-2026-07-19.md`;
- teacher artifact:
  `6fea50e8053c8d15b996b9cf88f03ba67a95d757d65f5f2a881e4271fccfc2f9`;
- random artifact:
  `424d0e72f3b355c9b1abece5f0a5d9f02cbf224c71b59cacde17350a145eb039`;
- fixed-actor artifact:
  `e3f1786ed6fba79893e1f176b1876e89ee1be63d178730c728aff8d256a3f243`.
