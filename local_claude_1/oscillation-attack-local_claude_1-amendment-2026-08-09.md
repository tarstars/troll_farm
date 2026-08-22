# Amendment to my oscillation answer

- Amends: `local_claude_1/oscillation-attack-local_claude_1-2026-08-09.md` (commit `1c65c9fc`)
- The original stays immutable. This is the amendment I required of the peers, applied to myself.
- Author: `local_claude_1`. Still written without reading either peer's answer.

Two things changed after I published: the owner restated the objective, and I found evidence
against a claim I had accepted. Both cut against my own conclusions.

## 1. My recommendation is withdrawn

I recommended repairing the **gate's reference build** rather than the shipped bot, and asked the
owner to consider replacing "raw D-1 = 0" with "no terminal oscillation".

The owner's objective is *control over the program, technical debt, test coverage,
understanding* — not score and not gate compliance. Against that objective **both of my
recommendations are wrong, and in the same way**: they make a number acceptable without making
the program more controlled. Repairing only the reference leaves the shipped bot able to enter a
194-turn no-op. Relaxing the condition hides it. Neither adds a line of understanding.

**Withdrawn: D1 and D3 as recommendations.** They remain in the original as options with their
costs, which is the right place for them.

**What I now recommend instead: A1 in the shipped bot, with a committed regression test.**
Record each unit's previous cell and exclude it from detour candidates. It is hours of work, uses
the per-unit-state pattern the bot already has, and — this is the part that matters under the new
objective — it comes with a test that reproduces a 2-cycle and fails without the fix. That
converts "we think it can't happen" into "a test says it can't". A1 was already my
implementation choice; what changes is that it goes in the *shipped* program and the deliverable
is the test, not the number.

If A1 turns out to convert oscillations into stalls, **B1 (the Elost rule) is the escalation** —
it removes the cause rather than the symptom, and it cannot produce a stall because the displaced
unit gets a different productive target. It needs the owner.

## 2. Evidence against the account I accepted — including my own §1

My §1 said I could not falsify `claude_1`'s D1-A account and did not dispute it. I have since
found something that partially does, and it applies to my own text too, since I described the
mechanism in terms of a contested target.

**The candidate carries yamo's coordination.** `select` (readable 665–687) enumerates candidate
**pairs** and rejects any pair failing `compatible(a.target, b.target)`, which is `a != b`
(643–653). **Two units can never choose the same target cell in the same turn.** So whatever the
34 episodes are, they are not two units electing the same target.

What survives, and what I now believe: **path blocking**. Unit A's route to its own distinct
target runs through the cell a parked peer occupies. The peer is parked because it is *working* —
30/34 of `claude_1`'s episodes have it standing on a plant. The memoryless detour then bounces A
between two cells forever.

This does not change my mechanism in §1 — the 4-step cycle, the pure-function detour, the closed
loop — all of that holds and is what actually produces the oscillation. It changes the *name of
the precondition*, from "both want the same tree" to "one is standing where the other must walk".
That matters for the fix: **B2 (exclusive target claiming) is now near-useless**, because targets
are already exclusive. I had it ranked as a structural option; it should be dropped.

`claude_1` owns the resolver replay and can settle this properly. The question is precise: if the
parked peer is on the target cell, how did that pair pass `compatible`?

## 3. The original author shipped this knowingly

`docs/reference/yann-moisan-postmortem-2026-05-26.txt:148`, the author of the bot ours
reproduces:

> *"I didn't optimize movement at all. I only set the destination, which meant my trolls
> occasionally blocked each other."*

He knew, accepted it, and placed 3rd in Legend. So this is a faithfully reproduced limitation,
not something we broke. Under the owner's objective that is **not** an argument for keeping it —
it is an argument that removing it is genuinely new ground rather than a repair, and that we
should not expect the original's score to have depended on it.

It also independently corroborates §2: *"I only set the destination"* is precisely a design with
no movement-level coordination, which is what path blocking requires.

## 4. What is unchanged

- The mechanism in §1, and the two facts I verified: the bot carries per-unit state across turns
  but has **zero** position memory, and **all 34 episodes are 2-cycles between orthogonally
  adjacent cells** (34/34), which is why A1 breaks every one by construction.
- **A3 stands**: the Gold-era watchdog tracks a *same-position* streak and cannot fire on a unit
  that is never in the same position twice running. Do not port it.
- My §2 margin analysis stands as measurement — terminal-oscillation games average +1.58 against
  +16.74, −13.6 after map-class control — and so does the reading that oscillation is a **marker
  of a cramped position rather than the cause of losing it**, given D176a's causal +0.045.

**But its consequence is now different.** I used that reading to argue *don't bother fixing it*.
Under the owner's objective it argues something more useful: **those 19 games contain a problem
we have not diagnosed.** If oscillation only costs +0.045 and those games are 13.6 points worse,
something else is wrong in them. Removing the oscillation without understanding that would erase
a signal that is currently pointing at it.

So I would add one action I did not list: **use the oscillating games as a diagnostic set.** They
are 19 pre-identified games where we barely win. Understanding why is squarely within "improve
our understanding of the situation", and it is free — the games are already measured.
