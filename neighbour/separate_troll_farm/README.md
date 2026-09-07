# Troll Farm ladder candidate

## Current state — September 5 restoration

`bot.rs` and `submission.rs` now contain the exact **V439 restoration**, accepted as submission
**41245746**, agent **6704418**. A prospectively frozen real-agent comparison produced **4 wins
from 6 games**, versus **2 from 6** for the previously deployed V543, with no lost target-rank win
and clean command/deployment audits. See `BASELINE-RESTORATION-RESULTS-2026-09-05.md`.

The compact source is 96,985 UTF-16 units, SHA-256
`7f61a6cd510a70e9389e794571512e2c5d0afb33bab957c70791c2c16fbff0bc`.
The rollout confirmed **rank 28/177 in Legend, rating 23.43**, with 160 completed games and
five-minute confirmation: `V439-RESTORATION-MATURE-2026-09-05.md`. Results are 95/0/65 with no
deployment failures. **Seventh place is not achieved.** V543's prior mature rank was 155;
its original files are archived in working storage.

`next_bot/` remains experimental, not the live policy. Its separate same-turn TRAIN correction
has passed 36 Rust fixtures across all eight configurations and 64 generated-start referee
checks. The reused 192-game development panel nevertheless loses four match points; it is not
promoted. See `TRAIN-EGRESS-RESULTS-2026-09-05.md`.
`NEIGHBOR-LEARNING-INVENTORY-2026-09-05.md` records a bounded Claude-assisted, independently
checked inventory: no supported stronger reusable neural export was identified. The neighbor
remains read-only. The chronological notes below describe earlier states, not current deployment.

`lookahead_search.rs` now implements experimental late-game sequence planning on a cloned V439,
with branch-local controller memory and an independently tested direct-endpoint simulator.
`rust_ident_minify.py` leaves room for the full stronger controller and model under the source
limit. Rank-zero, shortened and cached variants each reproduce all 160 production replay streams.
`LOOKAHEAD-RESULTS-2026-09-05.md` records resolved runtime failures and the rejected first policy.
The persistent-horizon follow-up wins three additional development games (176/5/11 versus
173/5/14), passes 43,263-turn equivalence/runtime checks and 320 interactive startups. Its real-agent
screen stopped on a compiler timeout before the candidate played; confirmation remains unopened.
`LOOKAHEAD-FIELD-FAILURE-2026-09-05.md` preserves that failure and the packaging-only repair plan.
Actual exports now compile without command-line warning suppression; the current full suite
passes **498 tests**. The repaired source also passes full command/startup equivalence but still
times out in a separate platform compilation diagnostic. Offline compiler-cost reduction is next;
no planner publication or top-seven claim has been made.
`COMPILER-COST-RESULTS-2026-09-05.md` records the measured platform Rust1.90 toolchain, closed
compile-cost experiments, and the independently reproduced cold opponent-history issue.

## Earlier development notes (historical)

Planning work during the restoration rollout is recorded in `PLANNING-MODEL-RESULTS-2026-09-05.md`.
The standalone model matches 2,889 supported official next-state transitions after correcting a
confirmed row/column plant-creation-order defect inherited from the local referee. Another 560
transitions are explicitly outside its direct-MOVE domain. All 471 tests pass. No planner is yet
integrated or claimed stronger; production V439 is unchanged.

September 5 reset: the current authority is `EVALUATION.md`, not the historical score-curve gate.
`CRITICAL-REVIEW-2026-09-05.md` reviews the earlier decisions. The first real-opponent calibration
pilot, `FIELD-CALIBRATION-RESULTS-2026-09-05.md`, found all three archived policies lost its three
matchups and exposed a no-wood fallback failure. V543 remains deployed at rank 155; it is not a
validated champion. The historical development narrative below is retained as evidence.

Follow-up: `NEXT-BOT-RESULTS-2026-09-05.md` records the implemented productive fallback and its
frozen twelve-game real-agent screen. V368 won 2/3 blocks; V468 and each new profile won 1/3.
Neither new profile earned deployment. Exact replay/source checks identify V468's removal of
resource denial as a concrete regression hypothesis. `next_bot/` is experimental,
not the selected champion; production remains unchanged. The full suite passed 396 tests.

The isolated six-map confirmation is now complete: `DENIAL-CONFIRMATION-RESULTS-2026-09-05.md`.
V439 and V468 both won 1/6; denial improved margins against ranks two/eight without creating a
new win. Seat-one evaluation was implemented and verified with an exact two-game A/A repeat.
`RENEWAL-CYCLE-RESULTS-2026-09-05.md` then repaired plot selection and added complete-cycle banana
production to `next_bot`. Its local score gain did not produce another real-opponent win, so it
also remains experimental. The final suite passed 410 tests. Next: jointly schedule capital,
timely denial and renewable production, rather than blindly restoring V439 or publishing the
latest higher-scoring allocator.

`CAPITAL-RELEASE-RESULTS-2026-09-05.md` now isolates that funding priority with a Claude-assisted
two-worker ceiling. Chopping begins on turn 5 instead of 116 in the putibuzu development game,
but the real screen remains 1/0/2 and local match points fall by eight. The variant is not selected
or published; default expansion remains four workers. All 435 tests pass. Next examine meaningful
opening capacity and timely scarce-fruit denial; neither indiscriminate expansion nor simply
forbidding it has established the requested strength.

`SCARCE-DENIAL-RESULTS-2026-09-05.md` tests scarce-fruit denial in that released two-worker
controller. It wins 179–86 on the putibuzu development map, but fresh confirmation versus V439
ends 1/0/5 for both, with zero rank-seven/eight wins. No publication. All 456 tests pass.
`TRAIN-EGRESS-FINDING-2026-09-05.md` separately disproves the prior MOVE/TRAIN ordering assumption;
the timing correction is not bundled into this failed candidate. Public strategy cross-checks and
a bounded read-only inventory of neighboring learning assets inform the next architectural review.

Before restoration, `bot.rs` was V543, a dual-controller standalone bot. It used a repaired R1FA-style
four-worker economy by default and latches to the exact V468 policy when an opponent
reveals its distinctive early pure-chopper opening. Only the selected controller is
evaluated each turn, and hot-path territory tests use constant-time symmetric distance
instead of rebuilding path maps for every candidate tree.

The prior compact V543 platform artifact was 99,825 bytes / UTF-16
units and its SHA-256 is
`922a233526ed590dafcc6302461de2dafef720fb003bd2359f55dfd93ac1b4a7`.

On a sealed 384-game panel it raised mean own score from 228.1 to 377.0, wood from
49.0 to 82.8, and paired margin by 95.94. Both seats improved by more than 92 margin;
there were zero critical or unclassified command issues. V543's readable and compact
programs emitted identical commands on 160 archived games. Full design and validation is
in `ADAPTIVE-R1FA-RESULTS-2026-09-04.md`.

V543 was accepted as platform submission `41242929`, agent `6701731`, on 2026-09-04, replacing the
timing-unsafe V542 agent `6701716`. The original V468 resident (`6699467`) had completed at
19.23 / rank 60. Rank 7 was 26.99 when the adaptive line was first submitted.

V543 subsequently completed all 160 games at **13.92 / rank 155 of 177 in Legend**; rank 7 was
still 26.99 at the mature reading. Its active games were positive against sub-14 opponents but
averaged -50.3 margin against rating-14+ opponents. The rating-18+ opponents produced 61.0 plants
and 160.7 wood to V543's 17.7 and 86.3, so the local holdout gain did not close the public field's
parallel-orchard gap. The complete replay archive and analysis are recorded in
`V543-MATURE-PLATFORM-RESULTS-2026-09-04.md`.

The subsequent V545 startup-hardening experiment removed both compatibility controllers and
reduced compact source to 70,981 units, but it failed the standard gate: it was 77.0 points behind
V468 at turn 100 and increased losses from 12 to 27 in 192 paired games. V543 therefore remains the
published artifact. Details are in `V545-FIRST-OUTPUT-HARDENING-RESULTS-2026-09-04.md`.

V546 then raised the R1FA live-tree target from six to ten, directly addressing the live agent's
dense-planting gap. Against exact V543 it gained 18.21 margin, 7.21 wood and three outcomes per game
panel, but retained the economy controller's −72.9 turn-100 deficit versus V468. It therefore failed
the absolute gate and was not published. See `V546-DENSE-SOURCE-ORCHARD-RESULTS-2026-09-04.md`.

V547 tested whether later-worker spending caused that opening deficit by delaying trolls three and
four until turn 101. It recovered 18.9 points at turn 100 versus V546, but lost 20.3 at turn 200,
19.7 final score, and two outcomes; it still trailed V468 by 54.0 at turn 100. The fixed delay was
rejected and V543 remains canonical. See `V547-FUND-BEFORE-HIRE-RESULTS-2026-09-04.md`.

## Build and smoke test

```sh
TMPDIR=/data/separate_troll_farm-working/tmp rustc --edition=2021 -O submission.rs -o /data/separate_troll_farm-working/current-bot
/data/separate_troll_farm-working/current-bot < /home/tarstars/prj/troll_farm/tests/sample_input.txt
```

The v1 farm candidate was paired against the resident on three disjoint sets of 24 real
ladder maps, with identical starting draws and scripted opponents. Aggregate
own-score delta: **+6,538 over 72 games (+90.81/game)**. It improved all 72 maps,
with zero invalid commands.

| map slice | candidate minus resident own score |
|---|---:|
| third-troll | +2,335 |
| the-floor | +1,743 |
| apple-farm | +2,460 |

`duel.py` then ran the two complete v1 bots directly against each other on those maps,
in both seats. The candidate scored **99 wins, 14 ties, and 31 losses** (68.8% wins)
across 144 games, with mean margins +30.46 and +36.88 by seat. The final v2 artifact
also completed a generated 40-map/two-seat fuzz panel with zero command errors; its
mean deltas were +0.08 own score and -0.23 margin versus the resident. The panel's
historical behavior-specific gate reports BLOCK because it was
written to require byte-identical behavior from a different candidate, not because
of protocol failure.

Readable and compacted v2 sources produced byte-identical command streams on eight
full 300-turn games. V2 itself scored 63 wins, 38 ties, and 43 losses against the
resident across both seats, with a +1.10 aggregate mean margin and zero command
errors. These are local results, not a ladder-rating claim; completion
still requires a mature platform read at least two rating points above the 18.19
resident reference, or ladder rank 7.

Against Orchard 6, the source project's newest measured ladder bot, the candidate
won **117/144** direct games across both seats (81.3%), with mean margins +67.38 and
+58.71. `platform_run.py` waits for the pre-existing Orchard 7 queue to finish,
checks that no queue item remains, submits `submission.rs` exactly once, and retains
the timed room readings in this directory.

Against final queued design Orchard 7, the v1 candidate won **125/144** direct games
across both seats (86.8%), with mean margins +61.71 and +56.92 and no command errors.

V1 was accepted as platform submission `41210451` and reached 13.20/rank 160 at
age 30.1 minutes; 68 retained early replays were 33–35 with mean margin −3.3 against
opponents averaging rating 14.12. Because that trajectory could not reach the
20.19 target, it was replaced by guarded v2 submission `41210542`. Its timed
readings are retained in `platform-readings-v2.jsonl`.

## Mature platform result

V2 is live as agent `6671640`. At age **65.1 minutes**, its mature platform reading
was **23.03, rank 32/177**. That is **+4.84 points** over the same-day resident
reference of 18.19, exceeding the requested +2 target by another 2.84 points. The
accepted one-shot submission record is `platform-submission-v2.json`.

## Working rule for platform waits

Do not spend platform rollout or ranking-stabilization time only waiting. Keep the
exact submitted agent monitored in the background, and use the wait for useful,
safe work such as replay analysis, a focused local test, or preparing the next
small candidate. Do not replace the live agent until its 160 games are archived
and its platform ranking has finished stabilizing at 100/100. Before starting a
local comparison, check the retained candidates for an identical earlier change;
stop immediately if the test would only repeat old work.

## Current cycle

V108 finished at **22.90, rank 32**. All 160 games are archived in
`public-v108-v54-value-banana-supply-agent6677556/` with no download failures.
The added banana supply raised our score only slightly but raised opponents much
more, so it was removed. The orchard cost filter (V114) and ownership-only tree
commitment (V116) also lost their local comparisons and were rejected.
An attempt to buy a very cheap third worker only from spare supplies never fired
in 384 local games, confirming that a third worker would require a costly farming
detour rather than use otherwise-wasted stock.
Staying longer on non-primary trees that an opponent was also cutting lost 492
total margin across 384 local games, mainly because it helped those trees fall
sooner and gave opponents more wood. That change was also rejected.
Using a top player's learned tree preference only as a small tie-break also failed
its 96-game screen: our score stayed nearly flat while opponents gained 513 points
in total. The current simple wood-per-trip choice remains better in this bot.
An audit found that early opponent farms, especially apples near their shack, were
more common in large losses. Giving those apples extra cutting priority nevertheless
lost 380 total margin in a 96-game paired screen: the detour reduced our score and
allowed opponents to score more. The observed farm pattern is therefore a symptom of
strong opponents, not a useful route change for this bot.
Removing the bot's existing small preference for nearby opponent-planted trees was
also much worse: opponents gained 1,336 points across the 96-game screen and total
margin fell by 972. The current small preference is the useful middle ground; both
removing it and increasing it have now failed.
V100's lean banana farm had activated in five archived games that were all large
losses, but a direct no-farm comparison showed that the correlation was misleading.
Disabling the farm changed five of 384 paired games and lost 77 total margin. Removing
the entire farm is therefore rejected; any follow-up should repair a concrete action
seen in its replays instead.
Requiring enough enemy-free time for the first banana harvest and bank was tested as
that concrete repair. It suppressed the same rare farm starts, changed six command
streams, and again lost 77 total margin over 384 games. A fixed start-time threshold
therefore does not solve the weak opening seen in the replay and was rejected.
Keeping the mother farmer on the neighboring bank cell while the banana grows also
changed only five of 384 games. It lost eight total margin and did not increase the
harvest count. This removes the visible wandering but is neutral by itself.
Combining that nearby wait with the stricter first-harvest start rule still lost the
same 77 total margin and produced 34 fewer harvests. The replay diagnosis is real,
but a fixed time cutoff cancels useful farms as well as the visibly bad one.
Harvesting ripe mother fruit before an emergency shutdown was also tested. It raised
our score by 38 over 384 games, but delaying the chop let opponents gain 71, reducing
total margin by 33. The immediate shutdown chop is therefore retained for defense.
The exact V125 archive corrected a false-positive in the farm analyzer: only three
real lean farms started, and all three lost. Each planted one mother banana, harvested
it zero times, planted no child, and eventually cut the mother down. Those starts had
15--22 trees already on the map. Restricting new farms to maps with at most 14 trees
was therefore tested with the priority tuple; it changed five of 1,536 games and gained
four total margin. This is essentially neutral locally, while excluding all three V125
farm failures. Keeping the farmer directly on the growing mother also changed five
games but added no harvests and lost 12 total margin over 384 games, so that visual
wandering repair was rejected.

V115 was a clean recheck of V54 and finished mature at **23.53, rank 29**. Its
160 games are archived in `public-v115-v54-recheck-agent6677635/` with no download
failures. The run produced 91 wins, 68 losses, and one tie; 25 large losses held
the rating down despite a small positive average game margin.

V121 was another byte-identical V54 recheck. It finished mature at **22.92, rank
31**; its 160 games are archived in `public-v121-v54-recheck-agent6677694/` with
no download failures. It produced 89 wins, 70 losses, and one tie.

V125 was the exact V100 recheck: submission `41216602`, agent `6677755`. It
finished mature at **23.76, rank 26**. All 160 games are archived in
`public-v125-v100-recheck-agent6677755/` with no download failures; the run had
95 wins, 61 losses, and four ties.

V133 was the priority-tuple candidate: submission `41216748`, agent `6677822`.
It finished mature at **22.30, rank 35**. All 160 games are archived in
`public-v133-priority-tuple-agent6677822/` with no download failures; the run had
82 wins, 72 losses, and six ties. No real lean farm started in this run, so its low
result cannot be attributed to the farm.

V137 is the sparse-map farm guard: submission `41216910`, agent `6677924`. It
keeps the tuple selector and allows a lean farm to start only with at most 14 trees.
It finished mature at **23.35, rank 28**. All 160 games are archived in
`public-v137-tree-sparse-farm-agent6677924/` with no download failures; the run had
95 wins, 64 losses, and one tie. The old farm started once, planted one mother at
turn 6, harvested it zero times, and eventually chopped it down in a 115-point loss.
The sparse-map rule reduced activations but did not repair the farm lifecycle.

V140 is the guarded compact-farm candidate: submission `41217058`, agent `6677957`.
It finished mature at **21.52, rank 37**. All 160 games are archived in
`public-v140-guarded-compact-tuple-agent6677957/` with no download failures; the run had
93 wins, 64 losses, and three ties. No compact farm started. The strict enemy-distance
check was the final observable blocker in every game that otherwise passed the start
checks. The apple orchard ran in 20 games; those games averaged a 37.4-point loss, but
the earlier direct no-orchard screen lost 837 points over 96 games, so that correlation
does not justify removing the orchard wholesale.

V152 is the early-tuple/scalar-endgame candidate: submission `41217305`, agent
`6678035`. It keeps V140's behavior before turn 200 and restores scalar pair selection
afterward. Its exact artifact checksum is
`ed24048928a9fdc88fa73deb890909ec470bce8401dd5e36db84ea27abe3ceef` (78,294 bytes).
It finished mature at **22.72, rank 30**. All 160 games are archived in
`public-v152-early-tuple-scalar-endgame-agent6678035/` with no download failures; the
replay package SHA-256 is
`6042cc486a57aaa735a8691b9d463794e7da85a163de2389a0f40e5c11d03e11`.

