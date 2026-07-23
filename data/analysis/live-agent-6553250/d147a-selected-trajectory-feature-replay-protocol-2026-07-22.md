# D147a selected-trajectory feature replay — frozen protocol

Date: 2026-07-22  
Status: frozen after D146's schedule-priority pass and before either complete replay

## Purpose

Validate that the live q6 state/action feature interface can exactly replay the 57 selected D145
two-intervention winners. This is a mechanics and data-integrity gate before collecting a broader
joint two-stage teacher on new maps; it is not a policy-value experiment and consumes no new seed.

Run deterministic repeats A and B on D144's consumed maps `9,844,128--9,844,135`. For each selected
task, reproduce its frozen first and second actions and record every legal candidate through the
selected second boundary. All 71 unselected tasks remain exact control. Each candidate row contains
64 state features and 379 action features from `Q6ProposalVecEnv`.

## Locked inputs

- collector: `cgauto/collect_d147a_selected_trajectory_features.py`, SHA-256
  `a9fd01e3e3e1f65b94503723d73fdbf811e6e61a5e133845f656b0e69a2c222d`;
- collector tests: `tests/test_collect_d147a_selected_trajectory_features.py`, SHA-256
  `42de3adb92c2fba817edb28c55a7cd611583c5868ea8ca7563a09c2335ba5cc0`;
- selected manifest: `d145a-selected-two-intervention-trajectories.tsv`, 57 rows, SHA-256
  `88b5e08ec55eae0bc54cacd285af7235b6dfb78181c525a069857be52bc9cf4e`;
- D144 repeat-A reference: `d144a-mc-a-9844128-9844135.tsv`, SHA-256
  `cbeb74ff83a1b9f29d79ad9d58c495d84ea33537665ab076943a95c31e679ba3`;
- expected selected decision groups: 153, including exactly 57 first and 57 second actions.

## Frozen gates

Both repeats must complete and their candidate TSVs must be byte-identical; replay TSVs must also
be byte-identical. The replay matrix must contain exactly 57 selected tasks and every frozen
terminal field must exactly equal the D144 reference.

For the candidate matrix:

- all 443 feature columns must be finite and the schema must contain exactly 64 state plus 379
  action features;
- there must be exactly 153 decision groups and one chosen row per group;
- candidate slots must be unique within each group, their count must equal `legal_candidates`, and
  control slot zero plus the chosen slot must both be present;
- all rows in a group must have identical state features and schedule metadata;
- all pre-first and between-action decisions must choose control; every first and second action
  must choose a legal noncontrol slot;
- action features for control slot zero must be exactly zero, and selected noncontrol actions must
  expose at least one nonzero action feature; and
- no terminal parity, provenance, invalid-command, prediction, or invalidated-job failure is
  allowed.

If every gate passes, open a new-map D148 corpus at D146's 64-row outcome-blind schedule priority
under `//home/delivery_ml/research/tarstars/troll_farm`. Otherwise repair only the feature/replay
interface and repeat D147 on these consumed maps. D147 cannot qualify a candidate, consume D126 or
final-validation seeds, change the resident, submit, or interact with Arena.
