# Referee TRAIN repair — REVISION r2: `engine.rs` is the sole authority

- Author: `claude_1` (implementer; own file, executed)
- Date: 2026-08-09
- Branch: `agent/claude_1-banana-restoration-r2`
- Commits: `f854b4b5` (RED) → `eaa8da58` (GREEN) → this report
- Supersedes: `claude_1/pipeline/referee-train-repair-2026-08-09.md` (r1), whose
  verdict was `REVISION_REQUIRED — NOT ACCEPTED`; panel `GATE_UNREADY`
- **Instrument version: `fuzz-panel/3-train-engine-authority`  |  Corpus version:
  `c3-train-engine-authority-2026-08-09`** (bumped from `fuzz-panel/2-train` / `c2`;
  declared in `fuzz-panel-config.json`, enforced by `load_config`, echoed in every
  report header and JSON payload)

Every number below is marked **MEASURED** (I ran it, command given) or **INFERRED**
(reasoning from source I read). Input digests are in §0.

---

## 0. Inputs — SHA-256

| file | sha256 |
|---|---|
| **`rust/src/game/engine.rs` (THE AUTHORITY, read-only, untouched)** | `7c240abfcfdf678993960fe73440735a19f934596c9651bdf915e2902f78fb05` |
| `rust/src/bin/yamo_orchard_live.rs` (byte-sacred, read-only, untouched) | `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f` |
| `claude_1/pipeline/fuzz_panel.py` (post-revision) | `eff0a98ff5b9f636cf6c73de131e64d629cf63e7cdd6b8dca5afb51ba0d2c11b` |
| `claude_1/pipeline/test_fuzz_panel.py` (post-revision) | `afe61f5d0d999496ad03393a51733d2b3fd5786938109db5bf8f06cb852cb904` |
| `claude_1/pipeline/fuzz-panel-config.json` (post-revision) | `dc0ea0596aeb66cbaf602208e451a949f4d9a49f4f9703d4e6b8fc87a632c343` |
| `cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs` | `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55` |
| `claude_1/banana-restoration-r2/make_banana_traces.py` (referee core, **not edited**) | `daf9996b2fa40d4a0f5b16dfc7bfd3c9d75c372d4c5761dac4327ce42e3f33d5` |
| `claude_1/banana-restoration-r2/trace_detectors.py` (**not edited**) | `59dce10dc87797bc6b1b8da0f628f4ddd82b561d93946fa91453d2ea40805209` |
| floor config BEFORE (`cfg-before.json`) | `acb10cc7d06c9866185d9f1fece3eb321d8658e6dba4f41d1f1d16d16371f29c` |
| floor config AFTER (`cfg-after.json`) | `ac6ef719633407bd26cb87c26528541c4da26e697bcfbab923a7af5846e84102` |

`engine.rs` digest `7c240abf…` and `yamo_orchard_live.rs` digest `fff6669b…` are
**unchanged from the r1 tree**. Both were read only. `trace_detectors.py`,
`make_banana_traces.py` and every bot/candidate/parent/`.min.rs` are untouched.

---

## 1. The blocker

r1 derived TRAIN legality from the **resident bot's** `can_train`:

```rust
// rust/src/bin/yamo_orchard_live.rs:834-836   (MoisanBot::can_train)
fn can_train(view: &GameState, stats: Stats) -> bool {
    let n = view.units.iter().filter(|u| u.player == 0).count() as i32;
    if n >= 2 || TOTAL_TURNS - view.turn <= 20 { return false; }
```

That is one bot's self-restraint, not the rules of the game. The authority is
`rust/src/game/engine.rs::apply_train` (lines 525-568), and it enforces **neither**
condition. The full body, with every rejection marked:

