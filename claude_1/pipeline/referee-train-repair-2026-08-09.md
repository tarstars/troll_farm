# Referee TRAIN repair — exhaustive command dispatch, TRAIN, MINE

- Author: `claude_1` (implementer; own file, executed)
- Date: 2026-08-09
- Branch: `agent/claude_1-banana-restoration-r2`
- Commits: `7edfd17c` (RED) → `5df633f5` (GREEN) → this report
- **Instrument version: `fuzz-panel/2-train`  |  Corpus version: `c2-train-2026-08-09`**
  (bumped from the unversioned pre-repair instrument, retro-named `fuzz-panel/1` /
  `c1`; declared in `fuzz-panel-config.json`, enforced by `load_config`, echoed in
  every report header and JSON payload)

Every number below is marked **MEASURED** (I ran it, command given) or **INFERRED**
(reasoning from source I read). Input digests are in §0.

---

## 0. Inputs — SHA-256

| file | sha256 |
|---|---|
| `claude_1/pipeline/fuzz_panel.py` (post-repair, incl. the `:485` citation fix) | `ab2d3b29de83aeaace03efaf8318d4aa9d9c18a090157db634117067f349823e` |
| `claude_1/pipeline/test_fuzz_panel.py` (post-repair) | `4ffe68f8987af8f17da8af1e1edbd702f0585de6385c195cf277c771a1dd51ca` |
| `claude_1/pipeline/fuzz-panel-config.json` (post-repair) | `f4018737aa7dfe39a21d0b87e669f51a9487785b5127a2041c686963f6b828a3` |
| `rust/src/bin/yamo_orchard_live.rs` (**authoritative engine, untouched**) | `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f` |
| `cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs` | `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55` |
| `claude_1/banana-restoration-r2/make_banana_traces.py` (referee core, **not edited**) | `daf9996b2fa40d4a0f5b16dfc7bfd3c9d75c372d4c5761dac4327ce42e3f33d5` |
| `claude_1/banana-restoration-r2/trace_detectors.py` (**not edited**) | `59dce10dc87797bc6b1b8da0f628f4ddd82b561d93946fa91453d2ea40805209` |
| `rust/src/game/engine.rs` (secondary reference, read-only) | `7c240abfcfdf678993960fe73440735a19f934596c9651bdf915e2902f78fb05` |
| floor config BEFORE (`cfg-before.json`) | `5c8f6a7d31ceb6c74cbeaaeffc2f65aa2ddde733632e517d00f7601f51771a49` |
| floor config AFTER (`cfg-after.json`) | `0713e39b5fe9212c1c39aba0fd9b6799f9b4c3510b0ed99311f0e1a88549412e` |

`rust/src/bin/yamo_orchard_live.rs` was **read only** — the digest above is unchanged
from the pre-repair tree and matches the declared sacred prefix `fff6669b`.

---

## 1. The defect

`grep -c TRAIN claude_1/pipeline/fuzz_panel.py` returned **0** (pre-repair; **38** in
the RED test file and **29** in the implementation now). `FuzzReferee` inherited
`make_banana_traces.Referee.apply`, whose dispatcher is

```python
if verb in ("MSG", "WAIT", "TRAIN"):
    continue
...
elif verb == "DROP":
    ...
# <- nothing here: every other verb falls out of the bottom
```

Two distinct failure modes in one construct:

1. **TRAIN was named in a skip list** — a deliberate-looking no-op with no record that
   it was unimplemented rather than effect-free.
2. **Every verb not in the if/elif chain was silently discarded** — a *default branch
   by omission*. That is how **MINE** was also being thrown away, unnoticed, for the
   whole life of the panel (§6).

**MEASURED** — the consequence on the 240-game floor (self-vs-self `a8eb3b2b`,
pre-repair instrument):

| | value |
|---|---|
| TRAIN commands emitted, all 240 games | **348** |
| games containing any TRAIN | **2** — `m040` seat 0, `m040` seat 1 |
| `m040` seat 0 | TRAIN on **166 of 200** turns, every turn `t=35 … 200` |
| `m040` seat 1 | TRAIN on **182 of 200** turns, every turn `t=19 … 200` |
| verdict on both | **CLEAN — D-1..D-9 all zero, `block=False`** |
| MINE commands emitted, all 240 games | **349** across **15** games |

Command (census over the archived pre-repair corpus):

```
python3 - <<'EOF'   # reads games-before/games.jsonl.gz written by the run in §5
import gzip, json, collections
verbs = collections.Counter(); games = collections.Counter()
for line in gzip.open(".../games-before/games.jsonl.gz", "rt"):
    r = json.loads(line); seen = set()
    for ln in r["artifacts"]["candidate_commands"].splitlines():
        for cmd in ln.split(";"):
            if cmd.strip():
                v = cmd.split()[0].upper(); verbs[v] += 1; seen.add(v)
    for v in seen: games[v] += 1
print(dict(verbs)); print(dict(games))
EOF
```

