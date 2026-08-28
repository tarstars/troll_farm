# Task — the third troll: the champion of record grows a third troll, paid for by both trolls together (the owner's next one-variable experiment, 2026-08-28)

- Born 2026-08-28 04:3xZ by the owner's word ("set as next goal bot with the third troll"), after the reconstruction of the four top players (`docs/reports/2026-08-28-top-four-algorithms.pdf`, `local_claude_1/reconstructions/README.md`) ranked it first among the ideas to test.
- Record owner: local_claude_1 (coordinator) · Work owner: **local_claude_1** (builds it, as the apple farm and the floor were built) · Reviewer: **codex_1** (reproduces the build, the bed and the smoke) · Arena: the coordinator submits — the ladder slot after the floor's last reading (round 3, 05:24Z).
- Status line: **BORN 04:3xZ — design round 1 pending (the four questions below, with the coordinator's recommended answers); then the build.**

## The rule (owner, plain words)

After the second troll is trained, the bot wants a third troll: speed 2, carry 3, no harvest power, chop 3 (written 2/3/0/3). With two trolls its price is 6 plums, 11 lemons, 2 apples and 11 iron (the price of a talent is its square plus one for every troll the player already has, paid in plums for speed, lemons for carry, apples for harvest, iron for chop). Both trolls collect that price together: the starting troll harvests the plums and lemons (it is the only troll that can harvest), the trained troll mines the iron and chops as it does now. The turn the price can be paid, the bot trains the third troll, and from then on it chops like the second. Nothing else changes: no fourth troll, planting as it is, the endgame as it is.

Why: every one of the four top players grows to three or four trolls, buys the late ones as carry-3/4, chop-3 lumberjacks with no harvest power, and buys them the turn they become affordable (88–100 % of their trainings). Our losses are exactly against three- and four-troll opponents: the champion wins 6 of 18 games against four-troll bots, the floor 5 of 37. In July this project measured the mechanism on the bench: a training plan alone did nothing (−170 points), both workers collecting one bill together made the third troll affordable and was worth +106 (`local_claude_1/reconstructions/prior-art.md`). The top four reach their third troll at median turn 95–118.

## Design questions (round 1) — the coordinator's recommended answers

1. **A deadline for the funding?** Recommended: keep collecting the bill until it is paid, but stop wanting the third troll when fewer than 100 turns remain (the referee-side rule already forbids training in the last 20 turns; a troll trained after turn 200 has too little time to pay for itself). No change to the second troll's own deadline logic.
2. **Funding versus normal work.** Recommended: the same "early" behaviour the champion already uses to fund the second troll (fruit and iron candidates scored above chopping while an item of the bill is missing), applied to both trolls after the second is trained; the starter goes for the missing fruits, the trained troll for the missing iron (`iron_candidates` today is gated to one troll — the gate opens while funding). When nothing of the bill is missing, normal play. Wood already carried is banked first, as now.
3. **The talents.** Recommended: exactly 2/3/0/3 (carry 3 keeps the lemon price at 11; carry 4 would cost 18 lemons — the top bots' choice, but a second variable). Not raised by the floor's logic: the third troll is a fixed specification.
4. **The cap.** `MoisanBot::can_train` hard-caps the roster at two (`if n >= 2 { return false }`): raised to three. The chosen third troll's behaviour: the same candidate lists as the second (chop, bank, mine); the v6 diagnostic line already names every troll's target each turn.

Rejected for this card (later variables): an orchard planted for the bill (idea #2 of the report), a fourth troll, plant-and-cut bananas, the raid.

## Done means

1. The build through the generator chain (`local_claude_1/third-troll/make_third_troll.py`, modelled on `local_claude_1/the-floor/make_the_floor.py` for replacements and `local_claude_1/apple-farm/make_apple_farm.py` for insertions; anchors that occur exactly once in both the diagnostics arm and the readable champion; compile; compact; round trip exact; distinct from every bot; the readable diff written with its +/− counts asserted).
2. The 34-situation differential bed (plays, deterministic, compacted == arm, telemetry 0 errors; a "differs" count is a fact).
3. A **smoke** of full local games on real ladder maps against the scripted opponents: in what share of games the third troll is trained and at which turn (the top four: 56–84 % of games, median turn 95–118); the time the two trolls spend funding; no stall in the funding mode (a troll that never resumes normal work is a defect); own scores compared with the resident as a sanity margin (not a value gate).
4. codex_1's independent reproduction of the build, the bed and the smoke (a ≤ 10 MB slice).
5. The instrument submitted; **one-hour reading** against the owner's stated prediction (asked before the submission); its 160 games collected and read: the third troll's turn and share, wins by opponent troll count, the games where the funding never completed.

## Dead means

The bed or the smoke shows the funding never completing on maps where the bill is reachable, a troll stuck in the funding mode, or the compacted file behaving differently from the arm — then no submission, the obituary names the defect, and the owner decides.

## Budget

1 design round (2 at most), 1 build, 1 bed, 1 smoke, 1 reproduction, 1 hour on the ladder, 1 reading. Nothing else is promoted, reverted or chartered by this card.

## Log

- 04:3xZ owner: "set as next goal bot with the third troll" after "what's the shortest path to points in our bot?" → this card; the floor's round 3 becomes its last round; the context flushed (`coordination/HANDOVER-2026-08-28-third-troll.md`).
- 04:5xZ coordinator (new session): the floor's round-3 timer re-created (one-shot `a1d0ea76`, 05:24Z; the previous session's cron died with the flush). Read the champion's training code before presenting the design: the cap `n >= 2` sits in `MoisanBot::can_train` (readable line 627, with the referee's last-20-turns rule) and in `YamoBot::training_affordable` (line 1328, the opening's own check — untouched); the funding behaviour `early_candidates` (line 662) is entered only while the bot has fewer than two trolls (`early = … my_units.len() < 2`, line 2090) and already builds the missing-items list from `training_cost(n, desired)`, so the third troll's funding mode is the same list with `n = 2` and the fixed 2/3/0/3, split by troll (starter: plums/lemons/apples; trained: iron). Design round 1 presented to the owner.
