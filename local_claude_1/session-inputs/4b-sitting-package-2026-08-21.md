# 4b sitting package — the harmless stamps, ready to run (2026-08-21)

## SITTING RESULT 2026-08-21 — stamps HELD; the two stalls get a look

The owner sat with this package the morning it was written and ruled twice:

1. **All six proposed stamps are HELD.** Nothing is stamped. Buckets B, D and E
   stay open. The stamps were offered with reasons but without the owner having
   seen the games, and the owner's standing rule is to judge from the game state
   down, never from the code up — so the six are re-listed below as a
   **look-and-rule sheet with viewer links**, in the shape 4a used. The
   investigation does **not** close until they are ruled.
2. **Bucket F is CHARTERED as a small look** — not stamped, not folded away:
   `coordination/tasks/20260821-osc032-033-no-goal-instrument.md`. Why was no
   goal ever assigned to those two trolls? Measurement only, no fix, no
   judgment; claude_1 builds, codex_1 reviews instrument-first.

Bucket C is unchanged and needed no ruling. Bucket A is unchanged and closed.

### The six held cases, with the game to watch

Open `claude_1/viewer/out/<CASE>.html` in a browser and judge the position.

| case | what to look for | proposed stamp (offered, NOT accepted) |
|---|---|---|
| OSC-005 | the troll waits exactly 1 turn of 12 | normal play, not starvation |
| OSC-010 | the troll never waits at all (0 of 7) | detector artifact |
| OSC-027 | never waits (0 of 22) | detector artifact |
| OSC-030 | never waits (0 of 8) | detector artifact |
| OSC-026 | only one troll exists in this game | no pairing decision exists to be wrong |
| OSC-012 | 193 turns of waiting, 0 turns with usable work | waiting was provably correct |

---


**What this is:** everything prepared so the owner's 4b sitting is a short
look-and-rule session. 4b is the **last** item of the oscillation investigation:
the deep-dive charter requires every one of the 34 recorded cases to end either
FIXED-with-proof or **owner-stamped "accepted, because…"**. The stamp kills
ghosts — an unstamped case gets rediscovered and re-investigated by a future
session that does not know it was already looked at.

**Where the other branches went:** 4a is COMPLETE (owner ruled the pairing-bench
a class-wide DEFECT, rule R-2). 4c is CLOSED (owner ruled OSC-031's silent chop
refusal a DEFECT; the forecast fix became cure C and then Door 1). So 4b is all
that is left.

## The grader used here, stated plainly

Every verdict below is the **standing FIXED grader** run against the **current
champion** — `547fa706…`, the Door-1 pure deletion the owner KEPT this morning —
not against the old resident the library was frozen on. FIXED means *the
detector is silent AND the troll made progress*. Source:
`claude_1/picker2/sweep34-door1-base.json`, causes and turn counts from the
accepted pool-3 table `claude_1/hstarve1/cause-table-pool3-2026-08-17.json`.

**A fact worth having before you rule:** on the frozen 34, the champion you kept
is **strictly better than the cure-C bot it replaced — 8 FIXED versus 3, and not
one case lost**. OSC-003, OSC-006, OSC-014, OSC-020 and OSC-034 are fixed by
Door 1 and were not fixed by cure C. The Arena called the same step immaterial;
the fixture grader does not. Both readings are true and they are measuring
different things.

---

## Bucket A — CLOSED as FIXED, nothing to stamp (8 of 34)

No ruling needed. Recorded here so the count adds to 34.

| case | turns waiting | cause on record |
|---|---:|---|
| OSC-003 | 21 | GOAL_SPLIT_WRONG |
| OSC-006 | 7 | GOAL_SPLIT_WRONG |
| OSC-008 | 7 | NO_GOAL_ASSIGNED |
| OSC-009 | 7 | GOAL_SPLIT_WRONG + NO_GOAL_ASSIGNED |
| OSC-014 | 168 | GOAL_SPLIT_WRONG |
| OSC-020 | 172 | GOAL_SPLIT_WRONG |
| OSC-028 | 51 | NO_GOAL_ASSIGNED |
| OSC-034 | 94 | GOAL_SPLIT_WRONG |

---

## Bucket B — the four NOT-STARVED cases: stamp candidates (4)

These are the ones the investigation itself already found innocent: the troll
was **working**, not parked. The detector fired on the shape of the moves, not
on idleness.

