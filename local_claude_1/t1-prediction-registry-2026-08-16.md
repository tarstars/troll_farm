# T-1 pre-registered predictions — which frozen situations the transport feature should cure

- Registered 2026-08-16 BEFORE any T-1 code exists (owner-directed triage: implement,
  re-run, hand-adjudicate only the residue). Grading these after the re-run tests both
  the fix and the M1/M2 transcript-inferred classification (unknown U1) at once.
- Feature under prediction: T-1 = Target::None visibility fix + idle-yield + swap
  (referee-legal per docs/mechanics.md:54-56; rules-ledger R-1).

## PREDICTED FIXED (25/34)

- M1 idle blocker on route — OSC-001, OSC-002, OSC-009 (swap or yield).
- M1 WORKING blocker on route — OSC-003, OSC-004, OSC-005, OSC-006, OSC-007, OSC-008,
  OSC-010, OSC-011 (SWAP ONLY — yield would interrupt the worker; predicted cost ~2
  worker-turns per resolution).
- M2 stationary occupier invisible to planning — OSC-012 … OSC-025 (all 14; visibility
  fix + yield; swap equivalently hands over the contested cell).

## PREDICTED NOT FIXED (9/34) — the owner's hand-review residue

- OSC-026 (M3, single own unit alive): level-3 scorer cycle (door pricing); transport
  cannot apply. Needs the separate D1-B fix.
- OSC-027 … OSC-030 (UNCLASSIFIED pacing, no adjacent stationary peer): mechanism
  unknown; Decision Packet material.
- OSC-031 … OSC-034 (P4_STALL): standing-still disease, likely intention-level (U4).

## Grading rule (frozen now)

A situation counts FIXED only if, replayed under the T-1 candidate: the D-1/P4 detector
is silent over the window AND progress is restored (the stuck unit reaches its target or
produces progress events) — detector-quiet-but-stalled counts as NOT FIXED (the 08-09
20/20 lesson). Any PREDICTED-FIXED case that survives, and any PREDICTED-NOT-FIXED case
that gets cured, is a named prediction miss and goes to the owner session with priority.
