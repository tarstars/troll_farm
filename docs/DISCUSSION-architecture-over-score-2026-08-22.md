# DISCUSSION 2026-08-22 — what we are optimising, and a defect in how we measure it

Owner session, 2026-08-21 evening into 2026-08-22. Written down at the owner's
instruction ("let's write down this discussion, I think it's important").

It records five things: a **reframing of the project's objective by the owner**; a
**hypothesis of theirs that was tested and not supported**; a **measurement defect found
while testing it**, which touches a ruling already made; a **diagnosis of why cure α is
stuck** that is structural rather than a missing tweak; and a **proposed acceptance rule**
that follows from the reframing.

Nothing here is a ruling except where marked **OWNER**. Open decisions are listed in §9.

---

## 1. The reframing (OWNER)

> "The total aim of the whole project is to find the best working architecture (or a set
> of) for this type of problems: control of a complex objects. Trolls and their world only
> provides an example to try against. Not all moves should strictly improve score. If score
> is the same, but the programm is smaller and cleaner, it's a good one."

Spelled out, because it changes what a verdict means:

- The Arena score is a **constraint**, not the objective. A floor to stay above, not a
  number to maximise.
- A change that is **score-neutral and smaller** is an improvement, not a null result.
  Under the old framing it read as "immaterial", which is why the distinction matters.
- The game is a **testbed**. A result that generalises to controlling complex objects is
  worth more than a result that only moves this ladder.

**We have already done this once without naming it.** The champion of record
`547fa706…` is cure C with the fictional-decay hunk **deleted** — `candidate-door1-pure-deletion.rs`.
Measured against its own parent it was **+0.220, ruled IMMATERIAL**, and the owner ruled
KEEP anyway. That was this principle in practice before it was written down; it should be
cited as the precedent whenever a score-neutral deletion is proposed.

## 2. Three things this discussion had to separate

The owner's correction of the integrator, who had run them together into one argument.

**(a) Local fixes.** Behavioural facts on the panel, true or false regardless of the
ladder. Cure α, rev 2, on the matched 240-game panel: dance episodes **27 → 9**
(healed 18, **new 0**), frozen-solid violations **16 → 0** (healed 16, **new 0**), **210 of
240 games byte-identical**, the 20 changed games each named
(`claude_1/swap1/g2-report-rev2-2026-08-21.md`).

**(b) Score.** A separate axis, measured by the instrument examined in §4.

**(c) Historical attempts. WITHDRAWN as evidence.** The integrator had cited "six
cleaner-but-negative re-architectures in the Gold/Silver era" and A2's stop at its Phase-1
kill rule as a caution against re-architecture now. The owner's objection is accepted:
those verdicts were produced with instruments we have since replaced — before paired
nights, before the noise band was estimated, before the 240-game panel and the detectors.
**They do not transfer.** If we want that caution it has to be re-derived with the current
equipment; until then it must not be used to argue against an architectural attempt.

## 3. Why cure α is stuck — an information boundary, not a missing tweak

Cure α implements the owner's rule R-1: when two of our trolls need to pass each other in
a corridor, issue the referee-legal exchange instead of making one wait (the worst recorded
case waits **193 turns**).

Its first version cured blocks by manufacturing a new dance: **27 fires, 98 re-swaps** in
one game — push a working troll off its square, it walks straight back, push again. The
charter's assumption that a displaced troll resumes "within about 2 ticks" was measured and
**contradicted**: resumption took 29, 27, 27, 25 … ticks.

Rev 2 narrows the trigger to *fire only when the partner's command this tick is `WAIT`*.
That game is now completely healed — zero fires, whole game byte-identical to the base —
and re-swaps fall **111 → 13**.

**The residual 13 are not separable at the layer the cure lives in, and that is a proof,
not a difficulty.** claude_1 tabulated every field visible at the decision seam — vacates,
target-is-landing, partner-`WAIT`, partner verb, path, detour-existed, both BFS distances —
and the OSC-011 dance fires sit in the **same bucket** as the two fires we must keep
(OSC-005 t52, OSC-012 t9). Over every field the table records they are indistinguishable,
so **no predicate over those fields can separate them**. The claim's exact strength, as
stated by its author: this is not a proof that no function of the whole `GameState` could.

