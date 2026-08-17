# Session input: cure candidate C — "fix the first door" (OWNER PREFERENCE 2026-08-17)

- Status: the owner's stated preference ("I like C"), recorded ahead of the verdict
  session (pool #6). The session holds the formal ruling; NO cure code before it.
- Displaces the integrator's B recommendation; B becomes the named fallback; D
  (pairing bench) stays a separate question pending L1 evidence the trades are bad.

## What C is, precisely

Do not route mid-game trolls into the endgame planner at all. At the fall-through
(`readable resident :1189`, `idle_regeneration && chops.is_empty()`), when NOT in
true endgame, replace `return endgame_candidates(...)` with an explicit MID-GAME
FALLBACK CHAIN assembled from EXISTING generators (no new candidate logic):

1. `idle_harvest_candidates` (exists; trusted in endgame today);
2. if the troll carries anything — `bank_candidates` (exists);
3. if all empty — WAIT, **stated as the chain's explicit end**, never as an
   accidental leftover.

The chain MUST be written out in full — the two-doors lesson applies to the cure
itself: an undefined tail is how the next wall gets built.

## What C closes (measured basis)

- **CORRECTED 2026-08-17 (claude_1's measured cross-tab, from the accepted
  instrument):** C's honest acceptance set is the BULLETPROOF FOUR — OSC-008, OSC-028,
  OSC-032, OSC-033 — cured completely (311 of their 311 no-goal turns), plus 14 bonus
  turns across OSC-031/001. Total: 325 of the 521 no-goal turns. **The other four
  situations are untouched by C, each through a DIFFERENT door:** OSC-009 (all
  endgame-branch — C alters only the non-endgame path, per sub-choice 2), OSC-005
  (full backpack exits at :1185 before the fall-through), OSC-031 (167 turns have no
  fruit anywhere — C's chain correctly reaches its WAIT tail; the same unresolved
  chop-side mechanism), OSC-001 (mostly endgame-branch + occupancy). **The acceptance
  fixtures are the FOUR at 311/311 — never the eight**: adopting eight would sink a
  working cure or invite relaxing the gate to fit the result.
- **Bonus synergy with the no-planting ruling:** the mid-game fall-through is one of
  the roads into the endgame planner's conversion PICK (the C2-style suppression
  corners). Closing the road shrinks the suppression-log surface the log-and-defer
  ruling watches. Fewer trolls in the endgame planner mid-game = fewer corners.

## Risks, named

- Collateral breadth: ANY temporarily-chopless troll now harvests mid-game —
  denial timing, banking cadence, and pairing equilibria shift outside the 8. Same
  collateral surface as B, PLUS these trolls lose the endgame planner's side
  behaviors mid-game (the shack-side conversion at ~83 — probably good riddance,
  but it is a behavior change and must be named in the diff).
- Harvest scores were tuned for their current contexts; in the new slot they may
  outbid or underbid unexpectedly. The panel and the paired night carry this risk,
  not argument.

## Decision procedure (already standing — nothing new to invent)

Pre-registered per-fixture cure predictions (8 rows, written before the build) →
implementation-validity gates with observed-failing tests → 240-game panel with
ZERO de-novo D-1 AND P4 → one paired A-vs-resident night under the M-1 rule
(1.96·SE winner, 1.0 materiality floor). One change per night; never stacked with
the banana farm.

## The residue — the session's bigger question (claude_1's framing, adopted)

OSC-031's 167 chop-only turns are a DIFFERENT mechanism that C does not address and
that remains deliberately unlocalized. If the owner wants THE PARKED TROLL fixed
rather than THE PHASE GATE fixed, that residue is the next question — and it is
bigger than the one C closes.

## Open sub-choices FOR THE SESSION (not decided by this preference)

1. The chain tail: plain WAIT, or endgame_candidates as a last resort? (Drafted:
   plain WAIT — a troll with no chops, no harvests, and nothing carried has no
   business in the endgame planner mid-game.)
2. Does true-endgame routing stay untouched? (Drafted: yes — C changes only the
   mid-game fall-through; endgame(view) routing is out of scope.)
3. Who implements: claude_1 is the natural owner (it built the audit); charter
   written at the session.

## Links

Mechanism: `claude_1/hstarve1/mechanism-note-pool5-2026-08-17.md` · Discovery note:
`docs/DISCOVERY-two-correct-doors-make-a-wall-2026-08-17.md` · Pricing:
`local_claude_1/pool4/margin-decomposition-2026-08-17.md` · Alternatives analysis:
the integrator's session-prep message of 2026-08-17 (A/B/C/D/E).
