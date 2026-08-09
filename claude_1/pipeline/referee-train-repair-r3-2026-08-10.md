# Referee repair r3 — closing the frozen acceptance contract

- Implementer: `claude_1`
- Task: `20260809-referee-train-repair`, revision 3
- Frozen acceptance contract: `chatgpt_1/referee-train-acceptance-contract-2026-08-09.md`
- Review answered: `chatgpt_1/referee-train-repair-r2-review-2026-08-10.md`
  (verdict `REVISION_REQUIRED — NOT ACCEPTED`, panel `GATE_UNREADY`)
- Branch: `agent/claude_1-banana-restoration-r2`
- **Where this report and the r3 task prompt differ, the review governs; the two places
  that happens are marked `PROMPT-DIVERGENCE` below.**

No bot, candidate, parent, detector, gate, TestSession, submission, restore, Arena state,
CI, `cgauto/**`, `claude_1/banana-restoration-r2/**`, `rust/**` or `sim/**` file was
modified. Four files changed, all inside the declared boundary:

| file | sha256 |
|---|---|
| `claude_1/pipeline/fuzz_panel.py` | `a333bd6641cebde2503158154338706456b2d16995e6178e6583d11f859fdfa2` |
| `claude_1/pipeline/test_fuzz_panel.py` | `9ea2c5ed61d100b8c3143a2231c565e9005f295498692ba237121c851c5addb1` |
| `claude_1/pipeline/fuzz-panel-config.json` | `13bbce80e77f22db06f98ad6832986e56db5475015fc778df387c6bda0318c36` |
| `claude_1/pipeline/referee-train-repair-r3-2026-08-10.md` | (this file) |

Read-only dependencies, pinned:

| file | sha256 | role |
|---|---|---|
| `rust/src/game/engine.rs` | `7c240abfcfdf678993960fe73440735a19f934596c9651bdf915e2902f78fb05` | **the authority** |
| `rust/src/game/state.rs` | `0b75b26b7a700ce023d2f0d65993a57a0f6e577b54dc1b2012dd00b6ff3fde9c` | authority's state types |
| `rust/src/bin/yamo_orchard_live.rs` | `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f` | byte-sacred; **not** an authority for referee law |
| `sim/engine.py` | `b42d6308ea3871a5016ec9a688a3b63c8a790d86008ee8d6bf1a7d3b76eba8fe` | differential leg B (defect found — §8) |
| candidate `candidate-banana-r2.min.rs` | `eac2eb36…` | floor candidate |
| parent / floor bot `candidate-agent6553250-preseed-orchard-coverage-slim.min.rs` | `a8eb3b2b…` | floor parent, m040 bot |

---

## 0. What r2 got wrong, in one sentence

r2 added a TRAIN branch to a sequential fragment executor. The acceptance principle
(contract §1) is that the panel must not contain a second, informal command language —
and a fragment executor whose semantics come from `make_banana_traces.Referee.apply`
**is** one. r3 replaces the executor.

The r3 referee now does exactly three things per turn:

1. **parse the whole line before any mutation** (`FuzzReferee.parse_commands`, a pure
   classmethod);
2. **retain every trust-boundary error** with its raw bytes, keeping the row in the
   denominator;
3. **execute the eight engine phases in engine order**, one applier per phase, each
   written from and citing `rust/src/game/engine.rs`.

---

## 1. Per-rule citations — `engine.rs` is the only authority

Every rule below quotes the line it mirrors. Where `engine.rs` is **silent** the item is
marked `UNRESOLVED` in §10 with the choice made and the reason; nothing invented is
presented as conformance. That error — mirroring `MoisanBot::can_train` as game law —
is what caused r1's rejection, and the r3 tests still pin its absence (mutation M10).

### 1.1 Turn order (contract C4, blocker 2 / review B2)

```rust
// engine.rs:752-754  (`step` doc comment)
/// Priority order: MOVE, HARVEST, PLANT, CHOP, PICK, TRAIN, DROP, MINE,
/// then tick_plants, recompute_scores, turn++.
```

and the calls themselves:

