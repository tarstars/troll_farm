# Task 20260903-three-troll-optimized-start — a three-troll bot with a wood-aware optimized start

- Born: 2026-09-03 16:20Z as chatgpt_1's claim (`20260903T162000Z`), on the owner's direct instruction to it —
  *"implement three troll bot with optimization on start"* — which the owner **confirmed to the coordinator at
  16:5xZ ("yes")** after the coordinator held the claim pending verification. The hold and its conditions are
  `coordination/messages/local_claude_1/20260903T164125Z`; the charter is the ack that follows this card.
- Work owner: **chatgpt_2** (builds) — **corrected 2026-09-04 13:4xZ; this header said `chatgpt_1` until now and
  that was wrong.** The identity was settled at 2026-09-03 17:58Z on the owner's three-part test (§ the 17:58Z log
  entry): the agent that built this candidate is `chatgpt_2`, and the original `chatgpt_1` is the one that returned
  the opening-solver ACCEPT-WITH-EDITS. The body of this card was corrected that evening; **the header was not**, so
  for a day the board showed two open tasks against `chatgpt_1` when it only ever had one. Every "chatgpt_1" below the
  16:20Z–17:58Z line means `chatgpt_2`. Verifier: **the coordinator** (reproduces everything by execution from the
  pinned commit; nothing enters the record otherwise).
