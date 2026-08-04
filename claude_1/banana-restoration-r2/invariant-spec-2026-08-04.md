# Invariant specification — banana wood-printer restoration (r2)

Status: PUBLISHED FOR INTEGRATOR REVIEW 2026-08-04. Produced by a claude_1 subagent from the
task record, the two negative-example implementations, and the family mechanics; mechanics
constants (banana cooldown 6, wet 4, health 2+size, WOOD_POINTS 4) and the factory failure
citations independently re-verified by claude_1 against the frozen parent before publication.
The I-28 rationale was corrected by claude_1 to match hypothesis-register v2's variance
finding. Per the task record, these invariants restate every contract ambiguity explicitly —
review of the resolutions (esp. I-27/I-28 exclusivity+priority, the Chebyshev-1 plot bound,
strict-ETA ownership, and the H=3/eps=1.0 commitment rule) is requested before implementation.

Task: `20260802-banana-restoration-r2`. This document restates the nine-bullet contract of the
task record as explicit, testable invariants, resolves each ambiguity with a mechanics-grounded
proposal, and defines the nine deterministic detector classes of acceptance check 5. It is a
specification, not a copy of either rejected wrapper.

## 0. Definitions and notation

- `S_t` — parsed `GameState` at turn `t`, `1 <= t <= 300` (`TOTAL_TURNS = 300`). `C_t` — the
  command list emitted at turn `t`. `pos(u,t)`, `carry(u,t)`, `inv(t)` = `inventories[0]` at `t`.
- `tent = shacks[0]`; `doors` = walkable orthogonal neighbours of `tent`;
  `diag(tent)` / `orth(tent)` = walkable diagonal / orthogonal Chebyshev-1 neighbours;
  `Ring = {c in walkable : cheby(c, tent) = 1}`.
- `eta_u(c,t) = ceil_div(bfs_dist(walkable, pos(u,t), c), speed(u))`;
  `eta_opp_h(c,t)` = min over opponent units with `harvest_power > 0`;
  `eta_opp_x(c,t)` = min over opponent units with `chop_power > 0`; unreachable = 10000.
- Banana mechanics (from `family-readable-guide.rs`, `game::rules`): `plant_cooldown(Banana)=6`,
  `water_boost(Banana)=2`, so `CD_wet = effective_cooldown(Banana, near_water) = 4`, `CD_dry = 6`;
  `tree_health_params(Banana) = (2,1)`, so `health(size) = 2 + size` — the weakest tree in the
  game (apple: `8+3s`). `WOOD_POINTS = 4`; a fruit in inventory scores 1. Chopped tree yields
  `size` wood (1..4), so one banana seed grown to size 2 and cut is 8 points vs 1 point banked.
- `T_ripe(c,t)` — normative time from a fresh `PLANT BANANA` at `c` to first ripe fruit, computed
  by the parent's `ticks_until_fruit` simulator on the just-planted state (grow to size 4, then
  one more cooldown period; approx. 4–5 periods = 16–20 turns near water, 24–30 dry).
- `starter` — the own unit with minimal id at turn 1 (as in `SecureOrchardBot::initialize`);
  the "resident" of the contract is the starter (resolution recorded under B3). In
  banana-enabled games the starter **is** the banana worker; the trained second worker stays on
  the main economy and is never claimed by the feature (rev. 2026-08-04, integrator item 1).
- Attribution: a command at turn `t` is *banana-attributable* iff it differs from the stable
  parent's command on the identical input stream (the acceptance-check-4 seam makes this
  well-defined: outside declared banana activation states, commands equal the parent exactly).
- `target(u,t)` — the declared commitment of unit `u` at `t` (a `Target`-typed value: tree cell,
  plant cell, bank door, mine cell, or mode-level task). The implementation must expose this
  deterministically (telemetry), so retarget events are trace-checkable.

Negative-example evidence used below: in `negative-example-factory.rs`,
`banana_factory_plant_cell` ranges over **all** walkable, plant-free, unit-free cells filtered
only by `from_home <= from_enemy` (no radius, no count cap); `banana_factory_starter_command`
has **no DROP branch** for carried bananas (harvest is only ever replanted, never banked);
`banana_factory_plant_target` is invalidated by any transient unit on the cell and re-chosen by
a fresh `min_by_key` (no hold, no margin); when the starter function returns `None` control
falls through to the inner policy (mode flapping); trained workers' `PICK/PLANT/HARVEST/MINE`
commands are rewritten wholesale (`banana_factory_trained_role_rewrites`).

---

## B1. "Early planted bananas form a self-reproducing orchard"

**Invariants**

