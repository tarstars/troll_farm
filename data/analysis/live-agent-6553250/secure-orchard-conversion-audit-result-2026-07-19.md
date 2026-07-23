# Secure-orchard conversion audit — discovery result, 2026-07-19

## Verdict

**The direct mechanism is confirmed, but the frozen audit formally fails its conformance floor.
Do not waive the floor and do not build or submit a candidate from this block.**

All 80 frozen games fetched and decoded, the stderr probe preserved exact-resident stdout in every
game, every decoded diff was understood, and every admitted force was on a ripe apple mother. Only
42/80 resident runs reproduced the complete recorded command stream, below the predeclared 60/80
floor. Earlier repository audits obtained 43/80 and 44/82 on comparable official streams, so the
floor was miscalibrated to known reconstruction behavior. That design error is closed rather than
retroactively repaired on consumed outcomes.

## Direct result

The exact-prefix evidence is nevertheless unambiguous and is retained for hypothesis generation:

- 11/80 games contain an admissible outer-orchard harvest;
- all 11 continue forcing harvests after the first apple has replaced the mother seed;
- the 11 games contain 1,053 admitted forced harvests, with complete count distribution
  `11, 15, 77, 85, 91, 115, 115, 120, 140, 140, 144`;
- seven activated games win, two lose ordinarily, and two lose catastrophically;
- activated wins average 15.86 opponent crops and 20.71 opponent crop wood, while activated
  ordinary/catastrophic losses average 47.75 opponent crops and 88.50 opponent crop wood; and
- the mechanism is therefore conditional: endless exclusive fruit farming can beat passive
  opponents but becomes a severe opportunity-cost lock against a compounding economy.

The two predeclared fruit-hoard games are full-stream exact:

| Game | Opponent | Margin | Forces | First--last | Final apples | Own plants | Opponent crops / crop wood |
|---:|---|---:|---:|---:|---:|---:|---:|
| 896294348 | daaskare | -198 | 140 | 22--300 | 143 | 10 | 51 / 121 |
| 896294247 | m4l0s4n | -104 | 115 | 71--299 | 115 | 9 | 48 / 83 |

In both games, the first forced apple is banked on the following turn and every remaining force
is after seed replacement. Forced-harvest amounts account for the recorded net apple growth. The
wrapper, not the inner idle-harvest fallback, causes the accumulation.

## Multilevel interpretation

1. **Source:** once the mother is alive, the outer wrapper forces `MOVE`, `HARVEST`, `DROP`, or
   `WAIT` forever and sets the inner starter to idle. There is no exit after seed replacement.
2. **Command:** sustained cases consume 77--144 starter harvest actions plus matching drops and
   waiting/movement. This is a complete role reservation, not one bad target choice.
3. **Economy:** apples score one point each, so the loop is viable when the opponent is passive.
   It loses the wood and denial output of a generalist when the opponent creates 40--50 crops.
4. **Tail:** two of three fresh catastrophes activate; those two contribute 302 negative-margin
   points. The third catastrophe is a separate opponent-compounding failure and remains outside
   this branch.
5. **Robustness:** seven wins forbid a blanket orchard ablation. A release controller must retain
   the initial private-mother option and test its opportunity-cost exit closed-loop.
6. **Evidence:** historical post-divergence states cannot score a release candidate. Only an
   independent prefix replication and fresh paired local rollouts can qualify one.

## Next move

Freeze the older 80 exact-resident battle ids from metadata before reading their outcomes. The
replication uses a 40/80 full-stream floor calibrated from the two older audits, but still admits
events only on exact prefixes. If breadth and loss relevance replicate, open a fresh local
discovery block comparing seed-replacement release with narrow observable opportunity-cost exits;
no platform game is authorized by this audit.

## Evidence

- `secure-orchard-conversion-audit-protocol-2026-07-19.md`;
- `secure-orchard-conversion-audit-2026-07-19.json`;
- `cgauto/secure_orchard_conversion_audit.py`;
- `recent-resident-restore-field-census-2026-07-19.json`;
- `idle-harvest-local-study.json`;
- `data/panels/top5-idle-harvest-telemetry.json`.
