# H4 opponent-bill deniability census protocol — 2026-07-31

## Question

In exact-resident catastrophic games where the opponent successfully trains worker three
before the permanent score crossover, what PLUM/LEMON/APPLE/IRON bill was paid, how much
of it necessarily came from post-start deposits, and could one replay-observable resident
action have made the original TRAIN unaffordable?

This is the read-only diagnosis required by the independent H4 review. It does not
implement timed denial, reuse Phase 21 scoring, simulate terminal alternatives, or
authorize an experiment.

## Frozen population

Use only the 200 exact resident games named in
`d159a-current-resident-all-finished-effect-refresh-raw.json`, SHA-256
`97dc82a730b5a691f2bf63036834b1a9ed23bc186b00d09b874ac092efddf443`.
The accepted D159 result has SHA-256
`bd3fe4571aec423cdb57d514a2f610c0dcfe9845099b5500a6721e98d72965ac`
and records 200/200 exact identities, zero unknown diff updates, and the existing
open-product partition. Read each named raw game and processed trajectory in place; do
not enumerate or open any other game.

The primary cohort is:

1. terminal resident margin ≤ −100;
2. an exact successful opponent TRAIN with `n_before=2`;
3. the TRAIN occurs strictly before the permanent resident score crossover.

Report all catastrophes and all successful opponent third-worker TRAINs descriptively,
but compute materiality gates only on that primary cohort.

## Exact reconstruction

- Parse the requested talents from the opponent's issued TRAIN command and require the
  opponent unit count to increase on that turn.
- Use the referee cost exactly:
  `PLUM=n+ms²`, `LEMON=n+cc²`, `APPLE=n+hp²`, `IRON=n+chop²`, with `n=2`.
- Require the pre-TRAIN bank to cover every charged item and the post-turn state to match
  the successful payment after accounting for same-turn resolution order.
- Track every successful opponent HARVEST, DROP, MINE, PICK, PLANT, earlier TRAIN, and
  carry change through the decoded states and issued unit commands. Unknown changes are
  an integrity failure, never silently assigned.

IRON terrain is non-depleting under the referee: MINE creates
`min(chopPower, freeCapacity)` iron for every legal command and does not consume a shared
stock. Starting inventory is also unreachable. Neither is a deniable source.

## Fungible-bank attribution

Banked items lose token identity. Preserve that uncertainty as exact intervals rather
than selecting FIFO or LIFO.

For each bill item at the third TRAIN, reconstruct:

- remaining starting-stock capacity after earlier exact TRAIN payments;
- total post-start deposited units and their exact acquisition/deposit batches;
- minimum/maximum starting-stock contribution to the bill;
- minimum/maximum post-start-deposit contribution to the bill.

For a source batch, its minimum bill contribution is the amount that remains necessary
after every other admissible unit of that item; its maximum is bounded by both batch size
and bill size. If no individual source is mandatory, report source attribution as
ambiguous even when a deposit contribution is mandatory in aggregate.

## Strict one-action causal block

A game is `strict_one_action_blockable` only when all of the following are proven from
the recorded pre-action state and referee order:

1. an opponent fruit acquisition/deposit batch has a positive minimum contribution to
   the original third-worker bill;
2. replacing exactly one resident unit command with one legal HARVEST or lethal CHOP
   removes enough units of that bill item that the original TRAIN bank falls below its
   exact cost;
3. the resident unit is already on the source cell in the relevant pre-action state;
   no hypothetical multi-turn MOVE prefix is credited;
4. simultaneous resolution order, harvest power/capacity, fruit count or tree health,
   and intervening regeneration cannot restore those units before the original TRAIN;
5. no unobserved or attribution-ambiguous source is required for the causal claim.

Also report a looser `reachable_upper_bound` using exact BFS/ETA before acquisition, but
it is descriptive and cannot clear a gate. A MOVE opportunity is not a one-action causal
denial.

Class the displaced recorded command as idle, movement, banking/logistics, suppression,
production, or other. This describes opportunity cost; it does not estimate terminal
value. Report alternate visible supply and original-bank surplus, but do not claim a
lasting cancel when only the original TRAIN turn is blocked.

## Integrity and materiality gates

All integrity gates must pass:

1. exact 200-game D159 ID set, identity, raw/trajectory presence, and no duplicate IDs;
2. zero decoder unknown updates or command/state train mismatches;
3. exact resident/source/manifests hashes;
4. every successful third TRAIN has an exact talents vector, bill, pre-bank coverage,
   and unit-count transition;
5. no game outside the frozen list and no alternative outcome influences eligibility.

Return `MATERIAL_PREFLIGHT_ONLY` only if all are true:

- primary cohort contains at least 8 games and at least 4 opponent identities;
- at least 25% of primary games are `strict_one_action_blockable`;
- strict-blockable games cover at least 3 opponent identities and both resident seats;
- at least 50% of strict blocks displace an idle or movement command rather than an
  observed banking, suppression, or production command.

These are coverage gates for a separately reviewed causal preflight, not a value or
candidate gate.

## Frozen verdicts

- `MATERIAL_PREFLIGHT_ONLY`: all integrity and materiality gates pass; request a separate
  continuation decision, with no experiment implicitly authorized.
- `NO_MATERIAL_DENIABLE_BILL`: integrity passes but at least one materiality gate fails.
- `UNIDENTIFIABLE`: exact replay observables cannot establish the required bill,
  provenance bounds, or strict causal-block classification.

## Stop rules

Stop after analyzer/tests, compact JSON/report/manifest, canonical closeout, and peer
handoff. Do not fit a selector, tune a threshold, implement a score/target branch, edit
the resident, open maps/games/ranges, create a candidate, submit, or touch Arena.
