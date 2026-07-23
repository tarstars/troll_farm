# D133a local capacity hedge

Date: 2026-07-22

The frozen YT operation `f68fd8f9-83f2b344-42e03e8-a0934784` was admitted but had all sixteen
jobs ready/pending and zero running because the shared physical scheduler had not granted a
16-CPU slot. Start one local hedge over the same training-only seeds `9,844,000--9,844,063` with
the identical locked D112 binary, expert bank, feature semantics, and 20 local workers.

The hedge neither changes D133 thresholds nor silently substitutes for its YT infrastructure
gate. If YT completes, retain the local output as an additional exact-data comparison. If YT
remains capacity-blocked, any use of the local corpus requires a separately recorded execution-
only repair preserving all D133 mechanics, teacher, block, and final-validation isolation rules.

The hedge was stopped without emitting artifacts after YT allocated all sixteen shards
concurrently. At that point YT supplied roughly 256 requested CPUs and the duplicate local run no
longer reduced wall-clock risk.
