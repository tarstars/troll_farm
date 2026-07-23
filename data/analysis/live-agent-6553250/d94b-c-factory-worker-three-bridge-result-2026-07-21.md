# D94b/D94c factory worker-three bridge — result

Date: 2026-07-21  
Status: rejected on the consumed D89 panel; no fresh maps opened

## Verdict

Reject and close the exact existing-stock worker-three bridge. D94b fails the TRAIN transaction
gate. Its single preregistered D94c repair changes no command or outcome, and D94c therefore fails
the amendment's immediate-rejection rule. Independently, the treatment loses `91.633` mean margin
to D89 and fails every development value gate. Do not repair, retune, prospectively test, submit,
or replace the resident with this branch.

## Integrity

The one-thread and 20-thread D94b runs and both D94c reruns are all byte-identical: 768 rows / 256
resident-D89-treatment triples, SHA-256
`05b9b2a596f8147ad512743105e800b2d9505999800a84d26923fe89eb347a24`.
The resident and D89 controls match D94a in all 226 shared fields in all 512 rows, including action
and terminal-state hashes. Source tests pass 37/37. The stable constructor remains unchanged.

Because D94c produces the same bytes as D94b, the proposed shack-forbidden move rule was inert in
this panel. It neither repairs the transaction nor changes value.

## Transaction diagnosis

The aggregate `189` attempts are not 42 independent failed games. Their distribution is:

| TRAIN attempts in a task | Tasks | Successful worker three |
|---:|---:|---:|
| 0 | 106 | 0 |
| 1 | 147 | 147 |
| 14 | 3 | 0 |

The three repeated failures are map/seat/opponent cells `9914034/0/mybot`,
`9914035/0/sched_bot`, and `9914036/1/mybot`. A deterministic command-level reproduction of the
first cell exposes the actual engine-order failure. At turn 252 the deposited inventory contains
the exact bill `[PLUM 6, LEMON 6, APPLE 2, IRON 6]`, the shack is empty, and the controller emits:

```text
PICK 0 PLUM
MOVE 3 4 6
TRAIN 2 2 0 2
```

The referee processes `PICK` before `TRAIN`. The PICK spends one deposited PLUM, leaves five, and
the subsequent TRAIN affordability check fails. The starter later banks another PLUM and repeats
the same transaction. The D94b `forbidden_commands` counter incorrectly checks only the dedicated
bridge override; it does not see a fallback D89 PICK selected when the fruit deficits are already
zero. Thus its recorded zero is not a valid proof of the frozen no-PICK invariant.

D94c was frozen around the wrong diagnosis—same-turn MOVE onto the shack—and therefore leaves all
four files identical. Its amendment states that any remaining transaction failure rejects
immediately and permits no further repair. Suppressing same-turn PICK would be a new D94d policy,
not a correction authorized by this protocol.

## Mechanism result

The bridge does acquire its intended material, but too slowly and at too much opportunity cost:

- all 256 tasks enter funding and complete the exact 1,344/1,344 initial BANANA bootstrap;
- successful bridge collections are 1,138 PLUM, 1,193 LEMON, 32 APPLE, and 800 IRON;
- 147/256 tasks train worker three, across both seats and all eight opponent families;
- every trained task records both successful bill-fruit harvesting and successful mining;
- median training turn is 164, range 96--250, and worker count never exceeds three; and
- only 173/256 tasks retain a successful harvest/replant loop, below the frozen 192-task floor.

There are 47,707 two-worker funding turns. That scale is the central mechanism: the bridge can
materialize the bill, but it diverts the two proven D89 roles for much of the game before the third
worker arrives.

## Value result

| Comparison | Mean margin | Map-cluster normal 95% CI | Improve / tie / regress | p10 | Worst |
|---|---:|---:|---:|---:|---:|
| D94 vs D89 | -91.633 | [-132.098, -51.168] | 33 / 2 / 221 | -230 | -367 |
| D94 vs resident | -12.191 | [-31.135, +6.753] | 94 / 2 / 160 | -105 | -238 |

Versus D89, own score falls `115.805`, opponent score falls only `24.172`, terminal wood falls
`29.238`, successful plants fall `25.254`, and own-crop harvest falls `25.418`. Every family is
negative: compact Gold `-75.500`, Gold adaptive `-67.406`, Gold elite `-75.500`, mybot
`-109.125`, printer `-96.688`, scheduler `-106.406`, script `-64.844`, and silver `-137.594`.
Catastrophes (`margin <= -100`) rise from 11 to 35 and negative-margin mass rises from 3,112 to
8,217.

Only two of eight family means remain positive versus resident. The three transaction-failure
cells cannot explain a broad 221/256 regression. Even a mechanically perfect TRAIN turn would not
repair the dominant loss from prolonged bill-funding labor.

## Retained conclusion and next experiment

D89 is a complete two-worker BANANA-to-WOOD economy, but grafting a serialized PLUM/LEMON/IRON
funding detour onto it destroys the production advantage. Strong multi-worker bots must establish
renewable training currency and production concurrently from the opening; they do not become
scalers through this late bridge.

Keep prospective maps `9,914,096--9,914,127` sealed. D95 must move up an architectural level and
reconstruct the early-to-third-worker lifecycle of strong public replay scalers before another
controller is implemented. It should measure per-worker roles, currency source lineage, exact
deposit/PICK/TRAIN transactions, and simultaneous production at the first three workforce
boundaries. It must use already-open public replays and remain read-only.

## Artifacts

- `d94b-factory-existing-stock-worker-three-bridge-protocol-2026-07-21.md`
- `d94c-worker-three-train-transaction-repair-amendment-2026-07-21.md`
- `d94b-factory-worker-three-bridge-development-rows-{a,b}.tsv`
- `d94c-factory-worker-three-bridge-corrected-rows-{a,b}.tsv`
- `rust/src/bin/yamo_orchard_live.rs` — disabled treatment and telemetry
- `rust/src/bin/ownership_aware_complete_economy.rs` — deterministic paired harness
