---
schema_version: 2
type: handoff
task_id: 20260902-cheap-third-troll
from: local_claude_1
to: ["claude_1"]
cc: ["user"]
message_id: coordination/messages/local_claude_1/20260902T181500Z-20260902-cheap-third-troll-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: 1edffa48a9ccad04190977efd9a720ec0513cd58
artifact_paths: ["coordination/tasks/20260902-cheap-third-troll.md"]
created_utc: 2026-09-02T18:15:00Z
---

- To: claude_1
- CC: user
- Task: 20260902-cheap-third-troll
- Requires acknowledgement: yes — a new card, step 1 chartered to you: the read. Acknowledge with your
  start time and, if you see it, the number you expect to decide it.

# HANDOFF — the successor is chartered by the owner ("yes", 18:0xZ): the cheap third troll. Step 1 is yours: the read, one day, no build

**The card:** `coordination/tasks/20260902-cheap-third-troll.md` at the pin above — read it whole; the roles are
set so the two-agent separation is back: **you read and build, I verify by execution**; the design review goes to
chatgpt_1 (the owner activates it on my request); codex_1 is out until 09-07 and off this card.

**The idea in one breath.** Our champion as it plays today (two trolls, wood from turn one), plus the weakest third
troll that still pays, bought with the smallest possible detour — no orchard, no talents, no long stop in the
chopping. The port and every earlier third-troll card lost in the funding phase; this card asks whether a bill of
eleven items (a 1/1/0/1 troll: 3 plums, 3 lemons, 2 apples, 3 iron with two trolls owned) can be paid without
losing the wood race, and whether that troll earns it back. The cost table is on the card (the referee's rule:
`n + talent²` per kind).

**Your step, the read — everything from what we already hold, nothing built:**

1. What the champion banks and holds: the fruit and iron in the bank after the second troll is trained, and what
   it banks afterwards, per game, on our own collected games (`local_claude_1/ladder-queue/games-41230202/`,
   `local_claude_1/denial-ablation/games-41202036/`, v6 telemetry); how far each cheap bill is from that.
2. What the trolls pass: fruit and iron within one step of the paths the two trolls actually walk in turns 20–150,
   by kind — the pickups that cost a turn and no detour.
3. The cost of the smallest dedicated detour: from the champion's own opening rate (items banked per troll-turn in
   turns 1–20) and its chopping rate afterwards, the turns two trolls need for 11 / 14 / 17 / 20 items and the wood
   they forgo, in points.
4. What a weak troll earns: wood per troll-turn by talent shape from the field's trolls (the census, the per-turn
   corpus), and on our games the wood a third troll would bank from the turn it could exist to the end.
5. Two designs costed and one recommended: (A) the opening buys it too (second and third trained back to back
   before chopping starts); (B) a minimal pass after the second troll, only while the bill is within N trips.
   Expected net points per game for each, with the uncertainty.

**Deliverable:** `claude_1/cheap-third-troll/READ-2026-09-0x.md` — one page for the owner (what a cheap troll
costs, what it earns, which design, the expected gain) and the tables behind it, the code beside it, one
ack-required handoff. **Dead on paper:** if the cheapest useful troll's bill costs more than about thirty turns of
two-troll chopping and its expected earnings do not cover it with margin, say so — the card dies at your handoff
and nothing is built. Budget: one day. No build, no panel, no ladder, no platform, no network action.

My own expectation, written on the card before your numbers: about 25 turns of two-troll collecting for the
cheapest bill when the fruit is near the shack; a 1/1/0/1 troll earning roughly a third of a 2/2/0/2 troll's
wood; net a few points either way. Your read decides.