```rust
// rust/src/game/engine.rs:525
pub fn apply_train(game: &mut GameState, player: i32, talents: (i32, i32, i32, i32)) {
 526    let p = player as usize;
 527    let n = game.units.iter().filter(|u| u.player == player).count() as i32;
 528    let cost = training_cost(n, talents);
 529    let inv = &game.inventories[p];
 531    // IRON (slot 4) only charged if iron terrain present (Bronze league guard)
 532    let pay: &[usize] = if !game.iron.is_empty() {
 533        &[0, 1, 2, 3, 4, 5]
 534    } else {
 535        &[0, 1, 2, 3, 5]
 536    };
 538    // Check affordability
 539    if pay.iter().any(|&i| inv[i] < cost[i]) {
 540        return;                          // <-- REJECTION 1 (the only ones)
 541    }
 543    // Check shack is unoccupied
 544    let shack = game.shacks[p];
 545    if game.units.iter().any(|u| u.pos() == shack) {
 546        return;                          // <-- REJECTION 2
 547    }
 549    // Deduct cost
 550    for &i in pay {
 551        game.inventories[p][i] -= cost[i];
 552    }
 554    let (ms, cc, hp, chop) = talents;
 555    let nid = game.next_id;
 556    game.units.push(Unit {
 557        id: nid, player,
 559        x: shack.0, y: shack.1,
 561        ms, cc, hp, chop,
 565        carry: [0; 6],
 566    });
 567    game.next_id += 1;
 568 }
```

`n` is read at **527** and consumed at **528** to price the bill. It is never compared
to anything. `game.turn` does not appear in 525-568 at all — the only writer in the
whole engine is `step` itself (`engine.rs:805  game.turn += 1;`).

So the r1 referee **forbade what the engine permits**: it would silently reject a
candidate that trains a third worker while the real game accepts it. Same class of
defect as the silently-discarded verb this work was repairing, pointing the other way.

---

## 2. Requirement 1+2+3 — the mirror, rule by rule, with citations

Every rule the referee now implements, and the `engine.rs` line it mirrors. Where
`engine.rs` is silent, the row says `UNRESOLVED` and §6 records what I chose and why.