| case | turns waiting | turns with usable work | proposed stamp |
|---|---:|---:|---|
| OSC-005 | 1 of 12 | 12 | *accepted — the troll waited one turn in twelve; this is normal play, not starvation* |
| OSC-010 | **0** of 7 | 7 | *accepted — the troll never waited at all; detector artifact* |
| OSC-027 | **0** of 22 | 22 | *accepted — never waited; detector artifact* |
| OSC-030 | **0** of 8 | 8 | *accepted — never waited; detector artifact* |

**Ruling asked:** accept all four with the stamp above? (One word: *accept*.)

---

## Bucket C — the 18 benching cases already ruled a BUG (18)

**Nothing to stamp and nothing to re-decide** — you ruled these class-wide on
2026-08-20 (rule R-2: *a troll with available, doable work that is not doing it
is a bug*). They are recorded as **BUG, cure built, cure on the shelf**: P1+P2
exists, was reproduced by codex_1, and was BLOCKED as a qualified cure, and this
morning you ruled D3 = HOLD, no Arena slot. They close as *known-open*, not as
*accepted*.

OSC-001, OSC-002, OSC-004, OSC-007, OSC-011, OSC-013, OSC-015, OSC-016,
OSC-017, OSC-018, OSC-019, OSC-021, OSC-022, OSC-023, OSC-024, OSC-025,
OSC-029, OSC-031 — waiting turns from 6 to 195, and in every one of them the
work was measurably there.

**One line inside this bucket does need your eye — OSC-031.** It is the case
that started the whole 4c thread; you ruled its silent chop refusal a defect;
the fix for it became cure C and then the champion. **It is still NOT FIXED on
the champion** (the detector still fires across its 190 waiting turns). That is
not a contradiction — the chop defect was real and was fixed, and what remains
firing in that game is the benching, which is bucket C's disease. But it should
be said out loud rather than left to be rediscovered.

**Ruling asked:** none required. Say *known-open* to confirm the bucket closes
that way, or name OSC-031 for its own follow-up.

---

## Bucket D — OSC-026, the single-troll case: stamp candidate (1)

There is only one unit in this game. There is no pair, so there is nothing for
the team-picker to get wrong; the anchor rule itself returns NO_ANCHOR for it.

**Proposed stamp:** *accepted — one troll on the board; no pairing decision
exists to be wrong.*

---

## Bucket E — OSC-012, the empty-hands case: stamp candidate (1)

The troll waited **193 turns** — and the instrument measured **0** turns in
which usable work existed. It is the only case in the 34 where waiting was
measurably the correct answer.

**Proposed stamp:** *accepted — nothing usable existed for 193 turns; waiting
was correct.*

---

## Bucket F — OSC-032 and OSC-033: these need a real ruling (2)

The only two cases the investigation never assigned to a class. Both are the
**stall** kind, both were labelled NO_GOAL_ASSIGNED, and both look exactly like
what rule R-2 calls a bug:

| case | turns waiting | turns with usable work | grader on the champion |
|---|---:|---:|---|
| OSC-032 | 110 | 110 | detector quiet, but the unit is still stalled |
| OSC-033 | 143 | 143 | detector quiet, but the unit is still stalled |

Every single turn the troll waited, work was available to it. If R-2 is read
literally, these are bugs — but they are **not** benching cases (no pair
mis-selection was measured), so the P1+P2 cure on the shelf does not address
them, and nothing else is chartered that would.

**Ruling asked, and this is the one real decision in the sitting:**

- **(a) fold into R-2 as known-open** — same status as bucket C: named a bug,
  no cure chartered, no work starts today; or
- **(b) stamp them accepted** — declare them harmless despite R-2, with your
  reason recorded; or
- **(c) charter a look** — a small measurement of *why* the goal was never
  assigned in these two, before anyone decides. Costs machine time, no Arena
  time.

My recommendation is **(a)**: R-2 is your rule and these fit it plainly, but
nothing is understood well enough to build against, and Phase 3 has just shown
how a plausible-looking generator gap can turn out to be a different mechanism
than assumed.

---

## The ruling sheet (owner fills; integrator records into the ledger)

| bucket | cases | ruling |
|---|---|---|
| B — not starved | OSC-005/010/027/030 | |
| C — benching | the 18 | |
| C — OSC-031 specifically | | |
| D — single troll | OSC-026 | |
| E — empty hands | OSC-012 | |
| F — the two stalls | OSC-032, OSC-033 | |

When this sheet is filled, the oscillation investigation is **closed**: every
one of the 34 cases ends either FIXED-with-proof or owner-stamped, and no ghost
survives to be re-investigated.
