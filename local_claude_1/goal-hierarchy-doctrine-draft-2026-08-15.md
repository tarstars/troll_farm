# Goal-hierarchy doctrine — DRAFT for owner correction

- v2 2026-08-15: revised per codex_1 review (oscillation-d2-d3-review-2026-08-15.md) and
  claude_1 P-2 feasibility response; v1 findings corrected in place.
- Status: **DRAFT — the OWNER owns this document.** Agents drafted it from code; the owner
  corrects and freezes it. After freezing, every "what should the trolls have done?" ruling in
  the oscillation deep-dive (`coordination/tasks/20260815-oscillation-deep-dive.md`, D3) must
  cite numbered principles from this page (C-, N-, T-numbers below).
- Subject: the current resident bot, file
  `cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs` (content hash `98628e98…`).
  "R:n" below means line n of that file; every line was re-verified 2026-08-15 in this worktree.
- Owner's definition of "ideal": *consider the situation, carefully justify the hierarchy of
  goals the trolls have at this moment, optimize the whole picture.*

## Part 1 — The hierarchy the CODE actually has (descriptive, highest score first)

**Structural layer FIRST — scores alone do not determine behavior.** Order of authority each
turn: (1) per-unit ROUTING picks which candidate generator even runs — endgame vs main vs early
path (R:1393-1411) — and generators can return early (a loaded troll gets only banking options,
R:1170-1187; carried-fruit conversion returns before chops are priced, R:1271-1279); (2) FORCED
REPLACEMENT — door clearing overwrites whole candidate lists with forced moves/DROPs (R:978,
applied R:1429-1430); (3) scoring + pair selection by sum (R:683, R:1432); (4) the move-conflict
RESOLVER can rewrite the selected commands after scoring (R:1433). A ruling that cites only a
C-number without its structural gate misattributes behavior to the ladder.

The bot picks actions by numeric score; bigger wins. The bands, in plain words:

- **C1. Unblock (20,000).** A forced sidestep move (R:962) or a forced DROP — put down carried
  goods — by a troll blocking the shack door (R:987, R:1059) beats everything.
- **C2. Endgame finish-the-chop (10,000).** CONDITIONAL, not global: exists only inside the
  endgame candidate path (`endgame_candidates` R:1233, reached via routing R:1191/1398/1404),
  for an empty-handed troll already able to CHOP where it stands — then the chop is overwritten
  to 10,000 and all other options are discarded (R:1282-1286).
- **C3. Endgame conversion planting (9,000 / 8,000−distance).** Also endgame-path only, and not
  generic "regeneration": planting a CARRIED fruit (troll must hold one, R:1239) on an empty
  square, feasibility-guarded — travel + plant + chop-back + return must fit in the turns left
  (R:1250). 9,000 on the target square, else 8,000 minus distance (R:1262, R:1265) — the same
  intention is worth 1,000 more just for already standing there.
- **C4. Bank, i.e. deliver goods home (8,000 / 7,000−travel).** 8,000 on the drop square, else
  7,000 minus travel turns (R:383, R:386); fallback "walk to our shack" is flat 7,000 (R:394).
- **C5. PICK a fruit for replanting (7,500−priority)** under a five-condition guard (R:1180).
- **C6. Conversion PICK — clock-split (endgame path too).** Same intention priced two ways:
  after turn 250 it is 7,000−priority (R:1292) or 6,000−priority−travel (R:1324); before, only
  750/(turns+3)−… (R:1295, R:1327). One tick moves it across four bands.
- **C7. Work (≈6,000–7,000) — two DIFFERENT walking formulas.** MINE iron: 6,100+900 = 7,000
  when adjacent (R:448, R:489); walking toward iron subtracts RAW map distance, not turns
  (R:501). HARVEST fruit: 6,000+900 = 6,900 on the tree (R:455, R:467); walking subtracts travel
  TURNS (distance ÷ speed) plus ripening wait (R:476-479). A fast troll is charged less to reach
  fruit but the same as a slow one to reach iron.
- **C8. Clear-the-shack-for-training move: 6,500** (R:1422).
- **C9. CHOP wood: 1000·wood/turns, plus denial bonus 900/(1+opponent-distance)** (R:619, R:622).
  Upper bound 2,400 — ASSUMPTION-DEPENDENT, not a proved attainable maximum: it assumes the
  shipped carry cap of 3 and permits opponent-distance 0, whose legal reachability is unproved
  (≥ 1 gives 1,950). The usable conclusion stands: under the shipped preset a normal chop can
  never outbid C7 (`claude_1/banana-restoration-r2/score-hierarchy-audit-method-2026-08-10.md`, S2.3).

Two more structural facts: the compatibility check waves through any troll whose target is
"None", i.e. no target (R:643-646) — so an idle troll constrains nobody and nobody constrains
it — and idle-harvest is only admitted when every candidate has no target (R:1413).

## Part 2 — PROPOSED normative hierarchy (what the trolls SHOULD value; owner to correct)

Each item is [PROPOSED — owner to confirm / correct / delete].

- **N1. Never block a working troll.** An idle or lower-value troll must yield the square/path a
  working troll needs, before its own preferences count. (Bears on the idle-blocker and door
  situations in the frozen library.)
- **N2. Plan value must not depend on the square the troll happens to stand on.** The worth of
  "replant here" or "finish this chop" is the same one step away; position may break ties only.
  (Directly contradicts C2's overwrite and C3's 9,000-vs-8,000 gap — the suspected oscillation fuel.)
- **N3. Never trade the same two squares back and forth.** Repeating a position with no change in
  goods, trees, or goal is always worse than committing to either square's plan.
- **N4. Income before denial when they compete.** Wood/fruit into our shack outranks making the
  opponent's life harder; denial (C9's +900 term) is a tie-breaker, not a goal. [Owner may invert.]
- **N5. Finish started work.** A chop or delivery already underway outranks switching to a plan of
  similar value; switching must clear a real threshold, not win by 1 point.
- **N6. When in doubt, act.** A productive move beats waiting. [Or the reverse — owner to rule;
  the code currently leans "act" only in endgame idle-harvest, R:1413.]
- **N7. The pair is the unit of optimization.** Judge the two trolls' joint plan (the code already
  sums, R:683), but a sum must never license one troll wrecking the other's path (see N1).
- **N8. Unblocking and rule-forced moves stay absolute** (keep C1 on top).

## Part 3 — Known tensions the owner must arbitrate

- **T1. Denial vs income** (C9's two terms; N4). How much wood is one denied opponent-lemon worth?
- **T2. Position-dependent pricing vs stability** (C2, C3 vs N2). Removing the standing bonus may
  reintroduce dithering; keeping it feeds oscillation. Which risk do we prefer?
- **T3. Endgame override vs the normal bands** (C2, C6). The turn-250 cliff moves one intention
  across four bands in one tick — intended design or accident?
- **T4. Sub-score sums crossing band boundaries** (owner's manifest point 6,
  `docs/MANIFEST-score-transparency-2026-08-09.md`). Audit verdict so far: zero arithmetic
  crossings among the ten known findings, but the global question is UNRESOLVED (method packet S4.4).
- **T5. Movement safety vs shortest path.** No score today prices "this path crosses a busy
  square"; only the pair-compatibility check does, and it ignores idle trolls (R:643-646).

Scale, for calibration only (do not re-litigate here): oscillation in 40/220 games, worst run
133 turns (`docs/CONSTRAINTS.md`, "Legend-era" entry ~981-1010); the closed fix was worth +0.045
while oscillating games ran ~13.6 below par — the open D6 mystery (task file, deliverable D6).