Five V133 games against `_H3R0_` clarified its banana factory. Its two 600+ scores
used a 2/2/1/1 harvester followed by a 2/4/0/3 chopper on turns 94 or 111; the three
games without that strong chopper scored only 6--46. Our retained three-worker factory
already has this kind of strong-chopper branch and previously lost heavily locally,
so the replay pattern is useful evidence but not a reason to repeat that old candidate.

A direct comparison with rating-24+ opponents found that V115's losses were short
by about 21 wood and 12 fruit on average, while those opponents often reached three
workers. Earlier tests showed that funding our own third worker requires a harmful
farming detour, so that observation does not justify repeating the worker experiment.
The latest archive made the pattern more precise: strong opponents that did scale
bought their third worker around turn 68, while our worker choices ignored harvesting.
Changing the old funding branch to wait for an MSz-style 2/4/1/2 worker nevertheless
lost 6,417 total margin in a 96-game screen and reached three workers only 11 times;
its exposed fruit farm helped opponents more than us. That branch remains rejected.
V100 remained the best distinct fallback: it previously finished at 24.03 and performed
better against many strong opponents. The checksum-locked script waited for V121's full
160-game archive and 100/100 stabilization, then submitted the exact V100 artifact as
the current V125 recheck.
The previously missing direct V100-versus-V54 comparison also passed: V100 gained 91
total margin over 384 paired games, changing only six games (five better, one worse).
That isolates the small benefit to V100's guarded lean-farm behavior and confirms it as
the next distinct fallback rather than another identical V54 retry.

The proposed priority tuple was also screened directly. It ranks the two chosen jobs
by highest priority, then second-highest priority, and uses the old combined score only
inside the same priority pair. Across 1,536 games it changed 25 command streams, removed
1,502 waits, and gained 81 total margin (+0.05/game). It repeatedly gave an idle worker
useful work, so the mechanism is valid, although the measured gain is small. After
V125 finished mature below the target and its exact 160 games were archived, the
standalone `candidate-v127-priority-tuple.min.rs` artifact was submitted as V133.

The replacement compact banana farm follows the project geometry directly: two diagonal
mother trees for repeated harvesting, two neighboring chop plots, and one hut door kept
free for banking. Combined with the tuple selector, V138 gained 668 total margin across
384 development comparisons. It then gained 2,031 on the untouched 1,152-game confirmation
set (+1.76/game, 95% interval +0.73 to +2.80); our score rose by 5,918 while opponents rose
by 3,887. The farm therefore creates value for both sides but retained a positive net gain.
A pre-existing stricter start variant, requiring both workers closer to home and more enemy
clearance, changed only five development games and improved the 384-game result by another
405 points. V139 then gained 2,135 margin on the same 1,152-game confirmation panel, 104 more
than V138 while changing only three games. Across all 1,536 comparisons V139 gained 3,208
total margin (+2.09/game). It is the qualified next candidate; compact-gold remained its weak
opponent family, while five of the six families were neutral or positive.

The tuple was then refactored locally so every job stores its priority separately from its
quality score instead of inferring priority from score thresholds. The explicit-priority copy
produced byte-identical panel rows and command streams to V139 across all 384 development
comparisons. This is a behavior-neutral cleanup and a safer base for any later priority tuning;
it is not a reason to replace V140 by itself.

A stricter follow-up compared quality separately at each priority level, so a lower-priority
job could never compensate for a slightly worse higher-priority job. That version changed 16
of 384 development games and lost 45 total margin versus V139 (six better, ten worse). It was
too rigid and was rejected. The retained rule is priority pattern first, then combined quality
as the tie-break.

Lowering the compact farm's enemy-distance limit from 18 turns to 10 allowed one extra
development start, but it lost 199 margin. The banana plan took both workers away from an
apple orchard and turned a 266-67 win into a 128-128 tie, so this looser V143 variant was
rejected. Running the inner orchard decision before the banana start removed that collapse,
but also removed every new farm start: V145 was identical to V139 in all 384 development
comparisons. This shows that the remaining interference is between the two whole plans, not
between ordinary jobs inside one plan.

The explicit tuple comparison was also extended to the one-worker and three-or-more-worker
paths, which had still sorted by scalar score. V146 was identical to V139 in all 384
development comparisons. The cleanup is sound, but the current numeric score bands already
preserve those priorities in observed games, so this is not a measurable improvement.

A softer V147 tuple protected only the highest-priority job, then chose by combined quality
instead of also protecting the second job's priority. It changed five of 384 development
games and lost 16 total margin versus V139. The current two-level priority pattern remains
the best measured compromise.

The tuple's rare late-game changes were then isolated. In the older V127 comparison, tuple
changes before turn 200 gained 134 points, while changes from turn 200 onward lost 53 because
keeping both workers busy could start trips too late to repay their travel. V148 therefore
uses the tuple before turn 200 and the scalar pair score afterward. Against V139 it was neutral
across 384 development comparisons and gained 23 points across the 1,152-game larger panel,
changing only 11 command streams in all 1,536 games. This is a small, behaviorally focused
improvement rather than a large strategy change.

V140's worst orchard replay prompted three focused response screens. Releasing the orchard
worker when six enemy banana trees were alive lost 115 points in 96 games. Releasing after
22 observed enemy banana plantings lost 30, and adding extra cutting preference for nearby
enemy bananas lost 801. All three were rejected. The replay's wood gap is real, but these
simple reactions damage otherwise useful work.

An orchard-first compact farm limited to sparse maps and enemy arrival beyond eight turns
was behavior-identical to V139 while workers had to remain within two cells of home. Widening
that worker limit to four finally started four extra farms in the 96-game screen, but lost
189 total margin. The farm still displaced valuable normal work and was rejected. Separately,
letting the apple worker fill spare carrying capacity before banking changed two games and
lost six points; immediate apple banking remains slightly better.

Making that same compact farm genuinely low priority—starting it only when both selected
workers would otherwise wait—was safe but nearly inactive. V157 improved one development
game by eight points and was identical to V139 throughout the larger confirmation set. Removing
the sparse-map limit in V158 produced exactly the same result: one eight-point improvement and
no changes in the other 1,440 comparisons. This is the right way to prevent the farm from
stealing important work, but it is not yet a large enough improvement to submit.

Reducing the wider orchard-first farm to one mother tree and one neighboring chop plot did
not fix its timing problem. V159 changed 15 games in the wider development screen and lost
1,102 total margin. A smaller plantation is desirable, but it must still start only when it
will not replace better work, so this variant was rejected.

V152's exact archive again contained no compact-farm starts. The run finished 81 wins,
77 losses, and two ties with a mean margin of -2.93. Unlike V140, its eight apple-orchard
games were useful: they averaged +25.9 margin and banked large amounts of fruit. Against
stronger opponents, losses averaged about 15 fewer wood, 23 fewer fruit, and only two workers
versus 2.64. The current gap is therefore production and scaling, not the apple orchard.

Two direct responses to the replay's uncollected banana were also screened. Giving every
near-home banana harvest a higher priority changed 60 of 96 games and lost 712 margin because
workers took harmful detours. Giving the bonus only while already standing on a ripe banana
changed four games and lost 19. Tracking only bananas planted by our bot was behavior-neutral
in the same screen. Harvesting is useful, but a blanket priority rule is not enough; it needs
a coordinated production plan.

Replacing the successful water-adjacent apple orchard with one banana mother was also rejected:
banana produces fruit more slowly on that terrain, and V163 lost 547 margin in 96 games. Copying
the turn-one cheap hybrid worker from a strong replay without copying its complete production
plan was much worse; V164 lost 8,675. The worker and its job plan cannot be tuned independently.

Starting the original two-mother/two-plot compact farm earlier exposed its lifecycle bug. The
farmer wandered while mothers grew, and the cutter repeatedly targeted protected young plots,
which the guard converted to waits. V166 stationed the farmer and redirected the cutter to normal
trees; this reduced the first screen's loss from 125 to 44 points. Removing the theft shutdown did
not help, and allowing starts before the opponent trained added bad farms. Those variants were
rejected, but the action repair is retained for the next design.

V169 is the first genuinely lean loop: one diagonal mother can start from one seed, the farmer
stays and harvests it, and only then supplies one neighboring chop plot while the cutter continues
ordinary work. Its first 96-game screen changed three games, improved all three, and gained 57
total margin. In the two main farm games it issued 18--20 mother harvests and 19--21 near-home
plants instead of the old one harvest and two plants. The wider 288-game screen exposed fourteen
regressions and lost 1,102 margin, however: the loop raised our output in several games but let
production-oriented opponents compound much faster. V169 itself was rejected.

Blocking the farm after any observed opponent crop reduced that wider loss to 144 points, but an
archive audit estimated only one eligible platform game, so V170 was both negative and too narrow.
Restoring the cutter's existing opponent-crop preference inside the farm reduced the ungated loss
from 1,102 to 807 points. This confirms that production and suppression must stay coupled, but V171
still failed. V172 adds a general race check: after 30 farm turns, clean up if the opponent's bank
has grown faster than ours. Its first screen retained V171's three improvements and +69 margin;
the wider loss fell again to 547 points, but the check also stopped a valuable farm early, so it
was rejected. Making the farmer hold its renewable seed instead of banking it was correct as a
lifecycle invariant but lost 19 points in the first screen; with only one fixed plot, waiting for
that plot cost more than the preserved seed returned.

V174 keeps the lean loop but doubles the existing nearby-opponent-crop preference only for the
farm's cutter. It improved all three changed first-screen games and raised the gain from +69 to
+122. The wider screen lost 802 points, with five better outcomes and thirteen worse, so V174 was
rejected. V175 keeps one mother banana but gives its cutter two neighboring chop plots. This is
still a small three-cell farm, but the second plot may consume seeds more steadily instead of
leaving harvested fruit unused. It produced exactly the same commands and the same 807-point wider
loss as the one-plot V171, so no tested geometry made the second plot usable and V175 was rejected.

The V176 start guard targets the losing pattern without banning farms altogether. It starts by turn
60 and only before any newly planted crop is growing. The wider V171 trace indicates that these two
conditions would skip the largest losses against opponents whose plantations were already underway,
while preserving the early resident and non-farming-opponent gains. The result matches that model:
the first screen retained all three gains for +69, and the wider screen changed nine games, improved
five, worsened four, and gained 91 total margin. All catastrophic starts were removed. An exact
observable audit of V152's 160 public games found six likely V176 starts; five were already wins and
one was a loss, so the change is safe enough for confirmation but probably too narrow to reach the
score target alone. The 1,152-game confirmation rejected that optimism: V176 changed 32 games,
improved 15, worsened 16, and lost 800 total margin. Several compact-production opponents still
compounded while our farmer waited, so the start guard is not sufficient.

The remaining V176 farm games also reveal an avoidable scheduling cost: compared with normal play,
the farm adds between 8 and 87 waits per game while the farmer stands beside a growing or cooling
mother. V178 expresses the intended tuple behavior more directly. A ready farm action (plant or
harvest) may replace the normal job; when no farm action is ready, the farmer keeps the inner bot's
best ordinary command. This isolates job priority from the farm's start guard and will be screened
separately after V176's confirmation.

V178 passed both development screens. It gained 45 points in the first 96 games and 23 in the
wider 288 games, with five better outcomes and four worse in the latter. This is less farm profit
than V176, but it repaired the earlier MyBot loss and directly removes the idle pattern behind the
largest confirmation failures. The large confirmation improved V176's loss from 800 to 563 points,
but still had 16 better and 15 worse outcomes with repeated compact-opponent collapses, so V178 was
rejected. V182 now tests a readiness window: use normal work during early growth/cooldown, then
return when the mother is within two turns of producing fruit. It retained +69 in the first screen
and gained 43 in the wider screen, but removed only two to four waits in the initial farm games and
made one Legend loss 46 points worse. It did not plausibly repair V176's large-panel failure and was
stopped before confirmation. V186 keeps the same return window but explicitly selects a non-farm
tree when the protected inner command would otherwise become a wait. It gained 57 points in the
first screen but lost 8 in the wider screen, with only two improvements and seven regressions, so
it was rejected.

V187--V194 test a much smaller design: one banana tree on a tent entrance. The bot remembers how
many bananas from that tree were banked. After three, passing trolls chop the tree and bank its
wood, returning the cell to empty. No troll is sent to the farm; normal work determines all travel.
The first versions accidentally reserved the entrance before the farm existed or reacted merely to
a troll standing there. Those mistakes changed ordinary work broadly and lost 3,056, 2,763, and
757 points in the first screen. V190 waited for a truly idle troll and was safe (+7), but activated
only twice and did not implement the intended action tax.

V191 applies the tax whenever a troll is on the entrance, and V192 corrects that trigger to a real
arrival from another cell. Both were rejected: they delayed the opening chore on almost every map
and lost 2,688 and 2,333 points against V148. V193 triggers only on return traffic, after the normal
chore has reached the tent. It preserves the opening and completes each farm transaction before the
troll resumes work, but the farm still lost 1,976 points: our own score was nearly unchanged while
opponents profited from our later arrival at contested trees. V194 starts the same state machine
only after a third troll exists. This was safe but too rare: it activated once in the 96-game screen
for +8 and never activated in the exact 288-game wider screen. The entrance state machine is now a
working reference implementation, but this two-troll bot cannot afford to run it generally.

V195--V199 tried to make the third troll available without disturbing the first two. Merely asking
for it did nothing because the required fruit never accumulated. Holding fruit back still did not
train it; sending one worker to collect the missing fruit trained a third troll in 40 of 96 games
but lost 2,720 points. Waiting until the opponent already had three trolls also lost 358. The game
accepts only one action from each troll per turn, so the farm action cannot be added for free beside
the troll's ordinary action.

V200 plants the entrance tree with a banana that a capable troll is already carrying home. This is
the lightest real tax found: it changes one return action instead of sending a worker to fetch a
seed. It reduced V193's loss to 320 points in the first 96 games. Restricting it to close maps looked
good in the small screen (+108) but failed the wider screen (-324), so that rule was rejected.
Waiting for several ripe fruits, requiring a pure banana load, and allowing only one farm cycle did
not change any result. The one-cycle test proved that none of those farms completed the full loop.

Focused traces found two separate causes. First, counting all doorway traffic could select a door
used mainly by a cutter that cannot harvest; counting returns by the same troll did not fix the
result and lost 462 points. Second, enemy trolls often reached the entrance and cut the young tree
before its first fruit. A traced game that improved by 14 points was actually using the tree as bait,
not as a farm. Letting the normal bank deposit finish before starting the farm added another delayed
turn and lost 498 points.

V210--V211 therefore require the planting troll to revisit the same door, to have both harvesting
and chopping skill, and to have enough distance from the nearest enemy cutter. An 18-turn safety
limit prevented every farm start. A 12-turn limit allowed one farm, which lost 11 points; the full
96-game result was -3 only because of one unrelated +8 change. The safe doorway needed by this exact
design does not occur often enough in the tested maps. These modules are kept as a faithful isolated
experiment, but none is submitted over V148.

V212 tried to split the first two trolls' skills so the fruit for a cheap third troll would be left
in the tent. It never trained the third troll and lost 6,341 points. I then returned to the old V20
three-troll factory, which really does train a third troll in 61 of 96 games. V213 raised our own
score by 3,456 points, but it helped opponents by 5,167 and finished 1,711 points behind V148.

V214 added V148's rule for quickly cutting nearby trees planted by the opponent. That single change
recovered 1,364 points: our gain rose to 3,583, the opponent gain fell to 3,930, and the remaining
loss was 347 over 96 games. Games that reached three trolls were +917; games stuck on two were
-1,264. This shows that the productive opening works only when it completes the third troll.

V215 restored job classes during the early game, but changed no command because the factory's fixed
jobs were already winning those choices. V216 made the third troll very cheap; it trained in 76
games but was too weak and lost 2,002 more than V214. V217 reduced only its carrying capacity; that
also lost 947 more and barely improved training frequency. V218 delayed late-game behavior from
turn 120 to turn 250 and lost 274 more. V214 remains the useful factory branch, but it failed the
first gate and was not promoted to wider tests or submitted.

The successful V214 third trolls arrived in waves. Those trained by turn 140 were worth +1,689
points, while later ones were worth -772 and games with no third troll were worth -1,264. That did
not make a safe deadline: V219 cancelled both funding and training after turn 140 and lost 468 more;
V220 stopped only special funding and lost 515 more. Once the orchard had been started, abandoning
it wasted more than accepting a late result.

V221 let the second capable troll help harvest only fruit missing from the training bill. It lost
3,915 more than V214 and completed fewer third trolls. The first two trolls' ordinary pressure is
therefore essential. Neither weaker workers, a deadline, nor shared funding repairs the factory's
remaining gap.

The archived E7a source was checked again as V222. It is the exact old program that once received
25.26 on the platform, but its recorded rank was 12 and it lost 1,220 points to V148 in the current
local screen. The old number is therefore not evidence that restoring it would reach the present
top ten.

V223--V227 checked other complete production programs and old harvest changes. The source-separated
three-troll factory produced much more for us, but produced still more for opponents and lost 504
points. Making it smaller was worse. The later GoldElite program also raised both scores but lost
4,264 margin. The older V162 harvest change generated exactly the same commands as V148, proving
that its useful behavior is already present in the current bot.

V228 gave extra preference to taking fruit only when the starter was already standing on a ripe
banana. It changed four of 96 games and lost 19 points because the carried fruit redirected many
later turns. V229--V230 implemented tuple priorities for every turn and every worker count. Both
produced exactly the same commands as V148 in all 96 games. Tuple priorities are a clean design,
but scalar weights are not crossing job boundaries in the observed V148 games.

V231 implements the entrance farm as a strict wrapper around normal work. The ordinary planner
runs first and knows nothing about the farm. Only a troll that really stepped onto the selected
entrance may spend its action on the next transition; the wrapper never sends, reserves, holds, or
reroutes a troll, and it merely observes later banking instead of forcing it. The first 96-game
screen gained 7 points. A separate 288-game screen gained 308 more: our score rose by 190 and the
opponents' score fell by 118, with no critical errors. The 1,152-game confirmation gained another
784 points. Across all 1,536 paired games it gained 1,099 points, so the exact compact source was
submitted once as platform submission 41218295 (agent 6678547). It matured at **24.01, rank 25**
after all 160 games and 100/100 stabilization. All replays were archived with zero failures in
`public-v231-strict-arrival-tax-fsm-agent6678547/`.

