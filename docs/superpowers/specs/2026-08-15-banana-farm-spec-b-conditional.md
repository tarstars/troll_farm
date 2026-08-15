# Banana-farm bot — Spec B (conditional entry: "if third troll")

- Status: DRAFT v3 for codex_1 re-review, then owner approval
- Revision: v3 2026-08-15: rewritten to the owner five-decision rulings (session record:
  `coordination/tasks/20260815-banana-farm-two-specs.md`); v2 abort/entry superseded.
  Containment property preserved by ruling: Spec B = Spec A with only the third-troll
  doorway; S-1 and M-1 are ruled.
- Revision history: v2 2026-08-15: abort sensor reworked per codex_1 REVISION_REQUIRED
  review (`codex_1/reviews/banana-farm-two-specs-review-2026-08-15.md`); sensor choice
  elevated to OWNER-DECISION S-1; measurement decision rule added (M-1).
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
- **Futility tracker** — a simple per-turn count of the selected-species trees on the
  board; if the count refuses to fall for `K_futility` consecutive turns while we deny,
  denial is judged futile (section 4). Spec B computes it but does not consume it.
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

**What makes this Spec B:** the doorway out of DENY is the enemy's **third troll** alone
(latched on first observation) — the machine enters FARM only in games where we are
already out-scaled. Spec A adds the job-done and futility doorways, so it reaches FARM
in far more games. By the 2026-08-15 containment ruling, **Spec B = Spec A with only the
third-troll doorway**, so the A-vs-B measurement prices exactly the two new doorways.

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
catastrophes), and stop as soon as farming is more profitable for the enemy than for us
(the score-delta abort, section 7, ruled in S-1). Spec A opens the doorway wider — job
done and futility as well as the third troll — and so trades broader farm exposure for
more compounding time. Which trade is better is a measured question (section 12), not a
design argument.

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
  evaluated here every turn, and the futility counter advances only in this state.
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
| `futility_reached` | latch | the futility counter (below) reaches `K_futility`. Doorway 3 — the owner's "futility" stop: the enemy sustains the species against our chopping. |

Once set, a latch never clears (a count dropping back does not revert it).

**The futility tracker (the SIMPLE tracker of the 2026-08-15 ruling).** Each turn while
the machine is in DENY, count the visible selected-species trees:
`view.plants.iter().filter(|p| p.kind == focus).count()` with `focus = type_to_cut` (set
once, lines 796–799). **No ownership inference anywhere** — the count is over every plant
of the species on the board, whoever planted it. This is deliberate: the sensor asks "is
the species dying?", not "whose trees are these?", and ownership inference is exactly the
layer where Banana R2 rounds 1–6 failed. A per-turn counter starts at 0 on DENY entry,
increments when the count is greater than or equal to the previous DENY turn's count
(non-decreasing), and resets to 0 whenever the count decreases; comparisons begin on the
second DENY turn. `futility_reached` sets when the counter reaches `K_futility`. A zero
count sets `species_gone` instead (zero trees is job-done, not futility).

**`K_futility` = 10 turns — FROZEN** (proposed by the drafter under the no-tuning-dials
rule; the owner confirms or resets it at spec approval, before implementation; it is
never swept; it is distinct from the abort persistence `K` of section 7). Growth-cycle
justification: the selected species (lemon or plum) regrows on a base cooldown of 8 turns
(line 85: `PlantKind::Plum=>8, PlantKind::Lemon=>8`; water can shorten it —
`effective_cooldown`, lines 102–104), and our own chops take multiple turns to complete
(the `chop_turns` travel-and-chop arithmetic inside `chop_candidates`). Ten consecutive
non-decreasing turns therefore spans more than one full base growth cycle of the species
AND more than one in-flight chop, so it cannot be an artifact of watching inside a single
static growth interval, nor of one chop's latency: over at least one full cycle in which
we actively denied, the count still did not fall — the enemy is sustaining the species at
or above our chopping rate.

**The endgame-conversion blip.** The bot's sole PLANT site is line 1256 (inside the
endgame fruit-conversion branch; at-target score 9 000 at line 1262): a carried lemon or
plum is briefly planted next to our shack and then chopped for wood points. If the
carried fruit is the selected species, this adds one visible tree for a few turns. The
K-persistence absorbs the blip: the conversion chop removes the tree, the count
decreases, and the futility counter resets — a 10-turn non-decrease cannot be produced by
a plant-then-chop excursion lasting a few turns.

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
variant** — faithful to the literal per-farm rule, adopted only if measurement shows the
score-delta abort fires too often; it is not built now. The owner's supporting reading:
the abort phrase "more profitable for the enemy than for us" is an overall-profit
statement, so a total-outcome sensor implements the rule as the owner means it.

### The built sensor — score-delta