| # | rule as implemented | `engine.rs` line(s) | quoted authority |
|---|---|---|---|
| 1 | own-unit count `n` is read to price the bill and for nothing else | 527-528 | `let n = game.units.iter().filter(\|u\| u.player == player).count() as i32;` / `let cost = training_cost(n, talents);` |
| 2 | `cost[PLUM] = n + ms*ms` | 517 | `cost[PLUM] = n + ms * ms;` |
| 3 | `cost[LEMON] = n + cc*cc` | 518 | `cost[LEMON] = n + cc * cc;` |
| 4 | `cost[APPLE] = n + hp*hp` | 519 | `cost[APPLE] = n + hp * hp;` |
| 5 | `cost[IRON] = n + chop*chop` | 520 | `cost[IRON] = n + chop * chop;` |
| 6 | BANANA and WOOD cost 0 (never written) | 516, 521 | `let mut cost = [0i32; 6];` … `cost` |
| 7 | pay slice with iron terrain = `[0,1,2,3,4,5]` | 532-533 | `if !game.iron.is_empty() { &[0, 1, 2, 3, 4, 5] }` |
| 8 | pay slice without iron terrain = `[0,1,2,3,5]` (IRON neither checked nor deducted) | 534-536 | `} else { &[0, 1, 2, 3, 5] }` |
| 9 | reject iff **any** pay slot is short (`<`, so exactly-affordable is affordable) | 539-541 | `if pay.iter().any(\|&i\| inv[i] < cost[i]) { return; }` |
| 10 | reject iff **any unit of either player** stands on the training player's shack | 544-547 | `let shack = game.shacks[p];` / `if game.units.iter().any(\|u\| u.pos() == shack) { return; }` |
| 11 | a rejected TRAIN charges nothing (both returns precede the deduction) | 540, 546 vs 550 | `return;` … `for &i in pay { game.inventories[p][i] -= cost[i]; }` |
| 12 | deduct over the pay slice | 550-552 | `for &i in pay { game.inventories[p][i] -= cost[i]; }` |
| 13 | spawn cell = the training player's own shack | 559 | `x: shack.0, y: shack.1,` |
| 14 | spawn stats = the TRAIN talents, in order ms, cc, hp, chop | 554, 561 | `let (ms, cc, hp, chop) = talents;` / `ms, cc, hp, chop,` |
| 15 | spawn carry = all zeros | 565 | `carry: [0; 6],` |
| 16 | spawn id from a **monotone** counter, incremented after use | 555, 567 | `let nid = game.next_id;` / `game.next_id += 1;` |
| 17 | spawn belongs to the training player | 557 | `id: nid, player,` |
| 18 | **no** worker cap | — | *(absent from 525-568)* |
| 19 | **no** turn condition of any kind | — | *(`game.turn` absent from 525-568; written only at 805)* |
| 20 | TRAIN parses only with ≥ 5 whitespace tokens | 698 | `if parts.len() >= 5 {` |
| 21 | unparsable talents become 0 | 699-702 | `let ms: i32 = parts[1].parse().unwrap_or(0);` |
| 22 | every TRAIN on a line is applied, in order | 697-706, 786-788 | `p.train.push((ms, cc, hp, chop)); … continue;` / `for talents in &a.train { apply_train(game, 0, *talents); }` |
| 23 | TRAIN resolves after MOVE/HARVEST/PLANT/CHOP/PICK and before DROP/MINE | 753, 762-801 | `/// Priority order: MOVE, HARVEST, PLANT, CHOP, PICK, TRAIN, DROP, MINE,` |
| 24 | MINE: no yield without chop power or free capacity | 652-654 | `if u_chop == 0 \|\| u_free <= 0 { continue; }` |
| 25 | MINE: manhattan-1 adjacency to an iron cell | 656-659 | `.any(\|(ix, iy)\| (ux - ix).abs() + (uy - iy).abs() == 1)` |
| 26 | MINE yield = `min(chop, free)` into the IRON slot | 661-663 | `let amount = u_chop.min(u_free);` / `u.carry[IRON] += amount;` |
| 27 | free capacity = `cc − sum(carry)`, i.e. carried iron counts against capacity | `state.rs:29-34` | `pub fn total(&self) -> i32 { self.carry.iter().sum() }` / `pub fn free(&self) -> i32 { self.cc - self.total() }` |

**Rule 26 was `INFERRED` in r1** because r1 treated `yamo_orchard_live.rs` as the
authority and that file states only MINE's emission precondition. Under the correct
authority it is a **direct citation**, not an inference. Nothing about the MINE
implementation changed; only its provenance did.

### 2.1 What was removed

```diff
-TOTAL_TURNS = 300          # yamo_orchard_live.rs:162  rules::TOTAL_TURNS
-WORKER_CAP = 2             # yamo_orchard_live.rs:836  `n >= 2 -> false`
-TRAIN_GUARD_TURNS = 20     # yamo_orchard_live.rs:836  `TOTAL_TURNS - turn <= 20`
```
```diff
     def can_train(self, talents):
         n = len(self.own_unit_ids())
-        if n >= WORKER_CAP:
-            return False
-        if TOTAL_TURNS - self.turn <= TRAIN_GUARD_TURNS:
-            return False
         cost = training_cost(n, talents)
```

`TOTAL_TURNS` had no other reader in `fuzz_panel.py`, so all three constants are gone.
**The referee no longer contains a single rule sourced from a bot.**

### 2.2 What else changed (both minimal, both traceable)

1. `train_billed_items` is now the engine's literal `pay` slice (rule 7/8) instead of
   `[PLUM, LEMON, APPLE] (+ IRON)`. Observationally identical (BANANA/WOOD cost 0, so
   the check is `inv[i] < 0` and the deduction is `-= 0`), but it is now a quotation
   rather than a simplification, and `test_banana_and_wood_are_on_the_pay_slice_but_
   cost_nothing` pins it.
