# Mutation ledger (generated — do not hand-edit)

Source: `results/mutation-results.json`  
manifest sha256 `686ce17d56890973314acf94a0089be5052fe1ee53c3d603d879f5e269caa989`  
runner sha256 `8dbf4f7774a2cdc014e702675cf9fcf3e051b57f91fcf914782451bc706dd519`  
probe corpus sha256 `9afe7f3cf3cb073158e67226ddbed31a750cda19900fc031853195cb8b0f3ddb`  
python 3.12.3, control green: True

Pinned sources:

- `conversion_race_oracle.py` sha256 `e0896e3f7cb2c7ac4ced35350469d704432f8c7a1a8a4c9c4ce41495ca13ecf7`
- `test_trace_detectors.py` sha256 `28bbe54f03093ce58bc9da039019a71c0af2dd8c252c19ee0820d7d0ed1b679e`
- `trace_detectors.py` sha256 `59dce10dc87797bc6b1b8da0f628f4ddd82b561d93946fa91453d2ea40805209`

Totals: **63 mutants run, 51 caught, 12 survived** (kill rate 81.0 %). `caught_by_expected` = 51; caught only by another detector's tests = 0. Liveness: 49 PROBE_SENSITIVE, 14 UNWITNESSED; PROBE_SENSITIVE survivors = 9.

## Per detector

| Det | mutants | caught | caught_by_expected | survived | PROBE_SENSITIVE survivors | kill rate |
|---|---|---|---|---|---|---|
| D-1 | 8 | 5 | 5 | 3 | 3 | 62 % |
| D-2 | 6 | 2 | 2 | 4 | 2 | 33 % |
| D-3 | 4 | 4 | 4 | 0 | 0 | 100 % |
| D-4 | 6 | 3 | 3 | 3 | 2 | 50 % |
| D-5 | 8 | 8 | 8 | 0 | 0 | 100 % |
| D-6 | 9 | 9 | 9 | 0 | 0 | 100 % |
| D-7 | 8 | 6 | 6 | 2 | 2 | 75 % |
| D-8 | 10 | 10 | 10 | 0 | 0 | 100 % |
| D-9 | 4 | 4 | 4 | 0 | 0 | 100 % |
| **all** | **63** | **51** | **51** | **12** | **9** | **81.0 %** |

## Full ledger

`result` = CAUGHT / SURVIVED against the full 28-test suite. `liveness` = PROBE_SENSITIVE if the patch changes the mutated detector's probe digest. PROBE_SENSITIVE means the mutation changes probe output on GENERATED traces; it does NOT establish legal-game reachability under the referee. digest over the independent probe corpus, UNWITNESSED if the corpus cannot witness any behavioural change (such a survivor is *not* evidence that the suite is weak).

