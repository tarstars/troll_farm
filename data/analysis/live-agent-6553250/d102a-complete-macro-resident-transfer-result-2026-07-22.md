# D102a complete-macro resident transfer audit — result

Date: 2026-07-22  
Status: integrity pass; mechanism pass; value and robustness fail

## Verdict

Retain the exact D40 work-conserving complete macro controller as a role-transition teacher, but
do not package it and do not replace the resident with it. D40 reproduces the public top-three
mechanism—persistent renewable production followed by a larger workforce—but loses heavily to the
resident because the extra production and longer games increase opponent output much more than
own output.

This closes wholesale D40 transfer. The useful object is its transition supervision: when to keep
a producer active, capitalize accumulated materials, and allocate later workers. Its complete
policy is not a candidate.

## Reproducibility and integrity

The frozen panel contains 32 fresh official maps (`9_824_100..9_824_131`), both seats, all eight
frozen opponent families, and both policies: 1,024 rows or 512 paired task cells. The one-worker
and 20-worker TSVs are byte-identical, SHA-256
`0120c834a88ec178f923dd741a129bf13fdb5d842cad55f54ec765be793046f4`.

Every frozen integrity gate passes: the grids are exact, all games terminate with exact score and
return identities, both controllers are called directly, and D40 has zero invalid commands and
deposit-prediction failures. There are zero unresolved provenance failures or ambiguous births.

The audit required two measurement-only corrections, both preserved in the protocol's audit
trail. A one-map smoke showed that D40's expected target-disappearance job invalidations are not
invalid commands, so the full panel was moved to untouched seeds. The first full pass then exposed
four same-kind simultaneous PLANT merges in two mirrored resident-versus-resident cells; the exact
engine identifies these as joint births, not ambiguous births. The runner added an explicit joint
owner and the exact frozen panel was rerun. Neither correction changes commands, scores, states,
mechanism thresholds, or value thresholds.

The one-worker run took 112.387 seconds and the 20-worker run 112.770 seconds. Thus this workload
has no useful in-process parallel speedup on the current host; additional workers only add
contention under the available CPU quota/cache behavior.

## Mechanism result

All nine mechanism gates pass.

| Measure | D40 | Resident |
|---|---:|---:|
| Creates an owned crop | 100.00% | 100.00% |
| Reaps an owned crop | 90.43% | 9.77% |
| Reinvests after an owned-crop receipt | 83.98% | 8.59% |
| Reaches worker three | 87.11% | 0.00% |
| Mean final workforce | 2.855 | 2.000 |
| Mean owned crops created | 33.355 | 11.086 |
| Mean owned-crop harvest units | 18.293 | 10.748 |
| Mean reinvested crops | 22.209 | 0.834 |

D40 therefore contains the missing productive-workforce mechanism identified by D101. The
resident reliably plants, but almost never closes the harvest/replant loop and always finishes
with exactly two workers.

## Value and robustness result

Every frozen value and robustness gate fails.

| Paired measure (`D40 - resident`) | Result |
|---|---:|
| Mean margin | -48.396 |
| Symmetric 5% trimmed mean margin | -46.325 |
| Map-clustered 95% lower bound | -61.706 |
| Mean own score | +17.547 |
| Mean opponent score | +65.943 |
| Strict improvement rate | 29.30% |
| Strict regression rate | 70.70% |
| Worst-decile mean margin | -211.115 |

D40's negative-margin rate is 36.33% versus 12.11% for the resident; its catastrophic-margin rate
is 11.13% versus 2.15%. Only `silver_boss` is positive (`+11.656`). The other family deltas range
from `-18.125` against `compact_gold` to `-120.922` against `legend_balanced`. Both seats lose by
about 48 points, so the result is not a seat artifact.

D40 raises own score by 17.5 points, but raises opponent score by 65.9 points. Its mean terminal
turn is 300.717 versus 258.141 for the resident. The direct interpretation is that an
unconditionally productive scheduler prolongs the match and leaves valuable field output for the
opponent to compound. Production persistence is necessary, but it must be coupled to source
control, suppression timing, and opponent-aware role allocation.

## Next eligible branch

Do not reopen wholesale D40 transfer, generic persistent producers, phase handoffs, static
selectors, or online Monte Carlo. The next discriminator is deeper rank-one policy archaeology at
the per-worker task-state level. D88 showed that public `MSG` streams can reveal a compact task
grammar; D95/D101 show that current rank-one `delineate` exhibits the desired production,
capitalization, and suppression split. First establish whether its messages expose a deterministic
finite-state grammar with command coverage sufficient for faithful reconstruction. Only then
freeze a controller experiment.

## Artifacts

- `d102a-complete-macro-resident-transfer-protocol-2026-07-22.md`
- `d102a-complete-macro-resident-transfer-{a-jobs1,b-jobs20}-9824100-9824131.tsv`
- `d102a-complete-macro-resident-transfer-result.json`
- `rust/src/bin/d102_complete_macro_resident_transfer.rs`
- `cgauto/analyze_d102a_complete_macro_resident_transfer.py`
