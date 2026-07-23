# Curriculum Level 2 randomized-worker preflight result — 2026-07-19

## Verdict

**Pass.**  The eight-recipe environment is deterministic, exposes the requested recipe, returns
exact terminal metadata, and has a legal perfect teacher on the frozen 2,000-seed bank.  The
behavior-clone discovery stage is authorized.

No resident or Arena change is authorized.

## Contract checks

- Rust tests cover all recipe IDs, observation encoding, legal teacher actions, and deterministic
  Level-2 batches.
- Python tests cover Rust/Python recipe agreement, shape/mask agreement, deterministic terminal
  metadata, random-mask legality, and exact seed-interval collection.
- The focused Rust suite passes 5/5 and the combined Python curriculum suite passes 12/12 before
  learning.
- A previously latent iron-navigation contract bug was found on seed 18 before controls: the
  teacher targeted a walkable iron-adjacent mining cell while the mask exposed only the iron cell.
  The mask now exposes both canonical iron and legal mining-adjacent goals; all 200 sampled
  recipe-state legality checks pass.

## Frozen controls: seeds 2,003,000--2,004,999

The deterministic teacher solves 2,000/2,000 overall, 1,135/1,135 nonzero-total-deficit episodes,
and 100% of every recipe and height bucket.  Median completion turns show that the recipe signal
changes the task materially:

| Recipe | Episodes | Teacher success | Median turn |
|---|---:|---:|---:|
| cheap-planter | 259 | 100% | 1 |
| compact-farmer | 258 | 100% | 1 |
| balanced-producer | 261 | 100% | 6 |
| harvest-producer | 266 | 100% | 22 |
| level1-anchor | 232 | 100% | 38 |
| lean-chopper | 246 | 100% | 8 |
| standard-chopper | 238 | 100% | 18 |
| hybrid-chopper | 240 | 100% | 46 |

Random legal solves 853/2,000 overall (42.65%) but 0/1,135 nonzero-deficit episodes.  Its apparent
strength comes entirely from recipes already affordable at reset and trained automatically on the
first turn.  Accordingly, nonzero-deficit and recipe-floor gates are essential; overall success
alone is misleading at Level 2.

## Frozen artifacts

- protocol: `c97ab3ad2158cd1b9b3b8d91a4dfe6936e178a44076d0c0f9f9d245d4b543eb8`;
- teacher control: `7b507e3fe2acf3e18f307a5d1aac1f10cd189a72180679598c4d00dfe055b7d8`;
- random control: `93660ad2912adbf7769972fa7259a32d43ac49c88bad5c38cd59519369dce288`;
- release environment library: `0d32fc22ddaf86f75618c96423178cc1f0a21476b6ce93f0cf77a33471f6ee1c`;
- Python Level-2 wrapper: `e42affed48b8c9f3d8eb077664c879e10a8e71101eeb2ca2211c7d7582c3901c`.

## Next move

Run the frozen seed-61 behavior clone on 400,000 online teacher labels from stream 5,000,000 and
evaluate it once on this consumed exact bank.  Only a full overall/nontrivial/recipe/height pass
opens teacher-anchored PPO on a new exact bank.