What separates them appears **one tick later**: in OSC-011 the displaced troll's next
command is `MOVE … 9 4`, straight back for the contested cell; in OSC-005/012 it stays
`WAIT`. So the distinguishing fact is the partner's **intention**, which is not present at
the transport seam at all. Restated in one line:

> **"Waiting this tick" is not "has nothing to do", and the conflict resolver cannot see
> the difference, because the difference is a fact about the other troll's plan.**

This is why the block does not look like a tuning problem. The layer is being asked a
question it structurally cannot answer. codex_1's reserved question is the minimal way to
give it the missing fact: *may the transport seam receive a read-only own-unit
planner-target map, including WAIT units, solely to suppress displacement from a partner's
own target?* — a charter exception, owner-blocked
(`coordination/messages/codex_1/20260821T110533Z-20260821-swap-r1-cure-ack.md`).

**A second, separate cost.** The narrowing deletes the CHOP/HARVEST displacement path, so
α now fixes only the *idle-blocker* family. In the two owner-ruled cases where the blocker
is **busy chopping** (OSC-005, 12 turns; OSC-027, 22 turns) it does nothing — on OSC-005 its
only fire lands at turn 52, long after the episode ends. That is roughly half of R-1 left
unimplemented, and it travels with every α verdict as a named scope cost.

## 4. The measurement defect: the pairing order carries the drift

Found while testing the owner's hypothesis in §5. **This is the most actionable item in
this document.**

Every night runs arms in strict alternation — A B A B A B … — and the verdict pairs each A
with the B **that follows it**. So **arm A always occupies the earlier slot of its pair**.
Pairing cancels noise; it does not cancel *trend*. Any drift over the night enters every
pair difference with a fixed sign.

Re-pairing the identical reads the other way — each A against the B **before** it — gives:

| night | as measured (A first) | re-paired (A second) | average (drift-cancelled) | within-night slope |
|---|---|---|---|---|
| cure C vs very-old resident | **+1.02** | +0.43 | **+0.72** | −0.19 / slot |
| door-1 vs cure C | +0.22 | +0.30 | +0.26 | +0.01 / slot |
| door-1 vs very-old resident (session 3, 4 pairs) | **+0.55** | +0.13 | **+0.34** | −0.18 / slot |

The middle night is stable — and it is the one with no slope. **Both nights with a downward
slope roughly halve.** Including the one that matters most: cure C's **+1.02** is the number
that cleared the 1.0 materiality floor and carried the **KEEP** ruling of 2026-08-19.
Symmetrised it is **+0.72 — below the floor.**

**Honest strength of this.** n is 4–5 pairs; the two pairings share reads and so are not
independent estimates; a slope of −0.19/slot is itself inside the noise band (σ_pair 1.5).
This does **not** establish that cure C was not an improvement. What does not depend on any
of those estimates is the design fault: **with a fixed A-then-B order, drift has nowhere to
cancel**, and two of our three nights show a slope of the sign that inflates the result.

**The fix is free.** Alternate the pair order — A B B A A B B A — or keep the order and
report the average of both pairings beside the primary. Same submissions, same hours, no
extra Arena cost. Proposed for the next block; not yet ruled.

**Consequence for reading the record.** Where a past verdict sat close to the floor or the
bar, the symmetrised figure should be reported beside it rather than the old number
silently restated.

## 5. The hypothesis that was tested and NOT supported

The owner's reasoning, recorded because it was the right question to ask:

> "if the change is really insignificant, we should have approximately equal amount of
> positive and negative score changes, but in our experiments positive scores clearly
> dominate."

Measured over all 14 recorded pairs: **10 positive, 3 negative, 1 zero**, sign-test
one-sided **p = 0.046**. The pattern is there in the pooled data.

It does not support the hypothesis, because the pool mixes questions. Two of the three
nights compare a newer bot against a **two-generations-older** one, where positive is the
expected answer rather than a symptom. **The only night that asked "is this step real?"
came out 3 up, 2 down, mean +0.22** — symmetric, exactly as the owner says a null should
look, and it was ruled IMMATERIAL.

