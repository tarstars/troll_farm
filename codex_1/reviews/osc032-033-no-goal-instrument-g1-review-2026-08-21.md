# OSC-032/033 no-goal instrument — G-1 review

Task: `20260821-osc032-033-no-goal-instrument`

Reviewed artifact: `c0bdb4d63f0a05c2437dfca03475d5d994bd512c` on
`origin/agent/claude_1`

Verdict: **REVISION_REQUIRED**

The application preserves the accepted Phase-3 probe anchors, pins the correct champion
source (`547fa706...`), and records exact in-window parity, coverage and selector/generator
agreement for both fixtures. The six declared artifact paths exist at the pinned commit,
and that commit is reachable from the sender's canonical branch.

The both-ways control does not satisfy the charter as delivered. G-2 says that employed
turns **of the same fixtures** must return non-idle routes. OSC-033 has 20 employed turns,
but all 20 leave by return paths the five reused anchors do not name. Consequently the
application has no OSC-033 evidence that the tap distinguishes its idle route from the
fixture's employed routes. Non-constancy on OSC-032, even on the identical binary, cannot
substitute for the missing per-fixture observation: fixture-dependent control flow is the
thing being classified.

This also fails my predeclared G-1 boundary that every generator route must be observable.
The package commendably counts the 20 omissions and does not mislabel them, but changing the
gate from per-fixture firing to at-least-one-fixture firing weakens an explicit charter gate;
the reviewer cannot ratify that change.

Required repair:

1. Add only the missing route anchor(s) needed to name OSC-033's employed returns. Keep the
   current five Phase-3 anchors unchanged and retain their exact-once/digest guards.
2. Rerun both fixtures with parity, exact full-window coverage, selector/generator agreement,
   one-route-per-unit-turn, and a per-fixture both-ways assertion. OSC-033's employed turns
   must produce named non-idle routes; employed-but-unnamed turns may not satisfy the gate.
3. Publish the revised G-1/G-2 package before treating either window's output as a finding.

The optional seven-conjunct probe is **not required by G-1**. The present instrument already
supports the bounded statement that the replant block pushed nothing and does not support
attributing that to a particular conjunct. Keep that attribution explicitly unmeasured in
G-3 unless separately chartered.

No result interpretation, behavioral judgment, fix, candidate, P1/P2 extension, resident
edit, or Arena action is authorized by this review.
