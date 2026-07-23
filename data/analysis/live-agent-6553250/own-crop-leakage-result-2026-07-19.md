# Resident own-crop leakage — result, 2026-07-19

## Verdict

**Reject and close a private-placement residual.**  The exact resident already plants almost
exclusively on resident-favored geometry, and opponent capture of those crops is too small and too
geometrically diffuse to explain the worker-rich loss tail.

All 131 consumed control games fetched and decoded exactly.  Attribution found 1,463 exclusively
resident-created crops with zero unknown diff updates.

| Gate | Required | Observed | Pass |
|---|---:|---:|:---:|
| Overall opponent wood share | >=15% | 14.38% | no |
| Catastrophic opponent wood/game | >=8 | 2.32 | no |
| Leaked wood on contested/opponent-favored cells | >=60% | 9.16% overall, 0% catastrophic | no |
| Capture-game coverage | >=20 | 59 | yes |
| Integrity/crop volume | 131 games, >=500 crops | 131, 1,463 | yes |

The resident captures 1,494 wood from its crops and opponents capture 251, or 1.92 per game.
1,420/1,463 crops are resident-favored; there are zero opponent-favored crops.  Catastrophic games
contain 264/264 resident-favored crops, with 263 resident wood and only 58 opponent wood total.
Moving PLANT destinations cannot remove the dominant opponent-created supply engine.

The more useful asymmetry remains the reverse direction: catastrophic opponents average roughly
84 wood from their own crops, while the resident takes only about 13 in the control census.
Continue with opponent-crop denial, but use a new value mechanism rather than retuning the closed
flat `b100_e6` bonus, ETA, commitment, or contact-harvest residuals.

Artifacts: `own-crop-leakage-protocol-2026-07-19.md`,
`own-crop-leakage-2026-07-19.json`, `cgauto/own_crop_leakage.py`, and
`tests/test_own_crop_leakage.py`.