Replay inspection found an important limit: V231 plants the entrance banana, but its ordinary
planner cuts that tree before any fruit is taken. Across the first 120 platform replays, our bot
harvested zero bananas from any banana planted on a hut door; opponents harvested from those trees
in two games. Its measured gain is therefore from a cheap disposable entrance tree, not from the
requested three-banana cycle. V232 permanently hid
the farm tree from normal chopping and lost 498 points in 96 games. V233 hid it only while a troll
was standing there, but workers still travelled toward it and then refused to cut; it lost 2,197.
V234 gave the ordinary planner an empty-looking farm cell. That caused repeated planting attempts
and lost 641. V235 kept the cell occupied while hiding the tree as a job; it stopped the repeated
planting but still lost 306 because preserving the tree displaced too much useful work. These four
versions were rejected. They confirm that the farm must remain only an arrival tax, while also
showing that a protected three-fruit cycle is not yet cheap enough for the current two-worker bot.

V236 skipped the entrance tax while our score was behind. It improved the first screen from +7 to
+18, but scored +297 on the independent wider screen where V231 scored +308. The two versions were
exactly tied at +315 across those 384 development games. The 1,152-game confirmation then gained
869, versus V231's 784, with no critical errors. Across all 1,536 games V236 gained 1,184, an
85-point improvement over V231. Its 84,516-byte compact artifact matched the readable source in
every command of the 96-game equivalence check and was accepted once as submission 41218425,
agent 6678620. It matured at **23.05, rank 29** after all 160 games and 100/100 stabilization.
All replays were archived with zero failures in
`public-v236-ahead-only-arrival-tax-fsm-agent6678620/`.
V237 copied the balanced 2/2/2/1 worker from a new strong-opponent replay into the complete factory
plan. Even when that worker trained by turn 3, the plan helped opponents more than us. Overall our
score rose by 1,699, opponents rose by 5,184, and margin fell by 3,485 in 96 games. The worker and
factory were rejected. A 105-game live audit instead showed that V231 won 26 of the 30 games where
its existing adaptive second troll trained by turn 3. The larger weakness is later scaling: V231
never bought a third troll, while opponents buying three or more extra trolls produced the worst
loss group.

V238 combined the entrance wrapper with the strongest distinct older V100 base. It lost 327 margin
to V148 in 96 games. A direct V238-versus-V100 isolation was identical in every command, showing
that V100's own farm consumed or redirected the relevant banana before the entrance tax could ever
fire; the loss belonged to the older base, not an interaction worth tuning. Two existing scaling
opponent models were also screened directly as candidate policies. The Legend proxy lost 15,090
margin and the Norx three-worker proxy lost 19,928 over 96 games. They are useful difficult opponent
models, but are not viable standalone ladder bots. These broad architecture substitutions were
closed without promotion.

V241--V244 tested whether the weak live openings were caused by one-chop workers. Merely preferring
two chop changed almost nothing. Requiring it safely lost 2,880 margin in 96 games, so stronger
woodcutting cannot be forced without damaging the opening. V245 protected the entrance tree so the
three-fruit cycle could run, but lost 287 margin; limiting that protected cycle to turns 100--124
still lost 66. The protection cost remains larger than the fruit return. V247 then collected only
the missing supplies for a cheap third worker. It trained one in 31 games but lost 3,126 margin,
confirming that even this focused collection trip cripples normal production.

V248 removes only the apple orchard's rule that banned starts when natural trees were close to the
tent. It was unchanged in the first 96 games. In the next 288 paired games it gained 1,808 margin:
29 games improved, two worsened, our score rose by 2,259, and every opponent family was positive.
The separate 1,152-game confirmation gained another 3,049 margin: 49 games improved, seven
worsened, our score rose by 4,325, and every opponent family was again positive. Across all 1,536
games V248 gained 4,857 margin (+3.16/game), with no critical errors. Its 84,482-byte compact source
matched the readable source in every command of the 96-game equivalence check. V248 is qualified
and was accepted once as submission 41218538, agent 6678643, after V236 finished and was archived.
It matured at score 22.45, rank 32, after all 160 games and both stabilization counters reached
100/100, so it missed the target. All 160 games were then archived without failures in
`public-v248-dense-map-apple-orchard-agent6678643`; the battle index SHA-256 is
`50ff9f6e7842f3cc0f53d6cd358b58102507139487be3c72b2f18e83483638f1` and the compressed games
SHA-256 is `6461e14a2131c2fac133a3507be5181aef3ecb003d790be1322a634da0a5b68d`.
V249 separately removed the preference for a contested wood tree over the apple orchard; it changed
none of the first 96 games.

Running V236's exact 160 archived trajectories through both programs showed four first-command
changes from V248. All four observed V236 games were losses, including margins -575 and -238. This
is not a counterfactual score, but it confirms that the new orchard permission targets the archived
failure group rather than broad successful play. V250 removes the next orchard veto as well: it no
longer gives up the orchard merely because the starter could win a contested natural tree first.
Against V248 it was unchanged in the first 96 games, then gained 329 margin in the next 288, with
five improvements, no regressions, and no errors. The separate 1,152-game confirmation gained 148
more. Across all 1,536 games V250 gained 477 margin (+0.31/game): 17 games improved, three worsened,
and there were no critical errors. Its 84,431-byte compact source matched the readable source in
every command of the 96-game equivalence check. On the V236 archive it changed three first commands:
two were observed losses and one was an observed win. V250 is qualified as a follow-up if V248
finishes below the target.

V251 keeps V250's two orchard permissions and makes one further cautious change: it allows the
orchard when the nearest enemy needs at least seven moves to reach it, instead of at least nine.
The first 96 paired games were unchanged. The next 288 gained 476 margin. The independent
1,152-game confirmation gained 866 more, and every opponent family was positive. Across all 1,536
games V251 gained 1,342 margin over V250 (+0.87/game): 30 games improved, nine worsened, our score
rose by 1,649, and there were no critical errors. Its compact source is 84,431 bytes with SHA-256
`6433b239a2d69855a7d17d8cab532247585b0b0488984ffa424b656734f56a03`.

The original V250 compact replay module was found to contain the preceding version, so its small
equivalence check was not sufficient. The replay module was corrected before submission. The
exact V251 compact source then matched the readable V251 source in all commands and scores across
the 13 maps where V251 changed behavior: 156 paired games and zero differences. On V236's archived
platform trajectories, V251 changed five first commands, all in observed losses. This remains a
targeting check rather than a counterfactual score. V251 was accepted exactly once as submission
41218608, agent 6678709. It matured at score 23.81, rank 27, after all 160 games and 100/100
stabilization, so it missed the target. All 160 games were archived without failures in
`public-v251-enemy-eta6-apple-orchard-agent6678709`; the battle index SHA-256 is
`02ed8e06fc29a997719ef69f6c1bdc788bd7a15d6c77293c3c822b1b0e9c0e3f` and the compressed games
SHA-256 is `30c4c074c951b816ef5faddcf3869a2ca4a81ceac494792868bce9dd7f87eb8c`.

V252 tested tuple-first job selection for the whole game instead of returning to the scalar score
after turn 200. It changed only 13 late commands across 384 games and changed no final score, so it
was closed as harmless but ineffective. V253--V256 then reduced the orchard's remaining static
enemy-door distance in cautious steps. A duplicated fixed distance check was found and corrected in
the experiment. Distance 10 was a no-op; distances 9 and 8 improved the development screens; the
dynamic enemy-arrival check made distance 7 the strongest safe endpoint.

V256 changes only the two copies of that static distance, from 11 to 7. In 96 paired games it gained
970 margin; in the next 288 it gained another 970; and in the independent 1,152-game confirmation
it gained 7,525. Every opponent family was positive in every aggregate screen. Across all 1,536
games V256 gained 9,465 margin over V251 (+6.16/game): 165 games improved, 28 worsened, our score
rose by 14,498, and there were no critical errors. Its exact 84,429-byte compact source has SHA-256
`ef005bd1379411fe84cab268e45afe064d4a04b4f9fde4de8cacde16bec78445` and matched the readable
source in all commands and scores on the four behavior-changing development maps: 48 paired games
and zero differences. On V248's archived states it changed ten games, six observed losses and four
wins, including losses by 308, 201, and 157 points. The later direct audit on V251's own archive
again found ten changed games, six observed losses and four wins. These are targeting checks, not
counterfactual scores. V256 was accepted exactly once as submission 41218724, agent 6678874.
It matured at score 23.65, rank 28, after all 160 games and 100/100 stabilization, so it missed the
target. All games were archived without failures in
`public-v256-enemy-door7-apple-orchard-agent6678874`; the battle index SHA-256 is
`48a7c2cd1015345d5332e9db15c9089555fc2f19cfda45953d6a4e96e4efe787` and the compressed games
SHA-256 is `ab1371a5a7b034b34d6e14227f32e74b16bd0cb44a9916de60c29efaa00eca0a`.

The mature replay audit showed that V256 still improved raw play even though its rating did not:
average margin rose from V251's +0.4 to +5.4 and banked fruit rose from 23.0 to 27.3. Its orchard
activated in 44 games, averaging +9.1 margin and 95.1 banked fruit, versus +4.0 margin without an
orchard. The remaining losses are concentrated against opponents with three or four workers; the
extra orchard supplies created only two no-detour third-worker opportunities in 160 games.

V257 lowers the last static distance step from 7 to 6 while retaining the live rule that the nearest
enemy must need more than six moves. It gained 866 margin in the first 96 paired games with eight
improvements and no regressions; the next 288 games had no boundary layout and were unchanged. Its
84,429-byte compact artifact has SHA-256
`5817f68183bcfb5aae893923856fbb8f64c297cc472fd8b88543765e8993aa43` and exactly matched the
readable source on every changed development case. The independent 1,152-game confirmation gained
517 margin, with 11 improvements, four regressions, and no critical errors. Across all 1,536 games
V257 gained 1,383 (+0.90/game) over V256 with a positive 95% confidence interval. On V256's archive
it changed only two games, both observed wins. V257 qualified but was not submitted because V258
proved stronger before the next platform mutation.

V258 removes the remaining static distance rule entirely while retaining the live requirement that
the nearest enemy must need more than six moves. It was unchanged in the first 96 paired games,
gained 245 in the next 288, and gained 2,219 in the independent 1,152-game confirmation. Across all
1,536 games it gained 2,464 over V257 (+1.60/game): 31 games improved, four worsened, our score rose
by 2,848, every opponent family was positive in confirmation, and there were no critical errors.
Its exact 84,429-byte compact source has SHA-256
`d8cd9b288053482906e3f8515ed64a741df4845425f1f6c25a2adc0d1f557515` and matched the readable
source in all commands and scores on the two behavior-changing development maps. On V256's archive
it changed five games, all observed wins. V258 was accepted exactly once as submission 41219291,
agent 6679604. It matured at score 24.59, rank 21, after all 160 games and 100/100
stabilization, so it missed the target. All games were archived without failures in
`public-v258-dynamic-only-apple-orchard-agent6679604`; the battle index SHA-256 is
`a154ce4db76414b1e0efd64af436fcfd4d8782847e82d00d84b66ac1822de459` and the compressed games
SHA-256 is `f509b049f469dc2b5ec82034c4a690b04d1513b9f5709cd950e4d496f6d7ef5e`.

A later audit corrected the candidate-selection measure. Platform rating is driven by wins, draws,
and losses, not by the size of the final score margin. V257 gained 1,383 raw margin but changed no
win/draw/loss outcome across the 1,536 local games. V258 gained another 2,464 raw margin but had a
net change of -0.5 match point: one draw became a win, but one win became a loss. These versions
played some games more efficiently without providing evidence of a higher platform rating. New
candidates are therefore selected by match outcomes first and raw margin only as a safety check.

V259--V264 were the first outcome-focused follow-ups. Removing an obsolete orchard condition was
a no-op. Extending the orchard deadline, lowering the live enemy-arrival limit everywhere, and
raising preference for opponent-planted trees either lost matches or failed to create any. A broad
tree-preference increase was especially misleading: it created two wins but destroyed seven across
the development screens. These versions were rejected.

V266 carefully reopens the entrance-tree tax while our banked-score deficit is no more than eight.
It converts two losses to wins and two losses to draws across the 1,536 independent paired games,
with no lost wins: +1.0 match point in the first 96 games, +0.5 in the next 288, and +1.5 in the
1,152-game confirmation. Raw margin is essentially unchanged at +4 total, which is acceptable
because match outcomes are the platform measure. Its exact compact source is 84,431 bytes with
SHA-256 `6f30e231d0f23be670324b1c6945a0796353cc74d233f22fc752adeda1e17188`;
the readable source compacts back to that exact file and both forms compile. V266 was accepted
exactly once as submission 41219458, agent 6679799. It matured at score 22.85, rank 30, after all
160 games and 100/100 stabilization, so it missed the target. All games were archived without
failures in `public-v266-small-deficit-arrival-tax-agent6679799`; the battle index SHA-256 is
`553ee2a39687ede2713ed6eb684bb7c5ab340df352452f81b824aed490875013` and the compressed games
SHA-256 is `6f77b7f85e79015e8d9d156571a679da76ab7a561ffe33e2ada90f5beb7b72cf`.

V267--V269 explored allowing the apple orchard one move closer to an enemy. Restricting the change
to immediate openings looked safe in 384 development games, but the large confirmation exposed two
lost wins. The orchard addition and its combination with V266 were rejected; V266 remains the
stronger candidate. V270--V272 then narrowed a different opponent-tree pressure rule. Remembering a
one-worker opponent that led while holding at least six unused iron converted one loss to a win in
each development screen. V272's confirmation added +3.5 match points but exposed one lost win when
the pressure began at turn 40. V273 limits activation to turns 11--32. It retained every gain and
removed that regression: +1.0 match point in the first 96 games, +1.0 in the next 288, and +4.5 in
the independent 1,152-game confirmation. Across all 1,536 games V273 gains 6.5 match points, loses
no existing win, and adds 139 raw margin. V273 is qualified while V266 stabilizes; the direct
V266+V273 combination was checked separately rather than assumed to be additive.

V274 is that direct combination. One development game overlaps, so the gains are not perfectly
additive, but the complete result is stronger: +1.0 match point in the first 96 games, +1.5 in the
next 288, and +6.0 in the independent 1,152-game confirmation. Across all 1,536 games V274 gains
8.5 match points over V258, loses no existing win, and adds 134 raw margin. Its exact 84,746-byte
compact artifact has SHA-256
`9853ec415f46d0c5ee09e3fcdd8b57261f722893a7249e0bcc5cc6231a036e58`.
The readable source compacts back to that exact file; both forms compile and pass the empty-input
check. V274 is qualified and packaged as the next replacement if mature V266 misses the target.
After that miss, V274 was accepted exactly once as submission 41219594, agent 6679963. It finished
all 160 games and rank stabilization at **23.32, rank 28**, so it missed the target. All public
replays were archived without failures in
`public-v274-arrival-tax-and-early-crop-pressure-agent6679963`; the battle index SHA-256 is
`4d2148aa88dc59cf00b605e7adaa02143d1ddb6aac856e909117133605af2050` and the compressed games
SHA-256 is `9aa0d287bfb751a0f4c055861ff9f60dee9280e88f4148d7b7ca465431baa2c6`.

V275 widened the entrance-tax deficit limit from eight to twelve. It was unchanged across 384
development games, but the large confirmation reintroduced the known unsafe case and turned one
existing win into a loss; it was rejected. V276 raised the gated opponent-tree pressure from 200
to 300 and V277 allowed it against two-worker opponents. Neither created a new match outcome in
384 games, and both reduced raw margin, so V274's original limits remain the safe endpoints.

V278 tested a different extension of that pressure: it allowed the remembered signal after turn
32 only while fewer than eight opponent-planted trees were still alive. The two development screens
matched V274 (+1.0 and +1.5 match points, no lost wins), but the independent confirmation gained
five wins while also losing an existing win. It is rejected despite the apparent aggregate gain;
the original turn-32 cutoff remains the safe limit.

V279 addressed a live replay pattern where our empty-handed troll was already standing on a ripe
banana tree that an opponent would destroy that turn. The proposed response was to join that chop,
but it never activated in either 96- or 288-game qualification screen. It is too rare to promote.

V280 made the early opponent-tree pressure wait until we trailed by at least nine banked points,
instead of the proven five-point threshold. In the first 96-game screen it removed V274's one
additional match point without creating a new win or avoiding a loss. The original threshold was
restored and this stricter gate was rejected.

V281 allowed the same signal whenever we trailed, rather than only after a five-point deficit.
It was unchanged in the first 96-game screen. The 288-game screen found two added cases, neither
of which changed the match result and together reduced the raw margin by 58. The original gate was
restored and the looser condition was rejected.

V282 made the entrance-tree tax stop when our deficit exceeded four, rather than eight. It was
unchanged in the 96-game screen, but the wider screen lost one of V274's benefits: a baseline loss
that V274 converted to a draw remained a loss. The eight-point limit was restored.

V283 applied the early opponent-tree preference only to banana trees. In the first 96-game screen
it kept one win but lost one draw improvement and reduced the raw margin from +109 to +16. Other
opponent-planted tree types are part of the useful response, so the filter was rejected.

V284 revisited V278's late pressure only after turn 60, skipping the known bad turn-40 case.
It was identical to V274 in all 1,536 local games. The apparent late gains in V278 were already
caused by V274's entrance-tree tax; the late pressure adds nothing once its regression is removed.

V285 extended the strictly gated opponent-tree reach from six moves to seven. The first 96-game
screen gained two wins but lost an existing win and reduced raw margin from +109 to -11. The
six-move reach was restored.

V286 shortened that reach to five moves. It gained one additional win in the first 96-game screen
with no regression, but the 288-game screen lost three existing wins, converted another to a draw,
and fell to -2.0 match points. The six-move reach remains the safe endpoint.

