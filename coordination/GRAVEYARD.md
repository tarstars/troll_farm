# GRAVEYARD — one paragraph per dead task (created 2026-08-26)

Format: **what it was · what killed it · what we learned · what would reopen it.** A dead task is
closed, not "in progress"; this file is the library the graveyard was missing. Older closures live
in `docs/CONSTRAINTS.md` (the register); from 2026-08-26 every kill lands here first.

- **2026-09-02 — Track P, the port of norxondor_gorgonax** (`20260902-norxondor-port`; closed 15:26Z by the
  coordinator's fallback seat, the paperwork landed 17:3xZ). **What it was:** the second-placed player's
  rule-based economy — the exact train ladder to five trolls with harvest talents, the fruit-first orchard,
  the plant-and-cut banana wood loop, the produce→deforest switch — rebuilt as a hybrid over our champion's
  own pathing, targeting and denial; designed, reviewed (one round, four edits, two per reviewer), built
  (v2, sha `411b0565…`) and reproduced byte for byte in one day. **What killed it:** rung 1, the field
  reading against four local opponents paired by map and seat — 16 wins of 400 against the champion,
  Δwin −0.42 [−0.45, −0.39] over 1,600 games, below all four; rung 2, 15 paired games against the five
  real Legend agents on the same seeds — champion 8 wins, port 0, 118 points a game to 172, wood 26 to
  42; the loss read (112,919 recorded scores replayed, all exact) named one mechanism, the
  Produce→Deforest switch (the port banks 9.45 fruit and no wood in turns 1–50 while the champion banks
  8.71 wood; a fruit is one point, a wood four; 30 points down by turn 50, 55 by turn 100; the third troll
  arrives at turn 74 and farms until turn 144); the one pre-registered repair (v3.1: Produce ends the turn
  after the third troll, not the fifth) read **worse** — 10 wins of 400, Δwin −0.47 [−0.50, −0.44], below
  v2 by 0.046 [0.031, 0.061], the fourth troll gone, the turn-100 deficit moved from 55.0 to 52.4 points.
  The card's third dead condition. **What we learned:** this economy is not viable against an opponent
  that converts the map to wood from turn 1 — the lead is made before turn 100, in the phase no switch
  rule reaches (the champion has banked 34.9 points of wood by turn 50 against the port's 0.3), and a
  bigger roster arriving on an emptied board cannot buy it back; a duel with our own clear-cutter is not a
  ladder proxy (orchard 6 loses 324 of 400 to the champion and read above it on the ladder the same day),
  so a selector must be a field reading paired by map and seat; two reviewers found disjoint holes in one
  design, keep both halves of a round; a build's test module is part of the build (v3 shipped with tests
  asserting the old cap and was caught by the byte-identity reproduction). **What would reopen it:** a
  real ladder field that rewards a fruit-first opening — none is known. The narrower successor the
  endgame read and the loss read both point at — our champion plus a cheaply funded third troll — is a
  new card on the owner's word, not a reopening. Instruments kept: `claude_1/h2h-panel/` (the field
  panel, `field.py`, the bed), codex_1's loss-read analyzer (`codex_1/norxondor-port/loss_read.py`), the
  switch-turn trace, the rung-2 burst driver (`cgauto/field_panel.py`).

- **2026-08-26 — Candidate 0, the champion's replant fallback fix** (`20260826-candidate-0-regeneration-fallback`).
  One-hunk change: when a troll's idle-regeneration plan has no chops, extend the command list
  instead of replacing it. Killed at G-1, reproduced by codex_1: blocking games 118/240 vs 43/240 —
  the surviving 7,500-point regeneration `PICK` beats every job for an empty-handed troll next to
  the shack, the bank clause offers `DROP` next turn, nothing links `PICK` to `PLANT`: a PICK↔DROP
  two-cycle. Learned: the regeneration value is real (+530 own-score points across the panel) but
  only a *plan-keeping* successor can capture it; also, the "−75 on m061" was Candidate 2's cost,
  not the champion's. Reopens only as Candidate 3's plan-keeping case (`PICK` and `PLANT` share
  `Target::Cell(c)`), tested on `m061` at G-2.

