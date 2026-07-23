# Curriculum Level 5 crop-before-scale D9 readiness — 2026-07-20

## Readiness verdict

**Ready for the single frozen fresh control execution on seeds 4,500--4,999.**  D9 is implemented,
mechanically validated, and smoke-tested only on consumed seeds.  The fresh bank remains unopened
and all gates remain exactly as preregistered.

## Integrity checks

- D9 is a distinct turn-180 mode; D7 remains turn 120 and D8 remains turn 180 with its original
  fund-before-crop scheduler.
- At the actual two-to-three-worker transition, the Rust test asserts that at least one rival crop
  was already created.  No D9 third-worker training may occur before that invariant.
- Both transactions use ordinary prices and existing talents.  Recorded events require fresh
  receipts; no resource or worker is gifted.
- Worker two remains the standard chopper during planting and funding.  Three-worker roles, cap
  three, and one-destruction limit remain unchanged.
- The observation/action contract and 29-argument terminal ABI remain unchanged.
- Sixteen focused Rust tests pass, including deterministic crop-before-scale ordering.
- Twenty-eight focused Python tests pass, including byte-identical D9 batches and terminal supply
  evidence for every recorded third-worker training episode.

Only four pre-existing warnings in unrelated Rust strategies are emitted.

## Consumed readiness

Teacher on seeds 0--499:

- 500/500 overall and nontrivial 295/295;
- 100% every recipe and height, player crop, renewable player harvest, and legal selections;
- every success at median turn 180;
- 100% first-worker and 95.40% third-worker training;
- 100% fresh funding attribution for both recorded transactions;
- 100% standard-chopper and 90.60% feeder productivity;
- exactly 100% rival crop creation and 88.60% rival own-crop harvest;
- 100% confirmed player-crop destruction, never above one; and
- maximum three rival workers.

Random legal on consumed seeds 0--99 with random seed 101 is 0/100 while the opponent remains
fully active.  Relative to consumed D8 teacher, crop-first ordering changes crop creation from
81.00% to 100% and rival harvest from 65.80% to 88.60%, while third training remains 95.40% versus
96.00%.  This is the expected causal signature: renewable supply improves without bypassing the
training transaction.

Consumed performance does not alter the frozen fresh thresholds.

## Frozen execution

Run exactly once, locally, with 100 environments and a 240-turn timeout:

1. teacher on seeds 4,500--4,999;
2. random legal on the same seeds with random seed 101; and
3. only after every control passes, the unchanged accepted Level-4 actor on that same bank against
   the exact teacher artifact.

Control failure closes D9 before actor replay.  Readiness authorizes no learning, YT, prospective,
deployment, or Arena action.

## Frozen anchors

- protocol:
  `b8e68069388cb9a88866d5c29b8ffb0155cd01d0240702138554d0a1cba68193`;
- consumed teacher artifact:
  `56a109cc19f216019f00bdf13a043c4fb4900148920c3ed7820c136c45012c90`;
- consumed random artifact:
  `a6d7868a2e3d0ee164c2620910b66e45694387f9885367ef59cbcd003df357f1`;
- Rust source:
  `73f7659abf7114a5cfe33bddd6825c6518b9192cb6e3b60d0bcc80fda30633fb`;
- Level-5 Python environment:
  `aab7a0303b2cf7f2582dca5c1ed90d9a55997460489c3ce7d0dc70d9eb81c427`;
- PPO/evaluation selector:
  `d1fa432aa2b5271207cd4bdedd8495933374cbf7af2530de1b02ba0225d69901`;
- Level-5 evaluator:
  `b797411f6daa7bfb9bd787f22abe112885651375c4bb01e4b03458fac8e3d37c`;
- focused Level-5 tests:
  `a05f0b4e57db822c493ec6636b76c55379fba411db240ba05c7313c54e032350`;
- release shared library:
  `328f64af58f64c885e25c03e0cf806c55c5079824ac559f6faa36db5448c0f43`;
- accepted checkpoint:
  `b5daae9ecf81e52ebf35f9bcb9d0eb75110abf0cc5da570f136c5505d96c4882`; and
- fresh seed interval:
  `[4500, 5000)`, unopened at this freeze.
