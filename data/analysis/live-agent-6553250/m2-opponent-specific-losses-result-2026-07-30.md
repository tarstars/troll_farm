# M2 — opponent-specific systematic losses

**Verdict: `NO_ACTIONABLE_MATCHUP`.** The exact resident has no currently active,
exact-identity opponent that clears the frozen evidence gates for an opponent-specific
policy or replay-mechanism follow-up.

## Sources and identification

- Exact resident: agent `6561795`.
- Processed corpus: 9,082 records, SHA-256
  `12f72265c2af19d69ddf9dad053ccc33b3c7f799182b23ca973210429500a73d`;
  9,018 clean games, 241 resident games, 72 exact opponent identities.
- Current leaderboard: 2026-07-30T02:17:01Z, SHA-256
  `7f6cdaa2b4fbce31ca5a4adbe5c78d59a9a16b56e76faac838b0a4b062c66815`.
- Expected outcome uses the resident's other games matched on resident seat, map
  dimensions, opponent contemporaneous arena score within ±1, resident score within
  ±0.25, and initial tree count within ±4. This is a within-resident matched comparison,
  not a recovered platform rating model; M1 found no defensible score-update rule.
- Primary eligibility requires at least five target games, at least two in each seat, a
  currently active exact identity, complete matching fields, and at least ten controls
  for every target game. Twelve active identities clear the game/seat gate; only three
  clear matched-control support.
- Uncertainty uses a 20,000-draw game bootstrap and a 50,000-draw matched null, with Holm
  correction over the three eligible identities. Actionability requires all ten frozen
  magnitude, uncertainty, win-rate, seat, time, score-band, and leave-one-out gates.

## Primary results

| exact agentId | pseudo | games (seat 0/1) | raw margin | matched residual | 95% CI | win residual | Holm p |
|---:|---|---:|---:|---:|---:|---:|---:|
| 6479863 | R1FA | 8 (4/4) | −40.75 | −31.621 | [−81.015, +22.243] | −0.087 | 0.229 |
| 6480545 | BoatBuilder | 5 (3/2) | −77.20 | −73.178 | [−166.993, +20.637] | −0.135 | 0.184 |
| 6512056 | a76a44 | 7 (4/3) | +14.14 | +9.526 | [−65.509, +81.816] | +0.134 | 0.635 |

R1FA is the only stable negative hint: its residual remains negative in both seats, both
chronological halves, both identified score-band sensitivities (−26.50 at ±0.5 and −29.57
at ±1.5), and every leave-one-game-out estimate. It nevertheless fails the uncertainty,
multiplicity, and win-effect gates: the upper confidence bound is +22.24, Holm p is 0.229,
and win residual is only −0.087 rather than ≤−0.15.

BoatBuilder's large point estimate is underpowered and unstable. Its confidence interval
crosses zero, Holm p is 0.184, the ±0.5 sensitivity lacks ten controls per game, and the
seat estimates reverse from −152.91 in seat 0 to +46.42 in seat 1. `a76a44` shows no
negative anomaly. The remaining 69 exact identities fail at least one primary eligibility
gate; the machine table preserves each reason.

## Decision

Do not build an identity-specific branch, infer a replay mechanism, change the resident,
or use Arena from M2. Preserve R1FA as a surveillance hint only. Reopen matchup-specific
work after materially more exact-ID games narrow its interval and multiplicity-adjusted
evidence, or after a stronger contemporaneous control design becomes available.

Frozen protocol: `docs/m2-opponent-specific-losses-protocol-2026-07-30.md`.
Machine bundle: `local_codex_1/m2-opponent-specific-losses/`.

Artifact SHA-256:

- analyzer: `46d0a53ddadcf261cd2d2eb9a1ce8cf92fa3ffdb567c42a8008d2e3a992581dc`
- tests: `55b414c99ada11ae94e0ec0b5b9902f56c1217f36469575b6462673c38711bc6`
- `result.json`: `0202252aebe18058485817f5eb0d2b80d2f6f4c07b526256c63ad16f726ac640`
- `report.md`: `e201c2e28c997d75745f7cafd9ab7f42074a2cca68de63d32497b8d1dca80a5a`
- `opponents.csv`: `1fc75fbc676f3b355e2b73e77e8e588aa771f96842c9c813c24333eaef28637f`
