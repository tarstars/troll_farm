# Banana-farm bot — Spec A (the owner's denial-preserving state machine)

- Status: DRAFT v10 — the five owner rulings unchanged; v10 closes codex_1's v9
  evidence-contract blockers. For codex_1 re-review, then the owner's final
  confirmation.
- Revision: v10 2026-08-17: census frozen as a SET of specific tree generations
  (new enemy trees cannot pay an old quota; member loss by other causes ends the
  round without a verdict); the panel backstop gains its second arm (zero de-novo
  D-1 AND P4); the suppression log follows the unit until commitment resolution or
  phase/game exit.
- Revision: v9 2026-08-17: the C1/C2/C3 corner analysis written in (two PICK sites,
  scores, routing); owner rules corners rare — suppression events logged with context,
  the 240-game panel's zero-de-novo-oscillation gate is the backstop, prevention
  machinery deferred to an owner decision IF logs show occurrences.
- Revision: v8 2026-08-17: owner ruling — PLANT suppressed while the machine is in
  DENY (sole site :1256; code-verified reachable only in a bare-board/late corner);
  the v6–v7 census-exclusion machinery (exclusion tracker, census-eligibility) is
  DELETED as unnecessary; gate GB gains the second named exception; GK's exclusion
  arm replaced by the suppression twins.
- Revision: v7 2026-08-17: round progress counts CENSUS-ELIGIBLE completions only
  (a chop of an excluded own tree advances nothing; the constructed
  census-1/own-tree must-not-fire case added to gate GK); the exclusion tracker
  receives its own built-now generation contract instead of leaning on section 7's
  future-variant table.
- Revision: v6 2026-08-17: futility mechanism replaced by the OWNER'S SEQUENCE DESIGN
  (census → chop that many → recount; stall or rise stops denial); `K_futility`
  RETIRED; the v4–v5 completion gate SUBSUMED (its confirmation rule survives as the
  round-progress element); own-plant census exclusion closes the conversion blip;
  gates GE/GK re-bound.
- Revision: v5 2026-08-17: per codex_1's v4 review — the completion gate gains its
  operational definition (confirmation rule, fail-closed ambiguity, fixed ordering
  against tracker reset; gate GK bound to it) and is entered in the OWNER-DECISION
  register as a new decision.
- Revision: v4 2026-08-17: abort-sensor characterization corrected to BOTH failure
  directions (wood masking via `WOOD_POINTS = 4`, line 82) with per-event score
  decomposition reporting; `K_futility` relabelled a heuristic, its in-flight span
  claim withdrawn, the completion gate added, and gate GK introduced — per
  `codex_1/reviews/banana-farm-two-specs-v3-review-2026-08-16.md`.
- Revision: v3 2026-08-15: rewritten to the owner five-decision rulings (session record:
  `coordination/tasks/20260815-banana-farm-two-specs.md`); v2 abort/entry superseded.
  Spec A is REDEFINED: the v2 "unconditional at second-troll materialization" entry is
  demoted to collection candidate Spec A0 (appendix, section 15); S-1 and M-1 are ruled.
- Revision history: v2 2026-08-15: abort sensor reworked per codex_1 REVISION_REQUIRED
  review (`codex_1/reviews/banana-farm-two-specs-review-2026-08-15.md`); sensor choice
  elevated to OWNER-DECISION S-1; measurement decision rule added (M-1).
- Author: `local_claude_1` (drafted by subagent under its direction)
- Date: 2026-08-15
- Task record: `coordination/tasks/20260815-banana-farm-two-specs.md` (stage 4 of
  `docs/PROGRAMME-banana-farm-2026-08-15.md`)
- Companion: Spec B, `docs/superpowers/specs/2026-08-15-banana-farm-spec-b-conditional.md`.
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
- Prior conditional design being re-based: the CBF spec (CBF = "conditional banana farm",
  the 2026-08-07 design), `docs/superpowers/specs/2026-08-07-conditional-banana-farm-design.md`.
  Its state machine, sensors, and frozen constants are reused here; its line references
  targeted the old compact resident and are all replaced below.

## 1. What this bot does, in the owner's words

Both specs implement the owner's state machine, decided on 2026-08-15 (it supersedes,
where it differs, the one-line sequence recorded earlier in the task record):

> COLLECT → (own second troll trained) → DENY → **doorway** → FARM → (score-delta abort)
> → WOOD — all transitions latched one-way.

The **doorway** — the condition that ends denial and starts the farm — is the only thing
that differs between the two specs (section 8).

Plain-language glossary for this document (owner rule: every code name explained at first
use; the recurring ones are gathered here):

- **Troll / unit** — one of our workers on the board. We start with one and can TRAIN
  (buy) a second.
- **Shack** — each player's home building. **Bank / inventory** — the stock of items
  stored at the shack; the referee sends both players' inventories every turn.
- **Denial** — chopping the fruit species the opponent needs, close to their shack, so
  they cannot pay for extra trolls.
- **Focus species** — the one species (lemon or plum) chosen for denial, picked once at
  game start and never changed. Also called the "selected species".
- **Doorway** — a condition that ends denial and opens the way to farming. The owner's
  doorways are denial's STOP conditions: the enemy out-scales us, the job is done, or
  the work is futile.
- **Futility tracker** — the owner's census sequence (RULED 2026-08-17): count the
  selected-species trees, chop that many down, recount; a recount that fails to fall
  below the previous census judges denial futile (section 4).
