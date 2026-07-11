# Etudes: forced-outcome oracle + situation format — design

**Status:** DESIGN — approved by user (brainstorming). Ready for writing-plans.

## Motivation
Six consecutive arena reverts (ownership, taskfloor, ringtune, trainfruit, roam4, fellmission)
taught that "obvious waste" usually isn't load-bearing — the tuned band champion v1.59.0-ringfix3
is a robust local optimum and we keep mistaking cosmetic inefficiency for arena-relevant loss.
The honest response: stop guessing, and build a tool that PROVES what decides games. Etudes =
Troll Farm positions with a proven verdict (who wins under ideal play) + a proof. Approach A
(user-chosen): EXACT/PROVABLE on small constructed positions — a micro-tablebase that discovers
transferable PRINCIPLES, not statistics over noisy full games.

## Scope (this sub-project = the crux only)
The full etudes vision has four parts: (1) situation format, (2) the forced-outcome ORACLE,
(3) an etude database, (4) a viewer. THIS spec builds ONLY (1) + (2) — the crux: *can we take a
small position and prove who wins?* The database and viewer are separate follow-on sub-projects
(they have nothing to store/show until the oracle works). YAGNI: no DB, no viewer, no
game-position extraction here.

## Forced outcome (the verdict definition, user-confirmed)
Troll Farm is SIMULTANEOUS-MOVE, so a general position's game value can require MIXED strategies
(a probability, not a winner). We restrict etudes to FORCED outcomes: a position is a
`ForcedWin(side)` iff that side can GUARANTEE a strictly-better final score regardless of ANY
opponent play. Positions where neither side can force it (contested / mixed-strategy value) are
`Unresolved` and excluded — never given a false crisp verdict. This keeps "proof" meaning a
checkable forcing strategy.