V287 kept the early opponent-tree rule unchanged and reopened late pressure only when the opponent
had a larger lead. Its independent 1,152-game screen still lost the same established win at turn
40 that invalidated V278. The original turn-32 cutoff was restored.

V288 enabled a small general penalty for chopping trees that an opponent could reach first. It
matched a replay-audit symptom, but the first 96-game screen lost six existing wins and 917 raw
margin. The generic safeguard remains disabled.

V289 offered an immediate harvest when our empty troll shared a damaged, ripe tree with an enemy
chopper. It gained four outcomes in the first 96-game screen but lost four existing ones and 305
raw margin. The broad harvest override was rejected.

V290 limited that harvest rule to verified opponent-planted trees. It converted one V274 draw to a
win in the first 96-game screen, but the wider screen lost two existing wins and 235 raw margin
relative to V274. The targeted override was also rejected.

V291 allowed the stronger opponent-tree preference only during its early activation window, then
returned to the normal preference. In the first 96-game screen it exchanged one V274 win for a
different win and reduced raw margin from +109 to +64. The remembered preference remains useful.

V292 preferred a tent entrance beside water when two normal chores happened to offer banana
planting at different entrances on the same turn. Live replays supported the intuition: these
entrances supplied 8 of the 13 bananas harvested, despite receiving only 132 of 1,155 plantings.
But the planned movement almost never offered that choice. Both the 96- and 288-game screens were
bit-for-bit equivalent in result to V274, so the preference was removed rather than submitted.

V293 made the passive farm ignore dry entrances entirely. Although water-side trees yield fruit
far more often, the first 96 games already reduced raw margin by 15. In the 288-game screen it
lost an existing V258 win, removed V274's match-point advantage, and reduced raw margin by 260
relative to V274. Dry entrance trees supply useful wood, so the unrestricted passive farm remains.

V294 tightened the passive entrance-tax score limit from eight points behind to six. It was
identical to V274 in both the 96- and 288-game screens, so it cannot justify a platform change.
The proven eight-point limit was restored.

V295 strengthened the existing nearby opponent-tree priority after turn 100 only when the opponent
had at least three trolls and led by twelve points. The public replay audit identified that signal
in 34 losses (average turn 198) and no wins, but it was too late to change a match. The independent
1,152-game panel retained V274's +6.0 match points but gave up 13 raw score, so the response was
removed. The signal is descriptive rather than a useful intervention point.

V296 moved that response earlier: from turns 101--220, after an opponent's third troll appeared,
while merely trailing. This caught the same 34 public losses much earlier (average turn 187) and
excluded the sole matching public win, but its independent panel result was again unchanged in
match outcomes and 13 raw points worse than V274. The scale pattern cannot be repaired by stronger
nearby-tree pressure and the baseline was restored.

V297 changed the second-troll build tie-breaker to prefer movement speed before chopping power.
Both development screens were exactly identical to V274, so this is not a meaningful policy change
and the established chopping-first tie-breaker remains.

V298 disabled the passive entrance tax while the apple orchard was carrying its seed or active.
This preserved all ordinary chores but was identical to V274 in both development screens: the two
production mechanisms rarely overlap. The ordinary passive-farm behavior was restored.

V299 retained the normal focus-tree preference after the opponent reached a third troll, instead
of dropping it once they exceeded two. The first 96-game screen kept the same match point but lost
90 raw score relative to V274. The original two-troll boundary was restored without a wider run.

V300 gave every possible second-troll build one harvesting skill. It is a broad production change,
not a new farm route, but the additional apple cost delayed the opening: the first screen gained
two wins while losing three existing wins and 136 raw score relative to V274. The zero-harvest
second-troll build was restored.

V301 chose the nearest, rather than farthest, water-side doorway for the apple orchard. In the
first screen it gained two wins but lost an existing win and 562 raw score relative to V274. The
farthest-from-opponent doorway remains the safe choice.

V302 gave the second troll one harvesting skill only when the opening bank held at least ten
apples. It improved V274 by half a match point with no lost win in the first screen, but the wider
screen lost 1.5 match points and 73 raw score. Every changed outcome began with exactly ten apples,
so a higher threshold would only disable the behavior. The harvest-build branch was closed.

V303--V307 mined the earlier mixed ETA-7 opponent-tree result. Short time windows removed its
regression but also removed its recovered loss. Restricting reach seven to the latched strong
pressure mode improved V274 by one match point and 13 raw score in the first screen, but lost a
V274 win in the wider screen. Requiring a 20-point lead moved that regression to the opposite seat
of the same map, and ending the extension before turn 54 again removed the original gain. The
useful interception needs the same sustained seventh-move reach that causes the regressions, so the
branch was closed and the proven six-move reach restored.

V308--V309 mined the complementary ETA-5 result. The development gain came from the trained second
troll finishing the tree underfoot instead of chasing a crop six moves away. Applying reach five
to every troll on a tree lost a wider-screen win; limiting it to the trained troll preserved all
development wins and added one match point over V274. The independent 1,152-game confirmation then
gained six V258 losses but lost two established V258 wins, finishing at +5.0 match points versus
V274's +6.0 and 32 raw score lower. The role-based gate was rejected and reach six restored.

V310 revisited the contested opponent-tree harvest without adding it to job selection. Planning and
collision handling finished first, and the harvest could replace only a final wait. This preserved
all normal chores and converted one V274 draw to a win. The independent screen retained every V274
outcome, but one two-fruit case reduced total margin by 12 points.

V311 takes only the last fruit from that damaged opponent-planted tree while an enemy troll is
already chopping it. The troll must be empty-handed, able to harvest, standing on the tree, and
otherwise waiting. The passive entrance farm and all planned jobs are unchanged. Direct replay
kept the V310 added win, retained three other positive cases, and removed the two-fruit regression.
The independent 1,152-game screen finished +104 raw margin and +6.0 match points versus V258, with
five gained wins and no lost win. That is three raw points better than V274 with identical outcomes.
The exact compact artifact is `candidate-v311-idle-last-fruit-rescue.min.rs`, SHA-256
`97cd81a68f518726991c234437192838e488098d5b3daf2834084d0786ef1daa`.
It was accepted exactly once as submission 41221074, agent 6681109. It matured after all 160 games
and 100/100 stabilization at **24.67, rank 22**, improving V274 but missing the strict target. The
complete public archive is `public-v311-idle-last-fruit-rescue-agent6681109/`.

V312 allowed the same idle last-fruit rescue on natural and own-planted trees. It was exactly
identical to V311 across both development screens (384 games), so no additional opportunity was
found and the verified opponent-planted check remains.

V313 broadened the final-wait tax to harvest any ripe, non-farm tree already underfoot. The first
screen added 1.5 match points over V311 without a loss. The wider screen added more wins but lost
an established win: the gains all began on apples, while the regressions began on a banana and an
early plum. The broad rule was rejected.

V314 applies that idle tax only to apples. It never routes toward a tree and runs only after normal
job selection and collision handling, so every non-wait chore and the passive banana automaton are
unchanged. The two development screens added three match points over V311 with no lost win. The
independent 1,152-game screen finished +142 raw margin and +10.0 match points versus V258, with ten
gained wins and no lost V258 win. Directly against V311 it added five wins, lost no win, improved
match points by 4.0, and improved raw margin by 38. The exact compact artifact is
`candidate-v314-idle-underfoot-apple-harvest.min.rs`, SHA-256
`de76dcb076affb713cd96922db7e8b426fea97af8582e6ca1622f0bb77cfeba8`.
V314 was accepted exactly once as submission 41221356, agent 6681205, after V311's terminal result
and complete archive. It matured after all 160 games and 100/100 stabilization at **22.72, rank
30**, with 86 wins, 72 losses, and two ties, so it missed the target. The complete public archive
is `public-v314-idle-underfoot-apple-harvest-agent6681205/`; all 160 replays were written with no
failures and the compressed replay SHA-256 is
`bfa826e077e397ad935eeeafabd2970a30be1a5b86f681df0cc6354f59f8d35f`.

Replaying V311 and V314 on the exact V314 platform states found only one game where the new apple
rule changed a command. It replaced a wait with a harvest on turn 75 of game 901042517, which was
observed as a one-point loss. The local gain was real, but the live opponent/map mix almost never
presented the opportunity. The mature production audit again concentrated the strongest losses
against opponents with three or more trolls: rating-24+ losses averaged 46 own wood versus 84
opponent wood, while a cheap third troll was never affordable.

V315 removed an unbankable final-turn apple harvest and was otherwise identical. V316--V321 then
rechecked the requested protected three-banana entrance lifecycle, including score, time, and
observed-traffic gates. Preserving the entrance tree consistently lost outcomes because the normal
bot's immediate young-tree wood was more valuable than the rarely completed fruit cycle, confirming
the earlier V232--V245 result. Disabling the entrance farm also lost a wider-screen win. V319's
one-hit underfoot chop never fired in 384 games. Earlier fruit-to-wood cash-out and the old
three-worker factory both lost heavily when applied to the current bot, so those broad branches
were closed again.

V322 confirmed that removing the entrance farm loses match points. V323 and V326 tried starting
the fruit-to-wood cash-out earlier; the first changed only raw score and the second lost twelve
match points. V325 restored the older three-worker factory directly and lost 9.5 match points.
V327--V328 let an otherwise idle troll help with an own tree underfoot, but never changed a score.

V329 let an idle troll join the opponent at the last remaining tree, but it could interrupt the
existing apple action and lost two wins. V330 moved the rule after the apple action and passed both
development screens. In the independent 1,152-game confirmation it changed 123 command streams and
improved total raw margin by 22, but it changed two wins into a loss and a draw while recovering
only one loss as a draw. Match points fell by one, so V330 was rejected and V314 remains on the
platform.

A read-only audit of 1,816 recent public games from the current top 15 found that the rank-eight
two-troll bot runs a continuous local farm: the original troll plants and harvests, while a trained
2/2/0/2 troll cuts wood. One representative replay kept at most eight planted trees, harvested only
within three steps of its tent, and gave the farmer no idle turns. Across 128 games it averaged
29.8 plants, 51.2 harvests, 129.5 chops, and 51.5 final wood. This is a real production farm, not
the passive entrance tax.

V331--V335 copied the broad idea but either replaced useful starter chopping or mixed farm jobs
into the ordinary scalar job list. The dedicated version lost 1.5 match points in the first 96
games; the optional version lost 7.5. Selecting maps by the starter's best wood-trip score still
lost 18.5 match points over 288 games. These versions also exposed two implementation errors: the
carried-fruit path could exceed the intended eight-tree cap, and the farmer wandered to distant
ripe trees.

V336--V341 repaired those errors using the measured replay behavior. The corrected V338 kept eight
nearby trees, pre-positioned for local harvests, and eliminated almost all pre-turn-250 waits. It
gained 2,069 raw margin over 288 games, but lost eight match points because home production replaced
too much cross-map denial. Delaying the farm or changing fruit order did not repair that tradeoff.

V342--V347 made the bounded farm a comeback action instead of an always-on role. The strongest
development selector, V346, enabled it only after an eight-point deficit on maps with at most one
initial tree within three steps of the tent. It gained 265 raw margin and one match point over the
first 288 games without losing a win or draw. The separate 1,152-game confirmation rejected it:
raw margin fell by 1,699 and match points by ten, with 15 established wins lost. The CompactGold
family accounted for -1,827 of that margin. V314 therefore remains the platform bot, and no farm
candidate from V331--V347 was submitted.

V348 combined the complete bounded farm with the rank-eight bot's exact 2/2/0/2 second
troll. It delayed training on many maps and lost 9.5 match points and 3,143 raw margin in
the first 96-game screen. V349 isolated that second-troll build without the farm; it lost
11.5 match points and 3,550 raw margin, worsening 15 outcomes while improving four. The
observed worker and farm are parts of a different complete strategy and are not safe
independent additions to this bot.

V338 also received a small live IDE check against three leading agents on six fixed
opponent/map blocks. Relative to V314, the farm raised our score by 123 but raised opponent
scores by 381, reduced total margin by 258, and changed one win into a loss. This agrees
with the independent local rejection, so no farm candidate was submitted. A parallel E7a
check gained one outcome in six blocks, but four recent mature E7a ladder runs finished
between 22.30 and 23.59; that larger live record rules out another E7a recycle.

Because V314 matured at 22.72 while exact V311 had the project's best recent mature score
of 24.67, the exact V311 artifact was restored as V350, submission `41222477`, agent
`6681943`. It completed all 160 games and 100/100 rank stabilization at **24.79, rank 20**.
The complete no-failure archive is `public-v350-v311-recheck-agent6681943/`; its battle-index
SHA-256 is `658ec6992774f9b01450b8174c95dcc08a56d1fb92d4ac4ee2834301ec3568ce`
and its compressed-replay SHA-256 is
`628a0cc87bb52cc0281286e1131694ee4078a97ff374d2b10ac07cbd43584b4d`.
The restored code improved the live result but still missed both parts of the target.

V351 tested whether the bot's job priorities interfere when the opponent starts scaling.
The change affected none of 384 replayed games, so the scalar-versus-tuple choice is not
the active limitation in those states. V352 tried abandoning a losing home orchard so its
starter could return to normal work. It changed four of 96 games and lost 1.5 match points;
simply releasing that troll often produced a wait instead of useful work, so it was rejected.

After V350 matured and was archived, the guard submitted exact V314 as V353, submission
`41222732`, agent `6682147`. It reached 100/100 rank stabilization at **23.22, rank 29**.
The platform emitted 161 rather than the usual 160 games; all 161 were unique, complete, and
saved without download failures in `public-v353-v314-recheck-agent6682147/`. The battle-index
SHA-256 is `90d8fe1b594d194180e9be23cf5cdaac98baeb9bbe04b766423e59af171519fd`
and the compressed-replay SHA-256 is
`28c6d835e9ab9592006e337161d56444844f55042cf2b867597125f38d4aff95`.

The V350 replay audit found a concrete late-game failure: in game 901064663, a troll carrying
one wood repeatedly backed away from the tent because the other, empty troll was waiting on the
needed entrance. V354 tried a general multi-entrance swap, but it changed nine of 96 games without
changing an outcome and reduced raw margin by ten, so it was rejected.

V355 makes the repair only when there are exactly two trolls, a wood carrier is visibly retracing
its previous step, and an empty waiting troll blocks a tent entrance that the pair can safely swap
through. The separate 1,152-game confirmation changed 14 games, gained 61 raw margin and one match
point, improved two outcomes, and worsened none. Replaying the real opponent commands from the
V350 loss reproduced the official 88--92 result exactly; V355 banked the stranded wood and finished
92--92. Two other affected platform games were also reproduced without a regression. The tested
wrapper and upload artifact emitted identical commands throughout 128 additional full games.
The locked upload is `candidate-v355-backtracking-wood-bank-swap.min.rs`, 89,422 bytes, SHA-256
`b084dd111819619f57d9c4ee01841b837f53add2000af88f840a5e8e9a2ab27a`. Its V356 submission guard
requires V353 to finish all 160 games, reach 100/100 stabilization, miss the target, and be archived
without download failures before it may replace the current bot. Those checks passed, and V355 was
accepted exactly once as V356, submission `41222915`, agent `6682252`. It completed all 160 games and
100/100 stabilization at **22.60, rank 30**, so the proven blockage repair was too rare to improve
the overall rank. All 160 games are archived without failures in
`public-v356-backtracking-wood-bank-swap-agent6682252/`; the battle-index SHA-256 is
`cbd3562e2bc216fe91f89b09022337d68244eb15a8465dc48538995a6b5677d6` and the compressed-replay
SHA-256 is `2ba661d1339829bd58e8d4737e20efe8ae72024f002442e90b7f8d3b0714413f`.

The V356 replays showed that losses let opponents harvest many more planted crops and leave them
ripe for longer before contact. V357--V362 therefore tested a small denial rule: when a troll with
no free carrying space is already standing on an opponent-planted tree near the opponent tent,
finish chopping it instead of walking away. The broad three-hit version V359 changed 270 of 1,152
independent games and added three match points, but it also lost two established outcomes, so it
was rejected.

V363 limited the same action to games where the bot was tied or behind. It still lost one win: the
troll attacked while 21 points behind and delayed bringing its own wood home. Both added wins began
only four points behind. V368 encodes that distinction directly and acts only from a tie through a
four-point deficit. It gained one win with no losses in the 288-game development panel. In the
separate 1,152-game confirmation it changed commands in 17 games, changed final scores in 16, and
turned two losses into wins without losing any outcome. Both wins came from the same map state
against two equivalent panel opponents, and total raw margin fell by 30, so this is deliberately
treated as a narrow tactical candidate rather than a broad score improvement.

The tested V368 module and compact upload emitted identical commands in 132 full games. The locked
upload is `candidate-v368-close-game-crop-finish.min.rs`, 93,146 bytes, SHA-256
`e592ce299d0da3bb744d5b6f0650f4d589afe472fe5421d1ddec5bed3de243d1`. After verifying V356's
mature result and complete archive, the one-shot guard accepted it as platform V370, submission
`41223244`, agent `6682355`. It completed all 160 games and 100/100 rank stabilization at **25.21,
rank 17**. This reached the score half of the target but not rank below 10. All games are archived
without failures in `public-v370-close-game-crop-finish-agent6682355/`; the battle-index SHA-256 is
`42f7b68494b53f95175da561efd90f5f73081c6ffffd6c573575b488153e3a9a` and the compressed-replay
SHA-256 is `106891173790b134a32fa22aa67db61a0d5121cbe856be83500902d59d458155`.

While V370 ran, V371 tested the same denial only from a one-to-four-point lead. It added one win
in development, but the independent 1,152-game screen lost one established win and added none.
V372 combined the proven deficit range with that small-lead range; confirmation added two wins but
still lost the same established win. V373 extended the lead to eight points and changed no outcome
in development while reducing raw margin. All three extensions are rejected; the V368 score gate
must not be widened from this evidence.

