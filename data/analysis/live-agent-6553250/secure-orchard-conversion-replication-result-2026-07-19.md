# Secure-orchard conversion audit — independent replication result, 2026-07-19

## Verdict

**Reject and close the universal secure-orchard release branch.**

The disjoint older-80 block passes every implementation/conformance check but fails all four
mechanism breadth/downside gates. Do not lower the gates, tune a release trigger on either
80-game block, build a candidate, run controlled games, or change the arena resident.

## Frozen replication

The ids were frozen from battle metadata before any result fetch. The block contains exactly 80
completed games from agent `6560353`, submission `41012883`, excludes the recent-80 discovery
corpus, and has ordered-id SHA-256
`8b9195beacadaf72ed740666c4f9139cf3dbf82fc66ec242b04275ee92666145`.

| Gate | Required | Result | Pass |
|---|---:|---:|:---:|
| All games fetched/decoded | 80 | 80 | yes |
| Full resident reproductions | >=40 | 44 | yes |
| Probe stdout neutral / unknown diffs | all / 0 | all / 0 | yes |
| Sustained activated games | >=5 | **2** | no |
| Distinct activated opponents | >=3 | **2** | no |
| Post-seed-replacement forces | >=200 | **26** | no |
| Activated losses | >=2 | **0** | no |

The two admitted activations are short exact prefixes: 19 forces against Dapps and 9 against
Adler3D. Both are wins (+94 and +60), with only 8--12 opponent crops and 8--15 opponent crop wood.
This independently resembles the passive-opponent side of discovery, not its rich-opponent tail.

## Interpretation

The recent fruit-hoard catastrophes remain correctly attributed; replication does not make those
facts false. It shows that their 11-game activation cluster is not representative enough to
justify a policy-wide exit. Secure orchard has a genuine bimodal opportunity cost, but the
available field sample does not provide a stable pre-action discriminator, and local evidence
previously found large exclusive-orchard gains. A universal first-seed release would discard a
proven sparse strength to address a non-replicating tail subtype.

The experiment closes at the mechanism level. Future work may revisit the component only after a
different controller makes orchard reservation part of a global task market; no standalone
orchard threshold or score switch is eligible.

## Evidence

- `secure-orchard-conversion-replication-protocol-2026-07-19.md`;
- `secure-orchard-conversion-replication-manifest-2026-07-19.json`;
- `secure-orchard-conversion-replication-2026-07-19.json`;
- `cgauto/secure_orchard_conversion_replication.py`.
