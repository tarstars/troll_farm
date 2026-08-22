# H-STARVE-1 increment-2 cause review — 2026-08-16

Verdict: **REVISION_REQUIRED; `GENERATOR_GAP 3/3` IS NOT ESTABLISHED.**

Reviewed artifact `f44fecf6a5cee4da6e9ba7c9590f75263b6bee5e`. The committed
runner reproduces its table, but the causal labels exceed the instrument.

## Blocking findings

1. **OSC-031 audits the wrong unit.** It is a `P4_STALL` whose frozen stalled anchor is
   `window.unit == 0`. `classify()` excludes that unit and reports unit 2 instead. The
   reported unit 2 is not even fully stationary in the frozen classification
   (`distinct_cells_in_window == 2`, wait fraction 0.9947), while unit 0 is the P4
   anchor. The OSC-031 row must be withdrawn.
2. **Player-level work does not prove a per-unit generator gap.** As the handoff itself
   admits, `fuzz_panel.work_remaining` uses reachability from all own units. Work
   reachable only by the dancer makes the predicate true while the parked unit may
   correctly have no reachable action. Therefore OSC-001/012 support only
   `PLAYER_WORK_EXISTS__PARKED_UNIT_ALL_WAIT_UNRESOLVED`, not `GENERATOR_GAP`.
3. **The label logic is temporally too coarse.** `work_turns > 0` labels the entire row
   `GENERATOR_GAP`, even if work exists on a different turn from an empty/all-WAIT
   candidate result. Classification must join world availability and generator output
   on the same `(situation, unit, turn)` and report counts of each conjunction.
4. **Empty-list labeling also assumes the conclusion.** `empty and not committed`
   immediately becomes `GENERATOR_GAP` without consulting world or per-unit
   reachability. An empty list on a genuinely exhausted/unreachable map is not a
   generator failure.

All five instrument repairs from the increment-1 review remain outstanding: correct
unit selection, exact row coverage/duplicate rejection, direct candidate-kind/chosen
logging, per-specimen non-interference, and safe stderr draining. Increment 2 was
published concurrently and does not address them.

## Evidence retained

The accepted raw facts for OSC-001 and OSC-012 remain: explicit blocker unit 2, MAIN on
every window turn, no held commitment, nonempty all-`Target::None` lists. Player-level
work is also present throughout. These facts motivate a per-unit reachability test but
do not decide its result.

Required next artifact: repair the instrument first, then compute resource-action
availability from the selected parked unit's own cell/stats/cargo on each exact turn,
with positive and negative controls against known reachable and isolated units. Keep
the table untrusted and causal headline withdrawn until independent re-review.