- **I-1 (activation window).** The first own `PLANT BANANA` occurs at a turn `t0` with
  `t0 <= 100` and `300 - t0 >= T_ripe + 4` (payback reachable); if the deterministic activation
  predicate never fires by turn 100, the feature stays dormant for the whole game and every
  command equals the stable parent (check 4).
- **I-2 (bootstrap budget).** Bank withdrawals for seeding are bounded: the number of
  `PICK <starter> BANANA` commands attributable to the feature is `<= B_boot = 1` per game.
  After the first successful own harvest, every seed used by the feature has harvest provenance.
- **I-3 (self-reproduction).** For all `t in [t0 + T_ripe, T_late]` (T_late from I-5): if the
  live **own**-banana count in `diag(tent)` dropped below the mother floor `M_min = 1` for a
  reason attributable to our own commands (not opponent chop), a replant `PLANT BANANA` in
  `diag(tent)` is issued within `CD_dry = 6` turns whenever a seed (carried or banked) exists.
  The floor counts diagonal mothers only — an orthogonal wood tree cannot mask the absence of
  every mother (rev. 2026-08-04, integrator item 3).

**Ambiguities and resolutions**

- *"early" = when?* → Resolve: activation deadline turn 100 with the payback feasibility term
  in I-1. Rationale: mirrors the parent orchard's `Dormant` deadline (`view.turn > 100 =>
  Abandoned`) and a seed needs ~`5*CD_wet = 20` turns before it pays anything back.
- *"self-reproducing" = seeds from where?* → Resolve: exactly one bank-bootstrap seed
  (`B_boot = 1`); all later seeds come from own harvests. Rationale: the factory's open-ended
  `banana_factory_initial_budget` goal was one of the two knobs that made the farm unbounded.
- *"orchard" = which cells reproduce?* → Resolve: only `diag(tent)` mothers are renewable fruit
  sources; `orth(tent)` slots are consumable wood trees (see B5). Rationale: the owner
  correction in `ring-task.md` fixes this role split; banana health `2+size` makes anything
  farther than Chebyshev-1 from the tent indefensible.

**Falsified by:** D-5 (unbounded planting), D-7 (lost harvested fruit — a "self-reproducing"
orchard that eats its own harvest without banking is the factory failure mode).

---

## B2. "Late ripe fruit is converted into wood"

**Invariants**

- **I-4 (conversion channel).** Wood conversion happens only on `orth(tent)` slots: an
  orthogonal own banana is chopped only at `size >= 2`, and every orthogonal own banana is
  eventually chopped (never fruit-farmed); `diag(tent)` mothers are never chopped (I-14, D-8).
- **I-5 (late cutoffs).** No `PLANT BANANA` on an orthogonal slot after
  `T_late = 300 - (2*CD(c) + ceil_div(health(2), chop_power) + 2)` for that cell (`CD(c)` = 4
  near water, else 6; `health(2) = 4`); no `PLANT BANANA` anywhere after the planted tree can no
  longer contribute `>= 4` points (size-1 chop) before turn 300.
- **I-6 (conversion dominance, late).** For `t >= T_conv = 300 - T_ripe`: when the resident must
  choose between fruit-harvest of a mother and servicing a ready orthogonal wood cut, the wood
  cut wins unless the fruit would otherwise be forfeited (opponent ETA, I-10). Rationale:
  4 pts/wood vs 1 pt/fruit; a size-2 cut is 8 points for a `<= 2*CD + 4`-turn cycle.

**Ambiguities and resolutions**

- *"late" = a fixed turn or a feasibility condition?* → Resolve: feasibility conditions I-5/I-6
  derived from cooldown and chop arithmetic, not a magic turn constant. Rationale: cutoffs then
  adapt to water adjacency (`CD_wet=4` vs `CD_dry=6`) exactly as the referee arithmetic does.
- *"converted" = chop ripe trees, or plant-grow-chop cycle?* → Resolve: the plant-grow-chop
  cycle on orthogonal slots (a banana fruit becomes up to `4 wood = 16` points); ripe *fruit*
  itself is banked (B3), the *tree* is the wood vehicle. Rationale: matches `ring-task.md`
  "orthogonal size-2 cut/replant wood cycle" and the score table.

**Falsified by:** D-8 (diagonal-mother chop), D-5 (planting past cutoff counts as a bound
violation), semantic test area "late conversion".

---

## B3. "Harvested fruit is collected/banked when the resident owns the resource"

**Invariants**

- **I-7 (ownership predicate).** Own fruit at cell `c` is *owned* at `t` iff
  `eta_res(c,t) < eta_opp_h(c,t)` **strictly**, where `eta_res` is the ETA of the **committed
  harvester** — the resident (= the starter, B3) — not a minimum over all workers: another
  worker's proximity cannot certify fruit the resident would lose (rev. 2026-08-04, integrator
  item 4). While the resident is wood-committed (I-19), the fruit is not owned until the
  commitment ends; ties are treated as not owned.
- **I-8 (banking latency).** For every own `HARVEST` of banana at turn `t` by unit `u`: each
  harvested banana is, within `A = 6` turns, either (a) consumed by a `PLANT BANANA` of `u`, or
  (b) present in `inv[BANANA]` via a `DROP` at a door, or (c) still carried with a live replant
  commitment; carried-banana age `> 12` turns without (a)/(b) is a violation.
- **I-9 (surplus rule).** Replant demand (an empty eligible `Ring` cell within horizon I-5) has
  priority for at most one carried seed; every additional carried banana is surplus and must be
  on a bank path (monotone door approach as in I-19, then `DROP`).

**Ambiguities and resolutions**

- *"the resident" = who?* → Resolve: the starter (min-id unit at turn 1), the same deterministic
  choice as `SecureOrchardBot::starter_id`. In banana-enabled games the starter is the resident
  and performs all banana work; the trained second worker stays on the main economy
  (funding/denial per B6). Any non-starter banana-worker selection (as in the pre-revision seam
  step B.2) contradicts this resolution and is disallowed. Rationale: deterministic, and keeps
  the trained worker free for funding/denial (B6).
- *"owns the resource" = what test?* → Resolve: strict ETA comparison of I-7, opponent side
  restricted to harvest-capable units, ties to the opponent. Rationale: `enemy_eta` already
  exists in the parent; strictness is required because simultaneous arrival is contested and the
  banana tree (`health = 2+size`) cannot be defended in a race.
- *bank vs replant priority?* → Resolve: I-9 (one seed for replant, rest banked). Rationale: the
  factory banked nothing at all (`banana_factory_starter_command` has no `DROP` branch), which
  is the owner's explicit correction "harvested bananas are not being collected to the tent".

**Falsified by:** D-7 (lost harvested fruit), D-2 (repeated PICK/DROP at the bank).

---

## B4. "Do not create fruit the opponent can harvest before us"

**Invariants**

- **I-10 (plant-time safety).** Every own `PLANT BANANA` at `(c,t)` satisfies
  `eta_opp_h(c,t) > min_u eta_u(c,t)` (strict, ties forbidden) **and**
  `eta_opp_x(c,t) > 2` (an opponent chopper 2 turns away kills a fresh `health = 3` sapling
  before it matters). For `Ring` cells this is normally automatic; it must still be checked.
- **I-10a (dynamic ownership-loss response, rev. 2026-08-04, integrator item 7).** If
  ownership of a live own banana asset is lost after plant time (I-7 flips false at some `t`
  through opponent movement), the resident responds deterministically at the first such `t`:
  if a ripe fruit is harvestable immediately, **harvest now**; otherwise **convert** (chop at
  current size, orthogonal arithmetic of B2) iff the conversion completes strictly before
  `eta_opp`, else **abandon** (no further commands invested in the asset). The choice is a pure
  function of `S_t`, hence trace-checkable.
- **I-11 (lifetime non-forfeiture — replay-outcome gate, reclassified rev. 2026-08-04,
  integrator item 7).** No fruit on an own-planted banana is ever harvested by an opponent:
  there is no `t` with an opponent unit standing on an own-planted banana cell whose `fruits`
  decreases while that opponent's banana carry increases. Count over the mandated replay
  panels: 0. I-11 is **not** a universal implementation invariant — no plant-time test can
  guarantee it against later opponent movement; where a violation remains despite I-10 and the
  I-10a response, it is a replay-outcome **gate failure** to triage, not a wrapper proof
  obligation.

**Ambiguities and resolutions**

- *static (plant-time) or dynamic (lifetime) obligation?* → Resolve: both — I-10 is the
  plant-time decision rule, I-10a the dynamic in-life response to ownership loss, and I-11 the
  trace-level replay-outcome gate (rev. 2026-08-04, integrator item 7). Rationale: the factory's only
  guard was `from_home[c] <= from_enemy[c]` on **door** BFS distances — a half-plane test that
  ignores actual opponent worker positions and speeds.
- *margin?* → Resolve: strict inequality, no extra margin for `Ring` cells (own ETA is 0–2
  there); for any future non-ring exception a margin of `CD_wet = 4` (one fruit period) would be
  required. Rationale: within the ring the enemy-door distance filter of the parent orchard
  (`enemy_distance >= 11`) already dominates; outside it, one fruit period is the natural unit.

**Falsified by:** D-6 (opponent-favored fruit creation).

---

## B5. "Gate-aware, bounded placement rather than an unbounded field"

**Invariants**

- **I-12 (geometry).** Every own `PLANT BANANA` cell lies in `Ring` (Chebyshev distance from own
  tent exactly 1, walkable): plants outside `Ring` = 0, for the whole game.
- **I-13 (capacity).** Concurrent live own-banana count `<= |Ring| <= 8`; cumulative distinct
  own-banana plant cells over the game `<= |Ring|`; live mothers `<= |diag(tent)| <= 4`.
  R2 caps the **protected**-mother set at exactly one — the single protected mother of I-29;
  additional diagonal plants are geometrically permitted but carry no protection claim
  (rev. 2026-08-04, integrator item 3). Service-rate note: one resident sustains at most `~2`
  fruit-bearing mothers (`cycle ~ 3-4 turns` vs `CD_wet = 4`), so mothers beyond 2 are
  unserviced surplus, not protected reserve.
- **I-14 (role map).** `c in diag(tent)` planted => mother: protected, harvest-only, never
  chopped by us. `c in orth(tent)` planted => wood slot: cut at size >= 2, replant per I-5.
- **I-15 (gate-awareness).** After any own plant/commitment, every own non-resident worker still
  reaches at least one door in `walkable` minus the protected-mother forbidden set (the parent's
  `worker_can_use_alternate` test); no full-ring bank `PICK` (seed `PICK` only under I-2).

**Ambiguities and resolutions**

- *"bounded" — bound = what?* → Resolve: `R = 1` (Chebyshev) and `K = |Ring| <= 8` as in I-12/13.
  Rationale: the owner correction fixes the ring; independently, `health = 2 + size` means any
  banana the resident cannot reach in `<= 1` move is free food for an opponent chopper, and
  `CD_wet = 4` means a 0–1-cell travel radius is what keeps the harvest cycle inside one
  cooldown period. The factory's "half the map" candidate set is the negative example.
- *"gate-aware" = what, precisely?* → Resolve: I-15 (door reachability for the non-resident,
  reusing the parent's doors/alternate-doors machinery) plus door-`DROP` banking preserved.
  Rationale: this is the "existing tent gate/front-door logic" the owner named; it is already
  implemented and measured in `SecureOrchardBot`.

**Falsified by:** D-5 (unbounded planting), D-3 (contention if gates are closed).

---

## B6. "Preserve second-worker funding before denial work"

**Invariants**

- **I-16 (activation requires the second worker).** Banana activation (first
  banana-attributable command) requires `|own units| >= 2`, or training permanently infeasible
  (`300 - t <= 20` per `can_train`). Same guard as the orchard's `has_second` checkpoint.
- **I-17 (TRAIN parity).** On every paired replay, the candidate issues `TRAIN` on the same turn
  with the same stats tuple as the stable parent; displacement (later, missing, or altered
  TRAIN) = 0. Note `training_cost` uses PLUM/LEMON/APPLE/IRON only — a banana-seed `PICK` never
  competes for funding *items*; the protected asset is worker **time** and the TRAIN turn.
- **I-18 (denial ordering).** Opponent-crop denial work (the ETA<=6 suppression class) by any
  worker is banana-compatible only after `TRAIN` has been issued or is infeasible; before that,
  funding-phase commands are byte-equal to the parent (check 4 makes this the default).

**Ambiguities and resolutions**

- *"funding" = resources or schedule?* → Resolve: schedule (TRAIN turn parity, I-17), since the
  cost vector cannot collide with bananas. Rationale: the factory's failure here was time-based
  — `banana_factory_trained_role_rewrites` rewrote worker commands wholesale.
- *may the feature ever pre-empt funding?* → Resolve: no; dormancy until `has_second`.
  Rationale: the second worker is a precondition of every downstream invariant (gate-awareness
  I-15, arbitration B8) and of the orchard's own measured activation logic.

**Falsified by:** D-9 (second-worker TRAIN displacement).

---

## B7. "A worker that commits to bank carried wood continues to the tent until DROP or loss of cargo"

**Invariants**

- **I-19 (commitment persistence).** Define `wood-committed(u,t)`: `carry[WOOD](u,t) > 0` and a
  bank-target command was emitted for `u` at some `t' <= t` with no intervening `DROP` or
  cargo loss. While wood-committed, `command(u,t)` is only: `MOVE` toward the currently nearest
  reachable door, or `DROP` at a door. Commitment ends only on executed `DROP`,
  `total_carried = 0`, unit death, or no door reachable.
