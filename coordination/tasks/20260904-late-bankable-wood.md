# Task 20260904-late-bankable-wood — settle one contradiction before building anything

- **Born:** 2026-09-04 13:5xZ. chatgpt_1's **Experiment B**, the second-ranked item of its judgement
  `chatgpt_1/judgement/2026-09-04-what-to-attack-next.md` (§1.2, §2 "Experiment B"), which the coordinator had **not**
  chartered when it chartered Experiment A. The owner opened capacity for it at 13:4xZ ("I can activate chatgpt_2 as
  well"; "codex_1 can work now by your request").
- **Work owner:** **chatgpt_2**. Verifier: the coordinator, by execution.
- **Kind:** **a read that adjudicates two of our own numbers. No build, no bot, no ladder, no platform.** A build
  follows only if the premise survives, and only on a new card.
- **Budget:** one read, **one day, to 2026-09-05 14:00Z.**

---

## 1. Why this is a read and not the build chatgpt_1 asked for

chatgpt_1 proposed a one-variable build: from turn 251, if any legal bankable chop exists, suppress `PICK` and `PLANT`
and choose among bank, move-to-bank and bankable `CHOP`; byte-identical to the champion through turn 250. Its gates
are good and are preserved in §4.

**But its premise contradicts a delivered, closed read of the same data, and the contradiction has to be settled
first.**

| | says | source |
|---|---|---|
| **chatgpt_1** | **705 of 734** trees left standing in one champion package were **a legal bankable chop for one of our trolls at some turn after 200**; on the last turn those trees were feasible and the trolls were chopping something else or running `PICK`/`PLANT` | `2026-09-04-what-to-attack-next.md` §1.2 |
| **claude_1** | of our idle late troll-turns, **84 % are terminal waits** — *nothing reachable could be felled or banked before turn 300* — half of them in the last ten turns | `claude_1/endgame-gap/READ-2026-09-02.md`, pin `447ff1d9…`, card `20260902-endgame-move-gap`, **closed 09-02 with "Candidate rule: none"** |

**Both can be literally true and still not support the build.** "Bankable at *some* turn after 200" is a much weaker
test than "bankable at the turn the troll was idle": a tree can be reachable-and-bankable at turn 210 and impossible
at turn 290, and the champion has ~100 turns in which to have been elsewhere. **If chatgpt_1's 705 is a
some-turn-in-a-hundred figure, it does not describe a recoverable opportunity at all**, and the build would be
optimising against a statistic that never had a decision behind it.

The E-1 read also priced the whole opportunity at **at most ~6 points a game against a 46-point gap**, decomposed as
roster ×0.70 · idleness ×0.85 · output ×0.93, and concluded the losing layer is the roster, not idleness. That is the
finding this card is testing against — not overturning by assertion.

## 2. The question, stated so it has a number for an answer

**On the same champion package, at each late troll-turn where the troll issued no command or issued `PICK`/`PLANT`:
was there, at that turn, a bankable chop the troll could have started and banked before turn 300?**

Not "at some turn after 200" — **at that turn**, with the walk home included. Report:

1. **The count and share** of late idle / `PICK` / `PLANT` troll-turns that had a feasible bankable chop **at that
   turn**, with the feasibility test written out (walk to tree, chops needed at that troll's chop power, carry, walk
   to a bank, turns remaining).
2. **The points** those feasible chops would have banked, per game, as a distribution and not only a mean.
3. **The reconciliation, in one paragraph:** where chatgpt_1's 705-of-734 and claude_1's 84 %-terminal-waits actually
   differ — different question, different population, different feasibility test, or one of them wrong. **Name which.**
4. **The referee's co-chop duplication** (the chop loop is commented *"last wood can duplicate"*) priced separately —
   E-1 put 2.5 of its 6 points there, and it is a different mechanism from an idle troll.

## 3. Dead means

**If the feasible-at-that-turn share is small, or the points it buys are below about four banked points a game with a
paired lower bound above zero, say so with the number and stop. No build follows.** That is chatgpt_1's own bar (four
points is one banked wood unit) applied to the premise instead of to the result, which is the cheaper place to apply
it. E-1's line closes for the second time and this card is the obituary.

## 4. If the premise survives — chatgpt_1's build and its gates, preserved verbatim for the successor card

**One variable.** From turn 251 onward, if any legal bankable chop candidate exists, suppress `PICK` and `PLANT`
candidates and choose among bank, move-to-bank and bankable `CHOP`. **No** opponent ownership, **no** unbankable
denial, **no** roster change.

**Control.** The unchanged champion. The two programs must be **byte-identical through turn 250** — the same
architectural discipline that makes row 3-8 immune to the disease that killed three builds.

**Mechanism gate, written before the run:** mechanics 24/24 and no new stall; at least **25 % fewer empty late
troll-turns**; at least **four extra banked score points per long game** with a paired map-bootstrap lower bound above
zero; **no score difference through turn 250**.

**And its honest ceiling, which the owner should see now rather than later:** chatgpt_1 expects **half to two rating
points**. That is **below the 2.2 a single ladder reading can resolve**, so this rule can never earn a ladder hour on
its own — it is a component to combine with a larger candidate, and it must be measured offline by paired replay. It
is on the board as a cheap, clean mechanism, not as a route to Legend.

## 5. What this card must not do

- **No build, no bot, no generator, no submission, no platform, no Arena.**
- **No re-opening of the roster question**, which is closed four independent ways.
- **No touching row 3-8's experiment or its maps.** This is the endgame; that is the opening.
- **Do not re-derive E-1's read** — take its numbers as given and test only the specific claim above against them.

## Log

- 2026-09-04 13:5xZ born; chatgpt_1's Experiment B converted from a build to a one-day adjudication read because its
  premise contradicts the closed E-1 endgame read; its build and gates preserved for the successor card. — coordinator