Result: `{'MSG': 240, 'WAIT': 55070, 'MOVE': 10797, 'HARVEST': 226, 'DROP': 1185,
'CHOP': 7913, 'PICK': 431, 'PLANT': 429, 'MINE': 349, 'TRAIN': 348}`.

The bot re-emits TRAIN forever because its own `can_train` reads the *referee's*
serialized unit list: the worker count `n` never rises, so `can_train` stays true.
The panel's two most pathological games were therefore among its best, and a
candidate could be rewarded for provoking a state that displaces real work while
remaining invisible.

---

## 2. Requirement 1 — the exhaustive dispatcher (the most important item)

`FuzzReferee.apply` now owns the dispatch. Design:

```python
VERB_HANDLERS = {                 # class attribute; ONE handler per verb
    "MSG": _cmd_noop,   "WAIT": _cmd_noop,
    "MOVE": _cmd_delegate, "HARVEST": _cmd_delegate, "CHOP": _cmd_delegate,
    "PLANT": _cmd_delegate, "PICK": _cmd_delegate,  "DROP": _cmd_delegate,
    "TRAIN": _cmd_train, "MINE": _cmd_mine,
}

for raw in self._ordered(raws):
    verb = self._verb(raw)
    handler = self.VERB_HANDLERS.get(verb)
    if handler is None:
        raise unsupported_command(verb, raw, self.turn)   # no default branch
    handler(self, raw.split(), raw)
```

Properties, and why each was chosen:

- **`UnsupportedCommand` subclasses `PanelError`.** `run_pair` converts candidate
  crashes (`RuntimeError`/`OSError`) into a per-game `P0` violation, i.e. into a
  *verdict*. An unimplemented verb must NOT become a verdict — the gate does not know
  what the world would have looked like, so it must refuse to judge. `PanelError`
  propagates through `pool.map` to `main()`, which prints the message and returns
  **exit 2 (`EXIT_ERROR`)**. One unsupported verb, on one turn, of one game,
  terminates the entire run.
- **Single-argument (message-only) exception**, constructed by the module function
  `unsupported_command(verb, raw, turn)`. Custom `__init__` signatures do not survive
  the multiprocessing pool's pickling of worker exceptions; this shape does.
  **MEASURED** — the end-to-end test runs the panel with `processes` defaulted (pool
  path) and gets exit 2 with the message intact.
- **The message names the remedy**: implement the verb in `VERB_HANDLERS` with
  conformance tests against `yamo_orchard_live.rs`, or withdraw it from the corpus.
- **`SUPPORTED_COMMANDS` / `ENGINE_COMMANDS`** are module constants and
  `test_dispatch_table_is_total_over_the_engine_verb_set` asserts
  `ENGINE_COMMANDS - SUPPORTED_COMMANDS == set()`. Adding a verb to the protocol
  without adding a referee handler is now a *test failure*, not a silent no-op.
- **Verbs are matched case-insensitively**, mirroring the engine parser's
  `parts[0].to_uppercase()`.
- **Known verb, malformed arity → no-op, not termination.** The engine parser itself
  guards each verb with `if parts.len() >= k`. Arity is a legality question, not a
  dispatch question; only an *unknown verb* is a dispatch failure.

**MEASURED** — end to end, verb `TELEPORT`:

```
python3 -m unittest test_fuzz_panel.TestExhaustiveDispatch
```

`test_panel_exits_gate_unready_on_an_unsupported_verb` compiles a planted bot that
emits `TELEPORT 0 1 1` every turn, runs `fp.main`, and asserts exit 2 with
`GATE_UNREADY` and `unsupported_command` on stderr.

**MEASURED** — and on the real floor, with `MINE` removed from the table (§6):

```
fuzz_panel: tool/config error: GATE_UNREADY / unsupported_command: the referee
implements no handler for verb 'MINE' (turn 14, command 'MINE 0'); the panel cannot
render a verdict on a world it cannot simulate. …
exit=2
```

---

## 3. Requirement 2 — TRAIN, rule by rule, with source citations

Conformance reference: `rust/src/bin/yamo_orchard_live.rs` (read-only). Line numbers
are from the digest in §0.

### 3.1 The bill — `yamo_orchard_live.rs:196-204`

```rust
pub fn training_cost(n: i32, talents: (i32, i32, i32, i32)) -> Stock {   // :196
    let (ms, cc, hp, chop) = talents;
    let mut cost = [0; 6];
    cost[PLUM]  = n + ms * ms;                                            // :199
    cost[LEMON] = n + cc * cc;                                            // :200
    cost[APPLE] = n + hp * hp;                                            // :201
    cost[IRON]  = n + chop * chop;                                        // :202
    cost
}
```

