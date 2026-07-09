# v1.55.0-taskfloor builder brief — the task producer must guarantee a task floor

**Framing (user, 2026-07-09):** the bot IS a task manager — `planner::candidates()` is the task
PRODUCER, `assign_resolved` is the MATCHER that hands tasks to trolls. A parked troll is not a
troll that "failed to pick work" — it is the producer handing over an empty task because it
produced an empty pool. This candidate fixes the PRODUCER, not troll behavior.

## Verified root cause (telemetry-proven, do NOT re-derive)
Instrumented games vs Crouistiti (agentId 6479836, @TFASSIGN probe, 2026-07-09): late-game
trolls get `band=park (value 1_000_000 = band 10), tgt=None, empty carry` for up to **82
consecutive turns** (a third of the game); both trolls can park simultaneously (whole team
idle). It is NOT a livelock — there is simply no task. The producer's task generation is
BOUNDED (chopper enumerates trees only inside its roam radius; fruit tasks are ripe-only), so
once the neighborhood is felled the pool collapses to PARK. idle-fruit (band 38) doesn't rescue
it — no ripe fruit remains either; what's left is distant wild trees to chop, and nothing
fetches them.

## The fix: emit low-band "reach-work" tasks so the pool never underflows
In `candidates()` (the per-troll task producer), AFTER the normal bands, ALWAYS additionally
emit "reach-work" tasks covering the nearest REACHABLE productive opportunities anywhere on the
map — NOT bounded by roam radius:
- **reach-chop**: the nearest reachable fellable wild tree(s) — band **20**.
- **reach-harvest**: the nearest reachable fruit (ripe OR maturing) — band **18**.
- **reach-plant**: nearest free plantable farm cell if farm below cap — band **16**.
Value = `band * BAND - eta(troll -> target)` (distance-discounted, so the NEAREST reachable work
wins, and even a very-far target stays far above PARK). Emit the K nearest of each (propose K=3)
so multiple idle trolls get distinct targets and the joint matcher can assign them conflict-free.

### The critical discipline (this is the fruitbank/idle-fruit trap — get it exactly right)
Reach-work bands (16/18/20) sit STRICTLY BETWEEN park (10) and anti-starvation (30/31), and
therefore strictly below EVERY genuine task (anti-starvation 30, chop-help 40/42, funding 58-65,
chop 70/72, harvest 75, banking 80/95). So a troll with ANY real task is UNAFFECTED — reach-work
can only ever be matched to a troll that would otherwise get PARK. Prove this ordering the way
D1/idle-fruit did (numeric: 20*BAND - eta_max still < 30*BAND, i.e. eta never exceeds ~10*BAND;
guard the value so it can't cross into the anti-starvation band even at eta→large). The matcher
then does WHO-does-what; there is NO per-troll idle logic and NO troll-behavior change.

### Guards
- reach-chop MUST consult `race()` and skip doomed trees (an enemy fells it before our ETA) —
  same as the fell bands and idle-fruit. Do not send a troll to donate travel to a doomed tree.
- Full-carry troll gets no reach-plant/harvest it can't hold (respect free_capacity like other bands).
- Endgame: reach-work's low band means banking (95)/full-bank (80) always outrank it — no special
  endgame handling needed, but confirm a reach-work trek can't strand carry past game end (it can't
  outrank banking, so it won't).
- This is OUT-PRODUCE, not counter-raid: reach-work targets neutral/our trees & fruit & plant
  cells (producing), never enemy trolls. Going for a neutral tree in enemy territory is fine
  (still producing); do not add any attack behavior.

## Where the code lives
- `rust/src/botmain/planner.rs` `candidates()` — the per-troll task producer (this is the ONLY
  behavior change: add the reach-work Cands). Reuse the existing per-troll distance map `d` (BFS
  from the troll) for eta; find nearest reachable trees/fruit/plant cells from it.
- Do NOT touch the matcher (`select_assignments`/`assign_resolved`), motion, or any real band.

## Tests (TDD, RED first, record actual failing output)
1. `taskfloor_idle_troll_gets_reachwork_not_park`: a state where a troll has NO normal task
   (local exhausted) but a reachable wild tree exists across the map. RED pre-fix: the troll's
   best candidate is PARK. GREEN post-fix: its best candidate is reach-chop toward that tree.
2. `taskfloor_never_displaces_real_work` (the trap guard, Test-B style): a troll with an
   available real task (e.g. chop-help 40 or anti-starvation 30) AND a nearby reachable tree.
   Assert the real task still wins — reach-work does NOT displace it. Must pass pre- AND
   post-fix. Flip-check: raise a reach-work band above 30 and assert THIS test fails (proving
   the ordering is load-bearing), then restore.
3. `taskfloor_two_idle_trolls_two_targets`: two idle trolls + two reachable trees → the two
   trolls get two DIFFERENT reach-chop targets (the matcher spreads them), not both the same.
4. `taskfloor_barren_map_parks`: a truly barren reachable map (no trees/fruit/plant cells) → the
   troll still PARKS (graceful; reach-work only fires when reachable work exists).
5. `taskfloor_reachchop_skips_doomed`: a reachable tree an enemy fells first → reach-chop is NOT
   emitted / not chosen (race guard), troll falls back to next reach-work or park.
6. Determinism: nearest-K selection uses canonical (sorted by (dist, cell)) order — no HashSet
   iteration into the chosen targets.

## Gates (standard builder procedure + one candidate-specific validation)
- `cargo test --release` all green (baseline 76; +6 new) + self-determinism equality 8 seeds.
- ★ THE key validation (this bug the sim CAN reproduce, unlike chokepoints): build the DEBUG
  probe (with the @TFASSIGN-style park visibility — OR just count MOVE-to-self idle turns from
  @TFMOVE), play >=4 games vs Crouistiti (6479836) and vs boss, and report the PARK/idle-turn
  count per game vs the pre-fix baseline (28-82 idle turns vs Crouistiti). Expect idle turns to
  DROP sharply toward ~0. If idle turns do NOT drop, the fix isn't firing — investigate before
  freezing. (This is the direct proof the producer no longer underflows.)
- NOTE the champion-equality caveat: this DOES change behavior whenever a troll would park, so
  it is NOT a no-op — do NOT expect stream-equality vs the champion. The band-ordering + Test 2
  are the "doesn't displace real work" guard instead.
- bundle -> rustc -> minify <100KB -> compile-check; freeze artifacts + debug probe.
- VERSION -> "1.55.0-taskfloor". Base = current session-2026-07-01 HEAD (champion line; VERSION
  currently 1.53.0-pressurefarm — orthogonal to the parked governor). Preserve all champion
  consts. Commit per step with the trailer `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.

## For later stages
- Arena isolation: baseline = the pre-taskfloor tree. This is the transfer class (idle turns ->
  productive turns) and the biggest measured waste (up to 82 idle turns/game) — the strongest
  arena bet of the current game-review batch.
