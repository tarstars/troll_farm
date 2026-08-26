# G-0 definitions and proof — Candidate 2: the standing-teammate exchange, no lock

- Task `20260825-dance-cure-candidate-2-swap`, chartered by
  `coordination/messages/local_claude_1/20260825T163400Z-…-policy.md` at
  `agent/local_claude_1@90f699f2207476815d6b67480d52d01f7d060824`; card
  `coordination/tasks/20260825-dance-cure-candidate-2-swap.md`; owner rule **R-1a** in
  `docs/RULES-LEDGER.md`.
- Work owner: claude_1 · G-0 reviewer: **codex_1** (design **and** proof) · optional second reader
  of the proof: chatgpt_1 · record and Arena: local_claude_1.
- **No line of Candidate 2 code exists yet and none will be written before codex_1's
  `DESIGN_ACCEPTED`.** This file is the whole G-0 deliverable: the exact predicate, the proof with
  its edge cases, the v5 grammar, the parity plan, the pre-committed bars, and the controls.
- Written 2026-08-25 (stamp from `date -u` in the writing command). Worktree pin at writing:
  `agent/claude_1@37f7de39db35840170ba76dc1ecae1ad328b3fc0`.

Plain words first in every section, then the exact text.

---

## 0. What the rule is, in one paragraph

Our troll wants to walk through the square where its own teammate is standing still and working,
and its road continues **past** that square. The two change places in a single tick: the mover
steps onto the teammate's square and the teammate steps back onto the mover's. The referee allows
exactly this — `docs/mechanics.md` §"Move conflict resolution": collisions are resolved within one
player's own units, contested cells go to the highest id, and **circular swaps are allowed**.
There is **no lock, no timer and no counter**: the rule's own two clauses — the partner must be
*standing* (same cell this turn and last) and the mover's target must lie *strictly beyond* the
partner's square — make the reverse exchange impossible on the next turn unconditionally, and make
any later reversal require the **planner** to move the teammate's own goal past its work square.
That is the theorem in §4, and §5 is the control that would falsify it.

---

## 1. Base, pins and what is imported

| item | pin | sha256 |
|---|---|---|
| champion (parity reference, α) | `cgauto/submissions/candidate-door1-pure-deletion.rs` | `547fa706cc1c684a1f8c2a08174792d95e553b2382facfe15884d2ef544070b0` |
| Candidate 1 source, the base of this build | `claude_1/cure1/cure1-hold-v4.rs` | `cc4b308705883f10192065dd205a36eb78baee3c1068a0697131b791f3d46e9b` |
| arm builder (one-line-diff gate) | `claude_1/cure1/build_arms.py` | `ae8ad83dd9b6e5a23ebaf817105946d16be6a7f8d89eb7f051dfc74abd601227` |
| source generator (anchored replacements) | `claude_1/cure1/make_cure1_source.py` | `01d61c091fea44453b28dfe72289d9e5e51bbb2ef9b6df9560056570fb37fa04` |
| per-troll idle-with-work safety net | `claude_1/cure1/idle_share.py` | `44e2de48a7d2fc489137582566b20ef73d3c847766177b6f2b6d44cb02490c72` |
| **read baseline** (the v4 instrument read, 160 games) | `agent/claude_1@22d6b2bb2418eece82d67d154c33441bbd655519:claude_1/cure1/results/g2-grade.json` | `45f5f22a1b2004886d59cc172586e0c132cae3b3e3c4c08e0d30ca742b4c90f9` |
| geometry evidence | `local_claude_1/dance-geometry/owner-brief-2026-08-25.md`; results at `agent/claude_1@c5727dc6` | — |

