# Handover — 2026-09-04 13:2xZ — the coordinator's session, from the four-day runbook to the orchard turn

Written at the owner's word ("prepare for context flush"). **Read this whole page, then `coordination/BOARD.md`.**
It supersedes nothing; it continues `HANDOVER-2026-09-03-four-days-runbook.md`, which is still the operating manual
for how the loop runs (wakes, the board, the ladder queue, the owner conversation). Everything below is what changed
in the twenty-five hours after it.

---

## 0. THE ONE THING NOT YET DONE — do this first

**At about 13:2xZ the owner said "run it", authorising the next experiment, and it has NOT been chartered.** No card,
no handoff. That is the first action of the next session.

**What was authorised, in the owner's own framing:** *one offline simulation experiment, no ladder.* Take the champion
of record **unchanged** and let it run to the moment it trains its own second troll (about game turn 9). From there,
try one different thing — **plant a small orchard near the tent, tend it, fell it for wood** — and **never train a
third troll**. Replay both that candidate and the continuously advanced champion to turn 300 against the same
opponents on the same maps, and compare final score margins.

**Why it is shaped that way** (this is load-bearing, see §3): three consecutive builds died of the same disease — each
changed the *roster* early and handed the altered situation to the champion's own continuation, which was never
validated for it. Keeping the prefix byte-identical to the champion through its own second `TRAIN` is what makes this
experiment immune to that.

**Who:** chatgpt_1 designed it and owns the search machinery (its DP oracle and anytime planner). **The coordinator
told the owner it would fold claude_1's overlapping orchard-kinetics read into this rather than run both.** The
intended shape: chatgpt_1 owns the experiment end to end; claude_1's read is closed as superseded with its delivered
geometry kept as an input; and **claude_1 is reassigned to independently reproduce the experiment when it lands** —
two independent implementations of one measurement, which is exactly what made the stage-2A field reading trustworthy
(both agents agreed to the digit).

**chatgpt_1's own falsification list, to become the card's dead conditions:** paired final-margin lower 95 % bound not
above zero; own-score lower bound negative; the no-plant champion normally selected; the effect reversing under high
raid; wood calibration failing; or the champion's second-troll talent or turn changing. Its prior: **+2.5 rating,
range 0 to +4, explicitly uncalibrated**, and it warns that a result below roughly **+15 paired margin** is too small
to deserve a ladder slot.

---

## 1. The state in one page

**The ladder.** The champion of record (`readable/denial-off-champion.rs`, arm
`cgauto/submissions/candidate-champion-denial-off-v6-instrument.rs`, sha `0e92f8fa…`) holds it at **19.23, rank 60 of
177** (submission `41240269`, read 2026-09-04 08:27Z). **That is the highest reading this project has ever recorded —
and it came from resubmitting the identical file.** The queue is empty. Nothing may be submitted without the owner's
prediction asked in chat.

**The agents.**

| agent | state |
|---|---|
| `claude_1` | **Back online.** Was silent 05:52–12:04Z: it had no `--model` flag in the launcher and hit the *Fable* model's cap while the account had capacity. Fixed (§6). |
| `chatgpt_1` | Idle. Its start-game optimizer build is **closed**; its design is **accepted and preserved**. |
| `chatgpt_2` | Idle. Its bot is dead but delivered and verified; its judgement round was the best diagnostic work of the session. |
| `codex_1` | Out of credits until 2026-09-07 — a genuine account limit, unrelated to claude_1's. |

**Two agents shared the name `chatgpt_1` on 09-03** and the identity was settled at 17:58Z on the owner's timeline
test. The original kept the name; the other became `chatgpt_2` on its own branch and namespace. Do not re-derive this.

---

## 2. What died, and what each death actually taught

Six lines closed in this session. **The roster question is now closed four independent ways and must not be
re-litigated.**

1. **Stage 2A, the opening dispatcher** — ladder **14.59 / rank 147** against the champion's 18.72. Its plan *worked*:
   third troll at game turn **74.5** against a bench-promised 70.5, about **23 turns ahead of the field**. It lost
   anyway.
2. **chatgpt_2's three-troll optimized start** — submitted at the owner's word, read **14.07 / rank 154**. Reached
   three trolls at **game turn 25**, ~71 turns before the field, and scored **19 points a game less** than the
   champion. The matchmaking confound ran *against* it (its opponents averaged 172.3 to the champion's opponents'
   210.1), so the gap is understated.
3. **claude_1's wood-charging gate** — the owner's own rule, faithfully built: forecast with-troll against
   without-troll, buy only if with wins. **The honest forecast declined all 4,593 evaluated turns.** Pricing the bill's
   fruit at the champion's realised seed value flips only **7.8 %** of admissions. And a loosened-forest variant that
   declines **4,024 of 4,219** turns **still loses all three games it admits**, with a nearly calibrated forecast
   (with 20–53 against without 17–41). **The trade is bad at the very margin where it looks closest.**
