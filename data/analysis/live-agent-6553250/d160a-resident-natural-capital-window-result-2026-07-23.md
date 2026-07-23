# D160a exact-resident natural-capital window — result

Date: 2026-07-23  
Decision: **fail the active field-probe gate; do not create TestSession games**

## Coverage and integrity

D160 decoded every available cached replay from the frozen D159 membership: 195/200 games,
including all 80 historical games and 115/120 independent suffix games. The five absent bodies
were reported and were not fetched. Agent identity, replay updates, membership, and terminal-score
checks all pass; the only score mismatch is the already disclosed penalty-style ending in game
`896349139`.

The focused analyzer/parser suite passes 9/9. Reproducibility hashes:

- D159 raw input: `97dc82a730b5a691f2bf63036834b1a9ed23bc186b00d09b874ac092efddf443`;
- frozen protocol: `93de19b65cc3e70724fb7756be4c87c5aef1f97128600247d8502db38f33491a`;
- analyzer: `63ca9ec3930b1f5cba15f21b41161ea65af5aee78314050318d20bddb88bba6a`;
- machine result: `e7e83fbde2d32a7a2a0268a02f3f4dba8b0235d70428e3f48aab8cd50650b644`.

## Result

The exact resident never naturally accumulates a third-worker bill. Across all 115 cached suffix
games, every specification has zero deposited-stock affordability, zero bank-plus-carried-inventory
liquidity, and zero immediately executable states through turn 225. Therefore all production-grade
gate counts through turn 200 are also zero.

| Worker specification | Suffix games executable by 200 | Liquid by 225 | Minimum deposited deficit | Median minimum deficit |
|---|---:|---:|---:|---:|
| `minimal_1101` | 0/115 | 0/115 | 2 | 7 |
| `balanced_2202` | 0/115 | 0/115 | 10 | 16 |
| `hybrid_2212` | 0/115 | 0/115 | 10 | 16 |
| `carry_2302` | 0/115 | 0/115 | 15 | 21 |

This is not a suffix-sampling accident: all 80 historical games also have zero liquid or executable
states for every specification. The balanced worker is missing at least 10 resource units in its
closest suffix game, and IRON, LEMON, and PLUM are limiting in all 115 closest states. Even the
cheapest helper comes within two units in only one suffix game.

## Interpretation and next move

The D159 workforce correlation is real, but it cannot be converted into an opportunistic TRAIN
wrapper around the current resident. Strong bots' extra workers are compatible with this result
because their policy deliberately funds the worker earlier; the resident spends or suppresses the
same resources before an affordable window can arise.

Close natural-capital grafting and cancel D160 platform games. The next experiment must change the
action representation so it can preserve the exact resident as fallback while planning a bounded,
multi-turn funding commitment. First prove that this interface can create and maintain a producer
without losing resident-relative value on local common maps; only then is PPO or Arena interaction
warranted. Reserved validation maps and the live resident remain untouched.
