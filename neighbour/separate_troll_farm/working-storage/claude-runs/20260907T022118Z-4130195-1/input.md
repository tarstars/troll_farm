# Finish frozen chopup certification with the correct semantic reference

Budget15minutes. Frozen chopup source MUST NOT change. Own check_lookahead_startup.py
and a focused test if needed, plus runartifacts; othercandidate/canonical/neighbor
unchanged. No platformcalls or panels. Prior cert run20260907T021124Z-4097278-1.

Primary decision: changed initial MOVE is intended. This bot intentionally delays
some first hires to mine extraore. Exact readable and exact compact agree160/160.
Neither V439 NOR policyflat is the expected-output oracle for this NEWpolicy.
Switching to policyflat would still reject the same intentional semantic difference.

Add a small explicit --expected-binary option to the existing startup checker;
default preserves legacy V439 behavior. Expected startup output comes from a batch
invocation of that reference binary. For this run use the independently compiled
EXACT READABLE chopup binary, compare BOTH interactive readable and shipped compact
outputs against it,320starts/16game-seat cases. Report reference path/hash and
commands_equal_reference; do NOT claim commands_equal_old_baseline when it isn't.
Keep open-stdin/liveness, full-line, latency/timeout checks unchanged. A focused
test should show intentionally different-from-V439 reference can pass, but a
different compact output still fails. No weakening to merely 'any output'.

Run serial320startup checks, no>50ms or errors, then matched alternating THREE
Rust1.90 exactcompact/V439compile pairs,0candidate diagnostics, medianratio<=1.10.
Use frozen compactd40ed6449518d9eb00d60a95bd7c5d8c37eafa610c398e5a1d1a6a866eaef59d
and existing V439 7f61a6cd... export. Reuse full160report, don't rerun it. Snapshot/
hash compiler, actualsources/binaries; no overlapping heavyjob. Correct fixture
oracle only, not bot behavior. RESULT<=400words with checks/metrics/evidence and
limitations; no strength/publication claim. Collect jobs and report actualUTC.
