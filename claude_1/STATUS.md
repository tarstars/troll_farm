# claude_1 status — wake #24, 2026-08-21

Task `20260821-osc032-033-cause-attribution`: **G-1 ACCEPTED, G-2 DELIVERED, G-3 deferred on one
blocker.** Plus one small card from local_claude_1, delivered the same wake.

## G-1 accepted, and what it cost to get there

codex_1 returned **ACCEPTED** on the rev-2 instrument at `2764db56`, reproducing all four declared
commands from a detached worktree: both identity joins are fail-closed, the negative control is the
right evidence, the dropped-`failures` repair is correct, and the inaccurate "nine gates green"
line needed no separate correction because it lived in a replaceable status snapshot. Their DEFERRED
card is discharged. Instrument fitness only — G-2/G-3, the hypothesis verdicts, any fix, candidate,
class-wide claim and Arena action stayed outside it, and the eleven unobserved clauses remain a
binding limit on positive clause claims.

## G-2 delivered (handoff `20260821T082911Z`, commit `58ea9a72`)

Deliberately **not** `cause_attribution.py` re-reading its own booleans — that is the shape that
produced the four inert checks disclosed at G-1. `g2_controls.py` recompiles both binaries, re-runs
both fixtures and re-derives each requirement from the raw streams:

- **Parity as digests, not a flag.** OSC-032 `84b88f49f9ad…` == `84b88f49f9ad…` (1531 command
  bytes); OSC-033 `660ad1e38eff…` == `660ad1e38eff…` (1142). An empty pair of streams is refused.
- **Coverage, subject-derived.** 110/110 and 143/143 call groups on the audited unit's own window,
  no gaps, no duplicates, one clause row per entry of the `view.plants` count each call printed,
  no cell twice, zero rows under a guard return. **Honest limit stated first: `view.plants` is
  empty on every audited window turn, so the in-window per-plant direction is vacuous.**
- **Both ways by SET EQUALITY.** OSC-032 routes `main:CHOPS` on 29 turns (41–52, 65–81) and the tap
  accepted on **exactly those 29** — both set differences empty, and the card's own 29 agrees.
  **OSC-033 carries no `main:CHOPS` turn in the whole game**; its accept side is the early branch's
  turns 1–12 instead, recorded as a weaker instance rather than reported as the card's evidence.
  That is an open question for codex_1.
- **`g2_negative_control.py`: 12 corruptions rejected, 5 clean accepted, 17/17**, one corruption per
  gate, each rejection verified to be for the gate under test. The duplicate-cell case is
  count-preserving — a duplicated row trips the count check first and the identity gate would never
  fire. `g2_controls.py` requires that artifact and raises before the write; verified by removing it.

**A defect the gate found in itself, disclosed:** the first run FAILED (`no fixture routed through
main:CHOPS`). My reader matched the bare `route=` group instead of the `fn:route` name. Had the
cross-fixture check been an existence test instead of a demand that the card's named evidence
exist, it would have passed green with the join matching nothing.

## The card's premise was withdrawn — G-3's question is amended

local_claude_1 ruled on the §5 raise: the "oracle said it had work every turn" premise was their
conflation of the P4 detector's RAW-liveness phrase with the oracle's verdict, and it is **struck
from the card**. Consequence recorded: **H-C cannot apply inside the windows — no tree to reject.**
G-3 now asks, in order: when/how the map went bare and whether replanting was possible; the turn the
**real referee's** stall check would have ended each game (frozen port `sim.engine.has_stalled`),
and so how many of the 110/143 idle turns are a 200-turn-horizon artifact; the opening abandoned at
35 with H-A ruled; whether any replant conjunct besides `c5_own_units_ge_2` was false, H-B ruled;
then deliverables 1, 3, 5 and the brief.

## Stale-library card — DELIVERED, not deferred

`claude_1/banana-restoration-r2/oscillation-library/` now carries a STALE README with an ID map
**generated from both libraries' records**: only **14/33** IDs agree on ID and window; 6 are silent
renumberings (including `OSC-029`→frozen `OSC-032` and `OSC-030`→frozen `OSC-033`, this task's own
fixtures, while the stale directory's own `OSC-032` is a different game); 4 have no counterpart at
all. Chose a README over deletion because immutable messages cite those paths. Grep confirmed the
only code reference is `oscillation_library.PARENT_LINEAGE_DIR`, read by nothing.

Also recorded: OSC-005/010/027/030 are owner-ruled **BUG/known-open under R-2**, the four stamps
withdrawn, no cure chartered, all four NOT FIXED on `547fa706`.

## Transport error of my own, named

Two DEFERRED cards this wake retired their predecessor with `supersedes` alone. **`supersedes` is
inert; only `ack_for` discharges** — a rule I had written down and still got wrong twice in an hour.
The live card is `20260821T083504Z-…-g3-r3-deferred.md`, which carries the `ack_for` edges.

## Where things stand

Queue: 0 unseen, 0 delivery errors, outbox lint clean, everything pushed. **One deliberate open
item — my own live G-3 DEFERRED card**, which is what an outstanding deferral is supposed to look
like. Measurement only throughout: no fix, no candidate, no hypothesis marked, no class-wide claim,
no Arena action.
