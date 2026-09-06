---
schema_version: 2
type: update
task_id: 20260904-orchard-reproduction
from: claude_1
to: ["claude_1"]
cc: ["local_claude_1", "chatgpt_1", "user"]
message_id: coordination/messages/claude_1/20260904T183000Z-20260904-orchard-reproduction-deferred.md
requires_ack: true
ack_for: ["coordination/messages/claude_1/20260904T173000Z-20260904-orchard-reproduction-deferred.md"]
supersedes: []
created_utc: 2026-09-04T18:30:00Z
---

- To: claude_1 (self)
- CC: local_claude_1, chatgpt_1, user
- Task: 20260904-orchard-reproduction
- Requires acknowledgement: yes — by the next claude_1 session.

DEFERRED, one item. This message discharges `20260904T173000Z-...-deferred.md`, whose **item 2 is now CLOSED**: the
`--mark` blocker cleared when the coordinator quarantined the defective handoff (ruling `20260904T173300Z`,
acknowledged at `20260904T181500Z`). This wake's sweep reported `delivery errors (0)` and `--mark` ran. **Exactly one
card of mine stays pending, and it is the live work.**

**The reproduction is live, both mechanics gates PASS, and no value number exists yet.** Artifact
`agent/claude_1@c875cff634866e3c12c4fa1e618a0f680d8057ce`, reported at `20260904T182500Z`. Due **2026-09-06 17:00Z**.

**Done so far:** gate 1 identity, 24/24 byte-identical with zero referee errors on both arms; gate 2, the referee
agrees with all five mechanics the parent card §4 gives for free; the branch-reading finding (**the champion trains
once**, so the charter's "second `TRAIN`" has one executable reading, adopted and registered in
`ADDENDUM-2026-09-04-gates.md` before any number existed); and two corrections to my own pre-registration —
`PLANT`/`CHOP` are **on-cell** actions, and a plant onto a tree-occupied cell is a **silent no-op** that a
no-command-streak exclusion rule cannot see.

**Next, in this order — cheap checks before expensive computation:**

1. The **plant-accounting assertion** (every emitted `PLANT` either raises the referee's plant count or spends the
   seed) — it is cheap and it guards the trap in point 2 above, so it goes in before the grid runs, not after.
2. The policy machine over the 48-policy grid + `NO_PLANT`, on the same 24 map-seats, seed 0.
3. Both exclusion-rule variants — mine, relative to the champion's own longest no-command streak on the same
   map-seat, and an absolute-threshold variant — **with their counts side by side and what the excluded policies
   score.**
4. The leave-one-map-out selector; the per-map choice reported **only** as an explicitly-labelled hindsight upper
   bound.
5. The fixed-policy table (no selection at all) and the margin-over-turns curve — the discriminator that tells
   *"the selector never planted"* apart from *"planting gained nothing"*.
6. Write the numbers down and **commit them**. Only then read `chatgpt_1/champion-prefix-orchard/`, then the direct
   comparison and a plain statement of whether the two implementations agree.

**THE STANDING CONSTRAINT, carried into every wake until delivery:** do not open any file body under
`chatgpt_1/champion-prefix-orchard/` until my own numbers are written down and committed. File **names** via
`git ls-tree --name-only` and existence via `git cat-file -e` are permitted; **bodies are not.** One contamination is
already on the record — the three per-policy means quoted to me in the coordinator's ruling of 17:33Z — declared in
`20260904T181500Z` and again in `20260904T182500Z`. **If I cross the line again, it goes in the handoff.**

**The owner's platform freeze binds this card** (policy `20260904T140500Z`): no submission by any route, no ladder
item, no runner, no cron. Nothing in the plan above wants one.

**Dead condition, kept in front of me:** if I cannot show my machinery reproduces the referee, I stop and say so
rather than shipping an aggregate I do not trust. Gate 2 is that check and it passed; if the plant-accounting
assertion fails on the grid, that is the same condition firing later and it gets the same treatment.

**On the next wake:** `python3 scripts/inbox_sweep.py --me claude_1 --fetch`, read everything, acknowledge this card,
then resume at step 1 above.

— claude_1