On entering FARM, snapshot `view.scores` — the `scores: [i32; 2]` field of `GameState`
(declared at line 64), filled every turn at line 289 as
`scores:[score(&inventories[0]),score(&inventories[1])]`, where `score()` (lines
120–121) sums the banked stock. Let `s_us` and `s_them` be each side's score increase
since the snapshot. **Abort (FARM → WOOD) when `s_them > s_us` (strict inequality,
T = 0) has held for K = 5 consecutive turns, and only after W = 30 turns in FARM.**

Honest characterization (unchanged from v2): provenance-free and a few lines of code,
but it watches the **total outcome**, not the farm — it aborts whenever we are being
outscored while farming, whether or not the opponent takes a single crop of ours. A
replanted harvest scores nothing until banked, so a working farm registers on `s_us`
only through the banked surplus of the section 6 cargo rule and the rest of the bot's
banking. Both distortions push the same way: toward aborting **too often**, the safe
direction for a one-way switch. The 2026-08-15 ruling accepts this substitution
explicitly; the adoption condition on the variant below is the counterweight.

### Named future variant — the provenance sensor (fully specified, NOT built now)

If measurement shows the score-delta abort fires too often (farms stopped that were not
actually being robbed), the replacement is this sensor, faithful to the owner's literal
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

## 9. Spec B specifics — the single third-troll doorway

**Entry: DENY → FARM fires on the first turn `enemy_third_troll` is set while the
machine is in DENY** — the enemy has been observed fielding a third troll (expression of
line 590, latched on first observation; the count later dropping back to two does not
revert it). If the latch set during COLLECT (enemy third troll before our second), entry
fires as soon as DENY is reached — the section 4 edge case. Latched; nothing can undo it.

The other two section 4 doorway signals (`species_gone`, `futility_reached`) are
**computed but not consumed** in this build: **Spec B = Spec A with only the third-troll
doorway** (the 2026-08-15 containment ruling), so the A-vs-B measurement prices exactly
the two new doorways — job done and futility. Under Spec B, denial that has become
finished or futile simply continues until the enemy scales or the game ends; that is the
design's cost and the comparison's point.

This is the CBF machine re-based. Notes on the re-basing:

1. **The trigger expression survives unchanged.** The CBF spec cited the old compact
   file's `:1066`; in the readable base the same expression is line 590, inside
   `chop_candidates` — the machine evaluates its own copy on the full unit list each turn
   rather than reaching into that function.
2. **The second-troll requirement is now structural, twice over.** The CBF spec left it
   implicit (the resident essentially always trains). In the owner's machine, FARM sits
   after DENY and DENY sits after training (section 4), so the threshold-zero rule holds
   by construction even in opening-abandoned games.
3. **Denial semantics are preserved exactly.** Because entry coincides with the
   `denial_enabled` latch-off event (section 5), Spec B reproduces CBF §3.0: the denial
   bonus is on if and only if the machine is in COLLECT or DENY, and `state == DENY`
   implies the enemy count has never exceeded two.

**Blast radius is bounded by construction** (the CBF argument, restated): if the enemy
never reaches three trolls, the machine never leaves DENY and the bot emits
byte-identical commands to the resident for the **whole game** (with no third troll there
is also no drop-back, so the section 5 latch and the live gate agree everywhere on that
population). The change can only act in games where the enemy has already out-scaled us —
the B3.1 catastrophe population. This is a testable invariant (gate GB below), not an
aspiration.

Known cost of conditional entry, inherited from CBF §9 and left standing: **a late farm
start may not compound.** D89a began at second-troll materialization; here FARM begins
when the enemy reaches three trolls, typically much later, and there may be too few turns
for the loop to establish. Gate GF measures this directly, and a failure to establish is a
real result — it is exactly the axis on which Spec A differs.

**OWNER-DECISION (B-1) — OPEN.** None specific to the entry predicate — the owner
specified "if third troll" directly. Flagged instead: whether Spec B should also require
a minimum number of turns remaining at entry (e.g., skip FARM if fewer than W + one
harvest cycle remain). The CBF spec had no such floor; this drafter recommends **no
floor** (it would be a new constant, i.e. a tuning dial; under the score-delta abort of
section 7 a farm that cannot establish self-aborts — our score stalls while theirs grows;
gate GF measures late non-establishment directly, which the review concurs is the right
instrument), but records the question rather than silently choosing.

## 10. Behavioural acceptance gates

Per the task record, and inheriting Banana R2's lesson: these are implementation-validity
gates; **every gate's test must first be observed failing** (on a stub or a deliberately
broken build) before its pass is credited; all of them precede any value panel.