**Candidate 1's machinery that is reused verbatim and not re-litigated:** the two-phase
`resolve_move_conflicts_hold` / `hold_pass` split, the `prev_cells` one-turn memory, the mover
ordering, the `granted` / `reserved` sets, the memoised `distance_cache`, the `d_cur` fallback rule
(codex_1 definition 7: a cell's key uses its **own** `manhattan` fallback), and the R-B orchard
scoping predicate. **Candidate 1's hold rule is off in every Candidate 2 arm**
(`HOLD_RULE_ENABLED=false`): Candidate 1 is PARKED, its code kept.

Consequence used throughout, and made control **C-4**: with the hold disabled `hold_pass` never
returns a holder, so `resolve_move_conflicts_hold`'s fixed-point loop terminates on its **first**
pass. Candidate 2 adds no holder either (§2.4). **Every turn of every Candidate 2 arm runs exactly
one pass, `pz=1`.** The two-phase ordering hazard that sent Candidate 1's G-0 back therefore cannot
arise here — but it is asserted on the wire every turn rather than assumed.

My exclusive write set is `claude_1/cure2/**` and `claude_1/narrate5/**`. `claude_1/cure1/**`,
`claude_1/geometry1/**` and `claude_1/dance1/**` are read-only to me on this task.

---

## 2. The predicate — exact text

### 2.1 Where it sits

Inside `hold_pass`, in the per-mover loop, **after** the free-landing fast path
(`if !landing_forbidden && !reserved.contains(&landing) { … continue }`) and **before** the detour
search. It is reached only when the landing is unavailable — i.e. exactly the turns that are `L`,
`R` or `W` in the v4 grammar today.

### 2.2 Names

For the mover `M` under consideration in this pass:

- `c = M.cell` (its cell in the view), `T = target` (its selected target),
  `L = next_cell(&view.walkable, c, T, M.stats.movement_speed)` — the base's landing; `L ≠ c`
  because non-movers were filtered out before the loop.
- `toward_goal = bfs_distances(&view.walkable, &[T])`, memoised per target for the turn.
  `d(x) = toward_goal.get(&x).copied().unwrap_or_else(|| manhattan(x, T))` — each cell with its own
  fallback, codex_1 definition 7.
- `moving_ids` — own units whose landing differs from their cell, computed once per pass from the
  **original** commands, exactly as today.
- `prev_cells` — where every own unit **stood** on the previous turn, written at the end of the
  previous turn's resolve for every arm.
- `displaced` — new, per pass: the ids already taken as an exchange partner in this pass.
- `slot_by_id` — new, per pass: `own units sorted by ascending id` zipped with the command indices
  `0..commands.len()`. This is the mapping `select_recording` itself produces (it iterates the
  `BTreeMap` keys, one command per own unit, ascending). It is **guarded**: if
  `commands.len() != own_unit_count` the map is not built and **no swap fires this turn**
  (counted `sf=`), because a positional mapping that cannot be verified must not rewrite another
  unit's command.

### 2.3 The predicate

`SWAP(M)` fires with partner `B` iff **all** of the following hold:

1. `SWAP_RULE_ENABLED` (compile-time flag) and the game is not orchard-scoped inert (§3.6).
2. `slot_by_id` is available (`sf` guard above).
3. `!landing_forbidden` — `landing_forbidden = !priority_ids.contains(&M.id) &&
   forbidden_for_non_priority.contains(&L)`. Both sets are empty on the live path; the clause is
   inert today and safe if the machinery is ever revived.
4. **A standing own partner is on the landing.** There is an own unit `B` with `B.cell == L`, and
   - `!moving_ids.contains(&B.id)` — `B` is not a mover this pass (a self-targeting `MOVE`
     resolved to `WAIT`, a `CHOP`/`PLANT`/`PICK`/`WAIT`, all count as not moving); **and**
   - `matches!(prev_cells.get(&B.id), Some(p) if *p == L)` — `B` stood on `L` last turn too. An
     **unknown** previous cell (turn 1, a unit trained this turn) **fails closed**: no swap. This
     mirrors Candidate 1's accepted R-A treatment; **and**
   - `!displaced.contains(&B.id)` — `B` has not already been exchanged with another mover in this
     same pass.
5. **The landing is adjacent.** `is_adjacent(c, L)` (`manhattan(c, L) == 1`). A landing two cells
   away (`movement_speed ≥ 2`) is **excluded, not handled** — see E-2 — and counted `sn=`.
6. **The target lies strictly beyond the landing.** `T != L` **and** `d(L) < d(c)`.
   `T != L` excludes the teammate-on-the-goal case (`TARGET_OCCUPIED`), which is **recorded**
   (`so=`) and left to the planner, per the card. `d(L) < d(c)` is normally automatic — `L` is the
   first step of a BFS path — and bites exactly when `next_cell` fell back to the
   nearest-reachable/Manhattan branch on an unreachable target, which is the case where "beyond"
   is not meaningful.
7. **The mover's own cell is free to give.** `!reserved.contains(&c) && !granted.contains(&c)`.
   `c` is never in the initial `reserved` (`M` is a mover), so this clause fires only when an
   earlier mover in this same pass was granted `c`. Then no swap; today's behaviour.
8. `priority_ids.contains(&M.id) || !forbidden_for_non_priority.contains(&c)` — the same dead-machinery
   guard for the cell handed to `B`.

### 2.4 The effect

```
reserved.insert(L);  granted.insert(L);
reserved.insert(c);  granted.insert(c);
displaced.insert(B.id);
commands[M_index]        = format!("MOVE {} {} {}", M.id, L.0, L.1);   branch[M.id] = 'S';
commands[slot_by_id[B]]  = format!("MOVE {} {} {}", B.id, c.0, c.1);   branch[B.id] = 'X';
swaps += 1;   // telemetry sw=
continue;     // M is resolved; the detour search is not reached
```

`B`'s previous branch letter (`W` or `N`) is **overwritten** by `X`. No holder is added, so the
fixed-point loop still stops on the first pass. `blocked_turns` is untouched (its only writer was
the retired `H`). `prev_cells` is written at the end of the turn exactly as today, for every arm.
`remember_selected_regeneration` reads the **final** commands, after the resolver, so a
regeneration command replaced by an exchange is correctly forgotten — the ordering Candidate 1
already established.

**At most `floor(n/2)` exchanges per turn** for `n` own units: each exchange consumes two distinct
cells into `granted` and one partner into `displaced`, and neither is ever released within a pass.

---

## 3. What deliberately does **not** change

1. A **transient** blocker (a mover, or one that arrived on its cell only last turn) gets today's
   detour or `W`. The swap is for the standing worker only.
2. A mover whose **target is** the landing does not swap (clause 6): recorded, not cured.
3. No re-targeting, no change to `select`, `compatible`, `stock_compatible`, or any candidate score.
4. **No lock, no timer, no counter, no new memory.** `prev_cells` is Candidate 1's, already written
   by the base path on every turn. `displaced` and `slot_by_id` are per-pass locals.
5. The base's W-collision exposure is unchanged and still only measured (`wc=`).
6. **Orchard scoping — R-B adopted verbatim.** The panel's P3 check compares the **whole** command
   stream on orchard-eligible seat views, and an exchange changes commands, so the swap is
   **inert for the whole game** on a seat view satisfying the base's `orchard_eligible` predicate,
   evaluated once on the first view and cached. I do **not** claim P3-neutrality: the honest cost
   is that dances on orchard-eligible maps are untouched by Candidate 2, and it is stated here so
   the read is not mistaken for a whole-corpus cure. The flag `SWAP_P3_SCOPING_ENABLED` is the red
   half of control C-16 on an identical map.

---

## 4. The proof

### 4.0 Assumptions, named so they can be attacked

- **A-1 (referee).** Two own units issued `MOVE M→L` and `MOVE B→c` with `manhattan(c,L)=1`,
  `M` on `c`, `B` on `L`, both with `movement_speed ≥ 1`, exchange cells in that tick
  (`docs/mechanics.md` §"Move conflict resolution": circular swaps allowed). Enemy units never
  block (same section). **A-1 is not taken on faith**: control C-10 checks the realised next-turn
  cells of both units against this claim on every exchange in every game of the panel and the read.
- **A-2 (memory).** `prev_cells` read on turn `t` equals the cells own units occupied on turn
  `t-1`, and is absent for a unit not alive at `t-1`. This is the base's own write, verified by
  Candidate 1's G-1 and re-asserted by control C-11.
- **A-3.** Own unit ids are stable across turns while a unit lives.

Write `c_t(u)` for `u`'s cell in the turn-`t` view, `prev_t(u)` for the `prev_cells` entry read on
turn `t` (so `prev_t(u) = c_{t-1}(u)` by A-2), and `SWAP_t(M,B)` for "the predicate of §2.3 fired
on turn `t` with mover `M` and partner `B`".

### 4.1 Lemma 1 (the post-state)

If `SWAP_t(M,B)` fires then `c_{t+1}(M) = L = c_t(B)` and `c_{t+1}(B) = c_t(M)`.
*Proof.* Clause 5 gives `manhattan(c_t(M), L) = 1`; both emitted commands are one-step moves onto
the other's cell; both cells are `granted` so no third own unit is sent to either; by A-1 the
referee executes the circular exchange. ∎

### 4.2 Theorem 1 — the immediate reversal is impossible, unconditionally

If `SWAP_t(M,B)` fires, then **neither** `SWAP_{t+1}(B,M)` **nor** `SWAP_{t+1}(M,B)` can fire —
whatever either unit's target is on turn `t+1`, whatever else is on the map.

*Proof.* Both would need clause 4's standing test on the partner.

- `SWAP_{t+1}(B,M)` needs `M` standing on `B`'s landing, i.e. `prev_{t+1}(M) = c_{t+1}(M)`. By A-2
  and Lemma 1, `prev_{t+1}(M) = c_t(M)` and `c_{t+1}(M) = L`, and `c_t(M) ≠ L` because
  `manhattan(c_t(M), L) = 1`. The test fails.
- `SWAP_{t+1}(M,B)` needs `B` standing, i.e. `prev_{t+1}(B) = c_{t+1}(B)`. By A-2 and Lemma 1,
  `prev_{t+1}(B) = c_t(B) = L` and `c_{t+1}(B) = c_t(M) ≠ L`. The test fails. ∎

This is the owner's requirement discharged in its strongest form: **the back-swap on the next tick
is not merely unattractive, it is unrepresentable**, and the reason is a clause the rule already
needs for its own purpose (only a *standing* worker may be displaced), not a lock bolted on.
Note it holds even when `M` is blocked ahead and stands still on `L` — one turn of memory is enough
because the exchange itself is what destroys both units' standing status.

### 4.3 Theorem 2 — any later reversal requires a planner event

Let `SWAP_t(M,B)` fire and let `t' > t+1` be the earliest turn at which `SWAP_{t'}(B,M)` fires
(the pair exchanging back). Then both of the following are true:

(a) `M` was stationary on `L` across turns `t'-1 → t'`: `prev_{t'}(M) = c_{t'}(M) = L`. In
    particular `M` did not advance along its road — it was blocked by something **other than** `B`
    (`B` is behind it), and its branch on `t'-1` was `W` or `N`, never `S`, `P`, `L` or `R`.

(b) `B`'s target `T_B` on turn `t'` satisfies `T_B ≠ L` and `d_{T_B}(L) < d_{T_B}(c_{t'}(B))` —
    **`B`'s own goal lies strictly beyond its former work square.**

*Proof.* (a) is clause 4 applied to `M` at `t'` plus A-2; since `SWAP_{t'}(B,M)` needs `B`'s landing
to be `M`'s cell and `M` standing there, `M` was on `L` at `t'-1` and `t'`. (b) is clause 6 applied
to `B` at `t'`. ∎

**Why (b) is a planner event and not something the rule can cause.** On turn `t`, `B` was a
non-mover standing on `L` — it was working there, or it wanted nothing, or its own landing was
`L` itself. For `SWAP_{t'}(B,M)` we need `B` to want a square **strictly past** `L` measured from
`c_{t'}(B) = c_t(M)`. Nothing in §2.4 writes a target: the exchange changes cells and commands, and
`select`/the candidate generators alone choose targets. So a reversal is possible only if the
planner has moved `B`'s goal to the far side of its own work square in the meantime.

**Corollary.** If `B`'s target is unchanged — `L` itself, or `Target::None`, the case the geometry
brief says dominates (the standing teammate on its work square, on every shortest road on 91 % /
78 % of measurable turns) — then **no reversal ever occurs, at any distance in time**, not merely
on the next tick.

### 4.4 What is **not** proved, and is therefore measured

The theorems bound what *the rule* can do. They do **not** forbid a planner oscillation: if
`select` flips `B`'s target back and forth across `L`, the pair can exchange repeatedly, one
exchange per flip, with a stationary `M` in between. That is a **planner** defect, and the card is
explicit that the remedy is never a lock. It is counted by control **C-5** (same unordered pair
exchanging twice within 6 turns); **any positive count on the panel or the read is a
stop-and-ask finding**, reported with the games, turns, ids and both targets, and the answer may
be Candidate 3 — never a timer here.

---

## 5. Edge cases — every one the card names, with its disposition

| # | case | disposition |
|---|---|---|
| E-1 | **three own trolls in one pass** | Clauses 4 (`!displaced`) and 7 (`c` not already granted) plus the unconditional `granted.insert` of both cells. A second mover blocked by the same `B` finds `B` in `displaced` → today's rule. A mover wanting `c` finds it in `reserved` → today's rule; its transient test sees `M` (a mover) on `c`, so it is treated as transient exactly as today. Chained exchanges within one pass are impossible; ≤ `floor(n/2)` per turn. **Handled.** |
| E-2 | **`movement_speed ≥ 2`** | `next_cell` BFS-walks up to `speed` cells and ignores occupancy, so a landing may be two cells away. `MOVE B c` is executed by the engine along `B`'s own path at `B`'s speed, and with a non-adjacent landing the two commands are not a cell exchange — the intermediate square belongs to nobody and A-1 does not apply. **Excluded by clause 5, counted `sn=`, reported in G-1 with the share of blocked turns it costs.** A fast troll blocked by a standing teammate keeps today's detour. |
| E-3 | **`B` on `M`'s target** (`TARGET_OCCUPIED`) | Excluded by clause 6 (`T != L`). Counted `so=` and reported per game; 10 + 15 turns across the two reads, a planner question, explicitly out of scope. **Handled by exclusion, with a number.** |
| E-4 | **`B` is a mover this pass** (transient) | Clause 4 fails; today's detour/`W`. **Handled.** |
| E-5 | **`prev_cells` unknown** — turn 1, or a unit trained this turn | `None => false`: **fails closed**, no swap, same as R-A. A swap on turn 1 is impossible by construction. **Handled.** |
| E-6 | **dead `priority_ids` / `forbidden_for_non_priority`** | Clauses 3 and 8 replicate the base's guard for **both** granted cells. Both sets are empty on the live path (`resolve_move_conflicts_hold` builds them empty), so the clauses are inert today; they are written so a revival cannot silently hand out a forbidden cell. **Handled.** |
| E-7 | **orchard-eligible maps (P3)** | R-B adopted verbatim: whole-game inert on an eligible seat view, decided once from the first view and cached. Not a neutrality claim — a scoping cost, stated in §3.6 and controlled by C-16. **Handled by scoping.** |
| E-8 | **what `B` loses on the swap turn** | Exactly one action: its `CHOP`/`PLANT`/`PICK`/`HARVEST`/`WAIT` for that tick is replaced by the step back. Paid once per exchange, never repeated for the same pair without a planner event (Theorem 2). Measured: `sw=` per turn, and the panel's per-game score delta and named-cost table. **Handled and priced.** |
| E-9 | **`B`'s command is a self-targeting `MOVE` resolved to `WAIT`** | It is not in `moving_ids`, its cell **is** in `reserved`, and its branch is already `W`; the exchange overwrites the command and the branch letter with `X`. `remember_selected_regeneration` reads post-resolver commands, so a replaced regeneration commitment is not remembered. **Handled.** |
| E-10 | **positional command mapping** | `select_recording` emits one command per own unit in ascending id order, and `commands[index]="WAIT"` in the base already relies on that positional identity. Candidate 2 rewrites **another** unit's slot, so the assumption is promoted to a guard: the map is built only when `commands.len()` equals the own-unit count; otherwise no swap this turn (`sf=`, expected 0, reported if not). **Handled by a fail-closed guard.** |
| E-11 | **enemy units** | `reserved`, `occupied_now` and the partner search are own-player only, as in the base; an enemy on `L` yields no partner → today's rule. Enemies cannot block moves (mechanics §53). **Handled.** |
| E-12 | **`B == M`** | Impossible: `B.cell = L ≠ c = M.cell`. |
| E-13 | **the fixed-point loop** | Candidate 2 adds no holder, and the hold is off, so `pz = 1` on every turn — asserted on the wire (C-4), not assumed. |

---

## 6. Telemetry grammar v5 — and mutual refusal with v4

`NARRATE v5 t=<turn>` then, for **every live own unit exactly once, ids ascending**,
`u<id>=<chosen>/<want>/r=<code>/b=<counter>`, then the per-turn fields
`pz=<passes> sp=<stale> wc=<w-collisions> sw=<exchanges> so=<target-occupied refusals>
sn=<non-adjacent refusals> sf=<slot-guard refusals>`.

- `r ∈ {P, L, R, W, N, S, X}` — `S` the mover of an exchange, `X` the displaced partner.
  **`H` is retired** and must never appear.
- `b=` is kept in the shape for the decoder's benefit and is **identically 0** in every v5 arm
  (`blocked_turns`' only writer was `H`); asserted by C-9.
- **Mutual refusal.** `claude_1/narrate5/` refuses any payload whose header is not `NARRATE v5`,
  and `claude_1/narrate4/narrate4_join.py` (`53e2c41ce264b6ce`) refuses `NARRATE v5`. Both
  directions are executed as controls, not asserted.
- Budget: v4's longest observed payload was 142 characters against 2,000; v5 adds four short
  integer fields. The G-1 report publishes the longest observed v5 payload.

---

## 7. The arms, and the parity plan

One source `claude_1/cure2/cure2-swap-v5.rs`, generated from `cure1-hold-v4.rs`
(`cc4b3087…`) by anchored replacements that must each match exactly once, with
`HOLD_RULE_ENABLED=false` in every arm. `build_arms.py`'s one-line-diff gate is reused: an arm that
differs from the source in more than the flag line is refused.

| arm | `SWAP_RULE_ENABLED` | `NARRATE_V5_ENABLED` | role |
|---|---|---|---|
| `arm-instrument.rs` | true | true | the G-2 read; never a champion |
| `arm-candidate.rs` | true | false | the G-3 block, and the ladder if kept |
| `arm-ruleoff.rs` | false | true | the α parity reference |
| `poison-p-c-*.rs` | true, **predicate gutted** | both | see C-7 |

**α parity claim.** With `SWAP_RULE_ENABLED=false` and `HOLD_RULE_ENABLED=false`, `hold_pass` is
the base loop verbatim: the `S`/`X` block is behind the flag, `displaced`/`slot_by_id` are unread,
and the hold arm is unreachable. Therefore rule-off must be the champion `547fa706…`
**byte-identical in play** (MSG stripped) on the 34 frozen fixtures and all 240 panel games, with
identical next referee state. That is control C-1 and it is a **hard gate**, not a target.

---

## 8. Pre-committed bars — fixed here, before any number exists

**G-1, the 240-game panel** (subject `arm-candidate.rs`, base = the champion over the identical
corpus):

| quantity | bar |
|---|---|
| rule-off vs champion, 34 fixtures + 240 panel | byte-identical in play — **hard** |
| candidate arm vs instrument arm, in play, 240 games | identical — **hard** |
| blocking games (D-3) | **not above the base's 43** |
| P3 games on orchard-eligible views (whole-game) | **0** |
| P4 violations | not above base; **and P4b** (`20260825-p4-per-troll-stall-gate`) once I have accepted it |
| per-troll idle-with-work share (net until P4b lands) | **≤ 1.5 %** |
| the 11 reproduced dance fixtures | `progress_restored` |
| swap ticks | **≤ 1 per 50 turns per game** |
| same pair exchanging twice within 6 turns (C-5) | **0** — any positive count is a *stop and ask* |
| same pair exchanging on consecutive turns (C-6) | **0**, and a positive count **falsifies Theorem 1** |
| games changed in play | each named with its first divergence |

**G-2, one ~160-game instrument read** (Arena; the owner's separate go, surfaced before it starts).
Baseline = the v4 read, same telemetry family, 160 games:

| quantity | v4 read | bar |
|---|---|---|
| D-1 episodes per 1,000 game turns | 0.594 | **≤ 0.30** |
| dances of ≥ 12 turns | 13 | **≤ 4** |
| regressive steps `R_pos` per 1,000 troll-turns | 4.31 | **≤ 2.2** |
| dances ending in the dancer's own progress | 44 % | **≥ 65 %** |

Kill conditions: idle-with-work > 1.5 %; D-3 > 0; long-stall share above the champion's 1.3 %; any
same-pair re-exchange within 6 turns → stop and ask.

**G-3**: one ABAB block vs the champion, floor −1.0; the owner rules KEEP on the verdict sheet.
Nothing in this file authorises an Arena action.

---

## 9. Controls — each with the number it must produce

| id | control | must produce |
|---|---|---|
| C-1 | α parity: rule-off vs champion, 34 fixtures + 240 panel, MSG stripped, plus identical next referee state | 34/34 and 240/240 byte-identical |
| C-2 | arm equivalence: candidate vs instrument in play | 240/240 |
| C-3 | build gate: exactly one line differs per arm | refusal otherwise |
| C-4 | single-pass invariant | `pz=1` on every turn of every arm and game |
| C-5 | **swap-loop counter**: same unordered pair exchanging twice within 6 turns | 0 on the panel and the read; positive ⇒ stop and ask, with games/turns/ids/targets |
| C-6 | **theorem control**: same pair exchanging on consecutive turns | 0 — a positive count is an emergency stop and falsifies Theorem 1 |
| C-7 | **poison arm P-c**: predicate gutted to "swap on every block" (no standing test, no beyond test, no adjacency) | C-5 and C-6 must both fire loudly ⇒ the counters are not inert |
| C-8 | positive control: a fixture where the exchange must fire and the dance ends | fires, and `progress_restored` |
| C-9 | v5 decode: one token per live own unit per turn, `r` in grammar, **no `H`**, `b==0` always, longest payload published | 0 telemetry errors over the whole corpus |
| C-10 | **A-1 check**: for every `S`/`X` pair, the realised next-turn cells are the exchange | 100 % of exchanges; any miss is a referee-model finding |
| C-11 | `prev_cells` check: the map read on turn `t` equals the cells of turn `t-1` | 100 % |
| C-12 | per-troll idle-with-work share, and P4b once accepted | ≤ 1.5 % |
| C-13 | determinism: two runs with explicit `--label`/`--peer-label`, byte-identical outputs | identical |
| C-14 | refusal counters `so=`, `sn=`, `sf=` reported per game | `sf` expected 0; `so`/`sn` are the cases excluded by rule, published as costs |
| C-15 | named costs: per-game score deltas vs base, every changed game named with its first divergence | published |
| C-16 | R-B red half: `SWAP_P3_SCOPING_ENABLED=false` on an identical orchard-eligible map | P3 fires ⇒ the scoping is doing work, not decoration |

---

## 10. What would make me withdraw the design

- C-6 positive: Theorem 1 is wrong and the rule goes back to G-0, not to a lock.
- C-10 below 100 %: A-1 is wrong about the referee and the whole exchange premise fails.
- C-1 not byte-identical: the parity story is broken before any claim can be made.
- C-5 positive with a stationary `M` and a flipping `B` target: the planner is the defect; I report
  it as a stop-and-ask finding and do **not** add a timer.

## 11. Open questions for codex_1 (answer with the ruling)

1. **Clause 5 (adjacency).** Excluding `speed ≥ 2` landings is the conservative reading; the
   alternative is to define the exchange for the *first step* of a fast mover's path (`MOVE M`
   toward `L₁`, `MOVE B` to `c`), which is representable but changes the mover's own landing and
   therefore its progress. I recommend the exclusion for G-1 and a measured share (`sn=`); say if
   you want the first-step variant defined now instead.
2. **Clause 7** currently declines the swap when an earlier mover was granted `c`. The alternative
   (re-ordering movers so exchanges are considered first) buys a few turns and costs determinism
   of the base's mover order. I recommend declining, i.e. no ordering change.
3. **§3.6 scoping.** I adopt R-B verbatim and state the cost. If you would rather see a
   P3-neutrality attempt, it is a different design and I would want it ruled before G-1.

---

## Addendum A — the record owner's answers to §11, adopted (2026-08-25)

Added after the first publication of this file, in response to
`coordination/messages/local_claude_1/20260825T165216Z-…-policy.md`. Nothing above is withdrawn or
altered; this section only fixes the three open judgement calls and adds two reporting obligations.
codex_1's G-0 ruling governs the whole file including this addendum.

**§11.1 — adjacency.** Excluded as written: `speed ≥ 2` landings do not swap, and `sn=` publishes the
share. The coordinator's measured context: 2 of 80 and 2 of 25 dancers on the two reads are speed-2,
so this is a number to report, not a design hole.

**§11.2 — clause 7.** Declined as written: when an earlier mover in the same pass already holds `c`,
no swap. The base's mover order is part of the α-parity story and is not re-ordered.

**§11.3 — scoping.** R-B verbatim with the cost stated, **plus** a new publication rule: the
**scope-inactive share must be printed beside every headline** of the G-2 read (14 of 160 games on
the v4 read were orchard-eligible), so the cure can never be quoted as whole-corpus.

**A-1 / control C-10 — first-game reporting.** The panel's referee is our own `referee.grow()` model;
the ladder is the first real test of the circular exchange. **G-2's ledger reports C-10 on the first
collected game before any other number is read**, and a C-10 miss there stops the read rather than
being averaged into it.

**C-5 — split any positive count by which side's target moved.** A same-pair re-exchange within 6
turns is reported with the side whose target churned: the **dancer's** (Theorem 2(a) — the dancer
stood still on `L`) or the **worker's** (Theorem 2(b) — the worker's goal moved past its own square).
The reads show the dancer's target churning in 9 of 25 dances, so the two paths are not equally
likely and a stop-and-ask must name the right one.

---

## Addendum B — codex_1's §4.3 wording correction, adopted (2026-08-25)

`codex_1` ruled **DESIGN_ACCEPTED** on this file at
`coordination/messages/codex_1/20260825T165607Z-20260825-dance-cure-candidate-2-swap-ack.md`
(full ruling `codex_1/reviews/dance-cure-candidate-2-swap-g0-2026-08-25.md`), reviewing the
artifact at `agent/claude_1@6eb89209961a67e22e80c8c807b38947868c990a`. One non-gating wording
correction was recorded, and it is adopted here verbatim in effect.

**The defect.** §4.3's proof of (a) says `M` was on `L` at `t'-1` and `t'`, and the surrounding
prose can be read as claiming that `B` remains on `c_t(M)` from `t` until the reversal. **That
claim is false and is not needed.** `B` may move in the intervening turns — it may wander off
`c_t(M)` and come back, or be somewhere else entirely at `t'-1`.

**What actually holds.** Clause 4 applied to `M` at `t'` gives `M` standing on `L` at `t'-1` and
`t'`; clause 6 applied to `B` at `t'` gives the inequality `d_{T_B}(L) < d_{T_B}(c_{t'}(B))` at
`B`'s **actual** cell on `t'`, whatever that cell is. The theorem needs the inequality at the
actual later cell, never an equality `c_{t'}(B) = c_t(M)` held across time.

**Binding on the evidence.** G-1 evidence for a reversal must be written from the **actual cells
and actual targets read on turn `t'`**, and must never restate the equality as an invariant. The
C-5 rows published in G-1 and G-2 therefore carry, for each reversal: both cells at `t'-1` and
`t'`, both targets at `t'`, and which side's target moved (the split required by Addendum A).

No clause of §2.3, no bar of §8 and no control of §9 changes. The theorem stands as proved with
the inequality in place of the equality.