Mirror: `fuzz_panel.training_cost(n, talents)`. `n` is the **current** own-unit
count, not the post-spawn count. BANANA (slot 3) and WOOD (slot 5) are never billed —
their cost entries stay 0. **MEASURED** by `TestTrainingCost` (three exact vectors
plus a BANANA/WOOD-always-zero sweep).

### 3.2 Worker cap and final-20-turn guard — `yamo_orchard_live.rs:834-838`

```rust
fn can_train(view: &GameState, stats: Stats) -> bool {                    // :834
    let n = view.units.iter().filter(|unit| unit.player == 0).count() as i32;  // :835
    if n >= 2 || TOTAL_TURNS - view.turn <= 20 {                          // :836
        return false;                                                     // :837
    }
```

with `pub const TOTAL_TURNS: i32 = 300;` at `:162`. Mirrored as `WORKER_CAP = 2`,
`TRAIN_GUARD_TURNS = 20`, `TOTAL_TURNS = 300` and `FuzzReferee.can_train`.

The referee needed a turn counter to evaluate the guard at all; it did not have one.
`FuzzReferee.turn` starts at 1 and increments once per applied command line, matching
the bot's own counter — `yamo_orchard_live.rs:6017-6023`:

```rust
let mut turn = 1;
while let Some(view) = read_turn(&mut reader, &map, turn) { … turn += 1; }
```

**MEASURED**: `test_final_twenty_turn_guard` (turn 280 refused, turn 279 allowed),
`test_worker_cap_stops_further_training`,
`test_referee_turn_counter_advances_one_per_applied_command_line`.

### 3.3 Affordability and the iron guard — `yamo_orchard_live.rs:839-844`

```rust
let cost = training_cost(n, stats.tuple());                               // :839
let pay_iron = !view.iron.is_empty();                                     // :840
view.inventories[0][PLUM]  >= cost[PLUM]                                  // :841
    && view.inventories[0][LEMON] >= cost[LEMON]                          // :842
    && view.inventories[0][APPLE] >= cost[APPLE]                          // :843
    && (!pay_iron || view.inventories[0][IRON] >= cost[IRON])             // :844
```

Mirrored as `FuzzReferee.train_billed_items()` → `[PLUM, LEMON, APPLE]` plus `IRON`
**iff the map has any iron cell**, and `can_train` requires `inv[i] >= cost[i]` for
each (`>=`, not `>`). The same list is what `train()` deducts, so an item that is not
required is not charged either. Corroborated by `rust/src/game/engine.rs:531-536`,
which selects the pay slice `[0,1,2,3,4,5]` vs `[0,1,2,3,5]` on `!game.iron.is_empty()`.

**MEASURED**: `test_iron_is_billed_only_when_the_map_has_iron` (three arms: no iron →
`TRAIN 1 1 0 3` succeeds with `inv[IRON]` untouched; iron present with 9 iron →
refused; iron present with 10 iron → succeeds and pays exactly 10),
`test_unaffordable_train_is_rejected_and_charges_nothing` (also pins the `>=`
boundary: exactly-affordable is affordable).

### 3.4 Spawn cell = the own shack, and the occupied-shack refusal

`yamo_orchard_live.rs` does not contain a TRAIN apply path (see §7 UNRESOLVED-1), but
it states the spawn cell and the occupancy precondition from the bot's side: whenever
the bot decides to train and one of its units is standing on `view.shacks[0]`, it
manufactures a MOVE off the shack **for that same turn**.

`yamo_orchard_live.rs:1564-1571`:

```rust
let clear_cell = (train_now && unit.cell == view.shacks[0])
    .then(|| {
        ortho_neighbors(view.shacks[0])
            .into_iter()
            .filter(|cell| view.walkable.contains(cell))
            .min()
    })
    .flatten();
```

and again at `:3604-3619`:

```rust
if train_now
    && unit.cell == view.shacks[0]
    && !candidates.iter().any(|c| c.command.starts_with("MOVE "))
{ … push a MOVE off the shack at score 6_500 … }
```

