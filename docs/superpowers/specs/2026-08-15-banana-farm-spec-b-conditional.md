# Banana-farm bot — Spec B (conditional entry: "if third troll")

- Status: DRAFT for `codex_1` review then owner review
- Author: `local_claude_1` (drafted by subagent under its direction)
- Date: 2026-08-15
- Task record: `coordination/tasks/20260815-banana-farm-two-specs.md` (stage 4 of
  `docs/PROGRAMME-banana-farm-2026-08-15.md`)
- Companion: Spec A, `docs/superpowers/specs/2026-08-15-banana-farm-spec-a-unconditional.md`.
  Sections 3–8 (the shared skeleton) are **identical text** in both files by design;
  section 9 is where the two specs differ.
- Base bot: `cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs`
  (1475 lines), SHA-256 (a cryptographic file fingerprint)
  `98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29`.
  **All line numbers in this document point into this file** and were verified against it
  on 2026-08-15. This is the "readable no-orchard" ladder resident: human-readable
  formatting, all old orchard (banana-planting) code removed. There is **no** farm code in
  it today; everything in section 6 is a fresh graft.
- Farm mechanism source: the D89a blueprint (D89a is the experiment code for the July 2026
  "banana seed factory" — the only farm this project ever ran at scale),
  `data/analysis/live-agent-6553250/d89a-banana-seed-factory-blueprint-2026-07-21.md`.
- Direct ancestor: the CBF spec (CBF = "conditional banana farm", the 2026-08-07 design),
  `docs/superpowers/specs/2026-08-07-conditional-banana-farm-design.md`. **This file is
  that design re-based** onto the readable resident, as the task record requires: the CBF
  spec's line references (`yamo_orchard_live.rs:1101-1105`, `:1066`, `:1193`) targeted the
  old compact resident (SHA `fff6669b…`) and are all replaced below; its machine, sensors,
  W=30/K=5/T=0 constants, and reasoning are kept.

## 1. What this bot does, in the owner's words

Both specs implement one pipeline, decided by the owner on 2026-08-15:

> gather resources → train the second troll → select lemon or plum → deny (chop) the
> selected species near the enemy → banana farm → **abort** to aggressive all-out chopping
> when the enemy collects more from our farm than we do.

Plain-language glossary for this document (owner rule: every code name explained at first
use; the recurring ones are gathered here):

- **Troll / unit** — one of our workers on the board. We start with one and can TRAIN
  (buy) a second.
- **Shack** — each player's home building. **Bank / inventory** — the stock of items
  stored at the shack; the referee sends both players' inventories every turn.
- **Denial** — chopping the fruit species the opponent needs, close to their shack, so
  they cannot pay for extra trolls.
- **Focus species** — the one species (lemon or plum) chosen for denial, picked once at
  game start and never changed.
- **Banana farm** — planting banked bananas, harvesting them when ripe, and replanting
  each harvest, so bananas compound into score (each banked banana is one point:
  `score()` at lines 120–121 counts `inventory[3]`, and `BANANA` is item index 3,
  line 14).
- **Abort** — a one-way switch to plain aggressive wood-chopping if the farm is feeding
  the opponent more than us.
- **Latched** — a switch that can only ever be flipped once, in one direction. It cannot
  un-flip, so the bot can never oscillate (flip back and forth) between behaviours.
- **Byte-identical** — the new bot's printed commands are exactly, character for
  character, what the resident would have printed.

**What makes this Spec B:** farming is *conditional* — the machine enters FARM only when
the enemy fields a **third troll** (latched on first observation), i.e. only in games
where we are already out-scaled. Spec A enters FARM in every game, at second-troll
readiness.

## 2. Prior art and what this design is built against

D89a (2026-07-21) proved the farm mechanism works: activation 256/256, 1,344 bank bananas
planted, a sustained harvest-and-replant loop in 252/256 games, mean paired margin
**+79.441** (CI [+40.991, +117.892]). It was rejected on tail risk: worst pair −235,
p10 margin −72, and the opponent's own score rose +82.863. Whether that opponent gain came
from stealing our crops or from their own production is **UNRESOLVED** (the once-quoted
+12.5/+76.5 split was prose, not measurement — see the correction in §2 of the CBF spec).
The D89a leak carries a standing `NOT_REPAIRABLE` verdict; per the task record it is
**bounded by design here, not repaired**.

