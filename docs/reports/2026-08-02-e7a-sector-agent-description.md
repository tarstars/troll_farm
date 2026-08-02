# E7a near-tie sector agent

Detailed description of the live Troll Farm agent deployed as CodinGame agent `6590141`,
submission `41081503` on 2 August 2026.

## Executive summary

The live agent is not a new controller. It is the exact stable pre-seed/secure-orchard
parent plus one 95-byte map-conditioned change to the initial PLUM-versus-LEMON denial
choice. The parent minimizes total path distance from the player's shack doors to all
trees of a species, choosing LEMON on a tie. E7a chooses PLUM when PLUM is already closer,
or when LEMON is closer by no more than eight aggregate path cells. It retains LEMON only
when LEMON's aggregate advantage is greater than eight.

That choice is computed once during opening initialization and cached. It changes a soft
chop-scoring bonus, not a hard command. The rest of the controller—training, collection,
chop-cycle valuation, joint assignment, collision handling, secure APPLE mother, and
endgame fruit-to-wood conversion—is inherited byte for byte from the stable parent.

At the recorded 160-game mature checkpoint the agent scored 25.34 and ranked 11/131, with
82 wins, 3 ties and 75 losses. This is the highest mature live score recorded in the
project, but it is not causal proof of the sector rule: the rule was selected on consumed
development data and no same-window parent A/A control exists. A later public-replay audit
also found an inherited liveness failure: 25/160 games contain a period-2 MOVE episode of
at least six turns. In game `897832286`, a troll carrying two wood alternates between two
cells for turns 160–286.

## Exact identity

| Artifact | Identity |
|---|---|
| Candidate | `cgauto/submissions/candidate-agent6553250-preseed-e7a-lemon-near-tie.min.rs` |
| Candidate SHA-256 | `97bfe71e3f2f05e1b8fa3c697c5e5db3624ac9739e90954e9fa9be79a8e48595` |
| Candidate bytes | 62,820 |
| Stable parent | `cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs` |
| Parent SHA-256 | `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55` |
| Parent bytes | 62,725 |
| Source delta | +95 bytes; one complete function anchor, `MoisanBot::focus_type` |
| Arena identity | agent `6590141`, submission `41081503` |

The sacred development source `rust/src/bin/yamo_orchard_live.rs` was not changed to build
this candidate.

## Controller pipeline

The controller has six layers:

1. Parse the referee protocol into `GameState` and maintain exact unit, tree, inventory,
   terrain, and turn state.
2. Initialize an opening plan: choose the denial species, estimate the second worker's
   resource bill and collection ETA, and select a worker specification.
3. Generate scored candidates independently for every worker: bank, collect fruit, mine,
   chop, plant, harvest, move, or wait.
4. Choose a compatible joint assignment for the two workers.
5. Resolve landing-cell conflicts, priority cells, shack-door clearing and movement
   detours.
6. Apply the secure-orchard wrapper and endgame conversion rules, then emit commands.

The agent deliberately caps itself at two workers. It is therefore a sophisticated
two-worker scheduling and denial controller, not a scalable economy.

## The E7a sector rule

Let `D_L` be the sum of shortest-path distances from all walkable orthogonal cells adjacent
to our shack to every natural LEMON tree. Define `D_P` identically for PLUM. An unreachable
tree contributes 10,000.

The parent selects PLUM iff `D_P < D_L`; otherwise it selects LEMON. E7a selects PLUM iff

```text
D_P < D_L  OR  0 <= D_P - D_L <= 8
```

Equivalently, when the parent would select LEMON, E7a accepts a PLUM access penalty of at
most eight aggregate path cells. The rule changes nothing when PLUM is already closer and
nothing when LEMON is clearly closer.

The selected type becomes `type_to_cut`. For every viable chop cycle, the base value is
approximately `1000 * expected_wood / total_cycle_turns`. If the tree's species equals
`type_to_cut` and the opponent has at most two workers, the controller adds

```text
900 / (1 + Manhattan(tree, enemy_shack))
```