## The soundness trick (how to prove forced wins in a simultaneous game)
To prove side X has a forced win, search the game tree giving the OPPONENT Y the advantage of
seeing X's joint move each turn (X = max, Y = informed min), i.e. a sequential minimax where X
commits first and Y best-responds with full knowledge. If X still wins the horizon under this
HANDICAP, then X certainly wins in the real game where Y is blind to X's move — so it is a genuine
guarantee. Formally: `informed_minimax_X(pos) <= X's true simultaneous security level`, so
`informed_minimax_X = win  ⇒  forced win for X`. (It is conservative: it may return Unresolved
for a position X could win only by hiding information via mixing — acceptable, we want soundness,
not completeness.) Run it once per side. Verdict:
- `informed_minimax_X` is a win for X (X's guaranteed score-diff at horizon > 0) → `ForcedWin(X)`.
- else `informed_minimax_Y` is a win for Y → `ForcedWin(Y)`.
- else `Unresolved`.
Outcome metric = `scores[X] - scores[Y]` at the horizon turn (scores = fruit + 4·wood, via
`engine::recompute_scores`). Strictly-better ⇒ diff > 0.

## Components

### 1. Situation format — `rust/src/etudes/situation.rs`
```
struct Situation { state: game::GameState, horizon: u32, prove_side: Option<usize> }
```
Reuses the existing `game::GameState` (width/height/walkable/shacks/inventories/units/plants/
scores/turn/iron/water — state.rs:57). `horizon` = number of turns to search from `state.turn`.
`prove_side` = None (try both sides) or Some(p) (only test p). Serialization: a text format
(`to_text`/`from_text`) capturing the FULL state so etudes are storable + hand-authorable —
extend the existing ASCII map (state.rs `from_ascii`) with explicit lines for units
(id,player,x,y,ms,cc,hp,chop,carry[6]), plants (type,x,y,size,health,fruits,cooldown),
inventories[2][6], scores, turn, and the horizon. Round-trip tested (from_text(to_text(s)) == s).

### 2. Action enumeration — `rust/src/etudes/actions.rs`
```
fn troll_actions(state: &GameState, unit: &Unit) -> Vec<String>   // pruned, sensible only
fn joint_actions(state: &GameState, player: usize) -> Vec<Vec<String>>  // per-player command sets
```
Per troll, enumerate ONLY sensible candidate commands (not 8 blind directions): `WAIT`; `MOVE`
toward each reachable tree / the shack / iron cell (one MOVE per distinct nearby target, via the
engine's `next_cell`); `CHOP`/`HARVEST`/`PLANT <fruit>`/`MINE`/`DROP`/`PICK <item>`/`TRAIN <spec>`
when the engine's preconditions hold at the unit's cell. This cuts per-troll branching from 8+ to
a handful. `joint_actions(player)` = the cartesian product over that player's trolls (small: this
sub-project targets 1 troll/side, so it's just one troll's actions; multi-troll is a bounded
product, flagged too-large past a cap). Canonical (sorted) order for determinism.

### 3. The oracle — `rust/src/etudes/oracle.rs`
```
enum Verdict { ForcedWin { side: usize, proof: Proof }, Unresolved, TooLarge }
fn forced_verdict(sit: &Situation) -> Verdict
```
`forced_verdict` runs `informed_minimax(state, X, depth=horizon)` for each side X (unless
`prove_side` pins one). `informed_minimax`:
- at `depth==0`: return `scores[X] - scores[Y]` (recompute first).
- else X (max) tries each `joint_actions(X)`; for each, Y (min, informed) tries each
  `joint_actions(Y)`; the successor = `engine::step(clone, x_cmds, y_cmds)`; value = min over Y of
  informed_minimax(successor, X, depth-1); X takes the max. Alpha-beta pruning on the X/Y loops.
- **Transposition table**: memoize on `(canonical(state), depth, X)` → value (many action
  sequences converge to the same state). Canonical state = a hash of walkable/units/plants/
  inventories/turn (order-normalized, no HashSet-iteration nondeterminism).
- **TooLarge guard**: a node-budget (e.g. 5e6 successor generations); exceeding it returns
  `TooLarge` rather than hanging. The situation is then out of the exact-oracle envelope.
X is a forced win iff its informed_minimax value > 0.

### 4. Proof — `rust/src/etudes/oracle.rs`
`Proof` = the winning side's forcing strategy: at each reachable node (under X's committed
actions and ALL of Y's responses), X's chosen joint action, recorded as a tree/line, plus the
horizon leaf score-diffs (all > 0). Serializable to text. VALIDATION (a test, and a
`replay_proof` fn): replay the proof against a BRUTE-FORCE opponent that tries every Y action at
every turn; assert every leaf still has score-diff > 0 — i.e. the proof genuinely holds.

## Where it lives
New `rust/src/etudes/` module (`mod etudes;` in lib.rs), depending only on `game::` (engine +
state). No dependency on `botmain` (the bot). A tiny bin `rust/src/bin/etude.rs` (optional,
next sub-project) to solve a situation file from the CLI — deferred; this spec ships the library +
tests.

## Tractability envelope (stated honestly)
Exact only for TINY positions: ~1 troll/side, small maps, horizon H≈5–20, with action-pruning +
alpha-beta + memoization. Larger positions return `TooLarge`. This is inherent to exact proof of a
branching simultaneous game and is the whole reason approach A means *constructed micro-positions*,
not real game states.

## Testing (`rust/tests/etudes.rs`)
- `situation_roundtrip`: `from_text(to_text(s)) == s` on a hand-authored position.
- `oracle_forced_win_by_felling`: 1 troll 2 cells from a size-2 tree (health 4), H=6, opponent
  troll far/none → `ForcedWin(us)`; the proof replays valid (all leaves diff>0).
- `oracle_forced_loss`: mirror — we're far, opponent adjacent to the only tree → `ForcedWin(opp)`.
- `oracle_unresolved_contested`: symmetric race for one tree both can reach same-turn (denial
  possible, neither forces) → `Unresolved`.
- `oracle_toolarge`: a position exceeding the node budget → `TooLarge` (no hang).
- `actions_pruned`: `troll_actions` returns only sensible commands (no blind 8-way moves; CHOP
  only when on a tree; etc.), canonical order.
- Determinism: `forced_verdict` is a pure function of the situation (no HashSet-iteration
  nondeterminism) — same verdict + proof across runs.

## Success criteria
The oracle returns a correct, proof-validated forced verdict (or Unresolved/TooLarge) on the
constructed test positions; the situation format round-trips; everything is deterministic and
depends only on the deterministic game engine. This is the substrate the etude DATABASE and
VIEWER (later sub-projects) build on, and the tool that lets us answer "in THIS position, who
wins and why" with a proof instead of a guess.
