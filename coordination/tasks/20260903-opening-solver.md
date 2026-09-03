# Task — the opening solver: a planner for the first hundred turns (train, plant, gather, mine in the exact order the referee rewards), offline first, in the bot's first second if it earns it (owner 2026-09-03 ~05:0xZ: "What do you think about building an off-line planner for this 'beginning of the game' part? If it's fast and efficient, we can try to put this solver into bot and use first second of computing time the bot have.")

- Born 2026-09-03 05:5xZ by the owner's proposal and the coordinator's assessment (both on record in the session of
  09-03 04:xxZ–05:xxZ), after the owner watched orchard 8's ladder game: "the algorithm of resources collection for the
  third troll is extremely inefficient … 'train, plant, gather' should be done in an extremely fine order. Figure it
  out." The owner's follow-up fixes the objective: **we lose tens of turns now; the third troll trained earlier lets the
  chopping start earlier; and more chopping power allows a bigger farm — the balance is that we must be able to fell and
  bank our own farm faster than the enemy can raid it.** Opponents cannot block a cell (owner); they can take a tree.
- Record owner: local_claude_1 (coordinator) · Work owner: **claude_1** (stage 1, the offline solver) · Verifier: **the
  coordinator** (replays every found schedule through the referee; reproduces the numbers) · Design reviewer: **chatgpt_1**
  (one round; the coordinator sends the assignment and asks the owner to switch it on) · The owner reads the one page.
