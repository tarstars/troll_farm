# Apple and banana orchard design specification

Task: `20260804-orchard-activation-species-audit`  
Owner: `chatgpt_1`  
Status: APPLE design is deployed and evidence-backed; BANANA design is a proposed bounded candidate  
Evidence: eight exact one-hour Arena legs, 1,280 games  
Platform mutation in this task: none

## 1. Executive result

The current **APPLE secure orchard should be retained unchanged** until a fresh closed-loop candidate beats it. It is a protected harvest mother, not a wood tree. APPLE is the right species for that role because the chosen mother cell is water-adjacent: APPLE produces every 2 turns there, while BANANA produces every 4 turns, and mature APPLE health is 20 versus BANANA health 6.

The simple activation refinements discussed so far do not work:

- `require_idle_starter = true` is effectively orchard deletion: it keeps only 3 of 54 observed activations and activates 0 times on the 640 no-orchard exact-prefix trajectories;
- rejecting activation when an enemy can arrive before the first bank ignores tree health and chop time; all 54 observed APPLE activations survive a conservative continuous attack through first harvest;
- replacing only the protected APPLE mother with BANANA preserves exactly the same activation support but approximately halves projected fruit output.

A **self-sustained BANANA orchard remains a valid separate design**, but its purpose must be wood production. It should contain one protected seed mother and one bounded cut/replant slot. The mother is harvested; the child tree is chopped. This is not a like-for-like replacement for the APPLE harvest mother.

## 2. Evidence summary

### 2.1 Repeated live comparison

| Variant | Legs | Games | Mean Arena score | Wins | Catastrophes | Mean game margin |
|---|---:|---:|---:|---:|---:|---:|
| no orchard | 4 | 640 | 23.1075 | 343 | 69 | +8.2328 |
| current APPLE orchard | 4 | 640 | 23.6925 | 381 | 91 | +6.1281 |

Adjacent orchard-minus-no-orchard Arena-score deltas:

```text
+1.60, +2.03, -0.36, -0.93
```

Mean: `+0.585`; median: `+0.620`. Exact enumeration of all `4^4 = 256` ordinary paired-bootstrap resamples gives interval `[-0.645, +1.815]` and probability `0.234375` that the mean is nonpositive. The opponent queues were not paired game-for-game, so this is repeated live evidence, not a clean causal rating estimate.

The stable qualitative effect is polarization:

- orchard queues produced 38 more wins;
- orchard queues produced 22 more catastrophic losses;
- wins increased in all four adjacent comparisons;
- catastrophes increased in all four adjacent comparisons.

A prior complete one-off ablation was also directionally positive for orchard: the exact E7a pre-trial row was approximately 25.3, while the pure no-orchard passthrough finished at 23.27. Queue composition prevents treating that difference as a paired causal estimate.

### 2.2 What happened in actual APPLE activations

The current orchard activated in `54/640 = 8.44%` of orchard games.

At the activation point, the ordinary inner controller wanted the starter to do:

```text
MOVE: 50 games
CHOP:  1 game
WAIT:  3 games
```

Observed orchard lifecycle:

- 52 mothers successfully planted;
- 51 games banked orchard fruit;
- 5,660 APPLE harvested;
- 5,615 APPLE banked;
- median 121 banked APPLE per activated game;
- median 13 turns from activation to first bank;
- 32 mothers alive at game end.

Activation selects difficult game states, so activated-game outcomes are descriptive and must not be read as the treatment effect of the orchard.

### 2.3 Data-quality boundary

- all eight Git LFS replay packages hash-verified;
- full fresh-process command parity: 696/1,280 games;
- exact deployed command prefix through the turn-100 activation window: 911/1,280 games;
- later mismatches are equal-choice MOVE/path tie drift;
- generated alternatives were interpreted only before first divergence and before any deployed-source drift;
- exact matches on initial state + opponent submission + seat across queues: zero;
- no raw replay bodies were duplicated.

## 3. Current APPLE secure orchard

### 3.1 Purpose

The APPLE orchard is a **persistent protected fruit source**. Its purpose is to create a large stream of banked APPLE while the second worker continues ordinary Yamo chopping and banking.

It is not intended to:

- produce wood directly;
- be chopped by our bot;
- fund worker three;
- expand into several trees;
- run on every map.

### 3.2 Static geometry

The deployed implementation constructs orchard geometry from the initial state.