- **Banana farm** — planting banked bananas, harvesting them when ripe, and replanting
  each harvest, so bananas compound into score (each banked banana is one point:
  `score()` at lines 120–121 counts `inventory[3]`, and `BANANA` is item index 3,
  line 14).
- **Abort** — a one-way switch to plain aggressive wood-chopping if farming turns out
  more profitable for the enemy than for us.
- **Latched** — a switch that can only ever be flipped once, in one direction. It cannot
  un-flip, so the bot can never oscillate (flip back and forth) between behaviours.
- **Byte-identical** — the new bot's printed commands are exactly, character for
  character, what the resident would have printed.

**What makes this Spec A:** the doorway out of DENY is the owner's full composite —
enemy third troll OR zero selected-species trees left OR a completed chopping round
that fails to lower the census (futility — mechanism re-ruled 2026-08-17, section 4). Denial is preserved in full until one of those
fires. Spec B keeps only the third-troll doorway.

## 2. Prior art and what this design is built against

D89a (2026-07-21) proved the farm mechanism works: activation 256/256, 1,344 bank bananas
planted, a sustained harvest-and-replant loop in 252/256 games, mean paired margin
**+79.441** (CI [+40.991, +117.892]). It was rejected on tail risk: worst pair −235,
p10 margin −72, and the opponent's own score rose +82.863. Whether that opponent gain came
from stealing our crops or from their own production is **UNRESOLVED** (the once-quoted
+12.5/+76.5 split was prose, not measurement — see the correction in §2 of the CBF spec).
The D89a leak carries a standing `NOT_REPAIRABLE` verdict; per the task record it is
**bounded by design here, not repaired**: the abort (section 7) stops the farm when
farming is more profitable for the enemy than for us.

What changed in v3: the v2 Spec A copied D89a's shape — farm from second-troll
materialization, overlapping denial. The owner read that as "throw out denial, plant
bananas instead" and demoted it to collection candidate **Spec A0** (section 15). Denial
is suspected **load-bearing** for rating (supported: N6's weak-denial arm lost −0.754, on
both seats) and is preserved in full until a doorway fires. The two new doorways —
job done (species eliminated) and futility (the enemy sustains the species against our
chopping) — are the owner's denial stop conditions, stated in writing for the first time
in the 2026-08-15 ruling. Spec B additionally restricts the doorway to the third troll
alone; which trade is better is a measured question (section 12), not a design argument.

## 3. Shared skeleton — the state machine (identical in both specs)

One persistent machine on the bot. Four states, three transitions, all latched — the
owner's 2026-08-15 machine. There is no path back and no skipped edge: DENY is reachable
only from COLLECT, FARM only from DENY, WOOD only from FARM.

```
COLLECT ──(own second troll observed; identical in both specs)────────────► DENY
DENY ──(doorway predicate; THE ONLY LINE THAT DIFFERS BETWEEN SPECS)──────► FARM
FARM ──(score-delta abort trips; identical in both specs)─────────────────► WOOD
```

- **COLLECT** — the resident's behaviour, unmodified: gathering, training the second
  troll, selecting the focus species. Honesty note: the resident already applies the
  denial chop bonus from turn one under its live gate, so denial is not literally "after"
  training; the COLLECT → DENY edge changes no behaviour — it exists to scope the doorway
  sensors, which begin counting only in DENY. Resident anchors:
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
- **DENY** — still the resident's behaviour, unmodified except the denial-bonus re-gating
  of section 5. What is new is observation: the doorway signals of section 4 are
  evaluated here every turn, and the futility tracker runs only in this state.
- **FARM** — denial has ended (the doorways are its stop conditions): the starter runs
  the grafted D89a farm task (section 6); the trained troll runs the resident
  wood/logistics behaviour with the denial bonus off. In the owner's framing, FARM
  replaces the aggressive-chopping fallback that today follows denial.
- **WOOD** — aggressive all-out chopping: no denial bonus, no farm actions, both trolls on
  the resident's plain wood policy. This is the abort target, reached only from FARM.

State and latches are new fields on the `YamoBot` struct (field list at line 335). The
machine is updated once per turn at the top of `commands()` (lines 1375–1441), next to the
existing per-turn housekeeping calls at lines 1377–1379.

**Why latched:** an A → B → A loop is unrepresentable by construction — this is the whole
anti-oscillation argument and it is structural, not tuned. Oscillation is closed in
`docs/CONSTRAINTS.md`; we get the property for free and claim no value for it. The owner
accepted latching's cost with open eyes on 2026-08-15: the machine may leave denial
incomplete (a doorway can fire while the species survives) — "I'm ready to take this
risk."

## 4. Shared skeleton — entry latch, doorway signals, and the futility tracker (identical in both specs)

| Signal | Kind | Definition (base-file anchors) |
|---|---|---|
| `second_troll_ready` | latch | our unit count reaches 2: `view.units.iter().filter(\|u\|u.player==0).count() >= 2` — same filter as line 401. Fires COLLECT → DENY. |
| `enemy_third_troll` | latch | opponent unit count exceeds 2: `view.units.iter().filter(\|u\|u.player==1).count() > 2` — same expression as line 590. Doorway 1. |
| `species_gone` | latch | the visible selected-species tree count (tracker below) is zero, observed while in DENY. Doorway 2 — the owner's "job done" stop: the species is eliminated from the board. |
| `futility_reached` | latch | a completed chopping round fails to lower the census (tracker below). Doorway 3 — the owner's "futility" stop: the enemy sustains the species against our chopping. |

Once set, a latch never clears (a count dropping back does not revert it).