4. **chatgpt_1's start-game optimizer build** — failed its own mechanics gate at **19/24**, reproduced to the digit.

**The single mechanism behind all of them:** a troll bought around turn 100 arrives at a board four trolls have been
felling for a hundred turns and cannot repay the wood its shopping cost. Getting the roster early is *not hard* — it
has been done at turns 25, 74.5, 108 and 144 — and it does not pay.

---

## 3. THE ARCHITECTURAL DISEASE — the most important engineering finding

**chatgpt_2 found it, the coordinator verified it, chatgpt_1 confirmed it independently.**

All five of chatgpt_2's candidate's stalled maps are **a strict subset** of its control's nine (checked: 5 of 5), and
on those maps both arms record the same second troll, no third troll and the same final score. **The stalls are not
caused by the optimizer — they are inherited from the shared stage-2A prelude**, which irreversibly buys a
harvest-capable chop-1 second troll and hands that altered roster to a champion continuation **never validated for it
and carrying no progress invariant**. chatgpt_1's own build shows the same shape (a turn-35 second-troll fallback on
14 of 24 maps, five stalls).

**Rule for every future build: an irreversible roster change must not be handed to a continuation validated for a
different roster.** The fix belongs in the optimizer *before* it commits to `TRAIN` or `PLANT`; a progress deadline on
macros is a secondary safety belt and cannot undo a bad commitment.

**A correction the coordinator owes:** the harness's `stalled` field is a **longest no-command streak**, not a crash,
not a referee end condition, and **not a loss label** — both arms answer all 300 turns with clean telemetry, and two of
chatgpt_2's five flagged maps *outscore* the resident. The coordinator repeatedly said a stalled bot "loses those games
outright"; that is withdrawn. It remains a valid fail-closed mechanics gate.

---

## 4. THE INSTRUMENT AUDIT — seven findings, and finding 7 changes the protocol

Card `coordination/tasks/20260904-instrument-audit.md`. Run on the owner's word after four coordinator numbers needed
correcting in one day.

1. **Ladder variability.** The champion's identical file read 18.19 / 17.04 / 18.14 / 18.72 / 19.23 — mean 18.26,
   spread **2.19**, sd **0.815**.
2. **Draws break the win indicator.** The champion ties **43.5 %** of games against *itself* but 2.8 % against orchard
   6 and 0.8 % against the clone, so every baseline built on champion self-play is deflated by draws a different bot
   never reproduces.
3. **A candidate that is itself one of the four panel opponents gets a structurally invalid self-play cell** — it must
   be dropped and the field averaged over the remaining three.
4. **The selector returned a confident false negative.** orchard 6's field reading is Δwin **−0.1969**, interval clear
   of zero — our kill verdict — yet it read **18.84** against the champion's 18.19. Beside it stage 2A read −0.2219 and
   went 4.13 *below*. **Two Δwin figures 0.025 apart; ladder outcomes 4.78 apart.**
5. **Margin works where the win rate does not**: orchard 6 −18.74 (ladder-neutral), stage 2A −28.71 (−4.13), the port
   −75.7 (0 wins of 15 against real Legend agents) — non-overlapping intervals, correct order.
6. **Our test sets are no longer tests** (chatgpt_1): the 24-map smoke and the pinned 200-map panel are **development
   data** — every build since August was shaped against them — so any result justifying a ladder hour needs a **fresh
   sealed holdout**.
7. **THE LADDER IS NOT A 2.2-POINT WALL — it is what ONE reading buys.** Verified: paired half-width =
   1.96 · sd · √(2/n) with sd 0.815, so **n = 1 gives ±2.26** (matching the observed 2.19), **n = 6 gives ±1.00**,
   **n = 21 gives ±0.50**. We have never paid for resolution.

**The protocol now in force:** screen offline with paired replay and a sealed fresh holdout; **a single ladder hour
settles nothing below ~2.2 and must not be quoted for a smaller effect**; for a candidate plausibly above that, spend
an **interleaved multi-read block** (alternate candidate and champion so field drift falls on both arms) and report the
paired difference with its interval and n. Drift is not modelled, so the arithmetic is the optimistic case.

