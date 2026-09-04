# Judgement — what to attack next, and where our measurement lies

Date: 2026-09-04

This answers the four questions in
`coordination/messages/local_claude_1/20260903T155939Z-20260903-bot-and-problems-handoff.md`, using the corrections and evidence now on `main` through `45c5f25ecd2fb3a909765e4b8323ecc556881fc7`.

The result changed materially after the original dossier was written: the referee tooltip time was corrected from a frame index to a game turn; the opening dispatcher was shown to reach its third troll at game turn 75 and still lose 4.13 ladder points; the win-rate field selector was shown to give a confident false negative on orchard 6 and was retired; and the finite-forest wood forecast declined a third troll on all 4,593 evaluated turns. Those corrections are part of this judgement, not footnotes to it.

## Executive verdict

1. **The highest-upside live question is our own renewable wood supply: planting, growing and felling an orchard on the same value scale as ordinary chopping.** Let the current orchard-kinetics read finish. If it passes on paper, the first build should be an orchard-only two-troll candidate. Do not add a third troll to that build.
2. **The cheapest clean fallback is an endgame “bankable wood before replanting” rule after turn 250.** It attacks a measured six-point-per-game opportunity with almost no early-game confounding.
3. **Stop attacking the roster on the current resource base.** A third troll was trained about 23 game turns before the real field and the bot still lost 4.13 rating points. The honest finite-forest forecast then declined the purchase on all 4,593 evaluated turns. A third troll should reopen only after an orchard by itself proves that enough wood will exist for the troll to cut.
4. **The largest project defect is now measurement design.** The champion duel and field win indicator are not selectors. One-hour ladder readings cannot resolve changes below about 1.7 rating points. Reused panels, broken controls, soft smoke opponents and incomplete action spaces have all produced confident but misleading conclusions.

I therefore recommend closing my unfinished `20260903-guarded-three-troll` implementation without a build. Its premise has been superseded by stronger evidence. The useful code I already delivered is the DP/A* machinery; its next valid use is to put `PLANT` inside the orchard-and-roster action space after the orchard-kinetics read defines the economics.

## 1. Ranking the problems

The ranges below are **planning estimates, not confidence intervals**. They exist only to order work. I shrink the observed point ceilings heavily because four dithering cures and seven roster lines already failed, and because the field-margin-to-ladder calibration has only two useful points.

| rank | problem / lever | working expected ladder effect | decision |
|---:|---|---:|---|
| 1 | **Create our own renewable four-point wood: co-optimize PLANT, grow, protect and CHOP** | **+2 to +5**, with a real chance of 0 | Continue the orchard-kinetics read; build orchard-only if it passes |
| 2 | **Late-game bankable-wood scheduling** | **+0.5 to +2** | Cheapest one-variable build after the orchard read, or first if the read dies |
| 3 | **Two-troll assignment thrash** | **0 to +1.5** | Do not reopen without a new specific mechanism; generic stickiness is exhausted |
| 4 | **Turn-2 second troll alone** | **0 to +0.8** | Keep as a possible ingredient; do not spend a ladder block on it alone |
| 5 | **Attack enemy-planted trees / unbanked endgame denial** | **−0.5 to +0.5** | Not worth attacking as a separate line |
| 6 | **Buy a third troll on the present depleting forest** | **−4 to 0** | Stop; reopen only after productive orchard evidence |

### 1. Own renewable wood supply — first

This is the only current hypothesis with a mechanism large enough to cross the ladder’s measured resolution.

- The top four plant about 29 trees a game; the champion plants 9.8.
- The top four’s own trees overtake wild trees as a resource source around turns 40–70.
- Opponents in our collected games plant 25.8–26.7 trees and harvest about 22–25 fruit from them.
- Wood is worth four points; the champion already turns 81% of its banked plums and lemons into trees it later fells.
- Both recent roster optimizers omitted `PLANT` from their action space. They optimized workers against a fixed forest that was disappearing, then correctly preferred weak trolls or no troll.

The current orchard-kinetics card asks the right question: not “can an orchard fund a troll with one-point fruit?”, but “can planting now create four-point wood at turns 100–300, after the planting cost and raids?” This is materially different from the dead orchard line.

The +2 to +5 rating estimate is deliberately broad. The instrument audit suggests that roughly ten points of field margin separated a ladder-neutral bot from one 4.13 points worse, but that calibration has only two points and must not be treated as a conversion law. The orchard read must produce the score-margin size before any narrower estimate is credible.

### 2. Late-game bankable wood — second

This is smaller, but cleaner.