A bot does not spend its unit's whole turn vacating a cell unless the spawn requires
it. Corroborated verbatim by `rust/src/game/engine.rs:543-547` ("Check shack is
unoccupied" — `if game.units.iter().any(|u| u.pos() == shack) { return; }`) and
`:556-566`, which pushes the new `Unit` at `x: shack.0, y: shack.1` with `carry: [0;6]`.

Mirror: `train()` refuses if **any** unit (either player) stands on `self.tent`, and
otherwise inserts the unit at `self.tent` with `carry = [0]*6`.
**MEASURED**: `test_occupied_shack_blocks_the_spawn`,
`test_legal_train_spawns_a_second_worker_and_charges_the_bill`.

### 3.5 Spawn stats and spawn id

Stats are the four TRAIN arguments in order — `yamo_orchard_live.rs:1548-1554` (and identically at `:3475-3481`):

```rust
out.push(format!("TRAIN {} {} {} {}",
    desired.movement_speed, desired.carry_capacity,
    desired.harvest_power, desired.chop_power));
```

so `(ms, cc, hp, chop)` → `(speed, cap, harvest, chop)` on the new unit. Non-numeric
talents parse to 0, mirroring the engine parser's `parse().unwrap_or(0)`; a TRAIN with
fewer than four talents is a no-op (`if parts.len() >= 5`).

The spawn id is `max(existing unit id) + 1`, which is the id the bot itself predicts —
`yamo_orchard_live.rs:485`, inside `read_turn`:

```rust
next_id = next_id.max(values[0] + 1);
```

**MEASURED**: `test_legal_train_spawns_a_second_worker_and_charges_the_bill` pins the
stats tuple, the cell, zero carry, `player == 0` and `nid == 6` (own 0 + opponent 5).

### 3.6 Turn timing — TRAIN's slot inside the turn

`rust/src/game/engine.rs:753` states the engine's command priority:

```
/// Priority order: MOVE, HARVEST, PLANT, CHOP, PICK, TRAIN, DROP, MINE,
/// then tick_plants, recompute_scores, turn++.
```

and `:751-800` applies exactly that order. **This is load-bearing, not cosmetic.** The
bot emits TRAIN **first** on its command line (`out.push(TRAIN)` before
`out.extend(selected)`, `yamo_orchard_live.rs:1546-1556` and `:3468-3483`) and relies
on the same turn's `clear_cell` MOVE to vacate the shack. A referee applying the line
in emission order would evaluate TRAIN while the unit is still standing on the shack,
hit the §3.4 guard, and refuse **every** TRAIN forever — reproducing the original
defect with extra steps.

`FuzzReferee._ordered` therefore moves TRAIN commands to just before the first
`DROP`/`MINE` on the line, preserving the emission order of everything else. This is a
**strict extension**: a command line containing no TRAIN is applied in exactly the
order the pre-repair referee used, so no non-TRAIN game can change through this rule.
(The rest of the line is still applied in emission order rather than in the engine's
global priority order — pre-existing drift, out of scope, see §7 UNRESOLVED-4.)

**MEASURED**: `test_turn_timing_train_resolves_after_moves_before_drops` runs
`"TRAIN 1 1 0 1;MOVE 0 1 0"` from a unit standing on the shack and asserts the spawn
happens, then `"TRAIN 1 1 0 1;MOVE 0 1 0;DROP 0"` and asserts the DROP banks the
mover's cargo while the freshly spawned worker is unaffected.

### 3.7 Companion fix — a spawned worker must be able to leave the shack

Shack cells are **not** walkable (`semantic_harness.parse_rows` puts `'0'` in
`shacks`, never in `walkable`; `yamo_orchard_live.rs:406-427` does the same). So a
worker spawned on the shack starts on a non-walkable cell. The pre-repair
`step_toward` did

```python
dist = self._bfs_from([target])
if current not in dist:
    return current          # <- frozen forever
```

The engine's `next_cell` seeds its BFS at the unit's own cell **regardless of
walkability** (`rust/src/game/engine.rs:99-123`, with `bfs_distances` at `:72-92`
inserting every source at distance 0 and expanding only into walkable cells), so the
unit can step out to a walkable neighbour. `step_toward` now mirrors that.

The extension is inert on everything the pre-repair panel could produce.
**MEASURED**: across all 240 pre-repair games, the number of games in which any unit
ever occupied a non-walkable cell is **0** (probe: rebuild each `td.Trace` from the
archived transcript and test `u.cell in tr.smap.walkable` for every unit of every
turn). Without this fix the TRAINed worker on `m040` would sit on the shack for the
remaining 165 / 181 turns and the repair would have swapped one fiction for another.

**MEASURED**: `test_a_spawned_worker_can_leave_the_shack`.

---

## 4. Requirement 3 — D-9 (context, no work done)

No detector code was touched (`trace_detectors.py` digest unchanged, §0). D-9's
`banana_before_train` proxy stays retired and its paired clauses remain
`INSTRUMENT_UNSUPPORTED`. Recorded here because this repair bears on that ruling:

**MEASURED** — over the full 240-game corpus, the number of games in which the
**parent** emits any TRAIN is **2** (both `m040`), not 0. The
`d9-calibration-execution-review-2026-08-08.md` figure of "**0** games in which the
parent emits any TRAIN" was taken over **"60 of 240 games, first 60 jobs"** — map
indices `m000`–`m029`, which exclude `m040`. Probe:

```
python3 -c '... td.CommandParser().parse(artifacts["parent_commands"]) ;
            first turn with tc.train is not None ...'
```

Result, both before and after the repair: `m040 seat 0 → parent first TRAIN t=35`,
`m040 seat 1 → t=19`; `td.detect_d9` on those two games returns `PASS 0` in all four
combinations. So D-9's paired block (`trace_detectors.py:1210`, gated on
`p_train is not None`) *does* execute — on exactly 2 of 240 games — and finds nothing.
That does not change the review's verdict (2/240 is still effectively unexercised),
but the stated premise "never happens on this map/opponent mix at a 200-turn horizon"
is corpus-dependent and should be restated as "on 2 of 240 games". Flagged to the D-9
owner; **no action taken here**.

