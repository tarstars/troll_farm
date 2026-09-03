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