A map is eligible only when:

1. the home shack has at least two orthogonal walkable doors;
2. at least one natural tree exists;
3. every initial natural tree is reachable from the home doors;
4. the median initial natural-tree return distance is at least 8.

The mother cell is selected among home-door cells that are:

- empty of plants;
- adjacent to water;
- at least 11 BFS cells from the opponent's accessible doors.

Selection order:

1. maximize distance from opponent doors;
2. break ties lexicographically.

The selected mother is itself an orthogonal cell next to the tent. This is deliberate: the starter can HARVEST and DROP without a separate return trip. Because the mother occupies a door, at least one alternate door must remain usable by the second worker.

### 3.3 Runtime activation predicate

The current APPLE orchard may activate only through turn 100, and only when all of the following hold:

1. the starter is empty and standing on one of the home doors;
2. worker two already exists;
3. at least one APPLE is in the home inventory;
4. the mother cell is reachable from the starter;
5. the mother cell is empty of a plant;
6. no other unit occupies the mother cell;
7. the earliest enemy chopper ETA to the mother is greater than 8;
8. a non-starter own worker with positive chop power and movement speed at least 1 can still use an alternate door when the mother cell is removed from walkability;
9. reserving the starter does not surrender a currently contestable natural tree that only the starter can secure and bank before the opponent.

The current implementation intentionally does **not** require the starter's inner command to be `WAIT`. The replay audit shows that such a requirement would remove almost the entire orchard behavior.

### 3.4 State machine

```text
Dormant
  -> CarryingSeed
  -> Active
  -> Abandoned
```

#### Dormant

- Inner Yamo commands pass through unchanged.
- Geometry and natural-tree provenance are tracked.
- Activation is allowed only before turn 101.

#### CarryingSeed

- The starter is reserved for the orchard.
- The mother cell is protected from the other worker.
- The starter moves to the mother, picks APPLE at the tent if needed, and plants exactly one APPLE mother.
- If the seed, route, occupancy, enemy ETA, or alternate-door invariant fails before planting, the orchard abandons.

#### Active

The starter follows a fixed loop:

```text
if not on mother: MOVE to mother
else if carrying fruit: DROP
else if mother has fruit and capacity remains: HARVEST
else: WAIT
```

The mother is protected from ordinary chop and movement targets. The other worker must use alternate routes and retains the ordinary Yamo economy.

#### Abandoned

- The wrapper stops intervening.
- Inner Yamo behavior passes through.
- The orchard is not replanted in the current design.

### 3.5 APPLE mechanics on the selected cell

The mother is water-adjacent.

| Property | APPLE |
|---|---:|
| nominal cooldown | 9 |
| water boost | 7 |
| effective cooldown | 2 |
| mature health | 20 |
| first bank after activation | starter travel + 11 turns |
| steady bank interval | 2 turns |

The hard-to-chop tree is an advantage because our bot does not chop it. The protection layer turns health into defensive duration.

### 3.6 Required invariants

1. Exactly one mother.
2. Mother is never an ordinary chop target.
3. Starter ownership is exclusive while CarryingSeed or Active.
4. Other workers cannot occupy, traverse onto, or consume the reserved mother/seed.
5. At least one alternate home door remains usable.
6. No replant loop after loss in the current design.
7. Parent behavior is exact outside the declared orchard activation and reservation surface.
8. No Arena promotion based only on activated-game associations.

### 3.7 Rejected APPLE activation changes

#### Idle-only / `work_conserving()`

Rejected as effective deletion:

- keeps 3/54 actual activations;
- blocks 51/54;
- activates 0/640 on no-orchard exact-prefix trajectories.

#### Enemy arrival after first bank

Rejected. A travel-only condition keeps 29 and blocks 25 observed activations, but the blocked group is descriptively stronger. More importantly, enemy arrival is not mother destruction.

#### Continuous-attack kill safety

Mechanically valid but non-discriminating. All 54 observed APPLE activations survive through first harvest under conservative continuous attack, including movement speed, chop power, tree growth, and action order.

#### Direct BANANA mother swap

Rejected. See Section 4.1.

### 3.8 Next APPLE improvement: opportunity-cost activation

The remaining credible APPLE refinement is a prospective comparison between orchard value and the exact starter job displaced by activation.

Before the wrapper overrides the starter, expose:

- inner selected task class;
- target cell/tree;
- predicted first-action ETA;
- predicted completion and banking ETA;
- expected banked material;
- expected terminal score contribution (`WOOD * 4`, fruit * 1);
- denial or contested-tree value;
- whether another worker can complete the same task.

Compute a mechanics-derived lower bound:

```text
V_orchard = guaranteed banked APPLE before turn 300
            - one consumed APPLE seed
            - explicit loss/risk deductions

V_displaced = guaranteed banked score from the selected starter task
              + non-duplicable denial value
```

Activation rule:

```text
activate only if V_orchard >= V_displaced + delta
```

`delta` must be frozen before fresh terminal outcomes are opened. It must not be fit on the 1,280 games in this audit. The first implementation should log both values and preserve current behavior until a separate protocol freezes the candidate threshold.

## 4. BANANA orchard designs

### 4.1 Rejected design: BANANA as a direct protected-mother replacement

A like-for-like swap changes only APPLE references in the secure mother to BANANA while keeping the same harvest-only lifecycle.

It is inferior on the exact-prefix audit:

- APPLE activations on 640 no-orchard trajectories: 46;
- BANANA activations: 46;
- shared support: 46;
- APPLE-only: 0;
- BANANA-only: 0;
- both seeds available in all 46 shared states.

Water-adjacent comparison:

| Property | APPLE | BANANA |
|---|---:|---:|
| effective cooldown | 2 | 4 |
| first bank after activation | travel + 11 | travel + 19 |
| mature health | 20 | 6 |
| steady bank interval | 2 | 4 |
| projected mean bank ceiling on shared support | 133.15 | 64.80 |

BANANA unlocks no new activation states, produces roughly half as much fruit, and is easier for the opponent to destroy. This direct swap is closed.

### 4.2 Proposed design: bounded self-sustained BANANA wood orchard

The valid BANANA hypothesis uses two different tree roles:

```text
protected mother -> harvested for BANANA seeds
cut plot         -> planted and chopped for WOOD
```

This design uses the user's tent-neighbor rule explicitly:

- **diagonal neighbors of the tent are mother/seeding cells and are never chopped;**
- **orthogonal side-neighbors of the tent are cut/banking cells and their BANANA trees are chopped for wood.**

Version 1 must use exactly one mother and one cut slot. Expansion is prohibited until this bounded form passes value and safety gates.

### 4.3 BANANA geometry

#### Mother cell

Choose one diagonal cell around the home tent that is:

- walkable and empty;
- reachable from a home door;
- preferably adjacent to water;
- farther from enemy access than the cut slot;
- not on the shortest route through the home doors;
- mechanically safe through first harvest under conservative enemy attack.

Tie order:

1. water-adjacent first;
2. maximize enemy kill ETA;
3. minimize home harvest-and-bank cycle ETA;
4. lexicographic tie-break.

If no valid diagonal mother exists, the bounded BANANA candidate remains inactive. Version 1 must not silently fall back to an unbounded or remote mother.

#### Cut/replant slot

Choose exactly one orthogonal side-neighbor of the tent that is:

- walkable and initially empty;
- not the unique usable home door;
- reachable by the designated chopper without crossing the mother;
- no farther from our tent than from the opponent's tent;
- immediately bankable after a chop.

The cut slot is disposable production space. Every BANANA planted there is intended to be chopped, never preserved as a second mother.

### 4.4 Worker roles

#### Mother worker

Prefer the original starter because it has harvest power.

Responsibilities:

1. bootstrap the mother;
2. remain the only owner of mother HARVEST;
3. carry harvested BANANA to a home door and DROP;
4. maintain the reserved-seed invariant;
5. never chop the mother;
6. release control to the parent only when no mother action or committed bank route exists.

#### Wood worker

Use the trained worker with positive chop power.

Responsibilities:

1. own the cut slot exclusively;
2. PICK only an unreserved BANANA seed;
3. PLANT only on the cut slot;
4. grow/fell the child according to the frozen cycle plan;
5. DROP wood immediately after the fell cycle;
6. never harvest the cut tree;
7. never target the mother.

### 4.5 BANANA state machine

```text
Dormant
  -> MotherBootstrap
  -> MotherMaturing
  -> MotherActive
  -> SeedBanking
  -> CutSeedReserved
  -> CutPlanting
  -> CutGrowingOrFelling
  -> WoodBanking
  -> CutSeedReserved ...

Any invariant failure -> Suspended or Abandoned
```