Corpus-wide D-9 output is unchanged by this repair: 196 episodes across 74 games
before and after (§5).

---

## 5. Requirement 5 — the floor, before → after

Recipe as specified: both `parent.source` and `candidate.source` set to the ABSOLUTE
`/home/tarstars/prj/troll_farm-claude_1/cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs`
(`a8eb3b2b…`), distinct `crate`, fresh `games_dir`. Configs are byte-identical apart
from `task`, `games_dir` and the version keys (digests in §0).

```
# BEFORE  (pre-repair working tree, commit 0d4ba238)
python3 claude_1/pipeline/fuzz_panel.py --config cfg-before.json \
        --report report-before.md --json before.json
→ fuzz_panel: BLOCK (240 games, 118 blocking, 0 flagged, 16.2 s)

# AFTER   (commit 5df633f5)
python3 claude_1/pipeline/fuzz_panel.py --config cfg-after.json \
        --report report-after.md --json after.json
→ fuzz_panel: BLOCK (240 games, 119 blocking, 0 flagged, 11.2 s)
```

**MEASURED. The floor got worse: 118 → 119 blocking games of 240.** Verdict BLOCK in
both. Nothing was tuned toward any number; the only knob touched in the config is the
version pair.

### 5.1 Per-detector / per-property breakdown

Games with at least one blocking violation of each kind, and total episodes:

| property / detector | games before | games after | Δ | episodes before | episodes after | Δ |
|---|---|---|---|---|---|---|
| D-1 | 32 | **33** | **+1** | 35 | **36** | **+1** |
| D-2 | 0 | 0 | 0 | 0 | 0 | 0 |
| D-3 | 0 | 0 | 0 | 0 | 0 | 0 |
| D-4 | 6 | 6 | 0 | 6 | 6 | 0 |
| D-5 | 1 | 1 | 0 | 1 | 1 | 0 |
| D-6 | 9 | 9 | 0 | 15 | 15 | 0 |
| D-7 | 0 | 0 | 0 | 0 | 0 | 0 |
| D-8 | 0 | 0 | 0 | 0 | 0 | 0 |
| D-9 | 74 | 74 | 0 | 196 | 196 | 0 |
| P0 (protocol liveness) | 0 | 0 | 0 | 0 | 0 | 0 |
| P2 (R-5 alternation) | 4 | **5** | **+1** | 4 | **5** | **+1** |
| P3 (orchard inertness) | 0 | 0 | 0 | 0 | 0 | 0 |
| P4 (liveness) | 30 | 30 | 0 | 30 | 30 | 0 |
| **blocking games (union)** | **118** | **119** | **+1** | | | |
| report-tier flags | 0 | 0 | 0 | | | |

By map class and opponent profile:

| class | games | blocking before | blocking after |
|---|---|---|---|
| choke_corridor | 60 | 32 | 32 |
| **forest_dense** | 20 | **3** | **4** |
| forest_sparse | 16 | 9 | 9 |
| multi_door | 24 | 11 | 11 |
| open_field | 36 | 18 | 18 |
| orchard_eligible | 24 | 11 | 11 |
| single_door_tent | 24 | 16 | 16 |
| water_diagonal | 36 | 18 | 18 |

| opponent profile | games | blocking before | blocking after |
|---|---|---|---|
| chopper_aggressor | 72 | 29 | 29 |
| **harvester** | 96 | **46** | **47** |
| idle | 72 | 43 | 43 |

Other corpus statistics: `banana_activated_games` 157 → **159**;
`orchard_eligible_games` 12 → 12; `orchard_inertness_checks_passed` 12 → 12.

### 5.2 What moved, and attribution

**MEASURED** — **17 of 240 game rows changed at all**:

```
m002 s0/s1  m031 s0/s1  m040 s0/s1  m043 s0/s1  m048 s0
m062 s0/s1  m085 s0/s1  m101 s0/s1  m119 s0/s1
```

= the 2 TRAIN games + the 15 MINE games. The other 223 rows are byte-identical, which
is the expected consequence of both changes being strict extensions.

To separate TRAIN's effect from MINE's I ran a third floor with TRAIN implemented and
MINE reverted to a *dispatched* no-op (scratch copy, not committed):

| floor | blocking | rows differing vs BEFORE |
|---|---|---|
| BEFORE (`c1`) | 118 | — |
| TRAIN only, MINE still discarded | **119** | exactly `m040` s0, `m040` s1 |
| AFTER (`c2`, TRAIN + MINE) | **119** | the 17 rows above |

