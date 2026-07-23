# D151a conditional-second counterfactual corpus — result

Date: 2026-07-23  
Decision: **open frozen D152 value analysis**

Operation `7c5178cd-39f3843f-42e03e8-2fe89acd` completes 16/16 YT jobs with zero failures. All shards
use 16 threads and finish in 195--437 seconds, versus the 1,200-second cap. Reconstructed A and B
are byte-identical: 16,228 rows, 2,530,794 bytes, SHA `103cead6...`.

All 909 conditional state/action hashes, task slot sets, branch ordinals, first paths, intervention
counts, arithmetic, and selection hashes reproduce. The corpus contains exactly 909 slot-zero
first-only controls and 15,319 noncontrol second actions; 6,834 branches belong to D148-active
targets. Every original selected second action exactly reproduces its D148 terminal. Invalid
commands, provenance failures, and deposit-prediction failures are all zero. Environmental job
invalidations are descriptive.

The corpus is mechanically safe for the already frozen D152 interpretation. Reserved maps remain
untouched. Result JSON SHA: `0179b7eb...`.
