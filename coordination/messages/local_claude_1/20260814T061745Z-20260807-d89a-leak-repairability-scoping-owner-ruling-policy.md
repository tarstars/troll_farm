---
schema_version: 2
type: policy
task_id: 20260807-d89a-leak-repairability-scoping
from: local_claude_1
to: ["claude_1", "codex_1"]
cc: ["user"]
message_id: coordination/messages/local_claude_1/20260814T061745Z-20260807-d89a-leak-repairability-scoping-owner-ruling-policy.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: d1be90271c81f92020c846c8fd0d9b8bd61bc447
artifact_paths: ["docs/BACKLOG.md", "coordination/tasks/20260814-iteration-3-work-plan.md"]
created_utc: 2026-08-14T06:17:45Z
---

- To: claude_1, codex_1
- CC: user
- Task: 20260807-d89a-leak-repairability-scoping
- Requires acknowledgement: yes

# Owner ruling: banana-leak question stays open at low priority — gate weakened, not removed

In plain terms, this records the owner's decision of 2026-08-14 on the question both
reviews answered: we will NOT write down that the banana-farming score leak is
impossible to repair. We write down that repairing it is unattractive right now, keep
the door open, and label it "for further investigation" — sized as a potentially big
analysis project, priced at low priority.

Binding consequences, now in `docs/BACKLOG.md` at `d1be9027`:

1. **Closure label:** `FOR_FURTHER_INVESTIGATION`, not structural. Nobody cites
   `NOT_REPAIRABLE` as a proven fact from now on; cite this ruling instead. Both review
   verdicts stand as written — claude_1's numbers reproduced, codex_1's dissent on the
   label is the position the owner adopted.
2. **The gate is weakened, not removed:** banana-leak work remains blocked by default,
   but the block is economic, reversible on cheap new evidence, and no longer claims
   impossibility.
3. **New programme entry `D89a-LI`** (backlog §P3, owner programmes): the standing
   question is *why* sustained banana farming raises the opponent's score, with the
   three known missing measurements listed (theft-vs-own-production split, dose timing,
   referee-mechanical vs opponent-behavioural). **LOW priority: it never displaces
   P0–P2 work, is assigned to no one, and starts only on a fresh owner charter.** Do
   not claim it, do not start it, do not fold it into other tasks.
4. **Unchanged:** the strict no-banana-before-second-troll rule (CONSTRAINTS §(h)); the
   CBF design stays parked as designed-not-implemented, its build decision still with
   the owner; the standard experiment bar (≥+1.0 at 5 runs/arm) for any future
   candidate from any of this.

Task `20260807-d89a-leak-repairability-scoping` is now fully closed: two reviews
delivered, owner ruling recorded. Thank you both — the disagreement was exactly the
service the two-review structure exists to provide.

No Arena action was taken or authorized.
