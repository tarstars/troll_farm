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

- The 8 no-goal situations (325 proven turns; bulletproof four: OSC-032 110/110,
  OSC-033 143/143, OSC-028 51/51, OSC-008 7/7) become observed-failing regression
  fixtures — the cure property flips green per situation.
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
