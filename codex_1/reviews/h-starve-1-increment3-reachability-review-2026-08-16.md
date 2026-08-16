# H-STARVE-1 increment-3 reachability review — 2026-08-16

Verdict: **REVISION_REQUIRED; `GENERATOR_GAP` IS NOT YET ESTABLISHED FOR OSC-001 OR
OSC-012. OSC-031 REMAINS WITHDRAWN.**

Reviewed artifact `f5a9d2e90944789845f4827c7f7827d568a48f12`. The static BFS
does match the bot's own navigation model: both ignore unit occupancy and traverse the same
static walkable cells. Transient peer blocking therefore cannot explain an absent candidate in
the bot's own path model.

The new predicate nevertheless answers only “can the unit topologically reach any plant?”, not
“does this unit have a resource action?”:

1. **OSC-012 is the decisive counterexample.** The reported parked unit 2 has
   `harvest_power=0` and `chop_power=0`. It cannot harvest or chop any plant. Counting every
   reachable plant as work makes `unitWork=193/193` even though plant reachability provides this
   unit no action. The `GENERATOR_GAP` label is unsupported and may be false for this row.
2. **OSC-001 also needs eligibility, not mere reachability.** Unit 2 has harvest power 1 but
   chop power 0. A reachable fruitless plant is not currently harvestable, and it cannot be
   chopped. The predicate must join plant fruit/state and the unit's powers on each turn before
   claiming an available action.
3. **Cargo must be reachable to its sink.** `sum(u.carry) > 0` is treated as work without
   verifying a static route to a valid bank/plant action. That mirrors the coarse player-level
   terminal predicate but is not a valid per-unit narrowing on a disconnected map.
4. **Copying the authority does not prevent drift.** `unit_offered_work` duplicates clauses
   rather than calling a parameterized shared predicate. More importantly, the player-level
   authority relies on the collective abilities of all own units; substituting one source cell
   while discarding that collective capability assumption is not a semantic narrowing.

The increment-2 temporal defect also remains: the cause is decided by `unit_work > 0` anywhere in
the window, rather than the same-turn conjunction between generator output and an eligible unit
action. OSC-031 still reports unit 2 instead of the frozen P4 anchor unit 0, so it remains
withdrawn regardless of predicate strength.

Required repair: after the five instrument-validity fixes already ordered, define and test a
per-unit, per-turn **eligible action** oracle in the bot's static-navigation frame:

- carried payload plus a reachable legal sink/action;
- harvest power plus a reachable plant with harvestable fruit;
- chop power/free capacity plus a reachable live plant (and any other generator-relevant action
  explicitly in scope).

Report the exact conjunction counts with direct candidate kinds/chosen command. Controls must
include a reachable plant with a zero-power unit (must be NO unit work), a fruitless plant with a
harvest-only unit, a genuinely harvestable plant, a chop-capable unit, and a disconnected carried
payload. Until those controls and correct anchor selection pass, the raw MAIN/no-commit/all-WAIT
facts remain the only trusted findings.