So **the entire +1 is TRAIN**; MINE changes 15 games' world states (and their scores)
without changing any verdict. Command emission over the corpus:

| | before | after |
|---|---|---|
| TRAIN commands | 348 | **2** |
| MINE commands | 349 | **27** |

MINE drops because mining now actually yields iron, so the bot stops re-issuing it;
TRAIN drops to exactly one per `m040` game.

Summed candidate score over the 17 changed rows: **620 → 675**. The repaired referee
is *kinder* to the bot in aggregate (it gets a second worker and it gets its iron) and
still produces one more blocking game — the extra worker creates a defect the
single-worker fiction could not.

---

## 6. MINE — the same defect, found by the new dispatcher

MINE was never implemented and was being silently discarded by the same missing
default branch. The exhaustive dispatcher surfaced it immediately.

**MEASURED counterfactual** — with `MINE` simply absent from `VERB_HANDLERS`, the
floor run terminates on the first MINE (`m002`, turn 14) with
`GATE_UNREADY / unsupported_command`, **exit 2**, and no verdict at all. Requirement 5
(rerun all 240, report the floor) is unsatisfiable in that state, so MINE had to be
implemented. I flag this explicitly because it is scope beyond the literal
"implement TRAIN" instruction, and it is exactly the outcome requirement 1 is designed
to force.

Rules implemented:

- **Emission gate / adjacency**, `yamo_orchard_live.rs:936-944`:
  ```rust
  fn iron_candidates(view: &GameState, unit: &Unit, base_score: f64) -> Vec<Candidate> {
      if view.iron.iter().any(|iron| is_adjacent(*iron, unit.cell)) {
          out.push(Candidate { command: format!("MINE {}", unit.id), … });
  ```
  with `is_adjacent(a, b) = manhattan(a, b) == 1` at `:239-241`. **Orthogonal
  adjacency to an iron cell**, not standing on it (iron cells are not walkable).
- **The mined item is IRON (slot 4)** — `yamo_orchard_live.rs:4879-4887` verifies a
  successful mine by `unit.carry[IRON] > before_iron`.
- **Yield = `min(chop_power, free_capacity)`, and nothing without chop power or free
  capacity** — **INFERRED**: this is *not* stated in the authoritative file. Taken
  from `rust/src/game/engine.rs:646-667` (`apply_mine`). See §7 UNRESOLVED-2.

**MEASURED**: `TestMineApplication` — yield with adjacency, no-op without adjacency /
without chop power / at full capacity, and the `min(chop, free)` cap.

---

## 7. UNRESOLVED

1. **The "authoritative engine" is a bot, and it is stricter than the repo's actual
   engine.** `rust/src/bin/yamo_orchard_live.rs` contains `game::rules` (shared
   constants, `training_cost`) and the bot-side `can_train` gate, but **no TRAIN apply
   path**. The repo's real simulator, `rust/src/game/engine.rs::apply_train`
   (`:525-568`), enforces **only** affordability (with the iron guard) and the
   unoccupied shack — it enforces **neither the worker cap nor the final-20-turn
   guard**; those exist only as the bot's own self-restraint in `can_train`. Per the
   brief I implemented `can_train` as *referee legality*, which is **stricter** than
   `engine.rs`. Consequence: a bot that emits TRAIN at `n == 2`, or inside the last 20
   turns, is refused by this referee but would spawn a third worker on the platform
   engine. **This needs an owner ruling.** It is not academic — a candidate whose
   whole strategy is a third worker would be measured against a world that forbids it,
   which is the same class of error this repair removed. Nothing in the current
   corpus exercises it (`TOTAL_TURNS = 300`, panel horizon 200, so the 20-turn guard
   is unreachable; and no bot in the corpus reaches `n == 2` and keeps training).
2. **MINE's yield rule is INFERRED** from `engine.rs`, not from the authoritative
   file, which states only the adjacency precondition and the IRON slot. If
   `min(chop, free)` is wrong, 15 games' iron economies are wrong (though, MEASURED,
   no verdict depends on it today).
3. **`next_id`.** I use `max(existing id) + 1` — the predictor the bot itself computes
   at `yamo_orchard_live.rs:485`. `engine.rs` uses a monotone global `game.next_id`.
   These diverge only if units can die and ids be reused; nothing in this referee
   removes units. INFERRED-equivalent, not proven.
4. **Only TRAIN's position in the turn is engine-conformant.** The rest of a command
   line is still applied in emission order rather than the engine's global priority
   (`MOVE, HARVEST, PLANT, CHOP, PICK, …`). This is pre-existing drift in the
   inherited referee and I deliberately did not change it, because reordering every
   line would move the floor for reasons unrelated to TRAIN. It is a real conformance
   gap and a candidate for the next repair.