Spec B is the CBF answer to that tail: do not try to fix the leak — bound exposure to it
twice over. Farm **only in games we are already losing** (the enemy's third troll; the
B3.1 audit found opponent scaling precedes our collapse by 42–125 turns in 84% of
catastrophes), and stop as soon as the farm is observably feeding the opponent (the
abort, section 7). Spec A keeps only the second bound. Which trade is better is a
measured question (section 12), not a design argument.

## 3. Shared skeleton — the state machine (identical in both specs)

One persistent machine on the bot. Three states, two transitions, both latched. There is
no path back and no direct DENY → WOOD edge.

```
DENY ──(FARM-entry predicate; THE ONLY LINE THAT DIFFERS BETWEEN SPECS)──► FARM
FARM ──(abort sensor trips; identical in both specs)──────────────────────► WOOD
```

- **DENY** — the resident's behaviour, unmodified except for the denial-bonus re-gating in
  section 5. Gathering, training the second troll, selecting the focus species, and
  chopping it near the enemy are all things the resident already does:
  - Focus selection: `focus_type()` at lines 341–356 picks lemon or plum by summed
    walking distance and is assigned **once** in `ensure_opening()` at lines 796–799
    (`if self.type_to_cut.is_none()` — an existing latch; we follow its pattern).
  - Training: `can_train()` at lines 400–408; the `TRAIN` command is emitted at
    lines 1387–1389; a hard deadline abandons the opening at turn 35
    (`enforce_training_deadline()`, lines 914–919).
  - Denial: inside `chop_candidates()` (lines 582–637) a chop is scored
    `1000.0*wood/turns` (line 619) and the focus species gets a proximity bonus
    `score += 900.0/(1+opponent_distance)` (line 622), today gated live on
    `opponent_trolls <= 2` (line 620), where `opponent_trolls` is
    `view.units.iter().filter(|unit|unit.player==1).count()` (line 590).
- **FARM** — DENY plus the grafted D89a farm task on the starter troll (section 6). The
  trained troll keeps the resident wood/logistics behaviour. Denial by the trained troll
  continues for as long as the denial latch permits (section 5).
- **WOOD** — aggressive all-out chopping: no denial bonus, no farm actions, both trolls on
  the resident's plain wood policy. This is the abort target, reached only from FARM.

State and latches are new fields on the `YamoBot` struct (field list at line 335). The
machine is updated once per turn at the top of `commands()` (lines 1375–1441), next to the
existing per-turn housekeeping calls at lines 1377–1379.

**Why latched:** an A → B → A loop is unrepresentable by construction — this is the whole
anti-oscillation argument and it is structural, not tuned. Oscillation is closed in
`docs/CONSTRAINTS.md`; we get the property for free and claim no value for it.

## 4. Shared skeleton — entry-condition scaffold (identical in both specs)

Two one-way observation latches feed the FARM-entry predicate:

| Latch | Set when first observed | Expression (base-file anchors) |
|---|---|---|
| `second_troll_ready` | our unit count reaches 2 | `view.units.iter().filter(\|u\|u.player==0).count() >= 2` — same filter as line 401 |
| `enemy_third_troll` | opponent unit count exceeds 2 | `view.units.iter().filter(\|u\|u.player==1).count() > 2` — same expression as line 590 |

Once set, a latch never clears (the count dropping back does not revert it).

- **Spec A:** FARM entry ⇔ `second_troll_ready`.
- **Spec B:** FARM entry ⇔ `second_troll_ready && enemy_third_troll`.

That single conjunct is the entire difference between the two specs (section 9).