- Supersedes: the cheap-third-troll card (dead on paper 05:2xZ; the owner: "it was an attempt to fix the order, now we
  can ignore it when we have solver") and any further orchard build (rows 3-1, 3-2 closed).
- Status line: **BORN 05:5xZ — stage 1 chartered to claude_1 (handoff pending): the offline solver, the schedules on real
  maps, the gap to our bots, the farm/chop balance; nothing in the bot yet.**

## What the two reads of 09-03 established (the baseline the solver must beat; `local_claude_1/funding-order/`)

- **Our orchard bot** (159 real games of orchard 6, byte for byte orchard 8 in the funding phase): the second troll at a
  **median turn 26** (the champion's: 10; turn 1 in 116 of 319 games); three seeds planted one per trip with the starting
  troll walking to a far door between the pick and the plant (turns 3–8 in the median game); the third troll at median
  turn 88 (84 % of games), its bill paced by 11 lemons (met at median turn 77) and 11 iron (turn 53); 77 % of trips home
  carry one item; 24.5 % of wild harvests five or more steps from the shack while the orchard stands at the door; 43 % of
  harvests take one fruit from a tree rather than three from a full one; walking is 60 % of every troll's turns. Not
  problems: planting is early (first seed median turn 5), the PICK-before-TRAIN clash never happens (0 of 283 trains), idling
  is 3 %, door blocking 0.25 %.
- **The top four** (782 exactly reconstructed games): turn 1 MOVE off the shack and **TRAIN the second troll from the
  starting draw** (MSz 97 % on turn 1, Bubaptik turn 2, norxondor 41 % on turn 1, median 9), each talent the highest its
  own fruit affords, never below 2/2, usually with harvest 1–2; turn 2 PICK a seed; turn 3 PLANT it on the free cell that
  minimises distance-to-shack plus distance-to-troll (78–90 % of 20,000 plants; 42–57 % at distance 1); one or two more
  pick-plant pairs; the first HARVEST on a full wild tree around turn 8–11; both trolls gather; mining only against the next
  bill's iron deficit (MSz mines early because its chop-3 bill is known); no troll idle; the third troll (2/3/1/2 for
  norxondor, 2/4/1/c for MSz — harvest kept) trained the very turn the pre-turn stock clears the bill (zero delay in 95–99 %);
  the fourth 30–35 turns after the third because three trolls fund it. They plant ~29 trees a game; their own trees overtake
  wild ones as the harvest source by turn 40–70.
- The mechanics that make the order fine: a planted plum or lemon bears its first fruit ~32 turns after planting inland
  (12 near water), an apple 36 (8 near water), a banana 24 (16); a full tree regrows one fruit the instant it is harvested;
  the per-turn task order is MOVE → HARVEST → PLANT → CHOP → PICK → TRAIN → DROP → MINE, so a pick shrinks the stock the
  train sees and a drop never pays for the same turn's train.

## Stage 1 — THE OFFLINE SOLVER (claude_1; budget three days; nothing in the bot, no ladder)

**The world.** One player on a real map from the pinned panel (`claude_1/h2h-panel/panel-200-seed1.jsonl`, sha
`77556dc9…`, 200 maps with their starting draws) plus the openings of the collected games; the exact referee
(`sim/engine.py`, or the Rust engine `rust/target/release/libtroll_farm.so` through the bench's binding — the referee
diff is the authority either way); no opponent in the first version (a raid model comes with the balance question below).

**The actions.** Macro-actions, each timed by the engine to the turn: go to tree X and take k fruits (harvest power and
carry decide k); go home and DROP; PICK n seeds and PLANT them at cells c₁…cₙ; MINE k iron; TRAIN talents t (the referee's
`n + talent²` bill, iron only on iron maps, checked after PICK and before DROP); CHOP tree X. The per-turn command
sequence is derived from the macro plan and must be legal in the referee.

**The objective (the owner's frame; the exact form is the design round's first question, the coordinator's
recommendation written here).** Lexicographic: (1) the turn at which a target chopping power is online — the sum of the
roster's chop talents reaches P (P swept: the second troll alone, then a third troll of chop 2 or 3); (2) at that turn,
the bank in points (wood four, fruit one) plus the standing own-tree wood the roster can fell before the game ends.
Report the whole curve time-versus-P per map, so the owner sees the trade-off rather than one number.

**The balance (the owner's second point).** From the collected games (ours and the field's): how fast enemies fell trees
planted next to our shack — the raid rate by turn and by distance — and from it the farm size a given chop power can
convert before it is raided. The solver's planting count is then a function of P, not a constant.

**Validation, by the verifier.** Every schedule the solver reports is replayed through the referee by a scripted policy
that follows it (the h2h harness with a schedule-following seat), and the turn the roster completes must match the
solver's to the turn; on the 24-map smoke slice, orchard 6's own real funding on the same maps (median third troll 88,
second troll 26) is the yardstick.

**Deliverables.** The solver (`claude_1/opening-solver/`), the schedules for the 200 panel maps as JSON, and a one-page
read for the owner: the optimal order in words with the turn numbers, the gap in turns between the solver and our bots
(the champion's opening; orchard 6's), how the gap splits by cause (the late second troll, the far-door walks, the
one-item trips, the far wild trees), the farm/chop balance curve, the solver's speed (schedules per second, and whether
one second suffices for one map), and a recommendation: rules distilled from the schedules, or the planner in the bot.

**Dead on paper.** If on the median panel map the solver cannot complete the same roster more than ten turns earlier than
orchard 6's real games do, the "tens of turns" are not in the order of the opening — the obituary says where the
turns went instead, and stage 2 is not started.

## Stage 2 — the planner in the bot (a separate charter on the owner's word after stage 1)

The first turn's 1,000 ms buys the deep plan, each later turn's 50 ms re-checks it against the board (a tree taken, the
farm raided) and repairs it; the plan is followed as a script otherwise. Gates: time per turn with margin, the source
under the 100,000-character limit (the champion is 64,000), the bed, the field reading, the owner's prediction, one
ladder hour.

## Done means

Stage 1's read and its verification on the card, with the owner's word on stage 2; or the dead-on-paper obituary.

## Budget

Stage 1: three days of claude_1, one design round (chatgpt_1 + the owner), the coordinator's replay verification. No ladder,
no platform, no cluster or host training touched. Stage 2 is not budgeted here.

## Log

- 2026-09-03 ~04:2xZ owner: "I checked the game of the submitted bot. Algorithm of resources collection for the third troll
  is extremely inefficient, and efficiency here is crucial for the success. Pay attention to the order of actions. 'train,
  plant, gather' should be done in an extremely fine order. Figure it out." → the two reads (`local_claude_1/funding-order/`).