5. **`make_banana_traces.Referee.apply` still contains the original silent-default
   dispatcher** and is still used by that module's own scenarios. It is outside my
   boundary. Any other consumer of that referee has the same defect.
6. **`m040` seat 0 is still CLEAN** after the repair (§8). Its game changed
   completely, but no detector fires on it. Whether that is correct or whether the
   detectors are blind to the new two-worker behaviour is not something this repair
   can answer.

---

## 8. Requirement 4 — the two `m040` rows

Identity (pinned in `test_m040_identity_is_pinned`): map index **40** of the committed
config, class **forest_dense**, opponent **harvester**, `roster.second is None` — a
**one-worker** game on both seats. Both seats are now **mandatory committed regression
tests** in `test_fuzz_panel.py::TestM040RegressionRows`, which compile the real floor
submission `a8eb3b2b…` and run the full 200-turn closed loop for each seat. They are
not to be removed.

### 8.1 ARCHIVE — the old, instrument-invalid results (corpus `c1`, do not delete)

Verbatim from `before.json` (pre-repair run, §5):

```json
("m040", 0)  {"block": false, "violations": [], "flags": [], "turns": 200,
  "detector_counts": {"D-1":0,"D-2":0,"D-3":0,"D-4":0,"D-5":0,
                      "D-6":0,"D-7":0,"D-8":0,"D-9":0},
  "candidate": {"inventory":[2,2,1,2,0,18],"score":79,
                "opp_inventory":[35,7,8,37,0,0],"opp_score":87,"margin":-8}}
  TRAIN emitted on turns 35,36,37,…,200  (166 of 200)

("m040", 1)  {"block": false, "violations": [], "flags": [], "turns": 200,
  "detector_counts": {"D-1":0,"D-2":0,"D-3":0,"D-4":0,"D-5":0,
                      "D-6":0,"D-7":0,"D-8":0,"D-9":0},
  "candidate": {"inventory":[2,2,1,2,0,20],"score":87,
                "opp_inventory":[36,0,30,36,0,0],"opp_score":102,"margin":-15}}
  TRAIN emitted on turns 19,20,21,…,200  (182 of 200)
```

**These two results are INSTRUMENT-INVALID.** They were produced by a referee that
discarded every one of those 348 TRAIN commands. They are retained as the historical
record of the defect and must not be cited as evidence about the bot.

### 8.2 What the two games do now (corpus `c2`)

**MEASURED** (`after.json`, and the archived command streams):

| | `m040` seat 0 | `m040` seat 1 |
|---|---|---|
| TRAIN turns | **35** only | **19** only |
| the TRAIN line | `TRAIN 1 1 0 1;MOVE 0 2 1` | `TRAIN 1 1 0 1;MOVE 0 8 0` |
| next turn | `MOVE 0 2 0;MOVE 6 1 1` | `MOVE 0 7 0;MOVE 6 8 1` |
| own workers at end | **2** (ids 0 and 6) | **2** (ids 0 and 6) |
| score / margin | 79 / −8 → **92 / +17** | 87 / −15 → **80 / −10** |
| **verdict** | `block=False` (still CLEAN) | **`block=True` — NEWLY BLOCKING** |

The `MOVE 0 …` on the TRAIN turn is the `clear_cell` manoeuvre of §3.4; the spawned
worker (`id 6`) starts moving on the very next turn, which is the §3.7 fix working.

**`m040` seat 1 blocks on two violations, both about the SAME episode:**

- **P1 / D-1**, 1 episode:
  `{"unit": 0, "turn_start": 80, "turn_end": 86, "k": 3, "cells": [[4,0],[3,0]]}`
- **P2** (R-5 alternation clause):
  *"full wood carrier (carry [0,0,0,0,0,2], free_capacity 0) exhibits a two-cell
  alternation cells (4,0)<->(3,0) over turns 80-86 (7 states, >= 3 A->B->A cycles)
  with cargo unchanged and no DROP — violates I-19 (no monotone door approach), I-20
  (non-progress beyond the one-turn conflict tolerance) and I-21 (banking commitment
  never completes); a D-1 episode by construction."*

Unit **0** — the original worker, not the spawned one — sits full of wood and
oscillates between two cells for seven turns instead of banking. This is a genuine
two-worker interaction defect that **could not exist** while the referee pretended the
second worker was never built. It is the direct answer to the brief's concern: the
pathological state was not merely invisible, it was *masking* a real defect.

`m040` seat 0 remains CLEAN — see §7 UNRESOLVED-6.

---

## 9. TDD and the mutation ledger

### 9.1 RED

Commit **`7edfd17c`**, tests committed with recorded failing output:

```
python3 -m unittest test_fuzz_panel test_pre_review
Ran 91 tests in 8.820s
FAILED (failures=8, errors=17)
```

including, verbatim:

```
AssertionError: 166 != 1 : m040 seat 0: TRAIN must be emitted once and then stop
                           -- it was re-emitted on 166 of 200 turns before the repair
AssertionError: 182 != 1 : m040 seat 1: TRAIN must be emitted once and then stop
                           -- it was re-emitted on 182 of 200 turns before the repair
```

covering all four mandated RED clauses: (a) unknown verb → `GATE_UNREADY /
unsupported_command`, at unit level and end-to-end through `fp.main` → exit 2;
(b) a legal TRAIN spawns a second worker, charges the bill, and the cap stops the
next one; (c) illegal TRAIN — unaffordable, at cap, inside the final-20-turn guard —
rejected exactly as the engine rejects it; (d) both `m040` rows.

### 9.2 GREEN

Commit **`5df633f5`**, minimal implementation:

```
python3 -m unittest test_fuzz_panel test_pre_review
Ran 91 tests in 8.808s
OK
```

Both suites pass. (`test_fuzz_panel` alone: 67 tests, OK.)

### 9.3 Mutation check — 12 mutations, **12 CAUGHT, 0 SURVIVED**

Method: copy `fuzz_panel.py` / `test_fuzz_panel.py` / the config into a scratch tree
(with `banana-restoration-r2` and `cgauto` symlinked so the real floor bot is
reachable), apply exactly one mutation to `fuzz_panel.py`, run the whole
`test_fuzz_panel` suite, record the result. Harness:
`scratchpad/train-repair/mutate.py`. Nothing in the repo was mutated.

| # | mutation | result | first tests that caught it |
|---|---|---|---|
| M1 | wrong bill: `cost[PLUM] = n + ms` (linear, not squared) | **CAUGHT** | `test_bill_matches_the_engine_formula` |
| M2 | cap off-by-one: `n > WORKER_CAP` instead of `n >= WORKER_CAP` | **CAUGHT** | `test_worker_cap_stops_further_training` |
| M3 | final-20-turn guard removed | **CAUGHT** | `test_final_twenty_turn_guard` |
| M4 | spawn cell wrong (a door instead of the shack) | **CAUGHT** | `…spawns_a_second_worker…`, `…can_leave_the_shack`, `…visible_in_the_serialized_state` (3) |
| M5 | **dispatcher default restored** (`if handler is None: continue`) | **CAUGHT** | `test_unknown_verb_raises_gate_unready`, `…anywhere_in_a_multi_command_line`, `test_panel_exits_gate_unready_on_an_unsupported_verb` (3) |
| M6 | iron guard removed (always bill IRON) | **CAUGHT** | 5 tests incl. **both `m040` rows** |
| M7 | TRAIN applied in emission order (timing rule removed) | **CAUGHT** | `test_turn_timing_train_resolves_after_moves_before_drops` |
| M8 | occupied-shack guard removed | **CAUGHT** | `test_occupied_shack_blocks_the_spawn` |
| M9 | MINE handler → no-op (the original MINE defect, restored) | **CAUGHT** | `test_mine_yields_iron_when_orthogonally_adjacent`, `test_mine_is_capped_by_free_capacity` |
| M10 | non-walkable-source escape reverted (spawned worker frozen) | **CAUGHT** | `test_a_spawned_worker_can_leave_the_shack`, `test_turn_timing…` |
| M11 | bill computed but never charged | **CAUGHT** | `…spawns_a_second_worker…`, `test_iron_is_billed_only_when_the_map_has_iron` |
| M12 | spawn id hard-coded (collides with the id rule) | **CAUGHT** | `…spawns_a_second_worker…` |

**M5 — the restored silent default — is caught by three tests.** That was the explicit
anti-vacuity requirement.

**One mutation initially SURVIVED and the test was strengthened in response.**
`M2` (cap off-by-one) first passed the whole suite: the original cap test trained once
and then immediately trained again, leaving the spawned worker standing on the shack,
so the *occupied-shack* guard — not the cap — refused the second TRAIN, and an
off-by-one cap was unobservable. The test now MOVEs the spawned worker off the shack,
asserts the shack is free, and only then asserts refusal (and that `can_train` itself
is false). M2 is CAUGHT after that change. Recording this because a green mutation
ledger whose greenness came from a masking precondition is exactly the vacuity this
programme keeps finding.

---

## 10. Reproduction

```
cd /home/tarstars/prj/troll_farm-claude_1
export PATH="$HOME/.cargo/bin:$PATH"

# suites
python3 -m unittest -v test_fuzz_panel test_pre_review     # cwd: claude_1/pipeline

# floor (AFTER); ~12 s
python3 claude_1/pipeline/fuzz_panel.py \
    --config <cfg with both sources = cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs> \
    --report <out.md> --json <out.json>

# mutation ledger
python3 <scratchpad>/train-repair/mutate.py
```

The floor configs are scratch artifacts (digests in §0); the committed
`fuzz-panel-config.json` is unchanged apart from the version keys and the corpus-bump
note, so the committed candidate-vs-parent panel keeps its own identity.
