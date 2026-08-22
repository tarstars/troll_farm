# 20260822-alpha-progress-regrade — does cure α's healing survive the two-clause test?

- Status: **OPEN — OWNER-APPROVED 2026-08-22** ("do it").
- Record owner: local_claude_1 · Work owner: **claude_1** · Reviewer: **codex_1**
  (instrument-first) · Integrator: local_claude_1
- Priority: **top of claude_1's queue.** It is the only unblocked work in that lane, it needs
  no owner ruling and no Arena time, and cure α's fate is held until it lands.
- Created UTC: 2026-08-22T15:52:00Z

## THE QUESTION

Cure α's headline on the matched 240-game panel is **D-1 dance episodes 27 → 9 (healed 18,
new 0)** and **P4 liveness violations 16 → 0 (healed 16, new 0)**. Those are **episode
counts**: they say a detector stopped firing. They do not say a troll started working.

We already know the difference matters, from our own measurement. P1+P2 silenced the dance
detector on **every** fixture it touched and restored progress on **exactly one of four**;
three cure-C fixtures landed *detector-quiet but still stalled*
(`agent/claude_1:claude_1/picker2/phase2-package-2026-08-20.md`, reproduced in
`agent/codex_1:codex_1/reviews/pair-selector-phase2-unified-review-2026-08-20.md`).
"Benched → 0 does not mean working" is claude_1's own sentence.

**So: how much of α's 34 healed events is real?**

## THE RULE, WHICH ALREADY EXISTS — DO NOT WRITE A SECOND ONE

`claude_1/t1/fixture_harness.py` already grades with two clauses:

```
verdict = "FIXED" if (detector_silent and progress_restored) else "NOT_FIXED"
why     = "detector quiet but the unit never progressed or left its cycle"
```

built from `progress_events` and `left_cycle`. The grading rule is inherited from
`local_claude_1/t1-prediction-registry-2026-08-16.md`. **Reuse that predicate byte-for-byte**
(shared-runners rule). The harness itself sets the precedent: it lifts two functions verbatim
from an accepted script and pins the copy with a test that says so. A second definition of
"progress" that disagrees with the fixture grader is worse than none.

## SCOPE — small, and bounded by α's own inertness

α left **210 of the 240 panel games byte-identical**. Only **20 games** can differ, and they
carry the **34 healed events** (18 D-1 + 16 P4). That is the entire re-grade surface. Do not
re-grade the unchanged 210.

## STEP 0 — before building anything, report the price

Establish and report whether the panel run's **traces were retained** (`g2-panel-rev2-2026-08-21.json`
and whatever it references), or whether the panel must be re-run to obtain them. If a re-run
is required, say so and stop for a cost decision rather than starting one.

## DELIVERABLES

1. **An adapter** from a panel episode (unit + turn range + game identity) to the shape the
   accepted predicate consumes. That adapter is G-1's review object; the predicate itself is
   not to be modified.
2. **A per-event table** over the 34 healed events, each landing in exactly one bucket:
   - **HEALED_WITH_PROGRESS** — detector silent AND the unit progressed or left its cycle;
   - **QUIET_BUT_STALLED** — detector silent, no progress. This is the P1+P2 outcome and it
     must come off the headline;
   - **WINDOW_ABSENT** — the base episode's window does not exist in the candidate run, so the
     question cannot be asked of it. Report separately; **never fold into either other bucket.**
     This is the identity trap that produced eight false "FIXED on the champion" grades.
3. **α's headline restated** in the surviving terms, with the named-costs discipline: every
   changed game named, and the three bucket counts printed beside the old 18 / 16.
4. One paragraph, plain words, for the owner: how much of the cure is real.

## GATES

- **G-1 — codex_1, instrument-first.** The adapter reviewed before any result is a finding:
  predicate lifted unmodified and proven byte-identical; identity handled as its own outcome;
  and controls observed firing BOTH ways — a known quiet-but-stalled case graded
  QUIET_BUT_STALLED, and a known genuinely-healed case graded HEALED_WITH_PROGRESS. P1+P2's
  own fixtures supply both: OSC-004/013/017 are quiet-but-stalled, OSC-034 is healed with
  progress.
- **G-2 — the table, the restated headline, the owner paragraph.**

## RULING CARRIED BY THIS CARD (coordinator, 2026-08-22)

**Cure α's G-2 bar is amended to two clauses.** "Healed minus new must be positive" now means
healed *with progress*, not detector-silent. This amends my own gate amendment of
`20260821T105914Z`, which counted episodes. The same correction is pending on the standing
acceptance rule proposed in `docs/DISCUSSION-architecture-over-score-2026-08-22.md` §7, which
is annotated and not adopted until it carries a progress term.

**α does not advance to G-3 or G-4 until this re-grade lands**, independently of the three
questions already open on `20260821-swap-r1-cure`.

## OUT OF SCOPE

No candidate edit, no new cure, no widening, no Arena action, no re-ruling of any case, and
no change to the accepted predicate. If the adapter cannot be built without touching the
predicate, STOP and report — that is a finding, not an obstacle to work around.

## HONEST EXPECTATION, RECORDED SO NOBODY OVERSELLS

The plausible outcomes span the range. α's panel is a different instrument from P1+P2's
fixtures and its cases are different, so its healing may be entirely real. It may also be
partly detector hygiene, as P1+P2's was. **Either answer is a good result**: one tells us α is
worth an Arena slot, the other tells us our headline measure has been overstating cures — and
that second finding would be worth more than the cure.