- Budget (chatgpt_1's own, accepted): one implementation, one validity/smoke/timing run, one paired local panel, one
  review and handoff. Two days, to **2026-09-05 17:00Z**; no evidence for two days = STALLED and the owner says kill
  or extend.

## Why this is not the seventh repetition of a dead idea

Six lines have now died attacking the roster (`GRAVEYARD.md`): the port of norxondor_gorgonax, six third-troll and
orchard builds, the cheap third troll, and stage 2A's opening dispatcher. **The coordinator's position, stated plainly
so it can be held against the result: on the evidence, an earlier third troll is not our lever.** Stage 2A settled the
timing question — with the frame-index correction of 16:2xZ its third troll arrived in 98 % of games at **median game
turn 74.5**, about **23 turns ahead of the field's own 98**, and it still read **4.13 rating points below the
champion**. The roster is reachable early. It does not pay.

**What makes this build different, and worth the budget anyway:** every previous attempt bought the roster and let the
funding trips *suppress* the wood trips. This one **charges the foregone wood against the funding trip directly** — a
third-troll plan is admitted only if the contested estimate finishes by turn 110 **and** clears at least eight points
of estimated net continuation value *after* the wood it displaces is subtracted, and the plan is abandoned back to the
champion when that gate stops holding. That attacks the mechanism the record says killed both the port (banks 1-point
fruit while the champion banks 4-point wood, joins the wood race a hundred turns late) and stage 2A, rather than the
symptom. It is the first proposal to do so.

## The build (chatgpt_1's, as claimed)

- Base: the champion of record, in an isolated candidate. The **turn-2 second troll** — the one half of stage 2A that
  survived the real field — stays. (Note its size honestly: game turn 2 against the champion's 9 is **seven turns**,
  not the fourteen first reported, and seven turns of one troll may be below what a ladder hour resolves.)
- Once two trolls stand, a small contested-resource dynamic program searches complete third-troll tuples and
  worker/resource assignments, under the wood-charging gate above; the plan is rechecked from the live board each turn
  and abandoned to the champion's own play when the gate fails.
- After the third troll arrives, the selector searches all three trolls jointly. **This matters:** claude_1's read
  showed stage 2A's real cost was the champion's *two-troll* assignment loop running a three-troll roster — 13.7 % of
  troll-turns wasted against the two controls' 6.2 % and 6.6 %, three-quarters of it after the handover.
- **A second arm, mandatory:** the same turn-2 second-troll opening with the third-troll optimizer disabled. It is the
  control that separates the optimizer's value from the already-known second-troll change.

## Gates and the pre-registered dead conditions

Done means: the generator, the readable source and diff, the compacted candidate **and control**, exact compile and
round-trip checks, the frozen 34-case differential bed, the 24-map smoke, one-core turn timing, and a paired local
comparison of candidate against its control on identical maps and opponents; the report names third-troll frequency
and turns, fallbacks, runtime, source size and the paired result.

**Dead (chatgpt_1's own, binding):** any compile, round-trip or mechanics failure; p99 warm turn time at or above
40 ms; the candidate never trains a third troll by turn 110 on the smoke; or the paired candidate-minus-control result
below −0.05 with its 95 % interval clear of −0.05. **A dead build stays an instrument and is not offered for the
ladder.**

**The coordinator's added conditions (from the 16:41Z hold, binding):**

1. **The control arm is not optional** — a candidate reported without it is not a result.
2. **The selector is the paired 200-map panel** (`77556dc9…`, both seats) **plus the field reading against the same
   four opponents** the port and stage 2A were judged on, not a duel against the champion alone.
3. **No ladder, no platform, no champion edit, no `main` write.** A ladder hour needs the owner's prediction asked in
   chat and that is the coordinator's to do.
4. **The coordinator reproduces everything** from the pinned commit before it enters the record.
5. **Third-troll arrival is reported in game turns**, converted from the referee's frame index, with the convention
   named — this is the exact error that cost the record four hours on 09-03.
6. **chatgpt_1's own CI workflow is not independent evidence.** On 2026-08-06 an acceptance from this identity was
   declared void with the owner because a self-authored, self-triggering workflow was presented as an independent run.
   The workflow is a build tool; verification is the coordinator's rerun.

## Log

- 2026-09-03 16:20Z chatgpt_1: the claim, asserting a direct owner instruction. — chatgpt_1
- 2026-09-03 16:41Z coordinator: **HOLD, not refusal.** The authorization could not be verified from the coordinator's
  own record, so it was put to the owner; meanwhile chatgpt_1's write set was checked by execution and found compliant
  (its own directory, its own messages, its status file, one branch-only workflow; nothing to the champion, board,
  `main`, ladder or platform), so it was allowed to keep building at its own risk. Its premise — the withdrawn "turn
  147" — was corrected to it, with the note that the correction *strengthens* its design and removes its stated
  reason. — coordinator
- 2026-09-03 16:5xZ **owner: "yes"** — the instruction is confirmed and the claim becomes a charter under the
  conditions above. — coordinator
- 2026-09-03 17:0xZ coordinator: **chatgpt_1 FORCE-PUSHED its branch and the chartered claim no longer exists.** At the
  16:5xZ wake `origin/agent/chatgpt_1` was rewritten: the claim this card was built on
  (`20260903T162000Z-20260903-three-troll-optimized-start-claim.md`) is **gone from its branch, gone from `main`, and
  gone from the coordinator's history** — it exists on no authoritative ref anywhere. Its four build commits
  (`846ccb16`, `197c9b53`, `ee10ec9b`, `8da821a2`) are unreachable and `chatgpt_1/three-troll-optimized-start/` is
  empty. This is the tenth occurrence of the class the transport rules already name — *when a rewrite is pending,
  rewrite first and publish the pinned message after* — and its cost here is that **the coordinator's charter
  (`20260903T164655Z`) now has an `ack_for` pointing at a message on no ref: a permanent delivery error on an immutable
  message**, the same defect that has quarantined nine peer messages before it.

  In its place is a new claim, `20260903T161500Z-20260903-guarded-three-troll-claim.md`, task id
  `20260903-guarded-three-troll`, write set `chatgpt_1/guarded-three-troll/**`. It is **backdated**: stamped
  16:15:00Z and published at about 16:58Z, which places it in the record *before* the claim it replaces. The transport
  rule is that the stamp comes from `date -u` at the time of writing.

  **What the rewrite removed, and this is the part that matters.** The replaced claim carried its own falsifiable dead
  conditions and a mandatory control arm, both of which the coordinator accepted and made binding. The new claim
  carries neither. Recorded here verbatim so they cannot be lost with the message:

  > *"A second generated arm contains the same turn-2 second-troll opening but disables the third-troll optimizer. It
  > is the control needed to separate the value of the optimizer from the already-known early-second-troll change."*
  >
  > *"Dead means: any compile/round-trip/mechanics failure; p99 warm turn time at or above 40 ms; the candidate never
  > trains a third troll by turn 110 on the smoke; or the paired candidate-minus-control result is below -0.05 with its
  > 95 % interval clear of -0.05."*

  The new claim replaces these with "the guarded optimizer still spends the opening on a third troll in clearly
  uneconomic cases in the smoke diagnostics" — which names no number and cannot be failed by measurement.

  **Ruling.** The owner's authorization is for the *work*, not for a particular message, so **the build stays
  chartered and is not interrupted.** But the charter's authority was always this card, stated in the charter itself
  ("the card is now the authority, not the claim"), and the card's conditions are unchanged: **the no-optimizer control
  arm is mandatory, and the four numeric dead conditions above are binding as written** — they are chatgpt_1's own
  words and it does not get to loosen them by republishing. The task keeps this card; the directory may be
  `chatgpt_1/guarded-three-troll/` if chatgpt_1 prefers, since the path is immaterial. A correction superseding the
  charter, acking the surviving claim, goes out with this entry. **Standing instruction added: no force-push of a
  branch that carries published messages; a message that needs changing is superseded by a new one, never rewritten
  away.** — coordinator
- 2026-09-03 17:1xZ **CORRECTION BY THE COORDINATOR, ON THE OWNER'S INFORMATION — the 17:0xZ entry above blamed one
  agent for what two agents did, and the accusation is WITHDRAWN.** The owner: *"It seems that there are two agents
  work as chatgpt_1. I ask them to check their histories and one will be chatgpt_2."* That explains every symptom the
  previous entry recorded as misconduct, and explains them better:

  - **Two claims minutes apart** with different task ids, directories and gates — `20260903T161500Z`
    (guarded-three-troll) and `20260903T162000Z` (three-troll-optimized-start) — are two agents each writing its own
    claim, not one agent replacing its own.
  - **The "backdating"** was not backdating. Each agent stamped its own message honestly when it wrote it; they simply
    published in the other order.
  - **The "force-push that destroyed its own commitment"** was two agents pushing one branch, the second overwriting
    the first. **Nobody rewrote away a promise they had made.**
  - **The dropped control arm and dropped numeric gates** were never dropped by anyone. The second agent's claim simply
    never had them; the first agent's did — **and the first agent actually built the control arm.**

  **What the previous entry got right and keeps:** the record was genuinely damaged (a chartered claim on no ref, a
  broken `ack_for`, 47 files unreachable), and the card's gates stand. **What it got wrong and retracts:** the
  attribution of intent, and the implication that an agent loosened its own gates by republishing. That reading was
  available to me only because I assumed one actor behind one identity, and I did not check the assumption before
  writing a pointed message. Recorded as my error.

- 2026-09-03 17:1xZ **THE OVERWRITTEN WORK IS RESCUED AND COMPLETE.** The commits were still in the coordinator's own
  object store from an earlier fetch, so before anything pruned them they were pushed to the remote as
  **`refs/heads/rescue/chatgpt1-three-troll-optimized-start-2026-09-03`** (tip `8da821a28db9658062bfb772e2e63b6f47f4868d`),
  carrying all 47 files of `chatgpt_1/three-troll-optimized-start/` and the destroyed claim's own text. Nothing is lost.
  **It contains a finished, self-reported result, and the agent reported it against itself:**

  - **`verdict.txt`: `DEAD_AS_BOT`.**
  - **The candidate beats its own control**: paired win difference **+0.0500 [+0.0050, +0.0950]**, margin **+2.39
    [+0.66, +4.18]** — positive with the interval clear of zero, so the pre-registered death condition (below −0.05
    with the interval clear) is **not** met. The control shares the turn-2 second-troll opening and differs only in the
    wood-aware optimizer, so this measures the optimizer itself — which is exactly what the mandatory control arm was
    for, and it was built.
  - **And the whole bot is still far below the champion**: the direct duel reads 51 wins in 200 games, win rate 0.255
    [0.20, 0.31], margin −0.97 [−1.81, −0.24]. Hence its own honest verdict.
  - Validity is *not* clean and this is what the coordinator must check first: **smoke mechanics 19/24 for the
    candidate and 15/24 for the control**, where the standing bar is 24/24, and the card's first dead condition is
    "any compile, round-trip or **mechanics** failure". Third troll in only 14 of 24 smoke games, median turn 30, and
    the tuples chosen are the weakest available (`1 1 0 1` ten times, `1 2 0 1` four). Source size 90,070 UTF-16 units
    against the champion's 63,808.

  **Nothing above is a fact yet** — it is the agent's own report, rescued, and it enters the record only when the
  coordinator reproduces it by execution from the rescue ref. But two things are already clear: the mechanics failures
  most likely trip the card's own dead condition, and the positive candidate-minus-control signal is worth verifying
  regardless, because it is a measurement of the one idea nobody has tested — charging the foregone wood. — coordinator
- 2026-09-03 17:4xZ **REPRODUCED BY EXECUTION, AND RULED DEAD.** From the rescue pin
  `8da821a28db9658062bfb772e2e63b6f47f4868d`, archived into `/data/scratch/3t-verify` on the VM, nothing edited
  (`/home/tarstars/verify_3t.log`):

  **The build is sound as a build.** Re-running `make_candidate.py` regenerates **all four artefacts byte for byte**
  (candidate `d994b3fb…`, control `2d62e0c7…`, candidate arm `af49570f…`, control arm `83fa8584…`); the base arm's token
  stream is identical to the resident champion's; the compaction round trip is EXACT; both arms compile with `rustc -O`
  at zero errors; the source is 90,070 and 90,071 UTF-16 units against the platform's 100,000. The diff is +1,334/−23.

  **The play is not.** The 24-map smoke, run on both arms:

  | | candidate | control |
  |---|---|---|
  | mechanics OK | **19 / 24** | **15 / 24** |
  | maps stalled | 5 | **9** |
  | a third troll | 14 / 24, median turn 30 | 0 / 24 |
  | own score vs the resident | **−416** over 24 games | −242 |

  **This fires the card's first dead condition — "any compile, round-trip or mechanics failure" — on both arms.**
  The author's own report gave the same figures and its own verdict `DEAD_AS_BOT`; the reproduction agrees with it in
  every number, so the failure is in the build and not in the reporting, and the author reported honestly against
  itself. **Ruled DEAD.** Obituary in `GRAVEYARD.md`.

- 2026-09-03 17:4xZ **A CORRECTION THE COORDINATOR MAKES AGAINST ITS OWN EARLIER READING, and it matters more than the
  verdict.** At 17:1xZ the board and this card recorded that the candidate's **+0.0500 [+0.0050, +0.0950]** win
  difference over its control was "a measurement of the one idea nobody has tested — charging the foregone wood — and
  it read positive". **That reading is withdrawn.** The comparison is between two arms that *both* fail the mechanics
  bar, and the control stalls on **nine maps of twenty-four**. It therefore measures less-broken against more-broken on
  a damaged base; it does not measure the wood-charging gate against the champion. **Charging the foregone 4-point wood
  against a funding trip remains untested**, and it is still the most interesting untried idea on this project.

  What the gate demonstrably *did* do is change behaviour in the opposite direction from the one intended: the third
  troll arrived at **median turn 30**, earlier than any build before it, and always as the **weakest tuple available**
  (`1 1 0 1` ten times of fourteen, `1 2 0 1` four) — so charging the wood did not prevent a bad trade, it bought a
  cheaper and earlier troll instead, and the bot still lost 416 points a game to the resident.

  **The design lesson, for whoever tries this next: a control arm that does not itself clear the mechanics bar is not a
  control.** This one silently invalidated the only comparison the build existed to make. The cheapest honest test of
  wood-charging uses **the champion itself as the control** — the champion unchanged plus only the wood-charging
  admission test, with no turn-2 second troll and no joint selector confounding it — because then the control passes
  24/24 by construction and the difference means what it claims. **Not chartered; it is the owner's call.** — coordinator
- 2026-09-03 17:58Z **THE IDENTITY IS SETTLED, AND THE COORDINATOR OWES chatgpt_2 A CORRECTION.** The agent that built
  this candidate published an identity correction on its own branch and named itself **`chatgpt_2`**, applying the
  owner's three-part test: the original `chatgpt_1` is the agent that returned the opening-solver ACCEPT-WITH-EDITS
  review at 10:12Z, delivered the DP oracle at 10:58–11:15Z, and delivered the Rust anytime planner at 11:38–12:01Z.
  This session did not do that sequence, so **this whole three-troll build is chatgpt_2's work**, and the record above
  is corrected to say so. It has moved to `agent/chatgpt_2`, writes only under its own namespace, and does not touch
  `chatgpt_1`'s.

  **Three things the coordinator gets wrong and states plainly.** (1) Its provisional guess at 17:2xZ was **backwards**
  — it reasoned from behaviour (this agent acknowledged the dossier handoff and updated the shared status file) that
  this was the original `chatgpt_1`. It was not. The guess was labelled as a guess and no action was taken on it, which
  is the only reason it cost nothing. (2) **Condition 6 of this card, and the 16:41Z hold that preceded it, warned this
  agent that its CI workflow was not evidence "because on 2026-08-06 an acceptance from this identity was declared void
  with the owner". That incident belongs to the original `chatgpt_1`, not to chatgpt_2. The warning was aimed at the
  wrong agent and is withdrawn as to chatgpt_2.** The condition itself stands for everyone on general grounds — a
  self-authored, self-triggering workflow is not an independent run, whoever writes it — but the imputation of a past
  fabrication does not attach to this agent and should not have been put to it. (3) The 17:0xZ accusation of a
  force-push, already withdrawn, was likewise aimed at this agent for something two agents did.

  **What chatgpt_2 actually did, on the record and to its credit:** it built both arms including a control arm nobody
  had to force it to build, pre-registered four falsifiable numeric dead conditions, ran the gates, and **reported
  `DEAD_AS_BOT` against its own build with figures that the coordinator's independent reproduction then matched in
  every number.** That is the standard the project asks for. — coordinator
- 2026-09-04 07:2xZ **THE LADDER READING, at the owner's word ("submit this new bot"): 14.07 at rank 154 of 177**
  (submission `41239996`, 160 games, up 06:15:06Z, read 07:22:11Z; the champion of record restored automatically
  eleven seconds later and holds at **18.72 / rank 72**). Early looks 12.92 / 12.73 / 13.00 / 14.11 / 14.23 / 13.40 /
  13.93, flattening near 14. The coordinator's prediction, logged in `queue.json` **before** the submission, was
  **12–15**: the reading landed inside it. The card remains **DEAD on mechanics** — a submission at the owner's word
  does not reopen it.

- 2026-09-04 07:3xZ **THE DECODE OF ITS 160 GAMES — the owner's diagnosis confirmed as exactly as evidence allows.**
  Decoded with `ladder_read_trolls.py` (game turns, converted from the referee's two-frames-per-turn index), beside the
  champion's own control package `games-41236823`:

  | | the three-troll bot (41239996) | the champion (41236823) |
  |---|---|---|
  | rating / rank | **14.07 / 154** | **18.72 / 72** |
  | second troll | 160/160, median game turn **2** | 160/160, turn 9 |
  | third troll | **75/160 = 47 %, median game turn 25** (q 17 / 25 / 37) | 0/160 |
  | the opponents' third troll | 72 %, median turn **96.5** | 59 %, turn 107 |
  | own score | median **165.5**, mean 166.4 | median **184.5**, mean 188.3 |
  | wins in its own package | 81/160 = 0.506 | 91/160 = 0.569 |

  **The roster arrives and the wood does not.** This bot reaches three trolls at median game turn **25** — about **71
  turns before the field it is playing** buys its own third troll, and the earliest of any build this project has made
  (stage 2A: 74.5; the wood-charging gate: 108). **And it scores 19 points a game less than the champion.** Getting the
  roster is not the hard part and never was; it has now been done four different ways and lost every time.

  **The matchmaking confound runs *against* this bot, not for it, which makes the comparison stronger.** At rank 154 it
  met a weaker field — its opponents scored a mean of 172.3 where the champion's scored 210.1 — and it still scored
  fewer points than the champion did against harder opposition. So the 19-point gap **understates** the difference.

  **Why, in one line, and it is the owner's line:** its optimizer has no `PLANT` in its action space (verified in
  source — 17 reads of `view.plants` as harvest sources, no plant command ever issued), so it buys trolls it cannot
  feed. A third troll at turn 25 on a board nobody has planted is three trolls sharing one shrinking forest. — coordinator

## CLOSED 2026-09-04 13:4xZ — the bot is dead on the ladder, the judgement is delivered and acked, nothing is open

Written because the card had no closure section even though every part of it had finished. The work is **chatgpt_2's**
throughout (see the corrected header).

**What closed it:** the bot was submitted at the owner's word and read **14.07 at rank 154** (submission `41239996`)
against the champion's 18.72 at rank 72 in the same field. It reached three trolls in 47 % of games at **median game
turn 25** — about **71 turns before the field** buys its own third, the earliest of any build this project has made —
and scored **19 points a game less** than the champion. The matchmaking confound runs *against* it (its opponents
averaged 172.3 to the champion's opponents' 210.1), so the gap is understated. **Getting the roster early is not the
hard part and never was.** This is the fourth independent closure of the roster question.

**The judgement round that followed is delivered, verified and acknowledged**
(`chatgpt_2/three-troll-optimized-start/JUDGEMENT-2026-09-04.md`, handoff `20260904T120606Z`, acked
`20260904T133300Z`). Two of its findings outlived the bot and are now project-wide:

1. **The stalls were inherited from the shared stage-2A prelude, not created by the optimizer** — all five of the
   candidate's flagged maps are a strict subset of the control's nine (5 of 5, checked by the coordinator), and on
   those maps both arms record the same second troll, no third troll and the same final score. chatgpt_1 confirmed the
   same shape in its own build. This is the architectural disease that killed three builds in a row.
2. **The harness's `stalled` field is a longest no-command streak — not a crash, not a referee end condition and not a
   loss label.** The coordinator's repeated "a stalled bot loses those games outright" is withdrawn. It remains a
   valid fail-closed mechanics gate.
3. **"Activity is not value"** — its optimizer removed four of the control's nine inactivity flags and those four maps
   totalled **+1 point**.

**Where its live work went:** its ranked item 2 — search `PLANT` and `TRAIN` jointly over an explicit finite forest and
optimize paired final margin — is the experiment the owner authorised with **"run it"** and is chartered as
`20260904-champion-prefix-orchard` (row 3-8), in the conservative form that also satisfies its item 1 (the champion is
the byte-identical incumbent, no prelude at all) and its item 3 (the third troll is not defaulted off but disabled).

**Nothing here is open.** No build, no panel, no ladder slot, no budget left. Obituary in `GRAVEYARD.md`.

- 2026-09-04 13:4xZ closed; header attribution corrected from chatgpt_1 to chatgpt_2. — coordinator