#### Dormant

Parent commands pass through exactly. Geometry and worker eligibility are observed but no command is changed.

#### MotherBootstrap

- Requires worker two to exist.
- Requires one BANANA seed in bank or already carried by the mother worker.
- Reserves only the mother worker and mother cell.
- Plants exactly one diagonal mother.

#### MotherMaturing

- Protect the mother.
- The mother worker may wait or perform a monotone route commitment.
- No cut slot is planted before the mother repays at least one seed to the bank.

#### MotherActive / SeedBanking

- HARVEST the mother when ripe.
- Move monotonically to the selected bank door.
- DROP before any new orchard action.
- Confirm the inventory delta before releasing the seed to the cut-slot ledger.

#### CutSeedReserved

A cut cycle may start only when:

```text
banked BANANA - reserved recovery seed >= 1
```

The wood worker receives one transactional seed lease. No other worker may PICK that seed in the same turn.

#### CutPlanting

- Move monotonically to the orthogonal cut slot.
- PLANT exactly one BANANA.
- Confirm next-state seed consumption and tree creation.
- On failure, clear the pending transaction; do not assume a tree exists.

#### CutGrowingOrFelling

Choose a target fell plan using the existing tree forecast and chop-outcome mechanics.

The plan must maximize bankable wood rate subject to:

1. completion and DROP before turn 300;
2. final wood not exceeding free carry capacity;
3. the child is killed before it can produce opponent-harvestable fruit;
4. the opponent cannot take control before the planned kill;
5. no second cut tree exists;
6. no movement oscillation is introduced.

A suitable objective is:

```text
4 * guaranteed_banked_wood / total_cycle_turns
```

If no safe positive cycle exists, chop immediately or suspend; never leave an uncontrolled fruiting child.

#### WoodBanking

Because the cut slot is side-neighboring to the tent, the wood worker should DROP immediately after collecting wood. If displacement occurs, the worker must follow a fixed monotone bank target until DROP. While carrying wood, no new seed PICK, PLANT, HARVEST, or remote target selection is allowed.

### 4.6 Transactional seed ledger

Track these explicit quantities:

```text
mother_alive
banked_banana
reserved_recovery_seed = 1 when mother is alive or replacement is allowed
cut_seed_lease = 0 or 1
pending_plant(turn, cell, before_carry)
pending_harvest(turn, before_carry)
pending_drop(turn, before_inventory)
```

Required rules:

1. Never spend the reserved recovery seed on the cut slot.
2. Never grant more than one cut seed lease.
3. A lease is consumed only after confirmed PLANT.
4. A harvested seed becomes available only after confirmed DROP.
5. Mother loss immediately stops new cut cycles until the reserve/replacement policy is resolved.
6. Inventory and carry deltas, not issued commands, are the source of truth.

### 4.7 BANANA activation predicate

Version 1 may activate only when all conditions hold:

1. worker two exists;
2. valid diagonal mother and valid orthogonal cut slot exist;
3. the starter/mother worker has harvest power;
4. the wood worker has positive chop power;
5. at least one BANANA seed is available for bootstrap;
6. the mother is mechanically safe through first harvest;
7. at least one mother-harvest plus cut/fell/drop cycle fits before turn 300;
8. neither role is required to surrender a non-duplicable contested natural-tree cycle;
9. parent movement remains collision-free with the reserved mother and cut slot;
10. no third-worker funding or unrelated crop policy is enabled.

The candidate should initially be narrower rather than wider. No remote plantation, multiple cut slots, dynamic ring expansion, or opportunistic second mother is allowed.

### 4.8 BANANA safety invariants

1. Exactly one protected mother.
2. Exactly one disposable cut slot.
3. Diagonal mother is never chopped.
4. Orthogonal child is always intended for chop.
5. Child must not reach a fruit state accessible to the opponent.
6. At least one recovery seed remains reserved.
7. One explicit owner per tree/slot.
8. No same-cell contention.
9. No period-2 MOVE episode.
10. A wood carrier follows a monotone bank commitment until DROP.
11. Plant count is statically bounded.
12. Parent commands are exact outside declared orchard ownership and activation.
13. No opponent-favored crop leakage increase is accepted.
14. No second-worker training displacement is accepted.

### 4.9 Why this differs from earlier banana implementations