- **2026-08-25 — Candidate 1, the resolver hold** (`cure1`). A hold in the resolver against the
  dance; fired 253× on 160 real games, kept every bound, and appeared in **0 of 25** recorded
  dances — real dances are permanent-block dances, not transient ones. Learned: the library's
  idle-blocker fixture shape is 0 of 80 in real games; measure on real games before building.
  Reopens: never in this form; the code is kept.

- **2026-08-25 — Candidate 2, the swap, as a qualified cure** (`cure2`). Panel dances 27→13, 16
  controls pass, but the pre-committed stops fired: the goals stay with the cells, so the two
  trolls swap and swap back (the loop, C-5 = 5), −5/game. Learned: a swap needs goals that travel
  with the troll — that is Candidate 3. Reopens: on top of Candidate 3, only if Candidate 3's
  panel shows an own-score gain (owner bound 08-26).

- **2026-08-26 — Candidate 3, the fixed-margin form** ("keep unless a challenger is clearly
  better by `M`"). Falsified, not mis-tuned: on the six loop games the challenger's advantage
  rises monotonically as the shared tree nears completion (0.02 → 0.27), so no constant `M`
  proves "no second exchange". Learned: a margin cannot bound a quantity that grows with the
  loop's length. Replaced by the absolute-keep form (same task, still alive).

- **2026-08-26 — Candidate 3, "a troll keeps its goal" (absolute form)** (`20260826-candidate-3-keep-your-goal`).
  A troll keeps its chosen goal until done (a tree: chopped there and carry full), gone, impossible
  or dead; when two kept goals cannot be paired the younger is released (contested release);
  telemetry v6. Built and measured in one day under the owner's bound. **What it did:** the loop it
  was built to remove is gone (`xc = 0` on all six loop games; blocking games 52 → 40; D-1 27 → 23;
  containment perfect, 0 telemetry errors over 48,000 turns). **What killed it:** its own
  pre-registered risk gate — **−65 own-score points over 240 games** (`m061` −47/−43, D-9 24 → 28)
  and a goal kept **171 turns** against a 30-turn stop; the packet says "the absolute form is too
  strong" and forbids repairing it with a margin. **Learned:** goals that travel with the troll do
  cure the swap loop, so the *mechanism* is right; a keep with no release for "a better tree is
  now beside me" is a keep that outlives its usefulness — the release list, not the keep, is the
  design problem. Also: a rule that is inert on `>= 3` units and never made a partner wait (`xp`,
  `xg`, `xw` all 0) is cheaper than feared on those axes. **Would reopen it:** a *bounded* keep —
  release on a strictly-better adjacent goal or a turn cap — as a new candidate with its own
  card, only if a top-10 read (Track T) says goal stability is something the strong bots have.
  Diff kept on `main`: `readable/diffs/candidate-3-keep-your-goal.diff`; packet
  `claude_1/cure3/g1-packet-2026-08-26.md`; codex_1's reproduction is the last act.

- **2026-08-26 — the 34 frozen oscillation fixtures (OSC-001…034) as gates** (`20260826-fixture-drift`).
  Cut in July from local games of the very-old bot `98628e98`; "reproducible on base" meant the
  candidate replays that bot's exact episode, so every bot generation since silently failed more of
  them (23 of 34 by the champion). Killed by the owner's ruling to retire old data and generate
  fixtures from fresh instrumented real games instead. Learned: a frozen position from an old bot is
  a wasting asset; fixtures must be a script's output tagged with the bot hash. The files and the
  08-21 verdicts stay as history. Would reopen: never as gates; the successor is
  `20260826-fresh-fixture-dataset`.

- **2026-08-26 — Candidate 3b, Candidate 3 plus the stuck-holder release** (`20260826-candidate-3b-stuck-holder-release`).
  The bounded successor the Candidate 3 obituary asked for: keep your goal, but release a troll that
  has held one goal too long while a partner waits. Nine gates were written into the card at 15:16Z
  before any source existed. **What it did:** the release fires exactly twice in 240 games, at
  `m061:0` t73 and `m061:1` t109 — the two seats and almost the two turns D-3 predicted (t72/t108) —
  cures the kept-goal age on those seats (171/170 → 43/78), and is otherwise free: 238 of 240 games
  are byte-for-byte Candidate 3, containment is command-identical on all 240 panel games and
  byte-identical on 34/34 fixtures, `xc = 0` on all six loop games, determinism 0/240.
  **What killed it:** gate 4 — the release recovers **none** of the lost points. `m061` still scores
  32/35, identical to Candidate 3, still −43/−47 against the champion. Gate 6 also fails (max kept-goal
  age 88, on `m068:1`, a game the rule does not touch — that pre-commitment was mis-specified, and
  saying so is part of the record). **Learned:** the −44/−47 on `m061` is **not** caused by the long
  kept goal. Two candidates now agree on it: cure the age and the points do not come back, so the
  cost lives somewhere else in the absolute keep and the release list is not the whole design problem
  after all. Also learned that a pre-committed gate can be *wrong* — gate 6 measured a game outside
  the rule's reach — and that the honest move is to fail on it anyway rather than rewrite it after
  seeing the number. **Would reopen it:** only on a new mechanism for `m061`'s deficit found by
  measurement first (what those two seats actually lose points doing), never as a retune of this rule.
  Packet `claude_1/cure3b/g1-packet-3b-2026-08-26.md`; diff
  `readable/diffs/candidate-3b-stuck-holder-release.diff` (+80/−3); result
  `claude_1/cure3b/results/panel-read3b.json` (SHA-256 `8280f927c2900559…`). codex_1's independent
  reproduction (`codex_1/reviews/candidate-3b-reproduction-2026-08-26.md`, commit `4dcd3d82`) was the
  last allowed act and returned **REPRODUCED FAIL** with a byte-identical verdict JSON.

- **2026-08-26 — the banana wood farm, first build** (`20260826-banana-farm-candidate`). Stopped at
  its own first validity gate the same night it was chartered, and reproduced by the second bot.
  **What it did:** containment perfect (with the farm switched off it is byte-identical in play to
  the champion on all 240 panel games and 34 fixtures); the diagnostic dialect decoded with zero
  errors; on the local bench its own score was **+3,100 over 240 games** — the opposite sign to the
  pre-registered expectation. **What stopped it:** blocking games rose **52 → 96** (50 new, 6
  cured), and on 35 of the 50 the cause is `opp_harvested_ours` — *the opponent walks onto our hut
  ring and eats the fruit we grew*. The pre-committed stop-latch fired in **0 of 240** games because
  it counts enemy **chops** on the ring while the theft that actually happens is **harvests**: one
  design defect showing up twice. **Learned:** the owner's stop criterion ("the farm is more
  profitable for the enemy than for us") is right, but its observable must count harvests, not
  chops; and a ring next to our own hut does not protect the crop — the enemy pays the trip. Denial
  was a formality on this corpus (509 turns in denial against 28,239 farming; in 141 of 240 games
  there was no aim tree left to deny when the second troll appeared). **Would reopen it:** a bounded
  repair with the latch counting harvests and a placement rule that does not hand the enemy a
  standing crop — the owner's call. Packet `claude_1/farm/g1-panel-farm-2026-08-26.md`; reproduction
  `codex_1/reviews/banana-farm-panel-reproduction-2026-08-26.md`; design
  `claude_1/farm/g0-farm-2026-08-26.md`; contract `docs/BANANA-FARM-CONTRACT-2026-08-26.md`.

- **2026-08-27 — the banana farm line, CLOSED by the owner** ("closed", 10:04Z; `20260826-banana-farm-candidate`,
  board row F-2). **What happened after the first build stopped:** the owner had it put on the ladder
  for one hour to be *seen* — 10.8 at rank 172 of 176 (submission `41201668`); its 160 games, collected
  and decoded from the farm's own telemetry, split 81 wins / 79 losses, mean margin −26 (own 169 vs
  opponent 195), 24 losses by 150 or more with the opponent near 400. **Correction to the paragraph
  above:** on the ladder the denial stage was *not* a formality — it ran ~65 turns a game in every game
  (ended: all aim trees felled 66, regrowth 35, opponent's third troll 31, deadline 14, still denying
  at the end 14); the local panel's maps and opponents were not the ladder's. The farm planted 16
  bananas a game and harvested 4.8 from mothers; the latch fired twice. **What killed the line:** the
  owner's judgment that the farm changed several things at once ("a dirty experiment"); a one-variable
  ablation of the champion's own denial rule was run instead and became the champion; then "closed".
  **Learned:** experiments change one variable; the ladder's answer differs from the bench's (the
  panel said denial never ran, the ladder said it always did); a hut-ring farm feeds a harvesting
  opponent. **Would reopen it:** only the owner's word; the denial-first repair the owner chose on
  the morning of 2026-08-27 (chop the opponent's plums and lemons first with hard priority, nothing
  planted until denial ends, farm afterwards) is written into the card for that day. Games
  `local_claude_1/farm-watch/games-41201668/`; readable diff `readable/diffs/banana-farm-vs-v6-instrument.diff`.

