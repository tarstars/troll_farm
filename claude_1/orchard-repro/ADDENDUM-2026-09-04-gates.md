# Addendum to the pre-registration — what the machinery taught me, 2026-09-04 18:xxZ

The pre-registration (`PREREGISTRATION-2026-09-04.md`) is **not edited**; its value is that its
timestamp precedes every number. This addendum is appended after the two mechanics gates ran and
**before any value number exists**. Three things in it need correcting or pinning down, and all
three were found by running the referee, which the card lists as a permitted input.

---

## 1. My published action vocabulary named a command this engine does not have

I published `PLANT <cell>`. **There is no such command.** `PLANT` has arity 3 —
`PLANT <uid> <KIND>` — and the tree appears at **the planter's own cell**. The corrected
vocabulary for the macro layer:

| action | exact form | meaning |
|---|---|---|
| `NO_PLANT` | *(no rewrite)* | the champion's own fragment passes through. Always legal. |
| `MOVE` | `MOVE <uid> <x> <y>` | step toward the policy's next planting cell |
| `PICK` | `PICK <uid> <KIND>` | take a seed from the bank; **requires the troll within 1 of the shack** |
| `PLANT` | `PLANT <uid> <KIND>` | plant at the troll's current cell |
| `CHOP` | `CHOP <uid>` | **requires the troll to be standing ON the tree's cell** |
| `DROP` | `DROP <uid>` | bank the whole carry; requires the troll within 1 of the shack |

`WAIT` remains deliberately absent. The change is to the *form* of two actions, not to the set:
the search can still reach exactly what §4 said it could.

**Why this matters beyond bookkeeping.** Chopping and planting are both **on-cell**, not adjacent,
actions. A policy therefore costs a walk out and a walk back for every tree, and my earlier
reasoning about "radius from the shack" is a *round-trip* cost, not a one-way one.

## 2. The self-occupancy question, answered from the referee rather than inherited

The card says chatgpt_1 found and repaired a self-occupancy bug in its own instrument, and told me
to write my own model and **not** inherit that fix. I have no model to fix — the referee is the
model — so I asked the referee directly instead (`mechanics_check.py` case 4):

- **A troll plants under itself.** Standing on the target cell does not block planting; it is
  required, since the tree appears at the troll's own cell.
- **Only an existing tree blocks a plant.** With a tree already on the cell the command is
  refused, the seed is **not** spent, and no referee error is raised — a silent no-op.

That silent no-op is the trap. A planting policy that walks a troll onto an occupied cell and
issues `PLANT` loses the turn with no error anywhere: it looks like a working policy that simply
did not plant. My exclusion rule is a no-command-streak rule and **would not catch it**, because
the troll is issuing commands. I am adding a **plant-accounting check** to the value run: for every
`PLANT` the macro emits, assert the referee's plant count rose or the seed was spent. It is cheap
and it runs before any Δ is read.

## 3. The branch point: the charter's sentence has two readings, and one of them cannot run

The charter says arm B is byte-identical **"through the champion's own second `TRAIN`"**. Measured
on 24 map-seats (`results/identity-gate.json`):

```text
TRAINs emitted per game:  1  on 24 of 24
own trolls at turn 300:   2  on 24 of 24
```

**The champion of record trains exactly once.** So:

- **Reading (a), the second TRAIN *event*:** the branch never arrives and the experiment cannot be
  run at all — arm B is arm A on every map-seat.
- **Reading (b), the TRAIN that creates the *second troll*:** executable, and it is the reading the
  charter's neighbouring sentence is written in — *"the second troll's specification and turn must
  never change."*

**I adopt reading (b) and state it here rather than in the write-up**, because it is a choice an
implementer had to make and the card's §3 is about exactly such choices. Branch turn: **median 13,
range 2–28** over the 24 map-seats. It is read from the **referee's roster** reaching two player-0
trolls, not from the text of the command line, so a `TRAIN` the referee refused cannot be mistaken
for one it accepted.

**This is reportable whichever way chatgpt_1 read it.** If it read (a), its candidate was the
champion by construction on every map — which would be a second, purely mechanical explanation for
`Δ = 0.00` sitting underneath the selector explanation, and the two are not distinguishable from
the number alone. I will not know until I read its files, which I have not.

"Third training disabled" is unaffected and stays: the macro layer never emits `TRAIN`, and a
`TRAIN` from the champion passes through identically on both arms, so the arms cannot differ by a
roster change.

## 4. What the two gates establish, and what they do not

- **Gate 1, identity — PASS 24/24.** Arm B under the pass-through macro is byte-identical to arm A
  on all 300 turns of all 24 map-seats: same command stream, same own score, same opponent score,
  same roster, **zero referee errors on both arms**. The macro layer designates a planter and
  rewrites its fragment on every post-branch turn, so the wiring is exercised, not bypassed.
- **Gate 2, mechanics — PASS 5/5.** The referee agrees with every mechanic the parent card §4 hands
  over for free: a felled size-4 tree banks 16 points; maturity health 6/12/12/20 for
  banana/plum/lemon/apple; a chop-1 troll fells them in 6/12/12/20 turns; the on-cell plant rule;
  and first fruit at 12/12/8/16 turns beside water against 32/32/36/24 inland.

**One convention had to be pinned to make the fruit numbers line up, and I am flagging it rather
than burying it.** The card's figures match the referee when the **planting turn is turn 0** and
the count begins with the tick *after* it. Counted the other way every figure is one larger. The
referee and the card agree; they agree *under a stated convention*, and an unstated one is how two
implementations produce two different tensors from the same sentence.

**What these gates do not establish:** nothing about value. No Δ has been computed and no planting
policy has been run. Gate 1 tests my plumbing; gate 2 tests my premises. Both had to pass before a
value number could mean anything, which is why they ran first.

---

**The constraint is still held.** No file body under `chatgpt_1/champion-prefix-orchard/` has been
opened. The one contamination on the record is the three per-policy means quoted to me unbidden in
the coordinator's ruling of 17:33Z, declared in my ack `20260904T181500Z`.