2. The spawn id comes from an explicit `self.next_id` counter seeded at `max(id) + 1`
   and incremented at spawn (rule 16), replacing r1's recomputed `max(self.units) + 1`.
   See §6 UNRESOLVED-A.

### 2.3 What was deliberately kept, unchanged

Explicit known-verb dispatch (`VERB_HANDLERS`); fail-closed unknown verbs
(`UnsupportedCommand` → `GATE_UNREADY / unsupported_command`, exit 2, no verdict);
the MINE implementation; the bill / iron-guard / spawn-field / occupied-shack
mechanics; **both `m040` identities as mandatory regression rows**
(`TestM040RegressionRows`, unmodified, both green); the corpus bump (bumped again).

---

## 3. TDD — RED then GREEN

### 3.1 RED — commit `f854b4b5`

**MEASURED**, `cd claude_1/pipeline && python3 -m unittest test_fuzz_panel`:
`Ran 77 tests … FAILED (failures=7)`.

| failing test | what it pins |
|---|---|
| `TestTrainAuthorityIsTheEngine.test_no_bot_derived_worker_cap_constant` | no `WORKER_CAP` in the module |
| `TestTrainAuthorityIsTheEngine.test_no_bot_derived_final_turn_guard_constant` | no `TRAIN_GUARD_TURNS` in the module |
| `TestTrainAuthorityIsTheEngine.test_can_train_does_not_consult_the_turn_counter` | `can_train`'s **AST** reads no `.turn` and no `*TURN*` global |
| **`TestTrainApplication.test_a_third_worker_trains_because_the_engine_has_no_worker_cap`** | **the blocker (a)** — `n == 2`, affordable, shack vacated → must spawn, and the bill must be priced at `n == 2` |
| `TestTrainApplication.test_the_worker_count_only_prices_the_bill` | four successive trains; `cost[i] == n` at each step (talents `0 0 0 0`) |
| **`TestTrainApplication.test_no_final_turn_guard_the_engine_imposes_none`** | **the blocker (b)** — turns 279, 280, 290, 299, 300, 400 all train |
| `TestTrainApplication.test_spawn_id_follows_the_engine_next_id_counter` | ids 6 then 7; never reused |

Failure output recorded in the RED commit message. The AST guard is itself guarded:
`test_the_turn_reader_itself_is_not_vacuous` shows `_reads_the_turn_counter` fires on
the bot's rule and not on a body whose only `turn` is inside `return` (a naive
substring test passes vacuously — I hit exactly that and fixed it before committing).

Three further tests were added in the RED commit that were **already green**; they are
conformance pins, not RED, and the commit message says so:
`test_an_opponent_unit_on_the_own_shack_blocks_the_spawn` (rule 10 — `engine.rs:545`
iterates ALL units), `test_two_trains_on_one_line_the_second_hits_the_fresh_spawn`
(rule 22 + rule 10), `test_banana_and_wood_are_on_the_pay_slice_but_cost_nothing`
(rules 6-8).

Requirement (c) — genuinely illegal TRAINs still rejected exactly as `engine.rs`
rejects them — is covered by `test_unaffordable_train_is_rejected_and_charges_nothing`
(rule 9 + 11, including the `>=`-not-`>` boundary),
`test_iron_is_billed_only_when_the_map_has_iron` (rules 5, 7, 8),
`test_occupied_shack_blocks_the_spawn` and
`test_an_opponent_unit_on_the_own_shack_blocks_the_spawn` (rules 10, 11),
`test_malformed_train_is_a_no_op_not_a_crash` (rule 20). All were green before and
after; the mutation check (§5) shows they are load-bearing.

Requirement (d) — both `m040` rows still behave as committed regression rows —
`TestM040RegressionRows` is untouched and green (§7).

### 3.2 GREEN — commit `eaa8da58`

