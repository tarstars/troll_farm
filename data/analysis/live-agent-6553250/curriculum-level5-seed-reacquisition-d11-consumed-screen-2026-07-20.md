# D11 seed-reacquisition expert consumed screen — 2026-07-20

## Verdict

**Prioritize and preregister the expert-only seed-reacquisition branch.**  On consumed seeds
0--499, it raises the exact D10 teacher from 86.60% to **99.40%** while recurrent pressure becomes
more, not less, active.  This repairs the reference expert without changing the task.

## Screened rule

Use the exact D10 environment and current teacher.  Only when all of the following hold for the
active farmer:

- the target worker is already built;
- the tracked player crop is absent;
- total carried inventory is zero; and
- home banana inventory is zero,

select the best reachable banana source using the existing deterministic `best_source` cost
(distance plus regrowth wait).  Harvest if standing on a ready banana source with free capacity;
otherwise move/wait at the selected source.  Once a banana is carried, the untouched existing
teacher path replants it.

The screen gifts no inventory, changes no opponent command, does not alter observations, and does
not reserve seeds prospectively.  Its temporary ignored aggregation test was removed; the small
unwired helper remains as the pre-implementation anchor for D11.

## Consumed result

| Measure | Frozen D10 teacher | Reacquiring expert | Change |
|---|---:|---:|---:|
| Overall success | 86.60% | **99.40%** | +12.80 pp |
| Nontrivial success | 87.12% | **98.98%** | +11.86 pp |
| Worst recipe | 78.57% | **94.64%** | +16.07 pp |
| Worst height | 82.11% | **98.40%** | +16.29 pp |
| Terminal crop | 86.60% | **99.40%** | +12.80 pp |
| Renewable harvest | 87.20% | **99.40%** | +12.20 pp |
| At least two destructions | 98.40% | **98.40%** | 0.00 pp |
| At least three destructions | 89.40% | **96.20%** | +6.80 pp |

The mechanism increase matters: success does not come from evading pressure.  Faster recovery
creates more opportunities for the opponent to complete all three contacts.

## Interpretation

The failure was an expert coverage gap, not an infeasible recurrent task.  This distinction opens a
valuable learning test: the fixed actor already observes plants, fruit, inventory, carried items,
crop existence, and remaining turns, but it has never been required to compose those signals into
post-depletion source reacquisition.

D11 should expose the exact same D10 game to external actions and change only `teacher_actions` for
the new mode.  Fresh controls must prove both reference feasibility and three-contact activation
before the actor is opened.