**Standing selector rules:** Δwin is **retired as a kill criterion** everywhere; **Δmargin with its 95 % interval is
the selector**, provisionally dead below about **−20** — and the relation is **flat then falling**, not linear (the
champion's own point is (0,0); orchard 6 (−18.74, ≈0); stage 2A (−28.71, −4.13)), so the coordinator's earlier "0.5
rating per margin unit" slope is **withdrawn**. Every optimizer must **publish its action vocabulary**. Both arms must
pass mechanics **independently** before any value number is read.

---

## 5. VERIFIED MECHANICS AND GEOMETRY — checked in `sim/engine.py` and on 400 map-seats

- **A mature size-4 tree is 16 points, not 4** (`WOOD_POINTS` 4; felling yields `plant.size`). Thirty trees are **480
  points of gross standing potential** against a champion score of about 184 a game.
- **Health at maturity, all yielding the same 4 wood: banana 6, plum 12, lemon 12, apple 20**
  (`TREE_HEALTH_BASE` 2/4/4/8, `TREE_HEALTH_SLOPE` 1/2/2/3). So a chop-1 troll fells a **banana in 6 turns against an
  apple's 20 — 3.3× the wood per chop-turn** — and the referee prices bananas at **zero** for training. **Plant
  bananas for wood; keep plums, lemons and apples for the training bill.** No bot of ours has ever done this.
- **First fruit**: plum and lemon ~12 turns beside water against 32 inland; apple 8 against 36; banana 16 against 24.
  A full tree regrows one fruit the instant it is harvested.
- **Planting geometry** (claude_1, 400 map-seats, preserved at `claude_1/orchard-kinetics/results/curve.json`): free
  cells **11.5 within two steps** of the shack (q1 9, q3 14, min 3), **27 within four**, of which only **2** and **5**
  are water-adjacent (13 within eight). Starting fruit draw median **24**. **So the fast orchard is small and the big
  orchard is slow** — that tension, not the tree count, is the subject.
- **Raids**: 0.19 per 100 tree-turns before turn 100, **0.6–1.0 after**. The opponent plants ~25.8 trees a game and
  takes 23.5 fruit from them; our champion plants 9.8 and fells 81 % of its banked plums and lemons; the top four plant
  ~29 and their own trees overtake wild ones by turn 40–70.
- The referee's chop loop is commented **"last wood can duplicate"** — a multi-chopper schedule must respect it.
- **Never model the opponent as idle.** That assumption is what made stage 2A promise turn 70 and deliver 74.5 into a
  stripped forest.

---

## 6. OPERATIONAL TRAPS LEARNED THIS SESSION — each cost real time

- **An agent that wakes and produces nothing may be on a model with no capacity.** `claude_1` had **no `--model` flag**
  in `/home/tarstars/launcher-config.json` and hit the *Fable* cap while the account was fine (the coordinator was on
  Opus throughout). **Read the session log before concluding anything about credits.**
- **The launcher reads its config once at startup** (line ~155, before the loop). Editing the config does nothing
  until `sudo -n systemctl restart agent-launcher.service`. It had been running 2 days 5 hours.
- **The launcher only rings an agent when its queue *changes*.** Wakes consumed by a failing model are not retried;
  a *new* ack-required message is required to ring it again.
- **Quarantine entries are FAIL-CLOSED.** An entry's `adjudicated_by` must **exist on its author's canonical branch
  AND name the quarantined path in its own `quarantines:` array**. One bad entry drops **every** quarantine — the
  coordinator briefly took 31 to 0 and errors to 36, reverted inside a minute, reproduced the fault deliberately, then
  applied it cleanly. `coordination/quarantine.json` is the registry; a policy message alone does not register.
- **Quote heredoc delimiters** (`<<'EOF'`) when a message body contains backticks, or the shell executes them — a
  filename was eaten from a published message and needed a correction.
- **The WIP limit** refuses a second ack-requiring handoff on the same task; name the earlier one in `supersedes`.
- **A cross-task `ack_for` or `supersedes` needs an explicit `cross-task:` marker** in the body naming why.
- **The sweep can exceed 120 s**; run `--fetch` and `--mark` as separate commands.
- **Two agents must never share a branch.** The 09-03 collision destroyed 47 files and a claim; they survived only
  because the coordinator's rescue push saved them from pruning — and that rescue then *surfaced* a delivery error that
  had been invisible, which had to be quarantined.

---

## 7. What needs the owner

1. **Nothing is blocked** except the charter in §0, which the owner has already authorised — write it.
2. **codex_1** returns 2026-09-07; nothing depends on it.
3. **The ladder** needs the owner's prediction before any submission, and on current rulings **no candidate should be
   submitted unless its plausible effect exceeds ~2.2 rating** — or unless the owner wants a reading regardless, as
   with the three-troll bot, which is legitimate and was recorded as such.

## 8. The coordinator's own errors this session, all corrected in place

Recorded because the record should be even-handed: a paired median compared across two populations (17–18 turns → 14);
a referee **frame index read as a game turn**, which doubled every roster time and made the coordinator tell the owner
a true bench result was an artefact; a **+0.05 read off two broken arms**; **misattributions to both chatgpt agents**
from assuming one actor behind one name; **"out of credits"** when it was a per-model cap; **"a stalled bot loses those
games outright"** when the flag is a no-command streak; and a **margin-to-ladder slope** fitted without the origin.
Every one was caught by re-derivation or by an agent, never by argument. That is the process working, and it is the
reason to keep verifying by execution rather than by reasoning.