**MEASURED**: `Ran 78 tests … OK` (`test_fuzz_panel`), `Ran 24 tests … OK`
(`test_pre_review`).

The 78th test is the end-to-end anti-vacuity check added with GREEN,
`test_a_real_bot_trains_past_two_workers_closed_loop`: a planted `TRAINER_BOT`
compiled and driven through `rt.run_binary_custom` — the same compile + binary +
referee loop the `m040` rows use. **MEASURED**: 8 turns, **9 own units**, spawn ids
`6, 7, 8, 9, 10, 11, 12, 13`, final inventory `[55, 55, 63, 0, 0, 0]` (non-negative;
the growing bill is the only limit). Under r1 this run produced 2.

Why an end-to-end test was necessary rather than optional: see §4.2 — the floor bot
cannot exercise this at all, so without it the revision's central claim would rest
entirely on unit-level referee calls.

---

## 4. Requirement 5 — the floor, before → after

Recipe as specified: a copy of `fuzz-panel-config.json` with **both** `parent.source`
and `candidate.source` set to the ABSOLUTE
`/home/tarstars/prj/troll_farm-claude_1/cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs`
(`a8eb3b2b…`), distinct `crate`, fresh `games_dir`. The two configs are byte-identical
apart from `task`, `games_dir` and the version pair (digests in §0).

```
# BEFORE  (commit f6a83990, instrument fuzz-panel/2-train, corpus c2)
python3 claude_1/pipeline/fuzz_panel.py --config cfg-before.json \
        --report report-before.md --json before.json
→ fuzz_panel: BLOCK (240 games, 119 blocking, 0 flagged, 16.1 s)

# AFTER   (commit eaa8da58, instrument fuzz-panel/3-train-engine-authority, corpus c3)
python3 claude_1/pipeline/fuzz_panel.py --config cfg-after.json \
        --report report-after.md --json after.json
→ fuzz_panel: BLOCK (240 games, 119 blocking, 0 flagged, 11.1 s)
```

**MEASURED. The floor did not move: 119 → 119 blocking games of 240, verdict BLOCK in
both, and 0 of 240 rows differ in any field** (block, detector counts, violation
count, score). Nothing was tuned toward any number; the only config keys touched are
the version pair. §4.2 explains why, and why that is a finding rather than a comfort.

### 4.1 Per-detector / per-property breakdown

Games with at least one blocking violation of each kind, and total episodes:

| property / detector | games before | games after | Δ | episodes before | episodes after | Δ |
|---|---|---|---|---|---|---|
| D-1 | 33 | 33 | 0 | 36 | 36 | 0 |
| D-2 | 0 | 0 | 0 | 0 | 0 | 0 |
| D-3 | 0 | 0 | 0 | 0 | 0 | 0 |
| D-4 | 6 | 6 | 0 | 6 | 6 | 0 |
| D-5 | 1 | 1 | 0 | 1 | 1 | 0 |
| D-6 | 9 | 9 | 0 | 15 | 15 | 0 |
| D-7 | 0 | 0 | 0 | 0 | 0 | 0 |
| D-8 | 0 | 0 | 0 | 0 | 0 | 0 |
| D-9 | 74 | 74 | 0 | 196 | 196 | 0 |
| P0 (protocol liveness) | 0 | 0 | 0 | 0 | 0 | 0 |
| P2 (R-5 alternation) | 5 | 5 | 0 | 5 | 5 | 0 |
| P3 (orchard inertness) | 0 | 0 | 0 | 0 | 0 | 0 |
| P4 (liveness) | 29 | 29 | 0 | 30 | 30 | 0 |
| **blocking games (union)** | **119** | **119** | **0** | | | |
| report-tier flags | 0 | 0 | 0 | | | |

**Biggest movers: there are none.** Every cell is unchanged. By class and by opponent
profile the picture is the same:

