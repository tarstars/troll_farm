# Task 20260905-port-postmortem — is the #2 player's design worth 10 points, and did we test it or something else?

- **Born:** 2026-09-05 05:5xZ, on the owner's choice from the strategic fork. The owner's framing: **the gap is ~9
  points and 1-point experiments cannot close it, so pick the big bet.** This is the bet.
- **Work owner:** **chatgpt_2** — it wrote neither the reconstruction nor the port, which is the qualification.
  Verifier: the coordinator, by execution. **codex_1 built the port and is available to answer questions about it**,
  but does not own this read.
- **Kind:** **a read. No bot, no build, no ladder, no platform.** A build, if any, is a separate card on the owner's word.
- **Budget:** one read, **two days, to 2026-09-07 06:00Z.**

---

## 1. The question, and why it is worth more than anything else on the board

**We implemented the design of the #2-ranked player — rated 29.66 — and it lost 8–0 to our own 19-point champion.**

That is a contradiction the size of the entire gap we are trying to close, and we closed the line after one parameter
fix. Three things can be true and they have completely different consequences:

| if… | then… |
|---|---|
| **the design is not actually worth 29.66 in our hands** | copying top players is a dead strategy and we stop doing it |
| **our reconstruction of it is wrong** | Track R's four documents are worth much less than we have been treating them, and every idea drawn from them is suspect |
| **the port broke it in a specific, identifiable way** | there is a ~10-point design sitting in our repo that we mis-built, and that is the whole gap |

**Nobody has asked which.** The line was closed on "it read worse", which is a fact about our build, not about the
design.

## 2. What the record already gives you — do not re-derive these

- **The port lost twice, consistently.** Rung 1: **Δwin −0.421 [−0.453, −0.389], Δmargin −71.1** over 1,600 local
  games. Rung 2: **the champion 8 wins to the port's 0** over 15 paired games on the same seeds against five real
  Legend agents. Two populations, same direction and size.
- **The loss was diagnosed once already:** the Produce→Deforest switch — the port banks 1-point fruit while the
  champion banks 4-point wood and joins the wood race about 100 turns late (30 points down by turn 50, 55 by turn
  100). 112,919 scores verified exact.
- **The one repair failed.** `PRODUCE_ROSTER_CAP` 3 (v3/v3.1) read FIELD **−0.4675**, *below* v2 by 0.046 → the third
  dead condition, and the line closed 09-02 15:26Z.
- **THE LEAD, and it is in our own reconstruction's own words.** `local_claude_1/reconstructions/README.md` lists
  under **"Not solid"**: *"the target-selection rules (**chop**; the plant kind) of all four; norxondor's tie-breaks
  and the meaning of its second message letter."* **The chop targeting was never recovered.** The port therefore ran
  **norxondor's economy on our champion's chop targeting** — and it lost *precisely in the wood race*. That is not a
  coincidence worth ignoring.
- **And our own history warned us:** the one previous time a norxondor-shaped controller was built from fitted rules,
  it lost **−173 points closed-loop while matching 77 % of its recorded decisions.** Per-decision accuracy does not
  survive the closed loop.
- **The composition hazard has a name here:** *two correct doors make a wall* — two individually correct components
  that fail when combined. A hybrid of their economy and our targeting is exactly that shape.

## 3. The read — and question 3 is the one that settles it without any implementation

1. **What did the port actually implement?** Part by part, which came from the reconstruction and which from our
   champion. Produce the boundary explicitly. **A hybrid was a design decision made because the reconstruction's own
   §5 said a straight port lost 173 points in July** — so name what that decision assumed.
2. **Is the Produce→Deforest failure a property of norxondor's design, or of the graft?** The port banks fruit while
   the champion banks wood. **Does the real norxondor do that too?** If the real bot also banks 1-point fruit early
   and still rates 29.66, then the diagnosis was of a symptom, not the cause, and the repair was aimed at the wrong
   thing.
3. **★ THE DECISIVE ONE, and it needs no bot at all: measure the real norxondor against our real champion, from
   recorded games.** We have **218 corpus games of the actual #2 bot** (agent `6480540`) and 160-game packages of our
   champion, both validated against the referee's own tallies (`local_claude_1/reconstructions/profiles/`,
   `local_claude_1/ladder-queue/games-*/`). Compare **score trajectories, wood-vs-fruit banking over time, roster
   timing, and final margins** against comparable opposition. **This answers "is the design worth ~10 points over
   ours" directly, from what both bots really did, with no implementation in the way.** Mind the confound that killed
   an earlier comparison: opponent strength differs between packages — report opponents' mean rating for every cut and
   do not compare raw scores across packages without it.
4. **Where exactly do the two diverge?** With the real norxondor's games and our champion's on comparable maps: the
   turn its economy pulls ahead, and what it is doing at that turn that we are not.
5. **Was the reconstruction right?** Its fits recorded training triggers exact on 784 games, plant cell 84–90 %, and
   **no chop formula fitting at all.** Given question 3's answer, say plainly whether the document is a sound basis
   for a build and which of its layers are load-bearing but unverified.

## 4. Done means

One page, plain words, that answers: **is there a ~10-point design here that we mis-built, or not?** With the numbers,
the intervals, the opponent-strength controls, and a straight recommendation — reopen with a specific repair named, or
close the copying strategy for good and say what the record should conclude about Track R's documents.

**Say which of the three outcomes in §1 the evidence supports.** That is the deliverable.

## 5. Dead means

**If the real norxondor's recorded games do not show a large, mechanically identifiable advantage over our champion's
against comparable opposition, say so with the number and stop.** Then the answer is that the 29.66 is not a
transferable 10 points for us, the port line stays closed, and — importantly — **we stop mining the top four for
ideas**, which is a strategy this project has spent weeks on. That is a real and valuable outcome, not a failure.

## 6. What this read must not do

- **No bot, no build, no port revival, no submission, no platform** — the owner has frozen the platform entirely
  (*"don't publish programs on platform until I say you can"*, policy `20260904T140500Z`).
- **Do not re-run the port or repair it.** This is a question about evidence we already hold.
- **Do not re-open the roster question**, closed four independent ways.
- **Do not judge on per-decision accuracy.** Our own history says 77 % decision agreement lost by 173 points. Only
  closed-loop outcomes count.

## Log

- 2026-09-05 05:5xZ born on the owner's choice from the strategic fork: of four options, reopen the port question as a
  read. Chartered to chatgpt_2. — coordinator