- **2026-09-03 — Track 3, the orchard line (the third troll → three heroes → the orchards 1–8)** (`20260828-third-troll`;
  rows 3-1 and 0-7; killed 06:0xZ by the owner's word "kill" after orchard 8's reading). **What it was:** the champion of
  record with a harvest-1 second troll, both trolls funding a 2/3/0/3 third troll, an orchard of lemons and plums planted
  beside the tent to feed the bill, protected from our own axes; eight builds in seven days, each one owner-ruled variable.
  **What killed it:** the readings — (a) 11.3, three heroes 11.7 / 12.0, orchard 5 14.7 / 13.5, orchard 6 18.8 (the champion
  18.2 that day), orchard 7 16.7 / 16.6, orchard 8 17.98 (the champion 17.0 the day before) — never more than a point above
  the champion and inside the ±1.5 noise; and the turn-by-turn read of 09-03 (`local_claude_1/funding-order/OUR-BOT-FUNDING-2026-09-03.md`):
  the second troll at a median turn 26 (the top four: turns 1–9 from the starting draw), one seed per far-door trip, 77 % of
  trips home carrying one item, a quarter of wild harvests five or more steps away with the orchard at the door. **What we
  learned:** the third troll is not the lever by itself — the top four buy theirs later (turn 95–115) and are far stronger;
  the order of train, plant and gather in the first thirty turns is, and our rules had it backwards (plant first, train
  late, gather alone); planting itself is early and the PICK-before-TRAIN clash never happens. **What would reopen it:**
  nothing in this form — the successor is the opening solver (`20260903-opening-solver`), which plans the same actions
  in the referee's own order. Instruments kept: the generator chain (`local_claude_1/third-troll/make_*.py`), the bed and
  the smoke slice, the collected batches (41206542 … 41234498) and their reads.