Because `second_troll_ready` is a conjunct of entry in **both** specs, the standing owner
rule — **no banana action before our second troll is trained, threshold zero, no
exemption** — is satisfied by construction: every farm action lives inside FARM, and FARM
is unreachable before the second troll exists. If the opening is abandoned (line 919, the
turn-35 deadline) the second troll never materializes, `second_troll_ready` never sets,
and the bot performs no banana action all game. (Pre-existing resident banana handling —
the regeneration PICK at lines 1178–1183, itself already guarded by an own-count ≥ 2
check at line 1177, and the endgame fruit-conversion at lines 1287–1301 — is unchanged
and out of scope; the owner rule binds the new farm.)

## 5. Shared skeleton — denial bonus follows the machine, never the live count

Today the bonus is re-computed every turn from the live opponent count (line 620). That
allows a silent re-enable: an opponent who reaches three trolls and then loses one would
switch denial back on. Both specs remove this:

- New latched flag `denial_enabled`, initially true, set **false permanently** when either
  (a) `enemy_third_troll` first sets, or (b) the machine enters WOOD.
- The gate at line 620 changes from `opponent_trolls <= 2` to `self.denial_enabled`
  (threaded down as a parameter, since `chop_candidates` is a static function).

While the enemy has never exceeded two trolls, `denial_enabled` equals the resident's live
gate, so behaviour is unchanged; the two differ only in never re-enabling. In Spec B the
moment `denial_enabled` latches off is the same moment DENY → FARM fires, reproducing the
CBF spec's "the gate becomes `state == DENY`" exactly. In Spec A the flag and the state
are decoupled: the trained troll goes on denying during FARM until the enemy scales or the
abort fires. The flag is part of the machine state; the acceptance gate GM (section 10)
checks it never returns to true.

## 6. Shared skeleton — the farm graft (identical in both specs)

The readable base has **no orchard code** (it was ablated), so the D89a mechanics come in
fresh. New code, and where it hooks in:

| New item | What it is | Hook point in the base file |
|---|---|---|
| `FarmState` enum + latches + abort fields | the machine of sections 3–5, 7 | new fields on `YamoBot` (line 335); updated at top of `commands()` (lines 1376–1379) |
| `farm_candidates()` | the starter's persistent farm task (below) | routed in the per-unit dispatch at lines 1394–1411, following the pattern of the existing commitment routing at lines 1396–1398 |
| Tracked-crop table | which live banana plants are ours (bank-sourced or replanted), incl. one protected reserve cell | reconciled from observed plants each turn, alongside `reconcile_regeneration_commitments` (line 1377); failed PICK/PLANT/HARVEST, death, opponent removal, or collision cannot invent progress, per the D89a blueprint's shared-safety rule |
| Reserve protection | the protected seed-reserve cell is excluded from both trolls' chop targets and from movement-conflict landing | filter candidates with `Target::Tree(reserve_cell)` after `chop_candidates`; pass the cell via the existing `resolve_move_conflicts_with_priority_and_forbidden` (line 726; plain wrappers at lines 720–725) |
| Trained-role filter (FARM only) | replace a resident-selected PICK/PLANT/HARVEST/MINE for the trained troll with its best wood/bank candidate, per the D89a trained-worker rule | applied to the trained troll's candidate list in the same dispatch loop (lines 1394–1411) |

