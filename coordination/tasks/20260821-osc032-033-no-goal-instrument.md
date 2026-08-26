# 20260821-osc032-033-no-goal-instrument — why these two trolls were never given a job

- Status: **CLOSED — DELIVERED 2026-08-21** (G-1 `c0bdb4d6` → REVISION_REQUIRED →
  revised `a7c57893` ACCEPTED_FOR_G3 06:41Z; G-3 `50fa5a8e` ACCEPTED by codex_1
  06:55Z; owner brief `claude_1/nogoal/owner-brief-2026-08-21.md` delivered to the
  owner by the integrator 07:1xZ). Finding: every window turn one seeded `WAIT`
  via `main:IDLE_REGEN_FALLBACK`, nothing real formed or discarded, one own unit
  all game in both fixtures. Bug-vs-correct-caution: **owner ruling pending**;
  follow-up measurement chartered at the owner's request:
  `20260821-osc032-033-cause-attribution`. Owner-chartered in the 4b sitting
  ("charter a small look"); package that raised it:
  `local_claude_1/session-inputs/4b-sitting-package-2026-08-21.md` bucket F.
- Record owner: local_claude_1 · Work owner: **claude_1** (instrument) ·
  Reviewer: **codex_1** (instrument-first) · Integrator: local_claude_1
- Area: oscillation verdict residue, branch **4b** (iteration pool #6)
- Base: the **current champion** `547fa706cc1c684a1f8c2a08174792d95e553b2382facfe15884d2ef544070b0`
  (Door-1 pure deletion, KEPT by the owner 2026-08-21), diagnostic copy only.
  The resident file, the dev copy and the live Arena are untouched; no
  candidate, no submission. Session 3 owns the Arena and this task must not
  touch it.
- Created UTC: 2026-08-21T05:20:00Z

## THE QUESTION (owner's, plain words)

In recorded cases OSC-032 and OSC-033 a troll stood still for **110** and **143**
turns, and on **every single one of those turns** the instrument measured that
work was available to it. Nobody assigned it a job. These are not benching cases
— no bad pairing was measured — so the anti-benching cure on the shelf does not
touch them, and nothing else explains them. **Why was no goal ever assigned?**

## THE GOAL

The generator names its own silence, from the real bot's execution: for each of
the two fixtures, for every turn of the window, for the stalled unit — which
route produced the candidate list, what was in the list before and after that
route, and what (if anything) was discarded. Deliverable = the measurement + an
owner brief in plain words.

**NO fix. NO candidate. NO judgment.** Bug-versus-correct-caution is the
OWNER's ruling afterward and nothing in the deliverable may pre-empt it
(smuggled-verdict discipline: attributions and measurements only, neutral
wording). This is the same shape as 4c, which is the shape that worked.

## What to build — reuse, do not reinvent

Phase 3 of the anti-benching task already built exactly this instrument for the
four benching fixtures and it passed five gates:
`claude_1/picker2/idle_shape.py`, `make_route_probe.py`, `route_census.py`
(`claude_1/picker2/phase3-generator-route-2026-08-20.md`). **Point them at
OSC-032 and OSC-033 on the champion base.** A new instrument is justified only
where the existing one provably cannot answer; say so if that happens rather
than quietly writing a second one.

Log unprivileged: every route, not only the one under suspicion. Phase 3's own
lesson applies directly — its card asserted an empty candidate list and the
measurement found a one-element list and a discarding fallback instead. **Do not
carry that finding across as an assumption.** Whether these two fixtures take
`main:IDLE_REGEN_FALLBACK` at all is a measurement, not a premise, and
`view.turn>=100` sits suspiciously close to both windows (110 and 143 turns).

## Gates (fail-first, in order)

1. **G-1 instrument review:** codex_1 reviews the probe application BEFORE any
   result is treated as a finding (instrument-first; self-audit is not the
   gate). If the Phase-3 probes are reused unmodified, the review may be short
   and may lean on their accepted gates — but it is still published before the
   finding.
2. **G-2 parity + coverage + both-ways controls:**
   - **Parity:** the instrumented build's command stream is byte-identical to
     the uninstrumented champion's on both fixtures.
   - **Coverage:** exactly one route row per audited unit per turn across each
     full window — no gaps, no duplicates, subject-derived, no constant to
     match (the 4c Amendment-1 lesson: never bound coverage by a number
     borrowed from another population).
   - **Cross-probe agreement:** the list length read at the generator's exit
     equals the selector probe's row count for the same unit and turn, as in
     Phase 3.
   - **Firing both ways:** the tap is not a constant — employed turns of the
     same fixtures must come back with non-idle routes.
3. **G-3 the finding:** per-turn route table (JSON + short md), the named
   route(s) with their distribution, whatever was formed and discarded, and an
   explicit statement of what is NOT claimed. Then the owner brief.

## Explicitly OUT of scope

- Any behavior change, however obvious the route looks; any harm/benefit
  judgment; any class-wide claim ("this happens in other games") — that is a
  possible follow-up the owner may charter after ruling.
- **Any extension of P1/P2 or any work against the owner's open
  extend-versus-replace design question**, which remains unruled and unstarted.
- Any Arena action of any kind. The Arena controller is local_claude_1 and
  session 3 is running.
- Any touch of the byte-sacred resident file or dev copy; no formatters over
  hash-locked sources.

## Why it is worth doing (recorded so the scope is not inflated later)

These are 2 cases of 34, and the owner chartered a **look**, not a cure. The
value is that they are the last unexplained cases in the investigation: 8 are
fixed, 18 are ruled bugs with a cure on the shelf, 6 are stamp candidates
awaiting the owner's own look, and these 2 are the only ones where nobody can
say what happened. If the answer turns out to be the same mechanism as the
benching class or the same fallback as Phase 3, that is a finding too, and a
cheap one.