So the suspicion was right that the delta measurement has a problem (§4), and wrong about
its direction: the defect found points to **over**-crediting changes, not to manufacturing
significance out of noise.

## 6. One root, three symptoms

Three defects have been worked as three separate bugs with three separate cures. They are
one design decision showing through in three places:

- **Benching.** The pair-picker prefers self-impossible pairs — the partner moves onto the
  benched troll's cell while that troll is ordered to `WAIT`, the referee drops it, repeat
  ×194 in one game; plus 810 exact ties broken by undesigned map order.
- **Corridor blocking (α).** Two trolls collide and a repair layer with no view of intent
  must guess (§3).
- **The parked troll.** A troll with no chopping or harvesting power sits on the only tree
  for 193 turns while the able troll dances in front of it, and nothing reassigns either.

The root: **our two trolls are planned independently, and every collision is repaired after
the fact by a layer that cannot see what the other troll means to do.**

## 7. Proposed acceptance rule — two axes and a guardrail

If score stops being the objective (§1), an explicit second axis is required, or "tolerate
a loss" has no stopping rule and every negative result can be read as "we are crossing the
valley". Both halves already exist; they have simply never been declared as *the* rule:

1. **Behaviour** — panel population: healed minus new must be positive, every changed game
   named, no new class left unexplained. (Already α's amended G-2 bar.)
2. **Cost** — readable bytes under the pinned formatter, which the project already treats
   as canonical for cost figures (`docs/readable-format.md`).
3. **Score** — a **floor**, not a target: do not regress below the materiality floor,
   measured with the §4 correction.

Under this rule α **passes today** — 18 + 16 healed, 0 new, one predicate of added size —
and fails only the fixture-level re-swap gate, on 13 events inside one already-broken game.

## 8. Escaping a local minimum needs a non-score objective

The owner's ML framing — we are in a local minimum and may have to tolerate a loss of
metric to reach a better solution — is accepted. The discipline that makes it safe is to
name, **before** the move, what the new architecture must demonstrate that the current one
structurally cannot, as a **property rather than a number**. For this family the property
is available and sharp:

> **A plan in which one troll is ordered to wait on a square its partner is simultaneously
> moving onto must be impossible by construction.**

Today that is not a bug we fix; it is a state the design can represent, which is why it
recurs as benching, as corridor blocking, and as the parked troll. The property is
checkable without the ladder, it is exactly what joint planning would buy, and it gives a
pre-registered stopping rule for a period of tolerated score loss.

## 9. Open decisions (owner)

1. **Cure α** — allow the read-only planner-target exception (§3), rule the 13 acceptable
   with the reduced scope named, or park α and design a replacement.
2. **The pairing fix (§4)** — change the runner to A B B A, or report both pairings, before
   the next block.
3. **Adopt the two-axis acceptance rule (§7)** as the standing verdict shape.
4. **Adopt the structural property (§8)** as the pre-registered target of any architectural
   attempt, and with it the size of the loss and the period we are willing to tolerate.
5. Unchanged from the standing queue: extend-versus-replace on `idle_regeneration`; which
   corpus is authoritative and how it reaches the workers.

## 10. How to reproduce what is claimed here

- Pair arithmetic and the re-pairing of §4/§5: read counts and timestamps are in
  `local_claude_1/cure-c-night-2026-08-18.md`,
  `local_claude_1/door1-night-state.json`,
  `local_claude_1/door1-vs-old-2026-08-20-state.json`. Pairs are adjacent reads; the
  re-pairing offsets by one slot; the slope is a least-squares fit of score on read index.
- α's panel numbers and the same-bucket event table:
  `claude_1/swap1/g2-report-rev2-2026-08-21.md`,
  `claude_1/swap1/g1-event-table-report-2026-08-21.md`, and codex_1's verdict
  `PACKAGE_REPRODUCED; BLOCKED AT G-1` at
  `coordination/messages/codex_1/20260821T123322Z-20260821-swap-r1-cure-ack.md`.
- The precedent of §1: `cgauto/submissions/candidate-door1-pure-deletion.rs`, sha
  `547fa706…`, and the session-2 verdict in `local_claude_1/door1-night-2026-08-20.md`.