**The starter's farm task** (D89a blueprint, restated): snapshot the initial banked-banana
count on turn one; on FARM entry, bootstrap — repeatedly travel to our shack, PICK one
banana, travel to an empty home-side cell (a walkable, plant-free cell at least as close
to our shack as to the enemy's, by the same `manhattan` used at line 621), and PLANT,
until the initial count is planted or the bank is empty. Rank and keep one protected
bank-sourced reserve (water adjacency, home accessibility, opponent distance,
deterministic cell order; promote a survivor if it is lost). When empty-handed, harvest a
ripe tracked own banana, reserve first; after a tracked harvest, carry the banana to the
nearest reachable empty conversion cell and PLANT; return to seed acquisition. Never DROP
renewable seed between farm actions. **Carrying wood, iron, or a non-banana fruit takes
precedence** and uses resident bank logistics (`bank_candidates`, lines 371–399;
`carried_fruit` at lines 1201–1202 distinguishes the payload).

**Routing, not score competition.** The farm is a task override for the starter, exactly
like the existing regeneration-commitment routing (lines 1396–1398): when the machine is
in FARM, the starter is not carrying a precedence payload, and no forced door-clear is
pending (the 20 000-scored overrides at lines 962, 987, 1059 stay above everything), the
starter's candidate set is `farm_candidates()`. Farm-internal scores order farm options
among themselves only and introduce no new constants into the resident's score ladder
(verified bands, for the reviewer's orientation: 20 000 forced door-clear, lines
962/987/1059; 10 000 endgame chop-in-place, line 1283; 9 000 endgame PLANT, line 1262;
8 000 drop-at-bank, line 383; 7 500 regeneration PICK, line 1180; 7 000 bank approach,
lines 386/394; base chop `1000*wood/turns` + 900 denial, lines 619–622). While in FARM
the farm task also outranks the endgame regeneration branch (`endgame()` at lines
1371–1373) **for the starter only**; the trained troll's endgame behaviour is unchanged.

## 7. Shared skeleton — abort sensor and frozen constants (identical in both specs)

**What is measured: banked-banana deltas.** On entering FARM, snapshot
`(turn, inventories[0][BANANA], inventories[1][BANANA])`. Both players' inventories are
parsed from the referee every turn (`read_turn`, lines 245–256, filling
`inventories: [Stock; 2]`, line 63) — no chop attribution or plant-lifecycle inference is
needed, which is the layer where Banana R2 (the six failed 2026 implementation rounds of
this idea) kept failing. Let `d_us` and `d_them` be each side's banked-banana increase
since the snapshot. **Abort (FARM → WOOD) when `d_them > d_us` has held for K consecutive
turns, and only after W turns in FARM.**

Why bananas and not score: bananas cost zero toward TRAIN (`docs/mechanics.md` line 91:
"BANANA and WOOD cost zero"), so the opponent has no training reason to farm bananas of
their own; a rise in their banked bananas is a sound proxy for harvesting from **our**
orchard — which is the owner's stated abort rule, expressed in directly observable
quantities. A farm that produces nothing also aborts (if `d_us` stays 0 and they collect
anything), which is intended. **Named alternative — total-score deltas:** snapshot
`view.scores` (computed at line 289 from `score()`, lines 120–121) and abort when their
score grows faster. It watches total outcome at identical implementation cost, and stays
on the shelf as the variant to try if the abort fires correctly but the tail does not
improve. Choosing between the two on evidence would need the theft-vs-own-production
decomposition that does not exist (section 2). Banked-banana deltas are primary per the
owner's wording and the CBF spec.

**Frozen constants** — chosen by reasoning, frozen before any run, **no tuning dials**
(the project's one permitted denial-weight sweep, N6, failed both arms; we do not sweep
our way out of a bad constant):

| Constant | Value | Justification |
|---|---:|---|
| `W` (warm-up turns in FARM before the abort may fire) | 30 | A banana planted at size 0 needs four growth steps at base cooldown 6 (line 85 of the base file: `PlantKind::Banana => 6`) plus one further cooldown to fruit; 30 turns is one "time to first banana". Aborting sooner would kill the farm before it could pay. |
| `K` (consecutive failing turns required) | 5 | Insurance against a single-turn spike; cheap, and the transition is one-way, so a spurious abort is unrecoverable within the game. |
| `T` (deficit threshold) | 0 | Strict inequality `d_them > d_us`. Warm-up and persistence carry the noise rejection; a third tunable would add surface without evidence. |

## 8. Shared skeleton — what differs between the specs (identical in both files)

Requirement 4 of the task record: one state machine, one farm, one abort; only the FARM
entry condition differs. Concretely, the two specs share every line of sections 3–8 and
differ in **exactly one predicate**:

| | FARM-entry predicate (evaluated on latches, section 4) |
|---|---|
| **Spec A** | `second_troll_ready` |
| **Spec B** | `second_troll_ready && enemy_third_troll` |

The spec-specific detail lives in each file's own section 9.

In code this is one function, e.g. `fn farm_entry(&self) -> bool`, whose body is the only
diff between the two built bots. Everything else — machine, latches, denial re-gating,
farm graft, trained-role filter, reserve protection, abort sensor, constants — is one
shared implementation compiled twice (or once with the predicate selected at build time;
implementation stage decides, not this spec).

## 9. Spec B specifics — the conditional ("if third troll") entry condition

**Entry: DENY → FARM fires on the first turn both latches of section 4 are set** — the
enemy has been observed fielding a third troll (`enemy_third_troll`, expression of
line 590, latched on first observation; the count later dropping back to two does not
revert it), and our second troll exists (`second_troll_ready`).

This is the CBF machine re-based. Notes on the re-basing and on the extra conjunct:

1. **The trigger expression survives unchanged.** The CBF spec cited the old compact
   file's `:1066`; in the readable base the same expression is line 590, inside
   `chop_candidates` — the machine evaluates its own copy on the full unit list each turn
   rather than reaching into that function.
2. **`second_troll_ready` is a new explicit conjunct.** The CBF spec left it implicit
   (the resident essentially always trains). Making it explicit costs nothing in the
   common case — an enemy third troll while we still have one troll is rare — and makes
   the owner's threshold-zero rule hold by construction even in opening-abandoned games
   (section 4). It is also what lets the two specs share the scaffold verbatim.
3. **Denial semantics are preserved exactly.** Because entry coincides with the
   `denial_enabled` latch-off event (section 5), Spec B reproduces CBF §3.0: the denial
   bonus is on if and only if the machine is in DENY, and `state == DENY` implies the
   enemy count has never exceeded two.

**Blast radius is bounded by construction** (the CBF argument, restated): if the enemy
never reaches three trolls, the machine never leaves DENY and the bot emits byte-identical
commands to the resident for the **whole game** (the section 5 latch and the live gate
agree everywhere on that population). The change can only act in games where the enemy has
already out-scaled us — the B3.1 catastrophe population. This is a testable invariant
(gate GB below), not an aspiration.

Known cost of conditional entry, inherited from CBF §9 and left standing: **a late farm
start may not compound.** D89a began at second-troll materialization; here FARM begins
when the enemy reaches three trolls, typically much later, and there may be too few turns
for the loop to establish. Gate GF measures this directly, and a failure to establish is a
real result — it is exactly the axis on which Spec A differs.

**OWNER-DECISION (B-1).** None specific to the entry predicate — the owner specified "if
third troll" directly. Flagged instead: whether Spec B should also require a minimum
number of turns remaining at entry (e.g., skip FARM if fewer than W + one harvest cycle
remain). The CBF spec had no such floor; this drafter recommends **no floor** (it would be
a new constant, i.e. a tuning dial, and a farm that cannot establish simply aborts by the
`d_us = 0` rule of section 7), but records the question rather than silently choosing.

## 10. Behavioural acceptance gates

Per the task record, and inheriting Banana R2's lesson: these are implementation-validity
gates; **every gate's test must first be observed failing** (on a stub or a deliberately
broken build) before its pass is credited; all of them precede any value panel.

