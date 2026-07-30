# A2-1 economy-skeleton external review

Prepared UTC: 2026-07-30T18:45:00Z  
Task: `20260730-a2-1-economy-skeleton`  
Work owner/integrator: `local_codex_1`  
Reviewer: `chatgpt_1`

## Disposition

**ACCEPT `FAILED_K1` and the Architecture-2 programme stop.**

The confirmation is a clean scientific failure of the preregistered Phase-1 workforce
conversion gate, not an evaluator/integrity block. The new scheduler proves the component
mechanics—unambiguous own planting/reaping/banking, opportunistic mining at rosters 2 and
3+, strict command-quality accounting, deterministic thread repeats, and full detector
coverage—but reaches fruit-funded worker 3 by post-step turn 110 in only
**582/2,048 = 28.418%**, below the frozen **40%** floor.

## Protocol, lock, and information chronology

The repository chronology is correct and inspectable:

1. protocol frozen at `b10c813eeb022b54c405aee4be1c30be41a258d1`;
2. implementation published at `2357ec672c971a23f8225ce63f8f1ff4c9214913`;
3. development result and implementation lock published at
   `d8ab0ac0f91ce6b49d571e264943b84882d8bd94`;
4. the single confirmation result and closeout followed at
   `f35e009036726fe08293689e9b5a85a67b248424`.

Git ancestry shows one implementation commit after protocol freeze, one lock commit after
implementation, and no locked source or dependency change between the lock and confirmation
result. The lock records the exact policy, runner, analyzer, referee substrate, module
registry, resident, Cargo, and toolchain hashes; the confirmation narrative records those
hashes as exact.

Development used seeds 9,880,000–031 and passed narrowly at 206/512 = 40.234%. The locked
single confirmation look used the fresh 9,881,000–127 range, both seats, and all eight frozen
families. No outcome-selection or second look is present.

## K1 semantics and provenance

The protocol's C2/K1 denominator is all 2,048 confirmation tasks. A task counts only when a
successful referee TRAIN changes the roster 2→3, the post-step turn is ≤110, and the bot had
already harvested and banked unambiguous fruit from its own generation. Successful TRAIN
also establishes real pre-TRAIN affordability under referee ordering.

The source implementation is consistent with that definition:

- own generations require a successful PLANT on a previously empty cell and exclude cells
  where an opponent PLANT command makes origin ambiguous;
- HARVEST credit is the positive carry delta on a live tracked own generation;
- DROP credit is the matching tracked carry provenance deposited at the shack;
- worker-3 TRAIN is proposed only when cumulative owned bill-fruit was already banked before
  the decision and the real inventory is affordable;
- the successful 2→3 transition records `after.turn <= 110`.

A possible ordering concern was checked: `observe_transition` processes DROP records before
its final TRAIN transition block, while referee task priority is TRAIN before DROP. This does
not create a false-positive gate count, because `commands()` will not issue worker-3 TRAIN
unless `own_bill_fruit_banked() > 0` was already true before that turn. Same-turn DROP cannot
make an otherwise ineligible TRAIN happen.

The separate `bill_needs_owned_fruit` diagnostic remains conservative and is not substituted
for the preregistered A2-0a-compatible gate, as required by the protocol.

## Confirmation integrity

The machine result supports the narrative:

- exact 128 × 2 × 8 matrix, 2,048/2,048 terminal, no duplicates or missing tasks;
- one-thread and 20-thread TSVs byte-identical at
  `efd793552a9a535de94a9429eb73fc82db69e11eaf282e83a8ef5ccc2cffe2fa`;
- 2,048 trajectory records with exact task coverage and all six detectors;
- repeated failed commands: zero;
- global critical and unclassified issues: zero;
- A2-owned issues: 198 / 1,365,709 commands = 0.0145%, in one task, all the allowed
  source-defined `opponent_plant_blocking` reason;
- own bill fruit harvested/banked: 128,979 / 127,614;
- mined iron: 755 at roster 2 and 840 at roster 3+; zero iron-directed moves;
- all opponent-family rates are 27.344%–31.250%, and seat rates are 26.953%/29.883%, so the
  miss is broad rather than a family or seat anomaly.

The analyzer's verdict branch is also correct: `FAILED_K1` is reachable only when coverage,
thread parity, trajectory/detector integrity, and command quality pass, while the 40% fruit-
funded worker-3 check fails. Other integrity/evaluator failures produce `BLOCKED`.

## Interpretation and closeout scope

The charter's amended K1 explicitly says that failure to convert the finite endowment into a
fruit-funded third worker in at least 40% of fresh games by about turn 110 stops the
programme. The integrated STATE, CONSTRAINTS, BACKLOG, approach register, task record, and
ledger preserve the proper scope:

- this scheduler and the current A2 programme stop before Phase 2;
- the result does not prove that all possible economy architectures are impossible;
- no retuning is permitted on the consumed ranges;
- reopening requires an owner-authorized new programme, materially different closed-loop
  representation, new protocol, and fresh ranges;
- no candidate and no Arena action exist.

The descriptive mean margin −113.11 and 1,368 catastrophes are correctly labelled
non-gating Phase-1 context rather than the cause of the verdict.

## Execution-review limitation

This reviewer runtime has GitHub connector access but no project checkout and no direct
network path for cloning. I therefore did **not** independently rerun the requested Cargo
test or analyzer self-test. I inspected the frozen protocol, lock, source logic, analyzer
verdict branch, machine result, commit ancestry, and all shared closeout records; the lock
records `27 passed, 0 failed`, analyzer compile passed, and self-test passed.

This limitation must remain visible. It does not change the K1 conclusion—the observed
28.418% is far below 40%, and any provenance correction could only leave the count unchanged
or reduce it—but it means I am not claiming an independent executable rerun.

## Final review verdict

**Scientific verdict and closeout: ACCEPT.**  
**Independent local command rerun: NOT PERFORMED in this runtime.**  
**Arena/candidate consequence: NONE.**
