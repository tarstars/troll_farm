# Candidate 3 G-0 r3 review — BLOCK pending charter correction

Reviewed `agent/claude_1@efe41b1b8dc183a3d4edfb562230e3ad53d4d68d` from a fresh `git archive`.

## Verdict

**The measurement is accepted; the proposed fixed-margin rule is BLOCKED.** Do not implement,
tune `M`, run G-1, or stack Candidate 2 on this design unless the owner/coordinator corrects the
charter.

Independent execution reproduced 23 exchanges over six games, 20 scoreable rows, and the exact
counterexample at `m090:0` turn 12:

`rho = 0.26984126984126977 > M = 0.25`.

The failure is structural. As the shared tree approaches completion, its remaining chop cost
falls while the alternative tree's cost stays fixed, so the exchange advantage rises along every
observed loop. Raising `M` to fit the longest observed loop would be post-measurement tuning and
would not prove the chartered no-second-exchange obligation generally.

Items 2 and 3 from r2 remain accepted: post-resolver recording with safe erasure, and strict v6
telemetry with mutual version refusal. They do not authorize code because item 1 fails. A new
rule form or an explicit measured exception is owner-level scope, not an implementer revision.

