# D89a banana seed-factory controller blueprint (2026-07-21)

## State hierarchy

The resident remains the fallback policy. The new layer owns only the two roles after the resident
has successfully materialized worker two.

### Starter: persistent farm task

1. Snapshot the initial banked BANANA count on turn one.
2. Before worker two exists, emit the exact resident policy.
3. On the first observed two-worker state, begin bootstrap. Repeatedly travel to the home shack,
   PICK one BANANA, travel to an empty home-side cell, and PLANT it until the initial count has been
   successfully planted or bank supply is unavailable.
4. Rank the first seed-reserve cell by water adjacency, home accessibility, opponent distance, and
   deterministic cell order. Keep one surviving bank-sourced BANANA protected from own chopping;
   if it disappears, promote the best surviving bank crop, then any surviving owned BANANA.
5. When empty-handed, harvest a ripe tracked own BANANA, preferring the protected reserve and then
   reachable bank-sourced crops. If it will ripen by arrival, travel early; otherwise fall back to
   resident useful work while retaining the task.
6. After a tracked-own-crop harvest, carry the BANANA to the nearest reachable empty conversion
   cell and PLANT. Return to seed acquisition. Never DROP renewable seed merely because the farm
   task is between actions.
7. Carrying wood, iron, or a non-BANANA fruit takes precedence and uses resident bank logistics.

### Trained worker: wood/logistics task

Keep the resident's trained specification and training time. After activation, accept only
CHOP/MOVE toward a nonprotected tree, RETURN/MOVE to the bank, DROP, or WAIT. A resident-selected
PICK, PLANT, HARVEST, or MINE is replaced with the best existing wood/bank candidate. The worker
never consumes reproductive stock.

### Shared safety

The protected reserve cell is excluded from both units' tree targets and movement conflict
resolution. Candidate state is reconciled from observed next-turn plants, so failed PICK, PLANT,
HARVEST, death, opponent removal, or collision cannot invent progress. Endgame feasibility may
bank an unspendable seed rather than strand it.

## Why this differs from closed branches

- It is not the single Apple secure orchard: the reserve feeds a continuing BANANA-to-wood queue
  and does not idle the starter at the mother.
- It is not sparse farming: bootstrap is the complete initial bank stock immediately after worker
  two, not a late one-tree/two-tree scarcity gate.
- It is not D87: only tracked owned crops enter renewable flow, and their descendants remain in a
  persistent farm task.
- It is not the fixed productive Gold grammar: workforce count/training remain resident-exact and
  the reproductive reserve is explicit.

The first implementation is intentionally one frozen controller, not a threshold sweep. Telemetry
must expose every activation, bootstrap attempt/success, reserve promotion/loss, own-crop harvest,
renewable replant, trained-role rewrite, and preactivation mismatch.
