# Serviced-source deployment repair: fresh field protocol

The original instrumented serviced-source SHA and its field schedule are closed after the
compiler timeout. This protocol covers only the behavior-equivalent, counter-free deployment
rendering, compact SHA-256
`32b52391da9b98b07d563c39973ecb658256a3f43d2118764cf9854abd4649c8`, against exact V439
SHA-256 `7f61a6cd510a70e9389e794571512e2c5d0afb33bab957c70791c2c16fbff0bc`.
The frozen plans are under
`/data/separate_troll_farm-working/serviced-source/2026-09-05/deployment-field-v1/`:
compile-smoke SHA-256 `8818f91eb7795248ab946e8caea28630f00d811adc6f56bcf7d5d37c68e12697`,
screen `d90ec633bb4425a08089120d55d3236afb30459116c550d1885f92efe4132c03`, and confirmation
`304711e7dfb6eeb8f4cdb6c47d99d159a5806ce67af25db202b8bbb4874e2b13`.

Before opening a request, the repaired rendering must compile without diagnostics under the
matched rustc 1.90 toolchain, reproduce the original enabled candidate's commands on every one of
the 160 archived streams, reproduce every non-latency row of the frozen 192-game adaptive panel,
pass the focused tests and full suite, and have a paired local compile median within 0.25 seconds
wall and 1.0 CPU-second of V439. This is a transparent replacement for the earlier vague
"materially beats V439" requirement: extra active ledger code cannot be cheaper than its absence,
while the bounds still reject the failed export's measured +0.73 wall/+2.80 CPU seconds.

## Compile smoke

Run the exact deployment source once on unopened seed 2609057601, candidate seat 0, against the
agent frozen at division rank 60. Its outcome is ignored. Advance only if the response is complete,
the replay identity and initial state verify, turn 1 exists without an error, and the exact local
command audit passes. Do not retry an ambiguous or failed request.

## Paired screen

If the compile smoke passes, run the six frozen paired blocks (12 requests) in
`screen-plan.json`. The top-boundary opponents at frozen ranks 7 and 8 each receive both candidate
seats; ranks 20 and 40 are controls. Advance only if all requests and exact command audits pass,
there are zero deployment failures, the candidate gains at least one total match point over V439,
wins at least two of the four rank-7/rank-8 blocks, and preserves every V439 win in the controls.

## Prospective confirmation and publication

The confirmation plan is frozen before the smoke but remains unopened unless the screen passes.
It again gives ranks 7 and 8 both seats, with rank 4 and rank 60 controls. It independently requires
all requests/audits, zero failures, at least one candidate match-point gain, at least two wins in
the four rank-7/rank-8 blocks, and preservation of every V439 control win. Across screen and
confirmation the candidate must gain at least two match points.

If every gate passes, publish this exact compact source once. Capture submission and agent IDs,
then monitor to 160 distinct games of the exact submission, progress 100/100, no pending games,
and a fresh confirmation at least five minutes later. Success remains an observed mature rank of
7 or better; field results are selection evidence, not a rank prediction.