- **I-20 (monotone progress).** While wood-committed and unblocked,
  `door_dist(u, t+1) <= door_dist(u, t) - 1` (`door_dist` = BFS distance to nearest reachable
  door); at most 1 consecutive turn of non-decrease is tolerated for conflict-resolver
  displacement; 2+ consecutive non-progress turns without `DROP`/loss is a violation.
- **I-21 (forced commitment).** `free_capacity(u,t) = 0` with `carry[WOOD] > 0` forces
  wood-commitment at `t` (a full worker has no other useful verb).

**Ambiguities and resolutions**

- *when does commitment start?* → Resolve: first emitted bank-target command while carrying
  wood, plus the forced case I-21. Rationale: makes the interval endpoints trace-visible, so
  D-4 is decidable without reading internal state.
- *"loss of cargo" = ?* → Resolve: `total_carried` drops to 0 for any reason other than our own
  `DROP` at a door (death/removal). Rationale: only observable state transitions may terminate
  an invariant interval.

**Falsified by:** D-4 (abandoned carried-wood return), D-1 (a wood-committed oscillator).

---

## B8. "Workers never chase each other's occupied tree/cell"

**Invariants**

- **I-22 (distinct nontrivial targets).** At every `t`, for distinct own `u, v`: if both targets
  are nontrivial (tree/plant/mine cell), `target(u,t) != target(v,t)`; exception: the bank-door
  *set* may be shared; when two or more doors are reachable the chosen door cells must differ.
  When only a single door is reachable, banking is **serialized deterministically** — resident
  first, then ascending unit id — rather than requiring distinct doors, which would make the
  invariant unsatisfiable (rev. 2026-08-04, integrator item 8).