| class | games | blocking before | blocking after |
|---|---|---|---|
| choke_corridor | 60 | 32 | 32 |
| forest_dense | 20 | 4 | 4 |
| forest_sparse | 16 | 9 | 9 |
| multi_door | 24 | 11 | 11 |
| open_field | 36 | 18 | 18 |
| orchard_eligible | 24 | 11 | 11 |
| single_door_tent | 24 | 16 | 16 |
| water_diagonal | 36 | 18 | 18 |

| opponent | games | blocking before | blocking after |
|---|---|---|---|
| chopper_aggressor | 72 | 29 | 29 |
| harvester | 96 | 47 | 47 |
| idle | 72 | 43 | 43 |

(For continuity across the two revisions: the c1 → c2 step was 118 → 119, the c2 → c3
step is 119 → 119. Cross-corpus comparison is not otherwise meaningful and
`load_config` refuses a config declaring the wrong version.)

### 4.2 Why the floor did not move — and why that is a finding, not a reassurance

I did not expect this and I am not presenting it as a good outcome. The direct cause,
**MEASURED** over the 240 `candidate_commands` transcripts in
`games-after/games.jsonl.gz`:

```
games with >= 1 TRAIN emission : 2 / 240
total TRAIN command lines      : 2
histogram of TRAIN lines/game  : {0: 238, 1: 2}
                                 m040 seat 0 -> turn 35
                                 m040 seat 1 -> turn 19
```

The floor bot **never asks for a third worker**, on any of the 240 games, because it
carries the very `n >= 2` self-restraint at `yamo_orchard_live.rs:836` that r1 mistook
for a rule. The 20-turn guard is likewise unreachable: `TOTAL_TURNS = 300` and the
panel horizon is 200. So the two conditions r2 removed are **never evaluated** on this
corpus, and an unchanged floor is the arithmetically necessary result — not evidence
that the change is safe or small.

The consequence for the gate is the important part: **the 240-game floor cannot detect
this class of defect.** It measures one bot, and that bot's policy happens to coincide
with the rule the referee wrongly encoded. A candidate whose strategy is a third
worker would have been mis-measured by r1 and the floor would have said nothing. That
is exactly why §3.2's closed-loop `TRAINER_BOT` test exists and why §5's M1 mutant is
the one that matters: the pin has to live in the self-tests, because the corpus does
not contain a witness. Widening the corpus with a bot that trains past two workers is
the obvious follow-up and is recorded in §6 as UNRESOLVED-E.

---

## 5. Mutation check (mandatory)

Method: `git`-clean copy of the tree at `eaa8da58` into a scratch directory; each
mutant is a single textual edit to the scratch `fuzz_panel.py`; a mutant is **CAUGHT**
iff `python3 -m unittest test_fuzz_panel` exits non-zero. The unmutated scratch copy
is verified green first. Driver: `mutate.py` (scratch artifact).

**MEASURED — 9 of 10 caught.**

| # | mutant | result | failing tests |
|---|---|---|---|
| **M1** | **reinstate the bot-derived worker cap (`if n >= 2: return False`)** | **CAUGHT** | **4** — `test_a_third_worker_trains_because_the_engine_has_no_worker_cap`, `test_the_worker_count_only_prices_the_bill`, `test_spawn_id_follows_the_engine_next_id_counter`, **`test_a_real_bot_trains_past_two_workers_closed_loop`** |
| **M2** | **reinstate the bot-derived final-20-turn guard (`if 300 - self.turn <= 20`)** | **CAUGHT** | **2** — `test_no_final_turn_guard_the_engine_imposes_none`, `test_can_train_does_not_consult_the_turn_counter` |
| M3 | wrong bill — drop the `n` term (`cost = talent²`) | CAUGHT | 7 |
| M3b | wrong bill — IRON billed with no iron terrain (drop `engine.rs:532-536`) | CAUGHT | 9 |
| M4 | wrong spawn cell — spawn on the opponent shack | CAUGHT | 5 |
| M4b | occupied-shack guard narrowed to own units (contra `engine.rs:545`) | CAUGHT | 1 — `test_an_opponent_unit_on_the_own_shack_blocks_the_spawn` |
| M4c | occupied-shack guard dropped entirely | CAUGHT | 3 |
| M5 | restored silent dispatcher default (`if handler is None: continue`) | CAUGHT | 3 — `test_unknown_verb_raises_gate_unready`, `test_unknown_verb_anywhere_in_a_multi_command_line`, `test_panel_exits_gate_unready_on_an_unsupported_verb` |
| M6 | spawn id `max(id)+1` instead of the `next_id` counter | **SURVIVED** | 0 |
| M7 | TRAIN back to a no-op (`"TRAIN": _cmd_noop`) | CAUGHT | 16 |

