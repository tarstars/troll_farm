# D51a workforce-history opponent population — frozen protocol (2026-07-21)

## Question

D50 proves that a population of recombined complete controllers adds real field support, including
three catastrophic confirmation games, but fixed turn-100/150 boundaries leave worker-rich at
11/28, rich-immediate at 3/9, and rich full at 0/9. Rich field replays reach worker three at highly
variable times (confirmation median turn 114), while coordinated funding and continuous production
replicate across the old 12/9 split.

D51a asks whether switching relative to **observed workforce completion history**, rather than a
global clock, can join a field-supported opening to a compatible productive continuation.

This is calibration on the same fully consumed 160-game field corpus. The original SHA split is
retained only to measure replication; neither half is fresh after D50. Even a pass can open only a
new field-domain model and a separately gated transfer audit, never policy promotion.

## Frozen components and population

Reuse the exact eight D50 component constructors and their current-substrate anchors. Early
components are restricted to the three controllers with field-supported rich openings:

- `v2_hp2_farm`;
- `v2_hp2_late`; and
- `v2_bal_farm`.

Late components are:

- `farm3`;
- `farm4`;
- `lean`;
- `norx_funded`; and
- `v2_hp2_late`.

For every non-identical early/late pair, create four permanent state/history switches:

1. `w3_now`: switch on the first decision with at least three own workers;
2. `w3_plus25`: switch 25 turns after the first decision with at least three own workers;
3. `w3_plus50`: switch 50 turns after that event; and
4. `w3_score60`: switch after worker three exists and deposited score is at least 60.

This yields `14 * 4 = 56` switches. Add the eight unchanged anchors for exactly 64 policies. The
wrapper resets its history on turn one, records the first three-worker turn once, and latches the
late controller permanently when its trigger first becomes true. The late component receives no
earlier decisions and begins with empty internal memory from the actual interactive state. No
fixed global turn, opponent identity, replay action, future state, random choice, or outcome enters
the trigger.

## Data and execution

Run exact `b100_e6` as local player 0 against all 64 policies on the same 160 exact Phase-21 maps.
Emit the first triggered switch turn (`0` if never) alongside the unchanged opening, turn-50,
turn-100, terminal, and production counters. Run the full 10,240-cell matrix twice with all
available CPU parallelism and require byte identity.

Frozen inputs:

- observed signatures SHA-256:
  `c94e3a188913b45c853242bb6a83e5d07f5726dea6c866a1cb1130450d5ae9bc`;
- map dataset SHA-256:
  `d7e4419fad0594673c795e01b6db9b758d646b9b865f612910513f47ddc18ff0`;
- current baseline/economy/structural/v1/v2 SHA-256:
  `73d441becb6628a9fddd1bf57c1f9e406c9a36489a45141d3c2a924860d557c7`,
  `6fcbdc1057c1b81de47c58037ea309d5d7ca2e54b6d19248594e2ade1732d8c4`,
  `29e85cb293cd527512260e6a083252f126f25557cbd491162abfd600d6fa5a2a`,
  `c18ba0a3a056eb89ce3f9df06c23cc7d3dcf1949cf88e620ed67bb66b58e6a93`, and
  `2a3150540d8b6b563d778ff0a3cca2e0d68c52bb130145030a71a896c2fe073b`.

Do not union D50's rejected fixed-clock policies into the comparator.

## Mechanical and activation gates

Pass mechanics only if:

1. both matrices contain exactly 160 x 64 unique complete cells and are byte-identical;
2. all eight anchor rows reproduce the corresponding current-substrate rows on all known fields;
3. every switch preserves its early anchor's exact first command;
4. at least 45/56 policies trigger in at least 16 maps and every recorded switch satisfies its
   exact workforce/history predicate; and
5. at least 35% of the 8,960 switch cells differ from the early anchor's complete checkpoint /
   terminal signature.

## Calibration support gates

Apply the unchanged frozen field-continuation scorer. Against the regenerated current legacy union,
the **confirmation** half must reach every D50 absolute and incremental target:

- overall macro/full at least 56/36 and increments at least +5/+3;
- catastrophic macro at least 7/19 and increment at least +3;
- worker-rich macro at least 12/28 and increment at least +4; and
- rich-immediate macro/full at least 4/9 and 1/9, with increments at least +2/+1.

To reject a confirmation-only fit, discovery must also add at least five overall macro games,
three worker-rich macro games, one catastrophic macro game, one rich-immediate macro game, and one
rich-immediate full game. No legacy-covered game may be lost on either split.

Report trigger rates/turns, support by trigger and early/late pair, nearest distances, named
opponents, coverage multiplicity, and every newly supported critical game.

## Decision rule

- **Pass:** freeze D51 as a calibrated opponent-population mechanism. Before it can judge or train
  a candidate, require a separate transfer audit on a different interaction corpus or explicitly
  authorized new field evidence.
- **Fail with broad activation:** close whole-controller switching, including more elapsed-time or
  score thresholds. Advance to a procedural factorized job allocator with hybrid workers and
  transactional resource revalidation.
- **Fail mechanics:** amend only the machinery before reading support.

No fresh map, TestSession game, submission, Arena action, or resident change is authorized.
