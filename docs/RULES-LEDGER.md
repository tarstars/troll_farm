# RULES LEDGER — the winning rule set, discovered ruling by ruling

Created 2026-08-15 by owner ruling (see docs/ADJUDICATION-TEMPLATE-2026-08-15.md).
Entries are OWNER-APPROVED only; each rule lists the situations that support it.
Empty until the first adjudication session.

## R-1 — The transport level must detect and execute swaps (owner-approved 2026-08-16)

When two of our trolls need to pass each other, the movement coordinator must recognize
it and issue the coordinated exchange — both step toward each other in one tick. The
referee explicitly allows own-unit circular swaps (`docs/mechanics.md:54-56`); today's
resident never generates them, which is self-imposed. In dead-end corridors a swap is
the ONLY resolution (yielding has nowhere to go).

- Supporting situations: OSC-001 (ruling: `local_claude_1/adjudications/OSC-001-ruling-2026-08-16.md`);
  expected to bear on the 11 M1 corridor episodes.
- Origin: owner statement in the first adjudication, 2026-08-16; early written trace
  `docs/reference/2026-07-11-yannbot-design.md:55`.

## R-2 — A troll with available work must be employed (owner-approved 2026-08-20)

There is work to do and the troll can do it — not doing it is a bug. No
materiality boundary: the rule was tested at the 4a sitting on the worst case
(194 benched turns), the corridor-blocker shape, the whole-bot stall shape,
and the shortest episode (12 turns), and the owner ruled BUG on all four. The
team-picker (joint pairing) discarding a troll's available work is the named
defect mechanism; the movement-level swap (R-1) treats only the symptom.

- Supporting situations: OSC-017, OSC-013, OSC-034, OSC-004 (owner rulings in
  `local_claude_1/session-inputs/4a-sitting-package-2026-08-19.md`); the
  class = all 24 GOAL_SPLIT cases of the pool-3 table (oracle-verified usable
  work on every benched turn).
- Origin: owner statements at the 4a sitting, 2026-08-20 ("when troll has a
  job to do, not doing it is a bug"; "there is work to do, trolls can do this
  job — they can swap or whatever. We should fix it").
- Consequence: pair-selector anti-benching fix chartered
  (`coordination/tasks/20260820-pair-selector-anti-benching.md`), evidence
  first; sibling of the pool verdict rule's generator-coverage property, one
  level up (the picker must not discard what the generator offers).
- 4b bucket B (owner rulings 2026-08-21, the four "harmless" stamps withdrawn):
  OSC-005 and OSC-027 — pass blocked by a working teammate in a one-wide
  corridor (the R-1 swap shape); OSC-010 — open-map pass blocked, a zero-cost
  detour ignored (teammate-aware routing); OSC-030 — same tree wanted while a
  teammate works it, a free tree two cells further (tree reservation, the
  picker family). All four NOT FIXED on champion `547fa706`; no cure chartered.
  Record: `local_claude_1/adjudications/4b-bucket-B-ruling-2026-08-21.md`.
- 4b buckets D/E (owner rulings 2026-08-21, stamps withdrawn; 4b CLOSED):
  OSC-026 — a single troll flips between two nearly-tied jobs for 9 turns with
  a reachable lemon on the map (goal-selector flip, M3); OSC-012 — a troll with
  no chop/harvest power parks on the only tree for 193 turns while the able
  troll dances in front of it (idle occupier invisible to the compatibility
  check, M2; a swap would have resolved it at turn 8). Both NOT FIXED on the
  champion; no cure chartered. Record:
  `local_claude_1/adjudications/4b-buckets-D-E-ruling-2026-08-21.md`.