A command replay against all 160 V370 platform games found that V368's new crop-finishing action
never activated on a live path. A separate guard audit explains why: a troll stood on an opponent
crop more than ten thousand times, but the complete rule was never eligible. Only five live moments
passed every check except the requirement that the troll's bag already be full. V374 placed the
same full-bag rule directly on the stronger V311 base and passed the local screens, but it was held
back because that would mostly restore V311 rather than deliver a behavior the platform had used.

V376 removed only the full-bag requirement, allowing the troll to collect the cut wood. It was much
more active: the independent 1,152-game screen gained four outcomes but lost one established win.
The loss began on turn 16, while every gain began on turn 44 or later. The unrestricted collecting
version is rejected. V378 keeps this opportunistic action out of the opening, starting it on turn
35. Its 1,152-game post-selection replay retained all four gained wins, lost no outcome, and
improved total raw margin by 208. A refreshed live-replay funnel found eligible actions after the
guard on turns 56, 57, 64, and 68 in three V370 games, confirming that the behavior can activate
on the platform. V379 applies the same rule to the exact current V355 base. It reproduced the same
four gained wins, zero losses, and +208 margin there. The eight untouched maps left in the frozen
panel changed three games, worsened no outcome, and added four raw margin. The compact artifact
emitted exactly the same commands as the tested module in 132 packaging games. The locked upload
is `candidate-v379-opening-safe-collecting-finish.min.rs`, 93,186 bytes, SHA-256
`d0ced6924d7d004389bebb170b1a8e9432d96158d545a86eb1636914c826aba0`. The one-shot guard accepted
it as platform V381, submission `41223623`, agent `6682505`; its rollout and rank stabilization
completed after all 160 games at **24.73, rank 22**. It missed both parts of the target and did not
beat V370's 25.21/rank 17. All 160 games are archived without failures in
`public-v381-opening-safe-collecting-finish-agent6682505/`; the battle-index SHA-256 is
`0d722f38bc547c10c7457277214a44a15c9d3397903e775f0afc2792e950933c` and the compressed-replay
SHA-256 is `381f0c94640bc78a21fc6a59891562a5b091df393465697c21b9aeb4391e8dd0`.

V382 briefly raised the three-chop limit to four while V381 rolled out. It changed two of 288
development games, changed no outcome, and added four raw margin. A more detailed live audit then
showed that the sole V370 opportunity blocked by the hit limit required 20 chops, not four. The
longer confirmation was stopped because V382 would add no live opportunity; the extension is
rejected rather than spending evaluation time on dormant behavior.

V383 removed the guard that forbids the finish while an enemy troll shares the tree. This covered
the last two plausible live opportunities and improved development margin by 48 without changing
an outcome. Independent confirmation rejected it: 29 games diverged, two outcomes improved, four
worsened, match points fell by two wins, and raw margin fell by 58. One regression destroyed a win
that V379 itself had recovered. The colocated-enemy guard remains, closing the remaining live
crop-finish relaxations.

The first worker-scaling comparisons exposed a test-wiring error: candidates that changed the
embedded Yamo base were also changing the supposedly independent baseline through a shared module.
`candidate_v379_full_baseline_bridge_module.rs` now embeds a separate exact V379 base. It was
verified command-for-command against the compact V379 artifact in 12 full games. All later
base-changing candidates use this independent bridge; the earlier V379 wrapper evidence is
unaffected because that comparison intentionally shared an unchanged base.

The complete V381 replay audit confirms the midgame scale problem. The bot kept exactly two trolls
in all 160 games. It averaged +157 margin when the opponent stayed at one troll, +12 when the
opponent reached two, -52 against three, and -130 against four. Eight games reached the narrow
state "we have two, they have at least three, and we trail by ten" before turn 150; all eight were
losses. The current bot nevertheless never held enough banked resources for even a 1/1/0/1 third
troll in any live game. Its closest shortfall averaged 6.5 resources.

V384 tried to react to that losing state by collecting for a cheap third troll. Against the
correct independent baseline it changed no command in 288 development games, and replaying the
eight live trigger games could not preserve an exact reactive path. V385 instead started funding a
2/2/0/1 third troll early on maps with at least six nearby trees. It lost 17 outcomes and improved
two in 288 games. Delaying the plan to turn 50 as V386 still lost 16 outcomes and improved two.
V387 assigned the funding job to the trained troll so the starter could keep denying trees; it was
worse still, losing 67 outcomes, improving one, and never completing the purchase. Full-time
funding with either troll is rejected.

V388 narrowed the bridge to games already only one iron short of the cheapest third troll. It was
inactive in the 288-game panel. On the one known platform map where it activated against autonomous
local opponents, it bought the third troll in all 12 seat/opponent tasks but lost 56 total margin
and changed one win into a loss. The attractive recorded-opponent replay result was invalid after
divergence because hundreds of those frozen opponent commands became illegal. Natural purchase,
broad funding, delayed funding, role swapping, and the final-one-resource bridge are therefore all
closed as additions to the current two-troll strategy.

V389 attacks the same failure without buying a worker. Once the opponent visibly has three trolls,
it permanently doubles the existing priority of reachable opponent-grown trees, using the already
tracked crop provenance and the existing six-turn reach limit. Before that trigger it is exact
V379. The first 288-game screen changed 26 games, added 68 raw margin, and worsened no outcome;
gold-adaptive, legend-balanced, and MyBot families were positive, while norx-native-three lost 31
raw margin without changing an outcome. The independent 1,152-game confirmation rejected it: it
improved three outcomes but worsened four, with all harmful outcome changes against Gold and Legend
teams that added general-purpose workers. V389 must not be submitted.

The useful distinction in those failures was the opponent's third-worker build. The successful
MyBot cases used a dedicated harvester with harvest power but no chopping power; the harmful Gold
and Legend cases used general-purpose workers that could chop. V390 therefore keeps V389's crop
pressure dormant unless at least three opponents are visible and one is such a dedicated
harvester. Its first 288-game screen changed eight games, all against the intended MyBot family,
added 20 raw margin, and changed no outcome for better or worse. It was completely inactive against
the other five opponent families. The independent 1,152-game confirmation changed 35 games, again
only against MyBot, turned two losses into wins, lost no outcome, and added 132 raw margin. It
worked from both seats. The eight-map reserve was dormant. On the seven exact V381 platform maps
where the rule could activate, autonomous local opponents produced three changed games, no outcome
regression, and +27 raw margin. The archived-trajectory audit found seven live activations, and the
readable and compact programs emitted identical commands in all 160 archived games.

The locked upload is `candidate-v390-harvest-specialist-pressure.min.rs`, 93,558 bytes, SHA-256
`829763144c99b67898ec8739d98b9fa8d00c2e1df7e2c3f6086614edcd6586dd`. The one-shot guard accepted
it as platform V392, submission `41223986`, at 2026-08-31 23:58 UTC. Its rollout and rank
stabilization completed after all 160 games at **21.15, rank 38**. It missed both targets and was
worse than V381 and V370. The complete no-failure archive is stored on the attached data disk at
`/data/public-v392-harvest-specialist-pressure-agent6682801`; its battle-index SHA-256 is
`fa21cd2e41ff8b50db089249c288cd3563693fba773efc920cde393c8c462dfb` and replay-package SHA-256 is
`035fe50fb2b80707f86ce31e5aae4addb1b9ac7b635c7eeae9272cb936f1bd51`. V390 changed commands in
only two of those games, both recorded losses to icecuber, so its qualified local gain was too rare
for this live opponent mix.

Post-submission tuning closed the rest of the crop-priority branch. A gentler 1.5x boost looked
strong in development but lost 67 raw margin in confirmation; a 3x boost lost 43 immediately.
Waiting for four enemy trolls was dormant even after two four-worker farm proxies were added to the
panel. Triggering earlier on a high-harvest factory worker was active, but lost 154 margin across
384 games, including -52 and -190 against the two new farm proxies. Earlier specialist pressure
also lost 60 on an exact live-map causal check. More crop priority is therefore not the answer.

The full V392 archive makes the remaining problem explicit. Against opponents that peaked at one,
two, three, and four trolls, mean margins were respectively +151, +18, -31, and -182. The four-troll
group went 1-14. V392 itself stayed at two trolls in every game and was never naturally able to
afford even the cheapest third. Future work should test a conditionally complete production policy
against the new farm proxies instead of further denial-weight patches.

V399--V404 tested that conditional production direction and rejected it. V399 enabled the bounded
near-tent farm only after observing an opponent with at least two trolls and a high-harvest,
low-chop worker. It looked strong against the ordinary development panel (+1,909 margin in 384
games), but on the exact live maps where it changed behavior it lost three outcomes. Restoring the
old sparse-map guard or an eight-point-deficit guard either retained those losses or made the rule
almost entirely dormant. V402's six real V392 openings were therefore continued against 12 adaptive
opponents from the last exact common turn; it lost 121 margin and exchanged one improved outcome for
one regression.

V403 required our other troll to be a fast chopper. It gained 316 margin without changing an
outcome on the two V392 openings that inspired the gate, but independent archives rejected the
post-selected rule. One V381 opening produced three new wins and no loss, while two V370 openings
lost one match point and 171 margin. V404 restricted the farm to turn 230 onward. It retained the
three V381 gains, but a V370 continuation still produced two worse outcomes versus one improvement,
and the V392 continuation lost 302 margin without changing an outcome. Taking control of the
starter for home production remains too disruptive, even under narrow opponent, worker, deficit,
and time gates.

The comparison runner now supports exact archived preludes. Both arms replay the recorded legal
commands through a chosen common turn, assert that the current baseline still matches every own
command, and then face the same adaptive opponent from the resulting real state. An optional
per-game switch cap handles the few turns where local referee parity ends before the policy changes.
This replaces misleading frozen-opponent counterfactuals after command divergence and is the
required check for future candidates selected from platform failures.

V405 returned to a pure action tax. It broadened the existing final-`WAIT` underfoot apple harvest
to any ripe fruit, but only after the opponent had at least three trolls. The candidate changed
nothing in a 576-game screen that included three- and four-worker opponent proxies, and nothing on
all 160 exact V392 platform trajectories. It is safe but dormant, so it cannot improve the rank and
will not be submitted.

V406 allowed a slightly less passive tax after the opponent reached three trolls: when our empty
harvester already shared a damaged, ripe opponent-grown tree with an enemy cutter and the selected
ordinary action was `CHOP`, it harvested before resuming the cut. It changed 11 of 288 development
games for +8 margin and no outcome change, but the real V392 openings exposed the cost of that one
turn. Across 120 adaptive continuations it lost five outcomes, gained none, and lost 478 margin.
Nine of the ten first interventions happened while our visible score still led; all five regressions
came from that group. V406 is rejected.

V407 required a current score deficit before taking the contested fruit. On the ten selected V392
openings it changed 10 of 120 adaptive continuations, gained 58 margin, and changed no outcome.
However, it accidentally retained V405's broader final-`WAIT` rule, so V408 restored the proven
apple-only wait tax and isolated the trailing `CHOP` replacement. V408 activated on seven observed
losses and no wins across the independent V370, V381, and V392 archives. Exact adaptive
continuations rejected it: the V381 holdout exchanged one gained outcome for one regression, and
the combined 84 continuations lost 359 margin. Harvesting before an already-selected contested chop
is therefore closed; the delayed cut is not free even while trailing.

V409 addressed the observed passive-tree symptom directly: if a troll was already standing on the
tracked entrance banana, the tree was ripe, and ordinary planning had already selected `CHOP`, it
would harvest first. The rule neither protected the tree nor changed movement. It was completely
dormant in 288 local games and in all 480 exact trajectories from V370, V381, and V392. The passive
tree is normally cut before fruit survives to this decision point, so a last-moment rescue cannot
repair the weak opening and V409 will not be submitted.

The next V392 replay audit found a different concrete failure. In game 901099122, a troll carrying
two wood oscillated between `(12,3)` and `(13,3)` for the final 240 period-two events while the
orchard troll occupied the useful tent entrance. The carrier never deposited its wood. V410 allowed
the older entrance swap to use an empty doorway troll that was harvesting, but the two actions were
out of phase and it never activated. V411 also allowed a doorway troll currently depositing fruit;
this rescued the long stall, but applying it after any single backtrack lost one V381 continuation.

V412 tried to require 32 consecutive two-cell repeats. A command audit caught a construction bug:
the threshold also delayed V379's older, already-proven empty-`WAIT` swap. That accidental change
reduced a V381 win from margin eight to four. V412 was rejected before submission. V413 preserves
the original swap exactly and applies the 32-repeat threshold only to the newly allowed harvesting
or depositing doorway troll. Exact command replay is byte-identical to V379 in all 320 archived
V370/V381 games. It changes three of 160 V392 trajectories: two recorded losses, including the
240-event stall, and one tie.

Across 144 adaptive continuations from the selected V370/V381/V392 openings, V413 added one win,
lost none, and gained 541 raw margin. On 864 fresh paired games it changed four games, changed no
outcome, and gained six total margin. The two confirmation changes added no critical or unclassified
command issue. Readable and compact programs emitted identical commands in all 160 V392 archived
games. The locked upload is `candidate-v413-gated-banking-door-swap.min.rs`, 94,193 bytes, SHA-256
`7066aa9717959640a0be4e7fc0cdbbc6fed15a549a4e8cfc50db3e9a3d23e33c`. The one-shot guard accepted
it as platform V414, submission `41224374`, agent `6683331`, at 2026-09-01 02:50 UTC. It completed
all 160 games and 100/100 rank stabilization at **22.66, rank 32**, missing both targets. Its complete
no-failure archive is `/data/public-v414-sustained-banking-door-escape-agent6683331`; the battle-index
SHA-256 is `2dce307760e9c56ebb8a3e72c0f4cc086a7eede0489d676b2f8b54fd7586ffcc`
and the replay-package SHA-256 is
`a7af695c8cd720177a29625fc53f292d32fdd2e08d6c4af57f7ae5a515cdf775`. V413 changed one of those
games, a recorded 31-point loss caused by a one-wood loop; V415 would have changed none.

The first disjoint V413 confirmation exposed a useful value gate. Both small negative changes had a
stuck troll carrying one wood, while the severe V392 rescue and both fresh gains carried two. V415
therefore requires two wood for the broadened banking swap. It keeps the V392 continuation gain
(one added win, no loss, +565 margin), keeps the two fresh gains (+14), and is completely dormant in
the 576-game confirmation and every V370/V381 selected continuation. Exact command replay changes
only the original 135-point V392 loss among all 480 archived V370/V381/V392 games. The locked compact
artifact is `candidate-v415-two-wood-banking-door-swap.min.rs`, 94,217 bytes, SHA-256
`ce533aa9bb42c112672b7cac3d83fa9ed49056b8e594b5981a0c9ac32f406eb3`.

Useful work during V414's rollout found a second long-stall class. In V414 game 901105620, an empty
chopper oscillated beside the tent for 151 repeats while the orchard troll occupied the entrance;
the recorded game lost by 452. V416 extends the same 32-repeat swap to an empty trapped worker while
retaining V415's two-wood banking gate and V379's original swap. Exact audits selected four V370,
four V381, two V392, and one partial V414 trajectory: ten recorded losses and one recorded win.
Adaptive continuations gained 5,938 total margin and eleven outcomes without losing any established
outcome. One V381 opening could be preserved only through turn 12; the other ten retained the exact
archived path to the intervention. The unselected 288-game screen kept the same +14 gain and the
independent 576-game confirmation was completely dormant, with no critical or unknown validity
change. Readable and compact V416 programs matched in all 160 V392 games. Its locked upload is
`candidate-v416-empty-trapped-door-swap.min.rs`, 94,299 bytes, SHA-256
`bb3a5da697292681eaa214d98f710d22e2c9c081344497cf15a3aaf561e89f26`. The full V414 audit confirmed
that it changes only the same recorded 452-point loss. After V414 matured and its archive passed all
hash checks, the one-shot guard accepted V416 as platform V417, submission `41224449`, agent
`6683528`, at 2026-09-01 03:34 UTC. It completed all 160 games and 100/100 rank stabilization at
**24.95, rank 20**, missing both targets. Its complete no-failure archive is
`/data/public-v417-empty-trapped-door-swap-agent6683528`; the battle-index SHA-256 is
`1d2461cdb70a9ac3b7f401998819a63a56987815383100ee897696bea64ad91d` and the replay-package
SHA-256 is `ff129cacb4536194c36566691115f06cfca4d5e8e70b22b2c8d80a7c3762dbeb`.

While V417 rolled out, V418 tested whether the new doorway escape could trigger after 16 repeats
instead of 32. It found one extra fresh activation, but exact adaptive continuations exposed four
worse outcomes across the V370 and V381 archives. V418 is rejected. The 32-repeat protection in
V417 remains necessary.

Large replay archives and new comparison output belong on the attached `/data` disk. After the
2026-09-01 cleanup it had about 86 GB free, while the root disk had about 5.6 GB free. `/tmp` now
contains only small system-managed directories. Useful old temporary project data was preserved in
`/data/separate_troll_farm-working/archive/tmp-recovery-2026-09-01`, and the old 44 MB Cargo cache
was moved to `/data/separate_troll_farm-working/archive/cargo-target-workspace-2026-09-01`.
Repository-level Cargo configuration now places every new build in
`/data/separate_troll_farm-working/tmp/cargo-target-workspace`; bulk results must also stay on
`/data`.

V417 game 901108690 exposed a different two-troll traffic jam. An empty troll alternated between
the tent entrance and the cell above it while a troll carrying two wood alternated two cells away.
Both wanted the same middle cell on opposite turns, so neither made progress for 62 repeats. V419
recognized only this exact arrangement after 32 repeats: both trolls must be in matching two-cell
loops, the entrance troll must be empty, the other troll must carry at least two wood, and both must
be contending for the same middle cell. It moved the empty troll aside and sent the wood carrier
toward the entrance. This changed only that recorded loss among the full V417 archive and none of
640 older archived games or 576 fresh paired games. Twelve adaptive continuations gained one match
outcome, lost none, and added 88 margin.