Thus, the rule changes relative target value most strongly for chosen-species trees near
the enemy shack. It does not force the worker to chop PLUM, and a better banking or chop
cycle can still win. Because `type_to_cut` is initialized once, the agent cannot oscillate
between resource-denial species as the board evolves.

The core strategic idea is conditionality. A global PLUM flip lost 12.17 mean margin on
the development panel, while a hindsight oracle gained 10.51. E7a preserves the parent on
most maps and flips only in a narrow geometry sector.

## Opening and second-worker training

The controller enumerates second-worker statistics with movement, carrying capacity and
chop power in `1..3`; harvest power remains zero. It estimates collection ETA for the
PLUM, LEMON, and—where present—IRON bill of each specification. The tuned preference is
carry at least two and chop at least one, with a 15-turn training horizon, up to 15 turns
of ETA slack for a better specification, and a hard turn-35 deadline. Candidates are
ranked primarily by total stats, then ETA, chop, carry and movement.

Before training, both workers cooperate to collect missing bill resources. A worker already
carrying useful material receives a strong banking candidate. At the deadline, the planner
can downgrade to the strongest affordable specification. Once the second worker exists,
`can_train` permanently rejects further training. This is the controller's most important
architectural limitation.

## Candidate valuation

Banking is represented explicitly. A worker already at a shack-adjacent door receives a
high-value DROP candidate; otherwise it receives a MOVE-to-bank candidate discounted by
travel ETA. Fruit candidates predict travel, ripening and waiting before issuing HARVEST.
IRON candidates route to a cell adjacent to ore and issue MINE on arrival.

Chop candidates forecast a full economic cycle: path to the tree, predicted tree growth
and health, opponent chop damage, own chop duration, return path to the shack, and final
deposit. Unreachable, nonviable or too-late cycles are discarded. Expected wood divided by
cycle time supplies the base throughput value; the E7a denial bonus is added afterward.

Carried regenerative fruit can become a persistent commitment rather than being abandoned
when a one-turn alternative looks slightly better. In scarce late positions, a worker at a
door may pick banked fruit as a seed. Outside the dedicated orchard and endgame modes, the
main controller remains chop-oriented and banks cargo when no worthwhile chop exists.

## Joint scheduling and movement

Each candidate has a target class: none, shack, bank, cell or tree. Target compatibility
prevents two workers from claiming the same exclusive object, and PICK compatibility checks
that the bank contains enough inventory for both commands. With exactly two workers the
controller exhaustively evaluates the Cartesian product of candidate sets and selects the
highest-scoring compatible pair.

The movement resolver projects landing cells at the worker's speed, reserves stationary
units and earlier mover destinations, and gives explicit priority to a protected orchard
starter. A blocked landing is replaced by an orthogonal detour that minimizes remaining BFS
distance; otherwise the unit waits. A specialized door-clear layer attempts to preserve at
least one usable shack entrance and can force a blocker to deposit or move away.

This machinery prevents many collision failures but does not establish a global liveness
invariant. The new 160-game audit proves that some target/door interactions still create
long executed ABAB routes even though every MOVE itself is legal.

## Secure APPLE orchard

The outer `SecureOrchardBot` wrapper has four phases: dormant, carrying seed, active and
abandoned. It may reserve one worker to create and protect an APPLE mother near the own
shack. Activation is deliberately narrow: the shack needs at least two doors, natural trees
must be sufficiently far away, an empty water-adjacent mother cell must be safe from the
enemy, the second worker must already exist, an APPLE must be banked, and the other worker
must retain an alternate door. It will not activate if reserving the starter would concede
a contested natural tree.

The starter picks the seed, plants the mother, then remains responsible for the mother. In
active mode it deposits cargo, harvests ripe APPLEs, and otherwise waits. Other workers are
kept off the mother and cannot steal the seed. If safety or ownership fails, the wrapper
abandons and returns control to the inner scheduler.

The orchard supplies a protected renewable asset, but it can monopolize one of only two
workers. Historical audits found long low-value harvest loops; a universal release rule was
tested and closed. The live E7a crop audit confirms the parent is not broadly renewable:
only 10 of 1,704 attributed created crops were reaped by the agent across its 160 games.