### 5.1 Specifically: is the reinstated bot cap caught?

**Yes — M1 is caught by four tests, including the end-to-end closed-loop one.** The
thing this revision is about is pinned at three levels: the unit level
(`test_a_third_worker_trains_…` — `n == 2`, affordable, shack free, must spawn), the
economic level (`test_the_worker_count_only_prices_the_bill` — four successive spawns
with `cost[i] == n` at each), and the binary-in-the-loop level
(`test_a_real_bot_trains_past_two_workers_closed_loop` — 9 own units in 8 turns
through a compiled bot). M2, the reinstated turn guard, is caught both behaviourally
(`test_no_final_turn_guard_…`) and structurally (the AST guard on `can_train`).

### 5.2 The survivor, M6

M6 is an **equivalent mutant**, and I am claiming that rather than excusing it.
`max(id) + 1` and a monotone `next_id` can only diverge if a unit id is retired and
re-issued. **MEASURED**: `grep -n "units.pop\|del .*units\|units.clear"` over
`make_banana_traces.py` and `fuzz_panel.py` returns nothing, and `engine.rs` contains
no `units.remove` / `units.retain` / `units.swap_remove` at all — the engine has no
unit-death path. With no removals, `max(id) + 1 == next_id` at every spawn, for every
reachable state, so no test *can* distinguish them without constructing an unreachable
world. The change to an explicit counter is a **conformance/robustness** change (it
quotes `engine.rs:555/567` directly instead of re-deriving the same value), not a
behaviour change, and I have not written a test that pretends otherwise.

---

## 6. UNRESOLVED

Where `engine.rs` is silent I had to decide. Each choice is recorded here rather than
presented as conformance.

- **RESOLVED by this revision** — r1's UNRESOLVED-1 (worker cap / turn guard: needs an
  owner ruling) is answered: `engine.rs::apply_train` is the authority, it imposes
  neither, the referee no longer does. r1's UNRESOLVED-2 (MINE's yield is INFERRED) is
  answered: under the correct authority `engine.rs:661-663` states it outright.

- **UNRESOLVED-A — seeding `next_id`.** `engine.rs` reads and increments
  `game.next_id` (555, 567) but never initialises it; initialisation lives in mapgen
  (`state.rs:164`, `official_mapgen.rs:466`, `a2_continued_mapgen.rs:459`, all
  `next_id: 2`, matching the two starter units 0 and 1). The referee reconstructs
  state from a serialized turn view, which carries no `next_id`. **I chose**
  `max(existing id) + 1`, seeded once at construction. **Why:** it reproduces the
  documented initial value exactly for the standard two-unit roster (`max(0,1)+1 = 2`),
  it is the value the bot itself predicts from the same wire data
  (`yamo_orchard_live.rs:485`), and it is the only function of the information the
  referee actually has. **Residual risk:** a generated roster with non-contiguous ids
  would give the referee a different `next_id` from a real engine seeded by mapgen.
  Nothing in the panel produces such a roster today.