| Gate | Statement | Measurement |
|---|---|---|
| GT — train | A second troll is trained | `TRAIN` issued (lines 1387–1389) and own unit count reaches 2. Resident already does this: a do-not-break gate. |
| GD — deny | One of lemon/plum is selected, frozen, and denied | `type_to_cut` set once (lines 796–799); focus-species chops occur while `denial_enabled`, preferentially near the enemy shack (bonus at line 622). Do-not-break. |
| GF — sustained farm cycle | FARM entered per this spec's predicate (and NOT entered when the enemy never fields a third troll); bootstrap plants ≥ 1 banked banana; at least one full harvest → replant cycle completes; the loop repeats while conditions hold | Telemetry per the D89a blueprint: every activation, bootstrap attempt/success, reserve promotion/loss, own-crop harvest, renewable replant, trained-role rewrite logged. Entry needs both arms too: games where it fires and games where it correctly does not. |
| GA+ — abort fires | In games where `d_them > d_us` persists ≥ K turns after warm-up, WOOD is entered | Constructed/replayed games on the development panel; sealed ranges stay closed. |
| GA− — abort does not misfire | In games where the condition never persists, WOOD is never entered | Both arms are mandatory: a rule that always fires is not conditional, and a rule that never fires is not a rule (the project's trigger-fidelity check). |
| GB — byte-identity before first transition | Emitted command lines are byte-identical to the resident for **entire games** in which the enemy never fields a third troll, and on every turn before FARM entry otherwise | Diff of full command transcripts. |
| GM — monotonicity | Over the whole test panel: no state transition ever reverses, and `denial_enabled` never returns to true after latching off | Assertions in the bot plus transcript audit. |

Boundary (unchanged from the CBF spec): behavioural gates deliver a *correctly built*
bot, never a *good* one. Passing GT–GM authorizes no Arena action; value comes only from
the measured stage below, and Arena submissions remain serialized through the single
arena controller under the standing rules in `docs/STATE.md`.

The value question this design exists to answer, when measurement comes: if the
conditioning and the abort work, **the tail improves** — p10 and worst-pair margins move
materially toward their old bars (−20 and −60) relative to D89a's −72 and −235 — without
giving back all of the +79.4 mean. A B that only matches A's tail has not earned its
restriction.

## 11. Implementation staging (stage 5 of the programme; out of scope here, recorded for review)

1. **Inert machine.** States, latches, predicate, denial re-gating — with FARM behaving
   as DENY (no farm actions). Must pass GB everywhere and GM; this proves the plumbing is
   inert before any behaviour changes.
2. **Farm graft.** Section 6 into FARM. GF. First report item: how many banked bananas
   remain at FARM entry (bank-exhaustion risk, carried over from CBF §9 — its old anchor
   `:1193`, the compact resident's shack-ring orchard spend, **has no equivalent in the
   readable base**: orchard code is ablated, and bananas leave the bank only via the
   regeneration/endgame paths at lines 1178–1183 and 1287–1301, so exposure is smaller
   here but still unmeasured; late entry makes the question sharper for B than for A).
3. **Abort.** Snapshot, warm-up, persistence, latch. GA+ and GA−, both arms.

Both specs are built as one code change with the predicate as the only fork (section 8).

## 12. Measurement plan stub (stage 6; owner gates every night)

Ladder noise σ (sigma — the measured standard deviation of a mature ladder run's score)
= 1.501 per the 2026-08-13 ruling. **One night = 8 mature runs = 4 per arm, interleaved
A/B/A/B** → uncertainty on the difference ≈ 1.501·√(¼+¼) ≈ 1.06 points → one night
cleanly resolves differences of ~2 points or more; a second night (8 per arm, SE ≈ 0.75)
usually settles closer calls.

**OWNER-DECISION (B-2, shared with Spec A).** Which comparison the first night buys —
Spec A vs Spec B, or winner vs resident — is the owner's call at the stage-6 go-ahead,
per the task record. This spec expresses no preference.

## 13. Out of scope, and known risks

Out of scope (task record): implementation, panels, candidates, Arena; repair of the D89a
leak (`NOT_REPAIRABLE` stands unappealed — bounded here, not fixed); any change to the
denial-bonus magnitude (N6 closed it: keep 900); denying the opponent's training bills
(H4 closed it). No formatter over `cgauto/`; the base file stays byte-exact.

Risks, carried over from CBF §9 and re-checked against the readable base:

- **The abort may watch a minor term — open question, not a finding.** The
  theft-vs-own-production split is UNRESOLVED; a farm could pass the banana test and
  still lose the way D89a lost. The score-delta sensor stays available as the named
  variant (section 7).
- **Late farm start may not compound** (section 9). GF answers it.
- **The proxy is not exact.** An opponent planting their own bananas inflates `d_them`
  and biases toward an early abort — the safe direction.
- **Bank exhaustion at late entry.** See stage 2 in section 11.

## 14. OWNER-DECISION register (this file)

| Id | Question | Drafter's recommendation |
|---|---|---|
| B-1 | Whether entry should carry a minimum-turns-remaining floor | No floor (section 9): it would add a tuning dial, and a non-establishing farm self-aborts |
| B-2 | First measurement night's pairing: A vs B, or winner vs resident | None — owner's call at stage-6 go-ahead |
