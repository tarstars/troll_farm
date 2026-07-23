# D139a local capacity hedge

Date: 2026-07-22

YT operation `ded9b633-d229c8cd-42e03e8-9fe8f069` remained in `running` state with all 16 jobs
ready/pending, zero allocation attempts, zero failures, no alerts, and no other visible running
operation in pool `delivery-ml`. Start one local exact collector over the same unused seeds
`9,844,064--9,844,127` with the D139-locked binary and expert population, using 20 local threads.

Outputs are isolated in this directory. The hedge does not change D139's YT gate and cannot
silently substitute for it. If YT allocates while the hedge is incomplete, stop the hedge. If the
local run completes first and YT remains unavailable, using it requires a separately frozen
execution-only repair with identical block, mechanics, teacher, and validation-isolation rules.

The hedge was stopped after roughly 195 seconds, before emitting either TSV, when YT allocated 11
of 16 shards concurrently. Only this note remains; no local result can enter D139 or D140.
