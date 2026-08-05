# Semantic harness skeleton — banana wood-printer restoration (r2)

Date: 2026-08-04. Deliverables:

- Harness: `/home/tarstars/prj/troll_farm-claude_1/claude_1/banana-restoration-r2/semantic_harness.py`
- TIER-P goldens: `/home/tarstars/prj/troll_farm-claude_1/claude_1/banana-restoration-r2/tier-p-golden.json`
- This report: `scratchpad/banana/harness-report.md`
- Smoke evidence (parent run as its own candidate): `scratchpad/banana/smoke-tier-c.json`

## What was built

Mirrors the house pattern of `harness-example-validate_semantics.py`:

- `compile_text()` — `rustc --edition=2021 -O -Awarnings` from stdin source, with
  `$HOME/.cargo/bin` prepended to PATH; binaries live only in a `tempfile.TemporaryDirectory`.
- State builders — `unit()` (14-field row incl. stats + 6-slot carry), `plant()` (kind, cell,
  size, health defaulting to the family formula incl. banana `2+size`, fruits, cooldown),
  `turn_text()` (own/opp inventories, plant block, unit block), `transcript(rows, turns)`
  (static map header + any number of per-turn blocks — the multi-turn serializer). Verified
  field-by-field against the parent's `protocol` module (`read_static_map` / `read_turn`).
- Map geometry mirrors — Python `parse_rows`/`bfs`/`doors`/`ring`/`orth_ring`/`diag_ring`/
  `door_distance` so fixtures can compute the Chebyshev-1 plot, door BFS distances, and ETA
  predicates identically to the spec's definitions.
- Command plumbing — `commands()` (splits `;`, strips `MSG`), `validate_command()` (arity
  table incl. `PLANT id KIND` / `TRAIN` 4-stats), `run_deterministic()` (every payload is run
  twice and byte-compared: determinism is asserted on every fixture).