V420 applies that same narrow clear after 16 repeats. It still changed only game 901108690 across
all 800 archived trajectories and changed nothing in the 576-game fresh confirmation. Starting 16
turns earlier was materially stronger in 12 adaptive continuations: four losses became wins, no
outcome became worse, and total margin rose by 250. The readable and compact programs emitted
identical commands in all 160 V417 games. The locked upload is
`candidate-v420-earlier-out-of-phase-door-clear.min.rs`, 96,487 bytes, SHA-256
`6c1048f65d36c662158c68e976e24b76aacadd7cbb49558169c5ebd0369091c2`. The one-shot guard accepted
it as platform V421, submission `41224609`, agent `6683824`, at 2026-09-01 04:40 UTC. Its rollout is
complete. After all 160 games and the full ranking adjustment it finished at **23.54, rank 27**,
missing both targets. The complete archive is
`/data/public-v421-earlier-out-of-phase-door-clear-agent6683824`.

V422 tested a top-player anti-griefing tactic on one exact V417 near-loss. When our colocated troll's
final action was `WAIT` and an opponent was strong enough to fell that tree immediately, it joined
the chop to share the wood. The rule changed only the recorded three-point loss in all 160 V417
games. Exact adaptive continuation rejected it: one win became a loss and total margin fell by 268
across 12 opponents. The apparently unused action changed later planning, so V422 will not be
submitted.

V423 tested whether the apple orchard should stay dormant after a high-harvest opponent worker was
visible. Across five platform archives, orchard games matching that visible signal had a negative
average margin, but the first fresh 288-game causal screen showed the correlation was misleading.
The veto changed nine games, improved no match outcome, and lost 527 total margin across every
affected opponent family. The orchard was helping even in many games that still ended as losses;
V423 is rejected without a confirmation run.

V424 re-ran the older V368 program because its first platform result had reached 25.21 and was the
best score seen so far. The repeat finished at **21.06, rank 37** after all 160 games and the full
ranking adjustment. This large difference showed that the platform score is noisy and that simply
uploading the same lucky program again is not a reliable improvement. Its complete archive is
`/data/public-v424-v368-remeasure-agent6684088`.

The V421 recordings then exposed another doorway jam. In game 901111939, a troll carrying one wood
walked back and forth outside the tent while the troll at the entrance repeatedly chopped a nearby
replanted tree. The old doorway swap waited for the entrance troll to become idle, so it acted too
late. V433 allowed the two trolls to exchange places after a long repeat, but a broad test found one
new loss. V434 delayed the exchange, and V435 limited it to games we were losing; both were still
too broad. V436 also required the game to be within 40 points. It repaired the selected loss, but an
older V417 game showed that moving the workers on turn 277 could turn two wins into a draw and a
loss.

V437 keeps the same close-game repair but allows it only on turns 270 through 275. This gives the
workers enough time to repay the cost of changing places. Across 640 recorded platform games it
changes only the original 21-point V421 loss. Replaying that position against 12 different opponents
gained 21 total margin, changed one loss into a draw, and made no result worse. A separate 576-game
test made no changes, which confirms that the rule stays out of ordinary play. The readable and
compact programs produced identical commands in all 160 V421 recordings. The locked upload is
`candidate-v437-payback-window-one-wood-swap.min.rs`, 96,773 bytes, SHA-256
`2e19147e57c51e27f1f2f0db1465b78018fda59669e18b4046899150b5a68906`. The one-use guard accepted
it as platform V438, submission `41225002`, agent `6684652`, at 2026-09-01 07:16 UTC. Its rollout
and ranking adjustment completed at **22.07, rank 35**, missing both targets. All 160 replays were
archived without failures in `/data/public-v438-payback-window-one-wood-swap-agent6684652`; the
battle-index SHA-256 is `9a2fb0b406bfe725b42a73029d0ddd23f413737b9b8208cc3430ea670f23063e`
and the replay-package SHA-256 is
`fc96b2b1e95213e3f406f690145395c896c6a36d82f8b513497b7ba506a5183e`.

The mature V438 archive contained one new farm-interference failure. In game 901122343, a troll
carrying one wood walked back and forth for 106 turns because the entrance troll kept planting and
chopping on the required doorway. The game lost by one point. V439 keeps every V437 rule and lets
the entrance chopper yield only after 32 confirmed backtracks, only on turns 120-240, and only while
trailing by no more than 40 points. Across 960 archived games it changes only that V438 loss and one
V392 tie; it changes no recorded win. The exactly reproducible V392 continuation gained 12 margin
across 12 adaptive opponents with no worse result. The V438 continuation had to begin at the local
engine's earlier divergence point and did not recreate the jam, so it supplies no extra claimed
gain. A separate 576-game confirmation was completely dormant, and readable and compact V439
programs emitted identical commands in all 160 V438 recordings.

The locked V439 upload is `candidate-v439-early-exhausted-one-wood-swap.min.rs`, 96,985 bytes,
SHA-256 `7f61a6cd510a70e9389e794571512e2c5d0afb33bab957c70791c2c16fbff0bc`.
The one-use guard accepted it as platform V440, submission `41225204`, agent `6684947`, at
2026-09-01 08:23 UTC. Its rollout and ranking adjustment completed at **22.91, rank 29** after all
160 games. A command-by-command audit found that V439's new repair never activated in those games,
so the 0.84-point difference from V438 is platform sampling noise rather than a measured benefit.
All replays were archived without failures in
`/data/public-v440-early-exhausted-one-wood-swap-agent6684947`; the battle-index SHA-256 is
`e9d17bec9ec72709e7423e5b1194678f825b48c1be2acdaf08abebd610b60fce` and the replay-package
SHA-256 is `018746e1847bf83b8b177e99450691aa7af1c061af544eb9f06eb63870e6d2a5`.

The next offline direction is to let a future selector see the map, not only the existing 64-number
summary of a position. A compose-only exporter was added for this purpose. It does not train a
model, change a bot, or contact the platform. It replays the frozen D172a archive, verifies the old
81 input values, and computes a compact fingerprint for a 72-layer map view at each decision.

The full 512-map replay reproduced all 79,997 archived decision rows and 27,392 distinct states.
There were no missing or extra rows, no inconsistent map fingerprints, no wrong map orientation,
and no wrong tensor sizes. One old value differed at the raw floating-point bit level: the
turns-remaining value `1/300` on map `9860166`, turn `299`. The archive intentionally stores only
nine decimal places, and both values serialize to the same `0.003333333`; the focused check passes
under that exact archive format while still reporting the raw bit difference. One-thread and
four-thread smoke runs also produced the same aggregate fingerprint. Evidence is under
`/data/separate_troll_farm-working/analysis/h10a/`. The frozen D172a source and its four corpus
shards were not modified. No training or platform submission has been started from this work.

The H10a pre-authorization package is now complete. It adds a deduplicated `/data` tensor writer,
the frozen 6,541-parameter trainer, matching Rust inference, and the unchanged selection/veto/
confirmation gates. A 51-state materialization smoke test passed; Python and Rust agreed on all 13
scores within `1.54e-8`; all nine Rust tests passed. Both fitting and held evaluation were also
deliberately attempted while disabled and correctly stopped before writing output. Exact evidence
and hashes are in `H10A_PREAUTHORIZATION_READINESS.md`. Full tensor export, training, held-map use,
and platform action remain disabled pending explicit owner approval.

Later on 2026-09-01 the owner authorized the complete frozen H10a sequence ("Publish any
candidate that passes all frozen offline gates; no additional approval is required"). The full
export materialized all 27,392 states and joined all 79,997 corpus rows, and both frozen seeds
were fitted exactly once with 6,541 parameters. The selection stage on the 128 held maps then
closed the experiment at 12:55 UTC: neither fit was admitted. Seed 101001 changed the pooled
margin by -0.02 with a worst block of -0.25 and used its one-time option in 1.7% of games; seed
101002 was effectively dormant, using the option in 0.05% of games with a pooled change of 0.00.
Both failed the +1.5 pooled-mean gate and the 5% minimum-activation gate, so veto and
confirmation were never opened. The decision is recorded in
`/data/separate_troll_farm-working/experiments/h10a-spatial-selector/selection-result.json`
with both 2,048-row selection files beside it. **H10a is closed**: under the frozen rules, giving
the one-time selector a map view did not improve it. `H10A_HANDOFF_2026-09-01.md` is kept only
as the record of that run.

Earlier the same morning a door-factory line, V441 through V454, was built from V440 with
`build_v441_v442_putibuzu_door_factory.py`. It grafted putibuzu's measured plant/chop/drop
tent-door factory and adaptive second-troll purchase onto V440 in several variants (committed,
early-trained, late-trained, opportunistic, sparse/dense, learned-role, faithful-adaptive, and
training-only). None was submitted. On 8-map development panels against V440 (192 games each)
only V448 and V450 gained, +3.05 and +3.66 mean margin, and both gave it back on independent
maps (V448 -0.70 over 384 games, V450 -4.79 over 48); V451 lost 10.80 over 384 independent
games; every other variant lost on its own smoke panel, V442, V453 and V454 by more than 30
points a game. Replaying V448 through the 160 archived V440 platform games changed 94 results
for -26 total margin with no match outcome improved or worsened. Against the champion of record
on the locked 72-map panel (first seat only) V450 won 54.2% and V454 won 47.2%, below V439's
59-62%. The line is paused. Panels are under `/data/separate_troll_farm-working/analysis/putibuzu/`
and the built programs under `/data/separate_troll_farm-working/build/v441-v442/`.

That afternoon a separate effort pursued the team repository's neural-network target by
cloning V439 into a small convolutional policy. It was stopped the same evening. A behaviour
clone is bounded by its teacher, V439 already clears that target's gates (62.3% against the
champion of record and 94.2% against orchard 6 over 400 games each), and the best clone won 0 to 1
of 20 games despite 87.5% per-decision agreement. The pipeline (corpus generator, DAgger loop,
trainer, network player, 15 tests) and its four reports are archived under
`/data/separate_troll_farm-working/nn/` and were removed from this directory on 2026-09-02.

Housekeeping on 2026-09-02: this directory was put under git with a baseline commit of the state
as found; the 155 compiled programs that had accumulated at the root were moved to
`/data/separate_troll_farm-working/archive/root-binaries-2026-09-02/` (they are rebuildable from
the retained sources and nothing referenced them by path); and a team-repository worktree that a
session had mistakenly created under the working storage was removed, with its branch deleted
locally and on origin and its files kept in
`/data/separate_troll_farm-working/archive/cleanroom-detour-2026-09-01/`. Two standing notes for
future builds. First, the Cargo panel runners in `Cargo.toml` are templates: they need
`E7A_HALF_BASELINE_MODULE` and `E7A_HALF_CANDIDATE_MODULE` set to the absolute paths of a
baseline bridge module and a candidate module (last used:
`candidate_v437_full_baseline_bridge_module.rs` and
`candidate_v439_v437_early_exhausted_one_wood_swap_module.rs`), so a bare `cargo build` fails by
design; only `h10a_spatial_exporter` builds unparametrized. Second, everything that reads
`troll_farm` sources (`Cargo.toml`, `build.rs`, `duel.py`, the runners' path attributes, and the
candidate build scripts) points at the plain checkout `/home/tarstars/prj/troll_farm` at commit
`c13f5635`; the frozen-hash pipelines depend on that checkout not being pulled forward without
re-checking their recorded hashes.

On 2026-09-02 the platform archives were profiled with the team repository's validated replay
tooling to find where the top players' advantage comes from (`ECONOMY-GAP-2026-09-02.md`). V440
issues as many CHOP commands as the top-ranked player, delineate (167 against 170 a game), but
banks 46 wood against 98: 0.28 wood per chop against 0.58. Sixty per cent of V440's chops are made
at chop power 1, and it fells its own trees at size 1 about five turns after planting, where the
referee pays one wood instead of the four a size-4 tree gives. Its wood income is flat at about
15 per hundred turns; delineate's runs 8, 32, 59 because it plants 41 trees a game and chops
mostly its own size-4 trees late. V440 leads every top player's score curve at turn 100 and is
overtaken by all of them between turns 175 and 250; it finishes at 215 where delineate finishes
at 415, putibuzu 246, R1FA 248 and astrobytes 258. Fruit is not the gap (V440 banks 31 fruit
points, delineate 28) and the third troll is a consequence of the surplus, not its cause. The
23 mature readings of this lineage have mean 23.1 and spread 1.1 with no trend, so the old
selection gate, "no recorded win becomes a loss over 960 archived games", is replaced: a
candidate must now match V440's mean own score at turns 100, 200 and 300 on the paired panel and
finish at least 40 points higher, with the old count kept only as a safety check. Re-read with
that yardstick, none of the door-factory candidates V441 to V454 raised own score by more than
4 points and three lost 28 to 39. The tools (`build_profile_corpus.py`, `profile_players.py`,
`score_curve.py`, 6 tests) and the profiles under
`/data/separate_troll_farm-working/profiles/2026-09-02/` are the reproduction.

The first candidates under the new gate, V455 to V458, tested the smallest form of the fix
(`GROW-BEFORE-FELL-RESULTS-2026-09-02.md`): keep V439, leave own planted trees to size 4 before
felling, and let the second troll carry harvest power. All four failed on the 8-map development
panel. The harvest talent cost 39 points on its own: a harvest-2 troll costs five apples instead
of one, the bot trained at the same turn and emptied the apple stock, and the apple orchard, which
needs one apple as its seed, started in 95 of 192 games instead of 185, halving harvests. Leaving
saplings to mature was neutral to slightly negative (-4.0 and -3.2 own score): V439's entrance
farm runs one tree at a time, so the troll that used to fell the sapling every five to seven turns
simply waited (waits rose from 17 to 55 a game) while the one slot produced wood more slowly per
turn than the old one-wood conversion loop. The lesson is that the top players' advantage needs
several trees growing at once, not a slower single one. Nothing was submitted.

The autonomous loop's first iteration (2026-09-02, `DOOR-FARM-RESULTS-2026-09-02.md`) tested the
multi-slot door farm, V459 to V463. None passed the gate. V459 to V461 never engaged the new farm
because V439 plants its seeds through the planner's regeneration path, not the farm layer, so they
repeated V457's -3.4. V462 and V463 adopted those trees into protected slots and lost 27 points:
waits rose to 131 a game and wood fell from 44 to 37 while opponents gained 12. A game trace showed
why: from about turn 50 the baseline's late income is its conversion loop, one banana seed planted
and felled at size 1 every six turns per troll until the stock runs out, and every design that
protects saplings removes that income without redeploying the troll, because nothing else is left
to chop near the shack. The next design keeps the loop and feeds it: one or two permanently
protected, water-adjacent mother bananas whose fruit supplies seeds for both trolls. Nothing was
submitted.

Loop iteration 2 (2026-09-02, `MOTHER-BANANA-RESULTS-2026-09-02.md`) tested one or two protected
mother bananas on water-adjacent doors as a seed source for the conversion loop, V464 to V467,
with a harvest-aware protection in the last two. All four failed, -7.8 to -12.1, with seed picks and
harvests unchanged at the baseline's level. A trace showed the starter is already saturated by the
apple engine, one apple every two turns from turn 20 to the end, and the second troll, which has no
harvest power, plants the mother and then waits for the rest of the game. Fruit is not where the
gap is; protecting any own tree from the planner has now cost points in every variant from V455 to
V467. The queue moves to the second troll's wood per chop trip (tree choice and the denial bonus)
and to funding a third troll by mining iron. Nothing was submitted.

Loop iteration 3 (2026-09-02, `CHOP-TARGET-RESULTS-2026-09-02.md`) removed the planner's chop-target
bonuses one at a time: V468 without the denial bonus toward the enemy shack, V469 also without the
opponent-crop priority. Both raised own score at every checkpoint on the 8-map development panel
(+8.8 and +11.4) and both shrank to about +3 on the 16 fresh maps, with wood unchanged in every
panel: the gain is apple-harvest time that the denial detours had been costing the starter. The
bonuses help against the stronger local families and hurt against the weaker ones. Neither passes
the +40 bar; V468 is a small safe gain with a better win count that the owner may fold into the next
submitted line. The lever for wood is more chopping troll-turns, so the queue moves to the harvest
talent with an apple reserve and then a third troll funded by mined iron. Nothing was submitted.

Loop iteration 4 (2026-09-02, `HARVEST-RESERVE-RESULTS-2026-09-02.md`) gave the second troll harvest
power with an apple reserve of one, V470 up to harvest 2 and V471 up to harvest 1. The reserve kept
the orchard intact and the troll trained at the same turn, but harvests per game did not move: in
this bot the starter does all the harvesting and the second troll only chops, so the talent is
never used and the two to five apples it costs are the whole loss (-3.2 and -1.5). Item closed. The
queue's remaining wood lever is a third troll funded by mined iron. Nothing was submitted.

On 2026-09-02 at 11:25 the owner made V468, V439 without the denial bonus, the development base and
baseline for the loop; `candidate_v468_full_baseline_bridge_module.rs` is its bridge for the panel
runner, and a one-map identity panel agreed on all 24 game rows.

Loop iteration 5 (2026-09-02, `THIRD-TROLL-RESULTS-2026-09-02.md`), on the V468 base, trained a third
troll from a bill gathered by the starter (V472 a 2/2/0/2 troll, V473 a 1/2/0/2) or with the second
troll mining the iron (V474, V475 with a wider window). A 2/2/0/2 troll pays +25 when its bill
completes, but the bill of 6 plums, 6 lemons, 2 apples and 6 iron completed in only 20 of 192 games
with the carry-1 starter, and letting the second troll mine lifted completion to a quarter of games
at the price of 17.7 points by turn 100; all four end within +5 and -2 of the baseline. With that
item the loop's autonomous queue is exhausted and the loop stopped: 21 candidates, V455 to V475,
fail the +40 bar, V468 (+3 on fresh maps) is the only measured gain, and the panels agree that no
single-mechanism addition closes the gap because every gatherer in V439 is already its income.
Nothing was submitted.

