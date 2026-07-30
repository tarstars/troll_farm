# M3 — resident seat-asymmetry audit

**Verdict: `NO_ACTIONABLE_SEAT_ASYMMETRY`.** The exact resident's point estimates favor
seat 1 over seat 0, but the effect is below the frozen materiality threshold, imprecise,
and not statistically distinguishable from zero. No seat-specific mechanism or policy
work is justified.

## Sources and identification

- Exact resident: agent `6561795`.
- Processed corpus: 9,082 records, SHA-256
  `12f72265c2af19d69ddf9dad053ccc33b3c7f799182b23ca973210429500a73d`;
  9,018 clean games, 241 resident games, 72 exact opponent identities.
- Raw seat support: 126 resident games in seat 0 and 115 in seat 1.
- Primary estimand: seat-1 minus seat-0 terminal margin. Each supported seat-1 game is
  compared with the resident's seat-0 games against the same exact opponent `agentId`,
  at identical map dimensions, opponent contemporaneous score within ±1, resident score
  within ±0.25, and initial-tree count within ±4.
- The primary panel has 37 supported seat-1 targets across 23 exact identities; controls
  per target range 1–4 (median 1). All frozen support gates pass.
- Uncertainty uses 20,000 exact-opponent-cluster bootstraps and a 50,000-draw two-sided
  cluster sign-flip null. A seat direction requires all ten frozen support, magnitude,
  uncertainty, win-effect, and stability gates.

## Result

| estimand | seat-1 minus seat-0 |
|---|---:|
| raw terminal margin | +6.752 |
| matched terminal margin | **+10.088** |
| cluster-bootstrap 95% CI | **[−16.813, +38.912]** |
| two-sided matched randomization p | **0.484** |
| raw win probability | +0.072 |
| matched win probability | +0.101 |

The point estimate labels seat 0 as worse, not seat 1. It fails three preregistered
actionability gates: absolute matched margin is 10.09 rather than at least 20, the
confidence interval crosses zero, and p is 0.484 rather than at most 0.05.

Directional matched sensitivities stay positive: reverse-oriented exact matching +19.56,
same-pseudo lineage +16.29, score bands ±0.5/±1.5 both +10.09, and early/late halves
+9.40/+10.74. Every leave-one-exact-opponent estimate remains positive (+4.81 to +19.95).
Those signs do not establish a structural seat effect: the broader fixed-opponent
contrast is only +5.29 when game-weighted and flips to −1.37 when each of 37 repeated
identities receives equal weight. With a median one control per primary target, the
direction is sensitive to composition even though the frozen matched checks agree.

## Decision

Do not create a seat branch, change the resident, inspect replays for a seat mechanism,
run a simulation panel, or use Arena from M3. Ordinary future corpus refreshes may repeat
the read-only audit. Reopen mechanism work only if a larger exact-opponent panel produces
an absolute effect of at least 20, an interval excluding zero, p≤0.05, and all remaining
frozen stability gates.

Frozen protocol: `docs/m3-seat-asymmetry-protocol-2026-07-30.md`.
Machine bundle: `local_codex_1/m3-seat-asymmetry/`.

Artifact SHA-256:

- analyzer: `2c8003e1e18b24cd5143d8440ab727ecc630e3180f0b7e3b1a65dc405c2912c5`
- tests: `4e585f1c8cdd71ca308e7dbdb6b560ddc152fb4d29cd02f06226763fa0451a38`
- `result.json`: `3c575043fcbce4fa08eb12404b1f78b840ca799b431d25383d80dc8fd018b0ee`
- `report.md`: `45767d29a52afb6df0e2986297cb611aa082e2f073bbd9cfcb4df4c12a873e8f`
- `clusters.csv`: `41959b9f3ec5874e974fc4846fabe47862c3ad37bb94abf110fa5488b274d529`