- **2026-09-03 — Track 3, the cheap third troll** (`20260902-cheap-third-troll`; dead on paper 05:2xZ by the
  coordinator's VM fallback seat, after claude_1's read of 04:23Z). **What it was:** the successor to the port —
  our champion exactly as it plays, plus the weakest third troll worth having (speed 1, carry 1, no harvest, chop 1:
  3 plums, 3 lemons, 2 apples, 3 iron with two trolls owned), bought with the smallest possible detour; a read from
  our own 320 collected ladder games before any build. **What killed it:** the champion never holds that bill — short
  in 319 of 319 games by a median of 6 items — and the shortfall is dear for two measured reasons: its trained troll
  cannot harvest, so the fruit is the starting troll's job alone, one item a trip (a median 37-turn detour while the
  trained troll mines the iron in 9), and the champion plants 81 % of its banked plums and lemons as seeds it fells for
  four points each, so a fruit it spends is worth up to 4 points, not 1. Net per game: +11 [9, 13] with fruit at face
  value, −6.5 [−8.4, −4.6] with fruit priced as the champion prices it; the only variant that loses under neither
  reading (buy only when the bill is within 30 turns, a third of the games) is worth +5 to −1 — below what the field
  panel can resolve. Every number reproduced by execution on the VM (`local_claude_1/cheap-third-troll/VERIFY-2026-09-03.md`).
  **What we learned:** a bot with a harvest-0 second troll pays for fruit with its starter's round trips; the
  champion's bank is not idle money but seed stock worth four points an item; the referee prices bananas at zero for
  training, so the seven bananas the champion holds buy no troll. **Would reopen it:** the owner's "build" for the
  30-turn variant (one variable, a build, a bed, a smoke, a field reading); or a different card — a harvest-1 second
  troll that makes the fruit a two-troll job, or a talent priced in bananas. Read
  `claude_1/cheap-third-troll/READ-2026-09-03.md` (pinned `54786b02…`); card `coordination/tasks/20260902-cheap-third-troll.md`.

