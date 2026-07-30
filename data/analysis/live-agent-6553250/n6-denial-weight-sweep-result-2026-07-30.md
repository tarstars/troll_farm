# N6 denial-distance weight sweep — closed at development

## Decision

**Verdict: `CLOSED_AT_DEVELOPMENT`.** Neither preregistered nonzero alternative to the
resident's `900/(1+opponent_distance)` focus bonus passes every development gate.
Confirmation maps 9,859,000–9,859,127 remain unconsumed. There is no candidate, resident
change, or Arena action.

This completes reproduction obligation G1 once. The zero-weight removal and
capable-worker-only variants remain rejected by the earlier record; the nonzero scalar
line is now closed as well. Do not retune the weight.

## Frozen panel and integrity

- Exact arms: LOW 450, CONTROL 900, HIGH 1800.
- Fresh maps 9,858,000–9,858,031 × two seats × eight opponent families.
- Exact coverage: 512/512 paired tasks and 512 rows per arm (1,536 total), no duplicates.
- Zero critical, unclassified, ownership, or opponent-command-mismatch issues; every game
  reached a terminal state.
- External panel SHA-256:
  `f57817b3d4906c3d7941df2ab8257069ccd199b8280843db156c13f255bd41ae`.
- The one-map pre-lock smoke, exact source-diff checks, thread identity, trajectory schema,
  and six-detector execution all passed before this panel.

## Development results

| Gate/metric | LOW 450 | HIGH 1800 |
|---|---:|---:|
| command-divergent tasks | 378/512 (73.83%) | 273/512 (53.32%) |
| intended directional comparable divergences | 15/97 (15.46%) | 12/77 (15.58%) |
| paired mean terminal-margin delta | −0.7539 | +0.5586 |
| seat-0 / seat-1 margin delta | −1.1133 / −0.3945 | +0.4141 / +0.7031 |
| positive opponent families | 3/8 | 4/8 |
| own-score delta | +0.0332 | +0.8301 |
| opponent-score delta | +0.7871 | +0.2715 |
| eligible | no | no |

LOW fails the directional, overall-value, both-seat, and family-breadth gates. HIGH is
slightly positive overall and in both seats, but fails the mechanism gate sharply and has
only four positive families rather than the required six. Its +0.56 mean is also far below
the later +20 confirmation threshold, although that threshold is not used to adjudicate
development.

## Interpretation and boundary

The weight materially changes commands, so this is not a no-activation result. However,
the first comparable command divergence rarely moves focus-tree intensity in the direction
the scalar implies. The small positive HIGH aggregate is heterogeneous and is accompanied
by a small increase in opponent score. The frozen selection rule therefore rejects it
without spending confirmation maps.

This panel evaluates only the exact resident snapshot, the A2-0b referee substrate, the
three registered weights, and the eight frozen macro-opponent families. It does not prove
that every conceivable denial scheduler is valueless. It does close further scalar tuning
inside this architecture under the one-sweep/no-retune rule.

Machine result:
`n6-denial-weight-sweep-development-result-2026-07-30.json`.