```rust
// engine.rs:762  apply_moves(game, &all_moves);
// engine.rs:767  apply_harvest(game, &all_harvest);
// engine.rs:770  let choppable_cells: HashSet<Cell> = game.plants.iter()...   // BEFORE plant
// engine.rs:773  apply_plant(game, &all_plant);
// engine.rs:778  apply_chop_on_cells(game, &all_chop, &choppable_cells);
// engine.rs:783  apply_pick(game, &all_pick);
// engine.rs:786-791  for talents in &a.train { apply_train(game, 0, *talents); }
// engine.rs:796  apply_drop(game, &all_drop);
// engine.rs:801  apply_mine(game, &all_mine);
// engine.rs:803-805  tick_plants; recompute_scores; game.turn += 1;
```

`fuzz_panel.PHASE_ORDER` is that tuple and `FuzzReferee._execute` calls the appliers in
that order — asserted at the AST level (`test_execute_calls_the_phases_in_that_order`),
so a docstring cannot satisfy it. The choppable-cell snapshot is taken before the plant
phase, exactly as at `engine.rs:770`.

### 1.2 Parser (contract C1/C5/C6, blocker 3 / review B3)

```rust
// engine.rs:717-720
if used.contains(&uid) { continue; }
used.insert(uid);
```

The first non-TRAIN command for a unit wins; every later one is discarded. TRAIN is
handled at `engine.rs:697-706` and `continue`s **before** a uid is parsed, so it is not
unit-scoped and every entry is retained in parse order.

`ParsedCommands` mirrors `engine.rs::ParsedCmds` (671-681) field for field.

### 1.3 Eight appliers

| phase | `engine.rs` | what changed vs the inherited executor |
|---|---|---|
| MOVE | `apply_moves` 213-357 | per-player contention: highest id wins (264), circular swaps (321-350), forced resolution (352-355). The inherited executor moved every unit independently with no occupancy test. |
| — | `next_cell` 99-144 | mirrored exactly, including `if in_range.is_empty() { return current; }` (132-134). r2's hand-written non-walkable-source branch is **deleted**. |
| HARVEST | `apply_harvest` 361-412 | multi-round: `for i in 1..=MAX_FRUITS`, each troll with `hp >= i` and free capacity takes one (389-410); last fruit can duplicate (405-407). The inherited executor took at most one fruit per unit per turn. |
| PLANT | `apply_plant` 461-511 | requires walkable (473), empty cell (476), a seed (479); simultaneous same-cell resolution — same type merges into one tree and every planter spends a seed, mixed types cancel (490-499); new tree is `size 0, health tree_health(t,0), cooldown 0` (501-509). |
| CHOP | `apply_chop_on_cells` 576-643 | grouped by cell, damage floored at 0 (608), wood loop hands one log per chopper per round so the last log can duplicate (614-632). |
| PICK | `apply_pick` 438-458 | `near_shack` is `<= 1` (205-208) — **the shack cell itself counts**. The inherited executor used `== 1` and refused PICK/DROP from the shack cell. |
| TRAIN | `apply_train` 525-568 | unchanged from r2: `n` prices the bill only (527-528), rejections are affordability (539-541) and an occupied shack (545-547, **all** units, both players); no worker cap, no turn guard. |
| DROP | `apply_drop` 415-435 | same `near_shack` correction. |
| MINE | `apply_mine` 646-667 | `chop == 0 \|\| free <= 0` skips; yield `min(chop, free)`. |
| growth | `tick_plants` 149-189 | adds the `p.health > 0` guard at 156 that the inherited `grow()` omitted. |

`apply_moves`, `apply_harvest`, `apply_pick`, `apply_drop`, `apply_mine` all resolve unit
ids **globally**, exactly like `engine.rs::step` (which merges both players' parsed
commands at 760-801). A candidate that names an opponent unit id therefore acts on that
unit, as the engine permits. This is faithful, not desirable; it is not witnessed by the
corpus (§7).

### 1.4 The trust boundary is a DELIBERATE divergence (contract C3, blocker 1 / review B1)

```rust
// engine.rs:697-706
"TRAIN" => {
    if parts.len() >= 5 {
        let ms: i32 = parts[1].parse().unwrap_or(0);
        ...
```

`engine.rs` is permissive: `>= 5` tokens, and `parse().unwrap_or(0)` coerces anything
unparsable to zero. The frozen contract (C3) says the panel must not do that, and this
report does **not** present the strict parser as engine conformance. It is a stated
divergence, for a stated reason:

- the referee reads its own trusted replay; the panel reads a candidate bot's stdout;
- the raw bytes of a malformed command are the evidence, and coercion destroys them;
- **a fabricated command fabricates state.** `TRAIN x 1 1 1` under the engine's coercion
  spawns a worker with `ms = 0` on the own shack. The shack is not walkable
  (`sh.parse_rows`, and `state.rs::from_ascii`), and `engine.rs::next_cell` with
  `speed == 0` has `in_range == {current}` at best, so that worker can never move — but
  r2's hand-written non-walkable-source branch stepped it one cell anyway. Both halves of
  that divergence are now gone: the command is rejected, and `next_cell` is the engine's.
  Pinned by `test_malformed_train_cannot_fabricate_a_zero_speed_worker` and
  `test_a_speed_zero_unit_on_the_shack_cannot_step_out`.

Strictness is applied to every verb, not only TRAIN: exact arity, integer unit ids and
talents, and item names drawn from `engine.rs::item_index` (17-27, which **panics** on an
unknown item) and `tree_health` (53-60, which panics on a non-tree PLANT type). Failing
closed where the engine panics is the conservative reading.

---

## 2. TDD — RED, then GREEN

RED commit `08079ed4`, GREEN commit `d686f3f8`. Both are on the branch; the RED commit
contains only tests.

**RED, recorded:** `Ran 122 tests … FAILED (failures=40, errors=39)`. Every blocker had at
least one failing test before any implementation existed. Selected RED lines (the full
list of 79 is reproducible with `git checkout 08079ed4 -- claude_1/pipeline/test_fuzz_panel.py`
and one `python3 -m unittest test_fuzz_panel`):

```
ERROR: test_four_field_train_is_a_malformed_command            (B1)
FAIL : test_rust_authority_agrees_on_every_case (case='move_onto_shack_blocks_train')      (B2/B5)
FAIL : test_rust_authority_agrees_on_every_case (case='second_command_for_a_unit_is_discarded_reversed')  (B3/B5)
FAIL : test_rust_authority_agrees_on_every_case (case='harvest_multi_round_by_harvest_power')             (B5)
FAIL : test_rust_authority_agrees_on_every_case (case='pick_and_drop_work_from_the_shack_cell_itself')    (B5)
FAIL : test_rust_authority_agrees_on_every_case (case='zero_speed_unit_on_the_shack_cannot_move')         (B1/B5)
ERROR: test_every_row_carries_execution_status_events_and_hashes  (B6)
ERROR: test_panel_retains_the_row_and_publishes_gate_unready      (B7)
FAIL : test_missing_corpus_version_is_rejected                    (B8)
ERROR: test_m040_seat_0_packet                                    (B9)
FAIL : test_every_mutation_anchor_still_exists_exactly_once        (B10)
FAIL : test_the_referee_never_delegates_to_the_inherited_dispatcher (B12-F)
```

**GREEN:** `python3 -m unittest test_fuzz_panel test_pre_review` → `Ran 148 tests … OK`
(123 panel + 24 pre-review + 1 mutant-validity guard). No pytest; python3.12 stdlib only.

Eleven r2 tests had to be *corrected*, not merely extended, because they were written
against the non-conformant executor and would otherwise have locked the defect in. Each
carries the `engine.rs` line that makes the old expectation wrong. The two most
instructive:

- `test_malformed_train_is_a_no_op_not_a_crash` explicitly ratified the behaviour C3
  forbids. Renamed and inverted.
- `test_the_worker_count_only_prices_the_bill` trained workers with talents `(0,0,0,0)`
  and then walked them off the shack — only possible because r2's mover ignored speed. It
  now uses `ms = 1` and pays the extra PLUM (`engine.rs:517`).

---

## 3. The independent differential oracle (blocker 5 / review B5) — the deepest item

The circularity this programme keeps finding is: *the expectation is derived from the
implementation, so the test agrees with the bug.* r1 promoted a bot's `can_train` guard
into game law and every hand-written test agreed with it. An oracle assembled from
`fuzz_panel` helpers, or a "reference implementation" transcribed by the same author in
the same sitting, reproduces that exactly.

**Leg A is not a mirror of the authority. It is the authority.** The self-tests pull
`rust/src/game/engine.rs` and `rust/src/game/state.rs` **byte-for-byte** into a throwaway
crate:

```rust
#[path = "/…/rust/src/game/state.rs"]  mod state;
#[path = "/…/rust/src/game/engine.rs"] mod engine;
```