- **2026-09-03 — Track 3, stage 2A of the opening solver: the opening dispatcher** (`20260903-opening-solver`, stage 2A;
  built by claude_1 10:57Z, dead 15:3xZ on the ladder reading the owner asked for). **What it was:** the champion of
  record with its opening replaced — five anchored replacements, +684/−5 lines, a 662-line deterministic dispatcher
  that ran from turn 1 to the third troll's TRAIN and then handed back to the champion's own play byte for byte. Its
  rules were the offline solver's, ruled after a design round: train the second troll from the starting draw on turn 1;
  carry useful loads; never PICK on a turn a TRAIN would fire; plant seeds by water else next door, on the way; nobody
  idle, mine only against the iron deficit; the third troll's shape by the iron-distance rule. Every gate before the
  selector passed: the build reproduced byte for byte by the coordinator from the pinned commit on the VM (all three
  artefacts, 0 compile errors, 78,035 of the platform's 100,000 characters), the bed 34/34, the 24-map smoke 24/24 with
  a third troll in every game, and timing with a fifteen-fold margin (turn 1 at 4.27 ms against 1,000; p99 2.28 ms
  against 50; 0 turns over budget in 1,940). **What killed it:** the field reading, then the ladder, agreeing.
  Rung 1 read `FIELD_BELOW_ZERO` — Δwin **−0.2219 [−0.2562, −0.1862]**, Δmargin −28.71, over 1,600 paired games with
  zero faults, measured twice independently (claude_1's run and the coordinator's from a fresh archive of the pin) and
  agreeing to the digit: 29 / 174 / 35 / 322 wins of 400 against the champion of record, orchard 6, the old champion
  with denial on and the network clone, against the champion's own 113 / 324 / 147 / 331. The owner then said "put it on
  the platform" against the coordinator's advice, and the ladder confirmed it: **14.59 at rank 147 of 177**
  (submission `41236483`, 160 games) where the champion of record, restored immediately and read in the same field an
  hour later, took **18.72 at rank 72** (`41236823`) — a gap of 4.13, nearly three times the ±1.5 a single reading
  moves by noise. **What we learned — and this is the part worth keeping.** (1) The order *is* implementable as rules
  and it does what it was designed to do: on the real ladder the second troll arrives at **median game turn 2** against
  the champion's 9, in 100 % of games, and a third troll arrives in **98 %** of games where the champion never builds
  one at all. (2) **The plan executed, and the plan was wrong — which is the finding.** *(Corrected 16:2xZ. The
  coordinator's first decode read the referee's tooltip `turn` as a game turn when it is a frame index at two frames
  per turn, doubling every roster time; it reported the third troll at "turn 147" and called the bench an artefact.
  claude_1 caught it and verified `turn` = 2 × game turn − 2 game by game on all 156 games; the coordinator confirmed
  the scale independently — 48 tooltips exceed 300 and the largest is 550, while a game cannot pass turn 300, and
  frames per game reach 601 = 2 × 300 + 1. The "bench artefact" reading is withdrawn.)* On our 24-map bench the third
  troll landed at median turn 70.5; **against the real field it lands at median game turn 74.5** (quartiles 61 / 74.5
  / 98) — **the bench held.** The real opponents in those same games bought their own third troll at median game turn
  98 when they bought one at all (77 %), so this build got its third troll **about 23 turns before the field did** and
  still read 4.13 below the champion. That is a harder and more useful result than a failed plan: the early third troll
  is not merely difficult to reach — it **is** reached, ahead of the field, and it still does not pay. (3) The bot scored **more raw points** than the champion (median 204 against 184.5)
  while rating 4.13 lower — a reminder that raw score across two packages is confounded by matchmaking (a bot at rank
  147 meets a weaker field: its opponents scored a mean 197.9 against the champion's opponents' 210.1), and that the
  paired panel and the rating, not the score, are the measures. (4) The mechanism of the loss is the port's mechanism
  again: the opening spends turns shopping while the champion banks wood at four points a unit, and the one opponent
  the dispatcher held level was the network clone — the only one of the four that does not race for wood.
  **What would reopen it:** two separable halves, and only the cheap one is attractive. (a) **The turn-2 second troll
  alone** — it is nearly free, being bought from the starting draw, it demonstrably survives the real field, and it is
  one variable on top of the champion with the third-troll farming detour removed; that is an untested build and the
  obvious next candidate. (b) A planner that plans against a *contesting* opponent instead of an idle board — which is
  stage 2B's search with its contested-tree repair gate, and needs the owner's go and a raid risk budget.
  **Instruments kept:** the generator `claude_1/opening-solver/stage2a/make_opening_dispatcher.py` and its probe, the
  coordinator's reproduction (`local_claude_1/opening-solver-verify/stage2a/`) including the field reading and the new
  `ladder_read_trolls.py` (roster timelines from the referee's own event tooltips, no board reconstruction needed), and
  the two collected 160-game packages `games-41236483` (the dispatcher) and `games-41236823` (the champion control).

- **2026-09-03 — Track 3, the wood-aware three-troll optimized start** (`20260903-three-troll-optimized-start`; built
  16:2x–16:5xZ by **chatgpt_2** (then accidentally labelled `chatgpt_1`; the identity was settled at 17:58Z by the
  owner's three-part test), overwritten by the other agent on the shared branch, rescued by the
  coordinator to `refs/heads/rescue/chatgpt1-three-troll-optimized-start-2026-09-03`, and ruled dead 17:4xZ).
  **What it was:** the champion of record plus stage 2A's turn-2 second troll, plus the first genuinely new idea anyone
  had brought to the roster problem — a contested-resource search over third-troll tuples in which a funding trip is
  **charged against the 4-point wood trip it displaces**, admitting a plan only if it finishes by turn 110 and clears
  eight points of net continuation value after that charge, abandoning back to the champion when the gate fails, and
  selecting for all three trolls jointly afterwards. It shipped with a **control arm** — the same opening with the
  optimizer disabled — which is the right instrument and which its author built without being made to.
  **What killed it: mechanics, on both arms, reproduced by the coordinator.** From the rescue pin, nothing edited, the
  generator regenerates all four artefacts **byte for byte** (candidate `d994b3fb…`, control `2d62e0c7…`), both compile
  with zero errors, the round trip is exact, and the source is 90,070 UTF-16 units of the platform's 100,000. Then the
  24-map smoke: **the candidate is mechanically OK on 19 of 24 maps and the control on 15 of 24**, against a 24/24 bar —
  the card's first dead condition, *any mechanics failure*. Five maps stall the candidate and **nine stall the control**;
  the candidate scores **−416 own points against the resident over 24 games** and the control −242. Its author had
  already reported the same numbers and its own verdict, `DEAD_AS_BOT`; the coordinator's reproduction agrees with it in
  every figure, so this is a failure of the build and not of the reporting.
  **What we learned, and the first point is a correction the coordinator made against its own earlier reading.**
  (1) **The +0.0500 [+0.0050, +0.0950] by which the candidate beat its control is NOT evidence for charging the foregone
  wood, and the board and card said it might be.** The comparison is between two arms that *both* fail mechanics, one of
  which stalls on nine maps of twenty-four: it measures less-broken against more-broken on a damaged base, not the idea
  against the champion. **Charging the foregone wood remains untested.** (2) The gate did change behaviour, but not in
  the direction hoped: the third troll arrived at **median turn 30** — far earlier than any previous build — and always
  as the *weakest* tuple available (`1 1 0 1` ten times of fourteen, `1 2 0 1` four). Charging the wood did not stop a
  bad trade; it selected a cheaper, earlier troll instead, and the bot still lost 416 points a game to the resident.
  (3) **A control arm must itself pass the mechanics bar or it is not a control.** This one did not, and it silently
  invalidated the only comparison the build existed to make. (4) The change costs +1,334 lines and takes the source to
  90 % of the platform's character limit, leaving little room for anything else.
  **What would reopen it:** the idea, not this build. **The cheapest honest test of wood-charging uses the champion
  itself as the control** — the champion unchanged, plus only the wood-charging admission test for a third troll, with
  no turn-2 second troll and no joint selector confounding it; then the control passes 24/24 mechanics by construction
  and the comparison means what it claims. Until a build clears the mechanics bar on both arms, nothing measured about
  this gate is admissible. **Instruments kept:** the rescue ref with all 47 files, both generators, and the coordinator's
  reproduction (`/data/scratch/3t-verify` on the VM, log `/home/tarstars/verify_3t.log`).

- **2026-09-04 — the wood-charging gate** (`20260904-wood-charging-gate`; built by claude_1 03:40–04:19Z on the owner's
  approval, dead 05:3xZ on its own pre-registered condition 1). **What it was:** the owner's own rule, in the owner's
  own words — *"predict two outcomes: with troll and without, and if 'with' wins, we do it."* The champion of record
  unchanged, plus a third-troll funding pathway that every turn forecast the same turns spent **funding** against those
  turns spent **chopping wood at four points a unit**, over 27 candidate troll shapes, admitting only the best shape
  whose WITH strictly beat WITHOUT and otherwise playing as the champion byte for byte. The control was the champion
  itself, so it cleared the mechanics bar by construction — the repair for what had broken chatgpt_2's build the day
  before. **What killed it:** the 24-map smoke read **mechanics ok on 23 of 24**, map `c14dea6aa5d28951` stalling with
  the second troll idle 30 consecutive turns inside the funding window against the resident's 0 — the card's first dead
  condition, *any mechanics failure*. claude_1 stopped there as chartered: no timing run, no panel, no field reading,
  nothing offered for the ladder. The coordinator reproduced it from the pinned commit: the generator regenerates all
  three artefacts **byte for byte**, the base's token stream matches the resident champion, the round trip is EXACT,
  both forms compile at zero errors, 67,902 bytes — and the smoke reproduces to the digit, same 23/24, same stalled
  map, same −174.

  **What we learned, and it is worth more than seven obituaries: the trade was finally computed honestly, and it loses.**
  Three forecasts were read before any verdict was reported. **The honest one — the version that caps the troll's future
  wood by the finite, contested forest — DECLINED ON ALL 4,593 EVALUATED TURNS.** On no map, at no turn, did "with"
  beat "without". The looser versions (the troll's rate × the turns remaining, with no forest limit) admitted in 22 of
  24 games, and that bot **lost 174 points** over the slice, worse on 18 of 24 maps. Read against the outcome, **WITH
  was overstated about tenfold and WITHOUT understated two to threefold**: the third troll arrives at median game turn
  **108**, into a forest four trolls have been felling for a hundred turns, and **adds no whole-game wood on average**
  (below the champion on 15 of 22 maps). The cost is exact — wood banked **55 against the champion's 204 by turn 50**,
  225 against 389 by turn 100, 793 against 836 at the end: **the funding cost 149 units of wood by turn 50 and the
  troll never earned them back.** That is precisely the mechanism the port's loss read and stage 2A's death both
  pointed at, now measured directly instead of inferred. Two honest caveats the builder volunteered: the letter of the
  "must decline" condition was met (275 declines of 2,595 turns, 158 of them because the troll could not repay its
  fruit) but not its substance, since a troll was still bought in 22 of 24 games; and the smoke opponents are **soft** —
  the resident's realised pair rate here is 0.090 against 0.171 on the real ladder — so the calibration was generous to
  the troll, not mean.

  **What would reopen it:** on this evidence, nothing about the roster. **Seven lines have now died attacking it, and
  this one explains why the other six died** — an extra troll bought around turn 100 arrives at an emptied board and
  cannot repay the wood its shopping cost. The one variant not run is v1 with its forest estimate widened to the
  record's 108 units felled after arrival; **claude_1 predicted in advance that it would still decline on most maps and
  read within noise of the champion**, the coordinator agreed, and it is not chartered. If the roster is ever revisited
  it must be bought **before** the wood race starts, not funded out of it — and stage 2A already showed that reaching
  three trolls 23 turns ahead of the field does not pay either. **Instruments kept:** `claude_1/wood-charging-gate/`
  (the generator, the two gate variants, `gate_read.py`, `calibrate_kappa.py` and all three forecast readings), and the
  coordinator's reproduction at `/data/scratch/wg-verify` on the VM (`/home/tarstars/verify_woodgate.log`).