The owner approved a multi-mechanism experiment on 2026-09-02 to test whether an opening farm
could feed a third troll's training bill. V476 planted plum and lemon mothers on the shack's door
cells for the starter to harvest, alongside V474's third-troll machinery: a 2/2/0/2 troll trained
once its bill of 6 plum, 6 lemon, 2 apple and 6 iron was affordable. V478 fixed the starter
camping on fruitless trees. V479 let mothers take the ring's diagonal cells on short-door maps
and carried the seed with a four-turn window. V480 widened that window to twelve turns and
targeted the nearest free cell. V481 added a bill run that let the starter leave the apple engine
to harvest a mother directly. V477, a 2/2/0/3 third troll, was built but not measured because
V476 failed the checkpoints. All five measured variants failed the gate: own score dipped 5 to 10
points behind the baseline at turn 100 before recovering to a 10 to 13 point gain at turn 300.
Two mechanisms explained the dip, read from the command stream. V479's four-turn seed-carry
window was too short for a speed-1 troll circling the shack, so the seed was repeatedly forgotten
and rebanked. V480's apple engine took priority over the bill gathering, so the starter
alternated harvest and drop on the watered apple mother for over a hundred turns and left its own
new mothers unharvested. V481's bill run pulled the starter off the apple engine to harvest the
mothers directly, training the third troll more often, 77 of 192 games, but later, and losing
harvests on the ring for the first time, -2.3, while trading apple income for fruit faster than
the third troll repaid it. The item is closed: an opening farm whose bill is fetched by the
starter cannot pass the checkpoints, because the starter is the apple income. The results are
recorded in `OPENING-FARM-RESULTS-2026-09-02.md`. Nothing was submitted.

On the evening of 2026-09-02 the owner, leaving for the night, authorized the whole research
queue to run unattended, and the loop took V468 through the remaining submission-gate steps
first. On the 400-record duel panel V468 won 59.5 % against the champion of record (238 wins,
81 ties, 81 losses, mean margins +13.4 and +16.4 by seat) and 89.5 % against orchard 6 (358, 11,
31, margins +49.5 and +48.8), against V439's 62.2 % and 94.2 % on the same games; the champion
difference is inside one standard error, the orchard 6 difference about two, consistent with the
earlier finding that removing the denial bonuses gives a little back against strong opponents.
The readable and compact V468 programs emitted identical commands in all 160 archived V440
games. The gate steps are recorded in `CHOP-TARGET-RESULTS-2026-09-02.md`; nothing was
submitted, and the upload decision stays with the owner.

Queue iteration V548 on 2026-09-04 gave V481's second troll harvest power one, kept one apple in
reserve, moved both fruit-bill paths off the starter, and fixed the apple mother's pre-plant door
reservation. The mechanism engaged: ring harvests rose 27.2, the third troll trained in 134 rather
than 77 of 192 games, and its median arrival moved from turn 140 to 105. It was still a losing
allocation: the second troll stopped being the main axe, wood fell 7.17, turn-100 score fell 30.5
versus V481, and margin fell 23.39. Its natural-fruit runner also repeatedly collided with the
starter on the occupied apple mother in eight games, but the 91 zero-issue games retained the same
early loss. V548 failed the V468 gate at -40.7/-26.6/+8.1 and was not submitted. The full result is
in `V548-SECOND-HARVESTER-RESULTS-2026-09-04.md`.

V543's platform rollout then matured at 13.92 / rank 155 of 177, with all 160 games archived and
no download failures. Seven first-batch games were turn-1 startup timeouts; over the other 153,
the bot went 86/67 with +11.69 mean margin. That aggregate hid the ladder problem: against active
rating-14+ opponents it averaged -50.29 margin, and the three rating-18+ opponents planted 61.0
trees and banked 160.7 wood to V543's 17.7 and 86.3. Rank 7 remained 26.99. This mature evidence
keeps parallel tree production and productive chopping—not extra fruit collection—as the required
step change. `V543-MATURE-PLATFORM-RESULTS-2026-09-04.md` records the frozen archive and breakdown.

Queue iteration V549 on 2026-09-04 tried to reclaim V481's idle time without repeating V548's
wholesale axe diversion. A harvest-capable second worker moved to a plum/lemon mother only when
its selected action was exactly `WAIT`, and the trip held no state. Waits fell 5.05 and harvests
rose 15.60 per game, but the resulting fruit still forced return and bank turns: drops rose 8.87,
chops fell 18.01, wood fell 5.19, and third-worker completions fell from 77 to 61. Margin fell
11.06 versus V481. Against V468 it was -12.49/-11.04/+7.39 at the three checkpoints and failed;
it was not submitted. `V549-IDLE-FARM-FALLBACK-RESULTS-2026-09-04.md` records the trace and panel.

Queue measurement V550 on 2026-09-04 added the archived V425 reconstruction as a thirteenth
opponent in a separate runner while leaving the frozen 12-family gate unchanged. Exact V468 in
both arms matched commands and outcomes in all 208 rows, and the original 12-family mean remained
247.25. V425 reproduced public R1FA's fixed training ladder in all 16 games with 2.31 versus 2.71
training attempts per game, but it lost every game and reached only 121.88 score and 25.44 wood,
49% and 42% of the 133-game public aggregates; its chop and plant rates were only 46% and 25%.
V425 was retained only as an optional training-signature/adversarial diagnostic, not admitted as
an R1FA proxy or gate family. Nothing was submitted. The result is in
`V550-V425-OPPONENT-MEASUREMENT-RESULTS-2026-09-04.md`.

Queue iteration V551 on 2026-09-04 closed the conditional third-troll item without building a
duplicate candidate because its farm-surplus prerequisite had failed. V548 already made the
mechanism engage, moving third-worker completion from 77 to 134 of 192 games and median arrival
from turn 140 to 105, but it lost 40.70 points at turn 100, 7.17 wood and 23.39 margin versus its
V481 parent and finished only 8.11 above V468. V472--V481 showed the same cause: a third troll
pays when it arrives, but collecting its bill consumes the existing apple or wood income. The
next queued mechanism preserves exact V468 through the opening and hands its banked two-worker
state to the repaired dense economy, a composition not tested by the failed funding lineage.
Nothing was submitted. `V551-THIRD-TROLL-PREREQUISITE-AUDIT-RESULTS-2026-09-04.md` records the
audit.

Queue iteration V552--V554 on 2026-09-04 ran exact V468 through turns 80, 100, or 120 and then
initialized V546's repaired ten-tree economy. A first trace exposed illegal harvest assignments
to V468's harvest-zero chopper; capability guards removed all but one noncritical issue before the
final panels. The transition itself still failed. None of 192 exact turn-101 states could
afford even a `1/1/1/1` third worker because every inventory held fewer than three plums, so R1FA
spent 80--130 turns redirecting the starter and chopper to rebuild its bill. Ring chops fell by
about 40 per game, moves nearly doubled, and final score deltas were -52.7, -60.1, and -59.9.
V553/V554 were exactly V468 through turn 100, proving that timing did not cause reconstruction
drift. A V546 recheck found no individual row meeting every gate condition, so whole-game
selection cannot rescue the composition. All variants failed and nothing was submitted.
`V552-V554-DENSE-HANDOFF-RESULTS-2026-09-04.md` records the panels and trace.

Queue measurement V555 on 2026-09-04 audited every unambiguous mature-tree chop in V543's frozen
platform games against rating-14+ opponents. The bot selected the best comparable current cycle
on 1,554 of 1,593 turns (97.6%). Its 13 losses contained ten actionable miss episodes and only six
material episodes; all better alternatives were natural or own-planted, never opponent-planted.
The sole missed opponent-planted alternative was one non-material turn in a +4 win. Mature target
choice is therefore too small to explain the ladder wood gap, and no candidate or submission was
opened. The next audit moves upstream to the constraint behind V543's low planting cadence.
`V555-CHOPPER-TARGET-AUDIT-RESULTS-2026-09-04.md` records the method and frozen evidence.

Queue measurement V556 on 2026-09-04 found that V543's public planting deficit was a crop-policy
lock rather than missing seeds or cells. In the three rating-18+ losses, all 276 post-fourth-worker
states had banana supply and usable source geometry and 273 had a reachable ripe banana, but the
producers harvested banana zero times. Maintenance saturation blocked 188 states; across the other
88 open-slot states the old lemon/apple routes refilled the orchard. V543's 21 post-training births
were 19 lemons and two apples, while the opponents' full games produced 183 generations, 163 of
them bananas, against V543's 53 and zero. No free override or candidate was claimed. The next item
keeps exact V468 through turn 100 and tests a bounded mature-banana reserve near the shack, avoiding
both R1FA's slow opening and another third-worker bill.
`V556-PLANTING-CONSTRAINTS-RESULTS-2026-09-04.md` records the audit and artifacts.

Queue iteration V557--V559 on 2026-09-04 wrapped exact V468 with one, two, or three near-shack
banana-reserve plots after turn 100 and nearby-wild exhaustion. A conversion-only start gate and
provenance repairs preserved every command through turn 100, kept two workers, and eliminated
critical issues. All caps still failed: V557 was -0.65 at turn 200 and +0.02 final; V558/V559 were
-0.63 and -0.01 and were behaviorally identical. The 52 changed games kept own score flat while
opponents gained 4.46. Ten extra banana plants displaced 35 apple pick/plant cycles, and harvest
routing added movement and waits while protection removed chops. The mature reserve consumed both
established roles instead of adding capacity, so nothing advanced or was published. The next item
isolates that finding by testing parallel size-four banana wood batteries without diverting the
starter to harvest. `V557-V559-CHAMPION-PREFIX-BANANA-RESERVE-RESULTS-2026-09-04.md` records the
panels and integrity locks.

Queue iteration V560--V562 removed the starter from that mature-banana reserve and assigned every
battery action to V468's higher-id chopper. Fruit-only masking and an immediate apple-commitment
guard repaired early versions without disturbing any command through turn 100. The full panels
still failed: cap one was -0.58 at turn 200 and +0.03 final; caps two and three produced identical
game rows at -0.63 and +0.05. The harvest-free form still displaced 35--38 apple cycles across the
panel, and cap two lost 2.26 chops, added 3.97 moves and 2.38 waits, and banked 0.13 less wood per
game. Opponents gained 1.22 and the candidate added a loss. This closes mature batteries on the
two-worker roster; nothing advanced or was published. The next audit reconstructs how rating-18+
public opponents fund their extra workers without the opening deficit seen in V472--V554.
`V560-V562-HARVEST-FREE-BATTERIES-RESULTS-2026-09-04.md` records the implementation, panels, and
integrity hashes.

Queue measurement V563 reconstructed every rating-18+ opponent hire in V543's mature archive.
The three active records contained seven successful `TRAIN` commands; commands, next-state births,
inventory debits and tooltips agreed exactly. The bots did not hide a free worker bill inside an
active wood loop: before every hire they performed zero chops while repeatedly harvesting a small
plum/lemon/apple source set and mining iron, then trained at first affordability. The actionable
difference was worker three. Bl4sterino/BoatBuilder and V543 reached it at the same mean turn 61,
but their capacity-three/four thirds reached worker four at mean turn 101 versus V543's 145.5.
A rating-14+ sensitivity decoded 21 active games: exact `2/3/1/2` thirds reached four in 6/6 games,
the elite `3/4/2/3` did so once, and eleven other thirds reached four zero times; every scaling
interval again had zero chops. No gameplay or platform state changed. The next item isolates those
two stronger third-worker specifications in V546's repaired dense source economy.
`V563-WORKER-FUNDING-PROVENANCE-RESULTS-2026-09-04.md` records the per-worker provenance,
limitations, archived reports, and integrity hashes.

Queue iteration V564--V565 on 2026-09-04 changed only V546's third-worker specification. V564's
observed `2/3/1/2` third was a genuine late accelerator: against exact V546 on the same 192 games
it gained 40.24 final own score, 10.21 wood, 32.31 margin, eight wins, and nine additional
fourth-worker completions; every opponent-family delta improved. The larger `3/4/2/3` V565 bill
arrived too late and finished 32.85 behind V546. V564 still inherited the dense opening deficit,
losing 68.75 points at turn 100 and 27.80 at turn 200 versus exact V468. A hindsight whole-game
selector between V468 and V564 can preserve both early checkpoints but gains at most 0.44 final
points, far below the +40 gate. Neither candidate advanced or was published. The next item keeps
the second worker chopping during a minimal producer-only bill farm, then hands the new
capacity-three worker to V564's measured late policy.
`V564-V565-HIGH-CAPACITY-THIRD-RESULTS-2026-09-04.md` records the isolation tests, panels, selector
bound, and archived artifacts.

Queue iteration V566 on 2026-09-04 reserved V564's higher-id second worker as an immediate axe
while the original worker alone built the third-worker bill, restoring the exact dense role map
after the `2/3/1/2` worker arrived. This recovered 44.14 turn-100 points versus V564, but the
carry-one producer moved worker three from mean command turn 96.59 to 165.53; fourth-worker
completions fell from 175 to 134 and final score fell 156.16. Against exact V468, V566 scored
-24.61/-59.94/+15.31, missed the +40 gate, and added 20 losses. It still performed 13.34 fewer
chops and 8.08 fewer harvests than V468 through turn 100 while using 37.75 more moves and 4.93
more plants. The next item reverses the specialization—carry-two worker producing, original
worker chopping—and compares source-first with natural-fruit-first collection. Nothing advanced
or was published. `V566-ONE-AXE-DENSE-OPENING-RESULTS-2026-09-04.md` records the isolated changes,
full panel, timing mechanism, and integrity hashes.

Queue iteration V567--V568 on 2026-09-04 reversed V566's two-worker allocation so the trained
movement-two/carry-two worker produced and the original worker chopped. The role swap worked as a
late accelerator: third/fourth-worker completions rose from 165/134 to 173/159 and final score rose
27.87 versus V566. It still lost 52.37 and 91.06 points to exact V468 at turns 100 and 200; its
43.18 final gain came with 31 additional losses. Harvesting reachable ripe deficit fruit before
planting recovered 11.10 at turn 200 but lost 6.07 final and added 14 more losses. Both candidates
failed, so no fresh panel, packaging, or publication opened. The dense roster-allocation line is
closed; the next item tests an early-grown banana wood reserve behind the exact champion prefix.
`V567-V568-CAPACITY-TWO-PRODUCER-RESULTS-2026-09-04.md` records the panels and mechanism.

Queue iteration V569--V571 tested one, two, and three early-grown banana wood reserves behind
V468's exact observed-second-worker prefix. Masking protected trees from the inner target selector,
ending reserve harvest after one fruit, and delaying starts to turn 45 repaired targeting and
lifecycle defects, but all arms failed the behavior gate. Their turn-100/200/final deltas were
-2.75/-5.21/-6.08, -5.38/-2.00/+6.88, and -5.75/-2.38/+5.38. Reserve work added 35--36 moves,
removed 36.5--54.6 chops, and left about 47.5 wood versus V468's 53.2; the carry-two feller could
bank only half of a mature tree's four wood. No full panel or publication opened. The next item
tests the missing architectural interval: exact V468 through its observed second train, followed
immediately by a capability-aware handoff into V564's proven capacity-three dense scaling.
`V569-V571-EARLY-BANANA-RESERVE-RESULTS-2026-09-04.md` records the repair path and integrity locks.

Queue iteration V572--V574 moved the V564 dense handoff to the first state after V468's own second
worker appeared. The state gate preserved all 192 first-train command/turn pairs across five
harvest-zero worker specifications. Capability-aware V573 still scored -24.20/-49.43/-25.69 at
turn 100/200/final, went 154/0/38 versus 177/3/12, and allowed opponents 18.57 more points. It
trained 159 capacity-three third workers and 93 fourth workers, but replacing both inherited
command policies added 202.46 moves while removing 39.59 chops and 12.75 harvests. V574's live
fruit credit gained 2.16 at turn 100 relative to V573 but lost 16.08 final and reduced later-worker
completions. No arm passed or was published. The next item preserves the champion axe command and
splices only bounded bill work into the starter until a third worker actually exists.
`V572-V574-OBSERVED-SECOND-DENSE-HANDOFF-RESULTS-2026-09-04.md` records the panels and mechanism.

Queue iteration V575--V577 preserved the inherited harvest-zero worker's exact V468 continuation
and lent only the original starter to bounded R1FA bill macros. Explicit worker-ID routing and a
V468-priority destination guard repaired cross-controller composition to zero movement issues.
Cooldowns 48/32/16 scored +0.67/+2.21/+0.17, +0.79/+3.75/-2.04, and
+1.00/+2.54/+1.38 at turn 100/200/final on the 24-game smoke. All three emitted zero mines and
zero third-worker trains, so the best final gain was only 1.38 versus the required 40. No arm
entered the full panel or was published. The next queue item tests continuous starter ownership
through a whole third-worker bill while retaining the repaired per-role boundary.
`V575-V577-PER-ROLE-BILL-SPLICE-RESULTS-2026-09-04.md` records the candidates and evidence.

Queue iteration V578--V580 kept the V468-priority inherited worker and gave only the starter one
continuous R1FA bill attempt. V579's 192-turn horizon gained +7.25/+21.04/+34.46 on the 24-game
smoke and improved own score against all 12 families, so it entered the frozen panel. Across 192
games it reversed to -14.24/-26.83/-31.20, went 158/2/32 versus V468's 177/3/12, and trained only
three third workers. Reassigning V468's main producer removed 55.53 harvests and 59.84 deposits
while adding 113.70 moves per game. No arm passed or was published. The controller-handoff line
is closed; the next item preserves the producer and tests a cheap hire funded from already-banked
fruit plus axe-only iron.
`V578-V580-CONTINUOUS-STARTER-BILL-RESULTS-2026-09-04.md` records the full evidence.