- Three purpose-built maps: `MAP_PLAIN` (no banana context), `MAP_RING` (full 8-cell ring, no
  water → `SecureOrchardBot` geometry is `None` → banana-eligible per I-28), `MAP_ORCHARD`
  (water-adjacent mother door, enemy door distance ≥ 11, natural-median ≥ 8 → orchard-eligible,
  verified against the parent's `initialize` gates).
- Fixture registry: `TIER_P` (7 fixtures, run now against the parent, outputs recorded as
  golden) and `TIER_C` (8 fixture families, executed only with `--candidate <src>`; reported
  as `PENDING_CANDIDATE` in the golden JSON otherwise). CLI:
  `semantic_harness.py [--parent P] [--candidate C] [--golden-out J] [--results-out J]`.

## TIER-P results (run now, parent `parent-a8eb3b2b.min.rs`, sha256 in the JSON)

All 7 PASS; goldens (full per-turn command lines + payload/stdout sha256) recorded in
`tier-p-golden.json`. Every TIER-P fixture also asserts the parent emits **zero**
BANANA-token commands (dormancy) and well-formed arities only.

| fixture | invariants | golden highlights |
|---|---|---|
| p_baseline_plain | check-4, I-1 | corridor, no banana context; byte-equality reference |
| p_orchard_eligible | I-27, I-28 | apple-priority map; candidate must byte-equal this |
| p_banana_inventory_dormant | I-1, I-2 | BANANA=2 banked, ring map; attribution seam reference |
| p_wood_banking | I-19–I-21 | MOVE, MOVE, DROP — parent banks carried wood at the door |
| p_two_worker | I-22, I-23 | one ripe tree: exactly one worker engages (`MOVE 1 4 1`), other WAITs |
| p_late_window | I-1 | 105 turns, banana banked, single worker: never a banana verb |
| p_training | I-16–I-18 | rich state: `TRAIN 3 3 0 3` at turn 1 (re-emitted open-loop) |

Surprises found while recording:

1. **On-cell verb model.** The parent emits `CHOP`/`HARVEST` only when `unit.cell ==
   plant.cell` (units walk onto trees). Fixtures originally scripted "adjacent" workers were
   redesigned to stand on the plant/vacancy cell.
2. **MSG banner.** Turn 1 starts with `MSG yamo-carry-regen-transit-idle-harvest-rust`;
   goldens keep raw lines, so byte-equality fixtures include it (a candidate derived from the
   parent reproduces it).
3. **Arbitration nuance.** In p_two_worker the parent sends the *farther* worker onto the tree
   and idles the adjacent one; and in the target-recovery scenario a lone alternative tree is
   claimed by the peer, making starter `WAIT` legitimate — the destroyed-target fixture needed
   a second alternative tree to make "definite retarget within 3 turns" a fair assertion.
4. **Open-loop TRAIN repeat.** Since scripted states never apply commands, the parent re-emits
   `TRAIN` every turn; parity is therefore asserted on the *first* occurrence (turn + tuple).

## TIER-C fixture list (implemented; run later with `--candidate`)

| fixture | check-7 area | invariants | asserts |
|---|---|---|---|
| c_bootstrap_budget | bootstrap | I-1, I-2, I-16 | 1-worker payload byte-equals parent (dormancy before second worker); every `PICK <id> BANANA` is by the starter (min id) |
| c_bounded_placement | bounded placement | I-12, I-13, I-15 | with a carried seed at 5 non-ring positions: zero `PLANT BANANA` (PLANT lands on the unit's scripted cell); ring controls recorded; full ring ⇒ no seed `PICK`, no `PLANT` |
| c_replant_renewable | renewable harvest/replant | I-3, I-9 | seed + ring vacancy at turn ~50 ⇒ `PLANT BANANA` within CD_dry=6 probe turns; surplus carrier (ring full, 2 bananas) banks or approaches a door |
| c_late_conversion | late conversion | I-4, I-5, I-6, I-14, I-1 | turn ~260 on a size-2 orth banana with fruited mother nearby: CHOP dominates, no HARVEST; 296-turn seed stream: first `PLANT BANANA` ≤ 100 and never a fresh decision after T_late=282; scripted plant-then-grow narrative: own diagonal mother never chopped (INCONCLUSIVE if candidate never plants) |
| c_banking | banking | I-7, I-8, I-9, I-21 | door-standing surplus carrier resolves within A=6 turns via `DROP` or the one replant `PLANT`; full far carrier emits door-approach MOVE (BFS distance strictly decreases) |
| c_eta_suppression | enemy ETA suppression | I-10, I-18, I-17 | opponent chopper 2 BFS moves from the seeded ring cell ⇒ zero `PLANT BANANA` (control at distance 7 recorded); funding payload byte-equals p_training golden |
| c_arbitration | two-worker arbitration | I-16, I-17, I-22, I-23, I-27, I-28 | byte-for-byte equality with p_orchard_eligible and p_baseline_plain goldens; TRAIN parity (turn + stats tuple) vs golden; on a shared mother: ≤1 HARVEST/turn, distinct MOVE destinations, no consecutive MOVE onto the working peer's cell |
| c_target_recovery | destroyed/occupied target recovery | I-24(i), I-26, I-23 | after scripted mother destruction: definite non-WAIT starter command within 3 turns, no period-2 a,b,a,b MOVE-destination alternation; peer standing-working on the mother: starter never orders MOVE onto it on 2+ consecutive turns |

Smoke run (parent compiled as its own candidate, `smoke-tier-c.json`): 6 of 8 PASS —
the parent already satisfies the non-banana predicates and the byte-equality/TRAIN-parity
checks are exact; `c_replant_renewable` FAILs (by construction it demands the banana feature)
and `c_late_conversion.mother_guard` is INCONCLUSIVE (parent never plants). This is the
expected discrimination signature: a correct candidate must flip exactly those two.

## Gaps — what single-turn/open-loop fixtures cannot cover

The serializer is **multi-turn but open-loop**: `transcript(rows, [s1, s2, ...])` feeds an
arbitrary scripted state *sequence* (used for the banking approach, the destroy-at-turn-41
switch, and the plant-invite → grown-mother narrative), but emitted commands are never
applied back to the state. Consequences, per check-7 area:

- **I-11 (lifetime non-forfeiture), D-6(b), D-7 full ledger, I-2 exact ≤1 bootstrap-PICK
  count, I-20 true positional monotonicity, D-1 real position oscillation** — all quantify
  over executed effects (positions, fruit counts, inventories responding to commands). Open
  loop can only see ordered intentions; re-emission of an unapplied command is
  indistinguishable from a repeated decision. These need the closed-loop replay gate
  (acceptance checks 5/6) or a Python mini-referee that applies MOVE/HARVEST/DROP/PLANT
  between turns — the serializer's state-sequence interface is already shaped for that: a
  referee would just generate the `turns` list from the previous turn's commands.
- **Plant provenance.** The stdin protocol carries no plant owner; "own-planted" invariants
  (I-4/I-14 mother protection) are approximated with scripted narratives where the candidate
  must plant first, else INCONCLUSIVE. Exact provenance needs replay telemetry
  (`target(u,t)` per the spec's attribution section).
- **T_ripe/payback arithmetic (I-1 feasibility term)** and **I-13 concurrent-live counting**
  over a whole game are replay-gate detector work (D-5), not few-turn fixtures.
- **I-15 full gate-awareness** (alternate-door reachability for the non-resident after
  commitments) is only spot-checked via the full-ring no-PICK/no-PLANT probe.

Constraints honored: Python 3.12 stdlib only; deterministic (no timestamps in outputs, every
run double-executed and byte-compared); parent file untouched; binaries only in temp dirs.