| id | det | file | result | liveness | mutation |
|---|---|---|---|---|---|
| D1-M1 | D-1 | `trace_detectors.py` | CAUGHT | PROBE_SENSITIVE | window threshold >= 6 transitions (k>=3) -> >= 4 |
| D1-M2 | D-1 | `trace_detectors.py` | SURVIVED | PROBE_SENSITIVE | window threshold >= 6 transitions (k>=3) -> >= 8 |
| D1-M7 | D-1 | `trace_detectors.py` | CAUGHT | PROBE_SENSITIVE | window threshold >= 6 transitions (k>=3) -> >= 5 |
| D1-M8 | D-1 | `trace_detectors.py` | SURVIVED | PROBE_SENSITIVE | window threshold >= 6 transitions (k>=3) -> >= 9 |
| D1-M3 | D-1 | `trace_detectors.py` | CAUGHT | PROBE_SENSITIVE | A2 progress event 'carry change' deleted |
| D1-M4 | D-1 | `trace_detectors.py` | CAUGHT | UNWITNESSED | A2 progress event 'plant created/removed at u's cell' deleted |
| D1-M5 | D-1 | `trace_detectors.py` | CAUGHT | UNWITNESSED | A2 progress event 'inventory change on a DROP/PICK turn' deleted |
| D1-M6 | D-1 | `trace_detectors.py` | SURVIVED | PROBE_SENSITIVE | period-2 A,B,A,B shape requirement deleted (any motion counts) |
| D2-M1 | D-2 | `trace_detectors.py` | CAUGHT | PROBE_SENSITIVE | D-2 window length <= 12 turns -> <= 3 |
| D2-M2 | D-2 | `trace_detectors.py` | SURVIVED | UNWITNESSED | D-2 window length <= 12 turns -> <= 120 |
| D2-M6 | D-2 | `trace_detectors.py` | SURVIVED | UNWITNESSED | D-2 window length <= 12 turns -> <= 4 |
| D2-M3 | D-2 | `trace_detectors.py` | CAUGHT | PROBE_SENSITIVE | >= 2 PICKs and >= 2 DROPs -> >= 1 each |
| D2-M4 | D-2 | `trace_detectors.py` | SURVIVED | PROBE_SENSITIVE | door-cell restriction on the PICK/DROP events deleted |
| D2-M5 | D-2 | `trace_detectors.py` | SURVIVED | PROBE_SENSITIVE | net-zero-over-window requirement deleted |
| D3-M1 | D-3 | `trace_detectors.py` | CAUGHT | PROBE_SENSITIVE | clause (a) run length >= 2 consecutive turns -> >= 1 |
| D3-M2 | D-3 | `trace_detectors.py` | CAUGHT | PROBE_SENSITIVE | clause (a) run length >= 2 consecutive turns -> >= 3 |
| D3-M3 | D-3 | `trace_detectors.py` | CAUGHT | PROBE_SENSITIVE | clause (b) landing-on-stationary-working-peer disabled outright |
| D3-M4 | D-3 | `trace_detectors.py` | CAUGHT | PROBE_SENSITIVE | clause (a) proxy widened: destination identity dropped, any two own MOVEs on one turn count as a shared target |
| D4-M1 | D-4 | `trace_detectors.py` | CAUGHT | PROBE_SENSITIVE | stall tolerance: 2 consecutive non-decreases -> 1 |
| D4-M2 | D-4 | `trace_detectors.py` | SURVIVED | PROBE_SENSITIVE | stall tolerance: 2 consecutive non-decreases -> 3 |
| D4-M3 | D-4 | `trace_detectors.py` | SURVIVED | PROBE_SENSITIVE | non-progress test d1 >= d0 (stall counts) -> d1 > d0 (only retreat counts): equality semantics flipped |
| D4-M4 | D-4 | `trace_detectors.py` | CAUGHT | PROBE_SENSITIVE | banned non-bank verb set reduced to {MINE} |
| D4-M5 | D-4 | `trace_detectors.py` | CAUGHT | PROBE_SENSITIVE | I-21 forced (full-capacity) commitment start deleted |
| D4-M6 | D-4 | `trace_detectors.py` | SURVIVED | UNWITNESSED | DROP-at-door commitment start deleted |
| D5-M1 | D-5 | `trace_detectors.py` | CAUGHT | PROBE_SENSITIVE | I-12 Ring membership cheby == 1 -> cheby == 2 |
| D5-M6 | D-5 | `trace_detectors.py` | CAUGHT | PROBE_SENSITIVE | I-12 Ring narrowed from cheby == 1 to the four orthogonal doors |
| D5-M2 | D-5 | `trace_detectors.py` | CAUGHT | UNWITNESSED | I-5 orthogonal cutoff 2*CD -> 1*CD |
| D5-M3 | D-5 | `trace_detectors.py` | CAUGHT | UNWITNESSED | I-5 orthogonal cutoff slack +2 -> +20 |
| D5-M7 | D-5 | `trace_detectors.py` | CAUGHT | PROBE_SENSITIVE | I-5 global cutoff slack +1 -> +40 |
| D5-M4 | D-5 | `trace_detectors.py` | CAUGHT | PROBE_SENSITIVE | I-13 cumulative \|Ring\| bound disabled |
| D5-M5 | D-5 | `trace_detectors.py` | CAUGHT | UNWITNESSED | I-13 concurrent \|Ring\| bound disabled |
| D5-M8 | D-5 | `trace_detectors.py` | CAUGHT | UNWITNESSED | water-boost branch collapsed: CD is always CD_wet |
| D6-M1 | D-6 | `trace_detectors.py` | CAUGHT | PROBE_SENSITIVE | clause (a2) opponent-chopper ETA bound <= 2 -> <= 1 |
| D6-M2 | D-6 | `trace_detectors.py` | CAUGHT | PROBE_SENSITIVE | clause (a2) opponent-chopper ETA bound <= 2 -> <= 6 |
| D6-M8 | D-6 | `trace_detectors.py` | CAUGHT | PROBE_SENSITIVE | clause (a2) opponent-chopper ETA bound <= 2 -> <= 5 |
| D6-M9 | D-6 | `trace_detectors.py` | CAUGHT | PROBE_SENSITIVE | clause (a2) opponent-chopper ETA bound <= 2 -> <= 7 |
| D6-M3 | D-6 | `trace_detectors.py` | CAUGHT | PROBE_SENSITIVE | clause (a1) arrival-order tie no longer conceded (<= -> <) |
| D6-M4 | D-6 | `trace_detectors.py` | CAUGHT | PROBE_SENSITIVE | clause (a1) harvest-race arrival-order test deleted entirely |
| D6-M5 | D-6 | `trace_detectors.py` | CAUGHT | UNWITNESSED | clause (b) opponent-harvested-ours replay ground truth deleted |
| D6-M6 | D-6 | `trace_detectors.py` | CAUGHT | PROBE_SENSITIVE | A7 flipped: min own ETA taken over harvest-capable own units only |
| D6-M7 | D-6 | `trace_detectors.py` | CAUGHT | PROBE_SENSITIVE | ETA formula ceil(bfs/speed) -> raw bfs distance |
| D7-M1 | D-7 | `trace_detectors.py` | CAUGHT | PROBE_SENSITIVE | carried-banana overage threshold age > 12 -> age > 0 |
| D7-M8 | D-7 | `trace_detectors.py` | CAUGHT | PROBE_SENSITIVE | carried-banana overage threshold age > 12 -> age > 2 |
| D7-M2 | D-7 | `trace_detectors.py` | CAUGHT | PROBE_SENSITIVE | end-of-game grace window T-6 -> T-600 (everything excused) |
| D7-M3 | D-7 | `trace_detectors.py` | SURVIVED | PROBE_SENSITIVE | banking conjunct 'DROP at a door cell' deleted |
| D7-M4 | D-7 | `trace_detectors.py` | SURVIVED | PROBE_SENSITIVE | banking conjunct 'own inventory[BANANA] increased' deleted |
| D7-M5 | D-7 | `trace_detectors.py` | CAUGHT | PROBE_SENSITIVE | PLANT-as-legitimate-sink exemption deleted |
| D7-M6 | D-7 | `trace_detectors.py` | CAUGHT | PROBE_SENSITIVE | harvest provenance labelling deleted (all acquisitions 'unknown') |
| D7-M7 | D-7 | `trace_detectors.py` | CAUGHT | PROBE_SENSITIVE | lost_bananas episode emission deleted |
| D8-M1 | D-8 | `trace_detectors.py` | CAUGHT | PROBE_SENSITIVE | base predicate cell set diag(tent) -> orth(tent) |
| D8-M2 | D-8 | `trace_detectors.py` | CAUGHT | UNWITNESSED | I-7 ownership tie no longer conceded (< -> <=) |
| D8-M3 | D-8 | `conversion_race_oracle.py` | CAUGHT | UNWITNESSED | CONVERSION_RACE_ORACLE race strictness < -> <= (tie now conceded to us) |
| D8-M4 | D-8 | `trace_detectors.py` | CAUGHT | UNWITNESSED | oracle result ignored: the conversion race is always won |
| D8-M5 | D-8 | `trace_detectors.py` | CAUGHT | PROBE_SENSITIVE | ownership-flip precondition ignored (lost forced True) |
| D8-M6 | D-8 | `conversion_race_oracle.py` | CAUGHT | PROBE_SENSITIVE | opponent deadline = arrival only (ripeness dropped) |
| D8-M7 | D-8 | `conversion_race_oracle.py` | CAUGHT | UNWITNESSED | opponent deadline = ripeness only (travel dropped) |
| D8-M9 | D-8 | `conversion_race_oracle.py` | CAUGHT | PROBE_SENSITIVE | growth-aware exact_chop_turns -> static ceil(health/chop) inside CONVERSION_RACE_ORACLE (the round-3 host-review counterexample) |
| D8-M10 | D-8 | `trace_detectors.py` | CAUGHT | PROBE_SENSITIVE | exemption conjunction 'lost AND race_won' -> disjunction |
| D8-M11 | D-8 | `trace_detectors.py` | CAUGHT | PROBE_SENSITIVE | health-decrease confirmation of an executed chop deleted |
| D9-M1 | D-9 | `trace_detectors.py` | CAUGHT | PROBE_SENSITIVE | \|own units\| == 1 qualifying guard deleted |
| D9-M4 | D-9 | `trace_detectors.py` | CAUGHT | PROBE_SENSITIVE | \|own units\| == 1 qualifying guard -> == 7 |
| D9-M2 | D-9 | `trace_detectors.py` | CAUGHT | PROBE_SENSITIVE | banana-attributable restriction widened to any resource argument |
| D9-M3 | D-9 | `trace_detectors.py` | CAUGHT | PROBE_SENSITIVE | ordering boundary t >= first_train -> t > first_train |