- **I-23 (no landing on a working peer).** No own `MOVE` whose `next_cell` landing equals the
  cell of another own unit that is stationary-working there (verb in
  `HARVEST/CHOP/PLANT/PICK/DROP/MINE/WAIT`), for 2+ consecutive turns; single-turn transients
  are the conflict resolver's to fix (parent's
  `resolve_move_conflicts_with_priority_and_forbidden` stays authoritative).

**Ambiguities and resolutions**

- *is same-tree stacking ever legal?* → Resolve: no for this feature (targets pairwise
  distinct); if a future variant wants stacked chops it must declare it as a new activation
  state. Rationale: with 2 workers, stacking always starves either funding, denial, or the ring.
- *transient vs sustained conflict?* → Resolve: 1-turn transients allowed, 2+ turns forbidden.
  Rationale: the resolver operates within a turn; anything that survives a full turn boundary
  is a policy bug, and the 2-turn threshold is what makes D-3 deterministic.

**Falsified by:** D-3 (same-target/occupied-cell contention).

---

## B9. "Target selection has commitment/hysteresis sufficient to prevent A->B->A loops"

**Invariants**

- **I-24 (retarget rule).** `target(u,t+1) != target(u,t)` only if: (i) *invalidation* — target
  destroyed/completed/planted-over/occupied by a working peer/unreachable; or (ii) *upgrade* —
  the target has been held `>= H = 3` turns AND `score(new) >= score(old) + eps`, `eps = 1.0`
  in candidate-score units (= one travel turn in the parent's scoring scale).
- **I-25 (mode hysteresis).** A unit's feature mode (resident-duty / wood-cycle / inner-policy
  fallthrough) is itself a target under I-24: mode flips obey the same `H = 3` hold and are
  never caused by a `None` fallthrough (every activation state must emit a definite command).
