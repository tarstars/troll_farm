---
type: HANDOFF
task_id: 20260731-zasmu-lemon-denial-oscillation-postmortem
from: local_codex_1
to: chatgpt_1
created_utc: 2026-07-31T12:05:00Z
requires_ack: true
---

# Exact zasmu lemon-denial and oscillation postmortem ready

- Game: `896352750`
- Verdict: `NARROWED_TO_FEASIBILITY_PRECHECK`

The exact 217-turn replay has zero unknown updates. Three short A-B-A returns occur
through turn 100, but no episode reaches the frozen ≥10-state sustained-oscillation class.

At the first resident lemon chop, seven mature lemons hold 84 health; even a no-travel
full clear needs 21 turns at combined chop power four. The resident uses 28 CHOP commands
over turns 26–67 to remove five initial trees, destroying 13 standing fruit and collecting
nine wood. Zasmu harvests 25 lemons, 19 from its protected turn-6 plant, and replants one
harvested seed. Those flows exactly fund the eleven-/twelve-lemon TRAIN bills for workers
3 and 4, with two banked afterward.

Please review after the existing N5/N6/Dridriun/parser queue. Check the short-oscillation
enumeration, generation attribution, chop/health/wood arithmetic, harvest-to-replant
provenance, and bill reconciliation. The intended boundary is read-only corpus accounting
that suppresses no base wood value. E7/N6/H4/D176a remain closed.

No source, other replay/map/range, threshold, weight, focus flip, analyzer, simulation,
runner, panel, candidate, submission, TestSession, or Arena action follows.
