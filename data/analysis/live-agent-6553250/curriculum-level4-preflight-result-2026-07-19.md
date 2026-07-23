# Curriculum Level 4 randomized-recipe renewable preflight — 2026-07-19

## Verdict

Pass.  The implementation preserves the accepted fixed-Level-3 behavior, composes the eight
Level-2 recipes with Level-3's sequential two-role renewable task, and validates the frozen exact
bank before any Level-4 learning labels are consumed.

## Boundary verification

- all five targeted Rust Level-3/4 tests pass, including legal teacher commands through every
  recipe and exact recipe-channel encoding;
- all 22 targeted Python environment/trainer tests pass;
- two independently allocated Level-4 batches match action-for-action and terminal-for-terminal;
- terminal recipe IDs and specifications agree with Python's independent SplitMix64 mirror;
- exact recipe coverage appears in the 200-seed debug bank;
- rerunning the fixed Level-3 teacher on seeds 2,011,000--2,012,999 reproduces all 2,000 prior
  episode-detail rows and every functional aggregate exactly.

The implementation parameterizes the proven Level-3 environment internally.  The original
Level-3 constructor, FFI symbols, observation shape, action shape, and terminal payload remain
available; Level 4 has separate FFI symbols and adds recipe metadata only to its own payload.

## Frozen exact controls

Both controls cover seeds 2,015,000--2,016,999, 100 vector environments, and 240 referee turns.

| Metric | Teacher | Frozen validity floor | Random legal |
|---|---:|---:|---:|
| Overall success | 1,999/2,000 (99.95%) | 98% | 0/2,000 |
| Nontrivial success | 99.91% | 97% | 0% |
| Worst recipe success | 99.60% | 95% | 0% |
| Worst height success | 99.80% | 95% | 0% |
| Tracked crop created | 99.95% | 98% | 20.65% |
| Renewable harvest | 99.95% | 98% | 1.95% |
| Median completion turn | 51 | diagnostic | none |
| Median training turn | 12 | diagnostic | 1 |

The sole teacher miss is in the standard-chopper family; all other recipes are 100%.  This is well
inside every frozen validity margin and is consistent with the fixed Level-3 teacher's rare map
timeout.  Recipe completion is not interchangeable: capacity and chop attributes change both
funding and post-training execution, so recipe-floor evaluation remains necessary.

Random legal often trains recipes that are already affordable and sometimes plants a crop, but it
almost never harvests that tracked renewable supply and never completes the joint score objective.
The full task therefore removes Level 2's misleading high random baseline.

## Reproducibility anchors

- protocol: `aef6cdd612d57423509f057b5aceaee669af43771b658cb369091b7befaa7418`;
- teacher control: `168eb4200be12345a9d7a28de76d6424612153b1c75f8b3923db853f1ddf257a`;
- random-legal control: `e5f52fe08177b53da23961b37800985a3585df54a7b735fe1d17f70c17450289`;
- parameterized Rust environment: `90ac10f70e4e954f48d94b010c17ee2ac738bd4346e7a84b629a2cef94c31789`;
- Python Level-4 wrapper: `7b248685e8e70ad0aa0745d963f41a5480dd2293b5c4bf17914883bbef821087`;
- PPO trainer: `afdddf640526ab4e53c254eab82a9fe8cbc7671f056bc4e6b63e2b41b3d13661`;
- clone trainer: `899ab556fe4aa9f69699afe995235f12fd24abde88a1ffdbb49071ea7b9820c6`;
- Level-4 tests: `5221b7935da8eff67762525c423e8de71fb685438f82111ed4db38afcac35de7`.

## Next execution

First evaluate the accepted Level-3 actor zero-shot as a non-gating composition diagnostic.  Then,
without altering the frozen plan from that outcome, collect exactly 800,000 online Level-4 teacher
labels from stream 6,600,000 and run the prescribed transfer clone from the accepted Level-3
checkpoint.
