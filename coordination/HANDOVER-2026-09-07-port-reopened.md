# Handover — 2026-09-07 06:3xZ — the port question reopened, the orchard closed twice, the platform frozen

Written at the owner's word ("prepare for context flush"). **Read this whole page, then `coordination/BOARD.md`.**
It continues `HANDOVER-2026-09-04-orchard-turn.md`; everything below is what changed in the three days after it.
`HANDOVER-2026-09-03-four-days-runbook.md` is still the operating manual for how the loop runs.

---

## 0. THE ONE THING WAITING — a yes/no on the owner's queue

**The owner has one decision in front of them and nothing else is blocked:**

> **Do we build the native orchard-turnover controller?**

chatgpt_2 specifies **one** thing: the tree-turnover engine — planting, replacement, own-orchard thinning, and
native crop/**chop** target selection — **recovered together**, not grafted onto our champion, with the training
timing emerging from that economy rather than forced independently.

**Its pre-registered closed-loop checkpoints become the gates** (these are the real bot's own numbers): third `TRAIN`
near turn 100, first Deforest near 153, **~49 wood points and 15 cumulative plants by turn 150**, **~155 and 22 by
turn 200**, and harvesting continuing through turns 151–200. **Teacher-forced action agreement is explicitly NOT a
gate** — our own history is 77 % decision agreement losing by 173 points closed-loop.

**Its dead condition is as valuable as its success: if those checkpoints cannot be reproduced, Track R stays
descriptive and top-bot copying closes as an implementation strategy for good.**

It cannot be settled by a ladder reading (§3), so it would be judged offline against those checkpoints. **Do not
charter it without the owner's word** — it is a build and it is the project's main bet.

---

## 1. The state in one page

**The ladder is FROZEN and the champion holds it.** `readable/denial-off-champion.rs`, sha `0e92f8fa…`, submission
`41240269`, **19.23 at rank 60 of 177** — still the highest reading this project has recorded, and it came from
resubmitting the identical file. **Nothing may be submitted (§3).**

| agent | state |
|---|---|
| `chatgpt_1` | Idle. Its orchard experiment closed on its own dead condition; its judgements are on `main`. |
| `chatgpt_2` | Idle. **Produced the two best results of the period** (the port post-mortem, the late-bankable adjudication). Needs the owner to activate it. |
| `claude_1` | Idle, queue clear. Delivered the orchard reproduction two days early. Mail-woken — **see the trap in §6**. |
| `codex_1` | Idle. **Unblocked 09-04** by the owner and delivered the sealed holdout in thirty minutes. |

**Transport is clean:** 0 unacknowledged, 0 delivery errors, 0 quarantine errors as of 06:2xZ. `main` == my branch.

---

## 2. THE BIG RESULT — we closed a ten-point line on a misdiagnosis

**Row P-2, `coordination/tasks/20260905-port-postmortem.md`. chatgpt_2 delivered it 41 minutes after the charter;
I verified it by running its `analyse.py` myself.** Verdict **`PORT_SPECIFIC_HYBRID_FAILURE`** — *the #2 player's
design is genuinely strong and our port never implemented it.*

| turn | the real bot: wood points / cumulative plants | our port |
|---|---|---|
| 100 | 6.60 / **9.44** | 6.60 / **4.01** |
| 150 | 49.32 / 15.13 | 26.05 / 7.34 |
| 200 | 154.72 / 21.53 | 61.65 / 10.34 |
| **end** | **334.16 / 31.89** | **99.95 / 13.01** |

**At turn 100 the two are level on wood and the real bot has already planted more than twice as many trees.** By the
end it banks 3.3× the wood off 2.5× the trees. **The orchard is the engine and the port never built one.** Its 31.89
plants a game independently reproduces Track R's "~29 trees" from a different measurement.

**The bug is one misreading.** The port saw that the real bot has a median of **seven trees alive** at its Deforest
switch and treated seven as a **production cap**. It is not a cap — it is the standing cohort after ~15 cumulative
plantings. With one planting job, our champion's chop targeting and no thinning, the port never recycled orchard
slots, then disabled harvesting in Deforest entirely.

**And our original diagnosis was wrong — that one is mine.** We closed Track P blaming the Produce→Deforest switch.
**Fruit-first is native behaviour, not the bug** (the real bot's first wood is at median turn **96.5**), and forcing
the repaired port to switch near turn 75 still left margin **−59.62**. I built that repair; the line's last budget
went on a parameter that could not have worked.

**The failure has this project's own name: *two correct doors make a wall*** — native macro-economy grafted onto our
micro-control across a boundary our own reconstruction had already listed under **"Not solid"** (the chop
target-selection rules of all four players were never recovered).

### What is solid and what is NOT — do not overstate this

**Solid:** the strength advantage and the mechanism. Those are direct measurements of two recorded populations.

**Not solid: the SIZE.** The packages have almost no common support — 218 native games at mean opponent rating
**25.50** against our champion's 320 at **17.51**; only 4 of 320 champion games faced rating ≥ 20. **The reweighting
returns `0.00 [0.0, 0.0]` with `opponents: 0`, which is the reweighting having nothing to work with, NOT a null** —
and chatgpt_2 **refused to report it**, writing *"I therefore do not report a fake direct reweighting."*

- **+11.23 rating points** (platform 29.66 vs our champion-package mean 18.43) is the defensible headline.
- **+156.57** rests on **nine** native games.
- **+152.80** is an extrapolation its own author labelled non-causal.

**The advantage is real; its transferable size is unknown.** Say it in those words.

---

## 3. THE OWNER'S STANDING RULE — nothing goes on the platform

**Owner, 2026-09-04: *"don't publish programs on platform until I say you can."*** No submission, no timed read, no
promotion cycle, no restore, by any agent, by any route.

- **This SUSPENDS the standing Arena authorization of 2026-07-30** ("submit anything worth trying"). Not revoked —
  not in force. Head of `docs/STATE.md` §3.
- **Enforced mechanically:** the VM ladder-queue cron is **DISABLED** — `#DISABLED-2026-09-04-owner-no-platform` in
  `crontab -l` on `troll-vm`. Before that it fired every five minutes and would have submitted anything pushed into
  `local_claude_1/ladder-queue/queue.json` within five minutes. **Verified holding: its log's last line is still
  `2026-09-04T13:55:03Z`, nearly three days of silence.** Re-enable by deleting the prefix — **only on the owner's word**.
- A candidate that earns a ladder hour now **waits for the owner**. Say so in the handoff and stop.

---

## 4. THE ORCHARD IS CLOSED TWICE — and the second close is the instructive one

**Rows 3-8 and 3-9.** chatgpt_1's experiment (the owner's "run it") died on its own dead condition 3: Δ final margin
**0.00 [0.00, 0.00], n=24**, its leave-one-map-out selector choosing `NO_PLANT` in all 24 folds. I reproduced its
whole result file field for field.

**A zero that arrives through a selector proves nothing on its own**, which is exactly why the reproduction existed.
claude_1's independent implementation agreed to every digit **and settled the question the headline could not**:

> **With no exclusion rule at all and all 48 planting policies in the pool, the selector still declines on 21 of 24
> folds; ALL 48 have a negative mean Δ; the best is −0.46 [−4.51, +3.60].**

**The zero is manufactured neither by an exclusion rule nor by a selector. There is nothing there.** I verified this
by rerunning its `analyse.py`: **byte-identical results file, `git diff` returns nothing.**

claude_1 also **withdrew its own central criticism** (chatgpt_1's rule was already relative, `oracle.py:803`; its own
was the stricter member of the same family), then ran its grid under chatgpt_1's exact rule — 29 of 48 policies kept
against its own 1, selector still declining 23/24 at Δ −0.83. **Widening the gate thirtyfold produces no winner
because the pool contains none.**

**★ Carry this number forward: the champion's OWN longest no-command streak on these maps is a median of 88 turns and
a maximum of 151.** An absolute 60-turn stall threshold would exclude **the champion itself on 17 of 24 map-seats**.
The next agent reaching for a fixed stall threshold must see this first.

---

## 5. The other two deliveries, both awaiting the coordinator's execution

- **The sealed holdout (row 0-8, codex_1)** — `46c39d98…`. Active `holdout-001`, standby `holdout-002`, **zero
  authorized opens**, development manifest and external-opponent set built. **Why it matters: every build since August
  was shaped against the 24-map smoke and the 200-map panel, so a good number there measures tuning, not
  generalisation.** Rules: **read once at a gate, then retire into development and draw a fresh standby**; nobody
  opens it otherwise, including me. **My execution verification is OWED.**
- **Late bankable wood (row E-2, chatgpt_2)** — `PREMISE_SURVIVES_READ`, **and it refuted the rule it was testing.**
  It resolved a contradiction between two of our own numbers: `705/734` was a tree-level *ever-event* count from turn
  200; `83.7 %` was a troll-turn count on `NONE` turns from 251; full-job feasibility falls from ~59 % in turns
  251–260 to **7.6–8.0 %** in 291–300, so both were true. **The refutation: for trees still standing at game end,
  ZERO points are exposed at an idle decision** — "replace idle with chop" is not supported; **82.1 % of the ceiling
  sits at `PICK` and `PLANT` decisions** in the late replant loop. Ceilings are **not** expected gains (they charge
  nothing for the orchard value lost). Co-chop duplication is 2.54 points, below the 4-point bar, stays separate. **Its
  successor build is unchartered and waits on the owner's sequencing. My execution verification is OWED.**

---

## 6. OPERATIONAL TRAPS — one of them cost 44 hours this period

- **★ A multi-day card given to a mail-woken agent needs a daily heartbeat.** The launcher rings an agent only when
  its **queue changes**. I chartered claude_1's two-day reproduction and then sent it nothing; **it was not woken once
  for 44 hours** and its deadline nearly passed with one wake of work done. **Silence from a bot is not evidence it is
  working.** Now written into `coordination/WORKING-RULES.md` §8. Check `/home/tarstars/launcher-state/wake-log.jsonl`
  before concluding anything about a quiet agent.
- **Do not quote one agent's numbers to another agent whose card forbids them.** My quarantine ruling quoted three of
  chatgpt_1's per-policy means to claude_1, contaminating a reproduction I had designed to be blind. claude_1 declared
  it; its registered choices predated the leak so the test stood, but that was luck.
- **`pgrep -f "<script>.py"` matches your own shell command** and reports a finished job as running. Cost one wrong
  conclusion.
- **chatgpt_1's orchard oracle needs ABSOLUTE paths.** With relative ones it does the whole computation and only then
  fails at the provenance step, after several minutes.
- **The laptop suspends for hours mid-session** (commute, idle timer). Real UTC can jump forward between two of your
  own commands — **take every message stamp from `date -u` at the moment of writing**, never guess forward.
- **The transport defect recorded eleven times now:** push the artifact commit first, confirm it is on the remote,
  **then** write the message that pins it. chatgpt_1's orchard handoff pinned a commit missing a `FINAL.md` committed
  forty seconds later; it is quarantined **on transport only** (registry `coordination/quarantine.json`, adjudication
  `20260904T173300Z`) and its result stands, verified.
- **Merging codex_1 can collide on hash-locked submission files.** Its v3 port checkpoint collided with the measured
  v3 on the canonical path; resolution kept **the measured artefact** (`84870bc9…`) and preserved codex_1's variant at
  `codex_1/norxondor-port/superseded-v3/`. **Never overwrite a hash-locked record with an unmeasured variant.**

---

## 7. The honest scoreboard, which the owner asked for and should stay visible

**Nine days of intense work bought a working laboratory and no better bot.** Twelve ladder readings since 08-27; every
candidate read at or below the champion (orchard 6's 18.84 was *indistinguishable*, not better). The champion of
record is the *old* champion with one rule deleted — its rising number is the field moving around an unchanged file.
**Fifteen lines in the graveyard.**

Two measured reasons, both now established rather than argued:

1. **We kept attacking the roster.** Closed four independent ways — we can reach three trolls at game turn 25, 71
   turns ahead of the field, and still lose.
2. **We could not have seen a win if we had one.** One ladder hour resolves nothing below ~2.2 rating points
   (paired half-width = 1.96 · sd · √(2/n), sd 0.815: n=1 → ±2.26, n=6 → ±1.00, n=21 → ±0.50) and almost everything
   we tried was smaller. **Δwin is retired as a kill criterion; Δmargin with its interval is the selector**, and the
   margin-to-rating relation is **flat then falling**, not linear — never convert a margin to a rating by a slope.

**On 09-05 the owner chose the big bet from four options** — reopen the port question — and §2 is what it returned.
That is the first time in this period that a line came back saying *there is something here and we broke it*, rather
than *there is nothing here*.

---

## 8. Verified mechanics and geometry — do not re-derive

- **A mature size-4 tree is 16 points, not 4** (`WOOD_POINTS` 4; felling yields `plant.size`).
- **Health at maturity, all yielding 4 wood: banana 6, plum 12, lemon 12, apple 20.** A chop-1 troll fells a banana in
  6 turns against an apple's 20 — **3.3× the wood per chop-turn** — and the referee prices bananas at **zero** for the
  training bill. **Plant bananas for wood; keep plums, lemons and apples for the bill.**
- **First fruit:** plum/lemon ~12 turns beside water vs 32 inland; apple 8 vs 36; banana 16 vs 24. A full tree regrows
  one fruit the instant it is harvested.
- **Planting geometry** (400 map-seats, `claude_1/orchard-kinetics/results/curve.json`): **11.5** free cells within
  two steps of the shack, **27** within four, of which only **2** and **5** are water-adjacent. Starting fruit draw
  median **24**. **The fast orchard is small and the big orchard is slow.**
- **Raids:** 0.19 per 100 tree-turns before turn 100, **0.6–1.0 after**.
- The referee's chop loop is commented **"last wood can duplicate"**.
- **Never model the opponent as idle.** That assumption made stage 2A promise turn 70 and deliver 74.5 into a
  stripped forest.
- **The champion trains once** — "byte-identical through the champion's own second `TRAIN`" has one executable
  reading (claude_1, registered before any number existed).

## 9. The coordinator's own errors this period, all corrected in place

The Produce→Deforest misdiagnosis and the repair built on it (§2); "codex_1 is out of credits until 09-07" when the
owner had cleared it and a one-shot probe returned `CODEX OK`; leaving claude_1 unwoken for 44 hours (§6);
contaminating its blind reproduction (§6); a stale header that showed two open tasks against `chatgpt_1` when the work
was `chatgpt_2`'s; and invented `16:5xZ` timestamps on a card, corrected against the real clock before publication.
Every one was caught by execution or by an agent. **That is the process working, and it is the reason to keep
verifying by execution rather than by reasoning.**
