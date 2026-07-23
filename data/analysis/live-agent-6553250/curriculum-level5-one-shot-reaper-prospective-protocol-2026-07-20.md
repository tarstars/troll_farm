# Curriculum Level 5 one-shot crop reaper prospective protocol — frozen 2026-07-20

## Scope

Confirm the D4 zero-shot result once on the previously unopened exact interval
2,023,000--2,024,999.  Freeze the deterministic one-worker one-shot reaper, D2 pre-creation
recovery, crop-loss bank-before-reseed lifecycle, teacher, random seed 89, 240-turn horizon,
100-environment batch, and accepted Level-4 checkpoint exactly as used in D4 development.

No failed seed may be inspected before the decision.  No behavior clone, PPO transition,
checkpoint selection, opponent change, threshold change, deployment, or Arena action is
authorized.

## Control gates

Teacher must reach:

- >=99% overall and nontrivial success;
- >=98% in every recipe and every height;
- >=99% player-0 crop presence and renewable harvest;
- zero illegal selections;
- >=95% positive opponent score;
- >=75% opponent crop creation and >=45% opponent own-crop harvest;
- >=70% confirmed player-0 crop destruction, with no episode above one; and
- exactly one opponent worker in every episode.

Random legal must remain <=5% overall.  Any control failure stops actor replay.

## Fixed-actor gates

Evaluate checkpoint
`b5daae9ecf81e52ebf35f9bcb9d0eb75110abf0cc5da570f136c5505d96c4882` once against the exact
teacher artifact from this bank.  It must reach:

- >=95% overall and >=93% nontrivial success;
- >=90% in every recipe and >=93% in every height;
- >=97% player-0 crop presence and renewable harvest;
- paired-teacher median completion delay <=10 turns; and
- the same opponent score, crop, harvest, destruction, and one-worker gates as the teacher.

Passing accepts this isolated interaction abstraction without a new checkpoint.  Failure rejects
prospective zero-shot transfer and permits diagnosis only after the binary decision is recorded.

## Development anchors

- D4 development result:
  `curriculum-level5-one-shot-reaper-d4-result-2026-07-20.md`;
- D4 protocol:
  `befc99e81ed1cb4907fce9c4e2428984166bcfda16d09302067cf47b219d822e`;
- teacher artifact:
  `69efc56362d766537b7134cbc42d9d31ec12d931945a521c1ff7f965a0a17bfb`;
- random artifact:
  `86323667836b25b062fdbac6b615ff03cdd39ad5c2ff5702141e4c8ca005febb`; and
- fixed-actor artifact:
  `01a2d949dfc807465fe3f6988190fb092c62278e0117a461191a60ce747fbc9f`.