Queue iteration V581--V583 left V468 fully in control and proposed mining only with its
harvest-zero axe after an already-banked fruit bill appeared. The three worker specifications
were byte-identical to V468 across the standard smoke and a targeted fruit-heavy seed, 48 games
per arm. Even V581's cheap `1/1/1/1` bill never became simultaneously available after reserving
same-turn seed picks with at least 96 turns left, despite 115.5 harvests and 140.2 deposits per
game on the targeted seed. No arm mined, trained, entered the full panel, or was published. The
next item preserves V468's harvest routes but escrows the minimum fruit bill by declining only
seed picks that would consume it.
`V581-V583-SURPLUS-AXE-HIRE-RESULTS-2026-09-04.md` records the reachability evidence.

Queue iteration V584--V586 protected the cheapest third-worker fruit bill by declining only V468
seed picks that would breach its reserve. Immediate, living-source, and ripe-source activation
produced identical gameplay: +0.00/-3.38/-13.17 at turn 100/200/final, with outcomes falling from
19/1/4 to 17/0/7. Each arm removed 4.50 picks and plants, 25.79 chops, and 4.42 final wood while
adding 17.75 waits per game; none completed the diversified bill or trained a third worker. The
source renewal and bank reserve are inseparable in V468's two-worker loop, closing the current
third-worker-funding line. No full panel or publication opened. The next item refreshes the public
rank-seven gap before choosing a new mechanism.
`V584-V586-BILL-ESCROW-RESULTS-2026-09-04.md` records the candidates, smoke, and integrity locks.

Queue measurement V587 refreshed the live top 15 from 1,735 unique public games with zero decode
failures. Rank seven remains 26.99, but the exact putibuzu agent/submission moved from rank 13 at
24.92 on August 2 to rank 7 at 26.99 without a code change; its two windows overlap in 63 games
and contain 198 unique games. Only one opponent identity overlaps its current window and V543's,
so their raw scores are not a causal comparison. The repeatable architectural signal is
two-worker orchard throughput: rank seven finishes 114/116 games with two workers, rank eight
121/122, and rank one's 58 two-worker games average 34.72 plants, 47.53 own-crop wood, 60.71 final
wood, 278.10 score, and 43/1/14 outcomes. The next item builds a scratch two-worker parallel
orchard whose task allocator owns the full crop lifecycle rather than wrapping V468's saturated
planner. No gameplay or platform state changed.
`V587-RANK7-GAP-RESULTS-2026-09-04.md` records the version lock, schedule boundary, and archive.

Queue iteration V588--V590 kept exact V468 through turn 100, disabled every later-worker bill,
and handed its two workers to one capability-aware allocator with live orchard caps six, eight,
and ten. Cap six was best but scored only +0.00/-2.38/+13.04 at turn 100/200/final; larger caps
regressed progressively. The allocator added 26.58 harvests and 59.21 moves while removing 3.63
plants, 31.71 chops, and 4.13 banked wood per game. Its harvest-any-ripe priority and lack of a
maturity guard for owned trees prevented repeated mature crop lifecycles; increasing the cap added
plants but no wood. All arms failed the smoke gate, so no full panel or publication opened. The
next item keeps the terminal two-worker architecture but makes ownership, mature felling, and
same-kind refill explicit allocator invariants.
`V588-V590-TWO-WORKER-PARALLEL-ORCHARD-RESULTS-2026-09-04.md` records the candidates and mechanism.

Queue iteration V591--V593 added typed crop ownership, durable same-kind refill, owned-only harvest
priority, and maturity targets two, three, and four to the terminal cap-six economy. Target-two
V591 scored +0.00/+15.83/+33.54 on the 24-game smoke and improved every family, so it entered the
frozen panel. Across 192 games it reversed to +0.00/-15.66/-22.20 and added 15 losses. The orchard
mechanism did work—V591 added 8.68 plants, 20.37 chops, and 4.42 wood—but the full controller
handoff removed 30.97 harvests and 39.18 deposits. It won on all three maps where V468 averaged
fewer than four harvests and lost on all five maps where V468 averaged at least 84.7. No fresh
panel or publication opened. The next item keeps V468's producer commands exact and redirects only
its harvest-zero axe around recorded owned crops.
`V591-V593-MATURITY-OWNED-LIFECYCLE-RESULTS-2026-09-04.md` records the transfer boundary.

Queue iteration V594--V596 ran one real V468 controller continuously and changed only its empty,
harvest-zero axe after turn 100. Persistent provenance from actual V468 plant commands protected
size-one crops; V595 also prioritized carry-matched size-two crops. Protection and positive
priority scored +0.00/+1.79/+9.75 and +0.00/+1.50/+10.46 on the 24-game smoke. V595 retained all
harvests and gained 2.25 wood, but first divergence had median turn 234 and waits rose 8.46 while
plants fell 1.42. Requiring empty fruit was gameplay-identical. The safe role boundary works, but
V468's existing 13.38 plants cannot provide the +40 step change, so no full panel or publication
opened. The next item lets only the axe seed a bounded secondary orchard from banked surplus while
the producer remains under V468.
`V594-V596-PRODUCER-PRESERVING-AXE-RESULTS-2026-09-04.md` records the scope and ceiling.

Queue iteration V597--V599 let V595's empty axe spend one fruit above a one-seed bank reserve on
one, two, or three live near-bank secondary crops. Cap one was best at
+0.00/+3.46/+14.13 at turn 100/200/final, retained the producer's two harvests, gained 3.25 wood,
and improved outcomes from 19/1/4 to 20/3/1. It nevertheless added only 0.29 plants over V595:
V468's axe already planted 8.58 crops, while V597's serial seed/mature/fell work planted 6.00 and
added 19.21 moves. Larger caps extended games and reduced score. No arm reached the +40 smoke bar,
so no full panel or publication opened. The next item preserves every inherited producer income
action and converts only selected power-one chop opportunities into a second crop lane.
`V597-V599-AXE-SEEDED-SECONDARY-ORCHARD-RESULTS-2026-09-05.md` records the candidates and mechanism.

Queue iteration V600--V602 replaced only post-turn-100 producer wood actions with surplus seed,
tagged-crop harvest, or premature-chop redirection while retaining every inherited income action.
Cap one failed turn 200 at +0.00/-1.21/+10.58; caps two and three were gameplay-identical at
+0.00/+0.92/+12.75. V601 issued 3.83 more producer picks but only 0.54 more producer plants, while
axe plants fell 2.46 and harvests stayed exactly 2.00. Every one of V468's 115 producer picks led
directly to `PLANT`; 72 of the candidate's 207 led to `DROP`, showing that injected seeds entered
the wrong native planner phase. No full panel or publication opened. The next item couples a
reserved harvest-capable second-worker bill with the explicit lifecycle that V470 lacked.
`V600-V602-LOW-POWER-PRODUCER-ORCHARD-RESULTS-2026-09-05.md` records the boundary and mechanism.

Queue iteration V603--V605 trained a harvest-one axe and gave it an explicit typed
seed-to-size-four-to-harvest-to-fell lifecycle with plot caps two, four, and six. The initial smoke
found and repaired a selector defect that rejected the worker's own planting cell; rebuilt V605
then exercised the intended pipeline, adding 11.58 plants and 19.71 harvests. It still scored
-36.75/-27.25/+5.96 at turn 100/200/final: crop work removed 36.34 early chops, including 15.05
from the inherited starter after the new plots changed its global planner state. Games ran 28.5
turns longer, own wood gained only 0.21, and opponents gained 84.33 score. No arm entered the full
panel or publication. The next item preserves V468 through turn 100 and isolates worker-owned plots
from the starter before activating the mature lane.
`V603-V605-DUAL-WORKER-LIFECYCLE-RESULTS-2026-09-05.md` records the repaired evidence and mechanism.

Queue iteration V606--V608 restored V468's harvest-zero train, stayed command-identical through
turn 100, then gave the axe a typed harvest-free mature-fell lane. V606 left those plots visible
to the inherited planner; V607 masked them as inert occupied plants for the planner only; V608
raised the isolated cap from six to eight. Isolation removed the starter's extra crop servicing
and all movement issues, but V607 scored +0.00/-6.04/-5.79 at turn 100/200/final. It made 8.88
more chops, ran 9.67 turns longer, and banked 1.04 less wood. The referee awards size-four wood
only on death and discards any amount beyond the killers' free capacity, so the lone carry-two axe
paid mature health while losing half the four-wood payout. Caps six and eight were behaviorally
identical. No full panel or publication opened; the next item measures carry-three/four training
cost separately before combining higher capacity with the isolated lane.
`V606-V608-STARTER-ISOLATED-DELAYED-ORCHARD-RESULTS-2026-09-05.md` records the candidates and rule-bound ceiling.

Queue iteration V609--V611 aligned mature-tree payout with a larger second worker. The
capability-only carry-three V609 scored +12.00/+20.38/+39.83 on the standard smoke; adding the
isolated lane made V610 the first exact smoke pass in this line at +12.00/+29.83/+40.00. The
frozen 192-game panel then reversed to -34.72/-49.37/-42.01 and 46 added losses. Carry three
trained at turn 14 on the smoke map but mean turn 54.3 across the field, removing 29.21 harvests
and 35.39 deposits; two games never trained. Carry four slipped to turn 98 even on the smoke map.
A row-level hindsight selector using V610 only where every checkpoint improves gains just +4.82
final, so a safer ETA cutoff cannot supply the required +40. No fresh maps, duels, packaging, or
publication opened. The next item aligns all structurally distinct frozen panels to measure
whether any cross-lineage portfolio has a realizable step-change ceiling.
`V609-V611-CARRY-ALIGNED-MATURE-WORKER-RESULTS-2026-09-05.md` records the smoke pass, reversal, and bound.

Queue item 29 inventoried every 192-row TSV in working storage and admitted 53 files whose row
keys and immutable V468 command/score fingerprints matched exactly, representing 40 distinct
candidate behaviors. The strongest checkpoint-safe row hindsight oracle gained only 25.55 final
points. An exact-map aggregate optimizer reached +0.07/+5.58/+37.84 at turns 100/200/final and
therefore missed the gate; adding exact seat identity barely reached +0.02/+0.82/+44.36 by mixing
seven lineages. A 69-feature selector trained without each held-out map scored
-4.67/-4.71/-0.37, so the apparent complementarity did not generalize from observable board
features. No candidate or publication opened. The next item tests a new chronological economy:
exact V468 through its own second train, then an up-front near-bank banana reserve that grows in
parallel while the axe returns to wild chopping.
`V612-CROSS-LINEAGE-PORTFOLIO-RESULTS-2026-09-05.md` records the inventory and exact bounds.

Queue iteration V612--V614 kept V468's exact second-worker train and redirected only its
harvest-zero axe to plant batches of two, four, or six near-bank banana reserves before resuming
wild work. Every arm completed its requested batch in all 24 smoke rows, but full-game banana
plantings stayed effectively fixed at eight: the early reserves consumed V468's existing seeds
instead of adding throughput. Each reserve pair displaced about one later ring plant while the
axe ceded wild trees, so the arms regressed monotonically by -5.96, -11.17, and -20.67 final;
own wood fell while opponent wood rose with cap. No arm entered the frozen panel or publication.
The next item keeps the seed schedule untouched and tests whether the existing two workers can
pool chop power and free carrying capacity on mature wild trees.
`V612-V614-NEAR-BANANA-RESERVE-RESULTS-2026-09-05.md` records the active branch and displacement mechanism.

Queue item 31 stopped before candidate construction because the proposed two-worker chop/payout
pool is impossible under the referee. Movement is resolved separately for each player and
preserves one own unit per cell, whereas chop damage and death wood are shared only among trolls
already occupying the tree's single cell on that fatal turn. Sequential pre-damage cannot add the
departed worker's capacity, and V468's assignment compatibility already forbids duplicate own tree
targets. Cross-player sharing is physically possible but was already rejected in V422's adaptive
continuations, so it was not reopened. The next item instead repairs V600's measured incomplete
seed transaction: explicitly carry an injected producer seed through planting rather than letting
the native wood phase drop it.
`V615-OWN-WORKER-POOLING-FEASIBILITY-RESULTS-2026-09-05.md` records the rule proof and source hashes.

Queue iteration V616--V618 made injected producer seeds durable across movement and retargeting.
All 107 routed jobs across caps one, two, and four ended in a matching plant with no transaction
drops, but the candidates scored only +5.13/+8.75/+9.88 final and all regressed at turn 200.
V618 completed 48 routed plants yet planted 0.21 fewer crops than its V595 parent, added 28.54
moves, removed 6.83 chops, and finished 0.54 lower. The explicit route replaced V468's native
one-turn producer planting rather than adding throughput, closing further overlays on that
saturated seed/action schedule. No full panel or publication opened. The next item uses the
read-only 215-replay rank-one reconstruction to build an integrated shack orchard with a local
farmer, rapid capable second worker, banana production, and mature own-tree felling.
`V616-V618-PERSISTENT-PRODUCER-SEED-TRANSACTION-RESULTS-2026-09-05.md` records the completion and
parent comparison.

Queue iteration V619--V621 kept V468 command-identical through turn 100, then replaced both roles
with one typed orchard allocator reconstructed from 215 read-only rank-one replays. After repairing
a deposited-seed loop and a persistent collision wait, V619 added 9.37 plants and 17.46 harvests
per game but scored only +0.00/-21.75/+1.42 at turn 100/200/final. Its crop refills produced 11.46
slow apples and only 4.62 bananas, wood fell 1.50, and the carry-four/chop-three third worker never
trained despite six mines per game. Moving the opponent-raid end to turn 150 or 200 changed final
gain only to +1.79 or +3.04 and worsened the middle checkpoint, identifying conversion and bill
reachability rather than raid timing as the common failure. No full panel or publication opened;
the next item tests an affordable staged orchard worker before escalating capacity.
`V619-V621-RANK-ONE-SHACK-ORCHARD-RESULTS-2026-09-05.md` records the repaired family and mechanism.

Queue iteration V622--V624 made the integrated orchard banana-first and reduced the proposed third
worker to `1/2/1/2`, `2/2/1/2`, or `2/3/1/2`. Tests and two smoke repairs stopped scarce bill
fruits from being replanted and protected their natural source trees, but none of the three workers
trained in 72 final rows. At turn 220 the cheapest arm had all required apple and iron, while 21 of
23 surviving rows still lacked lemon and 10 lacked plum; the exact V468 prefix leaves one
harvest-power-one starter competing for finite natural fruit. V623 planted 9.79 bananas and raised
wood per chop from 0.291 to 0.355, yet 35.21 fewer chops left wood 0.88 lower and scored only
`+0.00/-11.38/+2.17` at turn 100/200/final. No full panel or publication opened. The next item
capitalizes the first scarce fruit into a protected local mother before reserving the worker bill.
`V622-V624-STAGED-ORCHARD-WORKFORCE-RESULTS-2026-09-05.md` records the inventory proof and repair trail.

Queue iteration V625--V627 invested the first deficient plum, lemon, or both in a protected
water-first mother near the shack before reserving the `1/2/1/2` third-worker bill. The selected
sources existed by turn 220 in 17/24, 19/24, and 16/24 rows, but they only produced two late trains
in V626 and two in V627 at turns 210--219. Source-aware harvest priority repaired the intended
path, yet all untrained turn-220 rows already had enough apple and iron and remained short in plum,
lemon, or both. The final arms scored only `+0.00/-8.46/+0.33`,
`+0.00/-14.71/+1.17`, and `+0.00/-14.13/-0.08`; added harvests displaced about 36 chops,
reduced wood, and did not repay by turn 200. No full panel or publication opened. The next item
replaces the directly useful third worker with a much cheaper independent producer bridge before
attempting mature-wood capacity.
`V625-V627-CAPITALIZED-SCARCE-FRUIT-MOTHERS-RESULTS-2026-09-05.md` records the source timing and bill audit.

Queue iteration V628--V630 replaced the late useful-worker bill with a cheaper `1/1/1/0`
producer, then optionally staged a `1/2/1/2` or `2/2/1/2` fourth worker. Source multiplication
worked after a reciprocal three-worker swap repair removed corridor stalls: trained producers
averaged about ten harvests and seven plants. They still appeared in only 8/24 rows at turns
153--176, and every trained V629/V630 row remained short in plum, lemon, and apple at turn 220;
no fourth worker trained. The arms scored only `+0.00/-9.83/+7.00`,
`+0.00/-13.42/+7.38`, and `+0.00/-13.42/+7.83` at turn 100/200/final. Added crop work
displaced about 34 chops, barely changed wood, and raised opponent score by 35--38, so no full
panel or publication opened. The next item reverses acquisition order: a cheap early producer
before the first capable axe.
`V628-V630-STOCK-LIGHT-PRODUCER-BRIDGE-RESULTS-2026-09-05.md` records the scheduler repairs and stock audit.

The owner's September 5 request for a from-scratch review paused the candidate queue before V631
was built. A fresh platform read confirmed V543 at 13.92/rank 155 and seventh place at 26.99. The
review found that the early own-score gate did not express ladder success, the repeated one/eight-map
proxy panels did not establish field strength, and several strategic closures exceeded their
evidence. An executable V630 probe also showed its crop-quota harvest filter selecting an unneeded
banana over a ripe, deficient lemon. Existing gameplay and panel results were preserved; the draft
V631 test was archived. `CRITICAL-REVIEW-2026-09-05.md` records the evidence and makes evaluation
calibration the next priority before more candidate tuning.

The September 5 field pilot ran ten unranked games against the exact rank-one, rank-seven and
rank-sixty agents, including one identical-bot repeat. A/A passed. All three scored policies lost
all three blocks, with mean margins -138.00 for V468, -272.33 for V543 and -259.00 for V564. Against
putibuzu, the dense policies lost their lemon sources, never trained a third worker and never
issued a CHOP despite 99/117 harvests. The audit also found a visualization-order reconstruction
defect: restoring sprite creation order removed two local/official command mismatches, leaving
all 2,552 turns exact. The success monitor was corrected to verified top seven with delayed
confirmation, and `EVALUATION.md` superseded the early-score selection rule. Production and the
read-only neighbor were unchanged; no new ladder agent was submitted. The next gameplay work is
a tested productive fallback under resource denial, not another late-worker quota sweep.
`FIELD-CALIBRATION-RESULTS-2026-09-05.md` preserves the results, limitations and reproduction paths.