- **I-26 (movement monotonicity + total order).** With a fixed target and no block,
  `bfs_dist(pos(u,t+1), target) < bfs_dist(pos(u,t), target)`; all candidate comparisons use the
  total order `(score, target-kind ordinal, cell lexicographic)` so equal-score sets cannot
  alternate; 2 consecutive blocked turns force invalidation-retargeting via I-24(i).

(Full rule and prevention argument in section (e); falsified by D-1, D-2.)

---

## Detector catalog (acceptance check 5)

Common inputs: per-turn command streams `C_t` (research and compact must agree, check 3), replay
states `S_t` for both players, the static map, the paired stable-parent stream on identical
inputs, and the feature's declared `target(u,t)` telemetry. All detectors are deterministic pure
functions of these inputs. All thresholds are **0 episodes** unless stated.

- **D-1 A->B->A movement.** Inputs: `pos(u,t)`, per-unit progress events (carry delta, inventory
  delta credited to `u`'s DROP/PICK, plant created/removed at `u`'s cell, score delta
  attributable to `u`). Predicate: exists unit `u`, cells `a != b`, window `[t, t+2k]`, `k >= 3`,
  with `pos(u, t+2i) = a`, `pos(u, t+2i+1) = b` for all `i`, and zero progress events for `u`
  in the window. Threshold: 0. Rationale: `k >= 3` (6+ turns) excludes legitimate 1-turn
  resolver sidesteps and 2-cell work loops (those emit progress events); the cited
  counterexample windows (turns 20–29, 269–280 of game 897829265) are 10 and 12 turns long and
  are caught. Gate 6 additionally requires task progress through both cited windows.
