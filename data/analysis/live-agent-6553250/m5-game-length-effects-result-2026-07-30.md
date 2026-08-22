# M5 — exact-resident game length and turn-cap association

**Verdict: `NO_MATERIAL_LENGTH_ASSOCIATION`.** Reaching turn 300 is not associated with
a stable or material terminal-margin loss in the exact resident's full matched panel.
The prior H3 duration concentration remains specific to its controlled quartet/roster
comparison and does not support a resident-wide duration-conditioned policy.

## Source and interpretation

- Exact resident: agent `6561795`.
- Processed corpus: 9,082 records, SHA-256
  `12f72265c2af19d69ddf9dad053ccc33b3c7f799182b23ca973210429500a73d`;
  9,018 clean games and 241 resident games.
- Recorded duration spans 106–300 turns; **125/241 (51.9%)** reach exactly turn 300.
- The source has no trusted terminal-reason label. Turn 300 is a post-game category, not
  a randomized treatment and not evidence of timeout, survival, stall, or mercy.
- Primary targets are turn-300 games. Non-cap controls use another pseudonym lineage and
  match resident seat, exact map dimensions, contemporaneous opponent score within ±1,
  resident score within ±0.25, and initial trees within ±4.
- Primary support is 97 cap targets across 43 exact identities and 32 pseudonyms, with
  1–13 controls per target (median 5). All frozen support gates pass.
- Uncertainty uses 20,000 target-exact-ID cluster bootstraps and a 50,000-draw two-sided
  matched null.

## Raw duration characterization

| turns | games | mean margin | win indicator |
|---|---:|---:|---:|
| 100–149 | 13 | +6.615 | 0.385 |
| 150–199 | 23 | +8.087 | 0.652 |
| 200–249 | 35 | +2.200 | 0.343 |
| 250–299 | 45 | −2.489 | 0.311 |
| 300 | 125 | −1.728 | 0.540 |

Raw cap-minus-non-cap margin is −3.771, while raw win difference is **+0.143**. Among
non-cap games, Spearman duration/margin correlation is only −0.170. Neither margin nor
win varies monotonically across duration bins.

## Matched cap association

| estimand | cap minus comparable non-cap |
|---|---:|
| terminal margin | **−1.440** |
| cluster-bootstrap 95% CI | **[−26.251, +25.112]** |
| two-sided matched-null p | **0.710** |
| win indicator | **+0.184** |

Eight of ten material-association gates fail. The point estimate is far below the frozen
20-point threshold, its interval crosses zero, and its p-value is non-significant. Win
moves in the opposite direction. Seat estimates reverse (+0.724 / −3.474), as do early
and late target halves (−14.529 / +11.381). Leave-one-pseudonym estimates span
−5.677 to +3.296.

Score-band sensitivities remain small and negative (−5.445 at ±0.5; −2.253 at ±1.5),
and the supported near-cap 250–299 comparison is −2.036. More controlled but smaller
same-pseudonym and same-exact-opponent estimates reverse positive (+11.852 and +3.867).
This is composition- and period-sensitive association, not a stable cap mechanism.

## Decision

Do not build a duration-conditioned policy, target turn 300, infer a referee termination
mechanism, inspect replays for a resident-wide cap mechanism, simulate a candidate, or use
Arena from M5. H3's cause-versus-symptom and always-on-control requirements remain binding
for its narrower contact-coverage lead. Reopen only if a future matched panel clears the
frozen magnitude, uncertainty, win, seat, time, lineage, and leave-one-out gates.

Frozen protocol: `docs/m5-game-length-effects-protocol-2026-07-30.md`.
Machine bundle: `local_codex_1/m5-game-length-effects/`.

Artifact SHA-256:

- analyzer: `ae6a2648e455f854d2ec86bd1a886e0fd38d6c8cd1414d71734182ca53b5198c`
- tests: `2f17050495488abb40023cb6d7d56270585a167e72686bc5b3cab1a43945120e`
- `result.json`: `277ee1d74885395d6368acb0c364d40a54c48ed08af90abc5039c58cfbc16abe`
- `report.md`: `2a4a5ba961a16512918e53824631d93628941cd57c28de5666ab6bff9636f9eb`
- `duration_bins.csv`: `e2dd2f325f24135d70e3460c134806ac1b687bb7894394c24ea9b280065486e4`
- `lineages.csv`: `059912c3a748ed55b0e4328c7d7157aab6343c0fddd03abde9705f55e01335d9`
