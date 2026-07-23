# Three-worker field-map/model gap — frozen diagnostic protocol, 2026-07-19

## Question

Did the exact three-worker controller fail Stage 2A primarily because the five official maps make
its funding plan infeasible, or because the eight local opponent continuations fail to reproduce
the resource competition created by current Legend bots?

This is a diagnosis on consumed TestSession games.  It cannot qualify the rejected candidate,
tune its ladder, authorize more controlled games, or change the arena resident.

## Frozen data and policies

- Use exactly the five candidate rows/game IDs from the completed Stage 2A panel: `896298158`,
  `896298179`, `896298192`, `896298204`, and `896298211`.
- Reconstruct each normalized player-0 initial state from its exact CodinGame replay.
- Verify the observed source hash, score, successful training count, and zero diagnostic output
  against the Stage 2A artifact.
- Run two unchanged player-0 policies from turn one: exact resident `SecureOrchardBot::new()` and
  exact `NorxondorThreeWorkerSilver`.
- Cross each with exactly eight unchanged player-1 continuations: CompactGold, adaptive Gold,
  GoldElite, MyBot, PrinterBot, SchedBot, ScriptBoss, and SilverBoss.
- Run to the corrected stall/terminal condition.  No parameter, map, seat, controller, opponent,
  or tie rule may change after output is read.

The grid is 5 maps x 2 policies x 8 opponents = 80 unique complete games.

## Recorded outcomes

For every cell record terminal turn, own/opponent score and margin, own/opponent wood, own worker
count, first and third successful training turns, and action counts.  For each official map compare
the actual three-worker field row with the eight local three-worker cells and compare the local
three-worker policy with the local resident on identical map/model cells.

## Frozen discriminators

1. Integrity requires five unique exact map records, 80 unique simulation cells, all terminal,
   and no panic or parser failure.
2. **Map-driven funding failure** is supported only if at least 8/16 local three-worker cells on
   the two actual two-worker maps also finish below three workers.
3. **Opponent/model-driven funding failure** is supported if at least 13/16 of those cells reach
   worker three.
4. The old local zoo is own-score calibrated only if the actual candidate own score lies within
   that map's eight-model local min--max interval on at least 4/5 maps.
5. It is margin calibrated only if actual margin lies within the local interval on at least 4/5.
6. Report, but do not threshold-tune, local resident-versus-three-worker mean deltas and the actual
   third-worker-turn residual from the local median on the three activated maps.

Counts 9--12/16 are explicitly mixed.  A failure of both calibration checks retires the current
generated-map/old-zoo terminal gate for field transfer; local tests remain implementation and
mechanism tools only.

## Continuation rule

- **Map-driven:** build a frozen official-map discovery corpus before new policy work; first test
  whether the map generator misses species, initial inventory, supply density, or access geometry.
- **Opponent/model-driven:** do not enlarge synthetic seed blocks.  The next policy representation
  must use replay-derived field-native closed-loop scenarios or a controlled-game screening design.
- **Mixed:** repair exact-map support first, then repeat behavioral coverage without treating either
  component as sufficient.
- **Old zoo calibrated despite candidate rejection:** retain it only for relative mechanism work;
  direct Silver transfer remains closed.