- **D-2 Repeated PICK/DROP.** Inputs: `C_t`, `inv(t)`, `carry(u,t)`. Predicate: exists `u` and a
  window of `<= 12` turns containing `>= 2` PICKs and `>= 2` DROPs by `u` at door cells with net
  `inv + carry` change of zero over the window. Threshold: 0. Rationale: one PICK-then-DROP pair
  is a legitimate seed abort; two full zero-net cycles are pure churn; 12 turns = 2 dry banana
  cooldowns, the longest natural wait the feature can justify near the tent.
- **D-3 Same-target/occupied-cell contention.** Inputs: `target(u,t)` telemetry, `C_t`,
  `pos(u,t)`, `next_cell` landings. Predicate: two own units share a nontrivial target, or one
  unit's MOVE lands on a stationary-working own peer's cell, for `>= 2` consecutive turns.
  Threshold: 0. Rationale: 1-turn transients belong to the intra-turn conflict resolver; the
  2-turn bound makes the check independent of resolver internals.
- **D-4 Abandoned carried-wood return.** Inputs: `carry[WOOD](u,t)`, `C_t`, door BFS distances.
  Predicate: exists wood-committed interval containing either a non-bank verb
  (`HARVEST/CHOP/PLANT/MINE/PICK`) for `u` (interval per I-19/I-21), or 2 consecutive turns
  with no decrease of `door_dist(u)` and no `DROP`/cargo-loss. Threshold: 0. Rationale: speed >= 1 guarantees 1
  cell/turn progress when unblocked; 1 turn of slack absorbs resolver displacement.
- **D-5 Unbounded planting.** Inputs: own `PLANT BANANA` commands, static map, live plant sets.
  Predicate: any own banana plant with `cheby(c, tent) != 1`; or concurrent live own bananas
  `> |Ring|`; or cumulative distinct plant cells `> |Ring|`; or any plant after its I-5 cutoff.
  Threshold: 0 violations. Rationale: direct encoding of the owner correction; the factory
  fails this on its first non-ring plant.
- **D-6 Opponent-favored fruit creation.** Inputs: own `PLANT BANANA` events, both sides' unit
  positions/stats, replay fruit counts. Predicate: (a) at any plant `(c,t)`:
  `eta_opp_h(c,t) <= min_u eta_u(c,t)` or `eta_opp_x(c,t) <= 2`; or (b) at any turn an opponent
  unit on an own-planted banana cell has its banana carry increase while the plant's `fruits`
  decreases. Threshold: 0. Rationale: (a) is the decision-time rule (ties to opponent because a
  `health = 3` sapling loses every race); (b) is ground truth from the replay.
- **D-7 Lost harvested fruit.** Inputs: own HARVEST/DROP/PLANT events, `carry`, `inv`.
  Predicate (ledger): over the game, `harvested_bananas != banked_bananas + planted_bananas +
  end_carry`, where `end_carry` only counts bananas harvested in the final 6 turns; or any
  carried banana with age `> 12` turns and no bank/plant. Threshold: 0 lost units. Rationale:
  6 = one dry cooldown covers a final in-flight harvest; 12 = two cooldowns bounds transit
  within the ring by an order of magnitude; the factory loses every non-replanted banana.
- **D-8 Diagonal-mother chop.** Inputs: `C_t`, plant sets, static map. Predicate: any own
  chop-class command targeting a cell in `diag(tent)` holding a live own banana, or any
  own-attributable health decrease of such a plant, at any turn including endgame. Threshold: 0.
  Rationale: matches `ring-task.md` "diagonal ordinary chops: 0"; terminal-window mother
  conversion is a value optimization deliberately excluded from this restoration (ambiguity
  resolved strict for r2; an owner amendment would be needed to relax it).
- **D-9 Second-worker TRAIN displacement.** Inputs: paired candidate-vs-parent command streams
  on identical replay inputs. Predicate: candidate `TRAIN` turn > parent `TRAIN` turn, or
  `TRAIN` absent where the parent trains, or a different stats tuple; or any
  banana-attributable command before the candidate's `TRAIN` while `|own units| = 1`.
  Threshold: 0 displaced turns. Rationale: check 4 (byte equality outside activation) makes the
  pairing exact; the factory's role rewrites and early activation are both caught.