- **UNRESOLVED-B — MINE and unit ownership.** `engine.rs::apply_mine` (646-667) does
  **not** check `u.player`; combined with `parse_cmds` (713-733), which does not check
  ownership either, the engine appears to let a player MINE with an opponent's unit.
  The referee's `_cmd_mine` refuses (`unit["player"] != 0 → return`), matching the
  inherited handling of every other unit-addressed verb. **I did not change this**: it
  is pre-existing behaviour shared by MOVE/HARVEST/CHOP/PLANT/PICK/DROP, it is not
  what this revision is about, and changing it would move the floor for unrelated
  reasons. Flagged as a genuine conformance gap, not claimed as conformance.

- **UNRESOLVED-C — full command priority order.** `engine.rs:753` and 762-801 specify
  MOVE, HARVEST, PLANT, CHOP, PICK, TRAIN, DROP, MINE. The referee's `_ordered`
  enforces only TRAIN's position; the rest of a line is applied in emission order.
  Carried over from r1 unchanged and for the same reason (reordering every line would
  move the floor for reasons unrelated to TRAIN). Real gap, next repair.

- **UNRESOLVED-D — per-unit command dedup.** `engine.rs:717-720` keeps a `used` set
  and drops a second command naming a unit already commanded this turn (TRAIN is
  exempt: 697-706 `continue`s before that bookkeeping). The referee has no such set —
  **MEASURED**, `make_banana_traces.Referee.apply` (133-145) does not track used ids.
  Pre-existing, out of scope, real.

- **UNRESOLVED-E — the corpus has no witness for the repaired rule.** §4.2: the floor
  bot emits TRAIN twice in 240 games and never at `n >= 2`, so the floor cannot
  observe this defect class in either direction. The self-tests carry the whole pin.
  A corpus bot that trains past two workers is the follow-up.

- **UNRESOLVED-F — `make_banana_traces.Referee.apply` still has the silent-default
  dispatcher** and is still used by that module's own scenarios. Outside my boundary
  (carried from r1).

---

## 7. The two `m040` regression rows

`TestM040RegressionRows` is **unmodified** by this revision — same identity pin, same
two seat assertions, same file. Both green in the GREEN run.

- `test_m040_identity_is_pinned` — map index 40 of the committed config is `m040`,
  class `forest_dense`, opponent `harvester`, one own worker in both seat variants.
- `test_m040_seat_0_no_longer_re_emits_train_every_turn` and
  `…_seat_1_…` — the real floor bot is compiled and run closed-loop for 200 turns;
  each seat must emit TRAIN **exactly once** (166/200 and 182/200 before the c1→c2
  repair) and that TRAIN must actually spawn the second worker.

They still hold under c3 for the reason §4.2 gives: the bot's own `can_train` stops it
after the second worker, so removing the referee's cap does not change what it emits.
The rows remain non-vacuous — `self.assertTrue(trains, …)` still requires a real TRAIN
attempt, and `len(own) == 2` still requires the spawn to have happened.

---

## 8. Reproduction

```bash
cd /home/tarstars/prj/troll_farm-claude_1/claude_1/pipeline
export PATH="$HOME/.cargo/bin:$PATH"

python3 -m unittest test_fuzz_panel      # 78 tests, OK
python3 -m unittest test_pre_review      # 24 tests, OK

# floor, ~12 s (config recipe in §4)
cd /home/tarstars/prj/troll_farm-claude_1
python3 claude_1/pipeline/fuzz_panel.py --config cfg-after.json \
        --report report-after.md --json after.json
```

The floor configs, the JSON payloads, the breakdown script and the mutation driver are
scratch artifacts (digests for the configs in §0); the committed
`fuzz-panel-config.json` still points at the real candidate/parent pair.

No Arena, no CI, no submissions. `rust/src/game/engine.rs`,
`rust/src/bin/yamo_orchard_live.rs`, `trace_detectors.py`, `make_banana_traces.py` and
every bot/candidate/parent/`.min.rs` were read only; their digests in §0 are unchanged.
