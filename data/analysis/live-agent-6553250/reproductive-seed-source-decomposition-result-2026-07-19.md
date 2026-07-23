# Reproductive seed-source decomposition — result, 2026-07-19

## Verdict

The early natural-seed hypothesis is **closed**. The productive farm does let adaptive Gold
harvest 140 more natural fruits through turn 100 across 60 games, but adaptive Gold makes 46
**fewer** successful plantings in that window. The extra expansion is a post-turn-100
self-reproduction cascade, not a larger first generation launched from natural trees.

The diagnostic used consumed seeds 0--29, both seats, against adaptive Gold only. It changed no
policy commands and qualifies no candidate.

## Integrity

- Complete common grid: 120 rows, 60 games per profile.
- All games completed.
- Harvested-fruit provenance assignment: 100.000% resident and 99.985% farm.
- Chopped-wood provenance assignment: 100.000% resident and 99.877% farm.
- The historical aggregate-parity check formally failed: the determinism-repaired engine now
  gives farm minus resident -47.600 mean margin rather than the frozen -47.933 reference, a
  0.333-point shift. The command streams and this diagnostic's common grid remain internally
  paired, but the miss is not waived and is recorded as an integrity limitation.

## Evidence at three levels

### Launch window

Through turn 100, adaptive Gold makes 275 successful plantings against the resident and 229
against the farm. Farm minus resident is therefore -46, which fails the frozen +60 materiality
floor in the opposite direction.

Adaptive Gold nevertheless harvests 140 additional natural fruits in the farm condition through
turn 100: +97 plum, +41 lemon, +3 apple, and -1 banana. Natural-fruit availability is therefore
not sufficient to explain the planting divergence.

### Reproductive cascade

Across complete games, adaptive Gold makes 2,787 successful plantings against the farm and 1,021
against the resident, a +1,766 difference. Subtracting the launch-window counts gives 2,558 versus
746 plantings after turn 100, a +1,812 late difference.

The added opponent-harvested fruit decomposes as:

| Tree origin | Added fruit, farm minus resident | Share of positive added fruit |
|---|---:|---:|
| Opponent crops | 1,575 | 74.7% |
| Natural trees | 407 | 19.3% |
| Our crops | 126 | 6.0% |
| Unknown | 0 | 0.0% |

Opponent-owned crop fruit is the dominant added source. This agrees with the prior wood ledger:
the missing suppression mechanism is downstream self-crop compounding.

### Architectural implication

Competing for mature crop wood is too late: a crop that has already fruited can finance another
generation even if it is later felled. A useful denial action must interrupt an attributed rival
crop before its first fruit while preserving the private farm's banking and seed loop. This is a
joint scheduling problem because the diverted chopper has a real private-production opportunity
cost.

## Closed and opened branches

Closed without tuning:

- more early natural-tree denial as the main adaptive-Gold fix;
- fruit-kind thresholds on the consumed 0--29 data; and
- interpreting total natural-fruit uplift as proof of a launch mechanism.

Opened as a fresh causal discriminator:

- coefficient-free pre-fruit interruption of an attributed opponent crop, gated by exact growth,
  travel, chop, and first-fruit timing. This is not the rejected mature-tree rate bonus or the
  rejected resident-command transplant.

Artifacts:

- `reproductive-seed-source-decomposition-0-29.tsv`
- `reproductive-seed-source-decomposition-0-29.json`
- `reproductive-seed-source-decomposition-protocol-2026-07-19.md`