## Endgame conversion

After turn 250—or earlier when few trees remain and the agent trails—the objective changes.
Fruit carried or picked from the bank may be planted on a feasible empty cell, chopped, and
returned before turn 300, converting fruit's one point into wood's four points. A worker
already standing on a tree receives very high chop priority, and ripe-fruit harvesting is
considered only when the complete harvest-return-deposit cycle fits before the end.

The mechanism is active at scale: the 160-game audit attributed 942 successfully completed
post-turn-250 planted-and-chopped conversions to this agent. Endgame conversion is therefore
a central parent capability, not a minor fallback.

## Evidence

The exploratory sector contained 13 of 60 development roots: 10 positive and 3 nonpositive,
76.92% precision, 41.67% recall, odds ratio 7.86, and Fisher `p=0.00348`. The mechanically
built candidate passed five focused tests, an optimized standalone compile, and a 16/16
behavioral bridge: inside the selected sector it matched the full PLUM flip; outside it
matched the parent, with zero faults.

Consumed-panel pricing gave +4.008 mean margin versus the parent, but the root-bootstrap
95% interval was `[-1.588, +13.101]`. Every opponent-family mean and every
leave-one-family-out mean was positive. The decomposition was approximately +0.21 own score
and -3.80 opponent score: the apparent gain came primarily from suppressing opponent
production.

The live 160-game checkpoint was 25.34 at rank 11/131, with 82 wins, 3 ties, 75 losses,
mean margin -29.3, 35 catastrophes, and negative-margin mass 10,045. The repeated mature
stable-parent median was 24.19 and its best recorded run 24.77, but these are cross-era
comparisons and cannot isolate the sector rule.

## Design ideas worth retaining

- Make a tiny conditional decision on top of a strong, exact parent.
- Condition a strategic objective on opening geometry instead of changing tactics globally.
- Use aggregate access burden, not only the nearest resource.
- Accept a small local efficiency penalty for stronger denial only in a near-tie sector.
- Freeze a strategic species choice once to avoid target-selection churn.
- Demand an exact inside/outside behavioral bridge before deployment.
- Decompose improvement into own production and opponent suppression.

## Limitations and failure modes

- The sector was selected from consumed outcome labels; it was an owner-overridden
  exploratory deployment, not a prospectively qualified experiment.
- There is only one live E7a deployment and no same-window stable-parent control.
- The controller permanently caps itself at two workers, while several top agents reach
  worker three in more than 80% of recent games and worker four in roughly 40–95%.
- Denial species is selected only once and only between PLUM and LEMON.
- Scores are hand tuned and deterministic; there is no learned opponent model.
- The secure orchard may monopolize half the workforce.
- The mature live tail is poor: 21.9% catastrophes and negative-margin mass 10,045.
- Liveness is not solved. Twenty-five of 160 games contain a period-2 MOVE run of at least
  six turns. Game `897832286` contains a 127-turn oscillation while carrying two wood.

The best immediate engineering priority is therefore a narrow, baseline-preserving
liveness fix for bank-bound cargo and alternating landing targets, proven on all 160 open
counterexamples before any further strategic extension. Workforce scaling and renewable
production remain the larger architectural gap.

## Reproducibility anchors

- Candidate manifest: `chatgpt_1/e7a-sector-candidate-manifest-2026-08-02.json`
- Exact bridge: `chatgpt_1/e7a-sector-candidate-bridge-2026-08-02.json`
- Pricing: `chatgpt_1/e7a-sector-candidate-pricing-2026-08-02.json`
- Arena execution: `data/analysis/live-agent-6553250/e7a-sector-owner-override-arena-execution-2026-08-02.md`
- Top-15 inventory: `data/analysis/live-agent-6553250/top15-public-battle-inventory-2026-08-02.json`
- Top-15 compact audit: `data/analysis/live-agent-6553250/top15-public-battle-audit-2026-08-02.json`

