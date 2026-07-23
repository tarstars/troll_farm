# D112a repair 1 — exact root snapshots

Date: 2026-07-22  
Status: frozen before any D112a value or teacher-signal field was read

The original replicate A completed all runtime assertions and emitted 128 baselines plus 13,377
arms, but its 10.403 arms/s end-to-end rate missed the prospectively frozen 12 arms/s mechanics
gate. No terminal score, paired gain, family result, feature target, or oracle statistic was read.
The only observed fields were process health, runtime, row count, file size, and artifact hash.

Repair 1 changes execution only. `CompleteMacroEnv` and every concrete opponent controller are now
cloneable. The collector stores the exact environment at each baseline q6 root, clones that state
for each arm, and simulates the proposal plus remaining continuation. It no longer reconstructs
the same prefix separately for every arm. Proposal construction, features, actions, one-use
authority, continuation policy, output schema/order, seeds, gates, and analysis are unchanged.

On excluded smoke seed `9,843,000`, the repaired 977-arm and 16-baseline matrices are byte-identical
to the pre-repair matrices. End-to-end throughput improves from approximately 17.2 to 39.76 arms/s.
An all-eight-family clone test also requires an original environment and its snapshot to produce
identical terminal structures after 40 shared decisions.

Run two repaired signal-panel replicates. Before interpreting mechanics or value, require:

- repaired A equals repaired B byte-for-byte;
- repaired A equals the complete pre-repair A byte-for-byte; and
- both repaired runs independently clear the unchanged 12 arms/s gate.

The preserved pre-repair hashes are:

- arms: `d097ad835d8ec2253c89b1558f3b3fb97eb3b71e32a8d952a8f0cf3297810032`;
- baselines: `47da570ab128a87315aebe57c8285ed79bf27956ab1656ed1f173310ab095dad`;
  and
- original frozen-input manifest:
  `0caf2e9c407a16fd2998791a10509b5e769e9b096c0160c76fbe94e517953ff6`.

All original D112a signal, safety, decision, platform, and map-isolation rules remain frozen.