**The futility tracker — THE OWNER'S SEQUENCE DESIGN (RULED 2026-08-17, superseding
the 2026-08-15 turn-counter and the v4–v5 completion gate, which it absorbs).** The
owner's statement of the rule: *"at select denial target we counted amount of trees
to chop. We chopped them. Then we again measure amount of target trees. We chopped
down this amount. We track this sequence of numbers. If it stalls (we have two equal
numbers in this sequence) or rises at some point — we stop denial."*

Mechanism, in the bot's terms — no per-turn window and **no `K_futility` constant
(retired by the same ruling; the clock is completed work, not turns)**:

- **Census.** On DENY entry record the census as the SET of specific standing
  selected-species trees — cell plus generation identity (v10, per codex_1's v9
  review) — and `C_0` = its size. No ownership exclusions are needed: planting is
  FORBIDDEN during DENY (owner ruling below), so no tree of ours can appear while
  censuses run. A focus tree our bot planted BEFORE DENY entry (degenerate pre-DENY
  endgame states only) counts as an ordinary census member — accepted: extra members
  make futility HARDER to reach, the conservative side.
- **Round.** A round completes when our confirmed completions of **CENSUS-MEMBER
  trees** reach `C_i` (v10: the quota is payable only by the trees that were counted
  — an enemy tree planted after the census cannot pay an old quota; it appears in
  the recount instead, which is where it belongs). If census members vanish through
  anything OTHER than our confirmed completions (enemy action, decay), the quota can
  no longer be met by us: when the last member is gone, re-census and start a fresh
  round WITHOUT a stall/rise comparison — the owner's verdict reads "against our
  chopping", and that round was not finished by our chopping. If the live count
  reaches 0 at any point, `species_gone` sets instead — zero trees is job-done, not
  futility.
- **Verdict.** At each round completion take the next census `C_{i+1}` and append it
  to the sequence. **`futility_reached` sets iff `C_{i+1} >= C_i`** — the owner's
  stall ("two equal numbers") or rise: we removed a full census of trees and the
  species stands as tall as before, so the enemy is sustaining it against our
  chopping, proven by a completed generation of work.
- **No completed round — no verdict.** A round that cannot complete (unreachable
  trees, trolls needed elsewhere) never fires futility, however many turns pass:
  erring toward CONTINUING denial, the conservative side (denial is suspected
  load-bearing, N6), with the other doorways still providing exits.

**No planting during DENY — OWNER RULING 2026-08-17 (v8).** While the machine is in
DENY, the endgame planner's sole `PLANT` candidate (readable resident :1256, the only
planting site in the bot) is SUPPRESSED. Code-verified basis: that site is reachable
during DENY only through the conversion pipeline, whose entry points are the two PICK
sites (main planner :1177, score 7500, needs turn ≥ 100 AND board ≤ 2 plants while
winning; endgame planner :1287, score 7000 after turn 250 / ~83 before, reachable
when losing on a ≤ 4-plant board or any time after turn 250) — the three corners
C1/C2/C3 of the 2026-08-17 session analysis. The ruling turns "the bot cannot plant
during denial" from a circumstance into an enforced invariant and DELETES the v6–v7
census-exclusion machinery whole. This is the SECOND named exception to gate GB
(byte-identity during DENY).

**Log-and-defer — OWNER RULING 2026-08-17 (v9, same session).** The suppressed
pipeline can strand a committed troll (walk-to-plant with the plant refused → a
manufactured dance between adjacent cells at scores 8000−distance, or all-WAIT at 0 —
the very pathologies of the standing-troll track). The owner judges the C1/C2/C3
corners RARE and rules: **no prevention machinery is built now** (no PICK
suppression, no commitment clearing). Instead: (a) every suppression event is LOGGED
with its full context — turn, board plant count, score sign, banked fruits, the
suppressed command — and the unit's per-turn branch / candidate summary / commitment
state / emitted command are logged FROM the event UNTIL its commitment resolves or
the phase or game exits (v10, per codex_1's v9 review — a fixed five-command window
cannot adjudicate a strand); (b) the implementation's mandatory 240-game acceptance
panel is the empirical backstop with BOTH arms: a manufactured dance surfaces as
de-novo D-1, a stranded parked troll as a de-novo P4 liveness violation — the panel
gate is ZERO de-novo D-1 AND ZERO de-novo P4 (the P4 arm confirmed by claude_1's
T-1 stage-1b measurement, not assumed); (c) the
interaction RETURNS TO THE OWNER if the logs show real occurrences. The integrator's
"C3 is common" claim is recorded as a mechanism argument to be tested by exactly this
log, not assumed.

**Completion confirmation (unchanged from v5 — now the round-progress element):**
evaluated by the same reconciliation pass as section 7, on (previous turn's
`GameState`, the commands we emitted, this turn's `GameState`): a focus-chop
completion is confirmed iff our unit emitted `CHOP` at cell C, the plant at C in the
PREVIOUS state was focus-species with `health <=` that unit's `chop_power` (removal
guaranteed by our own hit, referee-deterministic), and no live focus plant of that
generation stands at C in THIS state. **Ambiguity fails closed to NO EVENT** (health
above our power and the plant vanished anyway → not attributed to us; the round does
not advance) — futility stays harder to reach, the same conservative direction.

Properties inherited and improved from the retired designs: the "troll still
walking" misfire is impossible BY CONSTRUCTION (no completed round → no census → no
comparison); the evidence per verdict is a full completed generation of chopping,
strictly stronger than the v4–v5 single-completion gate; and the tuning constant is
gone.