| Gate | Statement | Measurement |
|---|---|---|
| GT — train | A second troll is trained | `TRAIN` issued (lines 1387–1389) and own unit count reaches 2. Resident already does this: a do-not-break gate. |
| GD — deny | One of lemon/plum is selected, frozen, and denied | `type_to_cut` set once (lines 796–799); focus-species chops occur while `denial_enabled`, preferentially near the enemy shack (bonus at line 622). Do-not-break. |
| GE — doorway fidelity | The third-troll doorway fires in games where the enemy fields a third troll (and our second exists), and does NOT fire where the enemy never does; the unconsumed signals (`species_gone`, `futility_reached`) provably never cause a transition | Constructed/replayed games; doorway and futility-tracker telemetry logged every DENY turn. |
| GF — sustained farm cycle | FARM entered per this spec's predicate (and NOT entered when the enemy never fields a third troll); bootstrap plants ≥ 1 banked banana; at least one full harvest → replant cycle completes; the loop repeats while conditions hold | Telemetry per the D89a blueprint: every activation, bootstrap attempt/success, reserve promotion/loss, own-crop harvest, renewable replant, trained-role rewrite logged. Entry needs both arms too: games where it fires and games where it correctly does not. |
| GA+ — abort fires | In games where the score-delta abort condition persists ≥ K turns after warm-up, WOOD is entered | Constructed/replayed games on the development panel; sealed ranges stay closed. |
| GA− — abort does not misfire | In games where the condition never persists, WOOD is never entered | Both arms are mandatory: a rule that always fires is not conditional, and a rule that never fires is not a rule (the project's trigger-fidelity check). |
| GB — byte-identity before first transition | Emitted command lines are byte-identical to the resident for **entire games** in which the enemy never fields a third troll, and on every turn before the first transition out of DENY fires otherwise (the sole permitted pre-doorway divergence is the COLLECT-phase no-re-enable caveat of section 5(a)) | Diff of full command transcripts. |
| GM — monotonicity | Over the whole test panel: no state transition ever reverses, `denial_enabled` never returns to true after latching off, and no doorway latch ever clears (the futility *counter* may reset; the `futility_reached` latch may not) | Assertions in the bot plus transcript audit. |

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

1. **Inert machine.** States, latches, doorway signals and futility tracker
   (telemetry-only), denial re-gating — with FARM behaving as DENY (no farm actions).
   Must pass GB everywhere, GE on telemetry, and GM; this proves the plumbing is inert
   before any behaviour changes.
2. **Farm graft.** Section 6 into FARM. GF. First report item: how many banked bananas
   remain at FARM entry (bank-exhaustion risk, carried over from CBF §9 — its old anchor
   `:1193`, the compact resident's shack-ring orchard spend, **has no equivalent in the
   readable base**: orchard code is ablated, and bananas leave the bank only via the
   regeneration/endgame paths at lines 1178–1183 and 1287–1301, so exposure is smaller
   here but still unmeasured; late entry makes the question sharper for B than for A).
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
  comparison — which prices exactly the two new doorways — runs only if A earns it;
  Spec B is measured only in that case.

## 13. Out of scope, and known risks

Out of scope (task record): implementation, panels, candidates, Arena; repair of the D89a
leak (`NOT_REPAIRABLE` stands unappealed — bounded here, not fixed); any change to the
denial-bonus magnitude (N6 closed it: keep 900); denying the opponent's training bills
(H4 closed it). No formatter over `cgauto/`; the base file stays byte-exact. Whether
denial should continue against a three-troll enemy is an explicit LATER experiment
(2026-08-15 ruling), not part of this spec.

Risks, carried over from CBF §9 and re-checked against the readable base:

- **The abort watches the total outcome, not the farm** (the S-1 ruling's accepted
  substitution, section 7): it errs toward early abort — the safe direction for a
  one-way switch; the cost is farms stopped that were not actually being robbed. The
  provenance variant is the specified answer if measurement shows this.
- **Denial can continue past usefulness.** Without the job-done and futility doorways,
  Spec B keeps denying a finished or futile species until the enemy scales. That is the
  price of the narrow doorway; the A-vs-B comparison prices it.
- **Late farm start may not compound** (section 9). GF answers it.
- **Bank exhaustion at late entry.** See stage 2 in section 11.

## 14. OWNER-DECISION register (this file)

| Id | Question | Status |
|---|---|---|
| B-1 | Whether entry should carry a minimum-turns-remaining floor | OPEN (section 9); drafter recommends no floor: it would add a tuning dial, and a non-establishing farm self-aborts under the score-delta sensor |
| B-2 | First measurement night's pairing | RULED 2026-08-15: Spec A vs current resident; Spec B runs only if A earns the A-vs-B comparison (section 12) |
| S-1 (shared with Spec A) | Abort sensor | RULED 2026-08-15: score-delta built; provenance fully specified as the named future variant (section 7) |
| M-1 (shared with Spec A) | Measurement decision rule | RULED 2026-08-15: paired-CI protocol of section 12 |
