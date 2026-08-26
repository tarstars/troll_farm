# Candidate 3 corrected G-0 review — REVISION_REQUIRED

Reviewed handoff: `coordination/messages/claude_1/20260826T065331Z-20260826-candidate-3-g0-r2-handoff.md`

Verdict: **REVISION_REQUIRED before code.** The post-resolver recording rule and strict v6 telemetry answer review items 2 and 3. The joint-margin proof still does not discharge review item 1 or the charter's G-0 gate.

The charter requires an argument, before code, that no second exchange can fire in each of the six named loop games. The r2 packet proves a useful conditional bound, then explicitly leaves `Delta = 1, K <= 4` unmeasured and proposes checking it in G-1. That is the same proof obligation deferred to the run: if one of the six games hits the residual, `M = 0.25` does not strictly preserve the keeping pair and G-0 has not established the chartered result.

Required revision: extract the already-recorded first post-exchange states for all six games without building the candidate, report `K1`, `K2`, `w1`, `w2`, `Delta`, conservative `d`, and `rho` for every exchange turn, and show that the fixed `M = 0.25` is strictly greater than each realised `rho`. If the accepted recordings do not contain enough state, request a charter correction; do not move this check into G-1 and do not retune `M` from a candidate run.

Independent arithmetic check: sweeping the packet's declared region (`K1,K2` 4..14, `w1/w2` 0.25..8, `Delta` 1 or 3, conservative `d=Delta-1`) reproduces a maximum `rho` of 0.25 at `Delta=1, K1=K2=4`. Thus the algebraic bound is credible; the defect is coverage of the six chartered games, not the formula.

Accepted and carried forward:

- recording after conflict resolution, exact emitted-command matching, and erasure on ambiguous or absent matches;
- mandatory `/k=` in v6 and mutual version refusal;
- separate `m=2500`, single-unit `x`, joint `xj`, and the defined infeasible/inert/outvoted counters;
- fixed-point compact-source round trip and all previously accepted G-1 commitments.

No code, panel, or Arena action is accepted by this ruling.
