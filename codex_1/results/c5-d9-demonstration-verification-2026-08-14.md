# c5 D-9 demonstration execution verification

**Verdict: `VERIFIED`**

Four constructed cases were run through the panel's own `fuzz_panel.eval_p1` path.
This verifies instrument capability only; it makes no live-corpus coverage claim.

| case | expected D-9 kinds | observed D-9 kinds | pass |
|---|---|---|---|
| `parent_t2_candidate_never` | `['train_missing']` | `['train_missing']` | `True` |
| `parent_t2_candidate_t4` | `['train_late']` | `['train_late']` | `True` |
| `both_t2_different_talents` | `['train_stats_differ']` | `['train_stats_differ']` | `True` |
| `both_t2_identical_talents` | `[]` | `[]` | `True` |

The three broken cases fired only their named paired clause; the identical-turn,
identical-talents case was silent. The raw gate returned no inherited or dropped D-9
channel in any case.