Because `second_troll_ready` is the only edge out of COLLECT and every doorway sits at
the far side of DENY, the standing owner rule — **no banana action before our second
troll is trained, threshold zero, no exemption** — is now doubly structural: FARM sits
after DENY, and DENY sits after training. If the opening is abandoned (line 919, the
turn-35 deadline) the second troll never materializes, the machine stays in COLLECT for
the whole game, and the bot performs no banana action at all. (Pre-existing resident
banana handling — the regeneration PICK at lines 1178–1183, itself already guarded by an
own-count ≥ 2 check at line 1177, and the endgame fruit-conversion at lines 1287–1301 —
is unchanged and out of scope; the owner rule binds the new farm.)

Edge case, stated for the record: `enemy_third_troll` can set while the machine is still
in COLLECT (an enemy third troll before our second). The latch holds; when our second
troll appears the machine steps COLLECT → DENY, and with the doorway predicate already
true, DENY → FARM fires on the next evaluation — DENY can be a single-turn state. The
second-troll rule still holds: FARM remains unreachable before our second troll exists.

## 5. Shared skeleton — denial bonus follows the machine, never the live count (identical in both specs)

Today the bonus is re-computed every turn from the live opponent count (line 620). That
allows a silent re-enable: an opponent who reaches three trolls and then loses one would
switch denial back on. Both specs remove this:

- New latched flag `denial_enabled`, initially true, set **false permanently** when
  either (a) `enemy_third_troll` first sets, or (b) the machine leaves DENY — in this
  machine the doorways ARE the denial stop conditions, so denial ends exactly at
  DENY → FARM (entering WOOD is downstream and already covered).
- The gate at line 620 changes from `opponent_trolls <= 2` to `self.denial_enabled`
  (threaded down as a parameter, since `chop_candidates` is a static function).

