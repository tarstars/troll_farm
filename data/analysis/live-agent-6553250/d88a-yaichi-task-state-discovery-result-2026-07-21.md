# D88a yaichi task-state archaeology — discovery result (2026-07-21)

## Decision

**Repair the frozen task vocabulary as D88b; validation remains unopened.**

D88a's discovery accounting is exact, and its mechanism evidence is strong, but the preregistered
message vocabulary misunderstood two exposed macro states and one persistent intent. The failure
is therefore a discovery-stage protocol defect rather than evidence against task-state imitation.

## Exact discovery result

The nine sampled historical and ten consumed current games have 100% MSG-turn coverage, 100%
living-unit segment coverage, exact decoded terminal states/scores, zero malformed, duplicate, or
foreign segments, zero provenance underflows, and exact PLANT/HARVEST species lineage.

The frozen vocabulary recognizes only 92.03% of sampled-historical and 91.35% of current unit
turns. All 873 unknown segments belong to two coherent prefixes observed in discovery:

- `GET_SEED_TREE`: 741 unit-turns, all issuing `MOVE`;
- `ATTACK`: 132 unit-turns, all issuing `MOVE`.

Among already recognized states, the only 558 command-table mismatches are persistent `PLANT`
intent reporting while the unit executes `HARVEST` (452) or `PICK` (106). Every other recognized
state/command pair conforms. Thus the message reports the controller's current macro task, not
always the primitive action name.

The discovery mechanism itself is stable. In seven sampled-historical renewable games, bank
bootstrap precedes renewable maintenance in 6/7, bank/own-crop tokens supply 97.09% of starter
plants, 162/163 own-crop tokens are replanted by the same worker, and the trained worker has only
658 successful CHOP plus 196 DROP actions. Six games contain the full ordered lifecycle. In six
current renewable games the corresponding rates are 6/6, 90.11%, 203/203, 807 CHOP plus 214 DROP,
and 6/6.

The deterministic 20-worker discovery rows are
`d88a-yaichi-task-state-discovery-rows-b.jsonl`, SHA-256
`39671ed09669c389145f450e8ace4a176723b52f40435fc5409d1c507060530d`; aggregate JSON SHA-256 is
`4844c4503dfa509ea53de36931ef3353778913498a0820eabefbf6acf198abdd`.

## Allowed repair

D88b may add the two discovery-observed macro states with their observed command mapping and may
model `PLANT` as the persistent task whose primitive actions are PICK, HARVEST, and PLANT. It may
not inspect validation, add any other alias, change lineage accounting, change mechanism gates, or
use outcomes to alter the controller hypothesis.
