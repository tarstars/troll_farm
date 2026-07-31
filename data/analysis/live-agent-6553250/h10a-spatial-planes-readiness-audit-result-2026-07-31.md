# H10a spatial-planes readiness audit — 2026-07-31

## Verdict

**`NARROWED_TO_GENERIC_SPATIAL_AUGMENTATION`.**

The literal register instruction—swap D172's 81-field extractor for the existing
104-channel board—is not a defined intervention. `rl_level1`'s tensor is an environment
observation, not a generic board encoding: 32/104 channels depend on one selected
curriculum unit, a fixed training recipe, Level-1 episode progress, resource deficits,
or the previous primitive action. D172 makes a global choice among 13 macro options and
has no single outcome-blind selected unit, training target, or previous primitive action
that can populate those channels.

The sanctioned scientific question remains viable. D172 already provides 27,392 unique
official-map decision states and 79,997 exact zero-noise option labels. A compose-only
replay can add a player-relative tensor for the same consumed state keys without
generating any new counterfactual labels. The narrow valid successor uses the 72
current-state channels whose semantics transfer, plus D172's existing 17-field
decision/arm/affordance block. It must be separately peer-reviewed before code or GPU
work.

## Why the 104 channels are not a drop-in

`rust/src/rl_level1.rs` partitions as follows:

| Channels | Count | Meaning | D172 status |
|---|---:|---|---|
| `0,1,3–6,8–67,82–85,99,103` | 72 | current terrain, units, plants, banks, scores, workforce, home geometry | definable after controlled-seat relabeling and canonical rotation |
| `2,7,68–79` | 14 | selected-unit marker, distances, carries, stats | no single unit exists across all global macro arms |
| `80–81` | 2 | Level-1 episode steps and remaining horizon | not literal; D172 already records game turn |
| `86–98,100–101` | 15 | fixed worker recipe, cost, deficit, affordability, needed-resource routing | no D172 meaning |
| `102` | 1 | previous primitive action plane | no frozen D172 equivalent |

The encoder also hardcodes player 0 and does not canonicalize the controlled seat. Even
the 72 valid channel semantics therefore require a named player-relative adaptation;
copying bytes or treating seat 1 as player 0 implicitly would be wrong.

## Existing exact substrate

D172's frozen training range is seeds 9,860,000–9,860,511, both seats, eight families:
8,192 tasks. The generator calls `generate_official`, and D33 independently established
120/120 parity for that map path. The four external corpus shards are present and contain:

- 79,997 unique state/arm rows;
- 27,392 unique `(map_seed, seat, opponent_index, turn)` state keys;
- zero duplicate state/arm keys;
- 11,077 states (40.44%) with some exact option label at least +2.

Each row stores the exact label and 81 float inputs, not a board snapshot. Therefore a
new spatial table is required, but new outcomes are not. The valid recovery path is to
replay the exact control trajectory on those already-consumed tasks, emit one tensor per
unique state key, and require exact joins plus parity with the existing 81-field rows.
Frozen D172 and resident modules stay byte-unchanged.

The external-storage preflight passed against the `medium_data` volume with
452,646,973,440 free bytes. No write was performed. Storage is modest when deduplicated:

| Layout | Apparent bytes |
|---|---:|
| Literal 104×11×22 uint8 repeated for 79,997 candidate rows | 2,013,364,496 |
| Literal 104-channel uint8 per 27,392 state keys | 689,401,856 |
| Corrected 72-channel uint8 per state key | 477,278,208 |
| D29-style 36-channel int16 per state key | 477,278,208 |

## Why prior spatial failures do not close this

D29 used 36 player-relative raw planes plus 426 trajectory scalars to choose a permanent
turn-75 farm. It passed generated-map gates, then activated on only 7/80 official roots.
D30 localized 72.122 of the 78.045-point raw prediction shift to the generated-map
scalar regime; D33 subsequently fixed the map substrate. D172 is already post-D33 and
uses different exact per-option labels, so D29 supplies encoder lessons rather than a
duplicate result.

D18 is the stronger negative prior: its 137-channel resident-residual spatial scorer
failed all 40 prospective recipes; at the first useful 2% tail its best spatial model
had 40.52% precision and −1.23 mean value. But D18 predicts primitive residual actions
on different states and noisy/heavy-tail labels. It never saw D172's 13 macro arms or
its exact zero-noise counterfactual corpus. It lowers the prior without consuming the
one sanctioned observation-class test.

## Minimal corrected successor

If peer review accepts H10a-r1, freeze:

- a 72×11×22 uint8 player-relative current-state tensor using only the transferable
  channel groups above;
- D172's exact 17-field decision block unchanged;
- a compact two-layer width-8 convolution, valid-cell mean/max pooling, width-8
  decision branch, and width-16 fusion with 13 option heads.

That example has 6,541 parameters, below D172's unchanged 12,288 cap. The exact 13 arms,
labels, arm timing, budget-1 runtime, offered-arm head, τ=+1.0, training/LOBO partitions,
admission gates, veto panel, and sealed confirmation decision tree remain fixed.

The first authorized phase must be exporter integrity only: exact state/candidate joins,
81-feature parity, player orientation, deterministic tensor hashes, and thread parity on
consumed maps. Only that pass may open fitting. The local host reports no `nvidia-smi`;
CPU versus YT/GPU routing is a successor-protocol decision, not evidence that the compact
model is scientifically blocked.

No source, bulk artifact, new map, label, model, GPU/YT job, candidate, submission, or
Arena state was created or changed by this audit.