Earlier banana-factory research demonstrated large production potential but also increased opponent production by relaxing suppression. The two live banana publications were implementation-invalid because they allowed unbounded geography, failed collection/banking, or produced long period-2 movement.

The bounded design addresses those failures directly:

- one mother, not a farm;
- one cut slot, not a ring expansion;
- explicit seed and owner ledger;
- confirmed banking before reuse;
- no child fruiting;
- monotone routing;
- exact parent preservation outside activation.

Those earlier failures do not establish that bounded BANANA wood production is harmful; they establish mandatory implementation gates.

## 5. APPLE versus BANANA: role comparison

| Dimension | APPLE secure orchard | Bounded BANANA wood orchard |
|---|---|---|
| Status | deployed, retain | proposed, unqualified |
| Primary output | banked fruit | banked wood |
| Mother location | orthogonal water-adjacent home door | diagonal near-tent cell, preferably water-adjacent |
| Disposable tree | none | one orthogonal cut slot |
| Mother action | HARVEST | HARVEST |
| Child action | n/a | CHOP before fruit |
| Desired durability | high | high for mother, low for child |
| Worker use | starter permanently reserved after activation | mother worker plus explicit wood worker |
| Banking | direct DROP on mother door | mother seed moved to door; child wood dropped at side slot |
| Current evidence | 54 activations, 5,615 banked APPLE | design only; prior factories not valid evidence |
| Immediate next step | opportunity-cost gate instrumentation | bounded one-mother/one-slot implementation and mechanism panel |

## 6. Frozen next experimental programme

Compare three arms on a fresh common-seed panel:

```text
C0: current APPLE orchard
C1: current APPLE orchard + prospective opportunity-cost activation gate
C2: bounded BANANA mother + one orthogonal cut/replant slot
```

### 6.1 Pre-value gates

All arms must pass:

- standalone compilation;
- research/compact source equivalence where applicable;
- exact parent commands outside declared activation;
- both seats;
- all selected opponent families;
- zero malformed commands or runtime errors;
- zero period-2 movement regressions;
- zero unbounded planting;
- zero same-cell ownership violations;
- zero lost banking commitments.

Additional C1 gates:

- logged `V_orchard` and `V_displaced` agree with mechanics reconstruction;
- no threshold fitted on the 1,280 audit outcomes;
- current behavior reproduced when the gate is disabled.

Additional C2 gates:

- mother planted and first seed banked;
- at least one cut cycle completed and wood banked;
- no cut-tree fruit leakage;
- mother never chopped;
- one recovery seed preserved;
- no opponent production increase attributable to our child trees;
- no worker-two training delay.

### 6.2 Value gates

Use paired common maps and seats. A candidate may proceed only if:

1. mean paired terminal margin versus C0 is positive;
2. root-cluster 95% lower confidence bound is above zero;
3. both seat means are positive;
4. opponent-family breadth is positive rather than concentrated in one family;
5. catastrophe count and negative-margin mass do not regress;
6. activation has enough support to be meaningful;
7. mechanism gains are banked resources, not merely extra plants or commands.

Arena testing remains serialized under `local_codex_1` and requires a separate explicit release.

## 7. Closed and open conclusions

### Closed by this analysis

- global orchard removal;
- idle-only APPLE activation as the next candidate;
- enemy-arrival-before-first-bank as an activation veto;
- continuous-kill safety as a selector for current APPLE geometry;
- like-for-like protected BANANA mother replacement.

### Still open

- APPLE opportunity-cost activation gate;
- bounded BANANA mother + one cut slot;
- later coordination improvements only after the bounded designs pass.

## 8. Authoritative evidence and artifacts

- corrected final analysis: `chatgpt_1/orchard-activation-species-audit-final-2026-08-04.md`;
- corrected machine verdict: `chatgpt_1/orchard-activation-species-audit-final-2026-08-04.json`;
- detailed 1,280-row table: `chatgpt_1/orchard-activation-opportunities-2026-08-04.csv`;
- analyzer: `chatgpt_1/orchard_activation_species_audit.py`;
- method/kill-safety patch: `chatgpt_1/patch_orchard_activation_species_audit.py`;
- current source: `cgauto/submissions/candidate-agent6553250-preseed-e7a-lemon-near-tie.min.rs`;
- full research source: `rust/src/bin/yamo_orchard_live.rs`;
- constraints: `docs/CONSTRAINTS.md`.