Semantic test map (check 7): bootstrap → I-1/I-2; renewable harvest/replant → I-3/I-9; bounded
placement → I-12..I-15; late conversion → I-4..I-6; banking → I-7..I-9; enemy ETA suppression →
I-10/I-10a/I-11/I-18; two-worker arbitration → I-16/I-17/I-22/I-23; destroyed/occupied target
recovery → I-24(i)/I-26 (invalidation clause + blocked-turn forcing).

---

## (d) Interaction with the existing apple orchard (`SecureOrchardBot`)

The parent (`candidate-agent6553250-preseed-orchard-coverage-slim`) already ships the secure
apple orchard: it reserves the **starter** permanently, plants an apple mother on a **door**
(water-adjacent, `enemy_distance >= 11`), forbids the mother cell to the other worker, and uses
the alternate-doors machinery. The banana ring wants the same three scarce assets: the starter
as resident, the Chebyshev-1 neighbourhood of the tent (its wood slots are exactly the door
cells the apple mother competes for), and the doors as the banking surface. With only two
workers, running both features leaves zero workers for funding, denial, and the main economy,
and the apple mother physically occupies an orthogonal ring slot.

**Resolution — mutually exclusive activation with a deterministic turn-1 priority rule
(recommended):**

- **I-27 (exclusivity).** In any single game, at most one of {apple orchard, banana ring} ever
  leaves its dormant phase; there is no turn at which both features have issued an attributable
  command. Evidence standard (rev. 2026-08-04, integrator item 2): **zero dual-attributable
  commands over the whole game**, checked on the full command stream — not post-hoc inspection
  of wrapper fields.
- **I-28 (priority rule).** Decided once, **before the first delegated call** (at the top of
  turn 1, when `SecureOrchardBot.geometry` and `starter_id` are still uninitialized), by
  **reproducing** `SecureOrchardBot::initialize`'s eligibility test **read-only** on the static
  map and initial plants: if the reproduced test yields an eligible water-adjacent mother door
  (i.e. `geometry` would be `Some(..)` and the natural-median test passes), the apple orchard
  owns the game and the banana feature is permanently disabled; otherwise the banana feature is
  enabled and the orchard remains structurally dormant. The wrapper never delegates first and
  inspects inner fields afterwards to learn the decision (rev. 2026-08-04, integrator item 2).
- Rationale: (1) apple-first because the orchard is the qualified, live-deployed lineage
  while the banana feature is exactly the unproven thing under test — priority defaults to
  the qualified incumbent. (Register v2 note: the orchard's live value is currently
  indistinguishable from zero across 13 settled legs — 22.81–25.30 orchard vs 23.11–24.76
  no-orchard — so this priority is about lineage discipline and check-4 economy, not about a
  proven apple advantage; if H2/H1-G4 later resolve the orchard's sign negative, I-28's
  priority order is the single line to revisit.) (2) a turn-1 decision is a pure function of
  the static map, so it is inspectable, replay-stable, and keeps acceptance check 4 trivially:
  in apple games the candidate is byte-identical to the parent everywhere; (3) apple mechanics
  dominate where both are possible (apple: health `8+3s`, `water_boost 7` → wet cooldown 2, vs
  banana health `2+s`, wet cooldown 4), so ceding those maps to the orchard loses nothing the
  banana ring could defend better.
- **I-29 (runtime non-interference).** In banana games the orchard's fields never transition
  out of Dormant/uninitialized-geometry, and the banana wrapper must not clear or repurpose the
  inner policy's reservations the way the factory did (`external_idle_unit = None`,
  `regeneration_commitments.clear()` each turn); it sets only its own declared reservation:
  the resident id plus a **single banana-side protected cell** (the one R2 protected mother of
  I-13), carried by the seam's dedicated `banana_protected_cell:Option<Cell>` reservation that
  mirrors `external_protected_tree`. A set-valued multi-cell reservation is deferred beyond R2;
  I-29 is never claimed from `banana_idle_unit` alone (rev. 2026-08-04, integrator item 5).

---

## (e) Hysteresis / commitment rule

**Rule (normative, implements I-24..I-26).** Each own unit `u` carries
`(target, mode, hold_age)`. On each turn:

1. If `target` is *invalid* — destroyed, completed (harvest taken / plant placed / drop done),
   planted-over, occupied by a working own peer, unreachable, or blocked 2 consecutive turns —
   recompute freely; reset `hold_age = 0`.