- 2026-09-03 ~05:0xZ owner: the offline planner proposal; the coordinator: yes, two stages, offline first, folded into the
  successor's read. ~05:4xZ owner: the successor card was an attempt to fix the order, ignore it now; opponents cannot block a
  cell; the objective is the roster's chopping power online earlier and a farm the chopping power can convert faster than the
  enemy raids it. — owner / coordinator
- 2026-09-03 05:5xZ coordinator: this card written; stage 1 chartered to claude_1 by an ack-required handoff; the two reads
  attached as the baseline. — coordinator
- 2026-09-03 09:1xZ: **stage 1 delivered by claude_1 at 09:05Z** (handoff `20260903T090548Z`, pin `e392e500…` on `agent/claude_1`: the
  page `claude_1/opening-solver/READ-2026-09-03.md`, the solver, the 400 schedules, the ablation, the raid rate). Headline: same roster
  as orchard 6 → third troll at median turn 70 vs 88.5 (292 map-seats; gap 21, p25–p75 10–35; earlier by >10 on 74 %; later on 22, the
  worst by 20 — a search miss); free curve chop 1 / 2 / 3 at 43 / 46 / 58; turn-1 train from the draw on 314 of 400; the ablation: one
  item a trip 7 turns median (mean 9.0, 43 of 51), the late second troll 7 where late (mean 5.2), seeds' cells 0 (mean 2.1), far trees 0
  (mean 0.9) — sum 17 vs a mean gap 18; raid rate 0.19 per 100 tree-turns before turn 100; Python 64 rollouts/s, 30 s a map-seat, a
  deterministic plan 15 ms. **Not dead on paper.** Verification by the coordinator's own replayer through `sim/engine.py` on all 400 ×
  4 schedules and the re-run of `report.py` is in progress; the ack waits on it. — coordinator
- 2026-09-03 09:4xZ: **stage 1 VERIFIED by execution.** The coordinator's own replayer (written from scratch, not claude_1's `replay.py`)
  fed every kept schedule to `sim/engine.py` with an idle opponent: **1,492 of 1,492** variant-schedules (400 free + 400 chop-2 + 400
  chop-1 + 292 same-roster) match on the TRAIN turns, talents, unit ids, final unit count, inventory and score; the two flagged
  map-seats (`c8133082…` s1, `b4a37d9e…` s1) are `done: false` for the same-roster variant only and excluded from n = 292 as the
  page says. `report.py` reproduces the page's numbers; the §3 verb-order table is not printed by `report.py` (a tooling gap) and
  was recomputed from the JSON — exact. The ablation table reproduces from `ablation.json`; the raid table re-executes from the
  raw inputs (6,200 trees, all 20 bins). **Two wording slips for the author:** the page's "mean gap of about 18" is the median
  (the mean is 21.7); "109 raided (6.4 %), 1,583 felled by itself" reads 114 / 6.68 % / 1,587 in the data. The verifier's own
  caveat, kept: the page is an idle-opponent, no-blocking model by design; the verification confirms its arithmetic and referee
  fidelity, not that the plan survives a contested opening — the design round's question 2. `sim/engine.py` has no error path for
  illegal commands (they no-op), so exact state matching stood in for a legality check. Record:
  `local_claude_1/opening-solver-verify/VERIFY-2026-09-03.md` (re-landing after a git mishap took the untracked copy).