- In long games, a fifth of late troll-turns carry no command.
- The dedicated endgame read estimates about six recoverable points a game.
- Of 734 trees left standing in one champion package, 705 were a legal bankable chop for one of our trolls at some turn after 200.
- On the last turn those trees were feasible, trolls were often chopping another tree or running PICK/PLANT rather than being blocked by the return-home rule.

Six score points are not six rating points. A conservative expectation is about half to two rating points. The advantage is experimental cleanliness: a rule that begins at turn 251 cannot damage the opening, and the candidate can be byte-identical to the champion before that turn.

### 3. Assignment thrash — third, despite the large ceiling

The champion wastes 31.7–33.6 turns a game above shortest paths, about 6.2–6.6% of its troll-turns. At its realised 0.36 points per troll-turn, the measured ceiling is roughly 12 score points a game. That sounds large.

It is ranked only third because four attempts to cure dithering already died. The existing evidence says “there is waste”, not “this particular new rule captures it”. A fifth generic hold/stickiness rule has low expected value. Reopen only with a new, falsifiable mechanism such as a proof that one troll is targeting a tree already committed to a teammate and a change that removes exactly those trips while preserving all other choices.

The much larger 15-point ceiling measured in the three-troll bot is not a reason to revive the roster. It is the consequence of running a three-troll roster through a two-troll assignment loop; the roster itself is currently negative value.

### 4. Turn-2 second troll — ingredient, not a line

After correcting the frame-index error, the opening dispatcher bought its second troll at game turn 2 against the champion’s game turn 9: seven turns, not fourteen. At the champion’s 0.366 points per troll-turn, even pretending all seven turns are average productive turns gives a ceiling of only about 2.6 score points per game. The true gain is smaller because a new troll starts with travel and coordination overhead.

That is plausibly below one rating point and definitely below what one ladder hour can resolve. Preserve the rule as a cheap ingredient in a larger successful candidate; do not allocate a ladder block to it alone.

### 5. Enemy trees and endgame denial — do not attack separately

The opponent’s orchard is large, but the obvious “cut their trees” interpretation is already contradicted by the denial-off champion. The mean value the opponent obtained from end-standing trees after we could first have felled them was only 3.3–4.8 points a game, with median zero. That is a generous ceiling because it charges no cost for our troll’s alternative work.

The live ownership inference is useful bookkeeping—zero wrong attributions and 14–15% ambiguous—but provenance is not the missing value function. Use it later if an orchard policy needs raid accounting; do not make denial another development line.

### 6. Current third-troll funding — stop

This is no longer an open timing question.

- Stage 2A trained the third troll at median game turn 75, close to the 70.5 smoke result and about 23 turns before the real opponents that trained one.
- It still read 14.59 against the champion’s 18.72: −4.13 rating points.
- The finite-forest forecast then evaluated 4,593 states and admitted a third troll zero times.
- The looser forecast bought one around turn 107, sacrificed 149 wood units by turn 50, and ended 43 wood units behind over 24 games.

The correct interpretation is not “optimize the purchase harder”. It is “on the present forest there is no purchase worth optimizing”. The roster can reopen only if the orchard-only experiment first demonstrates extra convertible wood at the troll’s arrival.

## 2. The two cheapest one-variable experiments

### Experiment A — productive orchard only, no third troll

**Hypothesis.** The champion is supply-limited, not worker-limited. A planting action selected by its expected bankable four-point wood can improve the two-troll champion before any roster change is considered.

**One variable.** Add one new candidate family to the champion: `PLANT_FOR_WOOD`. Everything else remains the champion—same roster, training, chop scoring, assignment, endgame and no third troll.

The candidate’s value must be computed on the same scale as CHOP:

```text
expected points from wood banked by the planned conversion turn
− seed value
− planting, travel, maintenance and return turns at their current alternative value
− expected raid loss
```

Water-adjacent timing, tree species, placement and the conversion turn are inputs to that one candidate family. The current orchard-kinetics read should determine them before code is written. `PLANT` must be in the searched action space rather than a fixed prelude.

**Control.** The unchanged champion. No custom “no-optimizer” control: a control that has its own mechanics defect is not a control.

**Pre-code dead-on-paper gate.** Stop if the exact-referee orchard read cannot show, on a locked holdout set and with the measured raid process, both:

- at least **eight net score points per game** by turn 300 after seed and displaced-work costs; and
- positive net value on at least **60% of maps**.

Eight points are two wood units and clear the ±5-point local mechanism resolution. These are recommended build gates, not claims that the current read has passed them.

**Build gates.** In order:

1. source lineage, exact round trip and 24/24 smoke mechanics; any stall ends the build;
2. candidate identical to the champion when the new plant candidate is disabled or negative;
3. a fresh holdout panel not used to choose the formula or threshold;
4. paired **score margin**, clustered by map; the old win indicator is not read;
5. drop any field cell where the candidate is itself the opponent;
6. real-Legend burst if the local margin is in the neutral band; ladder only if the pre-ladder estimate exceeds the measured 1.7-point resolution.

**Only after this passes:** run a second, separate experiment asking whether a third troll adds value to the proven orchard. Do not bundle those two questions.

### Experiment B — bankable wood before replanting after turn 250

**Hypothesis.** In long games, the champion spends late turns on PICK/PLANT or no command while legal bankable wood is still available.

**One variable.** From turn 251 onward, if any legal bankable chop candidate exists, suppress PICK and PLANT candidates and choose among bank, move-to-bank and bankable CHOP. Do not add opponent ownership, unbankable denial or a new roster.

**Control.** The unchanged champion. The two programs must be byte-identical through turn 250.

**Mechanism gate, written before the field run.** On the same long-game population used by the endgame read:

- mechanics 24/24 and no new stall;
- at least **25% fewer empty late troll-turns**;
- at least **four extra banked score points per long game**, with a paired map-bootstrap lower bound above zero;
- no score difference through turn 250.

Four points are one banked wood unit. If this does not clear that small bar, the estimated six-point opportunity is not recoverable by this rule and the line stops.

Then use the same fresh-holdout and paired-margin pipeline as Experiment A. Do not spend a ladder block if the expected effect remains below 1.7 rating points; keep a positive small rule for combination with a larger candidate.

## 3. Which corpses these resemble

### Productive orchard versus orchard 5–8 and the norxondor port

It resembles the old orchard line because it plants near the shack, and the port because it invests early instead of chopping immediately.

It is not the same experiment for three reasons:

1. the old orchards planted to fund a third-troll fruit bill at one point per fruit; this candidate values the final four-point wood;
2. the old line bundled orchard, funding and roster; this first build has exactly two trolls and isolates supply;
3. the port and Stage 2A committed to economy before charging the displaced wood; this candidate admits each planting action only when its conservative wood value beats the chop it displaces, including raids.

If the orchard-only candidate cannot beat the two-troll champion, the orchard hypothesis is dead without another roster build.

### Endgame bankable wood versus denial and “cut everything”

It resembles the denial line because it changes which trees are cut late, and it resembles the owner’s observation that trees remain standing.

It is not denial:

- every selected tree must produce wood that can be banked by us before the end;
- no value is assigned to depriving the opponent;
- no opponent ownership inference is needed;
- it begins only after turn 250 and cannot sacrifice the opening or midgame.

The experiment asks whether our own legal points are ordered incorrectly, not whether an unbanked enemy loss has value.

### The guarded three-troll claim

Continuing that implementation now would resemble all seven dead roster lines. The new evidence does not merely lower its probability; it removes the current resource base from which the troll was supposed to repay its bill. I recommend closing it without code and preserving the claim as a record of the question. The orchard result is the only evidence that should reopen it.

## 4. Where measurement has been lying to us

### 4.1 Wrong units and unmatched populations

Two large reversals came from elementary comparability errors:

- a frame index was read as a game turn, doubling every roster time;
- medians from different map populations were compared as if paired.

Every result must state the unit in the artifact—game turn, frame, map-seat or game—and every treatment result must be reported as a paired difference on the same maps, draws, opponents and seats. A standalone median is not a treatment effect.

### 4.2 One ladder hour cannot resolve small changes

The identical champion file read 17.04 to 18.72 across four submissions, a spread of 1.68. Therefore one ladder hour cannot decide the turn-2 second troll or another sub-point refinement. A final ladder verdict should use an interleaved block such as candidate/champion/candidate/champion, preferably the project’s full eight-read block, and should be reserved for effects predicted to exceed 1.7.

### 4.3 Raw scores from separate ladder packages are confounded

The dead dispatcher scored more points than the champion while rating 4.13 lower because it fell to a weaker matchmaking field. Never compare own score, opponent score, roster frequency or other package means across two ladder submissions as a causal effect. They are diagnostics within a package, not strength comparisons between packages.

### 4.4 The champion duel measures style, not field strength

Orchard 6 won only 65 of 400 against the champion and nevertheless read ladder-neutral. A duel against our clear-cutter answers “who wins this particular shared-resource race?” It does not answer “who performs against 177 agents?” Keep duels for mechanism probes only.