While the machine is in COLLECT or DENY and the enemy has never exceeded two trolls,
`denial_enabled` equals the resident's live gate, so behaviour is unchanged. The
divergences are exactly two, both deliberate: (a) **no silent re-enable** — an enemy that
reaches three trolls and then drops back to two does not switch denial back on (in DENY
this coincides with the doorway firing; in COLLECT it is a real, rare divergence from the
resident, flagged in gate GB's wording); (b) in Spec A, a `species_gone` or
`futility_reached` doorway turns the bonus off while the enemy still fields ≤ 2 trolls —
that is the point of those doorways, and it coincides with the machine's first transition
out of DENY. The flag is part of the machine state; the acceptance gate GM (section 10)
checks it never returns to true.

## 6. Shared skeleton — the farm graft (identical in both specs)

The readable base has **no orchard code** (it was ablated), so the D89a mechanics come in
fresh. New code, and where it hooks in:

| New item | What it is | Hook point in the base file |
|---|---|---|
| `FarmState` enum + latches + abort fields | the machine of sections 3–5, 7 | new fields on `YamoBot` (line 335); updated at top of `commands()` (lines 1376–1379) |
| `farm_candidates()` | the starter's persistent farm task (below) | routed in the per-unit dispatch at lines 1394–1411, following the pattern of the existing commitment routing at lines 1396–1398 |
| Tracked-crop table | which live banana plants are ours (bank-sourced or replanted), incl. one protected reserve cell — ownership per the transactional contract in section 7: a tracked crop is ours iff created by our own confirmed PLANT and not since removed or replaced; ambiguity fails closed to NOT-ours | reconciled from observed plants each turn, alongside `reconcile_regeneration_commitments` (line 1377); failed PICK/PLANT/HARVEST, death, opponent removal, or collision cannot invent progress, per the D89a blueprint's shared-safety rule |
| Reserve protection | the protected seed-reserve cell is excluded from both trolls' chop targets and from movement-conflict landing | filter candidates with `Target::Tree(reserve_cell)` after `chop_candidates`; pass the cell via the existing `resolve_move_conflicts_with_priority_and_forbidden` (line 726; plain wrappers at lines 720–725) |
| Trained-role filter (FARM only) | replace a resident-selected PICK/PLANT/HARVEST/MINE for the trained troll with its best wood/bank candidate, per the D89a trained-worker rule | applied to the trained troll's candidate list in the same dispatch loop (lines 1394–1411) |

**The starter's farm task** (D89a blueprint, restated): snapshot the initial banked-banana
count on turn one; on FARM entry, bootstrap — repeatedly travel to our shack, PICK one
banana, travel to an empty home-side cell (a walkable, plant-free cell at least as close
to our shack as to the enemy's, by the same `manhattan` used at line 621), and PLANT,
until the initial count is planted or the bank is empty. Rank and keep one protected
bank-sourced reserve (water adjacency, home accessibility, opponent distance,
deterministic cell order; promote a survivor if it is lost). When empty-handed, harvest a
ripe tracked own banana, reserve first. A harvest can yield more than one banana (harvest
power; cargo up to carry capacity — review finding F3), so the post-harvest loop is
specified for every banana carry count 1..capacity: travel to the nearest reachable empty
conversion cell and PLANT exactly one; if banana cargo remains, bank it at our shack via
resident bank logistics; then return to seed acquisition. One PLANT keeps the renewable
generation in the ground; banking the surplus terminates the loop at every carry count
and makes farm output visible in the bank and score. Never DROP renewable seed between
farm actions (banking surplus is banking, not dropping). **Carrying wood, iron, or a
non-banana fruit takes precedence** and uses resident bank logistics (`bank_candidates`, lines 371–399;
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

## 7. Shared skeleton — the abort sensor (S-1 RULED: score-delta) and frozen constants (identical in both specs)

**Sensor history, kept for the record.** The v1 draft froze banked-banana deltas —
snapshot `(turn, inventories[0][BANANA], inventories[1][BANANA])` on FARM entry, abort
when `d_them > d_us` persists — and called that "a sound proxy for harvesting from our
orchard". codex_1's review (finding F1,
`codex_1/reviews/banana-farm-two-specs-review-2026-08-15.md`) showed the proxy wrong in
both directions, with the defect inherited from CBF §4: our farm loop HARVESTs and
re-PLANTs, so collection from our own farm need not raise our bank at all; the opponent
can harvest and bank bananas from **its own** plants ("no training reason to farm
bananas" — `docs/mechanics.md` line 91 — is not "no scoring reason": every banked banana
is a point, `score()`, lines 120–121); and a cumulative bank comparison mixes each side's
pre-existing independent production into the farm window. Banked-banana deltas are
**withdrawn**. The observability facts that frame every sensor: the referee sends both
inventories every turn (`read_turn`, lines 245–256, filling `inventories: [Stock; 2]`,
line 63), every unit with player, cell, cargo, and stats including `harvest_power`
(`Unit`, lines 47–48; `Stats`, line 40; parsed at line 282), and the full plant list —
but a `Plant` carries only kind, cell, size, health, fruits, cooldown (lines 58–59),
**no owner field**. The owner's literal rule — abort when the enemy collects more **from
our farm** than we do — therefore has no free observable: ownership must be inferred
(the provenance sensor below) or given up for a coarser observable (the score-delta
sensor).

**S-1 RULED 2026-08-15: both-in-collection.** The score-delta sensor is **THE built
abort of both specs**. The provenance sensor stays **fully specified as the named future
variant** — faithful to the literal per-farm rule, adopted only if measurement shows
either of its failure modes material (v4: false aborts OR wood-masked robbery); it is
not built now. The owner's supporting reading:
the abort phrase "more profitable for the enemy than for us" is an overall-profit
statement, so a total-outcome sensor implements the rule as the owner means it.

### The built sensor — score-delta

On entering FARM, snapshot `view.scores` — the `scores: [i32; 2]` field of `GameState`
(declared at line 64), filled every turn at line 289 as
`scores:[score(&inventories[0]),score(&inventories[1])]`, where `score()` (lines
120–121) sums the banked stock. Let `s_us` and `s_them` be each side's score increase
since the snapshot. **Abort (FARM → WOOD) when `s_them > s_us` (strict inequality,
T = 0) has held for K = 5 consecutive turns, and only after W = 30 turns in FARM.**

Honest characterization — REVISED v4 per codex_1's v3 review (the v2/v3 claim that
"both distortions push the same way: toward aborting too often, the safe direction"
was FALSE and is withdrawn): the sensor watches the **total outcome**, not the farm,
and it fails in BOTH directions.

- **Fires too often (false abort):** it aborts whenever we are being outscored while
  farming, whether or not the opponent takes a single crop of ours; and a replanted
  harvest scores nothing until banked, so a working farm registers on `s_us` only
  through the banked surplus of the section 6 cargo rule and the rest of the bot's
  banking.
- **Fires too late or never (masked robbery):** `score()` (lines 120–121) sums ALL
  banked stock, and wood banks at `WOOD_POINTS = 4` per unit (line 82) against 1 per
  banana. Our trained troll's wood production therefore feeds `s_us` at four points a
  bank and can mask the opponent's banana gain — including gain taken from our own
  farm — keeping `s_us >= s_them` while the farm is being robbed. The abort then
  fires late or never.

Neither direction is "safe"; the sensor is a frozen heuristic with both failure modes
accepted for now by the S-1 ruling. **Measurement must report both** (M-1 nights and
the development panel alike): every abort event is logged with the decomposition of
each side's score growth since FARM entry into wood and non-wood components, and
every FARM phase that ends without an abort logs the same decomposition at exit — so
false-abort candidates and masked-robbery candidates are both inspectable per game.
The 2026-08-15 ruling's substitution stands; the adoption condition on the variant
below is the counterweight.

### Named future variant — the provenance sensor (fully specified, NOT built now)

If measurement shows either failure mode material — false aborts (farms stopped that
were not being robbed) or masked robbery (wood-fed score keeping the abort silent while
the farm is drained) — the replacement is this sensor, faithful to the owner's literal
per-farm rule. Two cumulative counters, both 0 at FARM entry. `farm_us` counts confirmed
harvest events **by us** from tracked-ours crops; `farm_them` counts inferred
enemy-collection events from tracked-ours crops (both per event, not per banana, so the
section 6 cargo rule does not skew the comparison). **Abort (FARM → WOOD) when
`farm_them > farm_us` has held for K consecutive turns, and only after W turns in FARM**
— the same frozen constants as the built sensor.

The counters require a **transactional ownership contract** on the section 6
tracked-crop table. Contract: **a tracked cell's crop is ours iff it was created by our
own confirmed PLANT command and has not since been removed or replaced.** The only
writer is the reconciliation pass at the top of `commands()` (alongside line 1377),
running each turn on (previous turn's `GameState`, the commands we emitted, this turn's
`GameState`). Transitions:

- **Plant.** We emitted PLANT at a cell last turn, a size-0 banana plant stands there
  now, and our unit's banana cargo dropped by one → a new tracked-ours entry with a
  generation identity (cell, confirmation turn, last observed size/fruits/cooldown).
  Anything else — no plant, wrong kind, wrong size — is a failed PLANT: no entry.
- **Grow.** An observation consistent with the tracked plant's own growth updates the
  identity and keeps ownership.
- **Replace.** Any inconsistent observation — size reset, kind change, or a plant
  present after the tracked plant was observed absent — means the crop at that cell is a
  **different generation, NOT ours** (the opponent can plant on the same cell): the
  entry is removed, and only our own confirmed PLANT can re-establish it.
- **Harvest (ours).** We emitted HARVEST at a tracked cell; its fruits dropped and our
  unit's banana cargo rose accordingly → one `farm_us` event.
- **Chop (ours).** Our confirmed CHOP removed a tracked plant → entry removed, no event.
- **Disappear.** A tracked plant is absent with no command of ours explaining it. If it
  bore fruit and at least one enemy unit with `harvest_power >= 1` was in reach of the
  cell across the transition → one `farm_them` event; entry removed. Otherwise (health
  death, no capable enemy nearby, or any ambiguity about the cause) → entry removed, no
  event.
- **Ambiguity fails closed to NOT-ours.** An untracked crop is never harvested by the
  farm task and never feeds `farm_us`; uncertainty shrinks our side of the comparison
  and the farm itself, biasing toward abort — the safe direction for a one-way switch.
  Reserve promotion (section 6) may promote only a tracked-ours crop, so an opponent
  replacement at a lost reserve cell can never inherit protection (review F2).

Honest observability limits: enemy HARVEST is never observed as an event —
"fruit-bearing tracked plant vanished with a capable enemy in reach" is an inference,
and the referee gives no way to distinguish it from edge cases the inference mislabels.
This layer — command confirmation plus plant-lifecycle diffing — is exactly where Banana
R2 rounds 1–6 failed. This variant is the only sensor that measures the owner's literal
rule; it is also the only one that depends on the layer with the six-failure history —
which is why it is the future variant, not the built abort.

**Frozen constants** — chosen by reasoning, frozen before any run, **no tuning dials**
(the project's one permitted denial-weight sweep, N6, failed both arms; we do not sweep
our way out of a bad constant). They govern the built score-delta sensor and carry over
unchanged if the provenance variant is ever adopted:

| Constant | Value | Justification |
|---|---:|---|
| `W` (warm-up turns in FARM before the abort may fire) | 30 | A banana planted at size 0 needs four growth steps at base cooldown 6 (line 85 of the base file: `PlantKind::Banana => 6`) plus one further cooldown to fruit; 30 turns is one "time to first banana". The farm cannot have moved `s_us` before then (and under the provenance variant, no `farm_us` event can exist before the first crop ripens). Aborting sooner would kill the farm before it could pay. |
| `K` (consecutive failing turns required) | 5 | Insurance against a single-turn spike; cheap, and the transition is one-way, so a spurious abort is unrecoverable within the game. It rides out score bursts such as an opponent banking a large cargo at once (and under the provenance variant it also spans the one-to-two-turn lag of event inference). |
| `T` (deficit threshold) | 0 | Strict inequality on the sensor's pair (`s_them > s_us`; `farm_them > farm_us` for the variant). Warm-up and persistence carry the noise rejection; a third tunable would add surface without evidence. |

## 8. Shared skeleton — what differs between the specs (identical in both files)

Requirement 4 of the task record: one state machine, one farm, one abort; only the FARM
entry condition differs. The 2026-08-15 ruling adds the containment property to
preserve: **Spec B = Spec A with only the third-troll doorway**, so the A-vs-B
measurement prices exactly the two new doorways. Concretely, the two specs share every
line of sections 3–8 and differ in **exactly one predicate** — the DENY → FARM doorway:

| | Doorway predicate (DENY → FARM, evaluated on the section 4 signals) |
|---|---|
| **Spec A** | `enemy_third_troll \|\| species_gone \|\| futility_reached` |
| **Spec B** | `enemy_third_troll` |

The spec-specific discussion lives in each file's own section 9.

In code this is one function, e.g. `fn doorway(&self) -> bool`, whose body is the only
diff between the two built bots. Everything else — machine, latches, futility tracker
(computed in both builds; consumed by the doorway only in Spec A), denial re-gating,
farm graft, trained-role filter, reserve protection, abort sensor, constants — is one
shared implementation compiled twice (or once with the predicate selected at build time;
implementation stage decides, not this spec).

## 9. Spec A specifics — the composite doorway (the owner's denial-preserving machine)

**Entry: DENY → FARM fires on the first turn any of the three section 4 doorway signals
is set**, latched; nothing can undo it:

1. **`enemy_third_troll`** — the enemy fields a third troll. Kept in the composite for
   now by explicit ruling; whether denial should continue against a three-troll enemy is
   an explicit LATER experiment, not this one.
2. **`species_gone`** — job done: zero selected-species trees left visible on the board.
3. **`futility_reached`** — futility: a completed chopping round failed to lower the
   census (the owner's sequence design, RULED 2026-08-17; tracker in section 4).

Why this is Spec A (the 2026-08-15 redefinition): the previously drafted entry — farm at
second-troll materialization, overlapping denial — read to the owner as "throw out
denial, plant bananas instead", a bad bot by expectation, and is demoted to collection
candidate **Spec A0** (appendix, section 15). Denial is suspected load-bearing for
rating (N6's weak arm lost −0.754, both seats) and is preserved in full until one of the
owner's stop conditions says it is finished (job done), not working (futility), or
overtaken (enemy scaling). The doorways are the owner's denial STOP conditions, stated
in writing for the first time; FARM replaces the aggressive-chopping fallback that today
follows denial. The owner's second-troll rule holds doubly structurally (section 4).

Accepted risk, recorded verbatim in the task record: the state-machine reading means we
may leave denial incomplete — futility can fire while the species survives. Owner: "I'm
ready to take this risk."

**Blast radius of Spec A** (honest statement, contrast with B): in most games one of the
three doorways eventually fires — the enemy scales, the species runs out, or the count
stalls — so Spec A is *not* protected by a rarely-true predicate; its tail bound is the
abort. Byte-identity with the resident holds on every turn before the first transition
out of DENY fires (with the single COLLECT-phase no-re-enable caveat of section 5(a)),
and for whole games where the opening is abandoned and the machine never leaves COLLECT.

## 10. Behavioural acceptance gates

Per the task record, and inheriting Banana R2's lesson: these are implementation-validity
gates; **every gate's test must first be observed failing** (on a stub or a deliberately
broken build) before its pass is credited; all of them precede any value panel.

| Gate | Statement | Measurement |
|---|---|---|
| GT — train | A second troll is trained | `TRAIN` issued (lines 1387–1389) and own unit count reaches 2. Resident already does this: a do-not-break gate. |
| GD — deny | One of lemon/plum is selected, frozen, and denied | `type_to_cut` set once (lines 796–799); focus-species chops occur while `denial_enabled`, preferentially near the enemy shack (bonus at line 622). Do-not-break. |
| GE — doorway fidelity | Each of the three doorways fires in constructed games where its condition holds, and does NOT fire where it does not (the conversion-blip hazard is closed structurally by the section 4 PLANT suppression; its tests live in GK's suppression twins) | Constructed/replayed games; futility-tracker telemetry (census sequence, round progress) logged every DENY turn. |
| GK — futility sequence twins (v6) | The unfinishable-round case CANNOT fire futility: a distant/unreachable focus tree keeps the round incomplete, no enemy planting → `futility_reached` never sets, however many turns pass. Positive twin: a completed round (a full census of confirmed completions) with enemy replanting keeping the recount ≥ the previous census → it sets. Suppression twins (v8): a constructed bare-board DENY state where the RESIDENT would emit PLANT → the machine bot emits none while DENY holds; after a doorway fires, PLANT resumes. | Constructed games per the section 4 sequence tracker and its confirmation rule (completions: removal with `health <= chop_power`); both arms observed, fail-first per the standing rule. |
| GF — sustained farm cycle | FARM entered on the first doorway firing and never before; bootstrap plants ≥ 1 banked banana; at least one full harvest → replant cycle completes; the loop repeats while conditions hold | Telemetry per the D89a blueprint: every activation, bootstrap attempt/success, reserve promotion/loss, own-crop harvest, renewable replant, trained-role rewrite logged. |
| GA+ — abort fires | In games where the score-delta abort condition persists ≥ K turns after warm-up, WOOD is entered | Constructed/replayed games on the development panel; sealed ranges stay closed. |
| GA− — abort does not misfire | In games where the condition never persists, WOOD is never entered | Both arms are mandatory: a rule that always fires is not conditional, and a rule that never fires is not a rule (the project's trigger-fidelity check). |
| GB — byte-identity before first transition | Emitted command lines are byte-identical to the resident on every turn before the first transition out of DENY fires (the two permitted pre-doorway divergences: the COLLECT-phase no-re-enable caveat of section 5(a), and the DENY-phase PLANT suppression of section 4 — owner ruling 2026-08-17), and for whole opening-abandoned games | Diff of full command transcripts. |
| GM — monotonicity | Over the whole test panel: no state transition ever reverses, `denial_enabled` never returns to true after latching off, and no doorway latch ever clears (census rounds restart freely; the `futility_reached` latch may not clear) | Assertions in the bot plus transcript audit. |

Boundary (unchanged from the CBF spec): behavioural gates deliver a *correctly built*
bot, never a *good* one. Passing GT–GM authorizes no Arena action; value comes only from
the measured stage below, and Arena submissions remain serialized through the single
arena controller under the standing rules in `docs/STATE.md`.

## 11. Implementation staging (stage 5 of the programme; out of scope here, recorded for review)

1. **Inert machine.** States, latches, doorway signals and futility tracker
   (telemetry-only), denial re-gating — with FARM behaving as DENY (no farm actions).
   Must pass GB everywhere, GE on telemetry, and GM; this proves the plumbing is inert
   before any behaviour changes.
2. **Farm graft.** Section 6 into FARM. GF. First report item: how many banked bananas
   remain at FARM entry (bank-exhaustion risk, carried over from CBF §9 — note the
   readable base spends bananas only via the regeneration/endgame paths at lines
   1178–1183 and 1287–1301, so exposure differs from the old resident).
3. **Abort.** Snapshot, warm-up, persistence, latch. GA+ and GA−, both arms.

Both specs are built as one code change with the predicate as the only fork (section 8).

## 12. Measurement plan (stage 6; M-1 RULED 2026-08-15; owner gates every night)

Ladder noise σ (sigma — the measured standard deviation of a mature ladder run's score)
= 1.501 per the 2026-08-13 ruling. The protocol below was RULED by the owner on
2026-08-15 (M-1); the owner still authorizes each night separately, and no campaign runs
before the oscillation gate (programme stage 3) and spec approval.

- **Procedure:** interleaved A B A B A B A B A B — ten submissions alternating arms, one
  submission per ~2 h (a mature 160-game read settles in ~2 h, measured 2026-08-12); one
  block ≈ 20 h and yields n = 5 adjacent A/B pairs.
- **Verdict object:** the 95% confidence interval of the PAIRED difference. Each
  adjacent A/B pair gives one difference d_i; Δ (delta) is the mean of the d_i. Because
  the two members of a pair run back-to-back, slow ladder drift cancels within pairs.
  **Never two separate per-bot intervals.**
- **Decision rule, n-independent:** winner declared when |Δ| ≥ 1.96·SE(Δ), with
  SE(Δ) = 1.501·√(2/n) (SE — the expected noise on the estimate). At n = 5 the bar is
  ≈ 1.9 points; pooled n = 10, ≈ 1.3.
- **Materiality floor:** |Δ| < 1.0 → stop, verdict "immaterial". The floor is fixed in
  points by design — it is the project's standing value bar, not a statistical bound,
  and it does not shrink as n grows.
- **Neither:** extend one block on the same pairing and re-apply the rule to the pooled
  Δ. **Maximum two extensions** (three blocks, 30 runs, n = 15, SE ≈ 0.55, bar ≈ 1.07
  points); after that the materiality floor forces the stop.
- **Honesty clause:** the campaign reports its own empirical paired-difference spread
  beside the planning σ = 1.501; gross disagreement raises a "re-measure σ" flag — never
  a license to choose the flattering number.
- **Night-1 pairing (RULED): Spec A vs the current resident** (`98628e98…`). The A-vs-B
  comparison — which prices exactly the two new doorways — runs only if A earns it.

## 13. Out of scope, and known risks

Out of scope (task record): implementation, panels, candidates, Arena; repair of the D89a
leak (`NOT_REPAIRABLE` stands unappealed — bounded here, not fixed); any change to the
denial-bonus magnitude (N6 closed it: keep 900); denying the opponent's training bills
(H4 closed it). No formatter over `cgauto/`; the base file stays byte-exact. Whether
denial should continue against a three-troll enemy is an explicit LATER experiment
(2026-08-15 ruling), not part of this spec.

Risks specific to A, beyond the shared ones:

- **The tail bound is still only the abort.** In most games some doorway eventually
  fires and the machine enters FARM, so Spec A re-exposes D89a's catastrophic tail
  (worst pair −235) in a large fraction of games and relies on the W=30/K=5 score-delta
  abort to cut it. If the abort is too slow for the worst cells, A reproduces the tail;
  that outcome is a real, informative result, not a spec defect.
- **Denial may end incomplete.** Futility or enemy scaling can end denial while the
  species survives — the owner's explicitly accepted risk. GE/GF telemetry reports
  which doorway fired and the surviving selected-species count at the transition, so
  the cost is observable.
- **FARM carries no denial at all** (unlike the demoted A0, where the trained troll
  kept denying). If denial was still buying rating at the moment the doorway fires,
  that value is given up; the night-1 pairing (A vs resident, section 12) prices
  exactly this trade.

## 14. OWNER-DECISION register (this file)

| Id | Question | Status |
|---|---|---|
| A-1 | v2's entry-anchor question (second-troll materialization vs a "denial visibly happened" marker) | RESOLVED 2026-08-15 by redefinition: entry is the composite doorway; the old materialization entry is demoted to Spec A0 (section 15) |
| A-2 | First measurement night's pairing | RULED 2026-08-15: Spec A vs current resident (section 12) |
| S-1 (shared with Spec B) | Abort sensor | RULED 2026-08-15: score-delta built; provenance fully specified as the named future variant (section 7) |
| M-1 (shared with Spec B) | Measurement decision rule | RULED 2026-08-15: paired-CI protocol of section 12 |
| — | `K_futility` (section 4) | RULED 2026-08-17: RETIRED — the owner's census-sequence design has no turn constant. (The same session's provisional "16" answer is superseded by this same ruling.) |
| — (shared with Spec B) | The v4–v5 completion gate | RULED 2026-08-17: SUBSUMED by the owner's census-sequence design; its confirmation rule survives as the round-progress element (section 4) |
| — (shared with Spec B) | May the bot plant during DENY? | RULED 2026-08-17: FORBIDDEN — the sole PLANT site is suppressed while the machine is in DENY; the census-exclusion machinery is deleted as unnecessary (section 4) |
| — (shared with Spec B) | Prevention machinery for the suppression corners (C1/C2/C3)? | RULED 2026-08-17: NOT BUILT — corners judged rare; suppression events logged with context; the acceptance panel's de-novo-oscillation gate is the backstop; returns to the owner if logs show occurrences (section 4, v9) |

## 15. Appendix — Spec A0, the demoted collection candidate (not built)

Kept on paper by owner instruction 2026-08-15; owner expectation: **poor** ("it sounds
like a bad bot"); may be measured someday; no gate, no schedule.

**Spec A0 is the v2 Spec A entry:** DENY → FARM fires on the first turn our second troll
is observed on the board (materialization — D89a's proven activation point,
`second_troll_ready` alone as the doorway), and **denial overlaps the farm**: the
starter farms while the trained troll keeps the denial bonus until the enemy fields a
third troll or the abort fires. Everything else — the farm graft (section 6), the
score-delta abort (section 7), WOOD — is as in this spec. Its arguments were D89a
fidelity (activation 256/256, mean paired margin +79.441) and maximum compounding time;
its defect, in the owner's reading, is that it effectively abandons denial as the game's
backbone the moment the second troll exists, while denial is suspected load-bearing for
rating (N6's weak-denial arm: −0.754, both seats). Measuring A0 someday requires only
the alternate doorway predicate `second_troll_ready` plus re-enabling the FARM-state
denial overlap; nothing else in the shared skeleton changes.
