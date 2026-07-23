# D78b referee-confirmed CHOP label repair — frozen protocol (2026-07-21)

## Quarantine

D78a's post-run attribution audit found that `crop_provenance()` records every assigned CHOP on a
crop cell, including attempts whose referee summary has no successful damage or wood-collection
event. Across the 1,811 resident crops, it records 834 opponent CHOP attempts; the existing
`successful_events()` helper is also insufficient because it recognizes "damaged a tree" but not
the equally successful "collected N WOOD" fell message.

Therefore all D78a model metrics and its provisional interface decision are quarantined. Preserve
its JSON/row artifacts and do not use their labels, gates, or model result.

## Sole repair

Keep the D78a snapshot, open-only cohort, account partition, deterministic row thinning, eight-turn
horizon, three nested feature families, model fits, thresholds, integrity/support gates, and
decision rule unchanged.

Replace only the target attribution:

1. parse referee summary lines by resolved turn and player;
2. count both `troll <id> damaged a tree` and `troll <id> collected <N> WOOD` as successful CHOP
   effects;
3. require that the same unit's assigned replay command for that turn is `CHOP`;
4. map that unit's pre-action cell to the exact live plant in the decoded state; and
5. label a resident crop-turn positive only when such a confirmed opponent event targets the same
   cell during `t+1..t+8`.

The descriptive terminal-chop label and resident-self-chop flag use the same confirmed mapping.
Every confirmed target event must be a subset of the old attempted attribution for that crop.
Record attempted and confirmed counts and require at least one filtered attempt, so the repair is
actually exercised.

## Execution and decision

Write new D78b rows and result artifacts without overwriting D78a. Repeat once with one process and
require byte-identical rows and identical report content apart from generation time.

Apply D78a's unchanged support and representation gates to the repaired labels. If attribution,
repeat, or any old integrity gate fails, quarantine performance. Regardless of outcome, D78b is a
behavior-representation audit only and cannot create a candidate, open confirmation, or authorize
platform activity.
