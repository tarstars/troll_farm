# H10a spatial selector — training and qualification proposal

Status: **DRAFT — training is not authorized.**

This document fixes the proposed experiment before any model is trained. Approval of this
document would authorize only local data export, model fitting, and offline evaluation. It would
not authorize a platform submission.

## Plain-language question

The old selector saw a short numerical summary of the game and found only small gains. Would it
make better one-time choices if it could also see where terrain, trolls, plants, resources, and
tents are on the map?

Everything except that map view stays the same. This is not a new banana farm, scheduler, arm set,
label source, or platform candidate.

## Completed prerequisite

The compose-only exporter has passed its integrity gate:

- It reproduced all 79,997 archived decision rows from 512 maps and found all 27,392 expected
  distinct states.
- There were no missing or extra rows, inconsistent state fingerprints, orientation errors, or
  tensor-size errors.
- One archived old value differs at the raw float-bit level: `1/300` at map `9860166`, seat 0,
  resident opponent, turn 299, feature 49. The archived TSV intentionally uses nine decimal
  places, and both values serialize exactly as `0.003333333`. The focused archive-format check
  passes and the raw difference remains reported.
- A one-map check produced the same aggregate fingerprint with one and four replay threads.
- The frozen D172a source and four archived corpus shards kept their original hashes.

Evidence is stored under `/data/separate_troll_farm-working/analysis/h10a/`. This prerequisite did
not write tensors, train a model, change a bot, or contact the platform.

## Inputs

For each already-consumed D172a decision state:

- one `72 × 11 × 22` unsigned-byte map tensor;
- the unchanged 17-number D172a decision block identifying game time, observed opponent worker
  count, currently offered arms, and the two arm-specific affordability values;
- the unchanged exact D172a counterfactual label for the offered arm.

The 72 map layers are exactly source channels
`0,1,3–6,8–67,82–85,99,103` from the Level-1 representation, adapted so our side is always “us”
and rotated 180 degrees when needed so our tent is in the canonical half of the board. Layers tied
to a selected primitive worker, a Level-1 training recipe, episode history, or previous primitive
action remain excluded because they have no honest meaning for this global one-time choice.

Map bytes are divided by 255 for model input. Padded cells outside the actual map are excluded from
pooling. No opponent name or identity is an input.

## Frozen model

Use one function class only:

1. `3 × 3` convolution, 72 map layers to width 8, padding 1, then ReLU.
2. `3 × 3` convolution, width 8 to width 8, padding 1, then ReLU.
3. Mean and maximum over valid map cells, producing 16 map values.
4. The 17-number decision block goes through a width-8 linear layer and ReLU.
5. The 24 combined values go through a width-16 linear layer and ReLU.
6. A 13-value output gives one predicted value for each unchanged D172a arm.

This is 6,541 trainable parameters, below the unchanged 12,288-parameter cap. No attention,
recurrence, residual blocks, architecture sweep, or ensemble is allowed in this experiment.

## Frozen fitting rules

- Training corpus: the existing maps `9860000–9860511`, both seats and all eight opponent
  families. No new counterfactual game labels are generated.
- Loss: Huber loss with delta `1.0`; each row trains only its offered arm's output.
- Two deterministic fits with seeds `101001` and `101002`.
- One CPU training thread per fit, `LC_ALL=C`. Training may not use the selection, veto, or
  confirmation ranges.
- Runtime rule stays unchanged: among all arms offered on a turn, invoke the highest predicted one
  only when its value is greater than `+1.0`; otherwise keep the resident behavior. At most one arm
  may be invoked per game.
- Epoch count, batch size, optimizer, learning rate, and checkpoint cadence must be written into a
  machine-readable lock before the first fit. They cannot change after any fitted or held result is
  viewed.

All tensors, checkpoints, caches, and evaluation rows must be written below
`/data/separate_troll_farm-working/`; `/tmp` and the root disk may hold only small source and system
files.

## Offline qualification

Selection uses the unchanged maps `9861000–9861127`, split into eight independent blocks of 16
maps. Each fit is played closed-loop against its paired resident control.

Every admission condition must pass:

- pooled mean margin gain at least `+1.5`;
- worst held block at least `0`;
- worst opponent-family mean at least `−1`;
- the one-time option used in 5–60% of tasks;
- crop and workforce safety exactly preserved;
- catastrophes no more frequent than control.

If both fits pass, select by highest worst-block result, then highest pooled mean, then lowest seed.
If neither passes, close this spatial-selector experiment without changing the model or thresholds.

Only an admitted fit may enter the already-consumed veto panel. It must have mean gain at least
`+1.0`, no opponent family below `−2`, no extra catastrophes, and no greater negative-margin mass.
Failure closes the experiment.

Only a veto pass may open the still-sealed maps `9862000–9862063`, exactly once. Confirmation
requires mean gain at least `+2.0`, a positive clustered confidence lower bound, every opponent
family at least `−1`, no extra catastrophes, and negative-margin mass no more than 1.1 times
control. Failure closes the experiment.

## Stop points

- Export/join/integrity failure: stop as blocked; do not fit.
- No selection admission: close the experiment; do not inspect veto or confirmation.
- Veto failure: close; do not inspect confirmation.
- Confirmation failure: close.
- Confirmation pass: stop and report. Building a deployable bot and submitting it to the platform
  require separate explicit owner approval.

No threshold, seed range, feature layer, architecture, or safety gate may be rescued after seeing
an outcome.