## Entries excluded from the totals

| id | det | result | liveness | why excluded |
|---|---|---|---|---|
| D8-M8 | D-8 | SURVIVED | UNWITNESSED |  |
| D3-M4-RETIRED | D-3 | SURVIVED | UNWITNESSED | RETIRED, excluded from totals. This patch is INERT: the command parser files a command under Trace.cmds(t).by_unit only when cmd.unit_id is not None (trace_detectors.py:410), and WAIT is parsed with unit_id None (:393-394), so cmd_of (:493-494) can never return a WAIT command and the widened branch is unreachable. It is kept and re-run so the delta against the 2026-08-08 ledger is auditable, and replaced in the counted set by D3-M4 (destination identity dropped). |

## Mutated-file SHA-256

| id | mutated `target file` sha256 |
|---|---|
| D1-M1 | `1585ca9cc85512e30402d2e391e5857e7b3b01cf3df321e5c1a7c102ee6027c6` |
| D1-M2 | `3d8c71a7bcc0e1f45e7cdb3257ba4733757609a7d6a65f1878de511a8d154c44` |
| D1-M7 | `51d5150374cb668945a36ec6a61f87653e2515b4d54136113eb80901438505fc` |
| D1-M8 | `1a08f891a1610ecbdcf503b5ae6c7322babd91ca96a1a24f453e481d39aae5f4` |
| D1-M3 | `9350539f4a4841a2452a9cab2d0c6d8f056d1496289f3e100826f4c60218cd97` |
| D1-M4 | `0cdf157776a5e10189ee54b72b43f0fc56f199abdcb13ee130bf82fbde27272f` |
| D1-M5 | `777d8800c284952b09893636d6cc311d7cd8366cd22d25f54a8fd83c2eb11c55` |
| D1-M6 | `59ec0afdc5f9ac5221a8158babc260a303cb22133624c9b04d705380279b174f` |
| D2-M1 | `cbf5a75f984850482f828682cc910cef571084923c9af65a8f548e20284e8c7a` |
| D2-M2 | `61760c68ba1d42756de790f3a334e7170de73f799cba0fa6dc14a4b51fbb9d00` |
| D2-M6 | `dbe773464cc5f08854db47f29d635fa6bd36932c21c439a51c0e40e3b05abf5c` |
| D2-M3 | `9a9bde2f1dd6abd693ab3b04b0a58088edcd5a379b0993565801426d76eda451` |
| D2-M4 | `b5c88cbca41132e29d231744785e8775009a0031636a3ccd7a571a5167d557e5` |
| D2-M5 | `159bfd140675d37fcaf3ceaa305fc2927746ad168a520f8a18ca7e4aea7e867c` |
| D3-M1 | `507f34fd91c45cc6fcaf85368addaafd36d0aebf0288ec65d8c5003849a283cc` |
| D3-M2 | `df9b20444f1e7a2fa63c541ad715d12cb5f695d4e7e2624a0135b5b0507e301a` |
| D3-M3 | `413f467f1a7baf05e4dfae9fe413562ae8ea402565119bf8ae063dc5540348db` |
| D3-M4 | `ff3f39990b1cfbbe6303267eefd8f23dad5573e535d879a292e1ceba04cd5cad` |
| D4-M1 | `d4dad8b0162948a1cd121e62d432e9164a1d23ea73c16fe936364a1b8c90e8bd` |
| D4-M2 | `69e187497850f09c56ed607d302c13cc3df88e570cfd51d61d5426d80b76890a` |
| D4-M3 | `8f976d25fe0a373aaf884dd8146a7a769d4ecf64720686da2bb22290a38f023b` |
| D4-M4 | `3c9097ac3d6034820cbf9181c03f2ddee0e33437016e420af2f79240cef2261c` |
| D4-M5 | `f5b534f7557c996f2dd537a1121fadd66d0497897d2d5d14a2f9cc881a68c773` |
| D4-M6 | `6cb1c8e9fc09fda732bde2e00d82c4be4c23df7b363ff5f3674da364a6000584` |
| D5-M1 | `51093365f2ef1ab3cb05dc5f92cfb5d1333ed357cdd258ac9ab62a93282a84e5` |
| D5-M6 | `4368e83fe9ad5afe2b17d0760f1b66615dbe251444214a32aeb420217a30908b` |
| D5-M2 | `00ef01fdb5cb2236cfe61b84bf2519f32112013210403c2f050fe81c986a1fb2` |
| D5-M3 | `16e8cdd84d3311cf067ef7c50b6ee80de4e9476f0cc6bd18d7693679750a2862` |
| D5-M7 | `03b76be7fa8df2f6c9d5e8890848f759d0493a5664e8f1aa55a65c32da123bc6` |
| D5-M4 | `e03627eb966e3476f188241a362e6df2a36d3e18f846defd3ffa2b57663890dc` |
| D5-M5 | `547b6dc06301387b083d14ad1891538ef238b4762f3fcdaf873e46594f69fb6e` |
| D5-M8 | `fc9d2dd4c4a5e90e7f08c9bc499826f6fb045eb60ee96e3b4c69a408fee7a6e4` |
| D6-M1 | `7af117d3ded6fd9abc53dd5007f2495929da76b7e9fd42a6ff455db9b0d358c1` |
| D6-M2 | `65a5620b835d3abac064dc1027a3b7a491f6583ae2671235fa812084a224de2e` |
| D6-M8 | `b6b300f719205a99ec6b29b3aa36b40e7eba2194be624d1dded1917875c99896` |
| D6-M9 | `41b420f4631a3bda98cbceade1abfeea1be257c428a6613a4d6b8bd83204ba4f` |
| D6-M3 | `6e1e7f1926a54ca9901d7cd89eb958000079f1045b2ce3266438e9b74d935667` |
| D6-M4 | `23482d03c494ca3868e90dd5b37e6c6ca650922f7c58ebcf40cc9e79ef39d974` |
| D6-M5 | `858fe8c1c6f6947244c96ae80559c5164fdeb610400a0720bf868950aeeb6218` |
| D6-M6 | `8823aa638e22775d5f4e55a931941e95a1e4003b53ece72bf76cbf74cc944529` |
| D6-M7 | `8bb35b4bb8cccb71fe3c481172fd16a7f5414361b4d1210099edf29f029a1624` |
| D7-M1 | `3ae743e502e396374bb639b262314b7a399de53663d7e64c8d64ce0024c55228` |
| D7-M8 | `8e46e7cc72d6519ac27e677911cf7920142f2079a20b88f05faefa152a17b938` |
| D7-M2 | `737ade04d5d8431d541377d28b8b499075d472bc85ec33e04e3c1b05fb30f20e` |
| D7-M3 | `f51a08909496819fb26ff777f45dddc1b61d8d034c1d43789ac5824ecda961e3` |
| D7-M4 | `54a4c0b0fe327b990d0eb91d46bbc4f4011f4dcc0fec5626a98480d07d05a441` |
| D7-M5 | `484408b0269f7554aa84994759d8de30cf83ee504b2a6cab5f7c24b67c9d0290` |
| D7-M6 | `0a08d69e4eab02da504c5db45c9768ef5cb80fc66ae96364edcc2fcad90635c6` |
| D7-M7 | `49786ce939c2d96f2df09169269a2be3e225e70b4192e879e3da7795e8d47c37` |
| D8-M1 | `68d434cb059ebc76bc1792d5fc91a503f790df032f24346e85bb25727302b712` |
| D8-M2 | `0c468f68dcd4c70353673713f30036bd7a7fa2d9c4d897e86f4394d65141c980` |
| D8-M3 | `1a98c05555d34e05b38894f5be4e230882da6f31f31b03e1afd856a03d79a442` |
| D8-M4 | `112555268a71d702c7f4148ce21ed743f2eb9e21f8b07a585170b6283e60ed59` |
| D8-M5 | `b3c7b66941ed6ef195be47c09a7f5d6aab9397870385c731873df717bb15aa0e` |
| D8-M6 | `78e83f855826c06dd64306015b56c0d5f862facfe9f4caee9e4ae00f3282b43f` |
| D8-M7 | `ab10840e299a70141dd9be99dc43792438838e6b4f4e73a3665997b1986a31b6` |
| D8-M9 | `38b12a2e65cb3900015c5b9efd54e6d53b49d4aa99532ac91059e35fbc53bf37` |
| D8-M10 | `d8b71301d37b42c6da64623ca15187149ea8594bde84104ab0cf1015c304147b` |
| D8-M11 | `dab82ddbe1995abf8b1807ba97d1b41438514629286ae236e93899536d9bd00b` |
| D9-M1 | `03c3a78a4c2b43b57527cf010436c1b3b35ce63e8b8ed37cb433e7e833d475f7` |
| D9-M4 | `3d15ca32928ca8ff1d0ee46f70605bfa96802797feb5094dc84f094512faba97` |
| D9-M2 | `a09640da6b8b8f07a8d67a856733eb47d4b5b845880d88443c18285a5bb35822` |
| D9-M3 | `2424832a09822ce4869680144af84465571b4631c1b6e374f375fcf3faab334b` |