No copy, no transcription, no edit — `#[path]` compiles the pinned files themselves
(`engine.rs`'s `use super::state::…` resolves because `engine` is a crate-root module).
The adapter reads a state + command line on stdin, calls `engine::step`, and prints the
full post-turn state. Nothing from `fuzz_panel` is on that side of the comparison, so
agreement cannot be an artefact of shared code or a shared misreading.

**Leg B** is `sim/engine.py`, a pre-existing, independently authored Python mirror of the
same authority, imported read-only and unmodified.

**Hand-written expected values** remain required (contract §1: "two mirrors cannot agree
on the same accidental error") and live in `TestTrainApplication`, `TestPhaseOrder`,
`TestParserUnitDedup` and the m040 packet.

Compared per case (contract §6): both inventories, every unit's id/player/cell/four
stats/carry, global `next_id`, every plant with its growth state, both scores, turn index.

**31 cases**, each run through referee + leg A + leg B: TRAIN success on iron and no-iron
maps, unaffordable, shack occupied by own and by opponent, MOVE off/onto the shack in both
textual orders, PICK before TRAIN, DROP before and after TRAIN, two TRAINs, first-fails-
second-succeeds, growing-roster costs, future-id DROP and MINE after a spawn, per-unit
dedup in both orders, duplicate MINE, MINE after DROP, harvest→plant→chop, multi-round
harvest, fresh tree not choppable, two units planting one cell, MOVE contention, speed-0
on a shack and on a walkable cell, PICK/DROP from the shack cell, MSG/WAIT no-ops.
Plus four permutation groups (identical multiset, different textual order).

Anti-vacuity guards, both committed:

- `test_the_oracle_is_not_vacuous` — a deliberately corrupted post-state must be
  **rejected** by leg A, so a green differential cannot be a no-op compare.
- `test_the_sim_leg_defects_are_real_and_named` — leg B is excluded from exactly one case
  and must still *fail* on it, for the documented reason. A silent exclusion list is how
  an oracle stops being an oracle.

---

## 4. Row provenance and row retention (blockers 6 and 7 / review B6, B7)

Every row now carries, per contract §8:

```
execution_status          "ok" | "unsupported_verb" | "malformed_command"
command_errors            [{kind, verb, raw, turn, reason}]   -- RAW BYTES, capped at 50
command_error_counts      complete counts per kind (never capped)
train_events              every TRAIN entry: turn, talents, cost, roster_before,
                          spawned, reason, inventory_before/after, unit_id, cell, carry
spawns                    the subset that spawned
successful_train_turns    turn list
parent_execution_status
provenance                {instrument_version, corpus_version, referee_sha256,
                           engine_sha256, engine_authority, phase_order}
```

and the JSON packet carries `referee_sha256`, `engine_sha256` and `provenance` at top
level. The report echoes both hashes and the phase order.

**Row retention.** An unsupported verb used to raise `UnsupportedCommand` out of the
worker, killing the aggregate before any row was written — the incomplete row vanished
from the denominator, which is precisely the "cannot distinguish *all commands executed*
from *the process ended before publishing evidence*" failure. Now:

- the verb is still fail-closed (never executed, never silently skipped);
- the error is retained on the row and the game runs to the horizon, so the row stays in
  the denominator;
- `aggregate_verdict` returns `GATE_UNREADY` — it **dominates** `BLOCK` and `CLEAR`,
  because the other rows were measured by the same instrument;
- the report and the JSON packet are **published**, with a dedicated
  "Instrument-invalid rows" table naming map, seat, status and the first raw command;
- the process still exits 2, so no caller can mistake it for a verdict.

Verified end to end by `test_panel_retains_the_row_and_publishes_gate_unready`, which runs
a planted `TELEPORT`-emitting bot through `fp.main` and asserts exit 2, verdict
`GATE_UNREADY`, **both** seats present in `games`, and raw bytes on each.

---

## 5. Version declaration fails closed (blocker 8 / review B7)

`instrument_version` and `corpus_version` are removed from `DEFAULTS`. `load_config`
requires both keys in the **raw** JSON before the defaults merge:

```python
if key not in raw:
    raise PanelError("config does not declare %s. …" % key)
```

`test_the_versions_are_not_in_defaults` pins the removal (the merge is what made the
equality check unreachable), and every self-test config now declares both — the review
correctly noted that the self-tests were themselves the demonstration that the fail-open
path was live.

---

## 6. Floor: before → after (`c3` → `c4`)

Config bumped to `instrument fuzz-panel/4-engine-conformant-referee`,
`corpus c4-engine-conformant-referee-2026-08-10`. Recipe:

```
cd claude_1/pipeline
python3 fuzz_panel.py --config fuzz-panel-config.json --report <md> --json <json>
```

Nothing was tuned toward a number. The `c3` baseline below is a **fresh rerun of the
committed r2 blob**, not a quotation.

| detector / property | c3 (r2 blob, rerun) | c4 (r3) | delta |
|---|---|---|---|
| D-1 | 30 | 32 | +2 |
| D-4 | 9 | 9 | 0 |
| D-6 | 10 | 11 | +1 |
| D-7 | 2 | 1 | −1 |
| D-9 | 74 | 74 | 0 |
| P2 | 1 | 1 | 0 |
| P4 | 31 | 32 | +1 |
| **blocking games** | **120** | **123** | **+3** |
| clean games | 120 | 117 | −3 |
| instrument-invalid games | n/a | 0 | — |
| games with a successful TRAIN | 2 | 2 | 0 |

Both runs verified deterministic (identical JSON on a repeat run).

### 6.1 A discrepancy that must be reported: r2's floor is not reproducible

The r2 report states `119 blocking` for corpus `c3`. Rerunning the **committed r2 blob**
today, twice, byte-identical both times, gives **120 blocking**. The r2 number cannot be
reconciled from the committed packet, because the r2 evidence was scratch-only — which is
exactly what review blocker B9/B10 said would happen. The honest before→after is
therefore `120 → 123`, and the "r1 118 → r2 119 → r3 119" chain quoted in the r3 task
prompt cannot be verified for its last link. `PROMPT-DIVERGENCE (1)`.

### 6.2 Why the floor moved by 3, and why 3 is a small number

34 of 240 rows changed in at least one measured field (27 in the candidate's terminal
state, 13 in detector counts, 23 in violations, 7 in the block flag: 5 clean→block
`m017 s0/s1`, `m071 s0/s1`, `m082 s0`; 2 block→clean `m024 s0`, `m074 s1`). The floor
moved by only +3 because the flips nearly cancel — the underlying corpus churn is 14%,
not 1%.

**This is the r2 headline lesson answered.** r2 reported `119 → 119` with **zero** rows
changed, and correctly said that proved nothing. r3 changes 34 rows, so the floor number
is now backed by an actually-perturbed corpus.

---

## 7. Witness census — which repaired rules the corpus actually exercises

Measured over the 240 `c4` candidate games (command-stream scan plus an instrumented
replay of all 240 games). This is the section r2's review asked for; it is not
reassuring everywhere, and it is reported as measured.

| repaired rule | witness in the 240-game corpus? | evidence |
|---|---|---|
| C4 full phase order | **YES** | 246 command lines in **67 of 240 games** write a DROP/MINE before a MOVE/HARVEST/PLANT/CHOP/PICK/TRAIN — under r2 those resolved in textual order |
| PLANT semantics (size-0 + same-turn tick) | **YES** | 573 PLANT applications in **203 of 240 games**; the r2 executor left the new tree one cooldown tick ahead |
| MOVE / `next_cell` rewrite | **YES, indirectly** | 27 rows have a changed terminal candidate state; no row exhibits an explicit contention refusal (own rosters are 1–2 units on open maps) |
| TRAIN (r2's repair, regression-guarded) | **YES, thin** | 2 of 240 games (`m040` s0 t=35, s1 t=19), one spawn each — unchanged from r2 |
| C5 first non-TRAIN command per unit | **NO** | 0 command lines repeat a unit id among non-TRAIN commands |
| C2 unsupported verb | **NO** | 0 occurrences |
| C3 malformed command | **NO** | 0 occurrences |
| O2 multiple TRAIN on one line | **NO** | 0 occurrences |
| `near_shack <= 1` (shack cell itself) | **NO** | 0 successful PICK/DROP from a shack cell |
| multi-round HARVEST (`hp >= 2`) | **NO** | 0 — the generated rosters have `harvest <= 1` |
| CHOP snapshot (fresh tree not felled) | **NO** | 0 — blocked by C5, one command per unit per turn |
| speed-0 unit issuing MOVE | **NO** | 0 |

So: **six of the eleven repaired rules have no corpus witness.** For those, the unit
tests, the differential oracle and the mutation drive are the *only* evidence, and the
240-game floor says nothing about them. That is a coverage finding about the corpus (two
bots, one roster generator), not a defect in the repair — but it means the floor must not
be cited as evidence for C2/C3/C5/O2 or the harvest/near-shack corrections.

---

## 8. Mutation drive (mandatory) — 10/10 caught

Definitions are **committed** in `test_fuzz_panel.MUTATIONS` (id, blocker, pinning test,
exact `old` → `new` byte edit), with two guards that keep them honest:
`test_every_mutation_anchor_still_exists_exactly_once` (an anchor that rots is a test
failure) and `test_every_mutant_is_valid_python` (a mutant that does not compile proves
nothing — the first draft of M1 had the wrong indentation and a naive driver scored it as
a SURVIVOR; that is why the guard exists).

Driver: apply the edit to `fuzz_panel.py`, run the whole suite, restore.

| id | blocker | result | failing tests | first caught by |
|---|---|---|---|---|
| M1 `if len(tok) != 5` → `if False` | 1 (C3 strict TRAIN) | **CAUGHT** | 4 | `test_four_field_train_is_a_malformed_command` |
| M2 drop PICK from the phase list | 2 (C4) | **CAUGHT** | 5 | `test_execute_calls_the_phases_in_that_order`, `test_pick_is_visible_to_the_same_turn_train` |
| M3 remove the `used` dedup | 3 (C5) | **CAUGHT** | 6 | `test_second_non_train_command_for_a_unit_is_discarded`, `test_rust_authority_agrees_on_every_case` |
| M4 swap DROP and MINE | 4 (O1 matrix) | **CAUGHT** | 2 | `test_execute_calls_the_phases_in_that_order` |
| M5 `next_cell` floors speed at 1 | 5 + the zero-speed shack divergence | **CAUGHT** | 5 | `test_a_speed_zero_unit_on_the_shack_cannot_step_out`, `test_rust_authority_agrees_on_every_case` |
| M6 blank the row provenance | 6 | **CAUGHT** | 2 | `test_every_row_carries_execution_status_events_and_hashes` |
| M7 raise instead of retaining the error | 7 | **CAUGHT** | 6 | `test_panel_retains_the_row_and_publishes_gate_unready` |
| M8 skip the raw-key presence check | 8 | **CAUGHT** | 3 | `test_missing_corpus_version_is_rejected` |
| M9 stop recording TRAIN events | 9 | **CAUGHT** | 5 | `test_m040_seat_0_packet`, `test_a_rejected_train_is_also_recorded` |
| M10 reinstate the bot's `n >= 2` cap | 12 / r1 regression | **CAUGHT** | 6 | `test_a_third_worker_trains_because_the_engine_has_no_worker_cap`, `test_a_real_bot_trains_past_two_workers_closed_loop` |

**10 of 10 caught, 0 survived.** No blocker is closed by code that no test pins.

---

## 9. The two `m040` rows — the six-part packet (blocker 9 / contract §7)

Both identities and both seats stay in the corpus (`test_m040_identity_is_pinned`), and
`TestM040SixPartPacket` now pins all six clauses byte-for-byte against a real
closed-loop 200-turn run of the compiled floor bot:

| clause | seat 0 | seat 1 |
|---|---|---|
| 1. first affordable TRAIN executed exactly once | turn **35**, 1 spawn | turn **19**, 1 spawn |
| 2. spawn id / stats / cell / carry | id 6, `(1,1,0,1)`, cell `(1,2)`, carry `[0]*6` | id 6, `(1,1,0,1)`, cell `(9,1)`, carry `[0]*6` |
| 2b. exact bill and inventory after | cost `[2,2,1,0,2,0]`, inv `[0,0,0,2,0,0]` | cost `[2,2,1,0,2,0]`, inv `[0,0,0,2,0,0]` |
| 2c. visible in the next serialized state | `6 0 1 2 1 1 0 1 0 0 0 0 0 0` | `6 0 9 1 1 1 0 1 0 0 0 0 0 0` |
| 3. repeated-TRAIN no-op loop gone | emissions `[35]` (was 166 of 200) | emissions `[19]` (was 182 of 200) |
| 4. no unsupported or malformed command | `command_errors == []`, status `ok` | idem |
| 5. old rows machine-readable as `instrument_invalid` | `fuzz-panel-config.json → instrument_invalid_rows` | idem |
| 6. referee hash + corpus version + floor-bot source SHA | `referee_sha256`, `c4…`, `a8eb3b2b…` (pinned) | idem |

Clause 5 is now data, not prose: `fuzz-panel-config.json` carries an
`instrument_invalid_rows` ledger retiring the two `c1` m040 rows **and** the whole `c2`
and `c3` corpora from calibration, each with `eligible_for_calibration: false` and a
reason. `test_old_rows_are_retained_as_machine_readable_invalid_evidence` pins it.

---

## 10. `UNRESOLVED` against `engine.rs`, and contract clauses that could not be met as written

Declared, not hidden. None of these is presented as conformance.

**UNRESOLVED-r3-A — the opponent is not engine-driven.** `engine.rs::step` takes two
command streams; the panel drives player 1 with a scripted policy (`OPP_POLICIES`) and
applies only the candidate's line to player 0. `engine.rs` has no notion of a scripted
opponent, so there is no rule to mirror. *Choice:* keep the scripted opponent — the
panel's job is to sample varied worlds against one candidate, and the contract's
differential clauses are about own-side command execution. *Consequence:* opponent-side
harvest/chop/banking remain the panel's own model and are **not** engine-conformant.
Pre-existing; not repaired by r3; visible in `_opp_seek_and_act` / `_act_harvest` /
`_act_chop`.

**UNRESOLVED-r3-B — `next_id` seeding.** The transcript does not serialize
`game.next_id`. Seeded at `1 + max(all existing unit ids)`. `engine.rs` is silent on
recovering the counter from a serialized state; it only guarantees monotonicity
(555/567) and contains no unit-removal path at all. Same choice as r2, which the review
accepted (A3). Non-contiguous seeded rosters would still start the counter above the
engine's true value.

**UNRESOLVED-r3-C — end-of-game.** The panel runs a fixed 200 turns and never applies
`engine.rs::has_stalled` (819-868). Pre-existing and untouched by r3, but it is now the
largest remaining gap between the panel and `step`-level conformance, so it is listed
rather than left implicit.

**UNRESOLVED-r3-D — MSG arity.** `engine.rs:696` treats `MSG` and `WAIT` identically
(`continue`), so the engine is silent on whether `MSG hello world` is well-formed.
*Choice:* `MSG` accepts any body (it is the protocol's free-text channel and rejecting it
would fail closed on legitimate output); `WAIT` must be bare. Stated so a reviewer can
overrule it.

**UNRESOLVED-r3-E — the strict boundary has no witness.** 0 of 240 games emit an
unsupported or malformed command (§7). C2 and C3 are pinned only by unit tests and
mutations M1/M7. If a future candidate does emit one, the panel will publish
`GATE_UNREADY` and retain the row — but that path has never run on real bot output.

**CONTRACT-DIVERGENCE-O1 — "PICK can fund TRAIN" is mechanically impossible.** The frozen
contract §5/O1 and review B4 both require a case where "a successful same-turn PICK
supplies the last required charged item and TRAIN succeeds". `engine.rs::apply_pick`
(451-456) moves an item **out of** the inventory into a unit's carry:

```rust
if game.inventories[player][idx] > 0 {
    game.inventories[player][idx] -= 1;
    ...u.carry[idx] += 1;
```

and `apply_train` reads `game.inventories[p]` (529-541). A PICK can therefore only ever
*starve* a bill, never supply one. Rather than invent a rule to satisfy the clause, r3
implements and pins the clause's real content — **phase visibility**: PICK's inventory
write is visible to TRAIN, DROP's is not. Both directions are pinned
(`test_pick_is_visible_to_the_same_turn_train`,
`test_drop_never_funds_a_same_turn_train`) and both appear in the differential matrix
(`pick_before_train_starves_the_bill` + its no-PICK control,
`drop_written_first/last_cannot_fund_train`). **The contract clause as literally worded
cannot be satisfied by any engine-conformant referee and should be amended.**
`PROMPT-DIVERGENCE (2)` — the r3 prompt repeats it as "PICK/DROP funding".

**CONTRACT-DIVERGENCE-C4/C5 — permutation invariance is bounded.** C4 requires that two
lines with the same command multiset in different textual order produce the same
post-state. That holds only when no unit appears twice among the non-TRAIN commands,
because C5 (`engine.rs:717-720`) makes textual order decide *which* of a unit's commands
survives. The two clauses are in tension as written; the engine resolves it in favour of
C5. The permutation groups therefore use distinct units, and the constraint is documented
at the definition site.

**FINDING — `sim/engine.py` diverges from the authority.** Found by this differential.
`sim/engine.py:115`

```python
best = min(target_dist[c] for c in in_range)
```

has no counterpart to `engine.rs:132-134`

```rust
if in_range.is_empty() { return current; }
```

so a speed-0 unit standing on a non-walkable cell — a shack, i.e. exactly where TRAIN
puts a fresh worker — raises `ValueError: min() iterable argument is empty` instead of
standing still. Leg A (the authority) is correct. `sim/**` is outside this task's
boundary, so this is **reported, not fixed**; leg B is excluded from that one case by a
named list whose reality is itself tested. Recommended owner: whoever owns `sim/`.

**Not mine, still open:** review blocker **B10** — the execution review by
`local_claude_1` required by contract §9 step 5. Nothing in r3 can close it.

---

## 11. Minor drift the review asked for

- `unsupported_command()` now points maintainers at `rust/src/game/engine.rs`, not
  `rust/src/bin/yamo_orchard_live.rs`.
- the MINE yield is no longer described as "INFERRED from a secondary file": `_apply_mine`
  cites `engine.rs:646-667` directly, and the bot-side emission gate is not mentioned.
- `_int_or_zero` (the `parse().unwrap_or(0)` helper) is deleted — C3 forbids it and dead
  permissive helpers are how coercion comes back.
- `UnsupportedCommand` is retained but no longer raised by the referee; its docstring says
  so and why.

---

## 12. Clause disposition (r3 self-assessment, for the adversarial reviewer to overrule)

| contract area | r2 | r3 |
|---|---|---|
| C1 known-verb table | accepted | accepted |
| C2 unknown-verb fail-closed + row retention | failed (B6) | closed; **no corpus witness** |
| C3 malformed TRAIN | failed | closed; **no corpus witness** |
| C4 full phase order | failed | closed, witnessed (67 games) |
| C5 first non-TRAIN per unit | failed | closed; **no corpus witness** |
| C6 parser details / multiple TRAIN | partial | closed; multiple-TRAIN unwitnessed |
| T1–T4 TRAIN economics, no cap | accepted | preserved, mutation-guarded (M10) |
| N1/N2 legal no-op cases | accepted | preserved + differential |
| N3 movement changes legality | partial | closed (both directions, both orders) |
| O1 PICK/DROP timing | failed | closed **as phase visibility** — see `CONTRACT-DIVERGENCE-O1` |
| O2 repeated TRAIN | partial | closed; **no corpus witness** |
| O3 future-id phase visibility | failed | closed (DROP + MINE after spawn) |
| O4 next-state visibility | partial | closed (m040 serialized rows pinned) |
| differential full-state equality | failed | closed — the authority's own bytes |
| `m040` six-part packet | failed | closed |
| per-row result/provenance schema | failed | closed |
| committed reproducibility packet | failed | closed (config + MUTATIONS + this report) |
| execution review before acceptance | not delivered | **still not delivered** (B10) |

## 13. Reproduction

```
git checkout agent/claude_1-banana-restoration-r2
cd claude_1/pipeline
PATH=$HOME/.cargo/bin:$PATH python3 -m unittest test_fuzz_panel test_pre_review   # 148 OK, ~13 s
PATH=$HOME/.cargo/bin:$PATH python3 fuzz_panel.py \
    --config fuzz-panel-config.json --report /tmp/r3.md --json /tmp/r3.json       # ~11 s
# mutation drive: for each entry of test_fuzz_panel.MUTATIONS, apply old->new to
# fuzz_panel.py, assert it compiles, run the suite, restore.
```

The differential oracle needs `rustc` (`$HOME/.cargo/bin`). It deliberately **raises**
rather than skipping when `rustc` is absent: a silently-absent oracle is the failure mode
this programme keeps rediscovering.

---

## 14. Handoff artifact list (review B9: the config must not be omitted again)

```json
"artifact_paths": [
  "claude_1/pipeline/fuzz_panel.py",
  "claude_1/pipeline/test_fuzz_panel.py",
  "claude_1/pipeline/fuzz-panel-config.json",
  "claude_1/pipeline/referee-train-repair-r3-2026-08-10.md"
]
```

All four are load-bearing and all four are committed on
`agent/claude_1-banana-restoration-r2` (RED `08079ed4`, GREEN `d686f3f8`, this report).
The config is on the list because the corpus/instrument bump `c3 -> c4` and the
`instrument_invalid_rows` ledger both live in it. The floor evidence (§6), the witness
census (§7) and the mutation definitions + results (§8) are in this committed report and
in `test_fuzz_panel.MUTATIONS`; nothing load-bearing remains scratch-only.
