# Goal-hierarchy doctrine — DRAFT for owner correction

- Status: **DRAFT — the OWNER owns this document.** Agents drafted it from code; the owner
  corrects and freezes it. After freezing, every "what should the trolls have done here?"
  ruling in the oscillation deep-dive (task `coordination/tasks/20260815-oscillation-deep-dive.md`,
  deliverable D3) must cite numbered principles from this page (C-, N-, T-numbers below).
- Subject: the current resident bot, file
  `cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs` (content hash `98628e98…`).
  "R:n" below means line n of that file; every line was re-verified 2026-08-15 in this worktree.
- Owner's definition of "ideal": *consider the situation, carefully justify the hierarchy of
  goals the trolls have at this moment, optimize the whole picture.*

## Part 1 — The hierarchy the CODE actually has (descriptive, highest score first)

The bot picks actions by numeric score; bigger wins. The bands, in plain words:

- **C1. Unblock (20,000).** A forced sidestep move (R:962) or a forced DROP — put down carried
  goods — by a troll blocking the shack door (R:987, R:1059) beats everything.
- **C2. Endgame finish-the-chop (10,000).** If a troll is already standing on the tree it should
  cut, the chop is overwritten to 10,000 and all other options are discarded (R:1282-1286).
- **C3. Stand-and-replant (9,000 / 8,000−distance).** Regeneration move: 9,000 if already on the
  target square, else 8,000 minus distance (R:1262, R:1265). Note: the same intention is worth
  1,000 more just for already standing there.
- **C4. Bank, i.e. deliver goods home (8,000 / 7,000−travel).** 8,000 on the drop square, else
  7,000 minus travel turns (R:383, R:386); fallback "walk to our shack" is flat 7,000 (R:394).
- **C5. PICK a fruit for replanting (7,500−priority)** under a five-condition guard (R:1180).
- **C6. Conversion PICK — clock-split.** Same intention priced two ways: after turn 250 it is
  7,000−priority (R:1292) or 6,000−priority−travel (R:1324); before, only 750/(turns+3)−… (R:1295,
  R:1327). One tick moves it across four bands.
- **C7. Work (≈6,000–7,000).** MINE iron: 6,100+900 = 7,000 (R:448, R:489). HARVEST fruit:
  6,000+900 = 6,900 (R:455, R:467); walking toward these costs turns off the base (R:479, R:501).
- **C8. Clear-the-shack-for-training move: 6,500** (R:1422).
- **C9. CHOP wood: 1000·wood/turns, plus denial bonus 900/(1+opponent-distance)** (R:619, R:622).
  Proved ceiling 2,400 — a chop can never outbid C7 (audit method packet,
  `claude_1/banana-restoration-r2/score-hierarchy-audit-method-2026-08-10.md`, S2.3).

Two structural facts, not scores: pairs of trolls are chosen by the SUM of two scores (R:683), and
the compatibility check waves through any troll whose target is "None", i.e. no target (R:643-646)
— so an idle troll constrains nobody and nobody constrains it. Idle-harvest is only admitted when
every candidate has no target (R:1413).

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

Known scale of the problem, for calibration only (do not re-litigate here): oscillation occurred in
40/220 games, worst run 133 turns (`docs/CONSTRAINTS.md`, "Legend-era" oscillation entry ~981-1010);
score value of the closed fix was +0.045 while oscillating games ran ~13.6 below par — the open D6
mystery (task file, deliverable D6).