- 2026-09-03 09:5xZ: **the design round opened** — the review assignment to chatgpt_1 (`20260903T095000Z`, ack-required, pinned to the
  landed merge of claude_1's branch): the objective's form (roster target vs chop sum; the third term for stage 2), the idle-opponent
  assumption (what a contested opening changes), the rules-first split, the farm balance, anything overclaimed. The owner is asked to
  activate chatgpt_1. — coordinator

## Stage 2 — chartered 2026-09-03 10:3xZ after the design round (chatgpt_1's review `chatgpt_1/opening-solver/stage2-design-review-2026-09-03.md`: ACCEPT-WITH-EDITS, every edit taken)

**The objective (replaces the chop-sum form above).** The in-bot planner keeps a frontier of full roster states —
completion turn, every troll's talents and arrival turn, bank, carried resources, positions, the tree state — with the
earliest completion first within a roster, and across rosters a turn-300 continuation value fed by the live state:
the bank, the expected fruit, four times the wood *actually banked* by turn 300 under a fixed continuation policy, minus
the expected raid loss. The same value replaces a count of planted trees (a lemon by water bears in 12 turns, inland
in 32; two equal counts are not equal farms). The third term is fixed offline as a policy or a table with live inputs.

**The 21 turns** (same roster, turn 70 against orchard 6's 88.5) are recorded as an idle-board potential. The two causes
that carry most of it — one item a trip (7 turns at the median on 43 of 51 map-seats) and the late second troll (7 where
it was late) — are our own scheduling defects and survive an opponent; the full number does not claim to. Units block
nothing and iron does not deplete (the referee), so stage 2 needs no path blocker and no iron model — it needs live
validation of tree fruits, tree existence and intended plant cells, and a repair.

**Stage 2A — the rules, now (claude_1; handoff `20260903T103500Z`; budget three days).** The solver's dispatcher in its
deterministic form, ported to Rust inside the champion of record as the opening controller from turn 1 to the third
troll's TRAIN, recomputed every turn from the live board; its rules in order of weight: (R1) turn 1 the starting troll
off the shack and the second troll trained from the draw when affordable (each talent the highest its fruit affords,
never below 2/2, the most harvest the draw affords), else from the first harvests; (R2) useful loads — up to capacity
unless a smaller load clears the next bill sooner; (R3) the invariant — no PICK on a turn a TRAIN would fire, planting
spends only the surplus over the next bill; (R4) seeds next to water when reachable, else next door, on the way; (R5)
everybody gathers, mining against the iron deficit only, nobody idle. The third troll's shape by the orchard bots'
iron-distance rule (chop 3 within 5 steps of a door, 2 within 10, 1 within 16; 2/3/0/c). Gates: the bed, the 24-map
smoke (the third troll's and the second troll's turn distributions against orchard 6's 88 / 26 and the solver's 70 / 1),
timing p99 under 50 ms, rung 1 the field reading (dead below zero with the interval clear of zero; the real-field burst
when it straddles zero), the owner's prediction, one ladder hour; the coordinator reproduces everything.

**Stage 2B — the planner, after 2A's field reading (a charter of its own).** The deterministic, referee-exact,
receding-horizon Rust controller: the roster frontier generated in the first turn's 1,000 ms, ranked by the
continuation value, one legal macro-action executed a turn, each 50 ms turn validating the scheduled target and
repairing only when the state changed. Its gates, beyond 2A's: (i) quality at the real budget — the online plan's
completion turn against the offline 1,800-rollout plan on the panel, the Rust speed measured, not projected; (ii) the
contested-tree repair — the replanner replayed against a mirrored strong opening and the recorded top-bot openings on
the same panel, reporting the delay relative to idle, the repairs, the failed or short harvests, the p25 / median / p75
completion turns; (iii) the roster frontier beyond a chop-only sweep (full tuples such as 2/3/1/2 and 2/4/1/c). The
farm: placement and the planned conversion order are the controls, size emerges; the 8-per-3 figure is an
after-turn-100 sanity check under the page's assumptions; **the owner's risk budget (expected loss below one, or 90 %
no loss, or the maximum expected lead) is asked when 2B is chartered.**

## Log (continued)

- 2026-09-03 10:12Z chatgpt_1: the design review, ACCEPT-WITH-EDITS (six points; verified arithmetic: the bound 7.91 /
  16.22, expected raids 1.02–1.15, a 64–68 % chance of at least one raid at eight trees). — chatgpt_1
- 2026-09-03 10:3xZ coordinator: the ruling above; stage 2A chartered to claude_1 (`20260903T103500Z`); the round closed
  to chatgpt_1 (`20260903T103501Z`); chatgpt_1's branch merged to `main`. — coordinator