2. Else if `hold_age < H = 3`: keep `target` unchanged, emit the move/verb for it,
   `hold_age += 1`. No exceptions — not even a better candidate.
3. Else: switch to the best alternative only if
   `score(alt) >= score(target) + eps`, `eps = 1.0` (one travel-turn in the parent's candidate
   scale, where MOVE candidates score `base - travel_turns`); on switch reset `hold_age = 0`.
4. All comparisons use the strict total order `(score, target-kind ordinal, cell lexicographic)`;
   mode changes (resident-duty / wood-cycle / inner fallthrough) pass through the same steps
   1–3, and every active mode returns a definite command (no `None` fallthrough).

**Why this is designed to suppress A->B->A (D-1 with k >= 3) — design rationale, not a
theorem (rev. 2026-08-04, integrator item 6):** (i) Within any hold interval the
target is fixed, and I-26 makes BFS distance to it strictly decrease on every unblocked turn,
so `pos(u, t+2) != pos(u, t)` — a period-2 position cycle is impossible without a block; (ii) a
2-turn block triggers clause 1 invalidation, ending the episode with a retarget, so a blocked
oscillation cannot reach length 6; (iii) an oscillation driven by preference flapping on a
fixed state needs a retarget at least every 2 turns, but clause 2 enforces 3 turns between
non-invalidation switches, and clause 3's margin plus the strict total order make the
preference relation acyclic on any fixed state, with each flip costing a `hold_age` reset.
**Known gap:** clause 1 invalidation bypasses the `H = 3` hold, and a changing occupancy state
can repeatedly make A and B valid in alternation, so invalidation-driven `A->B->A` is *not*
excluded by this argument; the acyclicity reasoning applies only to preference-driven switches
on a fixed state. Constants: `H = 3` (minimal hold strictly exceeding the observed period 2
plus the 1-turn resolver allowance) and `eps = 1.0` (the score value of one saved travel turn)
are **candidate parameters**, not proven-sufficient values. Acceptance for B9 therefore rests
on detector D-1 returning 0 episodes plus the exact-game gate on `897829265` (both cited
windows), not on this paragraph.

**Failure evidence this rule targets:** the factory re-ran `min_by_key` selection every turn
with tie-breaks that shift as the unit moves, invalidated `banana_factory_plant_target` on any
transient occupant, and fell through to the inner policy whenever `starter_command` returned
`None` — three independent flap sources, all closed by clauses 1–4; the live period-2 episodes
(game 897829265, worker 2, `(10,4)<->(11,4)` turns 20–29 and `(8,2)<->(8,3)` turns 269–280) are
the acceptance-gate counterexamples for this section.

---

## Revision 2026-08-04 (integrator review 20260804T194501Z)

Corrections from `local_codex_1`'s ACK review, applied in place (no invariant renumbered; the
one added invariant uses the suffix form I-10a):

1. Resident contradiction → §0 (`starter` definition), B3 ambiguity resolution → in
   banana-enabled games the banana worker is the starter (resident); the trained second worker
   stays on the main economy; non-starter selection language disallowed.
2. Turn-1 arbitration ordering → I-27, I-28 → decision moved to before the first delegated call
   by reproducing the eligibility test read-only; I-27's evidence standard is zero
   dual-attributable commands over the whole game, not field inspection after delegation.
3. Mother accounting → I-3, I-13 → the mother floor now counts live own bananas in `diag(tent)`
   (an orthogonal wood tree cannot mask a missing mother); R2 caps the protected-mother set at
   a single protected mother.
4. Ownership actor → I-7 → ownership compares the ETA of the committed harvester (the
   resident/starter), not the minimum over all non-wood-committed workers.
5. Protection seam → I-29 → protection is a single banana-side protected cell carried by the
   seam's dedicated `banana_protected_cell:Option<Cell>` reservation; set-valued reservation
   deferred beyond R2; I-29 never claimed from `banana_idle_unit` alone.
6. Hysteresis gate-not-proof → section (e) → "provably prevents" theorem wording removed;
   mechanism kept; known invalidation-bypass gap stated; H=3/eps=1.0 are candidate parameters;
   acceptance rests on detector D-1 plus the exact-game gate on 897829265.
7. Lifetime safety → B4: new I-10a, I-11, ambiguity resolution, semantic test map → dynamic
   ownership-loss response defined (harvest now / convert / abandon, deterministically); I-11
   reclassified as a replay-outcome gate where residual, not a universal invariant.
8. Single-door maps → I-22 → single-reachable-door banking is serialized deterministically
   (resident first, then ascending unit id) instead of requiring distinct doors.
