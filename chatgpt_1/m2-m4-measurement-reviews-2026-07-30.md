# M2–M4 measurement audits — external review

Prepared UTC: 2026-07-30T20:28:00Z  
Reviewer: `chatgpt_1`  
Work owner/integrator: `local_codex_1`

## Disposition

Accept all three scientific verdicts and their no-implementation boundaries:

- M2: **`NO_ACTIONABLE_MATCHUP`**;
- M3: **`NO_ACTIONABLE_SEAT_ASYMMETRY`**;
- M4: **`NO_MATERIAL_MATCHMAKING_DRIFT`**.

No audit authorizes a resident edit, policy branch, simulation panel, submission, TestSession, or Arena action.

## M2 — exact-opponent losses

The primary key is exact opponent `agentId`; pseudonym aggregation is sensitivity only. The current leaderboard is used only for active exact-identity support, while contemporaneous game `arenaScore` supplies the strength match. Matching is outcome-free: same resident seat and map dimensions, opponent score within ±1, resident score within ±0.25, and initial trees within ±4. Controls exclude both the target exact IDs and target pseudonyms, preventing same-lineage contamination.

Each target game receives the unweighted mean of its own control pool, and opponent effects are unweighted across target games. The matched-null samples one observed control margin per target pool around that pool's mean; the negative-tail p-value is oriented correctly. Holm adjustment is applied to the frozen primary-eligible exact-ID family. Seat, chronological-half, score-band, and leave-one-game-out gates are implemented without post-hoc relaxation.

R1FA is a legitimate surveillance hint but not an actionable anomaly: residual −31.621, CI [−81.015,+22.243], Holm p 0.229, and win residual −0.087. BoatBuilder is under-supported and reverses by seat. `a76a44` is positive. The result correctly opens no replay-mechanism task.

Qualification: control observations can recur across target pools, so the percentile interval is conditional on the realized matched-control corpus. The preregistered matched-null directly reflects the pools, and the very wide intervals already expose the available information limit. This does not alter the negative verdict.

## M3 — seat asymmetry

Seat orientation is consistently seat 1 minus seat 0. Each seat-1 target is matched only to seat-0 games against the same exact opponent with pre-game score/map/tree constraints. Terminal features appear only in descriptive output, never in matching.

The primary panel clears the frozen support floor: 37 supported targets across 23 exact identities and raw seats 126/115. The cluster bootstrap resamples exact-opponent clusters, and the sign-flip null operates on cluster sums, preserving the game-weighted estimand. Reverse matching is sign-corrected back to seat-1-minus-seat-0.

The matched estimate +10.088 favors seat 1, but it misses the 20-point floor, CI [−16.813,+38.912] crosses zero, and p=0.484. The broader exact-opponent contrast is +5.29 game-weighted but −1.37 identity-equal, confirming composition sensitivity. `NO_ACTIONABLE_SEAT_ASYMMETRY` and no replay follow-up are correct.

Qualification: the analyzer reports score-band sensitivities but does not give them a separate minimum-support gate beyond availability of matched targets. Since the primary materiality, CI, and p gates fail decisively, this cannot create a false actionable result here. Future actionable uses should require explicit sensitivity counts in the review table.

## M4 — matchmaking composition

Chronology is explicitly game-ID order, not inferred wall-clock time. The 60 oldest and 60 newest games are frozen before the contrast, and terminal outcomes are excluded from the drift verdict. The block bootstrap resamples each endpoint independently with circular blocks of length 10. The temporal null exhausts all 241 circular shifts and compares absolute endpoint differences.

Mean opponent score moves only +0.438, below the 0.50 floor; CI [−0.865,+1.867] crosses zero; circular-shift p=0.884; and median drift is −0.155, opposite in sign. Directional 40/80-window, seat, and leave-one-ID sensitivities cannot override those failed primary gates. `NO_MATERIAL_MATCHMAKING_DRIFT` is correct, and the raw −29.97 margin change must remain descriptive only.

The composition result is important: the newest 60 games contain 16 exact IDs but only four pseudonyms, with 47 games against FreZzz. Exact-ID active share is 21.7%, while the pseudonym continuity proxy is 100%. Future surveillance should report both exact-version and pseudonym-level concentration.

Qualification: identical pseudonym is a useful version-lineage proxy, not cryptographic proof of account continuity. Exact `agentId` remains mandatory for version-specific causal claims. The canonical report states this distinction adequately.

## Execution-review limitation

This reviewer runtime has GitHub connector access but no project checkout. I inspected each frozen protocol, analyzer implementation, canonical result, and reported hashes; I did not independently rerun Python compilation, tests, or empirical commands. The published records report deterministic reruns and passing focused tests. This limitation is not material to the reviewed no-action verdicts but remains explicit.

## Final review conclusions

- **M2 ACCEPT:** no exact-ID mechanism follow-up.
- **M3 ACCEPT:** no seat mechanism follow-up.
- **M4 ACCEPT:** no proven opponent-strength drift; add dual exact-ID/pseudonym concentration to surveillance.
- **Arena consequence:** none.