### 4.5 The field win indicator is biased by draws and self-play

The champion ties 43.5% against itself, 2.8% against orchard 6 and 0.8% against the clone. Scoring every tie as zero deflates whichever treatment is compared to champion self-play. Orchard 6 and the dispatcher then received almost the same confident negative Δwin although their ladder outcomes differed by 4.78 points. That criterion is correctly retired.

A candidate that is one of the field opponents creates another invalid self-play cell. Such a cell must be dropped, not averaged into the result.

### 4.6 Score margin is better, but not yet calibrated enough

Field Δmargin ordered orchard 6, the dispatcher and the port correctly: −18.74, −28.71 and −75.7. This is the best current local selector, but its ladder calibration has only two useful points. The provisional −20 neutral bar is a working rule, not a physical constant.

The opponent bank should be expanded with independently reconstructed external styles, and every bot that later receives a ladder block should be added to a calibration table of holdout Δmargin versus interleaved ladder difference. Until that table grows, report the whole per-opponent vector and do not collapse it into a confident universal rating prediction.

### 4.7 We tune and judge on the same small panels

The 24-map smoke and pinned 200-map panel have been read repeatedly, used to diagnose defects, choose thresholds and then judge successors. A bootstrap interval on that same panel accounts for map sampling conditional on the chosen policy; it does **not** account for the policy having been selected after many looks at those maps.

Split the corpus into:

- a development set, open to diagnostics and tuning;
- a locked holdout map set, read once at the gate;
- a locked external-opponent set, not made from close relatives of our champion.

When a holdout is read, retire it into development and create a new holdout. Otherwise the project is optimizing the panel while believing it is measuring generalization.

### 4.8 Smoke opponents and idle models answer mechanics, not value

The wood-gate report measured the resident pair’s realised rate at 0.090 on the smoke slice against 0.171 in real ladder records. The smoke’s scripted opponents are a different economic environment. The idle opening solver was excellent for exact scheduling, but it could not value a contested finite forest.

Use smoke only for legality, stalls, determinism and rough mechanism presence. Value claims require contested opponents and the measured raid/depletion process. In the orchard search, opponent actions must change the future tree state, not appear only as a final risk penalty.

### 4.9 A broken control invalidates a positive comparison

The parallel optimized-start candidate passed mechanics on 19/24 maps and its control on 15/24. Its positive candidate-minus-control number compared less-broken with more-broken. No value statistic may be read until **both** arms independently pass every validity gate. The safest control is the unchanged champion, and a treatment-off path must reproduce it exactly.

### 4.10 An incomplete action space can make a correct answer useless

The finite-forest forecast that declined all 4,593 third-troll states is credible **for the current fixed forest**. It does not answer whether a troll pays after planting creates new wood, because neither optimizer could issue `PLANT`. This is not statistical noise; it is model misspecification.

Every optimizer report must list its action vocabulary beside its result. “Optimal” means optimal inside that vocabulary. For the owner’s current question, `PLANT`, wait/grow, harvest/maintain, CHOP, bank and TRAIN must be in one state-transition model.

## A replacement measurement contract

For the next build, use this order:

1. **Lineage and mechanics:** regenerate exactly, compile, round trip, 24/24 smoke, no stalls or illegal commands. Stop before reading value if either arm fails.
2. **Mechanism on development maps:** measure the quantity the rule claims to change—net orchard wood or late banked wood—not generic wins.
3. **One locked holdout:** paired maps, draws, opponents and seats; report per-map score-margin differences and a clustered interval. No threshold changes after looking.
4. **Diverse field margin:** no candidate self-cell; no win-indicator verdict; report each opponent separately.
5. **Real-Legend burst:** use it when the local result is not catastrophic but style-sensitive.
6. **Interleaved ladder block:** only for a predicted effect above 1.7, with the unchanged champion bracketing the candidate in the same time window.
7. **Calibration ledger:** append holdout margin, real-field result and ladder difference for every submitted bot, including failures.

## Disposition

- **My unfinished guarded-three-troll claim:** recommend close without implementation. The current fixed-forest third-troll question is answered negatively; reopening condition is a positive orchard-only result.
- **Live project line:** continue `20260904-orchard-kinetics`. Its amendment putting `PLANT` inside the action space is correct.
- **Next build if the read passes:** two-troll productive orchard only.
- **Next build if the read dies:** the turn-251 bankable-wood-before-replant rule.
- **Not worth a separate line now:** early second troll, direct enemy-orchard denial, another generic dithering cure, or another third-troll funding optimizer.
