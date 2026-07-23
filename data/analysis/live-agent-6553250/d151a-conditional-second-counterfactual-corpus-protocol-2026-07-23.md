# D151a conditional-second counterfactual corpus — frozen protocol

Date: 2026-07-23  
Status: frozen after D150a support failure, before building or executing a D151 branch plan

## Hypothesis and scope

D150 proves that first-action population support is sufficient but exact-first-path second support
is too sparse for near-tie/value learning. Fill only that missing axis. On the already consumed D148
maps `9,844,136--9,844,199`, replay each of the 909 selected first actions to its selected second
boundary, then branch every legal second action, including slot zero (continue control), and roll to
terminal.

The frozen D148 candidate interface contains exactly 909 second states and 16,228 legal branches:
15,319 noncontrol plus 909 control, 6,834 branches on the 388 active D149 targets, maximum 28 and
median 18 branches/task. Build a compact plan containing the first path, exact second legal slots,
target activity, and a SHA-256 over the 64 state plus every ordered 379-action feature vector. The
runner must reproduce that hash at the conditional state before branching.

Run two independent replicas A/B, each split into eight 8-map YT shards with 16 threads, under
`//home/delivery_ml/research/tarstars/troll_farm`. Each shard cycles its 128 scenarios only up to its
maximum branch count; scenarios without a manifest or beyond their own branch count run control and
are discarded. This is about 28k simulated episodes per replica but only 16,228 emitted branches.

## Frozen corpus gates

- both replicas complete all eight prescribed shards within 1,200 active seconds each and use
  exactly 16 threads;
- each replica emits exactly 16,228 unique `(map, seat, opponent, second_slot)` terminals over
  exactly 909 tasks, with per-task slot sets exactly equal to the frozen plan;
- all 909 conditional state/action hashes reproduce before any second branch;
- every task executes its exact planned first boundary and noncontrol first slot;
- slot-zero terminals execute exactly one intervention; noncontrol second slots execute exactly two;
- all terminal map/seat/opponent, arithmetic, branch indices, boundary counts, and selection hashes
  reproduce their deterministic definitions;
- the selected second slot for every task exactly reproduces D148's selected replay terminal;
- invalid-command, provenance, and deposit-prediction failure totals are zero; environmental job
  invalidations are descriptive; and
- reconstructed A and B TSV files are byte-identical.

Passing opens separately frozen D152 return/near-tie target analysis and grouped learning on the
same eight discovery folds. D151 cannot interpret value thresholds, fit a model, read/generate
reserved maps `9,844,200--9,844,215`, integrate Rust, qualify or submit a candidate, change the
resident, or interact with Arena.
